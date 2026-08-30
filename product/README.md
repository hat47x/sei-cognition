# SOZA `product/` 文書体系

更新日: 2026-08-31  
状態: **Product Documentation Baseline**

## 1. このディレクトリの役割

`product/`は、SOZAが**なぜ存在するか、何を価値として守るか、どのようなEvidenceで価値充足を確認するか、どのような長期像を目指すか、下位設計でどの原則を反復して使うか**を定める上位文書です。

`plan/`、`architecture/`、implementation等の都合を正当化するためにProduct Valueを後付けで変更しません。

一方、実装、検証、実運用からProduct Valueの仮説に反証が得られた場合は、そのEvidenceを明示したうえで上位文書へ戻ります。

## 2. 文書の役割

### `value/SOZA_PRODUCT_VALUE.md`

SOZAが存在する理由と、最も上位で守る製品価値を定めます。

### `value/SOZA_VALUE_MODEL.md`

Product Valueを、Requirements・ADR・Architectureの判断へ使える粒度へ具体化します。

主に、価値の三層、価値衝突時の優先規則、Universal Coreへの昇格基準、V1〜V8のvalidation axis、価値上の失敗パターンを定めます。

### `value/SOZA_VALUE_ACCEPTANCE.md`

V1〜V8を満たしたと主張するために必要なEvidence境界を定めます。

Design / Executable / Release / Operational Evidenceを区別し、未検証をPASSへ変換しません。

### `value/SOZA_VALUE_SCENARIOS.md`

Product ValueとV1〜V8を、具体的な判断場面へ戻します。

Value ScenarioはRequirementやAcceptance Scenarioそのものではありません。上位価値が現実の場面でどの意味差として現れるかを確認し、Requirements以下へ展開するための橋渡しです。

### `value/SOZA_VALUE_TRACEABILITY.md`

Product Value / Value Model / Value Acceptance / Value Scenarioと、現在のADR・Issue・Evidence gapの関係を一覧化します。

これはcoverage scoreではありません。ADRが多いことや表が埋まっていることを、Product Valueの実証とは扱いません。

### `vision/SOZA_PRODUCT_VISION.md`

Product Valueを時間軸へ延ばし、技術やProviderが変わっても目指す長期像を定めます。

### `principles/SOZA_PRODUCT_PRINCIPLES.md`

Product ValueとVisionを、Requirements、ADR、Architecture、Implementationで繰り返し使う判断原則へ落とします。

## 3. 文書間の関係

概念上は、次のように具体化します。

```text
SOZA Product Value
  → Value Model
  ├─ Value Acceptance
  ├─ Vision / Principles
  └─ Value Scenarios
        ↓
Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Implementation / Test / Evidence
```

`Value Acceptance`、`Vision / Principles`、`Value Scenarios`は、Value Modelを異なる方向から具体化する補完文書です。単純な上下関係ではありません。

`SOZA_VALUE_TRACEABILITY.md`は、この体系と現在の下位文書・Evidenceの対応状況を記録します。

実装や運用から反証が得られた場合は、下位から上位へ戻して再検討します。重要なのは、**下位の都合で上位価値を黙って書き換えないこと**です。

## 4. 権威関係

Product Valueの意味に関しては、次を原則とします。

1. `SOZA_PRODUCT_VALUE.md` — 存在理由と最上位価値
2. `SOZA_VALUE_MODEL.md` — 価値優先、Core境界、V1〜V8
3. `SOZA_VALUE_ACCEPTANCE.md` — 価値充足を主張するためのEvidence境界
4. `SOZA_PRODUCT_VISION.md` / `SOZA_PRODUCT_PRINCIPLES.md` — 長期像と反復原則
5. `SOZA_VALUE_SCENARIOS.md` — 具体場面への展開
6. `SOZA_VALUE_TRACEABILITY.md` — 現在の下位文書・Evidenceとの対応状況

Traceability文書は現状を記録する文書であり、Product Valueそのものを上書きしません。

Product Value変更の統治規則はADR-0018を正とします。

## 5. Value ScenarioとAcceptance Scenarioを分ける

両者は似ていますが、役割を分けます。

