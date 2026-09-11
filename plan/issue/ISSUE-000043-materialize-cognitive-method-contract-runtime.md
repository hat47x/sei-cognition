# ISSUE-000043: Cognitive Method Contractとfirst runtime sliceを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0022, ADR-0025**  
Updated: 2026-09-01

## Goal

ADR-0025に基づき、`sei.cognitive-method/v1alpha1`のContract Definition、machine-readable schema、fixture、semantic validator、Go runtime read / validate / reconstructをactual repositoryへ実体化し、SCN-0005 / SCN-0015に最初のExecutable Evidenceを与える。

このIssueではCognitive Methodを実行するengineは作らない。SEIが耐久的に保持すべき**Method Definition / Realization / Applicationの意味と来歴**を、特定Promptやprivate chain-of-thoughtへ依存せずportableに読み直せることをfirst sliceとする。

## Resolution

Cognitive Methodを5番目のcurrent Semantic Contract familyとして実体化し、Contract / Schema / fixture / semantic validator / typed runtime / Traceability / Scenario Evidenceまで接続した。

current Contract:

```text
sei.cognitive-method/v1alpha1
```

record type:

```text
method_definition
method_realization
method_application
```

次の意味境界を維持する。

```text
Method Definition != Realization != Method Application
Pattern != Cognitive Method
Pattern match != Recommendation != Decision
Method Application != Assurance
Method Application != Authority != Execution
Logical Reference != Exact Historical Binding
not_verified != failed
```

Realizationがrecord上で省略されていても、Realizationが存在しない、またはMethodが適用されていないという否定事実へ変換しない。

## Contract / Fixture Evidence

current Contract Catalog / Traceabilityでは、Cognitive Methodについて次をactual materialとして扱っている。

- human-readable Contract Definition
- `cognitive-method.schema.json`
- C1〜C8 positive / boundary fixture
- Method ApplicationへのDecision / Assurance / Pattern固有field混入を拒否するnegative fixture
- Method / Application required-reference欠落を拒否するfixture
- unknown `sei.cognitive-method/v1alpha2`をknown versionへ昇格させず、Interchangeでopaque + `not_verified`として保持するfixture

Contract Conformance:

- Run `33467838961`: **success**
- current fixture baseline: **31**（Cognitive Methodを含む5 Contract family）

fixtureのPASSはMethod execution、Method品質、Assuranceを実証しない。

## Runtime Evidence

Go semantic runtimeで、少なくとも次を確認した。

- C1〜C7 standalone documentのtyped load
- C8 Semantic Interchange nested Method Applicationのtyped load
- Method Definition / Realization / Applicationの区別
- original Interchange bytesのlossless export
- Realization省略を勝手に補完しないこと
- Exact-bound Method / Realization Referenceの保持
- Pattern相当の外部Artifactをinput Referenceとして保持すること
- output / residual Referenceの保持
- unknown Method Contract versionをopaque + `not_verified`として保持すること
- Method ApplicationをRecommendation / Decision / Authority / Execution / Assuranceへ昇格させないこと
- private chain-of-thoughtを入力契約として要求しないこと

Semantic Runtime Conformance:

- Run `33467838941`: **success**

さらにSCN-0018のProduct Journey harnessでは、Cognitive Method ApplicationをRecommendation / Decisionと別recordのままend-to-end経路へ接続できることを確認している。

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
- [x] Method ApplicationへのDecision / Assurance等の混入を拒否できる。
- [x] Application without Realizationを否定事実へ変換しない。
- [x] exact-bound Method / Realization Referenceを読み直せる。
- [x] `go test ./...`とContract Conformanceがactual CIでsuccessする。

### Evidence update

- [x] SCN-0005 / SCN-0015を確認済み範囲だけ`Partially Satisfied`へ更新した。
- [x] REQ-0004のExecutable Evidenceを確認済み範囲だけ`Partially Satisfied`へ更新した。
- [x] REQ-0015 / REQ-0021を、private chain-of-thought非依存、交換可能なRealization境界の確認範囲だけ再評価した。
- [x] Product Value TraceabilityへCognitive Method first sliceを反映した。
- [x] Contract Catalog / Traceabilityとruntime Evidenceをcurrent実体へ更新した。

## Evidence state

- Design Evidence: **Satisfied for the current Cognitive Method boundary**
- Executable Evidence: **Partially Satisfied for SCN-0005 / SCN-0015**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
Cognitive Method Contract / typed read PASS
  != Method execution verified
  != production Realization replacement verified
  != Pattern matching workflow verified
  != Method quality / Assurance verified
```

## Non-goals / follow-up

本Issueでは次を完了扱いにしない。

- Method execution engine
- Prompt orchestration
- private chain-of-thought保存
- KJ法等の特定MethodのUniversal Core化
- TEI Pattern catalog / Pattern matchingのproduction統合
- Method quality / truth / assurance score
- production UI / Method Provider
- Release / Operational / Adoption / Outcome Evidence

SCN-0018のend-to-end接続はISSUE-000050で扱い、Product InteractionはISSUE-000045へ分離している。cross-contract Exact Binding一般化はISSUE-000049で扱う。

## Reopen conditions

次の場合は再開を検討する。

- current Cognitive Method ContractではMethod / Realization / Applicationの意味差を保持できなくなった。
- production Realization交換でportable semantic recordに不足する新しい意味差が確認された。
- PatternとCognitive Methodの分離をcurrent Contract / runtimeで維持できなくなった。
- unknown versionやExact Bindingの扱いが他Contract familyと整合しなくなった。

Method executorを実装するという理由だけでは、このIssueを再開しない。

## Natural Japanese review

REQ-0003 / 0004 / 0015 / 0016 / 0021、SCN-0005 / 0015 / 0018、ADR-0017 / 0025、Contract Catalog / Traceability、31 fixtureのContract Conformance、Go typed runtime、Product Journey harnessを相互照合した。作業開始時の未完了checklistをactual repositoryの実体へ戻して監査し、確認できた範囲だけをExecutable Evidenceとして`Partially Satisfied`へ更新した。Method executionやPattern matching、production Realization交換、AssuranceへEvidenceを広げず、意味、Acceptance強度、非対象を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
