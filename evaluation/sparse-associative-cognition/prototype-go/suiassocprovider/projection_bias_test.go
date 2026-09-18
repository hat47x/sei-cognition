package suiassocprovider

import (
	"math"
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
		Channel:       "provenance:source",
		Key:           "critical:s1",
		Multiplier:    2,
		ProvenanceRef: "policy-source:critical-v1",
	}
	cases := []*ProjectionBiasPolicy{
		{},
		{PolicyRef: "policy:b3", MaxMultiplier: 1, Rules: []ProjectionBiasRule{validRule}},
		{PolicyRef: "policy:b3", MaxMultiplier: MaxProjectionBiasMultiplier + 1, Rules: []ProjectionBiasRule{validRule}},
		{PolicyRef: "policy:b3", MaxMultiplier: 2},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Key: "critical:s1", Multiplier: 2, ProvenanceRef: "policy-source:critical-v1",
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: "provenance:source", Multiplier: 2, ProvenanceRef: "policy-source:critical-v1",
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: "provenance:source", Key: "critical:s1", Multiplier: 2,
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: "provenance:source", Key: "critical:s1", Multiplier: 1,
				ProvenanceRef: "policy-source:critical-v1",
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: "provenance:source", Key: "critical:s1", Multiplier: 3,
				ProvenanceRef: "policy-source:critical-v1",
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules:         []ProjectionBiasRule{validRule, validRule},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: float32(math.NaN()),
			Rules:         []ProjectionBiasRule{validRule},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: float32(math.Inf(1)),
			Rules:         []ProjectionBiasRule{validRule},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: "provenance:source", Key: "critical:s1",
				Multiplier: float32(math.NaN()), ProvenanceRef: "policy-source:critical-v1",
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: " provenance:source", Key: "critical:s1", Multiplier: 2,
				ProvenanceRef: "policy-source:critical-v1",
			}},
		},
		{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel: "provenance:source", Key: "critical:s1 ", Multiplier: 2,
				ProvenanceRef: "policy-source:critical-v1",
			}},
		},
	}
	for i, policy := range cases {
		cfg := base
		cfg.ProjectionBias = policy
		if _, err := New(cfg); err == nil {
			t.Fatalf("case %d must fail closed: %#v", i, policy)
		}
	}
}

func TestProviderClonesProjectionBiasPolicy(t *testing.T) {
	policy := &ProjectionBiasPolicy{
		PolicyRef:     "policy:b3",
		MaxMultiplier: 2,
		Rules: []ProjectionBiasRule{{
			Channel:       "provenance:source",
			Key:           "critical:s1",
			Multiplier:    2,
			ProvenanceRef: "policy-source:critical-v1",
		}},
	}
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

	policy.PolicyRef = "mutated"
	policy.MaxMultiplier = 4
	policy.Rules[0].Multiplier = 4
	if p.cfg.ProjectionBias.PolicyRef != "policy:b3" ||
		p.cfg.ProjectionBias.MaxMultiplier != 2 ||
		p.cfg.ProjectionBias.Rules[0].Multiplier != 2 {
		t.Fatalf("provider retained caller-mutated policy: %#v", p.cfg.ProjectionBias)
	}
	selector := projectionBiasSelector{channel: "provenance:source", key: "critical:s1"}
	if p.projectionBias[selector] != 2 {
		t.Fatalf("compiled projection bias changed after caller mutation: %#v", p.projectionBias)
	}
}

