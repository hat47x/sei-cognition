package interactionprobe

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestProgressiveExplicitnessPreservesInquiryIdentityAsDetailAccumulates(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	// 最初は問いだけで開始し、最大field setを要求しない。
	inquiry, err := human.StartInquiry("I-PROGRESSIVE", "移行候補を検討する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	initialInquiry, found, err := store.Find(inquiry)
	if err != nil {
		t.Fatalf("Find(inquiry) initial error = %v", err)
	}
	if !found {
		t.Fatal("initial inquiry was not canonicalized")
	}
	minimal, err := human.LightView()
	if err != nil {
		t.Fatalf("LightView() minimal error = %v", err)
	}
	if minimal.Inquiry.Ref != inquiry {
		t.Fatalf("minimal inquiry = %v, want %v", minimal.Inquiry.Ref, inquiry)
	}
	if len(minimal.Observations) != 0 || len(minimal.Unknowns) != 0 || len(minimal.Conflicts) != 0 || len(minimal.Recommendations) != 0 || len(minimal.Decisions) != 0 {
		t.Fatalf("minimal start required later-stage semantic records: %#v", minimal)
	}

	// 必要になった時点でbasis / unresolved / recommendationを後から追加する。
	observation, err := human.RecordManualObservation("O-PROGRESSIVE", "候補Aは必要機能を満たす")
	if err != nil {
		t.Fatalf("RecordManualObservation() error = %v", err)
	}
	unknown, err := human.RecordUnknown("U-PROGRESSIVE", "移行後の運用負荷は未確認")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}
	recommendation := lr("recommendation", "R-PROGRESSIVE")
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "候補Aを比較対象に残す",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		BasisRefs:   []semanticruntime.LogicalReference{observation},
	}); err != nil {
		t.Fatalf("RecordRecommendation() error = %v", err)
	}
	decision := lr("decision", "D-PROGRESSIVE")
	if err := human.RecordDecisionWithReviewCheckpoint(DecisionInput{
		Ref:                decision,
		Statement:          "候補Aで限定的な検証へ進む",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry},
		BasisRefs:          []semanticruntime.LogicalReference{observation},
		RecommendationRefs: []semanticruntime.LogicalReference{recommendation},
		UnresolvedRefs:     []semanticruntime.LogicalReference{unknown},
	}); err != nil {
		t.Fatalf("RecordDecisionWithReviewCheckpoint() error = %v", err)
	}

	// detail追加のためにInquiry自身を書き換えたり、新しいCase / Workspace identityへ
	// 置き換えたりしていないことを確認する。
	finalInquiry, found, err := store.Find(inquiry)
	if err != nil {
		t.Fatalf("Find(inquiry) final error = %v", err)
	}
	if !found {
		t.Fatal("inquiry disappeared after detail accumulation")
	}
	if !reflect.DeepEqual(initialInquiry, finalInquiry) {
		t.Fatalf("progressive detail rewrote root inquiry:\ninitial=%#v\nfinal=%#v", initialInquiry, finalInquiry)
	}

	resume, err := human.ResumeProjection(decision)
	if err != nil {
		t.Fatalf("ResumeProjection() error = %v", err)
	}
	if resume.Inquiry.Ref != inquiry {
		t.Fatalf("resume inquiry = %v, want original %v", resume.Inquiry.Ref, inquiry)
	}
	if len(resume.Basis) != 1 || resume.Basis[0].Ref != observation {
		t.Fatalf("resume basis = %#v, want %v", resume.Basis, observation)
	}
	if len(resume.Unresolved) != 1 || resume.Unresolved[0].Ref != unknown {
		t.Fatalf("resume unresolved = %#v, want %v", resume.Unresolved, unknown)
	}
	if len(resume.Recommendations) != 1 || resume.Recommendations[0].Ref != recommendation {
		t.Fatalf("resume recommendations = %#v, want %v", resume.Recommendations, recommendation)
	}
}
