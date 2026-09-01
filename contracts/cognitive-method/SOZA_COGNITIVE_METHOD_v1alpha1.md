# SOZA Cognitive Method Contract v1alpha1

contract_id: `soza.cognitive-method`  
version: `v1alpha1`  
状態: **Current pre-stable Design Baseline / Executable Evidence Pending**  
更新日: 2026-09-01

## 1. 目的

このContractは、SOZAで用いるCognitive Methodについて、**方法そのもの、現在の実現方法、特定場面での適用記録を分けたまま交換・再構成するための意味契約**を定めます。

主な対象はREQ-0003、REQ-0004、REQ-0015、REQ-0016、REQ-0021、SCN-0005、SCN-0015です。

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance
```

本ContractはMethodを実行するworkflowやagent runtimeを定義しません。

## 2. record type

v1alpha1では次の3種類だけをportable recordとして定義します。

```text
method_definition
method_realization
method_application
```

一つのdocumentは一つのrecord typeだけを持ちます。

## 3. Method Definition

Method Definitionは、Prompt、model、code、人間手順等の現在の実現方式から独立した、Methodの耐久的な意味を表します。

最低限、次を保持します。

- Method自身のLogical Reference
- 人間がMethodを識別するtitle
- 何のための方法かを外在化したpurpose

必要に応じて次を保持できます。

- context / specification等へのReference
- implementation固有でない補足情報
- extension

固定step machine、特定Prompt文字列、特定model ID、domain-specific PatternをMethod Definitionの必須構造にはしません。

```text
Method identity != Prompt identity != model identity
```

## 4. Method Realization

Method Realizationは、あるMethodを特定時点でどのように実現するかを表す交換可能な実現層です。

最低限、次を保持します。

- Realization自身のLogical Reference
- 対象MethodへのReference
- 実現内容を外在化したdescription

必要に応じてPrompt、code、procedure、tool等のimplementation Artifactを`implementation_refs`で参照できます。

`prompt`、`human`、`model_program`等をUniversalな固定`realization_kind`として必須化しません。実装上必要な分類はExtension、Profile、参照Artifact側で扱えます。

```text
Method Definition != Method Realization
```

Realizationを交換してもMethod Definitionを別Methodへ黙って読み替えてはなりません。

## 5. Method Application

Method Applicationは、特定のInquiry、設計、調査、レビュー等でMethodを適用した事実と、後からその意味を読み直すための外在化された来歴を表します。

最低限、次を保持します。

- Application自身のLogical Reference
- 使用したMethodへのReference

必要に応じて次を保持できます。

- 使用したRealizationへのReference
- context refs
- input refs
- output refs
- residual refs
- provenance refs
- contextual Responsibility refs
- applied_at
- 外在化されたsummary
- extension

### 5.1 Realizationが不明でもApplicationを失わない

Realizationの記録はoptionalです。

```text
realization_ref omitted
  != realization did not exist
  != method not applied
```

古い記録、外部実行、人間手順等でRealizationを正確に特定できない場合、その欠落を否定事実へ変換しません。

### 5.2 input / output / residual

`input_refs`はMethod Applicationが明示的に利用した主要Artifactを指します。

`output_refs`は適用によって外在化された成果物を参照できます。RecommendationやHypothesis等がoutputである場合、それぞれ別のsemantic Artifactとして参照します。

`residual_refs`は、適用後も残ったQuestion、Unknown、Conflict、反例、保留事項等を参照できます。

```text
output reference exists
  != output accepted
  != Decision made
```

## 6. Reference / Exact Binding

Method、Realization、input、output、residual等のReferenceには、current Semantic Reference ContractのLogical Reference / Exact Binding境界を再利用します。

```text
Logical Reference != Exact Historical Binding
```

過去Applicationの再構成に特定版のMethod、Realization、inputが重要な場合、Exact Bindingを利用できます。

すべての低影響ApplicationへExact Bindingを必須化しません。必要な明示性はProfile / Policy側で決めます。

## 7. Pattern / Reference Modelとの境界

PatternやReference ModelはADR-0017どおりdomain-specific Design Knowledgeです。

Method ApplicationがPatternを探索、比較、参照した場合、そのPatternをcontextまたはinputへのReferenceとして保持できます。

```text
Pattern != Cognitive Method
Pattern referenced by Method != Pattern becomes Method
Pattern match != Recommendation != Decision
```

本ContractへPattern固有のUniversal field setやUniversal match scoreを追加しません。

## 8. Recommendation / Decision / Authority / Executionとの境界

Method Applicationは認知手続の来歴であり、後続の判断や実行を意味しません。

```text
Method Application
  != Recommendation
  != Decision
  != Authority
  != Action Intent
  != Execution
  != Assurance
