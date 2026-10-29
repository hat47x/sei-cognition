package interactionprobe

import (
	"reflect"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func lr(kind, id string) semanticruntime.LogicalReference {
	return semanticruntime.LogicalReference{Kind: kind, ID: id}
}

func TestHumanAndMachineSurfacesShareCanonicalMeaning(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-001", "外部サービスの実行結果を確認し、必要なら判断を見直す")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}

	minimal, err := human.LightView()
	if err != nil {
		t.Fatalf("LightView() minimal error = %v", err)
	}
	if minimal.Inquiry.Ref != inquiry || minimal.Inquiry.Text == "" {
		t.Fatalf("minimal LightView() inquiry = %#v, want %v", minimal.Inquiry, inquiry)
	}
	if len(minimal.Decisions) != 0 || len(minimal.Recommendations) != 0 {
		t.Fatalf("minimal LightView() unexpectedly contains later-stage records: %#v", minimal)
	}

	unknown, err := human.RecordUnknown("U-001", "実行後の業務成果はまだ分からない")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}
	conflict, err := human.RecordConflict("C-001", "可用性について二つの観測結果が食い違っている")
	if err != nil {
		t.Fatalf("RecordConflict() error = %v", err)
	}

	capability := lr("capability", "CAP-001")
	provider := lr("provider", "PROVIDER-A")
	observation := lr("capability_observation", "CO-001")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           observation,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-01T10:10:00Z",
		Conditions: []semanticruntime.ObservedCondition{
			{Key: "availability", State: "available"},
		},
		ProvenanceRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() error = %v", err)
	}

	method := lr("method", "M-001")
	methodApplication := lr("method_application", "MA-001")
	recommendation := lr("recommendation", "R-001")
	if err := machine.RecordMethodApplication(MethodApplicationInput{
		Ref:          methodApplication,
		MethodRef:    method,
		ContextRefs:  []semanticruntime.LogicalReference{inquiry},
		InputRefs:    []semanticruntime.LogicalReference{inquiry, observation, unknown, conflict},
		OutputRefs:   []semanticruntime.LogicalReference{recommendation},
		ResidualRefs: []semanticruntime.LogicalReference{unknown, conflict},
		AppliedAt:    "2026-09-01T10:12:00Z",
		Summary:      "観測結果と未解決事項を分けたまま比較した",
	}); err != nil {
		t.Fatalf("RecordMethodApplication() error = %v", err)
	}

	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "実行を進めるが、業務成果は後から別途確認する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{methodApplication, observation},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}

	afterMachine, err := human.LightView()
	if err != nil {
		t.Fatalf("LightView() after machine writes error = %v", err)
	}
	if len(afterMachine.Observations) != 1 || afterMachine.Observations[0].Ref != observation {
		t.Fatalf("human surface did not read machine observation: %#v", afterMachine.Observations)
	}
	if len(afterMachine.Recommendations) != 1 || afterMachine.Recommendations[0].Ref != recommendation {
		t.Fatalf("human surface did not read machine recommendation: %#v", afterMachine.Recommendations)
	}
	if len(afterMachine.Unknowns) != 1 || afterMachine.Unknowns[0].Ref != unknown {
		t.Fatalf("unknown was flattened or lost: %#v", afterMachine.Unknowns)
	}
	if len(afterMachine.Conflicts) != 1 || afterMachine.Conflicts[0].Ref != conflict {
		t.Fatalf("conflict was flattened or lost: %#v", afterMachine.Conflicts)
	}

	decision := lr("decision", "D-001")
	responsibility := lr("responsibility", "HUMAN-OWNER")
	if err := human.RecordDecision(DecisionInput{
		Ref:                decision,
		Statement:          "実行を進め、結果を新しいObservationとして確認する",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry, methodApplication},
		BasisRefs:          []semanticruntime.LogicalReference{observation, methodApplication},
		RecommendationRefs: []semanticruntime.LogicalReference{recommendation},
		UnresolvedRefs:     []semanticruntime.LogicalReference{unknown, conflict},
		ResponsibilityRefs: []semanticruntime.LogicalReference{responsibility},
		Rationale:          "実行可能性は確認できたが、業務成果は未確認のため後続レビューを残す",
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}

	machineDecision, err := machine.ReadDecision(decision)
	if err != nil {
		t.Fatalf("ReadDecision() error = %v", err)
	}
	if machineDecision.Ref != decision || machineDecision.Statement == "" {
		t.Fatalf("machine surface did not preserve Decision identity: %#v", machineDecision)
	}
	if len(machineDecision.RecommendationRefs) != 1 {
		t.Fatalf("machine surface collapsed recommendation/decision boundary: %#v", machineDecision.RecommendationRefs)
	}
	if !reflect.DeepEqual(logicalRefs(machineDecision.UnresolvedRefs), []semanticruntime.LogicalReference{unknown, conflict}) {
		t.Fatalf("machine surface did not preserve unresolved refs: %#v", machineDecision.UnresolvedRefs)
	}

	structured, err := machine.StructuredView()
	if err != nil {
		t.Fatalf("StructuredView() error = %v", err)
	}
	foundDecision := false
	for _, record := range structured.Records {
		if record.Ref == decision {
			foundDecision = true
			if record.Kind != "decision" {
				t.Fatalf("Decision was exposed as %q", record.Kind)
			}
		}
	}
	if !foundDecision {
		t.Fatal("machine StructuredView() did not contain human Decision")
	}
}

