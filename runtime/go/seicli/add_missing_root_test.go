package seicli

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// `sei add` against a data root that does not exist must fail with "no store
// found" and leave nothing behind: no directory and no store.lock. Only
// `sei init` creates the data root.
func TestAddToAMissingDataRootCreatesNothing(t *testing.T) {
	fixClock(t)
	base := t.TempDir()
	root := filepath.Join(base, "deep", "x")

	for _, kind := range []string{"recommendation", "decision"} {
		_, err := run(t, "add", kind, "--data-root", root, "--id", "a", "--statement", "b",
			"--responsible", "person:lead")
		if err == nil || !strings.Contains(err.Error(), "no store found") {
			t.Fatalf("add %s to a missing root: err = %v, want \"no store found\"", kind, err)
		}
	}
	entries, err := os.ReadDir(base)
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 0 {
		t.Errorf("a failed add left %d entries under %s", len(entries), base)
	}
}

// The same holds when the store is reached through `sei mcp`, whose data root
// is fixed at startup.
func TestMCPAddToAMissingDataRootCreatesNothing(t *testing.T) {
	fixClock(t)
	base := t.TempDir()
	root := filepath.Join(base, "deep", "x")

	responses := session(t, []string{"--data-root", root, "--allow-decision"},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R1","statement":"s"}}}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D1","statement":"s","responsible":["person:lead"]}}}`,
	)
	for i, resp := range responses[1:] {
		text, isError := callText(resp)
		if !isError || !strings.Contains(text, "no store found") {
			t.Errorf("call %d: want a \"no store found\" tool error, got isError=%v %q", i+1, isError, text)
		}
	}
	entries, err := os.ReadDir(base)
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 0 {
		t.Errorf("a failed MCP add left %d entries under %s", len(entries), base)
	}
}
