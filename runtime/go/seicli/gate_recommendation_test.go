package seicli

import (
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// recommendationBundle builds a synthetic bundle in memory. It is not read
// through the CLI, so it can hold exact-form references that `sei add` cannot
// write yet (#686).
func recommendationBundle(recs []semanticruntime.LogicalReference, decisions ...*semanticruntime.Decision) *semanticruntime.Bundle {
	bundle := &semanticruntime.Bundle{}
	for i := range recs {
		bundle.Records = append(bundle.Records, semanticruntime.RuntimeRecord{
			Decision: &semanticruntime.DecisionMemoryDocument{
				Recommendation: &semanticruntime.Recommendation{Ref: recs[i], Statement: "r"},
			},
		})
	}
	for _, d := range decisions {
		bundle.Records = append(bundle.Records, semanticruntime.RuntimeRecord{
			Decision: &semanticruntime.DecisionMemoryDocument{Decision: d},
		})
	}
	return bundle
}

func logicalRecRef(id, scope string) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: "recommendation", ID: id, Scope: scope}
}

func exactRecRef(id, scope string) semanticruntime.Reference {
	return semanticruntime.Reference{
		LogicalRef:            &semanticruntime.LogicalReference{Kind: "recommendation", ID: id, Scope: scope},
		ContentDigest:         "sha256:" + "0000000000000000000000000000000000000000000000000000000000000000",
		RepresentationProfile: &semanticruntime.RepresentationProfile{ProfileID: "synthetic", Version: "1"},
	}
}

func decisionRelying(id string, refs ...semanticruntime.Reference) *semanticruntime.Decision {
	return &semanticruntime.Decision{
		Ref:                semanticruntime.LogicalReference{Kind: "decision", ID: id},
		Statement:          "s",
		RecommendationRefs: refs,
	}
}

func TestGateRelianceMatchesKindIDAndScopeForLogicalAndExactRefs(t *testing.T) {
	recorded := []semanticruntime.LogicalReference{{Kind: "recommendation", ID: "R1", Scope: "team-a"}}
	cases := []struct {
		name string
		ref  semanticruntime.Reference
		want string
	}{
		{"logical, recorded", logicalRecRef("R1", "team-a"), "allow"},
		{"exact, recorded", exactRecRef("R1", "team-a"), "allow"},
		{"logical, not recorded", logicalRecRef("R2", "team-a"), "deny"},
		{"exact, not recorded", exactRecRef("R2", "team-a"), "deny"},
		{"logical, same id other scope", logicalRecRef("R1", "team-b"), "deny"},
		{"exact, same id other scope", exactRecRef("R1", "team-b"), "deny"},
		{"logical, same id without scope", logicalRecRef("R1", ""), "deny"},
		{"other kind with the recorded id", semanticruntime.Reference{Kind: "question", ID: "R1", Scope: "team-a"}, "deny"},
	}
	for _, c := range cases {
		bundle := recommendationBundle(recorded, decisionRelying("D", c.ref))
		got := CheckDecision(bundle, "D", GatePolicy{RequireRecommendation: true})
		if got.Verdict != c.want {
			t.Errorf("%s: verdict = %s, want %s (%v)", c.name, got.Verdict, c.want, got.Reasons)
		}
	}
}

func TestGateAndResumeAgreeOnWhichRecommendationsAreRelied(t *testing.T) {
	recorded := []semanticruntime.LogicalReference{
		{Kind: "recommendation", ID: "R1", Scope: "team-a"},
		{Kind: "recommendation", ID: "R1", Scope: "team-b"},
		{Kind: "recommendation", ID: "R2"},
	}
	bundle := recommendationBundle(recorded,
		decisionRelying("D-exact", exactRecRef("R1", "team-a")),
		decisionRelying("D-logical", logicalRecRef("R2", "")),
		decisionRelying("D-missing", exactRecRef("R9", "team-a")),
	)

	view := BuildResume(bundle)
	if len(view.RecommendationsRelied) != 2 || len(view.RecommendationsOpen) != 1 {
		t.Fatalf("resume relied=%d open=%d, want 2 and 1: %+v", len(view.RecommendationsRelied), len(view.RecommendationsOpen), view)
	}

	// The same recorded recommendations must give the same answer in the gate.
	want := map[string]string{"D-exact": "allow", "D-logical": "allow", "D-missing": "deny"}
	for id, verdict := range want {
		if got := CheckDecision(bundle, id, GatePolicy{RequireRecommendation: true}); got.Verdict != verdict {
			t.Errorf("%s: gate verdict = %s, want %s", id, got.Verdict, verdict)
		}
	}
}
