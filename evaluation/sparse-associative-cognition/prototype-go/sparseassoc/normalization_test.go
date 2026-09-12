package sparseassoc

import (
	"fmt"
	"testing"
)

func TestNormalizeFeaturesDoesNotMutateInput(t *testing.T) {
	input := []Feature{{Channel: "lex", Key: "a", Weight: 2}}
	got, err := NormalizeFeatures(input, NormalizationConfig{Mode: NormalizationGlobal, DenominatorFloor: 1})
	if err != nil {
		t.Fatal(err)
	}
	if input[0].Weight != 2 {
		t.Fatalf("input mutated: %v", input[0].Weight)
	}
	got[0].Weight = 99
	if input[0].Weight != 2 {
		t.Fatalf("output aliases input: %v", input[0].Weight)
	}
}

func TestGlobalNormalizationProducesUnitPositiveWeightWhenAboveFloor(t *testing.T) {
	input := []Feature{{"lex", "a", 2}, {"graph", "b", 1}, {"graph", "c", 1}}
	got, err := NormalizeFeatures(input, NormalizationConfig{Mode: NormalizationGlobal, DenominatorFloor: 1})
	if err != nil {
		t.Fatal(err)
	}
	want := []float32{0.5, 0.25, 0.25}
	for i := range want {
		if got[i].Weight != want[i] {
			t.Fatalf("weight[%d]=%v want %v", i, got[i].Weight, want[i])
		}
	}
}

func TestPerChannelNormalizationBoundsEachChannelWithoutAmplifyingWeakChannel(t *testing.T) {
	input := []Feature{{"lex", "a", 2}, {"lex", "b", 2}, {"graph", "c", 0.25}}
	got, err := NormalizeFeatures(input, NormalizationConfig{Mode: NormalizationPerChannel, DenominatorFloor: 1})
	if err != nil {
		t.Fatal(err)
	}
	if got[0].Weight != 0.5 || got[1].Weight != 0.5 {
		t.Fatalf("lex not normalized: %#v", got)
	}
	if got[2].Weight != 0.25 {
		t.Fatalf("weak graph channel was amplified: %v", got[2].Weight)
	}
}

func TestIgnoredFeaturesDoNotAffectDenominator(t *testing.T) {
	input := []Feature{{"lex", "a", 2}, {"lex", "", 100}, {"lex", "negative", -5}}
	got, err := NormalizeFeatures(input, NormalizationConfig{Mode: NormalizationGlobal, DenominatorFloor: 1})
	if err != nil {
		t.Fatal(err)
	}
	if got[0].Weight != 1 {
		t.Fatalf("valid feature denominator included ignored inputs: %v", got[0].Weight)
	}
	if got[1].Weight != 100 || got[2].Weight != -5 {
		t.Fatalf("ignored features should be preserved: %#v", got)
	}
}

func TestGlobalPositiveScalingDoesNotChangeBinarySignature(t *testing.T) {
	e, err := NewEncoder(Config{Dimensions: 4096, Fanout: 8, Active: 64, Seed: 47})
	if err != nil {
		t.Fatal(err)
	}
	base := []Feature{{"lex", "制度", 1}, {"graph", "causal", 0.5}, {"history", "recent", 0.25}}
	scaled := []Feature{{"lex", "制度", 100}, {"graph", "causal", 50}, {"history", "recent", 25}}
	a := e.Encode(base)
	b := e.Encode(scaled)
	if len(a.Active) != len(b.Active) {
		t.Fatalf("active lengths differ: %d %d", len(a.Active), len(b.Active))
	}
	for i := range a.Active {
		if a.Active[i] != b.Active[i] {
			t.Fatalf("global scaling changed signature at %d: %d != %d", i, a.Active[i], b.Active[i])
		}
	}
}

