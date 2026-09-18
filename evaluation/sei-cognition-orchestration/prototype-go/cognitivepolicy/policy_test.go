package cognitivepolicy

import (
	"math"
	"reflect"
	"testing"
)

func testDefinitions() []ProblemPolicy {
	return []ProblemPolicy{
		{
			ProblemClass:            "routine-summary",
			StaticRoute:             "general-llm",
			AllowedRoutes: []RouteOption{
				{ID: "local-slm", EscalationLevel: 1},
				{ID: "general-llm", EscalationLevel: 2},
			},
			RequiredSuccessRate:     0.80,
			MinAssessedObservations: 5,
		},
		{
			ProblemClass:            "novel-analysis",
			StaticRoute:             "general-llm",
			AllowedRoutes: []RouteOption{
				{ID: "local-slm", EscalationLevel: 1},
				{ID: "general-llm", EscalationLevel: 2},
			},
			RequiredSuccessRate:     0.80,
			MinAssessedObservations: 5,
		},
	}
}

func outcomes(problemClass, route string, sufficient, insufficient, notAssessed, executionFailed int) []OutcomeRecord {
	var out []OutcomeRecord
	for i := 0; i < sufficient; i++ {
		out = append(out, OutcomeRecord{
			ProblemClass: problemClass, Route: route,
			CognitiveOutcome: CognitiveSufficient,
			ExecutionOutcome: ExecutionCompleted,
			ProvenanceRef: "fixture:assessed", ObservedPolicyVersion: BaselineVersion,
		})
	}
	for i := 0; i < insufficient; i++ {
		out = append(out, OutcomeRecord{
			ProblemClass: problemClass, Route: route,
			CognitiveOutcome: CognitiveInsufficient,
			ExecutionOutcome: ExecutionCompleted,
			ProvenanceRef: "fixture:assessed", ObservedPolicyVersion: BaselineVersion,
		})
	}
	for i := 0; i < notAssessed; i++ {
		execution := ExecutionNotRecorded
		if i < executionFailed {
			execution = ExecutionFailed
		}
		out = append(out, OutcomeRecord{
			ProblemClass: problemClass, Route: route,
			CognitiveOutcome: CognitiveNotAssessed,
			ExecutionOutcome: execution,
			ProvenanceRef: "fixture:not-assessed", ObservedPolicyVersion: BaselineVersion,
		})
	}
	return out
}

func TestCandidateIsNotActivatedImplicitly(t *testing.T) {
	store, err := NewStore(testDefinitions())
	if err != nil {
		t.Fatal(err)
	}
	records := outcomes("routine-summary", "local-slm", 9, 1, 0, 0)
	candidate, err := store.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	if candidate.Version != "v1" || candidate.ParentVersion != BaselineVersion {
		t.Fatalf("unexpected candidate identity: %#v", candidate)
	}
	if got := candidate.Selections["routine-summary"].Route; got != "local-slm" {
		t.Fatalf("candidate route=%s want local-slm", got)
	}
	if store.ActiveVersion() != BaselineVersion {
		t.Fatalf("candidate creation activated policy: %s", store.ActiveVersion())
	}
	route, err := store.Route("routine-summary")
	if err != nil {
		t.Fatal(err)
	}
	if route != "general-llm" {
		t.Fatalf("active route changed before explicit activation: %s", route)
	}
}

func TestCandidateUsesLowestEscalationRouteMeetingEvidenceFloor(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	records := append(
		outcomes("routine-summary", "local-slm", 8, 2, 0, 0),
		outcomes("routine-summary", "general-llm", 10, 0, 0, 0)...,
	)
	candidate, err := store.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	selection := candidate.Selections["routine-summary"]
	if selection.Route != "local-slm" {
		t.Fatalf("selected=%s want local-slm", selection.Route)
	}
	if selection.Stats.Assessed != 10 || selection.Stats.Sufficient != 8 || selection.Stats.SuccessRate != 0.8 {
		t.Fatalf("unexpected selected stats: %#v", selection.Stats)
	}
}

func TestCandidateFallsBackWhenLowerRouteMissesFloor(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	records := outcomes("novel-analysis", "local-slm", 3, 2, 0, 0)
	candidate, err := store.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	if got := candidate.Selections["novel-analysis"].Route; got != "general-llm" {
		t.Fatalf("fallback route=%s want general-llm", got)
	}
}

