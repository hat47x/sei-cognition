// Package modelprobe connects the evaluation-only cognitive comparison fixtures
// to a localhost OpenAI-compatible chat-completions endpoint.
//
// It intentionally treats model output as proposal/evaluation material only.
// Hidden chain-of-thought is neither requested nor represented.
package modelprobe

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

type Mode string

const (
	ModeRaw       Mode = "raw"
	ModeWorkspace Mode = "workspace"
	ModeStaged    Mode = "staged"
)

type Plan struct {
	FixtureID                   string            `json:"fixture_id"`
	Mode                        Mode              `json:"mode"`
	ShouldInvokeModel           bool              `json:"should_invoke_model"`
	Reason                      string            `json:"reason"`
	BoundaryBypassedForBaseline bool              `json:"boundary_bypassed_for_baseline"`
	Route                       string            `json:"route"`
	SystemPrompt                string            `json:"system_prompt,omitempty"`
	UserPrompt                  string            `json:"user_prompt,omitempty"`
	RequestChars                int               `json:"request_chars"`
	RefAliases                  map[string]string `json:"-"`
}

type Config struct {
	Endpoint    string
	Model       string
	MaxTokens   int
	Temperature float64
	HTTPClient  *http.Client
}

type TokenUsage struct {
	PromptTokens     int `json:"prompt_tokens,omitempty"`
	CompletionTokens int `json:"completion_tokens,omitempty"`
	TotalTokens      int `json:"total_tokens,omitempty"`
}

type Result struct {
	FixtureID      string                         `json:"fixture_id"`
	Mode           Mode                           `json:"mode"`
	Model          string                         `json:"model"`
	Endpoint       string                         `json:"endpoint"`
	Skipped        bool                           `json:"skipped"`
	SkipReason     string                         `json:"skip_reason,omitempty"`
	Route          string                         `json:"route"`
	RequestChars   int                            `json:"request_chars"`
	ResponseChars  int                            `json:"response_chars,omitempty"`
	TotalLatencyMS int64                          `json:"total_latency_ms,omitempty"`
	HTTPStatus     int                            `json:"http_status,omitempty"`
	Usage          TokenUsage                     `json:"usage,omitempty"`
	Output         *cognitiveeval.ModelOutput      `json:"output,omitempty"`
	Evaluation     *cognitiveeval.EvaluationReport `json:"evaluation,omitempty"`
	RawContent     string                         `json:"raw_content,omitempty"`
}

const systemPrompt = `You are an evaluation-only bounded reasoner.
Use only the material supplied by the user message.
Do not invent missing evidence. Preserve unresolved Unknown and Conflict items.
A Recommendation is not a Decision. Later-captured evidence must not be inserted into a historical Decision basis.
Return ONLY one JSON object. Do not output hidden reasoning or chain-of-thought.
The JSON shape is:
{
  "proposal": "string",
  "supporting_refs": ["ref"],
  "decision_basis_refs": ["ref"],
  "preserved_unknown_refs": ["ref"],
  "preserved_conflict_refs": ["ref"],
  "recommendation_ref": "ref or empty string",
  "decision_ref": "ref or empty string",
  "need_more_evidence": true,
  "claims": [
    {"text": "material claim", "supporting_refs": ["ref"]}
  ]
}
Every material claim should cite the record refs actually used.`

func BuildPlan(f cognitiveeval.Fixture, mode Mode) (Plan, error) {
	bundle, err := cognitiveeval.BuildComparisonBundle(f)
	if err != nil {
		return Plan{}, err
	}

	plan := Plan{
		FixtureID: f.ID,
		Mode:      mode,
		Route:     string(bundle.Staged.Routing.Route),
	}

	var material string
	switch mode {
	case ModeRaw:
		plan.ShouldInvokeModel = true
		plan.Reason = "raw-context baseline intentionally bypasses staged routing"
		plan.BoundaryBypassedForBaseline = !bundle.Staged.Routing.LocalModelAllowed
		plan.RefAliases = map[string]string{}
		flat := make([]string, 0, len(f.Records))
		for i, record := range f.Records {
			alias := fmt.Sprintf("R%03d", i+1)
			plan.RefAliases[alias] = record.Ref
			line := fmt.Sprintf("[%s] %s", alias, record.Summary)
			if record.CapturedAt != "" {
				line += " | captured_at=" + record.CapturedAt
			}
			if record.SubjectAt != "" {
				line += " | subject_at=" + record.SubjectAt
			}
			flat = append(flat, line)
		}
		material = "OBJECTIVE:\n" + bundle.Raw.Objective +
			"\n\nRAW CONTEXT:\n" + bundle.Raw.Context +
			"\n\nREFERENCE MATERIAL (opaque IDs; semantic role labels intentionally omitted):\n" +
			strings.Join(flat, "\n")
	case ModeWorkspace:
		plan.ShouldInvokeModel = true
		plan.Reason = "workspace comparison intentionally holds model constant"
		plan.BoundaryBypassedForBaseline = !bundle.Staged.Routing.LocalModelAllowed
		encoded, err := json.MarshalIndent(bundle.Workspace, "", "  ")
		if err != nil {
			return Plan{}, fmt.Errorf("marshal workspace: %w", err)
		}
		material = "COGNITIVE WORKSPACE:\n" + string(encoded)
	case ModeStaged:
		if !bundle.Staged.Routing.LocalModelAllowed {
			plan.ShouldInvokeModel = false
			plan.Reason = bundle.Staged.Routing.Reason
			return plan, nil
		}
		plan.ShouldInvokeModel = true
		plan.Reason = bundle.Staged.Routing.Reason
		encoded, err := json.MarshalIndent(bundle.Workspace, "", "  ")
		if err != nil {
			return Plan{}, fmt.Errorf("marshal workspace: %w", err)
		}
		material = "COGNITIVE WORKSPACE:\n" + string(encoded)
	default:
		return Plan{}, fmt.Errorf("unsupported probe mode %q", mode)
	}

	plan.SystemPrompt = systemPrompt
	plan.UserPrompt = material
	plan.RequestChars = len([]rune(plan.SystemPrompt)) + len([]rune(plan.UserPrompt))
	return plan, nil
}

type chatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type chatRequest struct {
	Model       string        `json:"model"`
	Messages    []chatMessage `json:"messages"`
	Temperature float64       `json:"temperature"`
	MaxTokens   int           `json:"max_tokens,omitempty"`
	Stream      bool          `json:"stream"`
}

type chatResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
	Usage TokenUsage `json:"usage"`
}

func Run(ctx context.Context, cfg Config, f cognitiveeval.Fixture, mode Mode) (Result, error) {
	plan, err := BuildPlan(f, mode)
	if err != nil {
		return Result{}, err
	}
	result := Result{
		FixtureID:    f.ID,
		Mode:         mode,
		Model:        cfg.Model,
		Endpoint:     cfg.Endpoint,
		Route:        plan.Route,
		RequestChars: plan.RequestChars,
	}
	if !plan.ShouldInvokeModel {
		result.Skipped = true
		result.SkipReason = plan.Reason
		return result, nil
	}
	if strings.TrimSpace(cfg.Endpoint) == "" {
		return Result{}, fmt.Errorf("endpoint is required")
	}
	if strings.TrimSpace(cfg.Model) == "" {
		return Result{}, fmt.Errorf("model is required")
	}

	client := cfg.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 120 * time.Second}
	}
	body := chatRequest{
		Model: cfg.Model,
		Messages: []chatMessage{
			{Role: "system", Content: plan.SystemPrompt},
			{Role: "user", Content: plan.UserPrompt},
		},
		Temperature: cfg.Temperature,
		MaxTokens:   cfg.MaxTokens,
		Stream:      false,
	}
	encoded, err := json.Marshal(body)
	if err != nil {
		return Result{}, fmt.Errorf("marshal chat request: %w", err)
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, cfg.Endpoint, bytes.NewReader(encoded))
	if err != nil {
		return Result{}, fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	started := time.Now()
	resp, err := client.Do(req)
	result.TotalLatencyMS = time.Since(started).Milliseconds()
	if err != nil {
		return result, fmt.Errorf("model request: %w", err)
	}
	defer resp.Body.Close()
	result.HTTPStatus = resp.StatusCode
	payload, err := io.ReadAll(io.LimitReader(resp.Body, 8<<20))
	if err != nil {
		return result, fmt.Errorf("read model response: %w", err)
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return result, fmt.Errorf("model endpoint returned %s: %s", resp.Status, strings.TrimSpace(string(payload)))
	}

	var decoded chatResponse
	if err := json.Unmarshal(payload, &decoded); err != nil {
		return result, fmt.Errorf("decode chat response: %w", err)
	}
	if len(decoded.Choices) == 0 {
		return result, fmt.Errorf("chat response has no choices")
	}
	content := decoded.Choices[0].Message.Content
	result.RawContent = content
	result.ResponseChars = len([]rune(content))
	result.Usage = decoded.Usage

	out, err := DecodeModelOutput(content)
	if err != nil {
		return result, err
	}
	if len(plan.RefAliases) > 0 {
		out = translateAliases(out, plan.RefAliases)
	}
	report, err := cognitiveeval.EvaluateOutput(f, out)
	if err != nil {
		return result, fmt.Errorf("evaluate model output: %w", err)
	}
	result.Output = &out
	result.Evaluation = &report
	return result, nil
}

func DecodeModelOutput(content string) (cognitiveeval.ModelOutput, error) {
	trimmed := strings.TrimSpace(content)
	if strings.HasPrefix(trimmed, "```") {
		lines := strings.Split(trimmed, "\n")
		if len(lines) >= 3 && strings.HasPrefix(lines[0], "```") && strings.TrimSpace(lines[len(lines)-1]) == "```" {
			trimmed = strings.Join(lines[1:len(lines)-1], "\n")
		}
	}
	var out cognitiveeval.ModelOutput
	decoder := json.NewDecoder(strings.NewReader(trimmed))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&out); err != nil {
		return cognitiveeval.ModelOutput{}, fmt.Errorf("model output is not valid expected JSON: %w", err)
	}
	if strings.TrimSpace(out.Proposal) == "" && !out.NeedMoreEvidence {
		return cognitiveeval.ModelOutput{}, fmt.Errorf("model output requires proposal or need_more_evidence=true")
	}
	return out, nil
}

func translateAliases(out cognitiveeval.ModelOutput, aliases map[string]string) cognitiveeval.ModelOutput {
	translate := func(ref string) string {
		if actual, ok := aliases[ref]; ok {
			return actual
		}
		return ref
	}
	translateSlice := func(refs []string) []string {
		translated := make([]string, len(refs))
		for i, ref := range refs {
			translated[i] = translate(ref)
		}
		return translated
	}

	out.SupportingRefs = translateSlice(out.SupportingRefs)
	out.DecisionBasisRefs = translateSlice(out.DecisionBasisRefs)
	out.PreservedUnknownRefs = translateSlice(out.PreservedUnknownRefs)
	out.PreservedConflictRefs = translateSlice(out.PreservedConflictRefs)
	out.RecommendationRef = translate(out.RecommendationRef)
	out.DecisionRef = translate(out.DecisionRef)
	for i := range out.Claims {
		out.Claims[i].SupportingRefs = translateSlice(out.Claims[i].SupportingRefs)
	}
	return out
}
