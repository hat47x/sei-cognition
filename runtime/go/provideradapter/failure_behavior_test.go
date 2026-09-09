package provideradapter

import (
	"strings"
	"testing"
)

func TestFailureBehaviorMappingFailureDoesNotEmitPartialObservation(t *testing.T) {
	tests := []struct {
		name        string
		adapter     Adapter
		payload     string
		wantMessage string
	}{
		{
			name:        "provider-a-unsupported-health",
			adapter:     ProviderAAdapter{},
			payload:     `{"service_ref":"provider-a://service/failure","health":"blue","delay_ms":240}`,
			wantMessage: `unsupported Provider A health "blue"`,
		},
		{
			name:        "provider-b-negative-latency",
			adapter:     ProviderBAdapter{},
			payload:     `{"endpoint":"provider-b://endpoint/failure","ready":true,"response_seconds":-0.1}`,
			wantMessage: "Provider B response_seconds must not be negative",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			document, err := tc.adapter.Observe(
				testContext("failure-"+tc.name, "synthetic://failure/"+tc.name),
				[]byte(tc.payload),
			)
			if err == nil || !strings.Contains(err.Error(), tc.wantMessage) {
				t.Fatalf("Observe error = %v, want message containing %q", err, tc.wantMessage)
			}
			if document.Contract != "" || document.Observation.Ref.Kind != "" || document.Observation.Ref.ID != "" {
				t.Fatalf("mapping failure emitted a partial Capability Observation: %#v", document)
			}
		})
	}
}

func TestFailureBehaviorSemanticValidationRejectsInvalidMappedObservation(t *testing.T) {
	adapter := ProviderAAdapter{}
	document, err := adapter.Observe(
		testContext("failure-semantic-validation", "synthetic-a://snapshot/semantic-validation"),
		[]byte(`{"service_ref":"provider-a://service/valid","health":"green","delay_ms":240}`),
	)
	if err != nil {
		t.Fatalf("Observe valid Provider state: %v", err)
	}

	// The Adapter mapping succeeded. Corrupt only the mapped semantic document so
	// this failure is observed at the current semantic runtime validation boundary,
	// not at Provider-specific decoding or mapping.
	document.Observation.Ref.ID = ""
	if _, err := ValidateObservation(document); err == nil || !strings.Contains(err.Error(), "capability observation requires ref") {
		t.Fatalf("ValidateObservation error = %v, want capability observation ref rejection", err)
	}
}

func TestFailureBehaviorRetryKeepsInitialMappingFailureDistinct(t *testing.T) {
	adapter := ProviderAAdapter{}
	context := testContext("failure-retry", "synthetic-a://snapshot/retry")

	firstDocument, firstErr := adapter.Observe(
		context,
		[]byte(`{"service_ref":"provider-a://service/retry","health":"blue","delay_ms":240}`),
	)
	if firstErr == nil {
		t.Fatal("first attempt unexpectedly succeeded")
	}
	if firstDocument.Contract != "" {
		t.Fatalf("first failed attempt emitted a document: %#v", firstDocument)
	}
	firstObservation := firstErr.Error()

	secondDocument, secondErr := adapter.Observe(
		context,
		[]byte(`{"service_ref":"provider-a://service/retry","health":"green","delay_ms":240}`),
	)
	if secondErr != nil {
		t.Fatalf("second attempt failed: %v", secondErr)
	}
	if _, err := ValidateObservation(secondDocument); err != nil {
		t.Fatalf("second attempt semantic validation failed: %v", err)
	}

	if !strings.Contains(firstObservation, `unsupported Provider A health "blue"`) {
		t.Fatalf("initial failure observation was lost or replaced: %q", firstObservation)
	}
	if firstObservation == secondErrString(secondErr) {
		t.Fatalf("retry outcome overwrote the initial failure observation: %q", firstObservation)
	}
}

func secondErrString(err error) string {
	if err == nil {
		return "success"
	}
	return err.Error()
}
