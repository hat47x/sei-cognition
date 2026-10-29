package seicli

import (
	"fmt"
	"strings"
	"unicode"
)

// Input checks for values that `sei add` and the MCP add tools write into the
// store. They apply to what is about to be recorded only. Reading never uses
// them, so a store that already holds such a value still loads, verifies and
// resumes. The Contract is unchanged: a stricter rule for what may be stored is
// for the Owner to decide (#717).

// checkIdentifier rejects an id (or the kind or id part of a reference) that
// is empty, only whitespace, has leading or trailing whitespace, or contains a
// control character such as a newline or tab. Two values that differ only by
// surrounding whitespace would otherwise be recorded as different ids that look
// the same.
func checkIdentifier(label, value string) error {
	if strings.TrimSpace(value) == "" {
		return fmt.Errorf("%s must not be empty or only whitespace", label)
	}
	if strings.TrimSpace(value) != value {
		return fmt.Errorf("%s %q must not start or end with whitespace", label, value)
	}
	for _, r := range value {
		if unicode.IsControl(r) {
			return fmt.Errorf("%s %q must not contain a control character (newline, tab, etc.)", label, value)
		}
	}
	return nil
}

// checkStatement rejects a statement that is empty or only whitespace. A
// statement may span lines, so other characters are not restricted here.
func checkStatement(value string) error {
	if strings.TrimSpace(value) == "" {
		return fmt.Errorf("--statement must not be empty or only whitespace")
	}
	return nil
}

// rejectDuplicateRefs refuses a list that names the same reference twice, so
// the record does not claim two items where there is one.
func rejectDuplicateRefs(flagName string, values []string) error {
	seen := map[string]bool{}
	for _, v := range values {
		if seen[v] {
			return fmt.Errorf("--%s names %q more than once", flagName, v)
		}
		seen[v] = true
	}
	return nil
}
