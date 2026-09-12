package realizationprobe

import (
	"bytes"
	"encoding/json"
	"os/exec"
	"path/filepath"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/interactionprobe"
	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

type providerRequest struct {
	State string `json:"state"`
}

type methodRequest struct {
	Inquiry        string   `json:"inquiry"`
	ObservationIDs []string `json:"observation_ids"`
	UnresolvedIDs  []string `json:"unresolved_ids"`
}

type methodResponse struct {
	Summary        string   `json:"summary"`
	Recommendation string   `json:"recommendation"`
	ResidualIDs    []string `json:"residual_ids"`
}

func TestOutOfProcessProviderAndMethodRealizationExchangePreservesDecisionMemory(t *testing.T) {
	providerBinary := buildReferenceCommand(t, "./cmd/sei-reference-provider")
	methodBinary := buildReferenceCommand(t, "./cmd/sei-reference-method")

	store := interactionprobe.NewCanonicalStore()
	human := interactionprobe.NewHumanSurface(store)
	machine := interactionprobe.NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-PORTABILITY", "ProviderとMethod Realizationを交換しても過去の判断を読み直せるか確認する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	unknown, err := human.RecordUnknown("U-OUTCOME", "実行後の業務成果はまだ確認できていない")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}

	capability := logical("capability", "CAP-PORTABLE")
	observationA := logical("capability-observation", "CO-PROC-A")
	observationB := logical("capability-observation", "CO-PROC-B")

	payloadA, err := RunRawJSON(providerBinary, []string{"--profile", "a"}, providerRequest{State: "healthy"})
	if err != nil {
		t.Fatalf("provider A process error = %v", err)
	}
	docA, err := (provideradapter.ReferenceProviderAAdapter{}).Observe(provideradapter.ObservationContext{
		ObservationID:  observationA.ID,
		CapabilityRef:  capability,
		ObservedAt:     "2026-09-01T13:40:00Z",
		SourceStateRef: "process://reference-provider-a/run-1",
	}, payloadA)
	if err != nil {
		t.Fatalf("ReferenceProviderAAdapter.Observe() error = %v", err)
	}
	recordA, err := provideradapter.ValidateObservation(docA)
	if err != nil {
		t.Fatalf("ValidateObservation(A) error = %v", err)
	}
	if err := store.Add(recordA); err != nil {
		t.Fatalf("store.Add(provider A) error = %v", err)
	}

	method := logical("method", "M-PORTABLE-REVIEW")
	realizationA := logical("method-realization", "MR-PROC-EVIDENCE-FIRST")
	realizationB := logical("method-realization", "MR-PROC-CAUTIOUS")
	addMethodDefinition(t, store, method)
	addMethodRealization(t, store, realizationA, method, "別processで動くevidence-first reference Realization")
	addMethodRealization(t, store, realizationB, method, "別processで動くcautious reference Realization")

	var methodA methodResponse
	if err := RunJSON(methodBinary, []string{"--profile", "evidence-first"}, methodRequest{
		Inquiry:        inquiry.ID,
		ObservationIDs: []string{observationA.ID},
		UnresolvedIDs:  []string{unknown.ID},
	}, &methodA); err != nil {
		t.Fatalf("method A process error = %v", err)
	}
	if methodA.Recommendation == "" || len(methodA.ResidualIDs) != 1 || methodA.ResidualIDs[0] != unknown.ID {
		t.Fatalf("method A output = %#v", methodA)
	}

	recommendationA := logical("recommendation", "R-PROC-A")
	applicationA := logical("method-application", "MA-PROC-A")
	if err := machine.RecordRecommendation(interactionprobe.RecommendationInput{
		Ref:         recommendationA,
		Statement:   methodA.Recommendation,
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{observationA},
		Rationale:   methodA.Summary,
	}); err != nil {
		t.Fatalf("RecordRecommendation(A) error = %v", err)
	}
	if err := machine.RecordMethodApplication(interactionprobe.MethodApplicationInput{
		Ref:            applicationA,
		MethodRef:      method,
		RealizationRef: &realizationA,
		ContextRefs:    []semanticruntime.LogicalReference{inquiry},
		InputRefs:      []semanticruntime.LogicalReference{observationA, unknown},
		OutputRefs:     []semanticruntime.LogicalReference{recommendationA},
		ResidualRefs:   []semanticruntime.LogicalReference{unknown},
		AppliedAt:      "2026-09-01T13:41:00Z",
		Summary:        methodA.Summary,
	}); err != nil {
		t.Fatalf("RecordMethodApplication(A) error = %v", err)
	}

	decision := logical("decision", "D-PORTABLE-001")
	responsibility := logical("responsibility", "SUBJECT-OWNER")
	if err := human.RecordDecision(interactionprobe.DecisionInput{
		Ref:                decision,
		Statement:          "Provider Aを使って限定実行し、未解決の業務成果は後続確認へ残す",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry, applicationA},
		BasisRefs:          []semanticruntime.LogicalReference{observationA, applicationA},
		RecommendationRefs: []semanticruntime.LogicalReference{recommendationA},
		UnresolvedRefs:     []semanticruntime.LogicalReference{unknown},
		ResponsibilityRefs: []semanticruntime.LogicalReference{responsibility},
		Rationale:          "当時利用したProvider観測とMethod Applicationを明示した",
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}
	before := decisionBytes(t, store, decision)

	payloadB, err := RunRawJSON(providerBinary, []string{"--profile", "b"}, providerRequest{State: "healthy"})
	if err != nil {
		t.Fatalf("provider B process error = %v", err)
	}
	docB, err := (provideradapter.ReferenceProviderBAdapter{}).Observe(provideradapter.ObservationContext{
		ObservationID:  observationB.ID,
		CapabilityRef:  capability,
		ObservedAt:     "2026-09-01T13:45:00Z",
		SourceStateRef: "process://reference-provider-b/run-1",
	}, payloadB)
	if err != nil {
		t.Fatalf("ReferenceProviderBAdapter.Observe() error = %v", err)
	}
	recordB, err := provideradapter.ValidateObservation(docB)
	if err != nil {
		t.Fatalf("ValidateObservation(B) error = %v", err)
	}
	if err := store.Add(recordB); err != nil {
		t.Fatalf("store.Add(provider B) error = %v", err)
	}

	var methodB methodResponse
	if err := RunJSON(methodBinary, []string{"--profile", "cautious"}, methodRequest{
		Inquiry:        inquiry.ID,
		ObservationIDs: []string{observationB.ID},
		UnresolvedIDs:  []string{unknown.ID},
	}, &methodB); err != nil {
		t.Fatalf("method B process error = %v", err)
	}
	if methodB.Recommendation == methodA.Recommendation {
		t.Fatal("method Realization exchange did not produce a distinguishable recommendation")
	}

	recommendationB := logical("recommendation", "R-PROC-B")
	applicationB := logical("method-application", "MA-PROC-B")
	if err := machine.RecordRecommendation(interactionprobe.RecommendationInput{
		Ref:         recommendationB,
		Statement:   methodB.Recommendation,
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{observationB},
		Rationale:   methodB.Summary,
	}); err != nil {
		t.Fatalf("RecordRecommendation(B) error = %v", err)
	}
	if err := machine.RecordMethodApplication(interactionprobe.MethodApplicationInput{
		Ref:            applicationB,
		MethodRef:      method,
		RealizationRef: &realizationB,
		ContextRefs:    []semanticruntime.LogicalReference{inquiry},
		InputRefs:      []semanticruntime.LogicalReference{observationB, unknown},
		OutputRefs:     []semanticruntime.LogicalReference{recommendationB},
		ResidualRefs:   []semanticruntime.LogicalReference{unknown},
		AppliedAt:      "2026-09-01T13:46:00Z",
		Summary:        methodB.Summary,
	}); err != nil {
		t.Fatalf("RecordMethodApplication(B) error = %v", err)
	}

	after := decisionBytes(t, store, decision)
	if !bytes.Equal(before, after) {
		t.Fatalf("Provider / Method exchange rewrote historical Decision\nbefore=%s\nafter=%s", before, after)
	}

	storedA := mustFind(t, store, observationA)
	storedB := mustFind(t, store, observationB)
	providerA := storedA.Capability.Observation.Target.ProviderRef
	providerB := storedB.Capability.Observation.Target.ProviderRef
	if providerA == nil || providerB == nil || providerA.ID == providerB.ID {
		t.Fatalf("Provider identities were flattened: A=%#v B=%#v", providerA, providerB)
	}
	if storedA.Capability.Observation.Target.CapabilityRef == nil || storedB.Capability.Observation.Target.CapabilityRef == nil ||
		*storedA.Capability.Observation.Target.CapabilityRef != capability || *storedB.Capability.Observation.Target.CapabilityRef != capability {
		t.Fatalf("Provider exchange changed Capability identity: A=%#v B=%#v", storedA.Capability.Observation.Target.CapabilityRef, storedB.Capability.Observation.Target.CapabilityRef)
	}

	appA := mustFind(t, store, applicationA).CognitiveMethod.MethodApplication
	appB := mustFind(t, store, applicationB).CognitiveMethod.MethodApplication
	if appA.RealizationRef == nil || appB.RealizationRef == nil {
		t.Fatal("Method Application lost realization_ref")
	}
	logicalA, okA := appA.RealizationRef.LogicalIdentity()
	logicalB, okB := appB.RealizationRef.LogicalIdentity()
	if !okA || !okB || logicalA != realizationA || logicalB != realizationB || logicalA == logicalB {
		t.Fatalf("Method Realization identities were not preserved: A=%#v B=%#v", logicalA, logicalB)
	}

	decisionRecord := mustFind(t, store, decision).Decision.Decision
	if len(decisionRecord.RecommendationRefs) != 1 {
		t.Fatalf("historical Decision recommendation refs changed: %#v", decisionRecord.RecommendationRefs)
	}
	decisionRecommendation, ok := decisionRecord.RecommendationRefs[0].LogicalIdentity()
	if !ok || decisionRecommendation != recommendationA {
		t.Fatalf("historical Decision was rebound to new recommendation: %#v", decisionRecord.RecommendationRefs)
	}

	digestBeforeFailure, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before failure error = %v", err)
	}
	var invalid methodResponse
	if err := RunJSON(methodBinary, []string{"--profile", "unsupported"}, methodRequest{Inquiry: inquiry.ID}, &invalid); err == nil {
		t.Fatal("unsupported Method Realization profile unexpectedly succeeded")
	}
	if _, err := RunRawJSON(providerBinary, []string{"--profile", "a"}, providerRequest{State: "unsupported"}); err == nil {
		t.Fatal("unsupported Provider state unexpectedly succeeded")
	}
	digestAfterFailure, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after failure error = %v", err)
	}
	if digestBeforeFailure != digestAfterFailure {
		t.Fatalf("failed external Realization mutated canonical source: before=%s after=%s", digestBeforeFailure, digestAfterFailure)
	}
}

