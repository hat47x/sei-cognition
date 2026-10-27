// Package seicli implements the first user-facing `sei` command set.
//
// It introduces no new Semantic Contract. Records are written as the existing
// Decision Memory Contract inside the existing Semantic Interchange envelope,
// and are append-only: a record already in the bundle is never rewritten.
package seicli

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/fs"
	"os"
	"sort"
	"strings"
	"time"

	"github.com/hat47x/sei-cognition/runtime/go/packagingprobe"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

var (
	BuildVersion = "dev"
	BuildCommit  = "unknown"
	BuildTarget  = "unknown"
)

// Stdin is the input of the long-running `mcp` command. Tests replace it.
var Stdin io.Reader = os.Stdin

// Now is replaceable so tests can fix the clock.
var Now = func() time.Time { return time.Now().UTC() }

const usage = `usage: sei <command> [flags]

commands:
  init     create an empty record store
  add      append a recommendation or a decision (append-only)
  resume   show where the work stands, from the store alone
  verify   validate a portable bundle without a store
  export   write the store as a portable bundle (never overwrites a file)
  doctor   check the binary, the store and the data root, without changing them
  gate     check that a recorded decision meets a policy before an action
  mcp      serve resume / add over the Model Context Protocol (stdio) for AI tools
  version  print build information

"sei gate check" answers whether a recorded decision meets a policy. It does not run the action and does not verify Authority. It appends each check to gate-checks.jsonl and never changes the decision store.`

// Run executes one sei command. Output goes to stdout; diagnostics to stderr.
func Run(ctx context.Context, args []string, stdout, stderr io.Writer) error {
	if len(args) == 0 {
		fmt.Fprintln(stderr, usage)
		return errors.New("subcommand is required")
	}
	switch args[0] {
	case "init":
		return runInit(ctx, args[1:], stdout, stderr)
	case "add":
		return runAdd(ctx, args[1:], stdout, stderr)
	case "resume":
		return runResume(ctx, args[1:], stdout, stderr)
	case "verify":
		return runVerify(args[1:], stdout, stderr)
	case "export":
		return runExport(ctx, args[1:], stderr)
	case "doctor":
		return runDoctor(ctx, args[1:], stdout, stderr)
	case "gate":
		return runGate(ctx, args[1:], stdout, stderr)
	case "mcp":
		return runMCP(ctx, args[1:], Stdin, stdout, stderr)
	case "version":
		return writeJSON(stdout, map[string]string{"version": BuildVersion, "commit": BuildCommit, "target": BuildTarget})
	case "help", "-h", "--help":
		fmt.Fprintln(stdout, usage)
		return nil
	default:
		fmt.Fprintln(stderr, usage)
		return fmt.Errorf("unknown subcommand %q", args[0])
	}
}

func newFlags(name string, stderr io.Writer) *flag.FlagSet {
	f := flag.NewFlagSet(name, flag.ContinueOnError)
	f.SetOutput(stderr)
	return f
}

func dataRootFlag(f *flag.FlagSet) *string {
	return f.String("data-root", "", "directory holding the record store (default: $SEI_DATA_ROOT or ./.sei)")
}

func resolveDataRoot(v string) string {
	if v != "" {
		return v
	}
	if env := os.Getenv("SEI_DATA_ROOT"); env != "" {
		return env
	}
	return ".sei"
}

type multiFlag []string

func (m *multiFlag) String() string     { return strings.Join(*m, ",") }
func (m *multiFlag) Set(v string) error { *m = append(*m, v); return nil }

// parseRef reads "kind:id" into a logical reference.
func parseRef(text string) (semanticruntime.Reference, error) {
	kind, id, ok := strings.Cut(text, ":")
	if !ok || kind == "" || id == "" {
		return semanticruntime.Reference{}, fmt.Errorf("reference %q must be written kind:id", text)
	}
	return semanticruntime.Reference{Kind: kind, ID: id}, nil
}

func parseRefs(values []string) ([]semanticruntime.Reference, error) {
	var refs []semanticruntime.Reference
	for _, v := range values {
		ref, err := parseRef(v)
		if err != nil {
			return nil, err
		}
		refs = append(refs, ref)
	}
	return refs, nil
}

