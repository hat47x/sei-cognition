# SEI Architecture Traceability

更新日: 2026-09-16  
状態: **Current Design / Evidence Traceability Baseline**

## 1. 目的

この文書は、Product Value V1〜V8、current Product Requirement、Accepted ADR、`SEI_REFERENCE_ARCHITECTURE.md`のarchitecture concernがどのようにつながり、どこまでExecutable / Release Evidenceへ到達しているかを示します。

追跡表は設計理由とEvidenceの高さを見失わないための索引です。Product Value、Requirement、ADR、Architecture、Contract、Issue、Evidence本文より強い意味上の正本ではありません。

```text
traceability coverage
  != implementation complete
  != release scope
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 2. Value AxisからArchitectureへの追跡

| Value Axis | 主なREQ | 主なArchitecture concern |
|---|---|---|
| V1 Historical Reconstruction | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022, 0023 | Decision Memory; Reference / Revision / Exact Binding; Provenance; Persistence; Canonical commit integrity; Evidence boundary |
| V2 Semantic Separation | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | Inquiry / Epistemics; Decision Memory; Responsibility / Authority; Capability Observation; Cognitive Method |
| V3 Revision Integrity | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018, 0023 | Semantic Revision; Exact Binding; Decision Memory; Cognitive Method provenance; Persistence; stale-write boundary |
| V4 Provider Independence | REQ-0001, 0007, 0012, 0013, 0021, 0022 | Capability; Provider / Adapter; Federation; Persistence; Execution boundary |
| V5 Uncertainty Preservation | REQ-0002, 0005, 0012, 0014, 0016, 0022 | Inquiry / Epistemics; Decision unresolved state; Capability Observation; Federation / Withheld context |
| V6 Human / AI Readability | REQ-0010, 0011, 0019, 0020 | Projection; Profile / Policy; Evidence boundary; human-readable Contract boundary |
| V7 Progressive Explicitness | REQ-0010 | Profile / Policy; Projection; context-sensitive Decision requirements |
| V8 Execution Independence | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022, 0023 | Provider / Adapter; Cognitive Method Realization; Projection; Persistence; Capability; Federation; Product-local commit coordination |

## 3. RequirementからArchitectureへの追跡

| REQ | 主なADR | Architecture concern | Design status |
|---|---|---|---|
| REQ-0001 | ADR-0003, 0007, 0008, 0014 | Durable Core; Reference / Revision; Persistence; Provider boundary | Covered |
| REQ-0002 | ADR-0002, 0010, 0019 | Inquiry / Epistemics; Decision unresolved state; Capability Observation | Covered |
| REQ-0003 | ADR-0007, 0011, 0017 | Provenance; Cognitive Method; Reference | Covered |
| REQ-0004 | ADR-0017, 0025 | Cognitive Method; Provider / Realization boundary | Covered |
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
| REQ-0015 | ADR-0017, 0025 | Cognitive Method; Decision rationale | Covered |
| REQ-0016 | ADR-0002, 0017, 0019, 0024 | Inquiry / Epistemics; Cognitive Method; Adapter interpretation | Covered |
| REQ-0017 | ADR-0004, 0010, 0016 | Responsibility / Authority | Covered |
| REQ-0018 | ADR-0007, 0008, 0009, 0023 | Persistence; Reference / Binding / Revision; Representation Profile boundary | Covered |
| REQ-0019 | ADR-0018, 0020, 0021, 0028 | Projection; Contract Definition; Product Interaction; traceability | Covered |
| REQ-0020 | ADR-0009, 0018, 0020, 0021 | Evidence / Assurance boundary | Covered |
| REQ-0021 | ADR-0013, 0014, 0017, 0022, 0024 | Provider / Adapter; Method Realization; runtime boundary | Covered |
| REQ-0022 | ADR-0006, 0008, 0012, 0013, 0014, 0019, 0024 | Capability Observation; Provider / Adapter; Exact Binding; Federation | Covered |
| REQ-0023 | ADR-0028 | Product Interaction commit boundary; Commit Coordinator; Persistence publication boundary; snapshot precondition | Covered — implementation mechanism remains Product / Persistence-local |

## 4. ADRからArchitectureへの追加境界

ADR-0001〜ADR-0021は、current Reference Architectureの基礎となる意味境界と権威関係を形成します。ADR-0022以降では、その意味境界をruntime、Contract、Product Interaction、Packaging、Product Accessへ具体化しています。

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

Provider-specific input schemaをSEI Universal ontologyへ統合しません。field mapping、unit conversion、status interpretation等の解釈をmapping provenanceとして追跡可能にし、missing / unknownをnegative factへ変換しない境界を維持します。

AdapterはMatching / Recommendation / Decision / Authority / Executionを所有しません。

### ADR-0025 / ADR-0026 — Cognitive Methodとcross-contract Exact Binding

Cognitive MethodのDefinition / Realization / Applicationをportable Contractとして分離し、Pattern / Recommendation / Decision / Assuranceへ自動昇格させません。

```text
Method Definition
  != Method Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance
