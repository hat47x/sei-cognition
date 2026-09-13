// Package cognitiveeval provides evaluation-only mechanics for comparing
// raw-context prompting with bounded Cognitive Workspace and staged routing.
// It does not invoke a model and does not grant generated output canonical
// semantic authority.
package cognitiveeval

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/hybridreasoning"
)

// Record is the minimal semantic material needed by this evaluation harness.
// CapturedAt is intentionally distinct from SubjectAt so late-arriving evidence
// can be tested without rewriting historical Decision basis.
type Record struct {
	Ref        string `json:"ref"`
	Kind       string `json:"kind"`
	Summary    string `json:"summary"`
	CapturedAt string `json:"captured_at,omitempty"`
	SubjectAt  string `json:"subject_at,omitempty"`
}

// Fixture describes one underlying evidence universe used to generate all
// comparison conditions.
type Fixture struct {
	ID                string                         `json:"id"`
	Objective         string                         `json:"objective"`
	Task              string                         `json:"task"`
	RawContext        []string                       `json:"raw_context"`
	Records           []Record                       `json:"records"`
	SelectedRefs      []string                       `json:"selected_refs"`
	UnknownRefs       []string                       `json:"unknown_refs,omitempty"`
	ConflictRefs      []string                       `json:"conflict_refs,omitempty"`
	Constraints       []string                       `json:"constraints,omitempty"`
	RecommendationRef string                         `json:"recommendation_ref,omitempty"`
	DecisionRef       string                         `json:"decision_ref,omitempty"`
	DecisionBasisRefs []string                       `json:"decision_basis_refs,omitempty"`
	DecidedAt         string                         `json:"decided_at,omitempty"`
	RouteContext      hybridreasoning.RoutingContext `json:"-"`
	ExpectedRoute     hybridreasoning.Route          `json:"expected_route"`
}

type RawRequest struct {
	Schema    string `json:"schema"`
	Status    string `json:"status"`
	Objective string `json:"objective"`
	Context   string `json:"context"`
}

type StagedRequest struct {
	Schema                       string                              `json:"schema"`
	Status                       string                              `json:"status"`
	Routing                      hybridreasoning.RoutingDecision     `json:"routing"`
	Workspace                    hybridreasoning.WorkingSet          `json:"workspace"`
	GeneralModelEscalationHint   bool                                `json:"general_model_escalation_hint"`
	HeavyCognitionOrEvidenceNeed bool                                `json:"heavy_cognition_or_evidence_need"`
}

type BundleStats struct {
	RawContextChars       int     `json:"raw_context_chars"`
	WorkspaceJSONChars    int     `json:"workspace_json_chars"`
	TotalRecordCount      int     `json:"total_record_count"`
	SelectedRecordCount   int     `json:"selected_record_count"`
	SelectedRecordRatio   float64 `json:"selected_record_ratio"`
	ExpectedRouteMatched  bool    `json:"expected_route_matched"`
	LocalModelAllowed     bool    `json:"local_model_allowed"`
	GeneralModelHint      bool    `json:"general_model_escalation_hint"`
}

type ComparisonBundle struct {
	Schema    string                     `json:"schema"`
	Status    string                     `json:"status"`
	FixtureID string                     `json:"fixture_id"`
	Raw       RawRequest                 `json:"raw_context_baseline"`
	Workspace hybridreasoning.WorkingSet `json:"cognitive_workspace"`
	Staged    StagedRequest              `json:"staged_cognition"`
	Stats     BundleStats                `json:"stats"`
}

// Claim is an externally inspectable material claim. Hidden chain-of-thought is
// neither required nor represented by this harness.
type Claim struct {
	Text           string   `json:"text"`
	SupportingRefs []string `json:"supporting_refs,omitempty"`
}

