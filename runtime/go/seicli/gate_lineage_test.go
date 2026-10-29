package seicli

import (
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func decisionRef(id, scope string) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: "decision", ID: id, Scope: scope}
}

func lineageDecision(id string, lineage *semanticruntime.SemanticLineage) *semanticruntime.Decision {
	return &semanticruntime.Decision{
		Ref:                semanticruntime.LogicalReference{Kind: "decision", ID: id},
		Statement:          "s",
		ResponsibilityRefs: []semanticruntime.Reference{{Kind: "person", ID: "lead"}},
		Lineage:            lineage,
	}
}

func lineageNotesOf(result GateResult) []string {
	var out []string
	for _, n := range result.NotVerified {
		if strings.HasPrefix(n, "Semantic Lineage ") {
			out = append(out, n)
		}
	}
	return out
}

func hasLineageNotVerified(result GateResult) bool {
	for _, n := range result.NotVerified {
		if n == lineageNotVerified {
			return true
		}
	}
	return false
}

func TestGateSaysItDidNotEvaluateLineageEvenWhenNoneExists(t *testing.T) {
	bundle := recommendationBundle(nil, lineageDecision("D1", nil))
	got := CheckDecision(bundle, "D1", GatePolicy{})
	if got.Verdict != "allow" || !hasLineageNotVerified(got) || len(lineageNotesOf(got)) != 0 {
		t.Errorf("want allow with the fixed not-verified line and no lineage notes: %+v", got)
	}
}

func TestGateListsLineageThatNamesTheDecisionWithoutChangingTheVerdict(t *testing.T) {
	// D2 supersedes D1 (lineage held by D2); a reference record also withdraws D1.
	d2 := lineageDecision("D2", &semanticruntime.SemanticLineage{
		Relation: "supersedes", From: decisionRef("D2", ""), To: decisionRef("D1", ""),
	})
	bundle := recommendationBundle(nil, lineageDecision("D1", nil), d2, lineageDecision("D3", &semanticruntime.SemanticLineage{
		Relation: "revises", From: decisionRef("D3", ""), To: decisionRef("D4", ""),
	}))
	bundle.Records = append(bundle.Records, semanticruntime.RuntimeRecord{
		Reference: &semanticruntime.SemanticReferenceDocument{SemanticLineage: &semanticruntime.SemanticLineage{
			Relation: "withdraws", From: decisionRef("D5", ""), To: decisionRef("D1", ""),
		}},
	})

	got := CheckDecision(bundle, "D1", GatePolicy{RequireResponsible: true})
	if got.Verdict != "allow" {
		t.Errorf("the verdict must not change because of lineage: %+v", got)
	}
	notes := lineageNotesOf(got)
	if len(notes) != 2 {
		t.Fatalf("want 2 lineage notes for D1 (D3's lineage names neither end), got %d: %v", len(notes), notes)
	}
	joined := strings.Join(notes, "\n")
	for _, want := range []string{`"supersedes"`, "decision:D2 -> decision:D1", `"withdraws"`, "decision:D5 -> decision:D1", "as to"} {
		if !strings.Contains(joined, want) {
			t.Errorf("notes missing %q: %s", want, joined)
		}
	}
	if !hasLineageNotVerified(got) {
		t.Errorf("the fixed not-verified line must be present: %+v", got.NotVerified)
	}
}

func TestGateDoesNotMixUpLineageOfADecisionWithTheSameIDInAnotherScope(t *testing.T) {
	bundle := recommendationBundle(nil, lineageDecision("D1", nil), lineageDecision("D2", &semanticruntime.SemanticLineage{
		Relation: "supersedes", From: decisionRef("D2", ""), To: decisionRef("D1", "other-scope"),
	}))
	got := CheckDecision(bundle, "D1", GatePolicy{})
	if n := lineageNotesOf(got); len(n) != 0 {
		t.Errorf("lineage that names D1 in another scope must not be listed: %v", n)
	}
}
