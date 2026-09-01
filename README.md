# 綜座 / SOZA

更新日: 2026-09-01  
状態: **Current semantic baseline + scoped Executable Evidence — development in progress**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で囲い込むことではありません。実行手段が変わっても残る意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 開発branch

通常の開発は`develop/vX.Y.Z`形式のbranchで進めます。現在の開発branchは`develop/v0.1.0`です。

`main`は安定した基線として保持し、開発中の変更を直接積み上げないことを原則とします。詳細は`plan/DEVELOPMENT_WORKFLOW.md`を参照してください。

## 2. actual repositoryの現在地

current treeには少なくとも次があります。

```text
.github/
product/
requirements/
architecture/
contracts/
evaluation/
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
Semantic Contract / Representation Profile
  ↓
Schema / Fixture / Validator
  ↓
Runtime / Provider Adapter / Payload Source / Projection Evaluation
  ↓
Executable Evidence
```

current repositoryでは、上位Design baselineに加え、Contract / Profile / first runtime / synthetic Provider Adapter / Representation Verifier / synthetic Payload Source / V6・V7 evaluationの限定された範囲でExecutable Evidenceまで実体化しています。

一方、production Provider integration、production Storage integration、Release、Operational、Adoption / Outcome Evidenceはまだありません。

## 3. Evidenceの読み方

SOZAでは次を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

historical candidateのPASSはcurrent PASSではありません。

```text
historical PASS != current PASS
```

本番で動くことと、利用者・組織に価値が届くことも別です。

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

### Architecture

11. `architecture/README.md`
12. `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
13. `architecture/TRACEABILITY.md`

### Contracts / Representation Profiles

14. `contracts/README.md`
15. `contracts/CONTRACT_CATALOG.md`
16. `contracts/TRACEABILITY.md`
17. `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
18. `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
19. `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
20. `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
21. `contracts/profiles/README.md`
22. `contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md`
23. `contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md`

### Planning / Decisions

24. `plan/README.md`
25. `plan/DEVELOPMENT_WORKFLOW.md`
26. `plan/DOCUMENT_AUTHORING_STANDARD.md`
27. `plan/registry.yaml`
28. `plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`

Statusの正本は各ADR / Issue本文と`plan/registry.yaml`です。

## 5. 意味境界

SOZAでは少なくとも次を同一視しません。

```text
Observation
  != Interpretation / Hypothesis
  != Recommendation
  != Decision
  != Authority
  != Action Intent
  != Execution
  != Business Outcome
```

加えて、次を守ります。

- `Unknown != No`
- `Conflict != latest-wins`
- `not observed != unavailable`
- `not_verified != failed`
- Capability != Provider
- Capability Definition != Capability Observation
- Matching != Decision
- Pattern != Cognitive Method
- Method Application != Assurance
- Logical Reference != Exact Historical Binding
- Projection != Canonical Semantic Authority
- Requirement != Acceptance Scenario != Test Case
- Semantic Contract != Representation Profile

## 6. Product Value

Product Valueは単一スコアへ還元せず、8軸で確認します。

- V1 — Historical Reconstruction
- V2 — Semantic Separation
- V3 — Revision Integrity
- V4 — Provider Independence
- V5 — Uncertainty Preservation
- V6 — Human / AI Readability
- V7 — Progressive Explicitness
- V8 — Execution Independence

各軸の受入れ境界は`SOZA_VALUE_ACCEPTANCE.md`、現在の追跡は`SOZA_VALUE_TRACEABILITY.md`を正とします。

## 7. Requirements / Architecture / Contract baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0017`です。

current Semantic Contractは次の4 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

代表的なExecutable Evidence:

- Requirements Registry: Run `33349256675` — **success**
- Contract Conformance: 17 fixtures — **success**
- first Semantic Runtime: Run `33348972805` — **success**

これらのPASSをRequirement全体やproduction readinessへ拡張しません。

## 8. Exact Binding / Representation Profile

Semantic ContractとRepresentation Profileを分離します。

```text
Semantic Contract != Representation Profile != verifier implementation
```

current/future Exact Binding向けProfile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Profile fixture / JCS probeはRun `33347989530`で**success**しています。

さらに、current runtimeにはProfileを解決するin-process Verifier Registryがあります。

- Verifier Registry: Run `33452115728` — **success**

VerifierはExact Bindingをmutateせず、少なくとも次を区別します。

```text
known profile + digest match      → verified
known profile + digest mismatch   → failed
unknown profile / unavailable     → not_verified
```

## 9. payload acquisition boundary

ISSUE-000040で、payload取得をVerifierから分離しました。

```text
Exact Binding
  ↓
Payload Source
  ↓
Verifier Registry
  ↓
Verification Outcome
```

synthetic Payload SourceによるRun `33457416359`は**success**しています。

確認した境界:

- raw bytes / JCS payloadをsource経由で検証できる。
- zero-length payloadを「取得不能」と誤認しない。
- unavailable / source error / local size limitを`failed`へ変換しない。
- operational acquisition errorとsemantic Verification Outcomeを分ける。
- Storage固有locatorをExact Binding / Profileへ書き戻さない。

