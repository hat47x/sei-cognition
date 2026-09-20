package modelprobe

import (
	"fmt"
	"sort"
	"strings"
	"time"
)

const (
	humanAdjudicationSchema       = "sei-cognition.local-model-human-adjudication/v0"
	humanAdjudicationReportSchema = "sei-cognition.local-model-human-adjudication-report/v0"
)

type HumanAdjudicationEntry struct {
	Mode             Mode   `json:"mode"`
	FixtureID        string `json:"fixture_id"`
	TaskSuccess      string `json:"task_success"`
	SemanticBoundary string `json:"semantic_boundary"`
	Notes            string `json:"notes,omitempty"`
}

type HumanAdjudication struct {
	Schema       string                   `json:"schema"`
	Status       string                   `json:"status"`
	SourceGitSHA string                   `json:"source_git_sha"`
	Model        string                   `json:"model"`
	ReviewerLabel string                  `json:"reviewer_label"`
	ReviewedAt   string                   `json:"reviewed_at"`
	Entries      []HumanAdjudicationEntry `json:"entries"`
	Notes        []string                 `json:"notes,omitempty"`
}

type HumanAdjudicationModeSummary struct {
	Mode                       Mode `json:"mode"`
	AssessedCount              int  `json:"assessed_count"`
	TaskPassCount              int  `json:"task_pass_count"`
	TaskFailCount              int  `json:"task_fail_count"`
	TaskUncertainCount         int  `json:"task_uncertain_count"`
	BoundaryPreservedCount     int  `json:"boundary_preserved_count"`
	BoundaryViolatedCount      int  `json:"boundary_violated_count"`
	BoundaryUncertainCount     int  `json:"boundary_uncertain_count"`
}

type HumanAdjudicationReport struct {
	Schema       string                         `json:"schema"`
	Status       string                         `json:"status"`
	SourceGitSHA string                         `json:"source_git_sha"`
	Model        string                         `json:"model"`
	ReviewerLabel string                        `json:"reviewer_label"`
	ReviewedAt   string                         `json:"reviewed_at"`
	Raw          HumanAdjudicationModeSummary   `json:"raw"`
	Workspace    HumanAdjudicationModeSummary   `json:"workspace"`
	Staged       HumanAdjudicationModeSummary   `json:"staged"`
	Entries      []HumanAdjudicationEntry       `json:"entries"`
	Notes        []string                       `json:"notes"`
}

func BuildHumanAdjudicationTemplate(
	matrix ActualMatrixArtifact,
	reviewerLabel string,
) (HumanAdjudication, error) {
	if err := validateMatrixForHumanAdjudication(matrix); err != nil {
		return HumanAdjudication{}, err
	}
	reviewerLabel = strings.TrimSpace(reviewerLabel)
	if reviewerLabel == "" {
		return HumanAdjudication{}, fmt.Errorf("reviewer_label is required")
	}

	entries := requiredHumanAdjudicationEntries(matrix)
	for i := range entries {
		entries[i].TaskSuccess = "unassessed"
		entries[i].SemanticBoundary = "unassessed"
	}

	return HumanAdjudication{
		Schema:        humanAdjudicationSchema,
		Status:        "draft",
		SourceGitSHA:  matrix.SourceGitSHA,
		Model:         matrix.Model,
		ReviewerLabel: reviewerLabel,
		ReviewedAt:    "",
		Entries:       entries,
		Notes: []string{
			"fill reviewed_at with the actual human review time in RFC3339",
			"replace every unassessed task_success and semantic_boundary value before validation",
			"do not infer an overall model score from these per-fixture judgments",
		},
	}, nil
}

