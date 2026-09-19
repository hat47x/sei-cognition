package suiassocprovider

import (
	"math"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/capacityprofile"
)

func envelopeStaticPolicy(
	t *testing.T,
	profile capacityprofile.Profile,
	policyID capacityprofile.ResidualPolicyID,
) *LocalCompetitionPolicy {
	t.Helper()
	switch policyID {
	case capacityprofile.ResidualPolicyBaseline:
		policy, err := softLocalPolicyForProfile(profile)
		if err != nil {
			t.Fatal(err)
		}
		return policy
	case capacityprofile.ResidualPolicyCap128:
		policy, err := softLocalCappedPolicyForProfile(profile, 128)
		if err != nil {
			t.Fatal(err)
		}
		return policy
	case capacityprofile.ResidualPolicyCap64:
		policy, err := softLocalCappedPolicyForProfile(profile, 64)
		if err != nil {
			t.Fatal(err)
		}
		return policy
	default:
		t.Fatalf("unsupported residual policy id: %q", policyID)
		return nil
	}
}

func TestCallerOwnedWorkloadEnvelopeReducesFixedPolicyRegretWithoutBecomingOracle(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}

	envelope, err := capacityprofile.NewWorkloadPolicyEnvelope(
		"b6g-grid-eval-v1",
		"evidence://sac-b6g/fixed-envelope",
		[]capacityprofile.WorkloadPolicyBinding{
			{WorkloadClass: "general", Policy: capacityprofile.ResidualPolicyCap128},
			{WorkloadClass: "structure-preserving", Policy: capacityprofile.ResidualPolicyBaseline},
		},
	)
	if err != nil {
		t.Fatal(err)
	}

	// WorkloadClass is deliberately declared in the fixture table. The
	// envelope resolver never observes textRunes, structured cardinality,
	// features, margins, or semantic content.
	cells := []struct {
		textRunes     int
		structured    int
		workloadClass string
	}{
		{5, 1, "general"},
		{5, 2, "general"},
		{5, 4, "general"},
		{5, 8, "structure-preserving"},
		{17, 1, "general"},
		{17, 2, "general"},
		{17, 4, "general"},
		{17, 8, "structure-preserving"},
		{33, 1, "general"},
		{33, 2, "general"},
		{33, 4, "general"},
		{33, 8, "structure-preserving"},
		{55, 1, "general"},
		{55, 2, "general"},
		{55, 4, "general"},
		{55, 8, "structure-preserving"},
	}

	baselinePolicy := envelopeStaticPolicy(t, oversized, capacityprofile.ResidualPolicyBaseline)
	cap128Policy := envelopeStaticPolicy(t, oversized, capacityprofile.ResidualPolicyCap128)
	cap64Policy := envelopeStaticPolicy(t, oversized, capacityprofile.ResidualPolicyCap64)

	var envelopeRegretSum float64
	var fixedCap128RegretSum float64
	var envelopeMaxRegret float64
	zeroRegretCells := 0

	for _, cell := range cells {
		anchor, desired, distractor := responseSurfaceItems(cell.textRunes, cell.structured)
		baseline := responseSurfaceResult(t, oversized, baselinePolicy, anchor, desired, distractor)
		cap128 := responseSurfaceResult(t, oversized, cap128Policy, anchor, desired, distractor)
		cap64 := responseSurfaceResult(t, oversized, cap64Policy, anchor, desired, distractor)

		best := float64(baseline.margin)
		if float64(cap128.margin) > best {
			best = float64(cap128.margin)
		}
		if float64(cap64.margin) > best {
			best = float64(cap64.margin)
		}

		policyID, err := envelope.Resolve(cell.workloadClass)
		if err != nil {
			t.Fatal(err)
		}
		chosenPolicy := envelopeStaticPolicy(t, oversized, policyID)
		chosen := responseSurfaceResult(t, oversized, chosenPolicy, anchor, desired, distractor)

		regret := best - float64(chosen.margin)
		if regret < 0 && regret > -1e-7 {
			regret = 0
		}
		envelopeRegretSum += regret
		if regret > envelopeMaxRegret {
			envelopeMaxRegret = regret
		}
		if regret <= 1e-7 {
			zeroRegretCells++
		}

		fixedCap128Regret := best - float64(cap128.margin)
		if fixedCap128Regret < 0 && fixedCap128Regret > -1e-7 {
			fixedCap128Regret = 0
		}
		fixedCap128RegretSum += fixedCap128Regret
	}

	envelopeMean := envelopeRegretSum / float64(len(cells))
	fixedCap128Mean := fixedCap128RegretSum / float64(len(cells))

	if math.Abs(envelopeMean-0.0102539) > 0.00001 {
		t.Fatalf("envelope mean regret=%v want approximately 0.0102539", envelopeMean)
	}
	if math.Abs(envelopeMaxRegret-0.0552083) > 0.00001 {
		t.Fatalf("envelope max regret=%v want approximately 0.0552083", envelopeMaxRegret)
	}
	if zeroRegretCells != 13 {
		t.Fatalf("zero-regret cells=%d want 13", zeroRegretCells)
	}
	if envelopeMean >= fixedCap128Mean {
		t.Fatalf("envelope mean regret=%v must be below fixed cap128=%v",
			envelopeMean, fixedCap128Mean)
	}
	if envelopeMean == 0 || envelopeMaxRegret == 0 {
		t.Fatal("fixed caller-owned envelope must not be mistaken for a cell-best oracle")
	}
}

func TestWorkloadEnvelopeResolutionDependsOnlyOnCallerDeclaration(t *testing.T) {
	envelope, err := capacityprofile.NewWorkloadPolicyEnvelope(
		"b6g-declaration-only-v1",
		"evidence://sac-b6g/declaration-only",
		[]capacityprofile.WorkloadPolicyBinding{
			{WorkloadClass: "general", Policy: capacityprofile.ResidualPolicyCap128},
			{WorkloadClass: "structure-preserving", Policy: capacityprofile.ResidualPolicyBaseline},
		},
	)
	if err != nil {
		t.Fatal(err)
	}

	general, err := envelope.Resolve("general")
	if err != nil {
		t.Fatal(err)
	}
	structural, err := envelope.Resolve("structure-preserving")
	if err != nil {
		t.Fatal(err)
	}
	if general == structural {
		t.Fatalf("caller declarations must remain distinct: general=%q structural=%q",
			general, structural)
	}

	// No Item, feature count, margin, or cardinality is passed to Resolve.
	// This test intentionally fixes the API boundary rather than inferring a
	// class from synthetic grid geometry.
}
