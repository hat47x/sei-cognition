# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## 目的

SOZAの既存開発文書を、技術的な意味・仕様・留保・Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この作業は一度限りの文章校正ではありません。新規・更新文書でも同じ工程を必須とし、継続的な品質ゲートとして扱います。

## 必須工程

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architecture、Contract、actual Evidenceとの整合を確認する。
3. 古い議論、破棄済み前提、古いEvidence記述が残っていないか確認する。
4. 技術的な矛盾、重複、不足を修正する。
5. 意味、仕様、留保、Evidence強度をいったん固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトで要求強度、条件、例外、Evidenceの高さが変わっていないか最終監査する。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を正とする。

## Evidenceの現在基準

Product Value Acceptanceに従い、少なくとも次を区別する。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

旧文書が4段階を前提としている場合も、現在の5段階へ同期する。ただし、Adoption / Outcome Evidenceがまだ存在しないことを理由に、過去の下位Evidenceを弱めたり強めたりしない。

## 監査管理

`plan/document_review_registry.yaml`を監査台帳とする。

台帳は意味上の正本ではなく、current Markdown開発文書の対象範囲と進捗を漏れなく管理するための補助資料である。

状態:

- `revised`
- `reviewed-no-change`
- `excluded-historical`
- `pending`

新規文書は作業単位の中で本標準を完了できる場合、直接`revised`または`reviewed-no-change`へ登録する。

## 完了済み範囲

### Product層

Product Value、Value Model、Value Acceptance、Value Traceability、Vision、Principles、Product READMEをcurrent上位baselineへ整合済み。

### ADR

ADR-0001〜ADR-0024をcurrent Product Value / Requirements / Architecture / Contract / Runtimeから逆向きに監査済み。

historical M48 / M49 / M50参照、Representation Profile確定前の表現、後続Executable Evidenceとの時系列差を整理した。Decision自体を後続実装都合で変更していない。

### Issue

ISSUE-000001〜ISSUE-000036をcurrent Evidenceへ戻って全件監査済み。

特に000005、000008〜000014、000020、000024、000026、000029〜000033、000035について、historical Milestone、自身のclosure、後続Executable Evidenceを分離し直した。

### Planning品質文書

次をcurrent 5段階Evidenceと文書監査台帳へ同期した。

- `plan/README.md`
- `plan/DEVELOPMENT_WORKFLOW.md`
- `plan/DOCUMENT_AUTHORING_STANDARD.md`
- `plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`
- `plan/scripts/README.md`

## 未完了範囲

`plan/document_review_registry.yaml`で`pending`となっているcurrent文書を上位から順に監査する。

優先順:

1. Requirements補助文書
2. Architecture
3. Contracts / Representation Profiles / Evidence
4. Runtime Evidence
5. fixture README
6. KJ統合文書
7. ADR / Issue Template

historical M47 digest Profile recoveryはISSUE-000034の独立Blocked事項であり、この文書監査の完了条件へ混ぜない。

## CI運用

CI failureを検出した場合は、その時点で原因を特定・修正し、successを確認してから次の作業へ進む。

Plan本文と`plan/registry.yaml`を同時に変更する場合は可能な範囲でatomic commitとし、一時Status不整合を避ける。

## Acceptance criteria

- [x] 固定100倍基準をcurrent Product正本から除去し、10〜50×のmoving horizonへ統一した。
- [x] X-TEAをcurrent Product名として扱わない。
- [x] TEIをSOZA内部Runtimeと誤読させないProduct / Architecture境界を整備した。
- [x] 5段階Evidenceをcurrent上位文書とPlanning規約へ反映した。
- [x] REQ / SCNのcurrent正本とhistorical mappingを分離した。
- [x] Architecture concernとruntime componentを分離した。
- [x] Semantic ContractとRepresentation Profileを分離した。
- [x] Contract DefinitionとSchema / implementationの権威関係を分離した。
- [x] ADR-0001〜ADR-0024をcurrent baselineから全件再監査した。
- [x] ISSUE-000001〜ISSUE-000036をcurrent baselineから全件再監査した。
- [x] current文書の監査対象一覧を`plan/document_review_registry.yaml`へ実体化した。
- [ ] `document_review_registry.yaml`のcurrent対象から`pending`をなくす。

`pending`が残る間は本IssueをResolvedにしない。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としません。

原文自体がEvidenceとなる資料、machine-readable Schema、固定fixture、source code等を、日本語化のためだけに改変しません。

読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしません。

## Natural Japanese review

Product Value、ADR-0001〜0024、ISSUE-000001〜000036、5段階Evidence、current repository treeへ戻って監査範囲を再確定し、document review registryへ対象を固定した。その後、完了済み範囲とpending範囲、原文保存対象を混同せず、意味、監査条件、Evidence強度を変えないよう自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
