# ISSUE-000045: first usable Product Interaction boundaryを定義する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

`SOZA_PRODUCT_SHAPE.md`で定めたWork / Interaction Surfaceについて、最初に利用可能な製品として**人間とAIがどの入口から同じcanonical meaningへ触れ、どの操作を一続きに行える必要があるか**を定義する。

UI frameworkやprotocolを先に選ぶのではなく、Product Value / Requirement / Acceptance ScenarioからInteraction boundaryを決める。

## 検討対象

少なくとも次を整理する。

### 人間向け入口

- 最初に作成・再開できる単位は何か。
- Inquiry / Decision contextをどの程度の入力から開始できるか。
- Observation、Unknown、Conflict、Recommendation、Decision、residualをどの順序・粒度で扱える必要があるか。
- light viewからaudit detailへどう降りるか。

### AI向け入口

- AIがcanonical contextを取得・更新するために必要な最小操作は何か。
- AI向けSurfaceをprivate chain-of-thought保存と混同しないための境界は何か。
- AIによるRecommendation / Decision / Method Application等をどのように明示するか。

### Human / AI parity

- 人間向け表示だけ、またはAI向けPromptだけに意味が閉じ込められないこと。
- 両者が同じcanonical recordへ戻れること。
- Projectionの簡略化がcanonical meaningの削除にならないこと。

### interaction protocol候補

Web UI、desktop UI、CLI、HTTP API、MCP等は候補として比較するが、このIssue開始時点では採用済みとしない。

## Requirement候補

stable REQ IDを付与する前に、既存REQとの重複を監査する。

特に次を確認する。

- REQ-0010 — Progressive Semantic Explicitness
- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0019 — 人間とAIの双方が意味を読める
- REQ-0020 — Evidenceを超える達成主張をしない

既存Requirementで十分なら新しいREQを作らない。製品Interactionとして追加の意味差が必要な場合だけ起票・採番する。

## Acceptance検討

少なくとも次のScenarioを具体化する。

1. 人間が低影響なInquiryを最小入力で開始し、後から詳細化する。
2. AIが同じInquiryへObservation / Recommendationを追加し、人間がcanonical basisへ戻って確認する。
3. light Projectionでは主要点だけを見せ、audit Projectionではbasis / provenance / responsibilityを読める。
4. Projectionだけを保存してcanonical sourceを失う実装を拒否する。
5. AI向けSurfaceがhidden reasoning transcriptを必須にしない。

## Non-goals

- UIデザイン完成
- frontend framework選定
- 認証方式確定
- production SLA確定
- workflow engine実装
- AI agent orchestration engine実装

## 完了条件

- [ ] Product Interactionの必須操作を利用者の仕事単位で定義する。
- [ ] human / AI / projection / canonical authorityの境界を定義する。
- [ ] 既存REQ / SCNとの重複監査を行う。
- [ ] 必要なREQ / SCNだけを追加・更新する。
- [ ] protocol / UI選択がarchitecture decisionを要する場合はADRを作成する。
- [ ] 最小interaction conformanceまたはprototypeのExecutable Evidence条件を定義する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Not Yet Verified for this Interaction boundary**
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product Shape、V6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0013へ戻り、UI技術選定ではなくhuman / AI双方が同じcanonical meaningへ触れるためのProduct Interaction課題として整理した。既存Requirementとの重複を避け、必要な意味差だけを後続設計へ落とす方針を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
