package journeyharness

import (
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func lr(kind, id string) semanticruntime.LogicalReference {
	return semanticruntime.LogicalReference{Kind: kind, ID: id}
}

func rr(ref semanticruntime.LogicalReference) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: ref.Kind, ID: ref.ID, Scope: ref.Scope}
}

func baseJourney() (*semanticruntime.Bundle, Manifest) {
	inquiry := lr("inquiry", "I-001")
	unresolved := lr("unknown", "U-001")
	method := lr("method", "M-001")
	methodApplication := lr("method_application", "MA-001")
	recommendation := lr("recommendation", "R-001")
	decision := lr("decision", "D-001")
	aiResponsibility := lr("responsibility", "AI-ANALYST")
	humanResponsibility := lr("responsibility", "HUMAN-OWNER")
	capability := lr("capability", "CAP-001")
	providerA := lr("provider", "PROVIDER-A")
	providerB := lr("provider", "PROVIDER-B")
	providerBefore := lr("capability_observation", "CO-BEFORE")
	providerAfter := lr("capability_observation", "CO-AFTER")
	receipt := lr("execution_receipt", "EXEC-001")
	result := lr("capability_observation", "CO-RESULT")
	reopen := lr("method_application", "MA-REOPEN")
	unsupported := lr("external_artifact", "EXT-001")

	records := []semanticruntime.RuntimeRecord{
		{
			EnvelopeRecord: semanticruntime.InterchangeRecord{LogicalRef: &inquiry},
			Status:         semanticruntime.RecordNotVerified,
		},
		{
			EnvelopeRecord: semanticruntime.InterchangeRecord{LogicalRef: &unresolved},
			Status:         semanticruntime.RecordNotVerified,
		},
		{
			Status: semanticruntime.RecordValidated,
			CognitiveMethod: &semanticruntime.CognitiveMethodDocument{
				Contract:   semanticruntime.ContractCognitiveMethod,
				RecordType: "method_application",
				MethodApplication: &semanticruntime.MethodApplication{
					Ref:                methodApplication,
					MethodRef:          rr(method),
					InputRefs:          []semanticruntime.Reference{rr(inquiry), rr(unresolved)},
					OutputRefs:         []semanticruntime.Reference{rr(recommendation)},
					ResidualRefs:       []semanticruntime.Reference{rr(unresolved)},
					ResponsibilityRefs: []semanticruntime.Reference{rr(aiResponsibility)},
				},
			},
		},
		{
			Status: semanticruntime.RecordValidated,
			Decision: &semanticruntime.DecisionMemoryDocument{
				Contract:   semanticruntime.ContractDecisionMemory,
				RecordType: "recommendation",
				Recommendation: &semanticruntime.Recommendation{
					Ref:         recommendation,
					Statement:   "Proceed while preserving the unresolved item.",
					ContextRefs: []semanticruntime.Reference{rr(inquiry)},
					BasisRefs:   []semanticruntime.Reference{rr(methodApplication)},
				},
			},
		},
		{
			Status: semanticruntime.RecordValidated,
			Decision: &semanticruntime.DecisionMemoryDocument{
				Contract:   semanticruntime.ContractDecisionMemory,
				RecordType: "decision",
				Decision: &semanticruntime.Decision{
					Ref:                decision,
					Statement:          "Execute the selected capability and review the result.",
					ContextRefs:        []semanticruntime.Reference{rr(inquiry), rr(methodApplication)},
					BasisRefs:          []semanticruntime.Reference{rr(inquiry)},
					RecommendationRefs: []semanticruntime.Reference{rr(recommendation)},
					UnresolvedRefs:     []semanticruntime.Reference{rr(unresolved)},
					ResponsibilityRefs: []semanticruntime.Reference{rr(humanResponsibility)},
				},
			},
		},
		{
			Status: semanticruntime.RecordValidated,
			Capability: &semanticruntime.CapabilityObservationDocument{
				Contract: semanticruntime.ContractCapabilityObservation,
				Observation: semanticruntime.CapabilityObservation{
					Ref:        providerBefore,
					Target:     semanticruntime.CapabilityTarget{CapabilityRef: &capability, ProviderRef: &providerA},
					ObservedAt: "2026-09-01T09:55:00Z",
					Conditions: []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
				},
			},
		},
		{
			EnvelopeRecord: semanticruntime.InterchangeRecord{LogicalRef: &receipt},
			Status:         semanticruntime.RecordNotVerified,
		},
		{
			Status: semanticruntime.RecordValidated,
			Capability: &semanticruntime.CapabilityObservationDocument{
				Contract: semanticruntime.ContractCapabilityObservation,
				Observation: semanticruntime.CapabilityObservation{
					Ref:        result,
					Target:     semanticruntime.CapabilityTarget{CapabilityRef: &capability, ProviderRef: &providerA},
					ObservedAt: "2026-09-01T10:05:00Z",
					Conditions: []semanticruntime.ObservedCondition{{
						Key:        "execution.status",
						State:      "succeeded",
						SourceRefs: []semanticruntime.Reference{rr(receipt)},
					}},
				},
			},
		},
		{
			Status: semanticruntime.RecordValidated,
			CognitiveMethod: &semanticruntime.CognitiveMethodDocument{
				Contract:   semanticruntime.ContractCognitiveMethod,
				RecordType: "method_application",
				MethodApplication: &semanticruntime.MethodApplication{
					Ref:       reopen,
					MethodRef: rr(method),
					InputRefs: []semanticruntime.Reference{rr(result), rr(unresolved)},
				},
			},
		},
		{
			Status: semanticruntime.RecordValidated,
			Capability: &semanticruntime.CapabilityObservationDocument{
				Contract: semanticruntime.ContractCapabilityObservation,
				Observation: semanticruntime.CapabilityObservation{
					Ref:        providerAfter,
					Target:     semanticruntime.CapabilityTarget{CapabilityRef: &capability, ProviderRef: &providerB},
					ObservedAt: "2026-09-01T11:00:00Z",
					Conditions: []semanticruntime.ObservedCondition{{Key: "availability", State: "available"}},
				},
			},
		},
		{
			EnvelopeRecord: semanticruntime.InterchangeRecord{LogicalRef: &unsupported},
			Status:         semanticruntime.RecordNotVerified,
		},
	}

	manifest := Manifest{
		InquiryRef:                    inquiry,
		MethodApplicationRef:          methodApplication,
		RecommendationRef:             recommendation,
		DecisionRef:                   decision,
		DecisionAt:                    "2026-09-01T10:00:00Z",
		ExecutionReceiptRef:           &receipt,
		ResultObservationRef:          &result,
		ReopenApplicationRef:          &reopen,
		UnsupportedRecordRef:          &unsupported,
		ProviderBeforeObservationRef:  &providerBefore,
		ProviderAfterObservationRef:   &providerAfter,
		RequireReopen:                 true,
		RequireUnresolvedCarry:        true,
		RequireDistinctResponsibility: true,
	}
	return &semanticruntime.Bundle{Records: records}, manifest
}

