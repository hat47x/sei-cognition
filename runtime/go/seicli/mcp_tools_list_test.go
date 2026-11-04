package seicli

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"testing"
)

// The tools/list output is fixed in testdata/mcp_tools_list.golden.json so a
// change to a tool name, description, schema or annotation shows up as a diff
// (#750). To accept an intended change, run
//
//	SEI_UPDATE_GOLDEN=1 go test ./seicli -run TestMCPToolsListMatchesGolden
//
// and review the diff of the golden file.
func TestMCPToolsListMatchesGolden(t *testing.T) {
	server := &mcpServer{allowDecision: true}
	got, err := json.MarshalIndent(server.tools(), "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	got = append(got, '\n')
	path := filepath.Join("testdata", "mcp_tools_list.golden.json")
	if os.Getenv("SEI_UPDATE_GOLDEN") == "1" {
		if err := os.MkdirAll("testdata", 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, got, 0o644); err != nil {
			t.Fatal(err)
		}
	}
	want, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if string(normalizeNewlines(want)) != string(got) {
		t.Errorf("tools/list differs from %s; review the change and update the golden file\n--- got ---\n%s", path, got)
	}
}

func normalizeNewlines(b []byte) []byte {
	out := make([]byte, 0, len(b))
	for _, c := range b {
		if c != '\r' {
			out = append(out, c)
		}
	}
	return out
}

// Every tool declares exactly the arguments the runtime accepts, and says
// whether it is read-only.
func TestMCPToolSchemasMatchAcceptedArguments(t *testing.T) {
	server := &mcpServer{allowDecision: true}
	wantReadOnly := map[string]bool{"resume": true, "check_decision": false, "add_recommendation": false, "add_decision": false}
	seen := map[string]bool{}
	for _, tool := range server.tools() {
		seen[tool.Name] = true
		if tool.InputSchema["additionalProperties"] != false {
			t.Errorf("%s: inputSchema must declare additionalProperties:false", tool.Name)
		}
		props, _ := tool.InputSchema["properties"].(map[string]any)
		var declared []string
		for k := range props {
			declared = append(declared, k)
		}
		accepted := append([]string(nil), mcpArgKeys[tool.Name]...)
		sort.Strings(declared)
		sort.Strings(accepted)
		if len(declared) != len(accepted) {
			t.Errorf("%s: schema declares %v, runtime accepts %v", tool.Name, declared, accepted)
			continue
		}
		for i := range declared {
			if declared[i] != accepted[i] {
				t.Errorf("%s: schema declares %v, runtime accepts %v", tool.Name, declared, accepted)
				break
			}
		}
		readOnly, ok := tool.Annotations["readOnlyHint"].(bool)
		if !ok {
			t.Errorf("%s: readOnlyHint is missing", tool.Name)
		} else if readOnly != wantReadOnly[tool.Name] {
			t.Errorf("%s: readOnlyHint = %v, want %v", tool.Name, readOnly, wantReadOnly[tool.Name])
		}
		if tool.Annotations["destructiveHint"] != false || tool.Annotations["openWorldHint"] != false {
			t.Errorf("%s: destructiveHint and openWorldHint must be false: %v", tool.Name, tool.Annotations)
		}
	}
	for name := range wantReadOnly {
		if !seen[name] {
			t.Errorf("tool %s is not listed", name)
		}
	}
}
