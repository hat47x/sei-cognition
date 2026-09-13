package livemethodintegration

import (
	"encoding/json"
	"os"
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/interactionprobe"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

type modelArtifactExchangeEvidence struct {
	Model           string `json:"model"`
	PromptSHA256    string `json:"prompt_sha256"`
	OllamaDone      bool   `json:"ollama_done"`
	PromptEvalCount int    `json:"prompt_eval_count"`
	EvalCount       int    `json:"eval_count"`
}

func TestLiveKJAtlasActualModelArtifactExchangePreservesHistoricalApplication(t *testing.T) {
	if os.Getenv("SEI_E3B_MODEL_EXCHANGE_LIVE") != "1" {
		t.Skip("actual model artifact exchange probe is enabled only by the dedicated E3b workflow")
	}

	resultA := readExchangeFile(t, "SEI_E3B_MODEL_EXCHANGE_RESULT_A")
	resultB := readExchangeFile(t, "SEI_E3B_MODEL_EXCHANGE_RESULT_B")
	evidenceA := readExchangeModelEvidence(t, "SEI_E3B_MODEL_EXCHANGE_EVIDENCE_A")
	evidenceB := readExchangeModelEvidence(t, "SEI_E3B_MODEL_EXCHANGE_EVIDENCE_B")

	if evidenceA.Model == evidenceB.Model {
		t.Fatalf("model artifact exchange used the same model twice: %q", evidenceA.Model)
	}
	if evidenceA.PromptSHA256 == "" || evidenceA.PromptSHA256 != evidenceB.PromptSHA256 {
		t.Fatalf("the two executions did not use the same model prompt: A=%q B=%q", evidenceA.PromptSHA256, evidenceB.PromptSHA256)
	}
	for label, evidence := range map[string]modelArtifactExchangeEvidence{"A": evidenceA, "B": evidenceB} {
		if !evidence.OllamaDone || evidence.PromptEvalCount <= 0 || evidence.EvalCount <= 0 {
			t.Fatalf("model %s did not show actual inference: %#v", label, evidence)
		}
	}

	if _, err := ParseKJAtlasGroupingResult(resultA); err != nil {
		t.Fatalf("result A was rejected by the KJ Atlas response boundary: %v", err)
	}
	if _, err := ParseKJAtlasGroupingResult(resultB); err != nil {
		t.Fatalf("result B was rejected by the KJ Atlas response boundary: %v", err)
	}

	runtimeVersion := exchangeRequiredEnv(t, "SEI_E3B_MODEL_EXCHANGE_RUNTIME_VERSION")
	modelIDA := exchangeRequiredEnv(t, "SEI_E3B_MODEL_EXCHANGE_MODEL_ID_A")
	modelIDB := exchangeRequiredEnv(t, "SEI_E3B_MODEL_EXCHANGE_MODEL_ID_B")
	if modelIDA == modelIDB {
		t.Fatalf("observed model digests are equal: %s", modelIDA)
	}

	store := interactionprobe.NewCanonicalStore()
	inputA := referenceInput(store, resultA)
	inputA.RealizationRef = logical("method-realization", "MR-KJ-ATLAS-M1B-QWEN25-05B")
	inputA.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-MODEL-EXCHANGE-A")
	inputA.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-MODEL-EXCHANGE-A")
	inputA.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-MODEL-EXCHANGE-A")
	inputA.Execution = ExecutionIdentity{
		Profile:        "ollama-model-backed",
		Runtime:        "ollama",
		RuntimeVersion: runtimeVersion,
		Model:          evidenceA.Model,
		ModelID:        modelIDA,
	}
	inputA.AppliedAt = "2026-09-02T12:00:00Z"

	if err := ApplyKJAtlasGroupingResult(inputA); err != nil {
		t.Fatalf("apply model artifact A: %v", err)
	}

	applicationABefore := exchangeMethodApplication(t, store, inputA.ApplicationRef)
	provenanceABefore := exchangeRecordPayload(t, store, inputA.ProvenanceRef)
	outputABefore := exchangeRecordPayload(t, store, inputA.OutputRef)

	inputB := referenceInput(store, resultB)
	inputB.RealizationRef = logical("method-realization", "MR-KJ-ATLAS-M1B-QWEN25-15B")
	inputB.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-MODEL-EXCHANGE-B")
	inputB.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-MODEL-EXCHANGE-B")
	inputB.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-MODEL-EXCHANGE-B")
	inputB.Execution = ExecutionIdentity{
		Profile:        "ollama-model-backed",
		Runtime:        "ollama",
		RuntimeVersion: runtimeVersion,
		Model:          evidenceB.Model,
		ModelID:        modelIDB,
	}
	inputB.AppliedAt = "2026-09-02T12:01:00Z"

	if err := ApplyKJAtlasGroupingResult(inputB); err != nil {
		t.Fatalf("apply model artifact B: %v", err)
	}

	applicationAAfter := exchangeMethodApplication(t, store, inputA.ApplicationRef)
	provenanceAAfter := exchangeRecordPayload(t, store, inputA.ProvenanceRef)
	outputAAfter := exchangeRecordPayload(t, store, inputA.OutputRef)
	applicationB := exchangeMethodApplication(t, store, inputB.ApplicationRef)

	if !reflect.DeepEqual(applicationABefore, applicationAAfter) {
		t.Fatalf("historical Application A changed after B was added\nbefore=%#v\nafter=%#v", applicationABefore, applicationAAfter)
	}
	if !reflect.DeepEqual(provenanceABefore, provenanceAAfter) {
		t.Fatalf("historical Provenance A changed after B was added\nbefore=%s\nafter=%s", provenanceABefore, provenanceAAfter)
	}
	if !reflect.DeepEqual(outputABefore, outputAAfter) {
		t.Fatalf("historical output A changed after B was added\nbefore=%s\nafter=%s", outputABefore, outputAAfter)
	}

	methodA, ok := applicationAAfter.MethodRef.LogicalIdentity()
	if !ok {
		t.Fatal("Application A lost its Method Reference")
	}
	methodB, ok := applicationB.MethodRef.LogicalIdentity()
	if !ok || methodA != methodB {
		t.Fatalf("model artifact exchange changed Method identity: A=%#v B=%#v", methodA, methodB)
	}

	realizationA := exchangeLogicalReference(t, applicationAAfter.RealizationRef)
	realizationB := exchangeLogicalReference(t, applicationB.RealizationRef)
	if realizationA == realizationB {
		t.Fatalf("two model artifact executions collapsed into one Realization: %#v", realizationA)
	}

	provenanceA := exchangeProvenance(t, store, inputA.ProvenanceRef)
	provenanceB := exchangeProvenance(t, store, inputB.ProvenanceRef)
	if provenanceA.Execution == nil || provenanceB.Execution == nil {
		t.Fatalf("execution identity is missing: A=%#v B=%#v", provenanceA, provenanceB)
	}
	if provenanceA.Execution.ModelID != modelIDA || provenanceB.Execution.ModelID != modelIDB {
		t.Fatalf("model identity was rebound: A=%#v B=%#v", provenanceA.Execution, provenanceB.Execution)
	}
	if provenanceA.Execution.RuntimeVersion != runtimeVersion || provenanceB.Execution.RuntimeVersion != runtimeVersion {
		t.Fatalf("runtime version changed unexpectedly: A=%#v B=%#v", provenanceA.Execution, provenanceB.Execution)
	}

	records, err := store.Records()
	if err != nil {
		t.Fatalf("Records() error = %v", err)
	}
	for _, record := range records {
		if record.Decision != nil {
			t.Fatalf("model artifact exchange promoted Method output to Decision Memory: %#v", record.Decision)
		}
	}
}

func readExchangeModelEvidence(t *testing.T, envName string) modelArtifactExchangeEvidence {
	t.Helper()
	data := readExchangeFile(t, envName)
	var evidence modelArtifactExchangeEvidence
	if err := json.Unmarshal(data, &evidence); err != nil {
		t.Fatalf("parse %s: %v", envName, err)
	}
	return evidence
}

func readExchangeFile(t *testing.T, envName string) []byte {
	t.Helper()
	path := exchangeRequiredEnv(t, envName)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s=%s: %v", envName, path, err)
	}
	return data
}