// recommendationRefsFrom reads --recommendation values. A bare id means a
// recommendation; any other kind is refused, because a decision can rely on a
// recommendation and on nothing else in this position.
func recommendationRefsFrom(values []string) ([]semanticruntime.Reference, error) {
	var refs []semanticruntime.Reference
	for _, v := range values {
		if !strings.Contains(v, ":") {
			v = "recommendation:" + v
		}
		ref, err := parseRef(v)
		if err != nil {
			return nil, err
		}
		if ref.Kind != "recommendation" {
			return nil, fmt.Errorf("--recommendation takes a recommendation id, not %q", v)
		}
		refs = append(refs, ref)
	}
	return refs, nil
}

// recordedRecommendations returns the ids of recommendations recorded in bundle.
func recordedRecommendations(bundle *semanticruntime.Bundle) map[string]bool {
	ids := map[string]bool{}
	for _, rec := range bundle.Records {
		if rec.Decision != nil && rec.Decision.Recommendation != nil {
			ids[rec.Decision.Recommendation.Ref.ID] = true
		}
	}
	return ids
}

func persistence(root string) packagingprobe.FilePersistence {
	return packagingprobe.FilePersistence{DataRoot: root}
}

func runInit(ctx context.Context, args []string, stdout, stderr io.Writer) error {
	f := newFlags("init", stderr)
	root := dataRootFlag(f)
	bundleID := f.String("bundle-id", "", "identifier of the store (default: sei-store-<UTC date>)")
	if err := f.Parse(args); err != nil {
		return err
	}
	dir := resolveDataRoot(*root)
	p := persistence(dir)
	id := *bundleID
	if id == "" {
		id = "sei-store-" + Now().Format("2006-01-02")
	}
	err := withStoreLock(dir, func() error {
		if _, err := p.Load(ctx); err == nil {
			return errors.New("store already exists; init never overwrites recorded work")
		} else if !errors.Is(err, packagingprobe.ErrPackageNotFound) {
			return err
		}
		envelope := semanticruntime.SemanticInterchange{
			Contract:  semanticruntime.ContractSemanticInterchange,
			BundleID:  id,
			CreatedAt: Now().Format(time.RFC3339),
			Records:   []semanticruntime.InterchangeRecord{},
		}
		data, err := marshalEnvelope(envelope)
		if err != nil {
			return err
		}
		return packagingprobe.Import(ctx, p, data)
	})
	if err != nil {
		return err
	}
	return writeJSON(stdout, map[string]string{"bundle_id": id, "data_root": dir})
}

func marshalEnvelope(envelope semanticruntime.SemanticInterchange) ([]byte, error) {
	data, err := json.MarshalIndent(envelope, "", "  ")
	if err != nil {
		return nil, err
	}
	return append(data, '\n'), nil
}

