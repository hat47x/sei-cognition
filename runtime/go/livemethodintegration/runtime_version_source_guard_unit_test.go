package livemethodintegration

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

func TestVerifyRuntimeExchangeKJAtlasSourceRejectsMissingMode(t *testing.T) {
	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, "")
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("runtime exchange source guard accepted a missing source mode")
	}
}

func TestVerifyRuntimeExchangeKJAtlasSourceRejectsUnsupportedMode(t *testing.T) {
	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, "unknown")
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("runtime exchange source guard accepted an unsupported source mode")
	}
}

func TestVerifyRuntimeExchangeKJAtlasSourceRejectsGitCheckoutMode(t *testing.T) {
	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, runtimeExchangeKJAtlasSourceModeGitCheckout)
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("runtime exchange source guard accepted a Git working tree as live Evidence source")
	}
}

func TestVerifyRuntimeExchangeKJAtlasBundleRequiresExplicitPaths(t *testing.T) {
	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, runtimeExchangeKJAtlasSourceModeBundle)
	t.Setenv(runtimeExchangeKJAtlasBackendDirEnv, "")
	t.Setenv(runtimeExchangeKJAtlasSourceVerifierEnv, "")
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("verified-runtime-bundle source mode accepted missing paths")
	}
}

func writeSourceVerifierFixture(t *testing.T, payload string) string {
	t.Helper()
	verifier := filepath.Join(t.TempDir(), "verifier.py")
	if err := os.WriteFile(
		verifier,
		[]byte("print("+fmt.Sprintf("%q", payload)+")\n"),
		0o600,
	); err != nil {
		t.Fatalf("write verifier fixture: %v", err)
	}
	return verifier
}

func pinnedSourceVerifierPayload() string {
	return fmt.Sprintf(
		`{"verified":true,"sourceMode":%q,"sourceCommit":%q,"pinnedBackendTree":%q,"runtimeSurfaceTree":%q,"verificationBasis":"pinned-git-object-identities"}`,
		runtimeExchangeKJAtlasSourceModeBundle,
		pinnedKJAtlasCommit,
		pinnedKJAtlasBackendTree,
		pinnedKJAtlasRuntimeSurfaceTree,
	)
}

func TestVerifyRuntimeExchangeKJAtlasBundleAcceptsPinnedVerifierIdentity(t *testing.T) {
	backendDir := t.TempDir()
	verifier := writeSourceVerifierFixture(t, pinnedSourceVerifierPayload())

	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, runtimeExchangeKJAtlasSourceModeBundle)
	t.Setenv(runtimeExchangeKJAtlasBackendDirEnv, backendDir)
	t.Setenv(runtimeExchangeKJAtlasSourceVerifierEnv, verifier)
	if err := verifyRuntimeExchangeKJAtlasSource(); err != nil {
		t.Fatalf("pinned bundle verifier identity was rejected: %v", err)
	}
}

func TestVerifyRuntimeExchangeKJAtlasBundleRejectsParentBackendTreeDrift(t *testing.T) {
	backendDir := t.TempDir()
	payload := fmt.Sprintf(
		`{"verified":true,"sourceMode":%q,"sourceCommit":%q,"pinnedBackendTree":%q,"runtimeSurfaceTree":%q,"verificationBasis":"pinned-git-object-identities"}`,
		runtimeExchangeKJAtlasSourceModeBundle,
		pinnedKJAtlasCommit,
		"0"+pinnedKJAtlasBackendTree[1:],
		pinnedKJAtlasRuntimeSurfaceTree,
	)
	verifier := writeSourceVerifierFixture(t, payload)

	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, runtimeExchangeKJAtlasSourceModeBundle)
	t.Setenv(runtimeExchangeKJAtlasBackendDirEnv, backendDir)
	t.Setenv(runtimeExchangeKJAtlasSourceVerifierEnv, verifier)
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("bundle source guard accepted parent backend tree drift")
	}
}

func TestVerifyRuntimeExchangeKJAtlasBundleRejectsRuntimeSurfaceTreeDrift(t *testing.T) {
	backendDir := t.TempDir()
	payload := fmt.Sprintf(
		`{"verified":true,"sourceMode":%q,"sourceCommit":%q,"pinnedBackendTree":%q,"runtimeSurfaceTree":%q,"verificationBasis":"pinned-git-object-identities"}`,
		runtimeExchangeKJAtlasSourceModeBundle,
		pinnedKJAtlasCommit,
		pinnedKJAtlasBackendTree,
		"0"+pinnedKJAtlasRuntimeSurfaceTree[1:],
	)
	verifier := writeSourceVerifierFixture(t, payload)

	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, runtimeExchangeKJAtlasSourceModeBundle)
	t.Setenv(runtimeExchangeKJAtlasBackendDirEnv, backendDir)
	t.Setenv(runtimeExchangeKJAtlasSourceVerifierEnv, verifier)
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("bundle source guard accepted runtime surface tree drift")
	}
}

func TestVerifyRuntimeExchangeKJAtlasBundleRejectsUnknownVerificationBasis(t *testing.T) {
	backendDir := t.TempDir()
	payload := fmt.Sprintf(
		`{"verified":true,"sourceMode":%q,"sourceCommit":%q,"pinnedBackendTree":%q,"runtimeSurfaceTree":%q,"verificationBasis":"path-name-only"}`,
		runtimeExchangeKJAtlasSourceModeBundle,
		pinnedKJAtlasCommit,
		pinnedKJAtlasBackendTree,
		pinnedKJAtlasRuntimeSurfaceTree,
	)
	verifier := writeSourceVerifierFixture(t, payload)

	t.Setenv(runtimeExchangeKJAtlasSourceModeEnv, runtimeExchangeKJAtlasSourceModeBundle)
	t.Setenv(runtimeExchangeKJAtlasBackendDirEnv, backendDir)
	t.Setenv(runtimeExchangeKJAtlasSourceVerifierEnv, verifier)
	if err := verifyRuntimeExchangeKJAtlasSource(); err == nil {
		t.Fatal("bundle source guard accepted an unknown verification basis")
	}
}
