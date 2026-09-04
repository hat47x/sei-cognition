package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"reflect"
	"strings"
	"testing"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const (
	runtimeExchangeRawProfile = "soza.raw-bytes+sha256"
	runtimeExchangeVersionA   = "0.32.13"
	runtimeExchangeVersionB   = "0.32.14"
	runtimeExchangeArtifactA  = "0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1"
	runtimeExchangeArtifactB  = "c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"
)

type runtimeExchangeRealizationRevision struct {
	Reference semanticruntime.Reference
	Record    semanticruntime.InterchangeRecord
}

// TestLiveKJAtlasRuntimeVersionExchangePreservesHistoricalApplicationは、
// model artifactを固定したままruntime versionだけを交換したとき、同じlogical
// Method Realizationの各revisionをExact Bindingで区別し、先に記録した
// Method Applicationの来歴が後続実行によって書き換わらないことを検査します。
//
// このtestはrepository-local harness等の実行器からactual Evidence pathと
// SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1を明示した場合だけ有効化します。通常のunit testでは
// actual runtimeを必須にせず、runtime名やversionをUniversal Contractへ昇格させません。
func TestLiveKJAtlasRuntimeVersionExchangePreservesHistoricalApplication(t *testing.T) {
	if os.Getenv("SOZA_E3B_RUNTIME_EXCHANGE_LIVE") != "1" {
		t.Skip("actual runtime version exchange probeは明示的なlive実行時だけ有効です")
	}

	resultA := readExchangeFile(t, "SOZA_E3B_RUNTIME_EXCHANGE_RESULT_A")
	resultB := readExchangeFile(t, "SOZA_E3B_RUNTIME_EXCHANGE_RESULT_B")
	evidenceA := readExchangeModelEvidence(t, "SOZA_E3B_RUNTIME_EXCHANGE_EVIDENCE_A")
	evidenceB := readExchangeModelEvidence(t, "SOZA_E3B_RUNTIME_EXCHANGE_EVIDENCE_B")

	if evidenceA.Model == "" || evidenceA.Model != evidenceB.Model {
		t.Fatalf("runtime exchange did not keep the same model: A=%q B=%q", evidenceA.Model, evidenceB.Model)
	}
	if evidenceA.PromptSHA256 == "" || evidenceA.PromptSHA256 != evidenceB.PromptSHA256 {
		t.Fatalf("runtime exchange did not keep the same model prompt: A=%q B=%q", evidenceA.PromptSHA256, evidenceB.PromptSHA256)
	}
	for label, evidence := range map[string]modelArtifactExchangeEvidence{"A": evidenceA, "B": evidenceB} {
		if !evidence.OllamaDone || evidence.PromptEvalCount <= 0 || evidence.EvalCount <= 0 {
			t.Fatalf("runtime %s did not show actual inference: %#v", label, evidence)
		}
	}

	if _, err := ParseKJAtlasGroupingResult(resultA); err != nil {
		t.Fatalf("result A was rejected by the KJ Atlas response boundary: %v", err)
	}
	if _, err := ParseKJAtlasGroupingResult(resultB); err != nil {
		t.Fatalf("result B was rejected by the KJ Atlas response boundary: %v", err)
	}

	runtimeVersionA := exchangeRequiredEnv(t, "SOZA_E3B_RUNTIME_EXCHANGE_RUNTIME_VERSION_A")
	runtimeVersionB := exchangeRequiredEnv(t, "SOZA_E3B_RUNTIME_EXCHANGE_RUNTIME_VERSION_B")
	if runtimeVersionA != runtimeExchangeVersionA || runtimeVersionB != runtimeExchangeVersionB {
		t.Fatalf("runtime exchange versions changed: A=%q B=%q want A=%q B=%q", runtimeVersionA, runtimeVersionB, runtimeExchangeVersionA, runtimeExchangeVersionB)
	}

	modelIDA := exchangeRequiredEnv(t, "SOZA_E3B_RUNTIME_EXCHANGE_MODEL_ID_A")
	modelIDB := exchangeRequiredEnv(t, "SOZA_E3B_RUNTIME_EXCHANGE_MODEL_ID_B")
	if modelIDA != modelIDB {
		t.Fatalf("runtime exchange changed the model artifact: A=%s B=%s", modelIDA, modelIDB)
	}

	realizationLogical := logical("method-realization", "MR-KJ-ATLAS-RUNTIME-EXCHANGE")
	revisionA := runtimeExchangeRealizationRevisionRecord(
		t,
		"record-runtime-exchange-realization-a",
		realizationLogical,
		runtimeVersionA,
		runtimeExchangeArtifactA,
		evidenceA.Model,
		modelIDA,
	)
	revisionB := runtimeExchangeRealizationRevisionRecord(
		t,
		"record-runtime-exchange-realization-b",
		realizationLogical,
		runtimeVersionB,
		runtimeExchangeArtifactB,
		evidenceB.Model,
		modelIDB,
	)

	bindingA, ok := revisionA.Reference.ExactBinding()
	if !ok {
		t.Fatal("runtime A realization reference is not exact")
	}
	bindingB, ok := revisionB.Reference.ExactBinding()
	if !ok {
		t.Fatal("runtime B realization reference is not exact")
	}
	if bindingA.LogicalRef != bindingB.LogicalRef || bindingA.LogicalRef != realizationLogical {
		t.Fatalf("runtime revisions changed realization logical identity: A=%#v B=%#v", bindingA.LogicalRef, bindingB.LogicalRef)
	}
	if bindingA.ContentDigest == bindingB.ContentDigest {
		t.Fatal("different runtime revisions unexpectedly produced the same realization exact binding")
	}

	store := interactionprobe.NewCanonicalStore()
	inputA := referenceInput(store, resultA)
	inputA.RealizationRef = realizationLogical
	inputA.RealizationReference = &revisionA.Reference
	inputA.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-RUNTIME-EXCHANGE-A")
	inputA.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-RUNTIME-EXCHANGE-A")
	inputA.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-RUNTIME-EXCHANGE-A")
	inputA.Execution = ExecutionIdentity{
		Profile:        "ollama-runtime-version-exchange",
		Runtime:        "ollama",
		RuntimeVersion: runtimeVersionA,
		Model:          evidenceA.Model,
		ModelID:        modelIDA,
	}
	inputA.AppliedAt = "2026-09-02T14:00:00Z"

	if err := ApplyKJAtlasGroupingResult(inputA); err != nil {
		t.Fatalf("apply runtime A result: %v", err)
	}

	applicationABefore := exchangeMethodApplication(t, store, inputA.ApplicationRef)
	provenanceABefore := exchangeRecordPayload(t, store, inputA.ProvenanceRef)
	outputABefore := exchangeRecordPayload(t, store, inputA.OutputRef)

	if applicationABefore.RealizationRef == nil || !reflect.DeepEqual(*applicationABefore.RealizationRef, revisionA.Reference) {
		t.Fatalf("Application A lost its exact realization revision: got=%#v want=%#v", applicationABefore.RealizationRef, revisionA.Reference)
	}

	inputB := referenceInput(store, resultB)
	inputB.RealizationRef = realizationLogical
	inputB.RealizationReference = &revisionB.Reference
	inputB.ApplicationRef = logical("method-application", "MA-KJ-ATLAS-RUNTIME-EXCHANGE-B")
	inputB.OutputRef = logical("cognitive-method-output", "MO-KJ-ATLAS-RUNTIME-EXCHANGE-B")
	inputB.ProvenanceRef = logical("provenance", "PROV-KJ-ATLAS-RUNTIME-EXCHANGE-B")
	inputB.Execution = ExecutionIdentity{
		Profile:        "ollama-runtime-version-exchange",
		Runtime:        "ollama",
		RuntimeVersion: runtimeVersionB,
		Model:          evidenceB.Model,
		ModelID:        modelIDB,
	}
	inputB.AppliedAt = "2026-09-02T14:01:00Z"

	if err := ApplyKJAtlasGroupingResult(inputB); err != nil {
		t.Fatalf("apply runtime B result: %v", err)
	}

	applicationAAfter := exchangeMethodApplication(t, store, inputA.ApplicationRef)
	provenanceAAfter := exchangeRecordPayload(t, store, inputA.ProvenanceRef)
	outputAAfter := exchangeRecordPayload(t, store, inputA.OutputRef)
	applicationB := exchangeMethodApplication(t, store, inputB.ApplicationRef)

	if !reflect.DeepEqual(applicationABefore, applicationAAfter) {
		t.Fatalf("historical Application A changed after runtime B was added\nbefore=%#v\nafter=%#v", applicationABefore, applicationAAfter)
	}
	if !reflect.DeepEqual(provenanceABefore, provenanceAAfter) {
		t.Fatalf("historical Provenance A changed after runtime B was added\nbefore=%s\nafter=%s", provenanceABefore, provenanceAAfter)
	}
	if !reflect.DeepEqual(outputABefore, outputAAfter) {
		t.Fatalf("historical output A changed after runtime B was added\nbefore=%s\nafter=%s", outputABefore, outputAAfter)
	}

	methodA, ok := applicationAAfter.MethodRef.LogicalIdentity()
	if !ok {
		t.Fatal("Application A lost its Method Reference")
	}
	methodB, ok := applicationB.MethodRef.LogicalIdentity()
	if !ok || methodA != methodB {
		t.Fatalf("runtime exchange changed Method identity: A=%#v B=%#v", methodA, methodB)
	}

	if applicationAAfter.RealizationRef == nil || applicationB.RealizationRef == nil {
		t.Fatal("runtime exchange lost realization_ref")
	}
	actualBindingA, ok := applicationAAfter.RealizationRef.ExactBinding()
	if !ok {
		t.Fatal("Application A realization_ref is not exact")
	}
	actualBindingB, ok := applicationB.RealizationRef.ExactBinding()
	if !ok {
		t.Fatal("Application B realization_ref is not exact")
	}
	if actualBindingA.LogicalRef != actualBindingB.LogicalRef || actualBindingA.LogicalRef != realizationLogical {
		t.Fatalf("Applications do not share one logical Realization: A=%#v B=%#v", actualBindingA, actualBindingB)
	}
	if actualBindingA.ContentDigest == actualBindingB.ContentDigest {
		t.Fatal("Applications collapsed two runtime revisions into one exact Realization binding")
	}

	provenanceA := exchangeProvenance(t, store, inputA.ProvenanceRef)
	provenanceB := exchangeProvenance(t, store, inputB.ProvenanceRef)
	if provenanceA.Execution == nil || provenanceB.Execution == nil {
		t.Fatalf("execution identity is missing: A=%#v B=%#v", provenanceA, provenanceB)
	}
	if provenanceA.Execution.RuntimeVersion != runtimeVersionA || provenanceB.Execution.RuntimeVersion != runtimeVersionB {
		t.Fatalf("runtime version was not retained: A=%#v B=%#v", provenanceA.Execution, provenanceB.Execution)
	}
	if provenanceA.Execution.ModelID != modelIDA || provenanceB.Execution.ModelID != modelIDB {
		t.Fatalf("model artifact identity changed: A=%#v B=%#v", provenanceA.Execution, provenanceB.Execution)
	}
	if provenanceA.Execution.ModelID != provenanceB.Execution.ModelID {
		t.Fatalf("runtime exchange did not preserve the same model artifact: A=%#v B=%#v", provenanceA.Execution, provenanceB.Execution)
	}

	runtimeExchangeVerifyPortableHistoricalReconstruction(t, revisionA, revisionB, applicationAAfter, applicationB)

	records, err := store.Records()
	if err != nil {
		t.Fatalf("Records() error = %v", err)
	}
	for _, record := range records {
		if record.Decision != nil {
			t.Fatalf("runtime version exchange promoted Method output to Decision Memory: %#v", record.Decision)
		}
	}
}

