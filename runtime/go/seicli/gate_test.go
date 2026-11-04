package seicli

import (
	"bytes"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func gateStore(t *testing.T) string {
	t.Helper()
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "r")
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D-full", "--statement", "s",
		"--recommendation", "R1", "--responsible", "person:lead")
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D-open", "--statement", "s",
		"--responsible", "person:lead", "--unresolved", "question:cost")
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D-orphan", "--statement", "s")
	return root
}

func exitCode(err error) int {
	var exit *ExitError
	if errors.As(err, &exit) {
		return exit.Code
	}
	if err != nil {
		return 1
	}
	return 0
}

func TestGateAllowsADecisionThatMeetsThePolicyAndSaysWhatItDidNotVerify(t *testing.T) {
	root := gateStore(t)
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-full")
	if err != nil {
		t.Fatalf("expected allow, got %v", err)
	}
	for _, want := range []string{`"verdict":"allow"`, "holds Authority", "matches what the decision covers"} {
		if !strings.Contains(out, want) {
			t.Errorf("result missing %q: %s", want, out)
		}
	}
}

func TestGateDeniesWithADistinctExitCodeAndAReason(t *testing.T) {
	root := gateStore(t)
	cases := []struct {
		name   string
		args   []string
		reason string
	}{
		{"unknown decision", []string{"--decision", "nope"}, "no decision with this id"},
		{"no responsible party", []string{"--decision", "D-orphan"}, "no responsible party"},
		{"no recommendation when required", []string{"--decision", "D-open", "--require-recommendation"}, "no recorded recommendation"},
		{"unresolved when denied", []string{"--decision", "D-open", "--deny-unresolved"}, "unresolved"},
	}
	for _, c := range cases {
		out, err := run(t, append([]string{"gate", "check", "--data-root", root}, c.args...)...)
		if exitCode(err) != ExitCodeDenied {
			t.Errorf("%s: exit code = %d, want %d (err %v)", c.name, exitCode(err), ExitCodeDenied, err)
		}
		if !strings.Contains(out, `"verdict":"deny"`) || !strings.Contains(out, c.reason) {
			t.Errorf("%s: result lacks verdict or reason %q: %s", c.name, c.reason, out)
		}
	}
}

func TestGateTreatsUnresolvedAsAllowedByDefaultAndRecommendationAsNotRequired(t *testing.T) {
	root := gateStore(t)
	if _, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-open"); err != nil {
		t.Errorf("an unresolved question must not block by default: %v", err)
	}
}

func TestGateFailsClosedWhenTheCheckCannotBeCompleted(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "missing")
	_, err := run(t, "gate", "check", "--data-root", root, "--decision", "D1")
	if exitCode(err) != 1 {
		t.Errorf("a missing store must be an error (exit 1), not allow or deny: code=%d err=%v", exitCode(err), err)
	}
	if _, err := run(t, "gate", "check", "--data-root", root); err == nil {
		t.Error("gate check without --decision must fail")
	}
}

func TestGateLogsEveryCheckBesideTheBundleWithoutChangingIt(t *testing.T) {
	root := gateStore(t)
	bundle := filepath.Join(root, "semantic.bundle.json")
	before, _ := os.ReadFile(bundle)

	run(t, "gate", "check", "--data-root", root, "--decision", "D-full")
	run(t, "gate", "check", "--data-root", root, "--decision", "D-orphan")

	log, err := os.ReadFile(filepath.Join(root, GateLogFile))
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(strings.TrimSpace(string(log)), "\n")
	if len(lines) != 2 || !strings.Contains(lines[0], `"verdict":"allow"`) || !strings.Contains(lines[1], `"verdict":"deny"`) {
		t.Errorf("expected one allow and one deny entry in order, got:\n%s", log)
	}
	if !strings.Contains(lines[0], `"checked_at":"2026-10-06T00:00:00Z"`) {
		t.Errorf("entry lacks a check time: %s", lines[0])
	}
	after, _ := os.ReadFile(bundle)
	if !bytes.Equal(before, after) {
		t.Error("a gate check changed the semantic bundle")
	}
	exported := filepath.Join(t.TempDir(), "out.json")
	mustRun(t, "export", "--data-root", root, "--output", exported)
	data, _ := os.ReadFile(exported)
	if strings.Contains(string(data), "verdict") {
		t.Error("the operational log leaked into the exported bundle")
	}
}

func TestGateFailsClosedWhenTheCheckCannotBeLogged(t *testing.T) {
	root := gateStore(t)
	// A directory where the log file should be makes appending impossible.
	if err := os.Mkdir(filepath.Join(root, GateLogFile), 0o755); err != nil {
		t.Fatal(err)
	}
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-full")
	if exitCode(err) != 1 {
		t.Errorf("an unloggable check must not be allowed: code=%d err=%v", exitCode(err), err)
	}
	if strings.Contains(out, `"verdict":"allow"`) {
		t.Errorf("an allow verdict was printed although it could not be logged: %s", out)
	}
}

