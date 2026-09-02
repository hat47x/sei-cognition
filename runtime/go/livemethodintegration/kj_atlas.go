package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"regexp"
	"strings"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

var fullCommitSHA = regexp.MustCompile(`^[0-9a-f]{40}$`)

// SourceIdentityは、KJ Atlas側の取得元と実行入口を追跡するためのprobe-local情報です。
// repositoryやcommitをUniversalなMethod identityへ昇格させるものではありません。
type SourceIdentity struct {
	Repository string `json:"repository"`
	Commit     string `json:"commit"`
	EntryPoint string `json:"entry_point"`
}

// ExecutionIdentityは、あるMethod Realizationを実行したときの具体的な実現条件を
// probe-local Provenanceとして残すための情報です。modelやruntimeをUniversal Contractの
// 固定fieldへ昇格させず、後から実行条件の違いを読み直せるようにします。
type ExecutionIdentity struct {
	Profile        string `json:"profile"`
	Runtime        string `json:"runtime,omitempty"`
	RuntimeVersion string `json:"runtime_version,omitempty"`
	Model          string `json:"model,omitempty"`
	ModelID        string `json:"model_id,omitempty"`
}

type KJAtlasGroup struct {
	Label     string   `json:"label"`
	CardIDs   []string `json:"cardIds"`
	Rationale string   `json:"rationale,omitempty"`
}

type KJAtlasGroupingResult struct {
	Groups          []KJAtlasGroup `json:"groups"`
	ExcludedCardIDs []string       `json:"excludedCardIds"`
	Truncated       bool           `json:"truncated"`
}

type ApplyGroupingInput struct {
	Store          *interactionprobe.CanonicalStore
	Source         SourceIdentity
	Execution      ExecutionIdentity
	MethodRef      semanticruntime.LogicalReference
	RealizationRef semanticruntime.LogicalReference
	ApplicationRef semanticruntime.LogicalReference
	OutputRef      semanticruntime.LogicalReference
	ProvenanceRef  semanticruntime.LogicalReference
	ContextRefs    []semanticruntime.LogicalReference
	InputRefs      []semanticruntime.LogicalReference
	AppliedAt      string
	ResultJSON     []byte
}

type provenancePayload struct {
	Repository   string             `json:"repository"`
	Commit       string             `json:"commit"`
	EntryPoint   string             `json:"entry_point"`
	Execution    *ExecutionIdentity `json:"execution,omitempty"`
	ResultSHA256 string             `json:"result_sha256"`
}

// ParseKJAtlasGroupingResultは、version固定したKJ Atlasのresponseを
// reference Adapterの境界で最小限だけ検査します。ここで扱うresponse shapeを
// SOZAのUniversal Contractへ一般化しません。
func ParseKJAtlasGroupingResult(raw []byte) (KJAtlasGroupingResult, error) {
	if len(raw) == 0 {
		return KJAtlasGroupingResult{}, errors.New("KJ Atlas result is empty")
	}

	var presence map[string]json.RawMessage
	if err := json.Unmarshal(raw, &presence); err != nil {
		return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas result is not valid JSON: %w", err)
	}
	for _, key := range []string{"groups", "excludedCardIds", "truncated"} {
		if _, ok := presence[key]; !ok {
			return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas result is missing %q", key)
		}
	}

	var result KJAtlasGroupingResult
	if err := json.Unmarshal(raw, &result); err != nil {
		return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas result has an invalid shape: %w", err)
	}
	for groupIndex, group := range result.Groups {
		if strings.TrimSpace(group.Label) == "" {
			return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas group %d requires a label", groupIndex)
		}
		if len(group.CardIDs) == 0 {
			return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas group %d requires at least one card id", groupIndex)
		}
		for cardIndex, cardID := range group.CardIDs {
			if strings.TrimSpace(cardID) == "" {
				return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas group %d card %d has an empty id", groupIndex, cardIndex)
			}
		}
	}
	for index, cardID := range result.ExcludedCardIDs {
		if strings.TrimSpace(cardID) == "" {
			return KJAtlasGroupingResult{}, fmt.Errorf("KJ Atlas excluded card %d has an empty id", index)
		}
	}
	return result, nil
}

