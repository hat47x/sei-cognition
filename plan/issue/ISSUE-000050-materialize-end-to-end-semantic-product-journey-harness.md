# ISSUE-000050: end-to-end Semantic Product Journey harnessを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0008, ADR-0009, ADR-0018, ADR-0020, ADR-0021, ADR-0022, ADR-0025**  
Updated: 2026-09-01

## Goal

SCN-0018「Inquiryから実行後の再検討までを一続きに扱う」について、個別Contract / runtime / Provider AdapterのPASSを足し合わせるのではなく、**一つのsemantic Product Journeyとして実際に接続して検査できるExecutable harness**をactual repositoryへ実体化する。

最初のharnessではproduction UIやproduction execution engineを必須にしない。既存Contractから読み取ったcanonical meaningを、評価用のJourney manifestで束ねて検査する。

Journey manifest自体はUniversal Contractでもcanonical product stateでもない。耐久的な意味上の正本は、あくまで既存Contract record側に残す。

## Why now

Product ShapeとREQ-0001〜REQ-0022のcomposition analysisから、新しいUniversal Requirementを増やすより、既存の意味要求をend-to-endで同時に検査することが不足していると分かった。

SCN-0018では、とくに次を一つの経路として扱う。

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

## 2026-09-01 executable slices

### first slice: in-memory semantic bundle

`runtime/go/journeyharness`を追加し、既存の`semanticruntime.Bundle`を入力とする評価用harnessを実体化した。

新しいUniversal Contractは追加していない。

利用する既存recordは次である。

- Cognitive Method `method_application`
- Decision Memory `recommendation`
- Decision Memory `decision`
- Capability Observation
- Semantic Interchange上のopaque / `not_verified` record
- Logical Reference

Inquiry、Unknown、execution receipt等でcurrent Universal Contractを持たない外部Artifactは、harness都合で新しいCore型を作らず、Interchange上のopaque record / stable Logical Referenceとして扱う。

### second slice: actual Semantic Interchange loader

`runtime/go/journeyharness/integration_test.go`を追加し、`semanticruntime.LoadInterchange`を通してwire dataからactual `Bundle`を構成するnormal pathを検査した。

この経路では次を確認する。

- unknown Inquiry / execution receiptはopaque + `not_verified`のまま保持する。
- Cognitive Method Application → Recommendation → Decision → execution result → review Method Applicationを一続きに辿る。
- `ExportOriginal()`が入力Interchange bytesをread時に書き換えない。
- execution後ObservationはDecisionより後に取得されたものとして扱う。
- execution resultが`succeeded`でもhistorical Decision statement / basisを書き換えない。

### third slice: Projection非権威

`runtime/go/journeyharness/projection_test.go`を追加し、Projectionが存在してもcanonical Product Journeyのauthorityへ昇格しないことを検査した。

- Projectionがcanonical recordsと併存してもJourney検査結果を変えない。
- canonical Decisionを除去しProjectionだけを残した場合、Decision欠落としてFAILする。
- Projectionのsummary text等からDecision meaningを推測復元しない。

## 評価用Journey manifest

manifestは、次のrecord identityと評価条件を束ねる。

- Inquiry
- Method Application
- Recommendation
- Decision
- Decision時刻
- execution receipt
- resulting Observation
- reopen Method Application
- unsupported record
- Provider交換前後のCapability Observation
- no-executionを許容するか
- reopen / unresolved carryを要求するか
- collaborative pathでResponsibility分離を要求するか

manifestは**評価用の検査構成**であり、SEIの新しいsemantic authorityにはしない。

## 検査できる意味境界

### Method → Recommendation → Decision

- Method ApplicationのoutputがRecommendationを参照する。
- DecisionがRecommendation referenceを保持する。
- DecisionがMethod Applicationをcontextまたはbasisとして辿れる。
- Recommendationのlogical identityをDecisionとして流用しない。

### Responsibility

- Decision側に明示的なResponsibility referenceがある。
- collaborative pathではMethod Application側とDecision側のResponsibilityを区別できる。
- actor種別だけからAuthorityを推定しない。

### execution後Observationと時間境界

- execution receiptとresult Observationを組として扱う。
- result Observationがreceiptへのprovenance / source referenceを保持する。
- result Observationの`observed_at`がDecision時刻より後である。
- 後から得たObservationを過去Decisionの`basis_refs`へ混入させない。
- execution successを理由にhistorical Decision自体を書き換えない。

