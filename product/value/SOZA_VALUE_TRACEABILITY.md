# SOZA Value Traceability

更新日: 2026-09-01  
状態: **Current Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Semantic Contract、Representation Profile、runtime、Provider Adapter、Payload Source、Projection Evaluation、end-to-end Product Journey harness、Release Candidate Gate、現在のEvidence状態まで上位から追跡するための索引です。

新しい意味上の正本は作りません。詳細は次を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Value Proposition: `SOZA_VALUE_PROPOSITION.md`
- Product Shape: `../definition/SOZA_PRODUCT_SHAPE.md`
- Evidence受入れ境界: `SOZA_VALUE_ACCEPTANCE.md`
- Requirement: `../../requirements/PRODUCT_REQUIREMENTS.md`
- Acceptance Scenario: `../../requirements/ACCEPTANCE_SCENARIOS.md`
- Product Journey composition: `../../requirements/PRODUCT_JOURNEY_COMPOSITION.md`
- Architecture: `../../architecture/SOZA_REFERENCE_ARCHITECTURE.md`, `../../architecture/TRACEABILITY.md`
- Contract: `../../contracts/TRACEABILITY.md`, `../../contracts/CONTRACT_CATALOG.md`
- Representation Profile: `../../contracts/profiles/`
- runtime: `../../runtime/go/`
- Product Journey harness: `../../runtime/go/journeyharness/`
- V6 / V7 evaluation: `../../evaluation/v6-v7/`
- release acceptance: `../../release/v0.1.0/RELEASE_ACCEPTANCE.md`
- ADR / Issue: `../../plan/`

この追跡表が埋まっていること自体をProduct Valueの達成とはみなしません。

## 2. 追跡の基本形

```text
Product Value / Value Proposition / Product Shape
  → V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Issue
  → Architecture concern
  → Semantic Contract / Representation Profile
  → Runtime / Provider Adapter / Payload Source / Projection / Journey harness
  → Fixture / Test / CI / Release Candidate Gate
  → Evidence state
```

関係は多対多です。リンク数やcoverage率をProduct ValueのKPIにはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | 主なADR | current executable material |
|---|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016, **0018** | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0019, 0021, 0022, 0023, 0024, 0025 | Semantic Reference / Decision Memory / Interchange fixture、F6 historical reconstruction、Cognitive Method、Go runtime、Verifier Registry、synthetic Payload Source、Adapter mapping provenance、Product Journey temporal-integrity / historical-basis tests |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016, **0018** | ADR-0002, 0004, 0010, 0011, 0012, 0016, 0017, 0019, 0022, 0024, 0025 | Recommendation-only、Decision with unresolved、Authority field rejection、Cognitive Method / Recommendation / Decision分離、Journey harnessのResponsibility分離・semantic promotion negative cases |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016, **0018** | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0017, 0021, 0023, 0024, 0025, 0026 | lineage / exact binding invariant、Profile fixture、runtime verification、Cognitive Method exact metadata、取得不能≠digest mismatch、mapping provenance、post-execution Observationのhistorical basis非混入 |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014, **0018** | ADR-0006, 0012, 0013, 0014, 0019, 0021, 0022, 0024 | Capability Observation F1〜F7、cross-provider fixture、synthetic Provider A/B Adapter、Journey harnessの同一Capability / 異Provider検査 |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016, **0018** | ADR-0002, 0005, 0006, 0010, 0011, 0019, 0022, 0024 | Unknown / Conflict / Withheld / partial knowledge、Adapter missing→unknown、Decision unresolved → reopen Method Applicationのsynthetic path |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | ADR-0005, 0017, 0018, 0020, 0021 | human-readable Contract / machine-readable schema、light/audit Projection、semantic questions / negative cases、Journey harnessでProjectionをcanonical Decisionの代替にしない検査 |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | ADR-0005, 0019 | low-impact minimal Decisionとhigh-impact rich Decisionを同一evaluation harnessで評価 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015, **0018** | ADR-0006, 0007, 0012, 0013, 0014, 0017, 0019, 0022, 0024, 0025 | Provider-neutral Contract、Cognitive Method portable Contract、execution非依存runtime、Adapter-local provider schema、Storage-neutral Payload Source、no-execution Product Journey |

表中のmaterialが存在しても、そのValue Axis全体のExecutable AcceptanceがSatisfiedになったとは読みません。

## 4. Requirement / Scenario / Product Journey baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0018`です。

```text
Requirement != Acceptance Scenario != Test Case
```

SCN-0018は、既存Scenarioを置き換えるものではありません。次を代表的な一つのProduct Journeyとして接続し、個別の意味境界が同時に壊れないことを検査します。

