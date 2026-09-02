# SOZA Value Traceability

更新日: 2026-09-02  
状態: **Current Product Value Traceability Baseline — v0.2.0 Release Evidence reflected**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Semantic Contract、Representation Profile、runtime、各種probe、Release Candidate Gate、actual Release Evidenceまで上位から追跡するための索引です。

この文書自体が新しい意味上の正本になることはありません。詳細は次を正とします。

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
- runtime: `../../runtime/go/`
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
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016, 0018 | Semantic Reference / Decision Memory / Interchange、Exact Binding、Cognitive Method、Verifier / Payload Source、historical basis非改変、known Contract横断bundle-local consistency |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016, 0018 | Recommendation / Decision / Authority分離、Unknown / Withheld、Cognitive Method分離、Responsibility分離、unknown Contract非推測解析 |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016, 0018 | lineage / Exact Binding invariant、Representation Profile、Cognitive Method exact refs、複数exact revision保持、historical basis非改変 |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014, 0018 | Capability Observation、synthetic Provider Adapter、Provider replacement journey、out-of-process exchange、E3a external artifact、E3b-P1 public live Provider |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016, 0018 | Unknown / Conflict / Withheld / partial knowledge、missing→unknown、Decision residual→reopen path |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | human-readable Contract、machine-readable schema、light / audit Projection、first Product Interaction reference probe |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | low-impact / high-impact Projection evaluation、canonical operationとInteractionの分離 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015, 0018 | provider-neutral Contract、Cognitive Method、Payload Source、no-execution journey、local package / Storage migration、out-of-process exchange、TEI executable injection boundary |

表中のmaterialが存在しても、そのValue Axis全体がOperational / OutcomeまでSatisfiedになったとは読みません。

## 4. Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0018`です。

```text
Requirement != Acceptance Scenario != Test Case
```

SCN-0018は個別Scenarioを置き換えません。InquiryからDecision、外部実行、実行後Observation、historical review / reopenまでを代表的なProduct Journeyとして接続し、複数の意味境界が同時に失われないことを検査します。

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

historical M47 digest ruleはISSUE-000034の方針どおり、現在保持されている直接Evidenceから回収できない範囲を`not_verified`として維持します。

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

外部bytesの取得はPayload Source、digest再計算はVerifier Registryの責務です。unknown Contractのpayloadに似たfieldがあっても、field名から推測解析しません。

## 7. semantic runtime / Provider / Storage

semantic runtimeはread / validate / reconstructを中核にし、SOZA自身をworkflow / agent execution engineへしません。

current scoped materialには次があります。

- known Contract typed runtime
- Representation Verifier Registry
- synthetic Payload Source
- synthetic Provider Adapter
- Cognitive Method typed runtime
- known Contract横断bundle-local Exact Binding consistency
- out-of-process Realization / Provider exchange
- packaged resume / Storage migration probe
- Product Interaction / Access probe
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- actual TEI実行前のexternal executable injection boundary

これらのPASSはproduction Provider / Storage / external executionの運用成立を意味しません。

## 8. Product Interaction / Access / Packaging

current Product baselineでは、次の境界とreference probeが成立しています。

- human-oriented / machine-oriented Surfaceから同じcanonical meaningへ戻るProduct Interaction
- Local Single-Node Packaging
- deterministic Linux / amd64 Local Reference Package
- process restart後のresume / Storage migration probe
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

E3bは現在、P1 / P2 / M1へ分けて観測しています。

- E3b-P1: public live Provider service — **Scoped Executable Evidence available**
- E3b-P2: actual TEI process / service — **Not Yet Verified**
- E3b-M1: external Cognitive Method live execution — **Not Yet Verified**

v0.2.0でsupportを主張するrelease scopeはE3aまでです。後続のE3b-P1 Evidenceが存在しても、release後にv0.2.0 scopeを拡張しません。

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

v0.2.0は、Local Reference Product Baselineとしてactual release済みです。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- GitHub Release ID: `380902898`
- Release Candidate Gate Run: `33574947445` — **9 gate success**
- release preparation: **success**
- publication: **success**

Local Reference Packageについて、release preparationで算出したSHA-256とactual GitHub Release assetのdigestが一致しています。

`37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`

4つのrelease assetも実在を確認済みです。

- `soza-local-reference-linux-amd64.tar.gz`
- `soza-local-reference-linux-amd64.tar.gz.sha256`
- `v0.2.0-candidate-report.json`
- `release-metadata.json`

