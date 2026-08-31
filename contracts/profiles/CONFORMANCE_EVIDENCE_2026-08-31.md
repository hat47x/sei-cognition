# Representation Profile Conformance Evidence — 2026-08-31

状態: **Fixture-scoped Executable Evidence — PASS**  
対象branch: `develop/v0.1.0`

## 1. Scope

本書は、current Representation Profile候補について、actual repository上で再現したfixture-scoped Executable Evidenceを記録します。

対象:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

このEvidenceはRuntime integration、Release Evidence、Operational Evidenceを意味しません。

## 2. Profile Definitions

```text
contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md
contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md
```

Semantic ContractとRepresentation Profileは別のauthorityです。

## 3. Fixtures / tools

```text
fixtures/representation-profiles/jcs-v1alpha1.json
fixtures/representation-profiles/raw-bytes-v1alpha1.json
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

Profile Definition説明を更新した後も同じ検査がgreenであることを確認しています。

## 5. Static / raw-bytes fixture result

Python 3.12 actual Action output:

```text
representation profile fixture check: PASS (JCS verified vectors=4, raw vectors=2)
```

このcheckerは、Profile ID、固定canonical digest、NFC/NFD差、unsafe integer negative fixture、raw bytes SHA-256を検査します。

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

## 9. Verified boundaries

今回のEvidenceが直接確認した範囲:

- property order / insignificant whitespaceによらずJCS canonical resultが一致する。
- RFC representative primitive / number serializationを再現できる。
- duplicate propertyを受理しない。
- `9007199254740993`を暗黙にbinary64へ丸めず、JCS前のSOZA境界で拒否できる。
- Unicode NFC / NFDを勝手にnormalizeしない。
- raw bytes ProfileでbytesそのもののSHA-256を再現できる。
- Go JCS implementationはcommit固定で交換可能なprobeとして利用できる。

## 10. Not verified here

本Evidenceから次を主張しません。

- historical M47 digestのRepresentation Profile特定
- current Production Runtimeへのverifier registry統合
- network / object storageからのlarge binary streaming運用
- Release Evidence
- Operational Evidence
- すべてのRFC 8785 test vectorを網羅した完全なcertification

historical M47はISSUE-000032で追跡します。

## 11. Natural Japanese review

GitHub Actionsの実ログ、Profile Definition、fixtureを相互照合し、どの結果が直接確認され、どこから先が未検証かを分離した。その後、Evidence強度と数値を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
