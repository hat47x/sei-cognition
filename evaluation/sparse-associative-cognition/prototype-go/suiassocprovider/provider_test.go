package suiassocprovider

import (
	"encoding/json"
	"fmt"
	"reflect"
	"strings"
	"testing"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

func testProvider(t *testing.T, minSimilarity float32) *Provider {
	t.Helper()
	p, err := New(Config{
		Sparse: sparseassoc.Config{
			Dimensions: 4096,
			Fanout:     8,
			Active:     64,
			Seed:       47,
		},
		MinInternalSimilarity: minSimilarity,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "2026-09-12-v1",
	})
	if err != nil {
		t.Fatal(err)
	}
	return p
}

func baseRequest() Request {
	return Request{
		Schema:     RequestSchema,
		RequestID:  "req-1",
		NetworkID:  "sui-net-1",
		Intent:     "neighborhood",
		AnchorRefs: []string{"c1"},
		Items: []Item{
			{
				Ref:  "c1",
				Kind: "card",
				Channels: Channels{
					Text: "現場観察では確認作業が増えた",
					Graph: &GraphChannel{
						RelationTypes: []string{"related"},
						NeighborKinds: []string{"card"},
					},
					Provenance: &ProvenanceChannel{SourceRefs: []string{"s1"}, ActorRefs: []string{"human:a"}},
				},
			},
			{
				Ref:  "c2",
				Kind: "card",
				Channels: Channels{
					Text: "確認作業の増加は引継ぎ時間にも影響している",
					Graph: &GraphChannel{
						RelationTypes: []string{"related"},
						NeighborKinds: []string{"card"},
					},
					Provenance: &ProvenanceChannel{SourceRefs: []string{"s1", "s2"}, ActorRefs: []string{"human:a"}},
				},
			},
			{
				Ref:  "c3",
				Kind: "card",
				Channels: Channels{
					Text:       "花と海と音楽についての記録",
					Provenance: &ProvenanceChannel{SourceRefs: []string{"s9"}, ActorRefs: []string{"human:z"}},
				},
			},
		},
		Policy: Policy{CandidateLimit: 2},
	}
}

func TestHandleReturnsContractResponseWithoutInternalSimilarity(t *testing.T) {
	p := testProvider(t, 0.10)
	resp, err := p.Handle(baseRequest())
	if err != nil {
		t.Fatal(err)
	}
	if resp.Schema != ResponseSchema || resp.RequestID != "req-1" {
		t.Fatalf("unexpected response identity: %#v", resp)
	}
	if resp.Outcome != "candidates" || len(resp.CandidateRefs) == 0 {
		t.Fatalf("expected candidates: %#v", resp)
	}
	for _, ref := range resp.CandidateRefs {
		if ref == "c1" {
			t.Fatal("anchor leaked into candidate refs")
		}
	}

	data, err := json.Marshal(resp)
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	for _, forbidden := range []string{
		`"similarity"`, `"activation"`, `"confidence"`, `"importance"`,
		`"rank"`, `"score"`, `"novelty_signal"`,
	} {
		if strings.Contains(text, forbidden) {
			t.Fatalf("provider leaked internal/ranking signal %s: %s", forbidden, text)
		}
	}
}

func TestResponseCandidateOrderIsStableRefNotSimilarityOrder(t *testing.T) {
	req := baseRequest()
	req.Items = append(req.Items, Item{
		Ref:  "c10",
		Kind: "card",
		Channels: Channels{Text: "確認作業が増えたという現場記録"},
	})
	req.Policy.CandidateLimit = 3
	p := testProvider(t, 0.05)
	resp, err := p.Handle(req)
	if err != nil {
		t.Fatal(err)
	}
	for i := 1; i < len(resp.CandidateRefs); i++ {
		if resp.CandidateRefs[i-1] > resp.CandidateRefs[i] {
			t.Fatalf("candidate refs are not stable ref order: %#v", resp.CandidateRefs)
		}
	}
}

func TestEvidenceUsesOnlyExternallyExplainableChannelProvenance(t *testing.T) {
	p := testProvider(t, 0.10)
	resp, err := p.Handle(baseRequest())
	if err != nil {
		t.Fatal(err)
	}
	var c2 *Evidence
	for i := range resp.Evidence {
		if resp.Evidence[i].Ref == "c2" {
			c2 = &resp.Evidence[i]
			break
		}
	}
	if c2 == nil {
		t.Fatalf("expected c2 evidence: %#v", resp)
	}
	for _, want := range []string{
		"channel:text",
		"graph:neighborKind:card",
		"graph:relationType:related",
		"provenance:actor:human:a",
		"provenance:source:s1",
	} {
		if !containsString(c2.MatchedChannelRefs, want) {
			t.Fatalf("missing channel provenance %q: %#v", want, c2.MatchedChannelRefs)
		}
	}
}

func TestHighInternalThresholdAbstainsWithoutNumericNovelty(t *testing.T) {
	p := testProvider(t, 0.99)
	resp, err := p.Handle(baseRequest())
	if err != nil {
		t.Fatal(err)
	}
	if resp.Outcome != "abstain" || resp.NoveltyCue != "abstain" {
		t.Fatalf("unexpected abstain response: %#v", resp)
	}
	if len(resp.CandidateRefs) != 0 || len(resp.Evidence) != 0 {
		t.Fatalf("abstain must be empty: %#v", resp)
	}
}

func TestDecodeRequestIsClosedWorld(t *testing.T) {
	data := []byte(`{
		"schema":"sui.associative-recall-request/v1alpha1",
		"requestId":"r",
		"networkId":"n",
		"intent":"neighborhood",
		"anchorRefs":["c1"],
		"items":[{"ref":"c1","kind":"card","channels":{"text":"x"},"reviewState":"human_reviewed"}],
		"policy":{"candidateLimit":1}
	}`)
	if _, err := DecodeRequest(data); err == nil || !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("expected closed-world decode failure, got %v", err)
	}
}

