package externalartifact

import (
	"crypto/sha1" // #nosec G505 -- Git blob identity is SHA-1 by Git format; content SHA-256 is also recorded below.
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"strings"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

// Descriptor identifies one version-pinned artifact owned outside SOZA.
// Repository, commit, path, and Git blob identity are acquisition/provenance
// metadata for this reference probe. They are not SOZA Universal semantic fields.
type Descriptor struct {
	ID          string `json:"id"`
	Repository  string `json:"repository"`
	Commit      string `json:"commit"`
	Path        string `json:"path"`
	GitBlobSHA1 string `json:"git_blob_sha1"`
}

// VerifiedArtifact is returned only after the acquired bytes match the pinned
// Git blob identity. ContentSHA256 gives the probe a stronger byte digest while
// retaining the repository-native Git identity used to select the artifact.
type VerifiedArtifact struct {
	Descriptor    Descriptor `json:"descriptor"`
	ContentSHA256 string     `json:"content_sha256"`
	Bytes         []byte     `json:"-"`
}

func (d Descriptor) Validate() error {
	if strings.TrimSpace(d.ID) == "" {
		return errors.New("external artifact ID is required")
	}
	if strings.TrimSpace(d.Repository) == "" || strings.TrimSpace(d.Commit) == "" || strings.TrimSpace(d.Path) == "" {
		return errors.New("external artifact requires repository, commit, and path")
	}
	if len(d.GitBlobSHA1) != 40 {
		return errors.New("external artifact Git blob SHA-1 must contain 40 hexadecimal characters")
	}
	if _, err := hex.DecodeString(d.GitBlobSHA1); err != nil {
		return fmt.Errorf("external artifact Git blob SHA-1 is invalid: %w", err)
	}
	return nil
}

func GitBlobSHA1(data []byte) string {
	h := sha1.New() // #nosec G401 -- required to reproduce Git blob object identity.
	_, _ = fmt.Fprintf(h, "blob %d\x00", len(data))
	_, _ = h.Write(data)
	return hex.EncodeToString(h.Sum(nil))
}

func ContentSHA256(data []byte) string {
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:])
}

// Verify refuses to return an artifact when acquired bytes differ from the
// version-pinned source identity. Callers must perform canonical mutation only
// after this function succeeds.
func Verify(descriptor Descriptor, data []byte) (VerifiedArtifact, error) {
	if err := descriptor.Validate(); err != nil {
		return VerifiedArtifact{}, err
	}
	actual := GitBlobSHA1(data)
	if !strings.EqualFold(actual, descriptor.GitBlobSHA1) {
		return VerifiedArtifact{}, fmt.Errorf("external artifact Git blob mismatch: got %s, want %s", actual, descriptor.GitBlobSHA1)
	}
	return VerifiedArtifact{
		Descriptor:    descriptor,
		ContentSHA256: ContentSHA256(data),
		Bytes:         append([]byte(nil), data...),
	}, nil
}

type provenancePayload struct {
	Repository    string `json:"repository"`
	Commit        string `json:"commit"`
	Path          string `json:"path"`
	GitBlobSHA1   string `json:"git_blob_sha1"`
	ContentSHA256 string `json:"content_sha256"`
}

// ProvenanceRecord keeps external source identity as an opaque not_verified
// record. SOZA preserves the provenance without pretending that repository or
// Git concepts are a Universal semantic Contract.
func ProvenanceRecord(artifact VerifiedArtifact) (semanticruntime.RuntimeRecord, error) {
	if err := artifact.Descriptor.Validate(); err != nil {
		return semanticruntime.RuntimeRecord{}, err
	}
	if artifact.ContentSHA256 == "" || len(artifact.Bytes) == 0 {
		return semanticruntime.RuntimeRecord{}, errors.New("verified external artifact bytes and content digest are required")
	}
	ref := semanticruntime.LogicalReference{Kind: "external-artifact-provenance", ID: artifact.Descriptor.ID}
	payload, err := json.Marshal(provenancePayload{
		Repository:    artifact.Descriptor.Repository,
		Commit:        artifact.Descriptor.Commit,
		Path:          artifact.Descriptor.Path,
		GitBlobSHA1:   strings.ToLower(artifact.Descriptor.GitBlobSHA1),
		ContentSHA256: artifact.ContentSHA256,
	})
	if err != nil {
		return semanticruntime.RuntimeRecord{}, err
	}
	return semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{
			Kind:       ref.Kind,
			LogicalRef: &ref,
			Payload:    payload,
		},
		Status: semanticruntime.RecordNotVerified,
	}, nil
}

func ProvenanceRef(artifact VerifiedArtifact) semanticruntime.LogicalReference {
	return semanticruntime.LogicalReference{Kind: "external-artifact-provenance", ID: artifact.Descriptor.ID}
}
