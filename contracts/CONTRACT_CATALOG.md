# SOZA Contract Catalog

更新日: 2026-09-01  
状態: **Current Contract Catalog**

## 1. 目的

この文書は、current Architectureからportable Semantic Contractとして独立させた境界と、Architecture、Profile、Provider、Adapter、domain-specific knowledge等に留める境界を一覧化します。

Contract数を増やすこと自体は目的ではありません。実装やProviderをまたいだ相互運用、historical reconstruction、verificationのために、意味を独立して固定する必要がある場合だけContract化します。

```text
important concept
  != automatically a Universal Contract
```

## 2. current Contract一覧

### `sei.semantic-reference/v1alpha1`

対象:

- Logical Reference
- Exact Artifact Binding
- Semantic Lineage
- Representation Profile identity
- Verification Outcomeの意味境界

主なRequirement:

- REQ-0001, REQ-0003, REQ-0005, REQ-0008, REQ-0009, REQ-0018

主なADR:

- ADR-0003, ADR-0007, ADR-0008, ADR-0009, ADR-0021, ADR-0023

current Executable material:

- JSON Schema
- exact binding / lineage / verification outcome fixture
- semantic validator
- Go semantic runtime
- Representation Verifier Registry

### `sei.decision-memory/v1alpha1`

対象:

- Decisionのhistorical reconstruction
- context / basis / recommendation / unresolved / Responsibilityの参照役割
- rationale
- Recommendationとの分離
- Authority / Executionを意味しないこと

主なRequirement:

- REQ-0005, REQ-0006, REQ-0008, REQ-0014, REQ-0015, REQ-0017

主なADR:

- ADR-0010, ADR-0011, ADR-0015, ADR-0016, ADR-0021

current Executable material:

- JSON Schema
- recommendation-only / unresolved Decision fixture
- Authority field rejection fixture
- Exact Binding mismatch検査
- Go semantic runtime

### `sei.capability-observation/v1alpha1`

対象:

- Capability Definitionへの参照
- Provider-neutralなObservation
- observed condition / time / provenance
- Unknown / Conflict / Withheld
- adapter / mapping provenance
- Provider-specific contextのReference境界

主なRequirement:

- REQ-0002, REQ-0007, REQ-0013, REQ-0016, REQ-0021, REQ-0022

主なADR:

- ADR-0012, ADR-0013, ADR-0014, ADR-0019, ADR-0021, ADR-0024

current Executable material:

- JSON Schema
- F1〜F7 Capability Observation fixture
- semantic validator / Go runtime
- synthetic Provider A / B Adapter slice

### `sei.cognitive-method/v1alpha1`

対象:

- Method Definition
- Method Realization
- Method Application
- Method / Realization / input / output / residual等へのReference
- private chain-of-thoughtに依存しない外在化
- Pattern / Recommendation / Decision / Assuranceへの自動昇格を行わない境界

主なRequirement:

- REQ-0003, REQ-0004, REQ-0015, REQ-0016, REQ-0021

主なScenario:

- SCN-0005
- SCN-0015

主なADR:

- ADR-0017, ADR-0021, ADR-0022, ADR-0025

current Executable material:

- JSON Schema
- C1〜C8 positive fixture
- semantic escalation / required-reference negative fixture
- unknown future Method version fixture
- standalone / Semantic Interchange双方のGo typed runtime

重要な非同値関係:

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance

Pattern != Cognitive Method
```

Realizationが記録されていないMethod Applicationを、Realization不存在やMethod未適用へ読み替えません。

### `sei.semantic-interchange/v1alpha1`

対象:

- portable semantic envelope
- Contract identity / version
- typed Artifact collection
- logical / exact referenceの接続
- provenance / extensionの保持
- unknown Contractを黙って既知扱いしないこと
- partial knowledgeとmalformed interchangeの分離
- known nested Contractのtyped validation

主なRequirement:

- REQ-0001, REQ-0002, REQ-0003, REQ-0018, REQ-0019, REQ-0020

主なADR:

- ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0021

current Executable material:

- JSON Schema
- current Cognitive Methodを含むknown nested Contract validation
- unknown-version / partial-knowledge / exact-binding mismatch fixture
- original bytesのlossless read/export
- Go semantic runtime

ADR-0026では、Decision basis専用だったbundle-local Exact Binding整合検査をknown Contract横断へ一般化する設計をAcceptedしました。実装はISSUE-000049で扱います。

## 3. current Contractへ独立させない境界

### Inquiry / Epistemics

Question、Observation、Hypothesis、Unknown、Conflict、EvidenceUse、Assurance等は重要な意味境界ですが、現時点では専用Contract familyへ分けるversioning上の利益が十分に実証されていません。

必要な意味はReference Architecture、既存ContractのReference、Semantic Interchange等から扱います。

### Pattern / Reference Model

Pattern、Reference Model、典型業務構造等はdomain-specific Design Knowledgeです。

Cognitive Methodがこれらをinput / contextとして参照しても、Patternそのものを`sei.cognitive-method`へ取り込みません。

```text
Pattern reference in Method Application
  != Pattern becomes Cognitive Method
