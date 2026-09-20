package modelprobe

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

func TestRunActualMatrixCompletesThreeModes(t *testing.T) {
	var healthCalls int32
	var chatCalls int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/health":
			atomic.AddInt32(&healthCalls, 1)
			w.WriteHeader(http.StatusOK)
		case "/v1/chat/completions":
			atomic.AddInt32(&chatCalls, 1)
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"choices": []any{map[string]any{
					"message": map[string]any{
						"content": `{"proposal":"bounded candidate","need_more_evidence":true}`,
					},
				}},
				"usage": map[string]any{
					"prompt_tokens":     2,
					"completion_tokens": 1,
					"total_tokens":      3,
				},
			})
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()

	matrix, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:    "matrix-001",
			SourceGitSHA:   artifactTestGitSHA,
			HealthEndpoint: server.URL + "/health",
			RuntimeName:    "fake-openai-runtime",
			RuntimeVersion: "test",
			Quantization:   "none",
			ContextSize:    4096,
			Threads:        2,
			Timeout:        2 * time.Second,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				MaxTokens:  800,
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures(),
	)
	if err != nil {
		t.Fatal(err)
	}

	if matrix.Schema != actualMatrixArtifactSchema || matrix.Status != "complete" {
		t.Fatalf("unexpected matrix metadata: %+v", matrix)
	}
	if len(matrix.Preflights) != 3 {
		t.Fatalf("preflight count=%d want=3", len(matrix.Preflights))
	}
	if got := atomic.LoadInt32(&healthCalls); got != 3 {
		t.Fatalf("health calls=%d want=3", got)
	}
	if got := atomic.LoadInt32(&chatCalls); got != 18 {
		t.Fatalf("chat calls=%d want=18", got)
	}
	if matrix.Raw == nil || matrix.Workspace == nil || matrix.Staged == nil || matrix.Comparison == nil {
		t.Fatalf("expected all mode artifacts and comparison: %+v", matrix)
	}
	if matrix.Raw.Telemetry.ActualModelInvocationAttempts != 7 ||
		matrix.Workspace.Telemetry.ActualModelInvocationAttempts != 7 ||
		matrix.Staged.Telemetry.ActualModelInvocationAttempts != 4 ||
		matrix.Staged.Telemetry.ActualSkippedCalls != 3 {
		t.Fatalf("unexpected invocation accounting: raw=%+v workspace=%+v staged=%+v",
			matrix.Raw.Telemetry, matrix.Workspace.Telemetry, matrix.Staged.Telemetry)
	}
	if len(matrix.Failures) != 0 {
		t.Fatalf("unexpected failures: %+v", matrix.Failures)
	}
}

func TestRunActualMatrixStopsOnBlockedPreflight(t *testing.T) {
	var chatCalls int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/health" {
			http.Error(w, "not ready", http.StatusServiceUnavailable)
			return
		}
		if r.URL.Path == "/v1/chat/completions" {
			atomic.AddInt32(&chatCalls, 1)
		}
		http.NotFound(w, r)
	}))
	defer server.Close()

	matrix, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:    "matrix-blocked",
			SourceGitSHA:   artifactTestGitSHA,
			HealthEndpoint: server.URL + "/health",
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures(),
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "blocked-preflight" {
		t.Fatalf("status=%q want=blocked-preflight", matrix.Status)
	}
	if len(matrix.Preflights) != 1 || len(matrix.Failures) != 1 {
		t.Fatalf("unexpected blocked artifact: %+v", matrix)
	}
	if matrix.Raw != nil || matrix.Comparison != nil {
		t.Fatalf("blocked preflight must not produce run/comparison: %+v", matrix)
	}
	if got := atomic.LoadInt32(&chatCalls); got != 0 {
		t.Fatalf("chat calls=%d want=0", got)
	}
}

func TestRunActualMatrixPreservesInferenceFailuresWithoutComparison(t *testing.T) {
	var chatCalls int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/health":
			w.WriteHeader(http.StatusOK)
		case "/v1/chat/completions":
			atomic.AddInt32(&chatCalls, 1)
			http.Error(w, "model failure", http.StatusInternalServerError)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()

	matrix, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:    "matrix-failed",
			SourceGitSHA:   artifactTestGitSHA,
			HealthEndpoint: server.URL + "/health",
			Timeout:        2 * time.Second,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures(),
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "incomplete-inference" {
		t.Fatalf("status=%q want=incomplete-inference", matrix.Status)
	}
	if got := atomic.LoadInt32(&chatCalls); got != 18 {
		t.Fatalf("chat calls=%d want=18", got)
	}
	if matrix.Raw == nil || matrix.Workspace == nil || matrix.Staged == nil {
		t.Fatalf("expected per-mode failure artifacts: %+v", matrix)
	}
	if matrix.Comparison != nil {
		t.Fatal("failed inference matrix must not produce comparison")
	}
	if len(matrix.Failures) != 18 {
		t.Fatalf("failure count=%d want=18", len(matrix.Failures))
	}
	if matrix.Staged.Telemetry.ActualSkippedCalls != 3 {
		t.Fatalf("staged explicit skips=%d want=3", matrix.Staged.Telemetry.ActualSkippedCalls)
	}
}

func TestRunActualMatrixRejectsInvalidIdentity(t *testing.T) {
	_, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:  "matrix-invalid",
			SourceGitSHA: "not-a-sha",
			Probe: Config{
				Endpoint: "http://127.0.0.1:8080/v1/chat/completions",
				Model:    "fake-model",
			},
		},
		cognitiveeval.ReferenceFixtures(),
	)
	if err == nil {
		t.Fatal("expected invalid source identity rejection")
	}
}
