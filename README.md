# 綜座 / SOZA

更新日: 2026-08-31  
状態: **Product / Requirements / Architecture / Contract baseline + fixture-scoped Executable Evidence — development in progress**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で増やすことではありません。実行手段が変わっても残る、意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 現在の開発branch

通常の開発は`develop/vX.Y.Z`形式のbranchで進めます。

現在の開発branchは`develop/v0.1.0`です。

`main`は安定した基線のために保持し、開発中の変更を直接積み上げないことを原則とします。詳細は`plan/DEVELOPMENT_WORKFLOW.md`を参照してください。

## 2. actual repositoryの現在地

2026-08-31時点で、`develop/v0.1.0`のrootには次が実体化されています。

```text
.github/
product/
requirements/
architecture/
contracts/
fixtures/
plan/
tools/
```

current `runtime/` baselineはまだ実体化していません。

正本関係は次のとおりです。

```text
Product Value / Value Model / Value Acceptance
  ↓
Requirements / Acceptance Scenarios
  ↓
ADR
  ↓
Reference Architecture
  ↓
Contract Definition
  ↓
Schema / Validator / Fixture
  ↓
Runtime / Provider Integration
```

現在は、上位Design baselineに加えて、Requirements registryとContract / Capability fixtureについて**限定されたExecutable Evidence**までactual repository上で再現できます。

一方、current runtime、stable Representation Profile、release、operational evidenceは未完成です。

## 3. Evidenceの読み方

SOZAでは、次を同一視しません。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
```

また、historical candidateのPASSはcurrent PASSではありません。

```text
historical PASS != current PASS
```

M48〜M50等の旧candidateは意味核・反例・実装候補として参照できますが、current Product Value / REQ / ADR / Contractへ再照合し、actual repositoryで検証するまでcurrent Executable Evidenceへ昇格しません。

## 4. 最初に読む文書

### Product Value

1. `product/value/SOZA_PRODUCT_VALUE.md`
2. `product/value/SOZA_VALUE_MODEL.md`
3. `product/value/SOZA_VALUE_ACCEPTANCE.md`
4. `product/vision/SOZA_PRODUCT_VISION.md`
5. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

### Requirements

6. `requirements/README.md`
7. `requirements/PRODUCT_REQUIREMENTS.md`
8. `requirements/ACCEPTANCE_SCENARIOS.md`
9. `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

### Architecture

10. `architecture/README.md`
11. `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
12. `architecture/TRACEABILITY.md`
13. `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

### Contracts

14. `contracts/README.md`
15. `contracts/CONTRACT_CATALOG.md`
16. `contracts/TRACEABILITY.md`
17. `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
18. `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
19. `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
20. `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
21. `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`
22. `contracts/history/HISTORICAL_CONTRACT_MAPPING.md`

### Planning / Decisions

23. `plan/README.md`
24. `plan/DEVELOPMENT_WORKFLOW.md`
25. `plan/DOCUMENT_AUTHORING_STANDARD.md`
26. `plan/registry.yaml`

個別の設計判断は`plan/adr/`、未完了作業や調査は`plan/issue/`を参照してください。

## 5. Product Valueの中心

SOZAでは、少なくとも次を重要な意味差として扱います。

```text
Observation
  != Interpretation / Hypothesis
  != Recommendation
  != Decision
  != Authority
  != Action Intent
  != Execution
```

これは処理を細分化するための形式ではありません。後から、何が観測で、何が解釈で、誰または何が何を判断し、どのAuthorityで何が実行されたのかを再構成するための境界です。

あわせて、次を守ります。

- `Unknown != No`
- `Conflict != latest-wins`
- `not observed != unavailable`
- `not_verified != failed`
- CapabilityとProviderを同一視しない。
- Capability ObservationをMatchingやDecisionへ自動昇格しない。
- actor / Providerの種類だけからAuthorityやTrustを推定しない。
- ProviderやStorageが変わっても過去Decisionの意味を変えない。
- private chain-of-thoughtの保存を耐久的意味の前提にしない。
- Design EvidenceをExecutable / Release / Operational Evidenceへ自動昇格させない。

## 6. Product Valueの評価軸

Product Valueは単一スコアへ還元せず、`SOZA_VALUE_MODEL.md`の8軸で確認します。

- V1 — Historical Reconstruction
- V2 — Semantic Separation
- V3 — Revision Integrity
- V4 — Provider Independence
- V5 — Uncertainty Preservation
- V6 — Human / AI Readability
- V7 — Progressive Explicitness
- V8 — Execution Independence

これらの軸自体を一つの総合点へ圧縮しません。

## 7. Requirements baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenarioは`SCN-0001`〜`SCN-0017`です。

旧`SOZA-PR-*`、`SOZA-NFR-*`、`SOZA-AS-*`はhistorical provenanceとしてmappingに残し、current IDへ機械的にrenameしていません。

RequirementがAcceptedであることと実装済みであることは別です。

```text
Requirement Accepted != Executable Evidence Satisfied
```

### Requirements Registry Executable Evidence

current registryについて、GitHub Actions `Requirements Registry Conformance`で次を再現しています。

```text
PASS: requirements registry checker self-tests
PASS: 22 requirements / 17 scenarios
```

Run ID: `33346697016`

