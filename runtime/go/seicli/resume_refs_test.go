package seicli

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// scopedRefsBundle is the synthetic reproduction of #725: two recommendations
// with one ID in scopes a and b, and one decision that relies on R-1 @a only.
func scopedRefsBundle(responsible, unresolved semanticruntime.Reference) *semanticruntime.Bundle {
	bundle := recommendationBundle([]semanticruntime.LogicalReference{
		{Kind: "recommendation", ID: "R-1", Scope: "a"},
		{Kind: "recommendation", ID: "R-1", Scope: "b"},
	}, &semanticruntime.Decision{
		Ref:                semanticruntime.LogicalReference{Kind: "decision", ID: "D-9"},
		Statement:          "s",
		RecommendationRefs: []semanticruntime.Reference{logicalRecRef("R-1", "a")},
		ResponsibilityRefs: []semanticruntime.Reference{responsible},
		UnresolvedRefs:     []semanticruntime.Reference{unresolved},
	})
	return bundle
}

func TestResumeKeepsScopeOfRecommendationResponsibleAndUnresolvedRefs(t *testing.T) {
	bundle := scopedRefsBundle(
		semanticruntime.Reference{Kind: "person", ID: "alice", Scope: "org-x"},
		exactBasis("Q-1", "org-y", zeroDigest))
	view := BuildResume(bundle)
	raw, _ := json.Marshal(view)
	var got struct {
		Decisions []struct {
			Recommendations          []string         `json:"recommendations"`
			RecommendationReferences []map[string]any `json:"recommendation_references"`
			Responsible              []string         `json:"responsible"`
			ResponsibilityReferences []map[string]any `json:"responsibility_references"`
		} `json:"decisions"`
		Relied []map[string]any `json:"recommendations_relied_on"`
		Open   []map[string]any `json:"recommendations_not_yet_relied_on"`
		Unres  []map[string]any `json:"unresolved"`
	}
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatal(err)
	}
	d := got.Decisions[0]
	// The legacy text lists are unchanged, so the scope is still lost there.
	if strings.Join(d.Recommendations, ",") != "recommendation:R-1" || strings.Join(d.Responsible, ",") != "person:alice" {
		t.Errorf("legacy text lists must keep their form: %v %v", d.Recommendations, d.Responsible)
	}
	if len(d.RecommendationReferences) != 1 || d.RecommendationReferences[0]["scope"] != "a" || d.RecommendationReferences[0]["form"] != "logical" {
		t.Errorf("recommendation_references must keep scope and form: %v", d.RecommendationReferences)
	}
	if len(d.ResponsibilityReferences) != 1 || d.ResponsibilityReferences[0]["scope"] != "org-x" {
		t.Errorf("responsibility_references must keep scope: %v", d.ResponsibilityReferences)
	}
	if len(got.Relied) != 1 || got.Relied[0]["scope"] != "a" || len(got.Open) != 1 || got.Open[0]["scope"] != "b" {
		t.Errorf("recommendation lists must carry scope: relied=%v open=%v", got.Relied, got.Open)
	}
	u := got.Unres[0]
	ref, _ := u["reference"].(map[string]any)
	lr, _ := ref["logical_ref"].(map[string]any)
	if u["reference_form"] != "exact" || ref["content_digest"] != zeroDigest || lr["scope"] != "org-y" {
		t.Errorf("unresolved entry must keep form, scope and digest: %v", u)
	}
}

func TestResumeHumanOutputSeparatesScopedRecommendationsAndResponsible(t *testing.T) {
	bundle := scopedRefsBundle(
		semanticruntime.Reference{Kind: "person", ID: "alice", Scope: "org-x"},
		exactBasis("Q-1", "org-y", zeroDigest))
	var buf bytes.Buffer
	renderResume(&buf, BuildResume(bundle))
	for _, want := range []string{
		"relied on: recommendation:R-1 @a",
		"responsible: person:alice @org-x",
		"artifact:Q-1 @org-y [exact " + zeroDigest + ", profile synthetic/1] (left open by D-9)",
		"[R-1 @a] r",
		"[R-1 @b] r",
	} {
		if !strings.Contains(buf.String(), want) {
			t.Errorf("human output missing %q:\n%s", want, buf.String())
		}
	}
}

func TestResumeScopeOnlyDifferenceIsInvisibleInLegacyFields(t *testing.T) {
	// Before #725 the two inputs below produced the same resume output. The
	// legacy fields still do; the added fields tell them apart.
	a := BuildResume(scopedRefsBundle(semanticruntime.Reference{Kind: "person", ID: "alice", Scope: "org-x"}, semanticruntime.Reference{Kind: "question", ID: "q"}))
	b := BuildResume(scopedRefsBundle(semanticruntime.Reference{Kind: "person", ID: "alice", Scope: "org-z"}, semanticruntime.Reference{Kind: "question", ID: "q"}))
	if strings.Join(a.Decisions[0].Responsible, ",") != strings.Join(b.Decisions[0].Responsible, ",") {
		t.Fatal("legacy responsible text is expected to stay identical")
	}
	ja, _ := json.Marshal(a)
	jb, _ := json.Marshal(b)
	if bytes.Equal(ja, jb) {
		t.Error("resume JSON must differ when only the responsible scope differs")
	}
	var ha, hb bytes.Buffer
	renderResume(&ha, a)
	renderResume(&hb, b)
	if ha.String() == hb.String() {
		t.Error("human output must differ when only the responsible scope differs")
	}
}

func TestResumeWithoutScopeOmitsAddedFieldsExceptForm(t *testing.T) {
	out := resumeJSON(t, basisDecision("D1", ""))
	for _, banned := range []string{"recommendation_references", "responsibility_references"} {
		if strings.Contains(out, banned) {
			t.Errorf("empty lists must stay omitted, found %s: %s", banned, out)
		}
	}
}
