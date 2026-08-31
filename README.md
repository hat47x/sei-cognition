# 綜座 / SOZA

更新日: 2026-08-31  
状態: **Product / Requirements / Architecture / Contract / Profile baseline + scoped Executable Evidence — development in progress**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で囲い込むことではありません。実行手段が変わっても残る、意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 開発branch

通常の開発は`develop/vX.Y.Z`形式のbranchで進めます。

現在の開発branchは`develop/v0.1.0`です。

`main`は安定した基線として保持し、開発中の変更を直接積み上げないことを原則とします。詳細は`plan/DEVELOPMENT_WORKFLOW.md`を参照してください。

## 2. actual repositoryの現在地

2026-08-31時点では、少なくとも次がactual treeにあります。

```text
.github/
product/
requirements/
architecture/
contracts/
fixtures/
plan/
runtime/
tools/
```

正本関係は概ね次のとおりです。

```text
Product Value / Value Model / Value Acceptance
  ↓
Requirements / Acceptance Scenarios
  ↓
ADR
  ↓
Reference Architecture
  ↓
Contract Definition / Representation Profile
  ↓
Schema / Validator / Fixture
  ↓
Runtime / Provider Adapter / Provider Integration
```

current repositoryでは、上位Design baselineに加え、限定された範囲でExecutable Evidenceまで実体化しています。

一方、Provider Adapterの次slice、release、production operation、利用者・組織におけるOutcomeは未検証です。

## 3. Evidenceの読み方

SOZAでは、少なくとも次を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

また、historical candidateのPASSはcurrent PASSではありません。

```text
historical PASS != current PASS
```

M48〜M50等の旧candidateは、意味核、反例、実装候補として参照できます。ただし、current Product Value / REQ / ADR / Architecture / Contractへ再照合し、actual repositoryで検証するまでcurrent Evidenceへ自動継承しません。

本番で動くことと、利用者に価値が届くことも分けます。

```text
Operational success != user-value realization
```

## 4. 最初に読む文書

### Product

1. `product/README.md`
2. `product/value/SOZA_PRODUCT_VALUE.md`
3. `product/value/SOZA_VALUE_MODEL.md`
4. `product/value/SOZA_VALUE_ACCEPTANCE.md`
5. `product/value/SOZA_VALUE_TRACEABILITY.md`
6. `product/vision/SOZA_PRODUCT_VISION.md`
7. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

### Requirements

8. `requirements/README.md`
9. `requirements/PRODUCT_REQUIREMENTS.md`
10. `requirements/ACCEPTANCE_SCENARIOS.md`
11. `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

### Architecture

12. `architecture/README.md`
13. `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
14. `architecture/TRACEABILITY.md`
15. `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

### Contracts / Representation Profiles

16. `contracts/README.md`
17. `contracts/CONTRACT_CATALOG.md`
18. `contracts/TRACEABILITY.md`
19. `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
20. `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
21. `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
22. `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
23. `contracts/profiles/README.md`
24. `contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md`
25. `contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md`

### Planning / Decisions

26. `plan/README.md`
27. `plan/DEVELOPMENT_WORKFLOW.md`
28. `plan/DOCUMENT_AUTHORING_STANDARD.md`
29. `plan/registry.yaml`
30. `plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`

個別の設計判断は`plan/adr/`、未完了作業・検証・調査は`plan/issue/`を参照してください。

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
- Design EvidenceをExecutable / Release / Operational / Outcomeへ自動昇格させない。

## 6. Product Valueの評価軸

Product Valueは単一スコアへ還元せず、8軸で確認します。

- V1 — Historical Reconstruction
- V2 — Semantic Separation
- V3 — Revision Integrity
- V4 — Provider Independence
- V5 — Uncertainty Preservation
- V6 — Human / AI Readability
- V7 — Progressive Explicitness
- V8 — Execution Independence

各軸の受入れ境界は`SOZA_VALUE_ACCEPTANCE.md`、現在の追跡は`SOZA_VALUE_TRACEABILITY.md`を参照してください。

## 7. Requirements baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenarioは`SCN-0001`〜`SCN-0017`です。

RequirementがAcceptedであることと、実装済みであることは別です。

```text
Requirement Accepted != Executable Evidence Satisfied
```

Requirements Registry Conformance:

- Run ID: `33346697016`
- checker self-tests: **PASS**
- `22 requirements / 17 scenarios`: **PASS**

これはstable ID、相互参照、Value Axis、status等のregistry構造整合に対するExecutable Evidenceです。Requirementの意味内容やproduction implementationを証明するものではありません。

## 8. Reference Architecture baseline

current ArchitectureはMilestone順や実装package順ではなく、意味上のarchitecture concernへ再構成しています。

主なconcern:

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

`architecture/TRACEABILITY.md`ではREQ-0001〜REQ-0022をcurrent concernへ追跡しています。

Architecture concernをGo package、service、database等へ一対一に固定しません。

## 9. Contract baseline

current Contractは、独立versioningと相互運用境界が必要な4 familyへ絞っています。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Markdown Contract Definitionをsemantic normative sourceとし、JSON Schemaはcurrent v1alpha1のmachine-readable representationとして扱います。

Contract Conformance:

- Run ID: `33346472419`
- fixture count: `17`
- conclusion: **success**

これはfixture-scoped Executable Evidenceです。

## 10. Exact Binding / Representation Profile

Semantic ContractとRepresentation Profileは分離します。

```text
Semantic Contract != Representation Profile != verifier implementation
```

ADR-0023 / ISSUE-000009により、current/future Exact Binding向けProfileとして次を定義しています。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Representation Profile Conformance:

- Run ID: `33347989530`
- Profile fixture: **success**
- JCS Go probe: **success**

historical M47 digest mappingはcurrent Profileとは分離し、ISSUE-000034でBlockedとして追跡します。

## 11. first semantic runtime slice

ADR-0022に従い、最初のruntime sliceはread / validate / reconstructへ限定しています。

```text
runtime/go/semanticruntime/
```

Semantic Runtime Conformance:

- Run ID: `33348972805`
- Head SHA: `834c3f2a8bd911829743c1582ef09f098c776a54`
- current Contract fixture checker: **PASS**
- Go runtime tests: **PASS**
- conclusion: **success**

このPASSはfirst runtime sliceのExecutable Evidenceであり、SOZA全runtimeやproduction Provider統合の完成を意味しません。

## 12. Provider Adapter observation mapping boundary

ADR-0024では、Provider AdapterをProvider固有stateの共通schemaではなく、Capability Observationへ変換する観測・解釈境界として定めます。

```text
Provider-owned state
  + observation context
        ↓
