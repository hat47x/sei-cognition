package semanticruntime

import (
	"context"
	"errors"
	"fmt"
)

var ErrPayloadVerificationLimitExceeded = errors.New("payload exceeds local verification limit")

// PayloadRequest describes one runtime acquisition request. MaxBytes is a
// caller-supplied local resource policy, not a Universal Core constant. A
// value <= 0 means that this orchestration layer does not impose a byte limit.
type PayloadRequest struct {
	Binding  ExactBinding
	MaxBytes int64
}

// PayloadLoadResult keeps source acquisition metadata separate from Exact
// Binding and Representation Profile semantics. SourceRef is intentionally an
// opaque runtime reference; it is not a canonical storage locator schema.
type PayloadLoadResult struct {
	Available bool
	Payload   []byte
	SourceRef string
}

// PayloadSource is a replaceable runtime realization for retrieving bytes
// referenced by an Exact Binding. Filesystem paths, object keys, HTTP details,
// credentials, retries, and similar mechanics remain source-specific.
type PayloadSource interface {
	LoadPayload(ctx context.Context, request PayloadRequest) (PayloadLoadResult, error)
}

// VerifyFromPayloadSource acquires payload bytes and then delegates content
// verification to the Representation Verifier Registry.
//
// Acquisition failure and content mismatch are intentionally different:
//   - unavailable source content -> not_verified
//   - operational acquisition error -> not_verified plus a returned error
//   - local verification limit -> not_verified plus a returned error
//   - acquired bytes with a digest mismatch -> failed with no acquisition error
//
// The returned PayloadLoadResult lets callers observe source metadata without
// copying source-specific locators into Exact Binding or VerificationOutcome.
func (r *VerifierRegistry) VerifyFromPayloadSource(
	ctx context.Context,
	binding ExactBinding,
	source PayloadSource,
	maxBytes int64,
) (VerificationOutcome, PayloadLoadResult, error) {
	outcome := VerificationOutcome{Binding: binding}
	if source == nil {
		outcome.Status = VerificationNotVerified
		outcome.Reason = "payload source is unavailable"
		return outcome, PayloadLoadResult{}, nil
	}

	request := PayloadRequest{Binding: binding, MaxBytes: maxBytes}
	loaded, err := source.LoadPayload(ctx, request)
	if err != nil {
		outcome.Status = VerificationNotVerified
		outcome.Reason = fmt.Sprintf("payload acquisition failed: %v", err)
		return outcome, loaded, err
	}
	if !loaded.Available {
		outcome.Status = VerificationNotVerified
		outcome.Reason = "payload is unavailable from source"
		return outcome, loaded, nil
	}
	if maxBytes > 0 && int64(len(loaded.Payload)) > maxBytes {
		outcome.Status = VerificationNotVerified
		outcome.Reason = fmt.Sprintf(
			"payload size %d exceeds local verification limit %d",
			len(loaded.Payload),
			maxBytes,
		)
		return outcome, loaded, ErrPayloadVerificationLimitExceeded
	}

	payload := loaded.Payload
	if payload == nil {
		// Available=true with a nil slice means the source successfully acquired
		// a zero-length payload. Convert only the Go slice representation so the
		// existing Verify method does not interpret nil as unavailable content.
		payload = []byte{}
	}
	return r.Verify(binding, payload), loaded, nil
}
