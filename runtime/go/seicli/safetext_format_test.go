package seicli

import (
	"fmt"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// cp builds a string from code points, so this file holds no invisible
// characters itself.
func cp(points ...rune) string { return string(points) }

// esc is the visible form safeText writes for a code point.
func esc(point rune) string {
	if point > 0xFFFF {
		return fmt.Sprintf("%cu{%x}", '\\', point)
	}
	return fmt.Sprintf("%cu%04x", '\\', point)
}

const (
	rlo  = 0x202e // right-to-left override
	pdf  = 0x202c // pop directional formatting
	zwsp = 0x200b // zero width space
	lri  = 0x2066 // left-to-right isolate
	pdi  = 0x2069 // pop directional isolate
	bom  = 0xfeff
	lrm  = 0x200e
	rlm  = 0x200f
	wj   = 0x2060 // word joiner
	tagA = 0xe0041
	shy  = 0x00ad
	zwj  = 0x200d
	vs16 = 0xfe0f
	vs15 = 0xfe0e
)

// #774: format characters that change how text reads, without being visible,
// are written as escapes in the human view.
func TestSafeTextEscapesFormatCharacters(t *testing.T) {
	cases := map[string]string{
		"approve " + cp(rlo) + "denied" + cp(pdf) + " ok":                  "approve " + esc(rlo) + "denied" + esc(pdf) + " ok",
		"a" + cp(zwsp) + "b" + cp(lri) + "c" + cp(pdi) + "d":               "a" + esc(zwsp) + "b" + esc(lri) + "c" + esc(pdi) + "d",
		"a" + cp(bom) + "b" + cp(lrm) + "c" + cp(rlm) + "d" + cp(wj) + "e": "a" + esc(bom) + "b" + esc(lrm) + "c" + esc(rlm) + "d" + esc(wj) + "e",
		"a" + cp(tagA) + "b":      "a" + esc(tagA) + "b",
		"soft" + cp(shy) + "hyph": "soft" + esc(shy) + "hyph",
	}
	for in, want := range cases {
		if got := safeText(in); got != want {
			t.Errorf("safeText(%q) = %q, want %q", in, got, want)
		}
	}
	if esc(tagA) != "\\u{e0041}" || esc(rlo) != "\\u202e" {
		t.Fatalf("esc helper is wrong: %q %q", esc(tagA), esc(rlo))
	}
}

// Ordinary Japanese text, combining voiced marks, ZWJ emoji sequences and
// variation selectors are not rewritten.
func TestSafeTextKeepsLegitimateText(t *testing.T) {
	for _, in := range []string{
		"判断を引き継ぐ。ガギグゲゴ",
		"か" + cp(0x3099) + " は" + cp(0x309a),
		cp(0x1F468, zwj, 0x1F469, zwj, 0x1F467),
		cp(0x2764, vs16) + " " + cp(0x2708, vs15),
		cp(0x845b, 0xe0100),
	} {
		if got := safeText(in); got != in {
			t.Errorf("safeText(%q) = %q, want it unchanged", in, got)
		}
	}
}

func TestResumeHumanViewEscapesFormatCharactersInEveryField(t *testing.T) {
	statement := "approve " + cp(rlo) + "denied" + cp(pdf) + " ok" + cp(zwsp)
	bundle := forgedBundle()
	bundle.Records[0].Decision.Recommendation.Statement = statement
	bundle.Records[0].EnvelopeRecord.ProvenanceRefs = []semanticruntime.LogicalReference{{Kind: "agent", ID: "tool" + cp(lri) + "x"}}
	view := BuildResume(bundle)
	var buf strings.Builder
	renderResume(&buf, view)
	out := buf.String()
	if strings.ContainsAny(out, cp(rlo, pdf, zwsp, lri)) {
		t.Errorf("raw format character in the human view: %q", out)
	}
	for _, want := range []string{
		"approve " + esc(rlo) + "denied" + esc(pdf) + " ok" + esc(zwsp),
		"tool" + esc(lri) + "x",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("want %q in the human view:\n%s", want, out)
		}
	}
	if view.RecommendationsOpen[0].Statement != statement {
		t.Errorf("BuildResume must keep the exact value for --json: %q", view.RecommendationsOpen[0].Statement)
	}
}

func TestGateBasisNoteEscapesFormatCharacters(t *testing.T) {
	id := "D" + cp(rlo) + "-04" + cp(zwsp)
	d := decisionWithBasis("D1", semanticruntime.Reference{Kind: "artifact", ID: id})
	got := CheckDecision(recommendationBundle(nil, d), "D1", GatePolicy{})
	notes := basisNotesOf(got)
	want := "basis artifact:D" + esc(rlo) + "-04" + esc(zwsp) + ":"
	if len(notes) != 1 || !strings.Contains(notes[0], want) {
		t.Fatalf("basis label must show format characters as escapes: %q", notes)
	}
	if strings.ContainsAny(notes[0], cp(rlo, zwsp)) {
		t.Errorf("raw format character leaked into the note: %q", notes[0])
	}
}
