package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

// seiBinary は TestMain が一度だけビルドした sei の実行ファイル。
var seiBinary string

func TestMain(m *testing.M) {
	os.Exit(runWithBinary(m))
}

func runWithBinary(m *testing.M) int {
	dir, err := os.MkdirTemp("", "sei-bin-")
	if err != nil {
		fmt.Fprintln(os.Stderr, "mkdir temp:", err)
		return 2
	}
	defer os.RemoveAll(dir)
	name := "sei"
	if runtime.GOOS == "windows" {
		name = "sei.exe"
	}
	seiBinary = filepath.Join(dir, name)
	build := exec.Command("go", "build", "-o", seiBinary, ".")
	if out, err := build.CombinedOutput(); err != nil {
		fmt.Fprintf(os.Stderr, "go build failed: %v\n%s", err, out)
		return 2
	}
	return m.Run()
}

// invoke は sei を実際のプロセスとして起動し、標準出力・標準エラー・終了コードを返す。
// 環境変数 SEI_DATA_ROOT は外し、呼び出し側が渡す --data-root 以外のstoreを触らせない。
func invoke(t *testing.T, args ...string) (stdout, stderr string, code int) {
	t.Helper()
	cmd := exec.Command(seiBinary, args...)
	cmd.Dir = t.TempDir()
	env := []string{}
	for _, kv := range os.Environ() {
		if !strings.HasPrefix(kv, "SEI_DATA_ROOT=") {
			env = append(env, kv)
		}
	}
	cmd.Env = env
	var out, errOut bytes.Buffer
	cmd.Stdout, cmd.Stderr = &out, &errOut
	err := cmd.Run()
	if err == nil {
		return out.String(), errOut.String(), 0
	}
	exit, ok := err.(*exec.ExitError)
	if !ok {
		t.Fatalf("sei %s: could not run: %v", strings.Join(args, " "), err)
	}
	return out.String(), errOut.String(), exit.ExitCode()
}

func newStore(t *testing.T) string {
	t.Helper()
	root := filepath.Join(t.TempDir(), "store")
	if _, errOut, code := invoke(t, "init", "--data-root", root); code != 0 {
		t.Fatalf("init: exit %d: %s", code, errOut)
	}
	if _, errOut, code := invoke(t, "add", "decision", "--data-root", root, "--id", "D-ok",
		"--statement", "s", "--responsible", "person:lead"); code != 0 {
		t.Fatalf("add decision: exit %d: %s", code, errOut)
	}
	return root
}

// 許可=0。呼び出し側は 0 のときだけ進む。
func TestExitCodeAllowIsZero(t *testing.T) {
	root := newStore(t)
	stdout, _, code := invoke(t, "gate", "check", "--data-root", root, "--decision", "D-ok")
	if code != 0 {
		t.Fatalf("exit code = %d, want 0", code)
	}
	if !strings.Contains(stdout, `"verdict":"allow"`) {
		t.Errorf("stdout lacks the allow verdict: %s", stdout)
	}
}

// 拒否=3。判定結果は標準出力に、理由は標準エラーに出る。
func TestExitCodeDenyIsThree(t *testing.T) {
	root := newStore(t)
	stdout, stderr, code := invoke(t, "gate", "check", "--data-root", root, "--decision", "nope")
	if code != 3 {
		t.Fatalf("exit code = %d, want 3 (stderr %q)", code, stderr)
	}
	if !strings.Contains(stdout, `"verdict":"deny"`) {
		t.Errorf("stdout lacks the deny verdict: %s", stdout)
	}
	if !strings.Contains(stderr, "denied") {
		t.Errorf("stderr should say denied: %q", stderr)
	}
}

// 確認不能=1。storeなし・不正store・未知のサブコマンド・引数誤りはどれも1で、0にも3にもならない。
func TestExitCodeCannotVerifyIsOne(t *testing.T) {
	broken := filepath.Join(t.TempDir(), "broken")
	if err := os.MkdirAll(broken, 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(broken, "semantic.bundle.json"), []byte("not json"), 0o600); err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		name string
		args []string
	}{
		{"missing store", []string{"gate", "check", "--data-root", filepath.Join(t.TempDir(), "absent"), "--decision", "D-ok"}},
		{"invalid store", []string{"gate", "check", "--data-root", broken, "--decision", "D-ok"}},
		{"unknown subcommand", []string{"frobnicate"}},
		{"no subcommand", nil},
		{"gate check without --decision", []string{"gate", "check"}},
		{"unknown flag", []string{"resume", "--nope"}},
	}
	for _, c := range cases {
		stdout, stderr, code := invoke(t, c.args...)
		if code != 1 {
			t.Errorf("%s: exit code = %d, want 1 (stdout %q, stderr %q)", c.name, code, stdout, stderr)
		}
		if strings.Contains(stdout, `"verdict":"allow"`) {
			t.Errorf("%s: must never print allow: %s", c.name, stdout)
		}
		if stderr == "" {
			t.Errorf("%s: the error must be explained on stderr", c.name)
		}
	}
}

// --help は 0 で、使い方を標準出力へ出す。エラー文言は標準エラーに出て、標準出力には出ない。
func TestHelpIsZeroOnStdoutAndErrorsGoToStderr(t *testing.T) {
	for _, args := range [][]string{{"--help"}, {"gate", "check", "--help"}} {
		stdout, stderr, code := invoke(t, args...)
		if code != 0 || !strings.Contains(stdout, "sei") || stderr != "" {
			t.Errorf("sei %s: code=%d stdout=%q stderr=%q", strings.Join(args, " "), code, stdout, stderr)
		}
	}
	stdout, stderr, code := invoke(t, "frobnicate")
	if code == 0 || stdout != "" || !strings.Contains(stderr, "frobnicate") {
		t.Errorf("unknown subcommand: code=%d stdout=%q stderr=%q", code, stdout, stderr)
	}
}
