package modelprobe

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

type RuntimePropsEvidence struct {
	Status                string `json:"status"`
	ObservedAt            string `json:"observed_at,omitempty"`
	Endpoint              string `json:"endpoint,omitempty"`
	Role                  string `json:"role,omitempty"`
	ModelAlias            string `json:"model_alias,omitempty"`
	ReportedModelFileName string `json:"reported_model_file_name,omitempty"`
	ContextSize           int    `json:"context_size,omitempty"`
	SameFileAsSupplied    *bool  `json:"same_file_as_supplied,omitempty"`
	Error                 string `json:"error,omitempty"`
}

func ObserveRuntimeProps(
	ctx context.Context,
	endpoint string,
	modelFilePath string,
	client *http.Client,
) RuntimePropsEvidence {
	endpoint = strings.TrimSpace(endpoint)
	modelFilePath = strings.TrimSpace(modelFilePath)
	if endpoint == "" {
		return RuntimePropsEvidence{Status: "not-requested"}
	}
	evidence := RuntimePropsEvidence{
		Status:     "unavailable",
		ObservedAt: time.Now().UTC().Format(time.RFC3339),
		Endpoint:   endpoint,
	}
	if client == nil {
		client = http.DefaultClient
	}

	requestCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	request, err := http.NewRequestWithContext(requestCtx, http.MethodGet, endpoint, nil)
	if err != nil {
		evidence.Error = err.Error()
		return evidence
	}
	response, err := client.Do(request)
	if err != nil {
		evidence.Error = err.Error()
		return evidence
	}
	defer response.Body.Close()

	if response.StatusCode < 200 || response.StatusCode >= 300 {
		_, _ = io.Copy(io.Discard, response.Body)
		evidence.Error = fmt.Sprintf("props endpoint returned HTTP %d", response.StatusCode)
		return evidence
	}

	var payload struct {
		Role       string `json:"role"`
		ModelPath  string `json:"model_path"`
		ModelAlias string `json:"model_alias"`
		DefaultGenerationSettings struct {
			ContextSize int `json:"n_ctx"`
		} `json:"default_generation_settings"`
	}
	decoder := json.NewDecoder(io.LimitReader(response.Body, 1<<20))
	if err := decoder.Decode(&payload); err != nil {
		evidence.Error = fmt.Sprintf("decode props response: %v", err)
		return evidence
	}

	evidence.Role = strings.TrimSpace(payload.Role)
	evidence.ModelAlias = strings.TrimSpace(payload.ModelAlias)
	evidence.ContextSize = payload.DefaultGenerationSettings.ContextSize
	reportedPath := strings.TrimSpace(payload.ModelPath)
	if reportedPath != "" {
		evidence.ReportedModelFileName = filepath.Base(filepath.Clean(reportedPath))
	}

	evidence.Status = "observed"
	if modelFilePath == "" || reportedPath == "" {
		return evidence
	}

	suppliedInfo, err := os.Stat(modelFilePath)
	if err != nil {
		evidence.Status = "partial"
		evidence.Error = fmt.Sprintf("stat supplied model file: %v", err)
		return evidence
	}
	reportedInfo, err := os.Stat(reportedPath)
	if err != nil {
		evidence.Status = "partial"
		evidence.Error = fmt.Sprintf("stat runtime-reported model file: %v", err)
		return evidence
	}
	same := os.SameFile(suppliedInfo, reportedInfo)
	evidence.SameFileAsSupplied = &same
	return evidence
}
