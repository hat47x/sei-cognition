package seicli

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"

	"github.com/hat47x/sei-cognition/runtime/go/packagingprobe"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// ExitCodeDenied is returned by `sei gate check` when the recorded Decision does
// not meet the stated policy. It differs from 1, which means the check itself
// could not be completed. A caller that treats every non-zero code as "do not
// proceed" fails closed.
const ExitCodeDenied = 3

// ExitError carries a process exit code.
type ExitError struct {
	Code    int
	Message string
}

func (e *ExitError) Error() string { return e.Message }

// GatePolicy is chosen by the operator at the call site. It is not stored in
// the bundle and is not a Semantic Contract.
type GatePolicy struct {
	RequireResponsible    bool `json:"require_responsible"`
	RequireRecommendation bool `json:"require_recommendation"`
	DenyUnresolved        bool `json:"deny_unresolved"`
}

// GateResult reports whether a recorded Decision meets a policy.
//
// "allow" means the Decision is recorded and meets the stated policy. It does
// not mean the responsible party holds Authority, and it does not start any
// execution. Those are listed under NotVerified rather than reported as passed.
type GateResult struct {
	Decision    string     `json:"decision"`
	Verdict     string     `json:"verdict"`
	Reasons     []string   `json:"reasons,omitempty"`
	Policy      GatePolicy `json:"policy"`
	NotVerified []string   `json:"not_verified"`
}

// reliesOnRecorded reports whether the decision names at least one
// recommendation that is itself recorded in the bundle. A reference to a
// recommendation that is not in the store does not count.
func reliesOnRecorded(bundle *semanticruntime.Bundle, d *semanticruntime.Decision) bool {
	recorded := recordedRecommendations(bundle)
	for _, ref := range d.RecommendationRefs {
		if recordedRecommendationRef(recorded, ref) {
			return true
		}
	}
	return false
}

// lineageNotVerified is the fixed statement that the gate does not evaluate
// Semantic Lineage. It is listed whether or not the bundle holds any lineage
// that names the decision, so a reader never takes "allow" to mean that no
// later revision, supersession or withdrawal exists.
const lineageNotVerified = "whether a later Semantic Lineage (revises, supersedes, withdraws) changes how this decision stands; the gate does not evaluate Semantic Lineage"

// lineageNotes lists the Semantic Lineage in the bundle that names d as its
// from or to endpoint, one note per lineage. It reports what exists and does
// not interpret it: what a lineage does to a decision's standing is not
// defined yet (#687), so the verdict never depends on these notes.
func lineageNotes(bundle *semanticruntime.Bundle, d *semanticruntime.Decision) []string {
	names := func(ref semanticruntime.Reference) bool {
		logical, ok := ref.LogicalIdentity()
		return ok && logical.Kind == "decision" && logical.ID == d.Ref.ID && logical.Scope == d.Ref.Scope
	}
	var notes []string
	add := func(lineage *semanticruntime.SemanticLineage) {
		if lineage == nil {
			return
		}
		role := ""
		switch {
		case names(lineage.From) && names(lineage.To):
			role = "from and to"
		case names(lineage.From):
			role = "from"
		case names(lineage.To):
			role = "to"
		default:
			return
		}
		notes = append(notes, fmt.Sprintf(
			"Semantic Lineage %q names this decision as %s (%s -> %s); its effect on this decision was not evaluated",
			lineage.Relation, role, refText(lineage.From), refText(lineage.To)))
	}
	for _, rec := range bundle.Records {
		if rec.Decision != nil && rec.Decision.Decision != nil {
			add(rec.Decision.Decision.Lineage)
		}
		if rec.Reference != nil {
			add(rec.Reference.SemanticLineage)
		}
	}
	return notes
}