func ValidateHumanAdjudication(
	matrix ActualMatrixArtifact,
	adjudication HumanAdjudication,
) (HumanAdjudicationReport, error) {
	if err := validateMatrixForHumanAdjudication(matrix); err != nil {
		return HumanAdjudicationReport{}, err
	}
	if adjudication.Schema != humanAdjudicationSchema {
		return HumanAdjudicationReport{}, fmt.Errorf("adjudication schema %q is unsupported", adjudication.Schema)
	}
	if adjudication.SourceGitSHA != matrix.SourceGitSHA {
		return HumanAdjudicationReport{}, fmt.Errorf("adjudication source_git_sha does not match matrix")
	}
	if adjudication.Model != matrix.Model {
		return HumanAdjudicationReport{}, fmt.Errorf("adjudication model does not match matrix")
	}
	adjudication.ReviewerLabel = strings.TrimSpace(adjudication.ReviewerLabel)
	if adjudication.ReviewerLabel == "" {
		return HumanAdjudicationReport{}, fmt.Errorf("reviewer_label is required")
	}
	if strings.TrimSpace(adjudication.ReviewedAt) == "" {
		return HumanAdjudicationReport{}, fmt.Errorf("reviewed_at is required")
	}
	if _, err := time.Parse(time.RFC3339, adjudication.ReviewedAt); err != nil {
		return HumanAdjudicationReport{}, fmt.Errorf("reviewed_at must be RFC3339: %w", err)
	}

	required := requiredHumanAdjudicationEntries(matrix)
	requiredByKey := make(map[string]HumanAdjudicationEntry, len(required))
	for _, entry := range required {
		requiredByKey[adjudicationKey(entry.Mode, entry.FixtureID)] = entry
	}

	seen := make(map[string]struct{}, len(adjudication.Entries))
	entries := append([]HumanAdjudicationEntry(nil), adjudication.Entries...)
	summaries := map[Mode]*HumanAdjudicationModeSummary{
		ModeRaw:       {Mode: ModeRaw},
		ModeWorkspace: {Mode: ModeWorkspace},
		ModeStaged:    {Mode: ModeStaged},
	}

	for i := range entries {
		entry := &entries[i]
		entry.FixtureID = strings.TrimSpace(entry.FixtureID)
		key := adjudicationKey(entry.Mode, entry.FixtureID)
		if _, exists := seen[key]; exists {
			return HumanAdjudicationReport{}, fmt.Errorf("duplicate adjudication entry %s", key)
		}
		seen[key] = struct{}{}
		if _, ok := requiredByKey[key]; !ok {
			return HumanAdjudicationReport{}, fmt.Errorf("adjudication entry %s does not correspond to an evaluated model result", key)
		}
		if !validTaskSuccess(entry.TaskSuccess) {
			return HumanAdjudicationReport{}, fmt.Errorf("entry %s task_success %q is not assessed", key, entry.TaskSuccess)
		}
		if !validSemanticBoundary(entry.SemanticBoundary) {
			return HumanAdjudicationReport{}, fmt.Errorf("entry %s semantic_boundary %q is not assessed", key, entry.SemanticBoundary)
		}
		if (entry.TaskSuccess == "fail" ||
			entry.TaskSuccess == "uncertain" ||
			entry.SemanticBoundary == "violated" ||
			entry.SemanticBoundary == "uncertain") &&
			strings.TrimSpace(entry.Notes) == "" {
			return HumanAdjudicationReport{}, fmt.Errorf("entry %s requires notes for fail/uncertain judgment", key)
		}

		summary := summaries[entry.Mode]
		if summary == nil {
			return HumanAdjudicationReport{}, fmt.Errorf("entry %s uses unsupported mode %q", key, entry.Mode)
		}
		summary.AssessedCount++
		switch entry.TaskSuccess {
		case "pass":
			summary.TaskPassCount++
		case "fail":
			summary.TaskFailCount++
		case "uncertain":
			summary.TaskUncertainCount++
		}
		switch entry.SemanticBoundary {
		case "preserved":
			summary.BoundaryPreservedCount++
		case "violated":
			summary.BoundaryViolatedCount++
		case "uncertain":
			summary.BoundaryUncertainCount++
		}
	}

	if len(seen) != len(requiredByKey) {
		missing := make([]string, 0)
		for key := range requiredByKey {
			if _, ok := seen[key]; !ok {
				missing = append(missing, key)
			}
		}
		sort.Strings(missing)
		return HumanAdjudicationReport{}, fmt.Errorf("adjudication is incomplete; missing entries: %s", strings.Join(missing, ", "))
	}

	sort.Slice(entries, func(i, j int) bool {
		if modeRank(entries[i].Mode) != modeRank(entries[j].Mode) {
			return modeRank(entries[i].Mode) < modeRank(entries[j].Mode)
		}
		return entries[i].FixtureID < entries[j].FixtureID
	})

	return HumanAdjudicationReport{
		Schema:        humanAdjudicationReportSchema,
		Status:        "human-adjudicated-evaluation-only",
		SourceGitSHA:  matrix.SourceGitSHA,
		Model:         matrix.Model,
		ReviewerLabel: adjudication.ReviewerLabel,
		ReviewedAt:    adjudication.ReviewedAt,
		Raw:           *summaries[ModeRaw],
		Workspace:     *summaries[ModeWorkspace],
		Staged:        *summaries[ModeStaged],
		Entries:       entries,
		Notes: []string{
			"counts preserve per-mode human judgments and are not an overall model score",
			"human adjudication does not turn model output into Truth or Decision",
			"staged routing skips are excluded because no model result exists to adjudicate",
		},
	}, nil
}

