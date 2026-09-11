# ISSUE-000030: current SOZA Contract baselineをactual repositoryへ実体化する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0019, ADR-0021**  
Updated: 2026-08-31

## Goal

ADR-0021に従い、current Architectureで相互運用・historical reconstruction・verificationのために必要と判断された境界を、human-readable Contract Definitionとしてactual repositoryへ実体化する。

historical Contract候補を一括復元せず、current REQ / ADR / Architectureで必要なContractだけを再構成する。

## Resolution

### 1. current Contract baselineを実体化した

current Contract familyは次の4つである。

- `sei.semantic-reference/v1alpha1`
- `sei.decision-memory/v1alpha1`
- `sei.capability-observation/v1alpha1`
- `sei.semantic-interchange/v1alpha1`

Architecture上の関心領域を一つずつContractへ変換せず、独立versioningと相互運用境界が必要な範囲へ絞った。

### 2. Semantic ContractとRepresentation Profileを分離した

Exact Bindingの意味は`sei.semantic-reference`が所有し、canonicalization、digest algorithm、対象bytes等のmechanicsはRepresentation Profileへ分離した。

```text
Semantic Contract != Representation Profile
```

本Issueの作成時点ではstable Profileを未確定としていたが、その後ADR-0023 / ISSUE-000009で次をcurrent / future基線としてAcceptedし、fixture-scoped Executable Evidenceまで得た。

```text
sei.jcs+sha256/v1alpha1
sei.raw-bytes+sha256/v1alpha1
```

historical M47 digest mappingはISSUE-000034へ分離している。

### 3. Decision Memoryの意味境界をContract化した

```text
Recommendation != Decision != Authority != Action Intent != Execution
Decision creation != uncertainty resolution
Rationale != private chain-of-thought
Responsibility != Authorization
```

過去Decisionのbasisを現在版へ黙って差し替えず、後続DecisionではSemantic Lineageを利用する。

### 4. Provider-neutral Capability ObservationをContract化した

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider Selection
  != Authority
  != Execution
```

Provider internal stateをUniversal field setへ直接コピーせず、Provider-specific target referenceとmapping / adapter provenanceを保持できる境界を定めた。

### 5. portable Semantic Interchangeを薄いEnvelopeとして定めた

各recordのContract identity / versionを保持し、複数Semantic Contractを組み合わせるportable envelopeとした。

unknown Contract version、partial knowledge、broken referenceを一つのinvalid状態へ潰さず、Projection stateをcanonical semantic authorityへしない。

### 6. historical Contractとの対応とTraceabilityを保存した

`contracts/history/HISTORICAL_CONTRACT_MAPPING.md`で旧Contract / Schemaの統合状態を記録し、`contracts/TRACEABILITY.md`でcurrent ContractからREQ / ADR / Architecture concern / Scenarioへ戻れる線を整理した。

旧field名、enum、schema version、Go struct、algorithm、local PASSはcurrentへ自動継承していない。

## Acceptance

### Semantic / Design Acceptance

- [x] current Contractの必要性がREQ / ADR / Architectureから説明できる。
- [x] contract_id / versionが明示されている。
- [x] Semantic ContractとRepresentation Profileを分けている。
- [x] Markdown Contract DefinitionとSchemaの権威関係がADR-0021と一致する。
- [x] historical Contractとの対応を追跡できる。
- [x] Design / Executable Evidenceを混同していない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を完了した。

### Downstream Executable Acceptance

本Issue自身はDesign baselineを閉じた。その後、別Issueで次を実体化した。

- machine-readable Schema / positive / negative / boundary fixture / semantic validator: **Satisfied — ISSUE-000031**
- Capability Observation F1〜F7: **Satisfied — ISSUE-000024**
- Representation Profile fixture conformance: **Satisfied — ISSUE-000009**
- first semantic runtime: **Satisfied — ISSUE-000033**
- synthetic Provider Adapter: **Satisfied — ISSUE-000036**

```text
Downstream Executable Evidence exists
  != this Design Issue was an implementation Issue
```

## Current evidence state

- Contract Design Baseline: **Satisfied**
- Contract Traceability: **Satisfied**
- Representation Profile current baseline: **Satisfied**
- Contract Fixture-scoped Executable Evidence: **Satisfied**
- Capability Observation Fixture Evidence: **Satisfied**
- first Runtime consumption of current Contract: **Satisfied within scoped runtime**
- historical M47 digest mapping: **Not Yet Verified — ISSUE-000034**
- Release / Operational: **Not Yet Verified**

## Follow-up

- ISSUE-000031 — Contract conformance（Resolved）
- ISSUE-000024 — Capability Observation fixture（Resolved）
- ISSUE-000009 — current Representation Profile（Resolved）
- ISSUE-000033 — first semantic runtime（Resolved）
- ISSUE-000036 — synthetic Provider Adapter（Resolved）
- ISSUE-000034 — historical M47 digest mapping（Blocked）

## Natural Japanese review

current Contract 4 family、Catalog、Traceability、historical mapping、Representation Profile、Schema / Fixture conformance、first runtime Evidenceへ戻って再照合した。そのうえで、本Issue自身のDesign closureと後続IssueのExecutable Evidenceを分離し、意味、規範強度、Evidence状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
