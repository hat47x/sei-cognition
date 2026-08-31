# SOZA Semantic Interchange Contract v1alpha1

contract_id: `soza.semantic-interchange`  
version: `v1alpha1`  
状態: **Design baseline / pre-stable**  
更新日: 2026-08-31

## 1. 目的

このContractは、SOZAの耐久的意味資産を、特定Storage、runtime、UI、Providerへ依存せずに交換するための**薄いportable envelope**を定めます。

このEnvelopeは、すべてのSOZA概念を一つの巨大Schemaへ閉じ込めるためのものではありません。

Semantic Reference、Decision Memory、Capability Observation等の個別Contractを組み合わせ、受信側が「どのContractで何を解釈すべきか」を失わないことを目的とします。

## 2. 基本原則

```text
Semantic Interchange Envelope
  != Canonical Runtime Storage
  != Universal Domain Model
  != Workflow State
  != Projection State
```

export formatをそのまま唯一のruntime storageとして利用することは要求しません。

## 3. Envelopeの最小意味

portable interchangeは、少なくとも次を識別できなければなりません。

- interchange contract identity / version
- 含まれるsemantic recordまたはartifact
- 各recordを解釈するcontract identity / version
- logical reference
- exact bindingが存在する場合のbinding情報
- semantic lineageが存在する場合のrelation
- provenance / derivation等が存在する場合のReference
- extension / profile identityが存在する場合の識別

具体的なJSON field名や配列構造はmachine-readable schema作成時に固定します。

## 4. typed semantic record

Envelope内のrecordは、意味上の種類と解釈Contractを明示できなければなりません。

例:

- Question
- Observation
- Hypothesis
- Unknown
- Conflict
- EvidenceUse
- Assurance
- Decision
- Recommendation
- Responsibility
- Capability Observation
- Semantic Lineage

この例を閉じたUniversal taxonomyにはしません。

Cognitive Method固有Artifact、domain-specific Artifact、optional Profile Artifactを追加できる余地を維持します。

## 5. Unknown contract / extension

受信側が未知のcontract_id、version、extension、profileを理解できない場合、その内容を既知Contractとして黙って解釈してはなりません。

可能な対応は実装やProfileにより異なりますが、少なくとも次を区別できることを推奨します。

- record自体を保持できるが意味検証はできない
- recordを受理できない
- known subsetだけ扱えるが、意味が不完全になる

known subsetだけを処理した結果、元record全体を完全に理解・検証したかのように表示してはなりません。

## 6. Partial Knowledge

Envelope内にUnknown / Conflict / unavailable referenceが存在することだけを理由に、bundle全体をinvalidにしてはなりません。

一方、Contract上必須なidentityやreference integrityが壊れている場合は、単なるUnknownと区別します。

```text
semantic uncertainty != malformed interchange
```

## 7. Reference integrity

recordがlogical referenceを持つ場合、Storage-specific locatorだけをsemantic identityとしてはなりません。

Exact Bindingが存在する場合、そのRepresentation Profile identityを保持します。

参照先が外部sourceやretention policyにより現在取得不能である場合、可能な範囲で「意図的にunavailableである」ことと単なるbroken referenceを区別します。

## 8. Provenance / Derivation

source origin、discovery route、Derivation、Method Application等の来歴を一つのgeneric `source`へ平坦化しません。

recordがこれらを利用する場合、それぞれの意味差を保持できるReferenceまたはtyped relationを利用します。

## 9. Decision Memory

Decision recordを交換する場合、`soza.decision-memory`の意味境界を満たさなければなりません。

EnvelopeはRecommendation、Decision、Authority、Executionを一つのgeneric `action`へ統合しません。

## 10. Capability Observation

Capability Observationを交換する場合、`soza.capability-observation`の意味境界を満たさなければなりません。

Provider internal SchemaをそのままUniversal interchange fieldへ昇格させず、必要なProvider-specific contextはReference / extensionとして扱います。

## 11. Representation Profile

Semantic Interchange Contractは、JSON、CBOR、JCS、SHA-256等をUniversal requirementにしません。

machine-readable representationを作る場合、そのrepresentation自体のProfile identityを明示できます。

同じsemantic interchangeが複数Representation Profileを持つことを妨げません。

## 12. Projection非権威

chat message order、canvas position、tab、viewport、UI selection等を、明示的にsemantic artifact化する別理由がない限りportable semantic authorityとして要求しません。

Projectionを交換・削除しても、耐久的意味資産を失わないことを優先します。

## 13. Security / Privacy

本Contractはcredential、暗号鍵、OAuth token等の交換方式を定めません。

Selective Disclosureが必要な場合、Profile / Provider側で交換範囲を制御できます。

「Envelopeに入れられる」ことと「共有してよい」ことを同一視してはなりません。

## 14. 不変条件

実装は少なくとも次を破ってはなりません。

1. Storage formatをsemantic identityへ昇格しない。
2. unknown contract versionをknownとして処理しない。
3. Unknown / Conflictの存在をmalformed dataと同一視しない。
4. Recommendation / Decision / Authority / Executionをgeneric actionへ平坦化しない。
5. source origin / discovery route / Derivationを一つへ黙って統合しない。
6. Provider-specific SchemaをUniversal interchange meaningへ無条件にコピーしない。
7. Projection stateをcanonical semantic authorityにしない。

## 15. versioning

本Contractのsemantic breaking changeはmajor version境界で扱います。

pre-stable期間は`v1alphaN`を更新できますが、historical exact bindingやDecision basisが特定versionを参照した場合、そのversionを後から識別できるようにします。

representation-only changeをsemantic Contract version changeへ自動変換しません。

## 16. Evidence境界

本Contract DefinitionはDesign Evidenceです。

Executable Acceptanceには少なくとも次が必要です。

- machine-readable schema
- positive fixture
- negative fixture
- unknown-version fixture
- partial-knowledge fixture
- Decision Memory / Capability Observationを含むround-tripまたはequivalent reconstruction test

これらがactual repositoryで再現できるまではExecutable Evidenceを主張しません。

## 17. 関連

- REQ-0001, REQ-0002, REQ-0003, REQ-0018, REQ-0019, REQ-0020
- ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0021
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
- `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
- `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`

## 18. 自然な日本語レビュー

portable interchangeの役割をruntime storageやUniversal Domain Modelから分離し、unknown version、partial knowledge、Reference integrity、Projection非権威の境界を確定した後、意味と規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
