package seicli

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func fixClock(t *testing.T) {
	t.Helper()
	original := Now
	Now = func() time.Time { return time.Date(2026, 10, 6, 0, 0, 0, 0, time.UTC) }
	t.Cleanup(func() { Now = original })
}

func run(t *testing.T, args ...string) (string, error) {
	t.Helper()
	var out, errOut bytes.Buffer
	err := Run(context.Background(), args, &out, &errOut)
	return out.String(), err
}

func mustRun(t *testing.T, args ...string) string {
	t.Helper()
	out, err := run(t, args...)
	if err != nil {
		t.Fatalf("sei %s: %v", strings.Join(args, " "), err)
	}
	return out
}

func TestFirstDecisionIsRecordedResumedAndVerifiedWithoutTheStore(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R-vendor-a",
		"--statement", "Choose vendor A.", "--source", "tool-a", "--basis", "evidence:quote-1")
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R-vendor-b",
		"--statement", "Choose vendor B.", "--source", "tool-b")
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D-vendor",
		"--statement", "Adopt vendor A for one year.", "--recommendation", "R-vendor-a",
		"--unresolved", "question:exit-cost", "--responsible", "person:team-lead")

	text := mustRun(t, "resume", "--data-root", root)
	for _, want := range []string{
		"[D-vendor] Adopt vendor A for one year.",
		"relied on: recommendation:R-vendor-a",
		"question:exit-cost (left open by D-vendor)",
		"[R-vendor-b] Choose vendor B. (from tool-b)",
	} {
		if !strings.Contains(text, want) {
			t.Errorf("resume output missing %q:\n%s", want, text)
		}
	}

	var view ResumeView
	if err := json.Unmarshal([]byte(mustRun(t, "resume", "--data-root", root, "--json")), &view); err != nil {
		t.Fatal(err)
	}
	if len(view.RecommendationsOpen) != 1 || view.RecommendationsOpen[0].ID != "R-vendor-b" {
		t.Errorf("a recommendation no decision relies on must stay open, got %+v", view.RecommendationsOpen)
	}
	if len(view.RecommendationsRelied) != 1 || view.RecommendationsRelied[0].ID != "R-vendor-a" {
		t.Errorf("relied recommendation misreported: %+v", view.RecommendationsRelied)
	}

	bundleFile := filepath.Join(t.TempDir(), "out.json")
	mustRun(t, "export", "--data-root", root, "--output", bundleFile)
	verified := mustRun(t, "verify", "--input", bundleFile)
	if !strings.Contains(verified, `"record_count":3`) || !strings.Contains(verified, `"validated_count":3`) {
		t.Errorf("unexpected verify result: %s", verified)
	}
}

func TestRecordedWorkIsNeverOverwritten(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "first")
	before, _ := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))

	if _, err := run(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "changed"); err == nil {
		t.Fatal("adding a duplicate id must fail")
	}
	if _, err := run(t, "init", "--data-root", root); err == nil {
		t.Fatal("init on an existing store must fail")
	}
	after, _ := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if !bytes.Equal(before, after) {
		t.Error("a rejected command changed the store")
	}
}

func TestAppendKeepsExistingRecordsAndUnknownContractsUntouched(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	seed := `{
  "contract": "sei.semantic-interchange/v1alpha1",
  "bundle_id": "imported",
  "records": [
    {"record_id": "foreign", "contract": {"contract_id": "example.future", "version": "v9"}, "kind": "x", "payload": {"opaque": [1, 2, 3]}}
  ]
}`
	if err := os.MkdirAll(root, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), []byte(seed), 0o644); err != nil {
		t.Fatal(err)
	}
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "s")

	data, _ := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if !strings.Contains(string(data), `"opaque"`) {
		t.Error("an unknown-contract record was dropped")
	}
	text := mustRun(t, "resume", "--data-root", root)
	if !strings.Contains(text, "1 record(s) use a Contract this runtime does not understand") {
		t.Errorf("unknown records must be reported as not verified:\n%s", text)
	}
}

func TestInvalidInputIsRejectedWithoutWriting(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	if _, err := run(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "s"); err == nil {
		t.Error("add before init must fail")
	}
	mustRun(t, "init", "--data-root", root)
	cases := [][]string{
		{"add", "recommendation", "--data-root", root, "--statement", "no id"},
		{"add", "recommendation", "--data-root", root, "--id", "R2", "--statement", "s", "--basis", "malformed"},
		{"add", "note", "--data-root", root},
	}
	for _, args := range cases {
		if _, err := run(t, args...); err == nil {
			t.Errorf("expected failure for %v", args)
		}
	}
	text := mustRun(t, "resume", "--data-root", root)
	if !strings.Contains(text, "0 records") {
		t.Errorf("rejected input must not be recorded:\n%s", text)
	}
}

func TestVerifyRejectsAnInvalidBundle(t *testing.T) {
	bad := filepath.Join(t.TempDir(), "bad.json")
	if err := os.WriteFile(bad, []byte(`{"contract":"wrong"}`), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := run(t, "verify", "--input", bad); err == nil {
		t.Error("an invalid bundle must not verify")
	}
}