func TestExecutionFailureDoesNotBecomeCognitiveFailure(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	records := outcomes("routine-summary", "local-slm", 4, 0, 3, 3)
	candidate, err := store.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	stats := candidate.Efficacy["routine-summary"]["local-slm"]
	if stats.Assessed != 4 || stats.Sufficient != 4 || stats.Insufficient != 0 || stats.NotAssessed != 3 || stats.ExecutionFailed != 3 {
		t.Fatalf("execution/cognitive dimensions were conflated: %#v", stats)
	}
	if stats.SuccessRate != 1 {
		t.Fatalf("success rate=%v want 1.0 from assessed cognitive outcomes only", stats.SuccessRate)
	}
	if got := candidate.Selections["routine-summary"].Route; got != "general-llm" {
		t.Fatalf("minimum assessed evidence was not respected: %s", got)
	}
}

func TestUnknownOrUnauthorizedRouteFailsClosed(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	_, err := store.BuildCandidate([]OutcomeRecord{{
		ProblemClass: "routine-summary", Route: "unapproved-cloud-route",
		CognitiveOutcome: CognitiveSufficient, ExecutionOutcome: ExecutionCompleted,
		ProvenanceRef: "fixture:x", ObservedPolicyVersion: BaselineVersion,
	}})
	if err == nil {
		t.Fatal("unapproved route must fail closed")
	}
}

func TestUnknownPolicyVersionFailsClosed(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	_, err := store.BuildCandidate([]OutcomeRecord{{
		ProblemClass: "routine-summary", Route: "local-slm",
		CognitiveOutcome: CognitiveSufficient, ExecutionOutcome: ExecutionCompleted,
		ProvenanceRef: "fixture:x", ObservedPolicyVersion: "v999",
	}})
	if err == nil {
		t.Fatal("unknown observed policy version must fail closed")
	}
}

func TestProblemPolicyValidationRejectsNonFiniteAndNonCanonicalValues(t *testing.T) {
	cases := []ProblemPolicy{
		{ProblemClass: " x", StaticRoute: "a", AllowedRoutes: []RouteOption{{ID: "a"}}, RequiredSuccessRate: 0.8, MinAssessedObservations: 1},
		{ProblemClass: "x", StaticRoute: " a", AllowedRoutes: []RouteOption{{ID: " a"}}, RequiredSuccessRate: 0.8, MinAssessedObservations: 1},
		{ProblemClass: "x", StaticRoute: "a", AllowedRoutes: []RouteOption{{ID: "a "}}, RequiredSuccessRate: 0.8, MinAssessedObservations: 1},
		{ProblemClass: "x", StaticRoute: "a", AllowedRoutes: []RouteOption{{ID: "a"}}, RequiredSuccessRate: math.NaN(), MinAssessedObservations: 1},
		{ProblemClass: "x", StaticRoute: "a", AllowedRoutes: []RouteOption{{ID: "a"}}, RequiredSuccessRate: math.Inf(1), MinAssessedObservations: 1},
	}
	for i, definition := range cases {
		if _, err := NewStore([]ProblemPolicy{definition}); err == nil {
			t.Fatalf("case %d must fail closed: %#v", i, definition)
		}
	}
}

func TestSnapshotIsImmutableFromCallerPerspective(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	candidate, err := store.BuildCandidate(outcomes("routine-summary", "local-slm", 5, 0, 0, 0))
	if err != nil {
		t.Fatal(err)
	}
	candidate.Selections["routine-summary"] = Selection{Route: "mutated"}
	candidate.Efficacy["routine-summary"]["local-slm"] = RouteStats{Assessed: 999}

	again, ok := store.Snapshot("v1")
	if !ok {
		t.Fatal("snapshot missing")
	}
	if again.Selections["routine-summary"].Route == "mutated" || again.Efficacy["routine-summary"]["local-slm"].Assessed == 999 {
		t.Fatal("caller mutated stored immutable snapshot")
	}
}

func TestExplicitActivationAndRollbackReproduceRoutes(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	candidate, err := store.BuildCandidate(outcomes("routine-summary", "local-slm", 5, 0, 0, 0))
	if err != nil {
		t.Fatal(err)
	}
	before, _ := store.Route("routine-summary")
	if err := store.Activate(candidate.Version); err != nil {
		t.Fatal(err)
	}
	adapted, _ := store.Route("routine-summary")
	if err := store.Activate(BaselineVersion); err != nil {
		t.Fatal(err)
	}
	rolledBack, _ := store.Route("routine-summary")
	if before != "general-llm" || adapted != "local-slm" || rolledBack != before {
		t.Fatalf("rollback mismatch: before=%s adapted=%s rollback=%s", before, adapted, rolledBack)
	}
}

