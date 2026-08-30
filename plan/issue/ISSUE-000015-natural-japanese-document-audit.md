# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## 目的

SOZAの既存開発文書を、技術的な意味・仕様・留保を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通します。

この作業は一度限りの文章校正ではありません。新規作成・更新する文書でも同じ工程を必須とし、SOZAの継続的な品質ゲートとして定着させます。

## 必須工程

開発文書は、原則として次の順序で確認します。

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architectureとの整合を確認する。
3. 古い議論や破棄済みの前提が残っていないか確認する。
4. 技術的な矛盾、重複、不足を修正する。
5. 技術的な意味、仕様、留保をいったん固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトによって意味の強度、条件、例外、Evidenceの強さが変わっていないか最終監査する。

第6工程は省略しません。詳細な基準は`plan/DOCUMENT_AUTHORING_STANDARD.md`を正とします。

## 監査の優先順位

1. `product/value`、`product/vision`、`product/principles`
2. `plan/adr`、`plan/issue`、`plan/registry.yaml`
3. `requirements`
4. `architecture`、`contracts`
5. `plan/rebaseline`等の報告・計画文書
6. repository README、補助文書

## 現在の進捗 — 2026-08-31

### 1. 品質基盤

次を整備しました。

- `plan/DEVELOPMENT_WORKFLOW.md`
- `plan/DOCUMENT_AUTHORING_STANDARD.md`
- `plan/README.md`の文書作成工程
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`の文書品質原則
- `plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`の中間報告

`plan/README.md`には、内容・構造を確定した後に全文を自然な日本語で再ドラフトし、その後に最終意味監査を行う工程を組み込んでいます。

今後の通常開発は`develop/vX.Y.Z`形式のbranchで行い、Product文書とADR / Issueを実装より先に整備します。

### 2. Product層

現在の正本branchには次のProduct文書があります。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

ここまでに次を実施しました。

- Product Valueの存在理由と中核価値を再整理。
- Value Modelで価値の三層、価値衝突時の優先規則、Core昇格基準、V1〜V8、失敗条件を明示。
- Value AcceptanceでDesign / Executable / Release / Operational Evidenceを分離。
- Product Visionを具体的な型一覧から長期的な利用状態へ戻して再構成。
- Product Principlesへsimple view / canonical meaning、単一スコア化禁止、Product Value再基線化等を追加。
- 各文書について、内容確定後の自然な日本語全文再ドラフトと最終意味監査を実施。

Product層は主要baselineについて一巡しました。今後、Architecture / Contractから反証が得られた場合は必要箇所を再監査します。

### 3. Plan層

`plan/registry.yaml`には、ADR-0001〜ADR-0020、ISSUE-000001〜ISSUE-000027を登録しています。

今回までに特に次を進めました。

- ADR-0017をregistryへ正式登録し、ISSUE-000019をResolvedへ正規化。
- ADR-0018でProduct Valueの権威関係と評価境界を固定。
- ADR-0019でProvider-neutralなCapability Observation境界を固定。
- ADR-0020でRequirementsのstable ID、Value traceability、Requirement / Scenario / Test、status / Evidence境界を固定。
- ISSUE-000020をResolvedとし、Capability Observationの実装fixtureをISSUE-000024へ分離。
- ISSUE-000025をResolvedとし、Requirements規約をADR-0020へ固定。
- ISSUE-000026をResolvedとし、Requirements Design baselineを実体化。
- Requirements registryのExecutable checkerをISSUE-000027へ分離。
- ISSUE-000022をactual repositoryの実在状態に合わせて更新。

新規・大幅更新した文書は、すべて自然な日本語全文再ドラフト工程と最終意味監査を通しています。

ただし、ADR-0001〜ADR-0020およびISSUE-000001〜ISSUE-000027の**既存部分を含む全件監査が完了したとはまだ扱いません。** current Product Value / Requirementsとの逆向き照合を継続します。

### 4. Requirements層

current Requirements Design baselineをactual repositoryへ実体化しました。

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  history/
    HISTORICAL_REQUIREMENT_MAPPING.md
```

現在の正本:

- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017

historical candidateの`SOZA-PR-001`〜`018`、NFR 10件、`SOZA-AS-001`〜`008`は、件数や旧IDを保存することを目的とせず、意味核をcurrent Product Valueへ戻して統合・分離しました。

旧Evidence状態はcurrent baselineへ自動継承していません。

Requirements文書については、current / historical / evidenceの三層を整理した後、全文を自然な日本語で再ドラフトし、意味、要求強度、例外、Evidence状態が変わっていないことを確認しています。

RequirementsのDesign baselineは完了しましたが、Executable registry checkは未検証であり、ISSUE-000027で追跡します。

### 5. Architecture / Contracts層

current `architecture/`と`contracts/`は、actual repository上ではまだbaselineを実体化していません。

historical candidateはLibraryに存在しますが、現在のProduct Value、REQ-0001〜0022、ADR-0001〜0020へ再照合する前にcurrent正本としてコピーしません。

次の主要監査対象はこの層です。

### 6. 過去の初回監査について

M48〜M50のローカル候補を対象に実施した初回監査は、現在branchより古い文書集合を対象としていました。このため、その時点の文書数をrepository全体の完了判定には使用しません。

中間結果は`plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`へ残し、現在の正本branchを基準として監査を継続します。

## 進行中の作業

優先順は次のとおりです。

1. ADR / Issue既存文書のcurrent Product Value / REQとの逆向き整合監査。
2. Architecture / Contracts baselineの構造・正本・追跡規約の整備。
3. historical Architecture / Contract candidateのcurrent baselineへの再評価。
4. Requirements registry checker（ISSUE-000027）。
5. Capability Observation fixture（ISSUE-000024）。
6. rebaseline reports / repository READMEのactual stateへの更新。
7. Runtime / Fixtures / Tools実体化後の自然な日本語説明監査。

## Acceptance criteria

- 固定100倍基準が現行の正本文書に残らない。
- X-TEAを現行Product名として扱わない。
- TEIをSOZA内部Runtimeと誤読させる記述を残さない。
- planning、design、historical/local executable、actual repository executable、release、operational evidenceを区別する。
- 重要な`!=`境界は、式だけでなく自然な日本語でも説明する。
- Product Valueとの関係を必要な文書から追跡できる。
- REQ / SCNのcurrent正本とhistorical mappingを区別する。
- 原文自体がEvidenceとなるhistorical資料や固定fixtureは、理由なく改変しない。
- 再ドラフト後に、技術的意味・条件・例外・Evidence強度が変わっていないことを確認する。
- current branchに存在する対象開発文書を確認し終えるまで、本IssueをResolvedにしない。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としません。また、読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしません。

自然な日本語と技術的精度を両立させます。

## Natural Japanese review

Product / Plan / Requirementsのcurrent到達点をactual branchへ戻って確認し、完了済みと未監査を分けて進捗を再構成しました。その後、監査範囲、Evidence強度、未完了条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