func buildReferenceCommand(t *testing.T, packagePath string) string {
	t.Helper()
	moduleRoot, err := filepath.Abs("..")
	if err != nil {
		t.Fatalf("module root error = %v", err)
	}
	binary := filepath.Join(t.TempDir(), filepath.Base(packagePath))
	cmd := exec.Command("go", "build", "-o", binary, packagePath)
	cmd.Dir = moduleRoot
	if output, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("go build %s error = %v\n%s", packagePath, err, output)
	}
	return binary
}

func logical(kind, id string) semanticruntime.LogicalReference {
	return semanticruntime.LogicalReference{Kind: kind, ID: id}
}

func ref(value semanticruntime.LogicalReference) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: value.Kind, ID: value.ID, Scope: value.Scope}
}

func addMethodDefinition(t *testing.T, store *interactionprobe.CanonicalStore, method semanticruntime.LogicalReference) {
	t.Helper()
	doc := &semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_definition",
		MethodDefinition: &semanticruntime.MethodDefinition{
			Ref:     method,
			Title:   "Reference decision review method",
			Purpose: "ProviderやRealizationを交換しても、入力・残差・出力の意味を分けて判断材料を整理する",
		},
	}
	if err := store.Add(semanticruntime.RuntimeRecord{CognitiveMethod: doc}); err != nil {
		t.Fatalf("add Method Definition error = %v", err)
	}
}

