package semanticruntime

import (
	"strings"
	"testing"
)

func TestRegisteredProfileContentDigestForm(t *testing.T) {
	valid := "sha256:" + strings.Repeat("a1", 32)
	cases := []struct {
		name      string
		profileID string
		version   string
		digest    string
		wantErr   bool
	}{
		{"jcs valid", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, valid, false},
		{"raw-bytes valid", ProfileIDRawBytesSHA256, ProfileVersionV1Alpha1, valid, false},
		{"jcs too short", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, "sha256:zz", true},
		{"jcs no prefix", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, strings.Repeat("a1", 32), true},
		{"jcs uppercase hex", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, "sha256:" + strings.Repeat("A1", 32), true},
		{"jcs 63 chars", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, valid[:len(valid)-1], true},
		{"jcs 65 chars", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, valid + "a", true},
		{"jcs non hex char", ProfileIDJCSSHA256, ProfileVersionV1Alpha1, "sha256:" + strings.Repeat("g1", 32), true},
		{"raw-bytes malformed", ProfileIDRawBytesSHA256, ProfileVersionV1Alpha1, "not-a-digest", true},
		{"unregistered profile is not inspected", "synthetic-review-markdown", "v0", "not-a-digest", false},
		{"unregistered version is not inspected", ProfileIDJCSSHA256, "v9", "not-a-digest", false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			binding := ExactBinding{
				LogicalRef:            LogicalReference{Kind: "artifact", ID: "D-04"},
				ContentDigest:         tc.digest,
				RepresentationProfile: RepresentationProfile{ProfileID: tc.profileID, Version: tc.version},
			}
			err := validateExact(binding)
			if tc.wantErr && err == nil {
				t.Fatal("expected a content_digest form error")
			}
			if !tc.wantErr && err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
		})
	}
}
