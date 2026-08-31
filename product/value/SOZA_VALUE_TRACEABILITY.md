# SOZA Value Traceability

更新日: 2026-08-31  
状態: **Current Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Contract、現在のEvidence状態まで上位から追跡するための索引です。

新しい意味上の正本を作る文書ではありません。

詳細は、それぞれ次を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Evidence受入れ境界: `SOZA_VALUE_ACCEPTANCE.md`
- Requirement: `../../requirements/PRODUCT_REQUIREMENTS.md`
- Acceptance Scenario: `../../requirements/ACCEPTANCE_SCENARIOS.md`
- Architecture: `../../architecture/SOZA_REFERENCE_ARCHITECTURE.md`, `../../architecture/TRACEABILITY.md`
- Contract: `../../contracts/TRACEABILITY.md`および各Contract Definition
- 設計判断: `../../plan/adr/`
- 作業・Evidence状態: `../../plan/issue/`

この追跡表が埋まっていること自体を、Product Valueの達成とはみなしません。

## 2. 追跡の基本形

current baselineでは、概ね次を辿れる状態を目標とします。

```text
Product Value
  → V1〜V8
  → REQ-*
  → SCN-*
  → ADR
  → Architecture concern
  → Contract / Implementation / Fixture
  → Evidence state
```

関係は多対多です。一つのRequirementが複数の価値軸を支えてよく、一つのScenarioが複数Requirementを同時に検証しても構いません。

一対一対応を増やすことや、リンク数を多くすることを品質指標にはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | 主なADR | 主なArchitecture concern | current Contract / executable material |
|---|---|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016 | ADR-0003, 0007, 0008, 0010, 0011, 0019, 0020, 0021 | Decision Memory; Reference / Revision / Exact Binding; Provenance; Persistence; Evidence boundary | Semantic Reference; Decision Memory; Semantic Interchange; historical reconstruction fixtureの一部 |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016 | ADR-0002, 0004, 0010, 0011, 0012, 0016, 0017, 0019 | Inquiry / Epistemics; Decision Memory; Responsibility / Authority; Capability Observation; Cognitive Method | Decision Memory; Capability Observation; Semantic Interchange; Recommendation-only / unresolved Decision / negative fixture |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016 | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0017, 0021 | Semantic Revision; Exact Binding; Decision Memory; Cognitive Method provenance; Persistence | Semantic Reference; Decision Memory; lineage / exact reference invariantの一部 |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014 | ADR-0006, 0012, 0013, 0014, 0019, 0021 | Capability; Provider / Adapter; Federation; Persistence; Execution boundary | Capability Observation; Semantic Interchange; cross-provider / TEI degradation fixtureの一部 |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016 | ADR-0002, 0005, 0006, 0010, 0011, 0019 | Inquiry / Epistemics; Decision unresolved state; Capability Observation; Withheld context | Decision Memory; Capability Observation; Semantic Interchange; Unknown / Conflict / Withheld / partial-knowledge fixture |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | ADR-0005, 0017, 0018, 0020, 0021 | Projection; Profile / Policy; Evidence boundary; human-readable Contract Definition | human-readable Contract Definitionとmachine-readable schemaの二層。Projectionの実利用検証は未完了 |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | ADR-0005, 0019 | Profile / Policy; Projection; context-sensitive Decision requirements | 専用Universal Contractは置かない。current Design baseline中心で、軽量／高影響の実利用検証は未完了 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015 | ADR-0006, 0007, 0012, 0013, 0014, 0017, 0019, 0021 | Provider / Adapter; Cognitive Method Realization; Projection; Persistence; Capability; Federation | Capability Observation / Semantic Interchange等は一部境界を支えるが、実Execution Provider交換のoperational evidenceは未取得 |

この表の「current Contract / executable material」は、その価値軸全体のExecutable AcceptanceがSatisfiedであることを意味しません。現在どこまで機械的検査へ降りているかを示す索引です。

## 4. current Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0017`です。

RequirementとScenarioは別の役割を持ちます。

```text
Requirement != Acceptance Scenario != Test Case
```

Product Value側に第二のScenario体系を作りません。具体的な場面は`SCN-*`を正本とし、この文書ではV1〜V8との関係だけを索引化します。

### V1〜V8とSCNの主な関係

