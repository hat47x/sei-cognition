# ISSUE-000040: Exact Binding検証のpayload取得境界を実装する

Status: **Open**  
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

ここでStorage locator、HTTP status、filesystem path、object key等をExact Bindingへ直接埋め込むと、ADR-0007のstorage-neutralityが崩れる。また、取得不能をdigest mismatchへ変換するとADR-0009の`not_verified != failed`を壊す。

そのため、source固有の取得処理を交換可能なruntime boundaryとして分離する。

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

## Boundary

runtime側では、概念的に次を分ける。

```text
Exact Binding
  ↓
Payload request
  ↓
Payload Source / Adapter
  ↓
Payload acquisition result
  ↓
Verifier Registry
  ↓
Verification Outcome
```

Payload Sourceは交換可能なruntime implementationであり、Universal Contract familyではない。

## Required semantics

### 1. available payload

sourceがpayloadを取得できた場合、そのbytesを変更せずVerifier Registryへ渡す。

```text
source payload bytes
  == verifier input bytes
```

JCS等のcanonicalizationはPayload SourceではなくRepresentation Verifierが担当する。

### 2. unavailable payload

retention、non-disclosure、not found、source未接続等によりpayloadを取得できない場合、Exact Bindingを`failed`へ変換しない。

```text
payload unavailable
  → not_verified

!= digest mismatch
```

### 3. operational acquisition error

一時的I/O障害等のsource errorもcontent mismatchではない。

semantic outcomeは`not_verified`としつつ、runtime callerが運用上のerrorを別に観測できるようにする。

```text
semantic Verification Outcome
  != operational acquisition error
```

### 4. resource limit

local runtimeのsize limit等でpayloadを読み込めない場合も、contentが誤っていると推定しない。

```text
local verification limit exceeded
  → not_verified
```

limit値自体をUniversal Core定数にはしない。caller / runtime policyから与える。

### 5. source provenance

source implementationは必要に応じてopaqueな`source_ref`等のmetadataを返してよいが、それをExact Binding identityやRepresentation Profileへ混ぜない。

Provider固有locatorのUniversal schemaは作らない。

## Non-goals

- S3、MinIO、Git、HTTP、filesystem等のproduction adapterを一括実装すること。
- credential / Authorization処理をUniversal Contract化すること。
- streaming verifierを今回の必須条件にすること。
- payload cache policyを固定すること。
- source locatorをLogical ReferenceやExact Bindingのcanonical fieldへ追加すること。
- acquisition成功をhistorical reconstruction全体の成功へ昇格させること。

## Required experiments

1. available raw payload + matching digest → `verified`。
2. available payload + digest mismatch → `failed`。
3. sourceが`available=false` → `not_verified`。
4. source operational error → outcomeは`not_verified`、errorは別に返る。
5. source未設定 → `not_verified`。
6. zero-length payloadは「取得不能」ではなく、availableな0 byteとして扱える。
7. caller指定limitを超えるpayload → `not_verified`であり`failed`ではない。
8. source metadata / locatorがExact Bindingへ書き戻されない。
9. JCS payloadでもPayload Source側はJSON normalizationを行わない。
10. current verifier / semantic runtime / Provider Adapter testsが回帰しない。

## Deliverables

- runtimeのPayload Source interface / request / result型。
- Payload SourceからVerifier Registryへ接続するorchestration。
- `not_verified`とoperational errorの分離。
- caller-supplied payload size limit。
- synthetic sourceを使ったGo tests。
- Runtime Conformanceへの統合。
- actual Evidenceに基づくruntime / traceability文書更新。

## Completion criteria

- [ ] Payload SourceをVerifier Registryから独立したinterfaceとして交換できる。
- [ ] available / unavailable / source error / size limitを区別できる。
- [ ] unavailable / source error / size limitをdigest mismatchへ誤変換しない。
- [ ] source固有metadataをExact Binding / Profileへ混入させない。
- [ ] raw bytesとJCSの少なくとも一例をsource経由で検証できる。
- [ ] zero-length available payloadを検証できる。
- [ ] current semantic runtime / Provider Adapter / Verifier Registryが回帰しない。
- [ ] Semantic Runtime Conformanceがsuccessする。
- [ ] Release / Operational / Adoption・Outcomeへ過大昇格していない。
- [ ] 文書を自然な日本語となることを最重要視して再ドラフトし、最終意味監査を行った。

## Reopen / follow-up conditions

Resolved後、次が具体化した場合は再開せず原則として後続Issueへ分ける。

- large objectを全量`[]byte`化せず検証するstreaming requirement。
- production S3 / MinIO / filesystem / HTTP adapter。
- cache / retry / backoff / timeout policy。
- credential / Authorization Provider integration。
- source provenance自体をportable semantic exchangeへ含める必要性。

それらの必要性からStorageやtransport mechanicsをUniversal Coreへ即座に昇格させない。

## CI / verification

最低限、次を確認する。

- Semantic Runtime Conformance
- Plan integrity

既存ContractやRepresentation Profileを変更した場合だけ、対応するConformance workflowも追加で確認する。

CI failureを検出した場合は、原因を解消してsuccessを確認してから後続作業へ進む。

## Natural Japanese review

ADR-0007 / 0008 / 0009 / 0022 / 0023、current Verifier Registry、SCN-0008 / 0010、REQ-0018 / 0020へ戻って境界を整理した。その後、取得不能とcontent failure、semantic outcomeとoperational error、Storage mechanicsとExact Binding意味を混同しないよう条件を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
