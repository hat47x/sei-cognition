# ISSUE-000040: Exact Binding検証のpayload取得境界を実装する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0022, ADR-0023**  
Updated: 2026-09-01

## Goal

`ISSUE-000038`で実装したRepresentation Verifier Registryへ、filesystem、object store、remote artifact service等から取得したpayloadを安全に渡せるよう、**payload acquisitionとcontent verificationを分離したruntime境界**を実装する。

このIssueでは特定Storageやobject storeをSOZA Coreへ固定しない。

```text
Payload acquisition
  != Representation verification
  != Exact Binding semantic identity
```

## Background

current Verifier Registryは`[]byte`のpayloadを受け取れば、JCS / raw-bytes Profileに従って`verified / failed / not_verified`を返せる。

一方、実際のExact Binding再検証では、payloadが別Storageや外部Sourceに存在する場合がある。

Storage locator、HTTP status、filesystem path、object key等をExact Bindingへ直接埋め込むとADR-0007のstorage-neutralityが崩れる。また、取得不能をdigest mismatchへ変換するとADR-0009の`not_verified != failed`を壊す。

そのため、本Issueではsource固有の取得処理を交換可能なruntime boundaryとして分離した。

## Product / Requirement trace

主に次へ関係する。

- V1 Historical Reconstruction
- V3 Revision Integrity
- V8 Execution Independence
- REQ-0001 — 耐久的な意味の連続性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0009 — Revision / Supersessionの完全性
- REQ-0018 — Storage実装から意味を独立させる
- REQ-0020 — Evidenceを超える達成主張をしない
- SCN-0008 — Storageを交換する
- SCN-0010 — 可変Artifact更新後に過去Decisionを再構成する

## Implemented boundary

runtime側では次を分離した。

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

実装:

```text
runtime/go/semanticruntime/payload_source.go
runtime/go/semanticruntime/payload_source_test.go
```

### PayloadRequest

Exact Bindingとcaller指定`MaxBytes`をPayload Sourceへ渡す。

`MaxBytes <= 0`は、このorchestration layerで固定byte limitを課さないことを意味する。limit値をUniversal Core定数にはしていない。

### PayloadLoadResult

取得結果は次を分ける。

- `Available`
- payload bytes
- opaqueな`SourceRef`

`SourceRef`はruntime metadataであり、Exact BindingやRepresentation Profileのcanonical fieldへ書き戻さない。

### PayloadSource

Storage / transport mechanicsを交換可能なinterfaceへ閉じ込める。

```text
PayloadSource.LoadPayload(ctx, request)
```

filesystem path、object key、HTTP detail、credential、retry等の共通Universal schemaは新設していない。

### VerifyFromPayloadSource

Payload Sourceから取得した結果をVerifier Registryへ接続する。

```text
available payload + matching digest
  → verified

available payload + digest mismatch
  → failed

unavailable payload
  → not_verified

operational acquisition error
  → not_verified + separate runtime error

local verification limit exceeded
  → not_verified + separate runtime error
```

## Verified semantics

### 1. available payload

sourceが取得したbytesをcontent verifierへ渡す。

JCS等のcanonicalizationはPayload SourceではなくRepresentation Verifierが担当する。

JCS testでは、sourceが非canonicalなJSON bytesを返しても、そのbytes自体をsource側で変更せず、JCS verifierがcanonicalizationを行ってdigest一致を確認できた。

### 2. unavailable payload

`Available=false`は`not_verified`になる。

```text
payload unavailable
  != digest mismatch
```

### 3. operational acquisition error

source error時はsemantic outcomeを`not_verified`とし、operational errorを別戻り値で保持する。

```text
semantic Verification Outcome
  != operational acquisition error
```

### 4. resource limit

caller指定limitを超えたpayloadは`ErrPayloadVerificationLimitExceeded`を返し、semantic outcomeは`not_verified`とする。

contentが不正であるとは推定しない。

### 5. zero-length payload

`Available=true`で0 byteのpayloadは、取得不能ではなく有効な0 byte contentとして検証できる。

### 6. source metadata / Exact Binding

sourceのopaque metadataは戻り値として観測できる一方、Exact Bindingは検証前後で不変であることをtestした。

## Executable Evidence

GitHub Actions `Semantic Runtime Conformance`:

- Run ID: `33457416359`
- Head SHA: `125bda1693f0712c2b741f149059d361cce7f97a`
- current Contract fixture recheck: **success**
- semantic runtime / Provider Adapter / Verifier / Payload Source tests: **success**
- conclusion: **success**

synthetic Payload Sourceで少なくとも次を確認した。

1. raw bytes + matching digest → `verified`
2. raw bytes + digest mismatch → `failed`
3. unavailable → `not_verified`
4. operational error → `not_verified` + error
5. nil source → `not_verified`
6. available zero-length payload → `verified`
7. local size limit超過 → `not_verified` + limit error
8. Exact Binding非変異
9. source metadataがExact Bindingへ混入しない
10. noncanonical JCS bytesをsource側でnormalizeせず、JCS verifier側で検証できる
11. existing semantic runtime / Provider Adapter / Verifier testsが回帰しない

## Completion criteria

- [x] Payload SourceをVerifier Registryから独立したinterfaceとして交換できる。
- [x] available / unavailable / source error / size limitを区別できる。
- [x] unavailable / source error / size limitをdigest mismatchへ誤変換しない。
- [x] source固有metadataをExact Binding / Profileへ混入させない。
- [x] raw bytesとJCSの少なくとも一例をsource経由で検証できる。
- [x] zero-length available payloadを検証できる。
- [x] current semantic runtime / Provider Adapter / Verifier Registryが回帰しない。
- [x] Semantic Runtime Conformanceがsuccessする。
- [x] Release / Operational / Adoption・Outcomeへ過大昇格していない。
- [x] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行った。

## Evidence boundary

本Issueで成立したのは、**synthetic Payload Sourceを使ったruntime-boundary scoped Executable Evidence**までである。

```text
Payload Source boundary PASS
  != production filesystem adapter
  != production S3 / MinIO / object-store adapter
  != production HTTP / remote artifact service
  != production streaming verification
  != Storage migration completed
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

実Storageの可用性、retention、credential、retry、network failure、large-object behaviorは未検証のまま残す。

## Reopen / follow-up conditions

本Issueは最小runtime boundaryが成立したためResolvedとする。

次が具体化した場合は、原則として後続Issueへ分ける。

- large objectを全量`[]byte`化せず検証するstreaming requirement。
- production S3 / MinIO / filesystem / HTTP adapter。
- cache / retry / backoff / timeout policy。
- credential / Authorization Provider integration。
- source provenance自体をportable semantic exchangeへ含める必要性。

それらの必要性からStorageやtransport mechanicsをUniversal Coreへ即座に昇格させない。

## CI / verification

本Issueのclosureに使用したSemantic Runtime Conformanceはsuccessしている。

Plan registryへResolved状態を同期した後、Plan integrityもsuccessであることを確認する。

既存ContractやRepresentation Profileの規範内容は変更していないため、本Issueのclosure条件として新しいContract familyやProfile versionは追加しない。

## Natural Japanese review

ADR-0007 / 0008 / 0009 / 0022 / 0023、current Verifier Registry、実装したPayload Source boundary、SCN-0008 / 0010、REQ-0018 / 0020、GitHub Actions Run `33457416359`へ戻ってResolutionを照合した。その後、取得不能とcontent failure、semantic outcomeとoperational error、Storage mechanicsとExact Binding意味、synthetic Evidenceとproduction Evidenceを混同しないよう条件を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
