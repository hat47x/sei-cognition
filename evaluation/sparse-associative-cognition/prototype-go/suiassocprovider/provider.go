// Package suiassocprovider adapts the evaluation-only sparse associative
// primitive to SUI's provider-neutral associative recall JSON contract.
//
// Similarity and novelty remain provider-internal execution signals. The
// response exposes only candidate refs, abstention, explainable channel
// provenance, and provider/version trace.
package suiassocprovider

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"sort"
	"strings"
	"unicode"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

const (
	RequestSchema  = "sui.associative-recall-request/v1alpha1"
	ResponseSchema = "sui.associative-recall-response/v1alpha1"

	MaxItems          = 512
	MaxAnchors        = 32
	MaxCandidateLimit = 64
)

var allowedIntents = map[string]struct{}{
	"neighborhood": {},
	"contrast":     {},
	"bridge":       {},
	"residual":     {},
	"unresolved":   {},
	"temporal":     {},
	"provenance":   {},
	"affinity":     {},
	"readout":      {},
}

type Request struct {
	Schema     string `json:"schema"`
	RequestID  string `json:"requestId"`
	NetworkID  string `json:"networkId"`
	Intent     string `json:"intent"`
	AnchorRefs []string `json:"anchorRefs"`
	Items      []Item `json:"items"`
	Policy     Policy `json:"policy"`
}

type Policy struct {
	CandidateLimit int `json:"candidateLimit"`
}

type Item struct {
	Ref      string   `json:"ref"`
	Kind     string   `json:"kind"`
	Channels Channels `json:"channels"`
}

type Channels struct {
	Text       string             `json:"text,omitempty"`
	Graph      *GraphChannel      `json:"graph,omitempty"`
	Provenance *ProvenanceChannel `json:"provenance,omitempty"`
	Grouping   *GroupingChannel   `json:"grouping,omitempty"`
}

type GraphChannel struct {
	RelationTypes []string `json:"relationTypes"`
	NeighborKinds []string `json:"neighborKinds"`
}

type ProvenanceChannel struct {
	SourceRefs []string `json:"sourceRefs"`
	ActorRefs  []string `json:"actorRefs"`
}

type GroupingChannel struct {
	IslandRef string `json:"islandRef,omitempty"`
	HoldState string `json:"holdState,omitempty"`
}

type Response struct {
	Schema        string       `json:"schema"`
	RequestID     string       `json:"requestId"`
	Provider      ProviderInfo `json:"provider"`
	Outcome       string       `json:"outcome"`
	CandidateRefs []string     `json:"candidateRefs"`
	Evidence      []Evidence   `json:"evidence"`
	NoveltyCue    string       `json:"noveltyCue"`
}

type ProviderInfo struct {
	ProviderID            string `json:"providerId"`
	ImplementationVersion string `json:"implementationVersion"`
}

type Evidence struct {
	Ref                string   `json:"ref"`
	MatchedChannelRefs []string `json:"matchedChannelRefs"`
}

// FeatureNormalizationMode controls evaluation-only input reweighting.
// The default keeps the current provider behavior unchanged.
type FeatureNormalizationMode uint8

const (
	FeatureNormalizationNone FeatureNormalizationMode = iota
	FeatureNormalizationExactChannel
	FeatureNormalizationFamily
)

type Config struct {
	Sparse                sparseassoc.Config
	MinInternalSimilarity float32
	ProviderID            string
	ImplementationVersion string
	FeatureNormalization  FeatureNormalizationMode
	NormalizationFloor    float32
}

type Provider struct {
	cfg Config
}

func New(cfg Config) (*Provider, error) {
	if err := sparseassoc.ValidateConfig(cfg.Sparse); err != nil {
		return nil, err
	}
	if cfg.MinInternalSimilarity < 0 || cfg.MinInternalSimilarity > 1 {
		return nil, errors.New("min internal similarity must be in [0,1]")
	}
	if strings.TrimSpace(cfg.ProviderID) == "" {
		return nil, errors.New("provider id must not be empty")
	}
	if strings.TrimSpace(cfg.ImplementationVersion) == "" {
		return nil, errors.New("implementation version must not be empty")
	}
	switch cfg.FeatureNormalization {
	case FeatureNormalizationNone:
	case FeatureNormalizationExactChannel, FeatureNormalizationFamily:
		if cfg.NormalizationFloor <= 0 {
			return nil, errors.New("normalization floor must be > 0 when normalization is enabled")
		}
	default:
		return nil, errors.New("unsupported feature normalization mode")
	}
	return &Provider{cfg: cfg}, nil
}

