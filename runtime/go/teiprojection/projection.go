// Package teiprojection reads a TEI decision projection artifact.
//
// The artifact is produced outside SEI. This package only parses and checks
// the envelope and the flat Decision fields; it does not write decisions or
// call the SEI runtime.
//
// Parse accepts what the TAI-side schema
// (tai-pleroma integrations/pilot-sei-decision/artifact.schema.json) accepts,
// or less. It repeats the schema's required fields and value checks, and adds
// three checks the schema leaves to the parser:
//
//   - A key that appears twice in one object is rejected. Parsers disagree on
//     which value wins, so the artifact would read differently elsewhere.
//   - A key that matches a known field only when case is ignored (for example
//     "RefId") is rejected. Go's encoding/json would accept it as refId, but
//     the schema treats it as an unknown key.
//   - A digest must be "sha256:" followed by 64 lowercase hex digits. The
//     schema only checks the "sha256:" prefix.
//
// Unknown keys under their exact spelling are ignored, as the schema allows
// them. A refId or statement made only of white space is rejected.
package teiprojection

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"regexp"
	"strings"
)

const ArtifactSchema = "tai.reference.tei-sei-decision-projection/v0"

// Artifact is the projection envelope.
type Artifact struct {
	Schema   string   `json:"schema"`
	Contract Contract `json:"contract"`
	Source   Source   `json:"source"`
	Decision Decision `json:"decision"`
}

// Contract identifies the projection contract.
type Contract struct {
	ID      string `json:"id"`
	Version string `json:"version"`
}

// Source records where the projection came from.
type Source struct {
	TEICommit string         `json:"teiCommit"`
	Contract  SourceContract `json:"contract"`
}

// SourceContract records the generator contract metadata.
type SourceContract struct {
	ContractID      string `json:"contractId"`
	ContractVersion string `json:"contractVersion"`
	ContractDigest  string `json:"contractDigest"`
	SourceDigest    string `json:"sourceDigest"`
	Cases           int    `json:"cases"`
}

// Decision is the flat projection of a decision-memory Decision.
type Decision struct {
	Contract   string `json:"contract"`
	RecordType string `json:"recordType"`
	RefKind    string `json:"refKind"`
	RefID      string `json:"refId"`
	Statement  string `json:"statement"`
	Rationale  string `json:"rationale,omitempty"`
}

// digestPattern is the form of contractDigest and sourceDigest.
var digestPattern = regexp.MustCompile(`^sha256:[0-9a-f]{64}$`)

// knownKeys lists the field names of each object whose keys Parse checks for
// case-variant spellings. The key is the dotted path from the artifact root.
var knownKeys = map[string][]string{
	"":                {"schema", "contract", "source", "decision"},
	"contract":        {"id", "version"},
	"source":          {"teiCommit", "contract"},
	"source.contract": {"contractId", "contractVersion", "contractDigest", "sourceDigest", "cases"},
	"decision":        {"contract", "recordType", "refKind", "refId", "statement", "rationale"},
}

// Parse decodes and checks a decision projection artifact.
func Parse(data []byte) (Artifact, error) {
	if err := checkKeys(data); err != nil {
		return Artifact{}, err
	}
	var artifact Artifact
	if err := json.Unmarshal(data, &artifact); err != nil {
		return Artifact{}, fmt.Errorf("decode projection: %w", err)
	}
	if artifact.Schema != ArtifactSchema {
		return Artifact{}, fmt.Errorf("unexpected schema %q", artifact.Schema)
	}
	if blank(artifact.Contract.ID) || blank(artifact.Contract.Version) {
		return Artifact{}, errors.New("contract id and version are required")
	}
	src := artifact.Source
	if blank(src.TEICommit) {
		return Artifact{}, errors.New("source teiCommit is required")
	}
	if blank(src.Contract.ContractID) || blank(src.Contract.ContractVersion) {
		return Artifact{}, errors.New("source contract contractId and contractVersion are required")
	}
	if !digestPattern.MatchString(src.Contract.ContractDigest) {
		return Artifact{}, fmt.Errorf("source contract contractDigest must be sha256: and 64 lowercase hex digits, got %q", src.Contract.ContractDigest)
	}
	if !digestPattern.MatchString(src.Contract.SourceDigest) {
		return Artifact{}, fmt.Errorf("source contract sourceDigest must be sha256: and 64 lowercase hex digits, got %q", src.Contract.SourceDigest)
	}
	if src.Contract.Cases < 1 {
		return Artifact{}, fmt.Errorf("source contract cases must be at least 1, got %d", src.Contract.Cases)
	}
	d := artifact.Decision
	if blank(d.Contract) {
		return Artifact{}, errors.New("decision contract is required")
	}
	if d.RecordType != "decision" {
		return Artifact{}, fmt.Errorf("decision recordType must be %q, got %q", "decision", d.RecordType)
	}
	if blank(d.RefKind) {
		return Artifact{}, errors.New("decision refKind is required")
	}
	if blank(d.RefID) || blank(d.Statement) {
		return Artifact{}, errors.New("decision refId and statement are required")
	}
	return artifact, nil
}

func blank(s string) bool { return strings.TrimSpace(s) == "" }

// checkKeys walks the JSON text and rejects duplicate keys in any object and,
// in the objects listed in knownKeys, keys that differ from a known field only
// by case. It also rejects data after the first JSON value.
func checkKeys(data []byte) error {
	dec := json.NewDecoder(bytes.NewReader(data))
	if err := walkValue(dec, "", true); err != nil {
		return fmt.Errorf("decode projection: %w", err)
	}
	if _, err := dec.Token(); err != io.EOF {
		return errors.New("decode projection: data after the top-level JSON value")
	}
	return nil
}

func walkValue(dec *json.Decoder, path string, known bool) error {
	tok, err := dec.Token()
	if err != nil {
		return err
	}
	delim, ok := tok.(json.Delim)
	if !ok {
		return nil
	}
	if delim == '[' {
		for dec.More() {
			if err := walkValue(dec, "", false); err != nil {
				return err
			}
		}
		_, err := dec.Token()
		return err
	}
	seen := map[string]bool{}
	fields := knownKeys[path]
	for dec.More() {
		keyTok, err := dec.Token()
		if err != nil {
			return err
		}
		key := keyTok.(string)
		if seen[key] {
			return fmt.Errorf("duplicate key %q", key)
		}
		seen[key] = true
		childKnown := false
		if known {
			exact := false
			for _, f := range fields {
				if key == f {
					exact = true
				} else if strings.EqualFold(key, f) {
					return fmt.Errorf("key %q differs from %q only by case", key, f)
				}
			}
			childKnown = exact
		}
		childPath := key
		if path != "" {
			childPath = path + "." + key
		}
		if err := walkValue(dec, childPath, childKnown); err != nil {
			return err
		}
	}
	_, err = dec.Token()
	return err
}
