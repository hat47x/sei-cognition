# SOZA Architecture Traceability

更新日: 2026-08-31  
状態: **Current Design Traceability Baseline**

## 1. 目的

この文書は、Product Value V1〜V8、current Product Requirement、Accepted ADR、`SOZA_REFERENCE_ARCHITECTURE.md`のarchitecture concernがどのようにつながるかを示します。

追跡表は設計理由を見失わないための索引です。Product Value、Requirement、ADR、Architecture本文より強い意味上の正本ではありません。

## 2. Value AxisからArchitectureへの追跡

| Value Axis | 主なREQ | 主なArchitecture concern |
|---|---|---|
| V1 Historical Reconstruction | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | Decision Memory; Reference / Revision / Exact Binding; Provenance; Persistence; Evidence boundary |
| V2 Semantic Separation | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | Inquiry / Epistemics; Decision Memory; Responsibility / Authority; Capability Observation; Cognitive Method |
| V3 Revision Integrity | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | Semantic Revision; Exact Binding; Decision Memory; Cognitive Method provenance; Persistence |
| V4 Provider Independence | REQ-0001, 0007, 0012, 0013, 0021, 0022 | Capability; Provider / Adapter; Federation; Persistence; Execution boundary |
| V5 Uncertainty Preservation | REQ-0002, 0005, 0012, 0014, 0016, 0022 | Inquiry / Epistemics; Decision unresolved state; Capability Observation; Federation / Withheld context |
| V6 Human / AI Readability | REQ-0010, 0011, 0019, 0020 | Projection; Profile / Policy; Evidence boundary; human-readable Contract boundary |
| V7 Progressive Explicitness | REQ-0010 | Profile / Policy; Projection; context-sensitive Decision requirements |
| V8 Execution Independence | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | Provider / Adapter; Cognitive Method Realization; Projection; Persistence; Capability; Federation |

## 3. RequirementからArchitectureへの追跡

| REQ | 主なADR | Architecture concern | Design status |
|---|---|---|---|
| REQ-0001 | ADR-0003, 0007, 0008, 0014 | Durable Core; Reference / Revision; Persistence; Provider boundary | Covered |
| REQ-0002 | ADR-0002, 0010, 0019 | Inquiry / Epistemics; Decision unresolved state; Capability Observation | Covered |
| REQ-0003 | ADR-0007, 0011, 0017 | Provenance; Cognitive Method; Reference | Covered |
| REQ-0004 | ADR-0017 | Cognitive Method; Provider / Realization boundary | Covered |
| REQ-0005 | ADR-0008, 0010, 0011 | Decision Memory; Exact Binding; Semantic Revision | Covered |
| REQ-0006 | ADR-0010, 0014, 0016 | Decision Memory; Responsibility / Authority; Provider crossing | Covered |
| REQ-0007 | ADR-0012, 0013, 0014, 0019, 0024 | Capability; Provider / Adapter | Covered |
| REQ-0008 | ADR-0004, 0010, 0011 | Decision Memory; Responsibility; Provenance | Covered |
| REQ-0009 | ADR-0003, 0008, 0009 | Semantic Revision; Exact Binding; Persistence | Covered |
| REQ-0010 | ADR-0005 | Profile / Policy; Projection; Decision Memory | Covered |
| REQ-0011 | ADR-0007 | Projection; Durable Core; Persistence | Covered — concrete Projection contract deferred |
| REQ-0012 | ADR-0006, 0019 | Federation; Capability Observation; Provider boundary | Covered |
| REQ-0013 | ADR-0004, 0012, 0016 | Responsibility / Authority; Capability / Provider | Covered |
| REQ-0014 | ADR-0010 | Inquiry / Epistemics; Decision Memory | Covered |
| REQ-0015 | ADR-0017 | Cognitive Method; Decision rationale | Covered |
| REQ-0016 | ADR-0002, 0017, 0019, 0024 | Inquiry / Epistemics; Cognitive Method; Adapter interpretation | Covered |
| REQ-0017 | ADR-0004, 0010, 0016 | Responsibility / Authority | Covered |
| REQ-0018 | ADR-0007, 0008, 0009, 0023 | Persistence; Reference / Binding / Revision; Representation Profile boundary | Covered |
| REQ-0019 | ADR-0018, 0020, 0021 | Projection; Contract Definition; traceability | Covered |
| REQ-0020 | ADR-0009, 0018, 0020, 0021 | Evidence / Assurance boundary | Covered |
| REQ-0021 | ADR-0013, 0014, 0017, 0022, 0024 | Provider / Adapter; Method Realization; runtime boundary | Covered |
| REQ-0022 | ADR-0006, 0008, 0012, 0013, 0014, 0019, 0024 | Capability Observation; Provider / Adapter; Exact Binding; Federation | Covered |

## 4. ADRからArchitectureへの追加境界

