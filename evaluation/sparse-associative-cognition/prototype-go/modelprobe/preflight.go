package modelprobe

import (
	"context"
	"encoding/json"
	"net/http"
	"runtime"
	"time"
)

const runManifestSchema = "sei-cognition.local-model-run-manifest/v1"

type HostInfo struct {
	OS        string `json:"os"`
	Arch      string `json:"arch"`
	LogicalCPU int   `json:"logical_cpu"`
	GoVersion string `json:"go_version"`
}

type EndpointInfo struct {
	URL       string `json:"url"`
	Reachable bool   `json:"reachable"`
	HTTPStatus int   `json:"http_status,omitempty"`
	LatencyMS int64  `json:"latency_ms,omitempty"`
	Error     string `json:"error,omitempty"`
}

type RunManifest struct {
	Schema        string       `json:"schema"`
	Status        string       `json:"status"`
	ObservedAt    string       `json:"observed_at"`
	ExecutionKind string       `json:"execution_kind"`
	RunID         string       `json:"run_id,omitempty"`
	SourceGitSHA  string       `json:"source_git_sha,omitempty"`
	Host          HostInfo     `json:"host"`
	Endpoint      EndpointInfo `json:"endpoint"`
	RuntimeName   string       `json:"runtime_name,omitempty"`
	RuntimeVersion string      `json:"runtime_version,omitempty"`
	RuntimeProcess RuntimeProcessIdentity `json:"runtime_process"`
	Model         string       `json:"model,omitempty"`
	ModelArtifact ModelArtifactIdentity `json:"model_artifact"`
	Quantization  string       `json:"quantization,omitempty"`
	ContextSize   int          `json:"context_size,omitempty"`
	Threads       int          `json:"threads,omitempty"`
	Fixture       string       `json:"fixture,omitempty"`
	Mode          Mode         `json:"mode,omitempty"`
	Notes         []string     `json:"notes,omitempty"`
}

func Preflight(ctx context.Context, endpoint string, client *http.Client) RunManifest {
	m := RunManifest{
		Schema: runManifestSchema,
		Status: "evaluation-only",
		ObservedAt: time.Now().UTC().Format(time.RFC3339),
		ExecutionKind: "preflight",
		RuntimeProcess: ObserveRuntimeProcessIdentity(0),
		ModelArtifact: ModelArtifactIdentity{Status: modelArtifactNotSupplied},
		Host: HostInfo{OS: runtime.GOOS, Arch: runtime.GOARCH, LogicalCPU: runtime.NumCPU(), GoVersion: runtime.Version()},
		Endpoint: EndpointInfo{URL: endpoint},
	}
	if endpoint == "" {
		m.Endpoint.Error = "endpoint not configured"
		return m
	}
	if client == nil {
		client = &http.Client{Timeout: 3 * time.Second}
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		m.Endpoint.Error = err.Error()
		return m
	}
	started := time.Now()
	resp, err := client.Do(req)
	m.Endpoint.LatencyMS = time.Since(started).Milliseconds()
	if err != nil {
		m.Endpoint.Error = err.Error()
		return m
	}
	defer resp.Body.Close()
	m.Endpoint.HTTPStatus = resp.StatusCode
	m.Endpoint.Reachable = resp.StatusCode > 0
	return m
}

func (m RunManifest) JSON() ([]byte, error) {
	return json.MarshalIndent(m, "", "  ")
}