func TestRequestBoundsFailClosed(t *testing.T) {
	p := testProvider(t, 0.1)

	t.Run("candidate limit", func(t *testing.T) {
		req := baseRequest()
		req.Policy.CandidateLimit = MaxCandidateLimit + 1
		if _, err := p.Handle(req); err == nil {
			t.Fatal("expected candidate limit error")
		}
	})

	t.Run("anchors", func(t *testing.T) {
		req := Request{
			Schema: RequestSchema, RequestID: "r", NetworkID: "n", Intent: "readout",
			Policy: Policy{CandidateLimit: 1},
		}
		for i := 0; i < MaxAnchors+1; i++ {
			ref := fmt.Sprintf("c%02d", i)
			req.AnchorRefs = append(req.AnchorRefs, ref)
			req.Items = append(req.Items, Item{Ref: ref, Kind: "card", Channels: Channels{Text: "x"}})
		}
		if _, err := p.Handle(req); err == nil {
			t.Fatal("expected anchor bound error")
		}
	})

	t.Run("items", func(t *testing.T) {
		req := Request{
			Schema: RequestSchema, RequestID: "r", NetworkID: "n", Intent: "readout",
			AnchorRefs: []string{"c000"}, Policy: Policy{CandidateLimit: 1},
		}
		for i := 0; i < MaxItems+1; i++ {
			req.Items = append(req.Items, Item{Ref: fmt.Sprintf("c%03d", i), Kind: "card"})
		}
		if _, err := p.Handle(req); err == nil {
			t.Fatal("expected item bound error")
		}
	})
}

func TestDuplicateAndMissingRefsFailClosed(t *testing.T) {
	p := testProvider(t, 0.1)

	t.Run("duplicate item", func(t *testing.T) {
		req := baseRequest()
		req.Items = append(req.Items, req.Items[0])
		if _, err := p.Handle(req); err == nil || !strings.Contains(err.Error(), "duplicate item") {
			t.Fatalf("expected duplicate item error, got %v", err)
		}
	})

	t.Run("anchor outside items", func(t *testing.T) {
		req := baseRequest()
		req.AnchorRefs = []string{"missing"}
		if _, err := p.Handle(req); err == nil || !strings.Contains(err.Error(), "outside items") {
			t.Fatalf("expected anchor scope error, got %v", err)
		}
	})
}

func TestHandleDoesNotMutateRequest(t *testing.T) {
	p := testProvider(t, 0.1)
	req := baseRequest()
	before := deepCopyRequest(t, req)
	if _, err := p.Handle(req); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(req, before) {
		t.Fatalf("request mutated\nbefore=%#v\nafter=%#v", before, req)
	}
}

func TestUnsupportedSchemaAndIntentFailClosed(t *testing.T) {
	p := testProvider(t, 0.1)
	req := baseRequest()
	req.Schema = "legacy/v0"
	if _, err := p.Handle(req); err == nil {
		t.Fatal("expected schema error")
	}
	req = baseRequest()
	req.Intent = "automatic_consensus"
	if _, err := p.Handle(req); err == nil {
		t.Fatal("expected intent error")
	}
}

func TestProviderMetadataIsExplicit(t *testing.T) {
	p := testProvider(t, 0.1)
	resp, err := p.Handle(baseRequest())
	if err != nil {
		t.Fatal(err)
	}
	if resp.Provider.ProviderID != "sei-sacs-go-eval" || resp.Provider.ImplementationVersion != "2026-09-12-v1" {
		t.Fatalf("unexpected provider metadata: %#v", resp.Provider)
	}
}

func deepCopyRequest(t *testing.T, req Request) Request {
	t.Helper()
	data, err := json.Marshal(req)
	if err != nil {
		t.Fatal(err)
	}
	var out Request
	if err := json.Unmarshal(data, &out); err != nil {
		t.Fatal(err)
	}
	return out
}

func containsString(values []string, want string) bool {
	for _, value := range values {
		if value == want {
			return true
		}
	}
	return false
}
