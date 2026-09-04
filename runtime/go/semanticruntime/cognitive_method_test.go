package semanticruntime

import (
	"bytes"
	"path/filepath"
	"strings"
	"testing"
)

func TestCognitiveMethodStandaloneFixturesLoad(t *testing.T) {
	files, err := filepath.Glob(fixturePath(t, "cognitive-method", "C[1-7]-*.json"))
	if err != nil {
		t.Fatal(err)
	}
	if len(files) != 7 {
		t.Fatalf("expected 7 standalone cognitive-method fixtures, got %d", len(files))
	}

	for _, path := range files {
		path := path
		t.Run(filepath.Base(path), func(t *testing.T) {
			record, err := LoadStandalone(readFixture(t, "cognitive-method", filepath.Base(path)))
			if err != nil {
				t.Fatalf("LoadStandalone: %v", err)
			}
			if record.Status != RecordValidated {
				t.Fatalf("status = %q, want %q", record.Status, RecordValidated)
			}
			if record.CognitiveMethod == nil {
				t.Fatal("cognitive method read model is nil")
			}
			if record.Decision != nil || record.Capability != nil || record.Reference != nil {
				t.Fatal("cognitive method record was promoted into another semantic contract")
			}
		})
	}
}

func TestCognitiveMethodApplicationWithoutRealizationPreservesUnknown(t *testing.T) {
	record, err := LoadStandalone(readFixture(t, "cognitive-method", "C4-application-without-realization.json"))
	if err != nil {
		t.Fatal(err)
	}
	if record.CognitiveMethod == nil || record.CognitiveMethod.MethodApplication == nil {
		t.Fatal("method application was not loaded")
	}
	application := record.CognitiveMethod.MethodApplication
	if application.RealizationRef != nil {
		t.Fatal("omitted realization_ref was invented")
	}
	if _, ok := application.MethodRef.LogicalIdentity(); !ok {
		t.Fatal("method_ref was not preserved")
	}
}

func TestCognitiveMethodExactReferencesArePreserved(t *testing.T) {
	record, err := LoadStandalone(readFixture(t, "cognitive-method", "C6-exact-bound-method-realization.json"))
	if err != nil {
		t.Fatal(err)
	}
	application := record.CognitiveMethod.MethodApplication
	if application == nil {
		t.Fatal("method application was not loaded")
	}
	if !application.MethodRef.IsExact() {
		t.Fatal("exact-bound method_ref was not preserved")
	}
	if application.RealizationRef == nil || !application.RealizationRef.IsExact() {
		t.Fatal("exact-bound realization_ref was not preserved")
	}
}

func TestCognitiveMethodOutputResidualAndPatternReferenceRemainReferences(t *testing.T) {
	patternRecord, err := LoadStandalone(readFixture(t, "cognitive-method", "C5-pattern-as-input-reference.json"))
	if err != nil {
		t.Fatal(err)
	}
	patternApplication := patternRecord.CognitiveMethod.MethodApplication
	if patternApplication == nil || len(patternApplication.InputRefs) == 0 {
		t.Fatal("pattern input reference was not preserved")
	}
	patternIdentity, ok := patternApplication.InputRefs[0].LogicalIdentity()
	if !ok || patternIdentity.Kind == "cognitive_method" {
		t.Fatalf("pattern reference was promoted into a cognitive method: %#v", patternIdentity)
	}

	residualRecord, err := LoadStandalone(readFixture(t, "cognitive-method", "C7-output-and-residual-refs.json"))
	if err != nil {
		t.Fatal(err)
	}
	application := residualRecord.CognitiveMethod.MethodApplication
	if application == nil || len(application.OutputRefs) == 0 || len(application.ResidualRefs) == 0 {
		t.Fatal("output or residual references were lost")
	}
}

func TestCognitiveMethodCurrentInterchangeLoadsTypedAndLosslessly(t *testing.T) {
	input := readFixture(t, "cognitive-method", "C8-interchange-method-application.json")
	bundle, err := LoadInterchange(input)
	if err != nil {
		t.Fatal(err)
	}
	if len(bundle.Records) != 1 {
		t.Fatalf("records = %d, want 1", len(bundle.Records))
	}
	record := bundle.Records[0]
	if record.Status != RecordValidated || record.CognitiveMethod == nil || record.CognitiveMethod.MethodApplication == nil {
		t.Fatal("current cognitive-method interchange record was not typed and validated")
	}
	if record.Decision != nil {
		t.Fatal("method application unexpectedly produced a decision")
	}
	if !bytes.Equal(bundle.ExportOriginal(), input) {
		t.Fatal("LoadInterchange rewrote cognitive-method bundle bytes")
	}
}

func TestUnknownCognitiveMethodVersionRemainsOpaque(t *testing.T) {
	bundle, err := LoadInterchange(readFixture(t, "boundary", "unknown-cognitive-method-version.json"))
	if err != nil {
		t.Fatal(err)
	}
	if len(bundle.Records) != 1 {
		t.Fatalf("records = %d, want 1", len(bundle.Records))
	}
	record := bundle.Records[0]
	if record.Status != RecordNotVerified {
		t.Fatalf("status = %q, want %q", record.Status, RecordNotVerified)
	}
	if record.CognitiveMethod != nil {
		t.Fatal("unknown cognitive-method version was interpreted as current v1alpha1")
	}
	if len(record.EnvelopeRecord.Payload) == 0 {
		t.Fatal("opaque future cognitive-method payload was not retained")
	}
}

func TestCognitiveMethodRejectsSemanticEscalationAndMissingMethodReferences(t *testing.T) {
	for _, name := range []string{
		"cognitive-method-decision-field.json",
		"cognitive-method-assurance-field.json",
		"cognitive-method-realization-missing-method-ref.json",
		"cognitive-method-application-missing-method-ref.json",
		"cognitive-method-pattern-field.json",
	} {
		t.Run(name, func(t *testing.T) {
			_, err := LoadStandalone(readFixture(t, "negative", name))
			if err == nil {
				t.Fatal("expected cognitive-method validation error")
			}
			if strings.TrimSpace(err.Error()) == "" {
				t.Fatal("validation error did not include a reason")
			}
		})
	}
}
