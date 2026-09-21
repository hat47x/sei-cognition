package modelprobe

import (
	"fmt"
	"os/exec"
	"strings"
)

func ResolveExactSourceGitSHA(expected string) (string, error) {
	output, err := exec.Command("git", "rev-parse", "HEAD").Output()
	if err != nil {
		return "", fmt.Errorf("git rev-parse HEAD: %w", err)
	}
	actual := strings.TrimSpace(string(output))
	if err := ValidateRunIdentity("source-head-check", actual); err != nil {
		return "", fmt.Errorf("current git HEAD is not a valid source identity: %w", err)
	}

	expected = strings.TrimSpace(expected)
	if expected != "" && expected != actual {
		return "", fmt.Errorf(
			"source Git SHA mismatch: expected %s, current HEAD is %s",
			expected,
			actual,
		)
	}

	statusOutput, err := exec.Command(
		"git",
		"status",
		"--porcelain=v1",
		"--untracked-files=all",
	).Output()
	if err != nil {
		return "", fmt.Errorf("git status --porcelain: %w", err)
	}
	if dirty := strings.TrimSpace(string(statusOutput)); dirty != "" {
		lines := strings.Split(dirty, "\n")
		const maxReported = 5
		if len(lines) > maxReported {
			lines = append(
				lines[:maxReported],
				fmt.Sprintf("... (%d more)", len(lines)-maxReported),
			)
		}
		return "", fmt.Errorf(
			"working tree is not clean; exact source Git SHA would be ambiguous: %s",
			strings.Join(lines, "; "),
		)
	}

	return actual, nil
}
