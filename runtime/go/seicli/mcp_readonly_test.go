package seicli

import (
	"bytes"
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestMCPReadOnlyOffersOnlyResumeAndRefusesEveryWritingTool(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s", "--responsible", "person:lead")
	bundle := filepath.Join(root, "semantic.bundle.json")
	before, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}

	responses := session(t, []string{"--data-root", root, "--read-only"},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/list"}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"resume","arguments":{}}}`,
		`{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R1","statement":"s"}}}`,
		`{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D2","statement":"s","responsible":["person:lead"]}}}`,
		`{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D1"}}}`,
	)
	if got := strings.Join(toolNames(responses[1]), ","); got != "resume" {
		t.Errorf("tools with --read-only = %q, want only resume", got)
	}
	if text, isError := callText(responses[2]); isError || !strings.Contains(text, "[D1]") {
		t.Errorf("resume must still work read-only: %v %s", isError, text)
	}
	for i, name := range []string{"add_recommendation", "add_decision", "check_decision"} {
		text, isError := callText(responses[3+i])
		if !isError || !strings.Contains(text, "not enabled") {
			t.Errorf("%s must be refused on a read-only server: %v %q", name, isError, text)
		}
	}
	after, _ := os.ReadFile(bundle)
	if !bytes.Equal(before, after) {
		t.Error("a read-only server changed the store")
	}
	if _, err := os.Stat(filepath.Join(root, GateLogFile)); err == nil {
		t.Error("a read-only server wrote gate-checks.jsonl")
	}
}

func TestMCPReadOnlyAndAllowDecisionCannotBeCombined(t *testing.T) {
	var out, errOut bytes.Buffer
	err := Run(context.Background(), []string{"mcp", "--data-root", t.TempDir(), "--read-only", "--allow-decision"}, &out, &errOut)
	if err == nil || !strings.Contains(err.Error(), "contradict") {
		t.Errorf("contradictory flags must be rejected, got %v", err)
	}
}