func runAdd(ctx context.Context, args []string, stdout, stderr io.Writer) error {
	if len(args) == 0 || (args[0] != "recommendation" && args[0] != "decision") {
		return errors.New("add requires a record type: recommendation or decision")
	}
	recordType := args[0]
	f := newFlags("add "+recordType, stderr)
	root := dataRootFlag(f)
	id := f.String("id", "", "record identifier, unique in the store (required)")
	statement := f.String("statement", "", "what is recommended or decided (required)")
	rationale := f.String("rationale", "", "why")
	source := f.String("source", "", "tool or person that produced this record; kept as provenance")
	var basis, unresolved, responsible, recommendations multiFlag
	f.Var(&basis, "basis", "basis reference kind:id (repeatable)")
	f.Var(&responsible, "responsible", "responsibility reference kind:id (repeatable)")
	if recordType == "decision" {
		f.Var(&unresolved, "unresolved", "unresolved reference kind:id left open by this decision (repeatable)")
		f.Var(&recommendations, "recommendation", "recommendation this decision relies on, a recorded recommendation id (repeatable)")
	}
	if err := f.Parse(args[1:]); err != nil {
		return err
	}
	if *id == "" || *statement == "" {
		return errors.New("add requires --id and --statement")
	}

	dir := resolveDataRoot(*root)
	p := persistence(dir)
	err := withStoreLock(dir, func() error {
		raw, err := p.Load(ctx)
		if errors.Is(err, packagingprobe.ErrPackageNotFound) {
			return errors.New("no store found; run `sei init` first")
		}
		if err != nil {
			return err
		}
		bundle, err := semanticruntime.LoadInterchange(raw)
		if err != nil {
			return fmt.Errorf("existing store is invalid, refusing to append: %w", err)
		}
		for _, rec := range bundle.Envelope.Records {
			if rec.RecordID == *id {
				return fmt.Errorf("record %q already exists; recorded work is never overwritten, use a new id", *id)
			}
		}

		basisRefs, err := parseRefs(basis)
		if err != nil {
			return err
		}
		responsibilityRefs, err := parseRefs(responsible)
		if err != nil {
			return err
		}

		logical := semanticruntime.LogicalReference{Kind: recordType, ID: *id}
		var payload any
		switch recordType {
		case "recommendation":
			payload = semanticruntime.DecisionMemoryDocument{
				Contract:   semanticruntime.ContractDecisionMemory,
				RecordType: "recommendation",
				Recommendation: &semanticruntime.Recommendation{
					Ref: logical, Statement: *statement, Rationale: *rationale,
					BasisRefs: basisRefs, ResponsibilityRefs: responsibilityRefs,
				},
			}
		case "decision":
			unresolvedRefs, err := parseRefs(unresolved)
			if err != nil {
				return err
			}
			recommendationRefs, err := recommendationRefsFrom(recommendations)
			if err != nil {
				return err
			}
			// A decision may rely only on a recommendation that is recorded here.
			// Otherwise "relied on" would name something the store cannot show.
			recorded := recordedRecommendations(bundle)
			for _, ref := range recommendationRefs {
				if !recorded[ref.ID] {
					return fmt.Errorf("the decision relies on recommendation %q, which is not recorded in this store; record it first", ref.ID)
				}
			}
			payload = semanticruntime.DecisionMemoryDocument{
				Contract:   semanticruntime.ContractDecisionMemory,
				RecordType: "decision",
				Decision: &semanticruntime.Decision{
					Ref: logical, Statement: *statement, Rationale: *rationale,
					BasisRefs: basisRefs, ResponsibilityRefs: responsibilityRefs,
					UnresolvedRefs: unresolvedRefs, RecommendationRefs: recommendationRefs,
				},
			}
		}
		payloadBytes, err := json.Marshal(payload)
		if err != nil {
			return err
		}
		record := semanticruntime.InterchangeRecord{
			RecordID:   *id,
			Contract:   semanticruntime.ContractIdentity{ContractID: "sei.decision-memory", Version: "v1alpha1"},
			Kind:       recordType,
			LogicalRef: &logical,
			Payload:    payloadBytes,
		}
		if *source != "" {
			record.ProvenanceRefs = []semanticruntime.LogicalReference{{Kind: "source", ID: *source}}
		}

		envelope := bundle.Envelope
		envelope.Records = append(append([]semanticruntime.InterchangeRecord{}, envelope.Records...), record)
		data, err := marshalEnvelope(envelope)
		if err != nil {
			return err
		}
		return packagingprobe.Import(ctx, p, data)
	})
	if err != nil {
		return err
	}
	return writeJSON(stdout, map[string]string{"recorded": recordType, "id": *id})
}

// ResumeView is what a person or an AI needs in order to continue the work.
// It is a Projection of the store and never replaces it.
type ResumeView struct {
	BundleID               string                 `json:"bundle_id"`
	SnapshotDigest         string                 `json:"snapshot_digest,omitempty"`
	Coverage               ResumeCoverage         `json:"coverage"`
	RecordCount            int                    `json:"record_count"`
	Decisions              []DecisionView         `json:"decisions"`
	RecommendationsOpen    []StatementView        `json:"recommendations_not_yet_relied_on"`
	RecommendationsRelied  []StatementView        `json:"recommendations_relied_on"`
	Unresolved             []UnresolvedView       `json:"unresolved"`
	NotVerifiedRecordCount int                    `json:"not_verified_record_count"`
	NotVerifiedRecords     []ResumeRecordLocation `json:"not_verified_records"`
}

// ResumeCoverage describes this projection, not all questions in the case.
type ResumeCoverage struct {
	UnresolvedSource                        string `json:"unresolved_source"`
	UnresolvedEntryCount                    int    `json:"unresolved_entry_count"`
	DistinctUnresolvedLogicalReferenceCount int    `json:"distinct_unresolved_logical_reference_count"`
	CaseCompleteness                        string `json:"case_completeness"`
}

// ResumeRecordLocation is a return hint within SnapshotDigest's original JSON.
// It neither resolves an external source nor interprets an unknown payload.
type ResumeRecordLocation struct {
	RecordID    string                           `json:"record_id"`
	Contract    semanticruntime.ContractIdentity `json:"contract"`
	JSONPointer string                           `json:"json_pointer"`
}

