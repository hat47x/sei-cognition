package seicli

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
)

// QUICKSTARTが案内するコマンド名が、`sei --help`の一覧に実在することを確かめる。
// 存在しない`sei check`を案内していた誤記(Issue #749)の再発を防ぐ。
func TestQuickstartCommandsExistInHelp(t *testing.T) {
	help, err := run(t, "--help")
	if err != nil {
		t.Fatal(err)
	}
	commands := map[string]bool{}
	inList := false
	for _, line := range strings.Split(help, "\n") {
		if strings.HasPrefix(line, "commands:") {
			inList = true
			continue
		}
		if inList {
			fields := strings.Fields(line)
			if len(fields) == 0 {
				break
			}
			commands[fields[0]] = true
		}
	}
	if len(commands) == 0 {
		t.Fatal("no commands parsed from usage")
	}

	body, err := os.ReadFile(filepath.Join("..", "cmd", "sei", "QUICKSTART.md"))
	if err != nil {
		t.Fatal(err)
	}
	re := regexp.MustCompile(`\bsei ([a-z][a-z-]*)`)
	matches := re.FindAllStringSubmatch(string(body), -1)
	if len(matches) == 0 {
		t.Fatal("no `sei <command>` found in QUICKSTART.md")
	}
	for _, m := range matches {
		if !commands[m[1]] {
			t.Errorf("QUICKSTART.md mentions `sei %s`, which is not in `sei --help`", m[1])
		}
	}
	// gateの下位コマンドはcheckだけである。
	gateRe := regexp.MustCompile(`\bsei gate ([a-z][a-z-]*)`)
	for _, m := range gateRe.FindAllStringSubmatch(string(body), -1) {
		if m[1] != "check" {
			t.Errorf("QUICKSTART.md mentions `sei gate %s`, but only `sei gate check` exists", m[1])
		}
	}
}
