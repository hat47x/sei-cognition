package interactionprobe

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

type HumanSurface struct {
	store *CanonicalStore
	local map[string]string
}

type MachineSurface struct {
	store *CanonicalStore
	local map[string]string
}

func NewHumanSurface(store *CanonicalStore) *HumanSurface {
	return &HumanSurface{store: store, local: map[string]string{}}
}

func NewMachineSurface(store *CanonicalStore) *MachineSurface {
	return &MachineSurface{store: store, local: map[string]string{}}
}

// Surface-local stateは操作上の便宜のためだけに使い、canonical stateへ昇格させません。
func (s *HumanSurface) SetLocalState(key, value string) {
	s.local[key] = value
}

func (s *HumanSurface) ResetLocalState() {
	s.local = map[string]string{}
}

func (s *MachineSurface) SetLocalState(key, value string) {
	s.local[key] = value
}

func (s *MachineSurface) ResetLocalState() {
	s.local = map[string]string{}
}

type opaqueTextPayload struct {
	Text string `json:"text"`
}

func (s *HumanSurface) StartInquiry(id, text string) (semanticruntime.LogicalReference, error) {
	if s == nil || s.store == nil {
		return semanticruntime.LogicalReference{}, errors.New("human surface requires a canonical store")
	}
	if strings.TrimSpace(id) == "" || strings.TrimSpace(text) == "" {
		return semanticruntime.LogicalReference{}, errors.New("inquiry requires id and text")
	}
	records, err := s.store.Records()
	if err != nil {
		return semanticruntime.LogicalReference{}, err
	}
	for _, record := range records {
		ref, ok := recordLogicalRef(record)
		if ok && ref.Kind == "inquiry" {
			return semanticruntime.LogicalReference{}, errors.New("reference probe supports one inquiry per canonical store")
		}
	}

	inquiry := semanticruntime.LogicalReference{Kind: "inquiry", ID: id}
	payload, _ := json.Marshal(opaqueTextPayload{Text: text})
	if err := s.store.Add(semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{Kind: "inquiry", LogicalRef: &inquiry, Payload: payload},
		Status:         semanticruntime.RecordNotVerified,
	}); err != nil {
		return semanticruntime.LogicalReference{}, err
	}
	s.local["opened"] = id
	return inquiry, nil
}

func (s *HumanSurface) RecordUnknown(id, text string) (semanticruntime.LogicalReference, error) {
	return s.recordOpaque("unknown", id, text)
}

func (s *HumanSurface) RecordConflict(id, text string) (semanticruntime.LogicalReference, error) {
	return s.recordOpaque("conflict", id, text)
}

func (s *HumanSurface) recordOpaque(kind, id, text string) (semanticruntime.LogicalReference, error) {
	if s == nil || s.store == nil {
		return semanticruntime.LogicalReference{}, errors.New("human surface requires a canonical store")
	}
	if strings.TrimSpace(id) == "" || strings.TrimSpace(text) == "" {
		return semanticruntime.LogicalReference{}, fmt.Errorf("%s requires id and text", kind)
	}
	logical := semanticruntime.LogicalReference{Kind: kind, ID: id}
	payload, _ := json.Marshal(opaqueTextPayload{Text: text})
	if err := s.store.Add(semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{Kind: kind, LogicalRef: &logical, Payload: payload},
		Status:         semanticruntime.RecordNotVerified,
	}); err != nil {
		return semanticruntime.LogicalReference{}, err
	}
	return logical, nil
}

type DecisionInput struct {
	Ref                semanticruntime.LogicalReference
	Statement          string
	ContextRefs        []semanticruntime.LogicalReference
	BasisRefs          []semanticruntime.LogicalReference
	RecommendationRefs []semanticruntime.LogicalReference
	UnresolvedRefs     []semanticruntime.LogicalReference
	ResponsibilityRefs []semanticruntime.LogicalReference
	Rationale          string
}