func DecodeRequest(data []byte) (Request, error) {
	var req Request
	dec := json.NewDecoder(bytes.NewReader(data))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&req); err != nil {
		return Request{}, err
	}
	if err := ensureEOF(dec); err != nil {
		return Request{}, err
	}
	if err := validateRequest(req); err != nil {
		return Request{}, err
	}
	return req, nil
}

func ensureEOF(dec *json.Decoder) error {
	var extra any
	if err := dec.Decode(&extra); err == io.EOF {
		return nil
	} else if err != nil {
		return err
	}
	return errors.New("multiple JSON values are not allowed")
}

func validateRequest(req Request) error {
	if req.Schema != RequestSchema {
		return errors.New("unsupported request schema")
	}
	if strings.TrimSpace(req.RequestID) == "" {
		return errors.New("requestId must not be empty")
	}
	if strings.TrimSpace(req.NetworkID) == "" {
		return errors.New("networkId must not be empty")
	}
	if _, ok := allowedIntents[req.Intent]; !ok {
		return fmt.Errorf("unsupported intent: %s", req.Intent)
	}
	if len(req.Items) == 0 || len(req.Items) > MaxItems {
		return fmt.Errorf("items must contain 1..%d entries", MaxItems)
	}
	if len(req.AnchorRefs) == 0 || len(req.AnchorRefs) > MaxAnchors {
		return fmt.Errorf("anchorRefs must contain 1..%d entries", MaxAnchors)
	}
	if req.Policy.CandidateLimit < 1 || req.Policy.CandidateLimit > MaxCandidateLimit {
		return fmt.Errorf("candidateLimit must be in 1..%d", MaxCandidateLimit)
	}

	items := make(map[string]struct{}, len(req.Items))
	for _, item := range req.Items {
		if strings.TrimSpace(item.Ref) == "" {
			return errors.New("item ref must not be empty")
		}
		if strings.TrimSpace(item.Kind) == "" {
			return errors.New("item kind must not be empty")
		}
		if _, exists := items[item.Ref]; exists {
			return fmt.Errorf("duplicate item ref: %s", item.Ref)
		}
		items[item.Ref] = struct{}{}
	}

	anchors := make(map[string]struct{}, len(req.AnchorRefs))
	for _, ref := range req.AnchorRefs {
		if strings.TrimSpace(ref) == "" {
			return errors.New("anchor ref must not be empty")
		}
		if _, exists := anchors[ref]; exists {
			return fmt.Errorf("duplicate anchor ref: %s", ref)
		}
		if _, exists := items[ref]; !exists {
			return fmt.Errorf("anchor ref outside items: %s", ref)
		}
		anchors[ref] = struct{}{}
	}
	return nil
}