func runtimeExchangeRealizationRevisionRecord(
	t *testing.T,
	recordID string,
	realizationLogical semanticruntime.LogicalReference,
	runtimeVersion string,
	runtimeArtifactSHA string,
	model string,
	modelID string,
) runtimeExchangeRealizationRevision {
	t.Helper()

	doc := semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_realization",
		MethodRealization: &semanticruntime.MethodRealization{
			Ref:       realizationLogical,
			MethodRef: logicalReference(logical("method", "M-KJ-ATLAS-GROUPING")),
			Description: fmt.Sprintf(
				"KJ Atlasの固定sourceとOllama %s上の%sでgrouping Methodを実現する。",
				runtimeVersion,
				model,
			),
			ImplementationRefs: []semanticruntime.Reference{
				logicalReference(logical("implementation-artifact", "KJ-ATLAS-SOURCE-4F28C13")),
				logicalReference(logical("implementation-artifact", "OLLAMA-RUNTIME")),
				logicalReference(logical("implementation-artifact", "QWEN25-05B-MODEL")),
			},
			Extensions: map[string]any{
				"source_repository":       "hat47x/kj-atlas",
				"source_commit":           pinnedKJAtlasCommit,
				"entry_point":             "POST /ai/suggest-card-groups",
				"runtime":                 "ollama",
				"runtime_version":         runtimeVersion,
				"runtime_artifact_sha256": runtimeArtifactSHA,
				"model":                   model,
				"model_id":                modelID,
			},
		},
	}
	payload, err := json.Marshal(doc)
	if err != nil {
		t.Fatalf("marshal runtime-specific Method Realization: %v", err)
	}
	binding := runtimeExchangeBinding(realizationLogical, payload)
	reference := runtimeExchangeExactReference(binding)
	logicalCopy := realizationLogical
	bindingCopy := binding

	return runtimeExchangeRealizationRevision{
		Reference: reference,
		Record: semanticruntime.InterchangeRecord{
			RecordID:     recordID,
			Contract:     runtimeExchangeCognitiveMethodIdentity(),
			Kind:         "method_realization",
			LogicalRef:   &logicalCopy,
			ExactBinding: &bindingCopy,
			Payload:      payload,
		},
	}
}

