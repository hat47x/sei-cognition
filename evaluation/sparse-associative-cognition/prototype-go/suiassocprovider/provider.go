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

	MaxItems                    = 512
	MaxAnchors                  = 32
	MaxCandidateLimit           = 64
	MaxProjectionBiasRules      = 64
	MaxProjectionBiasMultiplier = float32(4)
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

// LocalCompetitionPolicy reserves bounded winner slots for caller-owned feature
// families and optionally keeps a global residual competition path.
type LocalCompetitionPolicy struct {
	FamilyActive         map[string]uint16
	GlobalResidualActive uint16
}

// ProjectionBiasRule is a caller-owned, provenance-bearing exact-feature prior.
// It changes projection competition only; it does not assert semantic importance.
type ProjectionBiasRule struct {
	Channel       string
	Key           string
	Multiplier    float32
	ProvenanceRef string
}

// ProjectionBiasPolicy bounds caller-provided static projection priors.
// SACS does not learn or infer these priors.
type ProjectionBiasPolicy struct {
	PolicyRef     string
	MaxMultiplier float32
	Rules         []ProjectionBiasRule
}

type Config struct {
	Sparse                sparseassoc.Config
	MinInternalSimilarity float32
	ProviderID            string
	ImplementationVersion string
	FeatureNormalization  FeatureNormalizationMode
	NormalizationFloor    float32
	LocalCompetition      *LocalCompetitionPolicy
	ProjectionBias        *ProjectionBiasPolicy
}

type projectionBiasSelector struct {
	channel string
	key     string
}

