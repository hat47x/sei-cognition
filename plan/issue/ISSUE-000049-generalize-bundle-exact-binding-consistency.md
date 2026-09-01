# ISSUE-000049: bundle-local Exact Binding整合をknown Contract横断で実装する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0021, ADR-0022, ADR-0025, ADR-0026**  
Updated: 2026-09-01

## Goal

ADR-0026に基づき、Semantic Interchange内のbundle-local Exact Binding整合検査をDecision basis専用ロジックから切り離し、current runtimeが意味を理解しているknown ContractのExact Referenceへ一貫して適用できるようにする。

このIssueで検査するのは、**同一bundleに含まれるexact-bound recordと、known typed Contractから得られたExact Referenceの内部整合**である。payload bytesの取得・再hash・Verification Outcome生成は対象外とする。

## Why now

v0.1.0 runtimeでは、Decisionのhistorical basis再構成を優先し、bundle内exact recordとDecision `basis_refs`の不一致を検出する最小検査を実装した。

v0.2.0では`soza.cognitive-method/v1alpha1`が加わり、Method Applicationが`method_ref`、`realization_ref`、`input_refs`等をExact Bindingとして保持できるようになった。

このままContractごとに個別比較を増やすと、同じ意味規則がfield名ごとに複製され、将来のContract追加時に検査漏れが起きやすい。

## Scope

### 1. typed Exact Reference extraction

current known Contractごとに、Exact Referenceを持ち得るsemantic Reference roleを型付きに抽出する。

少なくとも検討対象:

- Decision Memory
  - context / basis / recommendation / unresolved / responsibility refs
- Cognitive Method
  - method / realization / context / input / output / residual / provenance / responsibility refs
- Capability Observation
  - condition source refs
  - provenance refs
  - mapping provenance ref
- Semantic Reference
  - lineage endpoints / basis refs等、bundle-local比較が意味を持つもの

Logical Referenceだけの値はExact Referenceとして抽出しない。

### 2. bundle exact index

Semantic Interchange envelopeの`exact_binding`をlogical identityごとに索引化する。

同一logical identityへ複数Exact Bindingが存在することを許容し、単一値へlatest-winsで潰さない。

```text
logical identity
  → [exact binding A, exact binding B, ...]
```

### 3. common consistency check

known Contractから抽出したExact Referenceについて、同一logical identityのexact-bound recordがbundle内に存在する場合、そのいずれかとbinding全体が一致することを確認する。

比較:

- logical ref
- content digest
- Representation Profile ID
- Representation Profile version

不一致の場合はSemantic Interchange validation errorとする。

### 4. external Exact Reference

同一logical identityのexact-bound recordがbundle内に存在しない場合は、この検査だけを理由にFAILとしない。

外部payloadの検証はPayload Source / Verifier Registryへ委ねる。

### 5. unknown Contract

unknown Contract versionはopaque + `not_verified`を維持する。

未知payloadをJSON field名から推測走査してExact Referenceを抽出しない。

## Required fixtures

少なくとも次を追加する。

### PASS

1. Cognitive Method Applicationのexact `method_ref`がbundle内Method Definition exact recordと一致する。
2. exact `realization_ref`がbundle内Realization exact recordと一致する。
3. 同じlogical identityの複数exact revisionがbundleにあり、参照がその一つへ正しく一致する。
4. external Exact Referenceでbundle内recordが存在しない。
5. logical-only Referenceとbundle内exact recordが共存するが、logical refをexactへ自動昇格しない。
6. unknown Contract payloadにExact Bindingらしいfieldがあってもopaque + `not_verified`を維持する。

### FAIL

1. Cognitive Method exact `method_ref`とbundle内Method Definitionのdigestが異なる。
2. Cognitive Method exact `realization_ref`とbundle内RealizationのProfile versionが異なる。
3. Capability Observationのexact provenance/source refがbundle内recordと不一致になる。
4. Decision以外のknown Contractで不一致があっても見逃さない。

## Implementation direction

Decision専用の`validateBundleExactReferences`を巨大なJSON再帰探索へ置き換えない。

概念上は次を分ける。

```text
extractExactReferences(known typed record)
        ↓
[]ExactBinding
        ↓
checkBundleLocalConsistency(index, refs)
```

具体的なGo API名は実装時に調整してよい。

Contract checker側も、同じ意味規則をPythonのknown Contract extractor + common compareとして実装する。Go実装とPython実装が互いのauthorityになるのではなく、ADR-0026と各Contract Definitionを共通の意味基準とする。

## Non-goals

- external payload acquisition
- digest再計算
- Verification Outcome生成
- signature / timestamp verification
- Truth / Assurance判定
- unknown Contractのbest-effort field introspection
- Logical ReferenceをExact Bindingへ自動変換すること
- bundle外Artifactの存在保証

## Acceptance criteria

### Design

- [x] ADR-0026でbundle-local Exact Binding整合の意味境界をAcceptedする。
- [ ] current ContractごとのReference roleを監査し、抽出対象を明文化する。

### Executable

- [ ] Decision専用比較を共通bundle-local consistency判定へ分離する。
- [ ] Cognitive Methodのexact Method / Realization Referenceを検査できる。
- [ ] Capability Observation等、Decision以外のknown Contractにも同じ規則を適用できる。
- [ ] 同一logical identityの複数exact revisionをlatest-winsで潰さない。
- [ ] external Exact Referenceをbundle不在だけでFAILにしない。
- [ ] logical-only Referenceをexactへ自動昇格しない。
- [ ] unknown Contractはopaque + `not_verified`を維持する。
- [ ] positive / negative fixtureをContract checkerとGo runtime testの双方で検査する。
- [ ] Contract ConformanceとSemantic Runtime Conformanceがactual CIでsuccessする。

### Evidence

- [ ] runtime / Contract Evidenceへscopeを反映する。
- [ ] historical reconstructionのExecutable Evidenceを、実際に確認した範囲だけ更新する。
- [ ] Release / Operational / Adoption・Outcomeへは昇格させない。

## Relation to ISSUE-000043

ISSUE-000043はCognitive Method Contractとfirst typed runtime sliceの実体化を扱う。

本Issueは、そのfirst sliceによって新たに露出した**cross-Contract bundle consistencyの一般化**を後続課題として扱う。ISSUE-000043をResolvedにするために本Issueの完了を必須とはしない。

```text
Cognitive Method typed runtime established
  != all cross-Contract exact consistency generalized
```

## Natural Japanese review

ADR-0008 / ADR-0009 / ADR-0022 / ADR-0025 / ADR-0026、current Semantic Interchange checker、Go runtime、Cognitive MethodのExact Reference roleを照合しました。実装課題をpayload verificationやunknown Contract解析へ拡張せず、bundle内で既に表明されたExact Binding同士の整合に限定しています。その後、AcceptanceとNon-goalの境界を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
