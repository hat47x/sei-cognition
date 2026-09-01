# ISSUE-000050: end-to-end Semantic Product Journey harnessを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0008, ADR-0009, ADR-0018, ADR-0020, ADR-0021, ADR-0022, ADR-0025**  
Updated: 2026-09-01

## Goal

SCN-0018「Inquiryから実行後の再検討までを一続きに扱う」について、個別のContract、runtime、Provider AdapterのPASSを足し合わせるだけではなく、**一つのsemantic Product Journeyとして接続して検査できるExecutable harness**をactual repositoryへ実体化する。

このharnessのために新しいUniversal Contractやcanonical product stateは作らない。耐久的な意味上の正本は既存Contract recordに置き、Journey manifestは評価用の検査構成として扱う。

## Resolution

`runtime/go/journeyharness`を実体化し、SCN-0018で要求する主要な意味境界を、fixture-scopedな一つのProduct Journeyとして検査できる状態にした。

最終的に、次の三つのExecutable sliceを接続した。

1. **in-memory semantic bundle** — 既存の`semanticruntime.Bundle`を使い、normal / uncertain / collaborative / provider replacement / no-executionの主要variantを検査する。
2. **Semantic Interchange wire path** — `semanticruntime.LoadInterchange`を通してactual wire dataからBundleを構成し、opaqueな外部Artifactを`not_verified`のまま保持する。
3. **Projection非権威** — Projectionが存在してもcanonical Decisionを代替せず、Projectionから欠落した意味を推測復元しないことを検査する。

これにより、SCN-0018のDesign EvidenceはSatisfied、Executable Evidenceは確認済み範囲でPartially Satisfiedとする。production Product Journey全体の成立を意味しない。

## 検査した意味境界

### Method → Recommendation → Decision

- Cognitive Method ApplicationのoutputからRecommendationを辿れる。
- DecisionがRecommendation referenceを保持する。
- DecisionからMethod Applicationをcontext / basisとして辿れる。
- RecommendationとDecisionのlogical identityを同一化しない。

### Responsibility

- Decision側に明示的なResponsibility referenceを保持できる。
- collaborative pathではMethod側とDecision側のResponsibilityを区別する。
- actor種別だけからAuthorityを推定しない。

### execution後Observationと時間境界

- execution resultを後続Observationとして接続できる。
- result ObservationはDecisionより後のObservationとして扱う。
- 後から得たObservationを過去Decisionの`basis_refs`へ混入させない。
- execution successによってhistorical Decision statement / basisを書き換えない。

### reopen / residual

- uncertain pathでDecisionの`unresolved_refs`を後続reviewへ持ち越せる。
- 新しいObservationをreopen Method Applicationのinputとして参照できる。

### Provider replacement

- 交換前後で同じCapability identityを維持する。
- Provider referenceだけを別Providerへ変更できる。
- Provider固有IDをDecision identityへ流用しない。

### unsupported / external record

- Inquiryやexecution receipt等、current Universal Contractを持たない外部Artifactをopaque recordとして保持できる。
- unsupported recordをknown semanticsへ昇格せず、`not_verified`のまま扱う。

### no-execution

- external executionがなくてもDecisionまでのJourneyを正当な状態として扱える。

### Projection

- Projectionはcanonical recordsと併存できるが、semantic authorityにはしない。
- canonical Decisionが欠落した場合、Projectionのsummary等からDecisionを補完しない。

## Executable Evidence

実装済みtestでは、少なくとも次を検査している。

1. end-to-end journeyの基本接続
2. no-execution journey
3. execution後Observationの時間逆行拒否
4. post-execution Observationのhistorical Decision basisへの混入拒否
5. Provider replacement不成立の拒否
6. unsupported recordの不当な`validated`昇格拒否
7. Recommendation / Decision identity同一化の拒否
8. Semantic Interchange loaderを通るnormal journey
9. opaque Inquiry / execution receiptの`not_verified`保持
10. `ExportOriginal()`によるInterchange原文のread時非改変
11. execution success後もhistorical Decision statement / basisを非改変に保つこと
12. Projectionとcanonical recordsの安全な併存
13. Projectionだけではcanonical Decisionを代替できないこと

主要な成立過程:

- Run `33477245347` — first in-memory harness: **success**
- Run `33477970035` — Semantic Interchange normal journey: **success**
- Run `33478127484` — Projection非権威を含むjourney harness: **success**

SCN-0018、Requirements、Product Value TraceabilityへEvidenceを反映した後も、current developへの統合commit `3295786702b04b2adde5132bd7656ec2500e7b0d` で次を再確認した。

- Plan integrity Run `33496402010` / #131: **success**
- Requirements Registry Conformance Run `33496402082` / #16: **success**
- V6 V7 Projection Evaluation Run `33496402054` / #21: **success**
- Semantic Runtime Conformance Run `33496402040` / #40: **success**

このpost-merge確認は、fixture-scopedなExecutable Evidenceがcurrent `develop/v0.2.0`でも維持されていることを示す。Release、Operational、Adoption / Outcome Evidenceへは昇格させない。

## Evidence update

- [x] SCN-0018のCurrent Evidenceを、確認済み範囲だけ`Partially Satisfied`へ更新した。
- [x] 関連REQのExecutable Evidenceを、component / journeyの確認範囲を超えないよう再評価した。
- [x] `SOZA_VALUE_TRACEABILITY.md`へend-to-end harnessのscopeを反映した。
- [x] component-level PASSとProduct Journeyのfixture-scoped PASSを区別し、production Product Journeyの成立と同一視しないことを明記した。

## Evidence boundary

```text
component-level PASS
  != fixture-scoped Product Journey PASS

fixture-scoped Product Journey PASS
  != production Product Journey validated
  != human interaction validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

現在のEvidence状態:

- Design Evidence: **Satisfied for the current harness structure**
- Executable Evidence: **Partially Satisfied for SCN-0018**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Non-goals / follow-up

本Issueでは次を完了扱いにしない。

- production UI
- production workflow / agent execution engine
- external Providerの本番接続
- Product Identity / Authorization / Collaboration全体
- Storage migrationの全面実証
- operational SLA
- human usability
- Adoption / Outcome

Product InteractionはISSUE-000045、Packaging / DeploymentはISSUE-000046、Identity / Authorization / CollaborationはISSUE-000047で扱う。cross-contract exact bindingの一般化はISSUE-000049へ分離している。

## Reopen conditions

次の場合は再開を検討する。

- SCN-0018の意味境界をcurrent harnessで再現できなくなった。
- Semantic Interchange経路とin-memory経路でmeaning reconstructionが乖離した。
- Projectionがcanonical authorityへ逆流する設計変更が入った。
- production Product Journeyの実装で、current fixtureでは見えていなかった新しいUniversal semantic gapが確認された。

新しいUIやProviderが追加されたという理由だけでは再開しない。

## Natural Japanese review

Product Shape、`PRODUCT_JOURNEY_COMPOSITION.md`、SCN-0018、REQ-0001〜REQ-0022、current Contract群、semantic runtime、V6/V7 Projection evaluation、actual CIを相互照合した。作業途中の時系列記録をそのまま残すのではなく、完了した意味境界、Executable Evidence、非主張範囲、follow-upを読み手が追える構造へ整理した。その後、意味、Acceptance強度、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
