package semanticruntime

import "encoding/json"

// RecordValidationStatus describes whether this runtime understood and validated
// a nested Contract record. It is not an Exact Binding verification outcome.
type RecordValidationStatus string

const (
	RecordValidated   RecordValidationStatus = "validated"
	RecordNotVerified RecordValidationStatus = "not_verified"
)

// VerificationStatus mirrors the semantic-reference Contract vocabulary for
// Exact Binding verification outcomes.
type VerificationStatus string

const (
	VerificationVerified    VerificationStatus = "verified"
	VerificationFailed      VerificationStatus = "failed"
	VerificationNotVerified VerificationStatus = "not_verified"
)

type ContractIdentity struct {
	ContractID string `json:"contract_id"`
	Version    string `json:"version"`
}

type LogicalReference struct {
	Kind  string `json:"kind"`
	ID    string `json:"id"`
	Scope string `json:"scope,omitempty"`
}

type RepresentationProfile struct {
	ProfileID string `json:"profile_id"`
	Version   string `json:"version"`
}

type ExactBinding struct {
	LogicalRef            LogicalReference      `json:"logical_ref"`
	ContentDigest         string                `json:"content_digest"`
	RepresentationProfile RepresentationProfile `json:"representation_profile"`
}

// Reference is the v1alpha1 wire union used by Decision basis and lineage
// endpoints. A reference is either logical (kind/id[/scope]) or exact
// (logical_ref/content_digest/representation_profile).
type Reference struct {
	Kind                  string                 `json:"kind,omitempty"`
	ID                    string                 `json:"id,omitempty"`
	Scope                 string                 `json:"scope,omitempty"`
	LogicalRef            *LogicalReference      `json:"logical_ref,omitempty"`
	ContentDigest         string                 `json:"content_digest,omitempty"`
	RepresentationProfile *RepresentationProfile `json:"representation_profile,omitempty"`
}

func (r Reference) IsExact() bool {
	return r.LogicalRef != nil && r.ContentDigest != "" && r.RepresentationProfile != nil
}

func (r Reference) LogicalIdentity() (LogicalReference, bool) {
	if r.LogicalRef != nil {
		return *r.LogicalRef, r.LogicalRef.Kind != "" && r.LogicalRef.ID != ""
	}
	if r.Kind == "" || r.ID == "" {
		return LogicalReference{}, false
	}
	return LogicalReference{Kind: r.Kind, ID: r.ID, Scope: r.Scope}, true
}

func (r Reference) ExactBinding() (ExactBinding, bool) {
	if !r.IsExact() {
		return ExactBinding{}, false
	}
	return ExactBinding{
		LogicalRef:            *r.LogicalRef,
		ContentDigest:         r.ContentDigest,
		RepresentationProfile: *r.RepresentationProfile,
	}, true
}

type SemanticLineage struct {
	Relation  string      `json:"relation"`
	From      Reference   `json:"from"`
	To        Reference   `json:"to"`
	BasisRefs []Reference `json:"basis_refs,omitempty"`
}

type VerificationOutcome struct {
	Binding     ExactBinding       `json:"binding"`
	Status      VerificationStatus `json:"status"`
	Reason      string             `json:"reason,omitempty"`
	VerifierRef string             `json:"verifier_ref,omitempty"`
}

type SemanticReferenceDocument struct {
	Contract            string               `json:"contract"`
	RecordType          string               `json:"record_type"`
	LogicalReference    *LogicalReference    `json:"logical_reference,omitempty"`
	ExactBinding        *ExactBinding        `json:"exact_binding,omitempty"`
	SemanticLineage     *SemanticLineage     `json:"semantic_lineage,omitempty"`
	VerificationOutcome *VerificationOutcome `json:"verification_outcome,omitempty"`
}

type Decision struct {
	Ref                LogicalReference `json:"ref"`
	Statement          string           `json:"statement"`
	ContextRefs        []Reference      `json:"context_refs,omitempty"`
	BasisRefs          []Reference      `json:"basis_refs,omitempty"`
	RecommendationRefs []Reference      `json:"recommendation_refs,omitempty"`
	UnresolvedRefs     []Reference      `json:"unresolved_refs,omitempty"`
	ResponsibilityRefs []Reference      `json:"responsibility_refs,omitempty"`
	Rationale          string           `json:"rationale,omitempty"`
	Lineage            *SemanticLineage `json:"lineage,omitempty"`
	Extensions         map[string]any   `json:"extensions,omitempty"`
}

