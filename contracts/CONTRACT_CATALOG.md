# SOZA Contract Catalog

更新日: 2026-08-31  
状態: **Current Contract Design Catalog**

## 1. 目的

この文書は、current ArchitectureからContractへ落とした境界と、まだArchitecture / Profile / Provider側に留めている境界を一覧化します。

Contract数を増やすこと自体は目的ではありません。相互運用・historical reconstruction・verificationのために、実装をまたいで意味を固定する必要がある場合だけContract化します。

## 2. current Contract一覧

### `soza.semantic-reference` / `v1alpha1`

対象:

- Logical Reference
- Exact Artifact Binding
- Semantic Lineage
- Representation Contract参照
- verification outcomeの意味境界

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

### `soza.capability-observation` / `v1alpha1`

対象:

- Capability Definitionへの参照
- Provider-neutralなObservation
- observed condition / time / provenance
- Unknown / Conflict / withheld state
- adapter / mapping provenance

主なRequirement:

- REQ-0002
- REQ-0007
- REQ-0013
- REQ-0021
- REQ-0022

主なADR:

- ADR-0012
- ADR-0013
- ADR-0014
- ADR-0019

### `soza.semantic-interchange` / `v1alpha1`

対象:

- portable semantic envelope
- contract identity / version
- typed artifact collection
- logical / exact referenceの接続
- provenance / extensionの保持
- unknown contractを黙って既知扱いしないこと

主なRequirement:

- REQ-0001
- REQ-0002
- REQ-0003
- REQ-0018
- REQ-0019
- REQ-0020

## 3. current Contractへ独立させない境界

### Inquiry / Epistemics

Question、Observation、Hypothesis、Unknown、Conflict、EvidenceUse、Assurance等はcurrent Semantic Interchangeで交換可能なsemantic artifact vocabularyとして扱います。

現時点では、これらだけを別Contract familyへ分けることで得られる独立したversioning上の利益が十分でないため、独立Contractを作りません。

将来、Inquiry-only interoperabilityが反復する場合は再検討します。

### Cognitive Method

Method Definition / Realization / Applicationは重要な意味境界ですが、current baselineでは既存Method contractの歴史資産を無検査で復元しません。

current Method interchangeを新設する場合は、REQ-0004とADR-0017へ戻り、別Issueで設計します。

### Federation / Selective Disclosure

Federationはoptional Profileです。Request / Offer / Commitment / Result / Withheld Context等の交換が具体的な外部相互運用として必要になった時点でProfile Contractを作ります。

### Authority Provider

credential、authorization token、revocation mechanism等はProvider-ownedです。SOZA Contractは必要に応じて外部Authority evidenceへのReferenceを保持しますが、認証・認可プロトコルそのものを所有しません。

## 4. Representation Profile

Representation ProfileはSemantic Contractと別version空間です。

current stable Profileは未確定です。ISSUE-000009でJCS / raw bytes / historical mappingを扱います。

## 5. versioning

Contractにはlogical `contract_id`と明示的`version`を持たせます。

- pre-stable: `v1alpha1`, `v1alpha2`, ...
- stable: `v1`, `v2`, ...

Git commit、file revision、schema revisionをContract versionと同一視しません。

pre-stableでもhistorical Decision等が特定versionへexact-bindした場合、そのversionを後から特定できるようにします。

## 6. 自然な日本語レビュー

Architecture、REQ、ADRとの対応を確定した後、意味・規範強度・留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
