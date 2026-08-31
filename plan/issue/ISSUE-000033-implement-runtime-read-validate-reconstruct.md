# ISSUE-000033: read / validate / reconstruct runtime sliceを実装する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0021, ADR-0022**  
Updated: 2026-08-31

## Goal

ADR-0022で確定したfirst runtime sliceをGoでactual repositoryへ実装し、current Contract fixtureをruntimeへ読み込むend-to-end conformanceを構築する。

外部Action実行を先行せず、Semantic Interchange、Decision Memory、Capability Observation、Semantic Referenceの読み込み・意味検査・historical reconstructionを最初のExecutable runtime Evidenceとする。

## Initial scope

### Runtime

候補root:

```text
runtime/go/
```

初期実装で必要な責務:

- Contract identity / version
- Logical Reference
- Exact Binding metadata
- verification outcome vocabulary
- Decision / Recommendation read model
- Capability Observation read model
- Semantic Interchange envelope loading
- unknown nested Contract handling
- same-logical-id lineage invariant
- bundle exact record / Decision basis consistency
- partial knowledge preservation

### Out of scope

- Authorization enforcement
- Action Intent dispatch
- workflow / queue / retry
- autonomous planning
- Provider execution session
- deployment lifecycle
- production TEI adapter
- stable JCS verifier

## Implementation constraints

- Contract Definitionをsemantic authorityとする。
- JSON SchemaとGo structが矛盾した場合、Go都合でContractを変更しない。
- package layoutをArchitecture concernの恒久identityにしない。
- Provider固有fieldをUniversal structへ追加しない。
- unknown Contractをsilently ignoreしてfully validatedと主張しない。
- `not_verified != failed`を維持する。
- stable Representation ProfileはISSUE-000009を待つ。

## Acceptance

### Executable Acceptance

- [ ] `runtime/go`がactual treeに存在する。
- [ ] Go moduleがcompile / testできる。
- [ ] Semantic Interchange v1alpha1を読み込める。
- [ ] F1〜F7をruntime read modelへ読み込める。
- [ ] Recommendation without Decisionを正常に扱える。
- [ ] Decision with unresolved stateを正常に扱える。
- [ ] partial-knowledge interchangeを正常に扱える。
- [ ] same-logical-id lineage without exact endpointを拒否できる。
- [ ] mismatched exact bindingを拒否できる。
- [ ] unknown nested Contractを`not_verified`相当として扱える。
- [ ] Runtime CIをactual branchで再現できる。
- [ ] Contract checkerとruntime testを同じfixture sourceへ接続できる。

### Evidence boundary

本Issueで得るのはfirst runtime sliceのExecutable Evidenceである。

```text
runtime tests PASS
  != stable Representation Profile
  != Provider production integration
  != release readiness
  != operational evidence
```

## Dependencies

- ADR-0022
- ISSUE-000009
- ISSUE-000022
- `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`

## Natural Japanese review

ADR-0022のruntime責務、current Contract fixture、ISSUE-000009の未解決境界へ戻って実装範囲を整理した。その後、Executionやstable Profileを先取りせず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
