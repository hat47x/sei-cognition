# ISSUE-000043: Cognitive Method Contractとfirst runtime sliceを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0022, ADR-0025**  
Updated: 2026-09-01

## Goal

ADR-0025に基づき、`soza.cognitive-method/v1alpha1`のcurrent Contract Definition、machine-readable schema、fixture、semantic validator、Go runtime read / validate / reconstructをactual repositoryへ実体化し、SCN-0005 / SCN-0015の最初のExecutable Evidenceを得る。

このIssueではMethodの実行engineを作らない。SOZAが耐久的に保持すべき**Method Definition / Realization / Applicationの意味と来歴**をportableに読めることをfirst sliceとする。

## Why now

v0.1.0では、Contract / runtime / Provider Observation / Exact Binding / Projectionの基線を作り、release candidate gateまで整備した。

一方、SCN-0005とSCN-0015は当初Executable Evidenceが`Not Yet Verified`であり、Cognitive MethodはSOZAがexecution runtimeより上位で保持する認知・判断層の中核concernだった。

次版でStorageやExecution Providerの実差し替えを先に進めるより、SOZA本体の認知境界を先にExecutableへ落とす方がProduct Valueに近いと判断した。

## Scope

### Contract

実体化済み:

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

current C1〜C8では次を検査する。

#### positive / boundary

1. Method Definition
2. Method Realization
3. Realizationを明示したMethod Application
4. Realizationを省略したMethod Application
5. inputにdomain-specific Pattern相当の外部Referenceを持つApplication
6. Exact Bindingで特定Method / Realization revisionへ結び付くApplication
7. output / residualを別Artifact Referenceとして保持するApplication
8. Semantic Interchange nested Method Application

#### negative / unknown-version

1. Method Applicationへ`decision`を埋め込むrecordを拒否する。
2. Method Applicationへ`assurance`を埋め込むrecordを拒否する。
3. Method Realizationが`method_ref`を持たないrecordを拒否する。
4. ApplicationがMethod DefinitionへのReferenceを欠くrecordを拒否する。
5. Pattern固有Universal fieldをMethod recordへ混入させるrecordを拒否する。
6. unknown `soza.cognitive-method/v1alpha2`をknown v1alpha1として読まず、Semantic Interchangeではopaque + `not_verified`として保持する。

### Runtime

`runtime/go/semanticruntime`へcurrent `v1alpha1`のtyped read modelを実体化した。

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
- production Realization交換の実証
- historical M47 digest ruleの推測復元

## Acceptance criteria

### Design Evidence

- [x] ADR-0025でportable boundaryをAcceptedした。
- [x] Contract Definitionをcurrent Architecture / Requirementsへtraceできる。
- [x] Contract Catalog / Traceabilityを5 family基線へ更新した。

### Executable Evidence

- [x] JSON Schemaで3 record typeを検証できる。
- [x] positive / boundary / negative fixtureをactual checkerで検証できる。
- [x] standalone Cognitive Method documentをGo runtimeでload / reconstructできる。
- [x] Semantic Interchange nested Cognitive Method recordをGo runtimeでload / reconstructできる。
- [x] unknown Method Contract versionをopaque + `not_verified`として保持できる。
- [x] Method ApplicationにDecision / Assurance等を混入させるfixtureを拒否できる。
- [x] Application without Realizationを否定事実へ変換しない。
- [x] exact-bound Method / Realization Referenceを読み直せる。
- [x] `go test ./...`とContract Conformanceがactual CIでsuccessする。

正本Evidence同期中のhead `643f3eb00ea836d4ab4b7dc1a916423d8e005912`では、次のCIがすべてsuccessした。

- Contract Conformance Run `33497886978`
- Requirements Registry Conformance Run `33497886995`
- V6 V7 Projection Evaluation Run `33497886908`
- Semantic Runtime Conformance Run `33497887048`
- Plan integrity Run `33497887115`

Cognitive Method実装そのものの代表的な基線Evidenceとして、Contract Conformance Run `33467838961`とSemantic Runtime Conformance Run `33467838941`もsuccessしている。

### CI transition note

Issue本文を先に`Resolved`へ変更した中間commit `be3ce32951fe2cde039f704f2ac0b53b686f8413`では、`plan/registry.yaml`がまだ`In Progress`だったため、Plan integrity Run `33498098681`が次の不一致を正しく検出してfailureとなった。

```text
ISSUE-000043: document='Resolved', registry='In Progress'
```

これはCognitive MethodのContract / runtime Evidenceの退行ではなく、同一closure作業内の一時的な計画状態不整合である。直後のcommit `a752cbab66f0c795346dae5fc7e665a148eb414a`でregistryを`Resolved`へ同期した。最終PR headでは、Issue本文・registry・Product Value Traceabilityが同じcurrent Plan状態を示すことをPlan integrityで再検証してからmergeする。

### Evidence update

- [x] SCN-0005 / SCN-0015を実際に確認できた範囲だけ`Partially Satisfied`へ更新した。
- [x] REQ-0004のExecutable Evidenceを実際に確認できた範囲だけ更新した。
- [x] REQ-0015 / REQ-0021のEvidenceを過大主張せず再評価した。
- [x] Product Value Traceabilityへv0.2.0 first sliceを反映した。
- [x] runtime / Contract Evidence文書を更新した。

### Release / Operational / Outcome

- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

本IssueをResolvedにしても、上記3段階を自動的にSatisfiedへ上げない。

## Resolution

`soza.cognitive-method/v1alpha1`について、Definition / Realization / Applicationを分けたportable Contract、JSON Schema、C1〜C8 fixture、negative / unknown-version境界、Contract checker、Go typed runtime、standalone / Semantic Interchange read / validate / reconstruct、および正本Evidenceの同期が完了した。

これにより、SCN-0005 / SCN-0015とREQ-0004 / REQ-0015 / REQ-0021について、**portable semantic boundaryに限ったfixture-scoped Executable Evidence**を得た。Realizationの省略を否定事実へ変換しないこと、PatternをCognitive Methodへ昇格させないこと、Exact-bound Method / Realization Referenceを保持すること、Method ApplicationをDecision / Assurance等へ昇格させないこと、unknown versionをopaque + `not_verified`として扱うことをactual testで確認している。

一方、Method execution engine、production Method Provider、actual Prompt / model program / human procedureの交換実行、production UI、Method quality / truth / Assurance、Release / Operational / Adoption / Outcomeは本Issueの完了条件ではなく、未検証のまま明示的に残す。

## Evidence state

- Design Evidence: **Satisfied for the current v1alpha1 first-slice boundary**
- Executable Evidence: **Partially Satisfied for related Product Requirements / Scenarios** — fixture-scoped Contract / runtime boundaryをactual CIで検査済み。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

REQ-0003 / 0004 / 0015 / 0016 / 0021、SCN-0005 / 0015、ADR-0017 / 0025、Reference Architecture、Contract Catalog / Traceability、31-fixture Contract Conformance、current semantic runtime、Product Value Traceabilityへ戻り、first sliceの実装内容とEvidenceを再照合した。完了したのはMethod実行そのものではなく、Method Definition / Realization / Applicationのportableな意味と来歴をread / validate / reconstructできる境界である。実際に確認した範囲だけExecutable Evidenceを`Partially Satisfied`として扱い、production Realization交換やRelease以降へは昇格させていない。closure中に検出されたPlan status不整合も、失敗を消さずに原因と是正を記録した。そのうえで、意味、規範強度、非対象範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。