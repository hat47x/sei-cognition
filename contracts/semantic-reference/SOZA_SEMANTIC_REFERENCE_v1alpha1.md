# SOZA Semantic Reference Contract v1alpha1

contract_id: `soza.semantic-reference`  
version: `v1alpha1`  
状態: **Design baseline / pre-stable**  
更新日: 2026-08-31

## 1. 目的

このContractは、SOZAのArtifactをStorageやrepresentationから独立して参照し、必要な場合に**当時の正確な内容**へ結び付け、semantic revisionの来歴を失わず交換するための意味契約を定めます。

主な対象はREQ-0001、REQ-0003、REQ-0005、REQ-0008、REQ-0009、REQ-0018です。

## 2. 基本境界

次を同一視してはなりません。

```text
Logical Reference
  != Exact Artifact Binding
  != Semantic Lineage
  != Storage Revision
  != Representation Revision
```

### 2.1 Logical Reference

Logical Referenceは「どの意味上のArtifactを指すか」を表します。

少なくとも次の性質を持たなければなりません。

- Storage row ID、file path、object key、Git commit等をsemantic identityそのものにしない。
- Storage migration後も同じlogical Artifactを指せる。
- Artifact kindまたは同等の解釈文脈を識別できる。
- scopeが必要なidentityでは、scopeを失わない。

具体的なwire field名は本Contractだけでは固定しません。

### 2.2 Exact Artifact Binding

Exact Artifact Bindingは、logical Artifactのうち**特定時点で参照した内容**を後から検証可能にするためのbindingです。

少なくとも次を関連付けます。

- logical reference
- content digestまたは同等のcontent identity
- そのdigestを再検証するためのRepresentation Contract / Profile identity

Exact Bindingは、mutableなverification stateそのものを保持しません。

```text
Exact Artifact Binding != Verification Outcome
```

### 2.3 Semantic Lineage

Semantic Lineageは、Artifact間の意味上の変更関係を表します。

current baselineでは少なくとも次の意味を区別します。

- `revises`: 意味上の後続・改訂
- `supersedes`: 履歴を残したまま、以後の参照候補として置換
- `withdraws`: 後継を置かず、以後の採用候補から取り下げ

Storage revisionやdigest差だけから、これらを自動生成してはなりません。

## 3. 同一logical identity内のrevision

同じLogical Referenceの旧内容から新内容へSemantic Lineageを張る場合、両端をlogical identityだけで示してはなりません。

旧内容と新内容を区別できるExact Artifact Bindingまたは同等のexact endpointが必要です。

これにより、次のような曖昧な自己参照を避けます。

```text
artifact:A revises artifact:A   # 内容の識別がないため不十分
```

## 4. Representation Contractとの分離

Semantic Reference Contractは、JSON、CBOR、JCS、SHA-256等のcanonicalization / digest方式を固定しません。

```text
Semantic Reference Contract != Representation Profile
```

Exact Bindingが利用するRepresentation Profileは明示的に識別します。

unknownなProfile、失われたverifier、取得不能なpayloadがある場合、検証済みとして扱ってはなりません。

## 5. Verification Outcome

verification outcomeは、少なくとも次を区別できなければなりません。

- `verified`: 指定Profileで再計算し一致を確認した
- `failed`: 指定Profileで再計算し不一致または検証失敗を確認した
- `not_verified`: verifier、payload、Profile等が利用できず、検証自体を完了できない

```text
not_verified != failed
```

過去bindingのverifierが失われたことを、content mismatchへ読み替えてはなりません。

## 6. Semantic changeとrepresentation change

representation-only changeをsemantic revisionへ自動変換してはなりません。

例:

- whitespace変更
- JSON key order変更
- storage format変更
- compression変更
- schema representationの非意味的変更

これらが意味変更を伴うかどうかは、digest差やfile差だけでは判断しません。

## 7. physical deletionとの境界

`withdraws`とphysical delete / retention purgeを同一視してはなりません。

内容を保持できない場合でも、許される範囲で次を区別できることを推奨します。

- logical reference
- 過去binding metadata
- 内容が現在取得不能である事実
- deletion / retention basis
- verification可能性

## 8. 不変条件

実装は少なくとも次を破ってはなりません。

1. Storage identityをsemantic identityへ暗黙昇格しない。
2. Exact Bindingが後から別内容を指すようにmutateしない。
3. `not_verified`を`verified`または`failed`へ黙って変換しない。
4. digest差だけからSemantic Lineageを推定しない。
5. 同一logical identity内のrevisionでexact endpointを失わない。
6. physical deletionとsemantic withdrawalを混同しない。

## 9. interoperability minimum

異なる実装間で本Contractを交換する場合、受信側は少なくとも次を復元できなければなりません。

- logical identity
- exact bindingがあるかどうか
- bindingが利用するRepresentation Profile identity
- semantic lineage relation
- unresolved / unavailableなreferenceが意図的かどうか

受信側がunknown contract versionを理解できない場合、既知versionとして黙って解釈してはなりません。

## 10. Evidence境界

本Contract文書の存在はDesign Evidenceです。

schema、validator、fixture、cross-storage migration、historical binding verificationが成立するまではExecutable Evidenceを主張しません。

ISSUE-000009のstable Representation Profileとhistorical M47 mappingは未完了です。

## 11. 関連

- REQ-0001, REQ-0003, REQ-0005, REQ-0008, REQ-0009, REQ-0018
- ADR-0003, ADR-0007, ADR-0008, ADR-0009, ADR-0021
- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`

## 12. 自然な日本語レビュー

logical identity、exact content、semantic lineage、verification outcomeの境界を確定した後、意味と規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
