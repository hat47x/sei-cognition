# SOZA Contract Traceability

更新日: 2026-08-31  
状態: **Current Contract Traceability Baseline**

## 1. 目的

この文書は、current ContractがProduct Requirement、Acceptance Scenario、ADR、Reference Architectureのどの境界を規範化し、現在どこまでExecutable Evidenceへ降りているかを示します。

Contract Definition、schema、fixture、conformance resultは異なる役割を持ちます。

```text
Contract Definition exists
  != Schema exists
  != Fixture-scoped conformance passes
  != Runtime implementation conforms
  != Operational interoperability
```

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

- REQ-0004 — Cognitive Method: current Method Contractは具体的なinteroperability需要が生じた場合に再評価
- REQ-0010 — Progressive Semantic Explicitness: Profile / Policy concern
- REQ-0011 — Projection非権威: Architecture + Interchange invariant
- REQ-0012 — Bounded Collaboration / Selective Disclosure: optional Federation Profile
- REQ-0016 — Observation / Interpretation: Interchange vocabulary + Epistemic architecture concern

この扱いは「Contract不要が永久に確定した」という意味ではありません。具体的な相互運用Scenarioが反復した場合に再評価します。

## 4. Acceptance Scenarioとの主な対応

| Scenario | Contract上の主な検証対象 |
|---|---|
| SCN-0001 根拠が割れている判断 | InterchangeがUnknown / Conflict / provenanceを潰さない |
| SCN-0002 同じIntent、異なるCapability Provider | Capability ObservationをProvider kindで優遇しない |
| SCN-0003 新しいEvidenceでDecisionを見直す | Decision Memory + Semantic Referenceで過去basisを保存する |
| SCN-0006 Projectionを作り直す | InterchangeがProjection stateをsemantic authorityにしない |
| SCN-0008 Storageを交換する | Semantic Reference / InterchangeがStorage identityに依存しない |
| SCN-0009 RecommendationからExecutionまでの責任線 | Decision MemoryがRecommendation / Decision / Authorityを混同しない |
| SCN-0010 可変Artifact更新後に過去Decisionを再構成する | Semantic Reference / Lineageで旧basisを現在版へ置換しない |
| SCN-0011 Providerが部分的にdegraded / 未観測である | Capability ObservationがUnknown / Conflict / conditionを保持する |
| SCN-0012 Provider内部をSelective Disclosureする | Capability ObservationがWithheldとUnknownを区別できる |
| SCN-0014 Execution Providerを交換する | Capability / ProviderとSemantic Interchangeを分離する |
| SCN-0016 Decision後も残差を次のInquiryへ渡す | Decision作成でUnknown / Conflictを解消済みにしない |

## 5. current Executable Evidence

2026-08-31時点では、current Contract Design baselineを次へ落としています。

- 4 ContractのJSON Schema
- positive / negative / boundary fixture
- cross-contract / cross-record semantic invariant checker
- unknown-version boundary
- partial-knowledge boundary
- GitHub Actions `Contract Conformance`

actual checkerは17 fixtureを扱い、current baselineに対してsuccessしている。

主なExecutable境界:

- DecisionへAuthorityを直接埋め込む → expected Schema FAIL
- Capability Observationの必須時刻欠落 → expected Schema FAIL
- same-logical-id lineage without exact endpoints → expected Semantic FAIL
- interchange recordとDecision basisのexact binding不一致 → expected Semantic FAIL
- unknown nested Contract version → expected `not_verified`
- `not_verified`と`failed` → 別状態として扱う
- Recommendation without Decision → valid
- Decision with unresolved Unknown / Conflict → valid
- partial-knowledge interchange → valid
- Capability Observation F1〜F7 → current fixtureとして検査可能

詳細な実行Evidenceは`CONFORMANCE_EVIDENCE_2026-08-31.md`とISSUE-000031を参照する。

## 6. Executable Evidenceの境界

現在のExecutable Evidenceは**Contract v1alpha1のfixture-scoped conformance**です。

次を意味しません。

- current runtime全体がContractへ適合済みである。
- stable Representation Profileが確定した。
- historical M47 digest mappingが完了した。
- release Artifactで同じ性質を確認した。
- productionで相互運用した。
- 利用者・組織へのProduct Valueが実証された。

```text
fixture-scoped conformance
  != full implementation conformance
  != release evidence
  != operational evidence
  != adoption / outcome evidence
```

## 7. Contractごとの次の検証点

### Semantic Reference

- stable Representation Profile
- historical M47 digest mapping
- long-lived Artifact / migrationをまたぐ実運用検証

### Decision Memory

- runtime / persistence integration
- Authorization boundaryとのactual crossing
- long-lived Decision revision / reconstruction

### Capability Observation

- actual Provider Adapter integration
- real Provider stateのpartial / withheld / degraded mapping
- Provider交換時のoperational reconstruction

### Semantic Interchange

- actual export / import path
- cross-implementation interchange
- release compatibility
- unknown future versionとの実運用境界

## 8. Product Valueへの戻り方

Contractやschemaの都合からProduct Valueを逆算しません。

Contractで新しいsemantic requirementが必要になった場合は、次の順に戻ります。

```text
Contract observation / failure
  → Architecture concern
  → ADR / Issue
  → REQ / SCN
  → Product Value / V1〜V8
```

実装を守るために上位意味を後付けしないことを原則とします。

Product側の横断索引は`../product/value/SOZA_VALUE_TRACEABILITY.md`を参照します。

## 9. Evidence状態

- Contract Design Baseline: **Satisfied**
- Contract v1alpha1 Fixture-scoped Executable Conformance: **Satisfied**
- Stable Representation Profile: **Not Yet Verified**
- Historical M47 digest mapping: **Not Yet Verified**
- Full runtime conformance: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 10. 自然な日本語レビュー

current Contract Definition、4 Schema、17 fixture、semantic checker、GitHub Actionsの実行結果をREQ / SCN / ADR / Architectureへ戻して照合しました。そのうえで、Contract Designとfixture-scoped Executable Evidenceを分け、Release / Operational / Adoption・Outcomeへ過大に昇格させないよう全体を再構成しました。最後に、意味、条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
