package suiassocprovider

import (
	"fmt"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/capacityprofile"
	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func capacityBaseProfile() capacityprofile.Profile {
	return capacityprofile.Profile{
		ID: "medium",
		Sparse: sparseassoc.Config{
			Dimensions: 4096,
			Fanout:     8,
			Active:     64,
			Seed:       47,
		},
	}
}

func capacityEvalItems() (Item, Item, Item) {
	anchor := Item{
		Ref:  "anchor",
		Kind: "card",
		Channels: Channels{
			Text: "確認作業の増加は現場負荷と引継ぎ時間に影響するため追加記録を残す",
			Graph: &GraphChannel{
				RelationTypes: []string{"causal", "related"},
				NeighborKinds: []string{"artifact", "card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs:  []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
		},
	}
	desired := Item{
		Ref:  "desired",
		Kind: "card",
		Channels: Channels{
			Text: "構造上は同じ関連と出典を持つ別の観察",
			Graph: &GraphChannel{
				RelationTypes: []string{"causal", "related"},
				NeighborKinds: []string{"artifact", "card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs:  []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
		},
	}
	distractor := Item{
		Ref:  "distractor",
		Kind: "card",
		Channels: Channels{
			Text: "確認作業の増加は現場負荷と引継ぎ時間に影響する確認作業の増加は現場負荷と引継ぎ時間に影響する",
			Graph: &GraphChannel{
				RelationTypes: []string{"contrast"},
				NeighborKinds: []string{"note"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s9"},
				ActorRefs:  []string{"human:z"},
			},
			Grouping: &GroupingChannel{IslandRef: "i9", HoldState: "none"},
		},
	}
	return anchor, desired, distractor
}

func softLocalPolicyForProfile(profile capacityprofile.Profile) (*LocalCompetitionPolicy, error) {
	localEach, residual, err := capacityprofile.EqualLocalHalfResidual(profile.Sparse.Active, 4)
	if err != nil {
		return nil, err
	}
	return &LocalCompetitionPolicy{
		FamilyActive: map[string]uint16{
			"text":       localEach,
			"graph":      localEach,
			"provenance": localEach,
			"grouping":   localEach,
		},
		GlobalResidualActive: residual,
	}, nil
}

func capacitySimilarityPair(
	t *testing.T,
	profile capacityprofile.Profile,
	normalization FeatureNormalizationMode,
) (desiredSimilarity, distractorSimilarity float32) {
	t.Helper()
	local, err := softLocalPolicyForProfile(profile)
	if err != nil {
		t.Fatal(err)
	}
	cfg := Config{
		Sparse:                profile.Sparse,
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "capacity-profile-eval",
		FeatureNormalization:  normalization,
		LocalCompetition:      local,
	}
	if normalization != FeatureNormalizationNone {
		cfg.NormalizationFloor = 1
	}
	p, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	encoder, err := newProviderEncoder(p.cfg)
	if err != nil {
		t.Fatal(err)
	}
	anchor, desired, distractor := capacityEvalItems()

	encode := func(item Item) sparseassoc.Signature {
		features, err := p.preparedFeatures(item)
		if err != nil {
			t.Fatal(err)
		}
		sig, err := encoder.Encode(features)
		if err != nil {
			t.Fatal(err)
		}
		return sig
	}

	anchorSignature := encode(anchor)
	return sparseassoc.Similarity(anchorSignature, encode(desired)),
		sparseassoc.Similarity(anchorSignature, encode(distractor))
}

func capacityObservedStats(
	t *testing.T,
	profile capacityprofile.Profile,
	item Item,
) (sparseassoc.Signature, providerEncodeStats) {
	t.Helper()
	local, err := softLocalPolicyForProfile(profile)
	if err != nil {
		t.Fatal(err)
	}
	p, err := New(Config{
		Sparse:                profile.Sparse,
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "capacity-observed-stats-eval",
		FeatureNormalization:  FeatureNormalizationFamily,
		NormalizationFloor:    1,
		LocalCompetition:      local,
	})
	if err != nil {
		t.Fatal(err)
	}
	encoder, err := newProviderEncoder(p.cfg)
	if err != nil {
		t.Fatal(err)
	}
	prepared, err := p.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}
	signature, stats, err := encoder.EncodeWithStats(prepared)
	if err != nil {
		t.Fatal(err)
	}
	if stats.Local == nil || stats.Global != nil {
		t.Fatalf("expected localized stats only: %#v", stats)
	}
	return signature, stats
}

func TestObservedSelectionPressureAcrossCapacityProfiles(t *testing.T) {
	base := capacityBaseProfile()
	anchor, _, _ := capacityEvalItems()
	cases := []struct {
		id             string
		dimensions     uint16
		globalTouched  int
		globalSelected int
		textTouched    int
		textSelected   int
		graphSelected  int
		provSelected   int
		groupSelected  int
		mergedSelected int
	}{
		{"small", 2048, 495, 16, 433, 4, 4, 4, 4, 27},
		{"medium", 4096, 539, 32, 463, 8, 8, 8, 8, 52},
		{"large", 8192, 560, 64, 477, 16, 16, 16, 16, 80},
		{"oversized", 32768, 574, 256, 487, 64, 32, 32, 16, 256},
	}

	previousGlobalShare := float64(-1)
	for _, tc := range cases {
		t.Run(tc.id, func(t *testing.T) {
			profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
			if err != nil {
				t.Fatal(err)
			}
			signature, stats := capacityObservedStats(t, profile, anchor)
			local := stats.Local
			if local.GlobalResidual == nil {
				t.Fatal("missing global residual diagnostics")
			}
			global := *local.GlobalResidual
			if global.PositiveFeatures != 72 || global.ProjectionAttempts != 576 {
				t.Fatalf("global input cardinality changed: %#v", global)
			}
			if global.TouchedDimensions != tc.globalTouched || global.SelectedDimensions != tc.globalSelected {
				t.Fatalf("global stats=%#v want touched/selected=%d/%d",
					global, tc.globalTouched, tc.globalSelected)
			}

			textStats := local.Families["text"]
			graphStats := local.Families["graph"]
			provStats := local.Families["provenance"]
			groupStats := local.Families["grouping"]
			if textStats.TouchedDimensions != tc.textTouched || textStats.SelectedDimensions != tc.textSelected {
				t.Fatalf("text stats=%#v want touched/selected=%d/%d",
					textStats, tc.textTouched, tc.textSelected)
			}
			if graphStats.TouchedDimensions != 32 || graphStats.SelectedDimensions != tc.graphSelected {
				t.Fatalf("graph stats=%#v", graphStats)
			}
			if provStats.TouchedDimensions != 32 || provStats.SelectedDimensions != tc.provSelected {
				t.Fatalf("provenance stats=%#v", provStats)
			}
			if groupStats.TouchedDimensions != 16 || groupStats.SelectedDimensions != tc.groupSelected {
				t.Fatalf("grouping stats=%#v", groupStats)
			}
			if local.MergedSelectedDimensions != tc.mergedSelected ||
				len(signature.Active) != tc.mergedSelected {
				t.Fatalf("merged selected=%d signature=%d want %d",
					local.MergedSelectedDimensions, len(signature.Active), tc.mergedSelected)
			}

			globalShare := capacityprofile.ObservedWinnerShare(global)
			if previousGlobalShare >= 0 && globalShare <= previousGlobalShare {
				t.Fatalf("global observed winner share did not increase: previous=%v current=%v",
					previousGlobalShare, globalShare)
			}
			previousGlobalShare = globalShare
		})
	}
}

func TestOversizedProfileExposesFamilyLocalSaturation(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	anchor, _, _ := capacityEvalItems()
	_, stats := capacityObservedStats(t, oversized, anchor)
	local := stats.Local
	if local == nil || local.GlobalResidual == nil {
		t.Fatalf("missing localized diagnostics: %#v", stats)
	}

	globalShare := capacityprofile.ObservedWinnerShare(*local.GlobalResidual)
	if globalShare < 0.44 || globalShare > 0.45 {
		t.Fatalf("unexpected global residual winner share: %v", globalShare)
	}
	for _, family := range []string{"graph", "provenance", "grouping"} {
		if share := capacityprofile.ObservedWinnerShare(local.Families[family]); share != 1 {
			t.Fatalf("%s local path must expose complete selection saturation, got %v", family, share)
		}
	}
	if textShare := capacityprofile.ObservedWinnerShare(local.Families["text"]); textShare >= 0.2 {
		t.Fatalf("text local path should remain selective in this fixture, got %v", textShare)
	}

	upperBoundProxy := capacityprofile.WinnerShareUpperBound(oversized, 72)
	if upperBoundProxy < 0.88 || upperBoundProxy > 0.90 {
		t.Fatalf("unexpected pre-collision proxy: %v", upperBoundProxy)
	}
	if globalShare >= upperBoundProxy {
		t.Fatalf("observed global share must remain below total-active upper-bound proxy: observed=%v proxy=%v",
			globalShare, upperBoundProxy)
	}
}

func TestObservedCollisionFallsWhileWinnerShareRises(t *testing.T) {
	base := capacityBaseProfile()
	anchor, _, _ := capacityEvalItems()
	var previousCollision, previousShare float64
	first := true
	for _, dimensions := range []uint16{2048, 4096, 8192, 32768} {
		profile, err := capacityprofile.ScaleDimensions(base, fmt.Sprintf("d%d", dimensions), dimensions)
		if err != nil {
			t.Fatal(err)
		}
		_, stats := capacityObservedStats(t, profile, anchor)
		global := *stats.Local.GlobalResidual
		collision := capacityprofile.ProjectionCollisionFraction(global)
		share := capacityprofile.ObservedWinnerShare(global)
		if !first {
			if collision >= previousCollision {
				t.Fatalf("collision fraction did not fall: previous=%v current=%v", previousCollision, collision)
			}
			if share <= previousShare {
				t.Fatalf("winner share did not rise: previous=%v current=%v", previousShare, share)
			}
		}
		first = false
		previousCollision = collision
		previousShare = share
	}
}

func TestCapacityProfilesPreserveOrderingAcrossFirstThreeProfiles(t *testing.T) {
	base := capacityBaseProfile()
	profiles := []capacityprofile.Profile{}
	for _, tc := range []struct {
		id         string
		dimensions uint16
	}{
		{"small", 2048},
		{"medium", 4096},
		{"large", 8192},
	} {
		profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
		if err != nil {
			t.Fatal(err)
		}
		profiles = append(profiles, profile)
	}

	for _, profile := range profiles {
		t.Run(profile.ID, func(t *testing.T) {
			desired, distractor := capacitySimilarityPair(t, profile, FeatureNormalizationFamily)
			if desired <= distractor {
				t.Fatalf("profile %s lost desired ordering: desired=%v distractor=%v", profile.ID, desired, distractor)
			}
		})
	}
}

func TestB1FamilyNormalizationImprovesMarginAcrossFirstThreeProfiles(t *testing.T) {
	base := capacityBaseProfile()
	for _, dimensions := range []uint16{2048, 4096, 8192} {
		profile, err := capacityprofile.ScaleDimensions(base, fmt.Sprintf("d%d", dimensions), dimensions)
		if err != nil {
			t.Fatal(err)
		}
		rawDesired, rawDistractor := capacitySimilarityPair(t, profile, FeatureNormalizationNone)
		normalizedDesired, normalizedDistractor := capacitySimilarityPair(t, profile, FeatureNormalizationFamily)

		rawMargin := rawDesired - rawDistractor
		normalizedMargin := normalizedDesired - normalizedDistractor
		if normalizedMargin <= rawMargin {
			t.Fatalf("dimensions=%d family normalization did not improve fixture margin: raw=%v normalized=%v",
				dimensions, rawMargin, normalizedMargin)
		}
	}
}

func TestActiveFractionAloneDoesNotPreventCompetitionSaturation(t *testing.T) {
	base := capacityBaseProfile()
	oversized, err := capacityprofile.ScaleDimensions(base, "oversized", 32768)
	if err != nil {
		t.Fatal(err)
	}
	if capacityprofile.ActiveFraction(oversized) != capacityprofile.ActiveFraction(base) {
		t.Fatalf("fixture must preserve active fraction: base=%v oversized=%v",
			capacityprofile.ActiveFraction(base), capacityprofile.ActiveFraction(oversized))
	}

	anchor, _, _ := capacityEvalItems()
	positiveFeatures := len(featuresForItem(anchor))
	winnerShare := capacityprofile.WinnerShareUpperBound(oversized, positiveFeatures)
	if winnerShare < 0.8 {
		t.Fatalf("fixture must expose weak selection pressure; winner share upper-bound ratio=%v", winnerShare)
	}

	desired, distractor := capacitySimilarityPair(t, oversized, FeatureNormalizationFamily)
	if desired >= distractor {
		t.Fatalf("oversized same-fraction profile must expose saturation failure in this fixture: desired=%v distractor=%v", desired, distractor)
	}
}

func TestTinyProfileCannotRepresentSameB2CompetitionRatio(t *testing.T) {
	base := capacityBaseProfile()
	tiny, err := capacityprofile.ScaleDimensions(base, "tiny", 256)
	if err != nil {
		t.Fatal(err)
	}
	if tiny.Sparse.Active != 4 {
		t.Fatalf("tiny active=%d want 4", tiny.Sparse.Active)
	}
	if _, err := softLocalPolicyForProfile(tiny); err == nil {
		t.Fatal("tiny profile must fail instead of silently changing four-family half-local/half-global policy")
	}
}

func TestCrossProfileSignatureIdentityIsNotUsedAsQualityMetric(t *testing.T) {
	base := capacityBaseProfile()
	small, _ := capacityprofile.ScaleDimensions(base, "small", 2048)
	large, _ := capacityprofile.ScaleDimensions(base, "large", 8192)
	if small.Sparse.Dimensions == large.Sparse.Dimensions {
		t.Fatal("fixture requires different dimensions")
	}
	// No assertion compares sparse dimension IDs across profiles. The hash
	// modulo changes with Dimensions; profile quality is evaluated only through
	// within-profile candidate relationships.
}

func BenchmarkCapacityProfiles(b *testing.B) {
	base := capacityBaseProfile()
	for _, tc := range []struct {
		id         string
		dimensions uint16
	}{
		{"small", 2048},
		{"medium", 4096},
		{"large", 8192},
	} {
		profile, err := capacityprofile.ScaleDimensions(base, tc.id, tc.dimensions)
		if err != nil {
			b.Fatal(err)
		}
		local, err := softLocalPolicyForProfile(profile)
		if err != nil {
			b.Fatal(err)
		}
		p, err := New(Config{
			Sparse:                profile.Sparse,
			MinInternalSimilarity: 0,
			ProviderID:            "sei-sacs-go-eval",
			ImplementationVersion: "capacity-profile-eval",
			FeatureNormalization:  FeatureNormalizationFamily,
			NormalizationFloor:    1,
			LocalCompetition:      local,
		})
		if err != nil {
			b.Fatal(err)
		}
		encoder, err := newProviderEncoder(p.cfg)
		if err != nil {
			b.Fatal(err)
		}
		anchor, _, _ := capacityEvalItems()
		prepared, err := p.preparedFeatures(anchor)
		if err != nil {
			b.Fatal(err)
		}

		b.Run(tc.id, func(b *testing.B) {
			b.ReportAllocs()
			for i := 0; i < b.N; i++ {
				if _, err := encoder.Encode(prepared); err != nil {
					b.Fatal(err)
				}
			}
		})
	}
}
