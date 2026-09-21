package modelprobe

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"sync/atomic"
	"syscall"
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
	if matrix.RuntimeMemory.Status != "not-requested" {
		t.Fatalf("runtime memory status=%q want=not-requested", matrix.RuntimeMemory.Status)
	}
	if matrix.RuntimeProcess.Status != "not-requested" {
		t.Fatalf("runtime process status=%q want=not-requested", matrix.RuntimeProcess.Status)
	}
	if matrix.RuntimeMetrics.Status != "not-requested" {
		t.Fatalf("runtime metrics status=%q want=not-requested", matrix.RuntimeMetrics.Status)
	}
	if matrix.RuntimeProps.Status != "not-requested" {
		t.Fatalf("runtime props status=%q want=not-requested", matrix.RuntimeProps.Status)
	}
	if matrix.RuntimeModelMapping.Status != "not-requested" {
		t.Fatalf("runtime model mapping status=%q want=not-requested", matrix.RuntimeModelMapping.Status)
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


func TestRunActualMatrixRecordsRuntimeMemoryWhenRequested(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/health":
			w.WriteHeader(http.StatusOK)
		case "/v1/chat/completions":
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"choices": []any{map[string]any{
					"message": map[string]any{
						"content": `{"proposal":"bounded candidate","need_more_evidence":false}`,
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

	fixtures := cognitiveeval.ReferenceFixtures()[:1]
	matrix, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:    "matrix-memory",
			SourceGitSHA:   artifactTestGitSHA,
			HealthEndpoint: server.URL + "/health",
			RuntimePID:     os.Getpid(),
			Timeout:        2 * time.Second,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		fixtures,
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "complete" {
		t.Fatalf("status=%q want=complete", matrix.Status)
	}
	if matrix.RuntimeMemory.Status != "observed" {
		t.Fatalf("runtime memory status=%q want=observed: %+v", matrix.RuntimeMemory.Status, matrix.RuntimeMemory)
	}
	if len(matrix.RuntimeMemory.Samples) != 4 {
		t.Fatalf("memory samples=%d want=4", len(matrix.RuntimeMemory.Samples))
	}
	if matrix.RuntimeMemory.MaxObservedRSSBytes == 0 || matrix.RuntimeMemory.PeakRSSBytes == 0 {
		t.Fatalf("runtime memory summary must be non-zero: %+v", matrix.RuntimeMemory)
	}
	if matrix.RuntimeProcess.Status != "observed" {
		t.Fatalf("runtime process status=%q want=observed: %+v", matrix.RuntimeProcess.Status, matrix.RuntimeProcess)
	}
	if matrix.RuntimeProcess.PID != os.Getpid() || matrix.RuntimeProcess.ExecutableName == "" || matrix.RuntimeProcess.SizeBytes <= 0 || len(matrix.RuntimeProcess.SHA256) != 64 {
		t.Fatalf("runtime process identity must be populated: %+v", matrix.RuntimeProcess)
	}
	for _, preflight := range matrix.Preflights {
		if preflight.RuntimeProcess.SHA256 != matrix.RuntimeProcess.SHA256 || preflight.RuntimeProcess.SizeBytes != matrix.RuntimeProcess.SizeBytes {
			t.Fatalf("preflight runtime process identity mismatch: matrix=%+v preflight=%+v", matrix.RuntimeProcess, preflight.RuntimeProcess)
		}
	}
}

func TestRunActualMatrixPropagatesModelArtifactToPreflight(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "not ready", http.StatusServiceUnavailable)
	}))
	defer server.Close()

	identity := ModelArtifactIdentity{
		Status:    modelArtifactObserved,
		FileName:  "candidate.gguf",
		SizeBytes: 1234,
		SHA256:    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
	}
	matrix, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:    "matrix-model-artifact",
			SourceGitSHA:   artifactTestGitSHA,
			HealthEndpoint: server.URL,
			ModelArtifact:  identity,
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
	if !SameModelArtifactIdentity(matrix.ModelArtifact, identity) {
		t.Fatalf("matrix model artifact mismatch: %+v", matrix.ModelArtifact)
	}
	if len(matrix.Preflights) != 1 || !SameModelArtifactIdentity(matrix.Preflights[0].ModelArtifact, identity) {
		t.Fatalf("preflight model artifact mismatch: %+v", matrix.Preflights)
	}
}

func TestRunActualMatrixRejectsMalformedModelArtifact(t *testing.T) {
	_, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:  "matrix-bad-model-artifact",
			SourceGitSHA: artifactTestGitSHA,
			ModelArtifact: ModelArtifactIdentity{
				Status:    modelArtifactObserved,
				FileName:  "candidate.gguf",
				SizeBytes: 1234,
				SHA256:    "not-a-digest",
			},
			Probe: Config{
				Endpoint: "http://127.0.0.1:8080/v1/chat/completions",
				Model:    "fake-model",
			},
		},
		cognitiveeval.ReferenceFixtures(),
	)
	if err == nil {
		t.Fatal("expected malformed model artifact rejection")
	}
}


