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
7. runtime / fixture / tool実体化後の説明文書・コメント

## 現在の進捗 — 2026-08-31

### 1. 品質基盤

次を整備しました。

- `plan/DEVELOPMENT_WORKFLOW.md`
- `plan/DOCUMENT_AUTHORING_STANDARD.md`
- `plan/README.md`の文書作成工程
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`の文書品質原則
- `plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`の中間報告

内容・構造を確定した後に全文を自然な日本語で再ドラフトし、その後に最終意味監査を行う工程を通常開発へ組み込みました。

今後の通常開発は`develop/vX.Y.Z`形式のbranchで行い、Product文書とADR / Issueを実装より先に整備します。

### 2. Product層

current Product文書:

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
- 各文書について自然な日本語全文再ドラフトと最終意味監査を実施。

Product層の主要baselineは一巡しました。Architecture / Contract / Executable Evidenceから反証が得られた場合は必要箇所を再監査します。

### 3. Plan層

`plan/registry.yaml`には、ADR-0001〜ADR-0021、ISSUE-000001〜ISSUE-000031を登録しています。

特に次を進めました。

- ADR-0018でProduct Valueの権威関係と評価境界を固定。
- ADR-0019でProvider-neutralなCapability Observation境界を固定。
- ADR-0020でRequirementsのstable ID、Value traceability、Requirement / Scenario / Test、status / Evidence境界を固定。
- ADR-0021でArchitecture / Contract / schema / implementationの権威関係とContract versioningを固定。
- ISSUE-000025 / 000026でRequirements Design baselineを整備。
- ISSUE-000028 / 000029でArchitecture規約とReference Architectureを整備。
- ISSUE-000030でContract Design baselineを整備。
- Requirements checkerをISSUE-000027、Contract conformanceをISSUE-000031へ分離。
- ISSUE-000022をactual repositoryの現在地に合わせて更新。

新規・大幅更新した文書は、自然な日本語全文再ドラフト工程と最終意味監査を通しています。

ただし、ADR-0001〜ADR-0021およびISSUE-000001〜ISSUE-000031の**既存部分を含む全件監査が完了したとはまだ扱いません。** current Product Value / Requirements / Architecture / Contractsからの逆向き照合を継続します。

### 4. Requirements層

current Requirements Design baseline:

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

historical candidateのProduct Requirements、NFR、Acceptance Scenarioは、件数や旧IDを保存することを目的とせず、意味核をcurrent Product Valueへ戻して統合・分離しました。

旧Evidence状態はcurrent baselineへ自動継承していません。

Requirements文書については、current / historical / evidenceの三層を整理した後、全文を自然な日本語で再ドラフトし、意味、要求強度、例外、Evidence状態が変わっていないことを確認しています。

Requirements Design baselineは完了しました。Executable registry checkはISSUE-000027で追跡します。

### 5. Architecture層

current Architecture Design baselineをactual repositoryへ実体化しました。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

M48 / M49 / M50等のMilestone順をcurrent ontologyへ持ち込まず、次のようなarchitecture concernへ再構成しています。

- Inquiry / Epistemic State
- Cognitive Method
- Decision Memory
- Capability Definition / Observation / Choice
- Responsibility / Authority
- Semantic Reference / Revision / Exact Binding
- Profile / Policy
- Federation / Selective Disclosure
- Provider / Adapter
- Projection
- Persistence
- Evidence / Assurance

REQ-0001〜REQ-0022が少なくとも一つのarchitecture concernへ追跡できることを確認しました。

historical ArchitectureはIntegrated / Split / Historical evidence only等へ分類し、old field set、package、algorithm、local PASSをcurrent正本へ自動継承していません。

Architecture 4文書は内容確定後に全文を自然な日本語で再ドラフトし、意味境界とEvidence強度が変わっていないことを確認しています。

### 6. Contracts層

current Contract Design baselineをactual repositoryへ実体化しました。

current Contract family:

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

主な正本:

- `contracts/README.md`
- `contracts/CONTRACT_CATALOG.md`
- `contracts/TRACEABILITY.md`
- 各Contract Definition
- `contracts/history/HISTORICAL_CONTRACT_MAPPING.md`

Semantic ContractとRepresentation Profileを分離し、JCS、SHA-256、raw bytes等をSemantic Coreへ固定していません。

Contract Definitionをhuman-readable semantic normative sourceとし、machine-readable schemaは検証可能なrepresentationとして後続実装します。

各Contract文書は、意味・規範強度・留保を確定後、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。

Executable conformanceは未検証であり、ISSUE-000031で追跡します。

### 7. repository README

root READMEをactual Design baselineへ同期しました。

現在はProduct / Requirements / Architecture / Contracts / Planが実体化済みであること、runtime / executable conformance / release / operational evidenceは未完了であることを分けて記載しています。

### 8. 過去の初回監査について

M48〜M50のローカル候補を対象に実施した初回監査は、現在branchより古い文書集合を対象としていました。このため、その時点の文書数をrepository全体の完了判定には使用しません。

中間結果は`plan/DOCUMENT_REVIEW_REPORT_2026-08-31.md`へ残し、current branchを基準として監査を継続します。

## 進行中の作業

優先順は次のとおりです。

1. ADR / Issue既存文書をcurrent Product Value / REQ / Architecture / Contractから逆向きに監査する。
2. Requirements registry checkerを実装する（ISSUE-000027）。
3. Contract schema / fixture / conformanceを実装する（ISSUE-000031）。
4. Capability Observation fixtureを実装する（ISSUE-000024）。
5. Representation Profile / Exact Binding verificationを安定化する（ISSUE-000009）。
6. rebaseline reports等のhistorical / active境界を再監査する。
7. runtime / fixture / tool実体化後の説明文書・コメントを同じ日本語工程へ通す。

## Acceptance criteria

- 固定100倍基準が現行の正本文書に残らない。
- X-TEAを現行Product名として扱わない。
- TEIをSOZA内部Runtimeと誤読させる記述を残さない。
- planning、design、historical/local executable、actual repository executable、release、operational evidenceを区別する。
- 重要な`!=`境界は、式だけでなく自然な日本語でも説明する。
- Product Valueとの関係を必要な文書から追跡できる。
- REQ / SCNのcurrent正本とhistorical mappingを区別する。
- Architecture concernとruntime componentを同一視しない。
- Semantic ContractとRepresentation Profileを同一視しない。
- Contract Definitionとschema / implementationの権威関係を混同しない。
- 原文自体がEvidenceとなるhistorical資料や固定fixtureは、理由なく改変しない。
- 再ドラフト後に、技術的意味・条件・例外・Evidence強度が変わっていないことを確認する。
- current branchに存在する対象開発文書を確認し終えるまで、本IssueをResolvedにしない。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としません。また、読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしません。

自然な日本語と技術的精度を両立させます。

## Natural Japanese review

Product / Plan / Requirements / Architecture / Contractsのcurrent到達点をactual branchへ戻って確認し、完了済みDesign baselineと未完了Executable作業を分けて進捗を再構成しました。その後、監査範囲、Evidence強度、未完了条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
