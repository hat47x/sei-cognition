package livemethodintegration

import (
	"encoding/json"
	"os"
	"reflect"
	"testing"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const pinnedKJAtlasCommit = "4f28c13abe4176503c6fed863383a2d1db2299e9"

var sampleGroupingResult = []byte(`{
  "groups": [
    {"label":"働き方の見立て","cardIds":["c-remote","c-office"],"rationale":"対面と在宅の見立てを同じ論点として扱う"}
  ],
  "excludedCardIds": ["c-held"],
  "truncated": false
}`)

func TestApplyKJAtlasGroupingResultRecordsMethodApplicationWithoutPromotingRecommendation(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, sampleGroupingResult)

	if err := ApplyKJAtlasGroupingResult(input); err != nil {
		t.Fatalf("ApplyKJAtlasGroupingResult() error = %v", err)
	}

	application, found, err := store.Find(input.ApplicationRef)
	if err != nil || !found || application.CognitiveMethod == nil || application.CognitiveMethod.MethodApplication == nil {
		t.Fatalf("method application not stored: found=%v err=%v record=%#v", found, err, application)
	}
	app := application.CognitiveMethod.MethodApplication
	if app.RealizationRef == nil {
		t.Fatal("method application lost realization_ref")
	}
	logicalRealization, ok := app.RealizationRef.LogicalIdentity()
	if !ok || logicalRealization != input.RealizationRef {
		t.Fatalf("realization_ref = %#v, want %#v", logicalRealization, input.RealizationRef)
	}
	if len(app.OutputRefs) != 1 || len(app.ProvenanceRefs) != 1 {
		t.Fatalf("method application refs: output=%#v provenance=%#v", app.OutputRefs, app.ProvenanceRefs)
	}

	output, found, err := store.Find(input.OutputRef)
	if err != nil || !found {
		t.Fatalf("method output not stored: found=%v err=%v", found, err)
	}
	if output.Status != semanticruntime.RecordNotVerified {
		t.Fatalf("opaque external method output status = %q, want %q", output.Status, semanticruntime.RecordNotVerified)
	}
	if !sameJSONMeaning(output.EnvelopeRecord.Payload, input.ResultJSON) {
		t.Fatalf("external result JSON meaning was not preserved\n got=%s\nwant=%s", output.EnvelopeRecord.Payload, input.ResultJSON)
	}

	records, err := store.Records()
	if err != nil {
		t.Fatalf("Records() error = %v", err)
	}
	for _, record := range records {
		if record.Decision != nil {
			t.Fatalf("KJ grouping result was promoted to Decision Memory automatically: %#v", record.Decision)
		}
	}
}

func TestApplyKJAtlasGroupingResultPreservesExecutionIdentityInProvenance(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, sampleGroupingResult)
	input.RealizationRef = logical("method-realization", "MR-KJ-ATLAS-MODEL-BACKED")
	input.Execution = ExecutionIdentity{
		Profile:        "ollama-model-backed",
		Runtime:        "ollama",
		RuntimeVersion: "0.32.14",
		Model:          "qwen2.5:0.5b",
		ModelID:        "a8b0c5157701",
	}

	if err := ApplyKJAtlasGroupingResult(input); err != nil {
		t.Fatalf("ApplyKJAtlasGroupingResult() error = %v", err)
	}

	provenance, found, err := store.Find(input.ProvenanceRef)
	if err != nil || !found {
		t.Fatalf("provenance not stored: found=%v err=%v", found, err)
	}
	var payload provenancePayload
	if err := json.Unmarshal(provenance.EnvelopeRecord.Payload, &payload); err != nil {
		t.Fatalf("decode provenance: %v", err)
	}
	if payload.Execution == nil {
		t.Fatal("execution identity was not retained in provenance")
	}
	if !reflect.DeepEqual(*payload.Execution, input.Execution) {
		t.Fatalf("execution identity = %#v, want %#v", *payload.Execution, input.Execution)
	}
}

func TestInvalidExecutionIdentityDoesNotMutateCanonicalState(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	input := referenceInput(store, sampleGroupingResult)
	input.Execution = ExecutionIdentity{RuntimeVersion: "0.32.14"}

	if err := ApplyKJAtlasGroupingResult(input); err == nil {
		t.Fatal("ApplyKJAtlasGroupingResult() succeeded without an execution profile")
	}
	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	if before != after {
		t.Fatalf("invalid execution identity mutated canonical state: before=%s after=%s", before, after)
	}
}

func TestInvalidKJAtlasResultDoesNotMutateCanonicalState(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	input := referenceInput(store, []byte(`{"excludedCardIds":[],"truncated":false}`))

	if err := ApplyKJAtlasGroupingResult(input); err == nil {
		t.Fatal("ApplyKJAtlasGroupingResult() succeeded for a result without groups")
	}
	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	if before != after {
		t.Fatalf("invalid external result mutated canonical state: before=%s after=%s", before, after)
	}
}