func runtimeExchangeVerifyPortableHistoricalReconstruction(
	t *testing.T,
	revisionA runtimeExchangeRealizationRevision,
	revisionB runtimeExchangeRealizationRevision,
	applicationA semanticruntime.MethodApplication,
	applicationB semanticruntime.MethodApplication,
) {
	t.Helper()

	applicationRecordA := runtimeExchangeApplicationRecord(t, "record-runtime-exchange-application-a", applicationA)
	applicationRecordB := runtimeExchangeApplicationRecord(t, "record-runtime-exchange-application-b", applicationB)

	envelope := semanticruntime.SemanticInterchange{
		Contract: semanticruntime.ContractSemanticInterchange,
		BundleID: "runtime-exchange-historical-reconstruction",
		Records: []semanticruntime.InterchangeRecord{
			revisionA.Record,
			revisionB.Record,
			applicationRecordA,
			applicationRecordB,
		},
	}
	raw, err := json.Marshal(envelope)
	if err != nil {
		t.Fatalf("marshal runtime exchange Semantic Interchange: %v", err)
	}
	bundle, err := semanticruntime.LoadInterchange(raw)
	if err != nil {
		t.Fatalf("portable runtime exchange reconstruction failed: %v", err)
	}
	if len(bundle.Records) != 4 {
		t.Fatalf("portable runtime exchange bundle record count = %d, want 4", len(bundle.Records))
	}

	// negative control: 同じlogical Realizationのcandidateがbundle内に存在する状態で、
	// Application Bのdigestだけを存在しないrevisionへ差し替えると拒否される必要があります。
	tamperedApplication := applicationB
	if tamperedApplication.RealizationRef == nil {
		t.Fatal("Application B lost realization_ref before negative control")
	}
	tamperedReference := *tamperedApplication.RealizationRef
	tamperedReference.ContentDigest = "sha256:" + strings.Repeat("0", 64)
	tamperedApplication.RealizationRef = &tamperedReference
	tamperedRecordB := runtimeExchangeApplicationRecord(t, "record-runtime-exchange-application-b", tamperedApplication)
	tamperedEnvelope := envelope
	tamperedEnvelope.BundleID = "runtime-exchange-historical-reconstruction-invalid"
	tamperedEnvelope.Records = []semanticruntime.InterchangeRecord{
		revisionA.Record,
		revisionB.Record,
		applicationRecordA,
		tamperedRecordB,
	}
	tamperedRaw, err := json.Marshal(tamperedEnvelope)
	if err != nil {
		t.Fatalf("marshal tampered runtime exchange Semantic Interchange: %v", err)
	}
	if _, err := semanticruntime.LoadInterchange(tamperedRaw); err == nil {
		t.Fatal("portable reconstruction accepted a non-existent exact Realization revision")
	}
}

