# ISSUE-000031: current ContractのExecutable Conformanceをactual repositoryへ実装する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0019, ADR-0021**  
Updated: 2026-08-31

## Goal

ISSUE-000030で確定したcurrent Contract Design baselineについて、machine-readable representation、semantic validator、positive / negative fixture、conformance runnerをactual repositoryへ実装し、再現可能なExecutable Evidenceを構築する。

Contract Definitionの存在をconformance PASSとみなさず、**自然言語で確定した意味を、機械検査できる範囲へ忠実に落とす**ことを目的とする。

## Current normative inputs

- `contracts/README.md`
- `contracts/CONTRACT_CATALOG.md`
- `contracts/TRACEABILITY.md`
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
- `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
- `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
- `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
- `contracts/history/HISTORICAL_CONTRACT_MAPPING.md`
- ADR-0021

## Architecture / authority rule

machine-readable schemaやvalidatorはContract Definitionの検証可能なrepresentationであり、意味上の正本ではない。

```text
Contract Definition
  → schema / validator
  → fixture
  → conformance result
```

schemaにしか存在しない新しいsemantic requirementを作らない。

Contract Definitionとschemaが矛盾した場合は、schemaを黙って優先せずContract inconsistencyとして扱う。

## Required work

### 1. contract identity / version registry

current 4 Contract familyについて、少なくとも次を機械的に識別できるようにする。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

unknown contract ID / versionを既知として処理しないnegative caseを持つ。

### 2. machine-readable schema

current Contractのinteroperability minimumを検査できる最小schemaを実体化する。

候補配置:

```text
contracts/schemas/v1alpha1/
```

schemaはproduction field setを先取りして肥大化させない。

自然言語ContractにあるすべてのinvariantをJSON Schema等だけで表現できない場合は、無理にschemaへ押し込まずsemantic validatorへ分ける。

### 3. semantic invariant validator

少なくとも次のようなschemaだけでは表しにくい意味境界を検査する。

- RecommendationをDecisionとして暗黙処理しない。
- DecisionをAuthority / Executionへ暗黙昇格しない。
- `not_verified`と`failed`を混同しない。
- same logical identity内のsemantic revisionでexact endpointを失わない。
- `not observed`を`unavailable`へ黙って変換しない。
- Provider-specific stateをCapability Definitionそのものとして扱わない。
- unknown contract / versionをknownとして処理しない。

validatorはProduct Valueの妥当性やDecisionの正しさを自動判定しない。

### 4. positive fixture

少なくとも次を含むcurrent positive fixtureを用意する。

- Semantic Reference + Exact Binding
- Decision Memory + basis + unresolved state
- Capability Observation + mapping provenance
- Semantic Interchange envelopeに上記複数Contractを含める例

### 5. negative fixture

少なくとも次を検出できるfixtureを用意する。

- unknown contract versionをknownとして要求する入力
- exact bindingに必要なcontent identityがない
- same logical identity revisionでexact endpointが曖昧
- DecisionとExecutionを一つのrecordへ意味上統合する入力
- `not_verified`をdigest mismatch相当へ潰す入力
- Capability Observation不足を`unavailable=false/true`へ確定する入力
- broken required reference

### 6. partial knowledge fixture

Semantic Interchangeでは、次をmalformed interchangeと区別できることを確認する。

- Unknown
- Conflict
- unresolved external reference
- unknown optional extension

```text
semantic uncertainty != malformed interchange
```

### 7. conformance runner

actual repositoryから一つの入口で再実行できるようにする。

候補:

```text
tools/check_contract_conformance.py
```

初期実装では依存を増やしすぎず、再現性と読みやすさを優先する。

## Coordination with existing Issues

### ISSUE-000009

Representation Profile、canonicalization、digest algorithmのstable acceptanceは本Issueで先取りしない。

Semantic ReferenceのfixtureはProfile identityを参照できる形にするが、stable Profile未確定を理由にsemantic Contract全体を停止させない。

### ISSUE-000024

Capability ObservationのProvider-neutral / TEI等の具体fixtureはISSUE-000024と共有できる。

本IssueはContract-level conformanceを担い、TEI固有mappingの詳細をUniversal schemaへ持ち込まない。

### ISSUE-000027

Requirements registry checkerとContract conformance runnerは責務を分ける。共通の軽量実行入口へ後から束ねることはできるが、一つの巨大checkerへ統合することを目的にしない。

## Acceptance

### Design Acceptance

- [x] normative Contract Definitionがactual repositoryに存在する。
- [x] machine-readable層の権威関係がADR-0021で定まっている。
- [x] required positive / negative / partial-knowledge caseが整理されている。

### Executable Acceptance

- [ ] actual repositoryにschema / validator / fixture / runnerが存在する。
- [ ] current positive fixtureがPASSする。
- [ ] required negative fixtureが期待どおりFAILする。
- [ ] partial knowledgeをmalformed dataへ誤分類しない。
- [ ] current 4 Contract familyのidentity / versionを検査できる。
- [ ] historical schema / local PASSをcurrent PASSとして継承していない。
- [ ] conformance resultを再現可能なEvidenceとして保存できる。

### Release / Operational Acceptance

本Issueでは要求しない。

## Non-goals

- Production runtime全体の実装
- Product Valueの自動採点
- Decision validityの自動判定
- Universal risk / confidence / suitability score
- JCS / SHA-256等のstable Representation Profileを本Issueだけで決定すること
- TEI内部SchemaのSOZA側への複製
- private chain-of-thoughtの保存・検証

## Dependencies

- ISSUE-000030
- ISSUE-000009
- ISSUE-000024
- ADR-0021

## Natural Japanese review

Contract Design baselineとExecutable conformanceの責務を分離し、schemaで検査する条件とsemantic validatorへ残す条件を整理した。その後、意味、規範強度、未完了範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
