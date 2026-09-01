package externalintegration

import (
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"

	"github.com/hat47x/soza/runtime/go/externalartifact"
	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/provideradapter"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const (
	culturalSubstrateCommit = "aa3651f3460a6db7dc70bd848f93b600f149ffe8"
	teiCommit               = "3a20c59ce14929afa1e091e1418a2eb66f0ff32d"
)

func repositoryRoot(t *testing.T) string {
	t.Helper()
	_, currentFile, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("runtime.Caller failed")
	}
	return filepath.Clean(filepath.Join(filepath.Dir(currentFile), "..", "..", ".."))
}

func readFixture(t *testing.T, path ...string) []byte {
	t.Helper()
	parts := append([]string{repositoryRoot(t), "fixtures", "external", "e3a"}, path...)
	data, err := os.ReadFile(filepath.Join(parts...))
	if err != nil {
		t.Fatal(err)
	}
	return data
}

func culturalSubstrateDescriptor() externalartifact.Descriptor {
	return externalartifact.Descriptor{
		ID:          "cultural-substrate-weaving-ja-weave-aa3651f",
		Repository:  "hat47x/cultural-substrate-weaving",
		Commit:      culturalSubstrateCommit,
		Path:        "plugins/cultural-substrate-weaving-ja/skills/weave/SKILL.md",
		GitBlobSHA1: "4d1cd77a3561c4da58bc030936f28ae2386a81ce",
	}
}

func teiDescriptor() externalartifact.Descriptor {
	return externalartifact.Descriptor{
		ID:          "tei-production-deployment-state-3a20c59",
		Repository:  "hat47x/tei-platform",
		Commit:      teiCommit,
		Path:        "reference/observed/production.deployment-state.json",
		GitBlobSHA1: "ff3c60a8d9873f6aeb38549104ef6bb484404d17",
	}
}

func TestPinnedExternalCognitiveMethodArtifactBindsWithoutRepositorySchemaLeak(t *testing.T) {
	artifact, err := externalartifact.Verify(culturalSubstrateDescriptor(), readFixture(t, "cultural-substrate-weaving", "SKILL.md.snapshot"))
	if err != nil {
		t.Fatal(err)
	}
	provenance, err := externalartifact.ProvenanceRecord(artifact)
	if err != nil {
		t.Fatal(err)
	}
	methodRef := semanticruntime.LogicalReference{Kind: "cognitive-method", ID: "cultural-substrate-weaving"}
	realizationRef := semanticruntime.LogicalReference{Kind: "method-realization", ID: "cultural-substrate-weaving-ja@aa3651f"}
	document, err := BindMethodRealization(artifact, methodRef, realizationRef)
	if err != nil {
		t.Fatal(err)
	}

	store := interactionprobe.NewCanonicalStore()
	if err := store.Add(provenance); err != nil {
		t.Fatal(err)
	}
	if err := store.Add(semanticruntime.RuntimeRecord{CognitiveMethod: &document}); err != nil {
		t.Fatal(err)
	}

	if document.MethodRealization == nil || len(document.MethodRealization.ImplementationRefs) != 1 {
		t.Fatalf("external Method Realization did not retain one implementation provenance reference: %#v", document)
	}
	got, ok := document.MethodRealization.ImplementationRefs[0].LogicalIdentity()
	if !ok || got != externalartifact.ProvenanceRef(artifact) {
		t.Fatalf("implementation provenance mismatch: %#v", document.MethodRealization.ImplementationRefs)
	}

	payload, err := json.Marshal(document)
	if err != nil {
		t.Fatal(err)
	}
	for _, forbidden := range []string{"hat47x/cultural-substrate-weaving", culturalSubstrateCommit, "SKILL.md", "git_blob_sha1"} {
		if strings.Contains(string(payload), forbidden) {
			t.Fatalf("repository acquisition detail leaked into Cognitive Method Contract: %s", forbidden)
		}
	}
}

func TestPinnedTEIObservedStateMapsToCurrentCapabilityObservation(t *testing.T) {
	artifact, err := externalartifact.Verify(teiDescriptor(), readFixture(t, "tei", "production.deployment-state.json"))
	if err != nil {
		t.Fatal(err)
	}
	provenance, err := externalartifact.ProvenanceRecord(artifact)
	if err != nil {
		t.Fatal(err)
	}
	context := provideradapter.ObservationContext{
		ObservationID:  "tei-production-state-e3a",
		CapabilityRef:  semanticruntime.LogicalReference{Kind: "capability", ID: "deployment-readiness"},
		ObservedAt:     "2026-08-27T18:30:00+09:00",
		SourceStateRef: "external-artifact-provenance/" + artifact.Descriptor.ID,
	}
	document, err := ObserveTEIDeploymentState(artifact, context)
	if err != nil {
		t.Fatal(err)
	}

	store := interactionprobe.NewCanonicalStore()
	if err := store.Add(provenance); err != nil {
		t.Fatal(err)
	}
	if err := store.Add(semanticruntime.RuntimeRecord{Capability: &document}); err != nil {
		t.Fatal(err)
	}

	if document.Observation.Target.ProviderRef == nil || document.Observation.Target.ProviderRef.ID != "tei-platform" {
		t.Fatalf("TEI Provider identity was not preserved: %#v", document.Observation.Target)
	}
	if len(document.Observation.ProvenanceRefs) != 1 {
		t.Fatalf("TEI observation lost external provenance: %#v", document.Observation.ProvenanceRefs)
	}
	var ready *semanticruntime.ObservedCondition
	for i := range document.Observation.Conditions {
		if document.Observation.Conditions[i].Key == "data_ready" {
			ready = &document.Observation.Conditions[i]
			break
		}
	}
	if ready == nil || ready.State != "observed" || string(ready.Value) != "true" {
		t.Fatalf("TEI data readiness was not mapped as observed true: %#v", ready)
	}

	payload, err := json.Marshal(document)
	if err != nil {
		t.Fatal(err)
	}
	for _, providerField := range []string{"dataReadiness", "activeApplications", "observedAt", "databases"} {
		if strings.Contains(string(payload), providerField) {
			t.Fatalf("TEI-specific input field leaked into Capability Observation: %s", providerField)
		}
	}
}

func TestExternalArtifactIdentityMismatchCannotMutateCanonicalState(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	before, err := store.Digest()
	if err != nil {
		t.Fatal(err)
	}

	data := readFixture(t, "cultural-substrate-weaving", "SKILL.md.snapshot")
	data = append(append([]byte(nil), data...), []byte("\n改変")...)
	if _, err := externalartifact.Verify(culturalSubstrateDescriptor(), data); err == nil {
		t.Fatal("modified external artifact unexpectedly passed identity verification")
	}

	after, err := store.Digest()
	if err != nil {
		t.Fatal(err)
	}
	if before != after {
		t.Fatalf("failed external acquisition changed canonical state: before=%s after=%s", before, after)
	}
}
