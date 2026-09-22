package main

import (
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

const verificationSchema = "sei-cognition.local-model-matrix-verification/v0"

type verificationReport struct {
	Schema        string                          `json:"schema"`
	Status        string                          `json:"status"`
	MatrixStatus  string                          `json:"matrix_status"`
	SourceGitSHA  string                          `json:"source_git_sha"`
	Model         string                          `json:"model"`
	ModelArtifact modelprobe.ModelArtifactIdentity `json:"model_artifact"`
	Host          modelprobe.HostInfo               `json:"host"`
	Notes         []string                        `json:"notes"`
}

func main() {
	matrixPath := flag.String("matrix", "", "local-model matrix artifact JSON to validate")
	expectedSource := flag.String("expected-source-git-sha", "", "optional expected matrix source Git SHA")
	expectedModelSHA256 := flag.String("expected-model-sha256", "", "optional expected observed model artifact SHA-256")
	expectedGoVersion := flag.String("expected-go-version", "", "optional expected matrix Go runtime version")
	expectedHostOS := flag.String("expected-host-os", "", "optional expected matrix host OS")
	expectedHostArch := flag.String("expected-host-arch", "", "optional expected matrix host architecture")
	observedExitCode := flag.Int("observed-modelmatrix-exit-code", -1, "optional observed modelmatrix exit code from the run evidence sidecar")
	outputPath := flag.String("output", "", "optional new verification report JSON path; stdout when omitted")
	flag.Parse()

	if strings.TrimSpace(*matrixPath) == "" {
		fatalf("--matrix is required")
	}

	var matrix modelprobe.ActualMatrixArtifact
	if err := readStrictJSON(*matrixPath, &matrix); err != nil {
		fatalf("read matrix: %v", err)
	}
	if err := modelprobe.ValidateActualMatrixArtifact(matrix); err != nil {
		fatalf("validate matrix: %v", err)
	}

	if expected := strings.TrimSpace(*expectedSource); expected != "" {
		if err := modelprobe.ValidateRunIdentity("matrix-verify-expected-source", expected); err != nil {
			fatalf("expected source Git SHA: %v", err)
		}
		if matrix.SourceGitSHA != expected {
			fatalf("source Git SHA mismatch: expected %s, matrix has %s", expected, matrix.SourceGitSHA)
		}
	}

	if expected := strings.ToLower(strings.TrimSpace(*expectedModelSHA256)); expected != "" {
		if err := validateSHA256(expected); err != nil {
			fatalf("expected model SHA-256: %v", err)
		}
		if matrix.ModelArtifact.Status != "observed" {
			fatalf("expected model SHA-256 requires observed model artifact identity")
		}
		if matrix.ModelArtifact.SHA256 != expected {
			fatalf("model artifact SHA-256 mismatch: expected %s, matrix has %s", expected, matrix.ModelArtifact.SHA256)
		}
	}

	if err := validateExpectedHost(
		matrix.Host,
		*expectedGoVersion,
		*expectedHostOS,
		*expectedHostArch,
	); err != nil {
		fatalf("%v", err)
	}

	if *observedExitCode < -1 {
		fatalf("--observed-modelmatrix-exit-code must be -1, 0, or 1")
	}
	if *observedExitCode >= 0 {
		expectedExitCode := 1
		if matrix.Status == "complete" {
			expectedExitCode = 0
		}
		if *observedExitCode != expectedExitCode {
			fatalf(
				"modelmatrix exit code mismatch: matrix status %q expects %d, sidecar reports %d",
				matrix.Status,
				expectedExitCode,
				*observedExitCode,
			)
		}
	}

	report := verificationReport{
		Schema:        verificationSchema,
		Status:        "valid-evaluation-artifact",
		MatrixStatus:  matrix.Status,
		SourceGitSHA:  matrix.SourceGitSHA,
		Model:         matrix.Model,
		ModelArtifact: matrix.ModelArtifact,
		Host:          matrix.Host,
		Notes: []string{
			"structural validation does not prove model quality, task success, or Product Value",
			"expected source, model, host, Go runtime, and exit-code checks are only applied when explicitly supplied",
		},
	}

	if strings.TrimSpace(*outputPath) == "" {
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(report); err != nil {
			fatalf("encode verification report: %v", err)
		}
		return
	}

	if err := writeJSONExclusive(*outputPath, report); err != nil {
		fatalf("write verification report: %v", err)
	}
}

func validateExpectedHost(
	host modelprobe.HostInfo,
	expectedGoVersion string,
	expectedOS string,
	expectedArch string,
) error {
	if expected := strings.TrimSpace(expectedGoVersion); expected != "" && host.GoVersion != expected {
		return fmt.Errorf("Go runtime version mismatch: expected %s, matrix has %s", expected, host.GoVersion)
	}
	if expected := strings.TrimSpace(expectedOS); expected != "" && host.OS != expected {
		return fmt.Errorf("host OS mismatch: expected %s, matrix has %s", expected, host.OS)
	}
	if expected := strings.TrimSpace(expectedArch); expected != "" && host.Arch != expected {
		return fmt.Errorf("host architecture mismatch: expected %s, matrix has %s", expected, host.Arch)
	}
	return nil
}

func validateSHA256(value string) error {
	if len(value) != 64 {
		return fmt.Errorf("must be 64 hexadecimal characters")
	}
	if _, err := hex.DecodeString(value); err != nil {
		return fmt.Errorf("must be hexadecimal: %w", err)
	}
	return nil
}

func readStrictJSON(path string, value any) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(value); err != nil {
		return err
	}
	if err := decoder.Decode(&struct{}{}); err != io.EOF {
		if err == nil {
			return fmt.Errorf("trailing JSON value is not allowed")
		}
		return fmt.Errorf("trailing data: %w", err)
	}
	return nil
}

func writeJSONExclusive(path string, value any) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		return err
	}
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(value); err != nil {
		_ = file.Close()
		return err
	}
	return file.Close()
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\\n", args...)
	os.Exit(1)
}
