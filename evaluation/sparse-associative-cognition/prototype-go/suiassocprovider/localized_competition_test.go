package suiassocprovider

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func TestLocalCompetitionConfigFailsClosed(t *testing.T) {
	base := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "localized-competition-eval",
	}

	cases := []LocalCompetitionPolicy{
		{},
		{FamilyActive: map[string]uint16{"unknown": 1}},
		{FamilyActive: map[string]uint16{"text": 0}},
		{FamilyActive: map[string]uint16{"text": 16}, GlobalResidualActive: 1},
	}
	for i := range cases {
		cfg := base
		cfg.LocalCompetition = &cases[i]
		if _, err := New(cfg); err == nil {
			t.Fatalf("case %d must fail closed: %#v", i, cases[i])
		}
	}
}

func TestProviderClonesLocalCompetitionPolicy(t *testing.T) {
	policy := &LocalCompetitionPolicy{
		FamilyActive:         map[string]uint16{"text": 2, "graph": 2},
		GlobalResidualActive: 4,
	}
	p, err := New(Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0.1,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "localized-competition-eval",
		LocalCompetition:      policy,
	})
	if err != nil {
		t.Fatal(err)
	}
	policy.FamilyActive["text"] = 9
	policy.GlobalResidualActive = 9
	if p.cfg.LocalCompetition.FamilyActive["text"] != 2 || p.cfg.LocalCompetition.GlobalResidualActive != 4 {
		t.Fatalf("provider retained caller-mutated policy: %#v", p.cfg.LocalCompetition)
	}
}

func TestMergeSparseSignaturesIsDeterministicAndDeduplicated(t *testing.T) {
	got := mergeSparseSignatures([]sparseassoc.Signature{
		{Active: []uint16{7, 2, 4}},
		{Active: []uint16{4, 1, 7}},
	})
	want := sparseassoc.Signature{Active: []uint16{1, 2, 4, 7}}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("merged=%#v want %#v", got, want)
	}
}

func TestLocalizedCompetitionDoesNotExceedConfiguredBudget(t *testing.T) {
	cfg := sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47}
	policy := softLocalCompetitionPolicy()
	encoder, err := newLocalizedCompetitionEncoder(cfg, policy)
	if err != nil {
		t.Fatal(err)
	}
	sig := encoder.Encode(featuresForItem(localCompetitionAnchor()))
	if len(sig.Active) > int(cfg.Active) {
		t.Fatalf("signature exceeded configured active budget: %d > %d", len(sig.Active), cfg.Active)
	}
	second := encoder.Encode(featuresForItem(localCompetitionAnchor()))
	if !reflect.DeepEqual(sig, second) {
		t.Fatalf("localized competition is not deterministic: %#v != %#v", sig, second)
	}
}

func TestLocalizedCompetitionRecoversTextCardinalityFixture(t *testing.T) {
	anchor := localCompetitionAnchor()
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

	baseDesired, baseDistractor := localCompetitionSimilarities(t, nil, anchor, desired, distractor)
	if baseDesired >= baseDistractor {
		t.Fatalf("fixture must expose global text domination: desired=%v distractor=%v", baseDesired, baseDistractor)
	}

	hard := hardLocalCompetitionPolicy()
	hardDesired, hardDistractor := localCompetitionSimilarities(t, &hard, anchor, desired, distractor)
	if hardDesired <= hardDistractor {
		t.Fatalf("hard family-local competition should recover structural candidate: desired=%v distractor=%v", hardDesired, hardDistractor)
	}

	soft := softLocalCompetitionPolicy()
	softDesired, softDistractor := localCompetitionSimilarities(t, &soft, anchor, desired, distractor)
	if softDesired <= softDistractor {
		t.Fatalf("local+global residual should recover structural candidate: desired=%v distractor=%v", softDesired, softDistractor)
	}
}

func TestGlobalResidualSoftensHardIsolationFailure(t *testing.T) {
	anchor := Item{
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
	}
	desired := Item{
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
	}
	distractor := Item{
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

	baseDesired, baseDistractor := localCompetitionSimilarities(t, nil, anchor, desired, distractor)
	if baseDesired <= baseDistractor {
		t.Fatalf("baseline fixture should prefer broad-evidence candidate: desired=%v distractor=%v", baseDesired, baseDistractor)
	}

	hard := hardLocalCompetitionPolicy()
	hardDesired, hardDistractor := localCompetitionSimilarities(t, &hard, anchor, desired, distractor)
	if hardDesired >= hardDistractor {
		t.Fatalf("hard family isolation should expose over-reservation failure: desired=%v distractor=%v", hardDesired, hardDistractor)
	}

	soft := softLocalCompetitionPolicy()
	softDesired, softDistractor := localCompetitionSimilarities(t, &soft, anchor, desired, distractor)
	if softDesired <= softDistractor {
		t.Fatalf("global residual should soften hard isolation failure: desired=%v distractor=%v", softDesired, softDistractor)
	}
}

func BenchmarkLocalizedCompetitionSoft(b *testing.B) {
	cfg := sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47}
	policy := softLocalCompetitionPolicy()
	encoder, err := newLocalizedCompetitionEncoder(cfg, policy)
	if err != nil {
		b.Fatal(err)
	}
	features := featuresForItem(localCompetitionAnchor())
	b.ReportAllocs()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = encoder.Encode(features)
	}
}

func hardLocalCompetitionPolicy() LocalCompetitionPolicy {
	return LocalCompetitionPolicy{
		FamilyActive: map[string]uint16{
			"text":       4,
			"graph":      4,
			"provenance": 4,
			"grouping":   4,
		},
	}
}

func softLocalCompetitionPolicy() LocalCompetitionPolicy {
	return LocalCompetitionPolicy{
		FamilyActive: map[string]uint16{
			"text":       2,
			"graph":      2,
			"provenance": 2,
			"grouping":   2,
		},
		GlobalResidualActive: 8,
	}
}

func localCompetitionAnchor() Item {
	return Item{
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
}

func localCompetitionSimilarities(
	t *testing.T,
	policy *LocalCompetitionPolicy,
	anchor Item,
	desired Item,
	distractor Item,
) (float32, float32) {
	t.Helper()
	cfg := Config{
		Sparse:                sparseassoc.Config{Dimensions: 32768, Fanout: 4, Active: 16, Seed: 47},
		MinInternalSimilarity: 0,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "localized-competition-eval",
		LocalCompetition:      policy,
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
