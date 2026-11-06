package seicli

import (
	"crypto/rand"
	"fmt"
	"strings"
	"unicode"
	"unicode/utf8"
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

// maxBundleIDRunes bounds the bundle id `sei init` records. The id appears in
// the resume heading, the verify and gate output and the gate log, so an
// unbounded value would reach every one of them (#776).
const maxBundleIDRunes = 200

// checkBundleID applies the id check to a --bundle-id value and bounds its
// length. It runs at init only; an existing store keeps whatever id it has.
func checkBundleID(value string) error {
	if err := checkIdentifier("--bundle-id", value); err != nil {
		return err
	}
	if n := utf8.RuneCountInString(value); n > maxBundleIDRunes {
		return fmt.Errorf("--bundle-id is %d characters; the limit is %d", n, maxBundleIDRunes)
	}
	return nil
}

// defaultBundleID returns the id used when --bundle-id is omitted: the UTC date
// plus 8 random hex digits, so two stores made on the same day get different
// ids. The id stays a name a person can read; it does not prove that two
// stores are the same or different, and bundle_digest remains the check for
// content.
func defaultBundleID(date string) string {
	var b [4]byte
	if _, err := rand.Read(b[:]); err != nil {
		return "sei-store-" + date
	}
	return fmt.Sprintf("sei-store-%s-%x", date, b)
}
