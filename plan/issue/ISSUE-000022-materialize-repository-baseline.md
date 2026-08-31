# ISSUE-000022: SOZA repositoryの基線ファイルを実体化し、Evidence claimを再整合する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`に、Product Valueから追跡可能なRequirements、Architecture、Contracts、Fixtures、Runtime、Tools等を、現在のProduct Boundaryへ合わせて段階的に実体化する。

同時に、「historical candidate / Library資産」と「GitHub actual repositoryで再現したcurrent Evidence」を分け、READMEや計画文書の達成主張をactual treeへ一致させる。

## 2026-08-31 current actual tree

`develop/v0.1.0`のrootには現在、次が実体化されている。

```text
.github/
product/
requirements/
architecture/
contracts/
fixtures/
plan/
tools/
```

`runtime/`はまだcurrent baselineとして実体化されていない。

## Current baseline

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
- registry checker / negative self-test
- GitHub Actions `Requirements Registry Conformance`

### Architecture

- `architecture/README.md`
- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
- `architecture/TRACEABILITY.md`
- `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

### Contracts

current Contract 4 family:

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

加えて、

- Contract Catalog / Traceability
- historical contract mapping
- Representation Profile boundary
- JSON Schema v1alpha1
- 17 positive / negative / boundary fixture
- semantic conformance checker
- GitHub Actions `Contract Conformance`

を実体化した。

### Capability Observation

ISSUE-000024のF1〜F7をactual fixtureとして実体化し、current Contract / schema / semantic validatorで検証した。

### Plan

- ADR-0001〜ADR-0021
- ISSUE-000001〜ISSUE-000031
- plan registry / integrity checker
- development workflow
- document authoring standard

## Current Evidence state

### A. Design Evidence

次のcurrent Design traceがactual repositoryに存在する。

```text
Product Value
  → REQ / SCN
  → ADR
  → Reference Architecture
  → Contract Definition
