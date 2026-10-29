package teiintegration

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os/exec"
	"strconv"
	"strings"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

const (
	teiCLIProviderID       = "tei-cli-reference"
	teiCLIMappingID        = "tei-deployment-provider-plan-to-capability-observation/reference-v1"
	maxTEIProviderPlanSize = 1 << 20
	maxTEIStderrSize       = 64 << 10
)

// CLI は外部から与えられたTEI executableを呼ぶreference integration境界です。
// ExecutableやPrefixArgsは取得方法・配布方式を表すだけであり、SEIのUniversal
// ContractやTEIの正式なintegration protocolではありません。
type CLI struct {
	Executable string
	PrefixArgs []string
}

// ProviderPlanRequest はTEIのdeployment-provider-planを呼ぶためのProvider固有設定です。
// field setをSEI Universal Contractへ昇格させる意図はありません。
type ProviderPlanRequest struct {
	Workspace        string
	Run              string
	Solution         string
	Version          string
	PluginLock       string
	ExpectedRevision *int
}

type providerRoute struct {
	Kind     string `json:"kind"`
	Provider string `json:"provider"`
	ActionID string `json:"actionId,omitempty"`
}

type providerPlan struct {
	Executors     []json.RawMessage `json:"executors,omitempty"`
	Observations  []providerRoute   `json:"observations,omitempty"`
	Evidence      []providerRoute   `json:"evidence,omitempty"`
	PluginRuntime json.RawMessage   `json:"pluginRuntime,omitempty"`
}

type limitedBuffer struct {
	buffer bytes.Buffer
	limit  int
}

func (w *limitedBuffer) Write(payload []byte) (int, error) {
	remaining := w.limit - w.buffer.Len()
	if remaining <= 0 {
		return 0, errors.New("external process output exceeded limit")
	}
	if len(payload) > remaining {
		_, _ = w.buffer.Write(payload[:remaining])
		return remaining, errors.New("external process output exceeded limit")
	}
	return w.buffer.Write(payload)
}

func (w *limitedBuffer) Bytes() []byte  { return w.buffer.Bytes() }
func (w *limitedBuffer) String() string { return w.buffer.String() }

func (request ProviderPlanRequest) args() ([]string, error) {
	if strings.TrimSpace(request.Workspace) == "" {
		return nil, errors.New("TEI workspace path is required")
	}
	if strings.TrimSpace(request.Run) == "" {
		return nil, errors.New("TEI durable run path is required")
	}
	if strings.TrimSpace(request.Solution) == "" {
		return nil, errors.New("TEI solution ID is required")
	}
	if strings.TrimSpace(request.Version) == "" {
		return nil, errors.New("TEI solution version is required")
	}
	if strings.TrimSpace(request.PluginLock) == "" {
		return nil, errors.New("TEI plugin lock path is required")
	}

	args := []string{
		"deployment-provider-plan",
		"-workspace", request.Workspace,
		"-run", request.Run,
		"-solution", request.Solution,
		"-version", request.Version,
		"-plugin-lock", request.PluginLock,
	}
	if request.ExpectedRevision != nil {
		args = append(args, "-expected-revision", strconv.Itoa(*request.ExpectedRevision))
	}
	return args, nil
}

func validatePlan(plan providerPlan) error {
	if len(plan.Executors) == 0 && len(plan.Observations) == 0 && len(plan.Evidence) == 0 && len(plan.PluginRuntime) == 0 {
		return errors.New("TEI Provider Plan did not contain recognized provider-plan information")
	}
	for _, route := range append(append([]providerRoute{}, plan.Observations...), plan.Evidence...) {
		if strings.TrimSpace(route.Kind) == "" || strings.TrimSpace(route.Provider) == "" {
			return errors.New("TEI Provider Plan contains an incomplete provider route")
		}
	}
	return nil
}

func decodeProviderPlan(payload []byte) (providerPlan, error) {
	decoder := json.NewDecoder(bytes.NewReader(payload))
	decoder.DisallowUnknownFields()
	var plan providerPlan
	if err := decoder.Decode(&plan); err != nil {
		return providerPlan{}, fmt.Errorf("TEI Provider Plan JSONを読めません: %w", err)
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return providerPlan{}, errors.New("TEI Provider Plan outputに複数のJSON値があります")
		}
		return providerPlan{}, fmt.Errorf("TEI Provider Plan outputの末尾を検査できません: %w", err)
	}
	if err := validatePlan(plan); err != nil {
		return providerPlan{}, err
	}
	return plan, nil
}

