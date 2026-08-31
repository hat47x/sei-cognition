# SOZA Representation Profiles

更新日: 2026-08-31  
状態: **Current v1alpha1 Profile baseline / Fixture-scoped Executable Conformance PASS**

## 1. 役割

Representation Profileは、Semantic Contractで定めた意味を、特定のbytes / serialization / canonicalization / digest方式で検証可能にするための実現契約です。

```text
Semantic Contract != Representation Profile
```

Representation ProfileはUniversal Coreの意味そのものではありません。

## 2. Profileが所有するもの

必要に応じて次を定めます。

- representation media type
- canonicalization
- encoding constraints
- digest algorithm
- verification procedure
- test vectors
- interoperability constraints

同じSemantic Contractに対して複数のRepresentation Profileを持てます。

## 3. current Profile baseline

2026-08-31時点で、current `v1alpha1`基線として次の2つをactual repositoryへ実体化しています。

### JSON semantic representation

```text
soza.jcs+sha256/v1alpha1
```

Definition:

```text
contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md
```

RFC 8785 JCSをcanonicalizationの正本とし、SHA-256でdigestを生成します。

SOZA独自canonical JSONをstable authorityにはしません。Go verifier implementationは交換可能なprobeであり、Profile identityは特定libraryに依存しません。

高精度semantic valueをbinary64へ暗黙丸めしないこと、Unicode normalizationを勝手に行わないことを明示的な境界とします。

### Raw bytes representation

```text
soza.raw-bytes+sha256/v1alpha1
```

Definition:

```text
contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md
```

明示されたbytesそのものへSHA-256を適用します。改行変換、Unicode normalization、再encode等のcanonicalizationは行いません。

binary / archive / large object等を対象にでき、streaming verificationを許します。

## 4. current fixtures / probes

固定fixture:

```text
fixtures/representation-profiles/jcs-v1alpha1.json
fixtures/representation-profiles/raw-bytes-v1alpha1.json
fixtures/representation-profiles/verification-outcomes-v1alpha1.json
```

checker / probe:

```text
tools/check_representation_profiles.py
tools/jcs_probe.go
```

GitHub Actions:

```text
.github/workflows/representation-profile-conformance.yml
```

JCS Go probeでは`github.com/gowebpki/jcs`をcommit SHA `1a4242a66e1a8e03d7458324d0bc95c327527cbb`へ固定して実行しています。Go module resolver上では`v1.0.1`へ解決されます。

ただし、このdependencyはProfile Definitionの正本ではありません。

## 5. Executable Evidence

actual GitHub Actionsで、current Profile基線のfixture-scoped Executable ConformanceがPASSしています。

最新の三状態fixture追加後run:

- Run ID: `33347989530`
- Head SHA: `30678df18f3382407d3e0562f6ba358afb3120b3`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

Python checker:

```text
representation profile fixture check: PASS
(JCS verified vectors=4, raw vectors=2, outcome vectors=3)
```

Go JCS probe:

```text
JCS probe PASS: verified=4 negative=2
```

詳細は次を正本とします。

```text
contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md
```

## 6. Verification Outcome

ADR-0009に従い、次を区別します。

```text
verified
failed
not_verified
```

current fixtureでは、少なくとも次をactual Actionで再現しています。

- known Profile + digest一致 → `verified`
- known Profile + digest mismatch → `failed`
- unknown Profile → `not_verified`

```text
not_verified != failed
```

Profileやverifierが利用できないことを、content mismatchと同一視しません。

## 7. historical candidateとの関係

historical candidateには、SOZA独自のcustom canonical JSON + SHA-256 `v1alpha1`がありました。

これはcross-language pressure testとして価値がありますが、current stable defaultへ自動昇格しません。

current JSON Profileは、外部標準RFC 8785へ責務を寄せる形で再構成しています。

historical candidateのPASSもcurrent Executable Evidenceへ自動継承しません。

## 8. historical binding

historical bindingがどのdigest規則で作られたか不明な場合、現在のProfileで推測して再hashしてはなりません。

Profileを特定できない、payloadがない、verifierがない等の場合は`not_verified`として扱います。

historical M47 digestの回収・Profile対応付けはISSUE-000032で独立して追跡します。

ADR-0022により、historical M47 mappingが未完了でもcurrent/future Profile基線を利用できることを明示しています。

## 9. versioning

Representation ProfileはSemantic Contractとは独立してversionを持ちます。

representation-only changeがSemantic Contractのmajor version変更を必ず伴うわけではありません。

一方、同じProfile ID / versionでcanonicalization、digest algorithm、input bytes規則を後から別物へ変更してはなりません。

## 10. Evidence boundary

今回成立したのは、current `v1alpha1` Profileについての**fixture-scoped Executable Evidence**です。

```text
Profile fixture conformance PASS
  != Production Runtime integration
  != Release Evidence
  != Operational Evidence
```

また、すべてのRFC 8785 vectorを網羅したcertificationを主張するものでもありません。

Production RuntimeのVerifier Registry / Adapterは、runtime baselineを実体化する後続sliceでProfile Definitionへ従って実装します。

## 11. Decision / planning

- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — Verification Outcome separation
- ADR-0022 — current Representation Profile baseline
- ISSUE-000009 — current/future Profile stabilization
- ISSUE-000032 — historical M47 digest recovery

## 12. Natural Japanese review

current JCS / raw-bytes Profile Definition、actual GitHub Actionsのconformance結果、Verification Outcome、historical M47分離、Evidence境界をactual repositoryの状態へ照合した。その後、Profileの役割、数値、未完了範囲、規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
