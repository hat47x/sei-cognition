# ISSUE-000022: SOZA repositoryの基線ファイルを実体化し、Evidence claimを再整合する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`に、READMEや過去candidate bundleが参照するProduct / Requirements / Architecture / Contracts / Fixtures / Runtime / Tools等を、現在のProduct Boundaryへ合わせて実体化する。

同時に、「Library上に候補実装が存在すること」と「GitHub repositoryに実装・検査資産が入っていること」を区別し、Evidence claimを現在の実体へ合わせる。

## Background

`soza` repository自体は利用可能になったが、初期`main` commitはREADME中心であり、READMEが列挙する旧Phase 1 candidateの多数のファイルがrepository内にまだ存在しない。

一方、Libraryには過去candidate bundle、runtime、fixtures、generated summaries等のEvidenceが残っている。

この状態でREADMEの記述だけを根拠に「actual repositoryでGo実装・full gatesが成立している」と扱うと、Evidenceの所在を混同する。

## Required work

1. Product / plan文書を最新基線へ整備する。
2. Requirements / Acceptance Scenariosを自然な日本語監査後にrepositoryへ入れる。
3. Architecture / Contractsを最新ADRへ照合してから入れる。
4. Libraryのruntime / fixtures / toolsを、現在のProduct Boundaryと衝突しないか監査する。
5. 歴史的M47 sourceがrepoに存在しないことを明示する。
6. Go module、package、schema、fixtures、test toolを実体化した後にのみactual-repo gateを実行する。
7. Library candidateのPASSとGitHub actual repositoryのPASSを別Evidence namespaceで記録する。
8. READMEの「現在地」をactual treeへ一致させる。

## Constraints

- Library candidateのPASSをactual repository PASSへ自動継承しない。
- 存在しないM47 regressionをPASS扱いしない。
- READMEの記述を実装存在のEvidenceとしない。
- 旧bundleを無検査で一括コピーしない。
- TEI実装をSOZA実装の代替Evidenceにしない。
- 文書・コードとも、最新ADRとSOZA↔TEI Product Boundaryを優先する。

## Completion criteria

- READMEで参照する必須ファイルがactual treeに存在する。
- actual repository上で実行可能なgateだけを列挙できる。
- actual repo evidenceとhistorical/local candidate evidenceが明確に分離される。
- ISSUE-000009の残件をactual treeで検証できる入口ができる。
- M49 / M50 production implementationを開始できるかを改めて判断できる。

## Natural Japanese review

repo実体と旧candidate claimを照合した後、自然な日本語となることを最重要視して全文を作成し、意味監査を実施済み。
