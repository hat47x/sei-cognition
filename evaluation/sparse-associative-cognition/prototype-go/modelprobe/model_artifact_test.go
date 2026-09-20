package modelprobe

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestObserveModelArtifactHashesExactFile(t *testing.T) {
	path := filepath.Join(t.TempDir(), "model.gguf")
	content := []byte("exact-model-bytes\n")
	if err := os.WriteFile(path, content, 0o600); err != nil {
		t.Fatal(err)
	}
	sum := sha256.Sum256(content)
	expected := hex.EncodeToString(sum[:])

	identity, err := ObserveModelArtifact(path, expected)
	if err != nil {
		t.Fatal(err)
	}
	if identity.Status != modelArtifactObserved || identity.FileName != "model.gguf" || identity.SizeBytes != int64(len(content)) || identity.SHA256 != expected {
		t.Fatalf("unexpected identity: %+v", identity)
	}
}

func TestObserveModelArtifactRejectsDigestMismatch(t *testing.T) {
	path := filepath.Join(t.TempDir(), "model.gguf")
	if err := os.WriteFile(path, []byte("model"), 0o600); err != nil {
		t.Fatal(err)
	}
	_, err := ObserveModelArtifact(path, strings.Repeat("0", 64))
	if err == nil || !strings.Contains(err.Error(), "model sha256 mismatch") {
		t.Fatalf("expected digest mismatch, got %v", err)
	}
}

func TestObserveModelArtifactWithoutFileIsExplicit(t *testing.T) {
	identity, err := ObserveModelArtifact("", "")
	if err != nil {
		t.Fatal(err)
	}
	if identity.Status != modelArtifactNotSupplied {
		t.Fatalf("status=%q", identity.Status)
	}
}

func TestValidateModelArtifactIdentityAcceptsLegacyZeroValue(t *testing.T) {
	if err := ValidateModelArtifactIdentity(ModelArtifactIdentity{}); err != nil {
		t.Fatal(err)
	}
	if got := NormalizeModelArtifactIdentity(ModelArtifactIdentity{}).Status; got != modelArtifactNotSupplied {
		t.Fatalf("normalized status=%q", got)
	}
}

func TestSameModelArtifactIdentityUsesExactBytesNotFilename(t *testing.T) {
	left := ModelArtifactIdentity{Status: modelArtifactObserved, FileName: "a.gguf", SizeBytes: 5, SHA256: strings.Repeat("a", 64)}
	right := ModelArtifactIdentity{Status: modelArtifactObserved, FileName: "b.gguf", SizeBytes: 5, SHA256: strings.Repeat("a", 64)}
	if !SameModelArtifactIdentity(left, right) {
		t.Fatal("same bytes should have the same model artifact identity")
	}
}
