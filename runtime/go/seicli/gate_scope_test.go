package seicli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func scopedDecision(id, scope string, responsible bool) *semanticruntime.Decision {
	d := &semanticruntime.Decision{
		Ref:       semanticruntime.LogicalReference{Kind: "decision", ID: id, Scope: scope},
		Statement: "s",
	}
	if responsible {
		d.ResponsibilityRefs = []semanticruntime.Reference{{Kind: "person", ID: "lead"}}
	}
	return d
}

func strPtr(s string) *string { return &s }

func TestGateDeniesAnIdInSeveralScopesWithoutAScopeInEitherRecordOrder(t *testing.T) {
	a := scopedDecision("D-1", "", true)
	b := scopedDecision("D-1", "project-b", false)
	policy := GatePolicy{RequireResponsible: true}
	for name, bundle := range map[string]*semanticruntime.Bundle{
		"a first": recommendationBundle(nil, a, b),
		"b first": recommendationBundle(nil, b, a),
	} {
		got := CheckDecisionInScope(bundle, "D-1", nil, policy)
		if got.Verdict != "deny" || len(got.Reasons) != 1 {
			t.Fatalf("%s: want one deny reason, got %+v", name, got)
		}
		for _, want := range []string{"multiple decisions match", "(none)", `"project-b"`, "--scope"} {
			if !strings.Contains(got.Reasons[0], want) {
				t.Errorf("%s: reason lacks %q: %s", name, want, got.Reasons[0])
			}
		}
		if got.Binding != nil {
			t.Errorf("%s: no binding when the decision is not identified", name)
		}
	}
}

func TestGateScopeSelectsTheNamedDecisionRegardlessOfRecordOrder(t *testing.T) {
	a := scopedDecision("D-1", "", true)
	b := scopedDecision("D-1", "project-b", false)
	policy := GatePolicy{RequireResponsible: true}
	for _, bundle := range []*semanticruntime.Bundle{recommendationBundle(nil, a, b), recommendationBundle(nil, b, a)} {
		none := CheckDecisionInScope(bundle, "D-1", strPtr(""), policy)
		if none.Verdict != "allow" || none.Binding == nil || none.Binding.DecisionScope != "" {
			t.Errorf("the scopeless decision must be allowed and identified: %+v", none)
		}
		other := CheckDecisionInScope(bundle, "D-1", strPtr("project-b"), policy)
		if other.Verdict != "deny" || other.Binding == nil || other.Binding.DecisionScope != "project-b" {
			t.Errorf("project-b has no responsible party and must be denied for that reason: %+v", other)
		}
		if other.RequestedScope == nil || *other.RequestedScope != "project-b" {
			t.Errorf("requested_scope must be reported: %+v", other.RequestedScope)
		}
		if none.Binding.DecisionDigest == other.Binding.DecisionDigest {
			t.Error("different decisions must have different digests")
		}
	}
}

func TestGateDeniesWhenTheNamedScopeHasNoDecisionOrSeveral(t *testing.T) {
	bundle := recommendationBundle(nil, scopedDecision("D-1", "a", true), scopedDecision("D-2", "a", true), scopedDecision("D-2", "a", true))
	policy := GatePolicy{}
	if got := CheckDecisionInScope(bundle, "D-1", strPtr("zzz"), policy); got.Verdict != "deny" || !strings.Contains(got.Reasons[0], `scope "zzz"`) {
		t.Errorf("an unknown scope must be denied with the scope named: %+v", got)
	}
	if got := CheckDecisionInScope(bundle, "D-2", strPtr("a"), policy); got.Verdict != "deny" || !strings.Contains(got.Reasons[0], "more than once") {
		t.Errorf("the same id and scope twice must be denied: %+v", got)
	}
	if got := CheckDecisionInScope(bundle, "D-1", nil, policy); got.Verdict != "allow" {
		t.Errorf("a single decision needs no scope: %+v", got)
	}
}

// twoScopeStore adds D-1, then clones its record into project-b by editing the
// bundle file, as the issue's reproduction does. The CLI cannot record a scope.
func twoScopeStore(t *testing.T) string {
	t.Helper()
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D-1", "--statement", "A", "--responsible", "person:alice")
	path := filepath.Join(root, "semantic.bundle.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var bundle map[string]any
	if err := json.Unmarshal(raw, &bundle); err != nil {
		t.Fatal(err)
	}
	records := bundle["records"].([]any)
	var clone map[string]any
	data, _ := json.Marshal(records[len(records)-1])
	if err := json.Unmarshal(data, &clone); err != nil {
		t.Fatal(err)
	}
	clone["record_id"] = "D-1-b"
	clone["logical_ref"].(map[string]any)["scope"] = "project-b"
	decision := clone["payload"].(map[string]any)["decision"].(map[string]any)
	decision["ref"].(map[string]any)["scope"] = "project-b"
	delete(decision, "responsibility_refs")
	bundle["records"] = append([]any{clone}, records...)
	out, err := json.Marshal(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, out, 0o644); err != nil {
		t.Fatal(err)
	}
	return root
}

func TestGateCLIScopeFlagResolvesTheSameIDAndLogsTheScope(t *testing.T) {
	root := twoScopeStore(t)
	out, err := run(t, "gate", "check", "--data-root", root, "--decision", "D-1")
	if exitCode(err) != ExitCodeDenied || !strings.Contains(out, "multiple decisions match") {
		t.Fatalf("no scope: want ambiguous deny, got err=%v out=%s", err, out)
	}
	out, err = run(t, "gate", "check", "--data-root", root, "--decision", "D-1", "--scope=")
	if err != nil || !strings.Contains(out, `"requested_scope":""`) || !strings.Contains(out, `"decision_scope":""`) {
		t.Fatalf("--scope= must name the scopeless decision: err=%v out=%s", err, out)
	}
	out, err = run(t, "gate", "check", "--data-root", root, "--decision", "D-1", "--scope", "project-b")
	if exitCode(err) != ExitCodeDenied || !strings.Contains(out, "no responsible party") || !strings.Contains(out, `"decision_scope":"project-b"`) {
		t.Fatalf("--scope project-b: want the project-b decision denied, got err=%v out=%s", err, out)
	}
	log, err := os.ReadFile(filepath.Join(root, GateLogFile))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(log), `"decision_scope":"project-b"`) || !strings.Contains(string(log), `"requested_scope":"project-b"`) {
		t.Errorf("the gate log must keep the scope: %s", log)
	}
}

func TestMCPCheckDecisionPassesScopeAndRefusesANonStringScope(t *testing.T) {
	root := twoScopeStore(t)
	responses := session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D-1"}}}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D-1","scope":""}}}`,
		`{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D-1","scope":"project-b"}}}`,
		`{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D-1","scope":1}}}`,
	)
	if text, _ := callText(responses[1]); !strings.Contains(text, "multiple decisions match") {
		t.Errorf("no scope must be ambiguous: %s", text)
	}
	if text, _ := callText(responses[2]); !strings.Contains(text, `"verdict":"allow"`) || !strings.Contains(text, `"requested_scope":""`) {
		t.Errorf("an empty scope names the scopeless decision: %s", text)
	}
	if text, _ := callText(responses[3]); !strings.Contains(text, `"decision_scope":"project-b"`) || !strings.Contains(text, `"verdict":"deny"`) {
		t.Errorf("project-b must be checked and denied: %s", text)
	}
	if text, isError := callText(responses[4]); !isError || !strings.Contains(text, "scope must be a string") {
		t.Errorf("a non-string scope must be refused, got %q error=%v", text, isError)
	}
}
