# Representation Profile Conformance Evidence — 2026-08-31

状態: **Fixture-scoped Executable Evidence — PASS**  
対象branch: `develop/v0.1.0`

## 1. Scope

本書は、ADR-0023でAcceptedしたcurrent Representation Profileについて、actual repository上で再現したfixture-scoped Executable Evidenceを記録します。

対象:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

このEvidenceはproduction verifier registry integration、Release、Operational、Adoption / Outcomeを意味しません。

## 2. Profile Definitions

```text
contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md
contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md
```

Semantic Contract、Representation Profile、verifier implementationは別のauthorityです。

## 3. Fixtures / tools

```text
fixtures/representation-profiles/jcs-v1alpha1.json
fixtures/representation-profiles/raw-bytes-v1alpha1.json
fixtures/representation-profiles/verification-outcomes-v1alpha1.json
tools/check_representation_profiles.py
tools/jcs_probe.go
.github/workflows/representation-profile-conformance.yml
```

## 4. GitHub Actions

### Initial conformance run

- Run ID: `33347799863`
- Head SHA: `535635df4d58923dddeb956bf06ff72c6da53826`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

### README追随後の再実行

- Run ID: `33347825731`
- Head SHA: `3318fc3e23232b46b972091c5a7e1fc740a8f917`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

### Verification Outcome追加後の再実行

- Run ID: `33347989530`
- Head SHA: `30678df18f3382407d3e0562f6ba358afb3120b3`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

`verified / failed / not_verified`の三状態fixtureを追加した後も、Profile DefinitionとGo probeの両jobがgreenであることを確認しています。

## 5. Static / raw-bytes / outcome fixture result

Python 3.12 actual Action output:

```text
representation profile fixture check: PASS
(JCS verified vectors=4, raw vectors=2, outcome vectors=3)
```

このcheckerは次を検査します。

- Profile IDとDefinitionの対応
- 固定canonical bytesとSHA-256
- NFC / NFDを勝手にnormalizeしないこと
- unsafe integer negative fixture
- raw bytes SHA-256
- known Profile + digest一致 → `verified`
- known Profile + digest mismatch → `failed`
- unknown Profile → `not_verified`

```text
not_verified != failed
```

## 6. Commit-pinned Go JCS probe

Go Actionsは`go1.23.12`で実行しました。

workflowでは次のcommitを明示しています。

```text
github.com/gowebpki/jcs@1a4242a66e1a8e03d7458324d0bc95c327527cbb
```

Go module resolver上では次へ解決されました。

```text
github.com/gowebpki/jcs v1.0.1
```

Profile Definitionの正本はこのmodule versionではなくRFC 8785とSOZA Profile Definitionです。dependency revisionはprobeの再現性のために固定しています。

## 7. JCS result

actual Action output:

```text
PASS JCS-001-key-order-whitespace:
  sha256:cc31fc728ab32ccfd6543dd8cce686b9633b3c47fbec82c88a466688f3a8cb81

PASS JCS-002-rfc-representative-sample:
  sha256:2d5e01a318d0f0879ab568c4be289c8b1f64ef8921a53c6277d5e069978baacb

PASS JCS-003-duplicate-key:
  JCS rejected representation (Duplicate key: a)

PASS JCS-004-unsafe-large-integer:
  rejected before JCS
  (unsafe integer outside IEEE-754 safe range: 9007199254740993)

PASS JCS-005-unicode-nfc:
  sha256:86028b41ba792eaf82aa26a45b218f6734f7f1096a86f1746c8296e088a0ccb4

PASS JCS-006-unicode-nfd:
  sha256:1fc0bd7cc93fca8092a2041d7d01842876422aa7e2838acf42c14578e9f2be05

JCS probe PASS: verified=4 negative=2
```

NFC / NFDは異なるdigestとなり、Unicode normalizationを暗黙実行していません。

## 8. Raw-bytes result

代表fixture:

```text
RAW-001-utf8-text
sha256:0215ad0b9b94223776bccbb76ef08a80ca09b4b078861dc12ea461687b8fdc06

RAW-002-binary-prefix
sha256:be45cb2605bf36bebde684841a28f0fd43c69850a3dce5fedba69928ee3a8991
```

base64 fixtureをdecodeしたbytesへ直接SHA-256を適用し、固定digestと一致することをactual Actionで確認しています。

## 9. Verification Outcome result

三状態を次のfixtureで直接確認しています。

```text
OUTCOME-001-known-profile-match       → verified
OUTCOME-002-known-profile-mismatch    → failed
OUTCOME-003-unknown-profile           → not_verified
```

unknown Profileをdigest mismatchとして扱わず、verification capability不足として`not_verified`へ残します。

## 10. Verified boundaries

今回のEvidenceが直接確認した範囲:

- property order / insignificant whitespaceによらずJCS canonical resultが一致する。
- RFC representative primitive / number serializationを再現できる。
- duplicate propertyを受理しない。
- `9007199254740993`を暗黙にbinary64へ丸めず、JCS前のSOZA境界で拒否できる。
- Unicode NFC / NFDを勝手にnormalizeしない。
- raw bytes ProfileでbytesそのもののSHA-256を再現できる。
- `verified / failed / not_verified`をProfile availabilityとdigest結果に応じて区別できる。
- Go JCS implementationはcommit固定で交換可能なprobeとして利用できる。

## 11. currentで未検証の事項

本Evidenceから次を主張しません。

- historical M47 digestのRepresentation Profile特定 — ISSUE-000034
- production runtimeへのverifier registry統合
- network / object storageからのlarge binary streaming運用
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence
- すべてのRFC 8785 test vectorを網羅した完全なcertification

current first semantic runtimeはExact Binding metadata / Profile identityを扱いますが、このProfile verifierのproduction統合を証明するものではありません。

## 12. Evidenceの読み方

```text
Profile Definition exists
  != fixture / probe PASS
  != production verification path established
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

historical candidateのPASSをcurrent Profile Evidenceへ継承していません。current Evidenceはactual repositoryで取り直したものです。

## 13. Natural Japanese review

GitHub Actionsの実ログ、Profile Definition、fixture、ADR-0023、first semantic runtime、ISSUE-000034を相互照合し、どの結果が直接確認され、どこから先が未検証かを再整理しました。run ID、digest、outcome分類、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
