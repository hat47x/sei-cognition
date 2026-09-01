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

Verifier Registryはpayload bytesを受け取れば、JCS / raw-bytes Profileに従って`verified / failed / not_verified`を判定できる。一方、実際のExact Binding再検証では、payloadが別Storageや外部Sourceに存在する場合がある。

Storage locator、HTTP status、filesystem path、object key等をExact Bindingへ直接埋め込むとstorage-neutralityが崩れる。また、取得不能や一時的I/O障害をdigest mismatchへ変換すると、`not_verified != failed`というVerification Outcome境界を壊す。

そのため、source固有の取得処理を交換可能なruntime boundaryとして分離した。

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

Product Value TraceabilityとRuntime Conformance Evidenceには、今回のPayload Source boundaryを限定Executable Evidenceとして反映済みである。

SCN-0008 / SCN-0010については、actual Storage migrationや長期production更新そのものを検証したわけではないため、Scenario全体の達成状態へは昇格させない。

## Implemented boundary

runtimeでは次を分離した。

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
VerificationOutcome
```

実装:

```text
runtime/go/semanticruntime/payload_source.go
runtime/go/semanticruntime/payload_source_test.go
```

### PayloadRequest

Exact Bindingとcaller-supplied `MaxBytes`をPayload Sourceへ渡す。`MaxBytes`はlocal runtime policyであり、Universal Coreの固定値ではない。

### PayloadSource

filesystem、object store、remote artifact service等を将来接続できる交換可能なruntime interfaceとした。

Storage path、object key、HTTP details、credential、retry等をUniversal Contractへ持ち込まない。

### PayloadLoadResult

取得結果では次を分ける。

- `Available`
- payload bytes
- opaque `SourceRef`

`SourceRef`はruntime metadataであり、Exact Binding identityやRepresentation Profileのcanonical fieldではない。

## Verified semantics

### available payload

sourceが取得したbytesをPayload Source側では変更せずVerifier Registryへ渡す。

```text
source payload bytes
  == verifier input bytes
```

JCS canonicalization等はPayload SourceではなくRepresentation Verifierが担当する。

### unavailable payload

payloadを取得できない場合は`not_verified`とする。

```text
payload unavailable
  → not_verified

!= digest mismatch
```

### operational acquisition error

一時的なsource errorはcontent mismatchではない。

- semantic outcome: `not_verified`
- operational error: 別戻り値

```text
Verification Outcome
  != operational acquisition error
```

### resource limit

caller指定のlocal size limitを超えた場合もcontent failureとは推定しない。

- outcome: `not_verified`
- error: `ErrPayloadVerificationLimitExceeded`

limit値はUniversal Coreへ固定しない。

### zero-length payload

`Available=true`で0 byteのpayloadは「取得不能」ではなく、有効な0 byte payloadとして検証できる。

### source provenance / metadata

`SourceRef`等のsource固有metadataはcallerが運用上観測できるが、入力Exact BindingやVerification Outcomeのsemantic identityへコピーしない。

## Executed experiments

synthetic Payload SourceによるGo testsで、Required experimentsを次のとおり確認した。

1. available raw payload + matching digest → `verified`。
2. available payload + digest mismatch → `failed`、acquisition errorなし。
3. `Available=false` → `not_verified`。
4. operational source error → `not_verified`とerrorを分離。
5. source未設定 → `not_verified`。
6. zero-length available payload → 通常のpayloadとして`verified`可能。
7. caller指定limit超過 → `not_verified` + local limit error。
8. `SourceRef`を保持しつつExact Bindingを変更しない。
9. JCS payloadをSource側でnormalizeせず、Verifier側のcanonicalizationで検証する。
10. `go test ./...`でsemantic runtime、Provider Adapter、Verifier Registry、Payload Sourceを同時に回帰検査する。

## Executable Evidence

GitHub Actions `Semantic Runtime Conformance`:

- Run ID: `33457416359`
- Head SHA: `125bda1693f0712c2b741f149059d361cce7f97a`
- current Contract fixture recheck: **success**
- semantic runtime / Provider Adapter / Verifier / Payload Source tests: **success**
- conclusion: **success**

このRunが直接示すのは、synthetic sourceとcurrent runtimeによるpayload acquisition boundaryのExecutable Evidenceである。

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

## Completion criteria

- [x] Payload SourceをVerifier Registryから独立したinterfaceとして交換できる。
- [x] available / unavailable / source error / size limitを区別できる。
- [x] unavailable / source error / size limitをdigest mismatchへ誤変換しない。
- [x] source固有metadataをExact Binding / Profileへ混入させない。
- [x] raw bytesとJCSをsource経由で検証できる。
- [x] zero-length available payloadを検証できる。
- [x] current semantic runtime / Provider Adapter / Verifier Registryが回帰しない。
- [x] Semantic Runtime Conformanceがsuccessする。
- [x] Release / Operational / Adoption・Outcomeへ過大昇格していない。
- [x] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行った。

## Resolution

Required experimentsとCompletion criteriaをactual repositoryとCIで満たしたため、本IssueをResolvedとする。

今回追加したのはruntimeの取得境界であり、Storageやtransport mechanicsをUniversal Coreへ追加していない。新しいUniversal semantic conceptやADRも必要なかった。

production Storage adapterやstreaming等の未実装は、このIssueの未完了ではなく後続の具体的Evidence sliceとして扱う。

## Follow-up conditions

次が具体的に必要になった場合は、原則として別Issueへ分ける。

- large objectを全量`[]byte`化せず検証するstreaming requirement。
- production S3 / MinIO / filesystem / HTTP adapter。
- cache / retry / backoff / timeout policy。
- credential / Authorization Provider integration。
- source provenance自体をportable semantic exchangeへ含める必要性。

これらの必要性だけを理由にStorageやtransport mechanicsをUniversal Coreへ昇格させない。

## Reopen conditions

次の場合は本Issueの境界自体に反例が出たものとして再開を検討する。

- source errorや取得不能がcontent mismatchへ誤変換される。
- Payload SourceがbytesをVerifierへ渡す前に意味上のcanonicalizationを行う必要が生じる。
- source locatorがExact Binding semantic identityへ混入しないと成立しない反例が得られる。
- local resource policyとUniversal semantic contractを分離できない反例が得られる。

## Natural Japanese review

ADR-0007 / 0008 / 0009 / 0022 / 0023、Verifier Registry、REQ-0018 / 0020、SCN-0008 / 0010、actual Payload Source実装、Go tests、Runtime Conformance Run `33457416359`、Product Value Traceability、Runtime Conformance Evidenceへ戻って実装結果を照合した。その後、取得不能とcontent failure、semantic outcomeとoperational error、Storage mechanicsとExact Binding意味、Executable EvidenceとRelease / Operational / Adoption・Outcomeを混同しないよう条件を固定し、自然な日本語となることを最重要視して全文を再ドラフトした。最後に、Resolved化によってEvidence強度を過大評価していないことを再監査済みである。