func withBuild(t *testing.T, version, commit, target string) {
	t.Helper()
	v, c, g := BuildVersion, BuildCommit, BuildTarget
	BuildVersion, BuildCommit, BuildTarget = version, commit, target
	t.Cleanup(func() { BuildVersion, BuildCommit, BuildTarget = v, c, g })
}

func TestGateResultAndLogNameTheCLIBuildThatDecided(t *testing.T) {
	withBuild(t, "v9.9.9", "abc1234", "linux/amd64")
	root := gateStore(t)
	want := `"cli":{"version":"v9.9.9","commit":"abc1234","target":"linux/amd64"}`
	for _, id := range []string{"D-full", "D-orphan", "no-such-decision"} {
		out, _ := run(t, "gate", "check", "--data-root", root, "--decision", id)
		if !strings.Contains(out, want) {
			t.Errorf("result for %s lacks the CLI build: %s", id, out)
		}
	}
	log, err := os.ReadFile(filepath.Join(root, GateLogFile))
	if err != nil {
		t.Fatal(err)
	}
	for i, line := range strings.Split(strings.TrimSpace(string(log)), "\n") {
		if !strings.Contains(line, want) {
			t.Errorf("gate log line %d lacks the CLI build: %s", i, line)
		}
	}
}

func TestGateResultStatesUnknownRatherThanOmittingTheBuild(t *testing.T) {
	withBuild(t, "dev", "unknown", "unknown")
	root := gateStore(t)
	out, _ := run(t, "gate", "check", "--data-root", root, "--decision", "D-full")
	if !strings.Contains(out, `"cli":{"version":"dev","commit":`) || !strings.Contains(out, `"target":"unknown"`) {
		t.Errorf("the cli field must be present even for an untagged build: %s", out)
	}
}

// addForeignRecord puts a record with a Contract this runtime does not know
// into the store by editing the bundle, as an externally produced bundle would.
func addForeignRecord(t *testing.T, root string) {
	t.Helper()
	path := filepath.Join(root, "semantic.bundle.json")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var bundle map[string]any
	if err := json.Unmarshal(data, &bundle); err != nil {
		t.Fatal(err)
	}
	records := bundle["records"].([]any)
	bundle["records"] = append(records, map[string]any{
		"record_id": "future-1",
		"contract":  map[string]any{"contract_id": "sei.decision-memory", "version": "v2"},
		"kind":      "decision",
		"payload":   map[string]any{"opaque": []any{1, 2, 3}},
	})
	out, err := json.MarshalIndent(bundle, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, out, 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestGateReportsUninterpretedRecordsOnAllowAndDenyAndInTheLog(t *testing.T) {
	root := gateStore(t)
	addForeignRecord(t, root)
	wantPointer := `"json_pointer":"/records/4"`

	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-full")
	if err != nil {
		t.Fatalf("an unreadable record is reported, not denied by default: %v", err)
	}
	for _, want := range []string{`"verdict":"allow"`, `"not_verified_record_count":1`, `"record_id":"future-1"`, wantPointer,
		"does not understand; they were not interpreted"} {
		if !strings.Contains(out, want) {
			t.Errorf("allow result missing %q: %s", want, out)
		}
	}

	out, err = run(t, "gate", "check", "--data-root", root, "--decision", "D-orphan")
	if exitCode(err) != ExitCodeDenied {
		t.Fatalf("expected deny, got %v", err)
	}
	for _, want := range []string{`"verdict":"deny"`, `"not_verified_record_count":1`, wantPointer} {
		if !strings.Contains(out, want) {
			t.Errorf("deny result missing %q: %s", want, out)
		}
	}

	// A decision that exists only as an unreadable record is denied, and the
	// result still says an unreadable record exists.
	out, err = run(t, "gate", "check", "--data-root", root, "--decision", "future-decision")
	if exitCode(err) != ExitCodeDenied || !strings.Contains(out, `"not_verified_record_count":1`) {
		t.Errorf("a missing decision must be denied with the unreadable record listed: %v %s", err, out)
	}

	log, err := os.ReadFile(filepath.Join(root, GateLogFile))
	if err != nil {
		t.Fatal(err)
	}
	for i, line := range strings.Split(strings.TrimSpace(string(log)), "\n") {
		if !strings.Contains(line, `"not_verified_record_count":1`) || !strings.Contains(line, wantPointer) {
			t.Errorf("gate log line %d lacks the unreadable record: %s", i, line)
		}
	}
}

func TestGateStatesThatNoRecordWasLeftOutWhenThereAreNone(t *testing.T) {
	root := gateStore(t)
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-full")
	if err != nil {
		t.Fatal(err)
	}
	for _, want := range []string{`"not_verified_record_count":0`, `"not_verified_records":[]`, "so none was left out of this verdict"} {
		if !strings.Contains(out, want) {
			t.Errorf("result missing %q: %s", want, out)
		}
	}
}
