package modelprobe

import (
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/hybridreasoning"
)

const artifactTestGitSHA = "89abcdef0123456789abcdef0123456789abcdef"

func makeArtifact(t *testing.T, mode Mode) ActualRunArtifact {
	t.Helper()
	fixtures := cognitiveeval.ReferenceFixtures()
	results := make([]Result, 0, len(fixtures))
	observations := make([]ActualRunObservation, 0, len(fixtures))
	for _, fixture := range fixtures {
		plan, err := BuildPlan(fixture, mode)
		if err != nil {
			t.Fatal(err)
		}
		result := Result{
			FixtureID:    fixture.ID,
			Mode:         mode,
			Model:        "candidate-model",
			Endpoint:     "http://127.0.0.1:8080/v1/chat/completions",
			Route:        plan.Route,
			RequestChars: plan.RequestChars,
		}
		if !plan.ShouldInvokeModel {
			result.Skipped = true
			result.SkipReason = plan.Reason
		} else {
			result.ModelInvocationAttempted = true
			result.TotalLatencyMS = 10
			result.Usage = TokenUsage{PromptTokens: 2, CompletionTokens: 1, TotalTokens: 3}
			output := cognitiveeval.ModelOutput{
				Proposal:              "bounded proposal",
				DecisionBasisRefs:     append([]string(nil), fixture.DecisionBasisRefs...),
				PreservedUnknownRefs:  append([]string(nil), fixture.UnknownRefs...),
				PreservedConflictRefs: append([]string(nil), fixture.ConflictRefs...),
				RecommendationRef:     fixture.RecommendationRef,
				DecisionRef:           fixture.DecisionRef,
				NeedMoreEvidence: fixture.ExpectedRoute == hybridreasoning.RouteExpandEvidence ||
					fixture.ExpectedRoute == hybridreasoning.RouteExternalEvidence,
			}
			report, err := cognitiveeval.EvaluateOutput(fixture, output)
			if err != nil {
				t.Fatal(err)
			}
			result.Evaluation = &report
		}
		results = append(results, result)
		observations = append(observations, ObserveActualRun(plan, result, nil))
	}
	summary, err := SummarizeActualTelemetry(
		"run-"+string(mode),
		artifactTestGitSHA,
		"candidate-model",
		mode,
		fixtures,
		observations,
	)
	if err != nil {
		t.Fatal(err)
	}
	artifact, err := BuildActualRunArtifact(summary, results)
	if err != nil {
		t.Fatal(err)
	}
	return artifact
}

func TestBuildActualRunArtifactBindsTelemetryAndResults(t *testing.T) {
	artifact := makeArtifact(t, ModeStaged)
	if artifact.Schema != actualRunArtifactSchema || artifact.Status != "evaluation-only" {
		t.Fatalf("unexpected artifact metadata: %+v", artifact)
	}
	if len(artifact.Results) != 7 {
		t.Fatalf("result count=%d want=7", len(artifact.Results))
	}
	if artifact.Telemetry.ActualModelInvocationAttempts != 4 ||
		artifact.Telemetry.ActualSkippedCalls != 3 {
		t.Fatalf("unexpected telemetry: %+v", artifact.Telemetry)
	}
}

func TestBuildActualRunArtifactRejectsInvocationMismatch(t *testing.T) {
	artifact := makeArtifact(t, ModeStaged)
	results := append([]Result(nil), artifact.Results...)
	for i := range results {
		if results[i].Skipped {
			results[i].ModelInvocationAttempted = true
			break
		}
	}
	if _, err := BuildActualRunArtifact(artifact.Telemetry, results); err == nil {
		t.Fatal("expected result/telemetry mismatch rejection")
	}
}

