package provideradapter

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

func repositoryRoot(t *testing.T) string {
	t.Helper()
	_, currentFile, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("runtime.Caller failed")
	}
	return filepath.Clean(filepath.Join(filepath.Dir(currentFile), "..", "..", ".."))
}

func readProviderFixture(t *testing.T, name string) []byte {
	t.Helper()
	path := filepath.Join(repositoryRoot(t), "fixtures", "providers", "synthetic", name)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read provider fixture %s: %v", path, err)
	}
	return data
}

func testContext(id, source string) ObservationContext {
	return ObservationContext{
		ObservationID: id,
		CapabilityRef: semanticruntime.LogicalReference{Kind: "capability", ID: "document-summarization"},
		ObservedAt: "2026-08-31T02:10:00Z",
		SourceStateRef: source,
	}
}

func conditionByKey(t *testing.T, document semanticruntime.CapabilityObservationDocument, key string) semanticruntime.ObservedCondition {
	t.Helper()
	for _, condition := range document.Observation.Conditions {
		if condition.Key == key {
			return condition
		}
	}
	t.Fatalf("condition %q not found", key)
	return semanticruntime.ObservedCondition{}
}

func decodeValue[T any](t *testing.T, raw json.RawMessage) T {
	t.Helper()
	var value T
	if err := json.Unmarshal(raw, &value); err != nil {
		t.Fatalf("decode observed value: %v", err)
	}
	return value
}

func assertValidated(t *testing.T, document semanticruntime.CapabilityObservationDocument) {
	t.Helper()
	record, err := ValidateObservation(document)
	if err != nil {
		t.Fatalf("ValidateObservation: %v", err)
	}
	if record.Status != semanticruntime.RecordValidated || record.Capability == nil {
		t.Fatalf("adapter output not validated: %#v", record)
	}
}

func TestSyntheticProvidersMapDifferentInputShapesToCapabilityObservation(t *testing.T) {
	a, err := (ProviderAAdapter{}).Observe(testContext("adapter-A", "synthetic-a://snapshot/42"), readProviderFixture(t, "provider-a-green.json"))
	if err != nil {
		t.Fatal(err)
	}
	b, err := (ProviderBAdapter{}).Observe(testContext("adapter-B", "synthetic-b://snapshot/99"), readProviderFixture(t, "provider-b-ready.json"))
	if err != nil {
		t.Fatal(err)
	}

	assertValidated(t, a)
	assertValidated(t, b)

	if a.Observation.Target.CapabilityRef == nil || b.Observation.Target.CapabilityRef == nil || a.Observation.Target.CapabilityRef.ID != b.Observation.Target.CapabilityRef.ID {
		t.Fatal("A/B observations do not preserve the same capability identity")
	}
	if a.Observation.Target.ProviderRef == nil || b.Observation.Target.ProviderRef == nil || a.Observation.Target.ProviderRef.ID == b.Observation.Target.ProviderRef.ID {
		t.Fatal("A/B observations did not preserve distinct Provider identities")
	}

	for name, document := range map[string]semanticruntime.CapabilityObservationDocument{"A": a, "B": b} {
		availability := conditionByKey(t, document, "availability")
		if availability.State != "observed" || !decodeValue[bool](t, availability.Value) {
			t.Fatalf("%s availability was not mapped as observed true: %#v", name, availability)
		}
		latency := conditionByKey(t, document, "latency")
		if latency.State != "observed" || latency.Unit != "ms" || decodeValue[float64](t, latency.Value) != 240 {
			t.Fatalf("%s latency was not normalized to 240 ms: %#v", name, latency)
		}
		if document.Observation.Target.ProviderTargetRef == "" {
			t.Fatalf("%s Provider-specific target reference was lost", name)
		}
		if document.Observation.MappingProvenance == nil || document.Observation.MappingProvenance.MappingRef.ID == "" {
			t.Fatalf("%s mapping provenance was lost", name)
		}
		if document.Observation.MappingProvenance.SourceStateRef == "" {
			t.Fatalf("%s source state reference was lost", name)
		}
	}
}

func TestSyntheticProvidersPreserveMissingValuesAsUnknown(t *testing.T) {
	tests := []struct {
		name    string
		adapter Adapter
		fixture string
		source  string
	}{
		{"provider-a", ProviderAAdapter{}, "provider-a-missing.json", "synthetic-a://snapshot/missing"},
		{"provider-b", ProviderBAdapter{}, "provider-b-missing.json", "synthetic-b://snapshot/missing"},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			document, err := tc.adapter.Observe(testContext(tc.name+"-missing", tc.source), readProviderFixture(t, tc.fixture))
			if err != nil {
				t.Fatal(err)
			}
			assertValidated(t, document)
			for _, key := range []string{"availability", "latency"} {
				condition := conditionByKey(t, document, key)
				if condition.State != "unknown" {
					t.Fatalf("%s %s = %q, want unknown", tc.name, key, condition.State)
				}
				if len(condition.Value) != 0 {
					t.Fatalf("%s %s invented a negative/default value: %s", tc.name, key, condition.Value)
				}
			}
		})
	}
}

func TestAdapterOutputDoesNotEscalateToDecisionAuthorityOrExecution(t *testing.T) {
	document, err := (ProviderAAdapter{}).Observe(testContext("no-escalation", "synthetic-a://snapshot/no-escalation"), readProviderFixture(t, "provider-a-green.json"))
	if err != nil {
		t.Fatal(err)
	}
	data, err := json.Marshal(document)
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	for _, forbidden := range []string{"\"recommendation\"", "\"decision\"", "\"authority\"", "\"execution\"", "\"suitability_score\""} {
		if strings.Contains(text, forbidden) {
			t.Fatalf("adapter output contains forbidden semantic escalation %s: %s", forbidden, text)
		}
	}
}

func TestProviderSpecificInputIsStrictAndDoesNotBecomeUniversalSchema(t *testing.T) {
	_, err := (ProviderAAdapter{}).Observe(testContext("strict-a", "synthetic-a://snapshot/strict"), []byte(`{"service_ref":"provider-a://service","ready":true}`))
	if err == nil || !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("Provider A accepted Provider B field unexpectedly: %v", err)
	}
}

func TestProviderSpecificFieldNamesDoNotLeakIntoObservationSchema(t *testing.T) {
	tests := []struct {
		name      string
		adapter   Adapter
		fixture   string
		source    string
		forbidden []string
	}{
		{
			name:      "provider-a",
			adapter:   ProviderAAdapter{},
			fixture:   "provider-a-green.json",
			source:    "synthetic-a://snapshot/no-schema-leak",
			forbidden: []string{"\"health\"", "\"delay_ms\"", "\"service_ref\""},
		},
		{
			name:      "provider-b",
			adapter:   ProviderBAdapter{},
			fixture:   "provider-b-ready.json",
			source:    "synthetic-b://snapshot/no-schema-leak",
			forbidden: []string{"\"ready\"", "\"response_seconds\"", "\"endpoint\""},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			document, err := tc.adapter.Observe(testContext(tc.name+"-no-schema-leak", tc.source), readProviderFixture(t, tc.fixture))
			if err != nil {
				t.Fatal(err)
			}
			data, err := json.Marshal(document)
			if err != nil {
				t.Fatal(err)
			}
			text := string(data)
			for _, field := range tc.forbidden {
				if strings.Contains(text, field) {
					t.Fatalf("Provider-specific input field leaked into Capability Observation schema: %s in %s", field, text)
				}
			}
		})
	}
}
