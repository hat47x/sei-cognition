# ISSUE-000032: current Contractから最小runtime vertical sliceを定義する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0019, ADR-0021, ADR-0022**  
Updated: 2026-08-31

## Goal

current `runtime/`をactual repositoryへ実体化する前に、Product Value、REQ、Reference Architecture、Contract v1alpha1から、最初に実装すべき最小vertical sliceとruntime / Provider境界を定める。

historical M48〜M50 Go candidateのpackage構成をそのまま復元せず、current Contractで必要性を確認できる機能だけを再導出する。

## Resolution

ADR-0022で、最初のruntime sliceを**read / validate / reconstruct**へ限定した。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
```

### Runtimeが最初に扱う意味

- Semantic Interchange v1alpha1
- Contract identity / version
- Logical Reference
- Exact Binding metadata
- Decision / Recommendation
- unresolved state
- Capability Observation
- bundle内exact reference整合
- unknown Contract / Profileの`not_verified`
- historical reconstruction
- semantic recordのlosslessな再export

### first sliceへ含めないもの

- Authorization enforcement
- Action Intent dispatch
- workflow / queue / retry
- autonomous planning
- Provider execution session
- deployment lifecycle
- automatic best-candidate selection
- stable JCS verifier

### Runtime / Contract authority

runtime structやpackage layoutをsemantic authorityにしない。

```text
Runtime type != Contract semantic authority
```

実装とContractが矛盾した場合は、実装都合で意味を変更せず、Product Value、REQ、ADR、Contractへ戻る。

### Go implementation boundary

current implementation laneはGoを基本とするが、Go自体をSOZA semantic identityへ含めない。

```text
Go implementation != SOZA semantic identity
```

別言語実装が同じContract conformanceを満たすことを妨げない。

### Provider boundary

Provider固有stateはadapter / mappingを通してCapability Observationへ変換する。

```text
Provider state
  → Adapter / Mapping
  → Capability Observation
  → Matching / Decision may consume
```

production TEI adapterをfirst sliceの必須条件にはしない。synthetic Provider inputでruntime境界を検証してから実Provider統合へ進む。

### Exact Binding boundary

runtimeはExact Binding metadataとbinding同値性を扱うが、stable verifierを先取りしない。

ISSUE-000009が未解決であるため、JCS / SHA-256等をUniversal defaultへhard-codeしない。

verifier不在や未知Profileは`not_verified`、実際の不一致は`failed`として分ける。

### historical Go candidate

historical codeはcurrent Contractへ照合して必要部分だけ再利用する。

```text
historical code exists != current runtime adopted
```

Milestone名、old package identity、old field、old Evidence stateを自動継承しない。

## Acceptance

### Semantic / Design Acceptance

- [x] runtimeが所有する責務と所有しない責務を明示した。
- [x] first vertical sliceをcurrent Contractから追跡できる。
- [x] Executionを先行実装しない理由を明示した。
- [x] Provider adapterがUniversal CoreへProvider schemaを漏らさない境界を定めた。
- [x] stable Representation Profile未確定状態を尊重した。
- [x] Go implementationとSOZA semantic identityを分離した。
- [x] historical candidate再利用規則を定めた。
- [x] 自然な日本語全文再ドラフトと最終意味監査を完了した。

### Executable Acceptance

本Issueでは要求しない。actual runtime implementationとend-to-end conformanceはISSUE-000033で追跡する。

## Evidence / Follow-up

- ADR-0022
- ISSUE-000033 — runtime implementation
- ISSUE-000009 — stable Representation Profile
- ISSUE-000022 — repository baseline全体

## Natural Japanese review

ADR-0022へ戻ってruntime責務、Provider境界、Exact Binding未確定範囲、historical code再利用規則を再確認した。その後、実装詳細を先取りせず、意味と制約を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
