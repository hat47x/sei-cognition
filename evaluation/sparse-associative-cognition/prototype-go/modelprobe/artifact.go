package modelprobe

import (
	"fmt"
	"sort"
)

const (
	actualRunArtifactSchema = "sei-cognition.local-model-probe-run/v0"
	runComparisonSchema     = "sei-cognition.local-model-run-comparison/v0"
)

type ActualRunArtifact struct {
	Schema       string                 `json:"schema"`
	Status       string                 `json:"status"`
	RunID        string                 `json:"run_id"`
	SourceGitSHA string                 `json:"source_git_sha"`
	Model        string                 `json:"model"`
	Mode         Mode                   `json:"mode"`
	Telemetry    ActualTelemetrySummary `json:"telemetry"`
	Results      []Result               `json:"results"`
}

type EvaluationAggregate struct {
	Mode                                     Mode    `json:"mode"`
	ResultCount                              int     `json:"result_count"`
	EvaluatedFixtureCount                    int     `json:"evaluated_fixture_count"`
	SkippedFixtureCount                      int     `json:"skipped_fixture_count"`
	UnknownPreservationRateMean              float64 `json:"unknown_preservation_rate_mean"`
	ConflictPreservationRateMean             float64 `json:"conflict_preservation_rate_mean"`
	RecommendationDecisionSeparatedCount     int     `json:"recommendation_decision_separated_count"`
	HistoricalBasisViolationCount            int     `json:"historical_basis_violation_count"`
	UnsupportedClaimCount                    int     `json:"unsupported_claim_count"`
	InvalidReferenceCount                    int     `json:"invalid_reference_count"`
	NeedMoreEvidenceAppropriateCount         int     `json:"need_more_evidence_appropriate_count"`
	AllMaterialClaimsHaveValidSupportCount   int     `json:"all_material_claims_have_valid_support_count"`
	ResponseHeaderLatencyMSTotal             int64   `json:"response_header_latency_ms_total"`
	FirstTokenObservedCount                  int     `json:"first_token_observed_count"`
	FirstTokenLatencyMSMean                  float64 `json:"first_token_latency_ms_mean"`
	TotalLatencyMS                           int64   `json:"total_latency_ms"`
	TotalPromptTokens                        int     `json:"total_prompt_tokens"`
	TotalCompletionTokens                    int     `json:"total_completion_tokens"`
	TotalTokens                              int     `json:"total_tokens"`
}

type PairwiseEvaluationDelta struct {
	SharedEvaluatedFixtureCount                         int     `json:"shared_evaluated_fixture_count"`
	WorkspaceMinusRawUnknownPreservationRateMean       float64 `json:"workspace_minus_raw_unknown_preservation_rate_mean"`
	WorkspaceMinusRawConflictPreservationRateMean      float64 `json:"workspace_minus_raw_conflict_preservation_rate_mean"`
	WorkspaceMinusRawRecommendationDecisionSeparated  int     `json:"workspace_minus_raw_recommendation_decision_separated"`
	WorkspaceMinusRawHistoricalBasisViolations         int     `json:"workspace_minus_raw_historical_basis_violations"`
	WorkspaceMinusRawUnsupportedClaims                 int     `json:"workspace_minus_raw_unsupported_claims"`
	WorkspaceMinusRawInvalidReferences                 int     `json:"workspace_minus_raw_invalid_references"`
	WorkspaceMinusRawNeedMoreEvidenceAppropriate       int     `json:"workspace_minus_raw_need_more_evidence_appropriate"`
	WorkspaceMinusRawValidMaterialSupport              int     `json:"workspace_minus_raw_valid_material_support"`
	SharedFirstTokenFixtureCount                       int     `json:"shared_first_token_fixture_count"`
	WorkspaceMinusRawFirstTokenLatencyMSMean           float64 `json:"workspace_minus_raw_first_token_latency_ms_mean"`
	WorkspaceMinusRawLatencyMS                         int64   `json:"workspace_minus_raw_latency_ms"`
	WorkspaceMinusRawTotalTokens                       int     `json:"workspace_minus_raw_total_tokens"`
}

type InvocationComparison struct {
	RawActualInvocationAttempts       int `json:"raw_actual_invocation_attempts"`
	WorkspaceActualInvocationAttempts int `json:"workspace_actual_invocation_attempts"`
	StagedActualInvocationAttempts    int `json:"staged_actual_invocation_attempts"`
	StagedExplicitSkippedCalls        int `json:"staged_explicit_skipped_calls"`
	StagedPlanMismatchCount           int `json:"staged_plan_mismatch_count"`
}

