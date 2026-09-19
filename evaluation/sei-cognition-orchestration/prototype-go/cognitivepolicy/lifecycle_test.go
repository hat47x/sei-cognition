package cognitivepolicy

import (
	"math"
	"strings"
	"testing"
	"time"
)

func lifecycleTimes() (time.Time, time.Time, time.Time) {
	validFrom := time.Date(2026, 9, 20, 0, 0, 0, 0, time.UTC)
	asOf := validFrom.Add(6 * time.Hour)
	expiresAt := validFrom.Add(24 * time.Hour)
	return validFrom, asOf, expiresAt
}

func lifecycleFor(snapshot Snapshot) PolicyLifecycle {
	validFrom, _, expiresAt := lifecycleTimes()
	return PolicyLifecycle{
		Version:                    snapshot.Version,
		ValidFrom:                  validFrom,
		ExpiresAt:                  expiresAt,
		MaxRegretAgainstStaticRate: 0.25,
	}
}

func candidateForLifecycleTest(t *testing.T) (*Store, Snapshot) {
	t.Helper()
	store, err := NewStore(testDefinitions())
	if err != nil {
		t.Fatal(err)
	}
	candidate, err := store.BuildCandidate(outcomes("routine-summary", "local-slm", 9, 1, 0, 0))
	if err != nil {
		t.Fatal(err)
	}
	return store, candidate
}

func TestLifecycleRetainsAtThresholdEquality(t *testing.T) {
	_, candidate := candidateForLifecycleTest(t)
	_, asOf, _ := lifecycleTimes()
	assessment, err := AssessLifecycle(
		candidate,
		lifecycleFor(candidate),
		asOf,
		ReplayMetrics{TotalCases: 4, RegretAgainstStaticRate: 0.25},
	)
	if err != nil {
		t.Fatal(err)
	}
	if assessment.Disposition != LifecycleRetain {
		t.Fatalf("disposition=%s want %s", assessment.Disposition, LifecycleRetain)
	}
}

func TestLifecycleRequestsRollbackWithoutMutatingActivePolicy(t *testing.T) {
	store, candidate := candidateForLifecycleTest(t)
	if err := store.Activate(candidate.Version); err != nil {
		t.Fatal(err)
	}
	before := store.ActiveVersion()
	_, asOf, _ := lifecycleTimes()
	assessment, err := AssessLifecycle(
		candidate,
		lifecycleFor(candidate),
		asOf,
		ReplayMetrics{TotalCases: 4, RegretAgainstStaticRate: 0.50},
	)
	if err != nil {
		t.Fatal(err)
	}
	if assessment.Disposition != LifecycleRequestRollback {
		t.Fatalf("disposition=%s want %s", assessment.Disposition, LifecycleRequestRollback)
	}
	if store.ActiveVersion() != before {
		t.Fatalf("diagnostic mutated active policy: before=%s after=%s", before, store.ActiveVersion())
	}
}

func TestLifecycleExpiryIsFailClosedAndDoesNotRollbackAutomatically(t *testing.T) {
	store, candidate := candidateForLifecycleTest(t)
	if err := store.Activate(candidate.Version); err != nil {
		t.Fatal(err)
	}
	lifecycle := lifecycleFor(candidate)
	assessment, err := AssessLifecycle(
		candidate,
		lifecycle,
		lifecycle.ExpiresAt,
		ReplayMetrics{TotalCases: 4, RegretAgainstStaticRate: 0},
	)
	if err != nil {
		t.Fatal(err)
	}
	if assessment.Disposition != LifecycleExpired {
		t.Fatalf("disposition=%s want %s", assessment.Disposition, LifecycleExpired)
	}
	if store.ActiveVersion() != candidate.Version {
		t.Fatalf("expiry diagnostic automatically changed active policy: %s", store.ActiveVersion())
	}
}

