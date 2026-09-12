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
	type attempt struct {
		outcome     string
		observation string
	}

	adapter := ProviderAAdapter{}
	context := testContext("failure-retry", "synthetic-a://snapshot/retry")
	attempts := make([]attempt, 0, 2)

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
	attempts = append(attempts, attempt{outcome: "failure", observation: firstErr.Error()})

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
	attempts = append(attempts, attempt{outcome: "success"})

	if len(attempts) != 2 || attempts[0].outcome != "failure" || attempts[1].outcome != "success" {
		t.Fatalf("retry attempts were not kept distinct: %#v", attempts)
	}
	if !strings.Contains(attempts[0].observation, `unsupported Provider A health "blue"`) {
		t.Fatalf("initial failure observation was lost or replaced: %#v", attempts)
	}
	if attempts[1].observation != "" {
		t.Fatalf("successful retry inherited the first failure observation: %#v", attempts)
	}
}
