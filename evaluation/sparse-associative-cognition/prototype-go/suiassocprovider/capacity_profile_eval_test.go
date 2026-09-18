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
