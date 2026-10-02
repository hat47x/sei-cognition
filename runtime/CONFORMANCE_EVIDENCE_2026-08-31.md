# Semantic Runtime / Provider Adapter Conformance Evidence — current through 2026-09-01

状態: **Fixture-scoped Executable Evidence — PASS**  
対象branch: `develop/v0.2.0`

## 1. Scope

本書は、current Semantic Contractから再導出したGo Semantic Runtime、synthetic Provider Adapter、Representation Verifier Registry、Payload Source boundary、およびv0.2.0で追加したCognitive Method first sliceについて、actual repository上で再現したExecutable Evidenceを記録します。

対象は次のとおりです。

```text
runtime/go/semanticruntime/
runtime/go/provideradapter/
```

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

production Provider / Storage、Method executor、Authorization / Action execution、Release、Operational、Adoption / Outcomeは本Evidenceから主張しません。

## 2. Semantic Runtime boundary

runtimeの基本sliceは次です。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
!= judge conclusion truth
```

current runtimeは次のcurrent known Contractを読み込みます。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

unknown nested Contract / unknown future versionは既知として扱わず、opaque payloadを保持した`not_verified`とします。

また、次を同一視しません。

```text
Recommendation != Decision != Authority != Execution
Unknown != false
not_verified != failed
Method Application != Decision != Assurance
Pattern != Cognitive Method
```

## 3. Cognitive Method first slice

ADR-0025 / ISSUE-000043に基づき、Cognitive Methodのportable meaningをfirst semantic runtimeへ追加しました。

実装は次のとおりです。

```text
runtime/go/semanticruntime/cognitive_method.go
runtime/go/semanticruntime/cognitive_method_test.go
```

runtime read modelは次を別型として保持します。

- Method Definition
- Method Realization
- Method Application

### 3.1 Definition / Realization / Application

```text
Method Definition
  != Method Realization
  != Method Application
```

ApplicationはMethodを必ず参照します。Realizationはoptionalであり、`realization_ref`が省略されていることからRealization不存在やMethod未適用を推定しません。

### 3.2 Reference preservation

Method Applicationは必要に応じて次をReferenceとして保持します。

- Method
- Realization
- context
- input
- output
- residual
- provenance
- contextual Responsibility

C6 fixtureではMethod / RealizationへのExact Binding metadataをtyped read modelへ保持できることを確認しています。

```text
Exact Binding metadata preserved
  != payload content verified by that fact alone
```

### 3.3 Pattern boundary

C5 fixtureではdomain-specific Patternをinput Referenceとして読み込みます。

PatternをCognitive Methodへ昇格させず、negative fixtureではPattern固有fieldをMethod recordへ直接埋め込む表現を拒否します。

### 3.4 semantic escalation boundary

Method Applicationの存在からRecommendation、Decision、Assuranceを生成しません。

negative fixtureではMethod Applicationへ`decision` / `assurance`を直接埋め込む表現をstrict validationで拒否します。

### 3.5 current / future version

C8ではcurrent `soza.cognitive-method/v1alpha1`をSemantic Interchange内でtyped loadします。

`unknown-cognitive-method-version.json`ではfuture `v1alpha2`をcurrent v1alpha1として推測解釈せず、opaque + `not_verified`を維持します。

### 3.6 lossless read

C8のInterchangeを読み込んでも、`ExportOriginal()`はoriginal bytesの独立copyを返します。

read成功を理由にbundleをnormalize / rewriteしません。

## 4. Representation Verifier boundary

ISSUE-000038で、Exact Binding metadataの構造検査とは別にpayloadからcontent digestを再計算するVerifier Registryを追加しました。

```text
Exact Binding metadata valid
  != Exact Binding content verified

Exact Binding
  != Verification Outcome
