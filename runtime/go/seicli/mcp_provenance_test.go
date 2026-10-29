package seicli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// These tests record what `sei mcp --allow-decision` stores when the client
// gives a misleading, empty or human-looking name, and when responsible names a
// person. They fix the behavior QUICKSTART describes: the provenance is the
// client's self-declared name and the responsible party is not verified.

type storedProvenance struct {
	Kind string `json:"kind"`
	ID   string `json:"id"`
}

// exportedDecisionProvenance exports the store and returns the provenance_refs
// of the decision record with the given logical id.
func exportedDecisionProvenance(t *testing.T, root, decisionID string) []storedProvenance {
	t.Helper()
	out := filepath.Join(t.TempDir(), "bundle.json")
	mustRun(t, "export", "--data-root", root, "--output", out)
	data, err := os.ReadFile(out)
	if err != nil {
		t.Fatal(err)
	}
	var bundle struct {
		Records []struct {
			Kind       string `json:"kind"`
			LogicalRef struct {
				ID string `json:"id"`
			} `json:"logical_ref"`
			ProvenanceRefs []storedProvenance `json:"provenance_refs"`
		} `json:"records"`
	}
	if err := json.Unmarshal(data, &bundle); err != nil {
		t.Fatal(err)
	}
	for _, r := range bundle.Records {
		if r.Kind == "decision" && r.LogicalRef.ID == decisionID {
			return r.ProvenanceRefs
		}
	}
	t.Fatalf("decision %s not found in export", decisionID)
	return nil
}

func addDecisionCall(id, decisionID, responsible string) string {
	return `{"jsonrpc":"2.0","id":` + id + `,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"` +
		decisionID + `","statement":"s","responsible":["` + responsible + `"]}}}`
}

func TestMCPClientNameIsStoredAsGivenEvenWhenItImpersonatesAPerson(t *testing.T) {
	fixClock(t)
	cases := []struct {
		name       string
		initialize string
		wantSource string
	}{
		{"name that claims to be a person", `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"person:lead"}}}`, "person:lead"},
		{"empty name", `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":""}}}`, "mcp-client"},
		{"no clientInfo", `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}`, "mcp-client"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			root := filepath.Join(t.TempDir(), "store")
			mustRun(t, "init", "--data-root", root)
			responses := session(t, []string{"--data-root", root, "--allow-decision"},
				tc.initialize,
				addDecisionCall("2", "D1", "person:lead"),
			)
			if text, isError := callText(responses[1]); isError {
				t.Fatalf("add_decision failed: %s", text)
			}
			got := exportedDecisionProvenance(t, root, "D1")
			if len(got) != 1 || got[0].ID != tc.wantSource {
				t.Fatalf("provenance_refs = %+v, want one entry with id %q", got, tc.wantSource)
			}
			// kind is always "source": a person, an AI client and a tool cannot be told apart.
			if got[0].Kind != "source" {
				t.Errorf("provenance kind = %q, want source", got[0].Kind)
			}
			if out := mustRun(t, "resume", "--data-root", root); !strings.Contains(out, "responsible: person:lead") {
				t.Errorf("resume does not show the responsible party as given:\n%s", out)
			}
		})
	}
}

func TestMCPResponsibleIsNotCheckedAgainstAnyone(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	// The named person is never consulted: any kind:id is stored, and the gate
	// reports the Authority of the responsible party as not verified.
	session(t, []string{"--data-root", root, "--allow-decision"},
		initialize,
		addDecisionCall("2", "D1", "person:nobody-confirmed-this"),
	)
	text, _ := callText(session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D1"}}}`,
	)[1])
	if !strings.Contains(text, "Authority") {
		t.Errorf("check_decision must list the unverified Authority, got %q", text)
	}
}
