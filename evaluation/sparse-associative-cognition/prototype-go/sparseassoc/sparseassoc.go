// Package sparseassoc provides a small, deterministic sparse-associative
// retrieval primitive for evaluation. It does not assign semantic truth,
// confidence, decisions, or labels.
package sparseassoc

import (
	"errors"
	"math"
	"sort"
)

// Feature is a caller-owned observation. Channel keeps independent feature
// families distinguishable; Key is an opaque stable identifier.
type Feature struct {
	Channel string
	Key     string
	Weight  float32
}

// Config bounds the in-memory representation. Dimensions is intentionally
// uint16-sized so a signature can store each active dimension in two bytes.
type Config struct {
	Dimensions uint16
	Fanout     uint16
	Active     uint16
	Seed       uint64
}

// Signature is a sorted sparse binary code. Active values are dimension IDs.
type Signature struct {
	Active []uint16
}

type Candidate struct {
	ID         string
	Similarity float32
}

// EncodeStats is evaluation-only instrumentation for one explicit encode call.
// TouchedDimensions counts unique post-hash dimensions before k-WTA selection.
// These counts are execution diagnostics, not semantic importance or quality.
type EncodeStats struct {
	PositiveFeatures   int
	ProjectionAttempts int
	TouchedDimensions  int
	SelectedDimensions int
}

type entry struct {
	id  string
	sig Signature
}

// Index stores signatures in a contiguous slice for cache-friendly scans.
// positions exists only for upsert/delete and is not touched during Query.
type Index struct {
	entries   []entry
	positions map[string]int
}

// Encoder reuses scratch buffers to minimize allocations. It is not safe for
// concurrent use; use one Encoder per goroutine/worker.
type Encoder struct {
	cfg     Config
	scores  []float32
	marks   []uint32
	epoch   uint32
	touched []uint16
}

func ValidateConfig(c Config) error {
	if c.Dimensions == 0 {
		return errors.New("dimensions must be > 0")
	}
	if c.Fanout == 0 {
		return errors.New("fanout must be > 0")
	}
	if c.Active == 0 {
		return errors.New("active must be > 0")
	}
	if c.Active > c.Dimensions {
		return errors.New("active must be <= dimensions")
	}
	return nil
}

func NewEncoder(cfg Config) (*Encoder, error) {
	if err := ValidateConfig(cfg); err != nil {
		return nil, err
	}
	return &Encoder{
		cfg:     cfg,
		scores:  make([]float32, int(cfg.Dimensions)),
		marks:   make([]uint32, int(cfg.Dimensions)),
		touched: make([]uint16, 0, minInt(int(cfg.Dimensions), 256)),
	}, nil
}

// Encode projects caller-provided features into a sparse code and applies a
// winner-take-all selection. Weight <= 0 and empty keys are ignored.
func (e *Encoder) Encode(features []Feature) Signature {
	e.begin()
	for _, f := range features {
		if f.Weight <= 0 || f.Key == "" {
			continue
		}
		h := hashFeature(e.cfg.Seed, f.Channel, f.Key)
		for i := uint16(0); i < e.cfg.Fanout; i++ {
			h = splitmix64(h + uint64(i) + 0x9e3779b97f4a7c15)
			idx := uint16(h % uint64(e.cfg.Dimensions))
			if e.marks[idx] != e.epoch {
				e.marks[idx] = e.epoch
				e.scores[idx] = 0
				e.touched = append(e.touched, idx)
			}
			e.scores[idx] += f.Weight
		}
	}
	if len(e.touched) == 0 {
		return Signature{}
	}

	sort.Slice(e.touched, func(i, j int) bool {
		a, b := e.touched[i], e.touched[j]
		if e.scores[a] == e.scores[b] {
			return a < b
		}
		return e.scores[a] > e.scores[b]
	})

	n := int(e.cfg.Active)
	if len(e.touched) < n {
		n = len(e.touched)
	}
	active := make([]uint16, n)
	copy(active, e.touched[:n])
	sort.Slice(active, func(i, j int) bool { return active[i] < active[j] })
	return Signature{Active: active}
}

// EncodeWithStats explicitly opts into diagnostic counting after Encode has
// completed. Normal Encode remains unchanged and does not pay per-feature
// instrumentation cost. Encoder is already single-goroutine only, so reading
// the current touched length immediately after Encode preserves its invariant.
func (e *Encoder) EncodeWithStats(features []Feature) (Signature, EncodeStats) {
	signature := e.Encode(features)
	positive := 0
	for _, feature := range features {
		if feature.Weight > 0 && feature.Key != "" {
			positive++
		}
	}
	return signature, EncodeStats{
		PositiveFeatures:   positive,
		ProjectionAttempts: positive * int(e.cfg.Fanout),
		TouchedDimensions:  len(e.touched),
		SelectedDimensions: len(signature.Active),
	}
}

func (e *Encoder) begin() {
	e.touched = e.touched[:0]
	e.epoch++
	if e.epoch == 0 { // extremely rare wraparound; restore mark invariant.
		clear(e.marks)
		e.epoch = 1
	}
}

