package interactionprobe

import (
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestProvisionalRecommendationDoesNotBecomeCanonicalUntilCommit(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-DRAFT", "AI提案を確認してからcanonicalへ反映する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	draft, err := machine.ProposeRecommendation(RecommendationInput{
		Ref:         lr("recommendation", "R-DRAFT"),
		Statement:   "最初のAI提案を採用する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err != nil {
		t.Fatalf("ProposeRecommendation() error = %v", err)
	}
	preview, err := draft.Preview()
	if err != nil {
		t.Fatalf("Preview() error = %v", err)
	}
	if preview.Statement != "最初のAI提案を採用する" {
		t.Fatalf("Preview().Statement = %q", preview.Statement)
	}

	afterPreview, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after preview error = %v", err)
	}
	if before != afterPreview {
		t.Fatalf("provisional preview changed canonical state: before=%s after=%s", before, afterPreview)
	}

	if err := draft.Revise(RecommendationInput{
		Ref:         lr("recommendation", "R-DRAFT"),
		Statement:   "条件を確認してから限定的に採用する",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
		Rationale:   "AI提案をそのままDecisionへ進めず、条件を明示した",
	}); err != nil {
		t.Fatalf("Revise() error = %v", err)
	}

	afterRevise, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after revise error = %v", err)
	}
	if before != afterRevise {
		t.Fatalf("draft revision changed canonical state: before=%s after=%s", before, afterRevise)
	}

	if err := draft.Commit(); err != nil {
		t.Fatalf("Commit() error = %v", err)
	}
	afterCommit, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after commit error = %v", err)
	}
	if before == afterCommit {
		t.Fatal("Commit() did not change canonical state")
	}

	got, err := machine.ReadRecommendation(lr("recommendation", "R-DRAFT"))
	if err != nil {
		t.Fatalf("ReadRecommendation() error = %v", err)
	}
	if got.Statement != "条件を確認してから限定的に採用する" {
		t.Fatalf("canonical recommendation statement = %q", got.Statement)
	}
	if err := draft.Commit(); err == nil {
		t.Fatal("second Commit() unexpectedly succeeded")
	}
}

func TestDismissedProvisionalRecommendationLeavesCanonicalStateUntouched(t *testing.T) {
	store := NewCanonicalStore()
	machine := NewMachineSurface(store)
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	draft, err := machine.ProposeRecommendation(RecommendationInput{
		Ref:       lr("recommendation", "R-DISMISS"),
		Statement: "このAI提案は却下する",
	})
	if err != nil {
		t.Fatalf("ProposeRecommendation() error = %v", err)
	}
	if err := draft.Dismiss(); err != nil {
		t.Fatalf("Dismiss() error = %v", err)
	}
	if err := draft.Commit(); err == nil {
		t.Fatal("Commit() succeeded after dismissal")
	}
	if _, err := machine.ReadRecommendation(lr("recommendation", "R-DISMISS")); err == nil {
		t.Fatal("dismissed draft appeared in canonical state")
	}

	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after dismissal error = %v", err)
	}
	if before != after {
		t.Fatalf("dismissal changed canonical state: before=%s after=%s", before, after)
	}
}

func TestFailedDraftCommitRemainsCorrectable(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)
	inquiry, err := human.StartInquiry("I-CONFLICT", "commit failure後もdraftを修正できる")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	ref := lr("recommendation", "R-CONFLICT")

	draft, err := machine.ProposeRecommendation(RecommendationInput{
		Ref:         ref,
		Statement:   "draft recommendation",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err != nil {
		t.Fatalf("ProposeRecommendation() error = %v", err)
	}
	if err := machine.RecordRecommendation(RecommendationInput{
		Ref:         ref,
		Statement:   "canonical recommendation written first",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("RecordRecommendation() setup error = %v", err)
	}

	if err := draft.Commit(); err == nil {
		t.Fatal("Commit() unexpectedly succeeded with duplicate canonical ref")
	}
	if err := draft.Revise(RecommendationInput{
		Ref:         lr("recommendation", "R-CORRECTED"),
		Statement:   "duplicateを解消した修正版",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	}); err != nil {
		t.Fatalf("Revise() after failed commit error = %v", err)
	}
	if err := draft.Commit(); err != nil {
		t.Fatalf("Commit() after correction error = %v", err)
	}
	got, err := machine.ReadRecommendation(lr("recommendation", "R-CORRECTED"))
	if err != nil {
		t.Fatalf("ReadRecommendation() corrected error = %v", err)
	}
	if got.Statement != "duplicateを解消した修正版" {
		t.Fatalf("corrected canonical statement = %q", got.Statement)
	}
}
