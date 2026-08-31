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

actual repositoryへ次を追加した。

```text
contracts/
  README.md
  CONTRACT_CATALOG.md
  TRACEABILITY.md
  semantic-reference/
    SOZA_SEMANTIC_REFERENCE_v1alpha1.md
  decision-memory/
    SOZA_DECISION_MEMORY_v1alpha1.md
  capability/
    SOZA_CAPABILITY_OBSERVATION_v1alpha1.md
  interchange/
    SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md
  profiles/
    README.md
  history/
    HISTORICAL_CONTRACT_MAPPING.md
```

### 2. Contract familyを必要最小限へ絞った

Architecture上の関心領域を一つずつContractへ変換せず、独立versioningと相互運用境界が必要な4 familyへ集約した。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Inquiry / EpistemicsはSemantic Interchange上のsemantic artifact vocabularyとして扱い、現時点では独立Contract familyへ分けていない。

Cognitive Methodは重要な意味境界だが、historical M47/M48 Contractを無検査でcurrentへ戻さず、必要なinteroperability Scenarioが明確になった時点で別途再設計する。

Federation / Selective Disclosureはoptional Profileとして、具体的な外部交換要件が生じた時点でContract化を再評価する。

### 3. Semantic ContractとRepresentation Profileを分離した

Exact Artifact Bindingの意味は`soza.semantic-reference`が所有するが、JSON canonicalization、JCS、SHA-256、raw bytes等の検証方式はRepresentation Profileへ分離した。

```text
Semantic Contract != Representation Profile
```

stable Representation Profileは現時点でAcceptedしていない。

historical custom canonical JSON、JCS candidate、raw-bytes candidateは`contracts/profiles/README.md`で候補として整理し、ISSUE-000009へ戻した。

### 4. Decision Memoryの意味境界をContract化した

`soza.decision-memory`で次をinvariantとして固定した。

```text
Recommendation != Decision != Authority != Action Intent != Execution
Decision creation != uncertainty resolution
Rationale != private chain-of-thought
Responsibility != Authorization
```

過去Decisionのbasisを現在版へ黙って差し替えず、後続DecisionではSemantic Lineageを利用する。

### 5. Provider-neutral Capability ObservationをContract化した

`soza.capability-observation`で次を分離した。

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider Selection
  != Authority
  != Execution
```

Provider internal stateをSOZAのUniversal field setへ直接コピーせず、Provider-specific target referenceとmapping / adapter provenanceを保持できる境界を定めた。

```text
Provider state != Capability interpretation != Decision
```

### 6. portable Semantic Interchangeを薄いEnvelopeとして定めた

`soza.semantic-interchange`は巨大なUniversal Domain Modelではなく、各recordのcontract identity / versionを保持し、複数Semantic Contractを組み合わせるportable envelopeとした。

unknown contract version、partial knowledge、broken referenceを一つのinvalid状態へ潰さない。

Projection stateをcanonical semantic authorityへしない。

### 7. historical Contractとの対応を保存した

`contracts/history/HISTORICAL_CONTRACT_MAPPING.md`で、旧Contract / schemaについて次を区別した。

- Integrated
- Partially integrated
- Split
- Historical bridge only
- Candidate only
- Historical schema only

旧field名、enum、schema version、Go struct、algorithm、local PASSはcurrentへ自動継承していない。

### 8. Contract traceabilityを作成した

`contracts/TRACEABILITY.md`で、current ContractからREQ / ADR / Architecture concern / Acceptance Scenarioへ戻れる線を整理した。

REQ-0004、0010、0011、0012、0016等については、重要であっても独立Contractを現時点で増やさず、Architecture / Profile / Interchange invariant側に留める理由を明示した。

## Acceptance

### Semantic / Design Acceptance

- [x] current Contractの必要性がREQ / ADR / Architectureから説明できる。
- [x] contract_id / versionが明示されている。
- [x] semantic ContractとRepresentation Profileを分けている。
- [x] Markdown Contract Definitionとschemaの権威関係がADR-0021と一致する。
- [x] historical Contractとの対応を追跡できる。
- [x] Design / Executable Evidenceを混同していない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を完了した。

### Executable Acceptance

本Issueでは未達のまま別Issueへ分離した。

- machine-readable schema
- positive / negative fixture
- unknown-version / partial-knowledge fixture
- semantic invariant validator
- actual conformance runner

これらはISSUE-000031で追跡する。

## Evidence state at closure

- Contract Design Baseline: **Satisfied**
- Contract Traceability: **Satisfied**
- Representation Profile Stable Acceptance: **Not Yet Verified** — ISSUE-000009
- Contract Executable Evidence: **Not Yet Verified** — ISSUE-000031
- Capability Observation Executable Fixture: **Not Yet Verified** — ISSUE-000024 / ISSUE-000031
- Release / Operational: **Not Yet Verified**

## Follow-up

- ISSUE-000031 — current Contract schema / fixture / conformance
- ISSUE-000024 — Capability Observation fixture
- ISSUE-000009 — stable Representation Profile / historical M47 mapping
- ISSUE-000027 — Requirements registry checker
- ISSUE-000022 — repository baseline全体

## Natural Japanese review

current Contract 4 family、Catalog、Traceability、historical mapping、Representation Profile境界を戻り照合した後、Design baselineとExecutable未完了範囲を分離した。そのうえで、意味、規範強度、Evidence状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
