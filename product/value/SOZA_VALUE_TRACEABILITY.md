# SOZA Value Traceability

更新日: 2026-09-02  
状態: **Current Product Value Traceability Baseline — v0.2.0 Release Evidence / E3b-P2 fixed-artifact / E3b-M1b reflected**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Semantic Contract、Representation Profile、runtime、各種probe、Release Candidate Gate、actual Release Evidenceまで上位から追跡するための索引です。

この文書自体を新しい意味上の正本にはしません。詳細は次の文書を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Value Proposition: `SOZA_VALUE_PROPOSITION.md`
- Product Shape: `../definition/SOZA_PRODUCT_SHAPE.md`
- Product Milestone: `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- Evidence受入れ境界: `SOZA_VALUE_ACCEPTANCE.md`
- Requirement: `../../requirements/PRODUCT_REQUIREMENTS.md`
- Acceptance Scenario: `../../requirements/ACCEPTANCE_SCENARIOS.md`
- Product Journey composition: `../../requirements/PRODUCT_JOURNEY_COMPOSITION.md`
- Architecture: `../../architecture/SOZA_REFERENCE_ARCHITECTURE.md`, `../../architecture/TRACEABILITY.md`
- Contract: `../../contracts/TRACEABILITY.md`, `../../contracts/CONTRACT_CATALOG.md`
- Representation Profile: `../../contracts/profiles/`
- runtime / probe Evidence: `../../runtime/`
- V6 / V7 evaluation: `../../evaluation/v6-v7/`
- release acceptance / evidence: `../../release/v0.2.0/`
- ADR / Issue: `../../plan/`

追跡表が埋まっていること自体をProduct Valueの達成とはみなしません。

## 2. 追跡の基本形

```text
Product Value / Value Proposition / Product Shape
  → Product Milestone
  → V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Issue
  → Architecture concern
  → Semantic Contract / Representation Profile
  → Runtime / Adapter / Payload Source / Projection / Probe / Journey harness
  → Fixture / Test / CI
  → Release Candidate Gate
  → actual Release Evidence
  → Operational / Adoption・Outcome Evidence
```

関係は多対多です。リンク数やcoverage率をProduct ValueのKPIにはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | current executable / release material |
|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016, 0018 | Semantic Reference / Decision Memory / Interchange、Exact Binding、Cognitive Method、historical basis非改変、known Contract横断bundle-local consistency、外部Method実行sourceのProvenance保持 |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016, 0018 | Recommendation / Decision / Authority分離、Unknown / Withheld、Cognitive Method分離、Responsibility分離、unknown Contract非推測解析、actual model-backed KJ grouping候補の非自動昇格 |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016, 0018 | lineage / Exact Binding invariant、Representation Profile、Cognitive Method exact refs、複数exact revision保持、historical basis非改変 |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014, 0018 | Capability Observation、Provider replacement journey、out-of-process exchange、E3a external artifact、E3b-P1 public live Provider、E3b-P2 fixed-artifact actual TEI、E3b-M1a / M1b live external Method |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016, 0018 | Unknown / Conflict / Withheld / partial knowledge、missing→unknown、Decision residual→reopen path、opaque `not_verified` external Method output |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | human-readable Contract、machine-readable schema、light / audit Projection、first Product Interaction reference probe |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | low-impact / high-impact Projection evaluation、canonical operationとInteractionの分離 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015, 0018 | provider-neutral Contract、Cognitive Method、Payload Source、local package、out-of-process exchange、E3b-P2 actual TEI process、E3b-M1a / M1b external Method process・actual inference |

表中のmaterialが存在しても、そのValue Axis全体がOperational / OutcomeまでSatisfiedになったとは読みません。

## 4. Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0018`です。

```text
Requirement != Acceptance Scenario != Test Case
```

SCN-0018は個別Scenarioを置き換えません。InquiryからDecision、外部実行、実行後Observation、historical review / reopenまでを代表的なProduct Journeyとして接続し、複数の意味境界が同時に失われないことを検査します。