type Provider struct {
	cfg            Config
	projectionBias map[projectionBiasSelector]float32
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
	if err := validateLocalCompetition(cfg.Sparse, cfg.LocalCompetition); err != nil {
		return nil, err
	}
	if err := validateProjectionBias(cfg.ProjectionBias); err != nil {
		return nil, err
	}
	cfg.LocalCompetition = cloneLocalCompetition(cfg.LocalCompetition)
	cfg.ProjectionBias = cloneProjectionBias(cfg.ProjectionBias)
	return &Provider{
		cfg:            cfg,
		projectionBias: compileProjectionBias(cfg.ProjectionBias),
	}, nil
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
	encoder, err := newProviderEncoder(p.cfg)
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
		sig, err := encoder.Encode(features)
		if err != nil {
			return Response{}, err
		}
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

func validateLocalCompetition(cfg sparseassoc.Config, policy *LocalCompetitionPolicy) error {
	if policy == nil {
		return nil
	}
	if len(policy.FamilyActive) == 0 {
		return errors.New("local competition requires at least one family budget")
	}
	knownFamilies := map[string]struct{}{
		"kind": {}, "text": {}, "graph": {}, "provenance": {}, "grouping": {},
	}
	total := uint32(policy.GlobalResidualActive)
	for family, active := range policy.FamilyActive {
		if _, ok := knownFamilies[family]; !ok {
			return fmt.Errorf("unsupported local competition family: %s", family)
		}
		if active == 0 {
			return fmt.Errorf("local competition family %s must have active > 0", family)
		}
		total += uint32(active)
	}
	if total == 0 {
		return errors.New("local competition total active budget must be > 0")
	}
	if total > uint32(cfg.Active) {
		return fmt.Errorf("local competition total active budget %d exceeds sparse active %d", total, cfg.Active)
	}
	return nil
}

func cloneLocalCompetition(policy *LocalCompetitionPolicy) *LocalCompetitionPolicy {
	if policy == nil {
		return nil
	}
	out := &LocalCompetitionPolicy{
		FamilyActive:         make(map[string]uint16, len(policy.FamilyActive)),
		GlobalResidualActive: policy.GlobalResidualActive,
	}
	for family, active := range policy.FamilyActive {
		out.FamilyActive[family] = active
	}
	return out
}

type providerEncoder struct {
	global *sparseassoc.Encoder
	local  *localizedCompetitionEncoder
}

func newProviderEncoder(cfg Config) (*providerEncoder, error) {
	if cfg.LocalCompetition == nil {
		encoder, err := sparseassoc.NewEncoder(cfg.Sparse)
		if err != nil {
			return nil, err
		}
		return &providerEncoder{global: encoder}, nil
	}
	local, err := newLocalizedCompetitionEncoder(cfg.Sparse, *cfg.LocalCompetition)
	if err != nil {
		return nil, err
	}
	return &providerEncoder{local: local}, nil
}

func (e *providerEncoder) Encode(features []sparseassoc.Feature) (sparseassoc.Signature, error) {
	if e.local != nil {
		return e.local.Encode(features), nil
	}
	return e.global.Encode(features), nil
}

type localizedCompetitionEncoder struct {
	policy   LocalCompetitionPolicy
	families []string
	encoders map[uint16]*sparseassoc.Encoder
}

func newLocalizedCompetitionEncoder(
	cfg sparseassoc.Config,
	policy LocalCompetitionPolicy,
) (*localizedCompetitionEncoder, error) {
	families := make([]string, 0, len(policy.FamilyActive))
	activeWidths := make(map[uint16]struct{}, len(policy.FamilyActive)+1)
	for family, active := range policy.FamilyActive {
		families = append(families, family)
		activeWidths[active] = struct{}{}
	}
	sort.Strings(families)
	if policy.GlobalResidualActive > 0 {
		activeWidths[policy.GlobalResidualActive] = struct{}{}
	}

	encoders := make(map[uint16]*sparseassoc.Encoder, len(activeWidths))
	for active := range activeWidths {
		localCfg := cfg
		localCfg.Active = active
		encoder, err := sparseassoc.NewEncoder(localCfg)
		if err != nil {
			return nil, err
		}
		encoders[active] = encoder
	}
	return &localizedCompetitionEncoder{
		policy:   policy,
		families: families,
		encoders: encoders,
	}, nil
}

func (e *localizedCompetitionEncoder) Encode(features []sparseassoc.Feature) sparseassoc.Signature {
	groups := make(map[string][]sparseassoc.Feature)
	for _, feature := range features {
		family := featureFamily(feature.Channel)
		groups[family] = append(groups[family], feature)
	}

	parts := make([]sparseassoc.Signature, 0, len(e.families)+1)
	for _, family := range e.families {
		familyFeatures := groups[family]
		if len(familyFeatures) == 0 {
			continue
		}
		active := e.policy.FamilyActive[family]
		parts = append(parts, e.encoders[active].Encode(familyFeatures))
	}
	if e.policy.GlobalResidualActive > 0 {
		parts = append(parts, e.encoders[e.policy.GlobalResidualActive].Encode(features))
	}
	return mergeSparseSignatures(parts)
}

func mergeSparseSignatures(signatures []sparseassoc.Signature) sparseassoc.Signature {
	var merged []uint16
	for _, signature := range signatures {
		merged = append(merged, signature.Active...)
	}
	if len(merged) == 0 {
		return sparseassoc.Signature{}
	}
	sort.Slice(merged, func(i, j int) bool { return merged[i] < merged[j] })
	write := 1
	for read := 1; read < len(merged); read++ {
		if merged[read] == merged[write-1] {
			continue
		}
		merged[write] = merged[read]
		write++
	}
	return sparseassoc.Signature{Active: merged[:write]}
}

func validateProjectionBias(policy *ProjectionBiasPolicy) error {
	if policy == nil {
		return nil
	}
	if strings.TrimSpace(policy.PolicyRef) == "" {
		return errors.New("projection bias policyRef must not be empty")
	}
	if policy.MaxMultiplier <= 1 || policy.MaxMultiplier > MaxProjectionBiasMultiplier {
		return fmt.Errorf(
			"projection bias maxMultiplier must be in (1,%g]",
			MaxProjectionBiasMultiplier,
		)
	}
	if len(policy.Rules) == 0 || len(policy.Rules) > MaxProjectionBiasRules {
		return fmt.Errorf("projection bias rules must contain 1..%d entries", MaxProjectionBiasRules)
	}
	seen := make(map[projectionBiasSelector]struct{}, len(policy.Rules))
	for i, rule := range policy.Rules {
		if strings.TrimSpace(rule.Channel) == "" {
			return fmt.Errorf("projection bias rule %d channel must not be empty", i)
		}
		if strings.TrimSpace(rule.Key) == "" {
			return fmt.Errorf("projection bias rule %d key must not be empty", i)
		}
		if strings.TrimSpace(rule.ProvenanceRef) == "" {
			return fmt.Errorf("projection bias rule %d provenanceRef must not be empty", i)
		}
		if rule.Multiplier <= 1 || rule.Multiplier > policy.MaxMultiplier {
			return fmt.Errorf(
				"projection bias rule %d multiplier must be in (1,%g]",
				i,
				policy.MaxMultiplier,
			)
		}
		selector := projectionBiasSelector{channel: rule.Channel, key: rule.Key}
		if _, exists := seen[selector]; exists {
			return fmt.Errorf(
				"duplicate projection bias selector: channel=%q key=%q",
				rule.Channel,
				rule.Key,
			)
		}
		seen[selector] = struct{}{}
	}
	return nil
}

func cloneProjectionBias(policy *ProjectionBiasPolicy) *ProjectionBiasPolicy {
	if policy == nil {
		return nil
	}
	out := &ProjectionBiasPolicy{
		PolicyRef:     policy.PolicyRef,
		MaxMultiplier: policy.MaxMultiplier,
		Rules:         append([]ProjectionBiasRule(nil), policy.Rules...),
	}
	return out
}

func compileProjectionBias(policy *ProjectionBiasPolicy) map[projectionBiasSelector]float32 {
	if policy == nil {
		return nil
	}
	out := make(map[projectionBiasSelector]float32, len(policy.Rules))
	for _, rule := range policy.Rules {
		out[projectionBiasSelector{channel: rule.Channel, key: rule.Key}] = rule.Multiplier
	}
	return out
}

// applyProjectionBias mutates request-owned prepared features in place.
// featuresForItem and both normalization paths return slices owned by the
// current preparation call, so B3 does not require an additional copy.
func applyProjectionBias(
	features []sparseassoc.Feature,
	bias map[projectionBiasSelector]float32,
) []sparseassoc.Feature {
	if len(bias) == 0 {
		return features
	}
	for i := range features {
		multiplier, ok := bias[projectionBiasSelector{channel: features[i].Channel, key: features[i].Key}]
		if !ok {
			continue
		}
		features[i].Weight *= multiplier
	}
	return features
}

func (p *Provider) preparedFeatures(item Item) ([]sparseassoc.Feature, error) {
	features := featuresForItem(item)
	switch p.cfg.FeatureNormalization {
	case FeatureNormalizationNone:
	case FeatureNormalizationExactChannel:
		normalized, err := sparseassoc.NormalizeFeatures(features, sparseassoc.NormalizationConfig{
			Mode:             sparseassoc.NormalizationPerChannel,
			DenominatorFloor: p.cfg.NormalizationFloor,
		})
		if err != nil {
			return nil, err
		}
		features = normalized
	case FeatureNormalizationFamily:
		features = normalizeFeaturesByFamily(features, p.cfg.NormalizationFloor)
	default:
		return nil, errors.New("unsupported feature normalization mode")
	}
	return applyProjectionBias(features, p.projectionBias), nil
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
