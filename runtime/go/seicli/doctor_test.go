package seicli

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
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
	// The definition is JSON, so a Windows path appears with doubled backslashes.
	escapedRoot := strings.ReplaceAll(root, `\`, `\\`)
	if !strings.Contains(mcp.Detail, filepath.ToSlash(root)) && !strings.Contains(mcp.Detail, root) && !strings.Contains(mcp.Detail, escapedRoot) {
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

func TestDoctorWarnsWhenTheBinaryCarriesNoCommit(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	withBuild(t, "dev", "unknown", "unknown")
	// A test binary carries no VCS revision, so the commit stays unknown.
	if c := findCheck(t, doctorChecks(context.Background(), root), "binary-identity"); c.Status != "warn" {
		t.Errorf("an untraceable binary must be warned about: %+v", c)
	}
	withBuild(t, "v1", "abc1234", "linux/amd64")
	for _, c := range doctorChecks(context.Background(), root) {
		if c.Name == "binary-identity" {
			t.Errorf("a binary with a commit must not be warned about: %+v", c)
		}
	}
}

func TestDoctorWarnsWhenTheBinaryWasBuiltFromADirtyTree(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	withBuild(t, "dev", "e8d13e09d475ff62c770dd539bb51cde9e6da3a8+dirty", "linux/amd64")
	checks := doctorChecks(context.Background(), root)
	if c := findCheck(t, checks, "binary-dirty"); c.Status != "warn" {
		t.Errorf("a dirty build must be warned about: %+v", c)
	}
	for _, c := range checks {
		if c.Name == "binary-identity" {
			t.Errorf("a dirty build still carries a commit, so it is not the unknown case: %+v", c)
		}
	}
	withBuild(t, "dev", "e8d13e09d475ff62c770dd539bb51cde9e6da3a8", "linux/amd64")
	for _, c := range doctorChecks(context.Background(), root) {
		if c.Name == "binary-dirty" {
			t.Errorf("a clean build must not be warned about: %+v", c)
		}
	}
}

func TestDoctorNamesTheContractsTheRuntimeValidates(t *testing.T) {
	checks := doctorChecks(context.Background(), filepath.Join(t.TempDir(), "not-yet"))
	c := findCheck(t, checks, "contracts")
	if c.Status != "info" {
		t.Fatalf("contracts check must be informational: %+v", c)
	}
	for _, id := range semanticruntime.KnownContracts() {
		if !strings.Contains(c.Detail, id) {
			t.Errorf("doctor does not list %s: %s", id, c.Detail)
		}
	}
}

func TestVersionCommandListsContracts(t *testing.T) {
	withBuild(t, "v9.9.9", "abc1234", "linux/amd64")
	out, err := run(t, "version")
	if err != nil {
		t.Fatal(err)
	}
	for _, want := range []string{`"version":"v9.9.9"`, `"commit":"abc1234"`, `"contracts":[`, `"sei.decision-memory/v1alpha1"`} {
		if !strings.Contains(out, want) {
			t.Errorf("version output lacks %s: %s", want, out)
		}
	}
}