```

Methodを適用しただけで結論を正しいとみなしません。

RecommendationやDecisionが存在する場合は、それぞれのContract / semantic Artifactを別に保持し、必要に応じてReferenceで接続します。

## 9. private chain-of-thought非依存

本ContractはAI内部の非公開推論列、hidden state、token列等の保存・復元を要求しません。

外在化して長期保持するのは、Method identity、主要input / output / residual、provenance、Responsibility、必要なsummary等です。

```text
portable Method Application != private reasoning transcript
```

summaryは人間やAIが後から適用内容を読み直すための外在化された説明であり、private chain-of-thoughtではありません。

## 10. revision / lineage

Method Definition、Realization、Applicationの改訂関係のために専用version graphを新設しません。

Semantic Reference ContractのLogical Reference、Exact Binding、Semantic Lineageを再利用できます。

```text
Contract version
  != Method semantic revision
  != Realization revision
  != Application identity
```

Contractが`v1alpha1`のままでも、Method Definition自体には複数semantic revisionが存在し得ます。

## 11. 不変条件

実装は少なくとも次を破ってはなりません。

1. Method DefinitionとRealizationを同一視しない。
2. RealizationとMethod Applicationを同一視しない。
3. Promptやmodel IDをMethod identityとして必須化しない。
4. Realization未記録をMethod未適用へ変換しない。
5. Method ApplicationをRecommendation、Decision、Authority、Execution、Assuranceへ自動昇格しない。
6. PatternをMethodへ自動昇格しない。
7. private chain-of-thoughtをportable適合条件にしない。
8. Exact Bindingが必要な過去Referenceを現在版へ黙って差し替えない。

## 12. interoperability minimum

異なる実装間でCognitive Method recordを交換する場合、受信側はrecord typeに応じて少なくとも次を復元できなければなりません。

### Method Definition

- Method identity
- title
- purpose

### Method Realization

- Realization identity
- 対象Method Reference
- description

### Method Application

- Application identity
- Method Reference
- Realization Referenceの有無
- input / output / residual Referenceが存在する場合の内容
- provenance / Responsibility Referenceが存在する場合の内容

optional情報が欠けていることを否定事実へ変換してはなりません。

## 13. unknown version

Semantic Interchange内に未知の`soza.cognitive-method` versionが含まれる場合、受信runtimeはcurrent v1alpha1として推測解釈してはなりません。

payloadをopaqueに保持し、意味検証状態を`not_verified`とします。

```text
unknown Method Contract version
  → opaque payload retained
  → not_verified
```

`not_verified`をschema failureやcontent mismatchと同一視しません。

## 14. Evidence境界

本Contract DefinitionはDesign Evidenceです。

schema、fixture、semantic validator、Go runtimeで実際に確認した範囲だけをExecutable Evidenceとします。

未検証のものを含みます。

- Method execution engine
- production Method Provider
- production UI
- Method quality / truth / Assurance
- 人間やAIによる実運用上の有効性
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

```text
Method fixture PASS
  != Method is good
  != conclusion is true
  != Decision is valid
```

## 15. 関連

- REQ-0003, REQ-0004, REQ-0015, REQ-0016, REQ-0021
- SCN-0005, SCN-0015
- ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0022, ADR-0025
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
- `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`

## 16. Natural Japanese review

current Product Value、REQ-0003 / 0004 / 0015 / 0016 / 0021、SCN-0005 / 0015、ADR-0017 / 0025、Reference Architecture、Semantic Reference、Decision Memoryへ戻って意味境界を照合しました。historical M47のfield setを正本化せず、Definition / Realization / Application、Pattern、Decision、Assurance、private chain-of-thought、Exact Bindingの差をcurrent要件から構成しています。その後、意味、規範強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
