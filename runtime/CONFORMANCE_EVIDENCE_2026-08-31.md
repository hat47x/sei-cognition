# Semantic Runtime / Provider Adapter Conformance Evidence — current through 2026-09-01

状態: **Fixture-scoped Executable Evidence — PASS**  
対象branch: `develop/v0.1.0`

## 1. Scope

本書は、current Contractから再導出したSemantic Runtime slice、synthetic Provider Adapter slice、current Representation Profileを解決するin-process Verifier Registry、およびVerifierへpayloadを渡すPayload Source boundaryについて、actual repository上で再現したExecutable Evidenceを記録します。

対象:

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

Production Provider integration、production Storage / object-store adapter、Authorization / Action execution、Release、Operational、Adoption / Outcomeは本Evidenceから主張しません。

## 2. Semantic Runtime boundary

runtimeの基本sliceは次を中心とします。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
```

current runtimeはSemantic Interchange、Semantic Reference、Decision Memory、Capability Observationを読み込み、known Contractを検査します。

unknown nested Contractは既知として扱わず、完全検証できない状態として保持します。また、RecommendationとDecision、DecisionとAuthority、Unknownとfalse、`not_verified`と`failed`を同一視しません。

## 3. Representation Verifier boundary

ISSUE-000038では、Exact Binding metadataの構造検査とは別に、payloadからcontent digestを再計算するVerifier Registryを追加しました。

```text
Exact Binding metadata valid
  != Exact Binding content verified

Exact Binding
  != Verification Outcome
```

current Registryが解決するProfile:

```text
soza.jcs+sha256/v1alpha1
soza.raw-bytes+sha256/v1alpha1
```

Profile authorityは各Profile DefinitionとRFC 8785です。runtimeのGo実装やJCS library APIをProfile authorityにはしません。

### JCS + SHA-256

runtime testでは既存`fixtures/representation-profiles/jcs-v1alpha1.json`を直接利用し、次を確認しています。

- property order / insignificant whitespace差をcanonicalizeできる。
- representative RFC 8785 sampleで固定digestを再現できる。
- duplicate key等の不正representationを`failed`にできる。
- `9007199254740993`等のunsafe integerをbinary64へ暗黙丸めせず`failed`にできる。
- NFC / NFDを勝手にnormalizeせず、fixtureで定めた異なるdigestを再現できる。

### Raw bytes + SHA-256

`fixtures/representation-profiles/raw-bytes-v1alpha1.json`を直接利用し、UTF-8 textとbinary bytesの固定digestを再現しています。

raw bytes verifierは改行変換、Unicode normalization、再encode等を行いません。

### Verification Outcome

runtime Registryは次を区別します。

- known Profile + digest一致 → `verified`
- known Profile + digest mismatch → `failed`
- Profile入力制約違反 → `failed`
- unknown Profile → `not_verified`
- payload unavailable (`nil`) → `not_verified`

検証結果は新しい`VerificationOutcome`として返し、入力Exact Bindingをmutateしません。

## 4. Payload acquisition boundary

ISSUE-000040では、payloadの取得処理とRepresentation verificationを別runtime boundaryへ分離しました。

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

`PayloadSource`はfilesystem、object store、remote artifact service等を将来接続するための交換可能なruntime interfaceです。Storage path、object key、HTTP details、credential、retry等をUniversal Coreへ持ち込みません。

`PayloadLoadResult`は次を分けます。

- `Available`
- payload bytes
- opaque `SourceRef`

`SourceRef`はruntime metadataであり、Exact BindingやRepresentation Profileのcanonical identityではありません。

### Acquisition outcome

current orchestrationは次を区別します。

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

callerが指定する`MaxBytes`はlocal resource policyであり、SOZA Universal Coreの固定制限ではありません。

Payload SourceはJCS canonicalization、Unicode normalization、改行変換等を行いません。JCS source testでは非canonical JSON bytesをそのまま返し、JCS Verifier側だけがcanonicalizationを担当することを確認しています。

## 5. Provider Adapter boundary

Provider Adapterは、Provider固有stateからCapability Observationへの観測・解釈境界として扱います。

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

これらのProvider固有field setをSOZA Universal ontologyにはしません。

## 6. Executable paths

current runtime / Adapter / Verifier / Payload Source実装:

```text
runtime/go/semanticruntime/model.go
runtime/go/semanticruntime/loader.go
runtime/go/semanticruntime/loader_test.go
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

CIは同じcheckoutで、概ね次を順に実行します。

1. current Contract checker dependencyを導入する。
2. `tools/check_contract_conformance.py`でcurrent Contract fixtureを再検査する。
3. `runtime/go`で`go test ./...`を実行する。

Representation Profile fixtureもruntime testの入力になったため、同fixture変更時にSemantic Runtime Conformanceが起動するようpath triggerを追加しています。

## 7. Current Contract fixture result

current baselineでは17 fixtureについて、期待結果とactual checkerの結果が一致することを確認しています。

```text
fixture_count = 17
passed = true
```

