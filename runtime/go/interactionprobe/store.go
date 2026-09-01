package interactionprobe

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

// CanonicalStore は、reference probe だけで使う単一Inquiry向けの共有ストアです。
// 新しいUniversal Contractやproduction Storageを定義するものではありません。
// 保存する耐久的意味には、既存semanticruntimeの型をそのまま利用します。
type CanonicalStore struct {
	records []semanticruntime.RuntimeRecord
}

func NewCanonicalStore() *CanonicalStore {
	return &CanonicalStore{}
}

// Add は既存Contractで表現できるrecordをsemanticruntimeで再検証してから追加します。
// 未対応recordはopaqueなnot_verified recordとしてのみ保持できます。
func (s *CanonicalStore) Add(record semanticruntime.RuntimeRecord) error {
	if s == nil {
		return errors.New("canonical store is required")
	}

	normalized, err := normalizeRecord(record)
	if err != nil {
		return err
	}
	ref, ok := recordLogicalRef(normalized)
	if !ok {
		return errors.New("record requires a logical reference")
	}
	if _, exists, err := s.Find(ref); err != nil {
		return err
	} else if exists {
		return fmt.Errorf("duplicate canonical record: %s/%s", ref.Kind, ref.ID)
	}

	cloned, err := cloneRecord(normalized)
	if err != nil {
		return err
	}
	s.records = append(s.records, cloned)
	return nil
}

// Records はSurface側からcanonical stateを直接書き換えられないよう、複製を返します。
func (s *CanonicalStore) Records() ([]semanticruntime.RuntimeRecord, error) {
	if s == nil {
		return nil, errors.New("canonical store is required")
	}
	out := make([]semanticruntime.RuntimeRecord, 0, len(s.records))
	for _, record := range s.records {
		cloned, err := cloneRecord(record)
		if err != nil {
			return nil, err
		}
		out = append(out, cloned)
	}
	return out, nil
}

func (s *CanonicalStore) Find(ref semanticruntime.LogicalReference) (semanticruntime.RuntimeRecord, bool, error) {
	if s == nil {
		return semanticruntime.RuntimeRecord{}, false, errors.New("canonical store is required")
	}
	if ref.Kind == "" || ref.ID == "" {
		return semanticruntime.RuntimeRecord{}, false, errors.New("logical reference requires kind and id")
	}
	for _, record := range s.records {
		candidate, ok := recordLogicalRef(record)
		if !ok || candidate != ref {
			continue
		}
		cloned, err := cloneRecord(record)
		return cloned, true, err
	}
	return semanticruntime.RuntimeRecord{}, false, nil
}

// Digest はProjection生成やSurface-local stateの変更がcanonical stateを書き換えていないことを
// probeで比較するための指標です。SOZAのRepresentation ProfileやExact Bindingではありません。
func (s *CanonicalStore) Digest() (string, error) {
	records, err := s.Records()
	if err != nil {
		return "", err
	}
	data, err := json.Marshal(records)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func normalizeRecord(record semanticruntime.RuntimeRecord) (semanticruntime.RuntimeRecord, error) {
	typed := 0
	if record.Decision != nil {
		typed++
	}
	if record.Capability != nil {
		typed++
	}
	if record.Reference != nil {
		typed++
	}
	if record.CognitiveMethod != nil {
		typed++
	}
	if typed > 1 {
		return semanticruntime.RuntimeRecord{}, errors.New("interaction probe record must contain at most one typed semantic document")
	}

	if typed == 0 {
		if record.Status != semanticruntime.RecordNotVerified {
			return semanticruntime.RuntimeRecord{}, errors.New("opaque interaction probe record must remain not_verified")
		}
		if _, ok := recordLogicalRef(record); !ok {
			return semanticruntime.RuntimeRecord{}, errors.New("opaque interaction probe record requires a logical reference")
		}
		return cloneRecord(record)
	}

	var document any
	switch {
	case record.Decision != nil:
		document = record.Decision
	case record.Capability != nil:
		document = record.Capability
	case record.Reference != nil:
		document = record.Reference
	case record.CognitiveMethod != nil:
		document = record.CognitiveMethod
	}

	payload, err := json.Marshal(document)
	if err != nil {
		return semanticruntime.RuntimeRecord{}, err
	}
	validated, err := semanticruntime.LoadStandalone(payload)
	if err != nil {
		return semanticruntime.RuntimeRecord{}, fmt.Errorf("semanticruntime validation failed: %w", err)
	}
	validated.EnvelopeRecord = record.EnvelopeRecord
	return validated, nil
}

func cloneRecord(record semanticruntime.RuntimeRecord) (semanticruntime.RuntimeRecord, error) {
	data, err := json.Marshal(record)
	if err != nil {
		return semanticruntime.RuntimeRecord{}, err
	}
	var cloned semanticruntime.RuntimeRecord
	if err := json.Unmarshal(data, &cloned); err != nil {
		return semanticruntime.RuntimeRecord{}, err
	}
	return cloned, nil
}

func recordLogicalRef(record semanticruntime.RuntimeRecord) (semanticruntime.LogicalReference, bool) {
	if record.EnvelopeRecord.LogicalRef != nil {
		return *record.EnvelopeRecord.LogicalRef, true
	}
	if record.Decision != nil {
		if record.Decision.Decision != nil {
			return record.Decision.Decision.Ref, true
		}
		if record.Decision.Recommendation != nil {
			return record.Decision.Recommendation.Ref, true
		}
	}
	if record.Capability != nil {
		return record.Capability.Observation.Ref, true
	}
	if record.CognitiveMethod != nil {
		if record.CognitiveMethod.MethodDefinition != nil {
			return record.CognitiveMethod.MethodDefinition.Ref, true
		}
		if record.CognitiveMethod.MethodRealization != nil {
			return record.CognitiveMethod.MethodRealization.Ref, true
		}
		if record.CognitiveMethod.MethodApplication != nil {
			return record.CognitiveMethod.MethodApplication.Ref, true
		}
	}
	if record.Reference != nil && record.Reference.LogicalReference != nil {
		return *record.Reference.LogicalReference, true
	}
	return semanticruntime.LogicalReference{}, false
}

func ref(value semanticruntime.LogicalReference) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: value.Kind, ID: value.ID, Scope: value.Scope}
}

func refs(values []semanticruntime.LogicalReference) []semanticruntime.Reference {
	out := make([]semanticruntime.Reference, 0, len(values))
	for _, value := range values {
		out = append(out, ref(value))
	}
	return out
}

func logicalRefs(values []semanticruntime.Reference) []semanticruntime.LogicalReference {
	out := make([]semanticruntime.LogicalReference, 0, len(values))
	for _, value := range values {
		logical, ok := value.LogicalIdentity()
		if ok {
			out = append(out, logical)
		}
	}
	return out
}
