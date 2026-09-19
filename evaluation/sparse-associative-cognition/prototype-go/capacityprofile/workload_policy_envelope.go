package capacityprofile

import (
	"errors"
	"fmt"
	"strings"
)

// ResidualPolicyID names an evaluation-only static residual policy.
// It carries no semantic quality, priority, or deployment meaning.
type ResidualPolicyID string

const (
	ResidualPolicyBaseline ResidualPolicyID = "baseline"
	ResidualPolicyCap128   ResidualPolicyID = "cap128"
	ResidualPolicyCap64    ResidualPolicyID = "cap64"
)

type WorkloadPolicyBinding struct {
	WorkloadClass string
	Policy        ResidualPolicyID
}

// WorkloadPolicyEnvelope resolves only caller-owned exact workload classes.
// It does not observe feature cardinality, item content, quality, or runtime
// statistics and therefore cannot infer a class on the caller's behalf.
type WorkloadPolicyEnvelope struct {
	id            string
	provenanceRef string
	bindings      map[string]ResidualPolicyID
}

func NewWorkloadPolicyEnvelope(
	id string,
	provenanceRef string,
	bindings []WorkloadPolicyBinding,
) (*WorkloadPolicyEnvelope, error) {
	if err := requireCanonicalEnvelopeString("envelope id", id); err != nil {
		return nil, err
	}
	if err := requireCanonicalEnvelopeString("provenance ref", provenanceRef); err != nil {
		return nil, err
	}
	if len(bindings) == 0 {
		return nil, errors.New("at least one workload policy binding is required")
	}

	out := &WorkloadPolicyEnvelope{
		id:            id,
		provenanceRef: provenanceRef,
		bindings:      make(map[string]ResidualPolicyID, len(bindings)),
	}
	for i, binding := range bindings {
		if err := requireCanonicalEnvelopeString("workload class", binding.WorkloadClass); err != nil {
			return nil, fmt.Errorf("binding %d: %w", i, err)
		}
		if !supportedResidualPolicy(binding.Policy) {
			return nil, fmt.Errorf("binding %d has unsupported residual policy: %q", i, binding.Policy)
		}
		if _, exists := out.bindings[binding.WorkloadClass]; exists {
			return nil, fmt.Errorf("duplicate workload class: %s", binding.WorkloadClass)
		}
		out.bindings[binding.WorkloadClass] = binding.Policy
	}
	return out, nil
}

func (e *WorkloadPolicyEnvelope) ID() string {
	return e.id
}

func (e *WorkloadPolicyEnvelope) ProvenanceRef() string {
	return e.provenanceRef
}

func (e *WorkloadPolicyEnvelope) Resolve(workloadClass string) (ResidualPolicyID, error) {
	if err := requireCanonicalEnvelopeString("workload class", workloadClass); err != nil {
		return "", err
	}
	policy, ok := e.bindings[workloadClass]
	if !ok {
		return "", fmt.Errorf("unknown workload class: %s", workloadClass)
	}
	return policy, nil
}

func supportedResidualPolicy(policy ResidualPolicyID) bool {
	switch policy {
	case ResidualPolicyBaseline, ResidualPolicyCap128, ResidualPolicyCap64:
		return true
	default:
		return false
	}
}

func requireCanonicalEnvelopeString(field, value string) error {
	if strings.TrimSpace(value) == "" {
		return fmt.Errorf("%s must not be empty", field)
	}
	if strings.TrimSpace(value) != value {
		return fmt.Errorf("%s must already be canonical", field)
	}
	return nil
}
