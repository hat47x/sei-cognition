package capacityprofile

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"testing"
)

type b6iGovernanceFixture struct {
	EnvelopeID             string            `json:"envelope_id"`
	RequiredClassPolicyMap map[string]string `json:"required_class_policy_map"`
	Classes                []struct {
		ClassID             string `json:"class_id"`
		PolicyID            string `json:"policy_id"`
		Version             int    `json:"version"`
		State               string `json:"state"`
		ResolutionAllowed   bool   `json:"resolution_allowed"`
		SupersededByVersion *int   `json:"superseded_by_version"`
	} `json:"classes"`
}

func governedTestEnvelope(t *testing.T) *WorkloadPolicyEnvelope {
	t.Helper()
	envelope, err := NewWorkloadPolicyEnvelope(
		"b6g-grid-eval-v1",
		"evidence://b6g/workload-policy-envelope",
		[]WorkloadPolicyBinding{
			{WorkloadClass: "general", Policy: ResidualPolicyCap128},
			{WorkloadClass: "structure-preserving", Policy: ResidualPolicyBaseline},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return envelope
}

func reviewedDeclaration(class string, policy ResidualPolicyID) GovernedWorkloadDeclaration {
	return GovernedWorkloadDeclaration{
		WorkloadClass:     class,
		Policy:            policy,
		Version:           1,
		State:             "reviewed",
		ResolutionAllowed: true,
		GovernanceRef:     "evidence://b6i/reviewed-snapshot",
	}
}

func TestResolveGovernedAdmitsReviewedMatchingDeclaration(t *testing.T) {
	envelope := governedTestEnvelope(t)
	got, err := envelope.ResolveGoverned(reviewedDeclaration("general", ResidualPolicyCap128))
	if err != nil {
		t.Fatal(err)
	}
	if got != ResidualPolicyCap128 {
		t.Fatalf("resolved policy=%q want %q", got, ResidualPolicyCap128)
	}
}

func TestResolveGovernedRejectsNonReviewedStates(t *testing.T) {
	envelope := governedTestEnvelope(t)
	for _, state := range []string{"candidate", "expired", "superseded", ""} {
		t.Run(state, func(t *testing.T) {
			decl := reviewedDeclaration("general", ResidualPolicyCap128)
			decl.State = state
			if _, err := envelope.ResolveGoverned(decl); err == nil {
				t.Fatalf("state %q must fail closed", state)
			}
		})
	}
}

func TestResolveGovernedRequiresResolutionAllowed(t *testing.T) {
	envelope := governedTestEnvelope(t)
	decl := reviewedDeclaration("general", ResidualPolicyCap128)
	decl.ResolutionAllowed = false
	if _, err := envelope.ResolveGoverned(decl); err == nil {
		t.Fatal("non-resolution-allowed declaration must fail closed")
	}
}

func TestResolveGovernedRejectsSupersededSnapshot(t *testing.T) {
	envelope := governedTestEnvelope(t)
	decl := reviewedDeclaration("general", ResidualPolicyCap128)
	v2 := 2
	decl.SupersededByVersion = &v2
	if _, err := envelope.ResolveGoverned(decl); err == nil {
		t.Fatal("superseded declaration must fail closed")
	}
}

func TestResolveGovernedRequiresPositiveVersionAndGovernanceRef(t *testing.T) {
	envelope := governedTestEnvelope(t)
	for _, mutate := range []func(*GovernedWorkloadDeclaration){
		func(d *GovernedWorkloadDeclaration) { d.Version = 0 },
		func(d *GovernedWorkloadDeclaration) { d.GovernanceRef = "" },
		func(d *GovernedWorkloadDeclaration) { d.GovernanceRef = " governance://invalid" },
	} {
		decl := reviewedDeclaration("general", ResidualPolicyCap128)
		mutate(&decl)
		if _, err := envelope.ResolveGoverned(decl); err == nil {
			t.Fatalf("invalid declaration must fail closed: %+v", decl)
		}
	}
}

func TestResolveGovernedRejectsPolicyMismatch(t *testing.T) {
	envelope := governedTestEnvelope(t)
	decl := reviewedDeclaration("general", ResidualPolicyBaseline)
	if _, err := envelope.ResolveGoverned(decl); err == nil {
		t.Fatal("declaration policy mismatch must fail closed")
	}
}

func TestResolveGovernedRejectsUnknownClass(t *testing.T) {
	envelope := governedTestEnvelope(t)
	decl := reviewedDeclaration("unknown", ResidualPolicyCap128)
	if _, err := envelope.ResolveGoverned(decl); err == nil {
		t.Fatal("unknown class must fail closed")
	}
}

func TestResolveGovernedRejectsUnsupportedPolicy(t *testing.T) {
	envelope := governedTestEnvelope(t)
	decl := reviewedDeclaration("general", ResidualPolicyID("cap96"))
	if _, err := envelope.ResolveGoverned(decl); err == nil {
		t.Fatal("unsupported policy must fail closed")
	}
}

func TestCurrentB6iCandidateDeclarationsCannotReachResolver(t *testing.T) {
	_, thisFile, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("runtime.Caller failed")
	}
	manifestPath := filepath.Clean(filepath.Join(
		filepath.Dir(thisFile),
		"..", "..", "workload-class-governance", "governance.json",
	))
	raw, err := os.ReadFile(manifestPath)
	if err != nil {
		t.Fatal(err)
	}
	var fixture b6iGovernanceFixture
	if err := json.Unmarshal(raw, &fixture); err != nil {
		t.Fatal(err)
	}
	if fixture.EnvelopeID != "b6g-grid-eval-v1" {
		t.Fatalf("envelope id=%q", fixture.EnvelopeID)
	}

	envelope := governedTestEnvelope(t)
	for _, entry := range fixture.Classes {
		decl := GovernedWorkloadDeclaration{
			WorkloadClass:       entry.ClassID,
			Policy:              ResidualPolicyID(entry.PolicyID),
			Version:             entry.Version,
			State:               entry.State,
			ResolutionAllowed:   entry.ResolutionAllowed,
			SupersededByVersion: entry.SupersededByVersion,
			GovernanceRef:       "file://workload-class-governance/governance.json",
		}
		if _, err := envelope.ResolveGoverned(decl); err == nil {
			t.Fatalf("current declaration must fail closed before review: %+v", decl)
		}
	}
}
