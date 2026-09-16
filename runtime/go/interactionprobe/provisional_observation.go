package interactionprobe

import (
	"encoding/json"
	"errors"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// ProvisionalObservation は、AI等のsuggestionをObservationへ再分類した後も
// canonical commit前に保持するProduct-localなdraftです。
// Universal Observation Contractやcanonical historyを新設するものではありません。
type ProvisionalObservation struct {
	surface             *MachineSurface
	ref                 semanticruntime.LogicalReference
	text                string
	baseCanonicalDigest string
	dismissed           bool
	committed           bool
}

// ObservationChangePreview は、Observationとしてcommitした場合の意味変更を
// canonical stateを書き換えずに確認するためのProduct-local previewです。
type ObservationChangePreview struct {
	Ref  semanticruntime.LogicalReference
	Text string
}

// ReclassifyAsObservation は、Recommendation候補だったdraftをObservation候補へ
// transientに再分類します。元Recommendation draftはdismissedとなり、両方を誤って
// canonicalizeできないようにします。snapshot preconditionは引き継ぎます。
func (d *ProvisionalRecommendation) ReclassifyAsObservation(ref semanticruntime.LogicalReference, text string) (*ProvisionalObservation, error) {
	if err := d.ensurePending(); err != nil {
		return nil, err
	}
	if ref.Kind != "observation" || strings.TrimSpace(ref.ID) == "" {
		return nil, errors.New("provisional observation requires an observation logical reference")
	}
	if strings.TrimSpace(text) == "" {
		return nil, errors.New("provisional observation requires text")
	}
	observation := &ProvisionalObservation{
		surface:             d.surface,
		ref:                 ref,
		text:                text,
		baseCanonicalDigest: d.baseCanonicalDigest,
	}
	d.dismissed = true
	return observation, nil
}

func (d *ProvisionalObservation) Preview() (ObservationChangePreview, error) {
	if err := d.ensurePending(); err != nil {
		return ObservationChangePreview{}, err
	}
	return ObservationChangePreview{Ref: d.ref, Text: d.text}, nil
}

// Revise はObservation draftだけを修正し、canonical stateへは触れません。
func (d *ProvisionalObservation) Revise(text string) error {
	if err := d.ensurePending(); err != nil {
		return err
	}
	if strings.TrimSpace(text) == "" {
		return errors.New("provisional observation requires text")
	}
	d.text = text
	return nil
}

// Dismiss はObservation draftを破棄し、negative factやDecisionとして保存しません。
func (d *ProvisionalObservation) Dismiss() error {
	if err := d.ensurePending(); err != nil {
		return err
	}
	d.dismissed = true
	return nil
}

// Commit は明示操作時だけopaqueなnot_verified Observationをcanonicalへ追加します。
// draft作成元snapshotからcanonical stateが変わっていれば既存stale境界と同じく拒否します。
func (d *ProvisionalObservation) Commit() error {
	if err := d.ensurePending(); err != nil {
		return err
	}
	if d.surface == nil || d.surface.store == nil {
		return errors.New("provisional observation requires a machine surface")
	}
	currentDigest, err := d.surface.store.Digest()
	if err != nil {
		return err
	}
	if currentDigest != d.baseCanonicalDigest {
		return errStaleProvisionalRecommendation
	}
	payload, err := json.Marshal(opaqueTextPayload{Text: d.text})
	if err != nil {
		return err
	}
	ref := d.ref
	if err := d.surface.store.Add(semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{Kind: "observation", LogicalRef: &ref, Payload: payload},
		Status:         semanticruntime.RecordNotVerified,
	}); err != nil {
		return err
	}
	d.committed = true
	return nil
}

func (d *ProvisionalObservation) ensurePending() error {
	if d == nil {
		return errors.New("provisional observation is required")
	}
	if d.dismissed {
		return errors.New("provisional observation was dismissed")
	}
	if d.committed {
		return errors.New("provisional observation was already committed")
	}
	return nil
}