これはproduction S3 / MinIO / filesystem / HTTP integrationのEvidenceではありません。

## 10. synthetic Provider Adapter

ADR-0024に従い、Provider固有stateは共通Universal `ProviderState`へ押し込めず、各AdapterからCapability Observationへ収束させます。

```text
runtime/go/provideradapter/
fixtures/providers/synthetic/
```

代表run:

- first synthetic Adapter slice: `33349604842` — **success**
- Provider-specific field非漏洩hardening: `33349801993` — **success**

AdapterはRecommendation / Decision / Authority / Executionを自動生成しません。

## 11. V6 / V7 evaluation

`evaluation/v6-v7/`では、Human / AI ReadabilityとProgressive Explicitnessをstatic / synthetic harnessで評価します。

Run `33456710459`は**success**しています。

- rich / low-impact canonical source: 2件
- Projection profile: light / audit
- semantic question: 6件
- negative case: 7件

low-impactでは最大詳細を一律必須にせず、high-impactではaudit Projectionを要求します。

これは実利用者の理解時間、見落とし率、production UX、異なるAI実装間のOperational Evidenceではありません。

## 12. historical M47 digest

historical M47の`content_digest`規則はcurrent Profileとは分離して調査しました。

`ISSUE-000034`では、GitHub reachable history、branch、Actions、Libraryのsemantic / exact-name search、個別Go / Python inventory、archive時系列まで回収経路を広げました。

回収できたもの:

- M47 semantic Contract
- M47 Implementation Report
- M47 Release Closure
- historical KJ / cultural-substrate-weaving Method Definition payload

回収できなかったもの:

- actual M47 digest-producing Go source
- actual M47 conformance tool
- actual historical binding digest anchor
- M47 source / release archive

そのため、`ISSUE-000034`は「Profileを特定した」としてではなく、**現在保持された直接Evidenceから規則を回収できないことを確定し、historical bindingを`not_verified`として維持する**方針でResolvedとしました。

```text
ISSUE resolved
  != historical Profile verified

unrecoverable historical verification
  != failed binding
```

新たな一次資料が見つかった場合はIssueを再開できます。

## 13. SOZAとTEI

鼎（TEI）はSOZAそのものではなく、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

関連製品であることだけを理由にTEIへPriority / Trust / Authorityを付与しません。TEI固有のApplication、Database、Release、Deployment schemaをSOZA Universal Coreへ複製しません。

## 14. current Plan

current registryはADR-0001〜ADR-0024、ISSUE-000001〜ISSUE-000040を管理しています。

- ISSUE-000001〜000020: **Resolved**
- ISSUE-000021 — design history provenance逐語監査: **Deferred**
- ISSUE-000022〜000040: **Resolved**

`ISSUE-000021`は、指定7チャットの逐語export等が取得できる場合にhistorical provenanceを再監査するための留保です。current Product / Architecture / Runtimeの進行を止めるblockerではありません。

Plan integrity:

- historical M47 closure commit: `7aaa1280da01810c212b83de28b0741f5adccd2b`
- Run `33461793246`: **success**

## 15. 次に深める領域

current baselineでは、未完了Issue数を増やすこと自体を目的にしません。次の実装sliceはProduct Valueから必要性を戻って判断します。

優先候補:

1. Product Value → REQ → SCN → ADR → Architecture → Contract / Profile / RuntimeのEvidence整合を維持する。
2. production Provider / Storage integrationが必要になる具体的ユースケースとAcceptanceを定義する。
3. Release Evidenceの成立条件を設計する。
4. 実利用開始後にOperational / Adoption・Outcome Evidenceを別の高さで収集する。
5. historical design provenanceの逐語資料が得られた場合だけISSUE-000021を再開する。

実装量、Issue数、CI本数、coverage率をProduct ValueのKPIにはしません。

## 16. Releaseについて

`develop/v0.1.0`は開発中のbaselineです。**Release Evidence、Operational Evidence、Adoption / Outcome Evidenceを主張する状態ではありません。**

`main`へ統合する場合は、Product Value、Requirements、ADR、Architecture、Contract / Profile、actual Executable Evidenceを戻り照合し、実際に得られたEvidenceを超えない範囲で状態を更新します。

## 17. 文書品質

開発文書は、内容・構造・技術的一貫性を整えた後、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を通し、その後に意味監査を行います。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。

## 18. 自然な日本語レビュー

2026-09-01時点のProduct Value、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、4 Contract family、2 Representation Profile、first semantic runtime、Verifier Registry、synthetic Payload Source、synthetic Provider Adapter、V6/V7 evaluation、ISSUE-000001〜000040、actual CIへ戻って現在地を再確認しました。そのうえで、historical M47 recoveryのResolvedとhistorical ProfileのNot Verifiedを混同せず、Design / Executable / Release / Operational / Adoption・OutcomeのEvidence強度を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
