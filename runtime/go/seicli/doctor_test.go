package seicli

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func findCheck(t *testing.T, checks []doctorCheck, name string) doctorCheck {
	t.Helper()
	for _, c := range checks {
		if c.Name == name {
			return c
		}
	}
	t.Fatalf("no %q check in %+v", name, checks)
	return doctorCheck{}
}

func TestDoctorOnAFreshDirectoryWarnsAndDoesNotFail(t *testing.T) {
	root := filepath.Join(t.TempDir(), "not-yet")
	checks := doctorChecks(context.Background(), root)
	if c := findCheck(t, checks, "data-root"); c.Status != "warn" || !strings.Contains(c.Detail, "sei init") {
		t.Errorf("a missing data root must be a warning that says how to create it: %+v", c)
	}
	for _, c := range checks {
		if c.Status == "fail" {
			t.Errorf("a fresh directory must not fail: %+v", c)
		}
	}
	if _, err := run(t, "doctor", "--data-root", root); err != nil {
		t.Errorf("doctor must exit 0 when there are only warnings: %v", err)
	}
	if _, err := os.Stat(root); !os.IsNotExist(err) {
		t.Error("doctor must not create the data root")
	}
}

func TestDoctorOnAHealthyStoreReportsOKAndDescribesTheMCPServer(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R1", "--statement", "s")

	checks := doctorChecks(context.Background(), root)
	if c := findCheck(t, checks, "store"); c.Status != "ok" || !strings.Contains(c.Detail, "1 records") {
		t.Errorf("a healthy store must be ok with its record count: %+v", c)
	}
	if c := findCheck(t, checks, "lock"); c.Status != "ok" {
		t.Errorf("no lock is held, so lock must be ok: %+v", c)
	}
	if c := findCheck(t, checks, "binary-hash"); c.Status != "info" || !strings.Contains(c.Detail, "sha256 ") {
		t.Errorf("the binary hash must be reported for comparison with SHA256SUMS: %+v", c)
	}
	mcp := findCheck(t, checks, "mcp")
	if !strings.Contains(mcp.Detail, `"mcpServers"`) || !strings.Contains(mcp.Detail, `"--data-root"`) {
		t.Errorf("the MCP definition must be a complete server definition: %s", mcp.Detail)
	}
	if !strings.Contains(mcp.Detail, filepath.ToSlash(root)) && !strings.Contains(mcp.Detail, root) {
		t.Errorf("the MCP definition must carry the absolute data root, not a relative one: %s", mcp.Detail)
	}
	if _, err := run(t, "doctor", "--data-root", root); err != nil {
		t.Errorf("a healthy store must pass doctor: %v", err)
	}
}

func TestDoctorWarnsOnALockAndNeverRemovesIt(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	lock := filepath.Join(root, storeLockFile)
	if err := os.WriteFile(lock, []byte("4242\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	checks := doctorChecks(context.Background(), root)
	if c := findCheck(t, checks, "lock"); c.Status != "warn" || !strings.Contains(c.Detail, "remove") {
		t.Errorf("a leftover lock must be a warning with the manual step: %+v", c)
	}
	if _, err := run(t, "doctor", "--data-root", root); err != nil {
		t.Errorf("a lock is a warning, not a failure: %v", err)
	}
	if _, err := os.Stat(lock); err != nil {
		t.Error("doctor removed the lock file; that must stay a person's decision")
	}
}

func TestDoctorFailsOnAnInvalidStore(t *testing.T) {
	root := filepath.Join(t.TempDir(), "store")
	if err := os.MkdirAll(root, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "semantic.bundle.json"), []byte(`{"contract":"wrong"}`), 0o644); err != nil {
		t.Fatal(err)
	}
	checks := doctorChecks(context.Background(), root)
	if c := findCheck(t, checks, "store"); c.Status != "fail" {
		t.Errorf("an invalid store must fail: %+v", c)
	}
	if _, err := run(t, "doctor", "--data-root", root); exitCode(err) != 1 {
		t.Errorf("an invalid store must make doctor exit 1, got %d (%v)", exitCode(err), err)
	}
}

func TestDoctorFailsWhenTheDataRootIsAFile(t *testing.T) {
	file := filepath.Join(t.TempDir(), "not-a-dir")
	if err := os.WriteFile(file, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	checks := doctorChecks(context.Background(), file)
	if c := findCheck(t, checks, "data-root"); c.Status != "fail" {
		t.Errorf("a file given as the data root must fail: %+v", c)
	}
}

func TestDoctorFailsWhenTheGateLogCannotBeAppended(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	if err := os.Mkdir(filepath.Join(root, GateLogFile), 0o755); err != nil {
		t.Fatal(err)
	}
	checks := doctorChecks(context.Background(), root)
	if c := findCheck(t, checks, "gate-log"); c.Status != "fail" {
		t.Errorf("a gate log that cannot be appended must fail, because gate checks would then be refused: %+v", c)
	}
}