主な境界にはCapability Observation F1〜F7、Decision / Authority分離、same-logical-id lineage、Exact Binding mismatch、unknown nested Contract、partial knowledge等を含みます。

## 8. Semantic Runtime evidence

runtime testではcurrent Contract fixtureを直接利用し、少なくとも次を確認しています。

- Semantic Interchange v1alpha1を読み込める。
- F1〜F7を適切なtop-level Contractとして読み込める。
- Recommendation without Decisionを保持できる。
- unresolved stateを残したDecisionを保持できる。
- Unknown / Withheldを保持したpartial knowledgeを扱える。
- same-logical-id lineageでexact endpointが必要な場合に違反を拒否できる。
- bundle内recordとDecision basisのExact Binding不一致を拒否できる。
- unknown nested Contractを完全検証済みとして扱わない。
- original Semantic Interchange bytesを読込み時に勝手にnormalizeせず再exportできる。

## 9. Synthetic Provider Adapter evidence

synthetic Provider A / Bについて、少なくとも次を確認しています。

- Providerごとに異なるinput shapeを保持できる。
- 同じCapabilityへのObservationへmappingできる。
- Provider identityを分離する。
- status interpretation / unit conversionをmappingとして扱う。
- `mapping_provenance`と`source_state_ref`を追跡できる。
- missing readiness / latencyを`false`や`0`へ捏造せず`unknown`として保持する。
- Provider-specific target referenceを保持する。
- Adapter出力をCapability Observation runtime validationへ通せる。
- Recommendation / Decision / Authority / Executionへ自動昇格しない。
- Provider固有fieldをCapability ObservationのUniversal field setへ直接漏らさない。

## 10. GitHub Actions evidence

### First semantic runtime closure

- Run ID: `33348972805`
- Head SHA: `834c3f2a8bd911829743c1582ef09f098c776a54`
- conclusion: **success**

### Synthetic Provider Adapter slice

- Run ID: `33349604842`
- Head SHA: `4450ea1acf41615a3679a65e266c008a460c5c33`
- conclusion: **success**

### Provider schema leakage hardening

- Run ID: `33349801993`
- Head SHA: `bff2522e9be004d48274d4743e7756130648169a`
- conclusion: **success**

### Representation Verifier Registry

初回実装後のRun `33452054067`では、Contract fixture再検査はsuccessしたものの、Go側でJCS moduleの`go.sum` entry不足を検出してfailureとなりました。

このCI failureを解消するため、JCS `v1.0.1`のmodule checksumを`runtime/go/go.sum`へ固定しました。

修正後:

- Run ID: `33452115728`
- Head SHA: `9941f49a5af3b5443f3cfaca3b263e07989d3ba4`
- Contract fixture recheck: **success**
- semantic runtime tests: **success**
- Provider Adapter tests: **success**
- Representation Verifier tests: **success**

JCS moduleは`v1.0.1`へ固定しており、ADR-0023の既存probeで使用しているcommit `1a4242a66e1a8e03d7458324d0bc95c327527cbb`に対応します。

### Payload acquisition boundary

- Run ID: `33457416359`
- Head SHA: `125bda1693f0712c2b741f149059d361cce7f97a`
- current Contract fixture recheck: **success**
- semantic runtime / Provider Adapter / Verifier / Payload Source tests: **success**
- conclusion: **success**

このRunではsynthetic Payload Sourceを用い、raw bytes / JCS、unavailable、operational error、nil source、zero-length payload、local size limit、Exact Binding非変異を検査しています。

## 11. Evidence boundary

今回追加で直接確認できたのは、**交換可能なPayload Sourceから取得結果を受け、in-process Verifier Registryへ接続する境界**です。

```text
Payload Source boundary PASS
  != production filesystem adapter
  != production object-storage adapter
  != production remote artifact service
  != production streaming verification
  != Storage migration completed
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

特に、synthetic Payload Sourceが動くことから実Storageの可用性・retention・credential・retry・network behaviorを推定しません。

historical M47 digestのRepresentation Profileも未確認であり、ISSUE-000034で独立して扱います。

current Evidence state:

- Design: **Satisfied** — ADR-0007 / ADR-0008 / ADR-0009 / ADR-0022 / ADR-0023とcurrent runtime boundaryで意味と実現を分離済み。
- Executable: **Partially Satisfied** — Contract fixture、first runtime、synthetic Adapter、current 2 Profileのverification、synthetic Payload Source acquisition boundaryを再現可能。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## 12. Natural Japanese review

actual GitHub Actions、current Contract fixture、Representation Profile fixture、Semantic Runtime、synthetic Provider Adapter、Verifier Registry、Payload Source boundaryの実装とtestを相互照合しました。取得不能、operational error、local resource limitをdigest mismatchへ誤変換しないこと、source固有metadataをExact Bindingへ混入させないことを確認し、production Storage / streaming以降の未検証範囲を分離しています。その後、意味、Evidence強度、Exact Binding / Verification Outcome / Profile authority / Storage-neutralityの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
