# Semantic Runtime / Provider Adapter Conformance Evidence — current through 2026-09-02

状態: **Scoped Executable Evidence — PASS**  
対象branch: `develop/v0.2.0`

## 1. Scope

本書は、current Semantic Contractから再導出したGo Semantic Runtimeについて、actual repositoryで再現したExecutable Evidenceを記録します。Representation Verifier Registry、Payload Source、synthetic Provider Adapter、Cognitive Method first slice、およびADR-0026 / ISSUE-000049のbundle-local Exact Binding整合を同じEvidence体系の中で読み分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

production Provider / Storage、Authorization / Action execution、Method quality、Release、Operational、Adoption / Outcomeは本書のPASSから主張しません。

## 2. Semantic Runtime boundary

runtimeの基本責務は次です。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
!= judge conclusion truth
```

current runtimeがtyped semanticsとして理解するContract:

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

unknown nested Contract / unknown future versionは既知として扱わず、opaque payloadを保持した`not_verified`とします。

## 3. Cognitive Method first slice

runtimeはMethod Definition、Method Realization、Method Applicationを別型として保持します。

```text
Method Definition
  != Method Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance
```

ApplicationはMethodを参照し、Realizationはoptionalです。Realization省略からRealization不存在やMethod未適用を推定しません。

Referenceとして、Method / Realization / context / input / output / residual / provenance / contextual Responsibilityを保持できます。

Patternはdomain-specific input Referenceとして扱い、Cognitive Methodそのものへ昇格させません。

## 4. bundle-local Exact Binding consistency

### 4.1 背景

従来runtimeは、同一bundle内のexact-bound recordとDecision `basis_refs`の不一致だけを検出していました。

Cognitive Methodの導入により、Method / Realization / input等にもExact Referenceが現れるため、ADR-0026 / ISSUE-000049でこの規則をknown Contract横断へ一般化しました。

### 4.2 typed extraction

`extractKnownExactReferences`は、runtimeが意味を理解しているtyped recordからだけExact Referenceを抽出します。

対象:

- Semantic Referenceの既知Reference role
- Decision / RecommendationのReference role
- Cognitive Method Definition / Realization / ApplicationのReference role
- Capability Observationのcondition source / provenance / mapping Reference

unknown Contractは`RecordNotVerified`のまま除外し、opaque payloadをJSON再帰探索しません。

### 4.3 bundle index

bundle envelopeに含まれるExact Bindingを次の形で索引化します。

```text
LogicalReference
  → []ExactBinding
```

同一logical identityの複数revisionをlatest-winsで潰しません。

### 4.4 common consistency check

known typed Exact Referenceについて、同じlogical identityのexact-bound recordがbundle内に存在する場合は、少なくとも一つのcandidateと次が一致する必要があります。

- logical reference
- content digest
- Representation Profile ID
- Representation Profile version

同じlogical identityのrecordがbundle内に存在しない場合はexternal Exact Referenceとして扱い、この検査だけを理由にFAILにしません。

logical-only Referenceは抽出対象にならないため、bundle内にexact-bound recordが存在してもExact Referenceへ自動昇格しません。

```text
Logical Reference != Exact Historical Binding
no local candidate != binding mismatch
```

### 4.5 runtime tests

`runtime/go/semanticruntime/bundle_exact_test.go`で次を直接確認します。

- Cognitive Method exact Method / Realization Referenceの一致
- 同一logical identityの複数exact revision
- external Exact Reference
- logical-only Referenceの非昇格
- Method digest mismatch拒否
- Realization Profile version mismatch拒否
- Capability source ref mismatch拒否
- unknown Contract exact-looking payloadのopaque + `not_verified`維持

既存Decision basis mismatch testも回帰確認されています。

## 5. Representation Verifier boundary

Exact Binding metadataの内部整合とは別に、Verifier Registryは取得済みpayloadからcontent digestを再計算します。

```text
Exact Binding metadata valid
  != bundle-local consistency PASS
  != payload content verified

