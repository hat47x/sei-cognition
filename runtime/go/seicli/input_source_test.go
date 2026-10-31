package seicli

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// --source と --rationale の検査(Issue #757)。検査は書き込みの入口だけで、
// Contractのschemaやloaderは変えない。

func TestAddRejectsMalformedSourceAndBlankRationaleWithoutChangingTheStore(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	bundle := filepath.Join(root, "semantic.bundle.json")
	before, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		name string
		args []string
		want string
	}{
		{"newline in source", []string{"recommendation", "--id", "R1", "--statement", "x", "--source", "a\nb"}, "--source"},
		{"whitespace-only source", []string{"decision", "--id", "D1", "--statement", "y", "--source", "  ", "--responsible", "person:p"}, "--source must not be empty or only whitespace"},
		{"padded source", []string{"recommendation", "--id", "R1", "--statement", "x", "--source", " tool"}, "must not start or end with whitespace"},
		{"tab in source", []string{"recommendation", "--id", "R1", "--statement", "x", "--source", "to\tol"}, "control character"},
		{"whitespace-only rationale", []string{"decision", "--id", "D1", "--statement", "y", "--rationale", "   ", "--responsible", "person:p"}, "--rationale must not be only whitespace"},
		{"newline-only rationale on a recommendation", []string{"recommendation", "--id", "R1", "--statement", "x", "--rationale", "\n\t"}, "--rationale must not be only whitespace"},
	}
	for _, c := range cases {
		var out, errOut bytes.Buffer
		args := append([]string{"add", c.args[0], "--data-root", root}, c.args[1:]...)
		err := Run(t.Context(), args, &out, &errOut)
		if err == nil || !strings.Contains(err.Error(), c.want) {
			t.Errorf("%s: want error containing %q, got %v", c.name, c.want, err)
		}
	}
	after, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(before, after) {
		t.Error("a rejected add must not change the store")
	}
}

func TestAddStillAcceptsMultiLineRationaleAndOrdinarySource(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s",
		"--rationale", "line one\nline two", "--source", "tool a/1", "--responsible", "person:lead")
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "s", "--rationale", "")
	mustRun(t, "verify", "--input", filepath.Join(root, "semantic.bundle.json"))
}

// 既にstoreにある空白だけ・改行入りの値は拒否せず、resume・verifyは従来どおり読める。
func TestAlreadyStoredBlankSourceAndRationaleStillLoad(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s",
		"--rationale", "placeholder", "--source", "placeholder", "--responsible", "person:p")
	path := filepath.Join(root, "semantic.bundle.json")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	edited := strings.ReplaceAll(string(data), `"rationale": "placeholder"`, `"rationale": "   "`)
	edited = strings.ReplaceAll(edited, `"id": "placeholder"`, `"id": "a\nb"`)
	if edited == string(data) {
		t.Fatalf("test setup did not edit the store: %s", data)
	}
	if err := os.WriteFile(path, []byte(edited), 0o600); err != nil {
		t.Fatal(err)
	}
	if out := mustRun(t, "verify", "--input", path); !strings.Contains(out, `"validated_count":1`) {
		t.Errorf("verify must still read a stored value: %s", out)
	}
	var view ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &view); err != nil {
		t.Fatalf("resume must still read a stored value: %v", err)
	}
}

func TestMCPAddRefusesBlankRationaleAndReplacesAnUnusableClientName(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	responses := session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R1","statement":"ok","rationale":"  "}}}`,
	)
	text, isError := callText(responses[1])
	if !isError || !strings.Contains(text, "--rationale") {
		t.Errorf("a blank rationale must be refused like the CLI: isError=%v %q", isError, text)
	}

	names := map[string]string{
		"newline and heading": `a\n## Decisions`,
		"whitespace only":     `   `,
		"padded":              ` tool `,
	}
	i := 0
	for label, name := range names {
		i++
		id := "R-name-" + string(rune('a'+i))
		init := `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"` + name + `"}}}`
		call := `{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"` + id + `","statement":"ok"}}}`
		resp := session(t, []string{"--data-root", root}, init, call)
		if text, isError := callText(resp[1]); isError {
			t.Fatalf("%s: add must still work with a replaced source: %s", label, text)
		}
	}
	out := filepath.Join(t.TempDir(), "bundle.json")
	mustRun(t, "export", "--data-root", root, "--output", out)
	data, err := os.ReadFile(out)
	if err != nil {
		t.Fatal(err)
	}
	var bundle struct {
		Records []struct {
			ProvenanceRefs []storedProvenance `json:"provenance_refs"`
		} `json:"records"`
	}
	if err := json.Unmarshal(data, &bundle); err != nil {
		t.Fatal(err)
	}
	if len(bundle.Records) != len(names) {
		t.Fatalf("records = %d, want %d (the refused add must not be stored)", len(bundle.Records), len(names))
	}
	for _, r := range bundle.Records {
		if len(r.ProvenanceRefs) != 1 || r.ProvenanceRefs[0].ID != "mcp-client" {
			t.Errorf("provenance = %+v, want the replacement mcp-client", r.ProvenanceRefs)
		}
	}
}