ADR-0001〜ADR-0021は、current Reference Architectureの基礎となる意味境界と権威関係を形成します。

### ADR-0022 — runtime first slice

最初のruntime sliceをread / validate / reconstructへ限定します。

```text
first runtime slice != workflow / Action execution platform
```

Go package構成をArchitecture concernの恒久identityにはしません。

### ADR-0023 — Representation Profile

Exact BindingのSemantic Contractと、bytes / canonicalization / digestを所有するRepresentation Profileを分離します。

```text
Semantic Contract != Representation Profile != verifier implementation
```

current ProfileとしてJCS+SHA-256とraw-bytes+SHA-256を定義していますが、これらをUniversal Core唯一のrepresentationへ昇格させません。

### ADR-0024 — Provider Adapter observation mapping boundary

Provider Adapterを、Provider固有stateからProvider-neutralなCapability Observationへの観測・解釈境界として扱います。

```text
Provider-owned state
  + observation context
        ↓
Adapter / Mapping
        ↓
Capability Observation
```

Provider-specific input schemaをSOZA Universal ontologyへ統合しません。field mapping、unit conversion、status interpretation等の解釈をmapping provenanceとして追跡可能にし、missing / unknownをnegative factへ変換しない境界を維持します。

AdapterはMatching / Recommendation / Decision / Authority / Executionを所有しません。

## 5. ArchitectureからContract / Profileへの追跡

current Architectureから、独立versioningと相互運用境界が必要な部分を4 Contract familyへ落としています。

| Architecture concern | current Contract |
|---|---|
| Semantic Reference / Revision / Exact Binding | `soza.semantic-reference/v1alpha1` |
| Decision Memory | `soza.decision-memory/v1alpha1` |
| Capability Observation / Provider boundary | `soza.capability-observation/v1alpha1` |
| portable semantic interchange | `soza.semantic-interchange/v1alpha1` |

Exact BindingのrepresentationはContract本体ではなく、次のProfileへ分離しています。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Provider Adapterの出力はcurrent Capability Observation Contractで検証しますが、Provider固有入力自体のUniversal Contractを新設しません。

Projection、Federation、Cognitive Method等についても、current baselineでは必要性のないUniversal Contractを先回りして追加しません。

## 6. runtime / Adapter sliceとの関係

actual repositoryには、Goのsemantic runtimeとProvider Adapter sliceがあります。

```text
runtime/go/
  semanticruntime/
  provideradapter/
```

`semanticruntime`はADR-0022に従い、current Contract fixtureのread / validate / reconstructを担当します。

`provideradapter`はADR-0024に従い、異なるProvider-specific inputからCapability Observationを生成し、既存runtime validationへ接続します。

Provider A / Bのfield setやGo interfaceはcurrent test implementationであり、ArchitectureのUniversal ontologyではありません。

## 7. Evidence状態

current ArchitectureのEvidenceは、次のように分けます。

### Design Evidence

- Product → REQ → ADR → Architecture: **Design trace established**
- Architecture → current four Contract family: **Design trace established**
- Architecture → Representation Profile boundary: **Design trace established**
- Architecture → first runtime slice boundary: **Design trace established**
- Architecture → Provider Adapter observation mapping boundary: **Design trace established**

### Executable Evidence

限定された範囲で次が存在します。

- Contract v1alpha1 17-fixture conformance — Run `33346472419`: **success**
- Representation Profile fixture / Go probe — Run `33347989530`: **success**
- first semantic runtime slice — Run `33348972805`: **success**
- synthetic Provider Adapter slice — Run `33349604842`: **success**
- Provider-specific field非漏洩の追加hardening — Run `33349801993`: **success**

```text
fixture-scoped runtime / adapter PASS
  != Architecture implementation complete
  != production Provider integration complete
```

### 未検証

- historical M47 digest mapping: **Not Yet Verified — ISSUE-000034**
- production Provider / TEI integration: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 8. 監査結果

REQ-0001〜REQ-0022について、current Reference Architecture上で少なくとも一つの主要concernへ追跡できることを確認しています。

current Architectureから必要性が収束したContract、Representation Profile、first runtime slice、synthetic Provider Adapter sliceには、限定されたExecutable Evidenceがあります。

この確認は「すべてのRequirementがproduction implementation済み」という意味ではありません。Design coverageとExecutable Evidenceの対象範囲を分けて読みます。

Product Value側の横断索引は`../product/value/SOZA_VALUE_TRACEABILITY.md`を参照してください。

## 9. Natural Japanese review

V1〜V8、REQ-0001〜0022、ADR-0001〜0024、current Contract、Representation Profile、first semantic runtime slice、synthetic Provider Adapter slice、actual CI結果へ戻って追跡を再確認しました。そのうえで、Design coverageと限定されたExecutable Evidenceを混同せず、Release / Operational / Adoption・Outcomeへ過大に昇格させないよう整理しました。最後に、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