```text
Value Scenario != Acceptance Scenario != Test Case
```

- **Value Scenario** — Product Valueが現実の判断場面でどの意味差として必要になるかを確認する上位シナリオ。
- **Acceptance Scenario** — REQ / SCN体系のもとで、Requirementを満たすために何が成立すべきかを示すcurrent requirements側のシナリオ。
- **Test Case** — actual repositoryでExecutable Evidenceを得るための具体的な検査。

同じ現実場面を参照していても、役割を混同しません。

## 6. Evidenceの扱い

Product文書が整っていることと、製品価値が実証されていることを分けます。

```text
Value Definition
  != Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
```

さらに、SOZAが実運用で期待どおりに動いたことと、利用者・組織の意思決定や成果が実際に改善したことも分けます。

```text
Operational Evidence != Adoption / Outcome Evidence
```

`Adoption / Outcome Evidence`はV1〜V8の新しい価値軸ではありません。製品が実際に利用され、期待した外部成果へつながったかを評価する、より上位のProduct effectiveness上のEvidenceです。

現時点で得られていないEvidenceを、設計文書の充実によって補ったことにはしません。

## 7. Product Valueを変更する場合

Product ValueまたはValue Modelの意味を変更する場合は、通常の文書修正として扱いません。

少なくとも次を確認します。

- どのEvidenceが変更を必要としたか。
- Value Acceptanceへどの影響があるか。
- 既存Value Scenarioへどの影響があるか。
- Requirements / ADR / Architectureのどこが影響を受けるか。
- 過去Decisionとの互換性・非互換性は何か。
- 何が確認済みで、何がまだ未実証か。
- どの条件で再び見直すか。

ADR-0018に従い、明示的なProduct Value再基線化として扱います。

## 8. Product文書を追加する基準

上位文書を増やすこと自体を価値にはしません。

新しいProduct文書を追加するのは、既存文書へ追記すると責務が混ざる場合や、独立した保守単位として扱うことで意味が明確になる場合を基本とします。

Value ScenarioとTraceabilityをValue Modelから分けるのは、次の理由によります。

- Value Modelは比較的安定した規範を持つ。
- Value Scenarioは実案件から増減・精緻化し得る。
- TraceabilityはADR / Requirement / Evidenceの進行に応じて頻繁に変化する。

変更頻度と文書責務の違いを分離し、上位価値そのものを不必要に揺らさないようにします。

## 9. 現在のProduct Value上の主要gap

2026-08-31時点では、設計判断としてHistorical Reconstruction、Semantic Separation、Revision Integrity、Provider Independence、Uncertainty Preservation、Execution Independenceが比較的厚く整理されています。

一方、次はactual Evidenceがまだ薄い領域です。

- Human / AI Readabilityのactual Acceptance
- current Requirements baselineのExecutable Evidence
- Capability Observation schema / fixtureのactual conformance
- operational evidence
- adoption / outcome evidence

このgapを、Product Valueの失敗や既達成として誤って扱わず、現在のEvidence levelとして保持します。

## 10. 文書品質

Product文書は、次の順序で整備します。

1. 意味と責務を定める。
2. Product Value相互の整合を確認する。
3. 具体Scenarioと反例へ戻す。
4. 下位ADR / Issueとの矛盾を確認する。
5. Evidence強度を監査する。
6. 意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。
7. 最終意味監査を行う。

この日本語ドラフト工程は省略しません。

## 11. 関連文書

- `value/SOZA_PRODUCT_VALUE.md`
- `value/SOZA_VALUE_MODEL.md`
- `value/SOZA_VALUE_ACCEPTANCE.md`
- `value/SOZA_VALUE_SCENARIOS.md`
- `value/SOZA_VALUE_TRACEABILITY.md`
- `vision/SOZA_PRODUCT_VISION.md`
- `principles/SOZA_PRODUCT_PRINCIPLES.md`
- `../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`

## 12. 自然な日本語ドラフト

Product Value一式、ADR-0018、ADR-0020の役割を整理した後、各文書の権威関係、変更規則、Evidence境界を変えず、自然な日本語となることを最重要視して全文をドラフトしました。その後、最終意味監査を実施しています。