func observedValue(value any) (json.RawMessage, error) {
	payload, err := json.Marshal(value)
	if err != nil {
		return nil, fmt.Errorf("observed valueをJSON化できません: %w", err)
	}
	return payload, nil
}

func buildObservation(observationContext provideradapter.ObservationContext) (semanticruntime.CapabilityObservationDocument, error) {
	if observationContext.ObservationID == "" || observationContext.CapabilityRef.Kind == "" || observationContext.CapabilityRef.ID == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("observation ID and capability reference are required")
	}
	if observationContext.ObservedAt == "" || observationContext.SourceStateRef == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("observed time and source state reference are required")
	}

	available, err := observedValue(true)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	planResolved, err := observedValue(true)
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}

	providerRef := semanticruntime.LogicalReference{Kind: "provider", ID: teiCLIProviderID}
	capabilityRef := observationContext.CapabilityRef
	document := semanticruntime.CapabilityObservationDocument{
		Contract: semanticruntime.ContractCapabilityObservation,
		Observation: semanticruntime.CapabilityObservation{
			Ref: semanticruntime.LogicalReference{Kind: "capability-observation", ID: observationContext.ObservationID},
			Target: semanticruntime.CapabilityTarget{
				CapabilityRef:     &capabilityRef,
				ProviderRef:       &providerRef,
				ProviderTargetRef: "tei-cli:deployment-provider-plan",
			},
			ObservedAt: observationContext.ObservedAt,
			Conditions: []semanticruntime.ObservedCondition{
				{Key: "availability", State: "observed", Value: available},
				{Key: "provider_plan_resolved", State: "observed", Value: planResolved},
			},
			MappingProvenance: &semanticruntime.MappingProvenance{
				MappingRef:     semanticruntime.Reference{Kind: "adapter-mapping", ID: teiCLIMappingID},
				SourceStateRef: observationContext.SourceStateRef,
				Description:    "外部TEI CLIのProvider Plan応答をcurrent Capability Observationへ変換するreference mapping",
			},
		},
	}
	if _, err := provideradapter.ValidateObservation(document); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("mapped TEI Capability Observation did not validate: %w", err)
	}
	return document, nil
}

// ObserveProviderPlan は外部から与えられたTEI executableを別OS processとして呼びます。
// executableの取得、repository clone、credential解決はこの境界の外側です。
// process failure、timeout、未知のtop-level field、malformed outputではObservationを返しません。
func (cli CLI) ObserveProviderPlan(ctx context.Context, request ProviderPlanRequest, observationContext provideradapter.ObservationContext) (semanticruntime.CapabilityObservationDocument, error) {
	executable := strings.TrimSpace(cli.Executable)
	if executable == "" {
		return semanticruntime.CapabilityObservationDocument{}, errors.New("TEI executable path is required")
	}
	providerArgs, err := request.args()
	if err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	args := append(append([]string{}, cli.PrefixArgs...), providerArgs...)

	stdout := &limitedBuffer{limit: maxTEIProviderPlanSize}
	stderr := &limitedBuffer{limit: maxTEIStderrSize}
	command := exec.CommandContext(ctx, executable, args...)
	command.Stdout = stdout
	command.Stderr = stderr
	if err := command.Run(); err != nil {
		if ctxErr := ctx.Err(); ctxErr != nil {
			return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("TEI process was cancelled or timed out: %w", ctxErr)
		}
		if strings.TrimSpace(stderr.String()) != "" {
			return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("TEI process failed: %w: %s", err, strings.TrimSpace(stderr.String()))
		}
		return semanticruntime.CapabilityObservationDocument{}, fmt.Errorf("TEI process failed: %w", err)
	}

	if _, err := decodeProviderPlan(stdout.Bytes()); err != nil {
		return semanticruntime.CapabilityObservationDocument{}, err
	}
	return buildObservation(observationContext)
}
