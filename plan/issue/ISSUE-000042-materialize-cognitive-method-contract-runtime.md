# ISSUE-000042: Cognitive Method Contractとfirst runtime sliceを実体化する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0022, ADR-0025**  
Updated: 2026-09-01

## Goal

ADR-0025に基づき、`soza.cognitive-method/v1alpha1`のcurrent Contract Definition、machine-readable schema、fixture、semantic validator、Go runtime read / validate / reconstructをactual repositoryへ実体化し、SCN-0005 / SCN-0015の最初のExecutable Evidenceを得る。

このIssueではMethodの実行engineを作らない。SOZAが耐久的に保持すべき**Method Definition / Realization / Applicationの意味と来歴**をportableに読めることをfirst sliceとする。

## Why now

v0.1.0では、Contract / runtime / Provider Observation / Exact Binding / Projectionの基線を作り、release candidate gateまで整備した。

一方、SCN-0005とSCN-0015はExecutable Evidenceが`Not Yet Verified`のままであり、Cognitive MethodはSOZAがexecution runtimeより上位で保持する認知・判断層の中核concernである。

次版でStorageやExecution Providerの実差し替えを先に進めるより、SOZA本体の認知境界を先にExecutableへ落とす方がProduct Valueに近い。

## Scope

### Contract

新設:

```text
contracts/cognitive-method/SOZA_COGNITIVE_METHOD_v1alpha1.md
contracts/schemas/v1alpha1/cognitive-method.schema.json
```

record type:

```text
method_definition
method_realization
method_application
```

### Fixtures

少なくとも次を用意する。

#### positive

1. Method Definition
2. 一つのMethodをPrompt / code等とは独立したRealizationとして参照するrecord
3. Realizationを明示したMethod Application
4. Realizationを省略したMethod Application
5. inputにdomain-specific Pattern相当の外部Referenceを持つApplication
6. Exact Bindingで特定Method / Realization revisionへ結び付くApplication
7. output / residualを別Artifact Referenceとして保持するApplication

#### negative / boundary

1. Method Applicationへ`decision`を埋め込むrecordを拒否する。
2. Method Applicationへ`assurance`を埋め込むrecordを拒否する。
3. Method Realizationが`method_ref`を持たないrecordを拒否する。
4. ApplicationがMethod Definitionを欠くrecordを拒否する。
5. Pattern固有Universal fieldをMethod recordへ混入させるrecordを拒否する。
6. unknown `soza.cognitive-method/v1alpha2`をknown v1alpha1として読まず、Semantic Interchangeではopaque + `not_verified`として保持する。

### Runtime

`runtime/go/semanticruntime`へcurrent `v1alpha1`だけのtyped read modelを追加する。

- standalone Contract documentをload / validateできる。
- Semantic Interchange nested recordをload / validateできる。
- Method Definition / Realization / Applicationを区別して復元できる。
- logical / exact Referenceを既存型で再利用する。
- unknown versionはopaque + `not_verified`を維持する。
- original payload / bundleを勝手にnormalize・rewriteしない。
- Method ApplicationからRecommendation / Decision / Authority / Execution / Assuranceを生成しない。
- private chain-of-thoughtを入力契約に要求しない。

## Semantic invariants

```text
Method Definition != Realization != Method Application
Pattern != Cognitive Method
Pattern match != Recommendation != Decision
Method Application != Assurance
Method Application != Authority != Execution
Logical Reference != Exact Historical Binding
not_verified != failed
```

さらに、次を守る。

```text
realization omitted
  != realization absent
  != method not applied
```

## Non-goals

- Methodを実際に実行するworkflow / agent engine
- Prompt orchestration
- private chain-of-thought保存
- KJ法等の特定MethodをUniversal Coreへ固定すること
- Pattern catalogのSOZA Core化
- Method quality / truth / assurance score
- production UI
- production Method Provider
- historical M47 digest ruleの推測復元

## Acceptance criteria

### Design Evidence

- [x] ADR-0025でportable boundaryをAcceptedした。
- [ ] Contract Definitionをcurrent Architecture / Requirementsへtraceできる。
- [ ] Contract Catalog / Traceabilityを5 family基線へ更新する。

### Executable Evidence

- [ ] JSON Schemaで3 record typeを検証できる。
- [ ] positive / boundary / negative fixtureをactual checkerで検証できる。
- [ ] standalone Cognitive Method documentをGo runtimeでload / reconstructできる。
- [ ] Semantic Interchange nested Cognitive Method recordをGo runtimeでload / reconstructできる。
- [ ] unknown Method Contract versionをopaque + `not_verified`として保持できる。
- [ ] Method ApplicationにDecision / Assurance等を混入させるfixtureを拒否できる。
- [ ] Application without Realizationを否定事実へ変換しない。
- [ ] exact-bound Method / Realization Referenceを読み直せる。
- [ ] `go test ./...`とContract Conformanceがactual CIでsuccessする。

### Evidence update

- [ ] SCN-0005 / SCN-0015を実際に確認できた範囲だけ`Partially Satisfied`へ更新する。
- [ ] REQ-0004のExecutable Evidenceを実際に確認できた範囲だけ更新する。
- [ ] REQ-0015 / REQ-0021のEvidenceを過大主張せず再評価する。
- [ ] Product Value Traceabilityへv0.2.0 first sliceを反映する。
- [ ] runtime / Contract Evidence文書を更新する。

### Release / Operational / Outcome

- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

このIssueをResolvedにしても、上記3段階を自動的にSatisfiedへ上げない。

## Implementation order

1. Contract Definition
2. JSON Schema
3. fixtures / contract checker
4. Go model
5. standalone loader
6. Interchange nested loader
7. runtime tests
8. traceability / Evidence更新
9. 自然な日本語全文再ドラフト
10. CI success確認

CI failureを検出した場合は、その原因を解消してsuccessを確認してから後続作業へ進む。

## Natural Japanese review

REQ-0003 / 0004 / 0015 / 0016 / 0021、SCN-0005 / 0015、ADR-0017 / 0025、Reference Architecture、Contract Catalog、Historical Contract Mapping、current runtime loaderを照合し、first sliceの範囲を実行engineではなくportable semantic read / validate / reconstructへ限定した。その後、実装順序、Acceptance、非対象、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