func TestGlobalNormalizationIsSignatureNegativeControl(t *testing.T) {
	e, err := NewEncoder(Config{Dimensions: 4096, Fanout: 8, Active: 64, Seed: 47})
	if err != nil {
		t.Fatal(err)
	}
	input := []Feature{{"lex", "a", 4}, {"lex", "b", 2}, {"graph", "c", 1}}
	normalized, err := NormalizeFeatures(input, NormalizationConfig{Mode: NormalizationGlobal, DenominatorFloor: 1})
	if err != nil {
		t.Fatal(err)
	}
	a := e.Encode(input)
	b := e.Encode(normalized)
	if Similarity(a, b) != 1 {
		t.Fatalf("global normalization should not change rank-only signature: similarity=%v", Similarity(a, b))
	}
}

func TestNormalizationRejectsInvalidConfig(t *testing.T) {
	if _, err := NormalizeFeatures(nil, NormalizationConfig{Mode: NormalizationNone, DenominatorFloor: 0}); err == nil {
		t.Fatal("expected denominator floor error")
	}
	if _, err := NormalizeFeatures(nil, NormalizationConfig{Mode: 255, DenominatorFloor: 1}); err == nil {
		t.Fatal("expected mode error")
	}
}

func TestPerChannelNormalizationCanRecoverMinorityChannelInSyntheticFixture(t *testing.T) {
	cfg := Config{Dimensions: 32768, Fanout: 4, Active: 4, Seed: 47}
	e, err := NewEncoder(cfg)
	if err != nil {
		t.Fatal(err)
	}

	makeFeatures := func(prefix, graphKey string) []Feature {
		features := make([]Feature, 0, 21)
		for i := 0; i < 20; i++ {
			features = append(features, Feature{Channel: "lex", Key: fmt.Sprintf("%s-%02d", prefix, i), Weight: 2})
		}
		return append(features, Feature{Channel: "graph", Key: graphKey, Weight: 1})
	}

	query := makeFeatures("shared", "target")
	desired := makeFeatures("desired", "target")
	distractor := makeFeatures("shared", "other")

	rawIndex := NewIndex(2)
	rawIndex.Put("desired", e.Encode(desired))
	rawIndex.Put("distractor", e.Encode(distractor))
	raw := rawIndex.Query(e.Encode(query), 2)
	if len(raw) != 2 || raw[0].ID != "distractor" {
		t.Fatalf("raw fixture should be dominated by shared lexical channel: %#v", raw)
	}

	normalize := func(features []Feature) []Feature {
		got, err := NormalizeFeatures(features, NormalizationConfig{Mode: NormalizationPerChannel, DenominatorFloor: 1})
		if err != nil {
			t.Fatal(err)
		}
		return got
	}
	normalizedIndex := NewIndex(2)
	normalizedIndex.Put("desired", e.Encode(normalize(desired)))
	normalizedIndex.Put("distractor", e.Encode(normalize(distractor)))
	normalized := normalizedIndex.Query(e.Encode(normalize(query)), 2)
	if len(normalized) != 2 || normalized[0].ID != "desired" {
		t.Fatalf("per-channel normalization did not recover graph-channel match: %#v", normalized)
	}
}

func BenchmarkNormalizeGlobal20Features(b *testing.B) {
	features := make([]Feature, 20)
	for i := range features {
		features[i] = Feature{Channel: "lex", Key: "feature", Weight: 1}
	}
	cfg := NormalizationConfig{Mode: NormalizationGlobal, DenominatorFloor: 1}
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		if _, err := NormalizeFeatures(features, cfg); err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkNormalizePerChannel20Features(b *testing.B) {
	features := make([]Feature, 20)
	for i := range features {
		channel := "lex"
		if i%2 == 1 {
			channel = "graph"
		}
		features[i] = Feature{Channel: channel, Key: "feature", Weight: 1}
	}
	cfg := NormalizationConfig{Mode: NormalizationPerChannel, DenominatorFloor: 1}
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		if _, err := NormalizeFeatures(features, cfg); err != nil {
			b.Fatal(err)
		}
	}
}
