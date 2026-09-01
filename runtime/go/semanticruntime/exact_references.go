package semanticruntime

// ExactReferenceRole binds a typed semantic Reference role to its Exact Binding.
// The role is diagnostic context only; the binding remains the semantic value
// checked against exact-bound records in the same Semantic Interchange bundle.
type ExactReferenceRole struct {
	Role    string
	Binding ExactBinding
}

func appendExactReference(result []ExactReferenceRole, role string, ref Reference) []ExactReferenceRole {
	binding, ok := ref.ExactBinding()
	if !ok {
		return result
	}
	return append(result, ExactReferenceRole{Role: role, Binding: binding})
}

func appendExactReferenceList(result []ExactReferenceRole, role string, refs []Reference) []ExactReferenceRole {
	for _, ref := range refs {
		result = appendExactReference(result, role, ref)
	}
	return result
}

func appendLineageExactReferences(result []ExactReferenceRole, role string, lineage *SemanticLineage) []ExactReferenceRole {
	if lineage == nil {
		return result
	}
	result = appendExactReference(result, role+".from", lineage.From)
	result = appendExactReference(result, role+".to", lineage.To)
	return appendExactReferenceList(result, role+".basis_refs", lineage.BasisRefs)
}

// extractKnownExactReferences returns Exact References only from Contract types
// that the current runtime has parsed and validated. Unknown Contract payloads
// remain opaque and are never searched heuristically for exact-looking fields.
func extractKnownExactReferences(record RuntimeRecord) []ExactReferenceRole {
	if record.Status != RecordValidated {
		return nil
	}

	var result []ExactReferenceRole

	if record.Decision != nil {
		if decision := record.Decision.Decision; decision != nil {
			result = appendExactReferenceList(result, "decision.context_refs", decision.ContextRefs)
			result = appendExactReferenceList(result, "decision.basis_refs", decision.BasisRefs)
			result = appendExactReferenceList(result, "decision.recommendation_refs", decision.RecommendationRefs)
			result = appendExactReferenceList(result, "decision.unresolved_refs", decision.UnresolvedRefs)
			result = appendExactReferenceList(result, "decision.responsibility_refs", decision.ResponsibilityRefs)
			result = appendLineageExactReferences(result, "decision.lineage", decision.Lineage)
		}
		if recommendation := record.Decision.Recommendation; recommendation != nil {
			result = appendExactReferenceList(result, "recommendation.context_refs", recommendation.ContextRefs)
			result = appendExactReferenceList(result, "recommendation.basis_refs", recommendation.BasisRefs)
			result = appendExactReferenceList(result, "recommendation.responsibility_refs", recommendation.ResponsibilityRefs)
		}
	}

	if record.CognitiveMethod != nil {
		if definition := record.CognitiveMethod.MethodDefinition; definition != nil {
			result = appendExactReferenceList(result, "method_definition.context_refs", definition.ContextRefs)
			result = appendExactReferenceList(result, "method_definition.specification_refs", definition.SpecificationRefs)
		}
		if realization := record.CognitiveMethod.MethodRealization; realization != nil {
			result = appendExactReference(result, "method_realization.method_ref", realization.MethodRef)
			result = appendExactReferenceList(result, "method_realization.implementation_refs", realization.ImplementationRefs)
			result = appendExactReferenceList(result, "method_realization.context_refs", realization.ContextRefs)
		}
		if application := record.CognitiveMethod.MethodApplication; application != nil {
			result = appendExactReference(result, "method_application.method_ref", application.MethodRef)
			if application.RealizationRef != nil {
				result = appendExactReference(result, "method_application.realization_ref", *application.RealizationRef)
			}
			result = appendExactReferenceList(result, "method_application.context_refs", application.ContextRefs)
			result = appendExactReferenceList(result, "method_application.input_refs", application.InputRefs)
			result = appendExactReferenceList(result, "method_application.output_refs", application.OutputRefs)
			result = appendExactReferenceList(result, "method_application.residual_refs", application.ResidualRefs)
			result = appendExactReferenceList(result, "method_application.provenance_refs", application.ProvenanceRefs)
			result = appendExactReferenceList(result, "method_application.responsibility_refs", application.ResponsibilityRefs)
		}
	}

	if record.Capability != nil {
		observation := record.Capability.Observation
		for _, condition := range observation.Conditions {
			result = appendExactReferenceList(result, "capability_observation.conditions.source_refs", condition.SourceRefs)
		}
		result = appendExactReferenceList(result, "capability_observation.provenance_refs", observation.ProvenanceRefs)
		if observation.MappingProvenance != nil {
			result = appendExactReference(result, "capability_observation.mapping_provenance.mapping_ref", observation.MappingProvenance.MappingRef)
		}
	}

	if record.Reference != nil {
		if record.Reference.ExactBinding != nil {
			result = append(result, ExactReferenceRole{Role: "semantic_reference.exact_binding", Binding: *record.Reference.ExactBinding})
		}
		result = appendLineageExactReferences(result, "semantic_reference.semantic_lineage", record.Reference.SemanticLineage)
		if record.Reference.VerificationOutcome != nil {
			result = append(result, ExactReferenceRole{Role: "semantic_reference.verification_outcome.binding", Binding: record.Reference.VerificationOutcome.Binding})
		}
	}

	return result
}
