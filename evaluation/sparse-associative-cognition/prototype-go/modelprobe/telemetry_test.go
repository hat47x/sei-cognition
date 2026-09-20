package modelprobe

import (
	"errors"
	"math"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

const testSourceGitSHA = "0123456789abcdef0123456789abcdef01234567"

func stagedObservations(t *testing.T, fixtures []cognitiveeval.Fixture) []ActualRunObservation {
	t.Helper()
	out := make([]ActualRunObservation, 0, len(fixtures))
	for _, fixture := range fixtures {
		plan, err := BuildPlan(fixture, ModeStaged)
		if err != nil {
			t.Fatal(err)
		}
		result := Result{
			FixtureID: fixture.ID,
			Mode:      ModeStaged,
			Route:     plan.Route,
		}
		if plan.ShouldInvokeModel {
			result.ModelInvocationAttempted = true
			result.TotalLatencyMS = 10
			result.Usage = TokenUsage{PromptTokens: 2, CompletionTokens: 1, TotalTokens: 3}
		} else {
			result.Skipped = true
		}
		out = append(out, ObserveActualRun(plan, result, nil))
	}
	return out
}

func TestSummarizeActualTelemetrySeparatesPlannedAndObservedCalls(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	observations := stagedObservations(t, fixtures)

	summary, err := SummarizeActualTelemetry(
		"run-001",
		testSourceGitSHA,
		"candidate-model",
		ModeStaged,
		fixtures,
		observations,
	)
	if err != nil {
		t.Fatal(err)
	}

	if summary.Schema != "sei-cognition.actual-model-telemetry/v0" ||
		summary.Status != "evaluation-only" {
		t.Fatalf("unexpected metadata: %+v", summary)
	}
	if summary.PlannedModelCalls != 4 || summary.PlannedSkippedCalls != 3 {
		t.Fatalf("planned calls=%d skipped=%d", summary.PlannedModelCalls, summary.PlannedSkippedCalls)
	}
	if summary.ActualModelInvocationAttempts != 4 ||
		summary.ActualModelInvocationSuccesses != 4 ||
		summary.ActualModelInvocationFailures != 0 ||
		summary.ActualSkippedCalls != 3 {
		t.Fatalf("unexpected actual call accounting: %+v", summary)
	}
	if summary.ActualCallsAvoidedVsRaw != 3 {
		t.Fatalf("actual calls avoided=%d want=3", summary.ActualCallsAvoidedVsRaw)
	}
	if math.Abs(summary.ActualCallAvoidanceRatioVsRaw-(3.0/7.0)) > 1e-12 {
		t.Fatalf("actual avoidance ratio=%f", summary.ActualCallAvoidanceRatioVsRaw)
	}
	if math.Abs(summary.ActualModelCallRate-(4.0/7.0)) > 1e-12 {
		t.Fatalf("actual call rate=%f", summary.ActualModelCallRate)
	}
	if summary.TotalLatencyMS != 40 ||
		summary.TotalPromptTokens != 8 ||
		summary.TotalCompletionTokens != 4 ||
		summary.TotalTokens != 12 {
		t.Fatalf("unexpected totals: %+v", summary)
	}
	if !summary.AllFixturesAccounted || !summary.CompleteWithoutInvocationError {
		t.Fatalf("expected complete telemetry: %+v", summary)
	}
	if summary.PlanExecutionMismatchCount != 0 {
		t.Fatalf("unexpected plan mismatch: %+v", summary)
	}
}

func TestObserveActualRunRecordsAttemptedFailure(t *testing.T) {
	fixture := cognitiveeval.ReferenceFixtures()[0]
	plan, err := BuildPlan(fixture, ModeStaged)
	if err != nil {
		t.Fatal(err)
	}
	result := Result{
		FixtureID:                  fixture.ID,
		Mode:                       ModeStaged,
		Route:                      plan.Route,
		ModelInvocationAttempted:   true,
		TotalLatencyMS:             17,
	}
	observation := ObserveActualRun(plan, result, errors.New("endpoint unavailable"))
	if !observation.PlannedModelInvocation ||
		!observation.ModelInvocationAttempted ||
		observation.ModelInvocationSucceeded {
		t.Fatalf("unexpected observation: %+v", observation)
	}
	if observation.Error == "" {
		t.Fatal("expected invocation error to be preserved")
	}
}

func TestSummarizeActualTelemetryMarksFailedAttemptIncomplete(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	observations := stagedObservations(t, fixtures)
	observations[0].ModelInvocationSucceeded = false
	observations[0].Error = "endpoint returned 500"

	summary, err := SummarizeActualTelemetry(
		"run-002",
		testSourceGitSHA,
		"candidate-model",
		ModeStaged,
		fixtures,
		observations,
	)
	if err != nil {
		t.Fatal(err)
	}
	if summary.ActualModelInvocationAttempts != 4 ||
		summary.ActualModelInvocationSuccesses != 3 ||
		summary.ActualModelInvocationFailures != 1 {
		t.Fatalf("unexpected failure accounting: %+v", summary)
	}
	if summary.CompleteWithoutInvocationError {
		t.Fatalf("failed attempt must not produce complete telemetry: %+v", summary)
	}
}

func TestSummarizeActualTelemetryRejectsIdentityGaps(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	observations := stagedObservations(t, fixtures)

	if _, err := SummarizeActualTelemetry(
		"",
		testSourceGitSHA,
		"candidate-model",
		ModeStaged,
		fixtures,
		observations,
	); err == nil {
		t.Fatal("expected empty run_id rejection")
	}
	if _, err := SummarizeActualTelemetry(
		"run-003",
		"not-a-sha",
		"candidate-model",
		ModeStaged,
		fixtures,
		observations,
	); err == nil {
		t.Fatal("expected invalid source sha rejection")
	}
}

func TestSummarizeActualTelemetryDetectsPlanExecutionMismatch(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	observations := stagedObservations(t, fixtures)
	for i := range observations {
		if !observations[i].PlannedModelInvocation {
			observations[i].ModelInvocationAttempted = true
			observations[i].Skipped = false
			break
		}
	}

	summary, err := SummarizeActualTelemetry(
		"run-004",
		testSourceGitSHA,
		"candidate-model",
		ModeStaged,
		fixtures,
		observations,
	)
	if err != nil {
		t.Fatal(err)
	}
	if summary.UnexpectedInvocationAttempts != 1 {
		t.Fatalf("unexpected invocation attempts=%d want=1", summary.UnexpectedInvocationAttempts)
	}
	if summary.PlanExecutionMismatchCount == 0 || summary.CompleteWithoutInvocationError {
		t.Fatalf("mismatch must fail completeness: %+v", summary)
	}
}


func TestSummarizeActualTelemetryRejectsPlannedCallAsSkip(t *testing.T) {
	fixtures := cognitiveeval.ReferenceFixtures()
	observations := stagedObservations(t, fixtures)
	for i := range observations {
		if observations[i].PlannedModelInvocation {
			observations[i].ModelInvocationAttempted = false
			observations[i].ModelInvocationSucceeded = false
			observations[i].Skipped = true
			break
		}
	}

	summary, err := SummarizeActualTelemetry(
		"run-005",
		testSourceGitSHA,
		"candidate-model",
		ModeStaged,
		fixtures,
		observations,
	)
	if err != nil {
		t.Fatal(err)
	}
	if summary.ActualSkippedCalls != 3 {
		t.Fatalf("planned-call skip must not count as avoided call: %+v", summary)
	}
	if summary.ActualCallsAvoidedVsRaw != 3 {
		t.Fatalf("actual calls avoided=%d want=3", summary.ActualCallsAvoidedVsRaw)
	}
	if summary.PlanExecutionMismatchCount == 0 || summary.CompleteWithoutInvocationError {
		t.Fatalf("inconsistent planned-call skip must fail completeness: %+v", summary)
	}
}
