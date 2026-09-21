package modelprobe

import (
	"os"
	"path/filepath"
	"runtime"
	"syscall"
	"testing"
)

func TestObserveRuntimeModelMappingNotRequested(t *testing.T) {
	evidence := ObserveRuntimeModelMapping(0, "")
	if evidence.Status != "not-requested" {
		t.Fatalf("status=%q want=not-requested", evidence.Status)
	}
}

func TestProcMapsPath(t *testing.T) {
	line := "7f000000-7f001000 r--p 00000000 08:01 12345 /tmp/model file.gguf"
	if got := procMapsPath(line); got != "/tmp/model file.gguf" {
		t.Fatalf("path=%q", got)
	}
	if got := procMapsPath("7f000000-7f001000 rw-p 00000000 00:00 0 [heap]"); got != "" {
		t.Fatalf("special mapping must be ignored, got %q", got)
	}
}

func TestObserveRuntimeModelMappingCurrentProcess(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	path := filepath.Join(t.TempDir(), "mapped-model.gguf")
	content := make([]byte, 4096)
	content[0] = 1
	if err := os.WriteFile(path, content, 0o600); err != nil {
		t.Fatal(err)
	}

	file, err := os.OpenFile(path, os.O_RDWR, 0)
	if err != nil {
		t.Fatal(err)
	}
	defer file.Close()

	mapped, err := syscall.Mmap(int(file.Fd()), 0, len(content), syscall.PROT_READ, syscall.MAP_SHARED)
	if err != nil {
		t.Fatal(err)
	}
	defer syscall.Munmap(mapped)

	evidence := ObserveRuntimeModelMapping(os.Getpid(), path)
	if evidence.Status != "observed" {
		t.Fatalf("status=%q want=observed: %+v", evidence.Status, evidence)
	}
	if evidence.MappingCount < 1 {
		t.Fatalf("mapping_count=%d want>=1", evidence.MappingCount)
	}
	if evidence.ModelFileName != "mapped-model.gguf" {
		t.Fatalf("model_file_name=%q", evidence.ModelFileName)
	}
	if evidence.Source == "" || evidence.Error != "" {
		t.Fatalf("unexpected evidence: %+v", evidence)
	}
}

func TestObserveRuntimeModelMappingNotObserved(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	path := filepath.Join(t.TempDir(), "unmapped-model.gguf")
	if err := os.WriteFile(path, []byte("not mapped"), 0o600); err != nil {
		t.Fatal(err)
	}

	evidence := ObserveRuntimeModelMapping(os.Getpid(), path)
	if evidence.Status != "not-observed" {
		t.Fatalf("status=%q want=not-observed: %+v", evidence.Status, evidence)
	}
	if evidence.MappingCount != 0 {
		t.Fatalf("mapping_count=%d want=0", evidence.MappingCount)
	}
}


func TestObserveRuntimeModelMappingUnavailablePID(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("Linux /proc test")
	}

	path := filepath.Join(t.TempDir(), "candidate.gguf")
	if err := os.WriteFile(path, []byte("candidate"), 0o600); err != nil {
		t.Fatal(err)
	}

	evidence := ObserveRuntimeModelMapping(1<<30, path)
	if evidence.Status != "unavailable" {
		t.Fatalf("status=%q want=unavailable: %+v", evidence.Status, evidence)
	}
	if evidence.MappingCount != 0 || evidence.Error == "" {
		t.Fatalf("unavailable PID must not invent mapping evidence: %+v", evidence)
	}
}