type ActualRunComparison struct {
	Schema         string                  `json:"schema"`
	Status         string                  `json:"status"`
	SourceGitSHA   string                  `json:"source_git_sha"`
	Model          string                  `json:"model"`
	Raw            EvaluationAggregate     `json:"raw"`
	Workspace      EvaluationAggregate     `json:"workspace"`
	Staged         EvaluationAggregate     `json:"staged"`
	WorkspaceVsRaw PairwiseEvaluationDelta `json:"workspace_vs_raw"`
	Invocations    InvocationComparison    `json:"invocations"`
	Notes          []string                `json:"notes"`
}

func BuildActualRunArtifact(summary ActualTelemetrySummary, results []Result) (ActualRunArtifact, error) {
	if summary.Schema != "sei-cognition.actual-model-telemetry/v0" {
		return ActualRunArtifact{}, fmt.Errorf("telemetry schema %q is unsupported", summary.Schema)
	}
	if summary.Status != "evaluation-only" {
		return ActualRunArtifact{}, fmt.Errorf("telemetry status %q is unsupported", summary.Status)
	}
	if err := ValidateRunIdentity(summary.RunID, summary.SourceGitSHA); err != nil {
		return ActualRunArtifact{}, err
	}
	if summary.Model == "" {
		return ActualRunArtifact{}, fmt.Errorf("telemetry model is required")
	}
	if summary.Mode != ModeRaw && summary.Mode != ModeWorkspace && summary.Mode != ModeStaged {
		return ActualRunArtifact{}, fmt.Errorf("unsupported telemetry mode %q", summary.Mode)
	}

	observations := make(map[string]ActualRunObservation, len(summary.Observations))
	for _, observation := range summary.Observations {
		if observation.FixtureID == "" {
			return ActualRunArtifact{}, fmt.Errorf("telemetry observation fixture_id is required")
		}
		if _, exists := observations[observation.FixtureID]; exists {
			return ActualRunArtifact{}, fmt.Errorf("duplicate telemetry observation fixture %q", observation.FixtureID)
		}
		observations[observation.FixtureID] = observation
	}

	seen := make(map[string]struct{}, len(results))
	copied := append([]Result(nil), results...)
	for _, result := range copied {
		if result.FixtureID == "" {
			return ActualRunArtifact{}, fmt.Errorf("result fixture_id is required")
		}
		if _, exists := seen[result.FixtureID]; exists {
			return ActualRunArtifact{}, fmt.Errorf("duplicate result fixture %q", result.FixtureID)
		}
		seen[result.FixtureID] = struct{}{}
		if result.Mode != summary.Mode {
			return ActualRunArtifact{}, fmt.Errorf("fixture %s mode %q does not match telemetry mode %q", result.FixtureID, result.Mode, summary.Mode)
		}
		if result.Model != summary.Model {
			return ActualRunArtifact{}, fmt.Errorf("fixture %s model %q does not match telemetry model %q", result.FixtureID, result.Model, summary.Model)
		}
		observation, ok := observations[result.FixtureID]
		if !ok {
			return ActualRunArtifact{}, fmt.Errorf("fixture %s has no telemetry observation", result.FixtureID)
		}
		if result.ModelInvocationAttempted != observation.ModelInvocationAttempted ||
			result.Skipped != observation.Skipped {
			return ActualRunArtifact{}, fmt.Errorf("fixture %s result/telemetry invocation state mismatch", result.FixtureID)
		}
		if !result.Skipped && result.Evaluation == nil {
			return ActualRunArtifact{}, fmt.Errorf("fixture %s successful result has no evaluation report", result.FixtureID)
		}
	}
	sort.Slice(copied, func(i, j int) bool {
		return copied[i].FixtureID < copied[j].FixtureID
	})

	return ActualRunArtifact{
		Schema:       actualRunArtifactSchema,
		Status:       "evaluation-only",
		RunID:        summary.RunID,
		SourceGitSHA: summary.SourceGitSHA,
		Model:        summary.Model,
		Mode:         summary.Mode,
		Telemetry:    summary,
		Results:      copied,
	}, nil
}

