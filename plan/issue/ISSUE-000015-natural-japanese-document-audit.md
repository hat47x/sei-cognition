# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## Goal

SOZAの既存開発文書を、技術的意味・仕様・留保を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この工程を一度限りの文章校正ではなく、今後の文書作成に必須の品質ゲートとして定着させる。

## Required workflow

各文書について、次を順番に実施する。

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architectureとの整合を確認する。
3. 古い議論や破棄済みの前提が残っていないかを確認する。
4. 技術的な矛盾・重複・不足を修正する。
5. 意味・仕様・留保を固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトによって意味の強度、条件、例外が変わっていないかを最終監査する。

第6工程は省略しない。

## Audit priorities

1. `product/value`, `product/vision`, `product/principles`
2. `plan/adr`, `plan/issue`, `plan/registry.yaml`
3. `requirements`
4. `architecture`, `contracts`
5. `plan/rebaseline`等の報告・計画文書
6. repository README、補助文書

## Progress — 2026-08-31

完了:

- Product Value / Vision / Principles
- `plan/README.md`
- ADR-0001〜ADR-0014
- ISSUE-000001〜ISSUE-000014
- ISSUE-000016〜ISSUE-000022の新規・更新文書
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`

進行中:

- `plan/registry.yaml`の再基線化
- Requirements / Acceptance Scenarios
- Architecture / Contracts
- rebaseline reports / repository README

## Acceptance criteria

- 固定100倍基準が正本として残らない。
- X-TEAを現行Product名として扱わない。
- TEIをSOZA内部Runtimeと誤読させる記述を残さない。
- planning、design、local executable、actual repository、operational evidenceを区別する。
- 重要な`!=`境界は、式だけでなく自然な日本語でも意味を説明する。
- 再ドラフト後に技術的意味差分を監査する。

## Non-goals

技術用語をすべて日本語へ翻訳したり、読みやすさのために未決事項を勝手に確定したりしない。自然な日本語と技術的精度を両立させる。