- **V1** — 根拠が割れている判断、判断の見直し、Method Realization交換、Storage交換、責任線、historical reconstruction、Execution Provider交換、残差からの再開
- **V2** — 根拠が割れている判断、異なるCapability Provider、軽量／高影響判断、責任線、Provider未観測、Pattern / Method分離、未解決Decision
- **V3** — 判断の見直し、Method Realization交換、Storage交換、historical reconstruction、Pattern / Method分離、残差からの再開
- **V4** — Provider比較、bounded collaboration、historical Provider state、degraded Provider、Selective Disclosure、Execution Provider交換
- **V5** — Conflictを含む判断、判断見直し、bounded collaboration、Provider未観測、Selective Disclosure、残差からの再開
- **V6** — 軽量／高影響判断、Projection作り直し、簡略UI、Design Evidence claim監査
- **V7** — 軽量／高影響判断、簡略UIとcanonical meaning
- **V8** — Provider比較、Method Realization交換、Projection交換、bounded collaboration、Storage交換、Selective Disclosure、Execution Provider交換、Pattern / Method分離

具体的な期待・失敗例は`requirements/ACCEPTANCE_SCENARIOS.md`を正とします。

## 5. Architectureへの追跡

`architecture/TRACEABILITY.md`では、REQ-0001〜REQ-0022が少なくとも一つのcurrent Architecture concernへ追跡できることを確認しています。

主なArchitecture concernは次のとおりです。

- Durable Semantic Core
- Inquiry / Epistemic State
- Cognitive Method
- Decision Memory
- Capability Understanding / Choice
- Responsibility / Authority boundary
- Semantic Reference / Revision / Exact Binding
- Profile / Policy
- Federation / Selective Disclosure
- Provider / Adapter
- Projection
- Persistence
- Evidence / Assurance boundary

このcoverageはDesign Evidenceです。

```text
Architecture trace exists != implementation is complete
```

Architecture concernをそのままGo package、service、database、processへ一対一対応させません。

## 6. Contractへの追跡

current Contract Design baselineでは、少なくとも次の4 familyが実体化されています。

| Contract | Product Value上の主な役割 |
|---|---|
| `soza.semantic-reference/v1alpha1` | V1 / V3を中心に、logical reference、exact historical binding、revision / lineageの意味を支える |
| `soza.decision-memory/v1alpha1` | V1 / V2 / V3 / V5を中心に、Recommendation / Decision / basis / unresolved / responsibilityの分離を支える |
| `soza.capability-observation/v1alpha1` | V2 / V4 / V5を中心に、Provider-neutral Observation、Unknown / Conflict / Withheld、Provider境界を支える |
| `soza.semantic-interchange/v1alpha1` | V1 / V2 / V4 / V5 / V6 / V8にまたがるportable interchange境界を支える |

Contractが存在すること自体をExecutable Evidenceとはしません。

一方、2026-08-31時点では、これら4 ContractについてJSON Schema、positive / negative / boundary fixture、semantic validator、GitHub Actionsがactual repositoryにあり、**17 fixtureを対象とするfixture-scoped Executable Conformance**が成功しています。

これは重要なExecutable Evidenceですが、対象範囲をContract v1alpha1 fixtureへ限定して読みます。

## 7. 現在のEvidence状態

### 7.1 Design Evidence

current repositoryでは、次のDesign baselineが実体化されています。

- Product Value / Value Model / Value Acceptance
- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017
- ADR-0001〜ADR-0021
- Reference Architecture / Architecture Traceability
- current Contract Definition / Contract Traceability

Product → REQ → ADR → Architecture → Contractの主要な追跡線は、Design levelではかなり具体化しています。

### 7.2 Executable Evidence

actual repositoryでは、少なくとも次があります。

- Planning registry integrity checker
- Requirements / Scenario registry checkerとnegative self-test
- Contract v1alpha1 schema
- Contract positive / negative / boundary fixture
- Contract semantic validator
- Contract conformance GitHub Actions

Requirements registryについては22 Requirement / 17 Scenarioの構造整合をactual checkerで確認しています。

Contractについては17 fixtureのfixture-scoped conformanceをactual GitHub Actionsで確認しています。

