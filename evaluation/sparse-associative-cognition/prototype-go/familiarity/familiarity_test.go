package familiarity

import (
	"reflect"
	"testing"
)

func testPolicy() Policy {
	return Policy{
		RepeatThreshold: 3,
		AttenuatedScale: 0.25,
		ExpiryTicks:     5,
		MaxEntries:      4,
	}
}

func eligible(key, fingerprint string, tick uint64) Observation {
	return Observation{
		Key:                 key,
		Fingerprint:         fingerprint,
		Tick:                tick,
		HabituationEligible: true,
	}
}

func TestPolicyFailsClosed(t *testing.T) {
	cases := []Policy{
		{RepeatThreshold: 1, AttenuatedScale: 0.25, ExpiryTicks: 5, MaxEntries: 4},
		{RepeatThreshold: 3, AttenuatedScale: 0, ExpiryTicks: 5, MaxEntries: 4},
		{RepeatThreshold: 3, AttenuatedScale: 1, ExpiryTicks: 5, MaxEntries: 4},
		{RepeatThreshold: 3, AttenuatedScale: 0.25, ExpiryTicks: 0, MaxEntries: 4},
		{RepeatThreshold: 3, AttenuatedScale: 0.25, ExpiryTicks: 5, MaxEntries: 0},
	}
	for i, policy := range cases {
		if _, err := New(policy); err == nil {
			t.Fatalf("case %d must fail closed: %#v", i, policy)
		}
	}
}

func TestRepeatedStableEventAttenuatesAtThreshold(t *testing.T) {
	tracker, err := New(testPolicy())
	if err != nil {
		t.Fatal(err)
	}

	first, err := tracker.Observe(eligible("job:1", "v1", 1))
	if err != nil {
		t.Fatal(err)
	}
	if first.Transition != TransitionNovel || first.AttentionScale != 1 || first.Attenuated || first.RepeatCount != 1 {
		t.Fatalf("unexpected first observation: %#v", first)
	}

	second, err := tracker.Observe(eligible("job:1", "v1", 2))
	if err != nil {
		t.Fatal(err)
	}
	if second.Transition != TransitionRepeated || second.AttentionScale != 1 || second.Attenuated || second.RepeatCount != 2 {
		t.Fatalf("unexpected second observation: %#v", second)
	}

	third, err := tracker.Observe(eligible("job:1", "v1", 3))
	if err != nil {
		t.Fatal(err)
	}
	if third.Transition != TransitionRepeated || third.AttentionScale != 0.25 || !third.Attenuated || third.RepeatCount != 3 {
		t.Fatalf("third observation should attenuate: %#v", third)
	}
}

func TestContentDeltaImmediatelyRecoversAttention(t *testing.T) {
	tracker, _ := New(testPolicy())
	for tick := uint64(1); tick <= 3; tick++ {
		if _, err := tracker.Observe(eligible("job:1", "v1", tick)); err != nil {
			t.Fatal(err)
		}
	}
	changed, err := tracker.Observe(eligible("job:1", "v2", 4))
	if err != nil {
		t.Fatal(err)
	}
	if changed.Transition != TransitionChanged || changed.AttentionScale != 1 || changed.Attenuated || changed.RepeatCount != 1 {
		t.Fatalf("content delta did not recover attention: %#v", changed)
	}
}

func TestExpiryImmediatelyRecoversAttention(t *testing.T) {
	tracker, _ := New(testPolicy())
	for tick := uint64(1); tick <= 3; tick++ {
		if _, err := tracker.Observe(eligible("job:1", "v1", tick)); err != nil {
			t.Fatal(err)
		}
	}
	expired, err := tracker.Observe(eligible("job:1", "v1", 8))
	if err != nil {
		t.Fatal(err)
	}
	if expired.Transition != TransitionExpired || expired.AttentionScale != 1 || expired.Attenuated || expired.RepeatCount != 1 {
		t.Fatalf("expiry did not recover attention: %#v", expired)
	}
}

func TestHighStakesBypassRecoversOneObservationWithoutErasingFamiliarity(t *testing.T) {
	tracker, _ := New(testPolicy())
	for tick := uint64(1); tick <= 3; tick++ {
		if _, err := tracker.Observe(eligible("job:1", "v1", tick)); err != nil {
			t.Fatal(err)
		}
	}
	high := eligible("job:1", "v1", 4)
	high.HighStakes = true
	high.StakesProvenanceRef = "policy:incident"
	result, err := tracker.Observe(high)
	if err != nil {
		t.Fatal(err)
	}
	if result.BypassReason != BypassHighStakes || result.AttentionScale != 1 || result.Attenuated {
		t.Fatalf("high-stakes observation did not bypass attenuation: %#v", result)
	}

	next, err := tracker.Observe(eligible("job:1", "v1", 5))
	if err != nil {
		t.Fatal(err)
	}
	if !next.Attenuated || next.AttentionScale != 0.25 || next.RepeatCount != 5 {
		t.Fatalf("high-stakes bypass unexpectedly erased familiarity state: %#v", next)
	}
}

