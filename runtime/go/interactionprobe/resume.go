package interactionprobe

import (
	"errors"
	"fmt"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// ResumeProjection は、canonical stateだけから再構成するProduct-localな再開用Projectionです。
// 新しいUniversal Contractやcanonical summaryを定義するものではありません。
type ResumeProjection struct {
	CanonicalDigest string
	Inquiry         AuditRecord
	Decision        AuditRecord
	Basis           []AuditRecord
	Recommendations []AuditRecord
	Unresolved      []AuditRecord
	MissingRefs     []semanticruntime.LogicalReference
}

// ResumeProjection は明示的に指定されたDecisionを中心に、canonical stateから
// Inquiry / basis / recommendation / unresolvedを再解決します。
//
// current Decisionをrecord順序等から推測しません。どのDecisionへ戻るかは呼び出し側が
// 明示する必要があります。また、参照先がcanonical storeに存在しない場合は黙って落とさず
// MissingRefsへ残します。
func (s *HumanSurface) ResumeProjection(decisionRef semanticruntime.LogicalReference) (ResumeProjection, error) {
	if s == nil || s.store == nil {
		return ResumeProjection{}, errors.New("human surface requires a canonical store")
	}
	if decisionRef.Kind == "" || decisionRef.ID == "" {
		return ResumeProjection{}, errors.New("resume projection requires a decision reference")
	}

	audit, err := s.AuditView()
	if err != nil {
		return ResumeProjection{}, err
	}

	index := make(map[semanticruntime.LogicalReference]AuditRecord, len(audit.Records))
	inquiries := make([]AuditRecord, 0, 1)
	for _, record := range audit.Records {
		index[record.Ref] = record
		if record.Kind == "inquiry" {
			inquiries = append(inquiries, record)
		}
	}
	if len(inquiries) != 1 {
		return ResumeProjection{}, fmt.Errorf("resume projection requires exactly one inquiry in the current probe, got %d", len(inquiries))
	}

	decision, ok := index[decisionRef]
	if !ok || decision.Kind != "decision" {
		return ResumeProjection{}, fmt.Errorf("decision not found for resume projection: %s/%s", decisionRef.Kind, decisionRef.ID)
	}

	projection := ResumeProjection{
		CanonicalDigest: audit.CanonicalDigest,
		Inquiry:         inquiries[0],
		Decision:        decision,
	}

	projection.Basis = resolveResumeRefs(decision.BasisRefs, index, &projection.MissingRefs)
	projection.Recommendations = resolveResumeRefs(decision.RecommendationRefs, index, &projection.MissingRefs)
	projection.Unresolved = resolveResumeRefs(decision.UnresolvedRefs, index, &projection.MissingRefs)

	return projection, nil
}

func resolveResumeRefs(
	refs []semanticruntime.LogicalReference,
	index map[semanticruntime.LogicalReference]AuditRecord,
	missing *[]semanticruntime.LogicalReference,
) []AuditRecord {
	resolved := make([]AuditRecord, 0, len(refs))
	for _, logical := range refs {
		record, ok := index[logical]
		if !ok {
			appendMissingResumeRef(missing, logical)
			continue
		}
		resolved = append(resolved, record)
	}
	return resolved
}

func appendMissingResumeRef(missing *[]semanticruntime.LogicalReference, logical semanticruntime.LogicalReference) {
	for _, existing := range *missing {
		if existing == logical {
			return
		}
	}
	*missing = append(*missing, logical)
}
