package liveintegration

import (
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/hat47x/soza/runtime/go/provideradapter"
)

const failureLiveEnvironment = "SOZA_E3B_FAILURE_LIVE"

func requireFailureLive(t *testing.T) {
	t.Helper()
	if os.Getenv(failureLiveEnvironment) != "1" {
		t.Skip("set SOZA_E3B_FAILURE_LIVE=1 to call live Provider failure probes")
	}
}

func failureObservationContext(id, revision string) provideradapter.ObservationContext {
	context := testObservationContext()
	context.ObservationID = id
	context.SourceStateRef = "live-service-response:github-rest-api/hat47x/cultural-substrate-weaving@" + revision
	return context
}

func assertNoCapabilityObservation(t *testing.T, document interface{ GetContract() string }) {
	t.Helper()
	if document.GetContract() != "" {
		t.Fatalf("failure probe emitted a Capability Observation contract: %q", document.GetContract())
	}
}

// TestGitHubCommitServiceHTTPFailureDoesNotLeakToken is deterministic. It
// verifies the secret-safe failure boundary without making a live request.
func TestGitHubCommitServiceHTTPFailureDoesNotLeakToken(t *testing.T) {
	const token = "evaluation-only-sensitive-token"
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if got := r.Header.Get("Authorization"); got != "Bearer "+token {
			t.Fatalf("Authorization header = %q, want bearer test token", got)
		}
		http.Error(w, "bad credentials", http.StatusUnauthorized)
	}))
	defer server.Close()

	document, err := (GitHubCommitService{BaseURL: server.URL, Token: token}).ObserveCommit(
		context.Background(),
		"hat47x/cultural-substrate-weaving",
		testCommitSHA,
		failureObservationContext("e3b-live-provider-failure-secret-safe", testCommitSHA),
	)
	if err == nil {
		t.Fatal("ObserveCommit() error = nil, want Provider rejection")
	}
	if document.Contract != "" || document.Observation.Ref.ID != "" {
		t.Fatalf("Provider rejection emitted a Capability Observation: %#v", document)
	}
	if strings.Contains(err.Error(), token) {
		t.Fatalf("Provider rejection leaked token into error: %v", err)
	}
}

// TestLiveGitHubCommitServiceMissingRevisionFailure is an explicit opt-in
// actual Provider probe. The concrete HTTP status is intentionally not treated
// as Universal semantics; the boundary under test is rejection without a
// Capability Observation.
func TestLiveGitHubCommitServiceMissingRevisionFailure(t *testing.T) {
	requireFailureLive(t)

	missingRevision := strings.Repeat("0", 40)
	service := GitHubCommitService{Token: os.Getenv("SOZA_LIVE_PROVIDER_TOKEN")}
	document, err := service.ObserveCommit(
		context.Background(),
		"hat47x/cultural-substrate-weaving",
		missingRevision,
		failureObservationContext("e3b-live-provider-failure-missing-revision", missingRevision),
	)
	if err == nil {
		t.Fatal("live ObserveCommit() error = nil, want missing revision rejection")
	}
	if document.Contract != "" || document.Observation.Ref.ID != "" {
		t.Fatalf("missing revision emitted a Capability Observation: %#v", document)
	}
	if !strings.Contains(err.Error(), "live Provider returned HTTP") {
		t.Fatalf("missing revision error did not remain at Provider failure boundary: %v", err)
	}
}

// TestLiveGitHubCommitServiceInvalidCredentialFailure sends only a fixed,
// intentionally invalid token. No real credential is required or persisted.
func TestLiveGitHubCommitServiceInvalidCredentialFailure(t *testing.T) {
	requireFailureLive(t)

	const invalidToken = "soza-intentionally-invalid-credential"
	service := GitHubCommitService{Token: invalidToken}
	document, err := service.ObserveCommit(
		context.Background(),
		"hat47x/cultural-substrate-weaving",
		testCommitSHA,
		failureObservationContext("e3b-live-provider-failure-invalid-credential", testCommitSHA),
	)
	if err == nil {
		t.Fatal("live ObserveCommit() error = nil, want credential rejection")
	}
	if document.Contract != "" || document.Observation.Ref.ID != "" {
		t.Fatalf("credential rejection emitted a Capability Observation: %#v", document)
	}
	if !strings.Contains(err.Error(), "live Provider returned HTTP") {
		t.Fatalf("credential rejection did not remain at Provider failure boundary: %v", err)
	}
	if strings.Contains(err.Error(), invalidToken) {
		t.Fatalf("credential rejection leaked invalid token into error: %v", err)
	}
}
