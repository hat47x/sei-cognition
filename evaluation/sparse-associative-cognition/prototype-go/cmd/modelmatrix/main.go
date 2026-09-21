package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func main() {
	runIDPrefix := flag.String("run-id-prefix", "", "stable prefix used for raw/workspace/staged run ids")
	sourceGitSHA := flag.String("source-git-sha", "", "expected exact source Git SHA; defaults to current git HEAD")
	healthEndpoint := flag.String("health-endpoint", "http://127.0.0.1:8080/health", "runtime health endpoint")
	endpoint := flag.String("endpoint", "http://127.0.0.1:8080/v1/chat/completions", "OpenAI-compatible chat-completions endpoint")
	runtimeName := flag.String("runtime", "", "runtime name")
	runtimeVersion := flag.String("runtime-version", "", "runtime version")
	runtimePID := flag.Int("runtime-pid", 0, "optional local runtime server PID for Linux RSS/peak RSS sampling")
	runtimeMetricsEndpoint := flag.String("runtime-metrics-endpoint", "", "optional runtime-specific Prometheus metrics endpoint, e.g. llama.cpp /metrics")
	runtimePropsEndpoint := flag.String("runtime-props-endpoint", "", "optional runtime-specific properties endpoint, e.g. llama.cpp /props")
	model := flag.String("model", "", "model identifier sent to endpoint")
	modelFile := flag.String("model-file", "", "optional local model artifact file to hash once before the matrix run")
	expectedModelSHA256 := flag.String("expected-model-sha256", "", "optional expected SHA-256 for --model-file")
	quantization := flag.String("quantization", "", "quantization label")
	contextSize := flag.Int("context-size", 0, "runtime context size")
	threads := flag.Int("threads", 0, "runtime thread count")
	timeout := flag.Duration("timeout", 120*time.Second, "per-request timeout")
	maxTokens := flag.Int("max-tokens", 800, "maximum completion tokens")
	stream := flag.Bool("stream", false, "use OpenAI-compatible SSE streaming and measure first content-delta latency")
	fixtureID := flag.String("fixture", "all", "fixture id or all")
	output := flag.String("output", "", "new matrix artifact JSON path")
	flag.Parse()

	if *output == "" {
		fatalf("--output is required")
	}
	if _, err := os.Stat(*output); err == nil {
		fatalf("output already exists: %s", *output)
	} else if !os.IsNotExist(err) {
		fatalf("inspect output: %v", err)
	}

	resolvedSourceGitSHA, err := resolveSourceGitSHA(*sourceGitSHA)
	if err != nil {
		fatalf("resolve source identity: %v", err)
	}

	modelArtifact, err := modelprobe.ObserveModelArtifact(*modelFile, *expectedModelSHA256)
	if err != nil {
		fatalf("resolve model artifact identity: %v", err)
	}

	fixtures := selectFixtures(*fixtureID)
	if len(fixtures) == 0 {
		fatalf("fixture not found: %s", *fixtureID)
	}

	matrix, err := modelprobe.RunActualMatrix(
		context.Background(),
		modelprobe.MatrixConfig{
			RunIDPrefix:    *runIDPrefix,
			SourceGitSHA:   resolvedSourceGitSHA,
			HealthEndpoint: *healthEndpoint,
			RuntimeName:    *runtimeName,
			RuntimeVersion: *runtimeVersion,
			RuntimePID:     *runtimePID,
			RuntimeMetricsEndpoint: *runtimeMetricsEndpoint,
			RuntimePropsEndpoint: *runtimePropsEndpoint,
			ModelFilePath: *modelFile,
			ModelArtifact:  modelArtifact,
			Quantization:   *quantization,
			ContextSize:    *contextSize,
			Threads:        *threads,
			Timeout:        *timeout,
			Probe: modelprobe.Config{
				Endpoint:  *endpoint,
				Model:     *model,
				MaxTokens: *maxTokens,
				Stream:    *stream,
			},
		},
		fixtures,
	)
	if err != nil {
		fatalf("run matrix: %v", err)
	}

	if err := writeJSONExclusive(*output, matrix); err != nil {
		fatalf("write matrix artifact: %v", err)
	}
	if matrix.Status != "complete" {
		os.Exit(1)
	}
}

func resolveSourceGitSHA(expected string) (string, error) {
	output, err := exec.Command("git", "rev-parse", "HEAD").Output()
	if err != nil {
		return "", fmt.Errorf("git rev-parse HEAD: %w", err)
	}
	actual := strings.TrimSpace(string(output))
	if err := modelprobe.ValidateRunIdentity("source-head-check", actual); err != nil {
		return "", fmt.Errorf("current git HEAD is not a valid source identity: %w", err)
	}
	expected = strings.TrimSpace(expected)
	if expected != "" && expected != actual {
		return "", fmt.Errorf("source Git SHA mismatch: expected %s, current HEAD is %s", expected, actual)
	}
	return actual, nil
}

func selectFixtures(id string) []cognitiveeval.Fixture {
	all := cognitiveeval.ReferenceFixtures()
	if id == "all" {
		return all
	}
	for _, fixture := range all {
		if fixture.ID == id {
			return []cognitiveeval.Fixture{fixture}
		}
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
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
