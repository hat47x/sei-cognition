# SOZA Contract Catalog

更新日: 2026-08-31  
状態: **Current Contract Catalog**

## 1. 目的

この文書は、current ArchitectureからContractへ独立させた境界と、Architecture、Profile、Provider、Adapter等に留めている境界を一覧化します。

Contract数を増やすこと自体は目的ではありません。相互運用、historical reconstruction、verificationのために、実装をまたいで意味を固定する必要がある場合だけContract化します。

## 2. current Contract一覧

### `soza.semantic-reference` / `v1alpha1`

対象:

- Logical Reference
- Exact Artifact Binding
- Semantic Lineage
- Representation Profile identity
- Verification Outcomeの意味境界

主なRequirement:

- REQ-0001
- REQ-0003
- REQ-0005
- REQ-0008
- REQ-0009
- REQ-0018

主なADR:

- ADR-0003
- ADR-0007
- ADR-0008
- ADR-0009
- ADR-0021
- ADR-0023

current Executable material:

- JSON Schema
- exact binding / lineage / verification outcome fixture
- semantic validator
- first semantic runtime slice

### `soza.decision-memory` / `v1alpha1`

対象:

- Decisionのhistorical reconstruction
- basis / rationale / unresolved state
- Recommendationとの分離
- contextual Responsibility参照
- Authority / Executionを意味しないこと

主なRequirement:

- REQ-0005
- REQ-0006
- REQ-0008
- REQ-0014
- REQ-0015
- REQ-0017

主なADR:

- ADR-0010
- ADR-0011
- ADR-0015
- ADR-0016
- ADR-0021

current Executable material:

- JSON Schema
- recommendation-only / unresolved Decision / Authority field rejection fixture
- semantic validator
- first semantic runtime slice

### `soza.capability-observation` / `v1alpha1`

対象:

- Capability Definitionへの参照
- Provider-neutralなObservation
- observed condition / time / provenance
- Unknown / Conflict / Withheld
- adapter / mapping provenance
- Provider-specific contextのReference境界

主なRequirement:

- REQ-0002
- REQ-0007
- REQ-0013
- REQ-0016
- REQ-0021
- REQ-0022

主なADR:

- ADR-0012
- ADR-0013
- ADR-0014
- ADR-0019
- ADR-0021
- ADR-0024

current Executable material:

- JSON Schema
- F1〜F7 Capability Observation fixture
- semantic validator / first semantic runtime
- synthetic Provider A / B Adapter slice

### `soza.semantic-interchange` / `v1alpha1`

対象:

- portable semantic envelope
- contract identity / version
- typed artifact collection
- logical / exact referenceの接続
- provenance / extensionの保持
- unknown Contractを黙って既知扱いしないこと
- partial knowledgeとmalformed interchangeの分離

主なRequirement:

- REQ-0001
- REQ-0002
- REQ-0003
- REQ-0018
- REQ-0019
- REQ-0020

主なADR:

- ADR-0007
- ADR-0008
- ADR-0009
- ADR-0014
- ADR-0021

current Executable material:

- JSON Schema
- unknown-version / partial-knowledge / exact-binding mismatch fixture
- semantic validator
- first semantic runtime slice

## 3. current Contractへ独立させない境界

### Inquiry / Epistemics

Question、Observation、Hypothesis、Unknown、Conflict、EvidenceUse、Assurance等はcurrent Semantic Interchangeで扱えるsemantic artifact vocabularyとして残しています。

現時点では、これらだけを別Contract familyへ分ける独立したversioning上の利益が十分でないため、専用Contractを作りません。

### Cognitive Method

Method Definition / Realization / Applicationは重要な意味境界ですが、current baselineではhistorical Method Contractを無検査で復元しません。

独立したMethod interoperabilityが必要になった場合は、REQ-0004、REQ-0015、ADR-0017へ戻ってIssue / ADRから設計します。

### Federation / Selective Disclosure

Federationはoptional Profileです。Request / Offer / Commitment / Result / Withheld Context等の交換に独立した相互運用契約が必要になった時点でProfile Contractを検討します。

### Authority Provider

credential、authorization token、revocation mechanism等はProvider-ownedです。SOZA Contractは必要に応じてAuthority evidenceへのReferenceを保持できますが、認証・認可プロトコルそのものをUniversal Contractとして所有しません。

### Provider-specific Adapter input

Provider Adapterが読む入力schemaはProvider固有です。異なるProvider inputを一つのUniversal Contractへ揃えることを要求しません。

Adapterは必要な意味をCapability Observationへ写像し、その写像のprovenanceを保持します。

## 4. current Representation Profile

Representation ProfileはSemantic Contractと別のversion空間を持ちます。

ADR-0023に基づくcurrent `v1alpha1`基線:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Profile fixture / Go probeはRun `33347989530`でsuccessしています。

```text
Profile conformance PASS
  != historical M47 digest identified
```

historical M47 digest mappingはISSUE-000034で追跡します。

## 5. versioning

Contractにはlogical `contract_id`と明示的`version`を持たせます。

- pre-stable: `v1alpha1`, `v1alpha2`, ...
- stable: `v1`, `v2`, ...

Git commit、file revision、schema revisionをContract versionと同一視しません。

pre-stableでもhistorical Decision等が特定versionへexact-bindした場合、そのversionを後から特定できるようにします。

Representation-only changeをSemantic Contractのversion changeへ自動変換しません。

## 6. current Evidenceの読み方

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

4 Contract familyにはDesign baselineがあり、17 fixture、schema、validator、first runtime、synthetic Adapter等により一部境界のExecutable Evidenceがあります。

Contractやfixtureの数をcoverage KPIにはしません。Release、Operational、Adoption / Outcomeはcurrent baselineでは`Not Yet Verified`です。

## 7. Natural Japanese review

current Product Value、REQ、ADR-0001〜0024、Reference Architecture、4 Contract Definition、2 Representation Profile、17 fixture、first runtime、synthetic Provider Adapterへ戻ってCatalogを再監査しました。historical時点の未確定Profile記述をcurrent Accepted baselineへ改め、Contract化しない境界も現在のAdapter設計まで含めて整理しています。その後、意味、規範強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
