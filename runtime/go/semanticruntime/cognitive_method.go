package semanticruntime

import (
	"errors"
	"fmt"
)

const (
	ContractCognitiveMethod   = "soza.cognitive-method/v1alpha1"
	ContractIDCognitiveMethod = "soza.cognitive-method"
)

type MethodDefinition struct {
	Ref               LogicalReference `json:"ref"`
	Title             string           `json:"title"`
	Purpose           string           `json:"purpose"`
	ContextRefs       []Reference      `json:"context_refs,omitempty"`
	SpecificationRefs []Reference      `json:"specification_refs,omitempty"`
	Extensions        map[string]any   `json:"extensions,omitempty"`
}

type MethodRealization struct {
	Ref                LogicalReference `json:"ref"`
	MethodRef          Reference        `json:"method_ref"`
	Description        string           `json:"description"`
	ImplementationRefs []Reference      `json:"implementation_refs,omitempty"`
	ContextRefs        []Reference      `json:"context_refs,omitempty"`
	Extensions         map[string]any   `json:"extensions,omitempty"`
}

type MethodApplication struct {
	Ref                LogicalReference `json:"ref"`
	MethodRef          Reference        `json:"method_ref"`
	RealizationRef     *Reference       `json:"realization_ref,omitempty"`
	ContextRefs        []Reference      `json:"context_refs,omitempty"`
	InputRefs          []Reference      `json:"input_refs,omitempty"`
	OutputRefs         []Reference      `json:"output_refs,omitempty"`
	ResidualRefs       []Reference      `json:"residual_refs,omitempty"`
	ProvenanceRefs     []Reference      `json:"provenance_refs,omitempty"`
	ResponsibilityRefs []Reference      `json:"responsibility_refs,omitempty"`
	AppliedAt          string           `json:"applied_at,omitempty"`
	Summary            string           `json:"summary,omitempty"`
	Extensions         map[string]any   `json:"extensions,omitempty"`
}

type CognitiveMethodDocument struct {
	Contract          string              `json:"contract"`
	RecordType        string              `json:"record_type"`
	MethodDefinition  *MethodDefinition   `json:"method_definition,omitempty"`
	MethodRealization *MethodRealization  `json:"method_realization,omitempty"`
	MethodApplication *MethodApplication  `json:"method_application,omitempty"`
}

func parseCognitiveMethod(data []byte) (*CognitiveMethodDocument, error) {
	var doc CognitiveMethodDocument
	if err := decodeStrict(data, &doc); err != nil {
		return nil, err
	}
	if doc.Contract != ContractCognitiveMethod {
		return nil, fmt.Errorf("unexpected cognitive-method contract %q", doc.Contract)
	}

	switch doc.RecordType {
	case "method_definition":
		if doc.MethodDefinition == nil || doc.MethodRealization != nil || doc.MethodApplication != nil {
			return nil, errors.New("method_definition record requires method_definition only")
		}
		definition := doc.MethodDefinition
		if !validLogical(definition.Ref) || definition.Title == "" || definition.Purpose == "" {
			return nil, errors.New("method definition requires ref, title, and purpose")
		}
		for label, refs := range map[string][]Reference{
			"context_refs": definition.ContextRefs,
			"specification_refs": definition.SpecificationRefs,
		} {
			if err := validateReferenceList(label, refs); err != nil {
				return nil, err
			}
		}

	case "method_realization":
		if doc.MethodRealization == nil || doc.MethodDefinition != nil || doc.MethodApplication != nil {
			return nil, errors.New("method_realization record requires method_realization only")
		}
		realization := doc.MethodRealization
		if !validLogical(realization.Ref) || realization.Description == "" {
			return nil, errors.New("method realization requires ref and description")
		}
		if err := validateReference(realization.MethodRef); err != nil {
			return nil, fmt.Errorf("method_ref: %w", err)
		}
		for label, refs := range map[string][]Reference{
			"implementation_refs": realization.ImplementationRefs,
			"context_refs": realization.ContextRefs,
		} {
			if err := validateReferenceList(label, refs); err != nil {
				return nil, err
			}
		}

	case "method_application":
		if doc.MethodApplication == nil || doc.MethodDefinition != nil || doc.MethodRealization != nil {
			return nil, errors.New("method_application record requires method_application only")
		}
		application := doc.MethodApplication
		if !validLogical(application.Ref) {
			return nil, errors.New("method application requires ref")
		}
		if err := validateReference(application.MethodRef); err != nil {
			return nil, fmt.Errorf("method_ref: %w", err)
		}
		if application.RealizationRef != nil {
			if err := validateReference(*application.RealizationRef); err != nil {
				return nil, fmt.Errorf("realization_ref: %w", err)
			}
		}
		for label, refs := range map[string][]Reference{
			"context_refs": application.ContextRefs,
			"input_refs": application.InputRefs,
			"output_refs": application.OutputRefs,
			"residual_refs": application.ResidualRefs,
			"provenance_refs": application.ProvenanceRefs,
			"responsibility_refs": application.ResponsibilityRefs,
		} {
			if err := validateReferenceList(label, refs); err != nil {
				return nil, err
			}
		}

	default:
		return nil, fmt.Errorf("unsupported cognitive-method record_type %q", doc.RecordType)
	}

	return &doc, nil
}