Exact Binding != Verification Outcome
```

current Profile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

known Profile + digest mismatchは`failed`、unknown Profileやpayload unavailableは`not_verified`です。

## 6. Payload acquisition boundary

Payload Sourceはfilesystem、object store、remote artifact service等を将来接続する交換可能なruntime interfaceです。

```text
payload unavailable
  != content mismatch
operational acquisition error
  != semantic Verification Outcome
```

Storage path、object key、HTTP、credential、retry等をUniversal Coreへ持ち込みません。

## 7. Provider Adapter boundary

synthetic Provider AdapterはProvider-owned stateからCapability Observationへの観測・解釈境界です。

- 異なるProvider-specific input shapeから同じCapabilityを観測する。
- status interpretation / unit conversionをmappingとして扱う。
- mapping provenance / source state referenceを保持する。
- missing valueを`false`や`0`へ捏造せず`unknown`にする。
- Provider固有fieldをUniversal ontologyへ漏らさない。
- Recommendation / Decision / Authority / Executionへ自動昇格しない。

## 8. Executable paths

```text
runtime/go/semanticruntime/model.go
runtime/go/semanticruntime/loader.go
runtime/go/semanticruntime/loader_test.go
runtime/go/semanticruntime/bundle_exact_test.go
runtime/go/semanticruntime/cognitive_method.go
runtime/go/semanticruntime/cognitive_method_test.go
runtime/go/semanticruntime/verifier.go
runtime/go/semanticruntime/verifier_test.go
runtime/go/semanticruntime/payload_source.go
runtime/go/semanticruntime/payload_source_test.go
runtime/go/provideradapter/
fixtures/contracts/v1alpha1/
fixtures/providers/synthetic/
fixtures/representation-profiles/
```

CIはcurrent Contract checkerと`go test ./...`を同じcheckoutで実行します。

## 9. Current Contract fixture result

current baselineでは36 fixtureについて期待結果とactual checker結果が一致します。

```text
fixture_count = 36
passed = true
```

Cognitive Method C1〜C9、bundle-local Exact Bindingのpositive / negative / unknown-boundary caseを含みます。

## 10. GitHub Actions evidence

今回の一般化を最新developへ追随させたPR head `5415972249e5f935337d8d872da2d9596da3098c`で再検証しました。

- Contract Conformance Run `33527524514`: **success**
- Semantic Runtime Conformance Run `33527524668`: **success**
- V6/V7 Projection Evaluation Run `33527524747`: **success**
- Local Package Artifact Run `33527524476`: **success**

過去の代表Evidence:

- first semantic runtime Run `33348972805`: **success**
- Representation Verifier Registry Run `33452115728`: **success**
- Payload Source Run `33457416359`: **success**
- synthetic Provider Adapterのscoped success runsあり

過去runは履歴として保持しますが、current 36-fixture / generalized runtimeの代わりにはしません。

## 11. Evidence boundary

current Evidence state:

- Design: **Satisfied** — current Contract / ADRで意味境界を分離済み。
- Executable: **Partially Satisfied overall; Satisfied within the ISSUE-000049 bundle-local consistency scope** — 36 Contract fixtureとGo runtime testsでknown typed Referenceの内部整合を再現可能。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

次は本Evidenceから主張しません。

- bundle-local consistencyだけによるpayload verification
- external Artifactの存在・取得可能性の保証
- Method execution quality / conclusion truth / Assurance
- production filesystem / object-storage adapterの全面実証
- production Provider / TEI integration
- production Authorization / Action execution
- Release / Operational / Adoption・Outcome

historical M47 digest ruleはISSUE-000034のResolved方針どおり回収不能範囲を`not_verified`として保持します。

## 12. Natural Japanese review

ADR-0026、ISSUE-000049、36 Contract fixture、Python Contract checker、Go semantic runtime、Verifier Registry、Payload Source、synthetic Provider Adapter、最新develop追随後のactual CIを相互照合しました。Decision専用だったbundle-local整合検査をknown typed Contractへ一般化しつつ、unknown payloadの推測走査やpayload verificationへ責務を広げていません。その後、意味、Evidence強度、Exact Binding / Verification Outcome / Profile authority / Storage-neutralityの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
