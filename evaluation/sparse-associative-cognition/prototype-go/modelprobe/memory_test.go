package modelprobe

import (
	"os"
	"runtime"
	"testing"
)

func TestReadLinuxProcessMemoryCurrentProcess(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	current, peak, processName, err := readLinuxProcessMemory(os.Getpid())
	if err != nil {
		t.Fatal(err)
	}
	if current == 0 {
		t.Fatal("current RSS must be greater than zero")
	}
	if peak == 0 {
		t.Fatal("peak RSS must be greater than zero")
	}
	if peak < current {
		t.Fatalf("peak RSS=%d must be >= current RSS=%d", peak, current)
	}
	if processName == "" {
		t.Fatal("process name must be recorded")
	}
}

func TestRuntimeMemoryEvidenceNotRequested(t *testing.T) {
	evidence := newRuntimeMemoryEvidence(0)
	if evidence.Status != "not-requested" {
		t.Fatalf("status=%q want=not-requested", evidence.Status)
	}
	evidence.Observe("matrix-start", "")
	if len(evidence.Samples) != 0 || len(evidence.Errors) != 0 {
		t.Fatalf("not-requested evidence must remain empty: %+v", evidence)
	}
}

func TestRuntimeMemoryEvidenceRecordsCurrentProcess(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	evidence := newRuntimeMemoryEvidence(os.Getpid())
	evidence.Observe("matrix-start", "")
	evidence.Observe("after-raw", ModeRaw)

	if evidence.Status != "observed" {
		t.Fatalf("status=%q want=observed: %+v", evidence.Status, evidence)
	}
	if len(evidence.Samples) != 2 {
		t.Fatalf("samples=%d want=2", len(evidence.Samples))
	}
	if evidence.MaxObservedRSSBytes == 0 || evidence.PeakRSSBytes == 0 {
		t.Fatalf("memory summary must be populated: %+v", evidence)
	}
	if evidence.PeakRSSBytes < evidence.MaxObservedRSSBytes {
		t.Fatalf("peak RSS=%d must be >= max observed RSS=%d", evidence.PeakRSSBytes, evidence.MaxObservedRSSBytes)
	}
}

func TestRuntimeMemoryEvidenceUnavailablePIDDoesNotInventZeroMeasurement(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	evidence := newRuntimeMemoryEvidence(1 << 30)
	evidence.Observe("matrix-start", "")

	if evidence.Status != "unavailable" {
		t.Fatalf("status=%q want=unavailable", evidence.Status)
	}
	if len(evidence.Samples) != 0 {
		t.Fatalf("unavailable PID must not create a zero-valued sample: %+v", evidence)
	}
	if len(evidence.Errors) != 1 {
		t.Fatalf("errors=%d want=1", len(evidence.Errors))
	}
}

func TestParseProcStatusBytes(t *testing.T) {
	got, err := parseProcStatusBytes("VmRSS:\t  1234 kB", "VmRSS:")
	if err != nil {
		t.Fatal(err)
	}
	if got != 1234*1024 {
		t.Fatalf("bytes=%d want=%d", got, 1234*1024)
	}

	if _, err := parseProcStatusBytes("VmRSS: 1234 MB", "VmRSS:"); err == nil {
		t.Fatal("expected unit rejection")
	}
}
