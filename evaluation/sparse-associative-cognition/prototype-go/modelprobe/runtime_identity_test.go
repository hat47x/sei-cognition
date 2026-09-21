package modelprobe

import (
	"os"
	"runtime"
	"strings"
	"testing"
)

func TestObserveRuntimeProcessIdentityCurrentProcess(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	identity := ObserveRuntimeProcessIdentity(os.Getpid())
	if identity.Status != "observed" {
		t.Fatalf("status=%q want=observed: %+v", identity.Status, identity)
	}
	if identity.PID != os.Getpid() {
		t.Fatalf("pid=%d want=%d", identity.PID, os.Getpid())
	}
	if identity.ExecutableName == "" {
		t.Fatal("executable name must be recorded")
	}
	if !strings.HasSuffix(identity.Source, "/exe") {
		t.Fatalf("unexpected source: %q", identity.Source)
	}
	if identity.SizeBytes <= 0 {
		t.Fatalf("size_bytes=%d", identity.SizeBytes)
	}
	if len(identity.SHA256) != 64 {
		t.Fatalf("sha256 length=%d", len(identity.SHA256))
	}
	if identity.Error != "" {
		t.Fatalf("unexpected error: %s", identity.Error)
	}
}

func TestObserveRuntimeProcessIdentityNotRequested(t *testing.T) {
	identity := ObserveRuntimeProcessIdentity(0)
	if identity.Status != "not-requested" {
		t.Fatalf("status=%q want=not-requested", identity.Status)
	}
	if identity.PID != 0 || identity.SHA256 != "" || identity.SizeBytes != 0 {
		t.Fatalf("not-requested identity must not invent evidence: %+v", identity)
	}
}

func TestObserveRuntimeProcessIdentityUnavailablePID(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	identity := ObserveRuntimeProcessIdentity(1 << 30)
	if identity.Status != "unavailable" {
		t.Fatalf("status=%q want=unavailable: %+v", identity.Status, identity)
	}
	if identity.SHA256 != "" || identity.SizeBytes != 0 {
		t.Fatalf("unavailable identity must not invent digest/size: %+v", identity)
	}
	if identity.Error == "" {
		t.Fatal("unavailable identity must record error")
	}
}