```

known ContractをまたぐExact Referenceについてはbundle-local consistencyを共通に検査します。latest-winsでhistorical revisionを潰しません。

### ADR-0027〜ADR-0030 — production runtime / Product surface

- ADR-0027: SEI自身が所有するproduction runtimeの標準実装言語をGoとする。
- ADR-0028: Product Interactionをcanonical meaning上の操作境界として分離する。
- ADR-0029: Local Single-Node Packageを最初のPackaging / Deployment Profileとする。
- ADR-0030: authentication identity、Product Access、semantic Responsibility / Authorityを分離する。

これらのRealizationをUniversal semanticsへ昇格させません。

REQ-0023はADR-0028で分離したProduct Interaction境界に対し、successful commitとしてcanonicalへ公開するstateの意味整合性を要求します。Commit Coordinator、staging clone、digest / generation等はArchitecture上のrealizationであり、新しいUniversal Transaction / Snapshot Contractを導きません。

## 5. ArchitectureからContract / Profileへの追跡

current Architectureから、独立versioningと相互運用境界が必要な部分を5 Contract familyへ落としています。

| Architecture concern | current Contract |
|---|---|
| Semantic Reference / Revision / Exact Binding | `sei.semantic-reference/v1alpha1` |
| Decision Memory | `sei.decision-memory/v1alpha1` |
| Capability Observation / Provider boundary | `sei.capability-observation/v1alpha1` |
| Cognitive Method Definition / Realization / Application | `sei.cognitive-method/v1alpha1` |
| portable semantic interchange | `sei.semantic-interchange/v1alpha1` |

Exact BindingのrepresentationはContract本体ではなく、次のProfileへ分離しています。

- `sei.jcs+sha256/v1alpha1`
- `sei.raw-bytes+sha256/v1alpha1`

Provider Adapterの出力はcurrent Capability Observation Contractで検証しますが、Provider固有入力自体のUniversal Contractを新設しません。

Projection、Federation、Product Access Policy、Packaging layout等も、独立したportable semantic agreementが必要だと確認される前にUniversal Contractを先回りして追加しません。

REQ-0023 / SCN-0019もcurrent 5 Contract familyを増やしません。commit atomicityやconcurrency preconditionはportable semantic payloadではなく、Product / Persistence境界のcorrectness responsibilityとして保持します。

## 6. runtime / Product sliceとの関係

actual repositoryには、Architectureの複数境界を限定範囲で検査するGo runtime / probe / integration materialがあります。

代表例は次のとおりです。

- semanticruntime — known Contractのread / validate / reconstruct
- provideradapter — Provider-specific inputからCapability Observationへのmapping
- Cognitive Method typed runtime / live method integration
- Product Journey harness
- Product Interaction reference probe
- Product Interaction Commit Coordinator / stale-draft guard probe source
- Packaging / Persistence probe
- Product Access / Collaboration probe
- external artifact / Provider / TEI integration

package名やGo interfaceはcurrent implementationであり、ArchitectureのUniversal ontologyではありません。

`interactionprobe`のcommit / provisional sourceはREQ-0023 / SCN-0019の実装候補を具体化しますが、sourceが存在することだけではExecutable Evidenceを成立させません。

## 7. Evidence状態

current ArchitectureのEvidenceは、次の5段階を分けて読みます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Design Evidence

- Product → REQ → ADR → Architecture: **Design trace established**
- Architecture → current 5 Contract family: **Design trace established**
- Architecture → Representation Profile boundary: **Design trace established**
- Architecture → semantic runtime / Provider Adapter / Cognitive Method boundary: **Design trace established**
- Architecture → Product Interaction / Packaging / Product Access boundary: **Design trace established**
- REQ-0023 / SCN-0019 → Product-local commit / stale-write boundary: **Design trace established**

### Scoped Executable Evidence

限定された範囲で、少なくとも次が存在します。

- Contract / Representation Profile conformance
- first semantic runtime slice
- synthetic Provider Adapter slice
- end-to-end Product Journey
- Product Interaction reference probe
- Packaging / Persistence and Local Reference Package probes
- Product Access / Collaboration probe
- E2 out-of-process reference exchange
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- E3b-P2 revision A fixed-artifact actual TEI CLI execution
- E3b-M1a / M1b live external Cognitive Method execution
- Method Realization historical reconstruction
- actual model artifact exchange後のhistorical Application保持
- fixed-model Ollama `0.32.13` / `0.32.14` runtime version exchange後のhistorical Application保持 — ISSUE-000070 Resolved

REQ-0023 / SCN-0019についてはcommit / stale-draft probeとtest sourceが存在しますが、本baseline更新時点でactual runをcurrent Requirement / Scenario Evidenceとして確認していないため、**Executable EvidenceはNot Yet Verified**です。

```text
scoped Executable Evidence
  != Architecture implementation complete
  != arbitrary Provider / runtime compatibility
  != production operation proven