// ApplyKJAtlasGroupingResultは、外部Cognitive Methodの結果をopaqueな出力として保持し、
// 既存Cognitive Method Application Contractから参照します。grouping結果を
// RecommendationやDecisionへ自動変換しません。
func ApplyKJAtlasGroupingResult(input ApplyGroupingInput) error {
	if input.Store == nil {
		return errors.New("canonical store is required")
	}
	if err := validateSource(input.Source); err != nil {
		return err
	}
	if err := validateExecution(input.Execution); err != nil {
		return err
	}
	if err := validateRef("method", input.MethodRef); err != nil {
		return err
	}
	if err := validateRef("realization", input.RealizationRef); err != nil {
		return err
	}
	if err := validateRef("application", input.ApplicationRef); err != nil {
		return err
	}
	if err := validateRef("output", input.OutputRef); err != nil {
		return err
	}
	if err := validateRef("provenance", input.ProvenanceRef); err != nil {
		return err
	}
	if strings.TrimSpace(input.AppliedAt) == "" {
		return errors.New("applied_at is required")
	}

	result, err := ParseKJAtlasGroupingResult(input.ResultJSON)
	if err != nil {
		return err
	}

	for _, ref := range []semanticruntime.LogicalReference{input.ApplicationRef, input.OutputRef, input.ProvenanceRef} {
		if _, found, err := input.Store.Find(ref); err != nil {
			return err
		} else if found {
			return fmt.Errorf("canonical record already exists: %s/%s", ref.Kind, ref.ID)
		}
	}

	digest := sha256.Sum256(input.ResultJSON)
	var execution *ExecutionIdentity
	if !executionIdentityEmpty(input.Execution) {
		value := input.Execution
		execution = &value
	}
	provenanceBytes, err := json.Marshal(provenancePayload{
		Repository:   input.Source.Repository,
		Commit:       input.Source.Commit,
		EntryPoint:   input.Source.EntryPoint,
		Execution:    execution,
		ResultSHA256: hex.EncodeToString(digest[:]),
	})
	if err != nil {
		return err
	}

	provenanceRecord := opaqueRecord(input.ProvenanceRef, provenanceBytes)
	outputRecord := opaqueRecord(input.OutputRef, json.RawMessage(append([]byte(nil), input.ResultJSON...)))

	// 先に一時storeで同じ3 recordを検証し、入力不備による部分追加を避けます。
	// production transactionを定義するものではなく、single-thread reference probeの安全策です。
	probeStore := interactionprobe.NewCanonicalStore()
	if err := probeStore.Add(provenanceRecord); err != nil {
		return err
	}
	if err := probeStore.Add(outputRecord); err != nil {
		return err
	}
	probeMachine := interactionprobe.NewMachineSurface(probeStore)
	if err := probeMachine.RecordMethodApplication(methodApplicationInput(input, result)); err != nil {
		return err
	}

	if err := input.Store.Add(provenanceRecord); err != nil {
		return err
	}
	if err := input.Store.Add(outputRecord); err != nil {
		return err
	}
	machine := interactionprobe.NewMachineSurface(input.Store)
	return machine.RecordMethodApplication(methodApplicationInput(input, result))
}

func methodApplicationInput(input ApplyGroupingInput, result KJAtlasGroupingResult) interactionprobe.MethodApplicationInput {
	realization := input.RealizationRef
	return interactionprobe.MethodApplicationInput{
		Ref:            input.ApplicationRef,
		MethodRef:      input.MethodRef,
		RealizationRef: &realization,
		ContextRefs:    input.ContextRefs,
		InputRefs:      input.InputRefs,
		OutputRefs:     []semanticruntime.LogicalReference{input.OutputRef},
		ProvenanceRefs: []semanticruntime.LogicalReference{input.ProvenanceRef},
		AppliedAt:      input.AppliedAt,
		Summary:        fmt.Sprintf("KJ Atlasのsuggest-card-groupsを実行し、%d件のgroup候補を得た。", len(result.Groups)),
	}
}

func opaqueRecord(ref semanticruntime.LogicalReference, payload json.RawMessage) semanticruntime.RuntimeRecord {
	logical := ref
	return semanticruntime.RuntimeRecord{
		EnvelopeRecord: semanticruntime.InterchangeRecord{
			Kind:       ref.Kind,
			LogicalRef: &logical,
			Payload:    payload,
		},
		Status: semanticruntime.RecordNotVerified,
	}
}

func validateSource(source SourceIdentity) error {
	if strings.TrimSpace(source.Repository) == "" {
		return errors.New("source repository is required")
	}
	if !fullCommitSHA.MatchString(source.Commit) {
		return errors.New("source commit must be a full lowercase Git commit SHA")
	}
	if strings.TrimSpace(source.EntryPoint) == "" {
		return errors.New("source entry point is required")
	}
	return nil
}

func validateExecution(execution ExecutionIdentity) error {
	if executionIdentityEmpty(execution) {
		return nil
	}
	if strings.TrimSpace(execution.Profile) == "" {
		return errors.New("execution profile is required when execution identity is recorded")
	}
	if strings.TrimSpace(execution.RuntimeVersion) != "" && strings.TrimSpace(execution.Runtime) == "" {
		return errors.New("execution runtime is required when runtime_version is recorded")
	}
	if strings.TrimSpace(execution.ModelID) != "" && strings.TrimSpace(execution.Model) == "" {
		return errors.New("execution model is required when model_id is recorded")
	}
	return nil
}

func executionIdentityEmpty(execution ExecutionIdentity) bool {
	return strings.TrimSpace(execution.Profile) == "" &&
		strings.TrimSpace(execution.Runtime) == "" &&
		strings.TrimSpace(execution.RuntimeVersion) == "" &&
		strings.TrimSpace(execution.Model) == "" &&
		strings.TrimSpace(execution.ModelID) == ""
}

func validateRef(label string, ref semanticruntime.LogicalReference) error {
	if strings.TrimSpace(ref.Kind) == "" || strings.TrimSpace(ref.ID) == "" {
		return fmt.Errorf("%s reference requires kind and id", label)
	}
	return nil
}
