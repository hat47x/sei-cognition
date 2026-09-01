# ISSUE-000042: Document Review Registryのcoverageを自動検査する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **—**  
Updated: 2026-09-01

## 目的

`plan/document_review_registry.yaml`で確立した自然な日本語監査の完了状態を、今後の文書追加でも取りこぼさないようにする。

actual treeへ新しいMarkdown開発文書が追加されたとき、その文書がreviewed scopeへ含まれていない、または監査が`pending`のまま残っている状態をCIで検出できるようにする。

## 背景

ISSUE-000015ではcurrent Markdown開発文書の全件監査を完了し、`document_review_registry.yaml`を監査台帳として確立した。

一方、従来の`Plan integrity`はADR / Issue / `plan/registry.yaml`の構造整合を検査していたが、Document Review Registryのcoverageは自動検査していなかった。そのため、新しいMarkdown文書を追加した際に、本文作成は完了していても監査台帳への反映だけが漏れる可能性があった。

これはProduct Value、Requirement、Architecture、Contract、Runtime、Releaseの意味やEvidenceを変更する課題ではなく、文書品質運用の機械的な抜けを閉じる課題である。

## 実施内容

1. 外部YAMLライブラリへ依存しない`check_document_review_registry.py`を追加した。
2. actual treeのMarkdown文書がreviewed scopeまたは明示的なMarkdown exclusionでcoveredされていることを検査するようにした。
3. `pending: []`でない場合は失敗するようにした。
4. checker自身のpositive / negative self-testを追加した。
5. `Plan integrity`を、Markdown文書が変更されたPR / develop pushでも起動するようにした。
6. `plan/scripts/README.md`へ保証範囲と非保証範囲を記載した。
7. 並行作業で追加された`release/README.md`と`release/v0.1.0/RELEASE_ACCEPTANCE.md`は本文を変更せず、監査済みであることを確認して`reviewed-no-change`として台帳へ回収した。

## 検査境界

checkerは次を検査する。

- actual `*.md`がreviewed scopeまたは明示的なMarkdown exclusionへ含まれること
- `pending: []`であること
- reviewed / exclusion statusが規定値であること
- reviewed scopeがactual Markdownへ少なくとも1件一致すること
- reviewed scopeが重複していないこと

一方、文書の意味、仕様、要求強度、Evidence強度、自然な日本語の品質そのものは機械判定しない。

```text
Document Review Registry coverage PASS
  != document meaning correct
  != natural-language quality automatically proven
  != Product Value satisfied
  != Release ready
```

## Constraints

- 文書の意味、仕様、要求強度、Evidence強度をcheckerが評価しない。
- `reviewed-no-change`を不合格にしない。原記録保全を尊重する。
- historical資料をcurrent結論へ合わせて改稿しない。
- Product / Requirements / Architecture / Contracts / Runtime / Release本文を、このIssueのために変更しない。
- CI PASSをRelease / Operational / Adoption / Outcome Evidenceへ昇格しない。

## 完了条件

- [x] Document Review Registry coverage checkerがactual treeでPASSする。
- [x] 未登録Markdownを追加したnegative self-testがFAILする。
- [x] `pending`を残したnegative self-testがFAILする。
- [x] Plan integrityからcheckerとself-testが実行される。
- [x] current actual treeのMarkdown coverage漏れがゼロである。
- [x] checkerの責務とEvidence境界が`plan/scripts/README.md`に明記される。

## 実行Evidence

PR #7のhead `01fb16bd3a6f16097e5c8e80dd7a159d588d979d` に対して、Plan integrity #107（Run ID `33466037167`）が**success**した。

このrunではcheckerのcompile、self-test、既存Plan registry integrity、Document Review Registry coverage検査を同じcheckoutで実行している。

これはPlanning / 文書監査台帳のExecutable Evidenceであり、Product、Runtime、Release、Operational、Adoption / OutcomeのEvidenceへは昇格しない。

## Reopen conditions

次のいずれかが起きた場合は再開を検討する。

- actual Markdownが台帳から漏れていてもcheckerがPASSする。
- 正当な`reviewed-no-change`や原記録保全をcheckerが不当に拒否する。
- registry書式の正当な拡張によって現checkerが意味なく壊れる。
- 文書coverageと意味品質を混同する運用が再発する。

## Natural Japanese review

ISSUE-000015、`plan/document_review_registry.yaml`、既存Plan integrityの責務、actual CI結果を確認し、Product / Runtime / Release側と作業が重複しない管理課題として範囲を限定した。完了後、実施内容・保証範囲・非保証範囲・再開条件を整理し、意味やEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
