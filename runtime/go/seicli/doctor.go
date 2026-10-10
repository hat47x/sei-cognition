package seicli

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"

	"github.com/hat47x/sei-cognition/runtime/go/packagingprobe"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// doctorCheck is one line of `sei doctor`. Status is ok, info, warn or fail.
// Only fail makes the command exit non-zero. doctor reads the store and never
// changes it, and it never removes a lock file: that is a decision for a person.
type doctorCheck struct {
	Name   string
	Status string
	Detail string
}

// doctorChecks runs the checks for the store at dataRoot. It is split out so
// tests can read the results without parsing text.
func doctorChecks(ctx context.Context, dataRoot string) []doctorCheck {
	var out []doctorCheck
	add := func(name, status, detail string) {
		out = append(out, doctorCheck{Name: name, Status: status, Detail: detail})
	}

	add("binary", "ok", fmt.Sprintf("sei %s, commit %s, target %s", BuildVersion, BuildCommit, BuildTarget))
	exe, exeErr := os.Executable()
	if exeErr != nil {
		add("binary-path", "warn", "could not locate the running executable: "+exeErr.Error())
	} else {
		add("binary-path", "info", exe)
		if data, err := os.ReadFile(exe); err != nil {
			add("binary-hash", "warn", "could not read the executable to hash it: "+err.Error())
		} else {
			sum := sha256.Sum256(data)
			add("binary-hash", "info", "sha256 "+hex.EncodeToString(sum[:])+" (compare with SHA256SUMS from the author)")
		}
	}

	abs, err := filepath.Abs(dataRoot)
	if err != nil {
		add("data-root", "fail", err.Error())
		return out
	}
	info, statErr := os.Stat(abs)
	switch {
	case errors.Is(statErr, fs.ErrNotExist):
		add("data-root", "warn", abs+" does not exist yet; create the store with: sei init --data-root "+abs)
	case statErr != nil:
		add("data-root", "fail", statErr.Error())
	case !info.IsDir():
		add("data-root", "fail", abs+" exists but is not a directory")
	default:
		if err := checkWritable(abs); err != nil {
			add("data-root", "fail", abs+" is not writable: "+err.Error())
		} else {
			add("data-root", "ok", abs+" (writable)")
		}
		addStoreChecks(ctx, abs, add)
		addLockCheck(abs, add)
		addGateLogCheck(abs, add)
	}

	if exeErr == nil {
		add("mcp", "info", "to connect an AI tool, use this server definition in its MCP settings:\n"+mcpServerDefinition(exe, abs))
	}
	return out
}

func addStoreChecks(ctx context.Context, dir string, add func(name, status, detail string)) {
	raw, err := persistence(dir).Load(ctx)
	switch {
	case errors.Is(err, packagingprobe.ErrPackageNotFound):
		add("store", "warn", "no store yet; create it with: sei init --data-root "+dir)
		return
	case err != nil:
		add("store", "fail", err.Error())
		return
	}
	bundle, err := semanticruntime.LoadInterchange(raw)
	if err != nil {
		add("store", "fail", "the store is invalid: "+err.Error())
		return
	}
	validated, notVerified := 0, 0
	for _, rec := range bundle.Records {
		if rec.Status == semanticruntime.RecordValidated {
			validated++
		} else {
			notVerified++
		}
	}
	detail := fmt.Sprintf("%s: %d records, %d validated, %d not verified", bundle.Envelope.BundleID, len(bundle.Records), validated, notVerified)
	if notVerified > 0 {
		add("store", "warn", detail+" (records from a Contract this runtime does not understand are kept)")
		return
	}
	add("store", "ok", detail)
}

func addLockCheck(dir string, add func(name, status, detail string)) {
	path := filepath.Join(dir, storeLockFile)
	if _, err := os.Stat(path); err == nil {
		add("lock", "warn", path+" is present. If no sei process is running, remove that file by hand and retry.")
		return
	}
	add("lock", "ok", "no lock held")
}

func addGateLogCheck(dir string, add func(name, status, detail string)) {
	path := filepath.Join(dir, GateLogFile)
	info, err := os.Stat(path)
	if errors.Is(err, fs.ErrNotExist) {
		add("gate-log", "ok", "will be created on the first gate check")
		return
	}
	if err != nil {
		add("gate-log", "fail", err.Error())
		return
	}
	if info.IsDir() {
		add("gate-log", "fail", path+" is a directory, so gate checks cannot be logged")
		return
	}
	f, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0)
	if err != nil {
		add("gate-log", "fail", "cannot append to "+path+": "+err.Error())
		return
	}
	_ = f.Close()
	add("gate-log", "ok", path+" (writable)")
}

// checkWritable creates and removes a temporary file, which is the only
// reliable test of writability across platforms.
func checkWritable(dir string) error {
	f, err := os.CreateTemp(dir, ".sei-doctor-*")
	if err != nil {
		return err
	}
	name := f.Name()
	if err := f.Close(); err != nil {
		return err
	}
	return os.Remove(name)
}

// mcpServerDefinition is the JSON a client needs. Both paths are absolute, so
// the definition works from any working directory.
func mcpServerDefinition(exe, dataRoot string) string {
	def := map[string]any{
		"mcpServers": map[string]any{
			"sei": map[string]any{
				"command": exe,
				"args":    []string{"mcp", "--data-root", dataRoot},
			},
		},
	}
	data, err := json.MarshalIndent(def, "", "  ")
	if err != nil {
		return ""
	}
	return string(data)
}

func runDoctor(ctx context.Context, args []string, stdout, stderr io.Writer) error {
	f := newFlags("doctor", stderr)
	root := dataRootFlag(f)
	if err := f.Parse(args); err != nil {
		return err
	}
	checks := doctorChecks(ctx, resolveDataRoot(*root))
	failed, warned := 0, 0
	for _, c := range checks {
		fmt.Fprintf(stdout, "%-11s %-5s %s\n", c.Name, c.Status, c.Detail)
		switch c.Status {
		case "fail":
			failed++
		case "warn":
			warned++
		}
	}
	if failed > 0 {
		fmt.Fprintf(stdout, "\n%d check(s) failed, %d warning(s). Fix the failed checks and run sei doctor again.\n", failed, warned)
		return &ExitError{Code: 1, Message: fmt.Sprintf("%d check(s) failed", failed)}
	}
	fmt.Fprintf(stdout, "\nno failed checks, %d warning(s)\n", warned)
	return nil
}
