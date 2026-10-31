package seicli

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"strings"
)

// This file is an Integration Surface Profile, not a Semantic Contract and not
// a Requirement. It lets an AI tool call the same operations a person calls
// from the command line, over the Model Context Protocol (stdio transport).
//
// Boundary choices:
//   - Reading (resume), proposing (add_recommendation) and asking whether a decision
//     meets a policy (check_decision) are always offered.
//   - Recording a Decision is offered only when the operator starts the server
//     with --allow-decision, and then requires a named responsible party. An AI
//     tool must not be able to turn its own output into a Decision by default.
//   - Every record written through this surface carries the name the client
//     gave at initialize as its provenance. The caller cannot choose another name.
//   - An argument that cannot be acted on is refused, never dropped. A dropped
//     policy flag would turn a check into an allow without any signal.

const mcpProtocolVersion = "2025-06-18"

// mcpMaxLineBytes bounds one JSON-RPC message. A longer line is answered with
// an error and discarded without being parsed.
const mcpMaxLineBytes = 1 << 20

// defaultProvenance is used when the client did not send a name at initialize.
const defaultProvenance = "mcp-client"

type rpcRequest struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      json.RawMessage `json:"id,omitempty"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params,omitempty"`
}

type rpcError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type rpcResponse struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      json.RawMessage `json:"id"`
	Result  any             `json:"result,omitempty"`
	Error   *rpcError       `json:"error,omitempty"`
}

type mcpTool struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	InputSchema map[string]any `json:"inputSchema"`
}

type mcpServer struct {
	dataRoot      string
	allowDecision bool
	clientName    string
	initialized   bool
}

// mcpArgKeys lists the arguments each tool accepts. Any other key is refused.
var mcpArgKeys = map[string][]string{
	"resume":             {"record_id", "snapshot_digest"},
	"check_decision":     {"decision", "scope", "require_recommendation", "deny_unresolved"},
	"add_recommendation": {"id", "statement", "rationale", "basis"},
	"add_decision":       {"id", "statement", "rationale", "basis", "recommendation", "unresolved", "responsible"},
}

func runMCP(ctx context.Context, args []string, stdin io.Reader, stdout, stderr io.Writer) error {
	f := newFlags("mcp", stderr)
	root := dataRootFlag(f)
	allow := f.Bool("allow-decision", false, "also offer add_decision to the connected tool (requires a named responsible party)")
	if done, err := parseFlags(f, args, stdout, stderr); done || err != nil {
		return err
	}
	server := &mcpServer{dataRoot: resolveDataRoot(*root), allowDecision: *allow}
	return server.serve(ctx, stdin, stdout)
}

func (s *mcpServer) serve(ctx context.Context, stdin io.Reader, stdout io.Writer) error {
	reader := bufio.NewReader(stdin)
	enc := json.NewEncoder(stdout)
	enc.SetEscapeHTML(false)
	for {
		line, tooLong, err := readBoundedLine(reader, mcpMaxLineBytes)
		var resp *rpcResponse
		switch {
		case tooLong:
			resp = &rpcResponse{JSONRPC: "2.0", ID: json.RawMessage("null"), Error: &rpcError{Code: -32600, Message: fmt.Sprintf("request line exceeds %d bytes", mcpMaxLineBytes)}}
		case len(bytes.TrimSpace(line)) > 0:
			resp = s.handle(ctx, line)
		}
		if resp != nil {
			if encErr := enc.Encode(resp); encErr != nil {
				return encErr
			}
		}
		if errors.Is(err, io.EOF) {
			return nil
		}
		if err != nil {
			return err
		}
	}
}

// readBoundedLine reads up to the next newline. When the line is longer than
// max, the rest of it is read and dropped and tooLong is true, so memory stays
// bounded however long the input line is.
func readBoundedLine(r *bufio.Reader, max int) (line []byte, tooLong bool, err error) {
	for {
		chunk, readErr := r.ReadSlice('\n')
		if !tooLong {
			if len(line)+len(chunk) > max {
				tooLong = true
				line = nil
			} else {
				line = append(line, chunk...)
			}
		}
		if errors.Is(readErr, bufio.ErrBufferFull) {
			continue
		}
		return line, tooLong, readErr
	}
}

