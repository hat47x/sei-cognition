package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestResolveSourceGitSHAUsesCurrentHead(t *testing.T) {
	repo, head := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	got, err := resolveSourceGitSHA("")
	if err != nil {
		t.Fatal(err)
	}
	if got != head {
		t.Fatalf("resolved SHA=%s want=%s", got, head)
	}
}

func TestResolveSourceGitSHAAcceptsMatchingExpectedHead(t *testing.T) {
	repo, head := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	got, err := resolveSourceGitSHA(head)
	if err != nil {
		t.Fatal(err)
	}
	if got != head {
		t.Fatalf("resolved SHA=%s want=%s", got, head)
	}
}

func TestResolveSourceGitSHARejectsMismatch(t *testing.T) {
	repo, _ := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	_, err := resolveSourceGitSHA("0123456789abcdef0123456789abcdef01234567")
	if err == nil {
		t.Fatal("expected source Git SHA mismatch")
	}
	if !strings.Contains(err.Error(), "source Git SHA mismatch") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func createTempGitRepo(t *testing.T) (string, string) {
	t.Helper()
	repo := t.TempDir()
	runGit(t, repo, "init", "-q")
	runGit(t, repo, "config", "user.name", "SEI Test")
	runGit(t, repo, "config", "user.email", "sei-test@example.invalid")
	if err := os.WriteFile(filepath.Join(repo, "fixture.txt"), []byte("fixture\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	runGit(t, repo, "add", "fixture.txt")
	runGit(t, repo, "commit", "-q", "-m", "test fixture")
	head := strings.TrimSpace(runGit(t, repo, "rev-parse", "HEAD"))
	if len(head) != 40 {
		t.Fatalf("unexpected test HEAD: %q", head)
	}
	return repo, head
}

func runGit(t *testing.T, repo string, args ...string) string {
	t.Helper()
	commandArgs := append([]string{"-C", repo}, args...)
	output, err := exec.Command("git", commandArgs...).CombinedOutput()
	if err != nil {
		t.Fatalf("git %v: %v\n%s", args, err, output)
	}
	return string(output)
}

func withWorkingDirectory(t *testing.T, dir string) {
	t.Helper()
	previous, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	if err := os.Chdir(dir); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		_ = os.Chdir(previous)
	})
}


func TestResolveSourceGitSHARejectsDirtyTrackedFile(t *testing.T) {
	repo, head := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	if err := os.WriteFile(filepath.Join(repo, "fixture.txt"), []byte("dirty\n"), 0o600); err != nil {
		t.Fatal(err)
	}

	_, err := resolveSourceGitSHA(head)
	if err == nil {
		t.Fatal("expected dirty working tree rejection")
	}
	if !strings.Contains(err.Error(), "working tree is not clean") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestResolveSourceGitSHARejectsStagedChange(t *testing.T) {
	repo, head := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	if err := os.WriteFile(filepath.Join(repo, "fixture.txt"), []byte("staged\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	runGit(t, repo, "add", "fixture.txt")

	_, err := resolveSourceGitSHA(head)
	if err == nil {
		t.Fatal("expected staged working tree rejection")
	}
	if !strings.Contains(err.Error(), "working tree is not clean") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestResolveSourceGitSHARejectsUntrackedFile(t *testing.T) {
	repo, head := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	if err := os.WriteFile(filepath.Join(repo, "untracked.go"), []byte("package ignored\n"), 0o600); err != nil {
		t.Fatal(err)
	}

	_, err := resolveSourceGitSHA(head)
	if err == nil {
		t.Fatal("expected untracked working tree rejection")
	}
	if !strings.Contains(err.Error(), "working tree is not clean") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestResolveSourceGitSHAAllowsIgnoredFile(t *testing.T) {
	repo, head := createTempGitRepo(t)
	withWorkingDirectory(t, repo)

	if err := os.WriteFile(filepath.Join(repo, ".gitignore"), []byte("ignored.tmp\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	runGit(t, repo, "add", ".gitignore")
	runGit(t, repo, "commit", "-q", "-m", "ignore test artifact")
	head = strings.TrimSpace(runGit(t, repo, "rev-parse", "HEAD"))

	if err := os.WriteFile(filepath.Join(repo, "ignored.tmp"), []byte("generated\n"), 0o600); err != nil {
		t.Fatal(err)
	}

	got, err := resolveSourceGitSHA(head)
	if err != nil {
		t.Fatal(err)
	}
	if got != head {
		t.Fatalf("resolved SHA=%s want=%s", got, head)
	}
}