func TestProjectionAndSurfaceStateDoNotBecomeCanonicalAuthority(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	if _, err := human.StartInquiry("I-001", "簡略表示と監査表示を往復する"); err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	unknown, err := human.RecordUnknown("U-001", "追加確認が必要")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}

	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}
	if _, err := human.LightView(); err != nil {
		t.Fatalf("LightView() error = %v", err)
	}
	audit, err := human.AuditView()
	if err != nil {
		t.Fatalf("AuditView() error = %v", err)
	}
	if audit.CanonicalDigest != before {
		t.Fatalf("AuditView() digest = %s, want %s", audit.CanonicalDigest, before)
	}
	afterProjection, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after projection error = %v", err)
	}
	if before != afterProjection {
		t.Fatalf("Projection generation changed canonical source: before=%s after=%s", before, afterProjection)
	}

	human.SetLocalState("selected-tab", "audit")
	machine.SetLocalState("cursor", "record-3")
	human.ResetLocalState()
	machine.ResetLocalState()
	afterReset, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after surface reset error = %v", err)
	}
	if before != afterReset {
		t.Fatalf("surface-local state changed canonical source: before=%s after=%s", before, afterReset)
	}

	foundUnknown := false
	for _, record := range audit.Records {
		if record.Ref == unknown {
			foundUnknown = true
			if record.Status != semanticruntime.RecordNotVerified || record.Kind != "unknown" {
				t.Fatalf("audit record lost opaque epistemic state: %#v", record)
			}
		}
	}
	if !foundUnknown {
		t.Fatal("audit projection did not preserve unknown record")
	}
}

func TestAuditViewExposesDecisionBasisAndResponsibility(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, _ := human.StartInquiry("I-001", "判断根拠を後から確認する")
	unknown, _ := human.RecordUnknown("U-001", "結果は未確認")
	observation := lr("capability_observation", "CO-001")
	capability := lr("capability", "CAP-001")
	provider := lr("provider", "P-001")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:            observation,
		CapabilityRef:  &capability,
		ProviderRef:    &provider,
		ObservedAt:     "2026-09-01T10:00:00Z",
		Conditions:     []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
		ProvenanceRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() error = %v", err)
	}

	recommendation := lr("recommendation", "R-001")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "限定条件付きで進める",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{observation},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}

	decision := lr("decision", "D-001")
	responsibility := lr("responsibility", "OWNER-001")
	if err := human.RecordDecision(DecisionInput{
		Ref:                decision,
		Statement:          "限定条件付きで実行する",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry},
		BasisRefs:          []semanticruntime.LogicalReference{observation},
		RecommendationRefs: []semanticruntime.LogicalReference{recommendation},
		UnresolvedRefs:     []semanticruntime.LogicalReference{unknown},
		ResponsibilityRefs: []semanticruntime.LogicalReference{responsibility},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}

	audit, err := human.AuditView()
	if err != nil {
		t.Fatalf("AuditView() error = %v", err)
	}
	var got *AuditRecord
	for i := range audit.Records {
		if audit.Records[i].Ref == decision {
			got = &audit.Records[i]
			break
		}
	}
	if got == nil {
		t.Fatal("audit view did not contain Decision")
	}
	if !reflect.DeepEqual(got.BasisRefs, []semanticruntime.LogicalReference{observation}) {
		t.Fatalf("audit basis refs = %#v", got.BasisRefs)
	}
	if !reflect.DeepEqual(got.ResponsibilityRefs, []semanticruntime.LogicalReference{responsibility}) {
		t.Fatalf("audit responsibility refs = %#v", got.ResponsibilityRefs)
	}
	if !reflect.DeepEqual(got.UnresolvedRefs, []semanticruntime.LogicalReference{unknown}) {
		t.Fatalf("audit unresolved refs = %#v", got.UnresolvedRefs)
	}
}

