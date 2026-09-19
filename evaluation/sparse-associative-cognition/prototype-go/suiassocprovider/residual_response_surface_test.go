package suiassocprovider

import (
	"fmt"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/capacityprofile"
)

func responseSurfaceText(start rune, length int) string {
	var b strings.Builder
	for i := 0; i < length; i++ {
		b.WriteRune(start + rune(i))
	}
	return b.String()
}

func responseSurfaceValues(prefix string, count int) []string {
	out := make([]string, count)
	for i := range out {
		out[i] = fmt.Sprintf("%s%d", prefix, i+1)
	}
	return out
}

func responseSurfaceItems(textRunes, structuredPerSubchannel int) (Item, Item, Item) {
	anchorText := responseSurfaceText(0x4e00, textRunes)
	desiredText := responseSurfaceText(0x5200, textRunes)

	relations := responseSurfaceValues("r", structuredPerSubchannel)
	neighbors := responseSurfaceValues("k", structuredPerSubchannel)
	sources := responseSurfaceValues("s", structuredPerSubchannel)
	actors := responseSurfaceValues("a", structuredPerSubchannel)

	anchor := Item{
		Ref:  fmt.Sprintf("surface-anchor-t%d-s%d", textRunes, structuredPerSubchannel),
		Kind: "card",
		Channels: Channels{
			Text: anchorText,
			Graph: &GraphChannel{
				RelationTypes: relations,
				NeighborKinds: neighbors,
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: sources,
				ActorRefs:  actors,
			},
			Grouping: &GroupingChannel{IslandRef: "surface-island", HoldState: "hold"},
		},
	}
	desired := Item{
		Ref:  fmt.Sprintf("surface-desired-t%d-s%d", textRunes, structuredPerSubchannel),
		Kind: "card",
		Channels: Channels{
			Text: desiredText,
			Graph: &GraphChannel{
				RelationTypes: relations,
				NeighborKinds: neighbors,
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: sources,
				ActorRefs:  actors,
			},
			Grouping: &GroupingChannel{IslandRef: "surface-island", HoldState: "hold"},
		},
	}
	distractor := Item{
		Ref:  fmt.Sprintf("surface-distractor-t%d-s%d", textRunes, structuredPerSubchannel),
		Kind: "card",
		Channels: Channels{
			Text: anchorText,
			Graph: &GraphChannel{
				RelationTypes: responseSurfaceValues("x", structuredPerSubchannel),
				NeighborKinds: responseSurfaceValues("y", structuredPerSubchannel),
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: responseSurfaceValues("u", structuredPerSubchannel),
				ActorRefs:  responseSurfaceValues("v", structuredPerSubchannel),
			},
			Grouping: &GroupingChannel{IslandRef: "surface-other", HoldState: "none"},
		},
	}
	return anchor, desired, distractor
}

type residualSurfaceResult struct {
	margin      float32
	incremental int
}

func responseSurfaceResult(
	t *testing.T,
	profile capacityprofile.Profile,
	policy *LocalCompetitionPolicy,
	anchor Item,
	desired Item,
	distractor Item,
) residualSurfaceResult {
	t.Helper()
	desiredSimilarity, distractorSimilarity := capacitySimilarityForItemsWithPolicy(
		t,
		profile,
		FeatureNormalizationFamily,
		policy,
		anchor,
		desired,
		distractor,
	)
	_, stats := capacityObservedStatsWithPolicy(t, profile, anchor, policy)
	return residualSurfaceResult{
		margin:      desiredSimilarity - distractorSimilarity,
		incremental: stats.Local.LocalIncrementalDimensions,
	}
}

