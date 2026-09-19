package capacityprofile

import "testing"

func testEnvelope(t *testing.T) *WorkloadPolicyEnvelope {
	t.Helper()
	envelope, err := NewWorkloadPolicyEnvelope(
		"b6g-eval-v1",
		"evidence://b6g/workload-policy-envelope",
		[]WorkloadPolicyBinding{
			{WorkloadClass: "general", Policy: ResidualPolicyCap128},
			{WorkloadClass: "structure-preserving", Policy: ResidualPolicyBaseline},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return envelope
}

func TestWorkloadPolicyEnvelopeResolvesExactCallerOwnedClass(t *testing.T) {
	envelope := testEnvelope(t)

	got, err := envelope.Resolve("general")
	if err != nil {
		t.Fatal(err)
	}
	if got != ResidualPolicyCap128 {
		t.Fatalf("general policy=%q want %q", got, ResidualPolicyCap128)
	}

	got, err = envelope.Resolve("structure-preserving")
	if err != nil {
		t.Fatal(err)
	}
	if got != ResidualPolicyBaseline {
		t.Fatalf("structure-preserving policy=%q want %q", got, ResidualPolicyBaseline)
	}
	if envelope.ID() != "b6g-eval-v1" ||
		envelope.ProvenanceRef() != "evidence://b6g/workload-policy-envelope" {
		t.Fatalf("unexpected envelope metadata: id=%q provenance=%q",
			envelope.ID(), envelope.ProvenanceRef())
	}
}

func TestWorkloadPolicyEnvelopeUnknownClassFailsClosed(t *testing.T) {
	envelope := testEnvelope(t)
	if _, err := envelope.Resolve("unknown"); err == nil {
		t.Fatal("unknown workload class must fail closed")
	}
}

func TestWorkloadPolicyEnvelopeRejectsNonCanonicalClass(t *testing.T) {
	envelope := testEnvelope(t)
	for _, workloadClass := range []string{" general", "general ", " "} {
		if _, err := envelope.Resolve(workloadClass); err == nil {
			t.Fatalf("noncanonical workload class %q must fail", workloadClass)
		}
	}
}

func TestWorkloadPolicyEnvelopeRejectsDuplicateClass(t *testing.T) {
	_, err := NewWorkloadPolicyEnvelope(
		"duplicate",
		"evidence://b6g/duplicate",
		[]WorkloadPolicyBinding{
			{WorkloadClass: "general", Policy: ResidualPolicyCap128},
			{WorkloadClass: "general", Policy: ResidualPolicyBaseline},
		},
	)
	if err == nil {
		t.Fatal("duplicate workload class must fail")
	}
}

func TestWorkloadPolicyEnvelopeRejectsUnsupportedPolicy(t *testing.T) {
	_, err := NewWorkloadPolicyEnvelope(
		"unsupported",
		"evidence://b6g/unsupported",
		[]WorkloadPolicyBinding{
			{WorkloadClass: "general", Policy: ResidualPolicyID("cap96")},
		},
	)
	if err == nil {
		t.Fatal("unsupported residual policy must fail")
	}
}

func TestWorkloadPolicyEnvelopeRejectsMissingMetadata(t *testing.T) {
	cases := []struct {
		id         string
		provenance string
	}{
		{"", "evidence://b6g/missing-id"},
		{" id", "evidence://b6g/noncanonical-id"},
		{"valid", ""},
		{"valid", " provenance"},
	}
	for _, tc := range cases {
		if _, err := NewWorkloadPolicyEnvelope(
			tc.id,
			tc.provenance,
			[]WorkloadPolicyBinding{{WorkloadClass: "general", Policy: ResidualPolicyCap128}},
		); err == nil {
			t.Fatalf("metadata id=%q provenance=%q must fail", tc.id, tc.provenance)
		}
	}
}
