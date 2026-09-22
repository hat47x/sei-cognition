package modelprobe

import (
	"fmt"
	"reflect"
	"strings"
)

func ValidateActualMatrixArtifact(matrix ActualMatrixArtifact) error {
	if matrix.Schema != actualMatrixArtifactSchema {
		return fmt.Errorf("matrix schema %q is unsupported", matrix.Schema)
	}
	if strings.TrimSpace(matrix.RunIDPrefix) == "" {
		return fmt.Errorf("matrix run_id_prefix is required")
	}
	if err := ValidateRunIdentity(matrix.RunIDPrefix+"-matrix", matrix.SourceGitSHA); err != nil {
		return fmt.Errorf("matrix identity: %w", err)
	}
	if strings.TrimSpace(matrix.Model) == "" {
		return fmt.Errorf("matrix model is required")
	}
	if err := ValidateModelArtifactIdentity(matrix.ModelArtifact); err != nil {
		return fmt.Errorf("matrix model artifact identity: %w", err)
	}
	if err := validateHostInfo(matrix.Host); err != nil {
		return fmt.Errorf("matrix host: %w", err)
	}
	if len(matrix.Preflights) > 3 {
		return fmt.Errorf("matrix has %d preflights; maximum is 3", len(matrix.Preflights))
	}
	if err := validateMatrixPreflights(matrix); err != nil {
		return err
	}
	if err := validateMatrixNestedArtifacts(matrix); err != nil {
		return err
	}

	switch matrix.Status {
	case "complete":
		return validateCompleteMatrixArtifact(matrix)
	case "incomplete-inference":
		return validateIncompleteMatrixArtifact(matrix)
	case "blocked-preflight":
		return validateBlockedPreflightMatrixArtifact(matrix)
	case "blocked-model-identity":
		return validateBlockedModelIdentityMatrixArtifact(matrix)
	default:
		return fmt.Errorf("matrix status %q is unsupported", matrix.Status)
	}
}

func validateHostInfo(host HostInfo) error {
	if strings.TrimSpace(host.OS) == "" {
		return fmt.Errorf("os is required")
	}
	if strings.TrimSpace(host.Arch) == "" {
		return fmt.Errorf("arch is required")
	}
	if host.LogicalCPU <= 0 {
		return fmt.Errorf("logical_cpu must be positive")
	}
	if strings.TrimSpace(host.GoVersion) == "" {
		return fmt.Errorf("go_version is required")
	}
	return nil
}

func validateMatrixPreflights(matrix ActualMatrixArtifact) error {
	modes := []Mode{ModeRaw, ModeWorkspace, ModeStaged}
	for i, preflight := range matrix.Preflights {
		mode := modes[i]
		if preflight.Schema != "sei-cognition.local-model-run-manifest/v0" {
			return fmt.Errorf("preflight %d schema %q is unsupported", i, preflight.Schema)
		}
		if preflight.Status != "evaluation-only" {
			return fmt.Errorf("preflight %d status %q is unsupported", i, preflight.Status)
		}
		if err := validateHostInfo(preflight.Host); err != nil {
			return fmt.Errorf("preflight %d host: %w", i, err)
		}
		if !reflect.DeepEqual(preflight.Host, matrix.Host) {
			return fmt.Errorf("preflight %d host does not match matrix host", i)
		}
		if preflight.RunID != matrix.RunIDPrefix+"-"+string(mode) {
			return fmt.Errorf("preflight %d run_id does not match matrix", i)
		}
		if preflight.SourceGitSHA != matrix.SourceGitSHA {
			return fmt.Errorf("preflight %d source_git_sha does not match matrix", i)
		}
		if preflight.Model != matrix.Model {
			return fmt.Errorf("preflight %d model does not match matrix", i)
		}
		if !SameModelArtifactIdentity(preflight.ModelArtifact, matrix.ModelArtifact) {
			return fmt.Errorf("preflight %d model_artifact does not match matrix", i)
		}
		if preflight.Mode != mode {
			return fmt.Errorf("preflight %d mode %q does not match expected %q", i, preflight.Mode, mode)
		}
		if preflight.Fixture != "all" {
			return fmt.Errorf("preflight %d fixture %q does not match matrix fixture set", i, preflight.Fixture)
		}
	}
	return nil
}

func validateMatrixNestedArtifacts(matrix ActualMatrixArtifact) error {
	for _, item := range []struct {
		label    string
		expected Mode
		artifact *ActualRunArtifact
	}{
		{"raw", ModeRaw, matrix.Raw},
		{"workspace", ModeWorkspace, matrix.Workspace},
		{"staged", ModeStaged, matrix.Staged},
	} {
		if item.artifact == nil {
			continue
		}
		if item.artifact.Mode != item.expected {
			return fmt.Errorf("%s artifact mode %q does not match expected %q", item.label, item.artifact.Mode, item.expected)
		}
		if err := validateActualRunArtifact(item.label, *item.artifact); err != nil {
			return err
		}
		if item.artifact.SourceGitSHA != matrix.SourceGitSHA ||
			item.artifact.Model != matrix.Model {
			return fmt.Errorf("%s artifact identity does not match matrix", item.label)
		}
	}
	return nil
}

