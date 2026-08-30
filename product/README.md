# SOZA `product/` 文書体系

更新日: 2026-08-31  
状態: **Product Documentation Baseline**

## 1. このディレクトリの役割

`product/`は、SOZAが**なぜ存在するか、何を価値として守るか、どのEvidenceで価値充足を確認するか、どのような長期像を目指すか、下位設計でどの原則を反復して使うか**を定める上位文書です。

`requirements/`、`plan/`、`architecture/`、実装の都合を正当化するためにProduct Valueを後付けで変更しません。

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

### `value/SOZA_VALUE_TRACEABILITY.md`

Product Value / Value Model / Value Acceptanceと、現在のRequirement、Acceptance Scenario、ADR、Issue、Evidence gapの関係を一覧化します。

これはcoverage scoreではありません。RequirementやADRの数、対応表の埋まり具合を、Product Valueの実証とは扱いません。

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
  └─ Value Traceability
        ↓
Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Implementation / Test / Evidence
```

`Value Acceptance`、`Vision / Principles`、`Value Traceability`は、Value Modelを異なる方向から具体化する補完文書です。単純な上下関係ではありません。

実装や運用から反証が得られた場合は、下位から上位へ戻して再検討します。重要なのは、**下位の都合で上位価値を黙って書き換えないこと**です。

## 4. 権威関係

Product Valueの意味に関しては、次を原則とします。

1. `SOZA_PRODUCT_VALUE.md` — 存在理由と最上位価値
2. `SOZA_VALUE_MODEL.md` — 価値優先、Core境界、V1〜V8
3. `SOZA_VALUE_ACCEPTANCE.md` — 価値充足を主張するためのEvidence境界
4. `SOZA_PRODUCT_VISION.md` / `SOZA_PRODUCT_PRINCIPLES.md` — 長期像と反復原則
5. `SOZA_VALUE_TRACEABILITY.md` — current Requirements / ADR / Evidenceとの対応状況

Traceability文書は現状を記録する文書であり、Product Valueそのものを上書きしません。

Product Value変更の統治規則はADR-0018を正とします。Requirementsのidentity、traceability、Evidence境界はADR-0020を正とします。

## 5. Requirement・Scenario・Testを分ける

現在のRequirements体系では、次を分離します。

```text
Requirement != Acceptance Scenario != Test Case
```

- **Requirement** — Product Valueを満たすために何が必要かを定める。
- **Acceptance Scenario** — どのような状況で、その意味差が必要になるかを示す。
- **Test Case / Fixture** — actual implementationでScenarioをどう再現・検査するかを定める。

Product Value側で別のScenario体系を重ねて作らず、具体場面のcurrent canonical entry pointは`requirements/ACCEPTANCE_SCENARIOS.md`とします。

Product Valueとの関係は`SOZA_VALUE_TRACEABILITY.md`から追跡します。

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

`Adoption / Outcome Evidence`はV1〜V8の新しいValue Axisではありません。製品が実際に利用され、期待した外部成果へつながったかを評価する、より上位のProduct effectiveness上のEvidenceです。

現時点で得られていないEvidenceを、設計文書の充実によって補ったことにはしません。

## 7. Product Valueを変更する場合

Product ValueまたはValue Modelの意味を変更する場合は、通常の文書修正として扱いません。

少なくとも次を確認します。

- どのEvidenceが変更を必要としたか。
- Value Acceptanceへどの影響があるか。
- Requirements / Acceptance Scenariosへどの影響があるか。
- ADR / Architectureのどこが影響を受けるか。
- 過去Decisionとの互換性・非互換性は何か。
- 何が確認済みで、何がまだ未実証か。
- どの条件で再び見直すか。

ADR-0018に従い、明示的なProduct Value再基線化として扱います。

## 8. Product文書を追加する基準

上位文書を増やすこと自体を価値にはしません。

新しいProduct文書を追加するのは、既存文書へ追記すると責務が混ざる場合や、独立した保守単位として扱うことで意味が明確になる場合を基本とします。

`SOZA_VALUE_TRACEABILITY.md`をValue Modelから分けるのは、ADR、Requirement、Acceptance Scenario、Evidenceの進行に応じて頻繁に変化する情報を、比較的安定したValue Modelから分離するためです。

## 9. 現在のProduct Value上の主要gap

2026-08-31時点では、current Product RequirementsとAcceptance Scenariosまでactual repositoryへ実体化されています。

一方、次はactual Evidenceがまだ薄い領域です。

- Human / AI ReadabilityのExecutable / Operational Acceptance
- current Requirements baselineのExecutable Evidence
- Capability Observation schema / fixtureのactual conformance
- runtime / provider replacementのExecutable Evidence
- operational evidence
- adoption / outcome evidence

このgapを、Product Valueの失敗や既達成として誤って扱わず、現在のEvidence levelとして保持します。

## 10. 文書品質

Product文書は、`plan/DOCUMENT_AUTHORING_STANDARD.md`に従って整備します。

内容・構造・技術的一貫性・Evidence強度を確認した後、意味、仕様、留保を変えず、自然な日本語となることを最重要視して全文をドラフトし直し、最後に意味を再監査します。

## 11. 関連文書

- `value/SOZA_PRODUCT_VALUE.md`
- `value/SOZA_VALUE_MODEL.md`
- `value/SOZA_VALUE_ACCEPTANCE.md`
- `value/SOZA_VALUE_TRACEABILITY.md`
- `vision/SOZA_PRODUCT_VISION.md`
- `principles/SOZA_PRODUCT_PRINCIPLES.md`
- `../requirements/PRODUCT_REQUIREMENTS.md`
- `../requirements/ACCEPTANCE_SCENARIOS.md`
- `../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`

## 12. 自然な日本語ドラフト

Product Value一式、current Requirements、ADR-0018、ADR-0020の役割を整理した後、各文書の権威関係、変更規則、Evidence境界を変えず、自然な日本語となることを最重要視して全文をドラフトしました。その後、最終意味監査を実施しています。