func TestResidualScalingResponseSurface(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}

	type expectedCell struct {
		textRunes     int
		structured    int
		textFeatures  int
		baseline      float32
		cap128        float32
		cap64         float32
		baselineInc   int
		cap128Inc     int
		cap64Inc      int
		expectedClass string
	}
	cells := []expectedCell{
		{5, 1, 7, -0.07142857, -0.07142857, -0.07142857, 0, 0, 48, "all-tie"},
		{5, 2, 7, 0.16666667, 0.16666667, 0.16666667, 0, 16, 80, "all-tie"},
		{5, 4, 7, 0.41826922, 0.41826922, 0.41826922, 0, 80, 144, "all-tie"},
		{5, 8, 7, 0.52734375, 0.41875, 0.41679686, 0, 81, 144, "baseline"},
		{17, 1, 31, -0.5859375, -0.1875, -0.13333334, 0, 0, 56, "cap64"},
		{17, 2, 31, -0.33984375, 0.10526316, 0.10526316, 0, 24, 88, "capped-tie"},
		{17, 4, 31, 0.15625, 0.36574075, 0.36574075, 0, 88, 152, "capped-tie"},
		{17, 8, 31, 0.5752795, 0.37037036, 0.37037036, 64, 90, 154, "baseline"},
		{33, 1, 63, -0.578125, -0.1796875, -0.125, 0, 0, 56, "cap64"},
		{33, 2, 63, -0.3359375, 0.1118421, 0.1118421, 0, 24, 88, "capped-tie"},
		{33, 4, 63, 0.15234375, 0.37121212, 0.37121212, 0, 88, 152, "capped-tie"},
		{33, 8, 63, 0.57421875, 0.36789772, 0.36789772, 63, 90, 154, "baseline"},
		{55, 1, 107, -0.57421875, -0.171875, -0.11666667, 0, 0, 56, "cap64"},
		{55, 2, 107, -0.328125, 0.118421055, 0.118421055, 0, 24, 88, "capped-tie"},
		{55, 4, 107, 0.1640625, 0.37424242, 0.37424242, 0, 88, 152, "capped-tie"},
		{55, 8, 107, 0.5763889, 0.36842105, 0.36842105, 63, 90, 154, "baseline"},
	}

	baselinePolicy, err := softLocalPolicyForProfile(oversized)
	if err != nil {
		t.Fatal(err)
	}
	cap128Policy, err := softLocalCappedPolicyForProfile(oversized, 128)
	if err != nil {
		t.Fatal(err)
	}
	cap64Policy, err := softLocalCappedPolicyForProfile(oversized, 64)
	if err != nil {
		t.Fatal(err)
	}

	near := func(got, want float32) bool {
		delta := got - want
		return delta > -0.00002 && delta < 0.00002
	}
	classify := func(baseline, cap128, cap64 float32) string {
		if near(baseline, cap128) && near(cap128, cap64) {
			return "all-tie"
		}
		if near(cap128, cap64) && cap128 > baseline {
			return "capped-tie"
		}
		if baseline > cap128 && baseline > cap64 {
			return "baseline"
		}
		if cap64 > baseline && cap64 > cap128 {
			return "cap64"
		}
		if cap128 > baseline && cap128 > cap64 {
			return "cap128"
		}
		return "mixed"
	}

	for _, cell := range cells {
		name := fmt.Sprintf("t%d-s%d", cell.textRunes, cell.structured)
		t.Run(name, func(t *testing.T) {
			anchor, desired, distractor := responseSurfaceItems(cell.textRunes, cell.structured)
			counts := map[string]int{}
			for _, feature := range featuresForItem(anchor) {
				counts[featureFamily(feature.Channel)]++
			}
			if counts["text"] != cell.textFeatures {
				t.Fatalf("text features=%d want %d", counts["text"], cell.textFeatures)
			}
			if counts["graph"] != 2*cell.structured ||
				counts["provenance"] != 2*cell.structured ||
				counts["grouping"] != 2 ||
				counts["kind"] != 1 {
				t.Fatalf("unexpected family counts: %#v", counts)
			}

			baseline := responseSurfaceResult(t, oversized, baselinePolicy, anchor, desired, distractor)
			cap128 := responseSurfaceResult(t, oversized, cap128Policy, anchor, desired, distractor)
			cap64 := responseSurfaceResult(t, oversized, cap64Policy, anchor, desired, distractor)

			if !near(baseline.margin, cell.baseline) ||
				!near(cap128.margin, cell.cap128) ||
				!near(cap64.margin, cell.cap64) {
				t.Fatalf(
					"margins=%v/%v/%v want approximately %v/%v/%v",
					baseline.margin, cap128.margin, cap64.margin,
					cell.baseline, cell.cap128, cell.cap64,
				)
			}
			if baseline.incremental != cell.baselineInc ||
				cap128.incremental != cell.cap128Inc ||
				cap64.incremental != cell.cap64Inc {
				t.Fatalf(
					"incremental=%d/%d/%d want %d/%d/%d",
					baseline.incremental, cap128.incremental, cap64.incremental,
					cell.baselineInc, cell.cap128Inc, cell.cap64Inc,
				)
			}
			if got := classify(baseline.margin, cap128.margin, cap64.margin); got != cell.expectedClass {
				t.Fatalf("policy class=%s want %s", got, cell.expectedClass)
			}
		})
	}
}

func TestResidualScalingCannotUseSingleCardinalityRatioThreshold(t *testing.T) {
	// These two cells have almost the same text/(graph+provenance+grouping)
	// cardinality ratio, yet prefer different static policies.
	leftAnchor, leftDesired, leftDistractor := responseSurfaceItems(17, 2)
	rightAnchor, rightDesired, rightDistractor := responseSurfaceItems(55, 8)

	ratio := func(item Item) float64 {
		counts := map[string]int{}
		for _, feature := range featuresForItem(item) {
			counts[featureFamily(feature.Channel)]++
		}
		structured := counts["graph"] + counts["provenance"] + counts["grouping"]
		return float64(counts["text"]) / float64(structured)
	}
	leftRatio := ratio(leftAnchor)
	rightRatio := ratio(rightAnchor)
	if diff := leftRatio - rightRatio; diff < -0.06 || diff > 0.06 {
		t.Fatalf("fixture ratios are not close enough: left=%v right=%v", leftRatio, rightRatio)
	}

	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	baseline, _ := softLocalPolicyForProfile(oversized)
	cap128, _ := softLocalCappedPolicyForProfile(oversized, 128)

	leftBaseline := responseSurfaceResult(t, oversized, baseline, leftAnchor, leftDesired, leftDistractor)
	leftCapped := responseSurfaceResult(t, oversized, cap128, leftAnchor, leftDesired, leftDistractor)
	rightBaseline := responseSurfaceResult(t, oversized, baseline, rightAnchor, rightDesired, rightDistractor)
	rightCapped := responseSurfaceResult(t, oversized, cap128, rightAnchor, rightDesired, rightDistractor)

	if leftCapped.margin <= leftBaseline.margin {
		t.Fatalf("left fixture must prefer capped policy: baseline=%v cap128=%v",
			leftBaseline.margin, leftCapped.margin)
	}
	if rightBaseline.margin <= rightCapped.margin {
		t.Fatalf("right fixture must prefer baseline: baseline=%v cap128=%v",
			rightBaseline.margin, rightCapped.margin)
	}
}
