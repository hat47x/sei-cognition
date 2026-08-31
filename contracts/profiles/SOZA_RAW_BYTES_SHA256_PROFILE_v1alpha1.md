# SOZA Raw Bytes + SHA-256 Representation Profile v1alpha1

Profile ID: `soza.raw-bytes+sha256/v1alpha1`  
Status: **Current v1alpha1 — Fixture-scoped Executable Conformance PASS**  
Updated: 2026-08-31

## 1. Purpose

このProfileは、JSON canonicalizationを必要としないbinary、archive、画像、large object等について、**明示されたbytesそのもの**へExact Bindingを作るためのRepresentation Profileです。

```text
raw bytes identity
  != semantic JSON identity
```

このProfileは、bytesの意味やmedia typeのsemantic interpretationを定義しません。

## 2. Input

入力は有限長のbyte sequenceです。

Verifierは入力bytesへ次のような暗黙変換を行いません。

- 改行変換
- Unicode normalization
- text encoding変換
- archive再圧縮
- image再encode
- metadata除去
- JSON化

同じ意味に見える別fileでも、bytesが異なれば本Profileでは異なるcontentです。

## 3. Digest

入力bytesへそのままSHA-256を適用します。

text representationは次です。

```text
sha256:<64 lowercase hexadecimal characters>
```

canonicalization stepはありません。

## 4. Streaming

large binaryを全件memoryへ保持する必要はありません。

SHA-256はstreamingで計算できるため、Provider / Adapterはchunked read等を使ってよいものとします。ただし、読んだbyte sequenceの順序・内容を変更してはなりません。

## 5. External source boundary

外部Sourceを参照しているだけでbytesを取得できない場合、digestを推測してはなりません。

- bytesを取得でき、digest一致: `verified`
- bytesを取得でき、digest不一致: `failed`
- bytesを取得できない: `not_verified`

URL、object key、file path、ETag等をcontent digestの代わりにしてはなりません。

## 6. Media type

`media_type`等のmetadataを持たせることはできますが、media typeはdigest対象bytesの意味を補助する情報であり、それ自体をcontent identityにはしません。

必要に応じて上位Contract / Policyで、許容media type、content acquisition、retention、maximum size等を制約します。

## 7. Relation to JCS Profile

JSON Artifactについて「semantic JSON representationとして相互運用したい」場合は`soza.jcs+sha256/v1alpha1`を優先候補とします。

一方、「そのJSON fileのraw bytesそのもの」を固定したい場合は本Profileを使えます。

同じpayloadへ両Profileを適用するとdigestが異なることがあります。これは不整合ではなく、**何をExact Bindingの対象にしたかが異なる**ためです。

## 8. Evidence fixtures

current fixture:

```text
fixtures/representation-profiles/raw-bytes-v1alpha1.json
fixtures/representation-profiles/verification-outcomes-v1alpha1.json
```

actual GitHub Actionsで、text bytesとbinary bytesの代表例をSHA-256で再現し、known Profileの一致=`verified`、digest mismatch=`failed`、unknown Profile=`not_verified`の三状態を確認しています。

Evidenceは`contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`に記録します。

## 9. Evidence boundary

本Profile DefinitionはDesign Evidenceであり、Run `33347989530`のfixture成功はscoped Executable Evidenceです。

```text
raw-bytes fixture conformance PASS
  != network / object storage streaming verified
  != production verifier registry integration
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

first semantic runtimeがExact Binding metadataを扱えることと、本Profileによる実payload verificationのproduction統合は分けます。

## 10. Explicit non-goals

- binary formatのsemantic canonicalization
- content-type inference
- decompression後contentとの自動同一視
- historical M47 digest規則の推定
- SHA-256をUniversal Coreの唯一のhashへ固定すること

## 11. Versioning

hash algorithmまたは「どのbytesを対象にするか」の規則を変更する場合、同じProfile ID / versionを再利用しません。

## 12. Natural Japanese review

JCS Profileとの使い分け、bytes取得不能時の`not_verified`、streaming可能性、Storage identityとの分離、actual fixture conformance、first runtimeとの境界を再確認しました。その後、意味、Evidence強度、検証条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
