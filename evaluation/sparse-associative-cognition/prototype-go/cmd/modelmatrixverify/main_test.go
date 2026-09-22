package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
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
