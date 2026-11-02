package teiprojection

import (
	"strings"
	"testing"
)

const valid = `{
  "schema": "tai.reference.tei-sei-decision-projection/v0",
  "contract": {"id": "sei.decision.projection", "version": "1"},
  "source": {"teiCommit": "abc", "contract": {"contractId": "sei.decision.record", "contractVersion": "1", "contractDigest": "sha256:x", "sourceDigest": "sha256:y", "cases": 4}},
  "decision": {"contract": "sei.decision-memory/v1alpha1", "recordType": "decision", "refKind": "decision", "refId": "decision-1", "statement": "Adopt option A"}
}`

func TestParseAcceptsValidArtifact(t *testing.T) {
	artifact, err := Parse([]byte(valid))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if artifact.Decision.RefID != "decision-1" {
		t.Fatalf("refId = %q", artifact.Decision.RefID)
	}
}

func TestParseRejectsWrongSchema(t *testing.T) {
	_, err := Parse([]byte(strings.Replace(valid, ArtifactSchema, "other", 1)))
	if err == nil {
		t.Fatal("expected an error")
	}
}

func TestParseRejectsMissingStatement(t *testing.T) {
	broken := strings.Replace(valid, `"statement": "Adopt option A"`, `"statement": ""`, 1)
	if _, err := Parse([]byte(broken)); err == nil {
		t.Fatal("expected an error")
	}
}