```

current Registryが解決するProfile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Profile authorityは各Profile DefinitionとRFC 8785です。runtimeのGo実装やJCS library APIをProfile authorityにはしません。

### JCS + SHA-256

既存Profile fixtureから、少なくとも次を確認しています。

- property order / insignificant whitespace差のcanonicalization
- representative RFC 8785 sampleの固定digest
- duplicate key等の不正representation → `failed`
- unsafe integerを暗黙丸めしない
- NFC / NFDを勝手にnormalizeしない

### Raw bytes + SHA-256

UTF-8 textとbinary bytesの固定digestを再現し、改行変換、Unicode normalization、再encode等を行いません。

### Verification Outcome

- known Profile + digest一致 → `verified`
- known Profile + digest mismatch → `failed`
- Profile入力制約違反 → `failed`
- unknown Profile → `not_verified`
- payload unavailable → `not_verified`

検証結果は新しい`VerificationOutcome`として返し、入力Exact Bindingをmutateしません。

## 5. Payload acquisition boundary

ISSUE-000040ではpayload取得とRepresentation verificationを分離しました。

```text
Exact Binding
  ↓
PayloadRequest
  ↓
PayloadSource
  ↓
PayloadLoadResult
  ↓
Verifier Registry
  ↓
Verification Outcome
```

`PayloadSource`はfilesystem、object store、remote artifact service等を将来接続するための交換可能なruntime interfaceです。Storage path、object key、HTTP、credential、retry等をUniversal Coreへ持ち込みません。

current orchestrationは少なくとも次を分けます。

- available payload + digest一致 → `verified`
- available payload + digest mismatch → `failed`
- sourceがavailableでない → `not_verified`
- source operational error → semantic outcomeは`not_verified`、operational errorは別戻り値
- source未設定 → `not_verified`
- caller指定local size limit超過 → `not_verified` + operational error
- availableな0 byte payload → 通常のpayloadとして検証可能

```text
payload unavailable
  != content mismatch

operational acquisition error
  != semantic Verification Outcome
```

Payload SourceはJCS canonicalization等を行わず、取得bytesをVerifierへ渡します。

## 6. Provider Adapter boundary

Provider AdapterはProvider固有stateからCapability Observationへの観測・解釈境界です。

```text
Provider-owned state
  + observation context
        ↓
Adapter / Mapping
        ↓
