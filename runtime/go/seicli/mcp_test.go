package seicli

import (
	"bytes"
	"context"
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"
)

// session feeds newline-delimited JSON-RPC lines to `sei mcp` and returns the
// parsed responses in order.
func session(t *testing.T, args []string, lines ...string) []map[string]any {
	t.Helper()
	original := Stdin
	Stdin = strings.NewReader(strings.Join(lines, "\n") + "\n")
	t.Cleanup(func() { Stdin = original })
	var out, errOut bytes.Buffer
	if err := Run(context.Background(), append([]string{"mcp"}, args...), &out, &errOut); err != nil {
		t.Fatalf("mcp: %v (%s)", err, errOut.String())
	}
	var responses []map[string]any
	for _, line := range strings.Split(strings.TrimSpace(out.String()), "\n") {
		if line == "" {
			continue
		}
		var m map[string]any
		if err := json.Unmarshal([]byte(line), &m); err != nil {
			t.Fatalf("bad response line %q: %v", line, err)
		}
		responses = append(responses, m)
	}
	return responses
}

func toolNames(resp map[string]any) []string {
	var names []string
	for _, tool := range resp["result"].(map[string]any)["tools"].([]any) {
		names = append(names, tool.(map[string]any)["name"].(string))
	}
	return names
}

func callText(resp map[string]any) (string, bool) {
	result := resp["result"].(map[string]any)
	isError, _ := result["isError"].(bool)
	content := result["content"].([]any)[0].(map[string]any)
	return content["text"].(string), isError
}

const (
	initialize  = `{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"assistant-x"}}}`
	initialized = `{"jsonrpc":"2.0","method":"notifications/initialized"}`
)

func TestMCPOffersOnlyReadAndProposeByDefault(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)

	responses := session(t, []string{"--data-root", root},
		initialize, initialized,
		`{"jsonrpc":"2.0","id":2,"method":"tools/list"}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D1","statement":"s","responsible":["person:x"]}}}`,
	)
	if len(responses) != 3 {
		t.Fatalf("a notification must not get a response; got %d responses", len(responses))
	}
	names := toolNames(responses[1])
	if strings.Join(names, ",") != "resume,add_recommendation,check_decision" {
		t.Errorf("default tools = %v, want resume, add_recommendation and check_decision only", names)
	}
	if text, isError := callText(responses[2]); !isError || !strings.Contains(text, "not enabled") {
		t.Errorf("add_decision must be refused by default, got %q error=%v", text, isError)
	}
	if strings.Contains(mustRun(t, "resume", "--data-root", root), "[D1]") {
		t.Error("a refused decision was recorded")
	}
}

func TestMCPRecommendationKeepsToolProvenanceAndIsNotADecision(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)

	responses := session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"add_recommendation","arguments":{"id":"R1","statement":"--id=evil","basis":["evidence:q1"]}}}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"resume","arguments":{}}}`,
	)
	if text, isError := callText(responses[1]); isError {
		t.Fatalf("add_recommendation failed: %s", text)
	}
	text, _ := callText(responses[2])
	for _, want := range []string{"Decisions (0)", "[R1] --id=evil (from assistant-x)"} {
		if !strings.Contains(text, want) {
			t.Errorf("resume missing %q:\n%s", want, text)
		}
	}
}

func TestMCPDecisionRequiresAResponsiblePartyWhenEnabled(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)

	responses := session(t, []string{"--data-root", root, "--allow-decision"},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/list"}`,
		`{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D1","statement":"s"}}}`,
		`{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add_decision","arguments":{"id":"D2","statement":"s","responsible":["person:lead"],"unresolved":["question:cost"]}}}`,
	)
	if got := strings.Join(toolNames(responses[1]), ","); got != "resume,add_recommendation,check_decision,add_decision" {
		t.Errorf("tools with --allow-decision = %s", got)
	}
	if text, isError := callText(responses[2]); !isError || !strings.Contains(text, "responsible") {
		t.Errorf("a decision without a responsible party must fail, got %q", text)
	}
	if text, isError := callText(responses[3]); isError {
		t.Errorf("a decision with a responsible party must succeed: %s", text)
	}
	out := mustRun(t, "resume", "--data-root", root)
	if strings.Contains(out, "[D1]") || !strings.Contains(out, "[D2]") || !strings.Contains(out, "responsible: person:lead") {
		t.Errorf("unexpected store state:\n%s", out)
	}
}

func TestMCPCheckDecisionReturnsADeniedVerdictAsAnAnswer(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "decision", "--data-root", root, "--id", "D1", "--statement", "s")

	responses := session(t, []string{"--data-root", root},
		initialize,
		`{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_decision","arguments":{"decision":"D1"}}}`,
	)
	text, isError := callText(responses[1])
	if isError || !strings.Contains(text, `"verdict":"deny"`) || !strings.Contains(text, "not_verified") {
		t.Errorf("a denied check must come back as a normal result with the verdict, got %q error=%v", text, isError)
	}
}

func TestMCPAnswersUnknownMethodsAndBadJSONWithErrors(t *testing.T) {
	root := filepath.Join(t.TempDir(), "store")
	responses := session(t, []string{"--data-root", root},
		`{"jsonrpc":"2.0","id":1,"method":"resources/list"}`,
		`not json`,
	)
	if len(responses) != 2 {
		t.Fatalf("got %d responses", len(responses))
	}
	for i, want := range []float64{-32601, -32700} {
		code := responses[i]["error"].(map[string]any)["code"].(float64)
		if code != want {
			t.Errorf("response %d code = %v, want %v", i, code, want)
		}
	}
}
