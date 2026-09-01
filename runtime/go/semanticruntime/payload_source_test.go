package semanticruntime

import (
	"context"
	"errors"
	"strings"
	"testing"
)

type syntheticPayloadSource struct {
	result      PayloadLoadResult
	err         error
	lastRequest PayloadRequest
}

func (s *syntheticPayloadSource) LoadPayload(_ context.Context, request PayloadRequest) (PayloadLoadResult, error) {
	s.lastRequest = request
	return s.result, s.err
}

func defaultRawBinding(payload []byte) ExactBinding {
	return testBinding(
		RepresentationProfile{ProfileID: ProfileIDRawBytesSHA256, Version: ProfileVersionV1Alpha1},
		sha256Digest(payload),
	)
}

func TestVerifyFromPayloadSourceVerifiedRawBytes(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	payload := []byte("source bytes\n")
	binding := defaultRawBinding(payload)
	source := &syntheticPayloadSource{result: PayloadLoadResult{
		Available: true,
		Payload:   append([]byte(nil), payload...),
		SourceRef: "synthetic://object/alpha",
	}}

	outcome, loaded, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 1024)
	if err != nil {
		t.Fatal(err)
	}
	if outcome.Status != VerificationVerified {
		t.Fatalf("status = %q, reason=%s", outcome.Status, outcome.Reason)
	}
	if loaded.SourceRef != "synthetic://object/alpha" {
		t.Fatalf("source ref = %q", loaded.SourceRef)
	}
	if outcome.Binding != binding {
		t.Fatal("payload acquisition or verification mutated exact binding")
	}
	if source.lastRequest.Binding != binding || source.lastRequest.MaxBytes != 1024 {
		t.Fatalf("unexpected source request: %#v", source.lastRequest)
	}
}

func TestVerifyFromPayloadSourceDigestMismatchIsFailed(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	binding := defaultRawBinding([]byte("expected"))
	source := &syntheticPayloadSource{result: PayloadLoadResult{Available: true, Payload: []byte("actual")}}

	outcome, _, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 0)
	if err != nil {
		t.Fatalf("digest mismatch unexpectedly returned acquisition error: %v", err)
	}
	if outcome.Status != VerificationFailed || !strings.Contains(outcome.Reason, "digest mismatch") {
		t.Fatalf("mismatch outcome = %#v", outcome)
	}
}

func TestVerifyFromPayloadSourceUnavailableIsNotVerified(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	binding := defaultRawBinding([]byte("expected"))
	source := &syntheticPayloadSource{result: PayloadLoadResult{Available: false, SourceRef: "synthetic://retained/missing"}}

	outcome, loaded, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 0)
	if err != nil {
		t.Fatal(err)
	}
	if outcome.Status != VerificationNotVerified {
		t.Fatalf("status = %q, want not_verified", outcome.Status)
	}
	if loaded.SourceRef == "" {
		t.Fatal("source metadata was lost for unavailable content")
	}
}

func TestVerifyFromPayloadSourceOperationalErrorIsSeparate(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	binding := defaultRawBinding([]byte("expected"))
	acquisitionErr := errors.New("temporary source read failure")
	source := &syntheticPayloadSource{
		result: PayloadLoadResult{Available: false, SourceRef: "synthetic://remote/error"},
		err:    acquisitionErr,
	}

	outcome, loaded, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 0)
	if !errors.Is(err, acquisitionErr) {
		t.Fatalf("acquisition error = %v, want %v", err, acquisitionErr)
	}
	if outcome.Status != VerificationNotVerified {
		t.Fatalf("status = %q, want not_verified", outcome.Status)
	}
	if strings.Contains(outcome.Reason, "digest mismatch") {
		t.Fatalf("source error was confused with content mismatch: %s", outcome.Reason)
	}
	if loaded.SourceRef != "synthetic://remote/error" {
		t.Fatalf("source ref = %q", loaded.SourceRef)
	}
}

func TestVerifyFromPayloadSourceNilSourceIsNotVerified(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	binding := defaultRawBinding([]byte("expected"))

	outcome, _, err := registry.VerifyFromPayloadSource(context.Background(), binding, nil, 0)
	if err != nil {
		t.Fatal(err)
	}
	if outcome.Status != VerificationNotVerified {
		t.Fatalf("status = %q, want not_verified", outcome.Status)
	}
}

func TestVerifyFromPayloadSourceZeroLengthAvailablePayload(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	binding := defaultRawBinding([]byte{})
	// A nil Go slice is acceptable here because Available=true states that the
	// source successfully acquired a zero-length payload.
	source := &syntheticPayloadSource{result: PayloadLoadResult{Available: true, Payload: nil}}

	outcome, _, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 1)
	if err != nil {
		t.Fatal(err)
	}
	if outcome.Status != VerificationVerified {
		t.Fatalf("zero-length payload status = %q, reason=%s", outcome.Status, outcome.Reason)
	}
}

func TestVerifyFromPayloadSourceLocalLimitIsNotVerified(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	payload := []byte("payload larger than limit")
	binding := defaultRawBinding(payload)
	source := &syntheticPayloadSource{result: PayloadLoadResult{Available: true, Payload: payload}}

	outcome, _, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 4)
	if !errors.Is(err, ErrPayloadVerificationLimitExceeded) {
		t.Fatalf("limit error = %v", err)
	}
	if outcome.Status != VerificationNotVerified {
		t.Fatalf("status = %q, want not_verified", outcome.Status)
	}
	if strings.Contains(outcome.Reason, "digest mismatch") {
		t.Fatalf("local limit was confused with content mismatch: %s", outcome.Reason)
	}
}

func TestVerifyFromPayloadSourceJCSLeavesCanonicalizationToVerifier(t *testing.T) {
	registry, err := NewDefaultVerifierRegistry()
	if err != nil {
		t.Fatal(err)
	}
	canonical := []byte(`{"a":1,"z":2}`)
	binding := testBinding(
		RepresentationProfile{ProfileID: ProfileIDJCSSHA256, Version: ProfileVersionV1Alpha1},
		sha256Digest(canonical),
	)
	// Source returns non-canonical JSON bytes. Verification succeeds only because
	// the JCS verifier, not the Payload Source, owns canonicalization.
	sourcePayload := []byte(" { \"z\": 2, \"a\": 1 } ")
	source := &syntheticPayloadSource{result: PayloadLoadResult{Available: true, Payload: sourcePayload}}

	outcome, loaded, err := registry.VerifyFromPayloadSource(context.Background(), binding, source, 1024)
	if err != nil {
		t.Fatal(err)
	}
	if outcome.Status != VerificationVerified {
		t.Fatalf("JCS source verification status = %q, reason=%s", outcome.Status, outcome.Reason)
	}
	if string(loaded.Payload) != string(sourcePayload) {
		t.Fatalf("payload source bytes changed before verification: %q", loaded.Payload)
	}
}
