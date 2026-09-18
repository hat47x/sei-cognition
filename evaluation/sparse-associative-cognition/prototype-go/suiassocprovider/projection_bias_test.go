package suiassocprovider

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func TestProjectionBiasPolicyFailsClosed(t *testing.T) {
	base := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
	}
	validRule := ProjectionBiasRule{
		Channel:       "graph:relationType",
		Key:           "critical",
		Multiplier:    1.01,
		ProvenanceRef: "policy:test",
	}
	cases := []*ProjectionBiasPolicy{
		{PolicyID: "", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{validRule}},
		{PolicyID: "p", MaxMultiplier: 1, Rules: []ProjectionBiasRule{validRule}},
		{PolicyID: "p", MaxMultiplier: MaxProjectionBiasMultiplier + 0.01, Rules: []ProjectionBiasRule{validRule}},
		{PolicyID: "p", MaxMultiplier: 1.25},
		{PolicyID: "p", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{{Key: "critical", Multiplier: 1.01, ProvenanceRef: "p"}}},
		{PolicyID: "p", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{{Channel: "graph:relationType", Multiplier: 1.01, ProvenanceRef: "p"}}},
		{PolicyID: "p", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{{Channel: "graph:relationType", Key: "critical", Multiplier: 1, ProvenanceRef: "p"}}},
		{PolicyID: "p", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{{Channel: "graph:relationType", Key: "critical", Multiplier: 1.5, ProvenanceRef: "p"}}},
		{PolicyID: "p", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{{Channel: "graph:relationType", Key: "critical", Multiplier: 1.01}}},
		{PolicyID: "p", MaxMultiplier: 1.25, Rules: []ProjectionBiasRule{validRule, validRule}},
	}
	for i, policy := range cases {
		cfg := base
		cfg.ProjectionBias = policy
		if _, err := New(cfg); err == nil {
			t.Fatalf("case %d must fail closed: %#v", i, policy)
		}
	}

	tooMany := make([]ProjectionBiasRule, MaxProjectionBiasRules+1)
	for i := range tooMany {
		tooMany[i] = ProjectionBiasRule{
			Channel:       "graph:relationType",
			Key:           fmt.Sprintf("critical-%02d", i),
			Multiplier:    1.01,
			ProvenanceRef: "policy:test",
		}
	}
	cfg := base
	cfg.ProjectionBias = &ProjectionBiasPolicy{
		PolicyID:      "p",
		MaxMultiplier: 1.25,
		Rules:         tooMany,
	}
	if _, err := New(cfg); err == nil {
		t.Fatal("too many projection bias rules must fail closed")
	}
}

func TestProviderClonesProjectionBiasPolicy(t *testing.T) {
	policy := projectionBiasCriticalPolicy(1.01)
	p, err := New(Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		ProjectionBias:        policy,
	})
	if err != nil {
		t.Fatal(err)
	}
	policy.PolicyID = "mutated"
	policy.Rules[0].Multiplier = 2
	if p.cfg.ProjectionBias.PolicyID != "b3-critical" {
		t.Fatalf("provider retained caller-mutated policy id: %#v", p.cfg.ProjectionBias)
	}
	if p.cfg.ProjectionBias.Rules[0].Multiplier != 1.01 {
		t.Fatalf("provider retained caller-mutated rule: %#v", p.cfg.ProjectionBias.Rules[0])
	}
	if got := p.projectionBiasMultipliers["graph:relationType\x00critical"]; got != 1.01 {
		t.Fatalf("compiled lookup changed after caller mutation: %v", got)
	}
}

func TestProjectionBiasPreservesFeatureIdentityAndInput(t *testing.T) {
	input := []sparseassoc.Feature{
		{Channel: "graph:relationType", Key: "critical", Weight: 1},
		{Channel: "text", Key: "ab", Weight: 1},
	}
	before := append([]sparseassoc.Feature(nil), input...)
	got := applyProjectionBias(input, map[string]float32{
		"graph:relationType\x00critical": 1.01,
	})
	if !reflect.DeepEqual(input, before) {
		t.Fatalf("input mutated: before=%#v after=%#v", before, input)
	}
	for i := range input {
		if got[i].Channel != input[i].Channel || got[i].Key != input[i].Key {
			t.Fatalf("feature identity changed at %d: input=%#v got=%#v", i, input[i], got[i])
		}
	}
	if got[0].Weight != 1.01 || got[1].Weight != 1 {
		t.Fatalf("unexpected biased weights: %#v", got)
	}
}

func TestProjectionBiasIsExplicitOptIn(t *testing.T) {
	item := projectionBiasAnchor()
	cfg := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
	}
	p, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	raw := featuresForItem(item)
	prepared, err := p.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(raw, prepared) {
		t.Fatal("default provider must keep current unbiased feature projection")
	}
}