func TestProjectionBiasAppliesAfterFamilyNormalizationAndOnlyToExactSelector(t *testing.T) {
	p, err := New(Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		FeatureNormalization:  FeatureNormalizationFamily,
		NormalizationFloor:    1,
		LocalCompetition: &LocalCompetitionPolicy{
			FamilyActive:         map[string]uint16{"provenance": 2},
			GlobalResidualActive: 4,
		},
		ProjectionBias: &ProjectionBiasPolicy{
			PolicyRef:     "policy:b3",
			MaxMultiplier: 2,
			Rules: []ProjectionBiasRule{{
				Channel:       "provenance:source",
				Key:           "critical:s1",
				Multiplier:    2,
				ProvenanceRef: "policy-source:critical-v1",
			}},
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	item := Item{
		Ref:  "item",
		Kind: "card",
		Channels: Channels{
			Provenance: &ProvenanceChannel{SourceRefs: []string{"critical:s1", "ordinary:s2"}},
		},
	}
	features, err := p.preparedFeatures(item)
	if err != nil {
		t.Fatal(err)
	}

	weights := map[string]float32{}
	for _, feature := range features {
		if feature.Channel == "provenance:source" {
			weights[feature.Key] = feature.Weight
		}
	}
	if weights["critical:s1"] != 1 {
		t.Fatalf("critical feature weight=%v want 1 after 0.5 normalization * 2 bias", weights["critical:s1"])
	}
	if weights["ordinary:s2"] != 0.5 {
		t.Fatalf("ordinary feature weight=%v want 0.5", weights["ordinary:s2"])
	}

	encoder, err := newProviderEncoder(p.cfg)
	if err != nil {
		t.Fatal(err)
	}
	sig, err := encoder.Encode(features)
	if err != nil {
		t.Fatal(err)
	}
	if len(sig.Active) > int(p.cfg.Sparse.Active) {
		t.Fatalf("projection bias exceeded sparse active capacity: %d > %d", len(sig.Active), p.cfg.Sparse.Active)
	}
}

func TestProjectionBiasRecoversRareCriticalFeatureFixture(t *testing.T) {
	anchor, desired, distractor, _ := projectionBiasFixtureItems()

	baseDesired, baseDistractor := projectionBiasSimilarities(t, nil, anchor, desired, distractor)
	if baseDesired >= baseDistractor {
		t.Fatalf("fixture must lose rare critical evidence under uniform projection: desired=%v distractor=%v", baseDesired, baseDistractor)
	}

	policy := rareCriticalProjectionBiasPolicy()
	biasedDesired, biasedDistractor := projectionBiasSimilarities(t, &policy, anchor, desired, distractor)
	if biasedDesired <= biasedDistractor {
		t.Fatalf("bounded exact-feature bias should recover rare critical candidate: desired=%v distractor=%v", biasedDesired, biasedDistractor)
	}
}

func TestProjectionBiasCommonFeatureCanInflateUnrelatedSimilarity(t *testing.T) {
	anchor, _, _, unrelated := projectionBiasFixtureItems()

	base, _ := projectionBiasPairSimilarity(t, nil, anchor, unrelated)
	policy := ProjectionBiasPolicy{
		PolicyRef:     "policy:b3-common-noise-negative-control",
		MaxMultiplier: 2,
		Rules: []ProjectionBiasRule{{
			Channel:       "kind",
			Key:           "card",
			Multiplier:    2,
			ProvenanceRef: "negative-control:common-kind",
		}},
	}
	biased, _ := projectionBiasPairSimilarity(t, &policy, anchor, unrelated)
	if biased <= base {
		t.Fatalf("negative control must expose common-feature false activation risk: base=%v biased=%v", base, biased)
	}
}

func TestProjectionBiasPreservesAbstentionWithoutSharedBiasedFeature(t *testing.T) {
	anchor, _, _, unrelated := projectionBiasFixtureItems()
	policy := rareCriticalProjectionBiasPolicy()
	p, err := New(Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.2,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		ProjectionBias:        &policy,
	})
	if err != nil {
		t.Fatal(err)
	}
	resp, err := p.Handle(Request{
		Schema:     RequestSchema,
		RequestID:  "b3-abstain",
		NetworkID:  "synthetic",
		Intent:     "neighborhood",
		AnchorRefs: []string{anchor.Ref},
		Items:      []Item{anchor, unrelated},
		Policy:     Policy{CandidateLimit: 1},
	})
	if err != nil {
		t.Fatal(err)
	}
	if resp.Outcome != "abstain" || resp.NoveltyCue != "abstain" || len(resp.CandidateRefs) != 0 {
		t.Fatalf("unexpected response for non-shared biased feature: %#v", resp)
	}
}

func BenchmarkProjectionBiasPreparedFeatures(b *testing.B) {
	anchor, _, _, _ := projectionBiasFixtureItems()
	base := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
	}
	policy := rareCriticalProjectionBiasPolicy()

	b.Run("uniform", func(b *testing.B) {
		p, err := New(base)
		if err != nil {
			b.Fatal(err)
		}
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			if _, err := p.preparedFeatures(anchor); err != nil {
				b.Fatal(err)
			}
		}
	})
	b.Run("biased", func(b *testing.B) {
		cfg := base
		cfg.ProjectionBias = &policy
		p, err := New(cfg)
		if err != nil {
			b.Fatal(err)
		}
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			if _, err := p.preparedFeatures(anchor); err != nil {
				b.Fatal(err)
			}
		}
	})
}

