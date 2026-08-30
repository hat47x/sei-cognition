# ISSUE-000023: Product Valueの優先規則と検証境界を正式化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018**  
Updated: 2026-08-31

## Goal

SOZAのProduct Valueを、抽象理念に留めず、下位設計の判断、具体Scenario、Evidence claimへ適用できる統治基線として正式化する。

## Background

SOZAのProduct Valueは、判断の意味、不確実性、責任、来歴、CapabilityとProviderの分離、実行基盤からの独立性を中核として定義されていた。

一方、下位設計が増えるにつれ、次の問いを個別ADRだけで処理すると判断基準が揺れる可能性があった。

- 意味保存、操作性、性能、実装容易性が衝突したとき、何を優先するか。
- 新しい概念をSOZA Universal Coreへ含める基準は何か。
- Product Valueを満たしたと判断するには、どの観点で検証するか。
- 特定ProviderやTEIとの密接な関係が、SOZA Coreへの昇格理由になり得るか。
- 将来技術が変わったときにも残すべき価値は何か。
- Product Valueを定義したこと、設計で扱ったこと、testが通ったこと、productionで動いたこと、利用者価値が実証されたことをどう区別するか。
- 抽象原則を具体的な判断場面へ戻し、Requirements以下へどう展開するか。

## Work completed

### 1. Product Valueを三層へ整理した

Product Valueを、次の三層として整理した。

1. 失ってはならない意味
2. 後から選び直せること
3. 利用し続けられること

### 2. Value Modelを設計判断へ使える粒度まで精緻化した

`product/value/SOZA_VALUE_MODEL.md`で、価値衝突時の優先規則、Universal Coreへの昇格基準、失敗パターン、V1〜V9のvalidation axisを定義した。

現在のvalidation axisは次である。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence
- V9 Evidence Calibration

### 3. Value Scenarioを追加した

`product/value/SOZA_VALUE_SCENARIOS.md`を追加し、Product Valueを13の代表的な判断場面へ戻した。

AI RecommendationとDecision、Unknown / Conflict、Questionの問い直し、Provider交換、Authorization、実行成功とDecision Validity、Cognitive Method、Selective Disclosure、Progressive Explicitness、技術交換、Evidence level等を含む。

Value ScenarioはRequirementやAcceptance Scenarioそのものではなく、上位価値を具体場面へ戻して下位文書へ展開するための橋渡しとする。

### 4. Evidence levelを明示した

少なくとも次を同一視しない。

```text
Value Definition
  != Design / Requirement Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

historical / local candidateのPASSも、actual repositoryのPASSへ自動継承しない。

### 5. ADRとの追跡基線を作った

`product/value/SOZA_VALUE_TRACEABILITY.md`を追加し、ADR-0001〜ADR-0019をValue Model validation axisとValue Scenarioへ戻して監査した。

ADR数や対応数をProduct Value coverageのscoreにはしない。設計上どこが扱われ、どこにactual Acceptance / operational / outcome Evidenceが不足しているかを明示するために使う。

### 6. Product Value governanceをADR-0018へ確定した

ADR-0018で次をAccepted Decisionとした。

- Product Valueを下位設計の正当化基準とする。
- 価値衝突時は意味保存を優先する。
- Value Scenarioへ戻して重要判断を確認する。
- Evidence levelを自動昇格させない。
- Core昇格はProduct Value上の必要性で判断する。
- Product Value変更は明示的な再基線化として扱う。

## Resolution

Product Valueの優先規則と検証境界は、Product Value / Value Model / Value Scenario / Value Traceability / ADR-0018へ分担して基線化できたため、本IssueをResolvedとする。

このResolutionは、SOZAのProduct Valueがproductionや利用者Outcomeで実証されたことを意味しない。

次の段階はISSUE-000024で、Value ScenarioからProduct Requirement / NFR / Acceptanceへ追跡基線を作ることである。

## Acceptance

- [x] Product Valueの価値階層が明文化されている。
- [x] 価値衝突時の優先規則が明文化されている。
- [x] Universal Coreへの昇格基準と除外基準が明文化されている。
- [x] V1〜V9のProduct Value validation axisが定義されている。
- [x] Product Valueの失敗パターンが列挙されている。
- [x] TEIや特定Providerとの近さだけではCoreへ昇格しないことが確認されている。
- [x] Product Valueを具体的なValue Scenarioへ戻せる。
- [x] Value Definitionとより強いEvidence levelを区別できる。
- [x] ADR-0001〜ADR-0019とProduct Valueの追跡基線がある。
- [x] actual repository / operational / adoption evidenceが不足している領域を未実証として残せる。
- [x] 自然な日本語を最優先に全文を再ドラフトし、意味監査を実施している。

## Follow-up

- ISSUE-000024 — Value Scenario → Requirement / NFR / Acceptance traceability
- ISSUE-000022 — actual repository baseline materialization
- ISSUE-000015 — natural Japanese document audit

## Related material

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- ADR-0001
- ADR-0012
- ADR-0013
- ADR-0014
- ADR-0017
- ADR-0018
- ADR-0019

## Natural Japanese review

Product Value一式、ADR-0018、Value Traceability、現在のEvidence levelへ戻してResolutionとAcceptanceを再確認した後、意味、強度、未実証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