### reopen / residual

- reopen Method Applicationが新しいresult Observationをinputとして受け取る。
- uncertain pathではDecisionの`unresolved_refs`をreopen側へ持ち越せる。

### Provider replacement

- 交換前後のCapability Observationが同じCapabilityを対象とする。
- Provider referenceだけが別Providerへ変わる。
- Provider固有IDをDecision identityにはしない。

### unsupported record

- unsupported / external recordをknown semanticsへ昇格させず、`not_verified`のまま保持する。

### no-execution

- external executionがなくてもDecisionまでのJourneyを正当な状態として扱える。

### Projection

- Projectionはcanonical recordと併存できるがauthorityにはしない。
- canonical DecisionがなければProjectionだけからDecisionを補完しない。

## Current executable tests

actual Go testとして、少なくとも次を実装済みである。

1. end-to-end journeyの基本接続
2. no-execution journey
3. execution後Observationの時間逆行拒否
4. execution後Observationをhistorical Decision basisへ混入させるケースの拒否
5. Provider replacementでProviderが実際には変わっていないケースの拒否
6. unsupported recordを`validated`へ昇格させるケースの拒否
7. RecommendationとDecisionを同じidentityへ潰すケースの拒否
8. Semantic Interchangeから読み込むnormal journey
9. opaque Inquiry / execution receiptの`not_verified`保持
10. Interchange original bytesのread時非改変
11. execution success後もhistorical Decision statement / basisを非改変のまま保つこと
12. Projectionとcanonical recordsの安全な併存
13. Projectionだけでは欠落したcanonical Decisionを代替できないこと

主なCI Evidence:

- Run `33477245347` — first in-memory harness: **success**
- Run `33477970035` — Semantic Interchange normal journey追加後: **success**
- Run `33478127484` — Projection非権威追加後: **success**
- Run `33478838079` — Product Requirements再評価後のSemantic Runtime Conformance: **success**
- Run `33478838088` — Product Requirements再評価後のRequirements Registry Conformance: **success**
- Run `33478838032` — Product Requirements再評価後のV6 V7 Projection Evaluation: **success**
- Run `33478838062` — Product Requirements再評価後のPlan integrity: **success**
- Merge commit `3295786702b04b2adde5132bd7656ec2500e7b0d` のpush CI:
  - Run `33496402040` — Semantic Runtime Conformance: **success**
  - Run `33496402082` — Requirements Registry Conformance: **success**
  - Run `33496402054` — V6 V7 Projection Evaluation: **success**
  - Run `33496402010` — Plan integrity: **success**

## Scope

### required variants

#### normal

必要なEvidenceが集まり、Decision後に外部実行まで進む。現在はSemantic Interchange loaderを通る専用fixtureで検査済み。

#### uncertain

Unknown / Conflictを残したままDecisionし、後日得たObservationからreview / Inquiryを再開する。unresolved carry / reopen境界を検査済み。

#### collaborative

AIがCognitive Method Application / Recommendationを担い、人間または明示的に委任された主体がDecisionする。actor種別だけからAuthorityを推定しない。Responsibility分離を検査済み。

#### provider replacement

後続実行では別Providerを利用するが、以前のDecision identityとbasisはProvider固有run IDに依存せず再構成できる。Capability / Provider分離を検査済み。

#### no execution

Decisionまでで終了し、external executionがなくてもDecision recordとhistorical valueが成立する。専用testで検査済み。

## Minimal executable checks

少なくとも次をactual testで検査する。

1. journey内の各Artifact / recordをstable Referenceで辿れる。
2. Decisionから当時のbasisへ戻れる。
3. DecisionからCognitive Method Application、Responsibility、residualへ戻れる。
4. execution resultを新しいObservationとして接続できる。
5. execution後Observationが過去Decision basisへ時間逆行して混入しない。
6. new Observationからreview / reopenの次のcontextへ接続できる。
7. Provider交換後もhistorical Decisionを再構成できる。
8. no-execution variantでもDecisionが成立する。
9. RecommendationをDecisionへ自動昇格しない。
10. Execution successをDecision correctness / Business Outcome successへ自動昇格しない。
11. unsupported versionをknown versionとして扱わない。
12. Projectionだけをcanonical sourceとして利用しない。

1〜12について、現時点ではsynthetic / fixture-scopedなExecutable Evidenceがある。これはproduction Product Journey全体の実証ではない。

## Non-goals

