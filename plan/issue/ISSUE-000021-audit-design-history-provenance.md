# ISSUE-000021: 7チャットの設計史provenanceを原文と再照合する

Status: **Deferred**  
Priority: **6**  
Related ADRs: **ADR-0014**  
Updated: 2026-08-31

## Goal

「渡辺幸三の業務システム設計」から「渡辺幸三の業務システム設計７」までの設計史について、将来チャットexport等の逐語原文を利用できる場合に、現在のKJ統合と正本文書を原文へ戻して再照合する。

## Background

2026-08-31のラウンドKJ統合では、過去会話から回収できた判断要約、後続の統合資料、現行TEI実装を突き合わせた。

主要な設計境界は複数の独立資料と実装から補強できる一方、現在の作業環境では指定7チャットの全文を一括して逐語取得できない箇所がある。

この制約のために現在の設計判断を止める必要はないが、historical provenanceを完全な形で保存する余地は残る。

## Current disposition

**Deferred**とする。

現行Product / ADR / Issueは、最新議論とactual implementationを優先して整備する。

将来、チャット原文を機械的に取得できるEvidenceが得られた場合にのみ再開する。

## Reopen conditions

- 7チャットのexportまたは全文Artifactが取得できる。
- chat message単位のtimestamp / provenanceを追跡できる。
- 現在のKJカードと原文を自動または半自動で対応付けられる。

## Required audit

再開時には、少なくとも次を確認する。

1. 現在のカードに原文にない一般化がないか。
2. 後発議論で破棄された案が正本へ残っていないか。
3. 重要な少数意見・例外・保留を核融合で失っていないか。
4. どの設計判断がどのチャットで初出・更新・確定したか。
5. X-TEA → TEI、Driver再定義、Application / Database独立、認証・認可、AI質問履歴等の更新線を逐語的に確認できるか。

## Non-goals

- 現行設計を古い議論へ巻き戻すこと
- 原文の量を正しさの指標にすること
- すべての会話断片をProduct文書へ転載すること

## Source

`plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md` のG08を起点とする。

## Natural Japanese review

Issue作成後に自然な日本語の全文ドラフト工程を実施済み。再開時には原文照合後に再度実施する。
