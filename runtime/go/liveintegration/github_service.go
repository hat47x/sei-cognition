package liveintegration

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/hat47x/soza/runtime/go/provideradapter"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const (
	defaultGitHubAPIBaseURL = "https://api.github.com"
	githubProviderID        = "github-rest-api"
	githubMappingID         = "github-commit-service-to-capability-observation/reference-v1"
	maxGitHubResponseBytes  = 1 << 20
)

// GitHubCommitService is a reference E3b client for one live Provider service.
// GitHub's HTTP protocol and response shape remain local to this realization;
// they are not SOZA Universal Contracts.
type GitHubCommitService struct {
	BaseURL string
	Token   string
	Client  *http.Client
}

type githubCommitResponse struct {
	SHA string `json:"sha"`
}

func splitRepository(repository string) (string, string, error) {
	repository = strings.TrimSpace(repository)
	parts := strings.Split(repository, "/")
	if len(parts) != 2 || strings.TrimSpace(parts[0]) == "" || strings.TrimSpace(parts[1]) == "" {
		return "", "", errors.New("repository must be in owner/name form")
	}
	return parts[0], parts[1], nil
}

func (service GitHubCommitService) client() *http.Client {
	if service.Client != nil {
		return service.Client
	}
	return &http.Client{Timeout: 5 * time.Second}
}

func (service GitHubCommitService) baseURL() string {
	if strings.TrimSpace(service.BaseURL) == "" {
		return defaultGitHubAPIBaseURL
	}
	return strings.TrimRight(service.BaseURL, "/")
}

func rawValue(value any) (json.RawMessage, error) {
	data, err := json.Marshal(value)
	if err != nil {
		return nil, fmt.Errorf("marshal observed value: %w", err)
	}
	return data, nil
}

func buildObservation(context provideradapter.ObservationContext, repository, expectedSHA string) (semanticruntime.CapabilityObservationDocument, error) {
	if context.ObservationID == "" || context.CapabilityRef.Kind == "" || context.CapabilityRef.ID == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("observation ID and capability reference are required")
	}
	if context.ObservedAt == "" || context.SourceStateRef == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("observed time and source state reference are required")
	}

	available, err := rawValue(true)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	revisionAvailable, err := rawValue(true)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}

	providerRef := semanticruntime.LogicalReference{Kind: "provider", ID: githubProviderID}
	capabilityRef := context.CapabilityRef
	document := semanticruntime.CapabilityObservationDocument{
		Contract: semanticruntime.ContractCapabilityObservation,
		Observation: semanticruntime.CapabilityObservation{
			Ref: semanticruntime.LogicalReference{Kind: "capability-observation", ID: context.ObservationID},
			Target: semanticruntime.CapabilityTarget{
				CapabilityRef:     &capabilityRef,
				ProviderRef:       &providerRef,
				ProviderTargetRef: "github-revision:" + repository + "@" + expectedSHA,
			},
			ObservedAt: context.ObservedAt,
			Conditions: []semanticruntime.ObservedCondition{
				{Key: "availability", State: "observed", Value: available},
				{Key: "expected_revision_available", State: "observed", Value: revisionAvailable},
			},
			MappingProvenance: &semanticruntime.MappingProvenance{
				MappingRef:     semanticruntime.Reference{Kind: "adapter-mapping", ID: githubMappingID},
				SourceStateRef: context.SourceStateRef,
				Description:    "live外部serviceの固定revision応答をcurrent Capability Observationへ変換するreference mapping",
			},
		},
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("mapped live Capability Observation did not validate: %w", err)
	}
	return document, nil
}

// ObserveCommit calls a live GitHub commit endpoint and maps only the minimal
// observed meaning into the current Capability Observation. HTTP failure,
// cancellation, malformed responses and revision mismatches return no document.
func (service GitHubCommitService) ObserveCommit(ctx context.Context, repository, expectedSHA string, observationContext provideradapter.ObservationContext) (semanticruntime.CapabilityObservationDocument, error) {
	owner, name, err := splitRepository(repository)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	expectedSHA = strings.TrimSpace(expectedSHA)
	if expectedSHA == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("expected commit SHA is required")
	}

	endpoint := service.baseURL() + "/repos/" + url.PathEscape(owner) + "/" + url.PathEscape(name) + "/commits/" + url.PathEscape(expectedSHA)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("build live Provider request: %w", err)
	}
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")
	req.Header.Set("User-Agent", "soza-e3b-live-provider-probe")
	if strings.TrimSpace(service.Token) != "" {
		req.Header.Set("Authorization", "Bearer "+service.Token)
	}

	response, err := service.client().Do(req)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("call live Provider service: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < http.StatusOK || response.StatusCode >= http.StatusMultipleChoices {
		_, _ = io.Copy(io.Discard, io.LimitReader(response.Body, 4096))
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("live Provider returned HTTP %d", response.StatusCode)
	}

	decoder := json.NewDecoder(io.LimitReader(response.Body, maxGitHubResponseBytes))
	var payload githubCommitResponse
	if err := decoder.Decode(&payload); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("decode live Provider response: %w", err)
	}
	if payload.SHA == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("live Provider response did not include commit SHA")
	}
	if payload.SHA != expectedSHA {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("live Provider revision mismatch: expected %s, got %s", expectedSHA, payload.SHA)
	}

	return buildObservation(observationContext, repository, expectedSHA)
}
