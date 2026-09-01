package semanticruntime

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
)

const (
	ContractSemanticInterchange     = "soza.semantic-interchange/v1alpha1"
	ContractSemanticReference       = "soza.semantic-reference/v1alpha1"
	ContractDecisionMemory          = "soza.decision-memory/v1alpha1"
	ContractCapabilityObservation   = "soza.capability-observation/v1alpha1"
	ContractIDSemanticReference     = "soza.semantic-reference"
	ContractIDDecisionMemory        = "soza.decision-memory"
	ContractIDCapabilityObservation = "soza.capability-observation"
	ContractVersionV1Alpha1         = "v1alpha1"
)

func decodeStrict(data []byte, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return err
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return errors.New("multiple JSON values are not allowed")
		}
		return err
	}
	return nil
}

func validLogical(ref LogicalReference) bool {
	return ref.Kind != "" && ref.ID != ""
}

func sameLogical(a, b LogicalReference) bool {
	return a.Kind == b.Kind && a.ID == b.ID && a.Scope == b.Scope
}

func sameProfile(a, b RepresentationProfile) bool {
	return a.ProfileID == b.ProfileID && a.Version == b.Version
}

func sameExact(a, b ExactBinding) bool {
	return sameLogical(a.LogicalRef, b.LogicalRef) &&
		a.ContentDigest == b.ContentDigest &&
		sameProfile(a.RepresentationProfile, b.RepresentationProfile)
}

func validateProfile(profile RepresentationProfile) error {
	if profile.ProfileID == "" || profile.Version == "" {
		return errors.New("representation_profile requires profile_id and version")
	}
	return nil
}

func validateExact(binding ExactBinding) error {
	if !validLogical(binding.LogicalRef) {
		return errors.New("exact binding requires a logical_ref with kind and id")
	}
	if binding.ContentDigest == "" {
		return errors.New("exact binding requires content_digest")
	}
	return validateProfile(binding.RepresentationProfile)
}

func validateReference(ref Reference) error {
	hasSimple := ref.Kind != "" || ref.ID != "" || ref.Scope != ""
	hasExact := ref.LogicalRef != nil || ref.ContentDigest != "" || ref.RepresentationProfile != nil
	if hasSimple && hasExact {
		return errors.New("reference must be logical or exact, not both")
	}
	if hasExact {
		binding, ok := ref.ExactBinding()
		if !ok {
			return errors.New("partial exact reference is not allowed")
		}
		return validateExact(binding)
	}
	if !validLogical(LogicalReference{Kind: ref.Kind, ID: ref.ID, Scope: ref.Scope}) {
		return errors.New("logical reference requires kind and id")
	}
	return nil
}

func validateLineage(lineage SemanticLineage) error {
	if lineage.Relation != "revises" && lineage.Relation != "supersedes" && lineage.Relation != "withdraws" {
		return fmt.Errorf("unsupported lineage relation %q", lineage.Relation)
	}
	if err := validateReference(lineage.From); err != nil {
		return fmt.Errorf("lineage from: %w", err)
	}
	if err := validateReference(lineage.To); err != nil {
		return fmt.Errorf("lineage to: %w", err)
	}
	fromLogical, fromOK := lineage.From.LogicalIdentity()
	toLogical, toOK := lineage.To.LogicalIdentity()
	if fromOK && toOK && sameLogical(fromLogical, toLogical) {
		if !lineage.From.IsExact() || !lineage.To.IsExact() {
			return errors.New("same-logical-id lineage requires exact endpoints")
		}
		fromExact, _ := lineage.From.ExactBinding()
		toExact, _ := lineage.To.ExactBinding()
		if sameExact(fromExact, toExact) {
			return errors.New("semantic lineage cannot relate the same exact content to itself")
		}
	}
	for i, ref := range lineage.BasisRefs {
		if err := validateReference(ref); err != nil {
			return fmt.Errorf("lineage basis_refs[%d]: %w", i, err)
		}
	}
	return nil
}

