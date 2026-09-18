package teiprobe

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
	"github.com/hat47x/sei-cognition/runtime/go/teiintegration"
)

func requirePOSIXShell(t *testing.T) {
	t.Helper()
	if runtime.GOOS == "windows" {
		t.Skip("fixture-scoped executable script requires a POSIX shell")
	}
}

func writeExecutable(t *testing.T, body string) string {
	t.Helper()
	requirePOSIXShell(t)
	path := filepath.Join(t.TempDir(), "tei-fixture")
	if err := os.WriteFile(path, []byte("#!/bin/sh\nset -eu\n"+body+"\n"), 0o700); err != nil {
		t.Fatalf("write executable: %v", err)
	}
	return path
}

func fixtureRequest(binary string) Request {
	return Request{
		BinaryPath:         binary,
		DeclaredRepository: "hat47x/tei-platform",
		DeclaredCommit:     "0123456789abcdef0123456789abcdef01234567",
		ProviderPlan: teiintegration.ProviderPlanRequest{
			Workspace:  "/fixture/workspace",
			Run:        "/fixture/run.json",
			Solution:   "order_rollout",
			Version:    "2026.9.18",
			PluginLock: "/fixture/plugin-lock.json",
		},
		ObservationContext: provideradapter.ObservationContext{
			ObservationID: "obs-e3b-probe",
			CapabilityRef: semanticruntime.LogicalReference{
				Kind: "capability",
				ID:   "deployment-provider-routing",
			},
			ObservedAt:     "2026-09-18T00:00:00Z",
			SourceStateRef: "caller-provided-value-must-not-survive",
		},
	}
}

func successScript() string {
	return `printf '%s\n' '{"observations":[{"kind":"deployment","provider":"fixture"}]}'`
}

func writeManifest(t *testing.T, request Request, digest string) string {
	t.Helper()
	manifest := BuildManifest{
		Schema:       ManifestSchema,
		Repository:   request.DeclaredRepository,
		Commit:       request.DeclaredCommit,
		BinarySHA256: digest,
	}
	payload, err := json.Marshal(manifest)
	if err != nil {
		t.Fatalf("marshal manifest: %v", err)
	}
	path := filepath.Join(t.TempDir(), "manifest.json")
	if err := os.WriteFile(path, payload, 0o600); err != nil {
		t.Fatalf("write manifest: %v", err)
	}
	return path
}

func TestProbeWithoutManifestRecordsUnverifiedBinding(t *testing.T) {
	binary := writeExecutable(t, successScript())
	request := fixtureRequest(binary)

	report, err := Probe(context.Background(), request)
	if err != nil {
		t.Fatalf("Probe() error = %v", err)
	}
	if report.Schema != ReportSchema || report.Result != "pass" {
		t.Fatalf("unexpected report identity: %#v", report)
	}
	if report.SourceBinding != SourceBindingNotVerified || report.ManifestProvided {
		t.Fatalf("unexpected source binding: %#v", report)
	}
	if report.Binary.SHA256 == "" || report.Binary.DigestStability != BinaryDigestPrePostMatched {
		t.Fatalf("unexpected binary identity: %#v", report.Binary)
	}
	if report.Execution.Solution != request.ProviderPlan.Solution || report.Execution.Version != request.ProviderPlan.Version {
		t.Fatalf("unexpected execution target: %#v", report.Execution)
	}
	if _, err := provideradapter.ValidateObservation(report.CapabilityObservation); err != nil {
		t.Fatalf("Capability Observation did not validate: %v", err)
	}
	if report.CapabilityObservation.Observation.MappingProvenance == nil {
		t.Fatal("Capability Observation mapping provenance is missing")
	}
	expectedSourceState := "tei-binary-sha256:" + report.Binary.SHA256
	if got := report.CapabilityObservation.Observation.MappingProvenance.SourceStateRef; got != expectedSourceState {
		t.Fatalf("source state ref = %q, want %q", got, expectedSourceState)
	}
}

func TestProbeWithMatchingManifestRecordsManifestMatched(t *testing.T) {
	binary := writeExecutable(t, successScript())
	request := fixtureRequest(binary)
	digest, err := hashRegularExecutable(binary)
	if err != nil {
		t.Fatalf("hash executable: %v", err)
	}
	request.ManifestPath = writeManifest(t, request, digest)

	report, err := Probe(context.Background(), request)
	if err != nil {
		t.Fatalf("Probe() error = %v", err)
	}
	if report.SourceBinding != SourceBindingManifestMatch || !report.ManifestProvided {
		t.Fatalf("unexpected source binding: %#v", report)
	}
}

