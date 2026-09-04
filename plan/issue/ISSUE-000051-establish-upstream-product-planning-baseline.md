# ISSUE-000051: 上流Product Planning baselineを整備する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0001, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

SOZAの開発で、Product Value、期限を持たないProduct Milestone、未定領域の探索、Requirement化、Architecture / Implementationの順序を明確にし、上流文書をcurrent repositoryの正本として整備する。

特に、まだ意味境界が十分に分かっていない領域を、実装都合だけでRequirementへ早期固定しない運用を明文化する。

## Background

SOZAはProduct Value / Value Model / Product Shapeと、SCN-0018のend-to-end Product Journeyまで具体化し、fixture-scoped Executable Evidenceも得ている。

一方、first usable Interaction、Packaging / Deployment、Identity / Authorization / Collaboration、実Realization / Providerをまたぐportability等は、まだ議論・実証を通して要件を精緻化する余地が大きい。

historical M48 / M49等の実装Milestoneだけでは、製品として次に何を成立させるかを十分に表せないため、期限ではなくOutcomeとEvidenceを基準にしたProduct Milestoneが必要になった。

## Resolution

次をcurrent baselineとして整備した。

1. `product/roadmap/SOZA_PRODUCT_MILESTONES.md`を追加し、Product ValueからOperational / Adoption Outcomeまでの製品成立段階を、期限なしのOutcome / Evidence基準で定義した。
2. `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`を追加し、Open Question → discussion / research / experiment → Candidate Requirement → stable Requirementの標準フローを定義した。
3. Milestoneの箇条書きをそのままRequirementへ変換しないことを明示した。
4. チャット上の議論は探索・統合に利用できるが、current正本はrepository文書へ戻すことを明示した。
5. synthetic / fixture-scoped Evidenceと、Release / Operational / Adoption Outcomeを混同しない既存の5段階Evidence境界を維持した。
6. current Product / Plan入口、Product Principles、Development Workflowへこの上流Planning baselineを接続した。

## Requirement policy

未定領域は次の三状態を区別する。

```text
Open Question
  → Candidate Requirement
  → Stable Requirement
```

Open Questionから直接stable REQ IDを作らない。

stable Requirementへ昇格する前に、少なくともProduct Valueとの関係、具体Scenario、既存REQとの重複、将来耐性、配置層、観測可能なAcceptanceを監査する。

調査の結果、既存Requirementで十分、または新Requirement不要と判断することも正当な完了とする。

## Current exploration priorities

- ISSUE-000045 — first usable Product Interaction
- ISSUE-000046 — Packaging / Deployment
- ISSUE-000047 — Product Identity / Authorization / Collaboration
- ISSUE-000049 — cross-contract exact binding consistency
- real Cognitive Method / Provider portability
- Operational / Adoption Outcomeの評価方法

## Non-goals

- calendar deadlineの設定
- release日程の確定
- 未定のUI / protocol / Storage / IdPの先行選定
- historical Milestone番号をProduct ontologyへ変換すること
- Product Milestoneから新しいUniversal Requirementを自動生成すること

## Acceptance criteria

- [x] Product Milestoneを期限なしの成立条件として正本化する。
- [x] 未定領域を議論・実証後にRequirement化する手順を正本化する。
- [x] Product文書とPlan文書の入口から新baselineへ辿れるようにする。
- [x] Development Workflowへ上流優先とRequirement化gateを反映する。
- [x] Product Principlesへ「仮説・実証・Requirementを分離する」原則を反映する。
- [x] `plan/registry.yaml`とDocument Review Registryを同期する。
- [x] 新規・更新文書を自然な日本語へ全文再ドラフトし、最終意味監査を行う。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Not applicable to the planning convention itself**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

このIssueのResolvedは、上流Planningの文書・運用境界が正本化されたことだけを意味する。Product Interaction、Packaging、Collaboration等の個別Product Milestone達成を意味しない。

## Reopen conditions

- Product Milestoneが実際の開発判断に使えず、期限のない順序だけの一覧へ形骸化した。
- Candidate RequirementとStable Requirementの境界が不十分で、未定事項が再び早期固定されるようになった。
- Product Value / Milestone / Requirementのauthority関係に矛盾が見つかった。
- 実利用Evidenceから、現行Milestone構造ではProduct Valueの到達段階を表せないことが分かった。

## Natural Japanese review

Product Value、Value Proposition、Product Shape、Product Principles、current Requirements、SCN-0018、ISSUE-000045〜000050へ戻り、今回の作業を「新しい実装計画」ではなく、Product Milestoneと未定領域のRequirement化手順を上位から整えるPlanning課題として整理した。期限や未検証の実装選択を持ち込まず、意味、規範強度、Evidence境界を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。