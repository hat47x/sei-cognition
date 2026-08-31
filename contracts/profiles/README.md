# SOZA Representation Profiles

更新日: 2026-08-31  
状態: **Profile boundary defined / stable profile not yet accepted**

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

## 3. current状態

stable ProfileはまだAcceptedしていません。

historical candidateには次がありました。

- custom canonical JSON + SHA-256 `v1alpha1`
- RFC 8785 JCS + SHA-256 candidate
- raw bytes + SHA-256 candidate

custom canonical JSONはcross-language experimentとして価値がありますが、current stable defaultへ自動昇格しません。

JCSはstable JSON候補ですが、高精度semantic valueをbinary64へ暗黙丸めしない境界、Go verifier dependency、RFC test vector、license / maintenanceをactual repositoryで確認する必要があります。

raw bytes profileはnon-JSON / large binary向け候補ですが、semantic representationとの使い分けを明示する必要があります。

これらはISSUE-000009で追跡します。

## 4. historical binding

historical bindingがどのdigest規則で作られたか不明な場合、現在のProfileで推測して再hashしてはなりません。

Profileを特定できない、payloadがない、verifierがない等の場合は`not_verified`として扱える必要があります。

```text
not_verified != failed
```

## 5. versioning

Representation ProfileはSemantic Contractとは独立してversionを持ちます。

representation-only changeがSemantic Contractのmajor version変更を必ず伴うわけではありません。

一方、同じProfile ID / versionで検証規則を後から別物へ変更してはなりません。

## 6. Evidence

Profile Definitionの存在はDesign Evidenceです。

stable acceptanceには、少なくとも独立実装または標準test vectorによる再現可能なExecutable Evidenceが必要です。

## 7. 自然な日本語レビュー

Semantic Contractとの責務境界、stable未確定状態、historical bindingの扱いを確定した後、意味と留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
