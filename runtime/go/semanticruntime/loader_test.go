package semanticruntime

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func repositoryRoot(t *testing.T) string {
	t.Helper()
	_, currentFile, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("runtime.Caller failed")
	}
	return filepath.Clean(filepath.Join(filepath.Dir(currentFile), "..", "..", ".."))
}

func fixturePath(t *testing.T, parts ...string) string {
	t.Helper()
	items := append([]string{repositoryRoot(t), "fixtures", "contracts", "v1alpha1"}, parts...)
	return filepath.Join(items...)
}

func readFixture(t *testing.T, parts ...string) []byte {
	t.Helper()
	path := fixturePath(t, parts...)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read fixture %s: %v", path, err)
	}
	return data
}

func TestCapabilityFixturesLoadFromContractSource(t *testing.T) {
	files, err := filepath.Glob(fixturePath(t, "capability", "F*.json"))
	if err != nil {
		t.Fatal(err)
	}
	if len(files) != 7 {
		t.Fatalf("expected 7 capability fixtures, got %d", len(files))
	}
	for _, path := range files {
		path := path
		t.Run(filepath.Base(path), func(t *testing.T) {
			data, err := os.ReadFile(path)
			if err != nil {
				t.Fatal(err)
			}

			var header struct {
				Contract string `json:"contract"`
			}
			if err := json.Unmarshal(data, &header); err != nil {
				t.Fatalf("read fixture contract identity: %v", err)
			}

			switch header.Contract {
			case ContractCapabilityObservation:
				record, err := LoadStandalone(data)
				if err != nil {
					t.Fatalf("LoadStandalone: %v", err)
				}
				if record.Status != RecordValidated {
					t.Fatalf("status = %q, want %q", record.Status, RecordValidated)
				}
				if record.Capability == nil {
					t.Fatal("capability read model is nil")
				}
				if record.Capability.Observation.ObservedAt == "" {
					t.Fatal("observed_at was not preserved")
				}

			case ContractSemanticInterchange:
				bundle, err := LoadInterchange(data)
				if err != nil {
					t.Fatalf("LoadInterchange: %v", err)
				}
				capabilityCount := 0
				for _, record := range bundle.Records {
					if record.Capability == nil {
						continue
					}
					capabilityCount++
					if record.Status != RecordValidated {
						t.Fatalf("capability record status = %q, want %q", record.Status, RecordValidated)
					}
					if record.Capability.Observation.ObservedAt == "" {
						t.Fatal("observed_at was not preserved in interchange capability record")
					}
				}
				if capabilityCount == 0 {
					t.Fatal("capability fixture interchange contains no capability observation")
				}

			default:
				t.Fatalf("unexpected top-level contract %q", header.Contract)
			}
		})
	}
}

func TestRecommendationWithoutDecision(t *testing.T) {
	record, err := LoadStandalone(readFixture(t, "boundary", "recommendation-without-decision.json"))
	if err != nil {
		t.Fatal(err)
	}
	if record.Decision == nil || record.Decision.Recommendation == nil {
		t.Fatal("recommendation was not loaded")
	}
	if record.Decision.Decision != nil {
		t.Fatal("recommendation-only fixture unexpectedly produced a decision")
	}
}

func TestDecisionRetainsUnresolvedReferences(t *testing.T) {
	record, err := LoadStandalone(readFixture(t, "boundary", "decision-with-unresolved.json"))
	if err != nil {
		t.Fatal(err)
	}
	if record.Decision == nil || record.Decision.Decision == nil {
		t.Fatal("decision was not loaded")
	}
	if len(record.Decision.Decision.UnresolvedRefs) == 0 {
		t.Fatal("unresolved references were lost")
	}
}

