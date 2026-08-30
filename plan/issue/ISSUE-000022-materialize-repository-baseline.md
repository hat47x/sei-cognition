# ISSUE-000022: SOZA repositoryの基線ファイルを実体化し、Evidence claimを再整合する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`に、Product Valueから追跡可能なRequirements、Architecture、Contracts、Fixtures、Runtime、Tools等を、現在のProduct Boundaryへ合わせて段階的に実体化する。

同時に、「過去candidate bundleやLibrary上に資産が存在すること」と「GitHub actual repositoryに実装・検査資産が存在すること」を分け、READMEや計画文書のEvidence claimをactual treeへ一致させる。

## 2026-08-31 actual tree audit

`develop/v0.1.0`のactual treeを直接確認し、その後Requirements baselineを実体化した。

現在、actual repositoryで確認できる主なDesign baseline:

- `product/`
  - Product Value
  - Value Model
  - Value Acceptance
  - Product Vision
  - Product Principles
- `plan/`
  - ADR / Issue
  - registry
  - planning / document authoring conventions
- `requirements/`
  - `README.md`
  - `PRODUCT_REQUIREMENTS.md`
  - `ACCEPTANCE_SCENARIOS.md`
  - `history/HISTORICAL_REQUIREMENT_MAPPING.md`

一方、current baselineとしてまだ実体化されていない主要領域:

- `architecture/`
- `contracts/`
- `runtime/`
- `tools/`

過去candidate bundleには同名のArchitecture、Contracts、Runtime、Tools等が存在するが、current actual repositoryのEvidenceとしては扱わない。

## Current evidence state

### A. Actual repository Design Evidence

Product、Plan、Requirements文書がactual treeに存在する。

Product Valueからcurrent Requirement、ADRまで追跡できるDesign baselineは成立し始めている。

ただし、Architecture / Contractsがまだcurrent treeにないため、設計全体のclosureは未完了である。

### B. Historical / Library candidate evidence

過去candidate bundle、runtime、fixtures、generated summaries、local PASS等をLibraryから参照できる。

これらはhistorical evidenceおよび再利用候補であり、current Product Value / Requirements / ADRへ再照合してからactual treeへ取り込む。

### C. Actual repository Executable Evidence

現時点では、READMEがhistorical candidateとして列挙するGo module、runtime、fixtures、tools、conformance gateのcurrent actual tree上での成立を主張しない。

Requirements registry checkerについても、Design baselineから分離して`ISSUE-000027`で追跡する。

### D. Release / Operational Evidence

現時点では主張しない。

## Required work

### Phase 1 — Product / Plan baseline

1. Product Value / Value Model / Value Acceptance / Vision / Principlesを整備する。
2. ADR / Issue / registryを最新Product Valueへ再照合する。
3. 自然な日本語ドラフト工程をactive文書へ適用する。

状態: **主要なProduct Value基線とADR-0020までを整備済み。全既存文書監査はISSUE-000015で継続。**

### Phase 2 — Requirements baseline

1. Product Value V1〜V8からProduct Requirementsを再導出する。
2. historical candidate Requirementをcurrent valueへ再評価する。
3. Design AcceptanceとExecutable Acceptanceを分ける。
4. Acceptance Scenarioをactual repositoryへ実体化する。
5. historical IDとのmappingを保存する。

状態: **Design baseline完了。ISSUE-000025 / ISSUE-000026はResolved。**

current baseline:

- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017
- historical requirement mapping

Executable registry checkは`ISSUE-000027`へ分離した。

### Phase 3 — Architecture / Contracts baseline

次の優先作業とする。

1. current RequirementsとAccepted ADRからArchitectureを再構成する。
2. historical candidate architectureを差分材料として監査する。
3. Universal Core / Profile / Provider / Adapter / Projection境界を再確認する。
4. current Contract / schemaを意味境界から再導出する。
5. Architecture / Contract文書を自然な日本語で全文再ドラフトする。
6. Product Value V1〜V8 → REQ → ADR → Architecture / Contractの追跡を作る。

historical candidateを一括コピーせず、現時点で必要な最小Design baselineから再構成する。

### Phase 4 — Runtime / Fixtures / Tools

1. historical candidateから再利用可能な実装を選別する。
2. Go module、package、schema、fixtures、test toolsをactual treeへ追加する。
3. 存在するgateだけをREADMEへ列挙する。
4. actual repository上で再現可能なExecutable Evidenceを初めて記録する。
5. ISSUE-000009、ISSUE-000024、ISSUE-000027のExecutable Acceptanceをactual treeで検証する。

### Phase 5 — README / Evidence claim closure

1. READMEの「現在地」をactual treeへ一致させる。
2. historical candidateの目録はhistory / referenceとして分離する。
3. 実在しないファイルやgateを「現在の読む順序」「実行可能な検査」として列挙しない。
4. Design / Executable / Release / Operational Evidenceを分けて表示する。

Requirements baselineが実体化したため、READMEの大幅なcurrent-state更新を行える段階に入った。

## Constraints

- Library candidateのPASSをactual repository PASSへ自動継承しない。
- 存在しないM47 regressionをPASS扱いしない。
- READMEの記述を実装存在のEvidenceとしない。
- 旧bundleを無検査で一括コピーしない。
- TEI実装をSOZA実装の代替Evidenceにしない。
- 文書・コードとも、最新Product Value、Value Acceptance、Requirements、ADR、SOZA↔TEI Product Boundaryを優先する。
- Design Evidenceしかない段階でExecutable Evidence以上を主張しない。

## Completion criteria

### Design baseline

- [x] Product ValueからRequirements / ADRまで追跡できる。
- [x] `requirements/`がactual treeに存在する。
- [x] current Product RequirementsとAcceptance Scenariosが自然な日本語監査済みである。
- [ ] current RequirementsからArchitecture / Contractsへ追跡できる。

### Executable baseline

- [ ] READMEで参照する必須runtime / fixture / toolがactual treeに存在する。
- [ ] actual repository上で実行可能なgateだけを列挙できる。
- [ ] actual repo evidenceとhistorical/local candidate evidenceが明確に分離される。
- [ ] ISSUE-000009の残件をactual treeで検証できる入口がある。
- [ ] ISSUE-000024のCapability Observation fixtureをactual treeで検証できる。
- [ ] ISSUE-000027のRequirements registry checkerをactual treeで検証できる。

### Evidence closure

- [ ] READMEがactual treeと一致する。
- [ ] Decision Memory / Capability Choice等のproduction implementationを開始できるか、current Evidenceから再判断できる。
- [ ] release / operational evidenceを未確認のまま引き上げていない。

## Immediate next work

1. Architecture / Contracts baselineの構造・正本・追跡規約をADR / Issueで先に定める。
2. current REQ / ADRから最小Architecture baselineを再構成する。
3. historical Architecture / Contract candidateを一件ずつcurrent baselineへ照合する。
4. Requirements registry checkerはISSUE-000027で並行して扱う。
5. READMEをactual Design baselineへ合わせ、historical executable claimをcurrent claimから分離する。

## Natural Japanese review

Requirements baseline実体化後のactual stateへ戻り、完了済みPhaseと未実体化領域を再分類した。その後、Evidenceの高さ、作業順序、完了条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