func validateVerificationOutcome(outcome VerificationOutcome) error {
	if err := validateExact(outcome.Binding); err != nil {
		return fmt.Errorf("verification outcome binding: %w", err)
	}
	switch outcome.Status {
	case VerificationVerified, VerificationFailed, VerificationNotVerified:
		return nil
	default:
		return fmt.Errorf("unsupported verification status %q", outcome.Status)
	}
}

func parseSemanticReference(data []byte) (*SemanticReferenceDocument, error) {
	var doc SemanticReferenceDocument
	if err := decodeStrict(data, &doc); err != nil {
		return nil, err
	}
	if doc.Contract != ContractSemanticReference {
		return nil, fmt.Errorf("unexpected semantic-reference contract %q", doc.Contract)
	}
	switch doc.RecordType {
	case "logical_reference":
		if doc.LogicalReference == nil || !validLogical(*doc.LogicalReference) {
			return nil, errors.New("logical_reference record requires kind and id")
		}
	case "exact_binding":
		if doc.ExactBinding == nil {
			return nil, errors.New("exact_binding record requires exact_binding")
		}
		if err := validateExact(*doc.ExactBinding); err != nil {
			return nil, err
		}
	case "semantic_lineage":
		if doc.SemanticLineage == nil {
			return nil, errors.New("semantic_lineage record requires semantic_lineage")
		}
		if err := validateLineage(*doc.SemanticLineage); err != nil {
			return nil, err
		}
	case "verification_outcome":
		if doc.VerificationOutcome == nil {
			return nil, errors.New("verification_outcome record requires verification_outcome")
		}
		if err := validateVerificationOutcome(*doc.VerificationOutcome); err != nil {
			return nil, err
		}
	default:
		return nil, fmt.Errorf("unsupported semantic-reference record_type %q", doc.RecordType)
	}
	return &doc, nil
}

func validateReferenceList(label string, refs []Reference) error {
	for i, ref := range refs {
		if err := validateReference(ref); err != nil {
			return fmt.Errorf("%s[%d]: %w", label, i, err)
		}
	}
	return nil
}

func parseDecisionMemory(data []byte) (*DecisionMemoryDocument, error) {
	var doc DecisionMemoryDocument
	if err := decodeStrict(data, &doc); err != nil {
		return nil, err
	}
	if doc.Contract != ContractDecisionMemory {
		return nil, fmt.Errorf("unexpected decision-memory contract %q", doc.Contract)
	}
	switch doc.RecordType {
	case "decision":
		if doc.Decision == nil || doc.Recommendation != nil {
			return nil, errors.New("decision record requires decision only")
		}
		decision := doc.Decision
		if !validLogical(decision.Ref) || decision.Statement == "" {
			return nil, errors.New("decision requires ref and statement")
		}
		for label, refs := range map[string][]Reference{
			"context_refs": decision.ContextRefs,
			"basis_refs": decision.BasisRefs,
			"recommendation_refs": decision.RecommendationRefs,
			"unresolved_refs": decision.UnresolvedRefs,
			"responsibility_refs": decision.ResponsibilityRefs,
		} {
			if err := validateReferenceList(label, refs); err != nil {
				return nil, err
			}
		}
		if decision.Lineage != nil {
			if err := validateLineage(*decision.Lineage); err != nil {
				return nil, fmt.Errorf("decision lineage: %w", err)
			}
		}
	case "recommendation":
		if doc.Recommendation == nil || doc.Decision != nil {
			return nil, errors.New("recommendation record requires recommendation only")
		}
		recommendation := doc.Recommendation
		if !validLogical(recommendation.Ref) || recommendation.Statement == "" {
			return nil, errors.New("recommendation requires ref and statement")
		}
		for label, refs := range map[string][]Reference{
			"context_refs": recommendation.ContextRefs,
			"basis_refs": recommendation.BasisRefs,
			"responsibility_refs": recommendation.ResponsibilityRefs,
		} {
			if err := validateReferenceList(label, refs); err != nil {
				return nil, err
			}
		}
	default:
		return nil, fmt.Errorf("unsupported decision-memory record_type %q", doc.RecordType)
	}
	return &doc, nil
}

