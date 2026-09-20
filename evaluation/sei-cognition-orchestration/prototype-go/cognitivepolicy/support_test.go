package cognitivepolicy

import (
	"reflect"
	"testing"
)

func supportDefinitions() []ProblemPolicy {
	return []ProblemPolicy{
		{
			ProblemClass: "routine-summary",
			StaticRoute:  "general-llm",
			AllowedRoutes: []RouteOption{
				{ID: "local-slm", EscalationLevel: 1},
				{ID: "general-llm", EscalationLevel: 2},
			},
			RequiredSuccessRate:     0.5,
			MinAssessedObservations: 1,
		},
	}
}

func supportRecord(route string, outcome CognitiveOutcome, version, provenance string) OutcomeRecord {
	return OutcomeRecord{
		ProblemClass:          "routine-summary",
		Route:                 route,
		CognitiveOutcome:      outcome,
		ExecutionOutcome:      ExecutionCompleted,
		ProvenanceRef:         provenance,
		ObservedPolicyVersion: version,
	}
}

func TestObservationalSupportReportsCompleteCoverageWithoutClaimingCorrection(t *testing.T) {
	store, err := NewStore(supportDefinitions())
	if err != nil {
		t.Fatal(err)
	}
	diagnostics, err := store.DiagnoseObservationalSupport([]OutcomeRecord{
		supportRecord("local-slm", CognitiveSufficient, BaselineVersion, "fixture:local"),
		supportRecord("general-llm", CognitiveSufficient, BaselineVersion, "fixture:general"),
	})
	if err != nil {
		t.Fatal(err)
	}
	got := diagnostics["routine-summary"]
	if !got.AllAllowedRoutesAssessed {
		t.Fatalf("expected descriptive full route coverage: %#v", got)
	}
	if got.SelectionBiasCorrected {
		t.Fatal("full route coverage must not claim selection-bias correction")
	}
	if got.TotalAssessed != 2 || got.TotalNotAssessed != 0 {
		t.Fatalf("unexpected totals: %#v", got)
	}
	if !reflect.DeepEqual(got.RoutesWithAssessed, []string{"general-llm", "local-slm"}) {
		t.Fatalf("routes with assessed=%v", got.RoutesWithAssessed)
	}
	if len(got.RoutesWithoutAssessed) != 0 {
		t.Fatalf("unexpected missing routes: %v", got.RoutesWithoutAssessed)
	}
}

func TestObservationalSupportFlagsMissingAssessedRoute(t *testing.T) {
	store, _ := NewStore(supportDefinitions())
	diagnostics, err := store.DiagnoseObservationalSupport([]OutcomeRecord{
		supportRecord("local-slm", CognitiveSufficient, BaselineVersion, "fixture:local"),
	})
	if err != nil {
		t.Fatal(err)
	}
	got := diagnostics["routine-summary"]
	if got.AllAllowedRoutesAssessed {
		t.Fatal("missing route support must not be reported as complete")
	}
	if !reflect.DeepEqual(got.RoutesWithoutAssessed, []string{"general-llm"}) {
		t.Fatalf("missing routes=%v", got.RoutesWithoutAssessed)
	}
	if got.Routes["general-llm"].Assessed != 0 {
		t.Fatalf("unobserved route unexpectedly assessed: %#v", got.Routes["general-llm"])
	}
}

func TestObservationalSupportDoesNotCountNotAssessedAsAssessed(t *testing.T) {
	store, _ := NewStore(supportDefinitions())
	diagnostics, err := store.DiagnoseObservationalSupport([]OutcomeRecord{
		supportRecord("local-slm", CognitiveNotAssessed, BaselineVersion, "fixture:not-assessed-1"),
		supportRecord("local-slm", CognitiveNotAssessed, BaselineVersion, "fixture:not-assessed-2"),
		supportRecord("general-llm", CognitiveSufficient, BaselineVersion, "fixture:general"),
	})
	if err != nil {
		t.Fatal(err)
	}
	got := diagnostics["routine-summary"]
	local := got.Routes["local-slm"]
	if local.Assessed != 0 || local.NotAssessed != 2 {
		t.Fatalf("not-assessed observations crossed support boundary: %#v", local)
	}
	if !reflect.DeepEqual(got.RoutesWithoutAssessed, []string{"local-slm"}) {
		t.Fatalf("missing routes=%v", got.RoutesWithoutAssessed)
	}
}