E3b-M1a / M1bでは新しいStable Requirement / Scenarioを追加していません。KJ Atlas、FastAPI、HTTP、SQLite、Ollama、特定model tag等の実装方式だけを理由にUniversalな要求を増やさず、既存のCognitive Method交換可能性、historical reconstruction、Realization / Execution交換の要求へ戻して評価します。

M1bのactual model接続でも、それらで表せない独立したProduct failureは確認されませんでした。model / runtime交換時のProvenance不足など、新しい意味上の欠落が実証で確認された場合にだけCandidate Requirementとして再検討します。

## 5. Contract / Representation baseline

current Semantic Contractは5 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Representation ProfileはSemantic Contractと別のversion空間を持ちます。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

```text
Semantic Contract
  != Representation Profile
  != verifier implementation
```

KJ Atlasのresponse shapeやOllama固有のinference fieldも、新しいUniversal Cognitive Method Contractではありません。M1a / M1bでは外部Method outputやintegration Evidenceとして扱います。

## 6. Exact Bindingとhistorical reconstruction

ADR-0026 / ISSUE-000049により、current runtimeが理解するknown typed ContractのReference roleについて、bundle-local Exact Binding consistencyを共通に検査します。

同じlogical identityに複数revisionが存在してもlatest-winsで一つへ潰さず、Referenceが指すexact revisionを候補の一つとして検査できます。

一方、bundle内に該当recordが存在しないことだけを理由にFAILとはしません。

```text
bundle-local consistency
  != external payload acquisition
  != digest verification
  != Verification Outcome
```

M1a / M1bではKJ Atlas source repository / commit / entry point / result digest等をProvenanceとして保持し、M1bのintegration Evidenceではinference runtime、model tag / observed ID、prompt digest、inference countersも区別しています。ただし、それらをMethod Definitionのsemantic identityへ置き換えたり、今回だけを根拠にUniversal Provenance fieldへ固定したりしません。

今後のmodel / runtime version交換実証で、historical Method Applicationを再構成するために不足する情報があるかを検査します。

## 7. semantic runtime / Provider / Storage / Method

semantic runtimeはread / validate / reconstructを中核にし、SOZA自身をworkflow / agent execution engineへしません。

current scoped materialには次があります。

- known Contract typed runtime
- Representation Verifier Registry
- synthetic Payload Source / Provider Adapter
- Cognitive Method typed runtime
- known Contract横断bundle-local Exact Binding consistency
- out-of-process Realization / Provider exchange
- packaged resume / Persistence exchange probe
- Product Interaction / Access probe
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- external TEI executable injection boundary
- E3b-P2 fixed-artifact actual TEI CLI integration
- E3b-M1a live KJ Atlas + deterministic model stub integration
- E3b-M1b live KJ Atlas + actual inference model integration

これらのPASSはproduction Provider / Storage / external executionの運用成立、あるいはmodel出力品質を意味しません。

## 8. Product Interaction / Access / Packaging

current Product baselineでは、次の境界とreference probeが成立しています。

- human-oriented / machine-oriented Surfaceから同じcanonical meaningへ戻るProduct Interaction
- Local Single-Node Packaging
- deterministic Linux / amd64 Local Reference Package
- process restart後のresume / Persistence exchange probe
- authentication identityとBounded Subjectの分離
- Product access permissionとsemantic Responsibility / Authorityの分離
- Selective Disclosureにおける`withheld`保持

```text
reference probe PASS
  != production UX validated
  != production authorization validated
  != operational deployment validated
```

## 9. Realization / Provider exchangeの現在地

