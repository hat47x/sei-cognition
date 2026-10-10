package seicli

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
)

// Concurrent adds must not lose records. Before the store lock, each add read
// the whole bundle and rewrote it, so overlapping adds dropped records while
// both reported success.
func TestConcurrentAddsKeepEveryRecord(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)

	const n = 20
	var wg sync.WaitGroup
	errs := make(chan error, n)
	for i := 0; i < n; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			if _, err := run(t, "add", "recommendation", "--data-root", root,
				"--id", fmt.Sprintf("R%02d", i), "--statement", "s"); err != nil {
				errs <- err
			}
		}(i)
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		t.Errorf("add failed under concurrency: %v", err)
	}

	raw, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	var envelope struct {
		Records []json.RawMessage `json:"records"`
	}
	if err := json.Unmarshal(raw, &envelope); err != nil {
		t.Fatal(err)
	}
	if len(envelope.Records) != n {
		t.Errorf("kept %d of %d concurrently added records", len(envelope.Records), n)
	}
	if _, err := os.Stat(filepath.Join(root, storeLockFile)); !os.IsNotExist(err) {
		t.Error("the store lock was not released")
	}
}

func TestStoreLockRefusesToWaitForever(t *testing.T) {
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	if err := os.WriteFile(filepath.Join(root, storeLockFile), []byte("999\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	original := storeLockTimeout
	storeLockTimeout = 0
	t.Cleanup(func() { storeLockTimeout = original })

	_, err := run(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "s")
	if err == nil || !strings.Contains(err.Error(), "locked by another sei process") {
		t.Errorf("a held lock must fail with a clear message, got %v", err)
	}
	// The lock belongs to another process; this command must not remove it.
	if _, statErr := os.Stat(filepath.Join(root, storeLockFile)); statErr != nil {
		t.Error("a command that timed out on the lock removed it")
	}
}

// A decision may rely only on a recommendation recorded in the store.
func TestDecisionCannotRelyOnAnUnrecordedRecommendation(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	if _, err := run(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s",
		"--responsible", "person:lead", "--recommendation", "R-ghost"); err == nil {
		t.Fatal("a decision naming an unrecorded recommendation must be refused")
	}
	if _, err := run(t, "add", "decision", "--data-root", root, "--id", "D2", "--statement", "s",
		"--recommendation", "evidence:quote-1"); err == nil {
		t.Error("--recommendation must not accept a non-recommendation kind")
	}
	if strings.Contains(mustRun(t, "resume", "--data-root", root), "[D1]") {
		t.Error("a refused decision was recorded")
	}
}

// The gate must not accept a reference to a recommendation that is not in the
// store, even when that reference came from a bundle written by hand.
func TestGateDoesNotCountAGhostRecommendationAsRelied(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	if err := os.MkdirAll(root, 0o755); err != nil {
		t.Fatal(err)
	}
	bundle := `{
  "contract": "sei.semantic-interchange/v1alpha1",
  "bundle_id": "handmade",
  "records": [
    {"record_id": "D-ghost", "contract": {"contract_id": "sei.decision-memory", "version": "v1alpha1"},
     "kind": "decision",
     "payload": {"contract": "sei.decision-memory/v1alpha1", "record_type": "decision",
       "decision": {"ref": {"kind": "decision", "id": "D-ghost"}, "statement": "s",
         "responsibility_refs": [{"kind": "person", "id": "lead"}],
         "recommendation_refs": [{"kind": "recommendation", "id": "R-ghost"}]}}}
  ]
}`
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), []byte(bundle), 0o644); err != nil {
		t.Fatal(err)
	}
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-ghost", "--require-recommendation")
	if exitCode(err) != ExitCodeDenied || !strings.Contains(out, `"verdict":"deny"`) {
		t.Errorf("a decision relying only on an unrecorded recommendation must be denied: code=%d out=%s", exitCode(err), out)
	}
}

// export never replaces a file. Replacing another store's bundle or the gate log
// would silently destroy recorded work.
func TestExportRefusesToOverwriteAnyFile(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "s")

	target := filepath.Join(t.TempDir(), "keep.json")
	if err := os.WriteFile(target, []byte("other store"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := run(t, "export", "--data-root", root, "--output", target); err == nil {
		t.Fatal("export over an existing file must be refused")
	}
	if got, _ := os.ReadFile(target); string(got) != "other store" {
		t.Errorf("export changed an existing file: %q", got)
	}
	bundle := filepath.Join(root, "semantic.bundle.json")
	if _, err := run(t, "export", "--data-root", root, "--output", bundle); err == nil {
		t.Error("export must not replace the store's own bundle")
	}
	fresh := filepath.Join(t.TempDir(), "fresh.json")
	mustRun(t, "export", "--data-root", root, "--output", fresh)
	if _, err := os.Stat(fresh); err != nil {
		t.Errorf("export to a new name must work: %v", err)
	}
}

// An empty resume projection is an empty list, not null, in --json output.
func TestResumeJSONUsesEmptyArraysNotNull(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	out := mustRun(t, "resume", "--data-root", root, "--json")
	for _, key := range []string{`"decisions":[]`, `"recommendations_not_yet_relied_on":[]`, `"recommendations_relied_on":[]`, `"unresolved":[]`} {
		if !strings.Contains(out, key) {
			t.Errorf("resume --json lacks %s: %s", key, out)
		}
	}
}

// An argument the server cannot act on is refused with an error result. It is
// never dropped, because a dropped policy flag turns a check into an allow.
func TestMCPRefusesArgumentsItCannotActOn(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s",
		"--responsible", "person:lead", "--unresolved", "question:cost")

	calls := []string{
		// A string "true" is not the boolean true; it must not turn the policy off.
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D1","deny_unresolved":"true"}}}`,
		// A misspelled policy flag must not be silently ignored.
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D1","deny_unresolvd":true}}}`,
		// Unresolved given as a bare string is not a list; it must not vanish.
		`{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D2","statement":"s","responsible":["person:lead"],"unresolved":"question:cost"}}}`,
		// An empty responsible value must not pass as a named party.
		`{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D3","statement":"s","responsible":[""]}}}`,
		// The caller cannot choose the provenance.
		`{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R1","statement":"s","source":"someone-else"}}}`,
	}
	responses := session(t, []string{"--data-root", root, "--allow-decision"}, append([]string{initialize}, calls...)...)
	for i := 1; i < len(responses); i++ {
		text, isError := callText(responses[i])
		if !isError {
			t.Errorf("call %d must be refused with an error result, got %q", i, text)
		}
	}
	if strings.Contains(mustRun(t, "resume", "--data-root", root), "[D2]") {
		t.Error("a decision with a malformed unresolved argument was recorded")
	}
	if strings.Contains(mustRun(t, "resume", "--data-root", root), "someone-else") {
		t.Error("the caller chose the provenance")
	}
}

func TestMCPProvenanceIsTheConnectedClientName(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	responses := session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R1","statement":"s"}}}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"resume","arguments":{}}}`,
	)
	if text, isError := callText(responses[1]); isError {
		t.Fatalf("add failed: %s", text)
	}
	text, _ := callText(responses[2])
	if !strings.Contains(text, "(from assistant-x)") {
		t.Errorf("provenance must be the client name from initialize:\n%s", text)
	}
}
