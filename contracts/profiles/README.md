# SEI Representation Profiles

更新日: 2026-09-01  
状態: **Current v1alpha1 Profile Baseline / Fixture-scoped Executable Conformance PASS**

## 1. 役割

Representation Profileは、Semantic Contractで定めた意味を、特定のbytes / serialization / canonicalization / digest方式で検証可能にするための実現契約です。

```text
Semantic Contract != Representation Profile != verifier implementation
```

Representation ProfileはUniversal Coreの意味そのものではありません。Semantic Contractとは独立したversioning・実装交換境界を持ちます。

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

ADR-0023により、current/future `v1alpha1`基線として次の2 ProfileをAcceptedしています。

### JSON semantic representation

```text
sei.jcs+sha256/v1alpha1
```

Definition:

```text
contracts/profiles/SEI_JCS_SHA256_PROFILE_v1alpha1.md
```

RFC 8785 JCSをcanonicalizationの正本とし、SHA-256でdigestを生成します。

SEI独自canonical JSONをstable authorityにはしません。Go verifier implementationは交換可能な実装であり、Profile identityを特定libraryへ固定しません。

高精度semantic valueをbinary64へ暗黙丸めしないこと、Unicode normalizationを勝手に行わないことを明示的な境界とします。

### Raw bytes representation

```text
sei.raw-bytes+sha256/v1alpha1
```

Definition:

```text
contracts/profiles/SEI_RAW_BYTES_SHA256_PROFILE_v1alpha1.md
```

明示されたbytesそのものへSHA-256を適用します。改行変換、Unicode normalization、再encode等のcanonicalizationは行いません。

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

Profile Conformance representative run:

- Run ID: `33347989530`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

JCS Go probeで利用する実装dependencyはProfile Definitionの正本ではありません。

## 5. Verification Outcome

ADR-0009に従い、次を区別します。

```text
verified
failed
not_verified
```

基本境界:

- known Profile + digest一致 → `verified`
- known Profile + digest mismatch → `failed`
- Profile input constraint違反 → `failed`
- unknown Profile → `not_verified`
- payload unavailable → `not_verified`

```text
not_verified != failed
```

Profile、verifier、payloadが利用できないことをcontent mismatchと同一視しません。

## 6. current runtime Verifier Registry

ISSUE-000038により、current Go semantic runtimeへRepresentation Verifier Registryを実装しました。

```text
runtime/go/semanticruntime/verifier.go
runtime/go/semanticruntime/verifier_test.go
```

current Registryは次を解決します。

```text
sei.jcs+sha256/v1alpha1
sei.raw-bytes+sha256/v1alpha1
```

Profile authorityはProfile Definitionと参照外部標準にあり、Go interfaceやlibrary APIを正本にはしません。

Verifier Registry closure:

- Run ID: `33452115728`
- Contract fixture recheck: **success**
- semantic runtime tests: **success**
- Provider Adapter tests: **success**
- Representation Verifier tests: **success**

これはin-process runtime implementationに対するExecutable Evidenceです。production deploymentや外部Storage取得までを証明しません。

## 7. payload acquisitionとの分離

ISSUE-000040では、payload取得をVerifier Registryから別の交換可能な`PayloadSource`境界へ分離しました。

```text
Exact Binding
  ↓
Payload Source
  ↓
Verifier Registry
  ↓
Verification Outcome
```

次を検査しています。

- available raw payload + digest一致 → `verified`
- available JCS payload + digest一致 → `verified`
- digest mismatch → `failed`
- payload unavailable → `not_verified`
- source operational error → semantic outcomeは`not_verified`、運用errorは別に返す
- caller指定size limit超過 → `not_verified`
- zero-length available payloadを取得不能と誤認しない
- source固有metadataをExact Binding / Profileへ混入させない

Payload acquisition boundary:

- Run ID: `33457416359`
- Contract fixture recheck: **success**
- semantic runtime / Provider Adapter / Verifier / Payload Source tests: **success**

これはsynthetic Payload SourceによるExecutable Evidenceです。production filesystem / S3 / MinIO / HTTP、credential、retry、streaming運用のEvidenceではありません。

## 8. historical candidateとの関係

historical candidateには、SEI独自のcustom canonical JSON + SHA-256や、JCS / raw-bytesの検討資産がありました。

それらはpressure testや設計入力として価値がありますが、current Profileへ自動昇格したものではありません。

```text
historical PASS != current Profile conformance
```

current 2 ProfileはADR-0023でcurrent Product Value / Requirement / Contractへ戻ってAcceptedし、actual fixture / probe / runtime testでEvidenceを取り直しています。

## 9. historical M47 binding

historical bindingがどのdigest規則で作られたか不明な場合、現在のProfileで推測して再hashしてはなりません。

ISSUE-000034では、historical M47 digest規則の回収を独立して実施しました。

回収できたもの:

- M47 semantic Contract
- M47 Implementation Report
- M47 Release Closure
- historical KJ / cultural-substrate-weaving Method Definition payload

回収できなかったもの:

- actual digest-producing M47 Go source
- actual M47 conformance tool
- actual historical binding digest anchor
- M47 source / release archive

GitHub reachable history、branch、Actions、Library semantic / exact-name search、個別Go / Python inventory、archive時系列まで確認したうえで、現在保持された直接Evidenceからhistorical digest ruleを一意に特定できないと結論づけました。

そのため、ISSUE-000034は**Resolved**ですが、historical M47 Representation Profileは**Not Verified**のままです。

```text
ISSUE resolved
  != historical Profile verified

unrecoverable historical verification
  != failed binding
```

current JCS / raw-bytes Profileへ遡及対応付けしません。新しい一次資料が見つかった場合はISSUE-000034を再開できます。

## 10. versioning

Representation ProfileはSemantic Contractとは独立してversionを持ちます。

representation-only changeがSemantic Contractのmajor version変更を必ず伴うわけではありません。

一方、同じProfile ID / versionでcanonicalization、digest algorithm、input bytes規則を後から別物へ変更してはなりません。

## 11. Evidence boundary

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current `v1alpha1` Profile DefinitionはDesign Evidenceです。fixture / Go probe / runtime verifier / synthetic Payload SourceのPASSは、それぞれscopeを限定したExecutable Evidenceです。

未検証:

- production-grade external payload acquisition
- production object storage / network behavior
- production streaming verification
- historical M47 digest Profile
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

すべてのRFC 8785 vectorを網羅したcertificationも主張しません。

## 12. Decision / planning

- ADR-0008 — Exact Binding verification boundary
- ADR-0009 — Verification Outcome separation
- ADR-0023 — current Representation Profile baseline
- ISSUE-000009 — current/future Profile stabilization（Resolved）
- ISSUE-000034 — historical M47 digest recovery（Resolved; Profile itself remains Not Verified）
- ISSUE-000038 — runtime Verifier Registry（Resolved）
- ISSUE-000040 — Payload Source boundary（Resolved）

## 13. Natural Japanese review

current JCS / raw-bytes Profile Definition、Profile Conformance、Verifier Registry、synthetic Payload Source、historical M47 recovery closure、5段階Evidenceへ戻って全文を再監査しました。その後、Issue closureとhistorical Profile verificationを混同せず、Profileの役割、数値、未検証範囲、規範強度を変えないまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
