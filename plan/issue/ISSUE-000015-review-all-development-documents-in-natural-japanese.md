# ISSUE-000015: 既存の開発文書を自然な日本語で全面監査する

Status: **Resolved**  
Priority: **1**

## 背景

SOZAの文書は、Product Value、ADR、Requirement、Architecture、Contract、検証報告まで広がっています。設計内容は蓄積されている一方、作業過程で`actual`、`local`、`candidate`、`planning`等の英語断片や生成AI向けの短い表現が混在し、正式文書として読みづらい箇所があります。

文書を人間とAIの双方が長期的に参照する意味資産とするため、新規文書だけでなく既存の開発文書も`plan/DOCUMENT_AUTHORING_STANDARD.md`の工程へ通します。

## 目的

1. activeな開発文書をすべてレビュー対象として列挙する。
2. 意味・仕様・留保を変えず、必要な文書を自然な日本語へ改稿する。
3. 改稿不要と判断した文書も、レビュー済みであることを記録する。
4. 原文保存が必要なhistorical evidence / fixtureは、除外理由を明示する。
5. 未監査文書が残った状態で本IssueをResolvedにしない。

## 優先順位

1. Product Value / Vision / Principles
2. ADR / Issue / `plan`運用文書
3. Requirements
4. Architecture / Contracts
5. rebaseline report / README
6. その他の現行開発文書

## 完了条件

- `plan/document_review_registry.yaml`に対象文書がすべて登録されている。
- `pending`状態が0件である。
- `tools/check_document_review_registry.py`がPASSする。
- 新規・更新文書の必須工程が`plan/README.md`、`plan/DEVELOPMENT_WORKFLOW.md`、`plan/DOCUMENT_AUTHORING_STANDARD.md`に明文化されている。
- Product文書とADR / Issueは優先監査を完了している。
- 改稿によって意味・Status・Evidence強度を不当に変えていないことを確認している。

## 対象外

自然な日本語への改稿を理由に、historical evidenceの原文、固定fixture、外部原資料の内容そのものを書き換えることはしません。

## 結果

93文書をレビュー台帳へ登録し、`pending`を0件にしました。原文保存が必要な5資料を除き、すべて`revised`または`reviewed-no-change`として監査を完了しています。検査結果は`plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`にまとめています。