// validRPCID reports whether raw is a JSON-RPC 2.0 id: a string, a number, or null.
func validRPCID(raw json.RawMessage) bool {
	trimmed := bytes.TrimSpace(raw)
	if len(trimmed) == 0 {
		return false
	}
	switch trimmed[0] {
	case '"', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9':
		return true
	}
	return string(trimmed) == "null"
}

// handle returns nil for notifications, which take no response.
func (s *mcpServer) handle(ctx context.Context, line []byte) *rpcResponse {
	var req rpcRequest
	if err := json.Unmarshal(line, &req); err != nil {
		return &rpcResponse{JSONRPC: "2.0", ID: json.RawMessage("null"), Error: &rpcError{Code: -32700, Message: "parse error"}}
	}
	invalid := func(msg string) *rpcResponse {
		return &rpcResponse{JSONRPC: "2.0", ID: json.RawMessage("null"), Error: &rpcError{Code: -32600, Message: msg}}
	}
	if req.JSONRPC != "2.0" {
		return invalid(`invalid request: jsonrpc must be "2.0"`)
	}
	if len(req.ID) == 0 {
		return nil
	}
	if !validRPCID(req.ID) {
		return invalid("invalid request: id must be a string, a number or null")
	}
	reply := func(result any) *rpcResponse { return &rpcResponse{JSONRPC: "2.0", ID: req.ID, Result: result} }
	fail := func(code int, msg string) *rpcResponse {
		return &rpcResponse{JSONRPC: "2.0", ID: req.ID, Error: &rpcError{Code: code, Message: msg}}
	}

	switch req.Method {
	case "initialize":
		var p struct {
			ProtocolVersion string `json:"protocolVersion"`
			ClientInfo      struct {
				Name string `json:"name"`
			} `json:"clientInfo"`
		}
		if err := json.Unmarshal(req.Params, &p); err != nil || p.ProtocolVersion == "" {
			return fail(-32602, "invalid params: protocolVersion is required")
		}
		s.clientName = p.ClientInfo.Name
		s.initialized = true
		// The server answers with the one version it implements, whatever the
		// client asked for; a client that cannot use it disconnects (MCP lifecycle).
		return reply(map[string]any{
			"protocolVersion": mcpProtocolVersion,
			"capabilities":    map[string]any{"tools": map[string]any{}},
			"serverInfo":      map[string]string{"name": "sei", "version": BuildVersion},
		})
	case "ping":
		return reply(map[string]any{})
	case "tools/list":
		return reply(map[string]any{"tools": s.tools()})
	case "tools/call":
		if !s.initialized {
			return fail(-32600, "invalid request: initialize must complete before tools/call")
		}
		var p struct {
			Name      string         `json:"name"`
			Arguments map[string]any `json:"arguments"`
		}
		if err := json.Unmarshal(req.Params, &p); err != nil {
			return fail(-32602, "invalid params")
		}
		text, err := s.call(ctx, p.Name, p.Arguments)
		if err != nil {
			// Tool failures are reported to the model as results, per the protocol.
			return reply(map[string]any{"isError": true, "content": []map[string]string{{"type": "text", "text": err.Error()}}})
		}
		return reply(map[string]any{"content": []map[string]string{{"type": "text", "text": text}}})
	default:
		return fail(-32601, "method not found: "+req.Method)
	}
}

func stringProp(desc string) map[string]any {
	return map[string]any{"type": "string", "description": desc}
}

func listProp(desc string) map[string]any {
	return map[string]any{"type": "array", "items": map[string]any{"type": "string"}, "description": desc}
}