func TestRareCriticalProjectionBiasCanRecoverCandidate(t *testing.T) {
	anchor, desired, distractor := projectionBiasCriticalFixture()

	baseDesired, baseDistractor := projectionBiasSimilarities(t, nil, FeatureNormalizationNone, nil, anchor, desired, distractor)
	if baseDesired >= baseDistractor {
		t.Fatalf("fixture must expose baseline text domination: desired=%v distractor=%v", baseDesired, baseDistractor)
	}

	bias := projectionBiasCriticalPolicy(1.01)
	biasedDesired, biasedDistractor := projectionBiasSimilarities(t, bias, FeatureNormalizationNone, nil, anchor, desired, distractor)
	if biasedDesired <= biasedDistractor {
		t.Fatalf("rare critical prior should recover desired candidate: desired=%v distractor=%v", biasedDesired, biasedDistractor)
	}
}

func TestCommonProjectionBiasCanReverseCorrectOrdering(t *testing.T) {
	anchor, desired, distractor := projectionBiasCommonFailureFixture()

	baseDesired, baseDistractor := projectionBiasSimilarities(t, nil, FeatureNormalizationNone, nil, anchor, desired, distractor)
	if baseDesired <= baseDistractor {
		t.Fatalf("fixture baseline must prefer broad-evidence candidate: desired=%v distractor=%v", baseDesired, baseDistractor)
	}

	bias := &ProjectionBiasPolicy{
		PolicyID:      "b3-common-failure",
		MaxMultiplier: 1.25,
		Rules: []ProjectionBiasRule{{
			Channel:       "graph:neighborKind",
			Key:           "artifact",
			Multiplier:    1.01,
			ProvenanceRef: "fixture:common-neighbor",
		}},
	}
	biasedDesired, biasedDistractor := projectionBiasSimilarities(t, bias, FeatureNormalizationNone, nil, anchor, desired, distractor)
	if biasedDesired >= biasedDistractor {
		t.Fatalf("fixture must expose harmful common-feature prior: desired=%v distractor=%v", biasedDesired, biasedDistractor)
	}
}

func TestTinyProjectionBiasCanCauseKWTADiscontinuity(t *testing.T) {
	anchor := projectionBiasAnchor()
	cfg := sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47}
	encoder, err := sparseassoc.NewEncoder(cfg)
	if err != nil {
		t.Fatal(err)
	}
	raw := encoder.Encode(featuresForItem(anchor))
	biased := encoder.Encode(applyProjectionBias(featuresForItem(anchor), compileProjectionBias(projectionBiasCriticalPolicy(1.01))))
	if similarity := sparseassoc.Similarity(raw, biased); similarity >= 0.75 {
		t.Fatalf("1.01 prior did not expose expected discrete winner change: signature similarity=%v", similarity)
	}
}

func TestFamilyNormalizationKeepsMassBoundedWhilePreservingRelativePrior(t *testing.T) {
	cfg := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		ProjectionBias:        projectionBiasCriticalPolicy(1.01),
		FeatureNormalization:  FeatureNormalizationFamily,
		NormalizationFloor:    1,
	}
	p, err := New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	prepared, err := p.preparedFeatures(projectionBiasAnchor())
	if err != nil {
		t.Fatal(err)
	}
	var graphTotal, criticalWeight, ordinaryWeight float32
	for _, feature := range prepared {
		if featureFamily(feature.Channel) != "graph" {
			continue
		}
		graphTotal += feature.Weight
		switch feature.Key {
		case "critical":
			criticalWeight = feature.Weight
		case "r1":
			ordinaryWeight = feature.Weight
		}
	}
	if graphTotal < 0.9999 || graphTotal > 1.0001 {
		t.Fatalf("family normalization did not bound graph mass: %v", graphTotal)
	}
	if criticalWeight <= ordinaryWeight {
		t.Fatalf("relative prior vanished inside normalized family: critical=%v ordinary=%v", criticalWeight, ordinaryWeight)
	}
}

func TestProjectionBiasInteractsWithSoftLocalizedCompetition(t *testing.T) {
	anchor, desired, distractor := projectionBiasCriticalFixture()
	soft := softLocalCompetitionPolicy()

	baseDesired, baseDistractor := projectionBiasSimilarities(t, nil, FeatureNormalizationNone, &soft, anchor, desired, distractor)
	if baseDesired >= baseDistractor {
		t.Fatalf("soft-local baseline fixture must still prefer text distractor: desired=%v distractor=%v", baseDesired, baseDistractor)
	}

	biasedDesired, biasedDistractor := projectionBiasSimilarities(t, projectionBiasCriticalPolicy(1.01), FeatureNormalizationNone, &soft, anchor, desired, distractor)
	if biasedDesired <= biasedDistractor {
		t.Fatalf("prior should remain effective through local+global competition: desired=%v distractor=%v", biasedDesired, biasedDistractor)
	}
}

