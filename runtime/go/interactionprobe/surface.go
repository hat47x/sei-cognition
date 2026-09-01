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
	RealizationRef     *semanticruntime.LogicalReference
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
	var realizationRef *semanticruntime.Reference
	if input.RealizationRef != nil {
		value := ref(*input.RealizationRef)
		realizationRef = &value
	}
	doc := &semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_application",
		MethodApplication: &semanticruntime.MethodApplication{
			Ref:                input.Ref,
			MethodRef:          ref(input.MethodRef),
			RealizationRef:     realizationRef,
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
	Inquiry         LightItem
	Observations    []LightItem
	Unknowns        []LightItem
	Conflicts       []LightItem
	Recommendations []LightItem
	Decisions       []LightItem
}

type AuditRecord struct {
	Ref                semanticruntime.LogicalReference
	Kind               string
	Status             semanticruntime.RecordStatus
	BasisRefs          []semanticruntime.LogicalReference
	RecommendationRefs []semanticruntime.LogicalReference
	UnresolvedRefs     []semanticruntime.LogicalReference
	ResponsibilityRefs []semanticruntime.LogicalReference
}

type AuditView struct {
	CanonicalDigest string
	Records         []AuditRecord
}

type MachineRecord struct {
	Ref    semanticruntime.LogicalReference `json:"ref"`
	Kind   string                           `json:"kind"`
	Status semanticruntime.RecordStatus     `json:"status"`
}

type MachineView struct {
	Records []MachineRecord `json:"records"`
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
		ref, ok := recordLogicalRef(record)
		if !ok {
			continue
		}
		switch {
		case record.EnvelopeRecord.Kind == "inquiry":
			view.Inquiry = LightItem{Ref: ref, Text: opaqueText(record.EnvelopeRecord.Payload)}
		case record.EnvelopeRecord.Kind == "unknown":
			view.Unknowns = append(view.Unknowns, LightItem{Ref: ref, Text: opaqueText(record.EnvelopeRecord.Payload)})
		case record.EnvelopeRecord.Kind == "conflict":
			view.Conflicts = append(view.Conflicts, LightItem{Ref: ref, Text: opaqueText(record.EnvelopeRecord.Payload)})
		case record.Capability != nil:
			view.Observations = append(view.Observations, LightItem{Ref: ref, Text: capabilitySummary(record.Capability)})
		case record.Decision != nil && record.Decision.Recommendation != nil:
			view.Recommendations = append(view.Recommendations, LightItem{Ref: ref, Text: record.Decision.Recommendation.Statement})
		case record.Decision != nil && record.Decision.Decision != nil:
			view.Decisions = append(view.Decisions, LightItem{Ref: ref, Text: record.Decision.Decision.Statement})
		}
	}
	return view, nil
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
		ref, ok := recordLogicalRef(record)
		if !ok {
			continue
		}
		item := AuditRecord{Ref: ref, Kind: recordKind(record), Status: record.Status}
		if record.Decision != nil && record.Decision.Decision != nil {
			item.BasisRefs = logicalRefs(record.Decision.Decision.BasisRefs)
			item.RecommendationRefs = logicalRefs(record.Decision.Decision.RecommendationRefs)
			item.UnresolvedRefs = logicalRefs(record.Decision.Decision.UnresolvedRefs)
			item.ResponsibilityRefs = logicalRefs(record.Decision.Decision.ResponsibilityRefs)
		}
		view.Records = append(view.Records, item)
	}
	return view, nil
}

func (s *MachineSurface) StructuredView() (MachineView, error) {
	if s == nil || s.store == nil {
		return MachineView{}, errors.New("machine surface requires a canonical store")
	}
	records, err := s.store.Records()
	if err != nil {
		return MachineView{}, err
	}
	view := MachineView{Records: make([]MachineRecord, 0, len(records))}
	for _, record := range records {
		ref, ok := recordLogicalRef(record)
		if !ok {
			continue
		}
		view.Records = append(view.Records, MachineRecord{Ref: ref, Kind: recordKind(record), Status: record.Status})
	}
	return view, nil
}

func (s *MachineSurface) ReadDecision(ref semanticruntime.LogicalReference) (semanticruntime.Decision, error) {
	record, ok, err := s.store.Find(ref)
	if err != nil {
		return semanticruntime.Decision{}, err
	}
	if !ok || record.Decision == nil || record.Decision.Decision == nil {
		return semanticruntime.Decision{}, fmt.Errorf("decision not found: %s/%s", ref.Kind, ref.ID)
	}
	return *record.Decision.Decision, nil
}

func opaqueText(payload json.RawMessage) string {
	var value opaqueTextPayload
	if err := json.Unmarshal(payload, &value); err != nil {
		return ""
	}
	return value.Text
}

func capabilitySummary(doc *semanticruntime.CapabilityObservationDocument) string {
	if doc == nil {
		return ""
	}
	parts := make([]string, 0, len(doc.Observation.Conditions))
	for _, condition := range doc.Observation.Conditions {
		parts = append(parts, condition.Key+"="+condition.State)
	}
	return strings.Join(parts, ", ")
}

func recordKind(record semanticruntime.RuntimeRecord) string {
	if record.EnvelopeRecord.Kind != "" {
		return record.EnvelopeRecord.Kind
	}
	if record.Decision != nil {
		return record.Decision.RecordType
	}
	if record.Capability != nil {
		return "capability_observation"
	}
	if record.CognitiveMethod != nil {
		return record.CognitiveMethod.RecordType
	}
	if record.Reference != nil {
		return record.Reference.RecordType
	}
	return "unknown"
}
