package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
	"testing"
)

func TestVerifyRuntimeExchangeVersionAcceptsExactVersionToken(t *testing.T) {
	path := filepath.Join(t.TempDir(), "version.txt")
	if err := os.WriteFile(path, []byte("ollama version is 0.32.13\n"), 0o600); err != nil {
		t.Fatalf("write version log: %v", err)
	}

	if err := verifyRuntimeExchangeVersion("A", path, "0.32.13"); err != nil {
		t.Fatalf("exact runtime version was rejected: %v", err)
	}
}

func TestVerifyRuntimeExchangeVersionRejectsLongerNumericSuffix(t *testing.T) {
	path := filepath.Join(t.TempDir(), "version.txt")
	if err := os.WriteFile(path, []byte("ollama version is 0.32.130\n"), 0o600); err != nil {
		t.Fatalf("write version log: %v", err)
	}

	if err := verifyRuntimeExchangeVersion("A", path, "0.32.13"); err == nil {
		t.Fatal("runtime version guard accepted a longer numeric suffix")
	}
}

func TestVerifyRuntimeExchangeArtifactAcceptsExactDigest(t *testing.T) {
	payload := []byte("runtime exchange artifact fixture")
	path := filepath.Join(t.TempDir(), "runtime.tar.zst")
	if err := os.WriteFile(path, payload, 0o600); err != nil {
		t.Fatalf("write runtime artifact: %v", err)
	}

	digest := sha256.Sum256(payload)
	expected := hex.EncodeToString(digest[:])
	if err := verifyRuntimeExchangeArtifact("A", path, expected); err != nil {
		t.Fatalf("exact runtime artifact digest was rejected: %v", err)
	}
}

func TestVerifyRuntimeExchangeArtifactRejectsDigestMismatch(t *testing.T) {
	path := filepath.Join(t.TempDir(), "runtime.tar.zst")
	if err := os.WriteFile(path, []byte("runtime exchange artifact fixture"), 0o600); err != nil {
		t.Fatalf("write runtime artifact: %v", err)
	}

	if err := verifyRuntimeExchangeArtifact(
		"A",
		path,
		"0000000000000000000000000000000000000000000000000000000000000000",
	); err == nil {
		t.Fatal("runtime artifact guard accepted a digest mismatch")
	}
}