func addMethodRealization(t *testing.T, store *interactionprobe.CanonicalStore, realization, method semanticruntime.LogicalReference, description string) {
	t.Helper()
	doc := &semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_realization",
		MethodRealization: &semanticruntime.MethodRealization{
			Ref:         realization,
			MethodRef:   ref(method),
			Description: description,
			ImplementationRefs: []semanticruntime.Reference{
				{Kind: "implementation", ID: realization.ID},
			},
		},
	}
	if err := store.Add(semanticruntime.RuntimeRecord{CognitiveMethod: doc}); err != nil {
		t.Fatalf("add Method Realization error = %v", err)
	}
}

func mustFind(t *testing.T, store *interactionprobe.CanonicalStore, target semanticruntime.LogicalReference) semanticruntime.RuntimeRecord {
	t.Helper()
	record, ok, err := store.Find(target)
	if err != nil {
		t.Fatalf("Find(%v) error = %v", target, err)
	}
	if !ok {
		t.Fatalf("Find(%v) did not find a record", target)
	}
	return record
}

func decisionBytes(t *testing.T, store *interactionprobe.CanonicalStore, target semanticruntime.LogicalReference) []byte {
	t.Helper()
	record := mustFind(t, store, target)
	if record.Decision == nil || record.Decision.Decision == nil {
		t.Fatalf("%v is not a Decision", target)
	}
	payload, err := json.Marshal(record.Decision.Decision)
	if err != nil {
		t.Fatalf("marshal Decision error = %v", err)
	}
	return payload
}