func TestDeterministicTieBreak(t *testing.T) {
	definitions := []ProblemPolicy{{
		ProblemClass: "tie",
		StaticRoute: "route-z",
		AllowedRoutes: []RouteOption{
			{ID: "route-b", EscalationLevel: 1},
			{ID: "route-a", EscalationLevel: 1},
			{ID: "route-z", EscalationLevel: 2},
		},
		RequiredSuccessRate: 0.5, MinAssessedObservations: 2,
	}}
	store, _ := NewStore(definitions)
	records := append(outcomes("tie", "route-a", 1, 1, 0, 0), outcomes("tie", "route-b", 1, 1, 0, 0)...)
	candidate, err := store.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	if got := candidate.Selections["tie"].Route; got != "route-a" {
		t.Fatalf("tie route=%s want lexical route-a", got)
	}
}

func TestReplayCanReduceEscalationWithoutReducingSyntheticSuccess(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	candidate, err := store.BuildCandidate(outcomes("routine-summary", "local-slm", 9, 1, 0, 0))
	if err != nil {
		t.Fatal(err)
	}

	cases := []ReplayCase{
		{
			ID: "r1", ProblemClass: "routine-summary",
			RouteOutcomes: map[string]bool{"local-slm": true, "general-llm": true},
		},
		{
			ID: "r2", ProblemClass: "routine-summary",
			RouteOutcomes: map[string]bool{"local-slm": true, "general-llm": true},
		},
	}
	adapted, err := store.Replay(candidate.Version, cases)
	if err != nil {
		t.Fatal(err)
	}
	baseline, err := store.Replay(BaselineVersion, cases)
	if err != nil {
		t.Fatal(err)
	}

	if adapted.PolicySuccessRate != 1 || baseline.PolicySuccessRate != 1 {
		t.Fatalf("positive fixture must preserve synthetic success: adapted=%#v baseline=%#v", adapted, baseline)
	}
	if adapted.UnnecessaryEscalationRate != 0 || baseline.UnnecessaryEscalationRate != 1 {
		t.Fatalf("expected escalation reduction without success change: adapted=%#v baseline=%#v", adapted, baseline)
	}
	if adapted.RegretAgainstStatic != 0 {
		t.Fatalf("positive fixture must not contain regret: %#v", adapted)
	}
}

func TestReplayPreservesDistributionShiftRegretAgainstStatic(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	candidate, err := store.BuildCandidate(outcomes("routine-summary", "local-slm", 9, 1, 0, 0))
	if err != nil {
		t.Fatal(err)
	}

	cases := []ReplayCase{
		{
			ID: "shift-1", ProblemClass: "routine-summary",
			RouteOutcomes: map[string]bool{"local-slm": false, "general-llm": true},
		},
		{
			ID: "novel-1", ProblemClass: "novel-analysis",
			RouteOutcomes: map[string]bool{"local-slm": false, "general-llm": true},
		},
	}
	adapted, err := store.Replay(candidate.Version, cases)
	if err != nil {
		t.Fatal(err)
	}
	baseline, err := store.Replay(BaselineVersion, cases)
	if err != nil {
		t.Fatal(err)
	}

	if adapted.PolicySuccesses != 1 || adapted.RegretAgainstStatic != 1 || adapted.RegretAgainstStaticRate != 0.5 {
		t.Fatalf("distribution-shift regret was not preserved: %#v", adapted)
	}
	if baseline.PolicySuccesses != 2 || baseline.RegretAgainstStatic != 0 {
		t.Fatalf("unexpected static baseline replay: %#v", baseline)
	}
}

func TestReplayRequiresCounterfactuallyCompleteRoutes(t *testing.T) {
	store, _ := NewStore(testDefinitions())
	_, err := store.Replay(BaselineVersion, []ReplayCase{{
		ID: "incomplete", ProblemClass: "routine-summary",
		RouteOutcomes: map[string]bool{"general-llm": true},
	}})
	if err == nil {
		t.Fatal("incomplete counterfactual replay must fail closed")
	}
}

func TestSameEvidenceProducesSameSelectionContent(t *testing.T) {
	records := append(
		outcomes("routine-summary", "local-slm", 8, 2, 0, 0),
		outcomes("routine-summary", "general-llm", 10, 0, 0, 0)...,
	)
	a, _ := NewStore(testDefinitions())
	b, _ := NewStore(testDefinitions())
	left, err := a.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	right, err := b.BuildCandidate(records)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(left, right) {
		t.Fatalf("same definitions/evidence did not reproduce candidate:\nleft=%#v\nright=%#v", left, right)
	}
}

func BenchmarkBuildCandidate(b *testing.B) {
	records := append(
		outcomes("routine-summary", "local-slm", 90, 10, 10, 3),
		outcomes("routine-summary", "general-llm", 98, 2, 5, 1)...,
	)
	for i := 0; i < b.N; i++ {
		store, err := NewStore(testDefinitions())
		if err != nil {
			b.Fatal(err)
		}
		if _, err := store.BuildCandidate(records); err != nil {
			b.Fatal(err)
		}
	}
}