func (s *HumanSurface) RecordDecision(input DecisionInput) error {
	if s == nil || s.store == nil {
		return errors.New("human surface requires a canonical store")
	}
	doc := &semanticruntime.DecisionMemoryDocument{
		Contract:   semanticruntime.ContractDecisionMemory,
		RecordType: "decision",
		Decision: &semanticruntime.Decision{
			Ref:                input.Ref,
			Statement:          input.Statement,
			ContextRefs:        refs(input.ContextRefs),
			BasisRefs:          refs(input.BasisRefs),
			RecommendationRefs: refs(input.RecommendationRefs),
			UnresolvedRefs:     refs(input.UnresolvedRefs),
			ResponsibilityRefs: refs(input.ResponsibilityRefs),
			Rationale:          input.Rationale,
		},
	}
	return s.store.Add(semanticruntime.RuntimeRecord{Decision: doc})
}

type RecommendationInput struct {
	Ref                semanticruntime.LogicalReference
	Statement          string
	ContextRefs        []semanticruntime.LogicalReference
	BasisRefs          []semanticruntime.LogicalReference
	ResponsibilityRefs []semanticruntime.LogicalReference
	Rationale          string
}

func (s *MachineSurface) RecordRecommendation(input RecommendationInput) error {
	if s == nil || s.store == nil {
		return errors.New("machine surface requires a canonical store")
	}
	doc := &semanticruntime.DecisionMemoryDocument{
		Contract:   semanticruntime.ContractDecisionMemory,
		RecordType: "recommendation",
		Recommendation: &semanticruntime.Recommendation{
			Ref:                input.Ref,
			Statement:          input.Statement,
			ContextRefs:        refs(input.ContextRefs),
			BasisRefs:          refs(input.BasisRefs),
			ResponsibilityRefs: refs(input.ResponsibilityRefs),
			Rationale:          input.Rationale,
		},
	}
	return s.store.Add(semanticruntime.RuntimeRecord{Decision: doc})
}

type MethodApplicationInput struct {
	Ref                semanticruntime.LogicalReference
	MethodRef          semanticruntime.LogicalReference
	ContextRefs        []semanticruntime.LogicalReference
	InputRefs          []semanticruntime.LogicalReference
	OutputRefs         []semanticruntime.LogicalReference
	ResidualRefs       []semanticruntime.LogicalReference
	ProvenanceRefs     []semanticruntime.LogicalReference
	ResponsibilityRefs []semanticruntime.LogicalReference
	AppliedAt          string
	Summary            string
}

func (s *MachineSurface) RecordMethodApplication(input MethodApplicationInput) error {
	if s == nil || s.store == nil {
		return errors.New("machine surface requires a canonical store")
	}
	doc := &semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_application",
		MethodApplication: &semanticruntime.MethodApplication{
			Ref:                input.Ref,
			MethodRef:          ref(input.MethodRef),
			ContextRefs:        refs(input.ContextRefs),
			InputRefs:          refs(input.InputRefs),
			OutputRefs:         refs(input.OutputRefs),
			ResidualRefs:       refs(input.ResidualRefs),
			ProvenanceRefs:     refs(input.ProvenanceRefs),
			ResponsibilityRefs: refs(input.ResponsibilityRefs),
			AppliedAt:          input.AppliedAt,
			Summary:            input.Summary,
		},
	}
	return s.store.Add(semanticruntime.RuntimeRecord{CognitiveMethod: doc})
}

type CapabilityObservationInput struct {
	Ref            semanticruntime.LogicalReference
	CapabilityRef  *semanticruntime.LogicalReference
	ProviderRef    *semanticruntime.LogicalReference
	ObservedAt     string
	Conditions     []semanticruntime.ObservedCondition
	ProvenanceRefs []semanticruntime.LogicalReference
}

func (s *MachineSurface) RecordCapabilityObservation(input CapabilityObservationInput) error {
	if s == nil || s.store == nil {
		return errors.New("machine surface requires a canonical store")
	}
	doc := &semanticruntime.CapabilityObservationDocument{
		Contract: semanticruntime.ContractCapabilityObservation,
		Observation: semanticruntime.CapabilityObservation{
			Ref:            input.Ref,
			Target:         semanticruntime.CapabilityTarget{CapabilityRef: input.CapabilityRef, ProviderRef: input.ProviderRef},
			ObservedAt:     input.ObservedAt,
			Conditions:     input.Conditions,
			ProvenanceRefs: refs(input.ProvenanceRefs),
		},
	}
	return s.store.Add(semanticruntime.RuntimeRecord{Capability: doc})
}

type LightItem struct {
	Ref  semanticruntime.LogicalReference
	Text string
}

