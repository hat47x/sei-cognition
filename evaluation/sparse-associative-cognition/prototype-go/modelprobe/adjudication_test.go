package modelprobe

import "testing"

func completeMatrixForAdjudication(t *testing.T) ActualMatrixArtifact {
	t.Helper()
	raw := makeArtifact(t, ModeRaw)
	workspace := makeArtifact(t, ModeWorkspace)
	staged := makeArtifact(t, ModeStaged)
	comparison, err := CompareActualRuns(raw, workspace, staged)
	if err != nil {
		t.Fatal(err)
	}
	matrix := ActualMatrixArtifact{
		Schema:       actualMatrixArtifactSchema,
		Status:       "complete",
		RunIDPrefix:  "matrix-review",
		SourceGitSHA: raw.SourceGitSHA,
		Model:        raw.Model,
		Host: HostInfo{
			OS:         "linux",
			Arch:       "amd64",
			LogicalCPU: 8,
			GoVersion:  "go1.25.14",
		},
		ModelArtifact: ModelArtifactIdentity{
			Status:    modelArtifactObserved,
			FileName:  "candidate.gguf",
			SizeBytes: 1234,
			SHA256:    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		},
		Raw:        &raw,
		Workspace:  &workspace,
		Staged:     &staged,
		Comparison: &comparison,
	}
	matrix.Preflights = []RunManifest{
		readyValidationPreflight(matrix, ModeRaw),
		readyValidationPreflight(matrix, ModeWorkspace),
		readyValidationPreflight(matrix, ModeStaged),
	}
	return matrix
}

func TestBuildHumanAdjudicationTemplateOnlyIncludesEvaluatedResults(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	template, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	if template.Schema != humanAdjudicationSchema ||
		template.Status != "human-review-template" {
		t.Fatalf("unexpected template metadata: %+v", template)
	}
	if len(template.Entries) != 18 {
		t.Fatalf("entries=%d want=18", len(template.Entries))
	}
	for _, entry := range template.Entries {
		if entry.TaskSuccess != "unassessed" ||
			entry.SemanticBoundary != "unassessed" {
			t.Fatalf("template must not pre-judge result: %+v", entry)
		}
	}
}

func TestValidateHumanAdjudicationProducesPerModeCounts(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.ReviewedAt = "2026-09-20T14:55:00Z"
	for i := range adjudication.Entries {
		adjudication.Entries[i].TaskSuccess = "pass"
		adjudication.Entries[i].SemanticBoundary = "preserved"
	}

	report, err := ValidateHumanAdjudication(matrix, adjudication)
	if err != nil {
		t.Fatal(err)
	}
	if report.Status != "human-adjudicated-evaluation-only" {
		t.Fatalf("status=%q", report.Status)
	}
	if report.Raw.AssessedCount != 7 ||
		report.Workspace.AssessedCount != 7 ||
		report.Staged.AssessedCount != 4 {
		t.Fatalf("unexpected mode counts: raw=%+v workspace=%+v staged=%+v",
			report.Raw, report.Workspace, report.Staged)
	}
	if report.Raw.TaskPassCount != 7 ||
		report.Workspace.TaskPassCount != 7 ||
		report.Staged.TaskPassCount != 4 {
		t.Fatalf("unexpected pass counts: %+v", report)
	}
}

func TestValidateHumanAdjudicationRejectsUnassessedEntry(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.ReviewedAt = "2026-09-20T14:55:00Z"

	if _, err := ValidateHumanAdjudication(matrix, adjudication); err == nil {
		t.Fatal("expected unassessed entry rejection")
	}
}

func TestValidateHumanAdjudicationRequiresNotesForUncertainOrFailure(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.ReviewedAt = "2026-09-20T14:55:00Z"
	for i := range adjudication.Entries {
		adjudication.Entries[i].TaskSuccess = "pass"
		adjudication.Entries[i].SemanticBoundary = "preserved"
	}
	adjudication.Entries[0].TaskSuccess = "uncertain"

	if _, err := ValidateHumanAdjudication(matrix, adjudication); err == nil {
		t.Fatal("expected notes requirement")
	}
	adjudication.Entries[0].Notes = "The proposal is plausible but task completion is ambiguous."
	if _, err := ValidateHumanAdjudication(matrix, adjudication); err != nil {
		t.Fatalf("expected noted uncertain judgment to validate: %v", err)
	}
}

func TestValidateHumanAdjudicationRejectsSkippedFixtureEntry(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.ReviewedAt = "2026-09-20T14:55:00Z"
	for i := range adjudication.Entries {
		adjudication.Entries[i].TaskSuccess = "pass"
		adjudication.Entries[i].SemanticBoundary = "preserved"
	}

	for _, result := range matrix.Staged.Results {
		if result.Skipped {
			adjudication.Entries = append(adjudication.Entries, HumanAdjudicationEntry{
				Mode:             ModeStaged,
				FixtureID:        result.FixtureID,
				TaskSuccess:      "pass",
				SemanticBoundary: "preserved",
			})
			break
		}
	}

	if _, err := ValidateHumanAdjudication(matrix, adjudication); err == nil {
		t.Fatal("expected skipped fixture adjudication rejection")
	}
}

func TestValidateHumanAdjudicationRejectsSourceMismatch(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.SourceGitSHA = "0123456789abcdef0123456789abcdef01234567"

	if _, err := ValidateHumanAdjudication(matrix, adjudication); err == nil {
		t.Fatal("expected source mismatch rejection")
	}
}

func TestValidateHumanAdjudicationRejectsModelArtifactMismatch(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.ModelArtifact.SHA256 = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	if _, err := ValidateHumanAdjudication(matrix, adjudication); err == nil {
		t.Fatal("expected model artifact mismatch rejection")
	}
}


func TestValidateHumanAdjudicationRejectsLegacyV0Schema(t *testing.T) {
	matrix := completeMatrixForAdjudication(t)
	adjudication, err := BuildHumanAdjudicationTemplate(matrix, "reviewer-1")
	if err != nil {
		t.Fatal(err)
	}
	adjudication.Schema = legacyHumanAdjudicationSchema

	if _, err := ValidateHumanAdjudication(matrix, adjudication); err == nil {
		t.Fatal("expected legacy v0 human adjudication rejection")
	}
}
