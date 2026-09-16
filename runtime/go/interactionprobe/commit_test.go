package interactionprobe

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestCommitCoordinatorPublishesSemanticChangesTogether(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	if _, err := human.StartInquiry("I-ATOMIC-COMMIT", "複数のcanonical changeを一つの操作として公開する"); err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}

	unknown := opaqueRuntimeRecord(t, "unknown", "U-ATOMIC-COMMIT", "確認待ちの論点")
	conflict := opaqueRuntimeRecord(t, "conflict", "C-ATOMIC-COMMIT", "観測結果に不一致がある")
	coordinator := NewCommitCoordinator(store)
	if err := coordinator.Commit(SemanticChangePlan{Records: []semanticruntime.RuntimeRecord{unknown, conflict}}); err != nil {
		t.Fatalf("Commit() error = %v", err)
	}

	for _, ref := range []semanticruntime.LogicalReference{
		lr("unknown", "U-ATOMIC-COMMIT"),
		lr("conflict", "C-ATOMIC-COMMIT"),
	} {
		if _, found, err := store.Find(ref); err != nil {
			t.Fatalf("Find(%v) error = %v", ref, err)
		} else if !found {
			t.Fatalf("Find(%v) found = false after successful commit", ref)
		}
	}
}

func TestCommitCoordinatorDoesNotExposePartialStateOnInjectedFailure(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	if _, err := human.StartInquiry("I-ATOMIC-FAULT", "commit途中のfailureで半端なcanonical stateを公開しない"); err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	firstRef := lr("unknown", "U-ATOMIC-FAULT")
	secondRef := lr("conflict", "C-ATOMIC-FAULT")
	plan := SemanticChangePlan{Records: []semanticruntime.RuntimeRecord{
		opaqueRuntimeRecord(t, firstRef.Kind, firstRef.ID, "先にstagingされる変更"),
		opaqueRuntimeRecord(t, secondRef.Kind, secondRef.ID, "後続の変更"),
	}}

	coordinator := NewCommitCoordinator(store)
	err = coordinator.commitWithProbeFault(plan, 0)
	if err == nil || !strings.Contains(err.Error(), "injected commit failure") {
		t.Fatalf("commitWithProbeFault() error = %v, want injected failure", err)
	}

	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after error = %v", err)
	}
	if before != after {
		t.Fatalf("failed commit changed canonical state: before=%s after=%s", before, after)
	}
	for _, ref := range []semanticruntime.LogicalReference{firstRef, secondRef} {
		if _, found, err := store.Find(ref); err != nil {
			t.Fatalf("Find(%v) error = %v", ref, err)
		} else if found {
			t.Fatalf("failed commit exposed partial record %v", ref)
		}
	}
}

func TestCommitCoordinatorDoesNotPublishEarlierChangesWhenLaterValidationFails(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	if _, err := human.StartInquiry("I-ATOMIC-VALIDATION", "後続validation failureでも先行変更を公開しない"); err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	firstRef := lr("unknown", "U-ATOMIC-VALIDATION")
	invalidRef := lr("conflict", "C-ATOMIC-VALIDATION")
	invalid := semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{Kind: invalidRef.Kind, LogicalRef: &invalidRef},
		Status:         semanticruntime.RecordValidated,
	}
	coordinator := NewCommitCoordinator(store)
	err = coordinator.Commit(SemanticChangePlan{Records: []semanticruntime.RuntimeRecord{
		opaqueRuntimeRecord(t, firstRef.Kind, firstRef.ID, "validation前にstagingされる変更"),
		invalid,
	}})
	if err == nil || !strings.Contains(err.Error(), "must remain not_verified") {
		t.Fatalf("Commit() error = %v, want opaque validation rejection", err)
	}

	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after error = %v", err)
	}
	if before != after {
		t.Fatalf("validation failure changed canonical state: before=%s after=%s", before, after)
	}
	if _, found, err := store.Find(firstRef); err != nil {
		t.Fatalf("Find(%v) error = %v", firstRef, err)
	} else if found {
		t.Fatalf("validation failure exposed earlier staged record %v", firstRef)
	}
}

func opaqueRuntimeRecord(t *testing.T, kind, id, text string) semanticruntime.RuntimeRecord {
	t.Helper()
	ref := lr(kind, id)
	payload, err := json.Marshal(opaqueTextPayload{Text: text})
	if err != nil {
		t.Fatalf("json.Marshal() error = %v", err)
	}
	return semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{Kind: kind, LogicalRef: &ref, Payload: payload},
		Status:         semanticruntime.RecordNotVerified,
	}
}