func runtimeExchangeApplicationRecord(t *testing.T, recordID string, application semanticruntime.MethodApplication) semanticruntime.InterchangeRecord {
	t.Helper()

	doc := semanticruntime.CognitiveMethodDocument{
		Contract:          semanticruntime.ContractCognitiveMethod,
		RecordType:        "method_application",
		MethodApplication: &application,
	}
	payload, err := json.Marshal(doc)
	if err != nil {
		t.Fatalf("marshal runtime exchange Method Application: %v", err)
	}
	logicalCopy := application.Ref
	return semanticruntime.InterchangeRecord{
		RecordID:   recordID,
		Contract:   runtimeExchangeCognitiveMethodIdentity(),
		Kind:       "method_application",
		LogicalRef: &logicalCopy,
		Payload:    payload,
	}
}

func runtimeExchangeCognitiveMethodIdentity() semanticruntime.ContractIdentity {
	return semanticruntime.ContractIdentity{
		ContractID: semanticruntime.ContractIDCognitiveMethod,
		Version:    semanticruntime.ContractVersionV1Alpha1,
	}
}

func runtimeExchangeBinding(logical semanticruntime.LogicalReference, payload []byte) semanticruntime.ExactBinding {
	digest := sha256.Sum256(payload)
	return semanticruntime.ExactBinding{
		LogicalRef:    logical,
		ContentDigest: "sha256:" + hex.EncodeToString(digest[:]),
		RepresentationProfile: semanticruntime.RepresentationProfile{
			ProfileID: runtimeExchangeRawProfile,
			Version:   "v1alpha1",
		},
	}
}

func runtimeExchangeExactReference(binding semanticruntime.ExactBinding) semanticruntime.Reference {
	logical := binding.LogicalRef
	profile := binding.RepresentationProfile
	return semanticruntime.Reference{
		LogicalRef:            &logical,
		ContentDigest:         binding.ContentDigest,
		RepresentationProfile: &profile,
	}
}
