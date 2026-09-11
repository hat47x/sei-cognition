# ADR-0023: current Exact BindingのRepresentation Profile基線を定める

Status: **Accepted**  
Related Issues: **ISSUE-000009, ISSUE-000034**  
Updated: 2026-08-31

## Context

ADR-0008では、Exact Bindingの検証可能性と、canonicalization / digest algorithm等のRepresentation mechanicsを分離した。

```text
Exact Binding semantic obligation
  != Representation Profile mechanics
```

ADR-0009では、bindingそのものとVerification Outcomeも分離した。

```text
verified
failed
not_verified
```

historical candidateではSOZA独自canonical JSON + SHA-256をpressure testへ用いたが、current baselineでは、外部標準に基づくJSON Profileとraw bytes Profileを明示的に分ける。

一方、historical M47ではcontent digestを用いていたことは確認できるものの、そのdigestをどのbytes / canonicalization / hash規則から生成したかは一次source未回収のため確認できていない。

historical mappingの不明点によってcurrent / future bindingのProfile利用まで停止しないよう、両者を分離して扱う。

## Decision

### 1. current JSON Representation ProfileはRFC 8785 JCS + SHA-256を基線とする

current JSON Exact Bindingの第一Profileを次とする。

```text
sei.jcs+sha256/v1alpha1
```

Profile Definition:

```text
contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md
```

canonicalizationの規範的な外部仕様はRFC 8785とする。

SOZA独自canonical JSON algorithmをstable authorityにはしない。

### 2. non-JSON / raw content向けProfileを別に持つ

明示されたbytesそのものをExact Binding対象にするProfileとして、次を置く。

```text
sei.raw-bytes+sha256/v1alpha1
```

Profile Definition:

```text
contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md
```

このProfileではcanonicalizationを行わず、対象bytesへ直接SHA-256を適用する。

```text
raw bytes identity != semantic JSON identity
```

JCS Profileとraw-bytes Profileを、一つの曖昧な「SHA-256 binding」へ統合しない。

### 3. SHA-256はUniversal CoreではなくProfile versionが所有する

current v1alpha1 ProfileではSHA-256を用いるが、SOZA Coreの唯一のhash algorithmとして固定しない。

将来別algorithmが必要になった場合は、新しいRepresentation Profileまたは新versionとして扱う。

### 4. 高精度semantic valueをJCS JSON numberへ暗黙丸めしない

RFC 8785 / I-JSONはJSON numberの相互運用でIEEE 754 binary64を前提とする。

SOZAでは、binary64で安全に保持できないsemantic valueを、値を失うJSON numberへ暗黙変換してからdigestしない。

最低限、safe integer範囲を越える整数はcurrent JCS verifier境界で拒否する。

```text
9007199254740993
  != silently canonicalized as
9007199254740992
```

より高精度な整数・decimal等が必要な場合は、型付き文字列等のlossless representationへ明示的に投影する。

Profile verifierだけでApplication固有のprecision requirementを推測しない。

### 5. Unicode normalizationをJCS Profile内では行わない

RFC 8785に従い、NFC / NFD等のUnicode normalizationをProfile内部で行わない。

見た目や言語上の意味が近いことを理由にbytesを自動同一化しない。

normalizationが必要なdomainでは、JCSの前段にある明示されたsemantic / representation変換として扱う。

### 6. verifier implementationはProfile authorityではない

current Go probeでは`github.com/gowebpki/jcs`を用いる。

ただし、次を区別する。

```text
RFC 8785 + SOZA Profile Definition
  = Profile authority

Go library
  = replaceable verifier implementation
```

actual CIではcommit SHA `1a4242a66e1a8e03d7458324d0bc95c327527cbb`へ固定し、Go module resolver上では`github.com/gowebpki/jcs v1.0.1`へ解決された。

依存libraryを将来差し替えても、同じProfile ID / versionを名乗る限りcanonical resultとdigest contractを変えてはならない。

### 7. SOZA自身のfixtureをProfile conformance境界として保持する

外部libraryのtestだけに依存せず、SOZA repositoryに次を保持する。

```text
fixtures/representation-profiles/jcs-v1alpha1.json
fixtures/representation-profiles/raw-bytes-v1alpha1.json
fixtures/representation-profiles/verification-outcomes-v1alpha1.json
```

current fixtureは少なくとも次を検査する。

- property order / whitespace差
- RFC representative number / string sample
- duplicate key rejection
- unsafe large integer rejection
- NFC / NFD non-normalization
- raw UTF-8 bytes
- raw binary bytes
- `verified / failed / not_verified`の分離

