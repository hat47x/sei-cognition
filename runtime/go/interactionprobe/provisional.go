package interactionprobe

import (
	"errors"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// ProvisionalRecommendation は、AI等が生成したRecommendation候補をcanonical commit前に
// 保持するProduct-localなdraftです。Universal Contractやcanonical historyではありません。
type ProvisionalRecommendation struct {
	surface   *MachineSurface
	input     RecommendationInput
	dismissed bool
	committed bool
}

// RecommendationChangePreview は、provisional Recommendationをcanonicalへcommitした場合に
// 何が追加されるかをSurfaceから確認するためのProduct-localなpreviewです。
type RecommendationChangePreview struct {
	Ref                semanticruntime.LogicalReference
	Statement          string
	ContextRefs        []semanticruntime.LogicalReference
	BasisRefs          []semanticruntime.LogicalReference
	ResponsibilityRefs []semanticruntime.LogicalReference
	Rationale          string
}

// ProposeRecommendation はcanonical storeを書き換えず、Recommendation候補をdraftとして返します。
// MachineSurface.RecordRecommendationは明示的なcanonical write APIとして別に残します。
func (s *MachineSurface) ProposeRecommendation(input RecommendationInput) (*ProvisionalRecommendation, error) {
	if s == nil || s.store == nil {
		return nil, errors.New("machine surface requires a canonical store")
	}
	if err := validateProvisionalRecommendationInput(input); err != nil {
		return nil, err
	}
	return &ProvisionalRecommendation{surface: s, input: cloneRecommendationInput(input)}, nil
}

// Preview はcanonical stateを変更せず、現在のdraftが意味上どのRecommendationを追加するかを返します。
func (d *ProvisionalRecommendation) Preview() (RecommendationChangePreview, error) {
	if err := d.ensurePending(); err != nil {
		return RecommendationChangePreview{}, err
	}
	input := cloneRecommendationInput(d.input)
	return RecommendationChangePreview{
		Ref:                input.Ref,
		Statement:          input.Statement,
		ContextRefs:        input.ContextRefs,
		BasisRefs:          input.BasisRefs,
		ResponsibilityRefs: input.ResponsibilityRefs,
		Rationale:          input.Rationale,
	}, nil
}

// Revise はdraftだけを置き換えます。canonical stateには書き込みません。
func (d *ProvisionalRecommendation) Revise(input RecommendationInput) error {
	if err := d.ensurePending(); err != nil {
		return err
	}
	if err := validateProvisionalRecommendationInput(input); err != nil {
		return err
	}
	d.input = cloneRecommendationInput(input)
	return nil
}

// Dismiss はdraftを却下します。却下そのものをcanonical Recommendationとして保存しません。
func (d *ProvisionalRecommendation) Dismiss() error {
	if err := d.ensurePending(); err != nil {
		return err
	}
	d.dismissed = true
	return nil
}

// Commit は現在のdraftを既存の明示canonical write境界へ渡します。
// validationやduplicate rejectionに失敗した場合、draftをcommitted扱いにはしません。
func (d *ProvisionalRecommendation) Commit() error {
	if err := d.ensurePending(); err != nil {
		return err
	}
	if d.surface == nil || d.surface.store == nil {
		return errors.New("provisional recommendation requires a machine surface")
	}
	if err := d.surface.RecordRecommendation(cloneRecommendationInput(d.input)); err != nil {
		return err
	}
	d.committed = true
	return nil
}

func (d *ProvisionalRecommendation) ensurePending() error {
	if d == nil {
		return errors.New("provisional recommendation is required")
	}
	if d.dismissed {
		return errors.New("provisional recommendation was dismissed")
	}
	if d.committed {
		return errors.New("provisional recommendation was already committed")
	}
	return nil
}

func validateProvisionalRecommendationInput(input RecommendationInput) error {
	if input.Ref.Kind != "recommendation" || strings.TrimSpace(input.Ref.ID) == "" {
		return errors.New("provisional recommendation requires a recommendation logical reference")
	}
	if strings.TrimSpace(input.Statement) == "" {
		return errors.New("provisional recommendation requires a statement")
	}
	return nil
}

func cloneRecommendationInput(input RecommendationInput) RecommendationInput {
	cloned := input
	cloned.ContextRefs = append([]semanticruntime.LogicalReference(nil), input.ContextRefs...)
	cloned.BasisRefs = append([]semanticruntime.LogicalReference(nil), input.BasisRefs...)
	cloned.ResponsibilityRefs = append([]semanticruntime.LogicalReference(nil), input.ResponsibilityRefs...)
	return cloned
}
