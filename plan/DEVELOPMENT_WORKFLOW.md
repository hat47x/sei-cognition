# SOZA 開発ワークフロー

更新日: 2026-09-01  
状態: **Accepted Development Convention**

## 1. 目的

この文書は、SOZAの開発をどのbranchで進め、どの順序で設計・文書化・実装・検証するかを定めます。

開発速度だけを優先して実装を先行させるのではなく、Product Valueと設計判断を先に明確にし、後から「なぜこの実装になったのか」を追える状態を維持します。

## 2. Branch運用

安定した基線は`main`で管理します。通常の開発は次の形式のbranchで進めます。

```text
develop/vX.Y.Z
```

例:

```text
develop/v0.1.0
develop/v0.2.0
develop/v1.0.0
```

原則として開発中の変更を`main`へ直接積み上げません。まとまりのよい単位まで`develop/vX.Y.Z`で整備し、文書・検査・Evidenceが揃った段階で`main`へ統合します。

緊急修正など別のbranch種別が必要になった場合は、その必要性と運用方法を先に`plan/`へ記録します。

## 3. 優先順位

開発作業は原則として次の順序を優先します。

1. `product/value`、`product/vision`、`product/principles`
2. `plan/adr`、`plan/issue`、`plan/registry.yaml`
3. `requirements`
4. `architecture`、`contracts`
5. runtime、Provider Adapter、fixture、test、tool
6. Release Evidence
7. Operational Evidence
8. Adoption / Outcome Evidence

上位文書を毎回大量に書くという意味ではありません。実装へ進む前に、上位の意味と判断が十分に定まっているかを確認するための優先順位です。

## 4. 一つの開発単位で行うこと

一つの課題を進めるときは、必要な範囲で次を行います。

1. Product Value / Principleとの関係を確認する。
2. 未決論点であればIssueを作成・更新する。
3. 設計判断が必要であればADRを作成・更新する。
4. Requirement / Acceptance Scenarioへ影響する場合は先に反映する。
5. Architecture / Contractを整える。
6. 実装する。
7. fixture / test / conformanceで確認する。
8. 実際に得られた高さまでEvidenceと未完了事項を更新する。
9. 文書を自然な日本語へ全文再ドラフトする。
10. 意味・仕様・留保・Evidence強度が変わっていないか最終監査する。
11. current Markdown文書を追加・更新した場合は、`plan/document_review_registry.yaml`へ監査状態を反映する。
12. 対象CIがsuccessしていることを確認する。

CI failureが出た場合は、12だけを最後まで先送りしません。**失敗を検出した時点で原因を解消し、successを確認してから後続作業へ進みます。**

## 5. 文書品質を後処理にしない

自然な日本語への再ドラフトは、release直前にまとめて行う後処理ではありません。

新しく作成・更新した開発文書は、その作業単位を閉じる前に`plan/DOCUMENT_AUTHORING_STANDARD.md`の工程を通します。

既存文書はISSUE-000015で全件監査し、`plan/document_review_registry.yaml`へ監査状態を記録しました。以後、新しいcurrent Markdown文書は通常の作業単位の中で監査状態まで反映します。

`Plan integrity`はMarkdown変更でも起動し、Document Review Registryのcoverageと`pending`の有無を検査します。新規文書を追加したのに監査台帳へ登録していない変更は、原則としてmerge前に検出されます。

ただし、このCIは自然な日本語の品質や文書の意味を自動判定しません。機械的なcoverage検査と、全文再ドラフト・最終意味監査は別の責務です。

## 6. Evidenceを超える状態更新をしない

Product Value Acceptanceでは次の5段階を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

たとえば、設計が完了したこと、actual repositoryでCIが通ったこと、release Artifactが成立したこと、本番で安定して動作したこと、利用者・組織へ価値が届いたことは、それぞれ別の主張です。

Issue、Requirement、README等の状態は、実際に確認できた高さまでだけ更新します。

## 7. 実装順序を製品ontologyにしない

`M48`、`M49`、`M50`等はhistoricalな開発Milestoneです。

その順序を利用者の業務workflowやSOZAのUniversal ontologyとして固定しません。Milestoneをまたいで意味上の前提が変わった場合は、旧実装を守ることよりProduct Value / Requirement / ADRへ戻って再検討することを優先します。

## 8. Planning変更は可能な範囲でatomicにする

ADR / Issue本文のStatus、`plan/registry.yaml`、関連文書を同時に変更する必要がある場合は、可能な範囲で一つのatomic commitへまとめます。

同様に、新しいcurrent Markdown文書を追加した場合は、可能な範囲で`plan/document_review_registry.yaml`への監査状態反映も同じ変更単位へ含めます。

これは履歴を細かくしないためではなく、途中commitだけを見たCIが「本文はResolvedだがregistryはIn Progress」「新規Markdownがあるが監査台帳にない」といった一時的不整合を検出することを避けるためです。

分割commitが必要な場合は、各commit単体でもPlan integrityが成立する順序を選びます。

## 9. CI failureの扱い

CI failureは次の設計入力でもあります。

1. 失敗したworkflow / step / fixtureを確認する。
2. Contract、fixture、runtime、tool、文書台帳のどの層の問題かを切り分ける。
3. current Product Value / Contractを安易に弱めず、誤っている層を修正する。
4. 同じCIを再実行し、successを確認する。
5. 必要ならIssue / Evidence文書へ原因と修正内容を残す。
6. その後に次の作業へ進む。

Document Review Registry coverage failureの場合も、文書をcheckerへ無理に合わせるのではなく、未登録なのか、監査未完了なのか、checkerの責務が誤っているのかを切り分けます。

## 10. Natural Japanese review

current Product Value、5段階Evidence、actual CI運用、Document Review Registry coverage gate、ISSUE-000015の全件監査へ戻ってworkflowを再確認した。その後、branch方針、開発順序、Evidence境界を変えず、文書監査状態の反映を通常の開発単位へ組み込む形で、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
