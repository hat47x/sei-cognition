package journeyharness

import (
	"strings"
	"testing"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

func TestProjectionMayCoexistWithoutBecomingJourneyAuthority(t *testing.T) {
	bundle, manifest := baseJourney()
	projection := lr("projection", "P-001")
	bundle.Records = append(bundle.Records, semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{LogicalRef: &projection},
		Status:         semanticruntime.RecordNotVerified,
	})

	if err := Validate(bundle, manifest); err != nil {
		t.Fatalf("Validate() with non-authoritative projection error = %v", err)
	}
}

func TestProjectionCannotReplaceCanonicalDecision(t *testing.T) {
	bundle, manifest := baseJourney()
	projection := lr("projection", "P-DECISION-SUMMARY")

	filtered := make([]semanticruntime.RuntimeRecord, 0, len(bundle.Records))
	for _, record := range bundle.Records {
		if record.Decision != nil && record.Decision.Decision != nil && record.Decision.Decision.Ref == manifest.DecisionRef {
			continue
		}
		filtered = append(filtered, record)
	}
	bundle.Records = append(filtered, semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{LogicalRef: &projection},
		Status:         semanticruntime.RecordNotVerified,
	})

	err := Validate(bundle, manifest)
	if err == nil || !strings.Contains(err.Error(), "decision ref is not present in bundle") {
		t.Fatalf("Validate() error = %v, want missing canonical decision failure", err)
	}
}