Adapter / Mapping
        ↓
Capability Observation
```

Adapterによるfield mapping、unit conversion、status interpretation、aggregation等は意味上の解釈を含み得るため、mapping provenanceを保持します。

次を維持します。

```text
missing != false
not observed != unavailable
Adapter mapping != Matching != Decision != Authority != Execution
```

最初のExecutable sliceはISSUE-000036でsynthetic heterogeneous Providersを使って検証します。

現在のStatus:

- ADR-0024: **Accepted**
- ISSUE-000035: **Resolved**
- ISSUE-000036: **Open**

したがってProvider Adapterについて現在主張できるのはDesign Evidenceまでです。

## 13. SOZAとTEI

鼎（TEI）はSOZAそのものではなく、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

関連製品であるという理由だけでTEIを優先しません。TEI固有のApplication、Database、Release、Deployment等をSOZA Universal Coreへ複製せず、必要な情報をProvider-neutralなCapability ObservationやProvider-specific referenceから扱います。

TEI production Adapterを最初のProvider Adapter検証対象にはしません。まずsyntheticな異質Providerで境界を検証します。

## 14. 現在のPlan

2026-08-31時点で、planning registryはADR-0024、ISSUE-000036まで管理しています。

主な未完了項目:

- ISSUE-000015 — 既存開発文書の自然な日本語による全面監査: **In Progress**
- ISSUE-000021 — design history provenance監査: **Deferred**
- ISSUE-000022 — repository baseline全体のclosure監査: **In Progress**
- ISSUE-000034 — historical M47 digest Profileの回収: **Blocked**
- ISSUE-000036 — synthetic Provider Adapter vertical slice: **Open**

Requirements registry、Capability Observation fixture、Contract schema / conformance、current Representation Profile、first semantic runtime sliceは、それぞれ定めた限定範囲でResolvedしています。

Statusの正本は`plan/registry.yaml`と各Issue本文です。

## 15. 次に深める領域

現在の上位優先順位は、概ね次です。

1. Product Value → REQ → ADR → Architecture → Contract / Profile / runtime / Adapterの追跡整合を維持する。
2. synthetic Provider Adapter sliceでADR-0024をExecutable Evidenceへ落とす。
3. 既存active開発文書を自然な日本語で再監査する。
4. repository baseline全体のclosure条件を監査する。
5. historical M47 digestについて、推測せずEvidenceを回収する。
6. Product Valueから必要性を確認したうえで、production Provider integrationや次のruntime sliceを設計する。
7. Release Evidenceを得る条件を整える。
8. Operational / Adoption・Outcome Evidenceを、実利用が始まった時点で別の高さとして収集する。

実装量やCI本数をProduct ValueのKPIにはしません。

## 16. Releaseについて

`develop/v0.1.0`は開発中のbaselineです。**Release Evidence、Operational Evidence、Adoption / Outcome Evidenceを主張する状態ではありません。**

`main`へ統合する際は、Product Value、Requirements、ADR、Architecture、Contract / Profile、actual Executable Evidenceを戻り照合し、実際に得られたEvidenceを超えない範囲で状態を更新します。

## 17. 文書品質

SOZAでは、開発文書の自然な日本語を設計品質の一部として扱います。

内容・構造・技術的一貫性を整えた後、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設け、その後に意味監査を行います。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。既存文書の再監査はISSUE-000015で継続します。

## 18. 自然な日本語レビュー

actual Product、Requirements、ADR-0001〜0024、Architecture、4 Contract family、Representation Profile、first semantic runtime slice、Provider Adapter observation mapping boundary、actual CI結果、plan registryへ戻って現在地を再確認しました。そのうえで、Design / Executable / Release / Operational / Adoption・OutcomeのEvidence強度を混同しないよう全体を再構成しました。最後に、意味・仕様・留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
