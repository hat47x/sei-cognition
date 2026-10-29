package seicli

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
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
	Decision string     `json:"decision"`
	Verdict  string     `json:"verdict"`
	Reasons  []string   `json:"reasons,omitempty"`
	Policy   GatePolicy `json:"policy"`
	// RequestedScope is the scope the caller asked for. It is absent when the
	// caller gave none, and an empty string means "the Decision with no scope".
	RequestedScope *string      `json:"requested_scope,omitempty"`
	Binding        *GateBinding `json:"binding,omitempty"`
	NotVerified    []string     `json:"not_verified"`
}

// GateBinding names the store content a verdict was computed against.
//
// BundleDigest is the SHA-256 of the bundle bytes as read (the same value
// `sei resume` reports as snapshot_digest). DecisionDigest is the
// sei.jcs+sha256/v1alpha1 digest of the Decision record's payload. Equal
// digests mean the same bytes were checked. They do not show that nothing
// changed after the check, and they do not show the content is current.
// Binding is absent when no single Decision was identified (not recorded, or
// ambiguous).
type GateBinding struct {
	BundleID         string `json:"bundle_id"`
	BundleDigest     string `json:"bundle_digest"`
	DecisionRecordID string `json:"decision_record_id"`
	// DecisionScope is the scope of the Decision that was checked ("" = none).
	DecisionScope                 string `json:"decision_scope"`
	DecisionDigest                string `json:"decision_digest"`
	DecisionRepresentationProfile string `json:"decision_representation_profile"`
}

const decisionDigestProfile = semanticruntime.ProfileIDJCSSHA256 + "/" + semanticruntime.ProfileVersionV1Alpha1

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

// basisNotVerified is the fixed statement that the gate does not resolve basis
// references. It is listed whether or not the decision has a basis, so "allow"
// is never read as "the basis exists and is unchanged".
const basisNotVerified = "whether each basis reference exists, and for an exact reference whether its content_digest matches the real content; the gate checks neither"

// recordedDecisionOrRecommendation reports whether the bundle holds a Decision
// or Recommendation record with the logical identity (kind, id, scope) of ref.
// Only those two record types carry content in the store. A Semantic Reference
// record only names something, so it does not count as the thing existing.
func recordedDecisionOrRecommendation(bundle *semanticruntime.Bundle, ref semanticruntime.Reference) bool {
	want, ok := ref.LogicalIdentity()
	if !ok {
		return false
	}
	for _, rec := range bundle.Records {
		if rec.Decision == nil {
			continue
		}
		if d := rec.Decision.Decision; d != nil && d.Ref == want {
			return true
		}
		if r := rec.Decision.Recommendation; r != nil && r.Ref == want {
			return true
		}
	}
	return false
}

// basisNotes lists, per basis reference of d, what the gate could and could not
// tell. It reports and does not decide: a basis that is not recorded here is
// not a reason to deny, because most basis references point outside the store
// (observations and interpretations cannot be recorded by the CLI, #711), and
// whether an unresolvable basis should be refused is an Owner decision (#710).
func basisNotes(bundle *semanticruntime.Bundle, d *semanticruntime.Decision) []string {
	var notes []string
	for _, ref := range d.BasisRefs {
		label := refText(ref)
		if logical, ok := ref.LogicalIdentity(); ok && logical.Scope != "" {
			label += " @" + logical.Scope
		}
		var note string
		if recordedDecisionOrRecommendation(bundle, ref) {
			note = fmt.Sprintf("basis %s: a Decision or Recommendation with this identity is recorded in this store; that is existence only and its content was not compared", label)
		} else {
			note = fmt.Sprintf("basis %s: no Decision or Recommendation with this identity is recorded in this store; whether the referenced material exists elsewhere is not confirmed, and the verdict does not depend on it", label)
		}
		if ref.IsExact() {
			note += fmt.Sprintf("; content_digest %s was not compared with any content", ref.ContentDigest)
		}
		notes = append(notes, note)
	}
	return notes
}

// CheckDecision evaluates one recorded Decision against a policy, without
// naming a scope. It is CheckDecisionInScope with no scope given.
func CheckDecision(bundle *semanticruntime.Bundle, id string, policy GatePolicy) GateResult {
	return CheckDecisionInScope(bundle, id, nil, policy)
}

