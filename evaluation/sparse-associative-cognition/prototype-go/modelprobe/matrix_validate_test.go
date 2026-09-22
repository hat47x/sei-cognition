package modelprobe

import "testing"

func completeMatrixForValidation(t *testing.T) ActualMatrixArtifact {
	t.Helper()
	matrix := completeMatrixForAdjudication(t)
	matrix.Preflights = []RunManifest{
		readyValidationPreflight(matrix, ModeRaw),
		readyValidationPreflight(matrix, ModeWorkspace),
		readyValidationPreflight(matrix, ModeStaged),
	}
	return matrix
}

func readyValidationPreflight(matrix ActualMatrixArtifact, mode Mode) RunManifest {
	return RunManifest{
		Schema:       runManifestSchema,
		Status:       "evaluation-only",
		RunID:        matrix.RunIDPrefix + "-" + string(mode),
		SourceGitSHA: matrix.SourceGitSHA,
		Host:          matrix.Host,
		Endpoint: EndpointInfo{
			Reachable:  true,
			HTTPStatus: 200,
		},
		Model:         matrix.Model,
		ModelArtifact: matrix.ModelArtifact,
		Fixture:       "all",
		Mode:          mode,
	}
}

func TestValidateActualMatrixArtifactComplete(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	if err := ValidateActualMatrixArtifact(matrix); err != nil {
		t.Fatal(err)
	}
}

func TestValidateActualMatrixArtifactRejectsTamperedComparison(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	matrix.Comparison.Raw.TotalTokens++

	if err := ValidateActualMatrixArtifact(matrix); err == nil {
		t.Fatal("expected tampered comparison rejection")
	}
}

func TestValidateActualMatrixArtifactRejectsPreflightIdentityMismatch(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	matrix.Preflights[1].SourceGitSHA = "0123456789abcdef0123456789abcdef01234567"

	if err := ValidateActualMatrixArtifact(matrix); err == nil {
		t.Fatal("expected preflight source identity mismatch rejection")
	}
}

func TestValidateActualMatrixArtifactIncompleteInference(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	matrix.Status = "incomplete-inference"
	matrix.Comparison = nil
	matrix.Failures = []MatrixFailure{{
		Mode:      ModeRaw,
		FixtureID: "fixture-failure",
		Error:     "synthetic invocation failure",
	}}
	matrix.Raw.Telemetry.CompleteWithoutInvocationError = false

	if err := ValidateActualMatrixArtifact(matrix); err != nil {
		t.Fatal(err)
	}
}

func TestValidateActualMatrixArtifactBlockedPreflight(t *testing.T) {
	base := completeMatrixForValidation(t)
	blocked := ActualMatrixArtifact{
		Schema:        actualMatrixArtifactSchema,
		Status:        "blocked-preflight",
		RunIDPrefix:   base.RunIDPrefix,
		SourceGitSHA:  base.SourceGitSHA,
		Model:         base.Model,
		ModelArtifact: base.ModelArtifact,
		Host:          base.Host,
		Preflights: []RunManifest{
			{
				Schema:       runManifestSchema,
				Status:       "evaluation-only",
				RunID:        base.RunIDPrefix + "-" + string(ModeRaw),
				SourceGitSHA: base.SourceGitSHA,
				Host:          base.Host,
				Endpoint: EndpointInfo{
					Reachable:  true,
					HTTPStatus: 503,
				},
				Model:         base.Model,
				ModelArtifact: base.ModelArtifact,
				Fixture:       "all",
				Mode:          ModeRaw,
			},
		},
		RuntimeProps: RuntimePropsEvidence{Status: "not-requested"},
		Failures: []MatrixFailure{{
			Mode:      ModeRaw,
			FixtureID: "preflight",
			Error:     "health endpoint returned HTTP 503",
		}},
	}
	if err := ValidateActualMatrixArtifact(blocked); err != nil {
		t.Fatal(err)
	}
}

func TestValidateActualMatrixArtifactBlockedModelIdentity(t *testing.T) {
	base := completeMatrixForValidation(t)
	same := false
	blocked := ActualMatrixArtifact{
		Schema:        actualMatrixArtifactSchema,
		Status:        "blocked-model-identity",
		RunIDPrefix:   base.RunIDPrefix,
		SourceGitSHA:  base.SourceGitSHA,
		Model:         base.Model,
		ModelArtifact: base.ModelArtifact,
		Host:          base.Host,
		RuntimeProps: RuntimePropsEvidence{
			Status:             "observed",
			SameFileAsSupplied: &same,
		},
		Failures: []MatrixFailure{{
			Stage:     "runtime-props",
			FixtureID: "model-identity",
			Error:     "runtime-reported model file does not match operator-supplied model file",
		}},
	}
	if err := ValidateActualMatrixArtifact(blocked); err != nil {
		t.Fatal(err)
	}
}

func TestValidateActualMatrixArtifactRejectsBlockedIdentityWithoutMismatch(t *testing.T) {
	base := completeMatrixForValidation(t)
	same := true
	blocked := ActualMatrixArtifact{
		Schema:        actualMatrixArtifactSchema,
		Status:        "blocked-model-identity",
		RunIDPrefix:   base.RunIDPrefix,
		SourceGitSHA:  base.SourceGitSHA,
		Model:         base.Model,
		ModelArtifact: base.ModelArtifact,
		Host:          base.Host,
		RuntimeProps: RuntimePropsEvidence{
			Status:             "observed",
			SameFileAsSupplied: &same,
		},
		Failures: []MatrixFailure{{
			Stage:     "runtime-props",
			FixtureID: "model-identity",
			Error:     "synthetic mismatch",
		}},
	}
	if err := ValidateActualMatrixArtifact(blocked); err == nil {
		t.Fatal("expected blocked-model-identity mismatch evidence rejection")
	}
}


func TestValidateActualMatrixArtifactRejectsHostMismatch(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	matrix.Preflights[1].Host.GoVersion = "go1.25.13"

	if err := ValidateActualMatrixArtifact(matrix); err == nil {
		t.Fatal("expected preflight host mismatch rejection")
	}
}

func TestValidateActualMatrixArtifactRejectsMissingMatrixHost(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	matrix.Host = HostInfo{}

	if err := ValidateActualMatrixArtifact(matrix); err == nil {
		t.Fatal("expected missing matrix host rejection")
	}
}


func TestValidateActualMatrixArtifactRejectsLegacyV0Schema(t *testing.T) {
	matrix := completeMatrixForValidation(t)
	matrix.Schema = legacyActualMatrixArtifactSchema

	if err := ValidateActualMatrixArtifact(matrix); err == nil {
		t.Fatal("expected legacy v0 matrix schema rejection")
	}
}
