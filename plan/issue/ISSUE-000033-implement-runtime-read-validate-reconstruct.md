# ISSUE-000033: read / validate / reconstruct runtime sliceを実装する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0021, ADR-0022, ADR-0023**  
Updated: 2026-08-31

## Goal

ADR-0022で確定したfirst runtime sliceをGoでactual repositoryへ実装し、current Contract fixtureをruntimeへ読み込むend-to-end conformanceを構築する。

外部Action実行を先行せず、Semantic Interchange、Decision Memory、Capability Observation、Semantic Referenceの読み込み・意味検査・historical reconstructionを最初のExecutable runtime Evidenceとする。

ADR-0023でcurrent Representation Profile基線は確定済みだが、そのfixture conformanceとProduction Runtime verifier統合は別Evidenceとして扱う。

## Initial scope

### Runtime

root:

```text
runtime/go/
```

初期実装で必要な責務:

- Contract identity / version
- Logical Reference
- Exact Binding metadata
- Representation Profile identity / version
- verification outcome vocabulary
- Decision / Recommendation read model
- Capability Observation read model
- Semantic Interchange envelope loading
- unknown nested Contract handling
- same-logical-id lineage invariant
- bundle exact record / Decision basis consistency
- partial knowledge preservation
- original semantic interchange bytesのlosslessな再export

### Out of scope

- Authorization enforcement
- Action Intent dispatch
- workflow / queue / retry
- autonomous planning
- Provider execution session
- deployment lifecycle
- production TEI adapter
- Production Runtime向けVerifier Registry / Adapterの完成

current JCS / raw-bytes Profile自体はADR-0023 / ISSUE-000009で確定済みであり、out of scopeなのは**Profile基線そのものではなくRuntime統合の完成**である。

## Implementation constraints

- Contract Definitionをsemantic authorityとする。
- JSON SchemaとGo structが矛盾した場合、Go都合でContractを変更しない。
- package layoutをArchitecture concernの恒久identityにしない。
- Provider固有fieldをUniversal structへ追加しない。
- unknown Contractをsilently ignoreしてfully validatedと主張しない。
- `not_verified != failed`を維持する。
- JCS / raw-bytes ProfileをUniversal defaultとしてhard-codeしない。
- verifierを接続する場合はADR-0023とProfile Definition / fixtureを正本とする。

## Current implementation state

actual treeでは、すでに次が実体化され始めている。

```text
runtime/go/go.mod
runtime/go/semanticruntime/model.go
```

`model.go`には、少なくとも次のread modelが入っている。

- `ContractIdentity`
- `LogicalReference`
- `RepresentationProfile`
- `ExactBinding`
- `VerificationOutcome`
- `Decision` / `Recommendation`
- `CapabilityObservation`
- `SemanticInterchange`
- `RuntimeRecord`
- `Bundle`

また、`Bundle.ExportOriginal()`はread成功だけを理由にbundleをnormalize / rewriteせず、元bytesのcopyを返す境界を持つ。

この存在だけではExecutable AcceptanceをSatisfiedにしない。loader / validation / fixture tests / CIが必要である。

## Acceptance

### Executable Acceptance

- [x] `runtime/go`がactual treeに存在する。
- [ ] Go moduleがcompile / testできる。
- [ ] Semantic Interchange v1alpha1を読み込める。
- [ ] F1〜F7をruntime read modelへ読み込める。
- [ ] Recommendation without Decisionを正常に扱える。
- [ ] Decision with unresolved stateを正常に扱える。
- [ ] partial-knowledge interchangeを正常に扱える。
- [ ] same-logical-id lineage without exact endpointを拒否できる。
- [ ] mismatched exact bindingを拒否できる。
- [ ] unknown nested Contractを`not_verified`相当として扱える。
- [ ] original semantic interchange bytesを意味を変えず再exportできる。
- [ ] Runtime CIをactual branchで再現できる。
- [ ] Contract checkerとruntime testを同じfixture sourceへ接続できる。

### Evidence boundary

本Issueで得るのはfirst runtime sliceのExecutable Evidenceである。

```text
runtime tests PASS
  != Representation Profile runtime integration
  != Provider production integration
  != release readiness
  != operational evidence
```

Representation Profile fixture-scoped Executable EvidenceはISSUE-000009で成立済みだが、それをruntime testの代わりにはしない。

## Dependencies

- ADR-0021 — Architecture / Contract authority
- ADR-0022 — first runtime slice
- ADR-0023 — current Representation Profile baseline
- ISSUE-000009 — current/future Profile stabilization（Resolved）
- ISSUE-000022 — repository baseline
- `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`
- `contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`

## Natural Japanese review

ADR-0022、ADR-0023、current runtime tree、Contract fixture、Representation Profile conformanceを照合して実装範囲を更新した。その後、Profile未確定を前提としていた記述を修正し、実装ファイルの存在をExecutable Evidenceへ先取りしないよう注意しながら、意味、Acceptance強度、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
