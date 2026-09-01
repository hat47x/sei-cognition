# ISSUE-000042: Document Review Registryのcoverageを自動検査する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **—**  
Updated: 2026-09-01

## 目的

`plan/document_review_registry.yaml`で確立した自然な日本語監査の完了状態を、今後の文書追加でも取りこぼさないようにする。

actual treeへ新しいMarkdown開発文書が追加されたとき、その文書がreviewed scopeへ含まれていない、または監査が`pending`のまま残っている状態をCIで検出できるようにする。

## 背景

ISSUE-000015ではcurrent Markdown開発文書の全件監査を完了し、`document_review_registry.yaml`を監査台帳として確立した。

一方、現行の`Plan integrity`はADR / Issue / `plan/registry.yaml`の構造整合を検査するが、Document Review Registryのcoverageは自動検査していない。そのため、将来新しいMarkdown文書を追加した際に、本文作成は完了していても監査台帳への反映だけが漏れる可能性がある。

これはProduct Value、Requirement、Architecture、Contract、Runtimeの意味やEvidenceを変更する課題ではなく、文書品質運用の機械的な抜けを閉じる課題である。

## 必要な作業

1. 外部YAMLライブラリへ依存しない`check_document_review_registry.py`を追加する。
2. actual treeのMarkdown文書がreviewed scopeでcoveredされていることを検査する。
3. `pending: []`でない場合は失敗する。
4. checker自身のpositive / negative self-testを追加する。
5. `Plan integrity`を、Markdown文書が変更されたPR / develop pushでも起動するようにする。
6. `plan/scripts/README.md`へ保証範囲と非保証範囲を記載する。
7. current actual treeに既存のcoverage漏れがあれば、意味を変更せずregistryへ回収する。

## Constraints

- 文書の意味、仕様、要求強度、Evidence強度をcheckerが評価しない。
- `reviewed-no-change`を不合格にしない。原記録保全を尊重する。
- historical資料をcurrent結論へ合わせて改稿しない。
- Product / Requirements / Architecture / Contracts / Runtime本文を、このIssueのために変更しない。
- CI PASSをRelease / Operational / Adoption / Outcome Evidenceへ昇格しない。

## 完了条件

- [ ] Document Review Registry coverage checkerがactual treeでPASSする。
- [ ] 未登録Markdownを追加したnegative self-testがFAILする。
- [ ] `pending`を残したnegative self-testがFAILする。
- [ ] Plan integrityからcheckerとself-testが実行される。
- [ ] current actual treeのMarkdown coverage漏れがゼロである。
- [ ] checkerの責務とEvidence境界が`plan/scripts/README.md`に明記される。

## Natural Japanese review

ISSUE-000015、`plan/document_review_registry.yaml`、既存Plan integrityの責務を確認し、Product / Runtime側と作業が重複しない管理課題として範囲を限定した。その後、意味やEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施している。
