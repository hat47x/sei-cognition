# SOZA Semantic Interchange Contract v1alpha1

contract_id: `soza.semantic-interchange`  
version: `v1alpha1`  
状態: **Design baseline / pre-stable**  
更新日: 2026-08-31

## 1. 目的

このContractは、SOZAのsemantic ArtifactをStorage、implementation、Provider、組織境界をまたいで受け渡すときに、**意味を黙って縮約・再解釈せずに交換するための最小外枠**を定めます。

主な対象はREQ-0001、REQ-0002、REQ-0003、REQ-0018、REQ-0019、REQ-0020です。

このContractは、SOZA全体の巨大なUniversal Message ontologyを定義するものではありません。個々のArtifactの意味は、Architecture、対応するSemantic Contract、Profile等を正とします。

## 2. 基本原則

交換形式が変わっても、少なくとも次を失ってはなりません。

- Artifactのsemantic kindまたは同等の解釈文脈
- logical identity
- exact bindingが存在する場合、そのbinding情報
- contract identity / version
- provenance
- semantic lineage
- Unknown / Conflict / Withheld等、交換対象に含まれる認識状態
- extensionが既知か未知かという区別

```text
Interchange representation != semantic meaning
```

JSON、CBOR、database export、file bundle等の具体形式は本Contractだけでは固定しません。

## 3. Interchange Envelope

一つの交換単位は、概念的に少なくとも次を識別できなければなりません。

- envelope自体が従うContract identity / version
- 含まれるArtifact collection
- Artifactごとのsemantic contract / kindを解釈するための情報
- Artifact間のReference
- unresolved referenceの有無
- extension / profileの利用情報

具体的なwire field名やcollection形式は、本ContractのDesign baselineでは固定しません。

## 4. Contract identity / version

受信側は、交換されたArtifactやEnvelopeがどのContract versionに基づくかを識別できなければなりません。

unknownなContract versionを、近い既知versionとして黙って解釈してはなりません。

受信側が理解できない場合は、少なくとも次を区別できる必要があります。

- contract identityは認識できるがversionを理解できない
- contract identity自体が未知
- Artifact kindは認識できるが一部extensionが未知
- payloadまたはReferenceが欠落している

「理解できない」を「無効」「false」「存在しない」へ自動変換してはなりません。

## 5. Artifact collection

Interchangeは複数Artifactを一つの交換単位へ含めて構いません。

ただし、bundle内に入っているという理由だけでArtifact同士の意味関係を推定してはなりません。

```text
same bundle != semantic relation
```

関係が必要な場合は、Reference、Lineage、basis、Derivation等の明示的な意味から読み取ります。

## 6. Semantic Referenceとの関係

logical reference、exact binding、semantic lineageの意味は`soza.semantic-reference`に従います。

Interchange層はこれらを運搬できますが、別の意味へ再定義しません。

- logical referenceをStorage pathへ置換しない。
- Exact Bindingをmutable latest referenceへ変換しない。
- Representation Profileが未知の場合にbindingを`verified`扱いしない。
- unresolved external referenceを黙って削除しない。

## 7. Provenance

交換時に必要なProvenanceは、少なくとも次の異なる意味を保持できるようにします。

- source origin
- discovery route
- derivation / method application等の派生経路
- adapter / mapping provenance

すべてのArtifactに全種類のProvenanceを必須化するものではありません。

ただし、Provenanceを持つArtifactを交換するときに、単一の`source`文字列へ黙って平坦化して意味差を失ってはなりません。

## 8. Unknown / Conflict / Withheld

認識状態を交換する場合、少なくとも次を同一視してはなりません。

```text
unknown != false
conflict != latest-wins
withheld != unknown
not observed != unavailable
```

受信実装が一部の状態を理解できない場合、その値を便宜上の確定値へ変換するのではなく、未解釈またはunsupportedとして扱える必要があります。

## 9. Extension / Profile

Optional Profileやdomain-specific extensionを交換することを許容します。

ただし、extensionの存在をUniversal Coreの意味へ自動昇格させません。

受信側は、未知のextensionを次のいずれかとして扱える必要があります。

- 保持して再送可能なopaque extension
- 理解不能だが存在は認識できるextension
- そのArtifactの意味を安全に解釈するため必須であるため処理を停止すべきextension

どの扱いが必要かは、extension / Profile側のContractで定めます。

## 10. Selective Disclosure

Interchangeは、すべての内部ArtifactやContextを常に全量交換することを要求しません。

共有できない情報が存在する場合、必要なProfileではWithheld Context等として、その存在や制約を外在化できます。

非開示を、Capability不存在、false、改ざんの証拠等へ自動変換してはなりません。

Federation専用Request / Offer / Commitment / Result wire contractは本Contractでは固定しません。

## 11. Persistenceとの関係

Storage-neutral export / importでは、少なくとも次を維持する必要があります。

- logical identity
- exact binding integrity
- semantic lineage
- provenance
- reference integrity
- contract / representation identity

一方、次のphysical mechanicsは交換意味の正本ではありません。

- DB primary key
- table / collection layout
- file path
- object key
- MVCC version
- event sequence
- Git commit

これらをtransport metadataとして含めることはできますが、semantic identityへ暗黙昇格してはなりません。

## 12. Human / AI Readability

machine-readable representationを持つ場合でも、semantic Contractを理解するために特定実装コードを読むことを前提にしません。

human-readable Contract Definitionとmachine-readable representationが矛盾した場合は、Contract inconsistencyとして修正します。

```text
schema validation success != semantic correctness proof
```

## 13. 不変条件

実装は少なくとも次を破ってはなりません。

1. unknown contract/versionを既知として黙って解釈しない。
2. bundle内共存だけからsemantic relationを推定しない。
3. Unknown / Conflict / Withheldを確定値へ黙って平坦化しない。
4. unresolved referenceを存在しないものとして削除しない。
5. Storage identityをsemantic identityへ昇格しない。
6. extension / ProfileをUniversal Core意味へ自動昇格しない。
7. Representation Profileの違いだけをsemantic changeとみなさない。

## 14. interoperability minimum

異なる実装間で本Contractを交換する場合、受信側は少なくとも次を確認できなければなりません。

- どのContract versionに基づく交換か
- 含まれるArtifactのlogical identity / kind
- Referenceがresolvedかunresolvedか
- exact bindingがあるかどうか
- provenance / lineageが存在するかどうか
- unknown extension / Profileがあるかどうか
- 理解できない意味を黙って既知値へ変換していないこと

## 15. Representation Profileとの分離

本Contractはcanonicalization、digest algorithm、encodingを固定しません。

```text
Semantic Interchange Contract != Representation Profile
```

Representation Profileは別のlogical identity / versionで管理し、ISSUE-000009で安定化します。

## 16. Evidence境界

本Contract文書の存在はDesign Evidenceです。

machine-readable schema、cross-storage round-trip、positive / negative fixture、unknown-version処理、cross-implementation exchangeが再現可能になるまではExecutable Evidenceを主張しません。

## 17. 関連

- REQ-0001, REQ-0002, REQ-0003, REQ-0018, REQ-0019, REQ-0020
- ADR-0006, ADR-0007, ADR-0014, ADR-0021
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`

## 18. 自然な日本語レビュー

portable exchange、Contract version、Reference、Provenance、不確実性、extension、Selective Disclosureの境界を確定した後、意味と規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
