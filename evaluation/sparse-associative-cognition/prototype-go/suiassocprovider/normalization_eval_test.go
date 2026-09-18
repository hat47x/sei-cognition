package suiassocprovider

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func TestFeatureFamilyMappingStaysCallerOwned(t *testing.T) {
	cases := map[string]string{
		"kind":                   "kind",
		"text":                   "text",
		"graph:relationType":     "graph",
		"graph:neighborKind":     "graph",
		"provenance:source":      "provenance",
		"provenance:actor":       "provenance",
		"grouping:island":        "grouping",
		"grouping:hold":          "grouping",
		"future:caller-specific": "future:caller-specific",
	}
	for channel, want := range cases {
		if got := featureFamily(channel); got != want {
			t.Fatalf("featureFamily(%q)=%q want %q", channel, got, want)
		}
	}
}

func TestFamilyNormalizationPreservesFeatureIdentity(t *testing.T) {
	item := Item{
		Ref:  "c1",
		Kind: "card",
		Channels: Channels{
			Text: "確認作業が増えた",
			Graph: &GraphChannel{
				RelationTypes: []string{"related"},
				NeighborKinds: []string{"card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1"},
				ActorRefs:  []string{"human:a"},
			},
			Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
		},
	}
	raw := featuresForItem(item)
	got := normalizeFeaturesByFamily(raw, 1)
	if len(got) != len(raw) {
		t.Fatalf("feature count changed: %d != %d", len(got), len(raw))
	}
	for i := range raw {
		if got[i].Channel != raw[i].Channel || got[i].Key != raw[i].Key {
			t.Fatalf("feature identity changed at %d: raw=%#v got=%#v", i, raw[i], got[i])
		}
	}
}

func TestFamilyNormalizationBoundsFamilyMass(t *testing.T) {
	item := Item{
		Ref:  "c1",
		Kind: "card",
		Channels: Channels{
			Text: "確認作業の増加は引継ぎ時間と現場負荷に影響している",
			Graph: &GraphChannel{
				RelationTypes: []string{"related", "causal"},
				NeighborKinds: []string{"card", "artifact"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1", "s2"},
				ActorRefs:  []string{"human:a", "ai:b"},
			},
			Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
		},
	}
	normalized := normalizeFeaturesByFamily(featuresForItem(item), 1)
	totals := map[string]float32{}
	for _, feature := range normalized {
		if feature.Weight > 0 && feature.Key != "" {
			totals[featureFamily(feature.Channel)] += feature.Weight
		}
	}
	for _, family := range []string{"kind", "text", "graph", "provenance", "grouping"} {
		got := totals[family]
		if got < 0.9999 || got > 1.0001 {
			t.Fatalf("family %q total=%v want approximately 1", family, got)
		}
	}
}

func TestExactChannelCanOverweightSplitStructuralFamily(t *testing.T) {
	item := Item{
		Ref:  "c1",
		Kind: "card",
		Channels: Channels{
			Graph: &GraphChannel{
				RelationTypes: []string{"related"},
				NeighborKinds: []string{"card"},
			},
			Provenance: &ProvenanceChannel{
				SourceRefs: []string{"s1"},
				ActorRefs:  []string{"human:a"},
			},
		},
	}
	raw := featuresForItem(item)
	exact, err := sparseassoc.NormalizeFeatures(raw, sparseassoc.NormalizationConfig{
		Mode:             sparseassoc.NormalizationPerChannel,
		DenominatorFloor: 1,
	})
	if err != nil {
		t.Fatal(err)
	}
	family := normalizeFeaturesByFamily(raw, 1)

	exactTotals := familyTotals(exact)
	familyTotals := familyTotals(family)
	if exactTotals["graph"] != 2 {
		t.Fatalf("exact-channel graph mass=%v want 2", exactTotals["graph"])
	}
	if familyTotals["graph"] != 1 {
		t.Fatalf("family-normalized graph mass=%v want 1", familyTotals["graph"])
	}
	if exactTotals["provenance"] != 2 {
		t.Fatalf("exact-channel provenance mass=%v want 2", exactTotals["provenance"])
	}
	if familyTotals["provenance"] != 1 {
		t.Fatalf("family-normalized provenance mass=%v want 1", familyTotals["provenance"])
	}
}

func TestPreparedFeaturesModesKeepBaselineOptIn(t *testing.T) {
	item := baseRequest().Items[0]
	baseCfg := Config{
		Sparse: sparseassoc.Config{Dimensions: 4096, Fanout: 8, Active: 64, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "normalization-eval",
	}
	pNone, err := New(baseCfg)
	if err != nil {
		t.Fatal(err)
	}
	raw := featuresForItem(item)
	none, err := pNone.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(raw, none) {
		t.Fatal("default provider must preserve current unnormalized feature projection")
	}

	exactCfg := baseCfg
	exactCfg.FeatureNormalization = FeatureNormalizationExactChannel
	exactCfg.NormalizationFloor = 1
	pExact, err := New(exactCfg)
	if err != nil {
		t.Fatal(err)
	}
	exact, err := pExact.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}
	if reflect.DeepEqual(raw, exact) {
		t.Fatal("exact-channel normalization should reweight this fixture")
	}

	familyCfg := baseCfg
	familyCfg.FeatureNormalization = FeatureNormalizationFamily
	familyCfg.NormalizationFloor = 1
	pFamily, err := New(familyCfg)
	if err != nil {
		t.Fatal(err)
	}
	family, err := pFamily.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}
	if reflect.DeepEqual(raw, family) {
		t.Fatal("family normalization should reweight this fixture")
	}
}