type LightView struct {
	Inquiry        LightItem
	Observations   []LightItem
	Unknowns       []LightItem
	Conflicts      []LightItem
	Recommendations []LightItem
	Decisions      []LightItem
}

func (s *HumanSurface) LightView() (LightView, error) {
	if s == nil || s.store == nil {
		return LightView{}, errors.New("human surface requires a canonical store")
	}
	records, err := s.store.Records()
	if err != nil {
		return LightView{}, err
	}
	view := LightView{}
	for _, record := range records {
		item, kind, ok := lightItem(record)
		if !ok {
			continue
		}
		switch kind {
		case "inquiry":
			view.Inquiry = item
		case "capability_observation":
			view.Observations = append(view.Observations, item)
		case "unknown":
			view.Unknowns = append(view.Unknowns, item)
		case "conflict":
			view.Conflicts = append(view.Conflicts, item)
		case "recommendation":
			view.Recommendations = append(view.Recommendations, item)
		case "decision":
			view.Decisions = append(view.Decisions, item)
		}
	}
	return view, nil
}

type AuditRecord struct {
	Ref                semanticruntime.LogicalReference
	Kind               string
	Status             semanticruntime.RecordValidationStatus
	Statement          string
	ContextRefs        []semanticruntime.LogicalReference
	BasisRefs          []semanticruntime.LogicalReference
	RecommendationRefs []semanticruntime.LogicalReference
	UnresolvedRefs     []semanticruntime.LogicalReference
	ResponsibilityRefs []semanticruntime.LogicalReference
	ProvenanceRefs     []semanticruntime.LogicalReference
	InputRefs          []semanticruntime.LogicalReference
	OutputRefs         []semanticruntime.LogicalReference
	ResidualRefs       []semanticruntime.LogicalReference
}

type AuditView struct {
	CanonicalDigest string
	Records         []AuditRecord
}

func (s *HumanSurface) AuditView() (AuditView, error) {
	if s == nil || s.store == nil {
		return AuditView{}, errors.New("human surface requires a canonical store")
	}
	digest, err := s.store.Digest()
	if err != nil {
		return AuditView{}, err
	}
	records, err := s.store.Records()
	if err != nil {
		return AuditView{}, err
	}
	view := AuditView{CanonicalDigest: digest}
	for _, record := range records {
		view.Records = append(view.Records, auditRecord(record))
	}
	return view, nil
}

type StructuredRecord struct {
	Ref                semanticruntime.LogicalReference `json:"ref"`
	Kind               string                           `json:"kind"`
	Status             semanticruntime.RecordValidationStatus `json:"status"`
	Statement          string                           `json:"statement,omitempty"`
	BasisRefs          []semanticruntime.LogicalReference `json:"basis_refs,omitempty"`
	UnresolvedRefs     []semanticruntime.LogicalReference `json:"unresolved_refs,omitempty"`
	ResponsibilityRefs []semanticruntime.LogicalReference `json:"responsibility_refs,omitempty"`
}

type StructuredView struct {
	CanonicalDigest string             `json:"canonical_digest"`
	Records         []StructuredRecord `json:"records"`
}

func (s *MachineSurface) StructuredView() (StructuredView, error) {
	if s == nil || s.store == nil {
		return StructuredView{}, errors.New("machine surface requires a canonical store")
	}
	digest, err := s.store.Digest()
	if err != nil {
		return StructuredView{}, err
	}
	records, err := s.store.Records()
	if err != nil {
		return StructuredView{}, err
	}
	view := StructuredView{CanonicalDigest: digest}
	for _, record := range records {
		audit := auditRecord(record)
		view.Records = append(view.Records, StructuredRecord{
			Ref:                audit.Ref,
			Kind:               audit.Kind,
			Status:             audit.Status,
			Statement:          audit.Statement,
			BasisRefs:          audit.BasisRefs,
			UnresolvedRefs:     audit.UnresolvedRefs,
			ResponsibilityRefs: audit.ResponsibilityRefs,
		})
	}
	return view, nil
}