func TestRunActualMatrixRecordsRuntimeMetricsWhenRequested(t *testing.T) {
	var chatCalls int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/health":
			w.WriteHeader(http.StatusOK)
		case "/metrics":
			calls := atomic.LoadInt32(&chatCalls)
			w.Header().Set("Content-Type", "text/plain")
			_, _ = w.Write([]byte(
				"llamacpp:prompt_tokens_total " + strconv.FormatInt(int64(calls*2), 10) + "\n" +
					"llamacpp:tokens_predicted_total " + strconv.FormatInt(int64(calls), 10) + "\n" +
					"llamacpp:kv_cache_usage_ratio 0.25\n" +
					"llamacpp:kv_cache_tokens 64\n" +
					"llamacpp:n_tokens_max 128\n",
			))
		case "/v1/chat/completions":
			atomic.AddInt32(&chatCalls, 1)
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"choices": []any{map[string]any{
					"message": map[string]any{
						"content": `{"proposal":"bounded candidate","need_more_evidence":false}`,
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
			RunIDPrefix:           "matrix-runtime-metrics",
			SourceGitSHA:          artifactTestGitSHA,
			HealthEndpoint:        server.URL + "/health",
			RuntimeMetricsEndpoint: server.URL + "/metrics",
			Timeout:               2 * time.Second,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures()[:1],
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "complete" {
		t.Fatalf("status=%q want=complete", matrix.Status)
	}
	if matrix.RuntimeMetrics.Status != "observed" {
		t.Fatalf("runtime metrics status=%q want=observed: %+v", matrix.RuntimeMetrics.Status, matrix.RuntimeMetrics)
	}
	if len(matrix.RuntimeMetrics.Samples) != 4 {
		t.Fatalf("runtime metrics samples=%d want=4", len(matrix.RuntimeMetrics.Samples))
	}
	for _, sample := range matrix.RuntimeMetrics.Samples {
		if sample.PromptTokensTotal == nil ||
			sample.TokensPredictedTotal == nil ||
			sample.KVCacheUsageRatio == nil ||
			sample.KVCacheTokens == nil ||
			sample.ContextTokensMax == nil {
			t.Fatalf("runtime metrics sample is incomplete: %+v", sample)
		}
	}
}


func TestRunActualMatrixRecordsRuntimeModelMappingWhenRequested(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	modelPath := filepath.Join(t.TempDir(), "candidate.gguf")
	modelBytes := make([]byte, 4096)
	modelBytes[0] = 1
	if err := os.WriteFile(modelPath, modelBytes, 0o600); err != nil {
		t.Fatal(err)
	}
	modelFile, err := os.OpenFile(modelPath, os.O_RDWR, 0)
	if err != nil {
		t.Fatal(err)
	}
	defer modelFile.Close()
	mapped, err := syscall.Mmap(int(modelFile.Fd()), 0, len(modelBytes), syscall.PROT_READ, syscall.MAP_SHARED)
	if err != nil {
		t.Fatal(err)
	}
	defer syscall.Munmap(mapped)

	identity, err := ObserveModelArtifact(modelPath, "")
	if err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/health":
			w.WriteHeader(http.StatusOK)
		case "/v1/chat/completions":
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"choices": []any{map[string]any{
					"message": map[string]any{
						"content": `{"proposal":"bounded candidate","need_more_evidence":false}`,
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
			RunIDPrefix:    "matrix-model-mapping",
			SourceGitSHA:   artifactTestGitSHA,
			HealthEndpoint: server.URL + "/health",
			RuntimePID:     os.Getpid(),
			ModelFilePath:  modelPath,
			ModelArtifact:  identity,
			Timeout:        2 * time.Second,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures()[:1],
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "complete" {
		t.Fatalf("status=%q want=complete", matrix.Status)
	}
	if matrix.RuntimeModelMapping.Status != "observed" {
		t.Fatalf("runtime model mapping status=%q want=observed: %+v", matrix.RuntimeModelMapping.Status, matrix.RuntimeModelMapping)
	}
	if matrix.RuntimeModelMapping.MappingCount < 1 {
		t.Fatalf("mapping_count=%d want>=1", matrix.RuntimeModelMapping.MappingCount)
	}
	if matrix.RuntimeModelMapping.ModelFileName != identity.FileName {
		t.Fatalf("model filename mismatch: mapping=%q identity=%q", matrix.RuntimeModelMapping.ModelFileName, identity.FileName)
	}
}


func TestRunActualMatrixRecordsRuntimePropsWhenRequested(t *testing.T) {
	modelPath := filepath.Join(t.TempDir(), "candidate.gguf")
	if err := os.WriteFile(modelPath, []byte("candidate"), 0o600); err != nil {
		t.Fatal(err)
	}
	identity, err := ObserveModelArtifact(modelPath, "")
	if err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/health":
			w.WriteHeader(http.StatusOK)
		case "/props":
			_ = json.NewEncoder(w).Encode(map[string]any{
				"role":        "model",
				"model_path":  modelPath,
				"model_alias": "candidate",
				"default_generation_settings": map[string]any{
					"n_ctx": 4096,
				},
			})
		case "/v1/chat/completions":
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"choices": []any{map[string]any{
					"message": map[string]any{
						"content": `{"proposal":"bounded candidate","need_more_evidence":false}`,
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
			RunIDPrefix:         "matrix-runtime-props",
			SourceGitSHA:        artifactTestGitSHA,
			HealthEndpoint:      server.URL + "/health",
			RuntimePropsEndpoint: server.URL + "/props",
			ModelFilePath:       modelPath,
			ModelArtifact:       identity,
			Timeout:             2 * time.Second,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures()[:1],
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "complete" {
		t.Fatalf("status=%q want=complete", matrix.Status)
	}
	if matrix.RuntimeProps.Status != "observed" {
		t.Fatalf("runtime props status=%q want=observed: %+v", matrix.RuntimeProps.Status, matrix.RuntimeProps)
	}
	if matrix.RuntimeProps.ModelAlias != "candidate" || matrix.RuntimeProps.ReportedModelFileName != identity.FileName {
		t.Fatalf("unexpected runtime props: %+v", matrix.RuntimeProps)
	}
	if matrix.RuntimeProps.SameFileAsSupplied == nil || !*matrix.RuntimeProps.SameFileAsSupplied {
		t.Fatalf("same-file runtime props correlation missing: %+v", matrix.RuntimeProps)
	}
}


func TestRunActualMatrixBlocksExplicitRuntimeModelIdentityMismatch(t *testing.T) {
	dir := t.TempDir()
	suppliedPath := filepath.Join(dir, "supplied.gguf")
	reportedPath := filepath.Join(dir, "reported.gguf")
	if err := os.WriteFile(suppliedPath, []byte("supplied"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(reportedPath, []byte("reported"), 0o600); err != nil {
		t.Fatal(err)
	}
	identity, err := ObserveModelArtifact(suppliedPath, "")
	if err != nil {
		t.Fatal(err)
	}

	var healthCalls int32
	var chatCalls int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/props":
			_ = json.NewEncoder(w).Encode(map[string]any{
				"model_path":  reportedPath,
				"model_alias": "wrong-model",
			})
		case "/health":
			atomic.AddInt32(&healthCalls, 1)
			w.WriteHeader(http.StatusOK)
		case "/v1/chat/completions":
			atomic.AddInt32(&chatCalls, 1)
			http.Error(w, "must not be called", http.StatusInternalServerError)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()

	matrix, err := RunActualMatrix(
		context.Background(),
		MatrixConfig{
			RunIDPrefix:          "matrix-model-identity-mismatch",
			SourceGitSHA:         artifactTestGitSHA,
			HealthEndpoint:       server.URL + "/health",
			RuntimePropsEndpoint: server.URL + "/props",
			ModelFilePath:        suppliedPath,
			ModelArtifact:        identity,
			Probe: Config{
				Endpoint:   server.URL + "/v1/chat/completions",
				Model:      "fake-model",
				HTTPClient: server.Client(),
			},
		},
		cognitiveeval.ReferenceFixtures()[:1],
	)
	if err != nil {
		t.Fatal(err)
	}
	if matrix.Status != "blocked-model-identity" {
		t.Fatalf("status=%q want=blocked-model-identity: %+v", matrix.Status, matrix)
	}
	if matrix.RuntimeProps.SameFileAsSupplied == nil || *matrix.RuntimeProps.SameFileAsSupplied {
		t.Fatalf("expected explicit same-file mismatch: %+v", matrix.RuntimeProps)
	}
	if len(matrix.Failures) != 1 || matrix.Failures[0].Stage != "runtime-props" {
		t.Fatalf("unexpected failures: %+v", matrix.Failures)
	}
	if got := atomic.LoadInt32(&healthCalls); got != 0 {
		t.Fatalf("health calls=%d want=0", got)
	}
	if got := atomic.LoadInt32(&chatCalls); got != 0 {
		t.Fatalf("chat calls=%d want=0", got)
	}
	if len(matrix.Preflights) != 0 || matrix.Raw != nil || matrix.Comparison != nil {
		t.Fatalf("identity mismatch must stop before preflight/inference: %+v", matrix)
	}
}
