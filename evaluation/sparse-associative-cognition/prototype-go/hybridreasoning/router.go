// Package hybridreasoning defines evaluation-only routing and bounded working
// sets for combining sparse-associative recall with a lightweight local SLM.
// It does not invoke a model and does not grant generated output canonical
// SEI authority.
package hybridreasoning

import (
	"sort"
	"strings"
)

type Route string

const (
	RouteSymbolic              Route = "symbolic"
	RouteNonLLMRecall          Route = "non-llm-recall"
	RouteLocalSLM              Route = "local-slm"
	RouteAbstain               Route = "abstain"
	RouteExpandEvidence        Route = "abstain-or-expand-evidence"
	RouteExternalEvidence      Route = "external-evidence-required"
	RouteHumanOrStrongerReview Route = "human-or-stronger-review"
)

type Candidate struct {
	Ref        string         `json:"candidate_ref"`
	Activation float32        `json:"retrieval_activation"`
	Meaning    map[string]any `json:"meaning"`
}

type RoutingContext struct {
	Task                         string
	CandidateCount               int
	NoveltySignal                float32
	HighStakes                   bool
	RequiresCurrentExternalFact  bool
	DeterministicAnswerAvailable bool
	MaxLocalNovelty              float32
}

type RoutingDecision struct {
	Route                 Route  `json:"route"`
	Reason                string `json:"reason"`
	LocalModelAllowed     bool   `json:"local_model_allowed"`
	CanonicalWriteAllowed bool   `json:"canonical_write_allowed"`
}

var symbolicTasks = map[string]struct{}{
	"validate": {}, "exact-lookup": {}, "schema-check": {},
	"constraint-check": {}, "historical-basis-check": {},
}

var recallTasks = map[string]struct{}{
	"recall": {}, "find-related": {}, "rank-candidates": {},
}

var localReasoningTasks = map[string]struct{}{
	"compare": {}, "synthesize": {}, "hypothesize": {}, "explain": {},
	"plan": {}, "interpret": {}, "contradiction-analysis": {},
}

func RouteReasoning(ctx RoutingContext) RoutingDecision {
	task := strings.ToLower(strings.TrimSpace(ctx.Task))
	maxNovelty := ctx.MaxLocalNovelty
	if maxNovelty <= 0 {
		maxNovelty = 0.70
	}

	if ctx.DeterministicAnswerAvailable {
		return RoutingDecision{Route: RouteSymbolic, Reason: "deterministic processing is sufficient"}
	}
	if _, ok := symbolicTasks[task]; ok {
		return RoutingDecision{Route: RouteSymbolic, Reason: "task is owned by symbolic validation"}
	}
	if _, ok := recallTasks[task]; ok {
		return RoutingDecision{Route: RouteNonLLMRecall, Reason: "requested output is candidate retrieval"}
	}
	if ctx.HighStakes {
		return RoutingDecision{Route: RouteHumanOrStrongerReview, Reason: "high-stakes use is outside autonomous local reasoning"}
	}
	if ctx.RequiresCurrentExternalFact {
		return RoutingDecision{Route: RouteExternalEvidence, Reason: "current external evidence must be acquired rather than generated"}
	}
	if _, ok := localReasoningTasks[task]; !ok {
		return RoutingDecision{Route: RouteAbstain, Reason: "task has no validated local-reasoning route"}
	}
	if ctx.CandidateCount <= 0 {
		return RoutingDecision{Route: RouteAbstain, Reason: "no bounded evidence working set is available"}
	}
	if ctx.NoveltySignal > maxNovelty {
		return RoutingDecision{Route: RouteExpandEvidence, Reason: "retrieval novelty is too high for bounded local reasoning"}
	}
	return RoutingDecision{
		Route: RouteLocalSLM, Reason: "bounded evidence exists and synthesis is required",
		LocalModelAllowed: true,
	}
}

type SemanticBoundary struct {
	OutputIsProposalOnly                        bool `json:"output_is_proposal_only"`
	MayNotRewriteHistoricalBasis               bool `json:"may_not_rewrite_historical_basis"`
	RecommendationIsNotDecision                bool `json:"recommendation_is_not_decision"`
	MustPreserveUnknownAndConflict             bool `json:"must_preserve_unknown_and_conflict"`
	MustCiteCandidateRefsForMaterialClaims     bool `json:"must_cite_candidate_refs_for_material_claims"`
	CanonicalWriteRequiresValidationOrHumanAct bool `json:"canonical_write_requires_validation_or_human_action"`
}