func TestNormalizationConfigFailsClosed(t *testing.T) {
	base := Config{
		Sparse:                sparseassoc.Config{Dimensions: 4096, Fanout: 8, Active: 64, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "normalization-eval",
	}
	for _, mode := range []FeatureNormalizationMode{
		FeatureNormalizationExactChannel,
		FeatureNormalizationFamily,
	} {
		cfg := base
		cfg.FeatureNormalization = mode
		if _, err := New(cfg); err == nil {
			t.Fatalf("mode %v must require positive normalization floor", mode)
		}
	}
	cfg := base
	cfg.FeatureNormalization = FeatureNormalizationMode(255)
	if _, err := New(cfg); err == nil {
		t.Fatal("unknown normalization mode must fail closed")
	}
}

func familyTotals(features []sparseassoc.Feature) map[string]float32 {
	totals := map[string]float32{}
	for _, feature := range features {
		if feature.Weight > 0 && feature.Key != "" {
			totals[featureFamily(feature.Channel)] += feature.Weight
		}
	}
	return totals
}


func TestNormalizationModesOnTextCardinalityFixture(t *testing.T) {
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

	noneDesired, noneDistractor := fixtureSimilarities(t, FeatureNormalizationNone, 16, anchor, desired, distractor)
	if noneDesired >= noneDistractor {
		t.Fatalf("fixture must expose text-cardinality domination without normalization: desired=%v distractor=%v", noneDesired, noneDistractor)
	}

	exactDesired, exactDistractor := fixtureSimilarities(t, FeatureNormalizationExactChannel, 16, anchor, desired, distractor)
	if exactDesired <= exactDistractor {
		t.Fatalf("exact-channel normalization should recover structural candidate in this fixture: desired=%v distractor=%v", exactDesired, exactDistractor)
	}

	familyDesired, familyDistractor := fixtureSimilarities(t, FeatureNormalizationFamily, 16, anchor, desired, distractor)
	if familyDesired <= familyDistractor {
		t.Fatalf("family normalization should recover structural candidate in this fixture: desired=%v distractor=%v", familyDesired, familyDistractor)
	}
}

func TestFamilyNormalizationAvoidsExactChannelSingletonOvercorrection(t *testing.T) {
	anchor := Item{
		Ref:  "anchor",
		Kind: "card",
		Channels: Channels{
			Text: "abcdefghijk",
			Graph: &GraphChannel{
				RelationTypes: []string{"rel0", "rel1", "rel2", "rel3", "rel4", "rel5", "rel6", "rel7"},
				NeighborKinds: []string{"artifact"},
			},
		},
	}
	desired := Item{
		Ref:  "desired",
		Kind: "card",
		Channels: Channels{
			Text: "lmnopqrstuv",
			Graph: &GraphChannel{
				RelationTypes: []string{"rel0", "rel1", "rel2"},
				NeighborKinds: []string{"other"},
			},
		},
	}
	distractor := Item{
		Ref:  "distractor",
		Kind: "card",
		Channels: Channels{
			Text: "wxyz0123456",
			Graph: &GraphChannel{
				RelationTypes: []string{"otherrel"},
				NeighborKinds: []string{"artifact"},
			},
		},
	}

	noneDesired, noneDistractor := fixtureSimilarities(t, FeatureNormalizationNone, 10, anchor, desired, distractor)
	if noneDesired <= noneDistractor {
		t.Fatalf("baseline fixture should prefer the multi-relation candidate: desired=%v distractor=%v", noneDesired, noneDistractor)
	}

	exactDesired, exactDistractor := fixtureSimilarities(t, FeatureNormalizationExactChannel, 10, anchor, desired, distractor)
	if exactDesired >= exactDistractor {
		t.Fatalf("exact-channel normalization should expose singleton-subchannel overcorrection: desired=%v distractor=%v", exactDesired, exactDistractor)
	}

	familyDesired, familyDistractor := fixtureSimilarities(t, FeatureNormalizationFamily, 10, anchor, desired, distractor)
	if familyDesired <= familyDistractor {
		t.Fatalf("feature-family normalization should avoid the exact-channel reversal: desired=%v distractor=%v", familyDesired, familyDistractor)
	}
}

func BenchmarkPreparedFeaturesFamily(b *testing.B) {
	p, err := New(Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "normalization-eval",
		FeatureNormalization:  FeatureNormalizationFamily,
		NormalizationFloor:    1,
	})
	if err != nil {
		b.Fatal(err)
	}
	item := baseRequest().Items[0]
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		if _, err := p.preparedFeatures(item); err != nil {
			b.Fatal(err)
		}
	}
}

func fixtureSimilarities(
	t *testing.T,
	mode FeatureNormalizationMode,
	active uint16,
	anchor Item,
	desired Item,
	distractor Item,
) (float32, float32) {
	t.Helper()
	cfg := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: active, Seed: 47},
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "normalization-eval",
		FeatureNormalization:  mode,
	}
	if mode != FeatureNormalizationNone {
		cfg.NormalizationFloor = 1
	}
	p, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	encoder, err := sparseassoc.NewEncoder(cfg.Sparse)
	if err != nil {
		t.Fatal(err)
	}
	anchorFeatures, err := p.preparedFeatures(anchor)
	if err != nil {
		t.Fatal(err)
	}
	desiredFeatures, err := p.preparedFeatures(desired)
	if err != nil {
		t.Fatal(err)
	}
	distractorFeatures, err := p.preparedFeatures(distractor)
	if err != nil {
		t.Fatal(err)
	}
	anchorSignature := encoder.Encode(anchorFeatures)
	return sparseassoc.Similarity(anchorSignature, encoder.Encode(desiredFeatures)),
		sparseassoc.Similarity(anchorSignature, encoder.Encode(distractorFeatures))
}
