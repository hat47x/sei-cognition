package modelprobe

import (
	"fmt"
	"sort"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

type RouteCallCount struct {
	Route              string `json:"route"`
	FixtureCount       int    `json:"fixture_count"`
	ModelInvocations   int    `json:"model_invocations"`
	SkippedInvocations int    `json:"skipped_invocations"`
}

type CallAvoidanceSummary struct {
	Schema                      string           `json:"schema"`
	Status                      string           `json:"status"`
	FixtureCount                int              `json:"fixture_count"`
	RawBaselineModelCalls       int              `json:"raw_baseline_model_calls"`
	WorkspaceBaselineModelCalls int              `json:"workspace_baseline_model_calls"`
	StagedModelCalls            int              `json:"staged_model_calls"`
	StagedSkippedModelCalls     int              `json:"staged_skipped_model_calls"`
	CallsAvoidedVsRaw           int              `json:"calls_avoided_vs_raw"`
	CallAvoidanceRatioVsRaw     float64          `json:"call_avoidance_ratio_vs_raw"`
	StagedModelCallRate         float64          `json:"staged_model_call_rate"`
	AllExpectedRoutesMatched    bool             `json:"all_expected_routes_matched"`
	RouteCounts                 []RouteCallCount `json:"route_counts"`
}

// SummarizeCallAvoidance evaluates routing mechanics only. It does not invoke
// any model and must not be interpreted as production LLM-call reduction,
// task-success, semantic-quality, or total-system-cost Evidence.
func SummarizeCallAvoidance(fixtures []cognitiveeval.Fixture) (CallAvoidanceSummary, error) {
	if len(fixtures) == 0 {
		return CallAvoidanceSummary{}, fmt.Errorf("at least one fixture is required")
	}

	summary := CallAvoidanceSummary{
		Schema:                   "sei-cognition.synthetic-model-call-avoidance/v0",
		Status:                   "evaluation-only",
		FixtureCount:             len(fixtures),
		AllExpectedRoutesMatched: true,
	}

	routeCounts := map[string]*RouteCallCount{}
	for _, fixture := range fixtures {
		raw, err := BuildPlan(fixture, ModeRaw)
		if err != nil {
			return CallAvoidanceSummary{}, fmt.Errorf("fixture %s raw plan: %w", fixture.ID, err)
		}
		workspace, err := BuildPlan(fixture, ModeWorkspace)
		if err != nil {
			return CallAvoidanceSummary{}, fmt.Errorf("fixture %s workspace plan: %w", fixture.ID, err)
		}
		staged, err := BuildPlan(fixture, ModeStaged)
		if err != nil {
			return CallAvoidanceSummary{}, fmt.Errorf("fixture %s staged plan: %w", fixture.ID, err)
		}
		bundle, err := cognitiveeval.BuildComparisonBundle(fixture)
		if err != nil {
			return CallAvoidanceSummary{}, fmt.Errorf("fixture %s comparison bundle: %w", fixture.ID, err)
		}

		if raw.ShouldInvokeModel {
			summary.RawBaselineModelCalls++
		}
		if workspace.ShouldInvokeModel {
			summary.WorkspaceBaselineModelCalls++
		}
		if staged.ShouldInvokeModel {
			summary.StagedModelCalls++
		} else {
			summary.StagedSkippedModelCalls++
		}
		if !bundle.Stats.ExpectedRouteMatched {
			summary.AllExpectedRoutesMatched = false
		}

		count := routeCounts[staged.Route]
		if count == nil {
			count = &RouteCallCount{Route: staged.Route}
			routeCounts[staged.Route] = count
		}
		count.FixtureCount++
		if staged.ShouldInvokeModel {
			count.ModelInvocations++
		} else {
			count.SkippedInvocations++
		}
	}

	summary.CallsAvoidedVsRaw = summary.RawBaselineModelCalls - summary.StagedModelCalls
	if summary.RawBaselineModelCalls > 0 {
		summary.CallAvoidanceRatioVsRaw = float64(summary.CallsAvoidedVsRaw) / float64(summary.RawBaselineModelCalls)
	}
	summary.StagedModelCallRate = float64(summary.StagedModelCalls) / float64(summary.FixtureCount)

	routes := make([]string, 0, len(routeCounts))
	for route := range routeCounts {
		routes = append(routes, route)
	}
	sort.Strings(routes)
	summary.RouteCounts = make([]RouteCallCount, 0, len(routes))
	for _, route := range routes {
		summary.RouteCounts = append(summary.RouteCounts, *routeCounts[route])
	}

	return summary, nil
}