// ModelOutput is the provider-neutral result shape accepted by the evaluator.
// Every field is proposal/evaluation material only.
type ModelOutput struct {
	Proposal              string   `json:"proposal"`
	SupportingRefs        []string `json:"supporting_refs,omitempty"`
	DecisionBasisRefs     []string `json:"decision_basis_refs,omitempty"`
	PreservedUnknownRefs  []string `json:"preserved_unknown_refs,omitempty"`
	PreservedConflictRefs []string `json:"preserved_conflict_refs,omitempty"`
	RecommendationRef     string   `json:"recommendation_ref,omitempty"`
	DecisionRef           string   `json:"decision_ref,omitempty"`
	NeedMoreEvidence      bool     `json:"need_more_evidence"`
	Claims                []Claim  `json:"claims,omitempty"`
}

type EvaluationReport struct {
	FixtureID                         string  `json:"fixture_id"`
	UnknownPreservationRate           float64 `json:"unknown_preservation_rate"`
	ConflictPreservationRate          float64 `json:"conflict_preservation_rate"`
	RecommendationDecisionSeparated   bool    `json:"recommendation_decision_separated"`
	HistoricalBasisViolationCount     int     `json:"historical_basis_violation_count"`
	UnsupportedClaimCount             int     `json:"unsupported_claim_count"`
	InvalidReferenceCount             int     `json:"invalid_reference_count"`
	SupportedMaterialClaimCount       int     `json:"supported_material_claim_count"`
	NeedMoreEvidenceAppropriate       bool    `json:"need_more_evidence_appropriate"`
	AllExpectedUnknownsPreserved      bool    `json:"all_expected_unknowns_preserved"`
	AllExpectedConflictsPreserved     bool    `json:"all_expected_conflicts_preserved"`
	NoHistoricalBasisViolation        bool    `json:"no_historical_basis_violation"`
	AllMaterialClaimsHaveValidSupport bool    `json:"all_material_claims_have_valid_support"`
}

func BuildComparisonBundle(f Fixture) (ComparisonBundle, error) {
	if err := ValidateFixture(f); err != nil {
		return ComparisonBundle{}, err
	}

	byRef := recordMap(f.Records)
	candidates := make([]hybridreasoning.Candidate, 0, len(f.SelectedRefs))
	for i, ref := range f.SelectedRefs {
		record := byRef[ref]
		activation := float32(1.0 - float64(i)*0.05)
		if activation < 0.10 {
			activation = 0.10
		}
		meaning := map[string]any{
			"ref":     record.Ref,
			"kind":    record.Kind,
			"summary": record.Summary,
		}
		if record.CapturedAt != "" {
			meaning["captured_at"] = record.CapturedAt
		}
		if record.SubjectAt != "" {
			meaning["subject_at"] = record.SubjectAt
		}
		candidates = append(candidates, hybridreasoning.Candidate{
			Ref: ref, Activation: activation, Meaning: meaning,
		})
	}

	unresolved := make([]map[string]any, 0, len(f.UnknownRefs)+len(f.ConflictRefs))
	for _, ref := range f.UnknownRefs {
		r := byRef[ref]
		unresolved = append(unresolved, map[string]any{
			"ref": ref, "kind": "unknown", "summary": r.Summary,
		})
	}
	for _, ref := range f.ConflictRefs {
		r := byRef[ref]
		unresolved = append(unresolved, map[string]any{
			"ref": ref, "kind": "conflict", "summary": r.Summary,
		})
	}

	workspace := hybridreasoning.BuildWorkingSet(
		f.Objective,
		f.Task,
		candidates,
		unresolved,
		f.Constraints,
		hybridreasoning.WorkingSetOptions{MaxCandidates: 8, MaxTextChars: 1200},
	)

	routingContext := f.RouteContext
	routingContext.Task = f.Task
	if routingContext.CandidateCount == 0 {
		routingContext.CandidateCount = len(candidates)
	}
	routing := hybridreasoning.RouteReasoning(routingContext)

	generalHint := routing.Route == hybridreasoning.RouteHumanOrStrongerReview
	heavyNeed := routing.Route == hybridreasoning.RouteExpandEvidence ||
		routing.Route == hybridreasoning.RouteExternalEvidence ||
		routing.Route == hybridreasoning.RouteHumanOrStrongerReview

	raw := RawRequest{
		Schema: "sei-cognition.raw-context-baseline/v0",
		Status: "evaluation-only",
		Objective: f.Objective,
		Context: strings.Join(f.RawContext, "\n"),
	}
	workspaceBytes, err := json.Marshal(workspace)
	if err != nil {
		return ComparisonBundle{}, fmt.Errorf("marshal workspace: %w", err)
	}
	selectedRatio := 0.0
	if len(f.Records) > 0 {
		selectedRatio = float64(len(f.SelectedRefs)) / float64(len(f.Records))
	}

	return ComparisonBundle{
		Schema: "sei-cognition.cognitive-workspace-comparison/v0",
		Status: "evaluation-only",
		FixtureID: f.ID,
		Raw: raw,
		Workspace: workspace,
		Staged: StagedRequest{
			Schema: "sei-cognition.staged-cognition-request/v0",
			Status: "evaluation-only",
			Routing: routing,
			Workspace: workspace,
			GeneralModelEscalationHint: generalHint,
			HeavyCognitionOrEvidenceNeed: heavyNeed,
		},
		Stats: BundleStats{
			RawContextChars: len([]rune(raw.Context)),
			WorkspaceJSONChars: len([]rune(string(workspaceBytes))),
			TotalRecordCount: len(f.Records),
			SelectedRecordCount: len(f.SelectedRefs),
			SelectedRecordRatio: selectedRatio,
			ExpectedRouteMatched: routing.Route == f.ExpectedRoute,
			LocalModelAllowed: routing.LocalModelAllowed,
			GeneralModelHint: generalHint,
		},
	}, nil
}