```text
Inquiry
  → Observation / Evidence / Unknown / Conflict
  → Cognitive Method Application
  → Recommendation
  → Decision / Responsibility
  → external Capability / Execution
  → resulting Observation
  → historical review / reopen
```

`requirements/PRODUCT_JOURNEY_COMPOSITION.md`の分析では、現時点でこのJourneyのためだけに新しいUniversal Requirementを追加する必要はないと整理しています。

Requirements Registry Conformanceのcurrent SCN-0018 Evidence反映後Run `33478396211`は**success**しています。これはRequirements RegistryとScenario正本の構造整合に対するExecutable Evidenceであり、Requirement内容のproduction実現を証明しません。

## 5. Architecture / Contract baseline

current Reference Architectureは実装package順ではなく、意味上のarchitecture concernで構成します。

current Semantic Contractは次の5 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Cognitive Methodは、Method Definition / Realization / ApplicationをPromptや実行engineから分離してportableに保持するContractです。Method Applicationの存在をRecommendation、Decision、Authority、Execution、Assuranceへ自動昇格させません。

current v1alpha1 fixture baselineは31件です。

```text
Capability Observation F1〜F7 = 7
Cognitive Method C1〜C8 = 8
Boundary / expected PASS or NOT_VERIFIED = 7
Negative schema / semantic FAIL = 9
Total = 31
```

代表的なcurrent Contract Conformance Run `33467838961`は**success**、同じHEADのSemantic Runtime Conformance Run `33467838941`も**success**しています。

2026-08-31の17-fixture runはhistorical Executable Evidenceとして残しますが、current 31-fixture baselineの代わりにはしません。

## 6. Representation Profile baseline

current/future Exact Binding向けProfile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Profile Conformance:

- Run `33347989530`: **success**

Runtime Verifier Registry:

- Run `33452115728`: **success**

```text
Semantic Contract != Representation Profile != verifier implementation
```

### historical M47 digest

historical M47 digest mappingはcurrent Profileとは別問題としてISSUE-000034で回収しました。

GitHub reachable history、branch、Actions、Library semantic / exact-name search、個別Go / Python inventory、archive時系列まで確認しましたが、actual digest-producing source、actual M47 conformance tool、actual historical digest anchor、M47 source archiveは回収できませんでした。

そのためISSUE-000034は、**現在保持された直接Evidenceからdigest ruleを回収不能であることを確定し、historical bindingを`not_verified`として保持する**方針でResolvedとしています。

```text
ISSUE-000034 Resolved
  != historical M47 Profile verified

current Profile verified
  != historical digest identified
```

新たな一次資料が得られた場合は再開できます。

## 7. semantic runtime / Verifier / Payload Source

semantic runtimeはread / validate / reconstructを中核にし、SOZA自身をworkflow / agent execution engineへしません。

代表的なcurrent Evidence:

- first semantic runtime: Run `33348972805` — **success**
- Verifier Registry: Run `33452115728` — **success**
- Payload acquisition boundary: Run `33457416359` — **success**
- Cognitive Methodを含む31-fixture runtime baseline: Run `33467838941` — **success**

Payload SourceはStorage固有mechanicsをCoreへ持ち込まず、取得不能・source error・local size limitをdigest mismatchと区別します。

```text
payload unavailable / operational acquisition failure
  → not_verified

payload available + digest mismatch
  → failed
```

synthetic Payload SourceのPASSをproduction S3 / MinIO / filesystem / HTTP integrationへ拡張しません。

## 8. synthetic Provider Adapter

ADR-0024 / ISSUE-000036に基づき、異なるProvider-specific input shapeを各Adapterが解釈し、Capability Observationへ収束させます。

- first Adapter slice: Run `33349604842` — **success**
- Provider-specific field非漏洩hardening: Run `33349801993` — **success**

AdapterはRecommendation / Decision / Authority / Executionを生成しません。

## 9. V6 / V7 Projection evaluation

代表Run `33456710459`は**success**しています。

- canonical source: rich / low-impact 2件
- Projection: light / audit
- semantic question: 6件
- negative case: 7件

SCN-0018 Evidence更新後もV6/V7 Projection Evaluation Run `33478396138`は**success**しています。

これはstatic / synthetic evaluation-harness scoped Executable Evidenceです。実利用者の理解可能性、入力負担、見落とし率、production UXのOperational / Adoption Evidenceではありません。

## 10. end-to-end Semantic Product Journey harness

`runtime/go/journeyharness`は、SCN-0018を一つのsynthetic semantic Product Journeyとして検査します。

Journey manifestは評価用の検査構成であり、新しいUniversal Contractやcanonical product stateではありません。耐久的な意味は既存Contract record側に残します。

