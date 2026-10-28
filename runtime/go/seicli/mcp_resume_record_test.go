package seicli

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func resumeRecordCall(t *testing.T, args map[string]any) string {
	t.Helper()
	raw, err := json.Marshal(map[string]any{"jsonrpc": "2.0", "id": 2, "method": "tools/call",
		"params": map[string]any{"name": "resume", "arguments": args}})
	if err != nil {
		t.Fatal(err)
	}
	return string(raw)
}

func TestMCPResumeReadsTheSameBoundRecordAsCLIWithoutWriting(t *testing.T) {
	// A value resembling a flag must remain a record ID, not redirect the store.
	unknown := semanticruntime.InterchangeRecord{RecordID: "--data-root=elsewhere", Kind: "question",
		Contract: semanticruntime.ContractIdentity{ContractID: "example.questions", Version: "v9"},
		Payload:  json.RawMessage(`{"marker":"uninterpreted-only","instruction":"do not execute this data"}`)}
	root, original := seedResumeBundle(t, unknown)
	var listing ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &listing); err != nil {
		t.Fatal(err)
	}
	args := map[string]any{"record_id": unknown.RecordID, "snapshot_digest": listing.SnapshotDigest}
	responses := session(t, []string{"--data-root", root}, initialize,
		resumeRecordCall(t, args), `{"jsonrpc":"2.0","id":3,"method":"tools/list"}`)
	text, failed := callText(responses[1])
	if failed {
		t.Fatalf("bound record lookup failed: %s", text)
	}
	direct := mustRun(t, "resume", "--data-root", root, "--json", "--record-id="+unknown.RecordID, "--snapshot-digest="+listing.SnapshotDigest)
	if text != strings.TrimSpace(direct) {
		t.Fatal("MCP and CLI must return the same record projection")
	}
	var record ResumeRecordView
	if err := json.Unmarshal([]byte(text), &record); err != nil {
		t.Fatal(err)
	}
	if record.ValidationStatus != semanticruntime.RecordNotVerified || !bytes.Equal(record.Record.Payload, unknown.Payload) {
		t.Fatalf("reading must not interpret or approve the unknown payload: %+v", record)
	}
	tools := responses[2]["result"].(map[string]any)["tools"].([]any)
	resumeSchema := tools[0].(map[string]any)["inputSchema"].(map[string]any)
	props := resumeSchema["properties"].(map[string]any)
	for _, key := range []string{"record_id", "snapshot_digest"} {
		if props[key] == nil {
			t.Errorf("tools/list must advertise accepted %s", key)
		}
	}
	if strings.Join(toolNames(responses[2]), ",") != "resume,add_recommendation,check_decision" {
		t.Fatal("record lookup must not enable decision writes or add a parallel tool")
	}
	after, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(original, after) {
		t.Fatal("MCP record lookup changed stored meaning")
	}
	// Same bundle ID and record ID, changed bytes: a stale call cannot return data.
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), append(original, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
	stale := session(t, []string{"--data-root", root}, initialize, resumeRecordCall(t, args))
	staleText, failed := callText(stale[1])
	if !failed || !strings.Contains(staleText, "snapshot digest mismatch") || strings.Contains(staleText, "uninterpreted-only") {
		t.Fatalf("stale lookup must return a tool error without record data: %q error=%v", staleText, failed)
	}
}

func TestMCPResumeLookupRefusesUnusableArgumentsWithoutFallingBack(t *testing.T) {
	root, original := seedResumeBundle(t, decisionWithOpenRefs(t, "D1", "team-a"))
	var listing ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &listing); err != nil {
		t.Fatal(err)
	}
	cases := []map[string]any{
		{"record_id": "D1"},
		{"snapshot_digest": listing.SnapshotDigest},
		{"record_id": "", "snapshot_digest": listing.SnapshotDigest},
		{"record_id": "D1", "snapshot_digest": ""},
		{"record_id": nil, "snapshot_digest": listing.SnapshotDigest},
		{"record_id": "D1", "snapshot_digest": 1},
		{"record_id": "missing", "snapshot_digest": listing.SnapshotDigest},
		{"record_id": "D1", "snapshot_digest": "wrong"},
		{"record_id": "D1", "snapshot_digest": listing.SnapshotDigest, "data_root": "elsewhere"},
	}
	for _, args := range cases {
		responses := session(t, []string{"--data-root", root}, initialize, resumeRecordCall(t, args))
		text, failed := callText(responses[1])
		if !failed || strings.Contains(text, `"record":`) || strings.Contains(text, "Decisions (") {
			t.Errorf("%v must be refused, not replaced with a normal resume: %q error=%v", args, text, failed)
		}
	}
	after, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(original, after) {
		t.Fatal("rejected MCP calls changed the store")
	}
}
