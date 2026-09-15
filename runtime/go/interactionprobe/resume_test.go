package interactionprobe

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestResumeProjectionRebuildsFromCanonicalStateAfterSurfaceLoss(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-RESUME", "外部Providerの変更後も判断を継続できるか確認する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	unknown, err := human.RecordUnknown("U-RESUME", "変更後の業務成果はまだ分からない")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}

	observation := lr("capability_observation", "CO-RESUME")
	capability := lr("capability", "CAP-RESUME")
	provider := lr("provider", "P-RESUME")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:            observation,
		CapabilityRef:  &capability,
		ProviderRef:    &provider,
		ObservedAt:     "2026-09-16T00:00:00Z",
		Conditions:     []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
		ProvenanceRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() error = %v", err)
	}

	recommendation := lr("recommendation", "R-RESUME")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "Provider変更を進め、業務成果は後続Observationで確認する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{observation},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}

	decision := lr("decision", "D-RESUME")
	if err := human.RecordDecision(DecisionInput{
		Ref:                decision,
		Statement:          "Provider変更を実施する",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry},
		BasisRefs:          []semanticruntime.LogicalReference{observation},
		RecommendationRefs: []semanticruntime.LogicalReference{recommendation},
		UnresolvedRefs:     []semanticruntime.LogicalReference{unknown},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}

	before, err := human.ResumeProjection(decision)
	if err != nil {
		t.Fatalf("ResumeProjection() before surface loss error = %v", err)
	}

	human.SetLocalState("selected-tab", "audit")
	machine.SetLocalState("chat", "temporary conversation")

	// Surface自体を作り直し、local stateやchat相当の状態を引き継がない。
	resumedHuman := NewHumanSurface(store)
	after, err := resumedHuman.ResumeProjection(decision)
	if err != nil {
		t.Fatalf("ResumeProjection() after surface loss error = %v", err)
	}

	if !reflect.DeepEqual(before, after) {
		t.Fatalf("resume projection changed after surface loss:\nbefore=%#v\nafter=%#v", before, after)
	}
	if after.Inquiry.Ref != inquiry || after.Inquiry.Statement == "" {
		t.Fatalf("resume inquiry = %#v, want %v with text", after.Inquiry, inquiry)
	}
	if after.Decision.Ref != decision || after.Decision.Statement == "" {
		t.Fatalf("resume decision = %#v, want %v", after.Decision, decision)
	}
	if len(after.Basis) != 1 || after.Basis[0].Ref != observation {
		t.Fatalf("resume basis = %#v, want observation %v", after.Basis, observation)
	}
	if len(after.Recommendations) != 1 || after.Recommendations[0].Ref != recommendation {
		t.Fatalf("resume recommendations = %#v, want %v", after.Recommendations, recommendation)
	}
	if len(after.Unresolved) != 1 || after.Unresolved[0].Ref != unknown {
		t.Fatalf("resume unresolved = %#v, want %v", after.Unresolved, unknown)
	}
	if len(after.MissingRefs) != 0 {
		t.Fatalf("resume missing refs = %#v, want none", after.MissingRefs)
	}
}

func TestResumeProjectionDoesNotRewriteHistoricalBasisWithLaterObservation(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, _ := human.StartInquiry("I-TEMPORAL", "Decision後の変化を過去のbasisへ混ぜない")
	basis := lr("capability_observation", "CO-BEFORE-RESUME")
	capability := lr("capability", "CAP-TEMPORAL")
	provider := lr("provider", "P-TEMPORAL")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           basis,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-16T00:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() basis error = %v", err)
	}

	decision := lr("decision", "D-TEMPORAL")
	if err := human.RecordDecision(DecisionInput{
		Ref:         decision,
		Statement:   "現時点のbasisで実行する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{basis},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}

	later := lr("capability_observation", "CO-AFTER-RESUME")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           later,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-16T01:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "execution.status", State: "succeeded"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() later error = %v", err)
	}

	projection, err := human.ResumeProjection(decision)
	if err != nil {
		t.Fatalf("ResumeProjection() error = %v", err)
	}
	if len(projection.Basis) != 1 || projection.Basis[0].Ref != basis {
		t.Fatalf("historical basis was changed: %#v", projection.Basis)
	}
	for _, record := range projection.Basis {
		if record.Ref == later {
			t.Fatalf("later observation leaked into historical basis: %#v", projection.Basis)
		}
	}
}

func TestResumeProjectionExposesMissingCanonicalReferences(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)

	inquiry, _ := human.StartInquiry("I-MISSING", "参照欠落を黙って隠さない")
	missingBasis := lr("capability_observation", "CO-MISSING")
	missingUnknown := lr("unknown", "U-MISSING")
	decision := lr("decision", "D-MISSING")
	if err := human.RecordDecision(DecisionInput{
		Ref:            decision,
		Statement:      "参照欠落を含むprobe Decision",
		ContextRefs:    []semanticruntime.LogicalReference{inquiry},
		BasisRefs:      []semanticruntime.LogicalReference{missingBasis},
		UnresolvedRefs: []semanticruntime.LogicalReference{missingUnknown},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}

	projection, err := human.ResumeProjection(decision)
	if err != nil {
		t.Fatalf("ResumeProjection() error = %v", err)
	}
	wantMissing := []semanticruntime.LogicalReference{missingBasis, missingUnknown}
	if !reflect.DeepEqual(projection.MissingRefs, wantMissing) {
		t.Fatalf("MissingRefs = %#v, want %#v", projection.MissingRefs, wantMissing)
	}
	if len(projection.Basis) != 0 || len(projection.Unresolved) != 0 {
		t.Fatalf("missing refs were exposed as resolved records: basis=%#v unresolved=%#v", projection.Basis, projection.Unresolved)
	}
}

func TestResumeProjectionRequiresDecisionTarget(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	inquiry, err := human.StartInquiry("I-NO-DECISION", "Decision以外をcurrent Decisionとして推測しない")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}

	if _, err := human.ResumeProjection(inquiry); err == nil {
		t.Fatal("ResumeProjection() accepted a non-decision target")
	}
}