func parseCapabilityObservation(data []byte) (*CapabilityObservationDocument, error) {
	var doc CapabilityObservationDocument
	if err := decodeStrict(data, &doc); err != nil {
		return nil, err
	}
	if doc.Contract != ContractCapabilityObservation {
		return nil, fmt.Errorf("unexpected capability-observation contract %q", doc.Contract)
	}
	observation := doc.Observation
	if !validLogical(observation.Ref) {
		return nil, errors.New("capability observation requires ref")
	}
	if observation.ObservedAt == "" {
		return nil, errors.New("capability observation requires observed_at")
	}
	if observation.Target.CapabilityRef == nil && observation.Target.ProviderRef == nil && observation.Target.ProviderTargetRef == "" {
		return nil, errors.New("capability observation requires a target")
	}
	if observation.Target.CapabilityRef != nil && !validLogical(*observation.Target.CapabilityRef) {
		return nil, errors.New("capability_ref requires kind and id")
	}
	if observation.Target.ProviderRef != nil && !validLogical(*observation.Target.ProviderRef) {
		return nil, errors.New("provider_ref requires kind and id")
	}
	for i, condition := range observation.Conditions {
		if condition.Key == "" || condition.State == "" {
			return nil, fmt.Errorf("conditions[%d] requires key and state", i)
		}
		if err := validateReferenceList(fmt.Sprintf("conditions[%d].source_refs", i), condition.SourceRefs); err != nil {
			return nil, err
		}
	}
	if err := validateReferenceList("provenance_refs", observation.ProvenanceRefs); err != nil {
		return nil, err
	}
	if observation.MappingProvenance != nil {
		if err := validateReference(observation.MappingProvenance.MappingRef); err != nil {
			return nil, fmt.Errorf("mapping_provenance.mapping_ref: %w", err)
		}
	}
	return &doc, nil
}

// LoadStandalone reads one current semantic Contract document.
func LoadStandalone(data []byte) (RuntimeRecord, error) {
	var header struct {
		Contract string `json:"contract"`
	}
	if err := json.Unmarshal(data, &header); err != nil {
		return RuntimeRecord{}, err
	}
	switch header.Contract {
	case ContractSemanticReference:
		doc, err := parseSemanticReference(data)
		return RuntimeRecord{Status: RecordValidated, Reference: doc}, err
	case ContractDecisionMemory:
		doc, err := parseDecisionMemory(data)
		return RuntimeRecord{Status: RecordValidated, Decision: doc}, err
	case ContractCapabilityObservation:
		doc, err := parseCapabilityObservation(data)
		return RuntimeRecord{Status: RecordValidated, Capability: doc}, err
	case ContractCognitiveMethod:
		doc, err := parseCognitiveMethod(data)
		return RuntimeRecord{Status: RecordValidated, CognitiveMethod: doc}, err
	case ContractSemanticInterchange:
		return RuntimeRecord{}, errors.New("semantic interchange must be loaded with LoadInterchange")
	default:
		return RuntimeRecord{Status: RecordNotVerified}, nil
	}
}

func expectedPayloadContract(identity ContractIdentity) string {
	if identity.ContractID == "" || identity.Version == "" {
		return ""
	}
	return identity.ContractID + "/" + identity.Version
}