// ResumeRecordView returns store data, not an interpretation or an approval.
type ResumeRecordView struct {
	BundleID         string                                 `json:"bundle_id"`
	SnapshotDigest   string                                 `json:"snapshot_digest"`
	SourceRecord     ResumeRecordLocation                   `json:"source_record"`
	ValidationStatus semanticruntime.RecordValidationStatus `json:"validation_status"`
	Record           semanticruntime.InterchangeRecord      `json:"record"`
}

type StatementView struct {
	ID        string   `json:"id"`
	Statement string   `json:"statement"`
	Sources   []string `json:"sources,omitempty"`
}

type DecisionView struct {
	ID              string   `json:"id"`
	Statement       string   `json:"statement"`
	Rationale       string   `json:"rationale,omitempty"`
	Basis           []string `json:"basis,omitempty"`
	Recommendations []string `json:"recommendations,omitempty"`
	Responsible     []string `json:"responsible,omitempty"`
	Sources         []string `json:"sources,omitempty"`
}

type UnresolvedView struct {
	Ref                 string                           `json:"ref"`
	LeftOpenBy          string                           `json:"left_open_by_decision"`
	Reference           semanticruntime.Reference        `json:"reference"`
	LeftOpenByReference semanticruntime.LogicalReference `json:"left_open_by_reference"`
	SourceRecord        ResumeRecordLocation             `json:"source_record"`
}

func refText(r semanticruntime.Reference) string {
	if r.LogicalRef != nil {
		return r.LogicalRef.Kind + ":" + r.LogicalRef.ID
	}
	return r.Kind + ":" + r.ID
}

func refTexts(refs []semanticruntime.Reference) []string {
	var out []string
	for _, r := range refs {
		out = append(out, refText(r))
	}
	return out
}

func sourcesOf(rec semanticruntime.InterchangeRecord) []string {
	var out []string
	for _, p := range rec.ProvenanceRefs {
		out = append(out, p.ID)
	}
	return out
}

// BuildResume projects a bundle. A recommendation is "relied on" only when a
// Decision names it; a recommendation alone is never reported as decided.
// Unresolved items are reported as open and never as answered.
func BuildResume(bundle *semanticruntime.Bundle) ResumeView {
	view := ResumeView{
		BundleID:              bundle.Envelope.BundleID,
		Coverage:              ResumeCoverage{UnresolvedSource: "recognized-decision-unresolved-refs", CaseCompleteness: "not_assessed"},
		RecordCount:           len(bundle.Records),
		Decisions:             []DecisionView{},
		RecommendationsOpen:   []StatementView{},
		RecommendationsRelied: []StatementView{},
		Unresolved:            []UnresolvedView{},
		NotVerifiedRecords:    []ResumeRecordLocation{},
	}
	if original := bundle.ExportOriginal(); len(original) > 0 {
		view.SnapshotDigest = fmt.Sprintf("sha256:%x", sha256.Sum256(original))
	}
	relied := map[string]bool{}
	for _, rec := range bundle.Records {
		if rec.Decision != nil && rec.Decision.Decision != nil {
			for _, r := range rec.Decision.Decision.RecommendationRefs {
				relied[refText(r)] = true
			}
		}
	}
	distinctUnresolved := map[semanticruntime.LogicalReference]bool{}
	for index, rec := range bundle.Records {
		location := ResumeRecordLocation{RecordID: rec.EnvelopeRecord.RecordID,
			Contract: rec.EnvelopeRecord.Contract, JSONPointer: fmt.Sprintf("/records/%d", index)}
		switch {
		case rec.Status == semanticruntime.RecordNotVerified:
			view.NotVerifiedRecordCount++
			view.NotVerifiedRecords = append(view.NotVerifiedRecords, location)
		case rec.Decision != nil && rec.Decision.Decision != nil:
			d := rec.Decision.Decision
			view.Decisions = append(view.Decisions, DecisionView{
				ID: d.Ref.ID, Statement: d.Statement, Rationale: d.Rationale,
				Basis: refTexts(d.BasisRefs), Recommendations: refTexts(d.RecommendationRefs),
				Responsible: refTexts(d.ResponsibilityRefs), Sources: sourcesOf(rec.EnvelopeRecord),
			})
			for _, u := range d.UnresolvedRefs {
				view.Unresolved = append(view.Unresolved, UnresolvedView{Ref: refText(u), LeftOpenBy: d.Ref.ID,
					Reference: u, LeftOpenByReference: d.Ref, SourceRecord: location})
				if logical, ok := u.LogicalIdentity(); ok {
					distinctUnresolved[logical] = true
				}
			}
		case rec.Decision != nil && rec.Decision.Recommendation != nil:
			r := rec.Decision.Recommendation
			s := StatementView{ID: r.Ref.ID, Statement: r.Statement, Sources: sourcesOf(rec.EnvelopeRecord)}
			if relied["recommendation:"+r.Ref.ID] {
				view.RecommendationsRelied = append(view.RecommendationsRelied, s)
			} else {
				view.RecommendationsOpen = append(view.RecommendationsOpen, s)
			}
		}
	}
	view.Coverage.UnresolvedEntryCount = len(view.Unresolved)
	view.Coverage.DistinctUnresolvedLogicalReferenceCount = len(distinctUnresolved)
	sort.SliceStable(view.Unresolved, func(i, j int) bool { return view.Unresolved[i].Ref < view.Unresolved[j].Ref })
	return view
}

