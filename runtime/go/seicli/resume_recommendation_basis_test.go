package seicli

import (
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"
)

func TestResumeShowsRecommendationBasisRationaleAndResponsible(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R-with", "--statement", "with basis",
		"--rationale", "because of the survey", "--basis", "observation:survey-1", "--responsible", "person:alice")
	mustRun(t, "add", "recommendation", "--data-root", root, "--id", "R-without", "--statement", "no basis")

	out := mustRun(t, "resume", "--data-root", root, "--json")
	var got struct {
		Open []map[string]any `json:"recommendations_not_yet_relied_on"`
	}
	if err := json.Unmarshal([]byte(out), &got); err != nil {
		t.Fatal(err)
	}
	byID := map[string]map[string]any{}
	for _, r := range got.Open {
		byID[r["id"].(string)] = r
	}
	with, without := byID["R-with"], byID["R-without"]
	if with == nil || without == nil {
		t.Fatalf("both recommendations must be listed: %v", got.Open)
	}
	basis, _ := with["basis_references"].([]any)
	if len(basis) != 1 || basis[0].(map[string]any)["id"] != "survey-1" || basis[0].(map[string]any)["form"] != "logical" {
		t.Errorf("basis_references must carry the recorded basis: %v", with["basis_references"])
	}
	if resp, _ := with["responsibility_references"].([]any); len(resp) != 1 {
		t.Errorf("responsibility_references must carry the responsible party: %v", with["responsibility_references"])
	}
	if with["rationale"] != "because of the survey" {
		t.Errorf("rationale = %v", with["rationale"])
	}
	// A recommendation with none of these keeps its old shape.
	for _, key := range []string{"basis_references", "responsibility_references", "rationale"} {
		if _, present := without[key]; present {
			t.Errorf("%s must be omitted when the recommendation has none: %v", key, without)
		}
	}

	human := mustRun(t, "resume", "--data-root", root)
	if !strings.Contains(human, "[R-with] with basis") || !strings.Contains(human, "basis: observation:survey-1") || !strings.Contains(human, "responsible: person:alice") {
		t.Errorf("human view must show the basis and responsible of R-with:\n%s", human)
	}
	idx := strings.Index(human, "[R-without]")
	if idx < 0 || strings.Contains(human[idx:], "basis:") {
		t.Errorf("R-without must show no basis line:\n%s", human)
	}
}
