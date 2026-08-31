# SOZA Representation Profiles

更新日: 2026-08-31  
状態: **Current Profile Definitions materialized / Executable conformance in progress**

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

## 3. current Profile Definitions

2026-08-31時点で、次の2つを`v1alpha1`候補としてactual repositoryへ実体化しています。

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

JCS Go probeでは`github.com/gowebpki/jcs`をcommit SHAで固定して実行します。ただし、このdependencyはProfile Definitionの正本ではありません。

## 5. historical candidateとの関係

historical candidateには、SOZA独自のcustom canonical JSON + SHA-256 `v1alpha1`がありました。

これはcross-language pressure testとして価値がありますが、current stable defaultへ自動昇格しません。

current JSON Profileは、外部標準RFC 8785へ責務を寄せる方向で再構成しています。

historical candidateのPASSもcurrent Executable Evidenceへ自動継承しません。

## 6. historical binding

historical bindingがどのdigest規則で作られたか不明な場合、現在のProfileで推測して再hashしてはなりません。

Profileを特定できない、payloadがない、verifierがない等の場合は`not_verified`として扱える必要があります。

```text
not_verified != failed
```

historical M47 digestの回収・Profile対応付けはISSUE-000032で独立して追跡します。

## 7. versioning

Representation ProfileはSemantic Contractとは独立してversionを持ちます。

representation-only changeがSemantic Contractのmajor version変更を必ず伴うわけではありません。

一方、同じProfile ID / versionでcanonicalization、digest algorithm、input bytes規則を後から別物へ変更してはなりません。

## 8. Evidence boundary

Profile Definitionとfixtureの存在はDesign Evidenceです。

Executable Evidenceには、actual repository上での再現可能な検査が必要です。

```text
Profile Definition exists
  != Profile conformance PASS
  != Runtime integration
  != Release Evidence
  != Operational Evidence
```

ISSUE-000009はcurrent/future Profileの安定化を追跡します。CIがsuccessするまではExecutable Acceptance完了を主張しません。

## 9. Natural Japanese review

current JCS / raw-bytes Profile Definition、historical M47分離、Evidence境界をactual repositoryの状態へ照合した。その後、Profileの役割と未完了範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
