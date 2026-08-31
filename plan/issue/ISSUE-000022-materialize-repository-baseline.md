# ISSUE-000022: SOZA repositoryの基線ファイルを実体化し、Evidence claimを再整合する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`に、Product Valueから追跡可能なRequirements、Architecture、Contracts、Fixtures、Runtime、Tools等を、現在のProduct Boundaryへ合わせて段階的に実体化する。

同時に、「過去candidate bundleやLibrary上に資産が存在すること」と「GitHub actual repositoryに実装・検査資産が存在すること」を分け、READMEや計画文書のEvidence claimをactual treeへ一致させる。

## 2026-08-31 current actual tree

`develop/v0.1.0`で、現在次のDesign baselineを確認できる。

```text
product/
requirements/
architecture/
contracts/
plan/
```

### Product

- Product Value
- Value Model
- Value Acceptance
- Product Vision
- Product Principles

### Requirements

- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017
- historical requirement mapping

### Architecture

- `architecture/README.md`
- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
- `architecture/TRACEABILITY.md`
- `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

### Contracts

- `contracts/README.md`
- `contracts/CONTRACT_CATALOG.md`
- `contracts/TRACEABILITY.md`
- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`
- Representation Profile候補の案内
- historical contract mapping

### Plan

- ADR-0001〜ADR-0021
- ISSUE-000001〜ISSUE-000031
- registry / development workflow / document authoring standard

## Current evidence state

### A. Design Evidence

Product Valueから次まで追跡できるcurrent Design baselineがactual repositoryに存在する。

```text
Product Value
  → REQ / SCN
  → ADR
  → Reference Architecture
  → Contract Definition
```

Requirements、Architecture、Contractはいずれもhistorical candidateを一括コピーせず、current Product Valueと後発ADRへ戻って再構成している。

### B. Historical / Library candidate evidence

過去candidate bundle、runtime、fixtures、generated summaries、local PASS等はhistorical evidenceおよび再利用候補として扱う。

旧field、schema、package、Milestone identity、local PASS、`VERIFIED`等をcurrent Evidenceへ自動継承しない。

### C. Executable Evidence

current actual repositoryでのExecutable Evidenceは、Design baselineより遅れている。

主な未完了slice:

- ISSUE-000027 — Requirements / Scenario registry checker
- ISSUE-000031 — Contract schema / fixture / conformance
- ISSUE-000024 — Capability Observation executable fixture
- ISSUE-000009 — Exact Binding Representation Profile / verifier安定化

Architecture / Contract Definitionが存在することだけでExecutable AcceptanceをSatisfiedにはしない。

### D. Release / Operational Evidence

現時点では主張しない。

## Phase progress

### Phase 1 — Product / Plan baseline

状態: **Design baseline主要部完了。既存文書の全件日本語監査はISSUE-000015で継続。**

Product Value governance、Provider-neutral Capability Observation、Requirements規約、Architecture / Contract authorityまでADR-0021で整備した。

### Phase 2 — Requirements baseline

状態: **Design baseline完了。**

- ISSUE-000025: Resolved
- ISSUE-000026: Resolved
- Executable registry check: ISSUE-000027

### Phase 3 — Architecture baseline

状態: **Design baseline完了。**

- ISSUE-000028: Resolved — Architecture / Contract規約
- ISSUE-000029: Resolved — current Reference Architecture

REQ-0001〜REQ-0022を少なくとも一つのarchitecture concernへ追跡できる。

### Phase 4 — Contract baseline

状態: **Design baseline完了。**

- ISSUE-000030: Resolved
- current Contract 4 familyを`v1alpha1`で実体化
- semantic ContractとRepresentation Profileを分離
- historical Contract mappingを保存
- Executable conformance: ISSUE-000031

### Phase 5 — Executable baseline

状態: **未完了。現在の主要作業。**

1. Requirements registry checkerを実装する。
2. current Contract schema / validator / fixture / conformance runnerを実装する。
3. Capability Observation fixtureをcurrent Contractへ合わせて実体化する。
4. Exact Binding Representation Profileの未決部分を解消する。
5. 必要なruntime / Provider adapter / toolをactual treeへ追加する。
6. actual repository上で再現できる検査だけをREADMEへ列挙する。

### Phase 6 — Evidence closure

READMEはArchitecture / Contract Design baseline実体化後のcurrent stateへ更新した。

今後はExecutable baselineの成立に応じて、Design / Executable / Release / Operationalの各Evidence状態を個別に更新する。

## Constraints

- Library candidateのPASSをactual repository PASSへ自動継承しない。
- 存在しないM47 regressionをPASS扱いしない。
- READMEやContract文書の記述を実装存在のEvidenceとしない。
- 旧bundleを無検査で一括コピーしない。
- TEI実装をSOZA実装の代替Evidenceにしない。
- Schemaやgenerated codeをsemantic authorityにしない。
- JCS、SHA-256、JSON等をProduct Value上の理由なしにUniversal meaningへ昇格させない。
- Design Evidenceしかない段階でExecutable Evidence以上を主張しない。

## Completion criteria

### Design baseline

- [x] Product ValueからRequirements / ADRまで追跡できる。
- [x] Requirements current baselineがactual treeに存在する。
- [x] RequirementsからArchitectureへ追跡できる。
- [x] Architectureから必要なContractへ追跡できる。
- [x] Product / Requirements / Architecture / Contractのcurrent文書を自然な日本語で再ドラフトしている。

### Executable baseline

- [ ] ISSUE-000027のRequirements registry checkerをactual treeで再現できる。
- [ ] ISSUE-000031のContract conformanceをactual treeで再現できる。
- [ ] ISSUE-000024のCapability Observation fixtureをactual treeで検証できる。
- [ ] ISSUE-000009の未決部分を検証できる入口がある。
- [ ] 必要なruntime / fixture / toolがactual treeに存在する。
- [ ] actual repository上で実行可能なgateだけを列挙できる。

### Evidence closure

- [x] READMEがcurrent Design baselineと一致する。
- [ ] actual repo evidenceとhistorical/local candidate evidenceが実装・報告上も明確に分離される。
- [ ] Decision Memory / Capability Choice等のproduction implementation開始可否をcurrent Executable Evidenceから再判断できる。
- [ ] release / operational evidenceを未確認のまま引き上げていない。

## Immediate next work

1. ISSUE-000027 — Requirements registry checker
2. ISSUE-000031 — Contract schema / fixture / conformance
3. ISSUE-000024 — Capability Observation fixture
4. ISSUE-000009 — Representation Profile / Exact Binding verification
5. current runtime / tools baselineの再導入
6. ISSUE-000015 — 新たに追加したArchitecture / Contractを含む文書全体監査

## Natural Japanese review

Architecture / Contract Design baseline実体化後のactual treeへ戻り、完了済みDesign層と未完了Executable層を再分類しました。その後、Evidenceの高さ、作業順序、完了条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
