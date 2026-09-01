# ISSUE-000048: end-to-end golden journeyとProduct Acceptanceを定義する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Updated: 2026-09-01

## Goal

個別Contract、fixture、runtime sliceの成立だけでなく、利用者から見た一続きの判断仕事としてSOZAの価値を確認できる代表的なend-to-end Acceptance Scenarioを定義する。

このScenarioを固定workflow ontologyにはせず、Product Shapeと既存REQ / SCNを横断してMinimum Usable Product Shapeを検査するgolden journeyとして扱う。

## Resolution

`requirements/PRODUCT_JOURNEY_COMPOSITION.md`でProduct ShapeとREQ-0001〜REQ-0022、SCN-0001〜SCN-0017を照合した結果、Minimum Usable Product Shapeの主要な意味要求は既存REQで概ね表現できると判断した。

したがって、Product Journeyのためだけに新しいUniversal Requirementを追加せず、既存Requirementを一つのjourneyで同時に成立させる統合Acceptance Scenarioを追加した。

current Acceptance Scenarioの正本には次を追加した。

```text
SCN-0018
Inquiryから実行後の再検討までを一続きに扱う
```

SCN-0018では、次を一続きに扱う。

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

とくに、external execution後に得たObservationを過去Decisionのbasisへ時間逆行させず、次のInquiry / Decision reviewへ接続する境界を明示した。

## Requirementに関する判断

現時点では新しいREQを追加しない。

- durable continuityはREQ-0001で扱える。
- historical Decision reconstructionはREQ-0005で扱える。
- residual / reopenはREQ-0014で扱える。
- Cognitive Method境界はREQ-0004 / REQ-0015 / REQ-0021で扱える。
- Capability / Provider中立性はREQ-0007 / REQ-0022で扱える。
- human / AI readabilityとProjection非権威はREQ-0010 / REQ-0011 / REQ-0019で扱える。

Product Interaction上の順序、workspace、session等をこのIssueからUniversal semantic Coreへ昇格させない。

## SCN-0018のvariant

- **normal path** — Evidenceが集まり、Decision後に外部実行まで進む。
- **uncertain path** — Unknown / Conflictを残したままDecisionし、後日新Evidenceから再開する。
- **collaborative path** — AIがMethod Application / Recommendationを担い、人間または委任された主体がDecisionする。
- **provider replacement path** — 実行Providerを交換しても以前のDecision identityとbasisを読み直せる。
- **no-execution path** — Decisionまでで完結してもhistorical valueが成立する。

## Executable follow-up

SCN-0018のExecutable Evidenceは本Issueでは取得しない。

実装・検証は次へ分離した。

```text
ISSUE-000049
end-to-end Semantic Product Journey harnessを実体化する
```

ISSUE-000049では、Cognitive Method、Decision、Capability / Provider、実行後Observation、historical review / reopenを一つの検査経路として接続する。

```text
component-level PASS
  != SCN-0018 end-to-end PASS
```

既存Contract / runtime / Provider Adapter / Projection evaluationのPASSを単純加算してSCN-0018をSatisfiedにはしない。

## 完了条件

- [x] Product Shapeと既存REQ / SCNの重複・不足を監査する。
- [x] 新しいREQを追加する必要が現時点でないことを確認する。
- [x] normal / uncertain / collaborative / provider replacement / no-executionの主要variantを整理する。
- [x] semantic end-to-end harnessの期待結果・失敗条件をDesignとして定義する。
- [x] SCN-0018をstable IDとしてAcceptance Scenario正本へ反映する。
- [x] Executable harnessをISSUE-000049へ分離して起票する。
- [x] Release / Operational / Adoption・Outcomeへ過大昇格させない。
- [x] 追加・更新文書を自然な日本語へ全文再ドラフトし、最終意味監査する。

## Evidence state

- Design Evidence: **Satisfied** — Requirement compositionとSCN-0018のcurrent正本化まで完了した。
- Executable Evidence: **Not Yet Verified for SCN-0018 end-to-end**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

CI successは本変更のPlanning / Requirements整合のEvidenceとして別途確認するが、SCN-0018のend-to-end Executable Evidenceには数えない。

## Reopen conditions

次の場合は再開を検討する。

- SCN-0018を実装する過程で既存REQでは表現できない独立した規範上の必要性が見つかる。
- Product Journeyが固定workflow ontologyとして誤用される。
- execution後Observationとhistorical Decision basisの時間境界が現行Scenarioでは曖昧であることが判明する。
- SCN-0018のvariantでは重要なProduct Shapeを検査できないことが分かる。

## Natural Japanese review

Product Shape、REQ-0001〜0022、SCN-0001〜0018、`PRODUCT_JOURNEY_COMPOSITION.md`、ISSUE-000049、5段階Evidenceへ戻り、DesignとExecutable実装の責務を分離した。新しいUniversal Requirementを増やさず、実行後Observationを次の再検討へ接続する統合Scenarioをcurrent正本へ置くという判断を維持したまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
