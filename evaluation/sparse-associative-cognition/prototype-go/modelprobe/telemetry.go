package modelprobe

import (
	"fmt"
	"regexp"
	"sort"
	"strings"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

var gitSHA40 = regexp.MustCompile("^[0-9a-f]{40}$")

type ActualRunObservation struct {
	FixtureID                  string     `json:"fixture_id"`
	Route                      string     `json:"route"`
	PlannedModelInvocation     bool       `json:"planned_model_invocation"`
	ModelInvocationAttempted   bool       `json:"model_invocation_attempted"`
	ModelInvocationSucceeded   bool       `json:"model_invocation_succeeded"`
	Skipped                    bool       `json:"skipped"`
	Error                      string     `json:"error,omitempty"`
	TotalLatencyMS             int64      `json:"total_latency_ms,omitempty"`
	Usage                      TokenUsage `json:"usage,omitempty"`
	EvaluationAvailable        bool       `json:"evaluation_available"`
}

type ActualTelemetrySummary struct {
	Schema                         string                 `json:"schema"`
	Status                         string                 `json:"status"`
	RunID                          string                 `json:"run_id"`
	SourceGitSHA                   string                 `json:"source_git_sha"`
	Mode                           Mode                   `json:"mode"`
	Model                          string                 `json:"model"`
	FixtureCount                   int                    `json:"fixture_count"`
	PlannedModelCalls              int                    `json:"planned_model_calls"`
	PlannedSkippedCalls            int                    `json:"planned_skipped_calls"`
	ActualModelInvocationAttempts  int                    `json:"actual_model_invocation_attempts"`
	ActualModelInvocationSuccesses int                    `json:"actual_model_invocation_successes"`
	ActualModelInvocationFailures  int                    `json:"actual_model_invocation_failures"`
	ActualSkippedCalls             int                    `json:"actual_skipped_calls"`
	UnattemptedPlannedCalls        int                    `json:"unattempted_planned_calls"`
	UnexpectedInvocationAttempts   int                    `json:"unexpected_invocation_attempts"`
	PlanExecutionMismatchCount     int                    `json:"plan_execution_mismatch_count"`
	ActualCallsAvoidedVsRaw        int                    `json:"actual_calls_avoided_vs_raw"`
	ActualCallAvoidanceRatioVsRaw  float64                `json:"actual_call_avoidance_ratio_vs_raw"`
	ActualModelCallRate            float64                `json:"actual_model_call_rate"`
	TotalLatencyMS                 int64                  `json:"total_latency_ms"`
	TotalPromptTokens              int                    `json:"total_prompt_tokens"`
	TotalCompletionTokens          int                    `json:"total_completion_tokens"`
	TotalTokens                    int                    `json:"total_tokens"`
	ResultsWithEvaluation          int                    `json:"results_with_evaluation"`
	AllFixturesAccounted           bool                   `json:"all_fixtures_accounted"`
	CompleteWithoutInvocationError bool                   `json:"complete_without_invocation_error"`
	Observations                   []ActualRunObservation `json:"observations"`
}

// ObserveActualRun converts one planned fixture execution into telemetry without
// promoting routing intent into an observed model call. ModelInvocationAttempted
// is set by Run only immediately before the HTTP client is invoked.
func ObserveActualRun(plan Plan, result Result, runErr error) ActualRunObservation {
	observation := ActualRunObservation{
		FixtureID:                plan.FixtureID,
		Route:                    plan.Route,
		PlannedModelInvocation:   plan.ShouldInvokeModel,
		ModelInvocationAttempted: result.ModelInvocationAttempted,
		Skipped:                  result.Skipped,
		TotalLatencyMS:           result.TotalLatencyMS,
		Usage:                    result.Usage,
		EvaluationAvailable:      result.Evaluation != nil,
	}
	if runErr != nil {
		observation.Error = runErr.Error()
	}
	observation.ModelInvocationSucceeded = (
		runErr == nil &&
			plan.ShouldInvokeModel &&
			result.ModelInvocationAttempted &&
			!result.Skipped)
	return observation
}

func ValidateRunIdentity(runID string, sourceGitSHA string) error {
	if strings.TrimSpace(runID) == "" {
		return fmt.Errorf("run_id is required")
	}
	if !gitSHA40.MatchString(strings.TrimSpace(sourceGitSHA)) {
		return fmt.Errorf("source_git_sha must be a lowercase 40-character Git SHA")
	}
	return nil
}

func SummarizeActualTelemetry(
	runID string,
	sourceGitSHA string,
	model string,
	mode Mode,
	fixtures []cognitiveeval.Fixture,
	observations []ActualRunObservation,
) (ActualTelemetrySummary, error) {
	runID = strings.TrimSpace(runID)
	sourceGitSHA = strings.TrimSpace(sourceGitSHA)
	model = strings.TrimSpace(model)
	if err := ValidateRunIdentity(runID, sourceGitSHA); err != nil {
		return ActualTelemetrySummary{}, err
	}
	if model == "" {
		return ActualTelemetrySummary{}, fmt.Errorf("model is required")
	}
	if mode != ModeRaw && mode != ModeWorkspace && mode != ModeStaged {
		return ActualTelemetrySummary{}, fmt.Errorf("unsupported mode %q", mode)
	}
	if len(fixtures) == 0 {
		return ActualTelemetrySummary{}, fmt.Errorf("at least one fixture is required")
	}

	fixtureByID := make(map[string]cognitiveeval.Fixture, len(fixtures))
	for _, fixture := range fixtures {
		if strings.TrimSpace(fixture.ID) == "" {
			return ActualTelemetrySummary{}, fmt.Errorf("fixture id is required")
		}
		if _, exists := fixtureByID[fixture.ID]; exists {
			return ActualTelemetrySummary{}, fmt.Errorf("duplicate fixture id %q", fixture.ID)
		}
		fixtureByID[fixture.ID] = fixture
	}

	observed := make(map[string]ActualRunObservation, len(observations))
	for _, observation := range observations {
		if _, ok := fixtureByID[observation.FixtureID]; !ok {
			return ActualTelemetrySummary{}, fmt.Errorf("unknown observation fixture %q", observation.FixtureID)
		}
		if _, exists := observed[observation.FixtureID]; exists {
			return ActualTelemetrySummary{}, fmt.Errorf("duplicate observation fixture %q", observation.FixtureID)
		}
		observed[observation.FixtureID] = observation
	}

	summary := ActualTelemetrySummary{
		Schema:       "sei-cognition.actual-model-telemetry/v0",
		Status:       "evaluation-only",
		RunID:        runID,
		SourceGitSHA: sourceGitSHA,
		Mode:         mode,
		Model:        model,
		FixtureCount: len(fixtures),
	}

	fixtureIDs := make([]string, 0, len(fixtures))
	for id := range fixtureByID {
		fixtureIDs = append(fixtureIDs, id)
	}
	sort.Strings(fixtureIDs)

	for _, id := range fixtureIDs {
		fixture := fixtureByID[id]
		plan, err := BuildPlan(fixture, mode)
		if err != nil {
			return ActualTelemetrySummary{}, fmt.Errorf("fixture %s plan: %w", id, err)
		}
		if plan.ShouldInvokeModel {
			summary.PlannedModelCalls++
		} else {
			summary.PlannedSkippedCalls++
		}

		observation, ok := observed[id]
		if !ok {
			continue
		}
		if observation.Route != plan.Route ||
			observation.PlannedModelInvocation != plan.ShouldInvokeModel {
			summary.PlanExecutionMismatchCount++
		}
		if observation.ModelInvocationAttempted {
			summary.ActualModelInvocationAttempts++
		}
		if observation.ModelInvocationSucceeded {
			summary.ActualModelInvocationSuccesses++
		}
		if observation.Error != "" && observation.ModelInvocationAttempted {
			summary.ActualModelInvocationFailures++
		}
		if !plan.ShouldInvokeModel && observation.Skipped {
			summary.ActualSkippedCalls++
		}
		if plan.ShouldInvokeModel && observation.Skipped {
			summary.PlanExecutionMismatchCount++
		}
		if plan.ShouldInvokeModel && !observation.ModelInvocationAttempted {
			summary.UnattemptedPlannedCalls++
		}
		if !plan.ShouldInvokeModel && observation.ModelInvocationAttempted {
			summary.UnexpectedInvocationAttempts++
		}
		if observation.EvaluationAvailable {
			summary.ResultsWithEvaluation++
		}
		summary.TotalLatencyMS += observation.TotalLatencyMS
		summary.TotalPromptTokens += observation.Usage.PromptTokens
		summary.TotalCompletionTokens += observation.Usage.CompletionTokens
		summary.TotalTokens += observation.Usage.TotalTokens
		summary.Observations = append(summary.Observations, observation)
	}

	summary.AllFixturesAccounted = len(observed) == len(fixtures)
	summary.PlanExecutionMismatchCount += summary.UnattemptedPlannedCalls + summary.UnexpectedInvocationAttempts
	// Count only explicit route skips as avoided calls. A planned call that failed
	// before an HTTP attempt is an execution shortfall, not an avoided model call.
	summary.ActualCallsAvoidedVsRaw = summary.ActualSkippedCalls
	if len(fixtures) > 0 {
		summary.ActualCallAvoidanceRatioVsRaw =
			float64(summary.ActualCallsAvoidedVsRaw) / float64(len(fixtures))
		summary.ActualModelCallRate =
			float64(summary.ActualModelInvocationAttempts) / float64(len(fixtures))
	}
	summary.CompleteWithoutInvocationError = (
		summary.AllFixturesAccounted &&
			summary.ActualModelInvocationFailures == 0 &&
			summary.PlanExecutionMismatchCount == 0)
	return summary, nil
}
