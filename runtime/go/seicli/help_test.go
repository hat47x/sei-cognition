package seicli

import (
	"bytes"
	"context"
	"strings"
	"testing"
)

// 全サブコマンドの -h / --help は、使い方を標準出力へ出して成功で終わる(Issue #753)。
func TestSubcommandHelpExitsZeroOnStdout(t *testing.T) {
	cases := [][]string{
		{"init"},
		{"add"},
		{"add", "recommendation"},
		{"add", "decision"},
		{"resume"},
		{"verify"},
		{"export"},
		{"doctor"},
		{"gate"},
		{"gate", "check"},
		{"mcp"},
	}
	for _, base := range cases {
		for _, flagName := range []string{"-h", "--help"} {
			args := append(append([]string{}, base...), flagName)
			var out, errOut bytes.Buffer
			err := Run(context.Background(), args, &out, &errOut)
			name := strings.Join(args, " ")
			if err != nil {
				t.Errorf("sei %s: want success, got %v", name, err)
			}
			if !strings.Contains(out.String(), "sei") && !strings.Contains(out.String(), "Usage of") {
				t.Errorf("sei %s: usage not on stdout: %q", name, out.String())
			}
			if errOut.Len() != 0 {
				t.Errorf("sei %s: stderr must be empty, got %q", name, errOut.String())
			}
		}
	}
}

// 未知のフラグは従来どおり失敗し、メッセージは標準エラーに出る。
func TestSubcommandUnknownFlagStillFailsOnStderr(t *testing.T) {
	for _, args := range [][]string{{"init", "--nope"}, {"resume", "--nope"}, {"gate", "check", "--nope"}} {
		var out, errOut bytes.Buffer
		err := Run(context.Background(), args, &out, &errOut)
		if err == nil {
			t.Errorf("sei %s: want error", strings.Join(args, " "))
		}
		if out.Len() != 0 {
			t.Errorf("sei %s: stdout must be empty, got %q", strings.Join(args, " "), out.String())
		}
		if !strings.Contains(errOut.String(), "nope") {
			t.Errorf("sei %s: stderr should name the flag, got %q", strings.Join(args, " "), errOut.String())
		}
	}
}
