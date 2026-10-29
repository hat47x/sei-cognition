package seicli

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

const zeroDigest = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
const otherDigest = "sha256:1111111111111111111111111111111111111111111111111111111111111111"

func exactBasis(id, scope, digest string) semanticruntime.Reference {
	return semanticruntime.Reference{
		LogicalRef:            &semanticruntime.LogicalReference{Kind: "artifact", ID: id, Scope: scope},
		ContentDigest:         digest,
		RepresentationProfile: &semanticruntime.RepresentationProfile{ProfileID: "synthetic", Version: "1"},
	}
}

func basisDecision(id, scope string, basis ...semanticruntime.Reference) *semanticruntime.Decision {
	return &semanticruntime.Decision{
		Ref:       semanticruntime.LogicalReference{Kind: "decision", ID: id, Scope: scope},
		Statement: "s", BasisRefs: basis,
	}
}

func resumeJSON(t *testing.T, d *semanticruntime.Decision) string {
	t.Helper()
	view := BuildResume(recommendationBundle(nil, d))
	out, err := json.Marshal(view.Decisions)
	if err != nil {
		t.Fatal(err)
	}
	return string(out)
}

func TestResumeDistinguishesBasisThatDiffersInFormDigestOrScope(t *testing.T) {
	inputs := map[string]*semanticruntime.Decision{
		"logical":       basisDecision("D1", "", semanticruntime.Reference{Kind: "artifact", ID: "D-04"}),
		"exact":         basisDecision("D1", "", exactBasis("D-04", "", zeroDigest)),
		"exact-digest2": basisDecision("D1", "", exactBasis("D-04", "", otherDigest)),
		"scoped":        basisDecision("D1", "", semanticruntime.Reference{Kind: "artifact", ID: "D-04", Scope: "other"}),
	}
	legacy := map[string]bool{}
	full := map[string]string{}
	human := map[string]string{}
	for name, d := range inputs {
		view := BuildResume(recommendationBundle(nil, d))
		legacy[strings.Join(view.Decisions[0].Basis, "|")] = true
		out, _ := json.Marshal(view.Decisions[0].BasisReferences)
		if prev, dup := full[string(out)]; dup {
			t.Errorf("basis_references of %q and %q are identical: %s", name, prev, out)
		}
		full[string(out)] = name
		var buf bytes.Buffer
		renderResume(&buf, view)
		if prev, dup := human[buf.String()]; dup {
			t.Errorf("human output of %q and %q is identical:\n%s", name, prev, buf.String())
		}
		human[buf.String()] = name
	}
	// The legacy text field is kept as it was, so the four inputs still collapse
	// there. That is the defect the new field exists to cure, not a regression.
	if len(legacy) != 1 {
		t.Errorf("the legacy basis field must keep its old text form, got %v", legacy)
	}
}

func TestResumeBasisReferencesKeepExactBindingAndForm(t *testing.T) {
	view := BuildResume(recommendationBundle(nil, basisDecision("D1", "",
		semanticruntime.Reference{Kind: "artifact", ID: "A"}, exactBasis("B", "s1", zeroDigest))))
	raw, err := json.Marshal(view.Decisions[0])
	if err != nil {
		t.Fatal(err)
	}
	var got struct {
		Basis           []string          `json:"basis"`
		BasisReferences []json.RawMessage `json:"basis_references"`
	}
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatal(err)
	}
	if strings.Join(got.Basis, ",") != "artifact:A,artifact:B" || len(got.BasisReferences) != 2 {
		t.Fatalf("legacy basis must be unchanged and basis_references parallel to it: %s", raw)
	}
	var logical, exact map[string]any
	_ = json.Unmarshal(got.BasisReferences[0], &logical)
	_ = json.Unmarshal(got.BasisReferences[1], &exact)
	if logical["form"] != "logical" || logical["kind"] != "artifact" || logical["id"] != "A" || logical["content_digest"] != nil {
		t.Errorf("logical entry: %v", logical)
	}
	lr, _ := exact["logical_ref"].(map[string]any)
	rp, _ := exact["representation_profile"].(map[string]any)
	if exact["form"] != "exact" || exact["content_digest"] != zeroDigest || lr["scope"] != "s1" || rp["profile_id"] != "synthetic" || rp["version"] != "1" {
		t.Errorf("exact entry must keep digest, scope and profile: %v", exact)
	}
}

func TestResumeShowsDecisionScopeSoSameIDDecisionsStayApart(t *testing.T) {
	bundle := recommendationBundle(nil, basisDecision("D1", "scope-a"), basisDecision("D1", "scope-b"))
	view := BuildResume(bundle)
	if len(view.Decisions) != 2 || view.Decisions[0].Scope != "scope-a" || view.Decisions[1].Scope != "scope-b" {
		t.Fatalf("scopes must be kept: %+v", view.Decisions)
	}
	var buf bytes.Buffer
	renderResume(&buf, view)
	for _, want := range []string{"scope: scope-a", "scope: scope-b"} {
		if !strings.Contains(buf.String(), want) {
			t.Errorf("human output missing %q:\n%s", want, buf.String())
		}
	}
}

func TestResumeHumanOutputMarksLogicalAndExactBasis(t *testing.T) {
	view := BuildResume(recommendationBundle(nil, basisDecision("D1", "",
		semanticruntime.Reference{Kind: "artifact", ID: "A"}, exactBasis("B", "s1", zeroDigest))))
	var buf bytes.Buffer
	renderResume(&buf, view)
	for _, want := range []string{"artifact:A [logical]", "artifact:B @s1 [exact " + zeroDigest + ", profile synthetic/1]"} {
		if !strings.Contains(buf.String(), want) {
			t.Errorf("human output missing %q:\n%s", want, buf.String())
		}
	}
}

func TestResumeWithoutBasisOmitsBasisReferences(t *testing.T) {
	if out := resumeJSON(t, basisDecision("D1", "")); strings.Contains(out, "basis_references") || strings.Contains(out, `"scope"`) {
		t.Errorf("empty basis and scope must stay omitted: %s", out)
	}
}
