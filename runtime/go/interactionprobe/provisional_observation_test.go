package interactionprobe

import (
	"errors"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestProvisionalRecommendationCanBeReclassifiedAsObservationBeforeCommit(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-RECLASSIFY", "AI suggestionの意味種別をcommit前に修正する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	recommendation := lr("recommendation", "R-WRONG-KIND")
	draft, err := machine.ProposeRecommendation(RecommendationInput{
		Ref:         recommendation,
		Statement:   "候補Aを進めるべきだ",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err != nil {
		t.Fatalf("ProposeRecommendation() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before reclassification error = %v", err)
	}

	observationRef := lr("observation", "O-RECLASSIFIED")
	observation, err := draft.ReclassifyAsObservation(observationRef, "資料には候補Aが要件Xを満たすと記載されている")
	if err != nil {
		t.Fatalf("ReclassifyAsObservation() error = %v", err)
	}
	if _, err := draft.Preview(); err == nil {
		t.Fatal("original recommendation draft remained usable after reclassification")
	}
	preview, err := observation.Preview()
	if err != nil {
		t.Fatalf("Observation Preview() error = %v", err)
	}
	if preview.Ref != observationRef || preview.Text == "" {
		t.Fatalf("observation preview = %#v", preview)
	}

	afterReclassification, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after reclassification error = %v", err)
	}
	if before != afterReclassification {
		t.Fatalf("reclassification changed canonical state: before=%s after=%s", before, afterReclassification)
	}
	if _, found, err := store.Find(recommendation); err != nil {
		t.Fatalf("Find(recommendation) error = %v", err)
	} else if found {
		t.Fatal("wrong-kind recommendation became canonical")
	}
	if _, found, err := store.Find(observationRef); err != nil {
		t.Fatalf("Find(observation) before commit error = %v", err)
	} else if found {
		t.Fatal("reclassified observation became canonical before explicit commit")
	}

	if err := observation.Commit(); err != nil {
		t.Fatalf("Observation Commit() error = %v", err)
	}
	record, found, err := store.Find(observationRef)
	if err != nil {
		t.Fatalf("Find(observation) after commit error = %v", err)
	}
	if !found {
		t.Fatal("reclassified observation was not canonicalized")
	}
	audit := auditRecord(record)
	if audit.Kind != "observation" || audit.Status != semanticruntime.RecordNotVerified {
		t.Fatalf("canonical observation = %#v", audit)
	}
	if _, found, err := store.Find(recommendation); err != nil {
		t.Fatalf("Find(recommendation) after observation commit error = %v", err)
	} else if found {
		t.Fatal("reclassification also canonicalized original recommendation")
	}
}

func TestReclassifiedObservationKeepsOriginalSnapshotPrecondition(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-RECLASSIFY-STALE", "再分類後もstale writeを防ぐ")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	draft, err := machine.ProposeRecommendation(RecommendationInput{
		Ref:         lr("recommendation", "R-RECLASSIFY-STALE"),
		Statement:   "古いsnapshotに基づく提案",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err != nil {
		t.Fatalf("ProposeRecommendation() error = %v", err)
	}
	observationRef := lr("observation", "O-RECLASSIFY-STALE")
	observation, err := draft.ReclassifyAsObservation(observationRef, "実際には観測内容だった")
	if err != nil {
		t.Fatalf("ReclassifyAsObservation() error = %v", err)
	}
	if _, err := human.RecordConflict("C-RECLASSIFY-STALE", "draft作成後に新しい対立が見つかった"); err != nil {
		t.Fatalf("RecordConflict() error = %v", err)
	}
	if err := observation.Commit(); !errors.Is(err, errStaleProvisionalRecommendation) {
		t.Fatalf("Observation Commit() error = %v, want stale rejection", err)
	}
	if _, found, err := store.Find(observationRef); err != nil {
		t.Fatalf("Find(observation) error = %v", err)
	} else if found {
		t.Fatal("stale reclassified observation was committed")
	}
}