func exchangeRequiredEnv(t *testing.T, name string) string {
	t.Helper()
	value := os.Getenv(name)
	if value == "" {
		t.Fatalf("%s is required", name)
	}
	return value
}

func exchangeMethodApplication(t *testing.T, store *interactionprobe.CanonicalStore, ref semanticruntime.LogicalReference) semanticruntime.MethodApplication {
	t.Helper()
	record, found, err := store.Find(ref)
	if err != nil || !found || record.CognitiveMethod == nil || record.CognitiveMethod.MethodApplication == nil {
		t.Fatalf("Method Application %s/%s not found: found=%v err=%v record=%#v", ref.Kind, ref.ID, found, err, record)
	}
	return *record.CognitiveMethod.MethodApplication
}

func exchangeRecordPayload(t *testing.T, store *interactionprobe.CanonicalStore, ref semanticruntime.LogicalReference) []byte {
	t.Helper()
	record, found, err := store.Find(ref)
	if err != nil || !found {
		t.Fatalf("record %s/%s not found: found=%v err=%v", ref.Kind, ref.ID, found, err)
	}
	return append([]byte(nil), record.EnvelopeRecord.Payload...)
}

func exchangeProvenance(t *testing.T, store *interactionprobe.CanonicalStore, ref semanticruntime.LogicalReference) provenancePayload {
	t.Helper()
	data := exchangeRecordPayload(t, store, ref)
	var payload provenancePayload
	if err := json.Unmarshal(data, &payload); err != nil {
		t.Fatalf("parse Provenance %s/%s: %v", ref.Kind, ref.ID, err)
	}
	return payload
}

func exchangeLogicalReference(t *testing.T, ref *semanticruntime.Reference) semanticruntime.LogicalReference {
	t.Helper()
	if ref == nil {
		t.Fatal("Realization Reference is missing")
	}
	logicalRef, ok := ref.LogicalIdentity()
	if !ok {
		t.Fatalf("Reference has no logical identity: %#v", ref)
	}
	return logicalRef
}
