package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"path/filepath"
	"testing"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
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

// Realization recordのExact Bindingはbundle内の参照整合だけでなく、
// Raw Bytes SHA-256 Profileに従って実際のpayload bytesとも一致する必要があります。
func TestRuntimeExchangeRealizationPayloadExactBindingVerification(t *testing.T) {
	revision := runtimeExchangeRealizationRevisionRecord(
		t,
		"record-runtime-exchange-realization-verifier",
		logical("method-realization", "MR-KJ-ATLAS-RUNTIME-EXCHANGE"),
		runtimeExchangeVersionA,
		runtimeExchangeArtifactA,
		"qwen2.5:0.5b",
		"a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67",
	)
	if revision.Record.ExactBinding == nil {
		t.Fatal("runtime realization record lost exact binding")
	}

	registry, err := semanticruntime.NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatalf("create verifier registry: %v", err)
	}
	outcome := registry.Verify(*revision.Record.ExactBinding, revision.Record.Payload)
	if outcome.Status != semanticruntime.VerificationVerified {
		t.Fatalf("runtime realization payload was not verified: %#v", outcome)
	}

	tampered := append([]byte(nil), revision.Record.Payload...)
	if len(tampered) == 0 {
		t.Fatal("runtime realization payload is empty")
	}
	tampered[len(tampered)-1] ^= 0x01
	outcome = registry.Verify(*revision.Record.ExactBinding, tampered)
	if outcome.Status != semanticruntime.VerificationFailed {
		t.Fatalf("tampered runtime realization payload was not rejected: %#v", outcome)
	}
}

func TestRuntimeExchangeRealizationBindingIsDeterministicForSameIdentity(t *testing.T) {
	logicalRef := logical("method-realization", "MR-KJ-ATLAS-RUNTIME-EXCHANGE")
	modelID := "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"

	first := runtimeExchangeRealizationRevisionRecord(
		t,
		"record-runtime-exchange-realization-deterministic-a",
		logicalRef,
		runtimeExchangeVersionA,
		runtimeExchangeArtifactA,
		"qwen2.5:0.5b",
		modelID,
	)
	second := runtimeExchangeRealizationRevisionRecord(
		t,
		"record-runtime-exchange-realization-deterministic-b",
		logicalRef,
		runtimeExchangeVersionA,
		runtimeExchangeArtifactA,
		"qwen2.5:0.5b",
		modelID,
	)

	if first.Record.ExactBinding == nil || second.Record.ExactBinding == nil {
		t.Fatal("deterministic realization record lost exact binding")
	}
	if first.Record.ExactBinding.ContentDigest != second.Record.ExactBinding.ContentDigest {
		t.Fatalf(
			"same realization identity produced different exact bindings: first=%s second=%s",
			first.Record.ExactBinding.ContentDigest,
			second.Record.ExactBinding.ContentDigest,
		)
	}
}

func TestRuntimeExchangeRealizationBindingChangesWhenExecutionArtifactIdentityChanges(t *testing.T) {
	logicalRef := logical("method-realization", "MR-KJ-ATLAS-RUNTIME-EXCHANGE")
	modelID := "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"
	base := runtimeExchangeRealizationRevisionRecord(
		t,
		"record-runtime-exchange-realization-base",
		logicalRef,
		runtimeExchangeVersionA,
		runtimeExchangeArtifactA,
		"qwen2.5:0.5b",
		modelID,
	)
	if base.Record.ExactBinding == nil {
		t.Fatal("base realization record lost exact binding")
	}

	tests := []struct {
		name            string
		runtimeVersion  string
		runtimeArtifact string
		modelID         string
	}{
		{
			name:            "runtime version",
			runtimeVersion:  runtimeExchangeVersionB,
			runtimeArtifact: runtimeExchangeArtifactA,
			modelID:         modelID,
		},
		{
			name:            "runtime artifact",
			runtimeVersion:  runtimeExchangeVersionA,
			runtimeArtifact: runtimeExchangeArtifactB,
			modelID:         modelID,
		},
		{
			name:            "model artifact",
			runtimeVersion:  runtimeExchangeVersionA,
			runtimeArtifact: runtimeExchangeArtifactA,
			modelID:         "b" + modelID[1:],
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			changed := runtimeExchangeRealizationRevisionRecord(
				t,
				"record-runtime-exchange-realization-changed",
				logicalRef,
				tt.runtimeVersion,
				tt.runtimeArtifact,
				"qwen2.5:0.5b",
				tt.modelID,
			)
			if changed.Record.ExactBinding == nil {
				t.Fatal("changed realization record lost exact binding")
			}
			if changed.Record.ExactBinding.ContentDigest == base.Record.ExactBinding.ContentDigest {
				t.Fatalf("%s change did not change realization exact binding", tt.name)
			}
		})
	}
}