```

### Federation / Selective Disclosure

Federationはoptional Profileです。Request / Offer / Commitment / Result等の交換に独立した相互運用契約が必要になった時点で、現在のbounded collaboration要件へ戻って判断します。

### Authority Provider

credential、authorization token、revocation mechanism等はProvider-ownedです。SOZA Contractは必要に応じてAuthority evidenceへのReferenceを保持できますが、認証・認可protocolそのものをUniversal Contractとして所有しません。

### Provider-specific Adapter input

Provider Adapterが読む入力schemaはProvider固有です。異なるProvider inputを一つのUniversal Contractへ揃えません。

Adapterは必要な意味だけをCapability Observationへ写像し、mapping provenanceを保持します。

### Method executor

`sei.cognitive-method`はMethodのportable meaningを扱いますが、Prompt runner、agent loop、model invocation、人間手順engine等の実行機構をUniversal Contractにしません。

```text
Cognitive Method Contract
  != Method execution runtime
```

## 4. current Representation Profile

Representation ProfileはSemantic Contractと別のversion空間を持ちます。

ADR-0023に基づくcurrent `v1alpha1`基線:

- `sei.jcs+sha256/v1alpha1`
- `sei.raw-bytes+sha256/v1alpha1`

```text
Semantic Contract
  != Representation Profile
  != verifier implementation
```

historical M47 digest規則はcurrent Profileから推定せず、ISSUE-000034のResolved方針どおり`not_verified`を保持します。

## 5. versioning

Contractにはlogical `contract_id`と明示的`version`を持たせます。

- pre-stable: `v1alpha1`, `v1alpha2`, ...
- stable: `v1`, `v2`, ...

Git commit、file revision、schema revisionをContract versionと同一視しません。

pre-stableでもhistorical DecisionやMethod Applicationが特定version / contentへExact Bindingを持つ場合、その当時内容を後から識別できる必要があります。

Representation-only changeをSemantic Contract version changeへ自動変換しません。

unknown future Contract versionは、current runtimeが意味を理解していない以上、opaque payloadとして保持し`not_verified`とします。

## 6. current Executable Evidence

current Contract checkerは5 familyを認識し、31 fixtureを検査します。

- Contract Conformance Run `33467838961`: **success**
- Semantic Runtime Conformance Run `33467838941`: **success**

31 fixtureには、従来のCapability / Decision / Semantic Reference / Interchange boundaryに加え、Cognitive Method C1〜C8、semantic escalation negative case、unknown Cognitive Method versionを含みます。

Go runtimeはcurrent Cognitive Methodをstandalone / nested Interchange双方でtyped loadし、未知versionはopaque + `not_verified`に保ちます。

これはscoped Executable Evidenceです。

```text
31-fixture PASS
  != Contract meaning fully covered
  != Method executor verified
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 7. Evidenceの読み方

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current 5 Contract familyにはDesign baselineがあり、schema、31 fixture、checker、Go runtime、Verifier、synthetic Adapter等により一部境界のExecutable Evidenceがあります。

Contract数、fixture数、CI件数をProduct ValueのKPIにはしません。Release、Operational、Adoption / Outcomeはcurrent `develop/v0.2.0`では`Not Yet Verified`です。

## 8. Natural Japanese review

current Product Value、REQ / SCN、ADR-0001〜0026、Reference Architecture、5 Contract Definition、2 Representation Profile、31 fixture、Go semantic runtime、synthetic Provider Adapter、actual CIへ戻ってCatalogを再監査しました。Cognitive Methodをhistorical Contractの復元ではなくADR-0025から再設計したcurrent familyとして追加し、Pattern、Method executor、Authority Provider等の非Contract境界も整理しています。その後、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
