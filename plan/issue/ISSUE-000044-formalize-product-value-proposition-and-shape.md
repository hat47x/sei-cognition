# ISSUE-000044: 利用者向けValue PropositionとProduct Shapeを明文化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

SEIのsemantic boundaryだけでなく、製品として誰のどの問題を解き、どの一連の仕事を支え、何をSEIの外へ委ねるかを上位Product文書で明確にする。

既存のProduct Value / V1〜V8を変更したり、新しいUniversal Core概念を増やしたりせず、現在の意味設計を利用者視点のValue PropositionとProduct Shapeへ接続する。

## 背景

current Product Value、Vision、Requirements、Architecture、Contractは、SEIが長期に守る意味境界をかなり具体化している。

一方、actual repositoryを製品として読むと、次は相対的に明示が弱かった。

- 主にどのような判断仕事で価値を出すか。
- 利用者・AI・外部Providerがどのように関わるか。
- 問いからDecision、外部実行、再検討までをどのような仕事として支えるか。
- UI / API / Integration / Projection等を、意味上どのようなSurfaceとして考えるか。
- SEI自身が所有しない実行・Identity・Storage等をどこへ置くか。
- 最初のusable productとして最低限何が一続きに成立すべきか。

この曖昧さを残すと、RuntimeやContractの実装が進んでも「何を完成させれば製品になるのか」が見えにくい。

## 実施内容

### 1. Value Proposition

`product/value/SEI_VALUE_PROPOSITION.md`を新設した。

利用者から見た主な価値を次へ整理した。

- 後から判断へ戻れる。
- Unknown / Conflictを消さずに前へ進める。
- AIへ広く委ねてもRecommendation / Decision等を混同しない。
- ProviderやRealizationを交換しても判断の意味を持ち運べる。
- 軽く始め、必要な場面だけ詳細化できる。

また、SEIの価値が大きくなりやすい場面と、SEIを第一選択にしなくてもよい場面を明示した。

### 2. Product Shape

`product/definition/SEI_PRODUCT_SHAPE.md`を新設した。

次をProduct Shapeとして整理した。

- 主要な仕事: Inquiry開始 / Observation・Evidence / Method Application / Recommendation / Decision / external execution / resulting Observation / historical review
- 論理Surface: Work / Interaction、Canonical Semantic Access、Integration、Projection / Review、Evidence / Governance
- SEIが所有する意味と、原則として外部へ委ねる機能
- Minimum Usable Product Shape
- Interaction、Packaging、Identity / Authorization、golden journey、非機能要件という未決境界

## Constraints

- Value Axis V1〜V8を変更しない。
- Product Shapeの説明から新しいUniversal Core recordを自動追加しない。
- Work journeyを固定workflow ontologyとして採用しない。
- UI / API / MCP / Storage / deployment技術を本Issueで確定しない。
- 個別RuntimeのExecutable Evidenceをend-to-end Product Evidenceへ昇格しない。

## 完了条件

- [x] 利用者から見たValue PropositionをProduct文書として明文化する。
- [x] Product内外境界と主要な仕事をProduct Shapeとして明文化する。
- [x] Minimum Usable Product Shapeを定義する。
- [x] 未決の製品仕様を後続Issueへ分離する。
- [x] 新しいValue Axis / Universal Coreを不用意に追加しない。
- [x] 文書を自然な日本語へ全文再ドラフトし、最終意味監査を行う。

## Evidence

- Design Evidence: Satisfied for the product-definition scope of this Issue
- Executable Evidence: Not Yet Verified as an end-to-end product
- Release Evidence: Not Yet Verified
- Operational Evidence: Not Yet Verified
- Adoption / Outcome Evidence: Not Yet Verified

本IssueのResolvedは、Product ShapeをDesign baselineとして確立したことを意味する。Minimum Usable Product Shapeが実装・release・実利用で成立したことを意味しない。

## Follow-up

- ISSUE-000045 — first usable Product Interaction boundary
- ISSUE-000046 — v0.2.0 Packaging / Deployment boundary
- ISSUE-000047 — Identity / Authorization / Collaboration boundary
- ISSUE-000048 — end-to-end golden journeyとRequirement / Scenario再整理

## Reopen conditions

次の場合は再開を検討する。

- 実利用調査により、想定した利用者問題と価値提案が大きく外れていることが分かる。
- Product Surface間の責務が実装上成立せず、上位のProduct Shape自体を変える必要がある。
- SEIが外部委譲するとした領域をCoreとして所有しなければProduct Valueを満たせないEvidenceが得られる。

## Natural Japanese review

current Product Value、Vision、REQ / SCN、ADR-0014 / 0018 / 0020 / 0021、current Contract / RuntimeのEvidenceへ戻り、semantic designを利用者視点と製品外形へ接続する課題として整理した。新しいCore概念を追加せず、未決仕様は後続Issueへ分離したうえで、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
