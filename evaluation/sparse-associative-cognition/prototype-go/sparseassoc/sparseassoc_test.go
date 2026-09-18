package sparseassoc

import (
	"fmt"
	"testing"
)

func cfg() Config { return Config{Dimensions: 4096, Fanout: 8, Active: 64, Seed: 47} }

func newTestEncoder(t testing.TB) *Encoder {
	t.Helper()
	e, err := NewEncoder(cfg())
	if err != nil {
		t.Fatal(err)
	}
	return e
}

func TestEncodeDeterministic(t *testing.T) {
	e := newTestEncoder(t)
	f := []Feature{
		{Channel: "lex", Key: "制度", Weight: 1},
		{Channel: "lex", Key: "責任", Weight: 1},
		{Channel: "graph", Key: "causal", Weight: .5},
	}
	a := e.Encode(f)
	b := e.Encode(f)
	if len(a.Active) == 0 || len(a.Active) != len(b.Active) {
		t.Fatalf("bad active lengths: %d %d", len(a.Active), len(b.Active))
	}
	for i := range a.Active {
		if a.Active[i] != b.Active[i] {
			t.Fatalf("non deterministic at %d", i)
		}
	}
}

func TestEncodeWithStatsMatchesEncodeAndCountsObservedTouches(t *testing.T) {
	features := []Feature{
		{Channel: "lex", Key: "制度", Weight: 1},
		{Channel: "lex", Key: "責任", Weight: 1},
		{Channel: "ignored", Key: "", Weight: 1},
		{Channel: "ignored", Key: "zero", Weight: 0},
	}
	plainEncoder := newTestEncoder(t)
	observedEncoder := newTestEncoder(t)

	plain := plainEncoder.Encode(features)
	observed, stats := observedEncoder.EncodeWithStats(features)
	if len(plain.Active) != len(observed.Active) {
		t.Fatalf("signature lengths differ: plain=%d observed=%d", len(plain.Active), len(observed.Active))
	}
	for i := range plain.Active {
		if plain.Active[i] != observed.Active[i] {
			t.Fatalf("signature differs at %d: plain=%d observed=%d", i, plain.Active[i], observed.Active[i])
		}
	}
	if stats.PositiveFeatures != 2 {
		t.Fatalf("positive features=%d want 2", stats.PositiveFeatures)
	}
	if stats.ProjectionAttempts != 16 {
		t.Fatalf("projection attempts=%d want 16", stats.ProjectionAttempts)
	}
	if stats.TouchedDimensions <= 0 || stats.TouchedDimensions > stats.ProjectionAttempts {
		t.Fatalf("invalid touched dimensions: %#v", stats)
	}
	if stats.SelectedDimensions != len(observed.Active) {
		t.Fatalf("selected dimensions=%d signature=%d", stats.SelectedDimensions, len(observed.Active))
	}
	if stats.SelectedDimensions > stats.TouchedDimensions {
		t.Fatalf("selected exceeds touched: %#v", stats)
	}
}

func TestEncodeWithStatsDeterministic(t *testing.T) {
	e := newTestEncoder(t)
	features := []Feature{
		{Channel: "lex", Key: "制度", Weight: 1},
		{Channel: "lex", Key: "責任", Weight: 1},
		{Channel: "graph", Key: "causal", Weight: .5},
	}
	a, sa := e.EncodeWithStats(features)
	b, sb := e.EncodeWithStats(features)
	if sa != sb {
		t.Fatalf("stats are not deterministic: %#v != %#v", sa, sb)
	}
	if len(a.Active) != len(b.Active) {
		t.Fatalf("signature lengths differ: %d %d", len(a.Active), len(b.Active))
	}
	for i := range a.Active {
		if a.Active[i] != b.Active[i] {
			t.Fatalf("signature differs at %d", i)
		}
	}
}

func TestSimilarInputMoreSimilarThanDisjoint(t *testing.T) {
	e := newTestEncoder(t)
	a := e.Encode([]Feature{{"lex", "制度", 1}, {"lex", "責任", 1}, {"lex", "現場", 1}})
	b := e.Encode([]Feature{{"lex", "制度", 1}, {"lex", "責任", 1}, {"lex", "事故", 1}})
	c := e.Encode([]Feature{{"lex", "花", 1}, {"lex", "海", 1}, {"lex", "音楽", 1}})
	if Similarity(a, b) <= Similarity(a, c) {
		t.Fatalf("expected related signatures to be closer: ab=%f ac=%f", Similarity(a, b), Similarity(a, c))
	}
}

func TestBundleRewardsSharedActivation(t *testing.T) {
	a := Signature{Active: []uint16{1, 2, 3, 9}}
	b := Signature{Active: []uint16{2, 3, 4, 8}}
	c := Bundle([]Signature{a, b}, 3)
	if len(c.Active) != 3 || !contains(c.Active, 2) || !contains(c.Active, 3) {
		t.Fatalf("unexpected bundle: %#v", c.Active)
	}
}

func TestIndexQueryAndNovelty(t *testing.T) {
	e := newTestEncoder(t)
	x := NewIndex(2)
	q := e.Encode([]Feature{{"lex", "制度", 1}, {"lex", "責任", 1}})
	near := e.Encode([]Feature{{"lex", "制度", 1}, {"lex", "責任", 1}, {"lex", "現場", 1}})
	far := e.Encode([]Feature{{"lex", "海", 1}, {"lex", "花", 1}})
	x.Put("near", near)
	x.Put("far", far)
	got := x.Query(q, 2)
	if len(got) != 2 || got[0].ID != "near" {
		t.Fatalf("unexpected query result: %#v", got)
	}
	if Novelty(got[0].Similarity) >= Novelty(got[1].Similarity) {
		t.Fatalf("near candidate should be less novel")
	}
}

func TestIndexUpsertDelete(t *testing.T) {
	e := newTestEncoder(t)
	x := NewIndex(2)
	a := e.Encode([]Feature{{"lex", "a", 1}})
	b := e.Encode([]Feature{{"lex", "b", 1}})
	x.Put("x", a)
	x.Put("x", b)
	if x.Len() != 1 {
		t.Fatalf("upsert changed length: %d", x.Len())
	}
	x.Delete("x")
	if x.Len() != 0 {
		t.Fatalf("delete failed: %d", x.Len())
	}
}

func contains(xs []uint16, want uint16) bool {
	for _, x := range xs {
		if x == want {
			return true
		}
	}
	return false
}

func TestConfigValidation(t *testing.T) {
	if _, err := NewEncoder(Config{}); err == nil {
		t.Fatal("expected invalid config")
	}
}

func BenchmarkEncode20Features(b *testing.B) {
	features := make([]Feature, 20)
	for i := range features {
		features[i] = Feature{Channel: "lex", Key: fmt.Sprintf("feature-%d", i), Weight: 1}
	}
	e := newTestEncoder(b)
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		_ = e.Encode(features)
	}
}

func BenchmarkQuery10000(b *testing.B) {
	e := newTestEncoder(b)
	x := NewIndex(10000)
	for i := 0; i < 10000; i++ {
		features := []Feature{
			{Channel: "lex", Key: fmt.Sprintf("term-%d", i%2000), Weight: 1},
			{Channel: "shape", Key: fmt.Sprintf("shape-%d", i%26), Weight: 1},
		}
		x.Put(fmt.Sprintf("item-%05d", i), e.Encode(features))
	}
	q := e.Encode([]Feature{{Channel: "lex", Key: "term-42", Weight: 1}})
	b.ReportAllocs()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = x.Query(q, 8)
	}
}
