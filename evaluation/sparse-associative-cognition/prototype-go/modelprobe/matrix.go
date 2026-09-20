package modelprobe

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

const actualMatrixArtifactSchema = "sei-cognition.local-model-matrix-run/v0"

type MatrixConfig struct {
	RunIDPrefix    string
	SourceGitSHA   string
	HealthEndpoint string
	RuntimeName    string
	RuntimeVersion string
	RuntimePID     int
	Quantization   string
	ContextSize    int
	Threads        int
	Timeout        time.Duration
	Probe          Config
}

type MatrixFailure struct {
	Mode      Mode   `json:"mode"`
	FixtureID string `json:"fixture_id"`
	Error     string `json:"error"`
}

type ActualMatrixArtifact struct {
	Schema       string               `json:"schema"`
	Status       string               `json:"status"`
	RunIDPrefix  string               `json:"run_id_prefix"`
	SourceGitSHA string               `json:"source_git_sha"`
	Model        string               `json:"model"`
	Preflights   []RunManifest        `json:"preflights"`
	Raw          *ActualRunArtifact   `json:"raw,omitempty"`
	Workspace    *ActualRunArtifact   `json:"workspace,omitempty"`
	Staged       *ActualRunArtifact   `json:"staged,omitempty"`
	Comparison   *ActualRunComparison `json:"comparison,omitempty"`
	RuntimeMemory RuntimeMemoryEvidence `json:"runtime_memory"`
	Failures     []MatrixFailure      `json:"failures,omitempty"`
	Notes        []string             `json:"notes"`
}

func RunActualMatrix(
	ctx context.Context,
	cfg MatrixConfig,
	fixtures []cognitiveeval.Fixture,
) (ActualMatrixArtifact, error) {
	cfg.RunIDPrefix = strings.TrimSpace(cfg.RunIDPrefix)
	cfg.SourceGitSHA = strings.TrimSpace(cfg.SourceGitSHA)
	cfg.Probe.Model = strings.TrimSpace(cfg.Probe.Model)
	if cfg.RunIDPrefix == "" {
		return ActualMatrixArtifact{}, fmt.Errorf("run_id_prefix is required")
	}
	if err := ValidateRunIdentity(cfg.RunIDPrefix+"-raw", cfg.SourceGitSHA); err != nil {
		return ActualMatrixArtifact{}, err
	}
	if cfg.Probe.Model == "" {
		return ActualMatrixArtifact{}, fmt.Errorf("model is required")
	}
	if strings.TrimSpace(cfg.Probe.Endpoint) == "" {
		return ActualMatrixArtifact{}, fmt.Errorf("probe endpoint is required")
	}
	if len(fixtures) == 0 {
		return ActualMatrixArtifact{}, fmt.Errorf("at least one fixture is required")
	}
	if cfg.Timeout <= 0 {
		cfg.Timeout = 120 * time.Second
	}

	matrix := ActualMatrixArtifact{
		Schema:       actualMatrixArtifactSchema,
		Status:       "evaluation-only",
		RunIDPrefix:  cfg.RunIDPrefix,
		SourceGitSHA: cfg.SourceGitSHA,
		Model:         cfg.Probe.Model,
		RuntimeMemory: newRuntimeMemoryEvidence(cfg.RuntimePID),
		Notes: []string{
			"complete means the three probe modes executed without invocation errors and produced a descriptive comparison",
			"complete does not mean task success, human adjudication, model adoption, or Product Value",
			"runtime process RSS is optional execution evidence; first-token latency, energy, and total system cost remain separate evidence",
		},
	}
	matrix.RuntimeMemory.Observe("matrix-start", "")

	modes := []Mode{ModeRaw, ModeWorkspace, ModeStaged}
	artifacts := make(map[Mode]ActualRunArtifact, len(modes))
	for _, mode := range modes {
		runID := cfg.RunIDPrefix + "-" + string(mode)
		preflight := Preflight(ctx, cfg.HealthEndpoint, cfg.Probe.HTTPClient)
		preflight.RunID = runID
		preflight.SourceGitSHA = cfg.SourceGitSHA
		preflight.RuntimeName = cfg.RuntimeName
		preflight.RuntimeVersion = cfg.RuntimeVersion
		preflight.Model = cfg.Probe.Model
		preflight.Quantization = cfg.Quantization
		preflight.ContextSize = cfg.ContextSize
		preflight.Threads = cfg.Threads
		preflight.Fixture = "all"
		preflight.Mode = mode
		matrix.Preflights = append(matrix.Preflights, preflight)

		if !preflightReady(preflight) {
			matrix.RuntimeMemory.Observe("blocked-preflight", mode)
			matrix.Status = "blocked-preflight"
			matrix.Failures = append(matrix.Failures, MatrixFailure{
				Mode:      mode,
				FixtureID: "preflight",
				Error:     preflightFailureReason(preflight),
			})
			return matrix, nil
		}

		artifact, failures, err := runActualMode(ctx, cfg, fixtures, mode, runID)
		if err != nil {
			return ActualMatrixArtifact{}, err
		}
		artifacts[mode] = artifact
		matrix.Failures = append(matrix.Failures, failures...)
		switch mode {
		case ModeRaw:
			matrix.Raw = &artifact
		case ModeWorkspace:
			matrix.Workspace = &artifact
		case ModeStaged:
			matrix.Staged = &artifact
		}
		matrix.RuntimeMemory.Observe("after-"+string(mode), mode)
	}

	if len(matrix.Failures) > 0 {
		matrix.Status = "incomplete-inference"
		return matrix, nil
	}

	comparison, err := CompareActualRuns(
		artifacts[ModeRaw],
		artifacts[ModeWorkspace],
		artifacts[ModeStaged],
	)
	if err != nil {
		return ActualMatrixArtifact{}, fmt.Errorf("compare completed matrix runs: %w", err)
	}
	matrix.Comparison = &comparison
	matrix.Status = "complete"
	return matrix, nil
}