func TestCompareActualRunsKeepsModesAndRoutingSeparate(t *testing.T) {
	raw := makeArtifact(t, ModeRaw)
	workspace := makeArtifact(t, ModeWorkspace)
	staged := makeArtifact(t, ModeStaged)

	comparison, err := CompareActualRuns(raw, workspace, staged)
	if err != nil {
		t.Fatal(err)
	}
	if comparison.Schema != runComparisonSchema || comparison.Status != "evaluation-only" {
		t.Fatalf("unexpected comparison metadata: %+v", comparison)
	}
	if comparison.Raw.EvaluatedFixtureCount != 7 ||
		comparison.Workspace.EvaluatedFixtureCount != 7 ||
		comparison.Staged.EvaluatedFixtureCount != 4 ||
		comparison.Staged.SkippedFixtureCount != 3 {
		t.Fatalf("unexpected mode aggregates: %+v", comparison)
	}
	if comparison.WorkspaceVsRaw.SharedEvaluatedFixtureCount != 7 {
		t.Fatalf("shared fixtures=%d want=7", comparison.WorkspaceVsRaw.SharedEvaluatedFixtureCount)
	}
	if comparison.WorkspaceVsRaw.WorkspaceMinusRawUnsupportedClaims != 0 ||
		comparison.WorkspaceVsRaw.WorkspaceMinusRawInvalidReferences != 0 {
		t.Fatalf("expected zero quality deltas: %+v", comparison.WorkspaceVsRaw)
	}
	if comparison.Invocations.RawActualInvocationAttempts != 7 ||
		comparison.Invocations.WorkspaceActualInvocationAttempts != 7 ||
		comparison.Invocations.StagedActualInvocationAttempts != 4 ||
		comparison.Invocations.StagedExplicitSkippedCalls != 3 {
		t.Fatalf("unexpected invocation comparison: %+v", comparison.Invocations)
	}
}

func TestCompareActualRunsReportsDescriptiveWorkspaceDelta(t *testing.T) {
	raw := makeArtifact(t, ModeRaw)
	workspace := makeArtifact(t, ModeWorkspace)
	staged := makeArtifact(t, ModeStaged)

	for i := range workspace.Results {
		if workspace.Results[i].Evaluation != nil {
			workspace.Results[i].Evaluation.UnsupportedClaimCount++
			workspace.Results[i].Evaluation.AllMaterialClaimsHaveValidSupport = false
			break
		}
	}

	comparison, err := CompareActualRuns(raw, workspace, staged)
	if err != nil {
		t.Fatal(err)
	}
	if comparison.WorkspaceVsRaw.WorkspaceMinusRawUnsupportedClaims != 1 {
		t.Fatalf("unsupported claim delta=%d want=1", comparison.WorkspaceVsRaw.WorkspaceMinusRawUnsupportedClaims)
	}
	if comparison.WorkspaceVsRaw.WorkspaceMinusRawValidMaterialSupport != -1 {
		t.Fatalf("valid support delta=%d want=-1", comparison.WorkspaceVsRaw.WorkspaceMinusRawValidMaterialSupport)
	}
}

func TestCompareActualRunsRejectsDifferentSourceRevision(t *testing.T) {
	raw := makeArtifact(t, ModeRaw)
	workspace := makeArtifact(t, ModeWorkspace)
	staged := makeArtifact(t, ModeStaged)
	workspace.SourceGitSHA = "0123456789abcdef0123456789abcdef01234567"

	if _, err := CompareActualRuns(raw, workspace, staged); err == nil {
		t.Fatal("expected source revision mismatch rejection")
	}
}


func TestCompareActualRunsRejectsOuterTelemetryIdentityMismatch(t *testing.T) {
	raw := makeArtifact(t, ModeRaw)
	workspace := makeArtifact(t, ModeWorkspace)
	staged := makeArtifact(t, ModeStaged)
	workspace.RunID = "tampered-run"

	if _, err := CompareActualRuns(raw, workspace, staged); err == nil {
		t.Fatal("expected outer/telemetry identity mismatch rejection")
	}
}

func TestBuildActualRunArtifactRejectsDuplicateTelemetryObservation(t *testing.T) {
	artifact := makeArtifact(t, ModeRaw)
	summary := artifact.Telemetry
	summary.Observations = append(summary.Observations, summary.Observations[0])

	if _, err := BuildActualRunArtifact(summary, artifact.Results); err == nil {
		t.Fatal("expected duplicate telemetry observation rejection")
	}
}

func TestBuildActualRunArtifactRejectsTelemetrySchemaDrift(t *testing.T) {
	artifact := makeArtifact(t, ModeRaw)
	summary := artifact.Telemetry
	summary.Schema = "sei-cognition.actual-model-telemetry/v999"

	if _, err := BuildActualRunArtifact(summary, artifact.Results); err == nil {
		t.Fatal("expected telemetry schema mismatch rejection")
	}
}


func TestValidateActualRunArtifactRejectsLegacyV0Schema(t *testing.T) {
	artifact := completeArtifactForTest(t, ModeRaw)
	artifact.Schema = legacyActualRunArtifactSchema

	if err := validateActualRunArtifact("raw", artifact); err == nil {
		t.Fatal("expected legacy v0 run artifact rejection")
	}
}
