# ISSUE-000009: Portable Exact BindingのRepresentation Profileを安定化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0023**  
Updated: 2026-08-31

## Goal

Portable Exact Bindingを、Go固有の実装やSOZA独自canonicalizationだけに依存せず、複数言語・複数representationで検証可能な仕組みへ安定化する。

本Issueでは、**current / future bindingに使用するRepresentation Profile**を対象とする。

historical M47 digestの規則回収はISSUE-000034へ分離した。historical Profileが未確認でも、ADR-0009に従って`not_verified`として保持できるため、current Profile基線の成立条件には含めない。

## Resolution

### 1. current JSON Profileを実体化した

current JSON Representation Profileとして次を実体化した。

```text
soza.jcs+sha256/v1alpha1
```

Definition:

```text
contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md
```

canonicalizationの正本はRFC 8785 JCSとし、SOZA独自canonical JSON algorithmをstable authorityにはしない。

SHA-256は本Profile versionが所有し、Universal Coreの唯一のhash algorithmにはしない。

### 2. raw-bytes Profileを別に実体化した

non-JSON / binary / raw file content向けに次を実体化した。

```text
soza.raw-bytes+sha256/v1alpha1
```

Definition:

```text
contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md
```

このProfileは、明示されたbytesへcanonicalizationを行わず直接SHA-256を適用する。

```text
raw bytes identity != semantic JSON identity
```

JCSとraw-bytesを一つの曖昧なdigest規則へ統合しない。

### 3. high-precision境界を固定した

RFC 8785 / I-JSONがJSON numberの相互運用でIEEE 754 binary64を前提とするため、binary64で安全に保持できないsemantic valueを暗黙に丸めてdigestしない。

current probeでは少なくとも`9007199254740993`をJCSへ渡す前に拒否する。

より高精度な整数・decimal等が必要な場合は、型付き文字列等のlossless representationへ明示的に投影する。

### 4. Unicode normalizationをProfile内部で行わない

NFC / NFD等を見た目や意味の近さだけで自動同一化しない。

current fixtureでは、同じ文字のNFC / NFD表現が異なるcanonical bytes / digestとして残ることを確認した。

normalizationが必要なdomainでは、JCSより前段の明示されたsemantic / representation変換として扱う。

### 5. verifier実装をProfile authorityから分離した

current Go probeでは`github.com/gowebpki/jcs`を使用するが、Profileの正本にはしない。

GitHub Actionsではcommit SHA `1a4242a66e1a8e03d7458324d0bc95c327527cbb`を固定し、Go module resolver上では`github.com/gowebpki/jcs v1.0.1`へ解決された。

```text
RFC 8785 + SOZA Profile Definition
  = Profile authority

Go library
  = replaceable verifier implementation
```

### 6. current fixtureをactual repositoryへ固定した

```text
fixtures/representation-profiles/jcs-v1alpha1.json
fixtures/representation-profiles/raw-bytes-v1alpha1.json
fixtures/representation-profiles/verification-outcomes-v1alpha1.json
```

検査:

```text
tools/check_representation_profiles.py
tools/jcs_probe.go
```

GitHub Actions:

```text
.github/workflows/representation-profile-conformance.yml
```

### 7. Verification Outcomeの三状態を実証した

```text
known Profile + digest match    → verified
known Profile + digest mismatch → failed
unknown Profile                 → not_verified
```

unknown Profileをcontent mismatchとして扱わない。

```text
not_verified != failed
```

## Executable Evidence

verification outcome追加後のGitHub Actions Run ID `33347989530`で、`profile-fixtures`と`jcs-go-probe`がともにsuccessした。

主要結果:

- key order / whitespace差 → 同じcanonical digest
- representative number / string sample → PASS
- duplicate key → reject
- unsafe integer `9007199254740993` → JCS前にreject
- NFC / NFD → 異なるdigestとして保持
- raw UTF-8 / binary bytes → fixed SHA-256再現
- known match / mismatch / unknown Profile → `verified / failed / not_verified`を分離

詳細は`contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`を正とする。

## Acceptance

### Design Acceptance

- [x] JCS Profile Definitionがactual repositoryに存在する。
- [x] Profileの正本をRFC / Profile Definitionとし、特定Go libraryをauthorityにしていない。
- [x] high-precision valueの暗黙丸め禁止を明示した。
- [x] Unicode normalizationを行わないことを明示した。
- [x] raw-bytes Profileとの意味差を明示した。
- [x] ADR-0023でcurrent Profile選択理由とhistorical M47分離をAcceptedした。
- [x] Profile文書を自然な日本語で再ドラフトし、最終意味監査を行った。

### Executable Acceptance

- [x] representative vectorがPASSした。
- [x] key order / whitespace差で同じcanonical resultを確認した。
- [x] duplicate keyを拒否した。
- [x] high-precision valueを暗黙丸めする入力をJCS前に拒否した。
- [x] Unicode normalizationを勝手に行わないことを確認した。
- [x] Go verifier candidateをcommit固定でactual GitHub Actionsから実行した。
- [x] Profile identity / Contract意味をGo library APIから分離した。
- [x] raw-bytes Profileの代表fixtureを再現した。
- [x] `verified / failed / not_verified`をactual fixtureで区別した。

## Evidence state at closure

- Representation Profile Design Baseline: **Satisfied**
- Representation Profile fixture-scoped Executable Evidence: **Satisfied**
- historical M47 digest mapping: **Not Yet Verified — ISSUE-000034**
- first semantic runtimeへのProduction Profile verifier統合: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

current first semantic runtime baseline自体はすでに実体化されている。ただしADR-0022のfirst sliceはProfile verifier統合をAcceptance条件としていないため、Profile fixture PASSをRuntime verifier integration済みとは読み替えない。

## What this closure does not mean

本IssueをResolvedにしても、次は未完了である。

- historical M47 digestのRepresentation Profile特定
- current runtimeへの必要な範囲でのVerifier Registry / Adapter統合
- network / object storageでのlarge binary streaming運用
- RFC 8785全vectorを網羅するcertification
- Release Evidence
- Operational Evidence

## Dependencies / Follow-up

- ADR-0007 — storage-neutral persistence
- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — verification outcome separation
- ADR-0023 — current Representation Profile baseline
- ISSUE-000031 — Contract fixture-scoped conformance（Resolved）
- ISSUE-000033 — first semantic runtime（Resolved）
- ISSUE-000034 — historical M47 digest recovery（Blocked）

Runtime verifier integrationは、current Product / Scenarioで必要性が具体化した時点で独立Issueとして扱う。runtime baselineが存在することだけを理由に暗黙実装しない。

## Natural Japanese review

Profile Definition、ADR-0023、GitHub Actions実ログ、current first runtime、verification outcome fixtureを照合した。その後、Profile fixtureで確認できた範囲とhistorical M47、Runtime verifier integration、Release、Operationalの未検証範囲を分離し、意味、数値、Evidence強度、規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
