package teiprojection

import (
	"os"
	"strings"
	"testing"
)

const valid = `{
  "schema": "tai.reference.tei-sei-decision-projection/v0",
  "contract": {"id": "sei.decision.projection", "version": "1"},
  "source": {"teiCommit": "abc", "contract": {"contractId": "sei.decision.record", "contractVersion": "1", "contractDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "sourceDigest": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "cases": 4}},
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

func TestParseRejectsInputsLooserThanTheTAISchema(t *testing.T) {
	cases := []struct{ name, from, to string }{
		{"recordType is not decision", `"recordType": "decision"`, `"recordType": "recommendation"`},
		{"recordType is missing", `"recordType": "decision", `, ``},
		{"refKind is empty", `"refKind": "decision"`, `"refKind": ""`},
		{"decision contract is empty", `"contract": "sei.decision-memory/v1alpha1"`, `"contract": ""`},
		{"contractDigest has no sha256 prefix", `"sha256:` + strings.Repeat("a", 64) + `"`, `"not-a-digest"`},
		{"contractDigest is too short", `"sha256:` + strings.Repeat("a", 64) + `"`, `"sha256:x"`},
		{"sourceDigest has upper-case hex", `"sha256:` + strings.Repeat("b", 64) + `"`, `"sha256:` + strings.Repeat("B", 64) + `"`},
		{"cases is zero", `"cases": 4`, `"cases": 0`},
		{"cases is a string", `"cases": 4`, `"cases": "4"`},
		{"source contractId is empty", `"contractId": "sei.decision.record"`, `"contractId": ""`},
		{"teiCommit is white space", `"teiCommit": "abc"`, `"teiCommit": "  "`},
		{"refId is only white space", `"refId": "decision-1"`, `"refId": "  "`},
		{"statement is only a newline", `"statement": "Adopt option A"`, `"statement": "
"`},
		{"decision refId appears twice", `"refId": "decision-1"`, `"refId": "a", "refId": "b"`},
		{"top-level key appears twice", `"schema": "` + ArtifactSchema + `",`, `"schema": "` + ArtifactSchema + `", "schema": "` + ArtifactSchema + `",`},
		{"known key differs only by case", `"refId": "decision-1"`, `"RefId": "decision-1"`},
		{"top-level key differs only by case", `"decision": {`, `"Decision": {`},
		{"data follows the value", `}
}`, `}
} {}`},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if !strings.Contains(valid, tc.from) {
				t.Fatalf("fixture does not contain %q", tc.from)
			}
			broken := strings.Replace(valid, tc.from, tc.to, 1)
			if _, err := Parse([]byte(broken)); err == nil {
				t.Fatalf("expected an error for %s", tc.name)
			}
		})
	}
}

// The TAI schema does not set additionalProperties to false, so an unknown key
// under its exact spelling is ignored.
func TestParseIgnoresUnknownKeys(t *testing.T) {
	withExtra := strings.Replace(valid, `"statement": "Adopt option A"`, `"statement": "Adopt option A", "status": "accepted"`, 1)
	artifact, err := Parse([]byte(withExtra))
	if err != nil {
		t.Fatalf("parse: %v", err)
	}
	if artifact.Decision.RefID != "decision-1" {
		t.Fatalf("refId = %q", artifact.Decision.RefID)
	}
}

// testdata/sei-decision-projection.json is a copy of the artifact tai-pleroma
// publishes; testdata/SOURCE.md records its origin. It is read without an
// environment variable so go test ./... always checks it.
func TestParseCommittedRealArtifact(t *testing.T) {
	data, err := os.ReadFile("testdata/sei-decision-projection.json")
	if err != nil {
		t.Fatalf("read artifact: %v", err)
	}
	artifact, err := Parse(data)
	if err != nil {
		t.Fatalf("parse artifact: %v", err)
	}
	if artifact.Decision.RefID != "decision-1" || artifact.Source.Contract.Cases != 4 {
		t.Fatalf("unexpected artifact content: %+v", artifact)
	}
}

func TestParseRealArtifactWhenProvided(t *testing.T) {
	path := os.Getenv("TEI_PROJECTION_ARTIFACT")
	if path == "" {
		t.Skip("TEI_PROJECTION_ARTIFACT is not set")
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read artifact: %v", err)
	}
	artifact, err := Parse(data)
	if err != nil {
		t.Fatalf("parse artifact: %v", err)
	}
	if artifact.Decision.RefID == "" {
		t.Fatal("decision refId is empty")
	}
}
