package seicli

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestAddRejectsBlankStatementsAndMalformedIdsWithoutChangingTheStore(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	bundle := filepath.Join(root, "semantic.bundle.json")
	before, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		name string
		args []string
		want string
	}{
		{"whitespace-only id and statement", []string{"decision", "--id", " ", "--statement", "  "}, "--id must not be empty or only whitespace"},
		{"newline in id", []string{"decision", "--id", "x\ny", "--statement", "x"}, "control character"},
		{"tab in id", []string{"decision", "--id", "x\ty", "--statement", "x"}, "control character"},
		{"leading space in id", []string{"recommendation", "--id", " R-1", "--statement", "ok"}, "must not start or end with whitespace"},
		{"trailing space in id", []string{"recommendation", "--id", "R-1 ", "--statement", "ok"}, "must not start or end with whitespace"},
		{"whitespace-only statement", []string{"decision", "--id", "D9", "--statement", "   ", "--responsible", "person:p1"}, "--statement must not be empty or only whitespace"},
		{"newline-only statement", []string{"recommendation", "--id", "R9", "--statement", "\n\t"}, "--statement must not be empty or only whitespace"},
		{"duplicate basis", []string{"decision", "--id", "D9", "--statement", "s", "--basis", "artifact:D-04", "--basis", "artifact:D-04"}, `--basis names "artifact:D-04" more than once`},
		{"duplicate responsible", []string{"decision", "--id", "D9", "--statement", "s", "--responsible", "person:a", "--responsible", "person:a"}, "--responsible names"},
		{"blank reference id", []string{"decision", "--id", "D9", "--statement", "s", "--basis", "artifact: "}, "reference id"},
		{"padded reference id", []string{"decision", "--id", "D9", "--statement", "s", "--responsible", "person: a"}, "must not start or end with whitespace"},
		{"newline in reference kind", []string{"decision", "--id", "D9", "--statement", "s", "--basis", "art\nifact:x"}, "control character"},
	}
	for _, c := range cases {
		var out, errOut bytes.Buffer
		err := Run(t.Context(), append(append([]string{"add"}, c.args[:1]...), append([]string{"--data-root", root}, c.args[1:]...)...), &out, &errOut)
		if err == nil || !strings.Contains(err.Error(), c.want) {
			t.Errorf("%s: want error containing %q, got %v", c.name, c.want, err)
		}
	}
	after, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(before, after) {
		t.Error("a rejected add must not change the store")
	}
}

func TestAddStillAcceptsMultiLineStatementsAndInteriorSpaces(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D 1/a", "--statement", "line one\nline two", "--responsible", "person:lead")
	mustRun(t, "verify", "--input", filepath.Join(root, "semantic.bundle.json"))
}

func TestMCPAddAndCLIAgreeOnWhatIsRefused(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	responses := session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":" R-1","statement":"ok"}}}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R-1","statement":"ok","basis":["artifact:A","artifact:A"]}}}`,
		`{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R-1","statement":"   "}}}`,
		`{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R-1","statement":"ok"}}}`,
	)
	for i, want := range []string{"must not start or end with whitespace", "more than once", "must not be empty"} {
		if text, isError := callText(responses[i+1]); !isError || !strings.Contains(text, want) {
			t.Errorf("response %d: want an error containing %q, got %q error=%v", i+1, want, text, isError)
		}
	}
	if text, isError := callText(responses[4]); isError {
		t.Errorf("a valid add must still succeed after refusals: %s", text)
	}
}

// A store written before these checks may hold blank or padded values. Reading
// must keep working, because the checks guard writing only.
func TestExistingStoreWithBlankAndPaddedValuesStillLoads(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D9", "--statement", "MARKER", "--responsible", "person:p1")
	path := filepath.Join(root, "semantic.bundle.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	edited := bytes.ReplaceAll(raw, []byte(`"MARKER"`), []byte(`"   "`))
	edited = bytes.ReplaceAll(edited, []byte(`"D9"`), []byte(`" D9"`))
	if bytes.Equal(raw, edited) {
		t.Fatal("test setup did not change the store")
	}
	if err := os.WriteFile(path, edited, 0o644); err != nil {
		t.Fatal(err)
	}
	mustRun(t, "verify", "--input", filepath.Join(root, "semantic.bundle.json"))
	if out := mustRun(t, "resume", "--data-root", root); !strings.Contains(out, "D9") {
		t.Errorf("resume must still show the decision:\n%s", out)
	}
}
