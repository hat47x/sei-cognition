package journeyharness

import (
	"fmt"
	"time"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

// Manifest describes one evaluation-only Product Journey over existing SOZA
// Contracts. It is not a Universal Contract and does not become canonical
// product state. The durable meaning remains in the referenced records.
type Manifest struct {
	InquiryRef                   semanticruntime.LogicalReference
	MethodApplicationRef         semanticruntime.LogicalReference
	RecommendationRef            semanticruntime.LogicalReference
	DecisionRef                  semanticruntime.LogicalReference
	DecisionAt                   string
	ExecutionReceiptRef          *semanticruntime.LogicalReference
	ResultObservationRef         *semanticruntime.LogicalReference
	ReopenApplicationRef         *semanticruntime.LogicalReference
	UnsupportedRecordRef         *semanticruntime.LogicalReference
	ProviderBeforeObservationRef *semanticruntime.LogicalReference
	ProviderAfterObservationRef  *semanticruntime.LogicalReference
	AllowNoExecution             bool
	RequireReopen                bool
	RequireUnresolvedCarry       bool
	RequireDistinctResponsibility bool
}

// Validate checks that existing semantic records compose into a Product
// Journey without promoting the manifest itself into a semantic authority.
func Validate(bundle *semanticruntime.Bundle, manifest Manifest) error {
	if bundle == nil {
		return fmt.Errorf("bundle is required")
	}

	index, err := indexRecords(bundle.Records)
	if err != nil {
		return err
	}

	if _, err := requireRecord(index, manifest.InquiryRef, "inquiry"); err != nil {
		return err
	}

	methodRecord, err := requireRecord(index, manifest.MethodApplicationRef, "method application")
	if err != nil {
		return err
	}
	if methodRecord.CognitiveMethod == nil || methodRecord.CognitiveMethod.MethodApplication == nil {
		return fmt.Errorf("method application ref does not resolve to a method_application record")
	}
	application := methodRecord.CognitiveMethod.MethodApplication

	recommendationRecord, err := requireRecord(index, manifest.RecommendationRef, "recommendation")
	if err != nil {
		return err
	}
	if recommendationRecord.Decision == nil || recommendationRecord.Decision.Recommendation == nil {
		return fmt.Errorf("recommendation ref does not resolve to a recommendation record")
	}

	decisionRecord, err := requireRecord(index, manifest.DecisionRef, "decision")
	if err != nil {
		return err
	}
	if decisionRecord.Decision == nil || decisionRecord.Decision.Decision == nil {
		return fmt.Errorf("decision ref does not resolve to a decision record")
	}
	decision := decisionRecord.Decision.Decision

	if !containsReference(application.OutputRefs, manifest.RecommendationRef) {
		return fmt.Errorf("method application does not reference the recommendation as an output")
	}
	if !containsReference(decision.RecommendationRefs, manifest.RecommendationRef) {
		return fmt.Errorf("decision does not preserve the recommendation reference")
	}
	if !containsReference(decision.ContextRefs, manifest.MethodApplicationRef) && !containsReference(decision.BasisRefs, manifest.MethodApplicationRef) {
		return fmt.Errorf("decision does not reference the method application in context or basis")
	}
	if len(decision.ResponsibilityRefs) == 0 {
		return fmt.Errorf("decision requires an explicit responsibility reference in this journey")
	}

	if manifest.RequireDistinctResponsibility {
		if len(application.ResponsibilityRefs) == 0 {
			return fmt.Errorf("collaborative journey requires method application responsibility")
		}
		if !responsibilitiesDiffer(application.ResponsibilityRefs, decision.ResponsibilityRefs) {
			return fmt.Errorf("collaborative journey requires distinct method and decision responsibility references")
		}
	}

	decisionAt, err := time.Parse(time.RFC3339, manifest.DecisionAt)
	if err != nil {
		return fmt.Errorf("decision_at must be RFC3339: %w", err)
	}

	if manifest.UnsupportedRecordRef != nil {
		record, err := requireRecord(index, *manifest.UnsupportedRecordRef, "unsupported record")
		if err != nil {
			return err
		}
		if record.Status != semanticruntime.RecordNotVerified {
			return fmt.Errorf("unsupported record must remain not_verified")
		}
	}

	if manifest.ProviderBeforeObservationRef != nil || manifest.ProviderAfterObservationRef != nil {
		if manifest.ProviderBeforeObservationRef == nil || manifest.ProviderAfterObservationRef == nil {
			return fmt.Errorf("provider replacement requires both before and after observations")
		}
		before, err := requireCapability(index, *manifest.ProviderBeforeObservationRef, "provider before observation")
		if err != nil {
			return err
		}
		after, err := requireCapability(index, *manifest.ProviderAfterObservationRef, "provider after observation")
		if err != nil {
			return err
		}
		if before.Target.CapabilityRef == nil || after.Target.CapabilityRef == nil || *before.Target.CapabilityRef != *after.Target.CapabilityRef {
			return fmt.Errorf("provider replacement observations must target the same capability")
		}
		if before.Target.ProviderRef == nil || after.Target.ProviderRef == nil || *before.Target.ProviderRef == *after.Target.ProviderRef {
			return fmt.Errorf("provider replacement observations must use distinct providers")
		}
	}

	if manifest.ExecutionReceiptRef == nil && manifest.ResultObservationRef == nil && manifest.ReopenApplicationRef == nil {
		if manifest.AllowNoExecution {
			return nil
		}
		return fmt.Errorf("execution journey requires receipt and result observation")
	}
	if manifest.ExecutionReceiptRef == nil || manifest.ResultObservationRef == nil {
		return fmt.Errorf("execution receipt and result observation must be supplied together")
	}

	if _, err := requireRecord(index, *manifest.ExecutionReceiptRef, "execution receipt"); err != nil {
		return err
	}
	result, err := requireCapability(index, *manifest.ResultObservationRef, "result observation")
	if err != nil {
		return err
	}

	observedAt, err := time.Parse(time.RFC3339, result.ObservedAt)
	if err != nil {
		return fmt.Errorf("result observation observed_at must be RFC3339: %w", err)
	}
	if !observedAt.After(decisionAt) {
		return fmt.Errorf("result observation must be acquired after the historical decision")
	}
	if containsReference(decision.BasisRefs, *manifest.ResultObservationRef) {
		return fmt.Errorf("post-decision observation must not appear in the historical decision basis")
	}
	if !observationReferences(result, *manifest.ExecutionReceiptRef) {
		return fmt.Errorf("result observation does not preserve provenance to the execution receipt")
	}

	if manifest.RequireReopen {
		if manifest.ReopenApplicationRef == nil {
			return fmt.Errorf("journey requires a reopen application")
		}
		reopenRecord, err := requireRecord(index, *manifest.ReopenApplicationRef, "reopen application")
		if err != nil {
			return err
		}
		if reopenRecord.CognitiveMethod == nil || reopenRecord.CognitiveMethod.MethodApplication == nil {
			return fmt.Errorf("reopen ref does not resolve to a method_application record")
		}
		reopen := reopenRecord.CognitiveMethod.MethodApplication
		if !containsReference(reopen.InputRefs, *manifest.ResultObservationRef) {
			return fmt.Errorf("reopen application must consume the new result observation")
		}
		if manifest.RequireUnresolvedCarry {
			if len(decision.UnresolvedRefs) == 0 {
				return fmt.Errorf("unresolved-carry journey requires unresolved decision references")
			}
			for _, unresolved := range decision.UnresolvedRefs {
				logical, ok := unresolved.LogicalIdentity()
				if ok && !containsReference(reopen.InputRefs, logical) {
					return fmt.Errorf("reopen application does not carry unresolved ref %s/%s", logical.Kind, logical.ID)
				}
			}
		}
	}

	return nil
}

func indexRecords(records []semanticruntime.RuntimeRecord) (map[semanticruntime.LogicalReference]*semanticruntime.RuntimeRecord, error) {
	index := make(map[semanticruntime.LogicalReference]*semanticruntime.RuntimeRecord)
	for i := range records {
		ref, ok := recordLogicalRef(&records[i])
		if !ok {
			continue
		}
		if _, exists := index[ref]; exists {
			return nil, fmt.Errorf("duplicate logical record in journey: %s/%s", ref.Kind, ref.ID)
		}
		index[ref] = &records[i]
	}
	return index, nil
}

func recordLogicalRef(record *semanticruntime.RuntimeRecord) (semanticruntime.LogicalReference, bool) {
	if record.EnvelopeRecord.LogicalRef != nil {
		return *record.EnvelopeRecord.LogicalRef, true
	}
	if record.Decision != nil {
		if record.Decision.Decision != nil {
			return record.Decision.Decision.Ref, true
		}
		if record.Decision.Recommendation != nil {
			return record.Decision.Recommendation.Ref, true
		}
	}
	if record.Capability != nil {
		return record.Capability.Observation.Ref, true
	}
	if record.CognitiveMethod != nil {
		if record.CognitiveMethod.MethodDefinition != nil {
			return record.CognitiveMethod.MethodDefinition.Ref, true
		}
		if record.CognitiveMethod.MethodRealization != nil {
			return record.CognitiveMethod.MethodRealization.Ref, true
		}
		if record.CognitiveMethod.MethodApplication != nil {
			return record.CognitiveMethod.MethodApplication.Ref, true
		}
	}
	if record.Reference != nil && record.Reference.LogicalReference != nil {
		return *record.Reference.LogicalReference, true
	}
	return semanticruntime.LogicalReference{}, false
}

func requireRecord(index map[semanticruntime.LogicalReference]*semanticruntime.RuntimeRecord, ref semanticruntime.LogicalReference, label string) (*semanticruntime.RuntimeRecord, error) {
	if ref.Kind == "" || ref.ID == "" {
		return nil, fmt.Errorf("%s ref requires kind and id", label)
	}
	record, ok := index[ref]
	if !ok {
		return nil, fmt.Errorf("%s ref is not present in bundle: %s/%s", label, ref.Kind, ref.ID)
	}
	return record, nil
}

func requireCapability(index map[semanticruntime.LogicalReference]*semanticruntime.RuntimeRecord, ref semanticruntime.LogicalReference, label string) (*semanticruntime.CapabilityObservation, error) {
	record, err := requireRecord(index, ref, label)
	if err != nil {
		return nil, err
	}
	if record.Capability == nil {
		return nil, fmt.Errorf("%s does not resolve to a capability observation", label)
	}
	return &record.Capability.Observation, nil
}

func containsReference(refs []semanticruntime.Reference, target semanticruntime.LogicalReference) bool {
	for _, ref := range refs {
		logical, ok := ref.LogicalIdentity()
		if ok && logical == target {
			return true
		}
	}
	return false
}

func observationReferences(observation *semanticruntime.CapabilityObservation, target semanticruntime.LogicalReference) bool {
	if containsReference(observation.ProvenanceRefs, target) {
		return true
	}
	for _, condition := range observation.Conditions {
		if containsReference(condition.SourceRefs, target) {
			return true
		}
	}
	return false
}

func responsibilitiesDiffer(methodRefs, decisionRefs []semanticruntime.Reference) bool {
	for _, methodRef := range methodRefs {
		methodLogical, methodOK := methodRef.LogicalIdentity()
		if !methodOK {
			continue
		}
		for _, decisionRef := range decisionRefs {
			decisionLogical, decisionOK := decisionRef.LogicalIdentity()
			if decisionOK && methodLogical != decisionLogical {
				return true
			}
		}
	}
	return false
}