func parseInterchangeRecord(record InterchangeRecord) (RuntimeRecord, error) {
	runtimeRecord := RuntimeRecord{EnvelopeRecord: record}
	if record.RecordID == "" || record.Contract.ContractID == "" || record.Contract.Version == "" || record.Kind == "" || len(record.Payload) == 0 {
		return runtimeRecord, errors.New("interchange record requires record_id, contract identity, kind, and payload")
	}
	if record.LogicalRef != nil && !validLogical(*record.LogicalRef) {
		return runtimeRecord, errors.New("interchange logical_ref requires kind and id")
	}
	if record.ExactBinding != nil {
		if err := validateExact(*record.ExactBinding); err != nil {
			return runtimeRecord, err
		}
		if record.LogicalRef != nil && !sameLogical(*record.LogicalRef, record.ExactBinding.LogicalRef) {
			return runtimeRecord, errors.New("interchange logical_ref and exact_binding.logical_ref differ")
		}
	}

	expectedContract := expectedPayloadContract(record.Contract)
	switch expectedContract {
	case ContractSemanticReference:
		doc, err := parseSemanticReference(record.Payload)
		if err != nil {
			return runtimeRecord, err
		}
		runtimeRecord.Status = RecordValidated
		runtimeRecord.Reference = doc
	case ContractDecisionMemory:
		doc, err := parseDecisionMemory(record.Payload)
		if err != nil {
			return runtimeRecord, err
		}
		runtimeRecord.Status = RecordValidated
		runtimeRecord.Decision = doc
	case ContractCapabilityObservation:
		doc, err := parseCapabilityObservation(record.Payload)
		if err != nil {
			return runtimeRecord, err
		}
		runtimeRecord.Status = RecordValidated
		runtimeRecord.Capability = doc
	case ContractCognitiveMethod:
		doc, err := parseCognitiveMethod(record.Payload)
		if err != nil {
			return runtimeRecord, err
		}
		runtimeRecord.Status = RecordValidated
		runtimeRecord.CognitiveMethod = doc
	default:
		// Unknown nested Contract is retained as opaque payload. The runtime does
		// not claim that it has validated semantics it does not understand.
		runtimeRecord.Status = RecordNotVerified
	}
	return runtimeRecord, nil
}

func validateBundleExactReferences(bundle *Bundle) error {
	exactByLogical := map[LogicalReference][]ExactBinding{}
	for _, record := range bundle.Records {
		if record.EnvelopeRecord.ExactBinding == nil {
			continue
		}
		binding := *record.EnvelopeRecord.ExactBinding
		exactByLogical[binding.LogicalRef] = append(exactByLogical[binding.LogicalRef], binding)
	}

	for _, record := range bundle.Records {
		if record.Decision == nil || record.Decision.Decision == nil {
			continue
		}
		for _, ref := range record.Decision.Decision.BasisRefs {
			binding, ok := ref.ExactBinding()
			if !ok {
				continue
			}
			candidates := exactByLogical[binding.LogicalRef]
			if len(candidates) == 0 {
				continue
			}
			matched := false
			for _, candidate := range candidates {
				if sameExact(binding, candidate) {
					matched = true
					break
				}
			}
			if !matched {
				return fmt.Errorf("decision basis exact binding does not match bundle record for %s/%s", binding.LogicalRef.Kind, binding.LogicalRef.ID)
			}
		}
	}
	return nil
}

// LoadInterchange reads the current v1alpha1 semantic interchange envelope,
// validates all known nested Contracts, preserves unknown nested Contracts as
// not_verified records, and enforces bundle-local exact-reference invariants.
func LoadInterchange(data []byte) (*Bundle, error) {
	var envelope SemanticInterchange
	if err := decodeStrict(data, &envelope); err != nil {
		return nil, err
	}
	if envelope.Contract != ContractSemanticInterchange {
		return nil, fmt.Errorf("unexpected interchange contract %q", envelope.Contract)
	}
	if envelope.BundleID == "" {
		return nil, errors.New("semantic interchange requires bundle_id")
	}

	bundle := &Bundle{Envelope: envelope, raw: append([]byte(nil), data...)}
	seenRecordIDs := map[string]struct{}{}
	for _, record := range envelope.Records {
		if _, exists := seenRecordIDs[record.RecordID]; exists {
			return nil, fmt.Errorf("duplicate interchange record_id %q", record.RecordID)
		}
		seenRecordIDs[record.RecordID] = struct{}{}
		runtimeRecord, err := parseInterchangeRecord(record)
		if err != nil {
			return nil, fmt.Errorf("record %q: %w", record.RecordID, err)
		}
		bundle.Records = append(bundle.Records, runtimeRecord)
	}
	if err := validateBundleExactReferences(bundle); err != nil {
		return nil, err
	}
	return bundle, nil
}