func CompareActualRuns(raw, workspace, staged ActualRunArtifact) (ActualRunComparison, error) {
	for label, artifact := range map[string]ActualRunArtifact{
		"raw": raw, "workspace": workspace, "staged": staged,
	} {
		if err := validateActualRunArtifact(label, artifact); err != nil {
			return ActualRunComparison{}, err
		}
	}
	if raw.Mode != ModeRaw || workspace.Mode != ModeWorkspace || staged.Mode != ModeStaged {
		return ActualRunComparison{}, fmt.Errorf("comparison requires raw, workspace, staged artifacts in that order")
	}
	if raw.SourceGitSHA != workspace.SourceGitSHA || raw.SourceGitSHA != staged.SourceGitSHA {
		return ActualRunComparison{}, fmt.Errorf("all comparison artifacts must use the same source_git_sha")
	}
	if raw.Model != workspace.Model || raw.Model != staged.Model {
		return ActualRunComparison{}, fmt.Errorf("all comparison artifacts must use the same model")
	}

	rawAgg := aggregateEvaluations(raw)
	workspaceAgg := aggregateEvaluations(workspace)
	stagedAgg := aggregateEvaluations(staged)
	delta := pairwiseWorkspaceRaw(raw, workspace)

	return ActualRunComparison{
		Schema:         runComparisonSchema,
		Status:         "evaluation-only",
		SourceGitSHA:   raw.SourceGitSHA,
		Model:          raw.Model,
		Raw:            rawAgg,
		Workspace:      workspaceAgg,
		Staged:         stagedAgg,
		WorkspaceVsRaw: delta,
		Invocations: InvocationComparison{
			RawActualInvocationAttempts:       raw.Telemetry.ActualModelInvocationAttempts,
			WorkspaceActualInvocationAttempts: workspace.Telemetry.ActualModelInvocationAttempts,
			StagedActualInvocationAttempts:    staged.Telemetry.ActualModelInvocationAttempts,
			StagedExplicitSkippedCalls:        staged.Telemetry.ActualSkippedCalls,
			StagedPlanMismatchCount:           staged.Telemetry.PlanExecutionMismatchCount,
		},
		Notes: []string{
			"deltas are descriptive workspace-minus-raw measurements, not an overall score",
			"staged skips are routing observations and are not task-success evidence",
			"human adjudication, memory, first-token latency, and total system cost remain separate evidence",
		},
	}, nil
}

func validateActualRunArtifact(label string, artifact ActualRunArtifact) error {
	if artifact.Schema != actualRunArtifactSchema {
		return fmt.Errorf("%s artifact schema %q is unsupported", label, artifact.Schema)
	}
	if artifact.Status != "evaluation-only" {
		return fmt.Errorf("%s artifact status %q is unsupported", label, artifact.Status)
	}
	if err := ValidateRunIdentity(artifact.RunID, artifact.SourceGitSHA); err != nil {
		return fmt.Errorf("%s artifact identity: %w", label, err)
	}
	if artifact.Telemetry.RunID != artifact.RunID ||
		artifact.Telemetry.SourceGitSHA != artifact.SourceGitSHA ||
		artifact.Telemetry.Model != artifact.Model ||
		artifact.Telemetry.Mode != artifact.Mode {
		return fmt.Errorf("%s artifact outer identity does not match embedded telemetry", label)
	}
	rebuilt, err := BuildActualRunArtifact(artifact.Telemetry, artifact.Results)
	if err != nil {
		return fmt.Errorf("%s artifact consistency: %w", label, err)
	}
	if rebuilt.RunID != artifact.RunID ||
		rebuilt.SourceGitSHA != artifact.SourceGitSHA ||
		rebuilt.Model != artifact.Model ||
		rebuilt.Mode != artifact.Mode {
		return fmt.Errorf("%s artifact rebuilt identity mismatch", label)
	}
	return nil
}

func aggregateEvaluations(artifact ActualRunArtifact) EvaluationAggregate {
	aggregate := EvaluationAggregate{Mode: artifact.Mode, ResultCount: len(artifact.Results)}
	var unknownSum float64
	var conflictSum float64
	var firstTokenSum int64
	for _, result := range artifact.Results {
		aggregate.ResponseHeaderLatencyMSTotal += result.ResponseHeaderLatencyMS
		if result.FirstTokenObserved {
			aggregate.FirstTokenObservedCount++
			firstTokenSum += result.FirstTokenLatencyMS
		}
		aggregate.TotalLatencyMS += result.TotalLatencyMS
		aggregate.TotalPromptTokens += result.Usage.PromptTokens
		aggregate.TotalCompletionTokens += result.Usage.CompletionTokens
		aggregate.TotalTokens += result.Usage.TotalTokens
		if result.Skipped {
			aggregate.SkippedFixtureCount++
			continue
		}
		if result.Evaluation == nil {
			continue
		}
		report := result.Evaluation
		aggregate.EvaluatedFixtureCount++
		unknownSum += report.UnknownPreservationRate
		conflictSum += report.ConflictPreservationRate
		if report.RecommendationDecisionSeparated {
			aggregate.RecommendationDecisionSeparatedCount++
		}
		aggregate.HistoricalBasisViolationCount += report.HistoricalBasisViolationCount
		aggregate.UnsupportedClaimCount += report.UnsupportedClaimCount
		aggregate.InvalidReferenceCount += report.InvalidReferenceCount
		if report.NeedMoreEvidenceAppropriate {
			aggregate.NeedMoreEvidenceAppropriateCount++
		}
		if report.AllMaterialClaimsHaveValidSupport {
			aggregate.AllMaterialClaimsHaveValidSupportCount++
		}
	}
	if aggregate.EvaluatedFixtureCount > 0 {
		aggregate.UnknownPreservationRateMean = unknownSum / float64(aggregate.EvaluatedFixtureCount)
		aggregate.ConflictPreservationRateMean = conflictSum / float64(aggregate.EvaluatedFixtureCount)
	}
	if aggregate.FirstTokenObservedCount > 0 {
		aggregate.FirstTokenLatencyMSMean = float64(firstTokenSum) / float64(aggregate.FirstTokenObservedCount)
	}
	return aggregate
}

