# SOZA JCS + SHA-256 Representation Profile v1alpha1

Profile ID: `soza.jcs+sha256/v1alpha1`  
Status: **Current v1alpha1 — Fixture-scoped Executable Conformance PASS**  
Updated: 2026-08-31

## 1. Purpose

このProfileは、JSONで表現されたSOZA Artifactについて、異なる実装・言語・保存方式の間でも同一contentを再検証できるようにするためのRepresentation Profileです。

このProfileはSemantic Contractの意味を定義しません。

```text
Semantic Contract
  != Representation Profile
  != verifier implementation
```

Profileの正本は、本書とRFC 8785です。特定のGo packageやそのAPIは正本ではありません。

## 2. Applicable representation

対象は、RFC 8785が前提とするI-JSON制約を満たすUTF-8 JSON representationです。

少なくとも次を満たす必要があります。

- JSON textとして妥当である。
- object property nameが重複していない。
- `NaN`、`Infinity`等のnon-finite numberを含まない。
- Unicode文字列が妥当であり、lone surrogate等を含まない。
- canonicalization前後で、Applicationが必要とするsemantic precisionを失わないrepresentationである。

## 3. Canonicalization

canonical bytesはRFC 8785 JSON Canonicalization Schemeに従って生成します。

主な性質:

- object propertyを再帰的に規定順序へ並べる。
- array elementの順序は変えない。
- JSON primitiveをRFC 8785が参照するECMAScript互換規則でserializeする。
- 出力はUTF-8 bytesとする。
- insignificant whitespaceを除去する。

SOZA独自のcanonical JSON algorithmを本Profileの正本にはしません。

## 4. Unicode boundary

本ProfileではUnicode normalizationを行いません。

```text
NFC text
  != automatically equal bytes to
NFD text
```

見た目や言語上の意味が近いことだけを理由に、NFC / NFD等を勝手に同一化してはなりません。

ApplicationがUnicode normalizationを必要とする場合は、JCSへ渡す前の明示されたsemantic / representation変換として扱います。

## 5. Numeric precision boundary

RFC 8785 / I-JSONのnumber interoperabilityはIEEE 754 binary64を前提とします。

そのため、SOZAのsemantic valueがbinary64で安全に保持できない場合、JSON numberへ暗黙変換してからdigestを計算してはなりません。

```text
high-precision semantic value
  != silently rounded JSON number
```

少なくとも、絶対値が`2^53 - 1`を超える整数を、精度保証のないJSON numberとして本Profileへ投入しません。

必要な場合は、型付き文字列等、値を失わないrepresentationへ明示的に投影します。

このProfile verifierは、Application固有のdecimal精度要件を推測しません。semantic precision requirementは上位Contract / Policy / Producerが明示する責務です。

## 6. Digest

canonical bytesへSHA-256を適用します。

text representationは次の形式です。

```text
sha256:<64 lowercase hexadecimal characters>
```

例:

```text
sha256:cc31fc728ab32ccfd6543dd8cce686b9633b3c47fbec82c88a466688f3a8cb81
```

SHA-256をSOZA Universal Coreの唯一のhash algorithmとして固定するものではありません。このProfile versionがSHA-256を所有します。

## 7. Verification outcomes

ADR-0009に従い、verification outcomeをbinding本体へ可変状態として埋め込みません。

代表的な分類:

- canonicalizationとdigestが一致した: `verified`
- JSON / Profile制約違反、またはdigest mismatch: `failed`
- Profile implementation、payload、必要なbytes等が利用できない: `not_verified`

```text
not_verified != failed
```

unknown Profile ID / versionを`verified`として扱ってはなりません。

## 8. Verifier implementation boundary

current Go probeでは`github.com/gowebpki/jcs`を使用していますが、Profile identityはこのpackageに依存しません。

current probeはcommit SHA `1a4242a66e1a8e03d7458324d0bc95c327527cbb`へ固定しており、Go module resolver上では`v1.0.1`へ解決されます。

採用条件:

- dependency revisionを明示的に固定する。
- RFC 8785 representative vectorをSOZA側fixtureで検査する。
- duplicate key、numeric boundary、Unicode non-normalization等をSOZA側でも検査する。
- libraryを差し替えてもProfile ID / canonical result / digest contractを変更しない。

Verifier implementationの更新だけを理由に、同じProfile ID / versionの意味を変更してはなりません。

## 9. Evidence fixtures

current fixture:

```text
fixtures/representation-profiles/jcs-v1alpha1.json
fixtures/representation-profiles/verification-outcomes-v1alpha1.json
```

最低限、次を含みます。

- property order / whitespace差
- RFC 8785 representative number / string sample
- duplicate key rejection
- unsafe large integer rejection
- NFC / NFDを勝手に同一化しないこと
- `verified / failed / not_verified`の分離

actual GitHub Actionsのfixture-scoped Executable Evidenceは次に記録します。

```text
contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md
```

このPASSはProduction Runtime integration、Release Evidence、Operational Evidenceを意味しません。

## 10. Explicit non-goals

- historical M47 digestを本Profileへ遡及変換しない。
- JSON以外のbytesをJCSへ押し込まない。
- semantic equalityをcanonical bytes equalityから一般化しない。
- ProfileだけからTruth / Authority / Assuranceを推定しない。
- storage keyやGit object IDをsemantic identityへ昇格しない。

## 11. Versioning

`soza.jcs+sha256/v1alpha1`のcanonicalization、digest algorithm、input制約を互換性なく変更する場合、同じProfile ID / versionを再利用しません。

semantic Contract versionとRepresentation Profile versionは独立です。

## 12. Natural Japanese review

RFC 8785、actual GitHub Actionsのconformance結果、SOZAのExact Binding / Verification Outcome境界を照合し、Profileが所有する規則、上位semantic precision責務、実装差替え境界を確定した。その後、技術条件、Evidence強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
