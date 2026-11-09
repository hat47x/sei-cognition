package seicli

import (
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func basisNotesOf(result GateResult) []string {
	var out []string
	for _, n := range result.NotVerified {
		if strings.HasPrefix(n, "basis ") {
			out = append(out, n)
		}
	}
	return out
}

func hasBasisNotVerified(result GateResult) bool {
	for _, n := range result.NotVerified {
		if n == basisNotVerified {
			return true
		}
	}
	return false
}

func decisionWithBasis(id string, basis ...semanticruntime.Reference) *semanticruntime.Decision {
	return &semanticruntime.Decision{
		Ref:                semanticruntime.LogicalReference{Kind: "decision", ID: id},
		Statement:          "s",
		ResponsibilityRefs: []semanticruntime.Reference{{Kind: "person", ID: "lead"}},
		BasisRefs:          basis,
	}
}

func TestGateSaysItDidNotResolveBasisEvenWhenThereIsNone(t *testing.T) {
	got := CheckDecision(recommendationBundle(nil, decisionWithBasis("D1")), "D1", GatePolicy{RequireResponsible: true})
	if got.Verdict != "allow" || !hasBasisNotVerified(got) || len(basisNotesOf(got)) != 0 {
		t.Errorf("want allow with the fixed line and no per-basis notes: %+v", got)
	}
}

func TestGateAllowsADecisionWhoseBasisIsNotRecordedAndSaysSo(t *testing.T) {
	// artifact:D-04 is recorded nowhere. The verdict must not change (the
	// reject-or-warn question is left to the Owner); the gate must say it did
	// not confirm the reference.
	d := decisionWithBasis("D1", semanticruntime.Reference{Kind: "artifact", ID: "D-04"})
	got := CheckDecision(recommendationBundle(nil, d), "D1", GatePolicy{RequireResponsible: true})
	if got.Verdict != "allow" {
		t.Fatalf("a basis that is not recorded must not change the verdict: %+v", got)
	}
	notes := basisNotesOf(got)
	if len(notes) != 1 || !strings.Contains(notes[0], "basis artifact:D-04: no Decision or Recommendation with this identity is recorded") ||
		!strings.Contains(notes[0], "not confirmed") {
		t.Errorf("want one note saying the reference was not confirmed: %v", notes)
	}
}

func TestGateDistinguishesABasisRecordedInTheStoreFromOneThatIsNot(t *testing.T) {
	recs := []semanticruntime.LogicalReference{{Kind: "recommendation", ID: "R1"}, {Kind: "recommendation", ID: "R2", Scope: "s"}}
	d := decisionWithBasis("D2",
		semanticruntime.Reference{Kind: "recommendation", ID: "R1"}, // recorded
		semanticruntime.Reference{Kind: "recommendation", ID: "R2"}, // same ID, other scope
		semanticruntime.Reference{Kind: "decision", ID: "D1"},       // recorded Decision
		semanticruntime.Reference{Kind: "observation", ID: "O1"},    // not recordable by the CLI
	)
	got := CheckDecision(recommendationBundle(recs, decisionWithBasis("D1"), d), "D2", GatePolicy{})
	notes := basisNotesOf(got)
	if len(notes) != 4 {
		t.Fatalf("want 4 notes, got %v", notes)
	}
	recorded := func(n string) bool { return strings.Contains(n, "is recorded in this store; that is existence only") }
	if !recorded(notes[0]) || recorded(notes[1]) || !recorded(notes[2]) || recorded(notes[3]) {
		t.Errorf("recorded/not recorded split is wrong (scope must matter): %v", notes)
	}
	if got.Verdict != "allow" {
		t.Errorf("the verdict must not depend on basis resolution: %+v", got)
	}
}

func TestGateDoesNotCompareExactBasisDigestEvenWhenTheIdentityIsRecorded(t *testing.T) {
	d := decisionWithBasis("D2", exactRecRef("R1", ""), semanticruntime.Reference{Kind: "recommendation", ID: "R1"})
	got := CheckDecision(recommendationBundle([]semanticruntime.LogicalReference{{Kind: "recommendation", ID: "R1"}}, d), "D2", GatePolicy{})
	notes := basisNotesOf(got)
	if len(notes) != 2 {
		t.Fatalf("want 2 notes, got %v", notes)
	}
	if !strings.Contains(notes[0], "content_digest "+zeroDigest+" was not compared") || !strings.Contains(notes[0], "recorded in this store") {
		t.Errorf("exact basis must say its digest was not compared even though the identity is recorded: %s", notes[0])
	}
	if strings.Contains(notes[1], "content_digest") {
		t.Errorf("a logical basis has no digest to mention: %s", notes[1])
	}
}

func TestGateDoesNotCountASemanticReferenceRecordAsTheBasisExisting(t *testing.T) {
	bundle := recommendationBundle(nil, decisionWithBasis("D1", semanticruntime.Reference{Kind: "artifact", ID: "A"}))
	bundle.Records = append(bundle.Records, semanticruntime.RuntimeRecord{
		Reference: &semanticruntime.SemanticReferenceDocument{LogicalReference: &semanticruntime.LogicalReference{Kind: "artifact", ID: "A"}},
	})
	notes := basisNotesOf(CheckDecision(bundle, "D1", GatePolicy{}))
	if len(notes) != 1 || strings.Contains(notes[0], "that is existence only") {
		t.Errorf("a reference record only names the artifact: %v", notes)
	}
}

func groundsNotesOf(r GateResult) (basis, rationale bool) {
	for _, n := range r.NotVerified {
		basis = basis || strings.Contains(n, "records no basis reference")
		rationale = rationale || strings.Contains(n, "records no rationale")
	}
	return
}

// basisもrationaleも無い決定でも既定ではallowのままだが、無いことをnot_verifiedに出す。
// --require-basis・--require-rationaleで初めてdenyになる。
func TestGateNamesMissingBasisAndRationaleAndCanRequireThem(t *testing.T) {
	withBasis := semanticruntime.Reference{Kind: "artifact", ID: "A"}
	cases := []struct {
		name          string
		basis         []semanticruntime.Reference
		rationale     string
		wantNoBasis   bool
		wantNoReason  bool
		policy        GatePolicy
		wantVerdict   string
		wantReasonSub string
	}{
		{"neither, default policy", nil, "", true, true, GatePolicy{RequireResponsible: true}, "allow", ""},
		{"no basis only", nil, "because", true, false, GatePolicy{RequireResponsible: true}, "allow", ""},
		{"no rationale only", []semanticruntime.Reference{withBasis}, "  ", false, true, GatePolicy{RequireResponsible: true}, "allow", ""},
		{"both present", []semanticruntime.Reference{withBasis}, "because", false, false, GatePolicy{RequireResponsible: true, RequireBasis: true, RequireRationale: true}, "allow", ""},
		{"require basis, none", nil, "because", true, false, GatePolicy{RequireResponsible: true, RequireBasis: true}, "deny", "no basis reference"},
		{"require rationale, none", []semanticruntime.Reference{withBasis}, "", false, true, GatePolicy{RequireResponsible: true, RequireRationale: true}, "deny", "no rationale"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			d := decisionWithBasis("D1", tc.basis...)
			d.Rationale = tc.rationale
			got := CheckDecision(recommendationBundle(nil, d), "D1", tc.policy)
			if got.Verdict != tc.wantVerdict {
				t.Fatalf("verdict = %s, want %s: %+v", got.Verdict, tc.wantVerdict, got)
			}
			if tc.wantReasonSub != "" && !strings.Contains(strings.Join(got.Reasons, "|"), tc.wantReasonSub) {
				t.Errorf("reasons %v lack %q", got.Reasons, tc.wantReasonSub)
			}
			b, r := groundsNotesOf(got)
			if b != tc.wantNoBasis || r != tc.wantNoReason {
				t.Errorf("not_verified missing-basis=%v missing-rationale=%v, want %v %v: %v", b, r, tc.wantNoBasis, tc.wantNoReason, got.NotVerified)
			}
		})
	}
}