func pairwiseWorkspaceRaw(raw, workspace ActualRunArtifact) PairwiseEvaluationDelta {
	rawByFixture := resultMap(raw.Results)
	workspaceByFixture := resultMap(workspace.Results)
	var delta PairwiseEvaluationDelta
	var unknownDelta float64
	var conflictDelta float64
	var firstTokenDelta float64

	fixtureIDs := make([]string, 0, len(rawByFixture))
	for fixtureID := range rawByFixture {
		fixtureIDs = append(fixtureIDs, fixtureID)
	}
	sort.Strings(fixtureIDs)

	for _, fixtureID := range fixtureIDs {
		rawResult := rawByFixture[fixtureID]
		workspaceResult, ok := workspaceByFixture[fixtureID]
		if !ok || rawResult.Evaluation == nil || workspaceResult.Evaluation == nil ||
			rawResult.Skipped || workspaceResult.Skipped {
			continue
		}
		r := rawResult.Evaluation
		w := workspaceResult.Evaluation
		delta.SharedEvaluatedFixtureCount++
		unknownDelta += w.UnknownPreservationRate - r.UnknownPreservationRate
		conflictDelta += w.ConflictPreservationRate - r.ConflictPreservationRate
		delta.WorkspaceMinusRawRecommendationDecisionSeparated += boolInt(w.RecommendationDecisionSeparated) - boolInt(r.RecommendationDecisionSeparated)
		delta.WorkspaceMinusRawHistoricalBasisViolations += w.HistoricalBasisViolationCount - r.HistoricalBasisViolationCount
		delta.WorkspaceMinusRawUnsupportedClaims += w.UnsupportedClaimCount - r.UnsupportedClaimCount
		delta.WorkspaceMinusRawInvalidReferences += w.InvalidReferenceCount - r.InvalidReferenceCount
		delta.WorkspaceMinusRawNeedMoreEvidenceAppropriate += boolInt(w.NeedMoreEvidenceAppropriate) - boolInt(r.NeedMoreEvidenceAppropriate)
		delta.WorkspaceMinusRawValidMaterialSupport += boolInt(w.AllMaterialClaimsHaveValidSupport) - boolInt(r.AllMaterialClaimsHaveValidSupport)
		if rawResult.FirstTokenObserved && workspaceResult.FirstTokenObserved {
			delta.SharedFirstTokenFixtureCount++
			firstTokenDelta += float64(workspaceResult.FirstTokenLatencyMS - rawResult.FirstTokenLatencyMS)
		}
		delta.WorkspaceMinusRawLatencyMS += workspaceResult.TotalLatencyMS - rawResult.TotalLatencyMS
		delta.WorkspaceMinusRawTotalTokens += workspaceResult.Usage.TotalTokens - rawResult.Usage.TotalTokens
	}
	if delta.SharedEvaluatedFixtureCount > 0 {
		delta.WorkspaceMinusRawUnknownPreservationRateMean =
			unknownDelta / float64(delta.SharedEvaluatedFixtureCount)
		delta.WorkspaceMinusRawConflictPreservationRateMean =
			conflictDelta / float64(delta.SharedEvaluatedFixtureCount)
	}
	if delta.SharedFirstTokenFixtureCount > 0 {
		delta.WorkspaceMinusRawFirstTokenLatencyMSMean =
			firstTokenDelta / float64(delta.SharedFirstTokenFixtureCount)
	}
	return delta
}

func resultMap(results []Result) map[string]Result {
	out := make(map[string]Result, len(results))
	for _, result := range results {
		out[result.FixtureID] = result
	}
	return out
}

func boolInt(value bool) int {
	if value {
		return 1
	}
	return 0
}
