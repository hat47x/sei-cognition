package interactionprobe

import (
	"errors"
	"fmt"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// WorkingSetProjection は、canonical record間の明示Referenceから導出する
// Product-localな関連意味の集合です。Workspace / Case等のUniversal semantic entityを
// 定義せず、pin / recent / filter等のSurface-local metadataもauthorityにしません。
type WorkingSetProjection struct {
	CanonicalDigest string
	RootDecision    semanticruntime.LogicalReference
	Records         []AuditRecord
	MissingRefs     []semanticruntime.LogicalReference
}

// WorkingSetProjection は指定Decisionをrootとして、canonical record間の明示Referenceを
// 双方向にたどり、同じ判断仕事として関連するrecordを再構成します。
// record順序やUI selectionから関連性を推定しません。
func (s *HumanSurface) WorkingSetProjection(decisionRef semanticruntime.LogicalReference) (WorkingSetProjection, error) {
	if s == nil || s.store == nil {
		return WorkingSetProjection{}, errors.New("human surface requires a canonical store")
	}
	if decisionRef.Kind == "" || decisionRef.ID == "" {
		return WorkingSetProjection{}, errors.New("working set projection requires a decision reference")
	}

	audit, err := s.AuditView()
	if err != nil {
		return WorkingSetProjection{}, err
	}
	index := make(map[semanticruntime.LogicalReference]AuditRecord, len(audit.Records))
	for _, record := range audit.Records {
		index[record.Ref] = record
	}
	root, ok := index[decisionRef]
	if !ok || root.Kind != "decision" {
		return WorkingSetProjection{}, fmt.Errorf("decision not found for working set projection: %s/%s", decisionRef.Kind, decisionRef.ID)
	}

	reachable := map[semanticruntime.LogicalReference]struct{}{decisionRef: {}}
	queue := []semanticruntime.LogicalReference{decisionRef}
	missing := make([]semanticruntime.LogicalReference, 0)

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		record := index[current]

		for _, ref := range auditRecordRefs(record) {
			if _, exists := index[ref]; !exists {
				appendUniqueLogicalRef(&missing, ref)
				continue
			}
			if _, seen := reachable[ref]; !seen {
				reachable[ref] = struct{}{}
				queue = append(queue, ref)
			}
		}

		// reverse edgeも明示Referenceに基づくderived relationとして辿る。
		for _, candidate := range audit.Records {
			if _, seen := reachable[candidate.Ref]; seen {
				continue
			}
			if containsLogicalRef(auditRecordRefs(candidate), current) {
				reachable[candidate.Ref] = struct{}{}
				queue = append(queue, candidate.Ref)
			}
		}
	}

	projection := WorkingSetProjection{
		CanonicalDigest: audit.CanonicalDigest,
		RootDecision:    decisionRef,
		MissingRefs:     missing,
	}
	for _, record := range audit.Records {
		if _, ok := reachable[record.Ref]; ok {
			projection.Records = append(projection.Records, record)
		}
	}
	return projection, nil
}

func auditRecordRefs(record AuditRecord) []semanticruntime.LogicalReference {
	refs := make([]semanticruntime.LogicalReference, 0,
		len(record.ContextRefs)+len(record.BasisRefs)+len(record.RecommendationRefs)+
			len(record.UnresolvedRefs)+len(record.ResponsibilityRefs)+len(record.ProvenanceRefs)+
			len(record.InputRefs)+len(record.OutputRefs)+len(record.ResidualRefs))
	refs = append(refs, record.ContextRefs...)
	refs = append(refs, record.BasisRefs...)
	refs = append(refs, record.RecommendationRefs...)
	refs = append(refs, record.UnresolvedRefs...)
	refs = append(refs, record.ResponsibilityRefs...)
	refs = append(refs, record.ProvenanceRefs...)
	refs = append(refs, record.InputRefs...)
	refs = append(refs, record.OutputRefs...)
	refs = append(refs, record.ResidualRefs...)
	return refs
}

func containsLogicalRef(refs []semanticruntime.LogicalReference, target semanticruntime.LogicalReference) bool {
	for _, ref := range refs {
		if ref == target {
			return true
		}
	}
	return false
}

func appendUniqueLogicalRef(values *[]semanticruntime.LogicalReference, value semanticruntime.LogicalReference) {
	if value.Kind == "" || value.ID == "" {
		return
	}
	for _, existing := range *values {
		if existing == value {
			return
		}
	}
	*values = append(*values, value)
}