- production UI完成
- production workflow / agent execution engine
- external Providerの本番接続
- Product Identity / Authorization / Collaboration全体の実装
- Storage migrationの全面実証
- operational SLAの検証
- human usabilityの実証
- Adoption / Outcomeの実証

これらはISSUE-000045〜000047や後続Release / Operational / Outcome課題へ分離する。

## Acceptance criteria

### Design

- [x] SCN-0018がcurrent Acceptance Scenarioとして定義されている。
- [x] Requirement composition上、新しいUniversal Requirementが現時点では不要と整理されている。
- [x] harnessのArtifact graph / fixture structureを評価用Journey manifestとして定義する。
- [x] current Contractで表現できないInquiry / execution receipt等を、Universal field追加ではなくopaque external Artifact / Logical Referenceとして扱えることをfirst sliceで確認する。

### Executable

- [x] normal variant専用fixtureがactual testでPASSする。
- [x] uncertain pathに必要なunresolved carry / reopen境界をactual testでPASSする。
- [x] collaborative pathに必要なResponsibility分離をactual testでPASSする。
- [x] provider replacement pathのCapability / Provider分離をactual testでPASSする。
- [x] no-execution variantがactual testでPASSする。
- [x] temporal integrity negative caseがFAILする。
- [x] Recommendation / Decisionの同一視negative caseがFAILする。
- [x] Provider replacement不成立negative caseがFAILする。
- [x] unsupported recordを`not_verified`として扱う境界を検査できる。
- [x] Semantic Interchangeからactual `Bundle`を構成するnormal pathがPASSする。
- [x] execution successがhistorical Decision statement / basisを書き換えないことを検査する。
- [x] Projectionがcanonical Decisionを代替しないことを検査する。
- [x] `go test ./...`とcurrent Contract fixture再検査がRun `33478127484`でsuccessする。

### Evidence update

- [x] SCN-0018のCurrent Evidenceを、確認済み範囲だけ`Partially Satisfied`へ更新する。
- [x] 関連REQのExecutable Evidenceを過大主張せず再評価する。
- [x] Product Value Traceabilityへend-to-end harnessのscopeを反映する。
- [x] component-level PASSとProduct Journey PASSの差をEvidence文書へ残す。

### Higher evidence

- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

本IssueをResolvedにしても、これらを自動的にSatisfiedへ上げない。

## Resolution

本Issueで必要としていたsynthetic / fixture-scopedなend-to-end Product Journey harnessと、そのEvidence反映は完了した。

SCN-0018は、normal / uncertain / collaborative / provider replacement / no-executionの各経路、Semantic Interchange loader、Recommendation / Decision分離、Responsibility分離、execution後Observationの時間境界、historical Decision非改変、unresolved carry / reopen、unsupported recordの`not_verified`保持、Projection非権威までを一続きのExecutable Evidenceとして`Partially Satisfied`にできる状態となった。

一方、production UI、production Provider / execution engine、実Authorization、長期運用上のreopen、Release / Operational / Adoption / Outcome Evidenceは本Issueの完了条件ではなく、未検証のまま明示的に残す。component-level PASSをproduction Product Journey全体の成立へ読み替えない。

## Evidence state

- Design Evidence: **Satisfied for the current harness structure** — 既存Contractを束ねる評価用Journey manifestと、Interchange loaderを通るnormal pathを定義した。
- Executable Evidence: **Partially Satisfied for SCN-0018** — normal / uncertain / collaborative / provider replacement / no-execution、temporal integrity、historical Decision非改変、unsupported record、Projection非権威をfixture-scopedに検査できた。マージ後の`develop/v0.2.0`でもRun `33496402040`を含む対象CIがsuccessしている。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product Shape、`PRODUCT_JOURNEY_COMPOSITION.md`、SCN-0018、REQ-0001〜REQ-0022、current Semantic Reference / Decision Memory / Capability Observation / Semantic Interchange / Cognitive Method Contract、first runtime、V6/V7 Projection evaluationへ戻り、三段階のExecutable sliceとEvidence反映を再整理した。Journeyを表すためだけにUniversal Contractを追加せず、評価用manifestは検査構成に限定し、耐久的な意味は既存record側へ残している。実際に検査したsynthetic / fixture-scopedな範囲だけExecutable Evidenceを`Partially Satisfied`として記録し、production UI、Release、Operational、Adoption / Outcomeへは昇格させていない。そのうえで、意味、規範強度、非対象範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。