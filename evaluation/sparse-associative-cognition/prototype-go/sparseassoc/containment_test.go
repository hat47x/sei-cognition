package sparseassoc

import (
	"fmt"
	"testing"
)

func TestBuildSketchDeterministic(t *testing.T) {
	features := []Feature{{"question", "markdown", 4}, {"question", "cloud", 4}, {"obs", "mobile", 1}}
	a := BuildSketch(47, features, 64)
	b := BuildSketch(47, features, 64)
	if len(a.Hashes) != len(b.Hashes) {
		t.Fatal("length mismatch")
	}
	for i := range a.Hashes {
		if a.Hashes[i] != b.Hashes[i] {
			t.Fatal("non deterministic")
		}
	}
}

func TestContainmentIsAsymmetricForShortCue(t *testing.T) {
	query := BuildSketch(47, []Feature{{"question", "markdown", 4}, {"question", "cloud", 4}}, 64)
	storedFeatures := []Feature{{"question", "markdown", 4}, {"question", "cloud", 4}}
	for i := 0; i < 50; i++ {
		storedFeatures = append(storedFeatures, Feature{"obs", string(rune('a' + i%26)), 1})
	}
	stored := BuildSketch(47, storedFeatures, 64)
	if got := Containment(query, stored); got != 1 {
		t.Fatalf("want 1 got %f", got)
	}
}

func TestCascadePrefersContainmentForRichItem(t *testing.T) {
	x := NewCascadeIndex(2)
	queryFeatures := []Feature{{"question", "markdown", 4}, {"question", "cloud", 4}, {"unknown", "mobile", 2}}
	personalFeatures := append([]Feature(nil), queryFeatures...)
	for i := 0; i < 40; i++ {
		personalFeatures = append(personalFeatures, Feature{"obs", "noise-" + string(rune('a'+i%26)), 1})
	}
	travelFeatures := []Feature{{"question", "hotel", 4}, {"question", "route", 4}, {"unknown", "car", 2}}
	x.Put("personal", Signature{Active: []uint16{1, 2, 3}}, BuildSketch(47, personalFeatures, 64))
	x.Put("travel", Signature{Active: []uint16{1, 2, 4}}, BuildSketch(47, travelFeatures, 64))
	result := x.Query(Signature{Active: []uint16{1, 2}}, BuildSketch(47, queryFeatures, 64), 2, .12)
	if result.Route != CascadeRouteContainment || len(result.Candidates) == 0 || result.Candidates[0].ID != "personal" {
		t.Fatalf("unexpected %#v", result)
	}
}

func TestCascadeFallsBackToSparse(t *testing.T) {
	x := NewCascadeIndex(1)
	x.Put("a", Signature{Active: []uint16{1, 2, 3}}, BuildSketch(47, []Feature{{"lex", "alpha", 1}}, 64))
	result := x.Query(Signature{Active: []uint16{1, 2}}, BuildSketch(47, []Feature{{"lex", "other", 1}}, 64), 1, .99)
	if result.Route != CascadeRouteSparse {
		t.Fatalf("route=%s", result.Route)
	}
}

func TestCascadePayloadBound(t *testing.T) {
	x := NewCascadeIndex(1)
	features := make([]Feature, 64)
	for i := range features {
		features[i] = Feature{"lex", string(rune(i + 1)), 1}
	}
	x.Put("a", Signature{Active: make([]uint16, 64)}, BuildSketch(47, features, 64))
	if got := x.ActivePayloadBytes(); got > 384 {
		t.Fatalf("payload=%d", got)
	}
}

func BenchmarkCascadeQuery10000(b *testing.B) {
	x := NewCascadeIndex(10000)
	for i := 0; i < 10000; i++ {
		features := []Feature{
			{Channel: "lex", Key: fmt.Sprintf("term-%d", i%2000), Weight: 4},
			{Channel: "shape", Key: fmt.Sprintf("shape-%d", i%26), Weight: 1},
		}
		sig := Signature{Active: []uint16{uint16(i % 4096), uint16((i + 1) % 4096)}}
		x.Put(fmt.Sprintf("item-%05d", i), sig, BuildSketch(47, features, 64))
	}
	qFeatures := []Feature{{Channel: "lex", Key: "term-42", Weight: 4}}
	qSketch := BuildSketch(47, qFeatures, 64)
	qSig := Signature{Active: []uint16{42, 43}}
	b.ReportAllocs()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = x.Query(qSig, qSketch, 8, .12)
	}
}
