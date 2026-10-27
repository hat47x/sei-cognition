package seicli

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func seedResumeBundle(t *testing.T, records ...semanticruntime.InterchangeRecord) (string, []byte) {
	t.Helper()
	raw, err := json.MarshalIndent(semanticruntime.SemanticInterchange{
		Contract: semanticruntime.ContractSemanticInterchange, BundleID: "resume-scope", Records: records,
	}, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), raw, 0o600); err != nil {
		t.Fatal(err)
	}
	return root, raw
}

func decisionWithOpenRefs(t *testing.T, id, scope string, refs ...semanticruntime.Reference) semanticruntime.InterchangeRecord {
	t.Helper()
	payload, err := json.Marshal(semanticruntime.DecisionMemoryDocument{
		Contract: semanticruntime.ContractDecisionMemory, RecordType: "decision",
		Decision: &semanticruntime.Decision{Ref: semanticruntime.LogicalReference{Kind: "decision", ID: id, Scope: scope},
			Statement: "A synthetic decision", UnresolvedRefs: refs},
	})
	if err != nil {
		t.Fatal(err)
	}
	return semanticruntime.InterchangeRecord{RecordID: id, Contract: semanticruntime.ContractIdentity{
		ContractID: semanticruntime.ContractIDDecisionMemory, Version: semanticruntime.ContractVersionV1Alpha1,
	}, Kind: "decision", Payload: payload}
}

func TestResumeZeroEntriesDoesNotClaimNoOpenQuestions(t *testing.T) {
	unknown := semanticruntime.InterchangeRecord{RecordID: "uninterpreted-Q1", Kind: "question",
		Contract: semanticruntime.ContractIdentity{ContractID: "example.questions", Version: "v9"},
		Payload:  json.RawMessage(`{"id":"Q1","state":"held"}`)}
	root, original := seedResumeBundle(t, unknown)
	var view ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &view); err != nil {
		t.Fatal(err)
	}
	if len(view.Decisions) != 0 || len(view.Unresolved) != 0 || view.NotVerifiedRecordCount != 1 {
		t.Fatalf("must preserve zero projected entries and the unknown record: %+v", view)
	}
	if view.Coverage.UnresolvedSource != "recognized-decision-unresolved-refs" || view.Coverage.CaseCompleteness != "not_assessed" {
		t.Fatalf("zero entries must retain an explicit limited scope: %+v", view.Coverage)
	}
	if view.SnapshotDigest != fmt.Sprintf("sha256:%x", sha256.Sum256(original)) {
		t.Fatal("snapshot digest must bind original bytes")
	}
	if len(view.NotVerifiedRecords) != 1 {
		t.Fatalf("missing original-record locator: %+v", view.NotVerifiedRecords)
	}
	loc := view.NotVerifiedRecords[0]
	if loc.RecordID != unknown.RecordID || loc.Contract != unknown.Contract || loc.JSONPointer != "/records/0" {
		t.Fatalf("unknown payload must remain uninterpreted with a source locator: %+v", loc)
	}
	text := mustRun(t, "resume", "--data-root", root)
	for _, want := range []string{"not a case-wide inventory", "Unresolved (0)", "uninterpreted-Q1", "/records/0", view.SnapshotDigest} {
		if !strings.Contains(text, want) {
			t.Errorf("missing %q in %s", want, text)
		}
	}
	after, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(original, after) {
		t.Fatal("resume must not create Decisions or rewrite the original bundle")
	}
	// A locator belongs to one byte snapshot, even if bundle_id stays the same.
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), append(original, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
	var changed ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &changed); err != nil {
		t.Fatal(err)
	}
	if changed.BundleID != view.BundleID || changed.SnapshotDigest == view.SnapshotDigest {
		t.Fatal("a matching logical bundle ID must not reuse the old byte binding")
	}
}

