package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func TestValidateSHA256(t *testing.T) {
	valid := strings.Repeat("a", 64)
	if err := validateSHA256(valid); err != nil {
		t.Fatal(err)
	}
	for _, invalid := range []string{
		"",
		strings.Repeat("a", 63),
		strings.Repeat("g", 64),
	} {
		if err := validateSHA256(invalid); err == nil {
			t.Fatalf("expected invalid digest rejection: %q", invalid)
		}
	}
}

func TestReadStrictJSONRejectsTrailingValue(t *testing.T) {
	path := filepath.Join(t.TempDir(), "value.json")
	if err := os.WriteFile(path, []byte("{\"value\":1}\n{\"value\":2}\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	var target struct {
		Value int `json:"value"`
	}
	if err := readStrictJSON(path, &target); err == nil {
		t.Fatal("expected trailing JSON rejection")
	}
}

func TestReadStrictJSONRejectsUnknownField(t *testing.T) {
	path := filepath.Join(t.TempDir(), "value.json")
	if err := os.WriteFile(path, []byte("{\"value\":1,\"extra\":2}\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	var target struct {
		Value int `json:"value"`
	}
	if err := readStrictJSON(path, &target); err == nil {
		t.Fatal("expected unknown field rejection")
	}
}

func TestReadStrictJSONAcceptsSingleValue(t *testing.T) {
	path := filepath.Join(t.TempDir(), "value.json")
	if err := os.WriteFile(path, []byte("{\"value\":1}\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	var target struct {
		Value int `json:"value"`
	}
	if err := readStrictJSON(path, &target); err != nil {
		t.Fatal(err)
	}
	if target.Value != 1 {
		t.Fatalf("value=%d want=1", target.Value)
	}
}


func TestValidateExpectedHost(t *testing.T) {
	host := modelprobe.HostInfo{
		OS:         "linux",
		Arch:       "amd64",
		LogicalCPU: 8,
		GoVersion:  "go1.25.14",
	}
	if err := validateExpectedHost(host, "go1.25.14", "linux", "amd64"); err != nil {
		t.Fatal(err)
	}
	if err := validateExpectedHost(host, "", "", ""); err != nil {
		t.Fatal(err)
	}
}

func TestValidateExpectedHostRejectsMismatch(t *testing.T) {
	host := modelprobe.HostInfo{
		OS:         "linux",
		Arch:       "amd64",
		LogicalCPU: 8,
		GoVersion:  "go1.25.14",
	}
	for name, values := range map[string][3]string{
		"go-version": {"go1.25.13", "linux", "amd64"},
		"os":         {"go1.25.14", "darwin", "amd64"},
		"arch":       {"go1.25.14", "linux", "arm64"},
	} {
		t.Run(name, func(t *testing.T) {
			if err := validateExpectedHost(host, values[0], values[1], values[2]); err == nil {
				t.Fatal("expected host mismatch rejection")
			}
		})
	}
}


func TestVerificationSchemaVersion(t *testing.T) {
	if verificationSchema != "sei-cognition.local-model-matrix-verification/v1" {
		t.Fatalf("verificationSchema=%q want v1", verificationSchema)
	}
}
