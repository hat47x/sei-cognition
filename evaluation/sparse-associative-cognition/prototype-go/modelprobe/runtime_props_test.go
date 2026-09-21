package modelprobe

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
)

func TestObserveRuntimePropsNotRequested(t *testing.T) {
	evidence := ObserveRuntimeProps(context.Background(), "", "", nil)
	if evidence.Status != "not-requested" {
		t.Fatalf("status=%q want=not-requested", evidence.Status)
	}
}

func TestObserveRuntimePropsCorrelatesSameModelFile(t *testing.T) {
	modelPath := filepath.Join(t.TempDir(), "model.gguf")
	if err := os.WriteFile(modelPath, []byte("model"), 0o600); err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"role":        "model",
			"model_path":  modelPath,
			"model_alias": "candidate",
			"default_generation_settings": map[string]any{
				"n_ctx": 4096,
			},
		})
	}))
	defer server.Close()

	evidence := ObserveRuntimeProps(context.Background(), server.URL, modelPath, server.Client())
	if evidence.Status != "observed" {
		t.Fatalf("status=%q want=observed: %+v", evidence.Status, evidence)
	}
	if evidence.ModelAlias != "candidate" || evidence.Role != "model" || evidence.ContextSize != 4096 {
		t.Fatalf("unexpected props evidence: %+v", evidence)
	}
	if evidence.ReportedModelFileName != "model.gguf" {
		t.Fatalf("reported model file=%q", evidence.ReportedModelFileName)
	}
	if evidence.SameFileAsSupplied == nil || !*evidence.SameFileAsSupplied {
		t.Fatalf("same-file correlation missing: %+v", evidence)
	}
}

func TestObserveRuntimePropsRecordsDifferentFile(t *testing.T) {
	dir := t.TempDir()
	supplied := filepath.Join(dir, "supplied.gguf")
	reported := filepath.Join(dir, "reported.gguf")
	if err := os.WriteFile(supplied, []byte("a"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(reported, []byte("b"), 0o600); err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"model_path": reported,
		})
	}))
	defer server.Close()

	evidence := ObserveRuntimeProps(context.Background(), server.URL, supplied, server.Client())
	if evidence.Status != "observed" {
		t.Fatalf("status=%q want=observed: %+v", evidence.Status, evidence)
	}
	if evidence.SameFileAsSupplied == nil || *evidence.SameFileAsSupplied {
		t.Fatalf("different model file must be recorded as false: %+v", evidence)
	}
}

func TestObserveRuntimePropsPartialWhenReportedPathIsInaccessible(t *testing.T) {
	supplied := filepath.Join(t.TempDir(), "supplied.gguf")
	if err := os.WriteFile(supplied, []byte("a"), 0o600); err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"model_path": "/definitely/not/present/model.gguf",
		})
	}))
	defer server.Close()

	evidence := ObserveRuntimeProps(context.Background(), server.URL, supplied, server.Client())
	if evidence.Status != "partial" {
		t.Fatalf("status=%q want=partial: %+v", evidence.Status, evidence)
	}
	if evidence.SameFileAsSupplied != nil || evidence.Error == "" {
		t.Fatalf("partial evidence must not invent same-file result: %+v", evidence)
	}
}

func TestObserveRuntimePropsUnavailableOnHTTPFailure(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "not ready", http.StatusServiceUnavailable)
	}))
	defer server.Close()

	evidence := ObserveRuntimeProps(context.Background(), server.URL, "", server.Client())
	if evidence.Status != "unavailable" {
		t.Fatalf("status=%q want=unavailable: %+v", evidence.Status, evidence)
	}
	if evidence.ReportedModelFileName != "" || evidence.SameFileAsSupplied != nil {
		t.Fatalf("unavailable props must not invent model identity: %+v", evidence)
	}
}
