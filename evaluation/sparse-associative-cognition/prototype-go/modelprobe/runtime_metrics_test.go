package modelprobe

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestParseRuntimePrometheusMetrics(t *testing.T) {
	values, err := parseRuntimePrometheusMetrics(strings.NewReader(`
# HELP llamacpp:prompt_tokens_total Number of prompt tokens processed.
llamacpp:prompt_tokens_total 42
llamacpp:tokens_predicted_total 9
llamacpp:kv_cache_usage_ratio 0.25
llamacpp:kv_cache_tokens 128
llamacpp:n_tokens_max 256
other_metric 999
`))
	if err != nil {
		t.Fatal(err)
	}
	if values["llamacpp:prompt_tokens_total"] != 42 ||
		values["llamacpp:tokens_predicted_total"] != 9 ||
		values["llamacpp:kv_cache_usage_ratio"] != 0.25 ||
		values["llamacpp:kv_cache_tokens"] != 128 ||
		values["llamacpp:n_tokens_max"] != 256 {
		t.Fatalf("unexpected metrics: %+v", values)
	}
	if _, ok := values["other_metric"]; ok {
		t.Fatalf("unsupported metric leaked into evidence: %+v", values)
	}
}

func TestRuntimeMetricsEvidenceNotRequested(t *testing.T) {
	evidence := newRuntimeMetricsEvidence("")
	evidence.Observe(context.Background(), "matrix-start", "", nil)
	if evidence.Status != "not-requested" {
		t.Fatalf("status=%q want=not-requested", evidence.Status)
	}
	if len(evidence.Samples) != 0 || len(evidence.Errors) != 0 {
		t.Fatalf("not-requested evidence must remain empty: %+v", evidence)
	}
}

func TestRuntimeMetricsEvidenceRecordsSupportedMetrics(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		_, _ = w.Write([]byte(`
llamacpp:prompt_tokens_total 12
llamacpp:tokens_predicted_total 4
llamacpp:kv_cache_usage_ratio 0.5
llamacpp:kv_cache_tokens 64
llamacpp:n_tokens_max 96
`))
	}))
	defer server.Close()

	evidence := newRuntimeMetricsEvidence(server.URL)
	evidence.Observe(context.Background(), "after-raw", ModeRaw, server.Client())

	if evidence.Status != "observed" || len(evidence.Samples) != 1 {
		t.Fatalf("unexpected evidence: %+v", evidence)
	}
	sample := evidence.Samples[0]
	if sample.PromptTokensTotal == nil || *sample.PromptTokensTotal != 12 {
		t.Fatalf("prompt tokens not recorded: %+v", sample)
	}
	if sample.KVCacheUsageRatio == nil || *sample.KVCacheUsageRatio != 0.5 {
		t.Fatalf("kv cache ratio not recorded: %+v", sample)
	}
}

func TestRuntimeMetricsEvidenceUnavailableDoesNotInventZeros(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "metrics disabled", http.StatusNotFound)
	}))
	defer server.Close()

	evidence := newRuntimeMetricsEvidence(server.URL)
	evidence.Observe(context.Background(), "matrix-start", "", server.Client())

	if evidence.Status != "unavailable" {
		t.Fatalf("status=%q want=unavailable: %+v", evidence.Status, evidence)
	}
	if len(evidence.Samples) != 0 || len(evidence.Errors) != 1 {
		t.Fatalf("unavailable endpoint must not create zero-valued samples: %+v", evidence)
	}
}


func TestParseRuntimePrometheusMetricsRejectsNonFinite(t *testing.T) {
	for _, value := range []string{"NaN", "+Inf", "-Inf"} {
		_, err := parseRuntimePrometheusMetrics(strings.NewReader("llamacpp:kv_cache_usage_ratio " + value + "\n"))
		if err == nil {
			t.Fatalf("expected non-finite metric %q to be rejected", value)
		}
	}
}