func TestProbeRejectsManifestMismatch(t *testing.T) {
	binary := writeExecutable(t, successScript())
	base := fixtureRequest(binary)
	digest, err := hashRegularExecutable(binary)
	if err != nil {
		t.Fatalf("hash executable: %v", err)
	}

	tests := []struct {
		name   string
		mutate func(*BuildManifest)
	}{
		{"repository", func(m *BuildManifest) { m.Repository = "other/repository" }},
		{"commit", func(m *BuildManifest) { m.Commit = "deadbeef" }},
		{"digest", func(m *BuildManifest) { m.BinarySHA256 = strings.Repeat("0", 64) }},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			manifest := BuildManifest{
				Schema:       ManifestSchema,
				Repository:   base.DeclaredRepository,
				Commit:       base.DeclaredCommit,
				BinarySHA256: digest,
			}
			tc.mutate(&manifest)
			payload, err := json.Marshal(manifest)
			if err != nil {
				t.Fatalf("marshal manifest: %v", err)
			}
			path := filepath.Join(t.TempDir(), "manifest.json")
			if err := os.WriteFile(path, payload, 0o600); err != nil {
				t.Fatalf("write manifest: %v", err)
			}
			request := base
			request.ManifestPath = path
			report, err := Probe(context.Background(), request)
			if err == nil {
				t.Fatalf("expected mismatch error, got report %#v", report)
			}
			if report.Schema != "" {
				t.Fatalf("failure must not return PASS report: %#v", report)
			}
		})
	}
}

func TestDecodeManifestRejectsUnknownFieldAndMultipleJSON(t *testing.T) {
	valid := `{"schema":"sei.tei-binary-build-manifest/v1","repository":"hat47x/tei-platform","commit":"abc","binary_sha256":"` + strings.Repeat("a", 64) + `"}`
	for _, payload := range []string{
		strings.TrimSuffix(valid, "}") + `,"token":"must-not-be-accepted"}`,
		valid + "\n" + valid,
	} {
		if manifest, err := decodeManifest([]byte(payload)); err == nil {
			t.Fatalf("expected strict manifest rejection, got %#v", manifest)
		}
	}
}

func TestProbeRejectsSymlinkExecutable(t *testing.T) {
	requirePOSIXShell(t)
	target := writeExecutable(t, successScript())
	link := filepath.Join(t.TempDir(), "tei-link")
	if err := os.Symlink(target, link); err != nil {
		t.Fatalf("create symlink: %v", err)
	}
	report, err := Probe(context.Background(), fixtureRequest(link))
	if err == nil {
		t.Fatalf("expected symlink rejection, got %#v", report)
	}
}

func TestProbeDoesNotReturnPassReportOnProcessFailure(t *testing.T) {
	binary := writeExecutable(t, "echo 'failed' >&2\nexit 7")
	report, err := Probe(context.Background(), fixtureRequest(binary))
	if err == nil {
		t.Fatalf("expected process failure, got %#v", report)
	}
	if report.Schema != "" {
		t.Fatalf("process failure must not produce PASS report: %#v", report)
	}
}

func TestProbeDoesNotReturnPassReportOnTimeout(t *testing.T) {
	binary := writeExecutable(t, "sleep 5\n"+successScript())
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()

	report, err := Probe(ctx, fixtureRequest(binary))
	if err == nil {
		t.Fatalf("expected timeout, got %#v", report)
	}
	if report.Schema != "" {
		t.Fatalf("timeout must not produce PASS report: %#v", report)
	}
}

func TestProbeRejectsExecutableDigestChangeDuringRun(t *testing.T) {
	binary := writeExecutable(t, successScript()+"\nprintf '%s\\n' '# changed during probe' >> \"$0\"")
	report, err := Probe(context.Background(), fixtureRequest(binary))
	if err == nil || !strings.Contains(err.Error(), "digest changed") {
		t.Fatalf("expected digest-change rejection, got report=%#v err=%v", report, err)
	}
	if report.Schema != "" {
		t.Fatalf("digest change must not produce PASS report: %#v", report)
	}
}

func TestReportShapeDoesNotIntroduceCredentialFields(t *testing.T) {
	binary := writeExecutable(t, successScript())
	report, err := Probe(context.Background(), fixtureRequest(binary))
	if err != nil {
		t.Fatalf("Probe() error = %v", err)
	}
	payload, err := json.Marshal(report)
	if err != nil {
		t.Fatalf("marshal report: %v", err)
	}
	for _, forbidden := range []string{"credential", "password", "api_key", "access_token", "stderr", "process_error", "caller-provided-value-must-not-survive"} {
		if strings.Contains(strings.ToLower(string(payload)), forbidden) {
			t.Fatalf("report unexpectedly contains secret-bearing field name %q: %s", forbidden, payload)
		}
	}
}
