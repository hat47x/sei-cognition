package livemethodintegration

import (
	"encoding/json"
	"os"
	"reflect"
	"testing"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

type modelCallEvidence struct {
	Model           string `json:"model"`
	PromptSHA256    string `json:"prompt_sha256"`
	OllamaDone      bool   `json:"ollama_done"`
	PromptEvalCount int    `json:"prompt_eval_count"`
	EvalCount       int    `json:"eval_count"`
}

func TestExecutionIdentityIsPreservedInOpaqueProvenance(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, sampleGroupingResult)
	input.RealizationRef = logical("method-realization", "MR-KJ-ATLAS-QWEN25-05B")
	input.Execution = &ExecutionIdentity{
		RuntimeName:     "ollama",
		RuntimeVersion:  "0.32.14",
		ModelTag:        "qwen2.5:0.5b",
		ModelArtifactID: "a8b0c5157701",
		PromptSHA256:    "cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33",
	}

	if err := ApplyKJAtlasGroupingResult(input); err != nil {
		t.Fatalf("ApplyKJAtlasGroupingResult() error = %v", err)
	}

	payload := readProvenancePayload(t, store, input.ProvenanceRef)
	if payload.Execution == nil {
		t.Fatal("execution provenance was not retained")
	}
	if !reflect.DeepEqual(*payload.Execution, *input.Execution) {
		t.Fatalf("execution provenance = %#v, want %#v", payload.Execution, input.Execution)
	}
}

func TestInvalidExecutionIdentityDoesNotMutateCanonicalState(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, sampleGroupingResult)
	input.Execution = &ExecutionIdentity{
		RuntimeName:     "ollama",
		RuntimeVersion:  "0.32.14",
		ModelTag:        "qwen2.5:0.5b",
		ModelArtifactID: "a8b0c5157701",
		PromptSHA256:    "not-a-sha256",
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}

	if err := ApplyKJAtlasGroupingResult(input); err == nil {
		t.Fatal("ApplyKJAtlasGroupingResult() succeeded with an invalid prompt digest")
	}
	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	if before != after {
		t.Fatalf("invalid execution identity mutated canonical state: before=%s after=%s", before, after)
	}
}

func TestLiveKJAtlasRealizationVersionExchange(t *testing.T) {
	if os.Getenv("SOZA_E3B_REALIZATION_HISTORY_LIVE") != "1" {
		t.Skip("realization version exchange probe is enabled only by the dedicated E3b workflow")
	}

	resultA := readRequiredFile(t, "SOZA_E3B_METHOD_RESULT_A")
	resultB := readRequiredFile(t, "SOZA_E3B_METHOD_RESULT_B")
	evidenceA := readModelEvidence(t, os.Getenv("SOZA_E3B_MODEL_EVIDENCE_A"))
	evidenceB := readModelEvidence(t, os.Getenv("SOZA_E3B_MODEL_EVIDENCE_B"))

	if evidenceA.Model == evidenceB.Model {
		t.Fatalf("model exchange probe used the same model twice: %q", evidenceA.Model)
	}
	if evidenceA.PromptSHA256 != evidenceB.PromptSHA256 {
		t.Fatalf("same Method input produced different prompt digests: A=%s B=%s", evidenceA.PromptSHA256, evidenceB.PromptSHA256)
	}
	for label, evidence := range map[string]modelCallEvidence{"A": evidenceA, "B": evidenceB} {
		if !evidence.OllamaDone || evidence.PromptEvalCount <= 0 || evidence.EvalCount <= 0 {
			t.Fatalf("model %s did not show actual inference: %#v", label, evidence)
		}
	}

	if _, err := ParseKJAtlasGroupingResult(resultA); err != nil {
		t.Fatalf("result A was not accepted by the KJ Atlas response boundary: %v", err)
	}
	if _, err := ParseKJAtlasGroupingResult(resultB); err != nil {
		t.Fatalf("result B was not accepted by the KJ Atlas response boundary: %v", err)
	}

	runtimeVersion := requiredEnv(t, "SOZA_E3B_RUNTIME_VERSION")
	artifactA := requiredEnv(t, "SOZA_E3B_MODEL_ARTIFACT_ID_A")
	artifactB := requiredEnv(t, "SOZA_E3B_MODEL_ARTIFACT_ID_B")
	if artifactA == artifactB {
		t.Fatalf("model artifact identities are equal: %s", artifactA)
	}

	store := interactionprobe.NewCanonicalStore()
	inputA := referenceInput(store, resultA)
	inputA.RealizationRef = logical("method-realization", "MR-KJ-ATLAS-QWEN25-05B")
	inputA.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-QWEN25-05B")
	inputA.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-QWEN25-05B")
	inputA.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-QWEN25-05B")
	inputA.AppliedAt = "2026-09-02T12:00:00Z"
	inputA.Execution = &ExecutionIdentity{
		RuntimeName:     "ollama",
		RuntimeVersion:  runtimeVersion,
		ModelTag:        evidenceA.Model,
		ModelArtifactID: artifactA,
		PromptSHA256:    evidenceA.PromptSHA256,
	}

	if err := ApplyKJAtlasGroupingResult(inputA); err != nil {
		t.Fatalf("apply realization A: %v", err)
	}

	applicationABefore := readMethodApplication(t, store, inputA.ApplicationRef)
	provenanceABefore := append([]byte(nil), readRecordPayload(t, store, inputA.ProvenanceRef)...)
	outputABefore := append([]byte(nil), readRecordPayload(t, store, inputA.OutputRef)...)

	inputB := referenceInput(store, resultB)
	inputB.RealizationRef = logical("method-realization", "MR-KJ-ATLAS-QWEN25-15B")
	inputB.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-QWEN25-15B")
	inputB.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-QWEN25-15B")
	inputB.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-QWEN25-15B")
	inputB.AppliedAt = "2026-09-02T12:01:00Z"
	inputB.Execution = &ExecutionIdentity{
		RuntimeName:     "ollama",
		RuntimeVersion:  runtimeVersion,
		ModelTag:        evidenceB.Model,
		ModelArtifactID: artifactB,
		PromptSHA256:    evidenceB.PromptSHA256,
	}

	if err := ApplyKJAtlasGroupingResult(inputB); err != nil {
		t.Fatalf("apply realization B: %v", err)
	}

	applicationAAfter := readMethodApplication(t, store, inputA.ApplicationRef)
	provenanceAAfter := readRecordPayload(t, store, inputA.ProvenanceRef)
	outputAAfter := readRecordPayload(t, store, inputA.OutputRef)
	applicationB := readMethodApplication(t, store, inputB.ApplicationRef)

	if !reflect.DeepEqual(applicationABefore, applicationAAfter) {
		t.Fatalf("historical application A changed after adding B\nbefore=%#v\nafter=%#v", applicationABefore, applicationAAfter)
	}
	if !reflect.DeepEqual(provenanceABefore, provenanceAAfter) {
		t.Fatalf("historical provenance A changed after adding B\nbefore=%s\nafter=%s", provenanceABefore, provenanceAAfter)
	}
	if !reflect.DeepEqual(outputABefore, outputAAfter) {
		t.Fatalf("historical output A changed after adding B\nbefore=%s\nafter=%s", outputABefore, outputAAfter)
	}

	methodA, ok := applicationAAfter.MethodRef.LogicalIdentity()
	if !ok {
		t.Fatal("application A lost Method Reference")
	}
	methodB, ok := applicationB.MethodRef.LogicalIdentity()
	if !ok || methodA != methodB {
		t.Fatalf("model exchange changed Method identity: A=%#v B=%#v", methodA, methodB)
	}
	realizationA := mustLogicalReference(t, applicationAAfter.RealizationRef)
	realizationB := mustLogicalReference(t, applicationB.RealizationRef)
	if realizationA == realizationB {
		t.Fatalf("different model executions collapsed into one Realization: %#v", realizationA)
	}

	provA := readProvenancePayload(t, store, inputA.ProvenanceRef)
	provB := readProvenancePayload(t, store, inputB.ProvenanceRef)
	if provA.Execution == nil || provB.Execution == nil {
		t.Fatalf("execution provenance is missing: A=%#v B=%#v", provA, provB)
	}
	if provA.Execution.ModelArtifactID != artifactA || provB.Execution.ModelArtifactID != artifactB {
		t.Fatalf("model artifact identity was rebound: A=%#v B=%#v", provA.Execution, provB.Execution)
	}

	records, err := store.Records()
	if err != nil {
		t.Fatalf("Records() error = %v", err)
	}
	for _, record := range records {
		if record.Decision != nil {
			t.Fatalf("model exchange promoted Method output to Decision Memory: %#v", record.Decision)
		}
	}
}

