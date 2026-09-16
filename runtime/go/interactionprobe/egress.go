package interactionprobe

import (
	"errors"
	"fmt"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// ContextEgressPlan は、external AI / Providerへ渡すcanonical contextを明示的に選択した
// Product-localな送出計画です。canonical store全体の暗黙送信やUniversal permission modelを
// 定義するものではありません。
type ContextEgressPlan struct {
	CanonicalDigest string
	Records         []AuditRecord
}

// PlanContextEgress は指定されたLogical Referenceだけをcanonical storeから取り出し、
// inspection可能な送出計画を作ります。Projection生成のみでcanonical stateは変更しません。
func (s *MachineSurface) PlanContextEgress(selected []semanticruntime.LogicalReference) (ContextEgressPlan, error) {
	if s == nil || s.store == nil {
		return ContextEgressPlan{}, errors.New("machine surface requires a canonical store")
	}
	if len(selected) == 0 {
		return ContextEgressPlan{}, errors.New("context egress requires at least one selected canonical reference")
	}

	digest, err := s.store.Digest()
	if err != nil {
		return ContextEgressPlan{}, err
	}
	plan := ContextEgressPlan{
		CanonicalDigest: digest,
		Records:         make([]AuditRecord, 0, len(selected)),
	}
	seen := make(map[semanticruntime.LogicalReference]struct{}, len(selected))
	for _, ref := range selected {
		if ref.Kind == "" || ref.ID == "" {
			return ContextEgressPlan{}, errors.New("selected context requires complete logical references")
		}
		if _, duplicate := seen[ref]; duplicate {
			return ContextEgressPlan{}, fmt.Errorf("duplicate selected context reference: %s/%s", ref.Kind, ref.ID)
		}
		seen[ref] = struct{}{}

		record, found, err := s.store.Find(ref)
		if err != nil {
			return ContextEgressPlan{}, err
		}
		if !found {
			return ContextEgressPlan{}, fmt.Errorf("selected canonical context not found: %s/%s", ref.Kind, ref.ID)
		}
		plan.Records = append(plan.Records, auditRecord(record))
	}
	return plan, nil
}

// ReceiveExternalRecommendation はexternal responseをcanonical writeへ直結せず、
// egress時点のsnapshotを基準とするprovisional Recommendationとして受け取ります。
// egress後にcanonical stateが変化していれば、既存stale-draft境界によりCommit時に拒否されます。
func (s *MachineSurface) ReceiveExternalRecommendation(plan ContextEgressPlan, input RecommendationInput) (*ProvisionalRecommendation, error) {
	if s == nil || s.store == nil {
		return nil, errors.New("machine surface requires a canonical store")
	}
	if plan.CanonicalDigest == "" || len(plan.Records) == 0 {
		return nil, errors.New("external recommendation requires an inspected context egress plan")
	}
	if err := validateProvisionalRecommendationInput(input); err != nil {
		return nil, err
	}
	return &ProvisionalRecommendation{
		surface:             s,
		input:               cloneRecommendationInput(input),
		baseCanonicalDigest: plan.CanonicalDigest,
	}, nil
}