func ValidateFixture(f Fixture) error {
	if strings.TrimSpace(f.ID) == "" {
		return fmt.Errorf("fixture id is required")
	}
	if strings.TrimSpace(f.Objective) == "" {
		return fmt.Errorf("fixture %s: objective is required", f.ID)
	}
	if strings.TrimSpace(f.Task) == "" {
		return fmt.Errorf("fixture %s: task is required", f.ID)
	}
	if len(f.RawContext) == 0 {
		return fmt.Errorf("fixture %s: raw context is required", f.ID)
	}
	byRef := map[string]Record{}
	for _, record := range f.Records {
		if record.Ref == "" {
			return fmt.Errorf("fixture %s: record ref is required", f.ID)
		}
		if _, exists := byRef[record.Ref]; exists {
			return fmt.Errorf("fixture %s: duplicate record ref %s", f.ID, record.Ref)
		}
		byRef[record.Ref] = record
	}
	for name, refs := range map[string][]string{
		"selected": f.SelectedRefs,
		"unknown": f.UnknownRefs,
		"conflict": f.ConflictRefs,
		"decision basis": f.DecisionBasisRefs,
	} {
		for _, ref := range refs {
			if _, ok := byRef[ref]; !ok {
				return fmt.Errorf("fixture %s: %s ref %s does not exist", f.ID, name, ref)
			}
		}
	}
	for name, ref := range map[string]string{
		"recommendation": f.RecommendationRef,
		"decision": f.DecisionRef,
	} {
		if ref != "" {
			if _, ok := byRef[ref]; !ok {
				return fmt.Errorf("fixture %s: %s ref %s does not exist", f.ID, name, ref)
			}
		}
	}
	if f.DecisionRef != "" {
		if f.DecidedAt == "" {
			return fmt.Errorf("fixture %s: decided_at is required when decision exists", f.ID)
		}
		if _, err := time.Parse(time.RFC3339, f.DecidedAt); err != nil {
			return fmt.Errorf("fixture %s: invalid decided_at: %w", f.ID, err)
		}
	}
	if f.ExpectedRoute == "" {
		return fmt.Errorf("fixture %s: expected route is required", f.ID)
	}
	return nil
}