func readModelEvidence(t *testing.T, path string) modelCallEvidence {
	t.Helper()
	if path == "" {
		t.Fatal("model evidence path is required")
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read model evidence %s: %v", path, err)
	}
	var evidence modelCallEvidence
	if err := json.Unmarshal(data, &evidence); err != nil {
		t.Fatalf("parse model evidence %s: %v", path, err)
	}
	return evidence
}

func readRequiredFile(t *testing.T, envName string) []byte {
	t.Helper()
	path := requiredEnv(t, envName)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s=%s: %v", envName, path, err)
	}
	return data
}

func requiredEnv(t *testing.T, name string) string {
	t.Helper()
	value := os.Getenv(name)
	if value == "" {
		t.Fatalf("%s is required", name)
	}
	return value
}

func readMethodApplication(t *testing.T, store *interactionprobe.CanonicalStore, ref semanticruntime.LogicalReference) semanticruntime.MethodApplication {
	t.Helper()
	record, found, err := store.Find(ref)
	if err != nil || !found || record.CognitiveMethod == nil || record.CognitiveMethod.MethodApplication == nil {
		t.Fatalf("method application %s/%s not found: found=%v err=%v record=%#v", ref.Kind, ref.ID, found, err, record)
	}
	return *record.CognitiveMethod.MethodApplication
}

func readRecordPayload(t *testing.T, store *interactionprobe.CanonicalStore, ref semanticruntime.LogicalReference) []byte {
	t.Helper()
	record, found, err := store.Find(ref)
	if err != nil || !found {
		t.Fatalf("record %s/%s not found: found=%v err=%v", ref.Kind, ref.ID, found, err)
	}
	return append([]byte(nil), record.EnvelopeRecord.Payload...)
}

func readProvenancePayload(t *testing.T, store *interactionprobe.CanonicalStore, ref semanticruntime.LogicalReference) provenancePayload {
	t.Helper()
	data := readRecordPayload(t, store, ref)
	var payload provenancePayload
	if err := json.Unmarshal(data, &payload); err != nil {
		t.Fatalf("parse provenance %s/%s: %v", ref.Kind, ref.ID, err)
	}
	return payload
}

func mustLogicalReference(t *testing.T, ref *semanticruntime.Reference) semanticruntime.LogicalReference {
	t.Helper()
	if ref == nil {
		t.Fatal("realization_ref is missing")
	}
	logicalRef, ok := ref.LogicalIdentity()
	if !ok {
		t.Fatalf("reference has no logical identity: %#v", ref)
	}
	return logicalRef
}