func (s *mcpServer) tools() []mcpTool {
	tools := []mcpTool{
		{
			Name:        "resume",
			Description: "Show where the work stands. With both record_id and snapshot_digest from a prior resume, return that stored record as JSON data only. A stale binding is refused; an unknown record remains not verified. Reading does not approve content or grant authority.",
			InputSchema: map[string]any{"type": "object", "additionalProperties": false,
				"properties": map[string]any{
					"record_id":       stringProp("Original record ID from resume; requires snapshot_digest"),
					"snapshot_digest": stringProp("Original bundle SHA-256 from the same resume; requires record_id"),
				}},
		},
		{
			Name:        "add_recommendation",
			Description: "Record a recommendation. This is a proposal only. It does not decide anything and does not authorize any action. The record is attributed to the connected client.",
			InputSchema: map[string]any{
				"type":     "object",
				"required": []string{"id", "statement"},
				"properties": map[string]any{
					"id":        stringProp("Unique identifier for this recommendation"),
					"statement": stringProp("What you recommend"),
					"rationale": stringProp("Why"),
					"basis":     listProp("Evidence references written kind:id"),
				},
			},
		},
	}
	tools = append(tools, mcpTool{
		Name:        "check_decision",
		Description: "Before acting, ask whether a recorded decision meets the policy. allow does not prove the responsible party has Authority and does not run anything; read not_verified in the result.",
		InputSchema: map[string]any{
			"type":     "object",
			"required": []string{"decision"},
			"properties": map[string]any{
				"decision":               stringProp("Id of the recorded decision the action relies on"),
				"scope":                  stringProp("Scope of that decision. Required when the same id exists in more than one scope; an empty string names the decision with no scope. Without it, an id that matches several decisions is denied as ambiguous"),
				"require_recommendation": map[string]any{"type": "boolean", "description": "Deny when no recorded recommendation is relied on by the decision"},
				"deny_unresolved":        map[string]any{"type": "boolean", "description": "Deny when the decision left questions unresolved"},
			},
		},
	})
	if s.allowDecision {
		tools = append(tools, mcpTool{
			Name:        "add_decision",
			Description: "Record a decision made by a named responsible party. A decision needs someone to answer for it: responsible is required. The record is attributed to the connected client.",
			InputSchema: map[string]any{
				"type":     "object",
				"required": []string{"id", "statement", "responsible"},
				"properties": map[string]any{
					"id":             stringProp("Unique identifier for this decision"),
					"statement":      stringProp("What was decided"),
					"rationale":      stringProp("Why"),
					"basis":          listProp("Evidence references written kind:id"),
					"recommendation": listProp("Ids of recorded recommendations this decision relies on; each must already exist in the store"),
					"unresolved":     listProp("Questions left open, written kind:id"),
					"responsible":    listProp("Who answers for this decision, written kind:id (at least one)"),
				},
			},
		})
	}
	return tools
}

// checkKeys refuses any argument the tool does not accept.
func checkKeys(tool string, args map[string]any) error {
	allowed := map[string]bool{}
	for _, k := range mcpArgKeys[tool] {
		allowed[k] = true
	}
	for k := range args {
		if !allowed[k] {
			return fmt.Errorf("%s does not accept the argument %q; check the spelling", tool, k)
		}
	}
	return nil
}

// requiredString returns a non-empty string argument or an error.
func requiredString(args map[string]any, key string) (string, error) {
	v, ok := args[key]
	if !ok {
		return "", fmt.Errorf("%s is required", key)
	}
	text, ok := v.(string)
	if !ok {
		return "", fmt.Errorf("%s must be a string", key)
	}
	if strings.TrimSpace(text) == "" {
		return "", fmt.Errorf("%s must not be empty", key)
	}
	return text, nil
}

// optionalString returns a string argument, or "" when absent.
func optionalString(args map[string]any, key string) (string, error) {
	if _, ok := args[key]; !ok {
		return "", nil
	}
	text, ok := args[key].(string)
	if !ok {
		return "", fmt.Errorf("%s must be a string", key)
	}
	return text, nil
}

// boolArg returns a boolean argument, or false when absent. A value that is
// not a boolean is an error, because "true" as a string must not mean "off".
func boolArg(args map[string]any, key string) (bool, error) {
	v, ok := args[key]
	if !ok {
		return false, nil
	}
	b, ok := v.(bool)
	if !ok {
		return false, fmt.Errorf("%s must be true or false, not %v", key, v)
	}
	return b, nil
}

// listArg returns an array of non-empty strings, or nil when absent.
func listArg(args map[string]any, key string) ([]string, error) {
	v, ok := args[key]
	if !ok {
		return nil, nil
	}
	items, ok := v.([]any)
	if !ok {
		return nil, fmt.Errorf("%s must be an array of strings", key)
	}
	var out []string
	for _, item := range items {
		text, ok := item.(string)
		if !ok {
			return nil, fmt.Errorf("%s must contain only strings", key)
		}
		if strings.TrimSpace(text) == "" {
			return nil, fmt.Errorf("%s must not contain an empty value", key)
		}
		out = append(out, text)
	}
	return out, nil
}

// flagArgs builds --name=value arguments. The "=" form keeps a value that
// begins with "-" from being read as another flag.
func flagArgs(name string, values ...string) []string {
	var out []string
	for _, v := range values {
		out = append(out, "--"+name+"="+v)
	}
	return out
}

