package interactionprobe

import "testing"

func TestSurfaceOnlyRecommendationAndDecisionDoNotBecomeCanonicalRecords(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)
	machine := NewMachineSurface(store)

	if _, err := human.StartInquiry("I-001", "Surfaceだけにある情報をcanonical meaningと混同しない"); err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}

	// 会話履歴や画面状態を模したlocal stateに、それらしい内容を置いても、
	// canonical recordとしては扱われないことを確認する。
	machine.SetLocalState("chat-recommendation", "この内容は会話履歴にしか存在しない")
	human.SetLocalState("ui-decision", "この内容は画面状態にしか存在しない")

	view, err := human.LightView()
	if err != nil {
		t.Fatalf("LightView() error = %v", err)
	}
	if len(view.Recommendations) != 0 {
		t.Fatalf("surface-only recommendation leaked into canonical Projection: %#v", view.Recommendations)
	}
	if len(view.Decisions) != 0 {
		t.Fatalf("surface-only decision leaked into canonical Projection: %#v", view.Decisions)
	}

	records, err := store.Records()
	if err != nil {
		t.Fatalf("Records() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("canonical record count = %d, want only the inquiry", len(records))
	}

	machine.ResetLocalState()
	human.ResetLocalState()
	view, err = human.LightView()
	if err != nil {
		t.Fatalf("LightView() after reset error = %v", err)
	}
	if len(view.Recommendations) != 0 || len(view.Decisions) != 0 {
		t.Fatalf("reset local state changed canonical Projection: %#v", view)
	}
}