Capability Observation
```

synthetic Provider A / Bは意図的に異なる入力Schemaを持ちます。

Provider A:

```text
health
delay_ms
service_ref
```

Provider B:

```text
ready
response_seconds
endpoint
```

Provider固有fieldをSOZA Universal ontologyにはしません。

主な確認範囲は次のとおりです。

- 異なるinput shapeから同じCapabilityへのObservationを生成する。
- status interpretation / unit conversionをmappingとして扱う。
- `mapping_provenance` / `source_state_ref`を保持する。
- missing readiness / latencyを`false`や`0`へ捏造せず`unknown`にする。
- Provider-specific fieldをUniversal field setへ漏らさない。
- Recommendation / Decision / Authority / Executionへ自動昇格しない。

## 7. Executable paths

current runtime / Adapter / Verifier / Payload Source / Cognitive Method実装:

```text
runtime/go/semanticruntime/model.go
runtime/go/semanticruntime/loader.go
runtime/go/semanticruntime/loader_test.go
runtime/go/semanticruntime/cognitive_method.go
runtime/go/semanticruntime/cognitive_method_test.go
runtime/go/semanticruntime/verifier.go
runtime/go/semanticruntime/verifier_test.go
runtime/go/semanticruntime/payload_source.go
runtime/go/semanticruntime/payload_source_test.go
runtime/go/provideradapter/adapter.go
runtime/go/provideradapter/synthetic.go
runtime/go/provideradapter/adapter_test.go
runtime/go/go.mod
runtime/go/go.sum
```

fixture:

```text
fixtures/contracts/v1alpha1/
fixtures/providers/synthetic/
fixtures/representation-profiles/
```

CI:

```text
.github/workflows/runtime-conformance.yml
```

CIは同じcheckoutでcurrent Contract checkerと`go test ./...`を実行します。

## 8. Current Contract fixture result

current baselineでは31 fixtureについて期待結果とactual checker結果が一致します。

```text
fixture_count = 31
passed = true
```

従来のCapability / Decision / Reference / Interchange boundaryに加え、Cognitive Method C1〜C8、Method semantic escalation negative case、unknown future Method versionを含みます。

## 9. Semantic Runtime evidence

current runtime testでは少なくとも次を確認しています。

### Existing semantic boundaries

- Semantic Interchangeを読み込める。
- Capability Observation F1〜F7を読み込める。
- Recommendation without Decisionを保持できる。
- unresolved stateを残したDecisionを保持できる。
- Unknown / Withheldを保持できる。
- same-logical lineage invariant違反を拒否できる。
- bundle内recordとDecision basisのExact Binding不一致を拒否できる。
- unknown nested Contractを完全検証済みとしない。
- original Interchange bytesを勝手にnormalizeしない。

### Cognitive Method boundaries

- C1〜C7 standaloneをtyped loadする。
- C8 nested current Method Applicationをtyped loadする。
- Method / Realization / input / output / residual / provenance等のReferenceを保持する。
- Realization省略を捏造しない。
- Exact-bound Method / Realization Referenceを保持する。
- Pattern inputをPatternのまま保持する。
- Method ApplicationをDecisionへ昇格させない。
- unknown Method `v1alpha2`をopaque + `not_verified`へ保つ。

## 10. GitHub Actions evidence

### First semantic runtime closure

- Run `33348972805`: **success**

### Synthetic Provider Adapter

- Run `33349604842`: **success**
- Run `33349801993`: **success** — Provider-specific field非漏洩hardening

### Representation Verifier Registry

初回Run `33452054067`ではJCS moduleの`go.sum` entry不足でfailureとなりました。

checksum固定後:

- Run `33452115728`: **success**

このfailureは解消済みであり、現在のCIを失敗状態として残していません。

### Payload acquisition boundary

- Run `33457416359`: **success**

### Cognitive Method Contract / runtime

Contract追加後:

- Contract Conformance Run `33467309405`: **success**
- Semantic Runtime Conformance Run `33467309362`: **success**
- V6/V7 Projection regression Run `33467309423`: **success**

Go typed runtime追加後:

- Contract Conformance Run `33467734204`: **success**
- Semantic Runtime Conformance Run `33467734123`: **success**

C8をContract checkerへ含め31 fixtureとしたcurrent代表run:

- Contract Conformance Run `33467838961`: **success**
- Semantic Runtime Conformance Run `33467838941`: **success**
- V6/V7 Projection regression Run `33467838952`: **success**

## 11. bundle-local Exact Binding generalization

current runtimeのbundle-local Exact Binding検査はDecision basisを中心に実装されています。

Cognitive MethodのMethod / Realization等にもExact Referenceが現れるため、ADR-0026 / ISSUE-000049でknown Contract横断の整合検査を次段として起票しました。

```text
current Decision-oriented consistency PASS
  != cross-Contract consistency generalized
```

ISSUE-000049はOpenです。したがってCognitive Method Exact Referenceを**保持できる**ことはcurrent Executable Evidenceですが、同一bundle内Method Definition / Realization exact recordとの全role整合検査は未検証です。

また、本一般化はpayload content verificationとは別です。

```text
bundle-local consistency
  != content verification
  != Verification Outcome
```

## 12. Evidence boundary

current Evidence state:

- Design: **Satisfied** — current ADR / Contract / runtime boundaryで意味と実現を分離済み。
- Executable: **Partially Satisfied** — 31 Contract fixture、known Contract typed read、Cognitive Method first slice、synthetic Adapter、current 2 Profile verification、synthetic Payload Sourceを再現可能。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

次は本Evidenceから主張しません。

- Method execution / orchestration
- Method quality / conclusion truth / Assurance
- ISSUE-000049一般化の完了
- production filesystem / object-storage adapter
- production Provider / TEI integration
- production streaming verification
- production Authorization / Action execution
- Release / Operational / Adoption・Outcome

historical M47 digest ruleはISSUE-000034のResolved方針どおり回収不能範囲を`not_verified`として保持します。

## 13. Natural Japanese review

actual GitHub Actions、31 Contract fixture、5 current Contract family、Semantic Runtime、Cognitive Method first slice、synthetic Provider Adapter、Verifier Registry、Payload Source boundaryを相互照合しました。Method ApplicationをDecision / Assuranceへ昇格させないこと、Realization省略を捏造しないこと、unknown future Methodをopaque + `not_verified`へ保つことをcurrent Evidenceへ追加し、ISSUE-000049やproduction以降の未検証範囲を分離しています。その後、意味、Evidence強度、Exact Binding / Verification Outcome / Profile authority / Storage-neutralityの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
