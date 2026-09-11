package journeyharness

import (
	"bytes"
	"encoding/json"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func mustRawJSON(t *testing.T, value any) json.RawMessage {
	t.Helper()
	data, err := json.Marshal(value)
	if err != nil {
		t.Fatalf("json.Marshal() error = %v", err)
	}
	return data
}

func TestNormalJourneyThroughSemanticInterchange(t *testing.T) {
	inquiry := lr("inquiry", "I-NORMAL-001")
	method := lr("method", "M-NORMAL-001")
	methodApplication := lr("method_application", "MA-NORMAL-001")
	recommendation := lr("recommendation", "R-NORMAL-001")
	decision := lr("decision", "D-NORMAL-001")
	decisionOwner := lr("responsibility", "OWNER-NORMAL-001")
	capability := lr("capability", "CAP-NORMAL-001")
	provider := lr("provider", "PROVIDER-NORMAL-001")
	executionReceipt := lr("execution_receipt", "EXEC-NORMAL-001")
	resultObservation := lr("capability_observation", "CO-NORMAL-RESULT-001")
	reviewApplication := lr("method_application", "MA-NORMAL-REVIEW-001")

	methodPayload := semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_application",
		MethodApplication: &semanticruntime.MethodApplication{
			Ref:        methodApplication,
			MethodRef:  rr(method),
			InputRefs:  []semanticruntime.Reference{rr(inquiry)},
			OutputRefs: []semanticruntime.Reference{rr(recommendation)},
		},
	}
	recommendationPayload := semanticruntime.DecisionMemoryDocument{
		Contract:   semanticruntime.ContractDecisionMemory,
		RecordType: "recommendation",
		Recommendation: &semanticruntime.Recommendation{
			Ref:         recommendation,
			Statement:   "Use the available capability and inspect the resulting observation.",
			ContextRefs: []semanticruntime.Reference{rr(inquiry)},
			BasisRefs:   []semanticruntime.Reference{rr(methodApplication)},
		},
	}
	decisionPayload := semanticruntime.DecisionMemoryDocument{
		Contract:   semanticruntime.ContractDecisionMemory,
		RecordType: "decision",
		Decision: &semanticruntime.Decision{
			Ref:                decision,
			Statement:          "Execute the selected capability and review the result.",
			ContextRefs:        []semanticruntime.Reference{rr(inquiry), rr(methodApplication)},
			BasisRefs:          []semanticruntime.Reference{rr(inquiry)},
			RecommendationRefs: []semanticruntime.Reference{rr(recommendation)},
			ResponsibilityRefs: []semanticruntime.Reference{rr(decisionOwner)},
		},
	}
	resultPayload := semanticruntime.CapabilityObservationDocument{
		Contract: semanticruntime.ContractCapabilityObservation,
		Observation: semanticruntime.CapabilityObservation{
			Ref: resultObservation,
			Target: semanticruntime.CapabilityTarget{
				CapabilityRef: &capability,
				ProviderRef:   &provider,
			},
			ObservedAt: "2026-09-01T10:05:00Z",
			Conditions: []semanticruntime.ObservedCondition{{
				Key:        "execution.status",
				State:      "succeeded",
				SourceRefs: []semanticruntime.Reference{rr(executionReceipt)},
			}},
		},
	}
	reviewPayload := semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_application",
		MethodApplication: &semanticruntime.MethodApplication{
			Ref:       reviewApplication,
			MethodRef: rr(method),
			InputRefs: []semanticruntime.Reference{rr(resultObservation)},
		},
	}

	envelope := semanticruntime.SemanticInterchange{
		Contract:  semanticruntime.ContractSemanticInterchange,
		BundleID:  "journey-normal-001",
		CreatedAt: "2026-09-01T10:10:00Z",
		Records: []semanticruntime.InterchangeRecord{
			{
				RecordID:   "inquiry",
				Contract:   semanticruntime.ContractIdentity{ContractID: "example.inquiry", Version: "v1"},
				Kind:       "inquiry",
				LogicalRef: &inquiry,
				Payload:    json.RawMessage(`{"question":"Which capability should be used?"}`),
			},
			{
				RecordID:   "method-application",
				Contract:   semanticruntime.ContractIdentity{ContractID: semanticruntime.ContractIDCognitiveMethod, Version: semanticruntime.ContractVersionV1Alpha1},
				Kind:       "method_application",
				LogicalRef: &methodApplication,
				Payload:    mustRawJSON(t, methodPayload),
			},
			{
				RecordID:   "recommendation",
				Contract:   semanticruntime.ContractIdentity{ContractID: semanticruntime.ContractIDDecisionMemory, Version: semanticruntime.ContractVersionV1Alpha1},
				Kind:       "recommendation",
				LogicalRef: &recommendation,
				Payload:    mustRawJSON(t, recommendationPayload),
			},
			{
				RecordID:   "decision",
				Contract:   semanticruntime.ContractIdentity{ContractID: semanticruntime.ContractIDDecisionMemory, Version: semanticruntime.ContractVersionV1Alpha1},
				Kind:       "decision",
				LogicalRef: &decision,
				Payload:    mustRawJSON(t, decisionPayload),
			},
			{
				RecordID:   "execution-receipt",
				Contract:   semanticruntime.ContractIdentity{ContractID: "example.execution-receipt", Version: "v1"},
				Kind:       "execution_receipt",
				LogicalRef: &executionReceipt,
				Payload:    json.RawMessage(`{"provider_run_id":"run-123","status":"succeeded"}`),
			},
			{
				RecordID:   "result-observation",
				Contract:   semanticruntime.ContractIdentity{ContractID: semanticruntime.ContractIDCapabilityObservation, Version: semanticruntime.ContractVersionV1Alpha1},
				Kind:       "capability_observation",
				LogicalRef: &resultObservation,
				Payload:    mustRawJSON(t, resultPayload),
			},
			{
				RecordID:   "review-application",
				Contract:   semanticruntime.ContractIdentity{ContractID: semanticruntime.ContractIDCognitiveMethod, Version: semanticruntime.ContractVersionV1Alpha1},
				Kind:       "method_application",
				LogicalRef: &reviewApplication,
				Payload:    mustRawJSON(t, reviewPayload),
			},
		},
	}

	data, err := json.Marshal(envelope)
	if err != nil {
		t.Fatalf("json.Marshal(envelope) error = %v", err)
	}
	bundle, err := semanticruntime.LoadInterchange(data)
	if err != nil {
		t.Fatalf("LoadInterchange() error = %v", err)
	}
	if !bytes.Equal(bundle.ExportOriginal(), data) {
		t.Fatal("LoadInterchange() rewrote the original interchange bytes")
	}

	manifest := Manifest{
		InquiryRef:           inquiry,
		MethodApplicationRef: methodApplication,
		RecommendationRef:    recommendation,
		DecisionRef:          decision,
		DecisionAt:           "2026-09-01T10:00:00Z",
		ExecutionReceiptRef:  &executionReceipt,
		ResultObservationRef: &resultObservation,
		ReopenApplicationRef: &reviewApplication,
		UnsupportedRecordRef: &inquiry,
		RequireReopen:        true,
	}

	var beforeStatement string
	var beforeBasis []semanticruntime.Reference
	for _, record := range bundle.Records {
		if record.Decision != nil && record.Decision.Decision != nil && record.Decision.Decision.Ref == decision {
			beforeStatement = record.Decision.Decision.Statement
			beforeBasis = append([]semanticruntime.Reference(nil), record.Decision.Decision.BasisRefs...)
		}
	}

	if err := Validate(bundle, manifest); err != nil {
		t.Fatalf("Validate() error = %v", err)
	}

	for _, record := range bundle.Records {
		if record.Decision == nil || record.Decision.Decision == nil || record.Decision.Decision.Ref != decision {
			continue
		}
		if record.Decision.Decision.Statement != beforeStatement {
			t.Fatal("successful execution changed the historical decision statement")
		}
		if len(record.Decision.Decision.BasisRefs) != len(beforeBasis) {
			t.Fatal("successful execution changed the historical decision basis")
		}
		for i := range beforeBasis {
			beforeLogical, beforeOK := beforeBasis[i].LogicalIdentity()
			afterLogical, afterOK := record.Decision.Decision.BasisRefs[i].LogicalIdentity()
			if beforeOK != afterOK || beforeLogical != afterLogical {
				t.Fatal("successful execution rewrote the historical decision basis")
			}
		}
	}
}