// CheckDecision evaluates one recorded Decision against a policy.
func CheckDecision(bundle *semanticruntime.Bundle, id string, policy GatePolicy) GateResult {
	result := GateResult{
		Decision: id,
		Verdict:  "allow",
		Policy:   policy,
		NotVerified: []string{
			"that the responsible party holds Authority for this action",
			"that the action matches what the decision covers",
		},
	}
	deny := func(reason string) {
		result.Verdict = "deny"
		result.Reasons = append(result.Reasons, reason)
	}

	var found *semanticruntime.Decision
	for _, rec := range bundle.Records {
		if rec.Decision != nil && rec.Decision.Decision != nil && rec.Decision.Decision.Ref.ID == id {
			found = rec.Decision.Decision
			break
		}
	}
	if found == nil {
		deny("no decision with this id is recorded")
		return result
	}
	if policy.RequireResponsible && len(found.ResponsibilityRefs) == 0 {
		deny("the decision names no responsible party")
	}
	if policy.RequireRecommendation && !reliesOnRecorded(bundle, found) {
		deny("the decision relies on no recorded recommendation")
	}
	if policy.DenyUnresolved && len(found.UnresolvedRefs) > 0 {
		deny(fmt.Sprintf("the decision left %d question(s) unresolved", len(found.UnresolvedRefs)))
	}
	result.NotVerified = append(result.NotVerified, lineageNotVerified)
	result.NotVerified = append(result.NotVerified, lineageNotes(bundle, found)...)
	return result
}

// GateLogFile is an append-only operational log of gate checks. It sits beside
// the semantic bundle but is not part of it: it is not a Semantic Contract and
// is not exported by `sei export`. Whether gate outcomes should become
// canonical records is left to a separate decision (ADR-0034).
const GateLogFile = "gate-checks.jsonl"

type gateLogEntry struct {
	CheckedAt string `json:"checked_at"`
	GateResult
}

func appendGateLog(dataRoot string, result GateResult) error {
	line, err := json.Marshal(gateLogEntry{CheckedAt: Now().Format(time.RFC3339), GateResult: result})
	if err != nil {
		return err
	}
	f, err := os.OpenFile(filepath.Join(dataRoot, GateLogFile), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	if _, err := f.Write(append(line, '\n')); err != nil {
		_ = f.Close()
		return err
	}
	return f.Close()
}

func runGate(ctx context.Context, args []string, stdout, stderr io.Writer) error {
	if len(args) == 0 || args[0] != "check" {
		return errors.New("gate requires a subcommand: check")
	}
	f := newFlags("gate check", stderr)
	root := dataRootFlag(f)
	id := f.String("decision", "", "id of the recorded decision the action relies on (required)")
	policy := GatePolicy{}
	f.BoolVar(&policy.RequireResponsible, "require-responsible", true, "deny when the decision names no responsible party")
	f.BoolVar(&policy.RequireRecommendation, "require-recommendation", false, "deny when the decision relies on no recorded recommendation")
	f.BoolVar(&policy.DenyUnresolved, "deny-unresolved", false, "deny when the decision left questions unresolved")
	if err := f.Parse(args[1:]); err != nil {
		return err
	}
	if *id == "" {
		return errors.New("gate check requires --decision")
	}
	raw, err := persistence(resolveDataRoot(*root)).Load(ctx)
	if errors.Is(err, packagingprobe.ErrPackageNotFound) {
		return errors.New("no store found; run `sei init` first")
	}
	if err != nil {
		return err
	}
	bundle, err := semanticruntime.LoadInterchange(raw)
	if err != nil {
		return fmt.Errorf("store is invalid, so nothing can be allowed: %w", err)
	}
	result := CheckDecision(bundle, *id, policy)
	// If the check cannot be logged it cannot be allowed: fail closed.
	if err := appendGateLog(resolveDataRoot(*root), result); err != nil {
		return fmt.Errorf("could not log the check, so nothing is allowed: %w", err)
	}
	if err := writeJSON(stdout, result); err != nil {
		return err
	}
	if result.Verdict != "allow" {
		return &ExitError{Code: ExitCodeDenied, Message: "denied: " + result.Reasons[0]}
	}
	return nil
}
