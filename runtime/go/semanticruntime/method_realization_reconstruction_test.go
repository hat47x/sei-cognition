package semanticruntime

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"testing"
)

const reconstructionRawProfile = "sei.raw-bytes+sha256"

func TestMethodRealizationVersionHistoricalReconstruction(t *testing.T) {
	methodRef := LogicalReference{Kind: "method", ID: "M-KJ-ATLAS-GROUPING"}
	realizationRef := LogicalReference{Kind: "method-realization", ID: "MR-KJ-ATLAS-GROUPING"}

	sourceRecord, sourceBinding := reconstructionArtifact(
		"implementation-artifact",
		"KJ-ATLAS-SOURCE-4F28C13",
		[]byte(`{"repository":"hat47x/kj-atlas","commit":"4f28c13abe4176503c6fed863383a2d1db2299e9","entry_point":"POST /ai/suggest-card-groups"}`),
	)
	stubRecord, stubBinding := reconstructionArtifact(
		"implementation-artifact",
		"KJ-ATLAS-DETERMINISTIC-MODEL-STUB",
		[]byte(`{"execution":"deterministic-model-stub","source_commit":"4f28c13abe4176503c6fed863383a2d1db2299e9","boundary":"POST /generate"}`),
	)
	modelRecord, modelBinding := reconstructionArtifact(
		"implementation-artifact",
		"KJ-ATLAS-QWEN25-05B-OLLAMA-03214",
		[]byte(`{"execution":"actual-model","runtime":"ollama","runtime_version":"0.32.14","model":"qwen2.5:0.5b","model_id":"a8b0c5157701","boundary":"POST /generate"}`),
	)

	stubRealization, stubRealizationBinding := reconstructionRealization(
		t,
		methodRef,
		realizationRef,
		"KJ Atlasの固定sourceとdeterministic model stubでgrouping Methodを実現する。",
		sourceBinding,
		stubBinding,
	)
	modelRealization, modelRealizationBinding := reconstructionRealization(
		t,
		methodRef,
		realizationRef,
		"KJ Atlasの固定sourceとOllama上のactual modelでgrouping Methodを実現する。",
		sourceBinding,
		modelBinding,
	)

	if stubRealizationBinding.LogicalRef != modelRealizationBinding.LogicalRef {
		t.Fatalf("realization logical identity changed across revisions: stub=%#v model=%#v", stubRealizationBinding.LogicalRef, modelRealizationBinding.LogicalRef)
	}
	if stubRealizationBinding.ContentDigest == modelRealizationBinding.ContentDigest {
		t.Fatal("different realization revisions unexpectedly share the same exact content digest")
	}

	stubApplication := reconstructionApplication(
		LogicalReference{Kind: "method-application", ID: "MA-KJ-ATLAS-M1A"},
		methodRef,
		stubRealizationBinding,
		"M1a deterministic model stub execution",
	)
	modelApplication := reconstructionApplication(
		LogicalReference{Kind: "method-application", ID: "MA-KJ-ATLAS-M1B"},
		methodRef,
		modelRealizationBinding,
		"M1b actual model-backed execution",
	)

	bundle := &Bundle{Records: []RuntimeRecord{
		sourceRecord,
		stubRecord,
		modelRecord,
		stubRealization,
		modelRealization,
		stubApplication,
		modelApplication,
	}}

	if err := validateBundleExactReferences(bundle); err != nil {
		t.Fatalf("versioned Method Realization bundle lost Exact Reference consistency: %v", err)
	}

	stubResolved, err := resolveHistoricalRealization(bundle, *stubApplication.CognitiveMethod.MethodApplication.RealizationRef)
	if err != nil {
		t.Fatalf("resolve M1a realization: %v", err)
	}
	modelResolved, err := resolveHistoricalRealization(bundle, *modelApplication.CognitiveMethod.MethodApplication.RealizationRef)
	if err != nil {
		t.Fatalf("resolve M1b realization: %v", err)
	}

	if got := exactImplementationDigests(stubResolved); !sameStrings(got, []string{sourceBinding.ContentDigest, stubBinding.ContentDigest}) {
		t.Fatalf("M1a realization implementation bindings = %#v", got)
	}
	if got := exactImplementationDigests(modelResolved); !sameStrings(got, []string{sourceBinding.ContentDigest, modelBinding.ContentDigest}) {
		t.Fatalf("M1b realization implementation bindings = %#v", got)
	}

	// 後続revisionが同じlogical identityで追加されても、過去Applicationが持つ
	// Exact Bindingは書き換わりません。
	stubHistoricalBinding, ok := stubApplication.CognitiveMethod.MethodApplication.RealizationRef.ExactBinding()
	if !ok {
		t.Fatal("M1a application lost exact realization binding")
	}
	if stubHistoricalBinding.ContentDigest != stubRealizationBinding.ContentDigest {
		t.Fatalf("M1a historical binding was rewritten: got=%s want=%s", stubHistoricalBinding.ContentDigest, stubRealizationBinding.ContentDigest)
	}

	// logical-only referenceは、同じlogical identityに複数revisionが存在する場合、
	// どちらを当時使ったかを一意に選べません。これはExact Bindingを必要とする
	// historical reconstructionのnegative controlです。
	logicalOnly := Reference{Kind: realizationRef.Kind, ID: realizationRef.ID}
	if candidates := countHistoricalRealizationCandidates(bundle, logicalOnly); candidates != 2 {
		t.Fatalf("logical-only realization candidate count = %d, want 2", candidates)
	}
}

