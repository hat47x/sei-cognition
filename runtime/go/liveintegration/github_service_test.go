package liveintegration

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/hat47x/soza/runtime/go/provideradapter"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const testCommitSHA = "aa3651f3460a6db7dc70bd848f93b600f149ffe8"

func testObservationContext() provideradapter.ObservationContext {
	return provideradapter.ObservationContext{
		ObservationID: "e3b-live-provider-001",
		CapabilityRef: semanticruntime.LogicalReference{Kind: "capability", ID: "external-source-revision-access"},
		ObservedAt:    "2026-09-02T00:00:00Z",
		SourceStateRef: "live-service-response:github-rest-api/hat47x/cultural-substrate-weaving@" + testCommitSHA,
	}
}

func TestGitHubCommitServiceMapsValidatedObservation(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			t.Fatalf("method = %s, want GET", r.Method)
		}
		if !strings.HasSuffix(r.URL.Path, "/repos/hat47x/cultural-substrate-weaving/commits/"+testCommitSHA) {
			t.Fatalf("unexpected path: %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"sha":"` + testCommitSHA + `","node_id":"provider-local-value","html_url":"https://example.invalid/provider-only"}`))
	}))
	defer server.Close()

	document, err := (GitHubCommitService{BaseURL: server.URL}).ObserveCommit(
		context.Background(),
		"hat47x/cultural-substrate-weaving",
		testCommitSHA,
		testObservationContext(),
	)
	if err != nil {
		t.Fatalf("ObserveCommit() error = %v", err)
	}
	if document.Observation.Target.ProviderRef == nil || document.Observation.Target.ProviderRef.ID != githubProviderID {
		t.Fatalf("provider ref = %#v", document.Observation.Target.ProviderRef)
	}
	if len(document.Observation.Conditions) != 2 {
		t.Fatalf("conditions = %d, want 2", len(document.Observation.Conditions))
	}
	if document.Observation.MappingProvenance == nil || document.Observation.MappingProvenance.MappingRef.ID != githubMappingID {
		t.Fatalf("mapping provenance = %#v", document.Observation.MappingProvenance)
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		t.Fatalf("ValidateObservation() error = %v", err)
	}

	encoded, err := json.Marshal(document)
	if err != nil {
		t.Fatal(err)
	}
	text := string(encoded)
	for _, providerField := range []string{"node_id", "html_url", "provider-local-value", "example.invalid"} {
		if strings.Contains(text, providerField) {
			t.Fatalf("provider-local field leaked into Capability Observation: %s", providerField)
		}
	}
}

func TestGitHubCommitServiceRejectsRevisionMismatchWithoutObservation(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"sha":"0000000000000000000000000000000000000000"}`))
	}))
	defer server.Close()

	document, err := (GitHubCommitService{BaseURL: server.URL}).ObserveCommit(context.Background(), "hat47x/cultural-substrate-weaving", testCommitSHA, testObservationContext())
	if err == nil {
		t.Fatal("ObserveCommit() error = nil, want revision mismatch")
	}
	if document.Contract != "" || document.Observation.Ref.ID != "" {
		t.Fatalf("unexpected observation on failure: %#v", document)
	}
}

func TestGitHubCommitServiceRejectsHTTPFailureWithoutObservation(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "provider unavailable", http.StatusServiceUnavailable)
	}))
	defer server.Close()

	document, err := (GitHubCommitService{BaseURL: server.URL}).ObserveCommit(context.Background(), "hat47x/cultural-substrate-weaving", testCommitSHA, testObservationContext())
	if err == nil {
		t.Fatal("ObserveCommit() error = nil, want HTTP failure")
	}
	if document.Contract != "" || document.Observation.Ref.ID != "" {
		t.Fatalf("unexpected observation on failure: %#v", document)
	}
}

func TestGitHubCommitServiceRejectsTimeoutWithoutObservation(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		select {
		case <-time.After(200 * time.Millisecond):
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write([]byte(`{"sha":"` + testCommitSHA + `"}`))
		case <-r.Context().Done():
			return
		}
	}))
	defer server.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
	defer cancel()
	document, err := (GitHubCommitService{BaseURL: server.URL}).ObserveCommit(ctx, "hat47x/cultural-substrate-weaving", testCommitSHA, testObservationContext())
	if err == nil {
		t.Fatal("ObserveCommit() error = nil, want timeout")
	}
	if document.Contract != "" || document.Observation.Ref.ID != "" {
		t.Fatalf("unexpected observation on timeout: %#v", document)
	}
}

func TestGitHubCommitServiceRejectsInvalidRepository(t *testing.T) {
	document, err := (GitHubCommitService{}).ObserveCommit(context.Background(), "not-an-owner-name", testCommitSHA, testObservationContext())
	if err == nil {
		t.Fatal("ObserveCommit() error = nil, want invalid repository error")
	}
	if document.Contract != "" {
		t.Fatalf("unexpected observation on invalid repository: %#v", document)
	}
}

func TestLiveGitHubCommitService(t *testing.T) {
	if os.Getenv("SOZA_E3B_LIVE") != "1" {
		t.Skip("set SOZA_E3B_LIVE=1 to call the public live Provider service")
	}

	service := GitHubCommitService{Token: os.Getenv("SOZA_LIVE_PROVIDER_TOKEN")}
	document, err := service.ObserveCommit(
		context.Background(),
		"hat47x/cultural-substrate-weaving",
		testCommitSHA,
		testObservationContext(),
	)
	if err != nil {
		t.Fatalf("live ObserveCommit() error = %v", err)
	}
	if document.Observation.Target.ProviderRef == nil || document.Observation.Target.ProviderRef.ID != githubProviderID {
		t.Fatalf("live provider ref = %#v", document.Observation.Target.ProviderRef)
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		t.Fatalf("live mapped observation did not validate: %v", err)
	}
}
