package seicli

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func gateJSON(t *testing.T, root, decision string) GateResult {
	t.Helper()
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", decision)
	if err != nil {
		t.Fatalf("gate check %s: %v\n%s", decision, err, out)
	}
	var result GateResult
	if err := json.Unmarshal([]byte(out), &result); err != nil {
		t.Fatalf("not JSON: %v\n%s", err, out)
	}
	return result
}

func TestGateResultAndLogCarryTheBundleAndDecisionBinding(t *testing.T) {
	root := gateStore(t)
	got := gateJSON(t, root, "D-full")
	raw, err := os.ReadFile(filepath.Join(root, "semantic.bundle.json"))
	if err != nil {
		t.Fatal(err)
	}
	if got.Binding == nil {
		t.Fatal("an allow result must carry a binding")
	}
	if want := fmt.Sprintf("sha256:%x", sha256.Sum256(raw)); got.Binding.BundleDigest != want {
		t.Errorf("bundle_digest = %s, want %s", got.Binding.BundleDigest, want)
	}
	if got.Binding.BundleID == "" || got.Binding.DecisionRecordID == "" {
		t.Errorf("bundle_id and decision_record_id must be set: %+v", got.Binding)
	}
	if !strings.HasPrefix(got.Binding.DecisionDigest, "sha256:") || got.Binding.DecisionRepresentationProfile != "sei.jcs+sha256/v1alpha1" {
		t.Errorf("decision digest or profile is wrong: %+v", got.Binding)
	}
	log, err := os.ReadFile(filepath.Join(root, GateLogFile))
	if err != nil {
		t.Fatal(err)
	}
	for _, want := range []string{`"bundle_digest":"` + got.Binding.BundleDigest + `"`, `"decision_digest":"` + got.Binding.DecisionDigest + `"`} {
		if !strings.Contains(string(log), want) {
			t.Errorf("gate log lacks %s: %s", want, log)
		}
	}
}

func TestGateBindingSeparatesStoreVersionFromDecisionContent(t *testing.T) {
	root := gateStore(t)
	before := gateJSON(t, root, "D-full")
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R2", "--statement", "other")
	after := gateJSON(t, root, "D-full")
	if before.Binding.BundleDigest == after.Binding.BundleDigest {
		t.Error("adding a record must change bundle_digest, so an old allow can be told from a new one")
	}
	if before.Binding.DecisionDigest != after.Binding.DecisionDigest {
		t.Error("an unrelated record must not change the checked Decision's digest")
	}
}

func TestGateDecisionDigestChangesWithTheDecisionContent(t *testing.T) {
	a := decisionWithBasis("D1")
	b := decisionWithBasis("D1", semanticruntime.Reference{Kind: "artifact", ID: "A"})
	ra := CheckDecision(recommendationBundle(nil, a), "D1", GatePolicy{})
	rb := CheckDecision(recommendationBundle(nil, b), "D1", GatePolicy{})
	if ra.Binding == nil || rb.Binding == nil {
		t.Fatal("both results need a binding")
	}
	if ra.Binding.DecisionDigest == rb.Binding.DecisionDigest {
		t.Error("a Decision whose basis changed must have a different digest")
	}
}

func TestGateDeniesWhenSeveralDecisionsShareTheID(t *testing.T) {
	first := decisionWithBasis("D1")
	second := decisionWithBasis("D1", semanticruntime.Reference{Kind: "artifact", ID: "A"})
	got := CheckDecision(recommendationBundle(nil, first, second), "D1", GatePolicy{RequireResponsible: true})
	if got.Verdict != "deny" || len(got.Reasons) == 0 || !strings.Contains(got.Reasons[0], "ambiguous") {
		t.Fatalf("duplicate ids must be denied as ambiguous: %+v", got)
	}
	if got.Binding != nil {
		t.Errorf("no binding may be reported when the Decision is not identified: %+v", got.Binding)
	}
	// The order of the records must not change the outcome.
	swapped := CheckDecision(recommendationBundle(nil, second, first), "D1", GatePolicy{RequireResponsible: true})
	if swapped.Verdict != "deny" {
		t.Errorf("record order changed the verdict: %+v", swapped)
	}
}

func TestGateDoesNotCreateAStoreDirectoryWhenNoneExists(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "missing")
	run(t, "gate", "check", "--data-root", root, "--decision", "D1")
	if _, err := os.Stat(root); err == nil {
		t.Error("gate check must not create the data root")
	}
}
