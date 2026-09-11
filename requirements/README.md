# SEI Requirements

更新日: 2026-09-01  
状態: **Current Requirements Baseline**

## 1. このディレクトリの役割

`requirements/`は、SEIのProduct Valueを満たすために**何が必要か**を定めます。

Product Valueそのものや長期Visionを定義する場所ではなく、具体的なArchitectureや実装方式を先に固定する場所でもありません。

概念上の関係は次のとおりです。

```text
Product Value / Value Model / Value Acceptance / Product Shape
  ↓
Requirements / Acceptance Scenarios
  ↓
Issue / ADR
  ↓
Architecture
  ↓
Contract / Representation Profile
  ↓
Runtime / Provider Adapter / Fixture / Test
  ↓
Evidence
```

Requirementは主に`what / why / constraint`を扱い、設計判断はADR、構造はArchitecture、相互運用境界はContractへ委ねます。

## 2. Current canonical files

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  PRODUCT_JOURNEY_COMPOSITION.md
  history/
    HISTORICAL_REQUIREMENT_MAPPING.md
```

- `PRODUCT_REQUIREMENTS.md` — current Product Requirementの正本入口
- `ACCEPTANCE_SCENARIOS.md` — current Acceptance Scenarioの正本入口
- `PRODUCT_JOURNEY_COMPOSITION.md` — Product Shapeを既存REQ / SCNへ照合し、end-to-end Product Journeyの重複・不足を分析する補助文書
- `history/HISTORICAL_REQUIREMENT_MAPPING.md` — historical candidateからcurrent baselineへの意味上の対応

`PRODUCT_JOURNEY_COMPOSITION.md`は、新しいRequirementやScenarioの第二の正本ではありません。分析結果からstableな意味を採用するときは、`PRODUCT_REQUIREMENTS.md`または`ACCEPTANCE_SCENARIOS.md`へ反映します。

将来、RequirementやScenarioを個別ファイルへ分割しても、stable IDは維持します。

## 3. Stable ID

Product Requirement:

```text
REQ-0001 ... REQ-9999
```

Acceptance Scenario:

```text
SCN-0001 ... SCN-9999
```

IDにはValue Axis、Milestone、type、status、Core / Profile等の配置を埋め込みません。

## 4. Requirement、Scenario、Testを分ける

```text
Requirement != Acceptance Scenario != Test Case
```

- Requirement — 何が必要かを定める。
- Acceptance Scenario — どのような状況で、その意味差が必要になるかを示す。
- Test Case / Fixture — actual implementationでScenarioをどう再現・検査するかを定める。

一つのScenarioが複数Requirementを同時に検証して構いません。fixtureがPASSしてもScenario全体が満たされたとは限らないため、確認した範囲を明示します。

SCN-0018のような統合Scenarioは、既存Scenarioを置き換えるものではありません。個別の意味境界が一つのProduct Journeyでも同時に保たれることを検査します。

## 5. Product Valueとの追跡

current Requirementは、原則として`SEI_VALUE_MODEL.md`のV1〜V8、または明示的なProduct Principle / external constraintへ追跡します。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

8軸すべてを形式的に付けず、実際に関係する軸だけを示します。

上位からの横断的な索引は`product/value/SEI_VALUE_TRACEABILITY.md`を参照します。

Product ShapeからRequirementへ降りるときは、製品上の操作や画面構造をそのままUniversal Requirementへ昇格させません。まず既存REQとの重複を確認し、既存の規範で表現できない独立した必要性がある場合だけ新しいREQを追加します。

## 6. Requirement statusとEvidenceを分ける

Requirementの意味上の状態には、たとえば次を用います。

- `Proposed`
- `Accepted`
- `Rejected`
- `Superseded`
- `Deprecated`

一方、Evidenceの高さはProduct Value Acceptanceに従い、次の5段階を分けます。

1. Design Evidence
2. Executable Evidence
3. Release Evidence
4. Operational Evidence
5. Adoption / Outcome Evidence

各高さでは必要に応じて次の状態を用います。

- `Satisfied`
- `Partially Satisfied`
- `Not Satisfied`
- `Not Yet Verified`
- `Not Applicable`

```text
Requirement Accepted
  != Executable Evidence Satisfied
  != Release Evidence Satisfied
  != Operational Evidence Satisfied
  != Adoption / Outcome Evidence Satisfied