func TestLifecycleRejectsVersionMismatch(t *testing.T) {
	_, candidate := candidateForLifecycleTest(t)
	lifecycle := lifecycleFor(candidate)
	lifecycle.Version = BaselineVersion
	_, asOf, _ := lifecycleTimes()
	_, err := AssessLifecycle(candidate, lifecycle, asOf, ReplayMetrics{TotalCases: 1})
	if err == nil || !strings.Contains(err.Error(), "does not match") {
		t.Fatalf("version mismatch must fail closed: %v", err)
	}
}

func TestLifecycleRejectsInvalidLogicalTimes(t *testing.T) {
	_, candidate := candidateForLifecycleTest(t)
	validFrom, asOf, expiresAt := lifecycleTimes()
	cases := []struct {
		name      string
		lifecycle PolicyLifecycle
		asOf      time.Time
	}{
		{
			name: "zero-valid-from",
			lifecycle: PolicyLifecycle{
				Version: candidate.Version, ExpiresAt: expiresAt, MaxRegretAgainstStaticRate: 0.25,
			},
			asOf: asOf,
		},
		{
			name: "zero-expires-at",
			lifecycle: PolicyLifecycle{
				Version: candidate.Version, ValidFrom: validFrom, MaxRegretAgainstStaticRate: 0.25,
			},
			asOf: asOf,
		},
		{
			name:      "zero-as-of",
			lifecycle: lifecycleFor(candidate),
		},
		{
			name: "reversed-window",
			lifecycle: PolicyLifecycle{
				Version: candidate.Version, ValidFrom: expiresAt, ExpiresAt: validFrom, MaxRegretAgainstStaticRate: 0.25,
			},
			asOf: asOf,
		},
		{
			name:      "not-yet-valid",
			lifecycle: lifecycleFor(candidate),
			asOf:      validFrom.Add(-time.Second),
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			_, err := AssessLifecycle(candidate, tc.lifecycle, tc.asOf, ReplayMetrics{TotalCases: 1})
			if err == nil {
				t.Fatal("invalid logical lifecycle must fail closed")
			}
		})
	}
}

func TestLifecycleRejectsInvalidRegretThreshold(t *testing.T) {
	_, candidate := candidateForLifecycleTest(t)
	_, asOf, _ := lifecycleTimes()
	for _, threshold := range []float64{-0.01, 1.01, math.NaN(), math.Inf(1), math.Inf(-1)} {
		lifecycle := lifecycleFor(candidate)
		lifecycle.MaxRegretAgainstStaticRate = threshold
		if _, err := AssessLifecycle(candidate, lifecycle, asOf, ReplayMetrics{TotalCases: 1}); err == nil {
			t.Fatalf("threshold %v must fail closed", threshold)
		}
	}
}

func TestLifecycleRejectsMissingOrInvalidReplay(t *testing.T) {
	_, candidate := candidateForLifecycleTest(t)
	_, asOf, _ := lifecycleTimes()
	lifecycle := lifecycleFor(candidate)
	cases := []ReplayMetrics{
		{TotalCases: 0, RegretAgainstStaticRate: 0},
		{TotalCases: 1, RegretAgainstStaticRate: -0.01},
		{TotalCases: 1, RegretAgainstStaticRate: 1.01},
		{TotalCases: 1, RegretAgainstStaticRate: math.NaN()},
		{TotalCases: 1, RegretAgainstStaticRate: math.Inf(1)},
	}
	for i, replay := range cases {
		if _, err := AssessLifecycle(candidate, lifecycle, asOf, replay); err == nil {
			t.Fatalf("case %d must fail closed: %#v", i, replay)
		}
	}
}

func TestLifecycleExpiryPrecedesRegretDisposition(t *testing.T) {
	_, candidate := candidateForLifecycleTest(t)
	lifecycle := lifecycleFor(candidate)
	assessment, err := AssessLifecycle(
		candidate,
		lifecycle,
		lifecycle.ExpiresAt.Add(time.Second),
		ReplayMetrics{TotalCases: 1, RegretAgainstStaticRate: 1},
	)
	if err != nil {
		t.Fatal(err)
	}
	if assessment.Disposition != LifecycleExpired {
		t.Fatalf("expired snapshot must remain expired, got %s", assessment.Disposition)
	}
}
