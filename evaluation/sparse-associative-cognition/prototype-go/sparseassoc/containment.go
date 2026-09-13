package sparseassoc

import "sort"

const (
	CascadeRouteContainment = "hashed-containment"
	CascadeRouteSparse      = "sparse"
	CascadeRouteAbstain     = "abstain"
)

// Sketch is a sorted, bounded set of caller-feature hashes. It is used only
// for candidate recall; it is not a semantic truth or confidence record.
type Sketch struct {
	Hashes []uint32
}

type weightedFeatureHash struct {
	hash   uint32
	weight float32
}

// BuildSketch keeps the highest-weight caller-owned features and stores only
// deterministic 32-bit hashes. It deliberately has no vocabulary/model table.
func BuildSketch(seed uint64, features []Feature, limit int) Sketch {
	if limit <= 0 || len(features) == 0 {
		return Sketch{}
	}
	candidates := make([]weightedFeatureHash, 0, len(features))
	for _, f := range features {
		if f.Weight <= 0 || f.Key == "" {
			continue
		}
		candidates = append(candidates, weightedFeatureHash{
			hash:   uint32(hashFeature(seed, f.Channel, f.Key)),
			weight: f.Weight,
		})
	}
	sort.Slice(candidates, func(i, j int) bool {
		if candidates[i].weight == candidates[j].weight {
			return candidates[i].hash < candidates[j].hash
		}
		return candidates[i].weight > candidates[j].weight
	})
	if len(candidates) < limit {
		limit = len(candidates)
	}
	selected := make([]uint32, 0, limit)
	for _, candidate := range candidates {
		duplicate := false
		for _, existing := range selected {
			if existing == candidate.hash {
				duplicate = true
				break
			}
		}
		if duplicate {
			continue
		}
		selected = append(selected, candidate.hash)
		if len(selected) == limit {
			break
		}
	}
	sort.Slice(selected, func(i, j int) bool { return selected[i] < selected[j] })
	return Sketch{Hashes: selected}
}

// Containment returns the fraction of query hashes present in stored. It is
// intentionally asymmetric so a short cue can recall a much richer item.
func Containment(query, stored Sketch) float32 {
	if len(query.Hashes) == 0 || len(stored.Hashes) == 0 {
		return 0
	}
	i, j, intersection := 0, 0, 0
	for i < len(query.Hashes) && j < len(stored.Hashes) {
		switch {
		case query.Hashes[i] == stored.Hashes[j]:
			intersection++
			i++
			j++
		case query.Hashes[i] < stored.Hashes[j]:
			i++
		default:
			j++
		}
	}
	return float32(intersection) / float32(len(query.Hashes))
}

type CascadeResult struct {
	Route      string
	Candidates []Candidate
	Novelty    float32
}

type cascadeEntry struct {
	id     string
	sparse Signature
	sketch Sketch
}

// CascadeIndex complements the sparse signature with a bounded asymmetric
// sketch. It scans containment first and only pays sparse similarity when the
// containment route is insufficient.
type CascadeIndex struct {
	entries   []cascadeEntry
	positions map[string]int
}

func NewCascadeIndex(capacity int) *CascadeIndex {
	if capacity < 0 {
		capacity = 0
	}
	return &CascadeIndex{
		entries:   make([]cascadeEntry, 0, capacity),
		positions: make(map[string]int, capacity),
	}
}

func (x *CascadeIndex) Put(id string, sparse Signature, sketch Sketch) {
	if id == "" {
		return
	}
	entry := cascadeEntry{id: id, sparse: cloneSignature(sparse), sketch: cloneSketch(sketch)}
	if pos, ok := x.positions[id]; ok {
		x.entries[pos] = entry
		return
	}
	x.positions[id] = len(x.entries)
	x.entries = append(x.entries, entry)
}

func (x *CascadeIndex) Delete(id string) {
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

func (x *CascadeIndex) Len() int { return len(x.entries) }

func (x *CascadeIndex) Query(qSparse Signature, qSketch Sketch, k int, minContainment float32) CascadeResult {
	if k <= 0 || len(x.entries) == 0 {
		return CascadeResult{Route: CascadeRouteAbstain, Novelty: 1}
	}
	containment := x.queryTop(k, func(item cascadeEntry) float32 {
		return Containment(qSketch, item.sketch)
	})
	if len(containment) > 0 && containment[0].Similarity >= minContainment {
		return CascadeResult{
			Route:      CascadeRouteContainment,
			Candidates: containment,
			Novelty:    Novelty(containment[0].Similarity),
		}
	}
	if len(qSparse.Active) == 0 {
		return CascadeResult{Route: CascadeRouteAbstain, Candidates: containment, Novelty: 1}
	}
	sparse := x.queryTop(k, func(item cascadeEntry) float32 {
		return Similarity(qSparse, item.sparse)
	})
	if len(sparse) == 0 || sparse[0].Similarity <= 0 {
		return CascadeResult{Route: CascadeRouteAbstain, Candidates: sparse, Novelty: 1}
	}
	return CascadeResult{
		Route:      CascadeRouteSparse,
		Candidates: sparse,
		Novelty:    Novelty(sparse[0].Similarity),
	}
}

func (x *CascadeIndex) queryTop(k int, similarity func(cascadeEntry) float32) []Candidate {
	if k > len(x.entries) {
		k = len(x.entries)
	}
	top := make([]Candidate, 0, k)
	for _, item := range x.entries {
		candidate := Candidate{ID: item.id, Similarity: similarity(item)}
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

// ActivePayloadBytes counts only compact numeric active payloads and excludes
// slice headers, strings, maps, allocator overhead, and source material.
func (x *CascadeIndex) ActivePayloadBytes() int {
	total := 0
	for _, item := range x.entries {
		total += len(item.sparse.Active) * 2
		total += len(item.sketch.Hashes) * 4
	}
	return total
}

func cloneSketch(s Sketch) Sketch {
	out := make([]uint32, len(s.Hashes))
	copy(out, s.Hashes)
	return Sketch{Hashes: out}
}