func TestDuplicateTargetDoesNotPartiallyApplyExternalMethodResult(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, sampleGroupingResult)
	logical := input.OutputRef
	if err := store.Add(semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{
			Kind:       logical.Kind,
			LogicalRef: &logical,
			Payload:    []byte(`{"existing":true}`),
		},
		Status: semanticruntime.RecordNotVerified,
	}); err != nil {
		t.Fatalf("precondition store.Add() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}

	if err := ApplyKJAtlasGroupingResult(input); err == nil {
		t.Fatal("ApplyKJAtlasGroupingResult() succeeded with a duplicate output ref")
	}
	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	if before != after {
		t.Fatalf("duplicate target partially mutated canonical state: before=%s after=%s", before, after)
	}
	if _, found, _ := store.Find(input.ApplicationRef); found {
		t.Fatal("method application was partially recorded after duplicate target failure")
	}
	if _, found, _ := store.Find(input.ProvenanceRef); found {
		t.Fatal("provenance was partially recorded after duplicate target failure")
	}
}

func TestLiveKJAtlasMethodExecution(t *testing.T) {
	if os.Getenv("SEI_E3B_METHOD_LIVE") != "1" {
		t.Skip("live KJ Atlas process probe is enabled only by the dedicated E3b workflow")
	}
	path := os.Getenv("SEI_E3B_METHOD_RESULT")
	if path == "" {
		t.Fatal("SEI_E3B_METHOD_RESULT is required")
	}
	commit := os.Getenv("SEI_E3B_METHOD_SOURCE_COMMIT")
	if commit != pinnedKJAtlasCommit {
		t.Fatalf("KJ Atlas source commit = %q, want pinned %q", commit, pinnedKJAtlasCommit)
	}
	realizationID := os.Getenv("SEI_E3B_METHOD_REALIZATION_ID")
	if realizationID == "" {
		t.Fatal("SEI_E3B_METHOD_REALIZATION_ID is required")
	}
	executionProfile := os.Getenv("SEI_E3B_METHOD_EXECUTION_PROFILE")
	if executionProfile == "" {
		t.Fatal("SEI_E3B_METHOD_EXECUTION_PROFILE is required")
	}
	result, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read live KJ Atlas result: %v", err)
	}

	parsed, err := ParseKJAtlasGroupingResult(result)
	if err != nil {
		t.Fatalf("ParseKJAtlasGroupingResult(live) error = %v\nresult=%s", err, result)
	}
	if len(parsed.Groups) == 0 {
		t.Fatalf("live KJ Atlas result has no grouping candidates: %s", result)
	}

	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, result)
	input.Source.Commit = commit
	input.Source.EntryPoint = "POST /ai/suggest-card-groups"
	input.RealizationRef = logical("method-realization", realizationID)
	input.Execution = ExecutionIdentity{
		Profile:        executionProfile,
		Runtime:        os.Getenv("SEI_E3B_METHOD_RUNTIME"),
		RuntimeVersion: os.Getenv("SEI_E3B_METHOD_RUNTIME_VERSION"),
		Model:          os.Getenv("SEI_E3B_METHOD_MODEL"),
		ModelID:        os.Getenv("SEI_E3B_METHOD_MODEL_ID"),
	}
	input.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-LIVE")
	input.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-LIVE")
	input.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-LIVE")
	if err := ApplyKJAtlasGroupingResult(input); err != nil {
		t.Fatalf("ApplyKJAtlasGroupingResult(live) error = %v", err)
	}

	application, found, err := store.Find(input.ApplicationRef)
	if err != nil || !found || application.CognitiveMethod == nil || application.CognitiveMethod.MethodApplication == nil {
		t.Fatalf("live method application not reconstructed: found=%v err=%v record=%#v", found, err, application)
	}
	app := application.CognitiveMethod.MethodApplication
	if app.RealizationRef == nil {
		t.Fatal("live method application lost realization_ref")
	}
	actualRealization, ok := app.RealizationRef.LogicalIdentity()
	if !ok || actualRealization != input.RealizationRef {
		t.Fatalf("live realization_ref = %#v, want %#v", actualRealization, input.RealizationRef)
	}
	if _, found, _ := store.Find(input.OutputRef); !found {
		t.Fatal("live external method output was not retained")
	}
	provenance, found, err := store.Find(input.ProvenanceRef)
	if err != nil || !found {
		t.Fatalf("live external method provenance was not retained: found=%v err=%v", found, err)
	}
	var payload provenancePayload
	if err := json.Unmarshal(provenance.EnvelopeRecord.Payload, &payload); err != nil {
		t.Fatalf("decode live provenance: %v", err)
	}
	if payload.Execution == nil || !reflect.DeepEqual(*payload.Execution, input.Execution) {
		t.Fatalf("live execution identity = %#v, want %#v", payload.Execution, input.Execution)
	}
}

func referenceInput(store *interactionprobe.CanonicalStore, result []byte) ApplyGroupingInput {
	return ApplyGroupingInput{
		Store:          store,
		Source:         SourceIdentity{Repository: "hat47x/kj-atlas", Commit: pinnedKJAtlasCommit, EntryPoint: "POST /ai/suggest-card-groups"},
		Execution:      ExecutionIdentity{Profile: "reference-deterministic-stub", Model: "mock"},
		MethodRef:      logical("method", "M-KJ-ATLAS-GROUPING"),
		RealizationRef: logical("method-realization", "MR-KJ-ATLAS-REFERENCE"),
		ApplicationRef: logical("method-application", "MA-KJ-ATLAS-001"),
		OutputRef:      logical("cognitive-method-output", "MO-KJ-ATLAS-001"),
		ProvenanceRef:  logical("provenance", "PROV-KJ-ATLAS-001"),
		ContextRefs:    []semanticruntime.LogicalReference{logical("inquiry", "I-KJ-ATLAS")},
		InputRefs:      []semanticruntime.LogicalReference{logical("observation", "CARD-REMOTE"), logical("observation", "CARD-OFFICE")},
		AppliedAt:      "2026-09-02T00:00:00Z",
		ResultJSON:     result,
	}
}

func logical(kind, id string) semanticruntime.LogicalReference {
	return semanticruntime.LogicalReference{Kind: kind, ID: id}
}

func sameJSONMeaning(left, right []byte) bool {
	var leftValue any
	var rightValue any
	if err := json.Unmarshal(left, &leftValue); err != nil {
		return false
	}
	if err := json.Unmarshal(right, &rightValue); err != nil {
		return false
	}
	return reflect.DeepEqual(leftValue, rightValue)
}
