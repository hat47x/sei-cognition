package provideradapter

import (
	"errors"
	"fmt"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const (
	providerAID = "synthetic-provider-a"
	providerBID = "synthetic-provider-b"
	mappingAID  = "synthetic-provider-a-to-capability-observation/v1"
	mappingBID  = "synthetic-provider-b-to-capability-observation/v1"
)

// ProviderAState deliberately uses a Provider-specific shape. It is not a SOZA
// Universal ProviderState contract.
type ProviderAState struct {
	Health     *string `json:"health,omitempty"`
	DelayMS    *int64  `json:"delay_ms,omitempty"`
	ServiceRef string  `json:"service_ref"`
}

// ProviderBState uses a different Provider-specific shape and unit system.
type ProviderBState struct {
	Ready           *bool    `json:"ready,omitempty"`
	ResponseSeconds *float64 `json:"response_seconds,omitempty"`
	Endpoint        string   `json:"endpoint"`
}

type ProviderAAdapter struct{}
type ProviderBAdapter struct{}

func availabilityFromHealth(health *string) (semanticruntime.ObservedCondition, error) {
	condition := semanticruntime.ObservedCondition{Key: "availability"}
	if health == nil || *health == "unknown" || *health == "amber" {
		condition.State = "unknown"
		condition.Note = "Provider Aの状態だけでは利用可否を真偽へ確定できない"
		return condition, nil
	}

	var available bool
	switch *health {
	case "green":
		available = true
	case "red":
		available = false
	default:
		return semanticruntime.ObservedCondition{}, fmt.Errorf("unsupported Provider A health %q", *health)
	}
	value, err := rawValue(available)
	if err != nil {
		return semanticruntime.ObservedCondition{}, err
	}
	condition.State = "observed"
	condition.Value = value
	return condition, nil
}

func latencyFromMilliseconds(delay *int64) (semanticruntime.ObservedCondition, error) {
	condition := semanticruntime.ObservedCondition{Key: "latency", Unit: "ms"}
	if delay == nil {
		condition.State = "unknown"
		condition.Unit = ""
		condition.Note = "Provider Aからlatencyを観測できていない"
		return condition, nil
	}
	if *delay < 0 {
		return semanticruntime.ObservedCondition{}, errors.New("Provider A delay_ms must not be negative")
	}
	value, err := rawValue(*delay)
	if err != nil {
		return semanticruntime.ObservedCondition{}, err
	}
	condition.State = "observed"
	condition.Value = value
	return condition, nil
}

func availabilityFromReady(ready *bool) (semanticruntime.ObservedCondition, error) {
	condition := semanticruntime.ObservedCondition{Key: "availability"}
	if ready == nil {
		condition.State = "unknown"
		condition.Note = "Provider Bからready状態を観測できていない"
		return condition, nil
	}
	value, err := rawValue(*ready)
	if err != nil {
		return semanticruntime.ObservedCondition{}, err
	}
	condition.State = "observed"
	condition.Value = value
	return condition, nil
}

func latencyFromSeconds(seconds *float64) (semanticruntime.ObservedCondition, error) {
	condition := semanticruntime.ObservedCondition{Key: "latency", Unit: "ms"}
	if seconds == nil {
		condition.State = "unknown"
		condition.Unit = ""
		condition.Note = "Provider Bからresponse timeを観測できていない"
		return condition, nil
	}
	if *seconds < 0 {
		return semanticruntime.ObservedCondition{}, errors.New("Provider B response_seconds must not be negative")
	}
	milliseconds := *seconds * 1000
	value, err := rawValue(milliseconds)
	if err != nil {
		return semanticruntime.ObservedCondition{}, err
	}
	condition.State = "observed"
	condition.Value = value
	return condition, nil
}

func baseObservation(context ObservationContext, providerID, providerTarget, mappingID, inputSchema string, conditions []semanticruntime.ObservedCondition) semanticruntime.CapabilityObservationDocument {
	providerRef := semanticruntime.LogicalReference{Kind: "provider", ID: providerID}
	capabilityRef := context.CapabilityRef
	return semanticruntime.CapabilityObservationDocument{
		Contract: semanticruntime.ContractCapabilityObservation,
		Observation: semanticruntime.CapabilityObservation{
			Ref: semanticruntime.LogicalReference{Kind: "capability-observation", ID: context.ObservationID},
			Target: semanticruntime.CapabilityTarget{
				CapabilityRef:     &capabilityRef,
				ProviderRef:       &providerRef,
				ProviderTargetRef: providerTarget,
			},
			ObservedAt: context.ObservedAt,
			Conditions: conditions,
			MappingProvenance: &semanticruntime.MappingProvenance{
				MappingRef:     logicalMappingRef(mappingID),
				SourceStateRef: context.SourceStateRef,
				Description:    "Provider固有stateをcurrent Capability Observationへ変換したmapping",
			},
			Extensions: map[string]any{
				"provider_context": map[string]any{
					"input_schema": inputSchema,
				},
			},
		},
	}
}

func (ProviderAAdapter) Observe(context ObservationContext, payload []byte) (semanticruntime.CapabilityObservationDocument, error) {
	if err := validateContext(context); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	var state ProviderAState
	if err := decodeStrict(payload, &state); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("decode Provider A state: %w", err)
	}
	if state.ServiceRef == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("Provider A service_ref is required")
	}
	availability, err := availabilityFromHealth(state.Health)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	latency, err := latencyFromMilliseconds(state.DelayMS)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	return baseObservation(context, providerAID, state.ServiceRef, mappingAID, "synthetic-provider-a/v1", []semanticruntime.ObservedCondition{availability, latency}), nil
}

func (ProviderBAdapter) Observe(context ObservationContext, payload []byte) (semanticruntime.CapabilityObservationDocument, error) {
	if err := validateContext(context); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	var state ProviderBState
	if err := decodeStrict(payload, &state); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("decode Provider B state: %w", err)
	}
	if state.Endpoint == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("Provider B endpoint is required")
	}
	availability, err := availabilityFromReady(state.Ready)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	latency, err := latencyFromSeconds(state.ResponseSeconds)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	return baseObservation(context, providerBID, state.Endpoint, mappingBID, "synthetic-provider-b/v1", []semanticruntime.ObservedCondition{availability, latency}), nil
}
