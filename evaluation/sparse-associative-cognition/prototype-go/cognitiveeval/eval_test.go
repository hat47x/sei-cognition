package cognitiveeval

import (
	"math"
	"testing"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/hybridreasoning"
)

func fixtureByID(t *testing.T, id string) Fixture {
	t.Helper()
	for _, f := range ReferenceFixtures() {
		if f.ID == id {
			return f
		}
	}
	t.Fatalf("fixture not found: %s", id)
	return Fixture{}
}

func TestReferenceFixturesBuildAndRoute(t *testing.T) {
	fixtures := ReferenceFixtures()
	if len(fixtures) != 7 {
		t.Fatalf("expected 7 reference fixtures, got %d", len(fixtures))
	}
	for _, f := range fixtures {
		bundle, err := BuildComparisonBundle(f)
		if err != nil {
			t.Fatalf("%s: build bundle: %v", f.ID, err)
		}
		if !bundle.Stats.ExpectedRouteMatched {
			t.Fatalf("%s: route=%s want=%s", f.ID, bundle.Staged.Routing.Route, f.ExpectedRoute)
		}
		if bundle.Raw.Context == "" {
			t.Fatalf("%s: raw baseline context must not be empty", f.ID)
		}
		if !bundle.Workspace.SemanticBoundary.OutputIsProposalOnly {
			t.Fatalf("%s: workspace must keep proposal-only boundary", f.ID)
		}
		if !bundle.Workspace.SemanticBoundary.MustPreserveUnknownAndConflict {
			t.Fatalf("%s: workspace must preserve Unknown/Conflict boundary", f.ID)
		}
		if bundle.Stats.SelectedRecordCount > bundle.Stats.TotalRecordCount {
			t.Fatalf("%s: selected records exceed universe", f.ID)
		}
	}
}

func TestDecisionlessInquiryDoesNotInventDecision(t *testing.T) {
	f := fixtureByID(t, "decisionless-inquiry")
	bundle, err := BuildComparisonBundle(f)
	if err != nil {
		t.Fatal(err)
	}
	if bundle.Staged.Routing.Route != hybridreasoning.RouteLocalSLM {
		t.Fatalf("route=%s", bundle.Staged.Routing.Route)
	}
	if f.DecisionRef != "" {
		t.Fatal("decisionless fixture unexpectedly has a Decision")
	}
	if len(bundle.Workspace.Unresolved) != 1 {
		t.Fatalf("expected one unresolved item, got %d", len(bundle.Workspace.Unresolved))
	}
}

func TestCurrentExternalFactRoutesToEvidenceNotModelMemory(t *testing.T) {
	f := fixtureByID(t, "current-external-fact")
	bundle, err := BuildComparisonBundle(f)
	if err != nil {
		t.Fatal(err)
	}
	if bundle.Staged.Routing.Route != hybridreasoning.RouteExternalEvidence {
		t.Fatalf("route=%s", bundle.Staged.Routing.Route)
	}
	if bundle.Staged.Routing.LocalModelAllowed {
		t.Fatal("local model must not be allowed to fill current external fact")
	}
	if !bundle.Staged.HeavyCognitionOrEvidenceNeed {
		t.Fatal("external evidence need should be explicit")
	}
}

func TestHighNoveltyRoutesToEvidenceExpansion(t *testing.T) {
	f := fixtureByID(t, "high-novelty")
	bundle, err := BuildComparisonBundle(f)
	if err != nil {
		t.Fatal(err)
	}
	if bundle.Staged.Routing.Route != hybridreasoning.RouteExpandEvidence {
		t.Fatalf("route=%s", bundle.Staged.Routing.Route)
	}
	if bundle.Staged.Routing.LocalModelAllowed {
		t.Fatal("high-novelty case must not guess with local model")
	}
}

func TestDeterministicCaseAvoidsGenerativeRoute(t *testing.T) {
	f := fixtureByID(t, "deterministic")
	bundle, err := BuildComparisonBundle(f)
	if err != nil {
		t.Fatal(err)
	}
	if bundle.Staged.Routing.Route != hybridreasoning.RouteSymbolic {
		t.Fatalf("route=%s", bundle.Staged.Routing.Route)
	}
	if bundle.Stats.GeneralModelHint || bundle.Stats.LocalModelAllowed {
		t.Fatal("deterministic case should not require a generative model")
	}
}

