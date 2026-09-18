package capacityprofile

import (
	"math"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func mediumProfile() Profile {
	return Profile{
		ID: "medium",
		Sparse: sparseassoc.Config{
			Dimensions: 4096,
			Fanout:     8,
			Active:     64,
			Seed:       47,
		},
	}
}

func TestScaleDimensionsPreservesActiveFractionForExactProfiles(t *testing.T) {
	base := mediumProfile()
	cases := []struct {
		id         string
		dimensions uint16
		active     uint16
	}{
		{"small", 2048, 32},
		{"medium-copy", 4096, 64},
		{"large", 8192, 128},
		{"oversized", 32768, 512},
	}
	for _, tc := range cases {
		got, err := ScaleDimensions(base, tc.id, tc.dimensions)
		if err != nil {
			t.Fatal(err)
		}
		if got.Sparse.Active != tc.active {
			t.Fatalf("%s active=%d want %d", tc.id, got.Sparse.Active, tc.active)
		}
		if got.Sparse.Fanout != base.Sparse.Fanout || got.Sparse.Seed != base.Sparse.Seed {
			t.Fatalf("%s changed fanout/seed: %#v", tc.id, got)
		}
		if math.Abs(ActiveFraction(got)-1.0/64.0) > 1e-12 {
			t.Fatalf("%s fraction=%v want 1/64", tc.id, ActiveFraction(got))
		}
	}
}

func TestScaleDimensionsRoundsDeterministicallyWhenFractionIsNotExact(t *testing.T) {
	base := mediumProfile()
	got, err := ScaleDimensions(base, "rounded", 3000)
	if err != nil {
		t.Fatal(err)
	}
	if got.Sparse.Active != 47 {
		t.Fatalf("active=%d want 47", got.Sparse.Active)
	}
}

func TestMemoryProxiesIncreaseWithProfileCapacity(t *testing.T) {
	base := mediumProfile()
	small, _ := ScaleDimensions(base, "small", 2048)
	medium, _ := ScaleDimensions(base, "medium-copy", 4096)
	large, _ := ScaleDimensions(base, "large", 8192)

	if SignaturePayloadBytes(small) != 64 || SignaturePayloadBytes(medium) != 128 || SignaturePayloadBytes(large) != 256 {
		t.Fatalf("unexpected signature payloads: %d %d %d",
			SignaturePayloadBytes(small), SignaturePayloadBytes(medium), SignaturePayloadBytes(large))
	}
	if EncoderScratchLowerBoundBytes(small) != 16384 ||
		EncoderScratchLowerBoundBytes(medium) != 32768 ||
		EncoderScratchLowerBoundBytes(large) != 65536 {
		t.Fatalf("unexpected scratch lower bounds: %d %d %d",
			EncoderScratchLowerBoundBytes(small),
			EncoderScratchLowerBoundBytes(medium),
			EncoderScratchLowerBoundBytes(large))
	}
}

func TestEqualLocalHalfResidualScalesB2Budget(t *testing.T) {
	cases := []struct {
		active   uint16
		local    uint16
		residual uint16
	}{
		{32, 4, 16},
		{64, 8, 32},
		{128, 16, 64},
	}
	for _, tc := range cases {
		local, residual, err := EqualLocalHalfResidual(tc.active, 4)
		if err != nil {
			t.Fatal(err)
		}
		if local != tc.local || residual != tc.residual {
			t.Fatalf("active=%d local/residual=%d/%d want %d/%d",
				tc.active, local, residual, tc.local, tc.residual)
		}
		if int(local)*4+int(residual) != int(tc.active) {
			t.Fatalf("active budget not conserved: active=%d local=%d residual=%d", tc.active, local, residual)
		}
	}
}

func TestEqualLocalHalfResidualCappedPreservesLocalHalfAndCapsResidual(t *testing.T) {
	cases := []struct {
		active   uint16
		cap      uint16
		local    uint16
		residual uint16
	}{
		{32, 64, 4, 16},
		{64, 64, 8, 32},
		{128, 64, 16, 64},
		{512, 64, 64, 64},
		{512, 128, 64, 128},
	}
	for _, tc := range cases {
		local, residual, err := EqualLocalHalfResidualCapped(tc.active, 4, tc.cap)
		if err != nil {
			t.Fatal(err)
		}
		if local != tc.local || residual != tc.residual {
			t.Fatalf("active/cap=%d/%d local/residual=%d/%d want %d/%d",
				tc.active, tc.cap, local, residual, tc.local, tc.residual)
		}
		reserved := int(local)*4 + int(residual)
		if reserved > int(tc.active) {
			t.Fatalf("reserved=%d exceeds active=%d", reserved, tc.active)
		}
	}
}

func TestEqualLocalHalfResidualCappedRejectsZeroCap(t *testing.T) {
	if _, _, err := EqualLocalHalfResidualCapped(64, 4, 0); err == nil {
		t.Fatal("zero residual cap must fail")
	}
}

func TestTooSmallProfileCannotPreserveFourFamilyHalfResidualPolicy(t *testing.T) {
	base := mediumProfile()
	tiny, err := ScaleDimensions(base, "tiny", 256)
	if err != nil {
		t.Fatal(err)
	}
	if tiny.Sparse.Active != 4 {
		t.Fatalf("tiny active=%d want 4", tiny.Sparse.Active)
	}
	if _, _, err := EqualLocalHalfResidual(tiny.Sparse.Active, 4); err == nil {
		t.Fatal("active=4 must fail rather than silently distort four-family half-residual policy")
	}
}

func TestWinnerShareUpperBoundRevealsSelectionPressureLoss(t *testing.T) {
	base := mediumProfile()
	small, _ := ScaleDimensions(base, "small", 2048)
	medium, _ := ScaleDimensions(base, "medium-copy", 4096)
	large, _ := ScaleDimensions(base, "large", 8192)
	oversized, _ := ScaleDimensions(base, "oversized", 32768)

	const positiveFeatures = 72
	shares := []float64{
		WinnerShareUpperBound(small, positiveFeatures),
		WinnerShareUpperBound(medium, positiveFeatures),
		WinnerShareUpperBound(large, positiveFeatures),
		WinnerShareUpperBound(oversized, positiveFeatures),
	}
	for i := 1; i < len(shares); i++ {
		if shares[i] <= shares[i-1] {
			t.Fatalf("winner share did not increase: %#v", shares)
		}
	}
	if shares[3] < 0.8 {
		t.Fatalf("oversized profile should expose weak selection pressure: %#v", shares)
	}
}

func TestObservedWinnerShareAndCollisionFraction(t *testing.T) {
	stats := sparseassoc.EncodeStats{
		PositiveFeatures:   72,
		ProjectionAttempts: 576,
		TouchedDimensions:  495,
		SelectedDimensions: 16,
	}
	if got := ObservedWinnerShare(stats); math.Abs(got-(16.0/495.0)) > 1e-12 {
		t.Fatalf("observed winner share=%v want %v", got, 16.0/495.0)
	}
	if got := ProjectionCollisionFraction(stats); math.Abs(got-(81.0/576.0)) > 1e-12 {
		t.Fatalf("collision fraction=%v want %v", got, 81.0/576.0)
	}
	if got := ObservedWinnerShare(sparseassoc.EncodeStats{}); got != 0 {
		t.Fatalf("zero touched winner share=%v want 0", got)
	}
	if got := ProjectionCollisionFraction(sparseassoc.EncodeStats{}); got != 0 {
		t.Fatalf("zero attempts collision fraction=%v want 0", got)
	}
}

func TestProfileValidationFailsClosed(t *testing.T) {
	if err := Validate(Profile{}); err == nil {
		t.Fatal("empty profile must fail")
	}
	base := mediumProfile()
	base.ID = ""
	if err := Validate(base); err == nil {
		t.Fatal("empty id must fail")
	}
	if _, err := ScaleDimensions(mediumProfile(), "", 2048); err == nil {
		t.Fatal("empty scaled id must fail")
	}
	if _, err := ScaleDimensions(mediumProfile(), "zero", 0); err == nil {
		t.Fatal("zero dimensions must fail")
	}
}

func TestProjectionUpperBound(t *testing.T) {
	if got := ProjectionUpperBound(72, 8); got != 576 {
		t.Fatalf("upper bound=%d want 576", got)
	}
	if got := ProjectionUpperBound(0, 8); got != 0 {
		t.Fatalf("zero features upper bound=%d", got)
	}
}
