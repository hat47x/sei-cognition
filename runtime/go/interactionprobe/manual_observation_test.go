package interactionprobe

import "testing"

func TestManualObservationAppearsInLightView(t *testing.T) {
	store := NewCanonicalStore()
	human := NewHumanSurface(store)

	if _, err := human.StartInquiry("I-MANUAL-LIGHT", "AIなしのmanual Observationをlight viewで読む"); err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	observation, err := human.RecordManualObservation(
		"O-MANUAL-LIGHT",
		"人間が確認した資料では必要機能を利用できる",
	)
	if err != nil {
		t.Fatalf("RecordManualObservation() error = %v", err)
	}

	view, err := human.LightView()
	if err != nil {
		t.Fatalf("LightView() error = %v", err)
	}
	if len(view.Observations) != 1 {
		t.Fatalf("LightView().Observations = %#v, want one manual observation", view.Observations)
	}
	if view.Observations[0].Ref != observation {
		t.Fatalf("LightView observation ref = %v, want %v", view.Observations[0].Ref, observation)
	}
	if view.Observations[0].Text == "" {
		t.Fatal("LightView manual observation lost its text")
	}
}
