# ISSUE-000032: current Contractから最小runtime vertical sliceを定義する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0019, ADR-0021**  
Updated: 2026-08-31

## Goal

current `runtime/`をactual repositoryへ実体化する前に、Product Value、REQ、Reference Architecture、Contract v1alpha1から、最初に実装すべき最小vertical sliceとruntime / Provider境界を定める。

historical M48〜M50 Go candidateのpackage構成をそのまま復元せず、current Contractで必要性を確認できる機能だけを再導出する。

## Background

2026-08-31時点で、actual repositoryには次が存在する。

```text
Product Value
  → REQ / SCN
  → ADR
  → Reference Architecture
  → Contract Definition
  → JSON Schema / semantic validator / fixture
```

Requirements RegistryとContract ConformanceはGitHub Actionsでfixture-scoped Executable Evidenceを得ている。

一方、rootにはcurrent `runtime/`が存在しない。

この段階で旧Go candidateを一括コピーすると、historical package layoutやMilestone分割がcurrent Architecture concernと一対一に固定される危険がある。

## Questions

1. current runtimeが所有すべき最小責務は何か。
2. Contract DTO / wire representationとruntime domain APIをどう分けるか。
3. Semantic Reference、Decision Memory、Capability Observation、Semantic Interchangeをどの粒度でruntimeへ実装するか。
4. Representation Profile未安定の状態でExact Bindingをどこまで実装するか。
5. Provider adapterをruntime Coreからどう分離するか。
6. 最初のvertical sliceでExecutionを扱う必要があるか。
7. historical Go candidateから何を再利用できるか。
8. runtime implementationが新しいsemantic authorityにならないため、どのconformanceを必須にするか。

## Constraints

- runtime struct / package layoutをProduct ontologyにしない。
- JSON Schemaだけをsemantic authorityにしない。
- GoをUniversal semantic requirementにしない。
- current runtimeへworkflow engine、queue、retry、agent-turn routingを便宜で追加しない。
- Recommendation / Decision / Authority / Action Intent / Executionを統合しない。
- Capability ObservationをMatching / Choice / Executionへ自動昇格しない。
- Provider-specific schemaをUniversal runtime structへ無条件にコピーしない。
- stable Representation Profile未確定のままJCS / SHA-256をhard-codeしない。
- historical local PASSをcurrent runtime PASSへ継承しない。

## Proposed first vertical slice

最初のruntime sliceは**read / validate / reconstruct**を中心とし、外部Action実行を含めない。

候補:

1. Semantic Interchange v1alpha1を読み込む。
2. recordのContract identity / versionを解決する。
3. Logical Reference / Exact Binding metadataを保持する。
4. Capability ObservationをProvider-neutralなruntime viewへ読み込む。
5. Decision Memoryをbasis / unresolved / Recommendation relationとともに読み込む。
6. bundle内exact recordとDecision basisの整合を検証する。
7. unknown nested Contractを`not_verified`として保持する。
8. historical Decision reconstruction用のread modelを返す。
9. original semantic recordsをlossなく再exportできることを確認する。

```text
read / validate / reconstruct
  != authorize
  != execute
```

## Runtime language

current implementation laneではGoを第一候補とする。ただし、これは実装上の選択でありProduct ValueやContractの意味には含めない。

```text
Go runtime implementation != SOZA semantic identity
```

将来別言語実装が同じContract conformanceを満たすことを妨げない。

## Provider boundary candidate

Provider adapterは、Provider固有stateを直接SOZA Core structへコピーする層ではない。

```text
Provider state
  → adapter / mapping
  → Capability Observation
  → Matching / Decision may consume
```

最初のvertical sliceでは、production TEI adapterを必須にせず、synthetic Provider fixtureからCapability Observationへ変換するadapter interface / test doubleを候補とする。

実Provider統合は、runtime Contract boundaryが安定してから別Issueで進める。

## Exact Binding boundary

current runtimeはExact Bindingのmetadataを保持・比較できる必要がある。

一方、stable Representation Profile verifierはISSUE-000009がBlockedであるため、最初のsliceで特定canonicalization / digest algorithmをUniversal defaultにしない。

候補:

```text
RepresentationVerifier interface
  verify(profile identity, payload, digest)
```

unknown / unavailable verifierは`not_verified`を返し、digest mismatchの`failed`と区別する。

具体interface shapeはADR確定後のimplementationで決める。

## Required deliverables

- current runtime責務境界
- first vertical slice scope
- runtime / Contract authority boundary
- Provider adapter boundary
- Exact Binding verifier boundary
- historical Go candidate reuse rule
- runtime acceptance scenarios
- ADR

## Acceptance

### Semantic / Design Acceptance

- [ ] runtimeが所有する責務と所有しない責務を明示できる。
- [ ] first vertical sliceがcurrent Contractから追跡できる。
- [ ] Executionを先行実装しない理由が明確である。
- [ ] Provider adapterがSOZA Universal CoreへProvider schemaを漏らさない。
- [ ] stable Representation Profile未確定状態を尊重している。
- [ ] Go implementationとSOZA semantic identityを分離している。
- [ ] historical candidate再利用規則を定めている。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行っている。

### Executable Acceptance

本Issueでは要求しない。runtime implementationとend-to-end conformanceは後続Issueへ分離する。

## Dependencies

- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
- `contracts/CONTRACT_CATALOG.md`
- `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`
- ADR-0014
- ADR-0019
- ADR-0021
- ISSUE-000009
- ISSUE-000022

## Natural Japanese review

current actual tree、Contract v1alpha1、fixture-scoped Executable Evidence、runtime未実体化状態を戻り照合し、最初のruntime sliceを「read / validate / reconstruct」へ限定する候補を整理した。その後、未決点を勝手に実装仕様へ固定せず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