func TestObservationalSupportDeduplicatesAndSortsPolicyVersions(t *testing.T) {
	store, _ := NewStore(supportDefinitions())
	candidate, err := store.BuildCandidate([]OutcomeRecord{
		supportRecord("local-slm", CognitiveSufficient, BaselineVersion, "fixture:candidate"),
	})
	if err != nil {
		t.Fatal(err)
	}
	diagnostics, err := store.DiagnoseObservationalSupport([]OutcomeRecord{
		supportRecord("local-slm", CognitiveSufficient, candidate.Version, "fixture:v1-a"),
		supportRecord("local-slm", CognitiveSufficient, BaselineVersion, "fixture:v0"),
		supportRecord("local-slm", CognitiveInsufficient, candidate.Version, "fixture:v1-b"),
		supportRecord("general-llm", CognitiveSufficient, BaselineVersion, "fixture:general"),
	})
	if err != nil {
		t.Fatal(err)
	}
	got := diagnostics["routine-summary"]
	if !reflect.DeepEqual(got.ObservedPolicyVersions, []string{"v0", "v1"}) {
		t.Fatalf("problem policy versions=%v", got.ObservedPolicyVersions)
	}
	if !reflect.DeepEqual(got.Routes["local-slm"].ObservedPolicyVersions, []string{"v0", "v1"}) {
		t.Fatalf("route policy versions=%v", got.Routes["local-slm"].ObservedPolicyVersions)
	}
	if got.SelectionBiasCorrected {
		t.Fatal("policy-version diversity must not claim randomized assignment or correction")
	}
}

func TestObservationalSupportRejectsInvalidOutcomeRecords(t *testing.T) {
	store, _ := NewStore(supportDefinitions())
	_, err := store.DiagnoseObservationalSupport([]OutcomeRecord{
		supportRecord("unknown-route", CognitiveSufficient, BaselineVersion, "fixture:invalid"),
	})
	if err == nil {
		t.Fatal("invalid outcome record must fail closed")
	}
}

func TestObservationalSupportZeroRecordsMarksAllAllowedRoutesMissing(t *testing.T) {
	store, _ := NewStore(supportDefinitions())
	diagnostics, err := store.DiagnoseObservationalSupport(nil)
	if err != nil {
		t.Fatal(err)
	}
	got := diagnostics["routine-summary"]
	if got.AllAllowedRoutesAssessed || got.TotalAssessed != 0 {
		t.Fatalf("zero records unexpectedly produced support: %#v", got)
	}
	if !reflect.DeepEqual(got.RoutesWithoutAssessed, []string{"general-llm", "local-slm"}) {
		t.Fatalf("missing routes=%v", got.RoutesWithoutAssessed)
	}
	if len(got.ObservedPolicyVersions) != 0 {
		t.Fatalf("unexpected policy versions=%v", got.ObservedPolicyVersions)
	}
}

func TestObservationalSupportDoesNotMutateActivePolicy(t *testing.T) {
	store, _ := NewStore(supportDefinitions())
	candidate, err := store.BuildCandidate([]OutcomeRecord{
		supportRecord("local-slm", CognitiveSufficient, BaselineVersion, "fixture:candidate"),
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := store.Activate(candidate.Version); err != nil {
		t.Fatal(err)
	}
	before := store.ActiveVersion()
	if _, err := store.DiagnoseObservationalSupport([]OutcomeRecord{
		supportRecord("local-slm", CognitiveSufficient, BaselineVersion, "fixture:local"),
		supportRecord("general-llm", CognitiveSufficient, BaselineVersion, "fixture:general"),
	}); err != nil {
		t.Fatal(err)
	}
	if store.ActiveVersion() != before {
		t.Fatalf("diagnostic mutated active policy: before=%s after=%s", before, store.ActiveVersion())
	}
}