func TestValidateEndToEndJourney(t *testing.T) {
	bundle, manifest := baseJourney()
	if err := Validate(bundle, manifest); err != nil {
		t.Fatalf("Validate() error = %v", err)
	}
}

func TestValidateNoExecutionJourney(t *testing.T) {
	bundle, manifest := baseJourney()
	manifest.ExecutionReceiptRef = nil
	manifest.ResultObservationRef = nil
	manifest.ReopenApplicationRef = nil
	manifest.RequireReopen = false
	manifest.RequireUnresolvedCarry = false
	manifest.AllowNoExecution = true

	if err := Validate(bundle, manifest); err != nil {
		t.Fatalf("Validate() no-execution error = %v", err)
	}
}

func TestRejectsTemporalBackflow(t *testing.T) {
	bundle, manifest := baseJourney()
	for i := range bundle.Records {
		if bundle.Records[i].Capability != nil && bundle.Records[i].Capability.Observation.Ref == *manifest.ResultObservationRef {
			bundle.Records[i].Capability.Observation.ObservedAt = "2026-09-01T09:59:00Z"
		}
	}

	err := Validate(bundle, manifest)
	if err == nil || !strings.Contains(err.Error(), "acquired after") {
		t.Fatalf("Validate() error = %v, want temporal integrity failure", err)
	}
}

func TestRejectsPostDecisionObservationInHistoricalBasis(t *testing.T) {
	bundle, manifest := baseJourney()
	for i := range bundle.Records {
		if bundle.Records[i].Decision != nil && bundle.Records[i].Decision.Decision != nil {
			bundle.Records[i].Decision.Decision.BasisRefs = append(bundle.Records[i].Decision.Decision.BasisRefs, rr(*manifest.ResultObservationRef))
		}
	}

	err := Validate(bundle, manifest)
	if err == nil || !strings.Contains(err.Error(), "historical decision basis") {
		t.Fatalf("Validate() error = %v, want historical-basis failure", err)
	}
}

func TestRejectsProviderReplacementWithoutProviderChange(t *testing.T) {
	bundle, manifest := baseJourney()
	var beforeProvider semanticruntime.LogicalReference
	for i := range bundle.Records {
		if bundle.Records[i].Capability != nil && bundle.Records[i].Capability.Observation.Ref == *manifest.ProviderBeforeObservationRef {
			beforeProvider = *bundle.Records[i].Capability.Observation.Target.ProviderRef
		}
	}
	for i := range bundle.Records {
		if bundle.Records[i].Capability != nil && bundle.Records[i].Capability.Observation.Ref == *manifest.ProviderAfterObservationRef {
			bundle.Records[i].Capability.Observation.Target.ProviderRef = &beforeProvider
		}
	}

	err := Validate(bundle, manifest)
	if err == nil || !strings.Contains(err.Error(), "distinct providers") {
		t.Fatalf("Validate() error = %v, want provider replacement failure", err)
	}
}

func TestRejectsUnsupportedRecordClaimedValidated(t *testing.T) {
	bundle, manifest := baseJourney()
	for i := range bundle.Records {
		if bundle.Records[i].EnvelopeRecord.LogicalRef != nil && *bundle.Records[i].EnvelopeRecord.LogicalRef == *manifest.UnsupportedRecordRef {
			bundle.Records[i].Status = semanticruntime.RecordValidated
		}
	}

	err := Validate(bundle, manifest)
	if err == nil || !strings.Contains(err.Error(), "must remain not_verified") {
		t.Fatalf("Validate() error = %v, want unsupported-version failure", err)
	}
}

func TestRejectsRecommendationDecisionCollapse(t *testing.T) {
	bundle, manifest := baseJourney()
	manifest.DecisionRef = manifest.RecommendationRef

	err := Validate(bundle, manifest)
	if err == nil || !strings.Contains(err.Error(), "decision ref does not resolve") {
		t.Fatalf("Validate() error = %v, want recommendation/decision separation failure", err)
	}
}