現在のfixture-scoped検査範囲:

- normal path
- uncertain path / unresolved → reopen
- collaborative path / Responsibility分離
- provider replacement path / same Capability, different Provider
- no-execution path
- RecommendationとDecisionの分離
- execution後Observationの時間境界
- post-execution Observationのhistorical Decision basisへの混入拒否
- execution success後もhistorical Decision statement / basisを非改変
- unsupported / external recordのopaque + `not_verified`保持
- Semantic Interchange loader経由のnormal journey
- Interchange original bytesのread時非改変
- Projectionがcanonical Decisionを代替しないこと

主なCI:

- Run `33477245347` — first in-memory harness: **success**
- Run `33477970035` — Semantic Interchange normal journey: **success**
- Run `33478127484` — Projection非権威を含むcurrent journey harness: **success**
- SCN-0018正本Evidence更新後のSemantic Runtime Conformance Run `33478396131`: **success**
- 同じ正本更新に対するPlan integrity Run `33478396165`: **success**
- Requirements Registry Run `33478396211`: **success**

SCN-0018のExecutable Evidenceはこの範囲で**Partially Satisfied**です。

```text
fixture-scoped Product Journey PASS
  != production Product Journey validated
  != human interaction validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 11. Evidenceの現在地

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Design Evidence

Product Value、Value Proposition、Product Shape、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0026、Reference Architecture、5 Semantic Contract family、2 Representation Profile、runtime / Adapter / Payload Source boundary、V6/V7 evaluation protocol、Product Journey composition / harness design、v0.1.0 release acceptanceがあります。

### Executable Evidence — scoped

- Plan registry integrity
- Requirements registry structural conformance
- current 31-fixture Contract conformance
- Representation Profile fixture / probe
- semantic runtime
- current 2 ProfileのVerifier Registry
- synthetic Payload Source
- synthetic Provider Adapter
- Cognitive Method typed runtime
- V6 / V7 Projection evaluation harness
- end-to-end Semantic Product Journey harness
- v0.1.0 Release Candidate Gate

### Release Candidate Evidence — Executable Evidence内のrelease準備分類

Release Candidate EvidenceはProduct Valueの第6段階ではありません。特定のsource commitについて主要Executable gateを同一checkoutで再検査したことを表す、Executable Evidence内のrelease準備上の分類です。

v0.1.0で記録済みの候補:

- source commit: `9313d527068ad587e03212f17e217dcac562109d`
- source tree: `b12b350a5a2d3fb3a6732accea229af5b9eeb257`
- Release Candidate Gate Run `33465412382`: **success**
- Plan integrity Run `33465412473`: **success**
- candidate report artifact ID: `9784659353`
- artifact digest: `sha256:cd97af7c03f59967b946e7e94b74b88e4378ace0575c9f78e433f51170e5e566`

統合gate内ではPlan、Requirements、Contract、Representation Profile、commit-pinned JCS probe、semantic runtime、V6/V7 Projection、release candidate policy / reportがsuccessしています。

```text
Release Candidate Gate success
  != source release exists
  != Release Evidence satisfied
