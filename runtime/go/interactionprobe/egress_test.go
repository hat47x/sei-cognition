package interactionprobe

import (
	"errors"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestContextEgressPlanContainsOnlySelectedCanonicalRecords(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-EGRESS", "必要なcontextだけをexternal AIへ渡す")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	unknown, err := human.RecordUnknown("U-EGRESS", "まだ確認できていない条件")
	if err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}
	unselected, err := human.RecordConflict("C-EGRESS-PRIVATE", "今回のAI呼び出しには渡さない別論点")
	if err != nil {
		t.Fatalf("RecordConflict() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	plan, err := machine.PlanContextEgress([]semanticruntime.LogicalReference{inquiry, unknown})
	if err != nil {
		t.Fatalf("PlanContextEgress() error = %v", err)
	}
	if plan.CanonicalDigest != before {
		t.Fatalf("egress digest = %s, want %s", plan.CanonicalDigest, before)
	}
	if len(plan.Records) != 2 || plan.Records[0].Ref != inquiry || plan.Records[1].Ref != unknown {
		t.Fatalf("egress records = %#v, want only selected refs", plan.Records)
	}
	for _, record := range plan.Records {
		if record.Ref == unselected {
			t.Fatalf("non-selected canonical data leaked into egress plan: %#v", plan.Records)
		}
	}
	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after error = %v", err)
	}
	if before != after {
		t.Fatalf("context egress planning changed canonical state: before=%s after=%s", before, after)
	}
}

func TestExternalRecommendationRemainsProvisionalUntilExplicitCommit(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-EGRESS-PROVISIONAL", "external AI responseをprovisionalに保つ")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	plan, err := machine.PlanContextEgress([]semanticruntime.LogicalReference{inquiry})
	if err != nil {
		t.Fatalf("PlanContextEgress() error = %v", err)
	}
	beforeResponse, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before response error = %v", err)
	}

	recommendation := lr("recommendation", "R-EGRESS-PROVISIONAL")
	draft, err := machine.ReceiveExternalRecommendation(plan, RecommendationInput{
		Ref:         recommendation,
		Statement:   "追加Evidenceを確認してから進める",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err != nil {
		t.Fatalf("ReceiveExternalRecommendation() error = %v", err)
	}
	preview, err := draft.Preview()
	if err != nil {
		t.Fatalf("Preview() error = %v", err)
	}
	if preview.Ref != recommendation || preview.Statement == "" {
		t.Fatalf("preview = %#v", preview)
	}

	afterResponse, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after response error = %v", err)
	}
	if beforeResponse != afterResponse {
		t.Fatalf("receiving external response changed canonical state: before=%s after=%s", beforeResponse, afterResponse)
	}
	if _, found, err := store.Find(recommendation); err != nil {
		t.Fatalf("Find() before commit error = %v", err)
	} else if found {
		t.Fatal("external response became canonical without explicit commit")
	}

	if err := draft.Commit(); err != nil {
		t.Fatalf("Commit() error = %v", err)
	}
	if _, found, err := store.Find(recommendation); err != nil {
		t.Fatalf("Find() after commit error = %v", err)
	} else if !found {
		t.Fatal("explicitly committed recommendation was not canonicalized")
	}
}

func TestExternalRecommendationUsesEgressSnapshotForStaleProtection(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	inquiry, err := human.StartInquiry("I-EGRESS-STALE", "external round trip中のcanonical changeを検出する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	plan, err := machine.PlanContextEgress([]semanticruntime.LogicalReference{inquiry})
	if err != nil {
		t.Fatalf("PlanContextEgress() error = %v", err)
	}
	if _, err := human.RecordConflict("C-EGRESS-STALE", "AI応答待ちの間に新しい対立が見つかった"); err != nil {
		t.Fatalf("RecordConflict() error = %v", err)
	}

	recommendation := lr("recommendation", "R-EGRESS-STALE")
	draft, err := machine.ReceiveExternalRecommendation(plan, RecommendationInput{
		Ref:         recommendation,
		Statement:   "送出時点のcontextだけに基づく提案",
		ContextRefs: []semanticruntime.LogicalReference{inquiry},
	})
	if err != nil {
		t.Fatalf("ReceiveExternalRecommendation() error = %v", err)
	}
	if err := draft.Commit(); !errors.Is(err, errStaleProvisionalRecommendation) {
		t.Fatalf("Commit() error = %v, want stale provisional rejection", err)
	}
	if _, found, err := store.Find(recommendation); err != nil {
		t.Fatalf("Find() error = %v", err)
	} else if found {
		t.Fatal("stale external recommendation was committed")
	}
}