ただし、これらは**構造・Contract境界のExecutable Evidence**です。REQ-0001〜REQ-0022すべてのproduction implementationや、V1〜V8全体のExecutable Acceptanceを意味しません。

### 7.3 現在まだ上げないEvidence

次はcurrent baselineから自動的にSatisfiedへ上げません。

- stable Representation Profile
- historical M47 digest mapping
- SOZA全体のruntime implementation coverage
- release artifactに対するValue Acceptance
- production operationに対するOperational Acceptance
- 実利用によるAdoption / Outcome Acceptance

```text
fixture PASS
  != release ready
  != operational success
  != user-value realization
```

## 8. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

Contract / fixtureで一部のexact referenceやhistorical reconstruction境界を検証している。一方、stable Representation Profile、historical M47 digest mapping、長期間の実運用履歴での再構成は未検証である。

### V2 Semantic Separation

Recommendation-only、unresolved Decision、Authority field rejection等のfixtureがある。一方、実際のProvider executionや業務責任線をまたぐ運用検証は未完了である。

### V3 Revision Integrity

lineage / exact referenceの一部invariantを検証している。一方、長期間のsemantic revisionとstorage migrationをまたぐ実運用Evidenceはない。

### V4 Provider Independence

Capability Observationのcross-provider / TEI scenarioをfixtureで検証している。一方、実Provider交換・廃止を伴うoperational evidenceはない。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / partial knowledgeをContract fixtureで扱える。一方、実利用で不確実性を保持したことが誤判断回避へ寄与したOutcome Evidenceはない。

### V6 Human / AI Readability

human-readable Contract Definitionとmachine-readable schemaを分離している。一方、representative Projectionを用いた人間・AI双方の実用上の可読性は未検証である。

### V7 Progressive Explicitness

Design boundaryは存在するが、軽量案件と高影響案件の双方で記録負担と意味保持を比較するoperational / outcome evidenceはない。

### V8 Execution Independence

Provider / Adapter / Persistenceの意味境界はDesignとして定義されている。一方、異なるExecution Provider間で実際に同じDecision semanticsを維持できることは、production相当では未検証である。

## 9. CoverageをKPIにしない

この文書の表は、coverage率や成熟度スコアを計算するためのものではありません。

次のような読み方をしません。

- REQリンクが多いValue Axisほど価値が高い。
- ContractがあるValue Axisほど完成している。
- fixture数が多いほどProduct Valueを満たしている。
- V1〜V8の平均点が高ければ重大な欠損を許容できる。

追跡の目的は、**価値の欠落、未検証箇所、過大な達成主張を見つけやすくすること**です。

## 10. Product Value変更時の使い方

Product Value、Value Model、Value Acceptanceを変更する場合は、この文書から影響するREQ / SCN / ADR / Architecture / Contractを抽出して再監査します。

ただし、Traceabilityの都合だけで上位価値を書き換えません。

下位文書がProduct Valueと矛盾する場合は、まず次を確認します。

1. 下位文書が古いのか。
2. Product Valueの仮説に反証が出たのか。
3. Provider固有要件をUniversal要件へ誤昇格させていないか。
4. Design EvidenceとOperational / Outcome Evidenceを混同していないか。

意味変更が必要な場合はADR-0018の変更規則に従います。

## 11. 関連文書

- `SOZA_PRODUCT_VALUE.md`
- `SOZA_VALUE_MODEL.md`
- `SOZA_VALUE_ACCEPTANCE.md`
- `../vision/SOZA_PRODUCT_VISION.md`
- `../principles/SOZA_PRODUCT_PRINCIPLES.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../architecture/TRACEABILITY.md`
- `../../contracts/TRACEABILITY.md`
- `../../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../../plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`
- `../../plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`
- `../../plan/issue/ISSUE-000027-implement-requirements-registry-checker.md`
- `../../plan/issue/ISSUE-000031-implement-contract-schemas-and-conformance.md`

## 12. Natural Japanese review

current Product Value、REQ-0001〜0022、SCN-0001〜0017、ADR、Architecture Traceability、Contract Traceability、actual checker / conformance Evidenceを横断して対応付けた後、Design coverageとExecutable / Release / Operational / Adoption・Outcomeを混同しないよう全体を再構成しました。その後、意味、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
