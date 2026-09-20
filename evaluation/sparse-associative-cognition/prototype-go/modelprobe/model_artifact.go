package modelprobe

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const (
	modelArtifactNotSupplied = "not-supplied"
	modelArtifactObserved    = "observed"
)

var sha256Hex64 = regexp.MustCompile(`^[0-9a-f]{64}$`)

type ModelArtifactIdentity struct {
	Status    string `json:"status"`
	FileName  string `json:"file_name,omitempty"`
	SizeBytes int64  `json:"size_bytes,omitempty"`
	SHA256    string `json:"sha256,omitempty"`
}

func ObserveModelArtifact(path, expectedSHA256 string) (ModelArtifactIdentity, error) {
	path = strings.TrimSpace(path)
	expectedSHA256 = strings.ToLower(strings.TrimSpace(expectedSHA256))
	if path == "" {
		if expectedSHA256 != "" {
			return ModelArtifactIdentity{}, fmt.Errorf("expected model sha256 requires model file")
		}
		return ModelArtifactIdentity{Status: modelArtifactNotSupplied}, nil
	}
	if expectedSHA256 != "" && !sha256Hex64.MatchString(expectedSHA256) {
		return ModelArtifactIdentity{}, fmt.Errorf("expected model sha256 must be 64 hexadecimal characters")
	}

	file, err := os.Open(path)
	if err != nil {
		return ModelArtifactIdentity{}, fmt.Errorf("open model file: %w", err)
	}
	defer file.Close()

	info, err := file.Stat()
	if err != nil {
		return ModelArtifactIdentity{}, fmt.Errorf("stat model file: %w", err)
	}
	if !info.Mode().IsRegular() {
		return ModelArtifactIdentity{}, fmt.Errorf("model file must be a regular file")
	}

	hasher := sha256.New()
	if _, err := io.Copy(hasher, file); err != nil {
		return ModelArtifactIdentity{}, fmt.Errorf("hash model file: %w", err)
	}
	digest := hex.EncodeToString(hasher.Sum(nil))
	if expectedSHA256 != "" && digest != expectedSHA256 {
		return ModelArtifactIdentity{}, fmt.Errorf("model sha256 mismatch: expected %s, observed %s", expectedSHA256, digest)
	}

	identity := ModelArtifactIdentity{
		Status:    modelArtifactObserved,
		FileName:  filepath.Base(filepath.Clean(path)),
		SizeBytes: info.Size(),
		SHA256:    digest,
	}
	if err := ValidateModelArtifactIdentity(identity); err != nil {
		return ModelArtifactIdentity{}, err
	}
	return identity, nil
}

func NormalizeModelArtifactIdentity(identity ModelArtifactIdentity) ModelArtifactIdentity {
	if strings.TrimSpace(identity.Status) == "" {
		return ModelArtifactIdentity{Status: modelArtifactNotSupplied}
	}
	identity.Status = strings.TrimSpace(identity.Status)
	identity.FileName = strings.TrimSpace(identity.FileName)
	identity.SHA256 = strings.ToLower(strings.TrimSpace(identity.SHA256))
	return identity
}

func ValidateModelArtifactIdentity(identity ModelArtifactIdentity) error {
	identity = NormalizeModelArtifactIdentity(identity)
	switch identity.Status {
	case modelArtifactNotSupplied:
		if identity.FileName != "" || identity.SizeBytes != 0 || identity.SHA256 != "" {
			return fmt.Errorf("not-supplied model artifact must not carry file_name, size, or sha256")
		}
		return nil
	case modelArtifactObserved:
		if identity.FileName == "" {
			return fmt.Errorf("observed model artifact file_name is required")
		}
		if identity.SizeBytes <= 0 {
			return fmt.Errorf("observed model artifact size_bytes must be positive")
		}
		if !sha256Hex64.MatchString(identity.SHA256) {
			return fmt.Errorf("observed model artifact sha256 must be 64 lowercase hexadecimal characters")
		}
		return nil
	default:
		return fmt.Errorf("unsupported model artifact status %q", identity.Status)
	}
}

func SameModelArtifactIdentity(left, right ModelArtifactIdentity) bool {
	left = NormalizeModelArtifactIdentity(left)
	right = NormalizeModelArtifactIdentity(right)
	if left.Status != right.Status {
		return false
	}
	if left.Status == modelArtifactNotSupplied {
		return true
	}
	return left.SizeBytes == right.SizeBytes && left.SHA256 == right.SHA256
}
