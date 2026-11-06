package seicli

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func lineageRecord(id string, l *semanticruntime.SemanticLineage) semanticruntime.RuntimeRecord {
	return semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{RecordID: id, Kind: "semantic_lineage"},
		Reference:      &semanticruntime.SemanticReferenceDocument{SemanticLineage: l},
	}
}

func TestResumeWithoutLineageShowsEmptyListAndZeroCount(t *testing.T) {
	view := BuildResume(recommendationBundle(nil, basisDecision("D1", "")))
	raw, _ := json.Marshal(view)
	if !strings.Contains(string(raw), `"lineages":[]`) || view.Coverage.LineageEntryCount != 0 {
		t.Errorf("want an empty lineages list: %s", raw)
	}
	var buf bytes.Buffer
	renderResume(&buf, view)
	if !strings.Contains(buf.String(), "Semantic Lineage, as recorded (0)") {
		t.Errorf("human output must say there are zero lineage entries:\n%s", buf.String())
	}
}

func TestResumeShowsSeparateLineageRecordAndDecisionHeldLineage(t *testing.T) {
	held := basisDecision("D2", "", semanticruntime.Reference{Kind: "artifact", ID: "A"})
	held.Lineage = &semanticruntime.SemanticLineage{
		Relation: "revises", From: decisionRef("D2", ""), To: decisionRef("D1", "s1"),
		BasisRefs: []semanticruntime.Reference{exactBasis("B", "s2", zeroDigest)},
	}
	bundle := recommendationBundle(nil, basisDecision("D1", "s1"), held)
	bundle.Records = append(bundle.Records, lineageRecord("L1", &semanticruntime.SemanticLineage{
		Relation: "supersedes", From: decisionRef("D3", ""), To: exactBasis("D2", "", otherDigest),
	}))
	view := BuildResume(bundle)
	if len(view.Lineages) != 2 || view.Coverage.LineageEntryCount != 2 {
		t.Fatalf("want 2 lineage entries, got %+v", view.Lineages)
	}
	h := view.Lineages[0]
	if h.HeldIn != "decision.lineage" || h.PayloadPointer != "/decision/lineage" || h.Relation != "revises" ||
		h.From.ID != "D2" || h.To.Scope != "s1" || h.SourceRecord.RecordID != "rec-1" || h.SourceRecord.JSONPointer != "/records/1" {
		t.Errorf("decision-held lineage: %+v", h)
	}
	if len(h.BasisReferences) != 1 || h.BasisReferences[0].Form != "exact" || h.BasisReferences[0].ContentDigest != zeroDigest {
		t.Errorf("lineage basis must keep its exact binding: %+v", h.BasisReferences)
	}
	l := view.Lineages[1]
	if l.HeldIn != "semantic_lineage" || l.PayloadPointer != "/semantic_lineage" || l.SourceRecord.RecordID != "L1" ||
		l.To.Form != "exact" || l.To.ContentDigest != otherDigest {
		t.Errorf("separate lineage record: %+v", l)
	}
	var buf bytes.Buffer
	renderResume(&buf, view)
	for _, want := range []string{
		"Semantic Lineage, as recorded (2)",
		"decision:D2 [logical] -> decision:D1 @s1 [logical] (revises)",
		"artifact:D2 [exact " + otherDigest + ", profile synthetic/1] (supersedes)",
		`held in semantic_lineage of record "L1"`,
	} {
		if !strings.Contains(buf.String(), want) {
			t.Errorf("human output missing %q:\n%s", want, buf.String())
		}
	}
}

func TestResumeDoesNotInterpretLineageDirectionOrEffect(t *testing.T) {
	// supersedes in either direction yields the same decisions; resume never
	// drops or flags a decision because of a lineage (#687 is not decided).
	for _, pair := range [][2]string{{"D2", "D1"}, {"D1", "D2"}} {
		bundle := recommendationBundle(nil, basisDecision("D1", ""), basisDecision("D2", ""))
		bundle.Records = append(bundle.Records, lineageRecord("L1", &semanticruntime.SemanticLineage{
			Relation: "supersedes", From: decisionRef(pair[0], ""), To: decisionRef(pair[1], ""),
		}))
		view := BuildResume(bundle)
		if len(view.Decisions) != 2 || view.Lineages[0].From.ID != pair[0] || view.Lineages[0].To.ID != pair[1] {
			t.Errorf("lineage must be shown as recorded: %+v", view)
		}
	}
}

func TestResumeCoverageReconcilesRecordCountWithShownRecords(t *testing.T) {
	bundle := recommendationBundle([]semanticruntime.LogicalReference{{Kind: "recommendation", ID: "R1"}},
		basisDecision("D1", ""))
	bundle.Records = append(bundle.Records,
		lineageRecord("L1", &semanticruntime.SemanticLineage{Relation: "withdraws", From: decisionRef("D1", ""), To: decisionRef("D0", "")}),
		semanticruntime.RuntimeRecord{EnvelopeRecord: semanticruntime.InterchangeRecord{RecordID: "C1", Kind: "capability_observation"},
			Capability: &semanticruntime.CapabilityObservationDocument{}},
		semanticruntime.RuntimeRecord{EnvelopeRecord: semanticruntime.InterchangeRecord{RecordID: "X1", Kind: "semantic_reference"},
			Reference: &semanticruntime.SemanticReferenceDocument{}},
		semanticruntime.RuntimeRecord{EnvelopeRecord: semanticruntime.InterchangeRecord{RecordID: "N1"}, Status: semanticruntime.RecordNotVerified},
	)
	view := BuildResume(bundle)
	shown := len(view.Decisions) + len(view.RecommendationsOpen) + len(view.RecommendationsRelied) +
		len(view.Lineages) + view.NotVerifiedRecordCount + view.Coverage.RecordsNotProjectedCount
	if shown != view.RecordCount {
		t.Errorf("record_count %d must equal the shown and counted records %d: %+v", view.RecordCount, shown, view.Coverage)
	}
	if view.Coverage.RecordsNotProjectedCount != 2 || len(view.Coverage.RecordsNotProjected) != 2 ||
		view.Coverage.RecordsNotProjected[0].Kind != "capability_observation" || view.Coverage.RecordsNotProjected[1].Kind != "semantic_reference" {
		t.Errorf("not projected kinds: %+v", view.Coverage.RecordsNotProjected)
	}
	var buf bytes.Buffer
	renderResume(&buf, view)
	if !strings.Contains(buf.String(), "2 verified record(s) are not shown by resume: capability_observation x1, semantic_reference x1") {
		t.Errorf("human output must explain the difference:\n%s", buf.String())
	}
}

func TestResumeKeepsAllExistingJSONFieldsWhenLineageIsAdded(t *testing.T) {
	raw, _ := json.Marshal(BuildResume(recommendationBundle(nil, basisDecision("D1", ""))))
	var got map[string]json.RawMessage
	_ = json.Unmarshal(raw, &got)
	for _, key := range []string{"bundle_id", "coverage", "record_count", "decisions", "recommendations_not_yet_relied_on",
		"recommendations_relied_on", "unresolved", "not_verified_record_count", "not_verified_records", "identity_notices"} {
		if _, ok := got[key]; !ok {
			t.Errorf("existing field %q must stay", key)
		}
	}
}