func TestPostDecisionObservationDoesNotRewriteHistoricalBasis(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, _ := human.StartInquiry("I-001", "実行後のObservationを追加する")
	basis := lr("capability_observation", "CO-BEFORE")
	capability := lr("capability", "CAP-001")
	provider := lr("provider", "P-001")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           basis,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-01T10:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() before error = %v", err)
	}

	decision := lr("decision", "D-001")
	if err := human.RecordDecision(DecisionInput{
		Ref:         decision,
		Statement:   "実行する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{basis},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}
	before, err := machine.ReadDecision(decision)
	if err != nil {
		t.Fatalf("ReadDecision() before error = %v", err)
	}

	result := lr("capability_observation", "CO-AFTER")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           result,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-01T10:30:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "execution.status", State: "succeeded"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() after error = %v", err)
	}
	after, err := machine.ReadDecision(decision)
	if err != nil {
		t.Fatalf("ReadDecision() after error = %v", err)
	}
	if !reflect.DeepEqual(before.BasisRefs, after.BasisRefs) {
		t.Fatalf("post-decision observation rewrote historical basis: before=%#v after=%#v", before.BasisRefs, after.BasisRefs)
	}
	if reflect.DeepEqual(logicalRefs(after.BasisRefs), []semanticruntime.LogicalReference{result}) {
		t.Fatal("post-decision observation replaced historical basis")
	}
}

func TestMachineSurfaceDoesNotInferResponsibilityOrRequirePrivateReasoning(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)
	inquiry, _ := human.StartInquiry("I-001", "AIの提案を受ける")

	recommendation := lr("recommendation", "R-001")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "候補Aを比較対象に残す",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}
	got, err := machine.ReadRecommendation(recommendation)
	if err != nil {
		t.Fatalf("ReadRecommendation() error = %v", err)
	}
	if len(got.ResponsibilityRefs) != 0 {
		t.Fatalf("machine surface inferred responsibility from actor kind: %#v", got.ResponsibilityRefs)
	}

	inputType := reflect.TypeOf(RecommendationInput{})
	for _, forbidden := range []string{"ChainOfThought", "PrivateReasoning", "ReasoningTranscript"} {
		if _, found := inputType.FieldByName(forbidden); found {
			t.Fatalf("RecommendationInput unexpectedly requires private reasoning field %q", forbidden)
		}
	}
}

func TestRejectsRecommendationDecisionIdentityCollapse(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)
	inquiry, _ := human.StartInquiry("I-001", "提案と判断を分離する")

	shared := lr("recommendation", "R-001")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         shared,
		Statement:   "進めることを提案する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}

	err := human.RecordDecision(DecisionInput{
		Ref:         shared,
		Statement:   "進める",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err == nil || !strings.Contains(err.Error(), "duplicate canonical record") {
		t.Fatalf("RecordDecision() error = %v, want duplicate identity rejection", err)
	}
}

func TestOpaqueRecordCannotClaimValidatedSemantics(t *testing.T) {
	store := NewCanonicalStore()
	unknown := lr("unknown", "U-001")
	err := store.Add(semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{Kind: "unknown", LogicalRef: &unknown},
		Status:         semanticruntime.RecordValidated,
	})
	if err == nil || !strings.Contains(err.Error(), "must remain not_verified") {
		t.Fatalf("Add() error = %v, want opaque validation claim rejection", err)
	}
}
