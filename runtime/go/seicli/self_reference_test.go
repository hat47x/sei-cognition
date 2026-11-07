package seicli

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func TestAddRejectsARecordThatNamesItselfAsBasisOrUnresolved(t *testing.T) {
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
		{"decision basis", []string{"decision", "--id", "d1", "--statement", "A", "--responsible", "person:a", "--basis", "decision:d1"}, "--basis decision:d1 names the decision being recorded"},
		{"decision unresolved", []string{"decision", "--id", "Y", "--statement", "d", "--responsible", "person:a", "--unresolved", "decision:Y"}, "--unresolved decision:Y names the decision being recorded"},
		{"recommendation basis", []string{"recommendation", "--id", "R1", "--statement", "s", "--basis", "recommendation:R1"}, "--basis recommendation:R1 names the recommendation being recorded"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			_, err := run(t, append([]string{"add", c.args[0], "--data-root", root}, c.args[1:]...)...)
			if err == nil || !strings.Contains(err.Error(), c.want) {
				t.Fatalf("want error containing %q, got %v", c.want, err)
			}
		})
	}
	after, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if string(before) != string(after) {
		t.Fatal("a rejected self-reference changed the store")
	}
}

func TestAddStillAcceptsReferencesThatOnlyShareTheIdOrTheKind(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	// Same id but a different kind, and a different id of the same kind.
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "X", "--statement", "s")
	mustRun(t, "add", "decision", "--data-root", root, "--id", "X2", "--statement", "d", "--responsible", "person:a",
		"--basis", "recommendation:X", "--basis", "decision:other", "--unresolved", "question:X2")
	mustRun(t, "add", "decision", "--data-root", root, "--id", "X3", "--statement", "d", "--responsible", "person:a",
		"--basis", "decision:X2")
}

func TestGateDoesNotReportASelfReferenceAsARecordedBasis(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "d1", "--statement", "A", "--responsible", "person:a")
	raw, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	bundle, err := semanticruntime.LoadInterchange(raw)
	if err != nil {
		t.Fatal(err)
	}
	d := bundle.Records[0].Decision.Decision
	// A store written before this check can hold a self-reference; reading it
	// must still work, and the gate must not call it a recorded basis.
	d.BasisRefs = []semanticruntime.Reference{{Kind: "decision", ID: "d1"}}
	notes := basisNotes(bundle, d)
	if len(notes) != 1 || !strings.Contains(notes[0], "names the decision itself") || strings.Contains(notes[0], "is recorded in this store") {
		t.Fatalf("self-reference basis note is wrong: %v", notes)
	}
}
