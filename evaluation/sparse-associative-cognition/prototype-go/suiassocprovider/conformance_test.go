package suiassocprovider

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"strings"
	"testing"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

const expectedConformanceDigest = "a9a627e3ce3580dab010608efd30d11e84de2c66a39dcb6ff508d793c00260d2"

type conformanceFixture struct {
	Schema                 string          `json:"schema"`
	FixtureID              string          `json:"fixtureId"`
	Canonicalization       string          `json:"canonicalization"`
	RequestCanonicalSHA256 string          `json:"requestCanonicalSha256"`
	Request                json.RawMessage `json:"request"`
}

func loadConformanceFixture(t *testing.T) conformanceFixture {
	t.Helper()
	data, err := os.ReadFile("testdata/associative_contract_conformance_v1.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture conformanceFixture
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	return fixture
}

func canonicalJSONDigest(t *testing.T, raw json.RawMessage) string {
	t.Helper()
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		t.Fatal(err)
	}
	canonical, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	digest := sha256.Sum256(canonical)
	return hex.EncodeToString(digest[:])
}

func TestConformanceFixtureIdentityAndCanonicalDigest(t *testing.T) {
	fixture := loadConformanceFixture(t)
	if fixture.Schema != "sui.associative-contract-conformance-fixture/v1alpha1" {
		t.Fatalf("unexpected fixture schema: %s", fixture.Schema)
	}
	if fixture.FixtureID != "sui-sei-associative-conformance-v1" {
		t.Fatalf("unexpected fixture id: %s", fixture.FixtureID)
	}
	if fixture.Canonicalization != "utf8-json-sort-keys-no-whitespace" {
		t.Fatalf("unexpected canonicalization: %s", fixture.Canonicalization)
	}
	if fixture.RequestCanonicalSHA256 != expectedConformanceDigest {
		t.Fatalf("unexpected declared digest: %s", fixture.RequestCanonicalSHA256)
	}
	if actual := canonicalJSONDigest(t, fixture.Request); actual != expectedConformanceDigest {
		t.Fatalf("canonical request digest mismatch: %s", actual)
	}
}

func TestConformanceFixtureIsAcceptedByProviderBoundary(t *testing.T) {
	fixture := loadConformanceFixture(t)
	req, err := DecodeRequest(fixture.Request)
	if err != nil {
		t.Fatalf("SUI fixture is not accepted by DecodeRequest: %v", err)
	}
	provider, err := New(Config{
		Sparse: sparseassoc.Config{
			Dimensions: 4096,
			Fanout:     8,
			Active:     64,
			Seed:       47,
		},
		MinInternalSimilarity: 0.10,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: "conformance-test",
	})
	if err != nil {
		t.Fatal(err)
	}
	resp, err := provider.Handle(req)
	if err != nil {
		t.Fatalf("SUI fixture could not be handled: %v", err)
	}
	if resp.Schema != ResponseSchema || resp.RequestID != req.RequestID {
		t.Fatalf("unexpected response identity: %#v", resp)
	}
	if resp.Outcome != "candidates" && resp.Outcome != "abstain" {
		t.Fatalf("unexpected outcome: %s", resp.Outcome)
	}

	encoded, err := json.Marshal(resp)
	if err != nil {
		t.Fatal(err)
	}
	text := string(encoded)
	for _, forbidden := range []string{
		`"similarity"`, `"activation"`, `"confidence"`, `"importance"`,
		`"rank"`, `"score"`, `"novelty_signal"`,
	} {
		if strings.Contains(text, forbidden) {
			t.Fatalf("conformance response leaked %s: %s", forbidden, text)
		}
	}
}
