# ISSUE-000031: current Contractのschema・fixture・conformanceを実装する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

current Contract Design baselineをmachine-readable schema、positive / negative fixture、validatorへ落とし、actual repository上でExecutable Evidenceを再現できる状態にする。

Contract Definitionの意味をschema都合で変更せず、schemaにしか存在しないsemantic requirementを作らない。

## Inputs

- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
- `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
- `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
- `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
- `contracts/TRACEABILITY.md`
- ADR-0021

## Initial executable scope

### 1. machine-readable schema

少なくとも次を検討する。

```text
contracts/schemas/v1alpha1/
  semantic-reference.schema.json
  decision-memory.schema.json
  capability-observation.schema.json
  semantic-interchange.schema.json
```

JSON Schemaは初期portable representation候補であり、JSONをUniversal semantic representationへ昇格させない。

### 2. fixtures

少なくとも次を用意する。

- valid logical reference
- valid exact binding
- invalid same-logical-id lineage without exact endpoints
- `not_verified`と`failed`の分離
- Decision with unresolved Unknown / Conflict
- Recommendation without Decision
- Decision without Recommendation
- Decision does not imply Authority
- Provider-neutral Capability Observation
- Observation with missing / conflicting data
- adapter / mapping provenance
- unknown contract version
- partial-knowledge interchange
- invalid flattening of Decision / Authority / Execution

### 3. conformance runner

少なくとも次を検査する。

- schema validation
- cross-reference consistency
- contract_id / version
- semantic invariantのうちschemaだけで検査できないもの
- expected PASS / expected FAIL

## Relationship with other Issues

### ISSUE-000024

Capability Observation fixtureは本Issueのfixture infrastructureと共通化できる。

ISSUE-000024の意味要件を吸収せず、Capability-specific Acceptanceを同Issueから追跡する。

### ISSUE-000009

Representation Profile verifierはISSUE-000009のstable profile判断を待つ部分がある。

Semantic schema / fixtureは先行できるが、stable JCS verifierが未確定のままExact Binding全体をExecutable Satisfiedにはしない。

### ISSUE-000027

Requirements registry checkerと本Contract checkerは目的が異なる。

共通の軽量validation utilityを使うことはできるが、REQ / SCN台帳検査とsemantic Contract conformanceを一つの巨大checkerへ統合しない。

## Constraints

- historical schemaを一括コピーしない。
- old local PASSをcurrent PASSへ継承しない。
- schema validationだけでsemantic conformance完了としない。
- Representation Profile未確定部分を推測でstable化しない。
- JSON Schemaで表現しにくいinvariantはvalidator / fixtureへ分離する。
- generated codeをsemantic authorityにしない。

## Acceptance

### Executable Acceptance

- [ ] current Contractごとに必要なschemaがactual treeに存在する。
- [ ] positive / negative fixtureが存在する。
- [ ] unknown-version / partial-knowledge fixtureが存在する。
- [ ] cross-contract referenceの検査ができる。
- [ ] Decision / Authority / Executionの非同一性をfixtureで確認できる。
- [ ] Capability ObservationのProvider-neutralityをfixtureで確認できる。
- [ ] `not_verified`と`failed`を区別できる。
- [ ] actual conformance runnerの結果を再現できる。
- [ ] schema / validator / fixtureを自然な命名・説明へ整え、文書との意味監査を行っている。

### Release / Operational Acceptance

本Issueでは要求しない。

## Natural Japanese review

Contract DesignとExecutable Evidenceを混同しないよう作業範囲を整理した後、未確定Profileを勝手に確定せず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
