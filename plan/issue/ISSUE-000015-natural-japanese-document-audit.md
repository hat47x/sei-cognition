# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## Goal

SOZAの既存開発文書を、技術的意味・仕様・留保を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この工程を一度限りの文章校正ではなく、今後の文書作成に必須の品質ゲートとして定着させる。

## Background

これまでの開発文書には、設計検討を高速に進めた結果として次の特徴が残っている。

- 日本語の中に英語の名詞句が過度に混在する。
- 生成AI向けの短いメモ表現が正式文書へ残る。
- 名詞を連結しただけで述語が弱い箇所がある。
- 同じ概念が日本語と英語で揺れる。
- 境界式だけがあり、本文の自然な説明が不足する箇所がある。
- 技術的には正しいが、初見の読み手が論理関係を追いにくい箇所がある。

文書の意味密度は維持しつつ、読み手が設計判断を正確に追える文章へ整える必要がある。

## Required workflow

各文書について次を順番に実施する。

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architectureとの整合を確認する。
3. 古い議論が残っていないかを確認する。
4. 技術的な矛盾・重複・不足を修正する。
5. 意味・仕様・留保を固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトによって意味の強度、条件、例外が変わっていないかを最終監査する。

第6工程を省略しない。

## Priority order

### P0

- `product/value/`
- `product/vision/`
- `product/principles/`
- `plan/README.md`

### P1

- `plan/adr/`
- `plan/issue/`
- `plan/registry.yaml`

### P2

- `requirements/`
- `architecture/`
- `contracts/`

### P3

- `plan/rebaseline/`
- repository README
- 補助・移行・監査文書

## Acceptance criteria

- Product上位3文書が最新議論と整合している。
- ADR / Issueの全実ファイルがregistryと一致する。
- ADR / Issueの本文が自然な日本語監査済みである。
- 文書内に過去の固定100倍基準が正本として残っていない。
- X-TEAが現行Product名として残っていない。
- TEIをSOZAの内部Runtimeと誤読させる記述がない。
- `Recommendation != Decision != Authority != Execution`等の重要境界は、式だけでなく自然な日本語でも説明されている。
- `design-only`、`planning pass`、`local evidence`等を実装済み・運用実績と誤読させない。
- 再ドラフト後に技術的意味の差分監査を行っている。

## Current progress

2026-08-31時点で次を新しい工程へ通した。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `plan/README.md`
- `plan/adr/ADR-0013-capability-realization-boundary.md`
- `plan/issue/ISSUE-000014-investigate-capability-realization-offering-boundary.md`
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`

既存ADR-0001〜0012、ISSUE-000001〜000013は引き続き対象とする。

## Non-goals

- 技術用語をすべて日本語へ翻訳すること
- 短い境界式を禁止すること
- 文書を入門記事のように薄くすること
- 読みやすさのために未決事項を勝手に確定すること
- 仕様の精度より文章の滑らかさを優先すること

自然な日本語と技術的精度を両立させる。
