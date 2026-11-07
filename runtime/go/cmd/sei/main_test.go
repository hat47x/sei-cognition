package main

import (
	"bytes"
	"encoding/json"
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

// 位置引数と "--" 以降は黙って捨てず、何も実行せず1で拒否する。
// 捨てると、指定したつもりの方針が落ちて、意図より緩いallowを返してしまう。
func TestExitCodeRejectsPositionalArguments(t *testing.T) {
	root := newStore(t)
	cases := []struct {
		name string
		args []string
	}{
		{"gate check after --", []string{"gate", "check", "--data-root", root, "--decision", "D-ok", "--", "--require-recommendation"}},
		{"gate check positional", []string{"gate", "check", "--data-root", root, "--decision", "D-ok", "require-recommendation"}},
		{"resume positional", []string{"resume", "--data-root", root, "extra"}},
		{"export positional", []string{"export", "--data-root", root, "--output", filepath.Join(t.TempDir(), "x.json"), "extra"}},
		{"verify positional", []string{"verify", "--input", filepath.Join(t.TempDir(), "none.json"), "extra"}},
		{"init positional", []string{"init", "--data-root", filepath.Join(t.TempDir(), "s2"), "extra"}},
		{"doctor positional", []string{"doctor", "--data-root", root, "extra"}},
		{"add positional", []string{"add", "decision", "--data-root", root, "--id", "D-x", "--statement", "s", "--responsible", "person:lead", "extra"}},
	}
	for _, c := range cases {
		stdout, stderr, code := invoke(t, c.args...)
		if code != 1 {
			t.Errorf("%s: exit code = %d, want 1 (stdout %q, stderr %q)", c.name, code, stdout, stderr)
		}
		if strings.Contains(stdout, `"verdict":"allow"`) {
			t.Errorf("%s: must never print allow: %s", c.name, stdout)
		}
		if !strings.Contains(stderr, "unexpected arguments") || !strings.Contains(stderr, "extra") && !strings.Contains(stderr, "require-recommendation") {
			t.Errorf("%s: stderr must name the leftover arguments: %q", c.name, stderr)
		}
	}
	// 拒否したaddは何も記録しない。
	if out, _, code := invoke(t, "gate", "check", "--data-root", root, "--decision", "D-x"); code != 3 || !strings.Contains(out, `"deny"`) {
		t.Errorf("rejected add must not record D-x: exit %d, %s", code, out)
	}
}

// 正しい呼び出し(--scope= の空指定を含む)は変わらない。
func TestExitCodeValidFlagsStillWork(t *testing.T) {
	root := newStore(t)
	if _, stderr, code := invoke(t, "gate", "check", "--data-root", root, "--decision", "D-ok", "--scope="); code != 0 {
		t.Errorf("--scope= : exit %d, want 0 (%s)", code, stderr)
	}
	if _, stderr, code := invoke(t, "gate", "check", "--data-root", root, "--decision=D-ok", "--require-recommendation=false"); code != 0 {
		t.Errorf("--flag=value: exit %d, want 0 (%s)", code, stderr)
	}
}

// version は、ldflagsなしのビルドでも、扱うContractの識別子と版の一覧を出す。
func TestVersionListsContractsTheRuntimeValidates(t *testing.T) {
	out, errOut, code := invoke(t, "version")
	if code != 0 {
		t.Fatalf("version: exit %d: %s", code, errOut)
	}
	var got struct {
		Version   string   `json:"version"`
		Commit    string   `json:"commit"`
		Target    string   `json:"target"`
		Contracts []string `json:"contracts"`
	}
	if err := json.Unmarshal([]byte(out), &got); err != nil {
		t.Fatalf("version output is not JSON: %v\n%s", err, out)
	}
	want := []string{
		"sei.semantic-interchange/v1alpha1",
		"sei.semantic-reference/v1alpha1",
		"sei.decision-memory/v1alpha1",
		"sei.capability-observation/v1alpha1",
		"sei.cognitive-method/v1alpha1",
	}
	if strings.Join(got.Contracts, ",") != strings.Join(want, ",") {
		t.Errorf("contracts = %v, want %v", got.Contracts, want)
	}
	if got.Version == "" || got.Commit == "" || got.Target == "" {
		t.Errorf("version, commit and target must be present: %s", out)
	}
}