このPASSが示すのは、stable ID、相互参照、Value Axis、status / Evidence vocabulary等のregistry構造整合です。Requirementの意味内容やimplementation coverageそのものを証明するものではありません。

## 8. Reference Architecture baseline

current ArchitectureはM48 / M49 / M50等のMilestone順ではなく、意味上のarchitecture concernへ再構成しています。

主な関心領域:

- Durable Semantic Core
- Inquiry / Epistemic State
- Cognitive Method
- Decision Memory
- Capability Definition / Observation / Choice
- Responsibility / Authority boundary
- Semantic Reference / Revision / Exact Binding
- Profile / Policy
- Federation / Selective Disclosure
- Provider / Adapter
- Projection
- Persistence
- Evidence / Assurance boundary

これらを一対一のservice、Go package、databaseへ固定しません。

`architecture/TRACEABILITY.md`ではREQ-0001〜REQ-0022をArchitecture concernへ追跡できます。

## 9. Contract baseline

current Contractは、独立versioningと相互運用境界が必要な4 familyへ絞っています。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Semantic ContractとRepresentation Profileは分離します。

```text
Semantic Contract != Representation Profile
```

Markdown Contract Definitionをsemantic normative sourceとし、JSON Schemaはv1alpha1のmachine-readable representationとして扱います。

### Contract Executable Evidence

current Contractについて、GitHub Actions `Contract Conformance`で17 fixtureを検証しています。

Run ID: `33346472419`

確認した主な境界:

- Capability Observation F1〜F7
- Recommendation without Decision
- Decision with unresolved Unknown / Conflict
- Decision recordへのAuthority埋め込み拒否
- same-logical-id lineage without exact endpointsのsemantic rejection
- bundle exact recordとDecision basisのdigest不一致検出
- unknown Contract versionを`not_verified`として扱う
- `failed`と`not_verified`の分離
- partial knowledgeをmalformed interchangeと同一視しない

詳細は`contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`を参照してください。

このPASSはfixture-scoped Executable Evidenceです。release readinessやoperational interoperabilityを意味しません。

## 10. SOZAとTEI

鼎（TEI）はSOZAそのものではなく、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

SOZA関連製品であるという理由だけでTEIを優先しません。

TEI固有のApplication、Database、Release、Deployment等をSOZA Universal Coreへ複製せず、必要な情報はProvider-neutralなCapability ObservationやProvider-specific referenceから扱います。

## 11. Exact Binding / Representation Profile

Exact Artifact Bindingの意味境界はcurrent Contractにありますが、stableなcanonicalization / digest ProfileはまだAcceptedしていません。

ISSUE-000009は**Blocked**を維持しています。

未完了の中心:

- historical M47 digest規則の正確な確認とmapping
- stable JCS verifierの選定とRFC test vector適合
- high-precision semantic valueをbinary64へ暗黙丸めしない境界
- verifier / payloadが失われたhistorical bindingのactual運用

fixtureで使う`fixture.raw-json/v0`は検査用のopaque Profile identityであり、stable Representation Profileではありません。

## 12. 現在のPlan

`plan/registry.yaml`ではADR-0021、ISSUE-000031まで管理しています。

現在の主要な未完了項目:

- ISSUE-000009 — stable Exact Binding Representation Profile / historical M47 mapping
- ISSUE-000015 — 既存開発文書の自然な日本語による全面監査
- ISSUE-000021 — design history provenance監査（Deferred）
- ISSUE-000022 — repository baseline全体の実体化

Requirements registry、Capability Observation F1〜F7、Contract schema / fixture / conformanceはcurrent actual repositoryで完了済みです。

Statusの正本は`plan/registry.yaml`と各Issue本文です。

## 13. 次の実体化

当面の優先順位は次のとおりです。

1. Product Value / REQ / ADR / Architecture / Contractの整合維持
2. current `runtime/`境界の設計と最小vertical slice
3. historical Go candidateのcurrent Contractへの差分評価
4. Provider adapterの最小実装
5. stable Exact Binding Representation Profileの安定化
6. Contract fixtureとruntimeを横断するend-to-end conformance
7. 既存文書を含む自然な日本語監査
8. release / operational Evidence

runtimeのためにArchitecture concernを一対一のpackage構成へ固定しません。また、旧candidateを一括コピーせず、current Contractから必要性を再導出します。

## 14. Releaseについて

`develop/v0.1.0`は開発中のbaselineです。**releaseやOperational Evidenceを主張する状態ではありません。**

`main`へ統合する際は、Product Value、Requirements、ADR、Architecture、Contracts、actual Executable Evidenceを戻り照合し、実際に得られたEvidenceを超えない範囲で状態を更新します。

## 15. 文書品質

SOZAでは、開発文書の自然な日本語を設計品質の一部として扱います。

内容・構造・技術的一貫性を整えた後、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設け、その後に意味監査を行います。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。既存文書の再監査はISSUE-000015で継続しています。

## 16. 自然な日本語レビュー

actual root tree、Requirements Registry CI、Contract Conformance CI、Capability Observation F1〜F7、plan registryへ戻って現在地を再確認しました。そのうえで、Design、fixture-scoped Executable、未検証のruntime / Representation / Release / Operational領域を分離し、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
