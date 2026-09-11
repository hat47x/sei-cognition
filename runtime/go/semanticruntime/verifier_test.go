package semanticruntime

import (
	"encoding/base64"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type jcsProfileFixture struct {
	ProfileID string `json:"profile_id"`
	Cases     []struct {
		ID             string `json:"id"`
		Expect         string `json:"expect"`
		Input          string `json:"input"`
		ExpectedDigest string `json:"expected_digest"`
	} `json:"cases"`
}

type rawProfileFixture struct {
	ProfileID string `json:"profile_id"`
	Cases     []struct {
		ID             string `json:"id"`
		BytesBase64    string `json:"bytes_base64"`
		ExpectedDigest string `json:"expected_digest"`
	} `json:"cases"`
}

func representationFixture(t *testing.T, name string) []byte {
	t.Helper()
	path := filepath.Join(repositoryRoot(t), "fixtures", "representation-profiles", name)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read representation fixture %s: %v", path, err)
	}
	return data
}

func testBinding(profile RepresentationProfile, digest string) ExactBinding {
	return ExactBinding{
		LogicalRef: LogicalReference{Kind: "fixture", ID: "representation-profile-test"},
		ContentDigest: digest,
		RepresentationProfile: profile,
	}
}

func TestJCSVerifierReusesProfileFixture(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	var fixture jcsProfileFixture
	if err := json.Unmarshal(representationFixture(t, "jcs-v1alpha1.json"), &fixture); err != nil {
		t.Fatal(err)
	}
	if fixture.ProfileID != "sei.jcs+sha256/v1alpha1" {
		t.Fatalf("unexpected fixture profile %q", fixture.ProfileID)
	}
	profile := RepresentationProfile{ProfileID: ProfileIDJCSSHA256, Version: ProfileVersionV1Alpha1}

	for _, tc := range fixture.Cases {
		t.Run(tc.ID, func(t *testing.T) {
			digest := tc.ExpectedDigest
			if digest == "" {
				digest = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
			}
			binding := testBinding(profile, digest)
			outcome := registry.Verify(binding, []byte(tc.Input))
			switch tc.Expect {
			case "verified":
				if outcome.Status != VerificationVerified {
					t.Fatalf("status = %q, want verified; reason=%s", outcome.Status, outcome.Reason)
				}
			case "invalid_representation", "invalid_semantic_number":
				if outcome.Status != VerificationFailed {
					t.Fatalf("status = %q, want failed", outcome.Status)
				}
			default:
				t.Fatalf("unexpected fixture expectation %q", tc.Expect)
			}
			if outcome.Binding != binding {
				t.Fatal("verification mutated exact binding")
			}
		})
	}
}

func TestRawBytesVerifierReusesProfileFixture(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	var fixture rawProfileFixture
	if err := json.Unmarshal(representationFixture(t, "raw-bytes-v1alpha1.json"), &fixture); err != nil {
		t.Fatal(err)
	}
	if fixture.ProfileID != "sei.raw-bytes+sha256/v1alpha1" {
		t.Fatalf("unexpected fixture profile %q", fixture.ProfileID)
	}
	profile := RepresentationProfile{ProfileID: ProfileIDRawBytesSHA256, Version: ProfileVersionV1Alpha1}

	for _, tc := range fixture.Cases {
		t.Run(tc.ID, func(t *testing.T) {
			payload, err := base64.StdEncoding.DecodeString(tc.BytesBase64)
			if err != nil {
				t.Fatal(err)
			}
			outcome := registry.Verify(testBinding(profile, tc.ExpectedDigest), payload)
			if outcome.Status != VerificationVerified {
				t.Fatalf("status = %q, want verified; reason=%s", outcome.Status, outcome.Reason)
			}
		})
	}
}

func TestVerifierOutcomeBoundaries(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	profile := RepresentationProfile{ProfileID: ProfileIDRawBytesSHA256, Version: ProfileVersionV1Alpha1}
	binding := testBinding(profile, sha256Digest([]byte("expected")))

	mismatch := registry.Verify(binding, []byte("actual"))
	if mismatch.Status != VerificationFailed || !strings.Contains(mismatch.Reason, "digest mismatch") {
		t.Fatalf("mismatch outcome = %#v", mismatch)
	}

	missing := registry.Verify(binding, nil)
	if missing.Status != VerificationNotVerified {
		t.Fatalf("missing payload status = %q", missing.Status)
	}

	unknownBinding := testBinding(
		RepresentationProfile{ProfileID: "example.unknown", Version: "v1"},
		binding.ContentDigest,
	)
	unknown := registry.Verify(unknownBinding, []byte("expected"))
	if unknown.Status != VerificationNotVerified {
		t.Fatalf("unknown profile status = %q", unknown.Status)
	}
	if unknown.VerifierRef != "" {
		t.Fatalf("unknown profile unexpectedly has verifier ref %q", unknown.VerifierRef)
	}

	verified := registry.Verify(binding, []byte("expected"))
	if verified.Status != VerificationVerified {
		t.Fatalf("verified status = %q, reason=%s", verified.Status, verified.Reason)
	}
	if verified.VerifierRef != VerifierRefRawBytesSHA256V1Alpha1 {
		t.Fatalf("verifier ref = %q", verified.VerifierRef)
	}
}

func TestVerifierRegistryRejectsDuplicateProfile(t *testing.T) {
	_, err := NewVerifierRegistry(rawBytesSHA256Verifier{}, rawBytesSHA256Verifier{})
	if err == nil || !strings.Contains(err.Error(), "duplicate verifier") {
		t.Fatalf("duplicate registration error = %v", err)
	}
}