func TestHighStakesRequiresProvenance(t *testing.T) {
	tracker, _ := New(testPolicy())
	obs := eligible("job:1", "v1", 1)
	obs.HighStakes = true
	if _, err := tracker.Observe(obs); err == nil {
		t.Fatal("high-stakes observation without provenance must fail closed")
	}
}

func TestIneligibleObservationBypassesAndDoesNotCreateState(t *testing.T) {
	tracker, _ := New(testPolicy())
	obs := Observation{
		Key:                 "job:1",
		Fingerprint:         "v1",
		Tick:                1,
		HabituationEligible: false,
	}
	result, err := tracker.Observe(obs)
	if err != nil {
		t.Fatal(err)
	}
	if result.BypassReason != BypassIneligible || result.AttentionScale != 1 || result.Attenuated {
		t.Fatalf("unexpected ineligible result: %#v", result)
	}
	if tracker.Len() != 0 {
		t.Fatalf("ineligible observation must not create familiarity state: len=%d", tracker.Len())
	}
}

func TestHiddenContentChangeWithUnchangedFingerprintRemainsMissedChangeRisk(t *testing.T) {
	tracker, _ := New(testPolicy())
	for tick := uint64(1); tick <= 3; tick++ {
		if _, err := tracker.Observe(eligible("sensor:1", "caller-fingerprint-v1", tick)); err != nil {
			t.Fatal(err)
		}
	}

	// Imagine the underlying event changed here, but the caller's projection
	// failed to change the fingerprint. The familiarity layer cannot recover
	// information it was not given and must continue to treat it as repeated.
	hiddenChange, err := tracker.Observe(eligible("sensor:1", "caller-fingerprint-v1", 4))
	if err != nil {
		t.Fatal(err)
	}
	if !hiddenChange.Attenuated || hiddenChange.Transition != TransitionRepeated {
		t.Fatalf("fixture must expose caller-fingerprint missed-change risk: %#v", hiddenChange)
	}
}

func TestCapacityEvictionIsDeterministic(t *testing.T) {
	policy := testPolicy()
	policy.MaxEntries = 2
	tracker, _ := New(policy)

	if _, err := tracker.Observe(eligible("b", "v1", 1)); err != nil {
		t.Fatal(err)
	}
	if _, err := tracker.Observe(eligible("a", "v1", 1)); err != nil {
		t.Fatal(err)
	}
	result, err := tracker.Observe(eligible("c", "v1", 2))
	if err != nil {
		t.Fatal(err)
	}
	if result.EvictedKey != "a" {
		t.Fatalf("oldest-tie eviction must be deterministic by key: %#v", result)
	}
	if tracker.Len() != 2 {
		t.Fatalf("tracker exceeded capacity: len=%d", tracker.Len())
	}

	again, err := tracker.Observe(eligible("a", "v1", 3))
	if err != nil {
		t.Fatal(err)
	}
	if again.Transition != TransitionNovel {
		t.Fatalf("evicted event should return as novel: %#v", again)
	}
}

func TestLogicalTickCannotMoveBackward(t *testing.T) {
	tracker, _ := New(testPolicy())
	if _, err := tracker.Observe(eligible("a", "v1", 2)); err != nil {
		t.Fatal(err)
	}
	if _, err := tracker.Observe(eligible("b", "v1", 1)); err == nil {
		t.Fatal("backward logical tick must fail closed")
	}
}

func TestEventIdentityAndFingerprintMustBeExplicit(t *testing.T) {
	tracker, _ := New(testPolicy())
	if _, err := tracker.Observe(eligible("", "v1", 1)); err == nil {
		t.Fatal("empty event key must fail closed")
	}
	if _, err := tracker.Observe(eligible("a", "", 1)); err == nil {
		t.Fatal("empty fingerprint must fail closed")
	}
}

func TestDeterministicReproducibility(t *testing.T) {
	sequence := []Observation{
		eligible("a", "v1", 1),
		eligible("a", "v1", 2),
		eligible("b", "x1", 2),
		eligible("a", "v1", 3),
		eligible("a", "v2", 4),
		eligible("b", "x1", 7),
	}
	first, _ := New(testPolicy())
	second, _ := New(testPolicy())

	var a, b []Result
	for _, observation := range sequence {
		left, err := first.Observe(observation)
		if err != nil {
			t.Fatal(err)
		}
		right, err := second.Observe(observation)
		if err != nil {
			t.Fatal(err)
		}
		a = append(a, left)
		b = append(b, right)
	}
	if !reflect.DeepEqual(a, b) {
		t.Fatalf("same sequence produced different results:\nleft=%#v\nright=%#v", a, b)
	}
}

func BenchmarkObserveRepeated(b *testing.B) {
	tracker, err := New(Policy{
		RepeatThreshold: 3,
		AttenuatedScale: 0.25,
		ExpiryTicks:     ^uint64(0),
		MaxEntries:      1024,
	})
	if err != nil {
		b.Fatal(err)
	}
	observation := eligible("job:1", "v1", 1)
	if _, err := tracker.Observe(observation); err != nil {
		b.Fatal(err)
	}
	b.ReportAllocs()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		observation.Tick++
		if _, err := tracker.Observe(observation); err != nil {
			b.Fatal(err)
		}
	}
}
