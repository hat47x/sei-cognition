package capacityprofile

import "fmt"

// GovernedWorkloadDeclaration is an evaluation-only admission snapshot.
//
// Lifecycle, review, expiry, and supersession consistency are validated by the
// upstream workload-class governance contract. This type intentionally does not
// duplicate that validator. It only carries the fields required to prevent an
// unreviewed, closed, superseded, or policy-mismatched declaration from reaching
// WorkloadPolicyEnvelope.Resolve.
type GovernedWorkloadDeclaration struct {
	WorkloadClass       string
	Policy              ResidualPolicyID
	Version             int
	State               string
	ResolutionAllowed   bool
	SupersededByVersion *int
	GovernanceRef       string
}

// ResolveGoverned admits only an already-governance-validated reviewed snapshot.
// It does not infer class correctness and does not activate a production policy.
func (e *WorkloadPolicyEnvelope) ResolveGoverned(
	declaration GovernedWorkloadDeclaration,
) (ResidualPolicyID, error) {
	if e == nil {
		return "", fmt.Errorf("workload policy envelope must not be nil")
	}
	if err := requireCanonicalEnvelopeString("governance ref", declaration.GovernanceRef); err != nil {
		return "", err
	}
	if declaration.Version < 1 {
		return "", fmt.Errorf("declaration version must be >= 1")
	}
	if declaration.State != "reviewed" {
		return "", fmt.Errorf("declaration state must be reviewed")
	}
	if !declaration.ResolutionAllowed {
		return "", fmt.Errorf("declaration is not resolution-allowed")
	}
	if declaration.SupersededByVersion != nil {
		return "", fmt.Errorf("superseded declaration must fail closed")
	}
	if !supportedResidualPolicy(declaration.Policy) {
		return "", fmt.Errorf("declaration has unsupported residual policy: %q", declaration.Policy)
	}

	resolved, err := e.Resolve(declaration.WorkloadClass)
	if err != nil {
		return "", err
	}
	if resolved != declaration.Policy {
		return "", fmt.Errorf(
			"declaration policy %q does not match envelope policy %q",
			declaration.Policy,
			resolved,
		)
	}
	return resolved, nil
}