```

ISSUE-000070で成立したのは固定KJ Atlas source、固定Method input、固定model artifact、同一promptの下でのOllama 2 revision交換です。model出力品質やKJ法としての成果品質は`not_evaluated`のままです。

### Release Evidence

v0.2.0 Local Reference Product Baselineについてactual Release Evidenceが成立しています。

ただしsupported release scopeはE3aまでです。release後に得たE3b-P1 / P2、M1a / M1b、historical reconstruction、model / runtime version exchange Evidenceを、公開済みv0.2.0のsupport範囲へ遡及させません。

REQ-0023 / SCN-0019はv0.2.0 release後のcurrent develop baselineで追加されたため、v0.2.0 Release Evidenceへ遡及的に含めません。

### Historical / unresolved boundary

- historical M47 digest profile: ISSUE-000034はResolved。保持されている直接Evidenceから旧digest規則を権威的に復元できないため、historical実装をcurrent authorityへ自動継承しない。
- TEI revision B executable / Provider Plan / current SEI Adapter compatibility: **Not Yet Verified — ISSUE-000072 Open**
- REQ-0023 / SCN-0019 actual commit fault / stale-write run: **Not Yet Verified — ISSUE-000073 Open**
- arbitrary Provider / model / runtime version portability: **Not Established**

### Operational / Adoption・Outcome

- E4 Operational portability: **Not Established**
- production long-running operation / support matrix: **Not Established**
- actual human outcome review: **Not Completed**
- Adoption / Outcome Evidence: **Not Established**

## 8. 監査結果

REQ-0001〜REQ-0023について、current Reference ArchitectureまたはProduct Interaction Architecture上で少なくとも一つの主要concernへ追跡できることを確認しています。

current Architectureから必要性が収束した5 Contract family、Representation Profile、semantic runtime、Provider Adapter、Cognitive Method、Product Interaction、Packaging / Persistence、Product Accessには、対象を限定したDesign / Executable Evidenceがあります。v0.2.0 Local Reference Product BaselineにはRelease Evidenceもあります。

ISSUE-000073ではCR-73.8 / 73.9を別々のUniversal mechanismへせず、successful canonical commitの整合性というREQ-0023とSCN-0019へ統合しました。Architecture上はCommit Coordinator / snapshot precondition / Persistence publication boundaryへ配置し、新しいContract familyやtransaction ontologyを作っていません。

ISSUE-000070のactual runtime version exchangeから新しいStable Requirement / Acceptance Scenario / Universal Contract fieldは必要と判断されませんでした。ISSUE-000072のactual revision B結果も、既存REQ / SCNで表現できない独立Product failureが確認されるまではUniversal semanticsへ先取りしません。

この確認は「すべてのRequirementがproduction implementation済み」「任意のProvider / Realization / versionを交換できる」「Operational / Outcomeが成立した」という意味ではありません。

Product Value側の横断索引は`../product/value/SEI_VALUE_TRACEABILITY.md`、PMS-06のcurrent version-exchange位置は`../product/roadmap/PMS06_CURRENT_STATE_2026-09-05.md`を参照してください。

## 9. Natural Japanese review

V1〜V8、REQ-0001〜0023、SCN-0019を含むcurrent Acceptance baseline、ADR-0001〜0030、current 5 Contract family、2 Representation Profile、semantic runtime、Provider Adapter、Cognitive Method、Product Journey、Product Interaction、Packaging / Persistence、Product Access、ISSUE-000073 Candidate Requirement監査、v0.2.0 Release Evidence、PMS-06のE3b / historical reconstruction / model・runtime version exchangeへ戻って追跡を再確認した。

REQ-0023はtransaction / snapshot方式そのものではなく、Product Interactionがsuccessful commitとして公開するcanonical meaningの整合性を規範化した。SCN-0019のpartial / stale failureはCommit Coordinator、Persistence publication boundary、snapshot preconditionへ追跡し、concurrency tokenとSemantic Revisionの意味差を維持している。probe / test sourceの存在はactual Executable Evidenceへ昇格させていない。

そのうえで、ISSUE-000070のfixed-scope Scoped Executable Evidenceをarbitrary portabilityや成果品質へ拡張せず、ISSUE-000072 revision B、ISSUE-000073 H1 / H2とSCN-0019 actual run、E4、Operational / Adoption・Outcomeを未検証として残した。意味、権威関係、Evidence強度を変えず、自然な日本語となることを最重要視して最終意味監査を行った。
