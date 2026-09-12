package modelprobe

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
)

func fixtureByID(t *testing.T, id string) cognitiveeval.Fixture {
	t.Helper()
	for _, f := range cognitiveeval.ReferenceFixtures() {
		if f.ID == id {
			return f
		}
	}
	t.Fatalf("fixture not found: %s", id)
	return cognitiveeval.Fixture{}
}

func TestBuildPlanRawAndWorkspaceInvokeModel(t *testing.T) {
	f := fixtureByID(t, "current-external-fact")
	for _, mode := range []Mode{ModeRaw, ModeWorkspace} {
		plan, err := BuildPlan(f, mode)
		if err != nil {
			t.Fatal(err)
		}
		if !plan.ShouldInvokeModel {
			t.Fatalf("%s baseline should invoke model for comparison", mode)
		}
		if !plan.BoundaryBypassedForBaseline {
			t.Fatalf("%s should mark staged-boundary bypass", mode)
		}
	}
}

func TestBuildPlanStagedSkipsExternalEvidenceCase(t *testing.T) {
	f := fixtureByID(t, "current-external-fact")
	plan, err := BuildPlan(f, ModeStaged)
	if err != nil {
		t.Fatal(err)
	}
	if plan.ShouldInvokeModel {
		t.Fatal("staged route must not call local model for current external fact")
	}
	if plan.Route != "external-evidence-required" {
		t.Fatalf("route=%s", plan.Route)
	}
}

func TestBuildPlanStagedSkipsHighNovelty(t *testing.T) {
	f := fixtureByID(t, "high-novelty")
	plan, err := BuildPlan(f, ModeStaged)
	if err != nil {
		t.Fatal(err)
	}
	if plan.ShouldInvokeModel {
		t.Fatal("high-novelty staged route must not guess with local model")
	}
	if plan.Route != "abstain-or-expand-evidence" {
		t.Fatalf("route=%s", plan.Route)
	}
}

func TestWorkspacePromptCarriesSemanticBoundary(t *testing.T) {
	f := fixtureByID(t, "decision-with-unknown")
	plan, err := BuildPlan(f, ModeWorkspace)
	if err != nil {
		t.Fatal(err)
	}
	for _, want := range []string{"must_preserve_unknown_and_conflict", "recommendation_is_not_decision", "unk-2"} {
		if !strings.Contains(plan.UserPrompt, want) {
			t.Fatalf("workspace prompt missing %q", want)
		}
	}
}

func TestDecodeModelOutputAcceptsJSONFence(t *testing.T) {
	content := "```json\n{\"proposal\":\"ok\",\"need_more_evidence\":false}\n```"
	out, err := DecodeModelOutput(content)
	if err != nil {
		t.Fatal(err)
	}
	if out.Proposal != "ok" {
		t.Fatalf("proposal=%q", out.Proposal)
	}
}

func TestRunCallsOpenAICompatibleEndpointAndEvaluates(t *testing.T) {
	f := fixtureByID(t, "recommendation-not-decision")
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Fatalf("method=%s", r.Method)
		}
		var req map[string]any
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			t.Fatal(err)
		}
		if req["model"] != "tiny-local" {
			t.Fatalf("model=%v", req["model"])
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]any{
			"choices": []any{map[string]any{
				"message": map[string]any{
					"content": `{"proposal":"B is faster, but A remains the recorded Decision.","supporting_refs":["obs-3","rec-3","dec-3"],"decision_basis_refs":["obs-3"],"recommendation_ref":"rec-3","decision_ref":"dec-3","need_more_evidence":false,"claims":[{"text":"B had lower measured latency.","supporting_refs":["obs-3"]}]}`,
				},
			}},
			"usage": map[string]any{"prompt_tokens": 100, "completion_tokens": 40, "total_tokens": 140},
		})
	}))
	defer server.Close()

	result, err := Run(context.Background(), Config{
		Endpoint: server.URL,
		Model: "tiny-local",
		MaxTokens: 512,
		HTTPClient: server.Client(),
	}, f, ModeWorkspace)
	if err != nil {
		t.Fatal(err)
	}
	if result.Skipped {
		t.Fatal("workspace comparison unexpectedly skipped")
	}
	if result.Evaluation == nil || !result.Evaluation.RecommendationDecisionSeparated {
		t.Fatal("expected Recommendation/Decision separation to pass")
	}
	if result.Usage.TotalTokens != 140 {
		t.Fatalf("usage=%+v", result.Usage)
	}
}

func TestRunStagedCanSkipWithoutEndpoint(t *testing.T) {
	f := fixtureByID(t, "deterministic")
	result, err := Run(context.Background(), Config{}, f, ModeStaged)
	if err != nil {
		t.Fatal(err)
	}
	if !result.Skipped {
		t.Fatal("deterministic staged case should skip model")
	}
	if result.Route != "symbolic" {
		t.Fatalf("route=%s", result.Route)
	}
}
