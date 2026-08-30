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

### 品質基盤

次を整備しました。

- `plan/DEVELOPMENT_WORKFLOW.md`
- `plan/DOCUMENT_AUTHORING_STANDARD.md`
- `plan/README.md`の文書作成工程
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`の文書品質原則
- `plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`の中間報告

今後の通常開発は`develop/vX.Y.Z`形式のbranchで行い、Product文書とADR / Issueを実装より優先して整備します。

### Product層

現在の正本branchには次のProduct文書があります。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

Product Valueは、価値階層、価値衝突時の優先規則、Core昇格基準、検証軸、失敗条件まで精緻化されています。Product Vision / Principlesについても、Value Modelとの意味整合を含めて再監査を継続します。

### Plan層

現在の`plan/registry.yaml`には、ADR-0020およびISSUE-000026まで登録されています。

これまでに、Product ValueからRequirements、Decision Memory、Capability、Provider、TEI境界へ至るADR / Issueの整備が進んでいます。旧文書についても、最新Product Valueとの整合と自然な日本語の両面から再確認します。

### 過去の初回監査について

M48〜M50のローカル候補を対象に実施した初回監査は、現在branchより古い文書集合を対象としていました。このため、その時点の文書数をrepository全体の完了判定には使用しません。

中間結果は`plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`へ残し、現在の正本branchを基準として監査を継続します。

## 進行中の作業

- Product Value / Value Model / Value Acceptance / Vision / Principlesの相互整合監査
- ADR-0001〜ADR-0020の最新Product Valueとの意味整合確認
- ISSUE-000001〜ISSUE-000026のStatus、Goal、完了条件、現在状態の再確認
- Requirements / Acceptance Scenariosの自然な日本語化と追跡可能性の整備
- Architecture / Contractsの自然な日本語化とADR整合監査
- rebaseline reports / repository READMEの現在状態への更新

## Acceptance criteria

- 固定100倍基準が現行の正本文書に残らない。
- X-TEAを現行Product名として扱わない。
- TEIをSOZA内部Runtimeと誤読させる記述を残さない。
- planning、design、local executable、actual repository、operational evidenceを区別する。
- 重要な`!=`境界は、式だけでなく自然な日本語でも説明する。
- Product Valueとの関係を必要な文書から追跡できる。
- 原文自体がEvidenceとなるhistorical資料や固定fixtureは、理由なく改変しない。
- 再ドラフト後に、技術的意味・条件・例外・Evidence強度が変わっていないことを確認する。
- 現行branchに存在する対象文書を確認し終えるまで、本IssueをResolvedにしない。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としません。また、読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしません。

自然な日本語と技術的精度を両立させます。