func BenchmarkPreparedFeaturesProjectionBias(b *testing.B) {
	p, err := New(Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		ProjectionBias:        projectionBiasCriticalPolicy(1.01),
	})
	if err != nil {
		b.Fatal(err)
	}
	item := projectionBiasAnchor()
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		if _, err := p.preparedFeatures(item); err != nil {
			b.Fatal(err)
		}
	}
}

func projectionBiasCriticalPolicy(multiplier float32) *ProjectionBiasPolicy {
	return &ProjectionBiasPolicy{
		PolicyID:      "b3-critical",
		MaxMultiplier: 1.25,
		Rules: []ProjectionBiasRule{
			{
				Channel:       "graph:relationType",
				Key:           "critical",
				Multiplier:    multiplier,
				ProvenanceRef: "fixture:critical-1",
			},
			{
				Channel:       "graph:relationType",
				Key:           "critical2",
				Multiplier:    multiplier,
				ProvenanceRef: "fixture:critical-2",
			},
		},
	}
}

func projectionBiasAnchor() Item {
	return Item{
		Ref:  "anchor",
		Kind: "card",
		Channels: Channels{
			Text: "abcdefghijklmnopqrstuvwx",
			Graph: &GraphChannel{
				RelationTypes: []string{"critical", "critical2", "r1", "r2"},
				NeighborKinds: []string{"card"},
			},
			Provenance: &ProvenanceChannel{SourceRefs: []string{"s1"}},
		},
	}
}

func projectionBiasCriticalFixture() (Item, Item, Item) {
	return projectionBiasAnchor(),
		Item{
			Ref:  "desired",
			Kind: "card",
			Channels: Channels{
				Text: "zyxwvutsrqponmlkjihgfedc",
				Graph: &GraphChannel{
					RelationTypes: []string{"critical", "critical2"},
					NeighborKinds: []string{"artifact"},
				},
				Provenance: &ProvenanceChannel{SourceRefs: []string{"s2"}},
			},
		},
		Item{
			Ref:  "distractor",
			Kind: "card",
			Channels: Channels{
				Text: "abcdefghijklmnopqrstuvwx",
				Graph: &GraphChannel{
					RelationTypes: []string{"other"},
					NeighborKinds: []string{"note"},
				},
				Provenance: &ProvenanceChannel{SourceRefs: []string{"s9"}},
			},
		}
}

func projectionBiasCommonFailureFixture() (Item, Item, Item) {
	return Item{
			Ref:  "anchor",
			Kind: "card",
			Channels: Channels{
				Text: "abcdefghijklmnopqrstuvwx",
				Graph: &GraphChannel{
					RelationTypes: []string{"r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"},
					NeighborKinds: []string{"artifact", "card"},
				},
				Provenance: &ProvenanceChannel{
					SourceRefs: []string{"s0", "s1", "s2", "s3"},
					ActorRefs:  []string{"a0", "a1"},
				},
				Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
			},
		},
		Item{
			Ref:  "desired",
			Kind: "card",
			Channels: Channels{
				Text: "abcdefghijklmnollfzvooct",
				Graph: &GraphChannel{
					RelationTypes: []string{"r0", "r1", "r4", "r5", "r6", "xrel15"},
				},
				Provenance: &ProvenanceChannel{
					SourceRefs: []string{"s0", "s2"},
					ActorRefs:  []string{"a1"},
				},
				Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "none"},
			},
		},
		Item{
			Ref:  "distractor",
			Kind: "card",
			Channels: Channels{
				Text: "abcdeqfsdurrhlfqpnuefxrx",
				Graph: &GraphChannel{
					NeighborKinds: []string{"artifact"},
				},
				Provenance: &ProvenanceChannel{
					ActorRefs: []string{"a0", "a1"},
				},
				Grouping: &GroupingChannel{IslandRef: "i1", HoldState: "hold"},
			},
		}
}

func projectionBiasSimilarities(
	t *testing.T,
	bias *ProjectionBiasPolicy,
	normalization FeatureNormalizationMode,
	local *LocalCompetitionPolicy,
	anchor Item,
	desired Item,
	distractor Item,
) (float32, float32) {
	t.Helper()
	cfg := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		ProjectionBias:        bias,
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
	anchorSig := encode(anchor)
	return sparseassoc.Similarity(anchorSig, encode(desired)),
		sparseassoc.Similarity(anchorSig, encode(distractor))
}
