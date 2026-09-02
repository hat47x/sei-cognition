package teiintegration

import (
	"context"
	"encoding/json"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/hat47x/soza/runtime/go/provideradapter"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

// TestLiveTEIProviderPlan は、外部から用意された実TEI CLIを使うE3b-P2専用検査です。
// 通常の単体テストでは実行せず、固定revisionのTEI executableとReference Workspaceを
// 明示的に与えた場合だけ実行します。資格情報やTEIの取得方法そのものは、このテストの
// 意味契約には含めません。
func TestLiveTEIProviderPlan(t *testing.T) {
	if os.Getenv("SOZA_E3B_TEI_LIVE") != "1" {
		t.Skip("SOZA_E3B_TEI_LIVE=1 の場合だけ実TEI検査を実行します")
	}

	executable := requireLiveTEIEnv(t, "SOZA_TEI_EXECUTABLE")
	workspace := requireLiveTEIEnv(t, "SOZA_TEI_WORKSPACE")
	run := requireLiveTEIEnv(t, "SOZA_TEI_RUN")
	pluginLock := requireLiveTEIEnv(t, "SOZA_TEI_PLUGIN_LOCK")
	sourceStateRef := requireLiveTEIEnv(t, "SOZA_TEI_SOURCE_STATE_REF")

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	document, err := (CLI{Executable: executable}).ObserveProviderPlan(
		ctx,
		ProviderPlanRequest{
			Workspace:  workspace,
			Run:        run,
			Solution:   "order_rollout",
			Version:    "2026.8.27",
			PluginLock: pluginLock,
		},
		provideradapter.ObservationContext{
			ObservationID: "obs-live-tei-provider-plan",
			CapabilityRef: semanticruntime.LogicalReference{
				Kind: "capability",
				ID:   "deployment-provider-routing",
			},
			ObservedAt:     "2026-09-02T00:00:00Z",
			SourceStateRef: sourceStateRef,
		},
	)
	if err != nil {
		t.Fatalf("実TEIのdeployment-provider-planをCapability Observationへ戻せませんでした: %v", err)
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		t.Fatalf("実TEIから変換したCapability Observationがcurrent validatorを通りません: %v", err)
	}
	if document.Observation.MappingProvenance == nil || document.Observation.MappingProvenance.SourceStateRef != sourceStateRef {
		t.Fatalf("実TEIのsource state provenanceが保持されていません: %#v", document.Observation.MappingProvenance)
	}

	conditions := map[string]semanticruntime.ObservedCondition{}
	for _, condition := range document.Observation.Conditions {
		conditions[condition.Key] = condition
	}
	for _, key := range []string{"availability", "provider_plan_resolved"} {
		condition, ok := conditions[key]
		if !ok || condition.State != "observed" || string(condition.Value) != "true" {
			t.Fatalf("実TEIの観測条件 %q が成立していません: %#v", key, condition)
		}
	}

	encoded, err := json.Marshal(document)
	if err != nil {
		t.Fatalf("Capability ObservationをJSON化できません: %v", err)
	}
	for _, forbidden := range []string{"executors", "observations", "evidence", "pluginRuntime"} {
		if strings.Contains(string(encoded), forbidden) {
			t.Fatalf("TEI固有fieldがCapability Observationへ漏れています: %q in %s", forbidden, encoded)
		}
	}
}

func requireLiveTEIEnv(t *testing.T, key string) string {
	t.Helper()
	value := strings.TrimSpace(os.Getenv(key))
	if value == "" {
		t.Fatalf("実TEI検査には環境変数 %s が必要です", key)
	}
	return value
}
