package semanticruntime

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/big"
	"strings"

	"github.com/gowebpki/jcs"
)

const (
	ProfileIDJCSSHA256      = "soza.jcs+sha256"
	ProfileIDRawBytesSHA256 = "soza.raw-bytes+sha256"
	ProfileVersionV1Alpha1  = "v1alpha1"

	VerifierRefJCSSHA256V1Alpha1      = "soza.runtime.verifier/jcs+sha256/v1alpha1"
	VerifierRefRawBytesSHA256V1Alpha1 = "soza.runtime.verifier/raw-bytes+sha256/v1alpha1"

	jcsSafeIntegerMax = "9007199254740991"
)

// RepresentationVerifier implements one explicit Representation Profile.
// Profile authority remains in the Profile Definition and referenced external
// standard; this interface is only a replaceable runtime implementation.
type RepresentationVerifier interface {
	Profile() RepresentationProfile
	VerifierRef() string
	Digest(payload []byte) (string, error)
}

// VerifierRegistry resolves a Representation Profile to a runtime verifier.
// It does not add new semantic meaning to Exact Binding or VerificationOutcome.
type VerifierRegistry struct {
	verifiers map[RepresentationProfile]RepresentationVerifier
}

// NewVerifierRegistry constructs a registry and rejects ambiguous duplicate
// Profile registrations.
func NewVerifierRegistry(verifiers ...RepresentationVerifier) (*VerifierRegistry, error) {
	registry := &VerifierRegistry{verifiers: make(map[RepresentationProfile]RepresentationVerifier, len(verifiers))}
	for _, verifier := range verifiers {
		if verifier == nil {
			return nil, errors.New("representation verifier must not be nil")
		}
		profile := verifier.Profile()
		if err := validateProfile(profile); err != nil {
			return nil, fmt.Errorf("verifier profile: %w", err)
		}
		if _, exists := registry.verifiers[profile]; exists {
			return nil, fmt.Errorf("duplicate verifier for profile %s/%s", profile.ProfileID, profile.Version)
		}
		registry.verifiers[profile] = verifier
	}
	return registry, nil
}

// NewDefaultVerifierRegistry returns the current runtime implementations for
// the two Representation Profiles accepted by ADR-0023.
func NewDefaultVerifierRegistry() (*VerifierRegistry, error) {
	return NewVerifierRegistry(jcsSHA256Verifier{}, rawBytesSHA256Verifier{})
}

// Verify checks payload bytes against an Exact Binding without mutating the
// binding. A nil payload means the content is unavailable; an empty but
// non-nil byte slice is an available zero-length payload.
func (r *VerifierRegistry) Verify(binding ExactBinding, payload []byte) VerificationOutcome {
	outcome := VerificationOutcome{Binding: binding}

	if payload == nil {
		outcome.Status = VerificationNotVerified
		outcome.Reason = "payload is unavailable"
		return outcome
	}
	if r == nil {
		outcome.Status = VerificationNotVerified
		outcome.Reason = "verifier registry is unavailable"
		return outcome
	}

	verifier, ok := r.verifiers[binding.RepresentationProfile]
	if !ok {
		outcome.Status = VerificationNotVerified
		outcome.Reason = fmt.Sprintf(
			"no verifier registered for profile %s/%s",
			binding.RepresentationProfile.ProfileID,
			binding.RepresentationProfile.Version,
		)
		return outcome
	}

	outcome.VerifierRef = verifier.VerifierRef()
	actualDigest, err := verifier.Digest(payload)
	if err != nil {
		outcome.Status = VerificationFailed
		outcome.Reason = err.Error()
		return outcome
	}
	if actualDigest != binding.ContentDigest {
		outcome.Status = VerificationFailed
		outcome.Reason = fmt.Sprintf("content digest mismatch: expected %s, got %s", binding.ContentDigest, actualDigest)
		return outcome
	}

	outcome.Status = VerificationVerified
	return outcome
}

type jcsSHA256Verifier struct{}

func (jcsSHA256Verifier) Profile() RepresentationProfile {
	return RepresentationProfile{ProfileID: ProfileIDJCSSHA256, Version: ProfileVersionV1Alpha1}
}

func (jcsSHA256Verifier) VerifierRef() string {
	return VerifierRefJCSSHA256V1Alpha1
}

func (jcsSHA256Verifier) Digest(payload []byte) (string, error) {
	if err := validateJCSSafeIntegers(payload); err != nil {
		return "", fmt.Errorf("JCS profile preflight failed: %w", err)
	}
	canonical, err := jcs.Transform(payload)
	if err != nil {
		return "", fmt.Errorf("JCS canonicalization failed: %w", err)
	}
	return sha256Digest(canonical), nil
}

type rawBytesSHA256Verifier struct{}

func (rawBytesSHA256Verifier) Profile() RepresentationProfile {
	return RepresentationProfile{ProfileID: ProfileIDRawBytesSHA256, Version: ProfileVersionV1Alpha1}
}

func (rawBytesSHA256Verifier) VerifierRef() string {
	return VerifierRefRawBytesSHA256V1Alpha1
}

func (rawBytesSHA256Verifier) Digest(payload []byte) (string, error) {
	return sha256Digest(payload), nil
}

func sha256Digest(payload []byte) string {
	sum := sha256.Sum256(payload)
	return fmt.Sprintf("sha256:%x", sum)
}

// validateJCSSafeIntegers preserves the numeric safety boundary already used
// by the commit-pinned JCS probe. It intentionally does not normalize Unicode
// or infer application-specific decimal precision requirements.
func validateJCSSafeIntegers(payload []byte) error {
	decoder := json.NewDecoder(bytes.NewReader(payload))
	decoder.UseNumber()

	var value any
	if err := decoder.Decode(&value); err != nil {
		return err
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return errors.New("multiple JSON values are not allowed")
		}
		return err
	}

	limit := new(big.Int)
	if _, ok := limit.SetString(jcsSafeIntegerMax, 10); !ok {
		return errors.New("invalid internal JCS safe integer limit")
	}
	return walkJCSNumbers(value, limit)
}

func walkJCSNumbers(value any, limit *big.Int) error {
	switch typed := value.(type) {
	case json.Number:
		text := typed.String()
		if strings.ContainsAny(text, ".eE") {
			return nil
		}
		number := new(big.Int)
		if _, ok := number.SetString(text, 10); !ok {
			return fmt.Errorf("invalid integer literal: %s", text)
		}
		if new(big.Int).Abs(number).Cmp(limit) > 0 {
			return fmt.Errorf("unsafe integer outside IEEE-754 safe range: %s", text)
		}
	case []any:
		for _, item := range typed {
			if err := walkJCSNumbers(item, limit); err != nil {
				return err
			}
		}
	case map[string]any:
		for _, item := range typed {
			if err := walkJCSNumbers(item, limit); err != nil {
				return err
			}
		}
	}
	return nil
}
