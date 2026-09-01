package teiintegration

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/hat47x/soza/runtime/go/provideradapter"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

func helperCLI() CLI {
	return CLI{
		Executable: os.Args[0],
		PrefixArgs: []string{"-test.run=TestTEIHelperProcess", "--"},
	}
}

func providerPlanRequest() ProviderPlanRequest {
	revision := 3
	return ProviderPlanRequest{
		Workspace:        "/reference/workspace",
		Run:              "/reference/run.json",
		Solution:         "order_rollout",
		Version:          "2026.8.27",
		PluginLock:       "/reference/plugin-lock.json",
		ExpectedRevision: &revision,
	}
}

func observationContext() provideradapter.ObservationContext {
	return provideradapter.ObservationContext{
		ObservationID: "obs-tei-cli-provider-plan",
		CapabilityRef: semanticruntime.LogicalReference{
			Kind: "capability",
			ID:   "deployment-provider-routing",
		},
		ObservedAt:     "2026-09-02T00:00:00Z",
		SourceStateRef: "tei-cli-external-process:reference-plan",
	}
}

func TestObserveProviderPlanMapsOnlyProviderNeutralMeaning(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "success")

	document, err := helperCLI().ObserveProviderPlan(context.Background(), providerPlanRequest(), observationContext())
	if err != nil {
		t.Fatalf("ObserveProviderPlan() error = %v", err)
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		t.Fatalf("mapped Capability Observation did not validate: %v", err)
	}
	if document.Observation.Target.ProviderRef == nil || document.Observation.Target.ProviderRef.ID != teiCLIProviderID {
		t.Fatalf("provider ref = %#v", document.Observation.Target.ProviderRef)
	}
	if document.Observation.Target.ProviderTargetRef != "tei-cli:deployment-provider-plan" {
		t.Fatalf("provider target ref = %q", document.Observation.Target.ProviderTargetRef)
	}

	encoded, err := json.Marshal(document)
	if err != nil {
		t.Fatalf("marshal document: %v", err)
	}
	for _, forbidden := range []string{
		"executors",
		"observations",
		"evidence",
		"pluginRuntime",
		"tei.internal.observation-provider",
		"tei.internal.evidence-provider",
	} {
		if strings.Contains(string(encoded), forbidden) {
			t.Fatalf("Provider固有fieldまたは値がCapability Observationへ漏れています: %q in %s", forbidden, encoded)
		}
	}

	conditions := map[string]semanticruntime.ObservedCondition{}
	for _, condition := range document.Observation.Conditions {
		conditions[condition.Key] = condition
	}
	for _, key := range []string{"availability", "provider_plan_resolved"} {
		condition, ok := conditions[key]
		if !ok {
			t.Fatalf("condition %q is missing", key)
		}
		if condition.State != "observed" || string(condition.Value) != "true" {
			t.Fatalf("condition %q = state %q value %s", key, condition.State, condition.Value)
		}
	}
}

func TestObserveProviderPlanRejectsUnknownTopLevelField(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "unknown-field")

	document, err := helperCLI().ObserveProviderPlan(context.Background(), providerPlanRequest(), observationContext())
	if err == nil || !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("expected unknown field error, got document=%#v err=%v", document, err)
	}
	if document.Contract != "" {
		t.Fatalf("failure must not return a Capability Observation: %#v", document)
	}
}

func TestObserveProviderPlanRejectsMalformedJSON(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "malformed")

	document, err := helperCLI().ObserveProviderPlan(context.Background(), providerPlanRequest(), observationContext())
	if err == nil {
		t.Fatalf("expected malformed JSON error, got document=%#v", document)
	}
	if document.Contract != "" {
		t.Fatalf("failure must not return a Capability Observation: %#v", document)
	}
}

func TestObserveProviderPlanRejectsMultipleJSONValues(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "multiple-json")

	document, err := helperCLI().ObserveProviderPlan(context.Background(), providerPlanRequest(), observationContext())
	if err == nil || !strings.Contains(err.Error(), "複数のJSON値") {
		t.Fatalf("expected multiple JSON error, got document=%#v err=%v", document, err)
	}
	if document.Contract != "" {
		t.Fatalf("failure must not return a Capability Observation: %#v", document)
	}
}