func EvaluateOutput(f Fixture, out ModelOutput) (EvaluationReport, error) {
	if err := ValidateFixture(f); err != nil {
		return EvaluationReport{}, err
	}
	byRef := recordMap(f.Records)
	validRef := func(ref string) bool {
		_, ok := byRef[ref]
		return ok
	}

	invalidRefs := 0
	for _, ref := range uniqueStrings(append(append(append(append([]string{}, out.SupportingRefs...), out.DecisionBasisRefs...), out.PreservedUnknownRefs...), out.PreservedConflictRefs...)) {
		if ref != "" && !validRef(ref) {
			invalidRefs++
		}
	}
	for _, ref := range []string{out.RecommendationRef, out.DecisionRef} {
		if ref != "" && !validRef(ref) {
			invalidRefs++
		}
	}

	unsupported := 0
	supportedClaims := 0
	for _, claim := range out.Claims {
		if len(claim.SupportingRefs) == 0 {
			unsupported++
			continue
		}
		allValid := true
		for _, ref := range claim.SupportingRefs {
			if !validRef(ref) {
				allValid = false
				invalidRefs++
			}
		}
		if allValid {
			supportedClaims++
		}
	}

	unknownRate := preservationRate(f.UnknownRefs, out.PreservedUnknownRefs)
	conflictRate := preservationRate(f.ConflictRefs, out.PreservedConflictRefs)

	separated := true
	if f.RecommendationRef != "" && f.DecisionRef != "" {
		separated = out.RecommendationRef == f.RecommendationRef &&
			out.DecisionRef == f.DecisionRef &&
			out.RecommendationRef != out.DecisionRef
	}

	historicalViolations := 0
	if f.DecisionRef != "" {
		allowed := stringSet(f.DecisionBasisRefs)
		decisionTime, _ := time.Parse(time.RFC3339, f.DecidedAt)
		for _, ref := range uniqueStrings(out.DecisionBasisRefs) {
			record, ok := byRef[ref]
			if !ok {
				continue
			}
			if _, ok := allowed[ref]; !ok {
				historicalViolations++
				continue
			}
			if record.CapturedAt != "" {
				captured, err := time.Parse(time.RFC3339, record.CapturedAt)
				if err == nil && captured.After(decisionTime) {
					historicalViolations++
				}
			}
		}
	}

	needsEvidenceRoute := f.ExpectedRoute == hybridreasoning.RouteExpandEvidence ||
		f.ExpectedRoute == hybridreasoning.RouteExternalEvidence
	needMoreAppropriate := true
	if needsEvidenceRoute {
		needMoreAppropriate = out.NeedMoreEvidence
	}

	return EvaluationReport{
		FixtureID: f.ID,
		UnknownPreservationRate: unknownRate,
		ConflictPreservationRate: conflictRate,
		RecommendationDecisionSeparated: separated,
		HistoricalBasisViolationCount: historicalViolations,
		UnsupportedClaimCount: unsupported,
		InvalidReferenceCount: invalidRefs,
		SupportedMaterialClaimCount: supportedClaims,
		NeedMoreEvidenceAppropriate: needMoreAppropriate,
		AllExpectedUnknownsPreserved: unknownRate == 1.0,
		AllExpectedConflictsPreserved: conflictRate == 1.0,
		NoHistoricalBasisViolation: historicalViolations == 0,
		AllMaterialClaimsHaveValidSupport: unsupported == 0 && invalidRefs == 0,
	}, nil
}

func preservationRate(expected, actual []string) float64 {
	if len(expected) == 0 {
		return 1.0
	}
	actualSet := stringSet(actual)
	preserved := 0
	for _, ref := range uniqueStrings(expected) {
		if _, ok := actualSet[ref]; ok {
			preserved++
		}
	}
	return float64(preserved) / float64(len(uniqueStrings(expected)))
}

