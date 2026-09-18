// Package familiarity provides an evaluation-only reversible familiarity
// modulator for repeated caller-identified events.
//
// It does not infer semantic sameness, stakes, truth, importance, or decisions.
// The caller owns stable event keys, content fingerprints, eligibility, and
// high-stakes provenance.
package familiarity

import (
	"errors"
	"fmt"
	"strings"
)

const (
	TransitionNovel    = "novel"
	TransitionRepeated = "repeated"
	TransitionChanged  = "changed"
	TransitionExpired  = "expired"

	BypassNone       = ""
	BypassIneligible = "ineligible"
	BypassHighStakes = "high-stakes"
)

type Policy struct {
	RepeatThreshold uint32
	AttenuatedScale float32
	ExpiryTicks     uint64
	MaxEntries      int
}

type Observation struct {
	Key                    string
	Fingerprint            string
	Tick                   uint64
	HabituationEligible    bool
	HighStakes             bool
	StakesProvenanceRef    string
}

type Result struct {
	AttentionScale float32
	Transition     string
	BypassReason   string
	RepeatCount    uint32
	Attenuated     bool
	EvictedKey     string
}

type entry struct {
	fingerprint string
	repeatCount uint32
	lastTick    uint64
}

type Tracker struct {
	policy   Policy
	entries  map[string]entry
	lastTick uint64
	haveTick bool
}

func New(policy Policy) (*Tracker, error) {
	if policy.RepeatThreshold < 2 {
		return nil, errors.New("repeat threshold must be >= 2")
	}
	if policy.AttenuatedScale <= 0 || policy.AttenuatedScale >= 1 {
		return nil, errors.New("attenuated scale must be in (0,1)")
	}
	if policy.ExpiryTicks == 0 {
		return nil, errors.New("expiry ticks must be > 0")
	}
	if policy.MaxEntries <= 0 {
		return nil, errors.New("max entries must be > 0")
	}
	return &Tracker{
		policy:  policy,
		entries: make(map[string]entry, policy.MaxEntries),
	}, nil
}

func (t *Tracker) Len() int {
	return len(t.entries)
}

func (t *Tracker) Observe(observation Observation) (Result, error) {
	if strings.TrimSpace(observation.Key) == "" {
		return Result{}, errors.New("event key must not be empty")
	}
	if strings.TrimSpace(observation.Fingerprint) == "" {
		return Result{}, errors.New("content fingerprint must not be empty")
	}
	if observation.HighStakes && strings.TrimSpace(observation.StakesProvenanceRef) == "" {
		return Result{}, errors.New("high-stakes observation requires provenance ref")
	}
	if t.haveTick && observation.Tick < t.lastTick {
		return Result{}, fmt.Errorf("logical tick moved backward: %d < %d", observation.Tick, t.lastTick)
	}
	t.lastTick = observation.Tick
	t.haveTick = true

	if !observation.HabituationEligible {
		return Result{
			AttentionScale: 1,
			BypassReason:   BypassIneligible,
		}, nil
	}

	current, exists := t.entries[observation.Key]
	result := Result{AttentionScale: 1}

	if !exists {
		result.Transition = TransitionNovel
		result.RepeatCount = 1
		result.EvictedKey = t.ensureCapacity(observation.Key)
		current = entry{
			fingerprint: observation.Fingerprint,
			repeatCount: 1,
			lastTick:    observation.Tick,
		}
	} else {
		expired := observation.Tick-current.lastTick >= t.policy.ExpiryTicks
		switch {
		case expired:
			result.Transition = TransitionExpired
			result.RepeatCount = 1
			current.fingerprint = observation.Fingerprint
			current.repeatCount = 1
		case observation.Fingerprint != current.fingerprint:
			result.Transition = TransitionChanged
			result.RepeatCount = 1
			current.fingerprint = observation.Fingerprint
			current.repeatCount = 1
		default:
			result.Transition = TransitionRepeated
			current.repeatCount++
			result.RepeatCount = current.repeatCount
			if current.repeatCount >= t.policy.RepeatThreshold {
				result.AttentionScale = t.policy.AttenuatedScale
				result.Attenuated = true
			}
		}
		current.lastTick = observation.Tick
	}

	t.entries[observation.Key] = current

	if observation.HighStakes {
		result.AttentionScale = 1
		result.Attenuated = false
		result.BypassReason = BypassHighStakes
	}
	return result, nil
}

func (t *Tracker) ensureCapacity(newKey string) string {
	if _, exists := t.entries[newKey]; exists || len(t.entries) < t.policy.MaxEntries {
		return ""
	}
	var evictKey string
	var evictTick uint64
	haveCandidate := false
	for key, value := range t.entries {
		if !haveCandidate || value.lastTick < evictTick || (value.lastTick == evictTick && key < evictKey) {
			evictKey = key
			evictTick = value.lastTick
			haveCandidate = true
		}
	}
	delete(t.entries, evictKey)
	return evictKey
}