```

また、個別Contract / runtime / Provider AdapterがそれぞれPASSしていても、それらを足し合わせるだけでend-to-end Product Acceptanceが成立したことにはしません。

## 7. current actual repositoryのEvidence

現在のactual repositoryには、Product / Plan / Requirementsに加えて、Reference Architecture、5 Contract family、JSON Schema、Contract fixture、Representation Profile、Go first semantic runtime、synthetic Provider Adapter、各checker / CIが存在します。

主なscoped Executable Evidence:

- Requirements Registry Conformance
- Contract Conformance
- Capability Observation F1〜F7
- Representation Profile Conformance
- first Semantic Runtime Conformance
- synthetic Provider Adapter Conformance
- V6 / V7 Projection Evaluation

これらのPASSをすべてのRequirementへ一律に継承しません。Requirement / Scenarioごとに実際に触れている意味境界だけを`Partially Satisfied`等へ更新します。

SCN-0018のend-to-end Product Journeyについては、component-level Evidenceは存在しますが、一続きのExecutable harnessは現時点で`Not Yet Verified`です。

Release、Operational、Adoption / Outcome Evidenceは現時点では主張しません。

## 8. Historical candidateの扱い

2026-08-30前後のcandidateには`SEI-PR-*`、`SEI-NFR-*`、`SEI-AS-*`が存在しました。

これらから次をcurrent baselineへ自動継承しません。

- 旧ID
- `direct` / `partial` / `design_only`等の旧Evidence状態
- `VERIFIED`やhistorical local PASS
- M48 / M49 / M50等のMilestone上の位置
- old Product Boundaryに依存する型・Architecture

意味核はcurrent Product Valueへ戻って再評価し、必要なものをcurrent REQ / SCNへ統合しています。

## 9. Requirement作成・更新の必須工程

1. Product Value / Value Model / Value Acceptance / Product Shapeを確認する。
2. Requirementとして必要な意味差を定める。
3. 既存REQとの重複を確認する。
4. 関連するV1〜V8、Scenario、ADR / Issueを確認する。
5. Requirementと実装方式、Product Interaction上の都合を混同していないか確認する。
6. Evidence状態をactual evidenceへ合わせる。
7. 内容と構造を確定する。
8. **意味・強度・例外・留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。**
9. 最終意味監査を行う。
10. Requirements Registry Conformance等、対象CIがある場合はsuccessを確認する。

CI failureを検出した場合は、原因を解消してsuccessを確認するまで後続作業へ進みません。

## 10. 関連文書

- `product/README.md`
- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_PROPOSITION.md`
- `product/definition/SEI_PRODUCT_SHAPE.md`
- `product/value/SEI_VALUE_MODEL.md`
- `product/value/SEI_VALUE_ACCEPTANCE.md`
- `product/value/SEI_VALUE_TRACEABILITY.md`
- `product/vision/SEI_PRODUCT_VISION.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`
- `plan/issue/ISSUE-000048-define-end-to-end-golden-journey-acceptance.md`

## 11. Natural Japanese review

current Product Value、Product Shape、5段階Evidence、REQ-0001〜REQ-0022、SCN-0001〜SCN-0018、Architecture / Contract / Runtime / Provider Adapterのactual Evidenceへ戻って運用規則を再確認した。Product Journeyの分析文書を第二の正本にせず、製品上の操作をそのままUniversal Requirementへ昇格させない境界を追加した。その後、RequirementとScenarioとTestの関係、stable ID、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