func reconstructionArtifact(kind, id string, payload []byte) (RuntimeRecord, ExactBinding) {
	binding := reconstructionBinding(LogicalReference{Kind: kind, ID: id}, payload)
	return RuntimeRecord{
		EnvelopeRecord: InterchangeRecord{
			Kind:         kind,
			ExactBinding: &binding,
			Payload:      append([]byte(nil), payload...),
		},
		Status: RecordNotVerified,
	}, binding
}

func reconstructionRealization(
	t *testing.T,
	methodRef LogicalReference,
	realizationRef LogicalReference,
	description string,
	implementationBindings ...ExactBinding,
) (RuntimeRecord, ExactBinding) {
	t.Helper()

	implementationRefs := make([]Reference, 0, len(implementationBindings))
	for _, binding := range implementationBindings {
		implementationRefs = append(implementationRefs, reconstructionExactReference(binding))
	}
	doc := &CognitiveMethodDocument{
		Contract:   ContractCognitiveMethod,
		RecordType: "method_realization",
		MethodRealization: &MethodRealization{
			Ref:                realizationRef,
			MethodRef:          Reference{Kind: methodRef.Kind, ID: methodRef.ID, Scope: methodRef.Scope},
			Description:        description,
			ImplementationRefs: implementationRefs,
		},
	}
	payload, err := json.Marshal(doc)
	if err != nil {
		t.Fatalf("marshal realization: %v", err)
	}
	binding := reconstructionBinding(realizationRef, payload)
	return RuntimeRecord{
		EnvelopeRecord: InterchangeRecord{
			Kind:         realizationRef.Kind,
			ExactBinding: &binding,
			Payload:      payload,
		},
		Status:          RecordValidated,
		CognitiveMethod: doc,
	}, binding
}

func reconstructionApplication(
	applicationRef LogicalReference,
	methodRef LogicalReference,
	realizationBinding ExactBinding,
	summary string,
) RuntimeRecord {
	realizationReference := reconstructionExactReference(realizationBinding)
	return RuntimeRecord{
		Status: RecordValidated,
		CognitiveMethod: &CognitiveMethodDocument{
			Contract:   ContractCognitiveMethod,
			RecordType: "method_application",
			MethodApplication: &MethodApplication{
				Ref:            applicationRef,
				MethodRef:      Reference{Kind: methodRef.Kind, ID: methodRef.ID, Scope: methodRef.Scope},
				RealizationRef: &realizationReference,
				Summary:        summary,
			},
		},
	}
}

func reconstructionBinding(logical LogicalReference, payload []byte) ExactBinding {
	digest := sha256.Sum256(payload)
	return ExactBinding{
		LogicalRef:    logical,
		ContentDigest: "sha256:" + hex.EncodeToString(digest[:]),
		RepresentationProfile: RepresentationProfile{
			ProfileID: reconstructionRawProfile,
			Version:   "v1alpha1",
		},
	}
}

func reconstructionExactReference(binding ExactBinding) Reference {
	logical := binding.LogicalRef
	profile := binding.RepresentationProfile
	return Reference{
		LogicalRef:            &logical,
		ContentDigest:         binding.ContentDigest,
		RepresentationProfile: &profile,
	}
}

func resolveHistoricalRealization(bundle *Bundle, ref Reference) (*MethodRealization, error) {
	binding, ok := ref.ExactBinding()
	if !ok {
		return nil, fmt.Errorf("historical reconstruction requires an exact realization reference")
	}
	var matched *MethodRealization
	for _, record := range bundle.Records {
		if record.EnvelopeRecord.ExactBinding == nil || record.CognitiveMethod == nil || record.CognitiveMethod.MethodRealization == nil {
			continue
		}
		if !sameReconstructionBinding(*record.EnvelopeRecord.ExactBinding, binding) {
			continue
		}
		if matched != nil {
			return nil, fmt.Errorf("exact realization binding matched multiple records")
		}
		matched = record.CognitiveMethod.MethodRealization
	}
	if matched == nil {
		return nil, fmt.Errorf("exact realization binding was not found in the reconstruction bundle")
	}
	return matched, nil
}

func countHistoricalRealizationCandidates(bundle *Bundle, ref Reference) int {
	logical, ok := ref.LogicalIdentity()
	if !ok {
		return 0
	}
	count := 0
	for _, record := range bundle.Records {
		if record.CognitiveMethod == nil || record.CognitiveMethod.MethodRealization == nil {
			continue
		}
		if record.CognitiveMethod.MethodRealization.Ref == logical {
			count++
		}
	}
	return count
}

func exactImplementationDigests(realization *MethodRealization) []string {
	result := make([]string, 0, len(realization.ImplementationRefs))
	for _, ref := range realization.ImplementationRefs {
		binding, ok := ref.ExactBinding()
		if !ok {
			continue
		}
		result = append(result, binding.ContentDigest)
	}
	return result
}

func sameReconstructionBinding(left, right ExactBinding) bool {
	return left.LogicalRef == right.LogicalRef &&
		left.ContentDigest == right.ContentDigest &&
		left.RepresentationProfile == right.RepresentationProfile
}

func sameStrings(left, right []string) bool {
	if len(left) != len(right) {
		return false
	}
	for index := range left {
		if left[index] != right[index] {
			return false
		}
	}
	return true
}
