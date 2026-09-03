# SOZA Value Traceability

更新日: 2026-09-03  
状態: **Current Product Value Traceability Baseline — v0.2.0 Release Evidence / E3b / historical reconstruction / model exchange reflected, runtime exchange pending**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Semantic Contract、Representation Profile、runtime、各種probe、Release Candidate、actual Release Evidenceまで上位から追跡するための索引です。

この文書自体を新しい意味上の正本にはしません。詳細は次の文書を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Value Proposition: `SOZA_VALUE_PROPOSITION.md`
- Product Shape: `../definition/SOZA_PRODUCT_SHAPE.md`
- Realization / Provider Exchange: `../definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`
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
- Cognitive Method outcome-quality evaluation: `../../evaluation/method-quality/`
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
  → Fixture / Test / repository checker / external execution
  → Release Candidate evaluation
  → actual Release Evidence
  → Operational / Adoption・Outcome Evidence
```

関係は多対多です。リンク数やcoverage率をProduct ValueのKPIにはしません。

実行基盤も意味上の正本ではありません。current baselineではGitHub Actionsを常設していません。過去のActions Runは、その時点で実際に得られたEvidenceとして保持しますが、現在の検証成立条件にはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | current executable / release material |
|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016, 0018 | Semantic Reference / Decision Memory / Interchange、Exact Binding、Cognitive Method、historical basis非改変、bundle-local consistency、ISSUE-000067 historical reconstruction、ISSUE-000068 model artifact exchange後の先行Application保持 |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016, 0018 | Recommendation / Decision / Authority分離、Unknown / Withheld、Cognitive Method分離、Responsibility分離、unknown Contract非推測解析、actual model-backed KJ grouping候補の非自動昇格、execution conformanceとoutcome qualityの分離 |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016, 0018 | lineage / Exact Binding invariant、Representation Profile、Cognitive Method exact refs、複数exact revision保持、same logical Realization / different historical revisionの区別、historical basis非改変 |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014, 0018 | Capability Observation、Provider replacement journey、out-of-process exchange、E3a external artifact、E3b-P1 public live Provider、E3b-P2 fixed-artifact actual TEI、E3b-M1a / M1b live external Method |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016, 0018 | Unknown / Conflict / Withheld / partial knowledge、missing→unknown、Decision residual→reopen path、opaque `not_verified` external Method output、outcome quality未評価の明示 |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | human-readable Contract、machine-readable schema、light / audit Projection、first Product Interaction reference probe、human outcome review template |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | low-impact / high-impact Projection evaluation、canonical operationとInteractionの分離、構造検査と人間評価の責務分離 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015, 0018 | provider-neutral Contract、Cognitive Method、Payload Source、local package、out-of-process exchange、E3b-P2 actual TEI process、E3b-M1a / M1b external Method process、model artifact exchange、repository-local runtime exchange harness |

表中のmaterialが存在しても、そのValue Axis全体がOperational / OutcomeまでSatisfiedになったとは読みません。

## 4. Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0018`です。

```text
Requirement != Acceptance Scenario != Test Case
```

SCN-0018は個別Scenarioを置き換えません。InquiryからDecision、外部実行、実行後Observation、historical review / reopenまでを代表的なProduct Journeyとして接続し、複数の意味境界が同時に失われないことを検査します。

E3b-M1a / M1b、ISSUE-000067のhistorical reconstruction、ISSUE-000068のactual model artifact exchangeでは、新しいStable Requirement / Scenarioを追加していません。KJ Atlas、FastAPI、HTTP、SQLite、Ollama、特定model tag等の実装方式だけを理由にUniversalな要求を増やさず、既存のCognitive Method交換可能性、historical reconstruction、Realization / Execution交換の要求へ戻して評価します。

ISSUE-000070のruntime version交換も同じです。actual A / B実証の結果として、現在のProvenance / Exact Bindingでは過去Applicationを十分に再構成できないなど、既存Requirementでは表せない独立したProduct failureが確認された場合にだけCandidate Requirementとして再検討します。

ISSUE-000071で成果品質の評価境界を確立したこと自体も、新しいStable Requirementの成立を意味しません。

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

runtime version、runtime archive digest、model artifact digest等もMethod Definitionのsemantic identityではありません。同じlogical Realizationのhistorical revisionを再構成する必要がある場合は、ProvenanceとExact Bindingで区別します。

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

ISSUE-000067では、異なる実現機構と同じ実現機構のhistorical revisionを区別しました。

```text
different realization mechanism
  → different logical Realization

same realization mechanism / different revision
  → same logical Realization
  + different Exact Binding
```

ISSUE-000068では、KJ Atlas source、runtime、Method inputを固定し、actual model artifactだけを交換しました。後続Applicationを追加しても、先行ApplicationのRealization、Provenance、outputを保持できることをScoped Executable Evidenceとして確認しています。

ISSUE-000070ではmodel artifactを固定し、Ollama `0.32.13` / `0.32.14`だけを交換する実証を進めています。repository-local harness、artifact guard、Exact Binding controls、Evidence保存、preflightは実装済みですが、current harnessによるactual A / B交換は**Not Yet Verified**です。

