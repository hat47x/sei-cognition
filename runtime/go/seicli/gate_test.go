package seicli

import (
	"bytes"
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