```

v0.2.0のcurrent development Evidenceを、過去のv0.1.0 Release Candidate Evidenceへ遡及的に混入させません。

### Release Evidence

**Not Yet Verified**

actual release identityと、そのrelease対象source / artifact / gateを結ぶEvidence recordは、current Product Value上のRelease Evidenceとしてまだ確認していません。

### Operational Evidence

**Not Yet Verified**

### Adoption / Outcome Evidence

**Not Yet Verified**

## 12. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

current Contract / Profile / runtime / Cognitive Method / Journey harnessの限定境界は検査済みです。Journey harnessではexecution後Observationを過去Decision basisへ時間逆行させず、historical Decision statement / basisを非改変のまま保持するsynthetic pathを確認しました。historical M47 digest ruleは回収不能として`not_verified`を維持しています。production Storage、実Provider変更、長期運用をまたぐhistorical reconstructionと再判断への寄与は未検証です。

### V2 Semantic Separation

Recommendation / Decision / Authority等の分離、Cognitive Method / Recommendation / Decisionの分離、Adapterが後続意味へ自動昇格しないこと、collaborative pathでのResponsibility分離を一部検査済みです。production責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

lineage / exact binding invariant、Cognitive Method exact metadata、mapping provenance、取得不能をdigest mismatchへ変換しない境界、post-execution Observationのhistorical basis非混入を検査済みです。ISSUE-000049のknown Contract横断bundle-local Exact Binding一般化はOpenであり、production Storage revisionや長期間のmapping changeをまたぐEvidenceもありません。

### V4 Provider Independence

cross-provider fixture、synthetic A/B Adapter、Journey harnessで同じCapabilityを別Providerへ接続するsemantic boundaryを検査済みです。実Providerの交換・廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / partial knowledge、Adapter missing→unknown、Decision unresolvedからreopen Method Applicationへのsynthetic引継ぎを検査済みです。実際のInquiry lifecycleや誤判断回避へ寄与したOutcome Evidenceはありません。

### V6 Human / AI Readability

semantic question一致とlight/audit Projectionをstatic harnessで確認し、Journey harnessではProjectionだけからcanonical Decisionを補完しないことも確認しました。実利用者・異なるAI実装によるOperational / Adoption Evidenceはありません。

### V7 Progressive Explicitness

low-impactでは軽量、high-impactではauditを要求するharnessを検査しました。実運用でのimpact判定、入力負担、見落とし率は未検証です。

### V8 Execution Independence

semantic runtime、Cognitive Method、Provider Adapter、Payload Sourceをexecution / provider / storage mechanicsから分離し、no-execution Product Journeyも成立することをfixtureで確認しました。異なるproduction Execution / Storage Provider間で意味を維持したEvidenceはありません。

## 13. current Planとの関係

current registryはADR-0001〜0026、ISSUE-000001〜000050を管理します。

主要なcurrent状態:

- ISSUE-000001〜000020: Resolved
- ISSUE-000021: Deferred — design history provenance逐語監査
- ISSUE-000022〜000044: Resolved — ISSUE-000043 Cognitive Method first sliceとISSUE-000044 Product Value Proposition / Product Shapeを含む
- ISSUE-000045: Open — first usable Product Interaction boundary
- ISSUE-000046: Open — v0.2.0 Product Packaging / Deployment boundary
- ISSUE-000047: Open — Product Identity / Authorization / Collaboration boundary
- ISSUE-000048: Resolved — SCN-0018 end-to-end Acceptance Design
- ISSUE-000049: Open — known Contract横断bundle-local Exact Binding consistency
- ISSUE-000050: Resolved — end-to-end Semantic Product Journey harness / Evidence同期

Cognitive Method正本Evidence同期後のPlan integrity Run `33497887115`は**success**しています。これに先立ち、SCN-0018正本Evidence更新後Run `33478396165`も**success**しています。

ISSUE-000021はhistorical chat export等が利用できる場合の再監査留保であり、current Product / Runtimeのblockerではありません。

## 14. CoverageをKPIにしない

次の読み方をしません。

- REQリンクが多いValue Axisほど重要である。
- Contractやfixtureが多いほどProduct Valueが高い。
- CIが多く通るほど利用者価値が高い。
- Executable Evidenceが増えればRelease / Operational / Outcomeも自動的に増える。
- IssueがResolvedなら、その対象がすべてVerifiedである。
- Product Journey fixtureが通ればproduct usabilityやbusiness outcomeが証明されたことになる。
- Release Candidate Gateが通ればactual release済みである。

追跡の目的は、**どこまで確認したかと、どこから先をまだ主張してはいけないかを見失わないこと**です。

## 15. 更新規則

Product Value、Value Proposition、Product Shape、REQ、SCN、ADR、Architecture、Contract、Profile、runtime、Provider Adapter、Payload Source、Projection Evaluation、Product Journey harness、release candidate、Evidence stateのいずれかが変わった場合、この文書を必要に応じて更新します。

下位実装の都合に合わせてProduct Valueを後付けで変更しません。上位仮説を変える必要がある場合はADR-0018の再基線化規則に従います。

## 16. Natural Japanese review

V1〜V8、Value Proposition、Product Shape、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0026、current Architecture、5 Semantic Contract family、31-fixture baseline、2 Representation Profile、semantic runtime、Cognitive Method、Verifier Registry、synthetic Payload Source、synthetic Provider Adapter、V6/V7 Projection evaluation、end-to-end Semantic Product Journey harness、ISSUE-000034 recovery closure、v0.1.0 Release Candidate Evidenceへ戻って追跡を再確認しました。Cognitive MethodについてはC1〜C8、negative / unknown-version fixture、typed runtimeで実際に確認したportable semantic boundaryだけをSCN-0005 / SCN-0015の`Partially Satisfied`へ反映し、Method executorやproduction Realization交換へは昇格させていません。SCN-0018についてもRun `33478127484`および正本更新後Run `33478396131`で実際に確認したfixture-scoped範囲だけExecutable Evidenceへ反映し、component-level PASSやsynthetic Product Journey PASSをproduction Product Acceptance、Release、Operational、Adoption / Outcomeへ昇格させていません。その後、Issue closureとVerification、Design / Executable / Release / Operational / Adoption・OutcomeのEvidence強度を混同せず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。