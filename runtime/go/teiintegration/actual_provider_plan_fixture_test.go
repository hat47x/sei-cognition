package teiintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"strings"
	"testing"

	"github.com/hat47x/soza/runtime/go/provideradapter"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const actualTEIProviderPlanSHA256 = "39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950"

// TestActualTEIProviderPlanFixtureMapsThroughCurrentBoundary は、固定した実TEIの
// deployment-provider-plan出力をcurrent SOZA runtimeで読み、Provider固有情報を
// Universal Capability Observationへ持ち込まずにmappingできることを確認します。
// このfixture test自体は実processの起動Evidenceではなく、実出力との互換性を継続して
// 検査するための回帰テストです。
func TestActualTEIProviderPlanFixtureMapsThroughCurrentBoundary(t *testing.T) {
	payload, err := os.ReadFile("testdata/tei-provider-plan-48a7ca1f.json")
	if err != nil {
		t.Fatalf("実TEIのProvider Plan fixtureを読めません: %v", err)
	}
	digest := sha256.Sum256(payload)
	if got := hex.EncodeToString(digest[:]); got != actualTEIProviderPlanSHA256 {
		t.Fatalf("実TEI Provider PlanのSHA-256 = %q, want %q", got, actualTEIProviderPlanSHA256)
	}

	if _, err := decodeProviderPlan(payload); err != nil {
		t.Fatalf("current Adapterで実TEIのProvider Planを読めません: %v", err)
	}

	document, err := buildObservation(provideradapter.ObservationContext{
		ObservationID: "obs-tei-actual-provider-plan-fixture",
		CapabilityRef: semanticruntime.LogicalReference{
			Kind: "capability",
			ID:   "deployment-provider-routing",
		},
		ObservedAt:     "2026-09-02T00:00:00Z",
		SourceStateRef: "tei-cli:48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67:provider-plan-fixture",
	})
	if err != nil {
		t.Fatalf("実TEI Provider Planのmappingに失敗しました: %v", err)
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		t.Fatalf("mapping後のCapability Observationがcurrent validatorを通りません: %v", err)
	}

	encoded, err := json.Marshal(document)
	if err != nil {
		t.Fatalf("Capability ObservationをJSON化できません: %v", err)
	}
	for _, forbidden := range []string{
		"migration.atlas",
		"pluginRuntime",
		"resourceBindings",
		"TEI_DATABASE_CREDENTIAL",
	} {
		if strings.Contains(string(encoded), forbidden) {
			t.Fatalf("TEI固有情報がCapability Observationへ漏れています: %q in %s", forbidden, encoded)
		}
	}
}
