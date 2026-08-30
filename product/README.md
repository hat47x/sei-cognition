# SOZA `product/` 文書体系

更新日: 2026-08-31  
状態: **Product Documentation Baseline**

## 1. このディレクトリの役割

`product/`は、SOZAが**なぜ存在するか、何を価値として守るか、どのような長期像を目指すか、下位設計でどの原則を反復して使うか**を定める上位文書です。

`plan/`、`architecture/`、implementation等の都合を正当化するためにProduct Valueを後付けで変更しません。

一方、実装、検証、実運用からProduct Valueの仮説に反証が得られた場合は、そのEvidenceを明示したうえで上位文書へ戻ります。

## 2. 文書の役割

### `value/SOZA_PRODUCT_VALUE.md`

SOZAが存在する理由と、最も上位で守る製品価値を定めます。

主な問い:

- SOZAは何のために存在するか。
- 何を失うとSOZAではなくなるか。
- 何を製品価値そのものとはみなさないか。

### `value/SOZA_VALUE_MODEL.md`

Product Valueを、下位設計の判断へ使える粒度へ具体化します。

主な内容:

- 価値の三層
- 価値衝突時の優先規則
- Universal Coreへの昇格基準
- V1〜V9のvalidation axis
- 価値上の失敗パターン
- Evidence level

### `value/SOZA_VALUE_SCENARIOS.md`

抽象的なProduct Valueを、具体的な判断場面へ戻します。

Value ScenarioはRequirementやAcceptance Scenarioそのものではありません。Product Valueが現実の場面でどの意味差として現れるかを確認し、Requirements以下へ展開するための橋渡しです。

### `value/SOZA_VALUE_TRACEABILITY.md`

Product Value / Value Model / Value Scenarioと、現在のADRや未検証gapの関係を一覧化します。

これはcoverage scoreではありません。ADRが多いことや対応表が埋まっていることを、Product Valueの実証とは扱いません。

### `vision/SOZA_PRODUCT_VISION.md`

Product Valueを時間軸へ延ばし、技術やProviderが変わっても目指す長期像を定めます。

現在の実装方式や将来予測を固定する文書ではありません。

### `principles/SOZA_PRODUCT_PRINCIPLES.md`

Product ValueとVisionを、Requirements、ADR、Architecture、Implementationで繰り返し使う判断原則へ落とします。

個別ADRのDecisionを先取りしたり、原則だけで個別判断の正しさを保証したりしません。

## 3. 文書間の関係

概念上は次の順で具体化します。

```text
SOZA Product Value
  → Value Model
  → Vision / Principles
  → Value Scenarios
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Implementation / Test / Evidence
```

ただし、これは一方向にしか戻れない階層ではありません。

実装や運用から反証が得られた場合は、下位から上位へ戻して再検討します。重要なのは、**下位の都合で上位価値を黙って書き換えないこと**です。

## 4. 権威関係

Product Valueの意味に関しては、次を原則とします。

1. `SOZA_PRODUCT_VALUE.md` — 存在理由と最上位価値
2. `SOZA_VALUE_MODEL.md` — 価値優先・Core境界・検証規則
3. `SOZA_PRODUCT_VISION.md` / `SOZA_PRODUCT_PRINCIPLES.md` — 長期像と反復原則
4. `SOZA_VALUE_SCENARIOS.md` — 具体場面への展開
5. `SOZA_VALUE_TRACEABILITY.md` — 現在の下位文書との対応状況

Traceability文書は現状を記録する文書であり、Product Valueそのものを上書きしません。

Value Scenarioで新しい重要境界が発見された場合も、既存Product Valueの具体化で済むのか、Product Value自体の変更が必要なのかを分けて判断します。

Product Value変更の統治規則はADR-0018を正とします。

## 5. Evidenceの扱い

Product文書が整っていることと、製品価値が実証されていることを分けます。

```text
Value Definition
  != Design / Requirement Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Product文書では、確認できていないEvidence levelを推測で埋めません。

たとえば、V6 Human / AI Readabilityを原則として定義できても、実際の利用者が意味を追えることはAcceptanceやoperational / outcome Evidenceで別に確認する必要があります。

## 6. Product Valueを変更する場合

Product ValueまたはValue Modelの意味を変更する場合は、通常の文書修正として扱いません。

少なくとも次を確認します。

- どのEvidenceが変更を必要としたか。
- 既存Value Scenarioへどの影響があるか。
- Requirements / ADR / Architectureのどこが影響を受けるか。
- 過去Decisionとの互換性・非互換性は何か。
- 何が確認済みで、何がまだ未実証か。
- どの条件で再び見直すか。

ADR-0018に従い、明示的なProduct Value再基線化として扱います。

## 7. Product文書を追加する基準

上位文書を増やすこと自体を価値にはしません。

新しいProduct文書を追加するのは、既存文書へ追記すると役割が混ざる場合や、独立した保守単位として扱うことで意味が明確になる場合を基本とします。

たとえば、Value ScenarioとTraceabilityをValue Modelから分けているのは、次の理由によります。

- Value Modelは比較的安定した規範を持つ。
- Value Scenarioは実案件から増減・精緻化し得る。
- TraceabilityはADR / Requirement / Evidenceの進行に応じて頻繁に変化する。

変更頻度と文書責務の違いを分離し、上位価値そのものを不必要に揺らさないようにします。

## 8. 現在のProduct Value上の主要gap

2026-08-31時点では、設計判断としてはHistorical Reconstruction、Semantic Separation、Revision Integrity、Provider Independence、Uncertainty Preservation、Execution Independenceが比較的厚く整理されています。

一方、次はactual Evidenceがまだ薄い領域です。

- Human / AI ReadabilityのAcceptance
- actual repository上のExecutable Conformance
- operational evidence
- adoption / outcome evidence

また、Value ScenarioからProduct Requirement / NFR / Acceptanceへの現行追跡基線はISSUE-000024で作成します。

このgapを、Product Valueの失敗や既達成として誤って扱わず、現在のEvidence levelとして保持します。

## 9. 文書品質

Product文書は、次の順序で整備します。

1. 意味と責務を定める。
2. Product Value相互の整合を確認する。
3. 具体Scenarioと反例へ戻す。
4. 下位ADR / Issueとの矛盾を確認する。
5. Evidence強度を監査する。
6. 意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。
7. 最終意味監査を行う。

この日本語ドラフト工程は省略しません。

## 10. 関連文書

- `value/SOZA_PRODUCT_VALUE.md`
- `value/SOZA_VALUE_MODEL.md`
- `value/SOZA_VALUE_SCENARIOS.md`
- `value/SOZA_VALUE_TRACEABILITY.md`
- `vision/SOZA_PRODUCT_VISION.md`
- `principles/SOZA_PRODUCT_PRINCIPLES.md`
- `../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../plan/issue/ISSUE-000024-derive-value-scenario-requirement-traceability.md`

## 11. 自然な日本語ドラフト

Product Value一式とADR-0018の役割を整理した後、各文書の権威関係、変更規則、Evidence境界を変えず、自然な日本語となることを最重要視して全文をドラフトしました。その後、最終意味監査を実施しています。
