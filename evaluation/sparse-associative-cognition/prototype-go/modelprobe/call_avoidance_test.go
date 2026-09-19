package modelprobe

import (
	"math"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

func routeCountMap(summary CallAvoidanceSummary) map[string]RouteCallCount {
	out := make(map[string]RouteCallCount, len(summary.RouteCounts))
	for _, count := range summary.RouteCounts {
		out[count.Route] = count
	}
	return out
}

func TestSummarizeReferenceFixtureCallAvoidance(t *testing.T) {
	summary, err := SummarizeCallAvoidance(cognitiveeval.ReferenceFixtures())
	if err != nil {
		t.Fatal(err)
	}

	if summary.Schema != "sei-cognition.synthetic-model-call-avoidance/v0" || summary.Status != "evaluation-only" {
		t.Fatalf("unexpected metadata: %+v", summary)
	}
	if summary.FixtureCount != 7 {
		t.Fatalf("fixture_count=%d want=7", summary.FixtureCount)
	}
	if summary.RawBaselineModelCalls != 7 || summary.WorkspaceBaselineModelCalls != 7 {
		t.Fatalf("baseline calls raw=%d workspace=%d", summary.RawBaselineModelCalls, summary.WorkspaceBaselineModelCalls)
	}
	if summary.StagedModelCalls != 4 || summary.StagedSkippedModelCalls != 3 {
		t.Fatalf("staged calls=%d skipped=%d", summary.StagedModelCalls, summary.StagedSkippedModelCalls)
	}
	if summary.CallsAvoidedVsRaw != 3 {
		t.Fatalf("avoided=%d want=3", summary.CallsAvoidedVsRaw)
	}
	if math.Abs(summary.CallAvoidanceRatioVsRaw-(3.0/7.0)) > 1e-12 {
		t.Fatalf("avoidance ratio=%f", summary.CallAvoidanceRatioVsRaw)
	}
	if math.Abs(summary.StagedModelCallRate-(4.0/7.0)) > 1e-12 {
		t.Fatalf("staged call rate=%f", summary.StagedModelCallRate)
	}
	if !summary.AllExpectedRoutesMatched {
		t.Fatal("expected all reference fixture routes to match")
	}

	counts := routeCountMap(summary)
	expected := map[string]RouteCallCount{
		"abstain-or-expand-evidence": {Route: "abstain-or-expand-evidence", FixtureCount: 1, SkippedInvocations: 1},
		"external-evidence-required":  {Route: "external-evidence-required", FixtureCount: 1, SkippedInvocations: 1},
		"local-slm":                   {Route: "local-slm", FixtureCount: 4, ModelInvocations: 4},
		"symbolic":                    {Route: "symbolic", FixtureCount: 1, SkippedInvocations: 1},
	}
	if len(counts) != len(expected) {
		t.Fatalf("route count size=%d want=%d: %+v", len(counts), len(expected), counts)
	}
	for route, want := range expected {
		if got := counts[route]; got != want {
			t.Fatalf("route %s: got=%+v want=%+v", route, got, want)
		}
	}
}

func TestSummarizeSingleLocalRouteHasNoAvoidance(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	summary, err := SummarizeCallAvoidance(fixtures[:1])
	if err != nil {
		t.Fatal(err)
	}
	if summary.RawBaselineModelCalls != 1 || summary.StagedModelCalls != 1 || summary.CallsAvoidedVsRaw != 0 {
		t.Fatalf("unexpected summary: %+v", summary)
	}
}

func TestSummarizeSingleDeterministicRouteAvoidsBaselineCall(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	summary, err := SummarizeCallAvoidance(fixtures[len(fixtures)-1:])
	if err != nil {
		t.Fatal(err)
	}
	if summary.RawBaselineModelCalls != 1 || summary.StagedModelCalls != 0 || summary.CallsAvoidedVsRaw != 1 {
		t.Fatalf("unexpected summary: %+v", summary)
	}
	if summary.CallAvoidanceRatioVsRaw != 1.0 {
		t.Fatalf("avoidance ratio=%f want=1", summary.CallAvoidanceRatioVsRaw)
	}
}

func TestSummarizeRejectsEmptyFixtures(t *testing.T) {
	if _, err := SummarizeCallAvoidance(nil); err == nil {
		t.Fatal("expected empty fixture error")
	}
}

func TestSummarizePropagatesInvalidFixture(t *testing.T) {
	fixture := cognitiveeval.ReferenceFixtures()[0]
	fixture.ID = ""
	if _, err := SummarizeCallAvoidance([]cognitiveeval.Fixture{fixture}); err == nil {
		t.Fatal("expected invalid fixture error")
	}
}
