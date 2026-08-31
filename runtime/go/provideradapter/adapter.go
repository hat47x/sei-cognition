package provideradapter

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

// ObservationContext contains the SOZA-side context supplied to a Provider
// Adapter. Provider-specific input remains outside this type.
type ObservationContext struct {
	ObservationID  string
	CapabilityRef  semanticruntime.LogicalReference
	ObservedAt     string
	SourceStateRef string
}

// Adapter is a replaceable runtime implementation boundary. It is not the
// semantic authority for Provider mapping; ADR-0024 and the Capability
// Observation Contract define that meaning.
type Adapter interface {
	Observe(context ObservationContext, payload []byte) (semanticruntime.CapabilityObservationDocument, error)
}

func validateContext(context ObservationContext) error {
	if context.ObservationID == "" {
		return errors.New("observation ID is required")
	}
	if context.CapabilityRef.Kind == "" || context.CapabilityRef.ID == "" {
		return errors.New("capability reference requires kind and id")
	}
	if context.ObservedAt == "" {
		return errors.New("observed time is required")
	}
	if context.SourceStateRef == "" {
		return errors.New("source state reference is required")
	}
	return nil
}

func decodeStrict(payload []byte, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(payload))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return err
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return errors.New("multiple JSON values are not allowed")
		}
		return err
	}
	return nil
}

func rawValue(value any) (json.RawMessage, error) {
	data, err := json.Marshal(value)
	if err != nil {
		return nil, fmt.Errorf("marshal observed value: %w", err)
	}
	return data, nil
}

func logicalMappingRef(id string) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: "adapter-mapping", ID: id}
}

// ValidateObservation sends Adapter output through the same current runtime
// Contract validation used for externally supplied Capability Observations.
func ValidateObservation(document semanticruntime.CapabilityObservationDocument) (semanticruntime.RuntimeRecord, error) {
	data, err := json.Marshal(document)
	if err != nil {
		return semanticruntime.RuntimeRecord{}, fmt.Errorf("marshal capability observation: %w", err)
	}
	record, err := semanticruntime.LoadStandalone(data)
	if err != nil {
		return semanticruntime.RuntimeRecord{}, err
	}
	if record.Status != semanticruntime.RecordValidated || record.Capability == nil {
		return semanticruntime.RuntimeRecord{}, errors.New("adapter output was not validated as a capability observation")
	}
	return record, nil
}