func runResume(ctx context.Context, args []string, stdout, stderr io.Writer) error {
	f := newFlags("resume", stderr)
	root := dataRootFlag(f)
	asJSON := f.Bool("json", false, "machine-readable output")
	recordID := f.String("record-id", "", "return one original record (requires --json and --snapshot-digest)")
	expectedDigest := f.String("snapshot-digest", "", "expected original bundle digest from resume")
	if err := f.Parse(args); err != nil {
		return err
	}
	if *recordID == "" && *expectedDigest != "" {
		return errors.New("--snapshot-digest requires --record-id")
	}
	if *recordID != "" && (!*asJSON || *expectedDigest == "") {
		return errors.New("--record-id requires --json and --snapshot-digest")
	}
	raw, err := persistence(resolveDataRoot(*root)).Load(ctx)
	if errors.Is(err, packagingprobe.ErrPackageNotFound) {
		return errors.New("no store found; run `sei init` first")
	}
	if err != nil {
		return err
	}
	if *recordID != "" && *expectedDigest != fmt.Sprintf("sha256:%x", sha256.Sum256(raw)) {
		return errors.New("snapshot digest mismatch; refresh resume before locating a record")
	}
	bundle, err := semanticruntime.LoadInterchange(raw)
	if err != nil {
		return fmt.Errorf("store is invalid: %w", err)
	}
	if *recordID != "" {
		for index, record := range bundle.Records {
			if record.EnvelopeRecord.RecordID == *recordID {
				return writeJSON(stdout, ResumeRecordView{BundleID: bundle.Envelope.BundleID,
					SnapshotDigest: *expectedDigest, SourceRecord: ResumeRecordLocation{
						RecordID: *recordID, Contract: record.EnvelopeRecord.Contract,
						JSONPointer: fmt.Sprintf("/records/%d", index)},
					ValidationStatus: record.Status, Record: record.EnvelopeRecord})
			}
		}
		return fmt.Errorf("record %q not found in the expected snapshot", *recordID)
	}
	view := BuildResume(bundle)
	if *asJSON {
		return writeJSON(stdout, view)
	}
	renderResume(stdout, view)
	return nil
}