// Bundle creates a small-set prototype. Activations shared by more input
// signatures win before one-off activations; ties are deterministic.
func Bundle(signatures []Signature, active int) Signature {
	if active <= 0 || len(signatures) == 0 {
		return Signature{}
	}
	counts := make(map[uint16]uint16)
	for _, s := range signatures {
		var previous uint16
		havePrevious := false
		for _, idx := range s.Active {
			if havePrevious && idx == previous {
				continue
			}
			counts[idx]++
			previous = idx
			havePrevious = true
		}
	}
	type counted struct {
		idx   uint16
		count uint16
	}
	ranked := make([]counted, 0, len(counts))
	for idx, count := range counts {
		ranked = append(ranked, counted{idx: idx, count: count})
	}
	sort.Slice(ranked, func(i, j int) bool {
		if ranked[i].count == ranked[j].count {
			return ranked[i].idx < ranked[j].idx
		}
		return ranked[i].count > ranked[j].count
	})
	if len(ranked) < active {
		active = len(ranked)
	}
	out := make([]uint16, active)
	for i := 0; i < active; i++ {
		out[i] = ranked[i].idx
	}
	sort.Slice(out, func(i, j int) bool { return out[i] < out[j] })
	return Signature{Active: out}
}

// Similarity returns cosine similarity for sparse binary signatures.
func Similarity(a, b Signature) float32 {
	if len(a.Active) == 0 || len(b.Active) == 0 {
		return 0
	}
	i, j, intersection := 0, 0, 0
	for i < len(a.Active) && j < len(b.Active) {
		switch {
		case a.Active[i] == b.Active[j]:
			intersection++
			i++
			j++
		case a.Active[i] < b.Active[j]:
			i++
		default:
			j++
		}
	}
	return float32(float64(intersection) / math.Sqrt(float64(len(a.Active)*len(b.Active))))
}

// Novelty is an internal retrieval signal, not epistemic Unknown or confidence.
func Novelty(bestSimilarity float32) float32 {
	if bestSimilarity <= 0 {
		return 1
	}
	if bestSimilarity >= 1 {
		return 0
	}
	return 1 - bestSimilarity
}

func NewIndex(capacity int) *Index {
	if capacity < 0 {
		capacity = 0
	}
	return &Index{
		entries:   make([]entry, 0, capacity),
		positions: make(map[string]int, capacity),
	}
}

func (x *Index) Put(id string, s Signature) {
	if id == "" {
		return
	}
	cloned := cloneSignature(s)
	if pos, ok := x.positions[id]; ok {
		x.entries[pos].sig = cloned
		return
	}
	x.positions[id] = len(x.entries)
	x.entries = append(x.entries, entry{id: id, sig: cloned})
}

func (x *Index) Delete(id string) {
	pos, ok := x.positions[id]
	if !ok {
		return
	}
	last := len(x.entries) - 1
	if pos != last {
		x.entries[pos] = x.entries[last]
		x.positions[x.entries[pos].id] = pos
	}
	x.entries = x.entries[:last]
	delete(x.positions, id)
}

func (x *Index) Len() int { return len(x.entries) }

// Query performs an exact scan over compact sparse signatures and retains only
// top-k candidates. This avoids a second ANN index for small/medium corpora.
func (x *Index) Query(q Signature, k int) []Candidate {
	if k <= 0 || len(q.Active) == 0 || len(x.entries) == 0 {
		return nil
	}
	if k > len(x.entries) {
		k = len(x.entries)
	}
	top := make([]Candidate, 0, k)
	for _, item := range x.entries {
		candidate := Candidate{ID: item.id, Similarity: Similarity(q, item.sig)}
		pos := sort.Search(len(top), func(i int) bool { return betterCandidate(candidate, top[i]) })
		if pos >= k {
			continue
		}
		if len(top) < k {
			top = append(top, Candidate{})
		}
		copy(top[pos+1:], top[pos:len(top)-1])
		top[pos] = candidate
	}
	return top
}

func betterCandidate(a, b Candidate) bool {
	if a.Similarity == b.Similarity {
		return a.ID < b.ID
	}
	return a.Similarity > b.Similarity
}

func cloneSignature(s Signature) Signature {
	out := make([]uint16, len(s.Active))
	copy(out, s.Active)
	return Signature{Active: out}
}

func hashFeature(seed uint64, channel, key string) uint64 {
	h := uint64(1469598103934665603) ^ splitmix64(seed)
	const prime = uint64(1099511628211)
	for i := 0; i < len(channel); i++ {
		h ^= uint64(channel[i])
		h *= prime
	}
	h ^= 0xff
	h *= prime
	for i := 0; i < len(key); i++ {
		h ^= uint64(key[i])
		h *= prime
	}
	return splitmix64(h)
}

func splitmix64(x uint64) uint64 {
	x += 0x9e3779b97f4a7c15
	x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9
	x = (x ^ (x >> 27)) * 0x94d049bb133111eb
	return x ^ (x >> 31)
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}
