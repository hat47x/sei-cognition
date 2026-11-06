package seicli

import (
	"fmt"
	"strings"
	"unicode"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
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

// checkRationale rejects a rationale that is only whitespace. An omitted
// rationale is allowed, and a rationale may span lines, so only a value that
// says nothing is refused (#757).
func checkRationale(value string) error {
	if strings.TrimSpace(value) == "" {
		return fmt.Errorf("--rationale must not be only whitespace; omit it when there is no rationale")
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

// rejectSelfReference refuses a --basis or --unresolved value that names the
// record being written. A record is not a basis for itself, and an open question
// cannot be the decision that leaves it open. Such a reference would later show
// as a recorded basis although nothing outside the record supports it (#794).
// Only what is about to be recorded is checked; a store that already holds one
// is still read as before. The CLI writes references without a scope, so the
// comparison is on kind and id.
func rejectSelfReference(flagName, kind, id string, refs []semanticruntime.Reference) error {
	for _, ref := range refs {
		if ref.Kind == kind && ref.ID == id {
			return fmt.Errorf("--%s %s:%s names the %s being recorded; a record cannot be its own %s, so name something outside it", flagName, kind, id, kind, flagName)
		}
	}
	return nil
}
