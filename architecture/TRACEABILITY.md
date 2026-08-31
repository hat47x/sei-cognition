# SOZA Architecture Traceability

更新日: 2026-08-31  
状態: **Current Design Traceability Baseline**

## 1. 目的

この文書は、Product Value V1〜V8、current Product Requirement、Accepted ADR、`SOZA_REFERENCE_ARCHITECTURE.md`のArchitecture concernがどのようにつながり、どの境界がcurrent Contractへ落ちているかを示します。

追跡表は設計理由を見失わないための索引です。Product Value、Requirement本文、ADR、Architecture本文、Contract Definitionより強い意味上の正本ではありません。

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
| REQ-0014 未解決残差と再開条件 | ADR-0010 | Inquiry / Epistemics; Decision Memory | Covered — concrete residual representation partially covered by Decision Memory contract |
| REQ-0015 private CoT非依存 | ADR-0017 | Cognitive Method; Decision rationale | Covered |
| REQ-0016 Observation / Interpretation分離 | ADR-0002, 0017, 0019 | Inquiry / Epistemics; Cognitive Method; Adapter interpretation | Covered |
| REQ-0017 contextual Responsibility | ADR-0004, 0010, 0016 | Responsibility / Authority | Covered |
| REQ-0018 Storage independence | ADR-0007, 0008, 0009 | Persistence; Reference / Binding / Revision | Covered |
| REQ-0019 Human / AI Readability | ADR-0018, 0020, 0021 | Projection; Contract Definition; traceability | Covered — concrete Projection representation deferred |
| REQ-0020 Evidence claim integrity | ADR-0009, 0018, 0020, 0021 | Evidence / Assurance boundary | Covered |
| REQ-0021 Replaceable Realization / Execution | ADR-0013, 0014, 0017 | Provider / Adapter; Method Realization; Persistence / Projection | Covered |
| REQ-0022 Provider-neutral Capability Observation | ADR-0006, 0008, 0012, 0013, 0014, 0019 | Capability Observation; Provider / Adapter; Exact Binding; Federation | Covered — current Contract fixture-scoped executable evidenceあり |

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
| ADR-0018 Product Value authority | ArchitectureをProduct Value / Requirements / ADRの下位current viewとして扱い、Evidenceの高さを分離する |
| ADR-0019 Provider-neutral Capability Observation | Provider内部state→Adapter→Capability Observation境界 |
| ADR-0020 Requirements traceability | REQ / SCNからArchitectureへのcurrent追跡を作る |
| ADR-0021 Architecture / Contract authority | Architecture concern != runtime component、Contractとの責務・版管理を分離 |

## 5. Architecture concernとcurrent Contract

| Architecture concern | current Contract | current state |
|---|---|---|
| Decision Memory | `soza.decision-memory/v1alpha1` | Design Contract + fixture-scoped executable conformance |
| Capability Observation | `soza.capability-observation/v1alpha1` | Design Contract + F1〜F7を含むfixture-scoped executable conformance |
| Reference / Exact Binding / Revision | `soza.semantic-reference/v1alpha1` | Design Contract + schema / semantic invariant fixture。stable Representation Profileは未確定 |
| Durable Semantic Core / portable exchange | `soza.semantic-interchange/v1alpha1` | Design Contract + partial-knowledge / cross-record fixture-scoped executable conformance |
| Federation / Selective Disclosure | Capability Observation / Interchangeの一部で境界を支える | 独立Federation Contractはcurrent baselineでは未採用 |
| Persistence | Semantic Reference / Interchangeがportable意味境界を支える | actual storage migration / operational evidenceは未検証 |
| Projection | current独立Contractなし | Architecture concernとして維持。具体的interchange需要から再評価 |
| Cognitive Method | current独立Contractなし | Method-specific interoperability需要が反復した場合に再評価 |

Contractの存在やfixture PASSを、Architecture concern全体のimplementation完了へ拡張しません。

## 6. 未実体化または未安定のDesign / Implementation detail

current Reference ArchitectureとContractで多くの意味境界を説明できますが、次はまだ固定・実証していません。

- production artifact field set全体
- Capability Definitionのcurrent portable schema
- Matchingのfirst-class Artifact shape
- Provider-specific context referenceの最終shape
- Projection interchange representation
- 独立Federation exchange Contract
- stable Representation Profile
- historical M47 digest mapping
- current runtime package / service構成
- production persistence / migration integration
- actual Provider Adapter implementation

これらをArchitectureの穴として機械的に埋めず、Requirement / Scenario / Contract / Implementation上の必要性を確認します。

## 7. Evidence状態

current ArchitectureのEvidenceは、次のように分けて読みます。

- Product → REQ → ADR → Architecture: **Design trace established**
- Architecture → current Contract: **Design trace established for the current four contract families**
- Contract v1alpha1 fixture-scoped conformance: **Executable Evidence exists for the tested boundaries**
- Architecture全体のruntime implementation: **Not Yet Verified**
- Stable Representation Profile: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
Design trace established
  != Architecture implementation complete
  != operational value realized
```

## 8. 監査結果

REQ-0001〜REQ-0022について、current Reference Architecture上で少なくとも一つの主要concernへ追跡できることを確認しています。

さらに、current Architectureから必要性が収束した4 Contract familyはDesign Definitionとfixture-scoped conformanceまで進んでいます。

この確認は「すべてのRequirementがproduction implementation可能と証明された」という意味ではありません。current Design baselineからRequirementが脱落していないことと、限定されたContract境界にExecutable Evidenceがあることを示すものです。

Product Value側の横断索引は`../product/value/SOZA_VALUE_TRACEABILITY.md`、Contract詳細は`../contracts/TRACEABILITY.md`を参照します。

## 9. Natural Japanese review

V1〜V8、REQ-0001〜0022、ADR-0001〜0021、current Contract Definitionとactual conformance Evidenceを再照合しました。そのうえで、Architecture Design coverageとContract fixture-scoped Executable Evidenceを混同せず、Release / Operational / Adoption・Outcomeへ過大に昇格させないよう全体を再構成しました。最後に、追跡の意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
