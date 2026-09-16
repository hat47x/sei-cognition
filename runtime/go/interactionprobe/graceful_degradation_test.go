package interactionprobe

import (
	"errors"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

var errTestAIAssistanceUnavailable = errors.New("test AI assistance unavailable")

type unavailableRecommendationAssistant struct{}

func (unavailableRecommendationAssistant) ProposeRecommendation(RecommendationInput) (*ProvisionalRecommendation, error) {
	return nil, errTestAIAssistanceUnavailable
}

func TestAIUnavailableKeepsHumanCanonicalPathUsable(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)

	inquiry, err := human.StartInquiry("I-AI-UNAVAILABLE", "AIが使えなくても判断仕事を継続できるか確認する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}

	beforeFailure, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before AI failure error = %v", err)
	}
	assistant := unavailableRecommendationAssistant{}
	if _, err := assistant.ProposeRecommendation(RecommendationInput{
		Ref:         lr("recommendation", "R-AI-UNAVAILABLE"),
		Statement:   "AIが使えないので判断を中止する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); !errors.Is(err, errTestAIAssistanceUnavailable) {
		t.Fatalf("ProposeRecommendation() error = %v, want AI unavailable", err)
	}
	afterFailure, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after AI failure error = %v", err)
	}
	if beforeFailure != afterFailure {
		t.Fatalf("AI availability failure changed canonical state: before=%s after=%s", beforeFailure, afterFailure)
	}

	auditAfterFailure, err := human.AuditView()
	if err != nil {
		t.Fatalf("AuditView() after AI failure error = %v", err)
	}
	if len(auditAfterFailure.Records) != 1 || auditAfterFailure.Records[0].Ref != inquiry {
		t.Fatalf("AI failure was flattened into canonical business meaning: %#v", auditAfterFailure.Records)
	}

	observation, err := human.RecordManualObservation("O-MANUAL-AI-DOWN", "外部資料では移行先Providerの主要機能を利用できる")
	if err != nil {
		t.Fatalf("RecordManualObservation() error = %v", err)
	}
	conflict, err := human.RecordConflict("C-AI-DOWN", "運用実績はまだ確認できていない")
	if err != nil {
		t.Fatalf("RecordConflict() error = %v", err)
	}

	decision := lr("decision", "D-AI-UNAVAILABLE")
	if err := human.RecordDecisionWithReviewCheckpoint(DecisionInput{
		Ref:            decision,
		Statement:      "AIの復旧を待たず、人間が確認できた範囲で限定的に進める",
		ContextRefs:    []semanticruntime.LogicalReference{inquiry},
		BasisRefs:      []semanticruntime.LogicalReference{observation},
		UnresolvedRefs: []semanticruntime.LogicalReference{conflict},
	}); err != nil {
		t.Fatalf("RecordDecisionWithReviewCheckpoint() error = %v", err)
	}

	audit, err := human.AuditView()
	if err != nil {
		t.Fatalf("AuditView() error = %v", err)
	}
	manualFound := false
	for _, record := range audit.Records {
		if record.Ref != observation {
			continue
		}
		manualFound = true
		if record.Kind != "observation" {
			t.Fatalf("manual observation kind = %q, want observation", record.Kind)
		}
		if record.Status != semanticruntime.RecordNotVerified {
			t.Fatalf("manual observation status = %q, want not_verified", record.Status)
		}
		if record.Statement == "" {
			t.Fatal("manual observation lost its human-entered text")
		}
	}
	if !manualFound {
		t.Fatalf("manual observation %v not found in audit view", observation)
	}

	review, err := human.ChangeReviewProjection(decision)
	if err != nil {
		t.Fatalf("ChangeReviewProjection() before later change error = %v", err)
	}
	if len(review.Resume.Basis) != 1 || review.Resume.Basis[0].Ref != observation {
		t.Fatalf("resume basis = %#v, want manual observation %v", review.Resume.Basis, observation)
	}
	if len(review.CanonicalChanges) != 0 {
		t.Fatalf("unexpected canonical changes before later manual input: %#v", review.CanonicalChanges)
	}

	laterObservation, err := human.RecordManualObservation("O-MANUAL-AFTER-DECISION", "限定移行後の手動確認では主要操作が完了した")
	if err != nil {
		t.Fatalf("RecordManualObservation() later error = %v", err)
	}
	review, err = human.ChangeReviewProjection(decision)
	if err != nil {
		t.Fatalf("ChangeReviewProjection() after later change error = %v", err)
	}
	if len(review.CanonicalChanges) != 1 || review.CanonicalChanges[0].Ref != laterObservation {
		t.Fatalf("canonical changes = %#v, want later manual observation %v", review.CanonicalChanges, laterObservation)
	}

	// AI sessionやSurface stateを引き継がずHumanSurfaceを作り直し、canonical stateだけから再開する。
	reopened := NewHumanSurface(store)
	resume, err := reopened.ResumeProjection(decision)
	if err != nil {
		t.Fatalf("ResumeProjection() after reopen error = %v", err)
	}
	if resume.Decision.Ref != decision {
		t.Fatalf("reopened decision = %v, want %v", resume.Decision.Ref, decision)
	}
	if len(resume.Basis) != 1 || resume.Basis[0].Ref != observation {
		t.Fatalf("reopened basis = %#v, want manual observation %v", resume.Basis, observation)
	}
	reopenedReview, err := reopened.ChangeReviewProjection(decision)
	if err != nil {
		t.Fatalf("ChangeReviewProjection() after reopen error = %v", err)
	}
	if len(reopenedReview.CanonicalChanges) != 1 || reopenedReview.CanonicalChanges[0].Ref != laterObservation {
		t.Fatalf("reopened canonical changes = %#v, want %v", reopenedReview.CanonicalChanges, laterObservation)
	}
}