// provenance is the client name given at initialize. It is not taken from the
// tool arguments, so a caller cannot attribute its record to another tool.
func (s *mcpServer) provenance() string {
	// A client name that sei add would refuse as a source (blank, padded or with a
	// control character) is replaced, so a hostile name is never stored and the
	// connection still works (#757).
	if s.clientName != "" && checkIdentifier("clientInfo.name", s.clientName) == nil {
		return s.clientName
	}
	return defaultProvenance
}

func (s *mcpServer) call(ctx context.Context, name string, args map[string]any) (string, error) {
	if _, ok := mcpArgKeys[name]; !ok {
		return "", fmt.Errorf("unknown tool %q", name)
	}
	if err := checkKeys(name, args); err != nil {
		return "", err
	}
	var cli []string
	switch name {
	case "resume":
		cli = []string{"resume", "--data-root=" + s.dataRoot}
		_, hasID := args["record_id"]
		_, hasDigest := args["snapshot_digest"]
		if hasID || hasDigest {
			id, err := optionalString(args, "record_id")
			if err != nil {
				return "", err
			}
			digest, err := optionalString(args, "snapshot_digest")
			if err != nil {
				return "", err
			}
			// Forward even missing/empty values so the same CLI preconditions
			// reject the lookup rather than silently falling back to a listing.
			cli = append(cli, "--json")
			cli = append(cli, flagArgs("record-id", id)...)
			cli = append(cli, flagArgs("snapshot-digest", digest)...)
		}
	case "check_decision":
		id, err := requiredString(args, "decision")
		if err != nil {
			return "", err
		}
		cli = []string{"gate", "check", "--data-root=" + s.dataRoot, "--decision=" + id}
		if _, ok := args["scope"]; ok {
			scope, err := optionalString(args, "scope")
			if err != nil {
				return "", err
			}
			cli = append(cli, "--scope="+scope)
		}
		for _, key := range []string{"require_recommendation", "deny_unresolved"} {
			on, err := boolArg(args, key)
			if err != nil {
				return "", err
			}
			if on {
				cli = append(cli, "--"+strings.ReplaceAll(key, "_", "-")+"=true")
			}
		}
	case "add_recommendation", "add_decision":
		kind := "recommendation"
		if name == "add_decision" {
			if !s.allowDecision {
				return "", errors.New("add_decision is not enabled on this server")
			}
			kind = "decision"
		}
		id, err := requiredString(args, "id")
		if err != nil {
			return "", err
		}
		statement, err := requiredString(args, "statement")
		if err != nil {
			return "", err
		}
		rationale, err := optionalString(args, "rationale")
		if err != nil {
			return "", err
		}
		basis, err := listArg(args, "basis")
		if err != nil {
			return "", err
		}
		cli = []string{"add", kind, "--data-root=" + s.dataRoot}
		cli = append(cli, flagArgs("id", id)...)
		cli = append(cli, flagArgs("statement", statement)...)
		if rationale != "" {
			cli = append(cli, flagArgs("rationale", rationale)...)
		}
		cli = append(cli, flagArgs("source", s.provenance())...)
		cli = append(cli, flagArgs("basis", basis...)...)
		if kind == "decision" {
			responsible, err := listArg(args, "responsible")
			if err != nil {
				return "", err
			}
			if len(responsible) == 0 {
				return "", errors.New("a decision requires at least one responsible party")
			}
			recommendations, err := listArg(args, "recommendation")
			if err != nil {
				return "", err
			}
			unresolved, err := listArg(args, "unresolved")
			if err != nil {
				return "", err
			}
			cli = append(cli, flagArgs("recommendation", recommendations...)...)
			cli = append(cli, flagArgs("unresolved", unresolved...)...)
			cli = append(cli, flagArgs("responsible", responsible...)...)
		}
	}
	var out, errOut bytes.Buffer
	if err := Run(ctx, cli, &out, &errOut); err != nil {
		// A denied check is a valid answer, not a tool failure: keep the verdict.
		var exit *ExitError
		if errors.As(err, &exit) && exit.Code == ExitCodeDenied {
			return strings.TrimSpace(out.String()), nil
		}
		return "", errors.New(strings.TrimSpace(err.Error()))
	}
	return strings.TrimSpace(out.String()), nil
}
