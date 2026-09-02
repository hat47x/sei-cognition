package livemethodintegration

import (
	"testing"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

func TestApplyKJAtlasGroupingResultPreservesExactRealizationReference(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	input := referenceInput(store, sampleGroupingResult)
	input.RealizationRef = semanticruntime.LogicalReference{Kind: "method-realization", ID: "MR-KJ-ATLAS-EXACT"}

	logical := input.RealizationRef
	profile := semanticruntime.RepresentationProfile{ProfileID: "soza.raw-bytes+sha256", Version: "v1alpha1"}
	exact := semanticruntime.Reference{
		LogicalRef:            &logical,
		ContentDigest:         "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
		RepresentationProfile: &profile,
	}
	input.RealizationReference = &exact

	if err := ApplyKJAtlasGroupingResult(input); err != nil {
		t.Fatalf("ApplyKJAtlasGroupingResult() error = %v", err)
	}

	record, found, err := store.Find(input.ApplicationRef)
	if err != nil || !found || record.CognitiveMethod == nil || record.CognitiveMethod.MethodApplication == nil {
		t.Fatalf("method application not stored: found=%v err=%v record=%#v", found, err, record)
	}
	actual := record.CognitiveMethod.MethodApplication.RealizationRef
	if actual == nil {
		t.Fatal("method application lost exact realization_ref")
	}
	binding, ok := actual.ExactBinding()
	if !ok {
		t.Fatalf("realization_ref is not exact: %#v", actual)
	}
	if binding.LogicalRef != logical || binding.ContentDigest != exact.ContentDigest || binding.RepresentationProfile != profile {
		t.Fatalf("exact realization_ref changed: got=%#v want=%#v", binding, exact)
	}
}

func TestApplyKJAtlasGroupingResultRejectsMismatchedRealizationIdentitiesWithoutMutation(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}

	input := referenceInput(store, sampleGroupingResult)
	input.RealizationRef = semanticruntime.LogicalReference{Kind: "method-realization", ID: "MR-KJ-ATLAS-A"}
	logical := semanticruntime.LogicalReference{Kind: "method-realization", ID: "MR-KJ-ATLAS-B"}
	profile := semanticruntime.RepresentationProfile{ProfileID: "soza.raw-bytes+sha256", Version: "v1alpha1"}
	input.RealizationReference = &semanticruntime.Reference{
		LogicalRef:            &logical,
		ContentDigest:         "sha256:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
		RepresentationProfile: &profile,
	}

	if err := ApplyKJAtlasGroupingResult(input); err == nil {
		t.Fatal("ApplyKJAtlasGroupingResult() accepted mismatched logical and exact realization identities")
	}
	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	if before != after {
		t.Fatalf("mismatched realization identity mutated canonical state: before=%s after=%s", before, after)
	}
}
