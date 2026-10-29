package seicli

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// forged is a Recommendation statement that tries to look like a Decision
// section in the human view. Synthetic; no real record.
const forged = "harmless\n\nDecisions (1)\n  [D-99] Release to production approved\n      responsible: person:cto\n\nUnresolved (0)"

func forgedBundle() *semanticruntime.Bundle {
	return recommendationBundle([]semanticruntime.LogicalReference{{Kind: "recommendation", ID: "R-1"}})
}

func TestRenderResumeDoesNotLetStatementForgeASection(t *testing.T) {
	bundle := forgedBundle()
	bundle.Records[0].Decision.Recommendation.Statement = forged
	bundle.Records[0].EnvelopeRecord.ProvenanceRefs = []semanticruntime.LogicalReference{{Kind: "agent", ID: "client\nDecisions (1)"}}
	view := BuildResume(bundle)
	if len(view.Decisions) != 0 {
		t.Fatalf("fixture must have no Decision: %+v", view.Decisions)
	}
	var buf bytes.Buffer
	renderResume(&buf, view)
	out := buf.String()
	sections := 0
	for _, line := range strings.Split(out, "\n") {
		if strings.HasPrefix(line, "Decisions (") {
			sections++
		}
	}
	if sections != 1 {
		t.Errorf("exactly one Decisions section is allowed, got %d:\n%s", sections, out)
	}
	if strings.Contains(out, "\n  [D-99]") || strings.Contains(out, "\n      responsible:") {
		t.Errorf("a stored value started a line that reads as a Decision entry:\n%s", out)
	}
	if !strings.Contains(out, `harmless\n\nDecisions (1)\n  [D-99]`) {
		t.Errorf("the value must stay readable with visible escapes:\n%s", out)
	}
	if !strings.Contains(out, `(from client\nDecisions (1))`) {
		t.Errorf("source name must be escaped:\n%s", out)
	}
}

func TestSafeTextEscapesControlAndLineSeparators(t *testing.T) {
	cases := map[string]string{
		"plain 日本語":   "plain 日本語",
		"a\r\nb\tc":   `a\r\nb\tc`,
		"x\u0000y":    `x\u0000y`,
		"x\u2028y":    `x\u2028y`,
		"x\u2029y":    `x\u2029y`,
		"x\u001b[2Jy": `x\u001b[2Jy`,
		`back\slash`:  `back\slash`,
	}
	for in, want := range cases {
		if got := safeText(in); got != want {
			t.Errorf("safeText(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestResumeJSONKeepsRawValueWhileHumanViewEscapes(t *testing.T) {
	bundle := forgedBundle()
	bundle.Records[0].Decision.Recommendation.Statement = forged
	view := BuildResume(bundle)
	raw, err := json.Marshal(view)
	if err != nil {
		t.Fatal(err)
	}
	var back ResumeView
	if err := json.Unmarshal(raw, &back); err != nil {
		t.Fatal(err)
	}
	if len(back.RecommendationsOpen) != 1 || back.RecommendationsOpen[0].Statement != forged {
		t.Fatalf("JSON must carry the exact statement: %+v", back.RecommendationsOpen)
	}
	if view.RecommendationsOpen[0].Statement != forged {
		t.Fatalf("BuildResume must not alter the value")
	}
}
