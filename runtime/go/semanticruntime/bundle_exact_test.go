package semanticruntime

import (
	"strings"
	"testing"
)

func TestBundleLocalExactReferenceConsistencyAcrossKnownContracts(t *testing.T) {
	bundle, err := LoadInterchange(readFixture(t, "cognitive-method", "C9-interchange-exact-reference-consistency.json"))
	if err != nil {
		t.Fatalf("LoadInterchange: %v", err)
	}
	if len(bundle.Records) != 4 {
		t.Fatalf("records = %d, want 4", len(bundle.Records))
	}

	var application *RuntimeRecord
	for i := range bundle.Records {
		record := &bundle.Records[i]
		if record.CognitiveMethod != nil && record.CognitiveMethod.MethodApplication != nil {
			application = record
			break
		}
	}
	if application == nil {
		t.Fatal("method application record was not loaded")
	}

	refs := extractKnownExactReferences(*application)
	if len(refs) != 3 {
		t.Fatalf("exact references = %d, want 3", len(refs))
	}
	context := application.CognitiveMethod.MethodApplication.ContextRefs
	if len(context) != 1 || context[0].IsExact() {
		t.Fatalf("logical-only context reference was unexpectedly promoted: %#v", context)
	}
}

func TestBundleLocalExactReferenceMismatchIsRejectedAcrossKnownContracts(t *testing.T) {
	for _, fixture := range []string{
		"interchange-cognitive-method-mismatched-method-ref.json",
		"interchange-cognitive-method-mismatched-realization-profile.json",
		"interchange-capability-mismatched-source-ref.json",
	} {
		t.Run(fixture, func(t *testing.T) {
			_, err := LoadInterchange(readFixture(t, "negative", fixture))
			if err == nil {
				t.Fatal("expected bundle-local exact reference mismatch")
			}
			if !strings.Contains(err.Error(), "does not match bundle record") {
				t.Fatalf("unexpected error: %v", err)
			}
		})
	}
}

func TestUnknownContractExactLookingReferenceRemainsOpaque(t *testing.T) {
	bundle, err := LoadInterchange(readFixture(t, "boundary", "unknown-contract-exact-looking-reference.json"))
	if err != nil {
		t.Fatalf("LoadInterchange: %v", err)
	}
	if len(bundle.Records) != 2 {
		t.Fatalf("records = %d, want 2", len(bundle.Records))
	}
	unknown := bundle.Records[1]
	if unknown.Status != RecordNotVerified {
		t.Fatalf("status = %q, want %q", unknown.Status, RecordNotVerified)
	}
	if unknown.Decision != nil || unknown.Capability != nil || unknown.Reference != nil || unknown.CognitiveMethod != nil {
		t.Fatal("unknown Contract exact-looking payload was interpreted as known semantics")
	}
}
