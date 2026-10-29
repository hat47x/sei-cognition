package seicli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// editBundle rewrites semantic.bundle.json by hand, as #724's reproduction
// does: the CLI cannot make records whose envelope and payload disagree.
func editBundle(t *testing.T, root string, edit func(records []any) []any) {
	t.Helper()
	path := filepath.Join(root, "semantic.bundle.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var bundle map[string]any
	if err := json.Unmarshal(raw, &bundle); err != nil {
		t.Fatal(err)
	}
	bundle["records"] = edit(bundle["records"].([]any))
	out, err := json.Marshal(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, out, 0o644); err != nil {
		t.Fatal(err)
	}
}

func cloneRecord(t *testing.T, record any) map[string]any {
	t.Helper()
	data, err := json.Marshal(record)
	if err != nil {
		t.Fatal(err)
	}
	var clone map[string]any
	if err := json.Unmarshal(data, &clone); err != nil {
		t.Fatal(err)
	}
	return clone
}

func singleDecisionStore(t *testing.T) string {
	t.Helper()
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D-1", "--statement", "A", "--responsible", "person:alice")
	return root
}

func resumeNotices(t *testing.T, root string) []IdentityNotice {
	t.Helper()
	var view ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &view); err != nil {
		t.Fatal(err)
	}
	if view.IdentityNotices == nil {
		t.Fatal("identity_notices must be present, empty or not")
	}
	return view.IdentityNotices
}

func TestResumeHasNoIdentityNoticeForAnOrdinaryStore(t *testing.T) {
	root := singleDecisionStore(t)
	if notices := resumeNotices(t, root); len(notices) != 0 {
		t.Fatalf("an ordinary store must report no notice: %+v", notices)
	}
	if out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-1"); err != nil {
		t.Fatalf("an ordinary store must still be allowed: err=%v out=%s", err, out)
	}
}

// The issue's reproduction: X-1 has a recommendation envelope around a Decision
// payload, and D-1-dup repeats D-1's logical reference.
func reproductionStore(t *testing.T) string {
	root := singleDecisionStore(t)
	editBundle(t, root, func(records []any) []any {
		x := cloneRecord(t, records[len(records)-1])
		x["record_id"] = "X-1"
		x["kind"] = "recommendation"
		x["logical_ref"] = map[string]any{"kind": "recommendation", "id": "ZZZ"}
		dup := cloneRecord(t, records[len(records)-1])
		dup["record_id"] = "D-1-dup"
		decision := dup["payload"].(map[string]any)["decision"].(map[string]any)
		decision["statement"] = "A-dup"
		delete(decision, "responsibility_refs")
		return append(records, x, dup)
	})
	return root
}

func TestResumeNamesEnvelopePayloadMismatchAndDuplicateLogicalRef(t *testing.T) {
	root := reproductionStore(t)
	// The store is still accepted: the Contracts do not forbid these shapes.
	if out, err := run(t, "verify", "--input", filepath.Join(root, "semantic.bundle.json")); err != nil {
		t.Fatalf("verify must keep accepting the store: err=%v out=%s", err, out)
	}
	byNotice := map[string][]string{}
	for _, notice := range resumeNotices(t, root) {
		byNotice[notice.Notice] = append(byNotice[notice.Notice], strings.Join(notice.RecordIDs, ","))
	}
	if got := byNotice[NoticeEnvelopeKindMismatch]; len(got) != 1 || got[0] != "X-1" {
		t.Errorf("kind mismatch must name X-1: %+v", byNotice)
	}
	if got := byNotice[NoticeEnvelopeLogicalRefMismatch]; len(got) != 1 || got[0] != "X-1" {
		t.Errorf("logical_ref mismatch must name X-1: %+v", byNotice)
	}
	if got := byNotice[NoticeDuplicateLogicalRef]; len(got) != 1 || got[0] != "D-1,X-1,D-1-dup" {
		t.Errorf("the duplicate must name all three records: %+v", byNotice)
	}
	human := mustRun(t, "resume", "--data-root", root)
	for _, want := range []string{"Identity notices (3)", NoticeDuplicateLogicalRef, NoticeEnvelopeLogicalRefMismatch} {
		if !strings.Contains(human, want) {
			t.Errorf("human resume must show %q:\n%s", want, human)
		}
	}
}

func TestGateDeniesWhenEnvelopeAndPayloadIdentitiesDisagree(t *testing.T) {
	root := singleDecisionStore(t)
	editBundle(t, root, func(records []any) []any {
		last := records[len(records)-1].(map[string]any)
		last["logical_ref"] = map[string]any{"kind": "decision", "id": "ZZZ"}
		return records
	})
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-1")
	if exitCode(err) != ExitCodeDenied || !strings.Contains(out, "envelope and payload identities disagree") {
		t.Fatalf("the payload id must not be trusted over the envelope: err=%v out=%s", err, out)
	}
	out, err = run(t, "gate", "check", "--data-root", root, "--decision", "ZZZ")
	if exitCode(err) != ExitCodeDenied || !strings.Contains(out, "envelope logical_ref names it") {
		t.Fatalf("the envelope id must be denied with its own reason: err=%v out=%s", err, out)
	}
	out, err = run(t, "gate", "check", "--data-root", root, "--decision", "nothing")
	if exitCode(err) != ExitCodeDenied || strings.Contains(out, "envelope logical_ref names it") {
		t.Fatalf("an unrelated id keeps the plain reason: err=%v out=%s", err, out)
	}
}

func TestResumeIdentityNoticesCannotForgeASectionWithANewlineInAnID(t *testing.T) {
	root := singleDecisionStore(t)
	editBundle(t, root, func(records []any) []any {
		x := cloneRecord(t, records[len(records)-1])
		x["record_id"] = "X-1\n\nDecisions (99)"
		return append(records, x)
	})
	human := mustRun(t, "resume", "--data-root", root)
	if strings.Contains(human, "\nDecisions (99)") {
		t.Fatalf("a newline in a record id must not start a line in the notice:\n%s", human)
	}
	if !strings.Contains(human, `X-1\n\nDecisions (99)`) {
		t.Fatalf("the escaped id must still be shown:\n%s", human)
	}
}