func validateCompleteMatrixArtifact(matrix ActualMatrixArtifact) error {
	if len(matrix.Preflights) != 3 {
		return fmt.Errorf("complete matrix requires 3 preflights")
	}
	for i, preflight := range matrix.Preflights {
		if !preflightReady(preflight) {
			return fmt.Errorf("complete matrix preflight %d is not ready", i)
		}
	}
	if len(matrix.Failures) != 0 {
		return fmt.Errorf("complete matrix must not contain failures")
	}
	if matrix.Raw == nil || matrix.Workspace == nil || matrix.Staged == nil || matrix.Comparison == nil {
		return fmt.Errorf("complete matrix requires raw/workspace/staged artifacts and comparison")
	}
	for label, artifact := range map[string]*ActualRunArtifact{
		"raw": matrix.Raw, "workspace": matrix.Workspace, "staged": matrix.Staged,
	} {
		if !artifact.Telemetry.CompleteWithoutInvocationError {
			return fmt.Errorf("complete matrix %s telemetry is incomplete", label)
		}
	}

	rebuilt, err := CompareActualRuns(*matrix.Raw, *matrix.Workspace, *matrix.Staged)
	if err != nil {
		return fmt.Errorf("rebuild complete matrix comparison: %w", err)
	}
	if !reflect.DeepEqual(rebuilt, *matrix.Comparison) {
		return fmt.Errorf("matrix comparison does not match rebuilt comparison")
	}
	return nil
}

func validateIncompleteMatrixArtifact(matrix ActualMatrixArtifact) error {
	if len(matrix.Preflights) != 3 {
		return fmt.Errorf("incomplete-inference matrix requires 3 preflights")
	}
	for i, preflight := range matrix.Preflights {
		if !preflightReady(preflight) {
			return fmt.Errorf("incomplete-inference preflight %d is not ready", i)
		}
	}
	if matrix.Raw == nil || matrix.Workspace == nil || matrix.Staged == nil {
		return fmt.Errorf("incomplete-inference matrix requires all 3 mode artifacts")
	}
	if matrix.Comparison != nil {
		return fmt.Errorf("incomplete-inference matrix must not contain comparison")
	}
	if len(matrix.Failures) == 0 {
		return fmt.Errorf("incomplete-inference matrix requires failures")
	}
	if matrix.Raw.Telemetry.CompleteWithoutInvocationError &&
		matrix.Workspace.Telemetry.CompleteWithoutInvocationError &&
		matrix.Staged.Telemetry.CompleteWithoutInvocationError {
		return fmt.Errorf("incomplete-inference matrix has no incomplete mode telemetry")
	}
	return nil
}

func validateBlockedPreflightMatrixArtifact(matrix ActualMatrixArtifact) error {
	if len(matrix.Preflights) < 1 || len(matrix.Preflights) > 3 {
		return fmt.Errorf("blocked-preflight matrix requires 1 to 3 preflights")
	}
	blockedIndex := len(matrix.Preflights) - 1
	for i, preflight := range matrix.Preflights {
		if i < blockedIndex && !preflightReady(preflight) {
			return fmt.Errorf("blocked-preflight matrix has an earlier blocked preflight at index %d", i)
		}
		if i == blockedIndex && preflightReady(preflight) {
			return fmt.Errorf("blocked-preflight matrix final preflight is ready")
		}
	}
	if matrix.Comparison != nil {
		return fmt.Errorf("blocked-preflight matrix must not contain comparison")
	}
	artifacts := []*ActualRunArtifact{matrix.Raw, matrix.Workspace, matrix.Staged}
	for i, artifact := range artifacts {
		if i < blockedIndex && artifact == nil {
			return fmt.Errorf("blocked-preflight matrix is missing prior mode artifact %d", i)
		}
		if i >= blockedIndex && artifact != nil {
			return fmt.Errorf("blocked-preflight matrix contains artifact at or after blocked mode %d", i)
		}
	}
	if len(matrix.Failures) == 0 {
		return fmt.Errorf("blocked-preflight matrix requires failures")
	}
	blockedMode := []Mode{ModeRaw, ModeWorkspace, ModeStaged}[blockedIndex]
	found := false
	for _, failure := range matrix.Failures {
		if failure.Mode == blockedMode && failure.FixtureID == "preflight" {
			found = true
			break
		}
	}
	if !found {
		return fmt.Errorf("blocked-preflight matrix is missing the blocking preflight failure")
	}
	return nil
}

func validateBlockedModelIdentityMatrixArtifact(matrix ActualMatrixArtifact) error {
	if len(matrix.Preflights) != 0 {
		return fmt.Errorf("blocked-model-identity matrix must not contain preflights")
	}
	if matrix.Raw != nil || matrix.Workspace != nil || matrix.Staged != nil || matrix.Comparison != nil {
		return fmt.Errorf("blocked-model-identity matrix must stop before mode artifacts")
	}
	if matrix.RuntimeProps.Status != "observed" ||
		matrix.RuntimeProps.SameFileAsSupplied == nil ||
		*matrix.RuntimeProps.SameFileAsSupplied {
		return fmt.Errorf("blocked-model-identity matrix requires an explicit runtime props same-file mismatch")
	}
	found := false
	for _, failure := range matrix.Failures {
		if failure.Stage == "runtime-props" && failure.FixtureID == "model-identity" {
			found = true
			break
		}
	}
	if !found {
		return fmt.Errorf("blocked-model-identity matrix is missing runtime-props model-identity failure")
	}
	return nil
}