func renderResume(w io.Writer, v ResumeView) {
	fmt.Fprintf(w, "Store %s: %d records\n", v.BundleID, v.RecordCount)
	fmt.Fprintln(w, "Unresolved scope: recognized Decision.unresolved_refs only; not a case-wide inventory.")
	fmt.Fprintf(w, "%d entries; %d distinct logical references. Case completeness: not assessed.\n",
		v.Coverage.UnresolvedEntryCount, v.Coverage.DistinctUnresolvedLogicalReferenceCount)
	if v.SnapshotDigest != "" {
		fmt.Fprintf(w, "Snapshot SHA-256: %s\n", v.SnapshotDigest)
	}
	section := func(title string, n int) { fmt.Fprintf(w, "\n%s (%d)\n", title, n) }
	section("Decisions", len(v.Decisions))
	for _, d := range v.Decisions {
		fmt.Fprintf(w, "  [%s] %s\n", d.ID, d.Statement)
		if d.Rationale != "" {
			fmt.Fprintf(w, "      why: %s\n", d.Rationale)
		}
		if len(d.Basis) > 0 {
			fmt.Fprintf(w, "      basis: %s\n", strings.Join(d.Basis, ", "))
		}
		if len(d.Recommendations) > 0 {
			fmt.Fprintf(w, "      relied on: %s\n", strings.Join(d.Recommendations, ", "))
		}
		if len(d.Responsible) > 0 {
			fmt.Fprintf(w, "      responsible: %s\n", strings.Join(d.Responsible, ", "))
		}
	}
	section("Unresolved", len(v.Unresolved))
	for _, u := range v.Unresolved {
		fmt.Fprintf(w, "  %s (left open by %s)\n", u.Ref, u.LeftOpenBy)
		refJSON, _ := json.Marshal(u.Reference)
		decisionJSON, _ := json.Marshal(u.LeftOpenByReference)
		fmt.Fprintf(w, "      reference: %s; decision: %s\n", refJSON, decisionJSON)
		fmt.Fprintf(w, "      source record %q at %s\n", u.SourceRecord.RecordID, u.SourceRecord.JSONPointer)
	}
	section("Recommendations not yet relied on by any decision", len(v.RecommendationsOpen))
	for _, r := range v.RecommendationsOpen {
		fmt.Fprintf(w, "  [%s] %s%s\n", r.ID, r.Statement, sourceSuffix(r.Sources))
	}
	section("Recommendations relied on by a decision", len(v.RecommendationsRelied))
	for _, r := range v.RecommendationsRelied {
		fmt.Fprintf(w, "  [%s] %s%s\n", r.ID, r.Statement, sourceSuffix(r.Sources))
	}
	if v.NotVerifiedRecordCount > 0 {
		fmt.Fprintf(w, "\n%d record(s) use a Contract this runtime does not understand. They are kept and not verified.\n", v.NotVerifiedRecordCount)
		for _, record := range v.NotVerifiedRecords {
			fmt.Fprintf(w, "  record %q: contract %q version %q at %s\n",
				record.RecordID, record.Contract.ContractID, record.Contract.Version, record.JSONPointer)
		}
	}
}

func sourceSuffix(sources []string) string {
	if len(sources) == 0 {
		return ""
	}
	return " (from " + strings.Join(sources, ", ") + ")"
}

func runVerify(args []string, stdout, stderr io.Writer) error {
	f := newFlags("verify", stderr)
	input := f.String("input", "", "portable bundle file (required)")
	if err := f.Parse(args); err != nil {
		return err
	}
	if *input == "" {
		return errors.New("verify requires --input")
	}
	data, err := os.ReadFile(*input)
	if err != nil {
		return err
	}
	bundle, err := semanticruntime.LoadInterchange(data)
	if err != nil {
		return fmt.Errorf("bundle is invalid: %w", err)
	}
	result := struct {
		BundleID         string `json:"bundle_id"`
		RecordCount      int    `json:"record_count"`
		ValidatedCount   int    `json:"validated_count"`
		NotVerifiedCount int    `json:"not_verified_count"`
	}{BundleID: bundle.Envelope.BundleID, RecordCount: len(bundle.Records)}
	for _, r := range bundle.Records {
		if r.Status == semanticruntime.RecordValidated {
			result.ValidatedCount++
		} else {
			result.NotVerifiedCount++
		}
	}
	return writeJSON(stdout, result)
}

func runExport(ctx context.Context, args []string, stderr io.Writer) error {
	f := newFlags("export", stderr)
	root := dataRootFlag(f)
	output := f.String("output", "", "file to create (required; an existing file is never overwritten)")
	if err := f.Parse(args); err != nil {
		return err
	}
	if *output == "" {
		return errors.New("export requires --output")
	}
	data, err := packagingprobe.Export(ctx, persistence(resolveDataRoot(*root)))
	if errors.Is(err, packagingprobe.ErrPackageNotFound) {
		return errors.New("no store found; run `sei init` first")
	}
	if err != nil {
		return err
	}
	// O_EXCL makes the check and the create one step, so an existing file,
	// including another store's bundle or the gate log, is never replaced.
	out, err := os.OpenFile(*output, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if errors.Is(err, fs.ErrExist) {
		return fmt.Errorf("%s already exists; export never overwrites a file, so choose a new name", *output)
	}
	if err != nil {
		return err
	}
	if _, err := out.Write(data); err != nil {
		_ = out.Close()
		return err
	}
	return out.Close()
}

func writeJSON(w io.Writer, v any) error {
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)
	return enc.Encode(v)
}