```

historical M48〜M50等の文書は意味核・反例・設計系譜として利用するが、Milestone identity、field、package、algorithm、Evidence stateをcurrentへ自動継承していない。

### B. Fixture-scoped Executable Evidence

current actual repositoryで次を再現できた。

#### Requirements Registry

GitHub Actions Run ID `33346697016`:

```text
PASS: requirements registry checker self-tests
PASS: 22 requirements / 17 scenarios
```

確認範囲はstable ID、相互参照、Value Axis、status / Evidence vocabulary、historical ID混入等のregistry構造である。

#### Contract Conformance

GitHub Actions Run ID `33346472419`:

- 4 Contract v1alpha1 schema
- 17 fixture
- expected PASS / Schema FAIL / Semantic FAIL / `not_verified`
- overall `passed = true`

詳細は`contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`を正とする。

#### Capability Observation

F1〜F7で、partial degradation、proposed / actual、Environment binding、observation gap、cross-provider comparison、historical reconstruction、selective disclosureを確認した。

### C. Historical / Library candidate Evidence

旧runtime、fixtures、generated summaries、local PASS等はhistorical evidence / 再利用候補として保持する。

```text
historical PASS != current PASS
```

current repositoryへ取り込み、current Product / REQ / ADR / Contractへ再照合し、current gateを通すまでExecutable Evidenceへ昇格しない。

### D. Release / Operational Evidence

現時点では主張しない。

## Phase progress

### Phase 1 — Product / Plan

状態: **主要Design baseline完了。全文日本語監査はISSUE-000015で継続。**

### Phase 2 — Requirements

状態: **Design + registry structural Executable baseline完了。**

- ISSUE-000025: Resolved
- ISSUE-000026: Resolved
- ISSUE-000027: Resolved

### Phase 3 — Architecture

状態: **Design baseline完了。**

- ISSUE-000028: Resolved
- ISSUE-000029: Resolved

### Phase 4 — Contracts / Fixtures

状態: **Design + fixture-scoped Executable baseline完了。**

- ISSUE-000030: Resolved
- ISSUE-000031: Resolved
- ISSUE-000024: Resolved

ただしstable Representation Profileは未完了である。

### Phase 5 — Runtime / Provider integration

状態: **未着手またはcurrent actual baseline未実体化。次の主要slice。**

必要な作業:

1. current Contractから必要最小限のruntime boundaryを導出する。
2. historical Go candidateを一括コピーせず、current Contractへ再照合する。
3. Decision Memory / Capability Observation / Semantic Referenceのproduction representationを実装する範囲を決める。
4. Provider adapterの最小vertical sliceを設計する。
5. runtime implementationをProduct ontologyにしない。

### Phase 6 — Exact Binding stable Representation Profile

状態: **Blocked — ISSUE-000009。**

current Contract fixtureではopaqueな`fixture.raw-json/v0`をexact-reference整合確認に利用したが、これはstable Representation Profileではない。

残る中心:

- historical M47 digest規則の確認と正しいmapping
- stable JCS verifier選定 / RFC test vector適合
- high-precision semantic value境界
- verifier / payloadが失われたhistorical bindingのactual運用

### Phase 7 — Evidence closure / release

runtime / Provider integrationとstable Representation ProfileのEvidenceが揃った後に、release candidateとしてのscopeを改めて定める。

Operational Evidenceは別段階で扱う。

## Constraints

- historical candidateのPASSをcurrent PASSへ自動継承しない。
- 存在しないM47 regressionをPASS扱いしない。
- READMEやContract Definitionの存在をExecutable Evidenceとしない。
- TEI実装をSOZA実装の代替Evidenceにしない。
- schema / generated codeをsemantic authorityにしない。
- JCS、SHA-256、JSON等をProduct Value上の理由なしにUniversal meaningへ昇格させない。
- fixture-scoped PASSをrelease / operational coverageへ広げない。
- runtime component構成をArchitecture concernと一対一に固定しない。

## Completion criteria

### Design baseline

- [x] Product ValueからRequirements / ADRまで追跡できる。
- [x] RequirementsからArchitectureへ追跡できる。
- [x] ArchitectureからContractへ追跡できる。
- [x] historical mappingをcurrent正本から分離した。
- [x] current文書を自然な日本語で再ドラフトする工程を適用した。

### Executable baseline — registry / contract / fixture

- [x] Requirements registry checkerをactual treeで再現できる。
- [x] Contract conformanceをactual treeで再現できる。
- [x] Capability Observation F1〜F7をactual treeで検証できる。
- [x] expected negative / boundary caseを検査できる。
- [x] actual repositoryで実行したEvidenceとhistorical candidateを分離できる。

### Executable baseline — remaining

- [ ] current `runtime/` baselineを実体化する。
- [ ] Provider adapter / runtime vertical sliceをcurrent Contractへ接続する。
- [ ] ISSUE-000009のstable Representation Profileをactual implementationで検証する。
- [ ] runtimeとContract fixtureを横断するend-to-end conformanceを構築する。

### Evidence closure

- [ ] READMEをcurrent Executable baselineへ同期する。
- [ ] Requirement文書の「未実体化」記述をcurrent treeへ同期する。
- [ ] Decision Memory / Capability Observation production implementation開始範囲をcurrent Evidenceから確定する。
- [x] release / operational Evidenceを未確認のまま引き上げていない。

## Immediate next work

1. README / Requirementsのcurrent Evidence記述を同期する。
2. runtime / Provider integrationの最小vertical sliceをIssue / ADRで設計する。
3. historical Go candidateから再利用可能な意味・実装をcurrent Contractへ差分評価する。
4. ISSUE-000009でstable Representation Profileを進める。
5. ISSUE-000015で新規Contract / Fixture / Toolを含む自然な日本語監査を継続する。

## Natural Japanese review

Requirements Registry、Contract Conformance、Capability Observation F1〜F7のactual CI Evidenceとroot treeを再確認し、完了したfixture-scoped Executable領域と未実体化のruntime / stable Representation Profileを再分類した。その後、Evidenceの高さと残作業の境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