func TestRecommendationDecisionSeparationCanBeEvaluated(t *testing.T) {
	f := fixtureByID(t, "recommendation-not-decision")
	out := ModelOutput{
		Proposal: "Latency favors B, but the recorded user Decision remains A.",
		SupportingRefs: []string{"obs-3", "rec-3", "dec-3"},
		DecisionBasisRefs: []string{"obs-3"},
		RecommendationRef: "rec-3",
		DecisionRef: "dec-3",
		Claims: []Claim{
			{Text: "Option B had lower measured latency.", SupportingRefs: []string{"obs-3"}},
		},
	}
	report, err := EvaluateOutput(f, out)
	if err != nil {
		t.Fatal(err)
	}
	if !report.RecommendationDecisionSeparated {
		t.Fatal("Recommendation and Decision should remain separated")
	}
	if !report.NoHistoricalBasisViolation {
		t.Fatalf("unexpected historical violation: %d", report.HistoricalBasisViolationCount)
	}
	if !report.AllMaterialClaimsHaveValidSupport {
		t.Fatal("supported claim should pass evidence discipline")
	}
}

func TestLateArrivingEvidenceCannotBecomeHistoricalBasis(t *testing.T) {
	f := fixtureByID(t, "late-arriving-evidence")
	out := ModelOutput{
		Proposal: "The later price evidence changes current understanding.",
		SupportingRefs: []string{"obs-4a", "obs-4b"},
		DecisionBasisRefs: []string{"obs-4a", "obs-4b"},
		DecisionRef: "dec-4",
		Claims: []Claim{
			{Text: "A price increase was discovered later.", SupportingRefs: []string{"obs-4b"}},
		},
	}
	report, err := EvaluateOutput(f, out)
	if err != nil {
		t.Fatal(err)
	}
	if report.HistoricalBasisViolationCount != 1 {
		t.Fatalf("historical violations=%d want=1", report.HistoricalBasisViolationCount)
	}
	if report.NoHistoricalBasisViolation {
		t.Fatal("late-arriving evidence must not pass as historical basis")
	}
}

func TestUnknownConflictAndEvidenceDiscipline(t *testing.T) {
	f := fixtureByID(t, "high-novelty")
	bad := ModelOutput{
		Proposal: "The incident is definitely caused by X.",
		NeedMoreEvidence: false,
		Claims: []Claim{
			{Text: "X is the cause."},
			{Text: "A nonexistent record proves it.", SupportingRefs: []string{"missing-ref"}},
		},
	}
	report, err := EvaluateOutput(f, bad)
	if err != nil {
		t.Fatal(err)
	}
	if report.ConflictPreservationRate != 0 {
		t.Fatalf("conflict preservation=%f want=0", report.ConflictPreservationRate)
	}
	if report.NeedMoreEvidenceAppropriate {
		t.Fatal("high-novelty output should acknowledge need for more evidence")
	}
	if report.UnsupportedClaimCount != 1 {
		t.Fatalf("unsupported claims=%d want=1", report.UnsupportedClaimCount)
	}
	if report.InvalidReferenceCount != 1 {
		t.Fatalf("invalid refs=%d want=1", report.InvalidReferenceCount)
	}
	if report.AllMaterialClaimsHaveValidSupport {
		t.Fatal("bad evidence discipline must fail")
	}
}

func TestPreservationRateIsIndependentPerBoundary(t *testing.T) {
	f := Fixture{
		ID: "mixed-unresolved",
		Objective: "Preserve independent uncertainty boundaries.",
		Task: "compare",
		RawContext: []string{"Two unknowns and one conflict remain."},
		Records: []Record{
			{Ref: "u1", Kind: "unknown", Summary: "u1"},
			{Ref: "u2", Kind: "unknown", Summary: "u2"},
			{Ref: "c1", Kind: "conflict", Summary: "c1"},
		},
		SelectedRefs: []string{"u1", "u2", "c1"},
		UnknownRefs: []string{"u1", "u2"},
		ConflictRefs: []string{"c1"},
		RouteContext: hybridreasoning.RoutingContext{NoveltySignal: 0.2},
		ExpectedRoute: hybridreasoning.RouteLocalSLM,
	}
	report, err := EvaluateOutput(f, ModelOutput{
		PreservedUnknownRefs: []string{"u1"},
		PreservedConflictRefs: []string{"c1"},
	})
	if err != nil {
		t.Fatal(err)
	}
	if math.Abs(report.UnknownPreservationRate-0.5) > 0.0001 {
		t.Fatalf("unknown rate=%f want=0.5", report.UnknownPreservationRate)
	}
	if report.ConflictPreservationRate != 1.0 {
		t.Fatalf("conflict rate=%f want=1", report.ConflictPreservationRate)
	}
}

func TestFixtureValidationRejectsUnknownReference(t *testing.T) {
	f := fixtureByID(t, "decisionless-inquiry")
	f.SelectedRefs = append(f.SelectedRefs, "missing")
	if _, err := BuildComparisonBundle(f); err == nil {
		t.Fatal("expected validation error")
	}
}
