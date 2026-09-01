package packagingprobe

import (
	"bytes"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"testing"
)

type processInspectResult struct {
	BundleID          string `json:"bundle_id"`
	RecordCount       int    `json:"record_count"`
	ValidatedCount    int    `json:"validated_count"`
	NotVerifiedCount  int    `json:"not_verified_count"`
}

func TestBuiltProbeExecutableReloadsFromNewProcess(t *testing.T) {
	temp := t.TempDir()
	binary := filepath.Join(temp, "soza-package-probe")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}

	build := exec.Command("go", "build", "-o", binary, "../cmd/soza-package-probe")
	buildOutput, err := build.CombinedOutput()
	if err != nil {
		t.Fatalf("build probe executable: %v\n%s", err, buildOutput)
	}

	fixture := filepath.Clean("../../../fixtures/contracts/v1alpha1/boundary/partial-knowledge-interchange.json")
	original, err := os.ReadFile(fixture)
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}

	dataRoot := filepath.Join(temp, "data")
	save := exec.Command(binary, "save", "--data-root", dataRoot, "--input", fixture)
	if output, err := save.CombinedOutput(); err != nil {
		t.Fatalf("save process: %v\n%s", err, output)
	}

	persisted, err := os.ReadFile(filepath.Join(dataRoot, DefaultBundleFile))
	if err != nil {
		t.Fatalf("read persisted bundle: %v", err)
	}
	if !bytes.Equal(original, persisted) {
		t.Fatal("save process changed the portable Semantic Interchange bytes")
	}

	// The save command has exited before this independent process starts. The
	// second process can therefore reconstruct the bundle only from durable
	// filesystem state, not from the first process heap.
	inspect := exec.Command(binary, "inspect", "--data-root", dataRoot)
	output, err := inspect.Output()
	if err != nil {
		t.Fatalf("inspect process: %v", err)
	}

	var result processInspectResult
	if err := json.Unmarshal(output, &result); err != nil {
		t.Fatalf("decode inspect output %q: %v", output, err)
	}
	if result.BundleID != "partial-knowledge-interchange" {
		t.Fatalf("bundle id = %q, want partial-knowledge-interchange", result.BundleID)
	}
	if result.RecordCount != 2 || result.ValidatedCount != 2 || result.NotVerifiedCount != 0 {
		t.Fatalf("unexpected inspect result: %+v", result)
	}
}

func TestBuiltProbeExecutablePreservesUnknownContractAcrossProcesses(t *testing.T) {
	temp := t.TempDir()
	binary := filepath.Join(temp, "soza-package-probe")
	if runtime.GOOS == "windows" {
		binary += ".exe"
	}

	build := exec.Command("go", "build", "-o", binary, "../cmd/soza-package-probe")
	if output, err := build.CombinedOutput(); err != nil {
		t.Fatalf("build probe executable: %v\n%s", err, output)
	}

	fixture := filepath.Clean("../../../fixtures/contracts/v1alpha1/boundary/unknown-contract-version.json")
	dataRoot := filepath.Join(temp, "data")
	if output, err := exec.Command(binary, "save", "--data-root", dataRoot, "--input", fixture).CombinedOutput(); err != nil {
		t.Fatalf("save process: %v\n%s", err, output)
	}

	output, err := exec.Command(binary, "inspect", "--data-root", dataRoot).Output()
	if err != nil {
		t.Fatalf("inspect process: %v", err)
	}
	var result processInspectResult
	if err := json.Unmarshal(output, &result); err != nil {
		t.Fatalf("decode inspect output %q: %v", output, err)
	}
	if result.BundleID != "unknown-contract-version" || result.RecordCount != 1 || result.ValidatedCount != 0 || result.NotVerifiedCount != 1 {
		t.Fatalf("unexpected inspect result: %+v", result)
	}
}