func TestObserveProviderPlanRejectsEmptyRecognizedContent(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "empty")

	document, err := helperCLI().ObserveProviderPlan(context.Background(), providerPlanRequest(), observationContext())
	if err == nil || !strings.Contains(err.Error(), "recognized provider-plan information") {
		t.Fatalf("expected empty plan error, got document=%#v err=%v", document, err)
	}
	if document.Contract != "" {
		t.Fatalf("failure must not return a Capability Observation: %#v", document)
	}
}

func TestObserveProviderPlanRejectsProcessFailure(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "failure")

	document, err := helperCLI().ObserveProviderPlan(context.Background(), providerPlanRequest(), observationContext())
	if err == nil || !strings.Contains(err.Error(), "TEI reference process failure") {
		t.Fatalf("expected process failure, got document=%#v err=%v", document, err)
	}
	if document.Contract != "" {
		t.Fatalf("failure must not return a Capability Observation: %#v", document)
	}
}

func TestObserveProviderPlanRejectsTimeout(t *testing.T) {
	t.Setenv("SOZA_TEI_HELPER_PROCESS", "1")
	t.Setenv("SOZA_TEI_HELPER_MODE", "slow")

	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()
	document, err := helperCLI().ObserveProviderPlan(ctx, providerPlanRequest(), observationContext())
	if err == nil || !errors.Is(err, context.DeadlineExceeded) {
		t.Fatalf("expected deadline exceeded, got document=%#v err=%v", document, err)
	}
	if document.Contract != "" {
		t.Fatalf("timeout must not return a Capability Observation: %#v", document)
	}
}

func TestProviderPlanRequestRequiresExternalInputs(t *testing.T) {
	request := providerPlanRequest()
	request.PluginLock = ""
	_, err := helperCLI().ObserveProviderPlan(context.Background(), request, observationContext())
	if err == nil || !strings.Contains(err.Error(), "plugin lock") {
		t.Fatalf("expected explicit TEI input validation, got %v", err)
	}
}

func TestTEIHelperProcess(t *testing.T) {
	if os.Getenv("SOZA_TEI_HELPER_PROCESS") != "1" {
		return
	}

	separator := -1
	for index, arg := range os.Args {
		if arg == "--" {
			separator = index
			break
		}
	}
	if separator < 0 || separator+1 >= len(os.Args) {
		fmt.Fprintln(os.Stderr, "helper did not receive TEI command")
		os.Exit(2)
	}
	args := os.Args[separator+1:]
	if args[0] != "deployment-provider-plan" {
		fmt.Fprintf(os.Stderr, "unexpected TEI command %q\n", args[0])
		os.Exit(2)
	}
	for _, expected := range []string{"-workspace", "-run", "-solution", "-version", "-plugin-lock", "-expected-revision"} {
		if !containsArg(args, expected) {
			fmt.Fprintf(os.Stderr, "required argument %s is missing\n", expected)
			os.Exit(2)
		}
	}

	switch os.Getenv("SOZA_TEI_HELPER_MODE") {
	case "success":
		fmt.Print(`{"executors":[{"provider":"tei.internal.executor"}],"observations":[{"kind":"deployment-state","provider":"tei.internal.observation-provider"}],"evidence":[{"kind":"deployment-evidence","provider":"tei.internal.evidence-provider","actionId":"action-1"}],"pluginRuntime":{"provider":"tei.internal.runtime"}}`)
	case "unknown-field":
		fmt.Print(`{"observations":[{"kind":"deployment-state","provider":"tei.internal.observation-provider"}],"futureField":true}`)
	case "malformed":
		fmt.Print(`{"observations":[`)
	case "multiple-json":
		fmt.Print(`{"observations":[{"kind":"deployment-state","provider":"tei.internal.observation-provider"}]} {"second":true}`)
	case "empty":
		fmt.Print(`{}`)
	case "failure":
		fmt.Fprintln(os.Stderr, "TEI reference process failure")
		os.Exit(7)
	case "slow":
		time.Sleep(2 * time.Second)
		fmt.Print(`{"observations":[{"kind":"deployment-state","provider":"tei.internal.observation-provider"}]}`)
	default:
		fmt.Fprintln(os.Stderr, "unknown helper mode")
		os.Exit(2)
	}
	os.Exit(0)
}

func containsArg(args []string, expected string) bool {
	for _, arg := range args {
		if arg == expected {
			return true
		}
	}
	return false
}
