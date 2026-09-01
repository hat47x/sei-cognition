# ISSUE-000053: first Product Interaction reference probeを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0028**  
Updated: 2026-09-01

## Goal

`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028で定めたfirst usable Product Interaction boundaryについて、human-oriented入口とmachine-oriented入口が**同じcanonical meaningを失わずに扱えること**をreference probeで検証する。

このprobeはproduction UIやsupported protocolを決定するものではない。PMS-03をDesign EvidenceからExecutable Evidenceへ進めるための限定実験として扱う。

## Resolution

`runtime/go/interactionprobe`に、単一Inquiryを対象とするevaluation-onlyのreference probeをGoで実体化した。

```text
HumanSurface ───┐
                ├─ CanonicalStore ─ existing semanticruntime records
MachineSurface ─┘
```

`CanonicalStore`はproduction Storageではなく、このprobeでSurface間の意味共有を検査するためのin-memory storeである。新しいUniversal Contractや新しいcanonical entityは追加していない。

既存Contractで表現できるRecommendation、Decision、Capability Observation、Cognitive Method Applicationは、既存`semanticruntime`型を利用し、`semanticruntime.LoadStandalone`でcurrent validatorを通してからcanonical storeへ追加する。

current typed runtimeで独立ContractがまだないInquiry、Unknown、Conflictは、意味を理解済みと偽らず、opaqueな`not_verified` recordとして保持する。

## 実体化したSurface

### human-oriented Surface

人間がContractのfield名を直接編集しなくても、次を扱える最小Surfaceを用意した。

- 短い文章からInquiryを開始する。
- Unknown / Conflictを追加する。
- machine側が追加したObservation / Recommendationをlight viewで読む。
- Recommendationと区別してDecisionを記録する。
- audit viewからbasis、Responsibility、unresolved refs等へ降りる。

これはproduction CLI仕様ではない。text / CLI相当の操作境界をGo APIとして最小限に表したreference probeである。

### machine-oriented Surface

機械向けには、構造化された操作として次を実体化した。

- Capability Observationを追加する。
- Cognitive Method Applicationを追加する。
- Recommendationを追加する。
- structured viewからcanonical recordを読む。
- human側が記録したDecisionをDecisionとして再読する。
- RecommendationをRecommendationとして再読する。

実AI modelやagent runtimeは接続していないため、AI integrationのproduction usabilityまでは検証していない。

## 必須検査の結果

### 1. 二つの入口が同じcanonical sourceを利用する

**Satisfied in scoped Executable Evidence.**

HumanSurfaceとMachineSurfaceを同一`CanonicalStore`へ接続し、一方が追加したtyped recordを他方から再読するtestを実装した。

### 2. 最小入力から開始し、後から詳細化できる

**Satisfied in scoped Executable Evidence.**

Inquiryだけの最小状態から開始し、その後にUnknown / Conflict、Observation、Method Application、Recommendation、Decisionを追加できることを確認した。

これはproduction UI上の入力負担が十分小さいことのEvidenceではない。

### 3. machine側のObservation / Recommendationをhuman側が再読できる

**Satisfied in scoped Executable Evidence.**

Capability ObservationとRecommendationをMachineSurfaceから追加し、HumanSurfaceのlight viewから同じlogical identityを再読できることを確認した。

### 4. human側Decisionをmachine側がDecisionとして取得できる

**Satisfied in scoped Executable Evidence.**

HumanSurfaceで記録したDecisionをMachineSurfaceからDecisionとして取得し、Recommendationへ読み替えないことを確認した。

### 5. RecommendationとDecisionを平坦化しない

**Satisfied in scoped Executable Evidence.**

RecommendationとDecisionを別typed recordとして扱い、Recommendationと同じlogical identityをDecisionへ再利用しようとした場合はduplicate canonical recordとして拒否する。

### 6. Unknown / Conflictを平坦化しない

**Satisfied in scoped Executable Evidence.**

UnknownとConflictを別のopaque `not_verified` recordとして保持し、light / audit Projectionから再読できることを確認した。

### 7. Projection再生成でcanonical sourceを変えない

**Satisfied in scoped Executable Evidence.**

light view / audit view / structured viewはcanonical storeから都度生成する。Projection生成前後でprobe内部のcanonical digestが変化しないことを確認した。

このdigestはprobe内部の比較用であり、Representation ProfileやExact Bindingではない。

### 8. audit Projectionから詳細へ降りられる

**Satisfied in scoped Executable Evidence.**

Decisionについて、audit viewからbasis、Responsibility、unresolved refsを確認できることをtestで固定した。

### 9. private chain-of-thoughtを保存しなくても成立する

**Satisfied in scoped Executable Evidence.**

MachineSurfaceのRecommendation入力はprivate chain-of-thoughtやreasoning transcriptを要求しない。statement、必要なbasis、任意のrationale等でtyped Recommendationを成立させる。

### 10. 実行後Observationでhistorical Decision basisを改変しない

**Satisfied in scoped Executable Evidence.**

Decision記録後に新しいCapability Observationを追加し、既存Decisionの`basis_refs`が変化しないことを確認した。

### 11. actor kindからAuthority / Responsibilityを自動推定しない

**Partially Satisfied in scoped Executable Evidence.**

MachineSurfaceからRecommendationを作成してもResponsibilityを自動付与しないことを確認した。Authority自体をこのprobe独自に生成する経路は持たないため、AI / machine SurfaceであることからAuthority recordを合成する実装もない。

production Identity / AuthorizationはISSUE-000047の範囲であり、本probeでは扱わない。

### 12. Surface固有stateを削除してもcanonical artifactを失わない

**Satisfied in scoped Executable Evidence.**

Surface-local stateをcanonical storeから分離し、選択状態等を設定・破棄してもcanonical digestが変化しないことを確認した。

さらに、会話履歴だけに置いたRecommendation相当の文字列や画面状態だけに置いたDecision相当の文字列が、canonical Recommendation / DecisionとしてProjectionへ現れないnegative testを追加した。

## Negative cases

次の失敗境界をactual testまたは構造上の拒否として確認した。

- chat / Surface-local stateだけのRecommendationをcanonical Recommendationとして扱わない。
- human UI / Surface-local stateだけのDecisionをcanonical Decisionとして扱わない。
- Recommendationと同じlogical identityをDecisionへ再利用する操作を拒否する。
- light viewに表示しない詳細をProjection生成だけでcanonical sourceから削除しない。
- MachineSurfaceであることを理由にResponsibilityを自動付与しない。
- post-decision Observation追加でhistorical Decision basisを書き換えない。
- opaque recordを`validated`として追加し、未対応意味を理解済みと偽る操作を拒否する。

## 既存runtimeとの重複監査

reference probeを第二のsemantic runtimeとして作っていない。

- typed validation — `semanticruntime.LoadStandalone`を再利用。
- semantic record型 — existing `semanticruntime`型を再利用。
- Recommendation / Decision separation — Decision Memory Contractの既存境界を利用。
- temporal integrity — `journeyharness`の既存Evidenceと同じ方向をInteraction操作で再確認。
- Projection非権威性 — V6 / V7 evaluationの既存方針と整合。

`interactionprobe`に追加したのは、これらの上へhuman-oriented / machine-oriented Surfaceを載せ、同じcanonical sourceを操作する最小Product Interactionを検査する範囲である。

## Requirement / Scenario再監査

probe結果から、現時点で新しいstable Product RequirementやAcceptance Scenarioを追加する必要性は確認されなかった。

引き続き次を検査軸とする。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0006 — 提案・判断・権限・実行の分離
- REQ-0010 — Progressive Semantic Explicitness
- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0014 — 未解決残差と再開条件の保持
- REQ-0015 — private chain-of-thoughtへ依存しない
- REQ-0019 — 人間とAIの双方が意味を読める
- SCN-0013 — 簡略UIとcanonical meaningを両立する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

Interaction probeの実装都合だけでREQ / SCNを追加しない。

## Non-goals / 未検証範囲

今回、次は確認していない。

- production Web / desktop / CLI UI
- 実AI modelからの呼び出し
- HTTP API / MCP / SDKのproduction protocol
- 複数Inquiryを扱うworkspace
- production persistence
- process restart後のresume
- concurrent write / transaction
- login / authorization / tenant / collaboration
- production security
- human usability test
- latency / throughput / resource usage
- actual Provider / TEI integration
- Operational / Adoption / Outcome Evidence

特に`CanonicalStore`は単一Inquiry向けのin-memory evaluation storeであり、その制約をSOZA Productの仕様へ一般化しない。

## 完了条件

- [x] human-oriented probeを実体化する。
- [x] machine-oriented probeを実体化する。
- [x] 両Surfaceを同じinteraction core / canonical sourceへ接続する。
- [x] 必須検査とnegative caseをactual testへ落とす。
- [x] current semantic runtime / journey harness / Projection evaluationとの重複を監査する。
- [x] CIで再現可能なExecutable Evidenceを得る。
- [x] Product Interaction / PMS-03 / Evidence文書へ結果を同期する。
- [x] Requirement / SCN追加の要否をprobe結果から再監査する。今回は追加しない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 対象CIをsuccessさせる。

追加negative testと上流文書・registry同期を含むhead `5d230c86845c32d1df5bb35192221f2b25105d71`で、Semantic Runtime Conformance Run `33504002579`とPlan integrity Run `33504002562`がともに**success**した。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Scoped Evidence available** — `runtime/go/interactionprobe`のcurrent testとSemantic Runtime Conformance Run `33504002579`。
- Planning / document integrity: **Satisfied for this work unit** — Plan integrity Run `33504002562`。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

詳細は`runtime/INTERACTION_PROBE_EVIDENCE_2026-09-01.md`を正とする。

## Reopen / escalation条件

- Case / Session等の新しい耐久的semantic entityがないと実利用上の意味を保持できないEvidenceが得られた。
- human / machine共通の操作境界では重要な意味差を保持できない。
- existing Semantic Contractに不足があり、Interactionだけでは解決できない。
- Packaging / DeploymentまたはIdentity / Authorizationの設計から、現在のInteraction boundaryと両立しない必須条件が確認された。
- production usability testで、current操作境界そのものが利用者の仕事と大きくずれていることが確認された。

## Natural Japanese review

Product Interaction baseline、ADR-0028、PMS-03、current semanticruntime、journeyharness、V6 / V7 Projection evaluation、`runtime/go/interactionprobe`のactual test、Semantic Runtime Conformance Run `33504002579`、Plan integrity Run `33504002562`を照合した。probeで確認できたSurface交換可能性と、production UX、protocol、Storage、Identity等の未検証範囲を分離している。また、probe固有のin-memory storeやSurface DTOをUniversal Coreへ昇格させず、既存Requirement / Scenarioを先に再利用する境界を維持した。そのうえで、意味、要求強度、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。