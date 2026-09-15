package interactionprobe

import (
	"encoding/json"
	"errors"
	"fmt"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

const decisionReviewCheckpointExtension = "interactionprobe.change_review_checkpoint/v1"

type decisionReviewCheckpoint struct {
	CanonicalRefs []semanticruntime.LogicalReference `json:"canonical_refs"`
}

// ChangeReviewProjection は、Decision時点のhistorical contextと、
// その後canonical stateへ新たに導入されたrecordを分離して示すProduct-local Projectionです。
//
// CanonicalChangesは現実世界のevent timeを表しません。Decision記録時に明示保存した
// checkpointに存在せず、現在のcanonical stateには存在するrecordを示します。
// record順序やObservedAtから「Decision後」を推測しません。
type ChangeReviewProjection struct {
	Resume           ResumeProjection
	CanonicalChanges []AuditRecord
}

// RecordDecisionWithReviewCheckpoint は、Decisionと同じcanonical recordのextensionsへ
// Product-localなreview checkpointを埋め込みます。checkpointはSemantic Revision、
// Exact Binding、Universal Contractではありません。
//
// snapshotを別recordとして後続commitしないため、Decisionだけが保存されcheckpointが
// 欠けるpartial stateをこのprobe API自身から作りません。
func (s *HumanSurface) RecordDecisionWithReviewCheckpoint(input DecisionInput) error {
	if s == nil || s.store == nil {
		return errors.New("human surface requires a canonical store")
	}

	records, err := s.store.Records()
	if err != nil {
		return err
	}
	checkpoint := decisionReviewCheckpoint{
		CanonicalRefs: make([]semanticruntime.LogicalReference, 0, len(records)+1),
	}
	seen := make(map[semanticruntime.LogicalReference]struct{}, len(records)+1)
	for _, record := range records {
		logical, ok := recordLogicalRef(record)
		if !ok {
			continue
		}
		if _, exists := seen[logical]; exists {
			continue
		}
		seen[logical] = struct{}{}
		checkpoint.CanonicalRefs = append(checkpoint.CanonicalRefs, logical)
	}
	if input.Ref.Kind != "" && input.Ref.ID != "" {
		if _, exists := seen[input.Ref]; !exists {
			checkpoint.CanonicalRefs = append(checkpoint.CanonicalRefs, input.Ref)
		}
	}

	doc := &semanticruntime.DecisionMemoryDocument{
		Contract:   semanticruntime.ContractDecisionMemory,
		RecordType: "decision",
		Decision: &semanticruntime.Decision{
			Ref:                input.Ref,
			Statement:          input.Statement,
			ContextRefs:        refs(input.ContextRefs),
			BasisRefs:          refs(input.BasisRefs),
			RecommendationRefs: refs(input.RecommendationRefs),
			UnresolvedRefs:     refs(input.UnresolvedRefs),
			ResponsibilityRefs: refs(input.ResponsibilityRefs),
			Rationale:          input.Rationale,
			Extensions: map[string]any{
				decisionReviewCheckpointExtension: checkpoint,
			},
		},
	}
	return s.store.Add(semanticruntime.RuntimeRecord{Decision: doc})
}

// ChangeReviewProjection はDecision recordに保存された明示checkpointから差分を再構成します。
// checkpointが存在しないlegacy Decisionではrecord順序等へfallbackせず、fail closedします。
func (s *HumanSurface) ChangeReviewProjection(decisionRef semanticruntime.LogicalReference) (ChangeReviewProjection, error) {
	if s == nil || s.store == nil {
		return ChangeReviewProjection{}, errors.New("human surface requires a canonical store")
	}

	resume, err := s.ResumeProjection(decisionRef)
	if err != nil {
		return ChangeReviewProjection{}, err
	}

	record, found, err := s.store.Find(decisionRef)
	if err != nil {
		return ChangeReviewProjection{}, err
	}
	if !found || record.Decision == nil || record.Decision.Decision == nil {
		return ChangeReviewProjection{}, fmt.Errorf("decision not found for change review: %s/%s", decisionRef.Kind, decisionRef.ID)
	}

	checkpoint, err := readDecisionReviewCheckpoint(*record.Decision.Decision)
	if err != nil {
		return ChangeReviewProjection{}, err
	}
	known := make(map[semanticruntime.LogicalReference]struct{}, len(checkpoint.CanonicalRefs))
	for _, logical := range checkpoint.CanonicalRefs {
		known[logical] = struct{}{}
	}

	audit, err := s.AuditView()
	if err != nil {
		return ChangeReviewProjection{}, err
	}
	projection := ChangeReviewProjection{Resume: resume}
	for _, candidate := range audit.Records {
		if _, existedAtDecision := known[candidate.Ref]; existedAtDecision {
			continue
		}
		projection.CanonicalChanges = append(projection.CanonicalChanges, candidate)
	}
	return projection, nil
}

func readDecisionReviewCheckpoint(decision semanticruntime.Decision) (decisionReviewCheckpoint, error) {
	value, ok := decision.Extensions[decisionReviewCheckpointExtension]
	if !ok {
		return decisionReviewCheckpoint{}, errors.New("change review requires an explicit decision review checkpoint")
	}
	data, err := json.Marshal(value)
	if err != nil {
		return decisionReviewCheckpoint{}, fmt.Errorf("encode decision review checkpoint: %w", err)
	}
	var checkpoint decisionReviewCheckpoint
	if err := json.Unmarshal(data, &checkpoint); err != nil {
		return decisionReviewCheckpoint{}, fmt.Errorf("decode decision review checkpoint: %w", err)
	}
	if len(checkpoint.CanonicalRefs) == 0 {
		return decisionReviewCheckpoint{}, errors.New("decision review checkpoint requires canonical references")
	}
	return checkpoint, nil
}
