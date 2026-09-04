# ISSUE-000049: bundle-local Exact Binding整合をknown Contract横断で実装する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0021, ADR-0022, ADR-0025, ADR-0026**  
Updated: 2026-09-02

## Goal

ADR-0026に基づき、Semantic Interchange内のbundle-local Exact Binding整合検査をDecision basis専用ロジックから切り離し、current runtimeが意味を理解しているknown ContractのExact Referenceへ一貫して適用できるようにする。

本Issueで検査するのは、**同一bundleに含まれるexact-bound recordと、known typed Contractから得られたExact Referenceの内部整合**である。payload bytesの取得・再hash・Verification Outcome生成は対象外とする。

## Resolution

Decision `basis_refs`専用だった比較処理を、次の二段構造へ一般化した。

```text
known typed Contract
  → typed Exact Reference extraction
  → common bundle-local consistency check
```

Go runtimeでは`runtime/go/semanticruntime/exact_references.go`でknown typed ContractのReference roleからExact Bindingを抽出し、`validateBundleExactReferences`でSemantic Interchange envelope側のExact Bindingと共通照合する。

Python Contract checkerも同じ意味境界を独立に実装した。Go実装とPython実装のどちらかを意味上の正本とはせず、ADR-0026と各Contract Definitionを共通の規範としている。

## 実装したReference role

### Decision Memory

- Decision: context / basis / recommendation / unresolved / responsibility refs
- Decision lineage: from / to / basis refs
- Recommendation: context / basis / responsibility refs

### Cognitive Method

- Method Definition: context / specification refs
- Method Realization: method / implementation / context refs
- Method Application: method / realization / context / input / output / residual / provenance / responsibility refs

### Capability Observation

- condition source refs
- provenance refs
- mapping provenance ref

### Semantic Reference

- exact_binding
- semantic lineage: from / to / basis refs
- verification outcome binding

Logical Referenceだけの値はExact Referenceとして抽出しない。

## bundle exact index

Semantic Interchange envelopeの`exact_binding`はlogical identityごとに複数件を保持する。

```text
logical identity
  → [exact binding A, exact binding B, ...]
```

同一logical identityに複数revisionが存在してもlatest-winsで潰さない。Referenceが候補のいずれかと、logical identity、content digest、Representation Profile ID / versionのすべてで一致すれば整合とする。

## external Exact Reference

同一logical identityのexact-bound recordがbundle内に存在しない場合は、この検査だけを理由にFAILとしない。

```text
bundle record absent
  != exact reference invalid
```

外部payloadの取得はPayload Source、digest再計算はVerifier Registryへ委ねる。

## unknown Contract

unknown Contract versionはopaque + `not_verified`を維持する。

未知payloadに`exact_binding`や`content_digest`というfield名が現れても、current known ContractのReference roleとして推測走査しない。

```text
unknown payload looks familiar
  != known typed Contract
```

## Fixture / Test Evidence

current v1alpha1 fixture baselineは39件となった。

今回、少なくとも次を直接固定した。

### PASS / `not_verified`

- Cognitive Method exact `method_ref`がbundle内Method recordと一致する。
- 同一logical identityに複数Exact Bindingがあり、参照がその一つへ一致する。
- external Exact Referenceの対象recordがbundle内にない。
- logical-only Referenceとexact-bound recordが共存しても、logical refをExactへ昇格しない。
- unknown Contractのexact風payloadを推測解析せず`not_verified`とする。

Go runtime testでは、exact `realization_ref`の一致も直接検査する。

### FAIL

- Cognitive Method exact `method_ref`のdigest不一致。
- Cognitive Method exact `realization_ref`のRepresentation Profile version不一致。
- Capability Observationのexact source refとbundle内recordのRepresentation Profile不一致。
- 従来のDecision basis Exact Binding不一致。

## Acceptance criteria

### Design

- [x] ADR-0026でbundle-local Exact Binding整合の意味境界をAcceptedした。
- [x] current ContractごとのReference roleを監査し、抽出対象を明文化した。

### Executable

- [x] Decision専用比較を共通bundle-local consistency判定へ分離した。
- [x] Cognitive Methodのexact Method / Realization Referenceを検査できる。
- [x] Capability Observation等、Decision以外のknown Contractにも同じ規則を適用できる。
- [x] 同一logical identityの複数exact revisionをlatest-winsで潰さない。
- [x] external Exact Referenceをbundle不在だけでFAILにしない。
- [x] logical-only Referenceをexactへ自動昇格しない。
- [x] unknown Contractはopaque + `not_verified`を維持する。
- [x] positive / negative fixtureとGo runtime testで境界を検査した。
- [x] Contract ConformanceとSemantic Runtime Conformanceがactual CIでsuccessした。

### Evidence

- [x] fixture README / Contract Conformance Evidence / Contract Traceabilityへscopeを反映した。
- [x] historical reconstructionのExecutable Evidenceを、実際に確認した範囲だけ更新した。
- [x] Release / Operational / Adoption・Outcomeへは昇格させていない。

## CI Evidence

39-fixture / current runtime基線を直接確認したRun:

- Contract Conformance `33527512045`: **success**
- Semantic Runtime Conformance `33527512016`: **success**
- Plan integrity `33527511976`: **success**
- V6 V7 Projection Evaluation `33527511966`: **success**
- Local Package Artifact `33527511934`: **success**

Issue / registryのResolved同期後にはPlan integrityを再確認する。

## Non-goals

- external payload acquisition
- digest再計算
- Verification Outcome生成
- signature / timestamp verification
- Truth / Assurance判定
- unknown Contractのbest-effort field introspection
- Logical ReferenceをExact Bindingへ自動変換すること
- bundle外Artifactの存在保証

## Evidence state

- Design Evidence: **Satisfied within current known Contract scope**
- Executable Evidence: **Satisfied within 39-fixture / current typed-role scope**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

本IssueのResolvedは、known current Contractに対するbundle-local consistency一般化の完了を意味する。external payload verificationやproduction historical reconstruction全体の成立を意味しない。

## Natural Japanese review

ADR-0008 / ADR-0009 / ADR-0022 / ADR-0025 / ADR-0026、current 5 Contract Definition、39 fixture、Python Contract checker、Go semantic runtime、Payload Source / Verifier Registry、actual CIへ戻って完了条件を再監査した。bundle内整合とpayload verification、Logical ReferenceとExact Binding、known Contractとunknown Contractを混同しないことを中心に整理し、確認していないEvidenceをRelease以降へ昇格させていない。そのうえで、意味と規範強度を変えず、自然な日本語となることを重要視して全文を再ドラフトし、最終意味監査を実施済みである。
