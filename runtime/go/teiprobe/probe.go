package teiprobe

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
	"github.com/hat47x/sei-cognition/runtime/go/teiintegration"
)

const (
	ReportSchema   = "sei.e3b-tei-probe/v1"
	ManifestSchema = "sei.tei-binary-build-manifest/v1"

	SourceBindingNotVerified    = "not_verified"
	SourceBindingManifestMatch  = "manifest_matched"
	BinaryDigestPrePostMatched  = "pre_post_matched"
)

var (
	sha256Pattern     = regexp.MustCompile(`^[0-9a-fA-F]{64}package teiprobe

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
	"github.com/hat47x/sei-cognition/runtime/go/teiintegration"
)

const (
	ReportSchema   = "sei.e3b-tei-probe/v1"
	ManifestSchema = "sei.tei-binary-build-manifest/v1"

	SourceBindingNotVerified    = "not_verified"
	SourceBindingManifestMatch  = "manifest_matched"
	BinaryDigestPrePostMatched  = "pre_post_matched"
)

)
	repositoryPattern = regexp.MustCompile(`^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)+package teiprobe

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
	"github.com/hat47x/sei-cognition/runtime/go/teiintegration"
)

const (
	ReportSchema   = "sei.e3b-tei-probe/v1"
	ManifestSchema = "sei.tei-binary-build-manifest/v1"

	SourceBindingNotVerified    = "not_verified"
	SourceBindingManifestMatch  = "manifest_matched"
	BinaryDigestPrePostMatched  = "pre_post_matched"
)

)
	commitPattern     = regexp.MustCompile(`^[0-9a-fA-F]{7,64}package teiprobe

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
	"github.com/hat47x/sei-cognition/runtime/go/teiintegration"
)

const (
	ReportSchema   = "sei.e3b-tei-probe/v1"
	ManifestSchema = "sei.tei-binary-build-manifest/v1"

	SourceBindingNotVerified    = "not_verified"
	SourceBindingManifestMatch  = "manifest_matched"
	BinaryDigestPrePostMatched  = "pre_post_matched"
)

)
)

// BuildManifest is an optional, evaluation-local declaration that binds one
// supplied executable digest to a declared source repository and commit.
// A match does not establish manifest authenticity or signed build provenance.
type BuildManifest struct {
	Schema       string `json:"schema"`
	Repository   string `json:"repository"`
	Commit       string `json:"commit"`
	BinarySHA256 string `json:"binary_sha256"`
}

// Request keeps executable acquisition and credentials outside the probe.
// BinaryPath must point directly at the executable file that will be invoked.
type Request struct {
	BinaryPath          string
	DeclaredRepository  string
	DeclaredCommit      string
	ManifestPath        string
	ProviderPlan        teiintegration.ProviderPlanRequest
	ObservationContext  provideradapter.ObservationContext
}

type BinaryIdentity struct {
	SHA256          string `json:"sha256"`
	DigestStability string `json:"digest_stability"`
}

type SourceDeclaration struct {
	Repository string `json:"repository"`
	Commit     string `json:"commit"`
}

type ExecutionTarget struct {
	Solution string `json:"solution"`
	Version  string `json:"version"`
}

// Report is derived execution Evidence. It is not a Universal semantic
// contract and does not authenticate the optional manifest.
type Report struct {
	Schema                string                                        `json:"schema"`
	Result                string                                        `json:"result"`
	Binary                BinaryIdentity                                `json:"binary"`
	Source                SourceDeclaration                             `json:"source"`
	SourceBinding         string                                        `json:"source_binding"`
	ManifestProvided      bool                                          `json:"manifest_provided"`
	Execution             ExecutionTarget                               `json:"execution"`
	CapabilityObservation semanticruntime.CapabilityObservationDocument `json:"capability_observation"`
}

func hashRegularExecutable(path string) (string, error) {
	info, err := os.Lstat(path)
	if err != nil {
		return "", fmt.Errorf("inspect TEI binary: %w", err)
	}
	if info.Mode()&os.ModeSymlink != 0 {
		return "", errors.New("TEI binary path must be a direct regular file, not a symlink")
	}
	if !info.Mode().IsRegular() {
		return "", errors.New("TEI binary path must be a regular file")
	}
	file, err := os.Open(path)
	if err != nil {
		return "", fmt.Errorf("open TEI binary: %w", err)
	}
	defer file.Close()

	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", fmt.Errorf("hash TEI binary: %w", err)
	}
	return hex.EncodeToString(hash.Sum(nil)), nil
}

func decodeManifest(payload []byte) (BuildManifest, error) {
	decoder := json.NewDecoder(bytes.NewReader(payload))
	decoder.DisallowUnknownFields()
	var manifest BuildManifest
	if err := decoder.Decode(&manifest); err != nil {
		return BuildManifest{}, fmt.Errorf("read TEI build manifest: %w", err)
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return BuildManifest{}, errors.New("TEI build manifest contains multiple JSON values")
		}
		return BuildManifest{}, fmt.Errorf("inspect TEI build manifest trailing data: %w", err)
	}
	if manifest.Schema != ManifestSchema {
		return BuildManifest{}, fmt.Errorf("TEI build manifest schema must be %s", ManifestSchema)
	}
	if strings.TrimSpace(manifest.Repository) == "" {
		return BuildManifest{}, errors.New("TEI build manifest repository is required")
	}
	if strings.TrimSpace(manifest.Commit) == "" {
		return BuildManifest{}, errors.New("TEI build manifest commit is required")
	}
	if !sha256Pattern.MatchString(manifest.BinarySHA256) {
		return BuildManifest{}, errors.New("TEI build manifest binary_sha256 must be a 64-character hexadecimal SHA-256")
	}
	return manifest, nil
}

func loadManifest(path string) (BuildManifest, error) {
	payload, err := os.ReadFile(path)
	if err != nil {
		return BuildManifest{}, fmt.Errorf("read TEI build manifest file: %w", err)
	}
	return decodeManifest(payload)
}

func sourceBinding(request Request, binaryDigest string) (string, bool, error) {
	if strings.TrimSpace(request.ManifestPath) == "" {
		return SourceBindingNotVerified, false, nil
	}
	manifest, err := loadManifest(request.ManifestPath)
	if err != nil {
		return "", true, err
	}
	if manifest.Repository != request.DeclaredRepository {
		return "", true, errors.New("TEI build manifest repository does not match declared repository")
	}
	if manifest.Commit != request.DeclaredCommit {
		return "", true, errors.New("TEI build manifest commit does not match declared commit")
	}
	if !strings.EqualFold(manifest.BinarySHA256, binaryDigest) {
		return "", true, errors.New("TEI build manifest binary digest does not match observed executable")
	}
	return SourceBindingManifestMatch, true, nil
}

func validateRequest(request Request) error {
	if strings.TrimSpace(request.BinaryPath) == "" {
		return errors.New("TEI binary path is required")
	}
	repository := strings.TrimSpace(request.DeclaredRepository)
	if repository == "" {
		return errors.New("declared TEI source repository is required")
	}
	if !repositoryPattern.MatchString(repository) {
		return errors.New("declared TEI source repository must be a non-URL repository identifier")
	}
	commit := strings.TrimSpace(request.DeclaredCommit)
	if commit == "" {
		return errors.New("declared TEI source commit is required")
	}
	if !commitPattern.MatchString(commit) {
		return errors.New("declared TEI source commit must be a hexadecimal object identity")
	}
	return nil
}

// Probe hashes the exact direct executable path, validates optional source
// binding, delegates Provider Plan interpretation to teiintegration, then
// re-hashes the executable. It returns a PASS report only when execution and
// current Capability Observation validation both succeed and the executable
// digest remains stable across the run.
func Probe(ctx context.Context, request Request) (Report, error) {
	if err := validateRequest(request); err != nil {
		return Report{}, err
	}
	request.DeclaredRepository = strings.TrimSpace(request.DeclaredRepository)
	request.DeclaredCommit = strings.ToLower(strings.TrimSpace(request.DeclaredCommit))

	beforeDigest, err := hashRegularExecutable(request.BinaryPath)
	if err != nil {
		return Report{}, err
	}
	binding, manifestProvided, err := sourceBinding(request, beforeDigest)
	if err != nil {
		return Report{}, err
	}

	observationContext := request.ObservationContext
	observationContext.SourceStateRef = "tei-binary-sha256:" + beforeDigest
	observation, err := (teiintegration.CLI{Executable: request.BinaryPath}).ObserveProviderPlan(
		ctx,
		request.ProviderPlan,
		observationContext,
	)
	if err != nil {
		return Report{}, err
	}

	afterDigest, err := hashRegularExecutable(request.BinaryPath)
	if err != nil {
		return Report{}, err
	}
	if afterDigest != beforeDigest {
		return Report{}, errors.New("TEI executable digest changed during probe execution")
	}

	return Report{
		Schema: ReportSchema,
		Result: "pass",
		Binary: BinaryIdentity{
			SHA256:          beforeDigest,
			DigestStability: BinaryDigestPrePostMatched,
		},
		Source: SourceDeclaration{
			Repository: request.DeclaredRepository,
			Commit:     request.DeclaredCommit,
		},
		SourceBinding:    binding,
		ManifestProvided: manifestProvided,
		Execution: ExecutionTarget{
			Solution: request.ProviderPlan.Solution,
			Version:  request.ProviderPlan.Version,
		},
		CapabilityObservation: observation,
	}, nil
}