```text
preflight ready
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

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
- historical Method reconstruction controls
- actual model artifact exchange Evidence
- repository-local runtime version exchange harness / guards / preflight
- Cognitive Method structural / outcome-quality evaluation boundary

これらのPASSはproduction Provider / Storage / external executionの運用成立、あるいはmodel出力・KJ法としての成果品質を意味しません。

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

ISSUE-000066のM1bでは、同じKJ Atlas revisionとMethod surfaceを保ったまま、model processを実際に推論するartifactへ置き換えました。historical Run `33596839607`ではactual model取得、actual inference、KJ Atlasによるresponse受理、既存SOZA Method mappingまでをskipなしで確認しています。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision

E3b-M1b execution PASS
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

M1b後には、次の横断Evidenceを追加しています。

- ISSUE-000067 — Definition / logical Realization / historical revision / Applicationの再構成境界
- ISSUE-000068 — actual model artifact交換後も先行Applicationを保持するScoped Executable Evidence
- ISSUE-000070 — fixed model artifact下でのruntime version交換。harness / guards / preflight実装済み、actual A / BはNot Yet Verified
- ISSUE-000071 — execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeを分ける評価境界

ISSUE-000071のResolvedは、human review完了やKJ-method outcome qualityがSatisfiedになったことを意味しません。

v0.2.0でsupportを主張するrelease scopeはE3aまでです。後続のE3b-P1 / P2 / M1a / M1bやhistorical reconstruction / model exchange Evidenceが存在しても、v0.2.0 scopeを遡及的に拡張しません。

## 10. Cognitive Method outcome-quality evaluation

ISSUE-000071では、actual Method executionの成立と成果品質を分離する評価境界を確立しました。

```text
execution conformance
  != structural safety
  != human outcome review
  != Product Value / Adoption outcome
```

machine checkは、card ID整合、重複、held card境界、manifest整合等の構造上の不変条件を扱います。case catalogはsemantic difficultyを含みますが、golden grouping、expected label、machine-authoritative quality scoreを持ちません。

actual historical M1b outputからhuman review bundleを再構成できる状態にしていますが、human review自体は未完了です。

```text
structure PASS
  != outcome quality PASS

AI auxiliary observation
  != human review