func (s *MachineSurface) ReadDecision(target semanticruntime.LogicalReference) (semanticruntime.Decision, error) {
	if s == nil || s.store == nil {
		return semanticruntime.Decision{}, errors.New("machine surface requires a canonical store")
	}
	record, found, err := s.store.Find(target)
	if err != nil {
		return semanticruntime.Decision{}, err
	}
	if !found || record.Decision == nil || record.Decision.Decision == nil {
		return semanticruntime.Decision{}, fmt.Errorf("decision not found: %s/%s", target.Kind, target.ID)
	}
	return *record.Decision.Decision, nil
}

func (s *MachineSurface) ReadRecommendation(target semanticruntime.LogicalReference) (semanticruntime.Recommendation, error) {
	if s == nil || s.store == nil {
		return semanticruntime.Recommendation{}, errors.New("machine surface requires a canonical store")
	}
	record, found, err := s.store.Find(target)
	if err != nil {
		return semanticruntime.Recommendation{}, err
	}
	if !found || record.Decision == nil || record.Decision.Recommendation == nil {
		return semanticruntime.Recommendation{}, fmt.Errorf("recommendation not found: %s/%s", target.Kind, target.ID)
	}
	return *record.Decision.Recommendation, nil
}

func lightItem(record semanticruntime.RuntimeRecord) (LightItem, string, bool) {
	logical, ok := recordLogicalRef(record)
	if !ok {
		return LightItem{}, "", false
	}
	kind := logical.Kind
	item := LightItem{Ref: logical}

	if record.Decision != nil {
		if record.Decision.Recommendation != nil {
			kind = "recommendation"
			item.Text = record.Decision.Recommendation.Statement
		}
		if record.Decision.Decision != nil {
			kind = "decision"
			item.Text = record.Decision.Decision.Statement
		}
	}
	if record.Capability != nil {
		kind = "capability_observation"
		parts := make([]string, 0, len(record.Capability.Observation.Conditions))
		for _, condition := range record.Capability.Observation.Conditions {
			parts = append(parts, condition.Key+"="+condition.State)
		}
		item.Text = strings.Join(parts, ", ")
	}
	if record.CognitiveMethod != nil && record.CognitiveMethod.MethodApplication != nil {
		kind = "method_application"
		item.Text = record.CognitiveMethod.MethodApplication.Summary
	}
	if item.Text == "" && len(record.EnvelopeRecord.Payload) > 0 {
		var payload opaqueTextPayload
		if json.Unmarshal(record.EnvelopeRecord.Payload, &payload) == nil {
			item.Text = payload.Text
		}
	}
	return item, kind, true
}

func auditRecord(record semanticruntime.RuntimeRecord) AuditRecord {
	logical, _ := recordLogicalRef(record)
	out := AuditRecord{Ref: logical, Kind: logical.Kind, Status: record.Status}
	if item, kind, ok := lightItem(record); ok {
		out.Kind = kind
		out.Statement = item.Text
	}
	if record.Decision != nil {
		if record.Decision.Decision != nil {
			decision := record.Decision.Decision
			out.ContextRefs = logicalRefs(decision.ContextRefs)
			out.BasisRefs = logicalRefs(decision.BasisRefs)
			out.RecommendationRefs = logicalRefs(decision.RecommendationRefs)
			out.UnresolvedRefs = logicalRefs(decision.UnresolvedRefs)
			out.ResponsibilityRefs = logicalRefs(decision.ResponsibilityRefs)
		}
		if record.Decision.Recommendation != nil {
			recommendation := record.Decision.Recommendation
			out.ContextRefs = logicalRefs(recommendation.ContextRefs)
			out.BasisRefs = logicalRefs(recommendation.BasisRefs)
			out.ResponsibilityRefs = logicalRefs(recommendation.ResponsibilityRefs)
		}
	}
	if record.Capability != nil {
		out.ProvenanceRefs = logicalRefs(record.Capability.Observation.ProvenanceRefs)
	}
	if record.CognitiveMethod != nil && record.CognitiveMethod.MethodApplication != nil {
		application := record.CognitiveMethod.MethodApplication
		out.ContextRefs = logicalRefs(application.ContextRefs)
		out.InputRefs = logicalRefs(application.InputRefs)
		out.OutputRefs = logicalRefs(application.OutputRefs)
		out.ResidualRefs = logicalRefs(application.ResidualRefs)
		out.ProvenanceRefs = logicalRefs(application.ProvenanceRefs)
		out.ResponsibilityRefs = logicalRefs(application.ResponsibilityRefs)
	}
	return out
}