type Recommendation struct {
	Ref                LogicalReference `json:"ref"`
	Statement          string           `json:"statement"`
	ContextRefs        []Reference      `json:"context_refs,omitempty"`
	BasisRefs          []Reference      `json:"basis_refs,omitempty"`
	Rationale          string           `json:"rationale,omitempty"`
	ResponsibilityRefs []Reference      `json:"responsibility_refs,omitempty"`
	Extensions         map[string]any   `json:"extensions,omitempty"`
}

type DecisionMemoryDocument struct {
	Contract       string          `json:"contract"`
	RecordType     string          `json:"record_type"`
	Decision       *Decision       `json:"decision,omitempty"`
	Recommendation *Recommendation `json:"recommendation,omitempty"`
}

type CapabilityTarget struct {
	CapabilityRef     *LogicalReference `json:"capability_ref,omitempty"`
	ProviderRef       *LogicalReference `json:"provider_ref,omitempty"`
	ProviderTargetRef string            `json:"provider_target_ref,omitempty"`
}

type ObservedCondition struct {
	Key        string          `json:"key"`
	State      string          `json:"state"`
	Value      json.RawMessage `json:"value,omitempty"`
	Unit       string          `json:"unit,omitempty"`
	SourceRefs []Reference     `json:"source_refs,omitempty"`
	Note       string          `json:"note,omitempty"`
}

type MappingProvenance struct {
	MappingRef     Reference `json:"mapping_ref"`
	SourceStateRef string    `json:"source_state_ref,omitempty"`
	Description    string    `json:"description,omitempty"`
}

type CapabilityObservation struct {
	Ref               LogicalReference    `json:"ref"`
	Target            CapabilityTarget    `json:"target"`
	ObservedAt        string              `json:"observed_at"`
	ValidUntil        string              `json:"valid_until,omitempty"`
	Conditions        []ObservedCondition `json:"conditions"`
	ProvenanceRefs    []Reference         `json:"provenance_refs,omitempty"`
	MappingProvenance *MappingProvenance  `json:"mapping_provenance,omitempty"`
	Extensions        map[string]any      `json:"extensions,omitempty"`
}

type CapabilityObservationDocument struct {
	Contract    string                `json:"contract"`
	Observation CapabilityObservation `json:"observation"`
}

type InterchangeRecord struct {
	RecordID           string             `json:"record_id"`
	Contract           ContractIdentity   `json:"contract"`
	Kind               string             `json:"kind"`
	LogicalRef         *LogicalReference  `json:"logical_ref,omitempty"`
	ExactBinding       *ExactBinding      `json:"exact_binding,omitempty"`
	Payload            json.RawMessage    `json:"payload"`
	ProvenanceRefs     []LogicalReference `json:"provenance_refs,omitempty"`
	ExtensionContracts []ContractIdentity `json:"extension_contracts,omitempty"`
}

type SemanticInterchange struct {
	Contract   string              `json:"contract"`
	BundleID   string              `json:"bundle_id"`
	CreatedAt  string              `json:"created_at,omitempty"`
	Records    []InterchangeRecord `json:"records"`
	Extensions map[string]any      `json:"extensions,omitempty"`
}

type RuntimeRecord struct {
	EnvelopeRecord  InterchangeRecord
	Status          RecordValidationStatus
	Decision        *DecisionMemoryDocument
	Capability      *CapabilityObservationDocument
	Reference       *SemanticReferenceDocument
	CognitiveMethod *CognitiveMethodDocument
}

type Bundle struct {
	Envelope SemanticInterchange
	Records  []RuntimeRecord
	raw      []byte
}

// ExportOriginal returns an independent copy of the original semantic
// interchange bytes. The first runtime slice does not normalize or rewrite a
// bundle merely because it was read successfully.
func (b *Bundle) ExportOriginal() []byte {
	return append([]byte(nil), b.raw...)
}