func (p *Provider) Handle(req Request) (Response, error) {
	if err := validateRequest(req); err != nil {
		return Response{}, err
	}
	encoder, err := sparseassoc.NewEncoder(p.cfg.Sparse)
	if err != nil {
		return Response{}, err
	}

	anchorSet := make(map[string]struct{}, len(req.AnchorRefs))
	for _, ref := range req.AnchorRefs {
		anchorSet[ref] = struct{}{}
	}

	itemByRef := make(map[string]Item, len(req.Items))
	anchorSignatures := make([]sparseassoc.Signature, 0, len(req.AnchorRefs))
	index := sparseassoc.NewIndex(len(req.Items) - len(req.AnchorRefs))

	for _, item := range req.Items {
		itemByRef[item.Ref] = item
		features, err := p.preparedFeatures(item)
		if err != nil {
			return Response{}, err
		}
		sig := encoder.Encode(features)
		if _, anchor := anchorSet[item.Ref]; anchor {
			anchorSignatures = append(anchorSignatures, sig)
			continue
		}
		index.Put(item.Ref, sig)
	}

	query := sparseassoc.Bundle(anchorSignatures, int(p.cfg.Sparse.Active))
	internal := index.Query(query, req.Policy.CandidateLimit)
	accepted := make([]string, 0, len(internal))
	for _, candidate := range internal {
		if candidate.Similarity >= p.cfg.MinInternalSimilarity {
			accepted = append(accepted, candidate.ID)
		}
	}
	if len(accepted) == 0 {
		return p.abstain(req.RequestID), nil
	}

	// Internal similarity determines narrowing only. External order is stable ref
	// order and does not expose provider ranking.
	sort.Strings(accepted)
	anchorChannelRefs := make(map[string]struct{})
	for _, ref := range req.AnchorRefs {
		for _, channelRef := range channelRefs(itemByRef[ref]) {
			anchorChannelRefs[channelRef] = struct{}{}
		}
	}

	evidence := make([]Evidence, 0, len(accepted))
	for _, ref := range accepted {
		matched := make([]string, 0)
		for _, channelRef := range channelRefs(itemByRef[ref]) {
			if _, ok := anchorChannelRefs[channelRef]; ok {
				matched = append(matched, channelRef)
			}
		}
		sort.Strings(matched)
		evidence = append(evidence, Evidence{Ref: ref, MatchedChannelRefs: matched})
	}

	return Response{
		Schema:        ResponseSchema,
		RequestID:     req.RequestID,
		Provider:      p.providerInfo(),
		Outcome:       "candidates",
		CandidateRefs: accepted,
		Evidence:      evidence,
		NoveltyCue:    "none",
	}, nil
}

func (p *Provider) abstain(requestID string) Response {
	return Response{
		Schema:        ResponseSchema,
		RequestID:     requestID,
		Provider:      p.providerInfo(),
		Outcome:       "abstain",
		CandidateRefs: []string{},
		Evidence:      []Evidence{},
		NoveltyCue:    "abstain",
	}
}

func (p *Provider) providerInfo() ProviderInfo {
	return ProviderInfo{
		ProviderID:            p.cfg.ProviderID,
		ImplementationVersion: p.cfg.ImplementationVersion,
	}
}

func (p *Provider) preparedFeatures(item Item) ([]sparseassoc.Feature, error) {
	features := featuresForItem(item)
	switch p.cfg.FeatureNormalization {
	case FeatureNormalizationNone:
		return features, nil
	case FeatureNormalizationExactChannel:
		return sparseassoc.NormalizeFeatures(features, sparseassoc.NormalizationConfig{
			Mode:             sparseassoc.NormalizationPerChannel,
			DenominatorFloor: p.cfg.NormalizationFloor,
		})
	case FeatureNormalizationFamily:
		return normalizeFeaturesByFamily(features, p.cfg.NormalizationFloor), nil
	default:
		return nil, errors.New("unsupported feature normalization mode")
	}
}

// normalizeFeaturesByFamily keeps each feature's original Channel and Key for
// hashing/provenance, and uses caller-owned families only to compute divisors.
func normalizeFeaturesByFamily(features []sparseassoc.Feature, denominatorFloor float32) []sparseassoc.Feature {
	out := append([]sparseassoc.Feature(nil), features...)
	totals := make(map[string]float32)
	for _, feature := range features {
		if feature.Weight <= 0 || feature.Key == "" {
			continue
		}
		totals[featureFamily(feature.Channel)] += feature.Weight
	}
	for i := range out {
		if out[i].Weight <= 0 || out[i].Key == "" {
			continue
		}
		denominator := totals[featureFamily(out[i].Channel)]
		if denominator < denominatorFloor {
			denominator = denominatorFloor
		}
		out[i].Weight /= denominator
	}
	return out
}

func featureFamily(channel string) string {
	switch {
	case channel == "kind":
		return "kind"
	case channel == "text":
		return "text"
	case strings.HasPrefix(channel, "graph:"):
		return "graph"
	case strings.HasPrefix(channel, "provenance:"):
		return "provenance"
	case strings.HasPrefix(channel, "grouping:"):
		return "grouping"
	default:
		return channel
	}
}