func runActualMode(
	ctx context.Context,
	cfg MatrixConfig,
	fixtures []cognitiveeval.Fixture,
	mode Mode,
	runID string,
) (ActualRunArtifact, []MatrixFailure, error) {
	results := make([]Result, 0, len(fixtures))
	observations := make([]ActualRunObservation, 0, len(fixtures))
	failures := make([]MatrixFailure, 0)

	for _, fixture := range fixtures {
		plan, err := BuildPlan(fixture, mode)
		if err != nil {
			return ActualRunArtifact{}, nil, fmt.Errorf("fixture %s plan: %w", fixture.ID, err)
		}

		requestCtx, cancel := context.WithTimeout(ctx, cfg.Timeout)
		result, runErr := Run(requestCtx, cfg.Probe, fixture, mode)
		cancel()

		observations = append(
			observations,
			ObserveActualRun(plan, result, runErr),
		)
		if runErr != nil {
			failures = append(failures, MatrixFailure{
				Mode:      mode,
				FixtureID: fixture.ID,
				Error:     runErr.Error(),
			})
			continue
		}
		results = append(results, result)
	}

	summary, err := SummarizeActualTelemetry(
		runID,
		cfg.SourceGitSHA,
		cfg.Probe.Model,
		mode,
		fixtures,
		observations,
	)
	if err != nil {
		return ActualRunArtifact{}, nil, err
	}
	artifact, err := BuildActualRunArtifact(summary, results)
	if err != nil {
		return ActualRunArtifact{}, nil, err
	}
	return artifact, failures, nil
}

func preflightReady(manifest RunManifest) bool {
	return manifest.Endpoint.Reachable &&
		manifest.Endpoint.Error == "" &&
		manifest.Endpoint.HTTPStatus >= 200 &&
		manifest.Endpoint.HTTPStatus < 300
}

func preflightFailureReason(manifest RunManifest) string {
	if manifest.Endpoint.Error != "" {
		return manifest.Endpoint.Error
	}
	if !manifest.Endpoint.Reachable {
		return "health endpoint is not reachable"
	}
	return fmt.Sprintf("health endpoint returned HTTP %d", manifest.Endpoint.HTTPStatus)
}
