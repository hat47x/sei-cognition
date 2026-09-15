package interactionprobe

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestChangeReviewProjectionSeparatesHistoricalBasisFromCanonicalChanges(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-CHANGE-REVIEW", "Decision後にcanonicalへ導入された変化を分けて確認する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	oldConflict, err := human.RecordConflict("C-BEFORE-DECISION", "判断前から存在していた未解決の対立")
	if err != nil {
		t.Fatalf("RecordConflict() old error = %v", err)
	}

	basis := lr("capability_observation", "CO-CHANGE-BASE")
	capability := lr("capability", "CAP-CHANGE-REVIEW")
	provider := lr("provider", "P-CHANGE-REVIEW")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           basis,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-16T00:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() basis error = %v", err)
	}

	decision := lr("decision", "D-CHANGE-REVIEW")
	if err := human.RecordDecisionWithReviewCheckpoint(DecisionInput{
		Ref:            decision,
		Statement:      "現在のbasisでProvider変更を進める",
		ContextRefs:    []semanticruntime.LogicalReference{inquiry},
		BasisRefs:      []semanticruntime.LogicalReference{basis},
		UnresolvedRefs: []semanticruntime.LogicalReference{oldConflict},
	}); err != nil {
		t.Fatalf("RecordDecisionWithReviewCheckpoint() error = %v", err)
	}

	laterObservation := lr("capability_observation", "CO-CHANGE-AFTER")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           laterObservation,
		CapabilityRef: &capability,
		ProviderRef:   &provider,
		ObservedAt:    "2026-09-16T01:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "execution.status", State: "succeeded"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() later error = %v", err)
	}
	laterConflict, err := human.RecordConflict("C-AFTER-DECISION", "運用条件に新しい対立が見つかった")
	if err != nil {
		t.Fatalf("RecordConflict() later error = %v", err)
	}
	laterRecommendation := lr("recommendation", "R-AFTER-DECISION")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         laterRecommendation,
		Statement:   "新しい対立を確認してから次の変更へ進む",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{laterObservation, laterConflict},
	}); err != nil {
		t.Fatalf("RecordRecommendation() later error = %v", err)
	}

	projection, err := human.ChangeReviewProjection(decision)
	if err != nil {
		t.Fatalf("ChangeReviewProjection() error = %v", err)
	}
	if len(projection.Resume.Basis) != 1 || projection.Resume.Basis[0].Ref != basis {
		t.Fatalf("historical basis = %#v, want only %v", projection.Resume.Basis, basis)
	}
	if len(projection.Resume.Unresolved) != 1 || projection.Resume.Unresolved[0].Ref != oldConflict {
		t.Fatalf("historical unresolved = %#v, want only %v", projection.Resume.Unresolved, oldConflict)
	}

	gotChanges := make([]semanticruntime.LogicalReference, 0, len(projection.CanonicalChanges))
	for _, change := range projection.CanonicalChanges {
		gotChanges = append(gotChanges, change.Ref)
	}
	wantChanges := []semanticruntime.LogicalReference{laterObservation, laterConflict, laterRecommendation}
	if !reflect.DeepEqual(gotChanges, wantChanges) {
		t.Fatalf("canonical changes = %#v, want %#v", gotChanges, wantChanges)
	}
	for _, change := range projection.CanonicalChanges {
		if change.Ref == basis || change.Ref == oldConflict {
			t.Fatalf("historical record leaked into canonical changes: %#v", projection.CanonicalChanges)
		}
	}
}

func TestChangeReviewProjectionReconstructsFromCanonicalRecordsAfterStoreRebuild(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, _ := human.StartInquiry("I-REBUILD-REVIEW", "checkpointをcanonical Decision recordから再構成する")
	decision := lr("decision", "D-REBUILD-REVIEW")
	if err := human.RecordDecisionWithReviewCheckpoint(DecisionInput{
		Ref:         decision,
		Statement:   "checkpoint付きDecisionを記録する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordDecisionWithReviewCheckpoint() error = %v", err)
	}
	change := lr("capability_observation", "CO-REBUILD-REVIEW")
	capability := lr("capability", "CAP-REBUILD-REVIEW")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           change,
		CapabilityRef: &capability,
		ObservedAt:    "2026-09-16T02:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() error = %v", err)
	}

	before, err := human.ChangeReviewProjection(decision)
	if err != nil {
		t.Fatalf("ChangeReviewProjection() before rebuild error = %v", err)
	}

	records, err := store.Records()
	if err != nil {
		t.Fatalf("Records() error = %v", err)
	}
	rebuiltStore := NewCanonicalStore()
	for _, record := range records {
		if err := rebuiltStore.Add(record); err != nil {
			t.Fatalf("rebuiltStore.Add() error = %v", err)
		}
	}
	rebuiltHuman := NewHumanSurface(rebuiltStore)
	after, err := rebuiltHuman.ChangeReviewProjection(decision)
	if err != nil {
		t.Fatalf("ChangeReviewProjection() after rebuild error = %v", err)
	}
	if !reflect.DeepEqual(before, after) {
		t.Fatalf("change review changed after canonical rebuild:\nbefore=%#v\nafter=%#v", before, after)
	}
}

func TestChangeReviewProjectionFailsClosedWithoutCheckpoint(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, _ := human.StartInquiry("I-NO-CHECKPOINT", "legacy Decisionではrecord順序を時間意味へ読み替えない")
	decision := lr("decision", "D-NO-CHECKPOINT")
	if err := human.RecordDecision(DecisionInput{
		Ref:         decision,
		Statement:   "checkpointを持たないlegacy Decision",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}
	change := lr("capability_observation", "CO-NO-CHECKPOINT")
	capability := lr("capability", "CAP-NO-CHECKPOINT")
	if err := machine.RecordCapabilityObservation(CapabilityObservationInput{
		Ref:           change,
		CapabilityRef: &capability,
		ObservedAt:    "2026-09-16T03:00:00Z",
		Conditions:    []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
	}); err != nil {
		t.Fatalf("RecordCapabilityObservation() error = %v", err)
	}

	if _, err := human.ChangeReviewProjection(decision); err == nil {
		t.Fatal("ChangeReviewProjection() inferred changes without an explicit checkpoint")
	}
}
