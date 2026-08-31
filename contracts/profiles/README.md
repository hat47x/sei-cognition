# SOZA Representation Profiles

更新日: 2026-08-31  
状態: **Current v1alpha1 Profile Baseline / Fixture-scoped Executable Conformance PASS**

## 1. 役割

Representation Profileは、Semantic Contractで定めた意味を、特定のbytes / serialization / canonicalization / digest方式で検証可能にするための実現契約です。

```text
Semantic Contract != Representation Profile != verifier implementation
```

Representation ProfileはUniversal Coreの意味そのものではありません。Semantic Contractと独立したversioning・実装交換境界を持ちます。

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

ADR-0023により、2026-08-31時点のcurrent/future `v1alpha1`基線として次の2 ProfileをAcceptedしています。

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

このdependencyはProfile Definitionの正本ではありません。

## 5. Executable Evidence

actual GitHub Actionsで、current `v1alpha1` Profile基線のfixture-scoped Executable ConformanceがPASSしています。

Verification Outcome追加後の代表run:

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

詳細は`contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`を参照します。

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

Profileやverifierが利用できないことをcontent mismatchと同一視しません。

## 7. first semantic runtimeとの関係

current Go first semantic runtimeはContract ArtifactのExact Binding metadataやProfile identityを読み、historical basisを再構成できる範囲を持ちます。

一方、Profileごとのcanonicalization / digest verifierをproduction Runtime Registryとして統合したことまでは、current first sliceのEvidenceに含めません。

```text
runtime can read binding metadata
  != production verifier registry established
```

Profile Definitionとverifier implementationの交換可能性を維持します。

## 8. historical candidateとの関係

historical candidateには、SOZA独自のcustom canonical JSON + SHA-256や、JCS / raw-bytesの検討資産がありました。

それらはcross-language pressure testや設計入力として価値がありますが、current Profileへ自動昇格したものではありません。

current 2 ProfileはADR-0023でcurrent Product Value / Requirement / Contractへ戻って改めてAcceptedし、actual fixture / probeでExecutable Evidenceを取り直しています。

```text
historical PASS != current Profile conformance
```

## 9. historical binding

historical bindingがどのdigest規則で作られたか不明な場合、現在のProfileで推測して再hashしてはなりません。

Profileを特定できない、payloadがない、verifierがない等の場合は`not_verified`として扱います。

historical M47 digestの回収・Profile対応付けはISSUE-000034で独立して追跡します。

ADR-0023により、historical M47 mappingが未完了でもcurrent/future Profile基線を利用できることを明示しています。

## 10. versioning

Representation ProfileはSemantic Contractとは独立してversionを持ちます。

representation-only changeがSemantic Contractのmajor version変更を必ず伴うわけではありません。

一方、同じProfile ID / versionでcanonicalization、digest algorithm、input bytes規則を後から別物へ変更してはなりません。

## 11. Evidence boundary

Product Valueに従い、次を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current `v1alpha1` Profile DefinitionはDesign Evidenceであり、fixture / Go probeのPASSはscoped Executable Evidenceです。

未検証:

- production-grade verifier registry integration
- network / object storageからのlarge binary streaming運用
- historical M47 digest mapping
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

すべてのRFC 8785 vectorを網羅したcertificationも主張しません。

## 12. Decision / planning

- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — Verification Outcome separation
- ADR-0023 — current Representation Profile baseline
- ISSUE-000009 — current/future Profile stabilization（Resolved）
- ISSUE-000034 — historical M47 digest recovery（Blocked）

## 13. Natural Japanese review

current JCS / raw-bytes Profile Definition、actual Profile Conformance、first semantic runtimeの境界、Verification Outcome、historical M47分離、5段階Evidenceへ戻って全文を再監査しました。その後、Profileの役割、数値、未完了範囲、規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
