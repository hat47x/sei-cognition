package cognitivepolicy

import (
	"errors"
	"fmt"
	"math"
	"time"
)

// LifecycleDisposition is an evaluation-only diagnostic. It never mutates the
// active policy or grants permission to activate or roll back a snapshot.
type LifecycleDisposition string

const (
	LifecycleRetain          LifecycleDisposition = "retain"
	LifecycleRequestRollback LifecycleDisposition = "request-rollback"
	LifecycleExpired         LifecycleDisposition = "expired"
)

// PolicyLifecycle is caller-owned evaluation metadata for one immutable
// snapshot. Logical timestamps are explicit so replay remains deterministic.
type PolicyLifecycle struct {
	Version                    string
	ValidFrom                  time.Time
	ExpiresAt                  time.Time
	MaxRegretAgainstStaticRate float64
}

type LifecycleAssessment struct {
	Disposition LifecycleDisposition
	Reason      string
}

// AssessLifecycle evaluates expiry and replay regret without changing Store
// state. replay must come from a counterfactually complete replay; this
// function is not an online regret estimator.
func AssessLifecycle(
	snapshot Snapshot,
	lifecycle PolicyLifecycle,
	asOf time.Time,
	replay ReplayMetrics,
) (LifecycleAssessment, error) {
	if snapshot.Version == "" {
		return LifecycleAssessment{}, errors.New("snapshot version must not be empty")
	}
	if lifecycle.Version == "" {
		return LifecycleAssessment{}, errors.New("lifecycle version must not be empty")
	}
	if lifecycle.Version != snapshot.Version {
		return LifecycleAssessment{}, fmt.Errorf(
			"lifecycle version %s does not match snapshot %s",
			lifecycle.Version,
			snapshot.Version,
		)
	}
	if lifecycle.ValidFrom.IsZero() || lifecycle.ExpiresAt.IsZero() || asOf.IsZero() {
		return LifecycleAssessment{}, errors.New("logical lifecycle times must not be zero")
	}
	if !lifecycle.ValidFrom.Before(lifecycle.ExpiresAt) {
		return LifecycleAssessment{}, errors.New("valid_from must be before expires_at")
	}
	if asOf.Before(lifecycle.ValidFrom) {
		return LifecycleAssessment{}, errors.New("snapshot is not yet valid at logical as_of")
	}
	if math.IsNaN(lifecycle.MaxRegretAgainstStaticRate) ||
		math.IsInf(lifecycle.MaxRegretAgainstStaticRate, 0) ||
		lifecycle.MaxRegretAgainstStaticRate < 0 ||
		lifecycle.MaxRegretAgainstStaticRate > 1 {
		return LifecycleAssessment{}, errors.New("maximum regret rate must be finite and in [0,1]")
	}
	if replay.TotalCases <= 0 {
		return LifecycleAssessment{}, errors.New("replay must contain at least one case")
	}
	if math.IsNaN(replay.RegretAgainstStaticRate) ||
		math.IsInf(replay.RegretAgainstStaticRate, 0) ||
		replay.RegretAgainstStaticRate < 0 ||
		replay.RegretAgainstStaticRate > 1 {
		return LifecycleAssessment{}, errors.New("replay regret rate must be finite and in [0,1]")
	}

	if !asOf.Before(lifecycle.ExpiresAt) {
		return LifecycleAssessment{
			Disposition: LifecycleExpired,
			Reason:      "caller-owned lifecycle expired",
		}, nil
	}
	if replay.RegretAgainstStaticRate > lifecycle.MaxRegretAgainstStaticRate {
		return LifecycleAssessment{
			Disposition: LifecycleRequestRollback,
			Reason:      "counterfactual replay regret exceeded caller-owned threshold",
		}, nil
	}
	return LifecycleAssessment{
		Disposition: LifecycleRetain,
		Reason:      "snapshot remains within lifecycle and regret threshold",
	}, nil
}