これにより、**v0.2.0 Local Reference Product BaselineについてRelease EvidenceをSatisfied**と評価します。

```text
Release Evidence Satisfied
  != E3b全体 Satisfied
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

詳細なEvidence recordは`../../release/v0.2.0/RELEASE_EVIDENCE.md`を正とします。

## 13. Evidenceの現在地

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Design Evidence

Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、current ADR群、Reference Architecture、5 Contract family、2 Representation Profile、Interaction / Access / Packaging / Provider exchange boundary等があります。

### Executable Evidence — scoped

Plan / Requirements / Contract conformance、semantic runtime、Representation Profile / Verifier Registry、Payload Source / Provider Adapter、Cognitive Method、V6 / V7 evaluation、Product Journey、Interaction / Packaging / Storage / Access / Realization exchange、E3a、E3b-P1等の限定Evidenceがあります。

### Release Evidence

**Satisfied for v0.2.0 Local Reference Product Baseline.**

supported scopeはE3aまでです。E3b-P1等の後続Evidenceをv0.2.0 release scopeへ自動的に取り込みません。

### Operational Evidence

**Not Yet Verified.**

### Adoption / Outcome Evidence

**Not Yet Verified.**

## 14. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

bundle-local Exact Binding整合、historical basis非改変、Payload Source / Verifier境界はscopedに検査済みです。production Storageや長期間のProvider / representation変更をまたぐhistorical reconstruction、実際の再判断への寄与は未検証です。

### V2 Semantic Separation

主要な意味分離はfixture / runtimeで検査しています。production責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

同一logical identityの複数Exact Bindingを保持し、参照先revisionをlatest-winsで潰さない境界を検査しています。cross-bundleの実payload検証や長期Storage revisionは未検証です。

### V4 Provider Independence

synthetic Adapter、Provider replacement journey、out-of-process exchange、E3a、E3b-P1までscopedに検査済みです。実Providerの交換・廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / residual / reopenの境界はscopedに検査済みです。実際の誤判断回避や再検討品質へのOutcome Evidenceはありません。

### V6 Human / AI Readability

ProjectionとInteraction reference probeはありますが、実利用者や異なるAI実装による理解度Evidenceはありません。

### V7 Progressive Explicitness

low-impact / high-impactのsynthetic evaluationはあります。実運用でのimpact判定、入力負担、見落とし率は未検証です。

### V8 Execution Independence

Provider / Storage / Realization交換のscoped probeは増えましたが、異なるproduction Execution / Storage Provider間で長期的に意味を維持したOperational Evidenceはありません。

## 15. current Planとの関係

current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000063を管理します。

主要状態:

- ISSUE-000021: **Deferred** — historical design provenance逐語監査
- ISSUE-000063: **Resolved** — v0.2.0 actual Release Evidence記録
- ISSUE-000001〜000020、000022〜000063: **Resolved**

IssueがResolvedであることは、その対象についてOperational / Adoption・Outcome EvidenceまでVerifiedであることを意味しません。

## 16. CoverageをKPIにしない

Requirement数、Scenario数、fixture数、Issue数、CI本数、release asset数をProduct ValueのKPIにはしません。

これらは追跡可能性や検査可能性を支える手段です。Product Valueの評価は、各Value AxisとEvidenceの高さへ戻って行います。

## 17. 次に必要なEvidence

v0.2.0 release後に深める主要な領域は次です。

- actual TEI process / serviceを用いたE3b-P2
- external Cognitive Method live execution
- E4 Operational portability
- production Provider / Storage / identity / securityが必要となる具体的な利用文脈
- Operational Evidence
- Adoption / Outcome Evidence

これらはv0.2.0 Release Evidence成立を理由に自動的にSatisfiedへ上げません。

## 18. Natural Japanese review

Product Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、5 Semantic Contract family、2 Representation Profile、current runtime / probe、E3a / E3b-P1、v0.2.0 Release Acceptance、actual `v0.2.0` tag、GitHub Release、release asset、Run `33574947445`、ISSUE-000063へ戻って全体を再監査しました。

旧本文に残っていた「Release Evidence Not Yet Verified」や古いPlan範囲をcurrent stateへ改める一方、Release Evidenceの成立範囲をv0.2.0 Local Reference Product Baselineへ限定しました。E3b全体、E4、production readiness、Operational Evidence、Adoption / Outcome Evidenceは未検証のままです。意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
