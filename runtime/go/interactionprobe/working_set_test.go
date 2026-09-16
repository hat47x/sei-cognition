package interactionprobe

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestWorkingSetProjectionRebuildsFromCanonicalRelationsAfterLocalStateLoss(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-WORKING-SET", "canonical relationだけからworking setを再構成する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	observation, err := human.RecordManualObservation("O-WORKING-SET", "比較対象Aには必要な機能がある")
	if err != nil {
		t.Fatalf("RecordManualObservation() error = %v", err)
	}
	unknown, err := human.RecordUnknown("U-WORKING-SET", "運用負荷は未確認")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}
	recommendation := lr("recommendation", "R-WORKING-SET")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "運用負荷を確認しつつ候補Aを残す",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{observation},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}
	decision := lr("decision", "D-WORKING-SET")
	if err := human.RecordDecision(DecisionInput{
		Ref:                decision,
		Statement:          "候補Aを次段階へ進める",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry},
		BasisRefs:          []semanticruntime.LogicalReference{observation},
		RecommendationRefs: []semanticruntime.LogicalReference{recommendation},
		UnresolvedRefs:     []semanticruntime.LogicalReference{unknown},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}

	// 同じcanonical storeに存在しても、明示Reference graphへ接続されないrecordは
	// working setへ暗黙混入させない。
	detached, err := human.RecordManualObservation("O-DETACHED", "別の検討に属する未接続メモ")
	if err != nil {
		t.Fatalf("RecordManualObservation() detached error = %v", err)
	}

	beforeDigest, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}
	before, err := human.WorkingSetProjection(decision)
	if err != nil {
		t.Fatalf("WorkingSetProjection() before error = %v", err)
	}
	if before.CanonicalDigest != beforeDigest {
		t.Fatalf("working set digest = %s, want %s", before.CanonicalDigest, beforeDigest)
	}
	if containsAuditRef(before.Records, detached) {
		t.Fatalf("detached record leaked into working set: %#v", before.Records)
	}
	for _, want := range []semanticruntime.LogicalReference{inquiry, observation, unknown, recommendation, decision} {
		if !containsAuditRef(before.Records, want) {
			t.Fatalf("working set missing related record %v: %#v", want, before.Records)
		}
	}

	// pin / recent / filter相当のSurface-local stateを作ってから失わせる。
	human.SetLocalState("pin", recommendation.ID)
	human.SetLocalState("filter", "unresolved")
	human.SetLocalState("recent", decision.ID)
	human.ResetLocalState()

	reopened := NewHumanSurface(store)
	after, err := reopened.WorkingSetProjection(decision)
	if err != nil {
		t.Fatalf("WorkingSetProjection() after local state loss error = %v", err)
	}
	if !reflect.DeepEqual(before, after) {
		t.Fatalf("working set changed after local state loss:\nbefore=%#v\nafter=%#v", before, after)
	}
	afterDigest, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after error = %v", err)
	}
	if beforeDigest != afterDigest {
		t.Fatalf("working set rebuild changed canonical state: before=%s after=%s", beforeDigest, afterDigest)
	}
}

func containsAuditRef(records []AuditRecord, target semanticruntime.LogicalReference) bool {
	for _, record := range records {
		if record.Ref == target {
			return true
		}
	}
	return false
}
