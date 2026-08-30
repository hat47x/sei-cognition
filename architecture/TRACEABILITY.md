# SOZA Architecture Traceability

更新日: 2026-08-31  
状態: **Current Design Traceability Baseline**

## 1. 目的

この文書は、Product Value V1〜V8、current Product Requirement、Accepted ADR、`SOZA_REFERENCE_ARCHITECTURE.md`のarchitecture concernがどのようにつながっているかを示します。

追跡表は設計理由を見失わないための索引です。本文やADRより強い意味上の正本ではありません。

## 2. Value AxisからArchitectureへの追跡

| Value Axis | 主なREQ | 主なArchitecture concern |
|---|---|---|
| V1 Historical Reconstruction | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | Decision Memory; Reference / Revision / Exact Binding; Provenance; Persistence; Evidence boundary |
| V2 Semantic Separation | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | Inquiry / Epistemics; Decision Memory; Responsibility / Authority; Capability Observation; Cognitive Method |
| V3 Revision Integrity | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | Semantic Revision; Exact Binding; Decision Memory; Cognitive Method provenance; Persistence |
| V4 Provider Independence | REQ-0001, 0007, 0012, 0021, 0022 | Capability; Provider / Adapter; Federation; Persistence; Execution boundary |
| V5 Uncertainty Preservation | REQ-0002, 0005, 0012, 0014, 0016, 0022 | Inquiry / Epistemics; Decision unresolved state; Capability Observation; Federation Withheld Context |
| V6 Human / AI Readability | REQ-0010, 0011, 0019, 0020 | Projection; Profile / Policy; Evidence boundary; human-readable Contract boundary |
| V7 Progressive Explicitness | REQ-0010 | Profile / Policy; Projection; Decision Memory requirements by context |
| V8 Execution Independence | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | Provider / Adapter; Cognitive Method Realization; Projection; Persistence; Capability; Federation |

## 3. RequirementからArchitectureへの追跡

| REQ | 主なADR | Architecture concern | current Design status |
|---|---|---|---|
| REQ-0001 耐久的な意味の連続性 | ADR-0003, 0007, 0008, 0014 | Durable Core; Reference / Revision; Persistence; Provider boundary | Covered |
| REQ-0002 不確実性と認識状態 | ADR-0002, 0010, 0019 | Inquiry / Epistemics; Decision unresolved state; Capability Observation | Covered |
| REQ-0003 出所・発見経路・派生 | ADR-0007, 0011, 0017 | Provenance; Cognitive Method; Reference | Covered |
| REQ-0004 Cognitive Method独立性 | ADR-0017 | Cognitive Method; Provider / Realization boundary | Covered |
| REQ-0005 Decision歴史再構成 | ADR-0008, 0010, 0011 | Decision Memory; Exact Binding; Semantic Revision | Covered |
| REQ-0006 提案・判断・権限・実行分離 | ADR-0010, 0014, 0016 | Decision Memory; Responsibility / Authority; Provider crossing | Covered |
| REQ-0007 Capability / Provider中立性 | ADR-0012, 0013, 0014, 0019 | Capability; Provider / Adapter | Covered |
| REQ-0008 判断経路とResponsibility来歴 | ADR-0004, 0010, 0011 | Decision Memory; Responsibility; Provenance | Covered |
| REQ-0009 Revision / Supersession | ADR-0003, 0008, 0009 | Semantic Revision; Exact Binding; Persistence | Covered |
| REQ-0010 Progressive Explicitness | ADR-0005 | Profile / Policy; Projection; Decision Memory | Covered |
| REQ-0011 Projection非権威 | ADR-0007 | Projection; Durable Core; Persistence | Covered — concrete Projection contract deferred |
| REQ-0012 Bounded Collaboration / Selective Disclosure | ADR-0006, 0019 | Federation; Capability Observation; Provider boundary | Covered |
| REQ-0013 actor kindからAuthorityを推定しない | ADR-0004, 0012, 0016 | Responsibility / Authority; Capability / Provider | Covered |
| REQ-0014 未解決残差と再開条件 | ADR-0010 | Inquiry / Epistemics; Decision Memory | Covered — concrete residual representation deferred |
| REQ-0015 private CoT非依存 | ADR-0017 | Cognitive Method; Decision rationale | Covered |
| REQ-0016 Observation / Interpretation分離 | ADR-0002, 0017, 0019 | Inquiry / Epistemics; Cognitive Method; Adapter interpretation | Covered |
| REQ-0017 contextual Responsibility | ADR-0004, 0010, 0016 | Responsibility / Authority | Covered |
| REQ-0018 Storage independence | ADR-0007, 0008, 0009 | Persistence; Reference / Binding / Revision | Covered |
| REQ-0019 Human / AI Readability | ADR-0018, 0020, 0021 | Projection; Contract Definition; traceability | Covered — concrete projection representation deferred |
| REQ-0020 Evidence claim integrity | ADR-0009, 0018, 0020, 0021 | Evidence / Assurance boundary | Covered |
| REQ-0021 Replaceable Realization / Execution | ADR-0013, 0014, 0017 | Provider / Adapter; Method Realization; Persistence / Projection | Covered |
| REQ-0022 Provider-neutral Capability Observation | ADR-0006, 0008, 0012, 0013, 0014, 0019 | Capability Observation; Provider / Adapter; Exact Binding; Federation | Covered — executable fixture deferred |