PMS-06ではEvidenceを次のように分けています。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 Operational portability
```

E3bは、現在次の範囲へ分けています。

- E3b-P1: public live Provider service — **Scoped Executable Evidence available**
- E3b-P2: actual TEI process / service — **fixed-artifact Scoped Executable Evidence available**
- external TEI executable injection boundary — **Scoped Executable Evidence with helper subprocess**
- E3b-M1a: live KJ Atlas process + deterministic model stub — **Scoped Executable Evidence available**
- E3b-M1b: live external model-backed KJ execution — **Scoped Executable Evidence available**

ISSUE-000064のM1aでは、固定revisionのKJ Atlas FastAPI backendとrepository同梱model stubをSOZAとは別processとして実行し、actual grouping responseを既存Cognitive Method Applicationへ戻しました。

ISSUE-000066のM1bでは、同じKJ Atlas revisionとMethod surfaceを保ったまま、model processを実際に推論するartifactへ置き換えました。先行Run `33596839607`ではactual model取得、actual inference、KJ Atlasによるresponse受理、既存SOZA Method mappingまでをskipなしで確認しています。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision

E3b-M1b execution PASS
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

v0.2.0でsupportを主張するrelease scopeはE3aまでです。後続のE3b-P1 / P2 / M1a / M1b Evidenceが存在しても、v0.2.0 scopeを遡及的に拡張しません。

## 10. V6 / V7 Projection evaluation

light / audit Projectionを同じcanonical sourceから生成し、semantic question setとnegative caseで意味境界を検査しています。

これはstatic / synthetic evaluation-harness scoped Executable Evidenceです。実利用者の理解可能性、入力負担、見落とし率、production UXのOperational / Adoption Evidenceではありません。

## 11. end-to-end Semantic Product Journey

`runtime/go/journeyharness`はSCN-0018をsynthetic semantic Product Journeyとして検査します。

主な確認範囲は次です。

- normal / uncertain / collaborative / provider replacement / no-execution
- RecommendationとDecisionの分離
- Responsibility分離
- execution後Observationの時間境界
- historical Decision statement / basisの非改変
- unresolved → reopen
- unsupported recordのopaque + `not_verified`
- Projectionがcanonical Decisionを代替しないこと

```text
fixture-scoped Product Journey PASS
  != production Product Journey validated
  != human interaction validated
```

## 12. v0.2.0 Release Evidence

v0.2.0はLocal Reference Product Baselineとしてactual release済みです。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- GitHub Release ID: `380902898`
- Release Candidate Gate Run: `33574947445` — **9 gate success**
- release preparation: **success**
- publication: **success**

Local Reference Packageについて、release preparationで算出したSHA-256とactual GitHub Release assetのdigestが一致しています。

```text
37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17
```

したがって、**v0.2.0 Local Reference Product BaselineについてRelease EvidenceはSatisfied**です。

```text
Release Evidence Satisfied
  != E3b included in v0.2.0 supported scope
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

詳細は`../../release/v0.2.0/RELEASE_EVIDENCE.md`を正とします。

## 13. Evidenceの現在地

### Design Evidence

Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、current ADR群、Reference Architecture、5 Contract family、2 Representation Profile、Interaction / Access / Packaging / Provider exchange boundary等があります。

### Executable Evidence — scoped

Plan / Requirements / Contract conformance、semantic runtime、Representation Profile / Verifier Registry、Payload Source / Provider Adapter、Cognitive Method、V6 / V7 evaluation、Product Journey、Interaction / Packaging / Persistence / Access / Realization exchange、E3a、E3b-P1、E3b-P2 fixed-artifact、E3b-M1a、E3b-M1b等の限定Evidenceがあります。

### Release Evidence

**Satisfied for v0.2.0 Local Reference Product Baseline.**

supported scopeはE3aまでです。E3b-P1 / P2 / M1a / M1b等の後続Evidenceをv0.2.0 release scopeへ自動的に取り込みません。

### Operational Evidence

**Not Yet Verified.**

### Adoption / Outcome Evidence

**Not Yet Verified.**

## 14. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

bundle-local Exact Binding整合、historical basis非改変、Payload Source / Verifier境界はscopedに検査済みです。production Storageや長期間のProvider / representation / model変更をまたぐhistorical reconstruction、実際の再判断への寄与は未検証です。

### V2 Semantic Separation