```

## 11. V6 / V7 Projection evaluation

light / audit Projectionを同じcanonical sourceから生成し、semantic question setとnegative caseで意味境界を検査しています。

これはstatic / synthetic evaluation-harness scoped Executable Evidenceです。実利用者の理解可能性、入力負担、見落とし率、production UXのOperational / Adoption Evidenceではありません。

## 12. end-to-end Semantic Product Journey

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

## 13. v0.2.0 Release Evidence

v0.2.0はLocal Reference Product Baselineとしてactual release済みです。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- GitHub Release ID: `380902898`
- historical Release Candidate Gate Run: `33574947445` — **9 gate success**
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

current developの再検証はGitHub Actionsを成立条件にせず、repository-local checker / test / probeへ戻します。これはhistorical Release Evidenceを変更するものではありません。

## 14. Evidenceの現在地

### Design Evidence

Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、current ADR群、Reference Architecture、5 Contract family、2 Representation Profile、Interaction / Access / Packaging / Provider exchange boundary等があります。

### Executable Evidence — scoped

Plan / Requirements / Contract conformance、semantic runtime、Representation Profile / Verifier Registry、Payload Source / Provider Adapter、Cognitive Method、V6 / V7 evaluation、Product Journey、Interaction / Packaging / Persistence / Access / Realization exchange、E3a、E3b-P1、E3b-P2 fixed-artifact、E3b-M1a、E3b-M1b、historical reconstruction、actual model artifact exchange等の限定Evidenceがあります。

ISSUE-000070のruntime version exchangeについては、harness / guard / preflightはありますが、actual A / B exchangeのScoped Executable Evidenceはまだありません。

ISSUE-000071のoutcome-quality評価境界は成立していますが、human outcome reviewは未完了です。

### Release Evidence

**Satisfied for v0.2.0 Local Reference Product Baseline.**

supported scopeはE3aまでです。後続Evidenceをv0.2.0 release scopeへ自動的に取り込みません。

### Operational Evidence

**Not Yet Verified.**

### Adoption / Outcome Evidence

**Not Yet Verified.**

## 15. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

bundle-local Exact Binding整合、historical basis非改変、Payload Source / Verifier境界に加え、historical Method revision再構成とmodel artifact交換後の先行Application保持までscopedに検査済みです。runtime version交換のactual A / B、production Storage、長期間のProvider / representation変更をまたぐ再構成、実際の再判断への寄与は未検証です。

### V2 Semantic Separation

主要な意味分離はfixture / runtimeで検査しています。M1a / M1bでもMethod outputをRecommendation / Decisionへ自動昇格させず、ISSUE-000071ではexecution conformanceと成果品質も分離しました。production責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

同一logical identityの複数Exact Bindingを保持し、参照先revisionをlatest-winsで潰さない境界を検査しています。model artifact交換でも先行Applicationのexact reference保持を確認しました。actual runtime version交換と長期Storage revisionは未検証です。

### V4 Provider Independence

synthetic Adapter、Provider replacement journey、out-of-process exchange、E3a、E3b-P1、fixed-artifact actual TEI、M1a、M1bまでscopedに検査しています。任意TEI / model / runtime versionへの交換、private artifact credential lifecycle、実Providerの廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / residual / reopenの境界はscopedに検査済みです。M1a / M1bの外部Method outputも`not_verified`として保持し、成果品質未評価もそのまま残します。実際の誤判断回避や再検討品質へのOutcome Evidenceはありません。

### V6 Human / AI Readability

ProjectionとInteraction reference probe、Method outcome human-review templateはありますが、実利用者や異なるAI実装による理解度Evidenceはありません。

### V7 Progressive Explicitness

low-impact / high-impactのsynthetic evaluationはあります。実運用でのimpact判定、入力負担、見落とし率は未検証です。

### V8 Execution Independence

Provider / Persistence / Realization交換、fixed-artifact actual TEI、M1a external Method process、M1b actual model-backed execution、actual model artifact exchangeまでscopedなExecutable Evidenceは増えました。runtime交換はrepository-local harnessへ移していますが、actual A / Bは未検証であり、production環境で長期的に意味を維持したOperational Evidenceもありません。

## 16. current Planとの関係

current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000071を管理します。

主要状態は次です。

- ISSUE-000021: **Deferred** — historical design provenance逐語監査
- ISSUE-000063: **Resolved** — v0.2.0 actual Release Evidence
- ISSUE-000064: **Resolved** — E3b-M1a live KJ Atlas Cognitive Method execution
- ISSUE-000065: **Resolved** — E3b-P2 fixed-artifact actual TEI CLI execution
- ISSUE-000066: **Resolved** — E3b-M1b actual model-backed execution
- ISSUE-000067: **Resolved** — Method Definition / Realization / Application historical reconstruction boundary
- ISSUE-000068: **Resolved** — actual model artifact exchange
- ISSUE-000069: **Resolved** — historical CI trigger / runner responsibility boundaryをcurrent no-Actions方針へ整理
- ISSUE-000070: **Open** — fixed model artifact下でのactual runtime version exchange
- ISSUE-000071: **Resolved** — Cognitive Method outcome-quality evaluation boundary

currentではISSUE-000070が唯一のOpen Issueです。

IssueがResolvedであることは、その対象についてOperational / Adoption・Outcome EvidenceまでVerifiedであることを意味しません。ISSUE-000071もhuman review完了やKJ-method outcome qualityのSatisfiedを意味しません。

## 17. CoverageをKPIにしない

Requirement数、Scenario数、fixture数、Issue数、自動検査数、release asset数をProduct ValueのKPIにはしません。

これらは追跡可能性や検査可能性を支える手段です。Product Valueの評価は、各Value AxisとEvidenceの高さへ戻って行います。

## 18. 次に必要なEvidence

v0.2.0 release後に深める主要な領域は次です。

- ISSUE-000070のactual Ollama `0.32.13` / `0.32.14`交換を、同じ固定model artifactとpromptの下で完走するEvidence
- private artifact acquisition / credential lifecycleとTEI version交換
- actual human reviewによるCognitive Method outcome qualityの評価
- model / Method / Provider / runtime交換をまたぐhistorical reconstructionの一般化
- E4 Operational portability
- production Provider / Storage / identity / securityが必要となる具体的な利用文脈
- 次releaseでE3bをsupported scopeへ含める条件
- Operational Evidence
- Adoption / Outcome Evidence

これらはv0.2.0 Release EvidenceやP2 / M1a / M1b、historical reconstruction、model artifact exchange、評価境界の成立を理由に自動的にSatisfiedへ上げません。

## 19. 自然な日本語レビュー

Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、5 Semantic Contract family、2 Representation Profile、current runtime / probe、E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1a / E3b-M1b、ISSUE-000067〜000071、v0.2.0 Release Acceptance / Release Evidenceへ戻って全体を再監査しました。

v0.2.0 Release Evidenceの成立範囲をLocal Reference Product Baselineへ限定したまま、release後に得られたE3b-P2 fixed-artifact actual TEI execution、M1a、M1b、historical Method reconstruction、actual model artifact exchangeをScoped Executable Evidenceとして追跡しています。

runtime version交換については、repository-local harness、guard、Evidence保存、preflightが存在することと、actual Ollama `0.32.13` / `0.32.14` A / B実行が成立したことを分けました。後者はまだNot Yet Verifiedであり、ISSUE-000070をOpenのまま維持しています。

成果品質についても、actual model inferenceの成立、構造検査、人間によるoutcome review、Product Value / Adoption outcomeを分離しました。ISSUE-000071の評価境界成立をhuman review完了やKJ法としての成果品質Satisfiedへ読み替えていません。

GitHub Actionsのhistorical Runは過去のEvidenceとして保持しつつ、current検証の成立条件からは切り離しています。private repositoryに関する未検証論点も、特定automation providerのcredential問題ではなく、private artifact acquisition / credential lifecycleという一般的な運用境界へ戻しました。

意味、規範強度、未決事項、supported scope、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
