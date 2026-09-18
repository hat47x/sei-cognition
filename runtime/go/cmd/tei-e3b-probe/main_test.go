package main

import (
	"strings"
	"testing"
)

func TestRunRejectsRemovedSourceStateRefFlag(t *testing.T) {
	err := run([]string{"--source-state-ref", "must-not-be-accepted"})
	if err == nil || !strings.Contains(err.Error(), "flag provided but not defined") {
		t.Fatalf("expected removed source-state-ref flag rejection, got %v", err)
	}
}

func TestRunRejectsPositionalArguments(t *testing.T) {
	err := run([]string{"unexpected"})
	if err == nil || !strings.Contains(err.Error(), "positional arguments") {
		t.Fatalf("expected positional argument rejection, got %v", err)
	}
}

func TestRunRejectsNonPositiveTimeout(t *testing.T) {
	err := run([]string{"--timeout", "0s"})
	if err == nil || !strings.Contains(err.Error(), "--timeout must be greater than zero") {
		t.Fatalf("expected timeout rejection, got %v", err)
	}
}

func TestRunRejectsUnsafeSourceRepositoryBeforeExecution(t *testing.T) {
	err := run([]string{
		"--binary", "/not-used-because-source-validation-fails",
		"--source-repository", "https://token@example.invalid/hat47x/tei-platform.git",
		"--source-commit", "0123456789abcdef0123456789abcdef01234567",
	})
	if err == nil || !strings.Contains(err.Error(), "non-URL repository identifier") {
		t.Fatalf("expected unsafe repository rejection, got %v", err)
	}
}

func TestRunRejectsAmbiguousSourceCommitBeforeExecution(t *testing.T) {
	err := run([]string{
		"--binary", "/not-used-because-source-validation-fails",
		"--source-repository", "hat47x/tei-platform",
		"--source-commit", "deadbeef",
	})
	if err == nil || !strings.Contains(err.Error(), "full hexadecimal object identity") {
		t.Fatalf("expected short commit rejection, got %v", err)
	}
}