func rareCriticalProjectionBiasPolicy() ProjectionBiasPolicy {
	return ProjectionBiasPolicy{
		PolicyRef:     "policy:b3-rare-critical",
		MaxMultiplier: 2,
		Rules: []ProjectionBiasRule{{
			Channel:       "provenance:source",
			Key:           "critical:s1",
			Multiplier:    2,
			ProvenanceRef: "policy-source:critical-v1",
		}},
	}
}

func projectionBiasFixtureItems() (Item, Item, Item, Item) {
	anchor := Item{
		Ref:  "anchor",
		Kind: "card",
		Channels: Channels{
			Text: "abcdefghijklmnopqrstuvwx",
			Graph: &GraphChannel{
				RelationTypes: []string{"r0", "r1"},
				NeighborKinds: []string{"card"},
			},
			Provenance: &ProvenanceChannel{SourceRefs: []string{"critical:s1"}},
		},
	}
	desired := Item{
		Ref:  "desired",
		Kind: "card",
		Channels: Channels{
			Text: "zyxwvutsrqponmlkjihgfedc",
			Graph: &GraphChannel{
				RelationTypes: []string{"x0"},
				NeighborKinds: []string{"artifact"},
			},
			Provenance: &ProvenanceChannel{SourceRefs: []string{"critical:s1"}},
		},
	}
	distractor := Item{
		Ref:  "distractor",
		Kind: "card",
		Channels: Channels{
			Text: "abcdefghxxzzzzzzzzzzzzzzzz",
			Graph: &GraphChannel{
				RelationTypes: []string{"r9"},
				NeighborKinds: []string{"note"},
			},
			Provenance: &ProvenanceChannel{SourceRefs: []string{"noise:s9"}},
		},
	}
	unrelated := Item{
		Ref:  "unrelated",
		Kind: "card",
		Channels: Channels{
			Text: "mnbvcxzlkjhgfdsapoiuytre",
			Graph: &GraphChannel{
				RelationTypes: []string{"u0"},
				NeighborKinds: []string{"other"},
			},
			Provenance: &ProvenanceChannel{SourceRefs: []string{"unknown:s7"}},
		},
	}
	return anchor, desired, distractor, unrelated
}

func projectionBiasSimilarities(
	t *testing.T,
	policy *ProjectionBiasPolicy,
	anchor Item,
	desired Item,
	distractor Item,
) (float32, float32) {
	t.Helper()
	desiredSimilarity, _ := projectionBiasPairSimilarity(t, policy, anchor, desired)
	distractorSimilarity, _ := projectionBiasPairSimilarity(t, policy, anchor, distractor)
	return desiredSimilarity, distractorSimilarity
}

func projectionBiasPairSimilarity(
	t *testing.T,
	policy *ProjectionBiasPolicy,
	left Item,
	right Item,
) (float32, int) {
	t.Helper()
	cfg := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "projection-bias-eval",
		ProjectionBias:        policy,
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
	leftSig := encode(left)
	rightSig := encode(right)
	return sparseassoc.Similarity(leftSig, rightSig), len(leftSig.Active)
}