func validateMatrixForHumanAdjudication(matrix ActualMatrixArtifact) error {
	if matrix.Schema != actualMatrixArtifactSchema {
		return fmt.Errorf("matrix schema %q is unsupported", matrix.Schema)
	}
	if matrix.Status != "complete" {
		return fmt.Errorf("matrix status %q is not complete", matrix.Status)
	}
	if err := ValidateRunIdentity(matrix.RunIDPrefix+"-human-review", matrix.SourceGitSHA); err != nil {
		return err
	}
	if strings.TrimSpace(matrix.Model) == "" {
		return fmt.Errorf("matrix model is required")
	}
	if matrix.Raw == nil || matrix.Workspace == nil || matrix.Staged == nil || matrix.Comparison == nil {
		return fmt.Errorf("complete matrix requires raw/workspace/staged artifacts and comparison")
	}
	for label, artifact := range map[string]ActualRunArtifact{
		"raw": *matrix.Raw, "workspace": *matrix.Workspace, "staged": *matrix.Staged,
	} {
		if err := validateActualRunArtifact(label, artifact); err != nil {
			return err
		}
		if artifact.SourceGitSHA != matrix.SourceGitSHA || artifact.Model != matrix.Model {
			return fmt.Errorf("%s artifact identity does not match matrix", label)
		}
	}
	return nil
}

func requiredHumanAdjudicationEntries(matrix ActualMatrixArtifact) []HumanAdjudicationEntry {
	var entries []HumanAdjudicationEntry
	for _, artifact := range []ActualRunArtifact{*matrix.Raw, *matrix.Workspace, *matrix.Staged} {
		for _, result := range artifact.Results {
			if result.Skipped || result.Evaluation == nil {
				continue
			}
			entries = append(entries, HumanAdjudicationEntry{
				Mode:      artifact.Mode,
				FixtureID: result.FixtureID,
			})
		}
	}
	sort.Slice(entries, func(i, j int) bool {
		if modeRank(entries[i].Mode) != modeRank(entries[j].Mode) {
			return modeRank(entries[i].Mode) < modeRank(entries[j].Mode)
		}
		return entries[i].FixtureID < entries[j].FixtureID
	})
	return entries
}

func adjudicationKey(mode Mode, fixtureID string) string {
	return string(mode) + "/" + fixtureID
}

func modeRank(mode Mode) int {
	switch mode {
	case ModeRaw:
		return 0
	case ModeWorkspace:
		return 1
	case ModeStaged:
		return 2
	default:
		return 99
	}
}

func validTaskSuccess(value string) bool {
	return value == "pass" || value == "fail" || value == "uncertain"
}

func validSemanticBoundary(value string) bool {
	return value == "preserved" || value == "violated" || value == "uncertain"
}