func featuresForItem(item Item) []sparseassoc.Feature {
	features := make([]sparseassoc.Feature, 0, 32)
	features = append(features, sparseassoc.Feature{Channel: "kind", Key: item.Kind, Weight: 1})
	for _, gram := range textNgrams(item.Channels.Text) {
		features = append(features, sparseassoc.Feature{Channel: "text", Key: gram, Weight: 1})
	}
	if item.Channels.Graph != nil {
		for _, value := range stableUnique(item.Channels.Graph.RelationTypes) {
			features = append(features, sparseassoc.Feature{Channel: "graph:relationType", Key: value, Weight: 1})
		}
		for _, value := range stableUnique(item.Channels.Graph.NeighborKinds) {
			features = append(features, sparseassoc.Feature{Channel: "graph:neighborKind", Key: value, Weight: 1})
		}
	}
	if item.Channels.Provenance != nil {
		for _, value := range stableUnique(item.Channels.Provenance.SourceRefs) {
			features = append(features, sparseassoc.Feature{Channel: "provenance:source", Key: value, Weight: 1})
		}
		for _, value := range stableUnique(item.Channels.Provenance.ActorRefs) {
			features = append(features, sparseassoc.Feature{Channel: "provenance:actor", Key: value, Weight: 1})
		}
	}
	if item.Channels.Grouping != nil {
		if value := strings.TrimSpace(item.Channels.Grouping.IslandRef); value != "" {
			features = append(features, sparseassoc.Feature{Channel: "grouping:island", Key: value, Weight: 1})
		}
		if value := strings.TrimSpace(item.Channels.Grouping.HoldState); value != "" {
			features = append(features, sparseassoc.Feature{Channel: "grouping:hold", Key: value, Weight: 1})
		}
	}
	return features
}

func channelRefs(item Item) []string {
	refs := make([]string, 0, 16)
	if strings.TrimSpace(item.Channels.Text) != "" {
		refs = append(refs, "channel:text")
	}
	if item.Channels.Graph != nil {
		for _, value := range stableUnique(item.Channels.Graph.RelationTypes) {
			refs = append(refs, "graph:relationType:"+value)
		}
		for _, value := range stableUnique(item.Channels.Graph.NeighborKinds) {
			refs = append(refs, "graph:neighborKind:"+value)
		}
	}
	if item.Channels.Provenance != nil {
		for _, value := range stableUnique(item.Channels.Provenance.SourceRefs) {
			refs = append(refs, "provenance:source:"+value)
		}
		for _, value := range stableUnique(item.Channels.Provenance.ActorRefs) {
			refs = append(refs, "provenance:actor:"+value)
		}
	}
	if item.Channels.Grouping != nil {
		if value := strings.TrimSpace(item.Channels.Grouping.IslandRef); value != "" {
			refs = append(refs, "grouping:island:"+value)
		}
		if value := strings.TrimSpace(item.Channels.Grouping.HoldState); value != "" {
			refs = append(refs, "grouping:hold:"+value)
		}
	}
	return stableUnique(refs)
}

func textNgrams(text string) []string {
	compact := make([]rune, 0, len(text))
	for _, r := range strings.TrimSpace(text) {
		r = unicode.ToLower(r)
		if unicode.IsLetter(r) || unicode.IsNumber(r) {
			compact = append(compact, r)
		}
	}
	if len(compact) == 0 {
		return nil
	}
	features := make([]string, 0, len(compact)*2)
	for _, n := range []int{2, 3} {
		if len(compact) < n {
			continue
		}
		for i := 0; i+n <= len(compact); i++ {
			features = append(features, string(compact[i:i+n]))
		}
	}
	if len(features) == 0 {
		features = append(features, string(compact))
	}
	return stableUnique(features)
}

func stableUnique(values []string) []string {
	seen := make(map[string]struct{}, len(values))
	out := make([]string, 0, len(values))
	for _, value := range values {
		value = strings.TrimSpace(value)
		if value == "" {
			continue
		}
		if _, ok := seen[value]; ok {
			continue
		}
		seen[value] = struct{}{}
		out = append(out, value)
	}
	sort.Strings(out)
	return out
}
