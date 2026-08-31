# SOZA Requirements

更新日: 2026-08-31  
状態: **Current Requirements Baseline**

## 1. このディレクトリの役割

`requirements/`は、SOZAのProduct Valueを満たすために**何が必要か**を定めます。

Product Valueそのものや長期Visionを定義する場所ではなく、Architectureや実装方式を決める場所でもありません。

概念上の関係は次のとおりです。

```text
Product Value / Value Model / Value Acceptance
  ↓
Requirements / Acceptance Scenarios
  ↓
Issue / ADR
  ↓
Architecture
  ↓
Contract
  ↓
Implementation / Test / Evidence
```

Requirementは主に`what / why / constraint`を扱い、具体的な設計判断はADRへ委ねます。

## 2. Current canonical files

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  history/
    HISTORICAL_REQUIREMENT_MAPPING.md
```

- `PRODUCT_REQUIREMENTS.md` — current Product Requirementの正本入口
- `ACCEPTANCE_SCENARIOS.md` — current Acceptance Scenarioの正本入口
- `history/HISTORICAL_REQUIREMENT_MAPPING.md` — 過去candidateからcurrent baselineへの対応

将来、RequirementやScenarioが増えた場合は個別ファイルへ分割できます。ただしstable IDは維持します。

## 3. Stable ID

Product Requirement:

```text
REQ-0001
REQ-0002
...
REQ-9999
```

Acceptance Scenario:

```text
SCN-0001
SCN-0002
...
SCN-9999
```

IDにはValue Axis、Milestone、type、status、Core / Profile等の配置を埋め込みません。

## 4. RequirementとScenarioとTestを分ける

```text
Requirement != Acceptance Scenario != Test Case
```

- Requirement — 何が必要か
- Acceptance Scenario — どのような状況で意味差を確認するか
- Test Case — actual implementationでどう再現・検査するか

一つのScenarioが複数Requirementを同時に検証して構いません。

Scenarioにfixtureやtestが対応しても、Scenario全体が満たされたとは限りません。検査できた期待・境界だけをExecutable Evidenceとして扱います。

## 5. Product Valueとの追跡

current Requirementは、原則として`SOZA_VALUE_MODEL.md`のV1〜V8、または明示的なProduct Principle / external constraintへ追跡します。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

8軸すべてを形式的に付けません。実際に関係する軸だけを記載します。

横断的な追跡は`../product/value/SOZA_VALUE_TRACEABILITY.md`を参照します。

## 6. Requirement statusとEvidenceを分ける

Requirementの意味上の状態:

- `Proposed`
- `Accepted`
- `Rejected`
- `Superseded`
- `Deprecated`

Evidenceは別に管理します。

- Design Acceptance
- Executable Acceptance
- Release Acceptance
- Operational Acceptance
- Adoption / Outcome Acceptance

各層の状態:

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

2026-08-31時点のactual repositoryには、Reference Architecture、Contract Definition、JSON Schema、Fixture、Representation Profile、Go semantic runtime、synthetic Provider Adapter、checker / CIが実体化されています。そのため、対象を限定したExecutable Evidenceは存在します。

一方、production Provider integration、Release、Operational、Adoption / Outcomeは別Evidenceとして扱い、下位Evidenceから自動的にSatisfiedへ上げません。

## 7. Current Executable Evidenceの読み方

current repositoryでは、少なくとも次をactual CIで再現しています。

- Requirements Registry Conformance
- Contract Conformance
- Capability Observation F1〜F7
- Representation Profile Conformance
- first Semantic Runtime Conformance
- synthetic Provider Adapter A / B mapping tests

これらは重要なExecutable Evidenceですが、検査対象へ限定して読みます。

```text
fixture / runtime CI PASS
  != whole Requirement satisfied
  != whole Scenario satisfied
  != production integration
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Requirementごとの現在地は`PRODUCT_REQUIREMENTS.md`、Scenarioごとの現在地は`ACCEPTANCE_SCENARIOS.md`を正とします。

## 8. Historical candidateの扱い

2026-08-30時点のcandidateには、`SOZA-PR-001`〜`SOZA-PR-018`とNFR 10件、Acceptance Scenario 8件等が存在しました。

これらは有用なhistorical evidenceですが、current baselineへ次を自動継承しません。

- 旧ID
- `direct` / `partial` / `design_only`等のEvidence状態
- `VERIFIED`やlocal PASS
- M48 / M49 / M50等のMilestone上の位置
- old Product Boundaryに依存する設計判断

意味核はcurrent Product Valueへ照合し、必要なものを新しいREQ / SCNへ移しています。

## 9. Requirement / Scenario作成の必須工程

1. Product Value / Value Model / Value Acceptanceを確認する。
2. RequirementまたはScenarioとして必要な意味差を定める。
3. 既存REQ / SCNとの重複を確認する。
4. 関連するV1〜V8、REQ、SCN、ADR / Issueを確認する。
5. Requirement / Scenarioと実装方式を混同していないか確認する。
6. Evidence状態をactual repositoryの証拠へ合わせる。
7. Evidenceの高さをDesign / Executable / Release / Operational / Adoption・Outcomeで分離する。
8. 内容と構造を確定する。
9. **意味・強度・例外・留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。**
10. 最終意味監査を行う。

第9工程は省略しません。

## 10. 関連文書

- `../product/value/SOZA_PRODUCT_VALUE.md`
- `../product/value/SOZA_VALUE_MODEL.md`
- `../product/value/SOZA_VALUE_ACCEPTANCE.md`
- `../product/value/SOZA_VALUE_TRACEABILITY.md`
- `../product/vision/SOZA_PRODUCT_VISION.md`
- `../product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`

## 11. 自然な日本語ドラフト

current Product Value、Product Requirements、Acceptance Scenarios、Architecture / Contract / Representation Profile / Runtime / Provider Adapterのactual Evidenceを照合し、旧baseline時点の記述を現在地へ更新しました。その後、Requirement / Scenario / Testの役割、Status、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
