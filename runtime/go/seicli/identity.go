package seicli

import (
	"fmt"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// Identity notice kinds. The Contracts do not say whether the envelope's
// kind/logical_ref must agree with the Decision Memory payload, nor whether one
// logical reference may appear in several records (#724). The runtime therefore
// does not reject such a store. resume and gate state what they found and do
// not pick one record over another.
const (
	NoticeEnvelopeKindMismatch       = "envelope_kind_mismatch"
	NoticeEnvelopeLogicalRefMismatch = "envelope_logical_ref_mismatch"
	NoticeDuplicateLogicalRef        = "duplicate_logical_ref"
)

// IdentityNotice reports a disagreement between the identities a store gives a
// record, or between records.
type IdentityNotice struct {
	Notice    string   `json:"notice"`
	RecordIDs []string `json:"record_ids"`
	Message   string   `json:"message"`
}

func decisionMemoryIdentity(rec semanticruntime.RuntimeRecord) (recordType string, ref semanticruntime.LogicalReference, ok bool) {
	doc := rec.Decision
	if doc == nil {
		return "", semanticruntime.LogicalReference{}, false
	}
	switch {
	case doc.Decision != nil:
		return "decision", doc.Decision.Ref, true
	case doc.Recommendation != nil:
		return "recommendation", doc.Recommendation.Ref, true
	}
	return "", semanticruntime.LogicalReference{}, false
}

func refLabel(ref semanticruntime.LogicalReference) string {
	label := ref.Kind + ":" + ref.ID
	if ref.Scope != "" {
		label += "@" + ref.Scope
	}
	return label
}

// recordIdentityNotices lists the disagreements between one record's envelope
// and its payload.
func recordIdentityNotices(rec semanticruntime.RuntimeRecord) []IdentityNotice {
	recordType, payloadRef, ok := decisionMemoryIdentity(rec)
	if !ok {
		return nil
	}
	env := rec.EnvelopeRecord
	var out []IdentityNotice
	if env.Kind != recordType {
		out = append(out, IdentityNotice{
			Notice: NoticeEnvelopeKindMismatch, RecordIDs: []string{env.RecordID},
			Message: fmt.Sprintf("the envelope kind is %q but the payload is a %s", env.Kind, recordType),
		})
	}
	if env.LogicalRef != nil && *env.LogicalRef != payloadRef {
		out = append(out, IdentityNotice{
			Notice: NoticeEnvelopeLogicalRefMismatch, RecordIDs: []string{env.RecordID},
			Message: fmt.Sprintf("the envelope logical_ref is %s but the payload ref is %s",
				refLabel(*env.LogicalRef), refLabel(payloadRef)),
		})
	}
	return out
}

// IdentityNotices lists, in record order, the identity disagreements in a
// bundle: envelope versus payload, and one logical reference recorded more than
// once. It never resolves them.
func IdentityNotices(bundle *semanticruntime.Bundle) []IdentityNotice {
	out := []IdentityNotice{}
	byRef := map[semanticruntime.LogicalReference][]string{}
	var order []semanticruntime.LogicalReference
	for _, rec := range bundle.Records {
		out = append(out, recordIdentityNotices(rec)...)
		recordType, payloadRef, ok := decisionMemoryIdentity(rec)
		if !ok {
			continue
		}
		key := semanticruntime.LogicalReference{Kind: recordType, ID: payloadRef.ID, Scope: payloadRef.Scope}
		if _, seen := byRef[key]; !seen {
			order = append(order, key)
		}
		byRef[key] = append(byRef[key], rec.EnvelopeRecord.RecordID)
	}
	for _, key := range order {
		ids := byRef[key]
		if len(ids) < 2 {
			continue
		}
		out = append(out, IdentityNotice{
			Notice: NoticeDuplicateLogicalRef, RecordIDs: ids,
			Message: fmt.Sprintf("%s is recorded %d times (records %s); the store does not say which is current",
				refLabel(key), len(ids), strings.Join(ids, ", ")),
		})
	}
	return out
}
