# SOZA 開発ワークフロー

更新日: 2026-08-31  
状態: **Accepted Development Convention**

## 1. 目的

この文書は、SOZAの開発をどのbranchで進め、どの順序で設計・文書化・実装・検証するかを定めます。

開発速度だけを優先して実装を先行させるのではなく、Product Valueと設計判断を先に明確にし、後から「なぜこの実装になったのか」を追える状態を維持することを目的とします。

## 2. Branch運用

安定した基線は`main`で管理します。通常の開発は、次の形式のbranchで行います。

```text
develop/vX.Y.Z
```

例:

```text
develop/v0.1.0
develop/v0.2.0
develop/v1.0.0
```

原則として、開発中の変更を`main`へ直接積み上げません。まとまりのよい単位まで`develop/vX.Y.Z`で整備し、文書・検査・Evidenceが揃った段階で`main`へ統合します。

緊急修正など別のbranch種別が必要になった場合は、その必要性と運用方法を先に`plan/`へ記録します。

## 3. 優先順位

開発作業は、原則として次の順序を優先します。

1. `product/value`、`product/vision`、`product/principles`
2. `plan/adr`、`plan/issue`、`plan/registry.yaml`
3. `requirements`
4. `architecture`、`contracts`
5. 実装、fixture、test、tool
6. release / operational evidence

これは、上位文書を毎回大量に書くという意味ではありません。実装へ進む前に、上位の意味と判断が十分に定まっているかを確認するための優先順位です。

## 4. 一つの開発単位で行うこと

一つの課題を進めるときは、必要な範囲で次を行います。

1. Product Value / Principleとの関係を確認する。
2. 未決論点であればIssueを作成・更新する。
3. 設計判断が必要であればADRを作成・更新する。
4. Requirement / Acceptance Scenarioへ影響する場合は先に反映する。
5. Architecture / Contractを整える。
6. 実装する。
7. fixture / test / conformanceで確認する。
8. Evidenceと未完了事項を更新する。
9. 文書を自然な日本語へドラフトし直す。
10. 最終的に、意味・仕様・留保が変わっていないか確認する。

## 5. 文書品質を実装後の後処理にしない

自然な日本語へのドラフト工程は、リリース直前だけにまとめて行う後処理ではありません。

新しく作成・更新した開発文書は、その作業単位を閉じる前に`plan/DOCUMENT_AUTHORING_STANDARD.md`の工程を通します。

既存文書については`ISSUE-000015`で全件監査を進め、監査状態を`plan/document_review_registry.yaml`へ記録します。

## 6. Evidenceを超える状態更新をしない

次を区別します。

```text
設計が完了した
!=
ローカル実装が存在する
!=
実repositoryで統合された
!=
release gateを通過した
!=
運用実績がある
```

IssueやEvidenceのStatusは、実際に確認できた範囲だけを反映します。

## 7. 実装順序を製品ontologyにしない

`M48`、`M49`、`M50`等は開発上のMilestoneです。

その順序を利用者の業務workflowや、SOZAのUniversal ontologyとして固定しません。Milestoneを跨いで意味上の前提が変わった場合は、実装を守るよりProduct / Requirement / ADRへ戻って再検討します。
