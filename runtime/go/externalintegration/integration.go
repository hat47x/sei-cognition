package externalintegration

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"

	"github.com/hat47x/sei-cognition/runtime/go/externalartifact"
	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

func ref(value semanticruntime.LogicalReference) semanticruntime.Reference {
	return semanticruntime.Reference{Kind: value.Kind, ID: value.ID, Scope: value.Scope}
}

// BindMethodRealization binds a verified externally owned artifact to an
// existing Cognitive Method without importing repository concepts into the
// Cognitive Method Contract itself. The source identity is referenced through
// an opaque provenance record created by externalartifact.ProvenanceRecord.
func BindMethodRealization(artifact externalartifact.VerifiedArtifact, methodRef, realizationRef semanticruntime.LogicalReference) (semanticruntime.CognitiveMethodDocument, error) {
	if methodRef.Kind == "" || methodRef.ID == "" || realizationRef.Kind == "" || realizationRef.ID == "" {
		return semanticruntime.CognitiveMethodDocument{}, errors.New("method and realization references are required")
	}
	provenance := externalartifact.ProvenanceRef(artifact)
	document := semanticruntime.CognitiveMethodDocument{
		Contract:   semanticruntime.ContractCognitiveMethod,
		RecordType: "method_realization",
		MethodRealization: &semanticruntime.MethodRealization{
			Ref:                realizationRef,
			MethodRef:          ref(methodRef),
			Description:        "SEI外でversion管理されるCognitive Method artifactを検証して結び付けたreference Realization",
			ImplementationRefs: []semanticruntime.Reference{ref(provenance)},
		},
	}
	payload, err := json.Marshal(document)
	if err != nil {
		return semanticruntime.CognitiveMethodDocument{}, err
	}
	record, err := semanticruntime.LoadStandalone(payload)
	if err != nil {
		return semanticruntime.CognitiveMethodDocument{}, fmt.Errorf("external Method Realization did not validate: %w", err)
	}
	if record.Status != semanticruntime.RecordValidated || record.CognitiveMethod == nil || record.CognitiveMethod.MethodRealization == nil {
		return semanticruntime.CognitiveMethodDocument{}, errors.New("external Method Realization was not validated as a Cognitive Method record")
	}
	return document, nil
}

type teiVersion struct {
	Major int `json:"major"`
	Minor int `json:"minor"`
}

type teiProvidedContract struct {
	ID      string     `json:"id"`
	Version teiVersion `json:"version"`
}

type teiDatabaseState struct {
	Database      string                `json:"database"`
	Source        string                `json:"source"`
	Release       string                `json:"release,omitempty"`
	Provides      []teiProvidedContract `json:"provides,omitempty"`
	DataReadiness string                `json:"dataReadiness,omitempty"`
	ObservedAt    string                `json:"observedAt,omitempty"`
}

type teiApplicationState struct {
	Application string `json:"application"`
	Version     string `json:"version"`
}

type teiDeploymentState struct {
	Environment        string                `json:"environment"`
	ObservedAt         string                `json:"observedAt"`
	ActiveApplications []teiApplicationState `json:"activeApplications"`
	Databases          []teiDatabaseState    `json:"databases"`
}

func decodeStrict(data []byte, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(data))
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
		return nil, err
	}
	return data, nil
}

// ObserveTEIDeploymentState maps one verified TEI observed-state artifact into
// the current Capability Observation. TEI's field names remain inside this
// adapter; they do not become a SEI Universal Provider State schema.
func ObserveTEIDeploymentState(artifact externalartifact.VerifiedArtifact, context provideradapter.ObservationContext) (semanticruntime.CapabilityObservationDocument, error) {
	if context.ObservationID == "" || context.CapabilityRef.Kind == "" || context.CapabilityRef.ID == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("observation ID and capability reference are required")
	}
	var state teiDeploymentState
	if err := decodeStrict(artifact.Bytes, &state); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("decode TEI deployment state: %w", err)
	}
	if state.Environment == "" || state.ObservedAt == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("TEI deployment state requires environment and observedAt")
	}

	applicationCount, _ := rawValue(len(state.ActiveApplications))
	databaseCount, _ := rawValue(len(state.Databases))
	conditions := []semanticruntime.ObservedCondition{
		{Key: "active_application_count", State: "observed", Value: applicationCount, Unit: "count"},
		{Key: "database_count", State: "observed", Value: databaseCount, Unit: "count"},
	}

	readiness := semanticruntime.ObservedCondition{Key: "data_ready"}
	if len(state.Databases) == 0 {
		readiness.State = "unknown"
		readiness.Note = "TEI observed stateにdatabaseが含まれず、data readinessを確定できない"
	} else {
		allObserved := true
		allReady := true
		for _, database := range state.Databases {
			if database.DataReadiness == "" {
				allObserved = false
				break
			}
			if database.DataReadiness != "ready" {
				allReady = false
			}
		}
		if !allObserved {
			readiness.State = "unknown"
			readiness.Note = "一部databaseのdata readinessをTEI artifactから観測できていない"
		} else {
			value, _ := rawValue(allReady)
			readiness.State = "observed"
			readiness.Value = value
		}
	}
	conditions = append(conditions, readiness)

	provenance := externalartifact.ProvenanceRef(artifact)
	capabilityRef := context.CapabilityRef
	providerRef := semanticruntime.LogicalReference{Kind: "provider", ID: "tei-platform"}
	document := semanticruntime.CapabilityObservationDocument{
		Contract: semanticruntime.ContractCapabilityObservation,
		Observation: semanticruntime.CapabilityObservation{
			Ref: semanticruntime.LogicalReference{Kind: "capability-observation", ID: context.ObservationID},
			Target: semanticruntime.CapabilityTarget{
				CapabilityRef:     &capabilityRef,
				ProviderRef:       &providerRef,
				ProviderTargetRef: "tei-environment:" + state.Environment,
			},
			ObservedAt:     state.ObservedAt,
			Conditions:     conditions,
			ProvenanceRefs: []semanticruntime.Reference{ref(provenance)},
			MappingProvenance: &semanticruntime.MappingProvenance{
				MappingRef:     semanticruntime.Reference{Kind: "adapter-mapping", ID: "tei-deployment-state-to-capability-observation/reference-v1"},
				SourceStateRef: provenance.Kind + "/" + provenance.ID,
				Description:    "version固定して検証したTEI deployment stateをcurrent Capability Observationへ変換するreference mapping",
			},
		},
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("mapped TEI Capability Observation did not validate: %w", err)
	}
	return document, nil
}
