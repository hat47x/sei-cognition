# ISSUE-000038: RuntimeへRepresentation Verifier Registryを実装する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0021, ADR-0022, ADR-0023**  
Updated: 2026-09-01

## Goal

Accepted済みのRepresentation ProfileをSemantic Runtimeへ接続し、Exact Bindingのcontent digestをruntime上で再検証できる最小のVerifier Registryを実装する。

対象Profile:

```text
soza.jcs+sha256/v1alpha1
soza.raw-bytes+sha256/v1alpha1
```

新しいSemantic ContractやUniversal Core型は追加せず、ADR-0008 / ADR-0009 / ADR-0023で決定済みの検証境界をExecutable Evidenceへ落とす。

## Resolution

### 1. Runtime Verifier Registryを実装した

次を追加した。

```text
runtime/go/semanticruntime/verifier.go
runtime/go/semanticruntime/verifier_test.go
```

`VerifierRegistry`は`RepresentationProfile`の`profile_id + version`からVerifierを解決する。

current default Registryは次の2 Profileを登録する。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Profile authorityはProfile Definition / RFC 8785側に残し、RegistryやGo libraryをsemantic authorityへ昇格させていない。

### 2. Exact BindingとVerification Outcomeを分離した

Registryは入力`ExactBinding`を変更せず、別の`VerificationOutcome`を返す。

```text
Exact Binding metadata valid
  != Exact Binding content verified

Exact Binding
  != Verification Outcome
```

### 3. 三つのVerification Outcomeを実装した

- known Profile + digest一致 → `verified`
- known Profile + digest mismatch / Profile入力制約違反 → `failed`
- unknown Profile / payload unavailable → `not_verified`

未知Profileやpayload不足をcontent mismatchへ読み替えていない。

### 4. JCS Profile fixtureをruntime testから直接再利用した

`fixtures/representation-profiles/jcs-v1alpha1.json`をGo runtime testから読み、少なくとも次を再現した。

- property order / insignificant whitespace差
- RFC 8785 representative sample
- duplicate key rejection
- unsafe large integer rejection
- NFC / NFD non-normalization
- fixed SHA-256 digest

unsafe integer preflightは既存JCS probeと同じ境界を実装し、`9007199254740993`をbinary64へ暗黙丸めしない。

### 5. raw-bytes Profile fixtureをruntime testから直接再利用した

`fixtures/representation-profiles/raw-bytes-v1alpha1.json`のUTF-8 text / binary bytesをそのまま検証し、固定digestを再現した。

改行変換、Unicode normalization、再encode等は行わない。

### 6. dependencyを再現可能に固定した

`runtime/go/go.mod`へ次を追加した。

```text
github.com/gowebpki/jcs v1.0.1
```

`runtime/go/go.sum`へmodule checksumを記録した。

ADR-0023の既存probeがcommit `1a4242a66e1a8e03d7458324d0bc95c327527cbb`から解決しているmodule versionと一致する。

### 7. CI triggerをProfile fixtureへ広げた

`.github/workflows/runtime-conformance.yml`のpath条件へ次を追加した。

```text
fixtures/representation-profiles/**
```

Profile fixtureが変わった場合もruntime verificationの回帰検査が走る。

## CI / Evidence

初回実装後のSemantic Runtime Conformance `33452054067`では、Contract fixture再検査はsuccessしたが、Go側でJCS moduleの`go.sum`不足を検出してfailureとなった。

このfailureをその場で解消し、checksumを追加した後に再実行した。

### Semantic Runtime Conformance

- Run ID: `33452115728`
- Head SHA: `9941f49a5af3b5443f3cfaca3b263e07989d3ba4`
- Contract fixture recheck: **success**
- semantic runtime tests: **success**
- Provider Adapter tests: **success**
- Representation Verifier tests: **success**

### 既存基線の回帰Evidence

- Representation Profile Conformance: Run `33389973772` — **success**
- Contract Conformance: Run `33390534942` — **success**
- Plan integrity（Issue登録時）: Run `33451921654` — **success**

Profile Definition / fixture自体は本Issueで変更していないため、Profile Conformanceの既存successを維持しつつ、同fixtureをruntime testへ直接接続した。

## Acceptance

- [x] current 2 Profileをruntime Registryから解決できる。
- [x] JCS Profile fixtureのpositive / negative境界をGo runtime testで再現できる。
- [x] raw-bytes fixtureをGo runtime testで再現できる。
- [x] `verified / failed / not_verified`をruntime testで区別できる。
- [x] unknown Profileとpayload不足を`failed`へ誤変換しない。
- [x] Exact Bindingを検証結果でmutateしない。
- [x] current Contract / runtime / Provider Adapter testsが回帰しない。
- [x] Representation Profile基線のconformance successを確認し、Semantic Runtime Conformanceをsuccessさせた。
- [x] Release / Operational / Adoption・Outcome Evidenceへ過大昇格していない。
- [x] 実装・文書を自然な日本語となることを最重要視して再監査した。

## Evidence boundary

本Issueで成立したのは、呼出し側から与えられたpayload bytesをcurrent Profileで検証する**in-process / fixture-scoped Executable Evidence**である。

```text
Runtime Verifier Registry PASS
  != external payload acquisition
  != object-storage integration
  != production streaming verification
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

historical M47 digest規則は推測していない。ISSUE-000034は独立Blocked事項のままとする。

## Reopen conditions

次の場合は再開または後続Issueを検討する。

- 同じProfile ID / versionで別実装間のdigest差が確認された。
- current verifier libraryに重大なsecurity / maintenance / interoperability問題が見つかった。
- streamingやexternal object source等、現在の`[]byte`入力では扱えない主要use caseが具体化した。
- 新しいRepresentation Profileをruntimeへ登録する際、current Registry abstractionでは意味を保てないことが分かった。

production Provider / TEI interoperability、Release、Operational、Adoption / Outcomeは本Issueの再開理由ではなく、それぞれ別Evidence sliceとして扱う。

## Natural Japanese review

ADR-0008、ADR-0009、ADR-0022、ADR-0023、current Profile Definition、Profile fixture、JCS Go probe、Semantic Runtime実装、Contract Traceability、actual CI結果へ戻って実装結果を照合した。初回CI failureとchecksum追加による解消もEvidence履歴として保持し、成立したin-process verificationと未検証のexternal / production範囲を分離した。その後、意味、仕様、留保、Evidence強度を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
