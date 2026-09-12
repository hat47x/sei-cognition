package hybridreasoning

import "testing"

func testCandidate(ref string, activation float32) Candidate {
	return Candidate{
		Ref: ref, Activation: activation,
		Meaning: map[string]any{
			"type": "Inquiry",
			"question": "ローカルMarkdownを主にするか",
			"unknowns": []map[string]any{{"summary": "外出先編集頻度は未確認"}},
		},
	}
}

func TestSymbolicTaskNeverCallsLocalModel(t *testing.T) {
	got := RouteReasoning(RoutingContext{Task: "historical-basis-check"})
	if got.Route != RouteSymbolic || got.LocalModelAllowed {
		t.Fatalf("unexpected route: %+v", got)
	}
}

func TestRecallTaskStaysNonLLM(t *testing.T) {
	got := RouteReasoning(RoutingContext{Task: "recall", CandidateCount: 2, NoveltySignal: 0.1})
	if got.Route != RouteNonLLMRecall {
		t.Fatalf("unexpected route: %+v", got)
	}
}

func TestBoundedSynthesisCanUseLocalSLM(t *testing.T) {
	got := RouteReasoning(RoutingContext{Task: "synthesize", CandidateCount: 2, NoveltySignal: 0.2})
	if got.Route != RouteLocalSLM || !got.LocalModelAllowed || got.CanonicalWriteAllowed {
		t.Fatalf("unexpected route: %+v", got)
	}
}

func TestHighNoveltyExpandsEvidence(t *testing.T) {
	got := RouteReasoning(RoutingContext{Task: "compare", CandidateCount: 1, NoveltySignal: 0.95})
	if got.Route != RouteExpandEvidence || got.LocalModelAllowed {
		t.Fatalf("unexpected route: %+v", got)
	}
}

func TestHighStakesRequiresReview(t *testing.T) {
	got := RouteReasoning(RoutingContext{Task: "compare", CandidateCount: 1, NoveltySignal: 0.1, HighStakes: true})
	if got.Route != RouteHumanOrStrongerReview {
		t.Fatalf("unexpected route: %+v", got)
	}
}

func TestCurrentFactRequiresEvidence(t *testing.T) {
	got := RouteReasoning(RoutingContext{Task: "synthesize", CandidateCount: 1, NoveltySignal: 0.1, RequiresCurrentExternalFact: true})
	if got.Route != RouteExternalEvidence {
		t.Fatalf("unexpected route: %+v", got)
	}
}

func TestWorkingSetIsBoundedProposalOnlyAndCloned(t *testing.T) {
	candidates := make([]Candidate, 12)
	for i := range candidates {
		candidates[i] = testCandidate(string(rune('a'+i)), 1-float32(i)/100)
	}
	originalQuestion := candidates[0].Meaning["question"].(string)
	got := BuildWorkingSet(
		"AとBを比較する", "compare", candidates,
		[]map[string]any{{"kind": "unknown", "summary": "価格改定は未確認"}},
		[]string{"Decisionを自動確定しない"},
		WorkingSetOptions{MaxCandidates: 4, MaxTextChars: 100},
	)
	if len(got.Candidates) != 4 {
		t.Fatalf("working set size = %d", len(got.Candidates))
	}
	if !got.SemanticBoundary.OutputIsProposalOnly || !got.SemanticBoundary.MustPreserveUnknownAndConflict || !got.SemanticBoundary.MustCiteCandidateRefsForMaterialClaims {
		t.Fatalf("semantic boundary missing: %+v", got.SemanticBoundary)
	}
	got.Candidates[0].Meaning["question"] = "mutated"
	if candidates[0].Meaning["question"] != originalQuestion {
		t.Fatal("working set mutated caller meaning")
	}
}

func TestWorkingSetClipsLongText(t *testing.T) {
	got := BuildWorkingSet("q", "synthesize", []Candidate{{
		Ref: "x", Activation: 0.9, Meaning: map[string]any{"summary": string(make([]byte, 5000))},
	}}, nil, nil, WorkingSetOptions{MaxTextChars: 100})
	if len([]rune(got.Candidates[0].Meaning["summary"].(string))) > 100 {
		t.Fatal("text was not clipped")
	}
}
