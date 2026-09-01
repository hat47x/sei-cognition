package semanticruntime

import (
	"strings"
	"testing"
)

func testExact(kind, id, digest, profileVersion string) ExactBinding {
	return ExactBinding{
		LogicalRef:    LogicalReference{Kind: kind, ID: id},
		ContentDigest: digest,
		RepresentationProfile: RepresentationProfile{
			ProfileID: "soza.jcs+sha256",
			Version:   profileVersion,
		},
	}
}

func testExactRef(binding ExactBinding) Reference {
	return Reference{
		LogicalRef:            &binding.LogicalRef,
		ContentDigest:         binding.ContentDigest,
		RepresentationProfile: &binding.RepresentationProfile,
	}
}

func exactRecord(binding ExactBinding) RuntimeRecord {
	return RuntimeRecord{EnvelopeRecord: InterchangeRecord{ExactBinding: &binding}}
}

func TestBundleExactConsistencyCognitiveMethodMatchesBundleRecord(t *testing.T) {
	method := testExact("cognitive_method", "method-1", "sha256:method-a", "v1alpha1")
	realization := testExact("method_realization", "realization-1", "sha256:realization-a", "v1alpha1")
	methodRef := testExactRef(method)
	realizationRef := testExactRef(realization)

	bundle := &Bundle{Records: []RuntimeRecord{
		exactRecord(method),
		exactRecord(realization),
		{
			Status: RecordValidated,
			CognitiveMethod: &CognitiveMethodDocument{
				MethodApplication: &MethodApplication{
					MethodRef:      methodRef,
					RealizationRef: &realizationRef,
				},
			},
		},
	}}

	if err := validateBundleExactReferences(bundle); err != nil {
		t.Fatalf("unexpected consistency error: %v", err)
	}
}

func TestBundleExactConsistencyCognitiveMethodRejectsDigestMismatch(t *testing.T) {
	bundleBinding := testExact("cognitive_method", "method-1", "sha256:method-a", "v1alpha1")
	refBinding := testExact("cognitive_method", "method-1", "sha256:method-b", "v1alpha1")

	bundle := &Bundle{Records: []RuntimeRecord{
		exactRecord(bundleBinding),
		{
			Status: RecordValidated,
			CognitiveMethod: &CognitiveMethodDocument{
				MethodApplication: &MethodApplication{MethodRef: testExactRef(refBinding)},
			},
		},
	}}

	err := validateBundleExactReferences(bundle)
	if err == nil {
		t.Fatal("expected mismatch error")
	}
	if !strings.Contains(err.Error(), "method_application.method_ref") {
		t.Fatalf("error did not identify semantic role: %v", err)
	}
}

func TestBundleExactConsistencyAcceptsOneOfMultipleRevisions(t *testing.T) {
	revisionA := testExact("artifact", "shared", "sha256:a", "v1alpha1")
	revisionB := testExact("artifact", "shared", "sha256:b", "v1alpha1")

	bundle := &Bundle{Records: []RuntimeRecord{
		exactRecord(revisionA),
		exactRecord(revisionB),
		{
			Status: RecordValidated,
			Decision: &DecisionMemoryDocument{
				Decision: &Decision{ContextRefs: []Reference{testExactRef(revisionB)}},
			},
		},
	}}

	if err := validateBundleExactReferences(bundle); err != nil {
		t.Fatalf("reference to one of multiple revisions should pass: %v", err)
	}
}

func TestBundleExactConsistencyAllowsExternalExactReference(t *testing.T) {
	external := testExact("artifact", "outside-bundle", "sha256:external", "v1alpha1")
	bundle := &Bundle{Records: []RuntimeRecord{{
		Status: RecordValidated,
		Decision: &DecisionMemoryDocument{
			Recommendation: &Recommendation{BasisRefs: []Reference{testExactRef(external)}},
		},
	}}}

	if err := validateBundleExactReferences(bundle); err != nil {
		t.Fatalf("bundle-absent external exact reference should not fail: %v", err)
	}
}

func TestBundleExactConsistencyDoesNotPromoteLogicalReference(t *testing.T) {
	binding := testExact("artifact", "logical-only", "sha256:a", "v1alpha1")
	logical := Reference{Kind: "artifact", ID: "logical-only"}
	bundle := &Bundle{Records: []RuntimeRecord{
		exactRecord(binding),
		{
			Status: RecordValidated,
			Decision: &DecisionMemoryDocument{
				Decision: &Decision{BasisRefs: []Reference{logical}},
			},
		},
	}}

	if err := validateBundleExactReferences(bundle); err != nil {
		t.Fatalf("logical-only reference must not be promoted to exact: %v", err)
	}
}

func TestBundleExactConsistencyIgnoresUnknownContractPayload(t *testing.T) {
	binding := testExact("artifact", "opaque", "sha256:a", "v1alpha1")
	bundle := &Bundle{Records: []RuntimeRecord{
		exactRecord(binding),
		{
			Status: RecordNotVerified,
			EnvelopeRecord: InterchangeRecord{Payload: []byte(`{"exact_binding":{"content_digest":"sha256:not-a"}}`)},
		},
	}}

	if refs := extractKnownExactReferences(bundle.Records[1]); len(refs) != 0 {
		t.Fatalf("unknown contract payload was introspected: %#v", refs)
	}
	if err := validateBundleExactReferences(bundle); err != nil {
		t.Fatalf("unknown opaque payload should not affect bundle consistency: %v", err)
	}
}

func TestBundleExactConsistencyCapabilityObservationRejectsProfileMismatch(t *testing.T) {
	bundleBinding := testExact("artifact", "source-1", "sha256:source", "v1alpha1")
	refBinding := testExact("artifact", "source-1", "sha256:source", "v1alpha2")
	bundle := &Bundle{Records: []RuntimeRecord{
		exactRecord(bundleBinding),
		{
			Status: RecordValidated,
			Capability: &CapabilityObservationDocument{
				Observation: CapabilityObservation{
					Conditions: []ObservedCondition{{SourceRefs: []Reference{testExactRef(refBinding)}}},
				},
			},
		},
	}}

	err := validateBundleExactReferences(bundle)
	if err == nil {
		t.Fatal("expected capability source profile mismatch")
	}
	if !strings.Contains(err.Error(), "capability_observation.conditions.source_refs") {
		t.Fatalf("error did not identify capability source role: %v", err)
	}
}