func recordMap(records []Record) map[string]Record {
	out := make(map[string]Record, len(records))
	for _, record := range records {
		out[record.Ref] = record
	}
	return out
}

func stringSet(values []string) map[string]struct{} {
	out := make(map[string]struct{}, len(values))
	for _, value := range values {
		out[value] = struct{}{}
	}
	return out
}

func uniqueStrings(values []string) []string {
	set := map[string]struct{}{}
	for _, value := range values {
		if value != "" {
			set[value] = struct{}{}
		}
	}
	out := make([]string, 0, len(set))
	for value := range set {
		out = append(out, value)
	}
	sort.Strings(out)
	return out
}

// ReferenceFixtures returns low-risk synthetic cases that exercise SEI
// Cognition-specific boundaries. They are mechanics fixtures, not adoption or
// outcome evidence.
func ReferenceFixtures() []Fixture {
	return []Fixture{
		{
			ID: "decisionless-inquiry",
			Objective: "Choose whether to continue evaluating a local-first note workflow.",
			Task: "compare",
			RawContext: []string{
				"The workflow can export plain files and works offline.",
				"The user has not yet measured reopen effort after a week.",
				"No decision has been made.",
			},
			Records: []Record{
				{Ref: "obs-1", Kind: "observation", Summary: "Plain-file export and offline read are available."},
				{Ref: "unk-1", Kind: "unknown", Summary: "Seven-day reopen effort has not been measured."},
			},
			SelectedRefs: []string{"obs-1", "unk-1"},
			UnknownRefs: []string{"unk-1"},
			Constraints: []string{"Do not invent a Decision."},
			RouteContext: hybridreasoning.RoutingContext{NoveltySignal: 0.25},
			ExpectedRoute: hybridreasoning.RouteLocalSLM,
		},
		{
			ID: "decision-with-unknown",
			Objective: "Reassess an existing local deployment choice without erasing unresolved risk.",
			Task: "synthesize",
			RawContext: []string{
				"A local deployment was chosen because it remains readable offline.",
				"Long-term migration cost remains unknown.",
				"The decision was made on 2026-09-01.",
			},
			Records: []Record{
				{Ref: "obs-2", Kind: "observation", Summary: "Offline readability was verified.", CapturedAt: "2026-08-30T10:00:00Z"},
				{Ref: "unk-2", Kind: "unknown", Summary: "Long-term migration cost is unknown.", CapturedAt: "2026-08-31T10:00:00Z"},
				{Ref: "dec-2", Kind: "decision", Summary: "Use the local deployment for the evaluation period.", CapturedAt: "2026-09-01T09:00:00Z"},
			},
			SelectedRefs: []string{"obs-2", "unk-2", "dec-2"},
			UnknownRefs: []string{"unk-2"},
			DecisionRef: "dec-2",
			DecisionBasisRefs: []string{"obs-2", "unk-2"},
			DecidedAt: "2026-09-01T09:00:00Z",
			RouteContext: hybridreasoning.RoutingContext{NoveltySignal: 0.20},
			ExpectedRoute: hybridreasoning.RouteLocalSLM,
		},
		{
			ID: "recommendation-not-decision",
			Objective: "Compare the current recommendation with the user's recorded decision.",
			Task: "compare",
			RawContext: []string{
				"The system recommended option B after a latency test.",
				"The user chose option A because portability was more important.",
			},
			Records: []Record{
				{Ref: "obs-3", Kind: "observation", Summary: "Option B had lower measured latency."},
				{Ref: "rec-3", Kind: "recommendation", Summary: "Prefer option B for latency."},
				{Ref: "dec-3", Kind: "decision", Summary: "Use option A because portability dominates latency."},
			},
			SelectedRefs: []string{"obs-3", "rec-3", "dec-3"},
			RecommendationRef: "rec-3",
			DecisionRef: "dec-3",
			DecisionBasisRefs: []string{"obs-3"},
			DecidedAt: "2026-09-02T09:00:00Z",
			RouteContext: hybridreasoning.RoutingContext{NoveltySignal: 0.15},
			ExpectedRoute: hybridreasoning.RouteLocalSLM,
		},
		{
			ID: "late-arriving-evidence",
			Objective: "Explain what changed after a historical Decision without rewriting its basis.",
			Task: "explain",
			RawContext: []string{
				"On September 2 the user decided using evidence then available.",
				"A price change had actually taken effect on September 1 but was only discovered on September 5.",
			},
			Records: []Record{
				{Ref: "obs-4a", Kind: "observation", Summary: "The known cost was within budget at decision time.", CapturedAt: "2026-09-02T08:00:00Z", SubjectAt: "2026-09-02T08:00:00Z"},
				{Ref: "dec-4", Kind: "decision", Summary: "Proceed under the known cost assumption.", CapturedAt: "2026-09-02T09:00:00Z"},
				{Ref: "obs-4b", Kind: "observation", Summary: "A price increase had become valid earlier but was discovered later.", CapturedAt: "2026-09-05T10:00:00Z", SubjectAt: "2026-09-01T00:00:00Z"},
			},
			SelectedRefs: []string{"obs-4a", "dec-4", "obs-4b"},
			DecisionRef: "dec-4",
			DecisionBasisRefs: []string{"obs-4a"},
			DecidedAt: "2026-09-02T09:00:00Z",
			Constraints: []string{"Later-captured evidence must not be added retroactively to the historical Decision basis."},
			RouteContext: hybridreasoning.RoutingContext{NoveltySignal: 0.25},
			ExpectedRoute: hybridreasoning.RouteLocalSLM,
		},
		{
			ID: "current-external-fact",
			Objective: "Determine the current status of an external service before making a recommendation.",
			Task: "synthesize",
			RawContext: []string{
				"The last saved status is one week old.",
				"A current external fact is required before answering.",
			},
			Records: []Record{
				{Ref: "obs-5", Kind: "observation", Summary: "Saved service status is one week old."},
				{Ref: "unk-5", Kind: "unknown", Summary: "Current service status is unknown."},
			},
			SelectedRefs: []string{"obs-5", "unk-5"},
			UnknownRefs: []string{"unk-5"},
			RouteContext: hybridreasoning.RoutingContext{RequiresCurrentExternalFact: true, NoveltySignal: 0.30},
			ExpectedRoute: hybridreasoning.RouteExternalEvidence,
		},
		{
			ID: "high-novelty",
			Objective: "Assess an unfamiliar incident pattern without filling missing evidence by model guess.",
			Task: "hypothesize",
			RawContext: []string{
				"The incident pattern has no close prior case.",
				"The available evidence is sparse and contradictory.",
			},
			Records: []Record{
				{Ref: "obs-6", Kind: "observation", Summary: "Observed signals do not match known incident patterns."},
				{Ref: "conf-6", Kind: "conflict", Summary: "Two available logs disagree about the event order."},
			},
			SelectedRefs: []string{"obs-6", "conf-6"},
			ConflictRefs: []string{"conf-6"},
			RouteContext: hybridreasoning.RoutingContext{NoveltySignal: 0.92},
			ExpectedRoute: hybridreasoning.RouteExpandEvidence,
		},
		{
			ID: "deterministic",
			Objective: "Validate whether a Decision basis contains a post-decision observation.",
			Task: "historical-basis-check",
			RawContext: []string{
				"The rule is deterministic: evidence captured after the Decision cannot be historical basis.",
			},
			Records: []Record{
				{Ref: "rule-7", Kind: "constraint", Summary: "Post-decision captured evidence cannot be historical basis."},
			},
			SelectedRefs: []string{"rule-7"},
			RouteContext: hybridreasoning.RoutingContext{DeterministicAnswerAvailable: true},
			ExpectedRoute: hybridreasoning.RouteSymbolic,
		},
	}
}
