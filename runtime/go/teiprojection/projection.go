// Package teiprojection reads a TEI decision projection artifact.
//
// The artifact is produced outside SEI. This package only parses and checks
// the envelope and the flat Decision fields; it does not write decisions or
// call the SEI runtime.
package teiprojection

import (
	"encoding/json"
	"errors"
	"fmt"
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

// Parse decodes and checks a decision projection artifact.
func Parse(data []byte) (Artifact, error) {
	var artifact Artifact
	if err := json.Unmarshal(data, &artifact); err != nil {
		return Artifact{}, fmt.Errorf("decode projection: %w", err)
	}
	if artifact.Schema != ArtifactSchema {
		return Artifact{}, fmt.Errorf("unexpected schema %q", artifact.Schema)
	}
	if artifact.Contract.ID == "" || artifact.Contract.Version == "" {
		return Artifact{}, errors.New("contract id and version are required")
	}
	if artifact.Source.TEICommit == "" {
		return Artifact{}, errors.New("source teiCommit is required")
	}
	if artifact.Decision.RefID == "" || artifact.Decision.Statement == "" {
		return Artifact{}, errors.New("decision refId and statement are required")
	}
	return artifact, nil
}
