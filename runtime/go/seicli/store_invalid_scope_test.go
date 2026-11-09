package seicli

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// invalidRecordStore returns a store with one valid Decision (D1) and one
// record under a known Contract that carries a field the Contract does not
// define (#760). The Go loader rejects such a record, and the whole store with it.
func invalidRecordStore(t *testing.T) string {
	t.Helper()
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s", "--responsible", "person:lead")
	path := filepath.Join(root, "semantic.bundle.json")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var bundle map[string]any
	if err := json.Unmarshal(data, &bundle); err != nil {
		t.Fatal(err)
	}
	records := bundle["records"].([]any)
	var clone map[string]any
	cloned, _ := json.Marshal(records[0])
	_ = json.Unmarshal(cloned, &clone)
	clone["record_id"] = "V1x"
	decision := clone["payload"].(map[string]any)["decision"].(map[string]any)
	decision["future_field"] = 1
	decision["ref"].(map[string]any)["id"] = "V1x"
	bundle["records"] = append(records, clone)
	out, err := json.MarshalIndent(bundle, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, out, 0o644); err != nil {
		t.Fatal(err)
	}
	return root
}

// TestOneInvalidKnownContractRecordStopsTheWholeStore fixes today's behaviour
// so a later change to it is deliberate. It does not say the behaviour is right:
// whether it should change is an Owner decision (#760).
func TestOneInvalidKnownContractRecordStopsTheWholeStore(t *testing.T) {
	root := invalidRecordStore(t)
	bundlePath := filepath.Join(root, "semantic.bundle.json")
	before, _ := os.ReadFile(bundlePath)
	where := `record "V1x" at /records/1`

	for _, args := range [][]string{
		{"resume", "--data-root", root},
		{"add", "recommendation", "--data-root", root, "--id", "R9", "--statement", "s"},
		{"gate", "check", "--data-root", root, "--decision", "D1"},
		{"verify", "--input", bundlePath},
	} {
		out, err := run(t, args...)
		if err == nil {
			t.Errorf("%s must fail while the store holds an invalid record, got output: %s", args[0], out)
			continue
		}
		if exitCode(err) != 1 {
			t.Errorf("%s: exit code %d, want 1", args[0], exitCode(err))
		}
		if !strings.Contains(err.Error(), where) || !strings.Contains(err.Error(), "future_field") {
			t.Errorf("%s: the error must name the record, its JSON pointer and the field: %v", args[0], err)
		}
		if strings.Contains(out, "D1") {
			t.Errorf("%s: a valid record must not be shown while the store is invalid: %s", args[0], out)
		}
	}

	// A refused gate check allows nothing, and an invalid store is not logged as a check.
	if _, err := os.Stat(filepath.Join(root, GateLogFile)); err == nil {
		t.Error("a gate check on an invalid store must not write a gate log line")
	}

	var buf, errBuf bytes.Buffer
	err := Run(context.Background(), []string{"doctor", "--data-root", root}, &buf, &errBuf)
	if err == nil || !strings.Contains(buf.String(), where) {
		t.Errorf("doctor must fail and name the record: %v\n%s", err, buf.String())
	}

	// export validates by default, so it refuses an invalid store. --unchecked
	// does not interpret records and writes the raw bundle: the one way out of
	// the store that works while it is invalid.
	exported := filepath.Join(t.TempDir(), "out.json")
	if _, err := run(t, "export", "--data-root", root, "--output", exported); err == nil {
		t.Error("export without --unchecked must refuse an invalid store")
	}
	if _, err := os.Stat(exported); err == nil {
		t.Error("a refused export must not leave a file")
	}
	mustRun(t, "export", "--data-root", root, "--output", exported, "--unchecked")
	got, _ := os.ReadFile(exported)
	if !bytes.Equal(got, before) {
		t.Error("export must write the stored bytes unchanged")
	}

	after, _ := os.ReadFile(bundlePath)
	if !bytes.Equal(before, after) {
		t.Error("a refused command changed the invalid store")
	}
}