// scopeLabel renders a scope for a reason string; "" is shown as "(none)".
func scopeLabel(scope string) string {
	if scope == "" {
		return "(none)"
	}
	return fmt.Sprintf("%q", scope)
}

// CheckDecisionInScope evaluates one recorded Decision against a policy.
//
// scope nil means the caller named no scope: the id must then match exactly one
// Decision in the store, whatever its scope. A non-nil scope (including the
// empty string, meaning "the Decision with no scope") restricts the match to
// that scope. More than one match is denied and never resolved by record order.
func CheckDecisionInScope(bundle *semanticruntime.Bundle, id string, scope *string, policy GatePolicy) GateResult {
	result := GateResult{
		Decision:       id,
		Verdict:        "allow",
		Policy:         policy,
		RequestedScope: scope,
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
	var foundRecord semanticruntime.InterchangeRecord
	matches := 0
	var matchScopes []string
	for _, rec := range bundle.Records {
		if rec.Decision == nil || rec.Decision.Decision == nil || rec.Decision.Decision.Ref.ID != id {
			continue
		}
		if scope != nil && rec.Decision.Decision.Ref.Scope != *scope {
			continue
		}
		if matches == 0 {
			found = rec.Decision.Decision
			foundRecord = rec.EnvelopeRecord
		}
		matches++
		matchScopes = append(matchScopes, scopeLabel(rec.Decision.Decision.Ref.Scope))
	}
	if found == nil {
		if scope != nil {
			deny(fmt.Sprintf("no decision with this id and scope %s is recorded", scopeLabel(*scope)))
		} else {
			deny("no decision with this id is recorded")
		}
		return result
	}
	if matches > 1 {
		// Taking the first of several would let the verdict depend on record
		// order and say nothing about which Decision was meant.
		hint := "; name one with --scope"
		if scope != nil {
			hint = "; the same id and scope is recorded more than once"
		}
		deny(fmt.Sprintf("multiple decisions match this id (%d, scopes: %s), so which one is meant is ambiguous and nothing is allowed%s",
			matches, strings.Join(matchScopes, ", "), hint))
		return result
	}
	digest, err := semanticruntime.JCSSHA256Digest(foundRecord.Payload)
	if err != nil {
		deny(fmt.Sprintf("the decision's content digest could not be computed: %v", err))
		return result
	}
	result.Binding = &GateBinding{
		BundleID:                      bundle.Envelope.BundleID,
		BundleDigest:                  fmt.Sprintf("sha256:%x", sha256.Sum256(bundle.ExportOriginal())),
		DecisionRecordID:              foundRecord.RecordID,
		DecisionScope:                 found.Ref.Scope,
		DecisionDigest:                digest,
		DecisionRepresentationProfile: decisionDigestProfile,
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
	result.NotVerified = append(result.NotVerified, basisNotVerified)
	result.NotVerified = append(result.NotVerified, basisNotes(bundle, found)...)
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
	scopeFlag := f.String("scope", "", "scope of that decision; required when the same id exists in several scopes (--scope= names the decision with no scope)")
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
	var scope *string
	f.Visit(func(fl *flag.Flag) {
		if fl.Name == "scope" {
			scope = scopeFlag
		}
	})
	dataRoot := resolveDataRoot(*root)
	if info, statErr := os.Stat(dataRoot); statErr != nil || !info.IsDir() {
		// Do not create a directory (and a lock) for a store that does not exist.
		return errors.New("no store found; run `sei init` first")
	}
	// The store lock is held from the read to the log append, so the logged
	// binding describes the bytes that were checked and no `add` lands between.
	// If the lock cannot be taken the check fails (exit 1), so nothing is allowed.
	var result GateResult
	err := withStoreLock(dataRoot, func() error {
		raw, err := persistence(dataRoot).Load(ctx)
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
		result = CheckDecisionInScope(bundle, *id, scope, policy)
		// If the check cannot be logged it cannot be allowed: fail closed.
		if err := appendGateLog(dataRoot, result); err != nil {
			return fmt.Errorf("could not log the check, so nothing is allowed: %w", err)
		}
		return nil
	})
	if err != nil {
		return err
	}
	if err := writeJSON(stdout, result); err != nil {
		return err
	}
	if result.Verdict != "allow" {
		return &ExitError{Code: ExitCodeDenied, Message: "denied: " + result.Reasons[0]}
	}
	return nil
}
