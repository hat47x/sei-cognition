# SOZA Contract Traceability

更新日: 2026-08-31  
状態: **Current Contract Design Traceability**

## 1. 目的

この文書は、current ContractがProduct Requirement、ADR、Reference Architectureのどの境界を規範化しているかを示します。

Contractがあること自体をExecutable Evidenceとはみなしません。

## 2. Contract → Requirement / ADR

| Contract | 主なRequirement | 主なADR | Architecture concern |
|---|---|---|---|
| `soza.semantic-reference/v1alpha1` | REQ-0001, 0003, 0005, 0008, 0009, 0018 | ADR-0003, 0007, 0008, 0009, 0021 | Semantic Reference / Revision / Exact Binding, Persistence |
| `soza.decision-memory/v1alpha1` | REQ-0005, 0006, 0008, 0014, 0015, 0017 | ADR-0010, 0011, 0015, 0016, 0021 | Decision Memory, Responsibility / Authority |
| `soza.capability-observation/v1alpha1` | REQ-0002, 0007, 0013, 0021, 0022 | ADR-0012, 0013, 0014, 0019, 0021 | Capability Understanding / Choice, Provider / Adapter |
| `soza.semantic-interchange/v1alpha1` | REQ-0001, 0002, 0003, 0018, 0019, 0020 | ADR-0007, 0008, 0009, 0014, 0021 | Durable Semantic Core, Persistence, Projection boundary |

## 3. Requirement coverage

### Contractが直接規範化するRequirement

- REQ-0001 — Semantic Reference / Interchange
- REQ-0002 — Interchange / Capability Observation
- REQ-0003 — Semantic Reference / Interchange
- REQ-0005 — Semantic Reference / Decision Memory
- REQ-0006 — Decision Memory
- REQ-0007 — Capability Observation
- REQ-0008 — Semantic Reference / Decision Memory
- REQ-0009 — Semantic Reference
- REQ-0013 — Capability Observation
- REQ-0014 — Decision Memory
- REQ-0015 — Decision Memory
- REQ-0017 — Decision Memory
- REQ-0018 — Semantic Reference / Interchange
- REQ-0019 — Interchangeのhuman-readable Contract境界
- REQ-0020 — Contract自体のEvidence階層
- REQ-0021 — Capability ObservationのProvider交換境界
- REQ-0022 — Capability Observation

### Architecture / Profile / Provider側に留めるRequirement

次のRequirementは重要ですが、current baselineで独立Semantic Contractを追加する必要はまだありません。

- REQ-0004 — Cognitive Method: current Method Contractは別Issueで必要性を再評価
- REQ-0010 — Progressive Semantic Explicitness: Profile / Policy concern
- REQ-0011 — Projection非権威: Architecture + Interchange invariant
- REQ-0012 — Bounded Collaboration / Selective Disclosure: optional Federation Profile
- REQ-0016 — Observation / Interpretation: Interchange vocabulary + Epistemic architecture concern

この扱いは「Contract不要が永久に確定した」という意味ではありません。具体的interoperability Scenarioが反復した場合に再評価します。

## 4. Acceptance Scenarioとの主な対応

| Scenario | Contract上の主な検証対象 |
|---|---|
| SCN-0001 根拠が割れている判断 | InterchangeがUnknown / Conflict / provenanceを潰さない |
| SCN-0002 同じ目的、異なるCapability | Capability ObservationをProvider kindで優遇しない |
| SCN-0003 後から判断が覆る | Decision Memory + Semantic Referenceで過去basisを保存する |
| SCN-0006 Projectionを作り直す | InterchangeがProjection stateをsemantic authorityにしない |
| SCN-0008 Storageを交換する | Semantic Reference / InterchangeがStorage identityに依存しない |
| SCN-0009 RecommendationとDecisionが異なる | Decision Memoryが両者を分離する |
| SCN-0010 Decisionをsupersedeする | Semantic Reference Lineageで旧Decisionを削除しない |
| SCN-0011 Capability情報が不足・競合する | Capability ObservationがUnknown / Conflictを保持する |
| SCN-0014 Providerを交換する | Capability / ProviderとSemantic Interchangeを分離する |
| SCN-0016 未解決のまま判断する | Decision作成でUnknown / Conflictを解消しない |

## 5. Executable Evidenceへの未完了線

current Contract Design baselineからExecutable Evidenceへ進むには、少なくとも次が必要です。

1. machine-readable schema
2. cross-contract reference rule
3. positive fixture
4. negative fixture
5. unknown-version fixture
6. partial-knowledge fixture
7. historical reconstruction fixture
8. Capability ObservationのProvider-neutral fixture
9. Representation Profile verifier
10. actual conformance runner

これらはDesign Contract Definitionとは別Issueで追跡します。

## 6. 自然な日本語レビュー

REQ / ADR / Architecture / Scenarioへの対応を確認した後、意味とEvidence状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
