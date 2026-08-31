# ISSUE-000031: current Contractのschema・fixture・conformanceを実装する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

current Contract Design baselineをmachine-readable Schema、positive / negative / boundary fixture、semantic validatorへ落とし、actual repository上でfixture-scoped Executable Evidenceを再現できる状態にする。

Contract Definitionの意味をSchema都合で変更せず、Schemaにしか存在しないsemantic requirementを作らない。

## Resolution

### 1. 4 ContractのJSON Schemaを実体化した

```text
contracts/schemas/v1alpha1/
  semantic-reference.schema.json
  decision-memory.schema.json
  capability-observation.schema.json
  semantic-interchange.schema.json
```

JSON Schemaはcurrent v1alpha1のmachine-readable representationであり、JSONをUniversal semantic representationへ昇格させない。

### 2. Schemaとsemantic validatorの責務を分けた

Schemaで自然に検査できるfield / shapeと、cross-record relationを見なければ判断できないsemantic invariantを分離した。

```text
Schema valid != Semantic conformance complete
```

### 3. Decision MemoryのRecommendation / Decision境界を実体化した

Recommendation-onlyを正常状態として扱い、Decisionは`unresolved_refs`を保持できる。Decision recordへ未定義のAuthorityを埋め込むfixtureは拒否する。

### 4. Capability Observation F1〜F7を検証可能にした

partial degradation、proposed / actual、Environment binding、Observation gap、cross-provider comparison、historical reconstruction、selective disclosureをactual fixtureとして検査した。

### 5. negative / boundary fixtureを追加した

current checkerは17 fixtureを扱い、Schema FAIL、Semantic FAIL、unknown Contractの`not_verified`、Verification Outcomeの`failed / not_verified`分離、Recommendation without Decision、Decision with unresolved、partial knowledge等を期待結果として検査する。

### 6. actual conformance runnerを実装した

- `tools/check_contract_conformance.py`
- `tools/contract-check-requirements.txt`
- `.github/workflows/contract-conformance.yml`

GitHub Actions `Contract Conformance` Run ID `33346472419`で17 fixtureの期待結果一致を確認した。

詳細は`contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`を正とする。

## Acceptance

- [x] current Contractごとに必要なSchemaがactual treeに存在する。
- [x] positive / negative fixtureが存在する。
- [x] unknown-version / partial-knowledge fixtureが存在する。
- [x] cross-contract / cross-record exact referenceの整合を検査できる。
- [x] Decision / Authority / Executionの非同一性をfixtureで確認できる。
- [x] Capability ObservationのProvider-neutralityをfixtureで確認できる。
- [x] `not_verified`と`failed`を区別できる。
- [x] actual conformance runnerの結果をGitHub Actionsで再現できる。
- [x] Schema / validator / fixtureを文書へ戻して意味監査した。

## Current evidence state

本Issueのclosure後にRepresentation ProfileとRuntimeが進展したため、current状態を次のように再基線化する。

- Contract Design Baseline: **Satisfied**
- Contract v1alpha1 Fixture-scoped Executable Conformance: **Satisfied**
- current Representation Profile baseline: **Satisfied — ADR-0023 / ISSUE-000009**
- historical M47 digest mapping: **Not Yet Verified — ISSUE-000034**
- first semantic runtime consumption: **Satisfied within ISSUE-000033 scope**
- synthetic Provider Adapter mapping: **Satisfied within ISSUE-000036 scope**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

`fixture.raw-json/v0`はfixture内部のhistorical exact-reference整合検査に使ったopaque Profile identityであり、current stable Profileの代替ではない。current / future ProfileはADR-0023で別途確定している。

```text
Contract fixture PASS
  != Runtime all requirements complete
  != Release readiness
```

## Follow-up

- ISSUE-000009 — current Representation Profile（Resolved）
- ISSUE-000033 — first semantic runtime（Resolved）
- ISSUE-000036 — synthetic Provider Adapter（Resolved）
- ISSUE-000034 — historical M47 digest recovery（Blocked）

## Natural Japanese review

4 Schema、17 fixture、semantic checker、Contract CI、current Representation Profile、first runtime、synthetic Adapter Evidenceへ戻って再照合した。その後、fixture-scoped Executable Evidenceと未検証のhistorical / Release / Operational領域を分離し、意味、条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
