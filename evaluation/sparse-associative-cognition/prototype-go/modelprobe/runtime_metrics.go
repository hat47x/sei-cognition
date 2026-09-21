package modelprobe

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"
)

type RuntimeMetricsSample struct {
	ObservedAt           string   `json:"observed_at"`
	Stage                string   `json:"stage"`
	Mode                 Mode     `json:"mode,omitempty"`
	PromptTokensTotal    *float64 `json:"prompt_tokens_total,omitempty"`
	TokensPredictedTotal *float64 `json:"tokens_predicted_total,omitempty"`
	KVCacheUsageRatio    *float64 `json:"kv_cache_usage_ratio,omitempty"`
	KVCacheTokens        *float64 `json:"kv_cache_tokens,omitempty"`
	ContextTokensMax     *float64 `json:"context_tokens_max,omitempty"`
}

type RuntimeMetricsEvidence struct {
	Status   string                 `json:"status"`
	Endpoint string                 `json:"endpoint,omitempty"`
	Samples  []RuntimeMetricsSample `json:"samples,omitempty"`
	Errors   []string               `json:"errors,omitempty"`
}

func newRuntimeMetricsEvidence(endpoint string) RuntimeMetricsEvidence {
	endpoint = strings.TrimSpace(endpoint)
	if endpoint == "" {
		return RuntimeMetricsEvidence{Status: "not-requested"}
	}
	return RuntimeMetricsEvidence{
		Status:   "pending",
		Endpoint: endpoint,
	}
}

func (e *RuntimeMetricsEvidence) Observe(
	ctx context.Context,
	stage string,
	mode Mode,
	client *http.Client,
) {
	if e == nil || e.Status == "not-requested" || strings.TrimSpace(e.Endpoint) == "" {
		return
	}
	if client == nil {
		client = http.DefaultClient
	}

	request, err := http.NewRequestWithContext(ctx, http.MethodGet, e.Endpoint, nil)
	if err != nil {
		e.recordRuntimeMetricsError(stage, err)
		return
	}
	response, err := client.Do(request)
	if err != nil {
		e.recordRuntimeMetricsError(stage, err)
		return
	}
	defer response.Body.Close()

	if response.StatusCode < 200 || response.StatusCode >= 300 {
		_, _ = io.Copy(io.Discard, response.Body)
		e.recordRuntimeMetricsError(stage, fmt.Errorf("metrics endpoint returned HTTP %d", response.StatusCode))
		return
	}

	values, err := parseRuntimePrometheusMetrics(response.Body)
	if err != nil {
		e.recordRuntimeMetricsError(stage, err)
		return
	}

	sample := RuntimeMetricsSample{
		ObservedAt:           time.Now().UTC().Format(time.RFC3339),
		Stage:                stage,
		Mode:                 mode,
		PromptTokensTotal:    metricPointer(values, "llamacpp:prompt_tokens_total"),
		TokensPredictedTotal: metricPointer(values, "llamacpp:tokens_predicted_total"),
		KVCacheUsageRatio:    metricPointer(values, "llamacpp:kv_cache_usage_ratio"),
		KVCacheTokens:        metricPointer(values, "llamacpp:kv_cache_tokens"),
		ContextTokensMax:     metricPointer(values, "llamacpp:n_tokens_max"),
	}
	if sample.PromptTokensTotal == nil &&
		sample.TokensPredictedTotal == nil &&
		sample.KVCacheUsageRatio == nil &&
		sample.KVCacheTokens == nil &&
		sample.ContextTokensMax == nil {
		e.recordRuntimeMetricsError(stage, fmt.Errorf("no supported llama.cpp metrics found"))
		return
	}

	e.Samples = append(e.Samples, sample)
	if len(e.Errors) == 0 {
		e.Status = "observed"
	} else {
		e.Status = "partial"
	}
}

func (e *RuntimeMetricsEvidence) recordRuntimeMetricsError(stage string, err error) {
	e.Errors = append(e.Errors, fmt.Sprintf("%s: %v", stage, err))
	if len(e.Samples) == 0 {
		e.Status = "unavailable"
	} else {
		e.Status = "partial"
	}
}

func parseRuntimePrometheusMetrics(reader io.Reader) (map[string]float64, error) {
	values := make(map[string]float64)
	scanner := bufio.NewScanner(reader)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		fields := strings.Fields(line)
		if len(fields) < 2 {
			continue
		}
		name := fields[0]
		if i := strings.IndexByte(name, '{'); i >= 0 {
			name = name[:i]
		}
		if !supportedRuntimeMetric(name) {
			continue
		}
		value, err := strconv.ParseFloat(fields[1], 64)
		if err != nil {
			return nil, fmt.Errorf("parse metric %s value %q: %w", name, fields[1], err)
		}
		values[name] = value
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return values, nil
}

func supportedRuntimeMetric(name string) bool {
	switch name {
	case "llamacpp:prompt_tokens_total",
		"llamacpp:tokens_predicted_total",
		"llamacpp:kv_cache_usage_ratio",
		"llamacpp:kv_cache_tokens",
		"llamacpp:n_tokens_max":
		return true
	default:
		return false
	}
}

func metricPointer(values map[string]float64, name string) *float64 {
	value, ok := values[name]
	if !ok {
		return nil
	}
	return &value
}