type RequestedOutput struct {
	Proposal                string `json:"proposal"`
	SupportingCandidateRefs string `json:"supporting_candidate_refs"`
	Unresolved              string `json:"unresolved"`
	NeedMoreEvidence        string `json:"need_more_evidence"`
}

type WorkingSet struct {
	Schema           string           `json:"schema"`
	Status           string           `json:"status"`
	Task             string           `json:"task"`
	Inquiry          string           `json:"inquiry"`
	SemanticBoundary SemanticBoundary `json:"semantic_boundary"`
	Candidates       []Candidate      `json:"working_set"`
	Unresolved       []map[string]any `json:"unresolved,omitempty"`
	Constraints      []string         `json:"constraints,omitempty"`
	RequestedOutput  RequestedOutput  `json:"requested_output"`
}

type WorkingSetOptions struct {
	MaxCandidates int
	MaxTextChars  int
}

func BuildWorkingSet(inquiry, task string, candidates []Candidate, unresolved []map[string]any, constraints []string, opts WorkingSetOptions) WorkingSet {
	maxCandidates := opts.MaxCandidates
	if maxCandidates <= 0 {
		maxCandidates = 8
	}
	maxTextChars := opts.MaxTextChars
	if maxTextChars < 64 {
		maxTextChars = 1200
	}

	ranked := append([]Candidate(nil), candidates...)
	sort.SliceStable(ranked, func(i, j int) bool {
		if ranked[i].Activation == ranked[j].Activation {
			return ranked[i].Ref < ranked[j].Ref
		}
		return ranked[i].Activation > ranked[j].Activation
	})
	if len(ranked) > maxCandidates {
		ranked = ranked[:maxCandidates]
	}
	bounded := make([]Candidate, len(ranked))
	for i, candidate := range ranked {
		bounded[i] = Candidate{
			Ref: candidate.Ref, Activation: candidate.Activation,
			Meaning: cloneBoundedMap(candidate.Meaning, maxTextChars),
		}
	}

	boundedUnresolved := make([]map[string]any, len(unresolved))
	for i, item := range unresolved {
		boundedUnresolved[i] = cloneBoundedMap(item, maxTextChars)
	}
	boundedConstraints := make([]string, len(constraints))
	for i, item := range constraints {
		boundedConstraints[i] = clipString(item, maxTextChars)
	}

	return WorkingSet{
		Schema: "sei.local-reasoning-working-set/v0", Status: "evaluation-only",
		Task: task, Inquiry: clipString(inquiry, maxTextChars),
		SemanticBoundary: SemanticBoundary{
			OutputIsProposalOnly: true,
			MayNotRewriteHistoricalBasis: true,
			RecommendationIsNotDecision: true,
			MustPreserveUnknownAndConflict: true,
			MustCiteCandidateRefsForMaterialClaims: true,
			CanonicalWriteRequiresValidationOrHumanAct: true,
		},
		Candidates: bounded, Unresolved: boundedUnresolved, Constraints: boundedConstraints,
		RequestedOutput: RequestedOutput{
			Proposal: "reasoned candidate answer, comparison, hypothesis, or plan",
			SupportingCandidateRefs: "candidate_ref values actually used",
			Unresolved: "remaining uncertainty or conflict",
			NeedMoreEvidence: "true when the bounded working set is insufficient",
		},
	}
}

func cloneBoundedMap(in map[string]any, limit int) map[string]any {
	if in == nil {
		return nil
	}
	out := make(map[string]any, len(in))
	for key, value := range in {
		out[key] = cloneBounded(value, limit)
	}
	return out
}

func cloneBounded(value any, limit int) any {
	switch v := value.(type) {
	case nil, bool, int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64, float32, float64:
		return v
	case string:
		return clipString(v, limit)
	case map[string]any:
		return cloneBoundedMap(v, limit)
	case []any:
		out := make([]any, len(v))
		for i, item := range v {
			out[i] = cloneBounded(item, limit)
		}
		return out
	case []map[string]any:
		out := make([]map[string]any, len(v))
		for i, item := range v {
			out[i] = cloneBoundedMap(item, limit)
		}
		return out
	case []string:
		out := make([]string, len(v))
		for i, item := range v {
			out[i] = clipString(item, limit)
		}
		return out
	default:
		return v
	}
}

func clipString(value string, limit int) string {
	runes := []rune(value)
	if len(runes) <= limit {
		return value
	}
	if limit <= 1 {
		return "…"
	}
	return string(runes[:limit-1]) + "…"
}
