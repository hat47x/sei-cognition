# ISSUE-000022: SOZA repositoryの基線ファイルを実体化し、Evidence claimを再整合する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0018**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`に、Product Valueから追跡可能なRequirements、Architecture、Contracts、Fixtures、Runtime、Tools等を、現在のProduct Boundaryへ合わせて段階的に実体化する。

同時に、「過去candidate bundleやLibrary上に資産が存在すること」と「GitHub actual repositoryに実装・検査資産が存在すること」を分け、READMEや計画文書のEvidence claimをactual treeへ一致させる。

## 2026-08-31 actual tree audit

`develop/v0.1.0`について、GitHub actual treeを直接確認した。

現時点で確認できる基線:

- `product/` — Product Value / Value Model / Value Acceptance / Vision / Principlesを整備中
- `plan/` — ADR / Issue / registry / planning conventionを整備中

現時点でactual directoryが存在しないことを確認したもの:

- `requirements/`
- `architecture/`
- `contracts/`
- `runtime/`
- `tools/`

したがって、repository READMEに列挙されているこれらのファイルや検査コマンドを、**actual repositoryに存在するEvidenceとして扱ってはならない。**

READMEはhistorical candidateの目録を含むが、現行actual treeの案内としてはstaleである。

## Current evidence state

現時点では、次を明確に分ける。

### A. Actual repository design evidence

GitHub actual treeに存在するProduct / Plan文書。

これはDesign Evidenceであり、Executable Evidenceではない。

### B. Historical / Library candidate evidence

過去candidate bundle、runtime、fixtures、generated summaries、local PASS等。

これらは再利用候補・historical evidenceとして価値があるが、actual repositoryへ取り込む前に最新Product Value / ADRへ再照合する。

### C. Actual repository executable evidence

現時点では、READMEが列挙するGo module、runtime、fixtures、tools、conformance gateについてactual tree上の存在を確認できないため、成立を主張しない。

### D. Release / Operational evidence

現時点では主張しない。

## Required work

### Phase 1 — Product / Plan baseline

1. Product Value / Value Model / Value Acceptance / Vision / Principlesを整備する。
2. ADR / Issue / registryを最新Product Valueへ再照合する。
3. 自然な日本語ドラフト工程を全active文書へ適用する。

状態: **進行中。Product Value層とADR-0019までを大きく前進。**

### Phase 2 — Requirements baseline

1. Product Value V1〜V8からProduct Requirementsを再導出する。
2. 過去candidateのRequirementをそのまま正本にせず、current valueとの対応を再評価する。
3. Design AcceptanceとExecutable Acceptanceを分ける。
4. Acceptance Scenarioをactual repositoryへ実体化する。

この作業は`ISSUE-000025`で独立追跡する。

### Phase 3 — Architecture / Contracts baseline

1. current RequirementsとADRからArchitectureを再構成する。
2. old candidate architectureを差分材料として監査する。
3. Universal Core / Profile / Provider / Adapter境界を再確認する。
4. schema / contractを現在の意味境界へ合わせて実体化する。

### Phase 4 — Runtime / Fixtures / Tools

1. historical candidateから再利用可能な実装を選別する。
2. Go module、package、schema、fixtures、test toolsをactual treeへ追加する。
3. 存在するgateだけをREADMEへ列挙する。
4. actual repository上で再現可能なExecutable Evidenceを初めて記録する。

### Phase 5 — README / Evidence claim closure

1. READMEの「現在地」をactual treeへ一致させる。
2. historical candidateの目録はhistoryとして分離する。
3. 実在しないファイルやgateを「読む順序」「実行可能な検査」として列挙しない。
4. Design / Executable / Release / Operational Evidenceを分離して表示する。

## Constraints

- Library candidateのPASSをactual repository PASSへ自動継承しない。
- 存在しないM47 regressionをPASS扱いしない。
- READMEの記述を実装存在のEvidenceとしない。
- 旧bundleを無検査で一括コピーしない。
- TEI実装をSOZA実装の代替Evidenceにしない。
- 文書・コードとも、最新Product Value、Value Acceptance、ADR、SOZA↔TEI Product Boundaryを優先する。
- Design Evidenceしかない段階でExecutable Evidence以上を主張しない。

## Completion criteria

### Design baseline

- [ ] Product ValueからRequirements / ADRまで追跡できる。
- [ ] `requirements/`がactual treeに存在する。
- [ ] current Product RequirementsとAcceptance Scenariosが自然な日本語監査済みである。
- [ ] current RequirementsからArchitecture / Contractsへ追跡できる。

### Executable baseline

- [ ] READMEで参照する必須runtime / fixture / toolがactual treeに存在する。
- [ ] actual repository上で実行可能なgateだけを列挙できる。
- [ ] actual repo evidenceとhistorical/local candidate evidenceが明確に分離される。
- [ ] ISSUE-000009の残件をactual treeで検証できる入口がある。
- [ ] ISSUE-000024のCapability Observation fixtureをactual treeで検証できる。

### Evidence closure

- [ ] READMEがactual treeと一致する。
- [ ] M49 / M50以降のproduction implementationを開始できるか、現在Evidenceから再判断できる。
- [ ] release / operational evidenceを未確認のまま引き上げていない。

## Immediate next work

1. `ISSUE-000025`でRequirements baselineの構造と導出規則を確定する。
2. Product Value V1〜V8からcurrent Product Requirementを再構成する。
3. その後にArchitecture / Contractsをactual treeへ入れる。
4. READMEの大幅更新は、少なくともRequirements baselineの実体化後に行う。ただし、それ以前でも誤解を招く重大なclaimは必要に応じて縮小する。

## Natural Japanese review

actual treeを直接確認し、過去candidateの記述と現在の実在状態を分けたうえで構造を作り直した。その後、Evidenceの高さと作業順序を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