### 8. historical M47 digest mappingをcurrent Profile acceptance条件から分離する

historical M47で使われたdigest規則が不明であっても、current / future Profileのverificationを停止しない。

historical mappingはISSUE-000034で独立して扱う。

規則を確認できないhistorical bindingを、JCSへ推測で対応付けない。

ADR-0009に従い、Profile / payload / verifier等が不足して再検証できない場合は`not_verified`を許す。

```text
historical digest exists
  != historical Profile known
```

### 9. Profile conformance PASSをRuntime / Release / Operational Evidenceへ昇格しない

actual GitHub ActionsでProfile Definition / fixture / Go probeがPASSしても、確認できるのはfixture-scoped Executable Evidenceまでとする。

```text
Profile fixture PASS
  != Production Runtime integration
  != Release readiness
  != Operational interoperability
```

## Alternatives considered

### A. SOZA独自canonical JSONをstable化する

不採用。

historical pressure testとしては有用だが、JSON canonicalizationという一般問題をSOZA独自標準として長期保守する必要性が弱い。

### B. raw JSON bytesだけをSHA-256する

JSON semantic interchangeの既定Profileとしては不採用。

whitespaceやproperty orderだけでdigestが変化し、portable semantic interchangeに不向きである。

raw bytesを固定したい用途には別Profileとして採用する。

### C. historical M47 digest規則が回収できるまで全ProfileをBlockedにする

不採用。

`not_verified`と`failed`を分離したADR-0009により、historical mapping不能とcurrent Profileの検証可能性は独立して扱える。

### D. Go libraryのAPIをProfile仕様にする

不採用。

library更新・置換がsemantic interoperabilityへ影響するため、RFC / Profile Definitionをauthorityとし、libraryは交換可能な実装として扱う。

## Consequences

### Positive

- SOZA独自canonicalizationをstable authorityとして抱えずに済む。
- JSONとraw binaryのExact Binding対象を明確に分けられる。
- high-precision valueの暗黙損失をProfile境界で防ぎやすい。
- verifier libraryを交換可能に保てる。
- historical M47の未回収がcurrent Profile利用を停止しない。
- `not_verified != failed`を実運用へつなげやすい。

### Costs

- JCS / I-JSONのnumber制約を理解し、semantic precisionを別途設計する必要がある。
- Profile fixtureと外部RFCの整合を継続して確認する必要がある。
- JSON fileのraw bytesを固定したい場合とsemantic JSONを固定したい場合でProfileを選ぶ必要がある。
- historical M47 mappingは別途回収作業が必要である。

## Current Evidence

actual GitHub Actions `Representation Profile Conformance`では、Verification Outcome追加後を含め、Profile fixtureとGo JCS probeの双方がsuccessしている。

Go JCS probe:

```text
verified=4
negative=2
```

Python fixture checker:

```text
JCS verified vectors=4
raw vectors=2
outcome vectors=3
```

詳細は次を正本とする。

```text
contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md
```

first semantic runtimeも現在は実体化されているが、current ProfileのProduction-grade Verifier Registryをruntimeへ完全統合したとはまだ主張しない。Runtimeの読込み・検査・再構成Evidenceとは別に扱う。

## Revisit conditions

次の場合に再検討する。

- RFC 8785では扱いにくいportable representationが主要use caseになる。
- CBOR等の別canonical representationが継続的に必要になる。
- SHA-256以外のdigest algorithmを必要とする相互運用要件が生じる。
- binary64を超えるnumeric semanticsをJSON中心で扱う必要が繰り返し現れ、型付き文字列表現だけでは不十分になる。
- current Go verifier candidateに重大な非互換・security・maintenance問題が見つかる。

## Follow-up

- ISSUE-000009 — current Profile stabilization（Resolved）
- ISSUE-000034 — historical M47 digest Profile recovery（Blocked）
- Production-grade Runtime verifier integrationが必要になった場合は、Profile Definitionと既存fixtureを正本とし、Runtime独自のcanonicalization規則を作らずに別Issueで扱う。

## Natural Japanese review

RFC 8785、ADR-0008 / ADR-0009、actual Profile conformance Evidence、first semantic runtime、historical M47の未回収範囲を照合した。その後、Runtime未実体化を前提としたFollow-upを現在状態へ更新し、Profile authority、実装依存、高精度値、Unicode、Evidence強度の境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後に意味監査を実施済みである。