func TestPartialKnowledgeInterchangeAndLosslessReexport(t *testing.T) {
	input := readFixture(t, "boundary", "partial-knowledge-interchange.json")
	bundle, err := LoadInterchange(input)
	if err != nil {
		t.Fatal(err)
	}
	if len(bundle.Records) != 2 {
		t.Fatalf("records = %d, want 2", len(bundle.Records))
	}
	if bundle.Records[0].Capability == nil {
		t.Fatal("first record is not a capability observation")
	}
	conditions := bundle.Records[0].Capability.Observation.Conditions
	if len(conditions) != 2 || conditions[0].State != "unknown" || conditions[1].State != "withheld" {
		t.Fatalf("partial knowledge states were not preserved: %#v", conditions)
	}
	if bundle.Records[1].Decision == nil || bundle.Records[1].Decision.Decision == nil {
		t.Fatal("second record is not a decision")
	}
	if len(bundle.Records[1].Decision.Decision.UnresolvedRefs) != 1 {
		t.Fatal("decision unresolved reference was not preserved")
	}
	if !bytes.Equal(bundle.ExportOriginal(), input) {
		t.Fatal("ExportOriginal changed semantic interchange bytes")
	}
	exported := bundle.ExportOriginal()
	exported[0] ^= 0xff
	if bytes.Equal(bundle.ExportOriginal(), exported) {
		t.Fatal("ExportOriginal did not return an independent copy")
	}
}

func TestUnknownNestedContractRemainsNotVerified(t *testing.T) {
	bundle, err := LoadInterchange(readFixture(t, "boundary", "unknown-contract-version.json"))
	if err != nil {
		t.Fatal(err)
	}
	if len(bundle.Records) != 1 {
		t.Fatalf("records = %d, want 1", len(bundle.Records))
	}
	record := bundle.Records[0]
	if record.Status != RecordNotVerified {
		t.Fatalf("status = %q, want %q", record.Status, RecordNotVerified)
	}
	if len(record.EnvelopeRecord.Payload) == 0 {
		t.Fatal("opaque payload was not preserved")
	}
	if record.Decision != nil || record.Capability != nil || record.Reference != nil {
		t.Fatal("unknown Contract was interpreted as a known semantic record")
	}
}

func TestSameLogicalLineageRequiresExactEndpoints(t *testing.T) {
	_, err := LoadStandalone(readFixture(t, "negative", "same-logical-lineage-without-exact.json"))
	if err == nil {
		t.Fatal("expected same-logical lineage validation error")
	}
	if !strings.Contains(err.Error(), "exact endpoints") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestMismatchedDecisionBasisExactBindingIsRejected(t *testing.T) {
	_, err := LoadInterchange(readFixture(t, "negative", "interchange-mismatched-exact-binding.json"))
	if err == nil {
		t.Fatal("expected exact binding mismatch error")
	}
	if !strings.Contains(err.Error(), "does not match bundle record") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestCapabilityMissingObservedAtIsRejected(t *testing.T) {
	_, err := LoadStandalone(readFixture(t, "negative", "capability-missing-observed-at.json"))
	if err == nil {
		t.Fatal("expected missing observed_at error")
	}
	if !strings.Contains(err.Error(), "observed_at") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestDecisionCannotSmuggleAuthorityField(t *testing.T) {
	_, err := LoadStandalone(readFixture(t, "negative", "decision-authority-field.json"))
	if err == nil {
		t.Fatal("expected unknown authority field to be rejected")
	}
	if !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestVerificationOutcomeVocabulary(t *testing.T) {
	for _, tc := range []struct {
		name string
		want VerificationStatus
	}{
		{"verification-not-verified.json", VerificationNotVerified},
		{"verification-failed.json", VerificationFailed},
	} {
		t.Run(tc.name, func(t *testing.T) {
			record, err := LoadStandalone(readFixture(t, "boundary", tc.name))
			if err != nil {
				t.Fatal(err)
			}
			if record.Reference == nil || record.Reference.VerificationOutcome == nil {
				t.Fatal("verification outcome was not loaded")
			}
			if got := record.Reference.VerificationOutcome.Status; got != tc.want {
				t.Fatalf("status = %q, want %q", got, tc.want)
			}
		})
	}
}