主要な意味分離はfixture / runtimeで検査しています。M1a / M1bでもMethod outputをRecommendation / Decisionへ自動昇格させない境界を確認しています。production責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

同一logical identityの複数Exact Bindingを保持し、参照先revisionをlatest-winsで潰さない境界を検査しています。cross-bundleの実payload検証や長期Storage revisionは未検証です。

### V4 Provider Independence

synthetic Adapter、Provider replacement journey、out-of-process exchange、E3a、E3b-P1、fixed-artifact actual TEI、M1a、M1bまでscopedに検査しています。任意TEI / model / runtime versionへの交換、実Providerの廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / residual / reopenの境界はscopedに検査済みです。M1a / M1bの外部Method outputも`not_verified`として保持します。実際の誤判断回避や再検討品質へのOutcome Evidenceはありません。

### V6 Human / AI Readability

ProjectionとInteraction reference probeはありますが、実利用者や異なるAI実装による理解度Evidenceはありません。

### V7 Progressive Explicitness

low-impact / high-impactのsynthetic evaluationはあります。実運用でのimpact判定、入力負担、見落とし率は未検証です。

### V8 Execution Independence

Provider / Persistence / Realization交換、fixed-artifact actual TEI、M1a external Method process、M1b actual model-backed executionまでscopedなExecutable Evidenceは増えました。ただし、任意version交換やproduction環境で長期的に意味を維持したOperational Evidenceはありません。

## 15. current Planとの関係

current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000066を管理します。

主要状態は次です。

- ISSUE-000021: **Deferred** — historical design provenance逐語監査
- ISSUE-000063: **Resolved** — v0.2.0 actual Release Evidence
- ISSUE-000064: **Resolved** — E3b-M1a live KJ Atlas Cognitive Method execution
- ISSUE-000065: **Resolved** — E3b-P2 fixed-artifact actual TEI CLI execution
- ISSUE-000066: **Open** — E3b-M1b actual model-backed executionのEvidence・文書同期とmerge後回帰を進行中
- その他のcurrent Issue: repository registryに従う

IssueがResolvedであることは、その対象についてOperational / Adoption・Outcome EvidenceまでVerifiedであることを意味しません。

## 16. CoverageをKPIにしない

Requirement数、Scenario数、fixture数、Issue数、CI本数、release asset数をProduct ValueのKPIにはしません。

これらは追跡可能性や検査可能性を支える手段です。Product Valueの評価は、各Value AxisとEvidenceの高さへ戻って行います。

## 17. 次に必要なEvidence

v0.2.0 release後に深める主要な領域は次です。

- E3b-P2で残るprivate-repository credential運用とTEI version交換
- model / runtime version交換をまたぐM1b Provenance / Exact Binding
- model出力品質・KJ法としての成果品質をsemantic executionから分離して評価するEvidence
- E4 Operational portability
- production Provider / Storage / identity / securityが必要となる具体的な利用文脈
- 次releaseでE3bをsupported scopeへ含める条件
- Operational Evidence
- Adoption / Outcome Evidence

これらはv0.2.0 Release EvidenceやP2 / M1a / M1bの成立を理由に自動的にSatisfiedへ上げません。

## 18. Natural Japanese review

Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、5 Semantic Contract family、2 Representation Profile、current runtime / probe、E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1a / E3b-M1b、v0.2.0 Release Acceptance / Release Evidence、ISSUE-000063〜000066へ戻って全体を再監査しました。

v0.2.0 Release Evidenceの成立範囲をLocal Reference Product Baselineへ限定したまま、release後に得られたE3b-P2 fixed-artifact actual TEI execution、M1a、M1bをScoped Executable Evidenceとして追跡しています。M1bではactual model inferenceが成立したことと、model出力品質やKJ法としての成果品質が十分であることを分けました。また、private-repository credential運用、任意TEI / model / runtime version互換性、E4、production readiness、Operational Evidence、Adoption / Outcome Evidenceは未検証のままです。

意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。