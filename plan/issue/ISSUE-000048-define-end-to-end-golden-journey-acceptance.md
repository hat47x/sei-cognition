# ISSUE-000048: end-to-end golden journeyとProduct Acceptanceを定義する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Updated: 2026-09-01

## Goal

個別Contract、fixture、runtime sliceの成立だけでなく、利用者から見た一続きの判断仕事としてSEIの価値を確認できる代表的なend-to-end Acceptance Scenarioを定義する。

このScenarioを固定workflow ontologyにはせず、Product Shapeと既存REQ / SCNを横断してMinimum Usable Product Shapeを検査するためのgolden journeyとして扱う。

## Resolution

本Issueでは、Product Shape、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017を照合し、次を確定した。

1. Minimum Usable Product Shapeの主要な意味要求は既存REQで概ね表現できる。
2. Product Journeyを理由に新しいUniversal Requirementを追加する必要は、現時点ではない。
3. 不足していたのは、新しいsemantic ontologyではなく、既存Requirementが一つのProduct Journeyで同時に壊れないことを確認するend-to-end Acceptanceである。
4. とくに、external execution後に得たObservationを、過去Decisionのbasisへ時間逆行させず、次のInquiry / Decision reviewへ戻す循環を明示する必要がある。
5. この不足をstable Scenario SCN-0018「Inquiryから実行後の再検討までを一続きに扱う」として`requirements/ACCEPTANCE_SCENARIOS.md`へ正本化した。
6. Executable harnessの実体化は、DesignとImplementationのEvidenceを混同しないため、ISSUE-000050へ分離した。

したがって、本IssueのDesign課題は完了とする。

## Product Journey

SCN-0018では、代表経路として次を扱う。

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

これは全利用者へ一つの手順を強制するworkflow定義ではない。個別Scenarioで守ってきた意味境界が、一つのProduct Journeyの中でも同時に失われないことを確認する統合Scenarioである。

## Requirement判断

新しいREQは追加しない。

Product Journeyの順序、Workspace、Session、画面遷移等をそのままUniversal Requirementへ昇格させると、Product Interactionや実装都合をsemantic Coreへ持ち込む危険がある。

新しいREQが必要になるのは、今後のExecutable / Interaction検証で、既存REQでは表現できない独立した規範上の必要性が見つかった場合だけとする。

## SCN-0018の主要variant

- **normal path** — 必要なEvidenceが集まり、Decision後に外部実行まで進む。
- **uncertain path** — Unknown / Conflictを残したままDecisionし、後日得たObservationから再開する。
- **collaborative path** — AIがMethod Application / Recommendationを担い、人間または明示的に委任された主体がDecisionする。actor種別だけからAuthorityを推定しない。
- **provider replacement path** — 後続実行でProviderを交換しても、以前のDecision identityとbasisを読み直せる。
- **no-execution path** — Decisionまでで完結し、外部実行がなくてもSEI上の記録価値が成立する。

## SCN-0018で守る意味境界

- Inquiry開始時に最大詳細を一律に強制しない。
- Observation、Interpretation、Unknown、ConflictをDecisionへ黙って畳み込まない。
- Method Definition / Realization / Applicationを必要な範囲で読み分けられる。
- RecommendationをDecisionへ自動昇格させない。
- DecisionとResponsibility / Authorityを必要な粒度で追える。
- Provider固有run IDをDecision identityにしない。
- Execution successをDecision correctnessやBusiness Outcomeへ自動昇格させない。
- 実行後に得たObservationを、過去Decision作成時から存在したEvidenceとして扱わない。
- residual / reopen informationを保持し、新しいObservationからInquiryへ戻れる。
- ProjectionやProviderを交換してもcanonical meaningとhistorical basisを再読できる。
- external executionを行わないDecisionも正当なProduct Journeyとして扱える。

## 代表的な失敗例

- AI RecommendationをそのままDecisionとして保存する。
- Decision作成時にUnknown / Conflictを自動的にresolvedへ変える。
- Provider runが成功しただけでDecisionを`verified`または「正しかった」と扱う。
- 実行後に得たObservationで過去Decisionのbasisを上書きする。
- current ProviderやProjectionが利用不能になると過去Decisionを読めない。
- external executionがないDecisionを不完全なrecordとして捨てる。

## Executable Acceptanceとの分離

本IssueはAcceptanceのDesignを確定するところまでを責務とする。

```text
SCN-0018 Design Satisfied
  != semantic end-to-end harness PASS
  != usable human interaction proven
  != packaged product proven
  != release ready
  != operationally reliable
  != user outcome proven
```

Executable harnessはISSUE-000050で扱う。human usabilityはISSUE-000045、PackagingはISSUE-000046、Identity / Authorization / CollaborationはISSUE-000047と連携して段階的にEvidenceを高める。

## Non-goals

- 一つのgolden journeyを全利用者へ強制すること
- Milestone順序を業務workflowへ固定すること
- production UI完成を本Issueの完了条件にすること
- workflow / agent engineの内製
- synthetic harnessだけでRelease / Operational / Adoption・OutcomeをSatisfiedにすること

## 完了条件

- [x] Product Shapeと既存REQ / SCNの重複・不足を監査する。
- [x] 新しいREQを追加する必要が現時点でないことを確認する。
- [x] normal / uncertain / collaborative / provider replacement / no-executionの主要variantをAcceptanceへ整理する。
- [x] semantic end-to-end harnessの入力・期待結果・失敗条件をDesignとして定義する。
- [x] stable ID SCN-0018を付与し、Acceptance Scenario正本へ反映する。
- [x] Cognitive Method、Decision、Capability / Provider、residual / reopenを一続きにtraceするExecutable harnessをISSUE-000050へ分離する。
- [x] Executable / Release / Operational / Adoption・Outcome EvidenceをDesign完了と同一視しない境界を明示する。
- [x] 今回追加・更新した文書を自然な日本語へ全文再ドラフトし、最終意味監査を行う。

## Evidence state

- Design Evidence: Satisfied — Requirement composition、主要variant、期待・失敗条件を確定し、SCN-0018として正本化した。
- Executable Evidence: Not Yet Verified by this Issue — 後続ISSUE-000050で検証する。
- Release Evidence: Not Yet Verified
- Operational Evidence: Not Yet Verified
- Adoption / Outcome Evidence: Not Yet Verified

## Reopen条件

次のいずれかが確認された場合は、本Issueまたは新しいDesign Issueとして再検討する。

- SCN-0018を実装するために、既存REQでは表現できない独立した規範が必要になった。
- Journey manifestやUI都合をsemantic Coreへ昇格させなければ成立しないことが判明した。
- external execution後Observationとhistorical Decision basisの時間境界が、現行Scenarioでは不十分だった。
- no-execution / provider replacement / collaborative pathのいずれかが、現行Scenarioでは意味を保持できなかった。

## Natural Japanese review

Product Shape、REQ-0001〜0022、SCN-0001〜0018、`PRODUCT_JOURNEY_COMPOSITION.md`、Cognitive Method / Decision / Capability / Providerのcurrent境界へ戻り、本Issueの責務を「新しいUniversal ontologyを作ること」ではなく「既存の意味境界を一つのProduct Journeyで検査できるAcceptanceとして正本化すること」に絞り直した。SCN-0018とISSUE-000050への分離によってDesignとExecutable Evidenceを明確に分け、意味、規範強度、非対象範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