## 4. ADRからArchitectureへの追跡

| ADR | Architectureでの反映 |
|---|---|
| ADR-0001 Moving Future Horizon | Core inclusion gate / future resistance review |
| ADR-0002 Claim / Interpretation boundary | Inquiry / EpistemicsでObservationとInterpretationを分離可能にし、Universal Claimを必須化しない |
| ADR-0003 Revision / Supersession | Semantic Revision / historical preservation |
| ADR-0004 Responsibility without Global Identity | bounded / contextual Responsibility、Global Principal ontologyを要求しない |
| ADR-0005 Progressive Semantic Explicitness | Profile / Policyが必要明示性を決める |
| ADR-0006 Bounded Federation / Selective Disclosure | Federationをoptional Profileとして扱う |
| ADR-0007 Canonical Persistence boundary | Storage-neutral semantic obligations、Projection非権威 |
| ADR-0008 Exact Binding verification | Logical ReferenceとExact Historical Bindingを分離 |
| ADR-0009 Binding Verification Outcome | `not_verified`と`failed`、Evidence claimを分離 |
| ADR-0010 Decision Memory minimal boundary | Recommendation / Decision / basis / unresolved / Responsibility / lineage |
| ADR-0011 Decision reference role separation | basis・参照役割を耐久的に追跡する方向 |
| ADR-0012 Capability Choice semantic boundary | Definition / Observation / Matching / Decision / Authority / Executionを分離 |
| ADR-0013 Capability Realization boundary | Provider-specific realizationをUniversal Coreへ統合しない |
| ADR-0014 SOZA / TEI Product boundary | TEI内部SchemaをProvider外部境界として扱う |
| ADR-0015 Requirement Inquiry / Decision Memory | Requirement inquiryとDecision Memoryの接続 |
| ADR-0016 Authorization Evidence / Provider boundary | AuthorityとResponsibility / Evidence / Providerを分離 |
| ADR-0017 Pattern / Cognitive Method boundary | domain PatternとMethodを分離、Method Application != Assurance |
| ADR-0018 Product Value authority | ArchitectureをProduct Value / Requirements / ADRの下位current viewとして扱う |
| ADR-0019 Provider-neutral Capability Observation | Provider内部state→Adapter→Capability Observation境界 |
| ADR-0020 Requirements traceability | REQ / SCNからArchitectureへのcurrent追跡を作る |
| ADR-0021 Architecture / Contract authority | Architecture concern != runtime component、Contractとの責務・版管理を分離 |

## 5. Architecture concernとContract候補

| Architecture concern | Contractが必要になる理由 | current follow-up |
|---|---|---|
| Inquiry / Epistemics | portable interchangeが必要な場合 | ISSUE-000030で評価 |
| Decision Memory | 異なるimplementation間でDecision / basis / unresolvedを交換する場合 | ISSUE-000030 |
| Capability Observation | Provider adapterをまたいで同じObservation意味を扱う場合 | ISSUE-000024 / 000030 |
| Reference / Exact Binding | historical contentをportableに特定・検証する場合 | ISSUE-000009 / 000030 |
| Semantic Revision | revision / supersession relationをportableに交換する場合 | ISSUE-000030 |
| Federation | bounded subject間の交換Artifactを相互運用する場合 | ISSUE-000030 |
| Persistence | portable export / import契約が必要な場合 | ISSUE-000030 |
| Projection | current baselineではcanonical contractを必須としない | 将来Scenarioから再評価 |

Contract候補が表にあることはContract採用を意味しません。actual interoperability / verification上の必要性をIssue-000030で再評価します。

## 6. 未実体化のDesign detail

current Reference Architectureで意味境界は説明できていますが、次はまだ固定していません。

- production artifact field set
- Decision basis relationのwire shape
- unresolved / reopen conditionのportable representation
- Capability Definitionの最小schema
- Capability Observation property vocabulary
- Matchingのfirst-class Artifact shape
- Provider-specific context reference shape
- Projection interchange representation
- Federation exchange schema
- Contract versionごとのmachine-readable schema
- Representation Profile

これらをArchitectureの不足として無条件に埋めず、ContractまたはImplementationとして必要性を確認します。

## 7. Evidence状態

このTraceabilityはDesign Evidenceです。

- Product → REQ → ADR → Architecture: **Design trace established**
- Architecture → current Contract: **Not Yet Completed**
- Contract → executable conformance: **Not Yet Verified**
- Runtime implementation: **Not Yet Verified**
- Release / Operational: **Not Yet Verified**

## 8. 監査結果

REQ-0001〜REQ-0022について、current Reference Architecture上で少なくとも一つの主要concernへ追跡できることを確認しました。

この確認は「すべてのRequirementがimplementation可能と証明された」という意味ではありません。current Design baseline上で、RequirementがArchitectureから脱落していないことを確認したものです。

## 9. Natural Japanese review

V1〜V8、REQ-0001〜0022、ADR-0001〜0021をcurrent Reference Architectureへ一件ずつ対応付けた後、追跡の意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