func TestResumeCountsEntriesSeparatelyAndPreservesScopedExactReferences(t *testing.T) {
	first := semanticruntime.Reference{Kind: "question", ID: "Q1", Scope: "sales"}
	second := semanticruntime.Reference{LogicalRef: &semanticruntime.LogicalReference{Kind: "question", ID: "Q1", Scope: "procurement"},
		ContentDigest: "sha256:" + strings.Repeat("1", 64), RepresentationProfile: &semanticruntime.RepresentationProfile{
			ProfileID: "sei.raw-bytes+sha256", Version: "v1alpha1"}}
	root, raw := seedResumeBundle(t, decisionWithOpenRefs(t, "D1", "team-a", first, second), decisionWithOpenRefs(t, "D2", "team-b", first))
	var view ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &view); err != nil {
		t.Fatal(err)
	}
	if len(view.Unresolved) != 3 || view.Coverage.UnresolvedEntryCount != 3 || view.Coverage.DistinctUnresolvedLogicalReferenceCount != 2 {
		t.Fatalf("same display ID, different scope, and repeated reference must remain distinct concepts: %+v", view)
	}
	for _, entry := range view.Unresolved {
		if entry.Ref != "question:Q1" {
			t.Fatal("legacy display field must remain compatible")
		}
		var envelope semanticruntime.SemanticInterchange
		if err := json.Unmarshal(raw, &envelope); err != nil {
			t.Fatal(err)
		}
		var index int
		if _, err := fmt.Sscanf(entry.SourceRecord.JSONPointer, "/records/%d", &index); err != nil {
			t.Fatal(err)
		}
		if index < 0 || index >= len(envelope.Records) || envelope.Records[index].RecordID != entry.SourceRecord.RecordID {
			t.Fatal("locator points to the wrong source record")
		}
		if entry.LeftOpenByReference.ID != entry.LeftOpenBy || entry.LeftOpenByReference.Scope == "" {
			t.Fatal("decision scope was lost")
		}
		identity, ok := entry.Reference.LogicalIdentity()
		if !ok || identity.Scope == "" {
			t.Fatal("unresolved scope was lost")
		}
		if identity.Scope == "procurement" && (!entry.Reference.IsExact() || entry.Reference.ContentDigest != second.ContentDigest) {
			t.Fatal("exact historical binding was lost")
		}
	}
	text := mustRun(t, "resume", "--data-root", root)
	for _, want := range []string{"3 entries; 2 distinct logical references", `"sales"`, `"procurement"`, `"team-a"`, `"team-b"`} {
		if !strings.Contains(text, want) {
			t.Errorf("human output lost %q: %s", want, text)
		}
	}
}

func TestResumeReturnsAnUninterpretedRecordOnlyFromTheExpectedSnapshot(t *testing.T) {
	unknown := semanticruntime.InterchangeRecord{RecordID: "Q1", Kind: "question",
		Contract: semanticruntime.ContractIdentity{ContractID: "example.questions", Version: "v9"},
		Payload:  json.RawMessage(`{"state":"held","unrecognized":{"keep":[1,2,3]}}`)}
	root, original := seedResumeBundle(t, unknown)
	var listing ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &listing); err != nil {
		t.Fatal(err)
	}
	var found struct {
		SnapshotDigest   string                                 `json:"snapshot_digest"`
		SourceRecord     ResumeRecordLocation                   `json:"source_record"`
		ValidationStatus semanticruntime.RecordValidationStatus `json:"validation_status"`
		Record           semanticruntime.InterchangeRecord      `json:"record"`
	}
	args := []string{"resume", "--data-root", root, "--json", "--record-id", listing.NotVerifiedRecords[0].RecordID,
		"--snapshot-digest", listing.SnapshotDigest}
	if err := json.Unmarshal([]byte(mustRun(t, args...)), &found); err != nil {
		t.Fatal(err)
	}
	if found.SnapshotDigest != listing.SnapshotDigest || found.SourceRecord != listing.NotVerifiedRecords[0] || found.ValidationStatus != semanticruntime.RecordNotVerified {
		t.Fatalf("retrieval must preserve snapshot, locator, and uninterpreted status: %+v", found)
	}
	if found.Record.RecordID != "Q1" || !bytes.Equal(found.Record.Payload, unknown.Payload) {
		t.Fatal("record payload was replaced or interpreted")
	}
	after, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(original, after) {
		t.Fatal("record retrieval rewrote the bundle")
	}
	// Same bundle ID and same record ID are insufficient after any byte change.
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), append(original, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
	out, err := run(t, args...)
	if err == nil || !strings.Contains(err.Error(), "snapshot digest mismatch") || out != "" {
		t.Fatalf("stale retrieval must return no record: out=%q err=%v", out, err)
	}
}

func TestResumeRecordLookupRejectsMissingPreconditionsWithoutOutput(t *testing.T) {
	root, original := seedResumeBundle(t, decisionWithOpenRefs(t, "D1", "team-a"))
	digest := fmt.Sprintf("sha256:%x", sha256.Sum256(original))
	cases := [][]string{
		{"--json", "--record-id", ""},
		{"--json", "--snapshot-digest", ""},
		{"--json", "--record-id", "D1"},
		{"--json", "--snapshot-digest", digest},
		{"--record-id", "D1", "--snapshot-digest", digest},
		{"--json", "--record-id", "missing", "--snapshot-digest", digest},
		{"--json", "--record-id", "D1", "--snapshot-digest", "sha256:" + strings.Repeat("0", 64)},
	}
	for _, tail := range cases {
		out, err := run(t, append([]string{"resume", "--data-root", root}, tail...)...)
		if err == nil || out != "" {
			t.Errorf("%v must fail without partial output: %q %v", tail, out, err)
		}
	}
	after, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(original, after) {
		t.Fatal("rejected lookup rewrote the bundle")
	}
}
