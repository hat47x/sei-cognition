# SOZA Value Traceability

更新日: 2026-09-01  
状態: **Current Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Contract、Representation Profile、runtime、Provider Adapter、現在のEvidence状態まで上位から追跡するための索引です。

新しい意味上の正本を作る文書ではありません。詳細は、それぞれ次を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Evidence受入れ境界: `SOZA_VALUE_ACCEPTANCE.md`
- Requirement: `../../requirements/PRODUCT_REQUIREMENTS.md`
- Acceptance Scenario: `../../requirements/ACCEPTANCE_SCENARIOS.md`
- Architecture: `../../architecture/SOZA_REFERENCE_ARCHITECTURE.md`, `../../architecture/TRACEABILITY.md`
- Contract: `../../contracts/TRACEABILITY.md`および各Contract Definition
- Representation Profile: `../../contracts/profiles/`
- runtime: `../../runtime/go/`
- V6 / V7 evaluation: `../../evaluation/v6-v7/`
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
  → Contract / Representation Profile / Runtime / Provider Adapter
  → Projection Evaluation / Fixture / Test / CI
  → Evidence state
```

関係は多対多です。一つのRequirementが複数の価値軸を支えてよく、一つのScenarioが複数Requirementを同時に検証しても構いません。

リンク数やcoverage率をProduct ValueのKPIにはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | 主なADR | current executable material |
|---|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016 | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0019, 0021, 0022, 0023, 0024 | Semantic Reference / Decision Memory / Interchange fixture、F6 historical reconstruction、Go runtime slice、Adapter mapping provenance / source state保持 |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016 | ADR-0002, 0004, 0010, 0011, 0012, 0016, 0017, 0019, 0022, 0024 | Recommendation-only、Decision with unresolved、Authority field rejection、Adapter outputのsemantic escalation非生成 |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016 | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0017, 0021, 0023, 0024 | lineage / exact binding invariant、Representation Profile fixture、runtime validation、Adapter mapping provenance |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014 | ADR-0006, 0012, 0013, 0014, 0019, 0021, 0022, 0024 | Capability Observation F1〜F7、cross-provider fixture、synthetic Provider A/B Adapter slice |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016 | ADR-0002, 0005, 0006, 0010, 0011, 0019, 0022, 0024 | Unknown / Conflict / Withheld / partial-knowledge fixture、Adapter missing→unknown検査 |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | ADR-0005, 0017, 0018, 0020, 0021 | human-readable Contract Definition / machine-readable schemaに加え、V6/V7 evaluation harnessでrich canonical source→light/audit Projection、6 semantic questions、7 negative casesを検査 |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | ADR-0005, 0019 | low-impact minimal Decisionとhigh-impact rich Decisionを同じharnessで評価し、low=light / high=auditの明示量policyを検査 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015 | ADR-0006, 0007, 0012, 0013, 0014, 0017, 0019, 0022, 0024 | Provider-neutral Contract、first runtime slice、Provider-specific inputをAdapter-localに保つsynthetic slice |

表中の実装・fixtureが存在しても、そのValue Axis全体のExecutable AcceptanceがSatisfiedになったとは読みません。

## 4. Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0017`です。

```text
Requirement != Acceptance Scenario != Test Case
```

具体的な場面の正本は`SCN-*`です。Product Value側に第二のScenario体系を作りません。

Requirements registryについては、actual checkerとnegative self-testが存在し、GitHub Actionsで次を確認しています。

- Run ID: `33346697016`
- `22 requirements / 17 scenarios`: **PASS**

このPASSはregistry構造のExecutable Evidenceであり、Requirement内容の真実性やimplementation coverageの証明ではありません。

## 5. Architecture baseline

current Reference Architectureは、Milestoneやpackage構成ではなく、意味上のarchitecture concernで構成します。

主なconcernは次のとおりです。

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

`architecture/TRACEABILITY.md`ではREQ-0001〜REQ-0022をcurrent Architecture concernへ追跡しています。

ADR-0024ではProvider Adapterを、Provider固有stateからProvider-neutralなCapability Observationへの観測・解釈境界としてAcceptedしています。Provider固有入力の共通Universal schemaは新設しません。

## 6. Contract baseline

current Contractは次の4 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Contract Conformance:

- Run ID: `33346472419`
- fixture count: `17`
- conclusion: **success**

これは4 Contractのtested boundaryに対するfixture-scoped Executable Evidenceです。

## 7. Representation Profile baseline

ADR-0023 / ISSUE-000009により、current/future Exact Binding向けのRepresentation Profileを次へ分離しました。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Representation Profile Conformance:

- Run ID: `33347989530`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

historical M47 digest mappingは別問題であり、ISSUE-000034でBlockedとして追跡しています。

```text
current Profile verified != historical digest identified
```

## 8. first semantic runtime slice

ADR-0022 / ISSUE-000033に基づき、Goのfirst runtime sliceがactual repositoryにあります。

対象はread / validate / reconstructです。外部Action実行やproduction Provider integrationを先行していません。

Semantic Runtime Conformance #3:

- Run ID: `33348972805`
- Head SHA: `834c3f2a8bd911829743c1582ef09f098c776a54`
- Contract fixture checker: **PASS**
- Go runtime tests: **PASS**
- conclusion: **success**

これはfirst runtime sliceのfixture-scoped Executable Evidenceです。

## 9. synthetic Provider Adapter slice

ADR-0024 / ISSUE-000036に基づき、actual repositoryへ次を実体化しました。

```text
runtime/go/provideradapter/
  adapter.go
  synthetic.go
  adapter_test.go

fixtures/providers/synthetic/
```

異なるProvider-specific input shapeを持つProvider A / Bを、一つのUniversal `ProviderState`へ押し込めず、各Adapterから同じCapability Observation Contractへ収束させます。

検査している主な境界:

- A/Bの異なるinput shape
- status interpretation
- seconds → msのunit conversion
- mapping provenance
- source state reference
- missing readiness / latencyをnegative defaultへ変換しない
- Provider-specific target referenceの保持
- Provider固有fieldをCapability Observation schemaへ漏らさない
- Adapter outputからRecommendation / Decision / Authority / Execution / universal suitability scoreを生成しない
- Adapter outputをcurrent Capability Observation validationへ通す

Semantic Runtime Conformance:

- Run #4 / Run ID `33349604842`: **success** — synthetic Adapter sliceを含む初回closure Evidence
- Run #5 / Run ID `33349801993`: **success** — Provider-specific fieldがAdapter-localに留まる検査を追加したhardening後

ISSUE-000036は**Resolved**です。

これはsynthetic Provider Adapter sliceのExecutable Evidenceです。

```text
synthetic Adapter CI PASS
  != TEI production adapter
  != SaaS production interoperability
  != Provider operational evidence
  != release readiness
```

## 10. Evidenceの現在地

Product Valueの受入れでは、次の高さを分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Design Evidence

current repositoryには、Product、Requirements、Accepted ADR-0001〜0024、Reference Architecture、Contract Definition、Representation Profile Definition、runtime / Provider Adapter boundary、V6/V7 Projection evaluation protocolがあります。

### Executable Evidence

限定された範囲で、次が再現可能です。

- Plan registry integrity
- Requirements registry structural conformance
- Contract v1alpha1 17-fixture conformance
- Representation Profile fixture / Go probe conformance
- first semantic runtime slice conformance
- synthetic Provider Adapter slice conformance
- V6 / V7 Projection evaluation harness conformance

V6 V7 Projection Evaluation:

- Run ID: `33456710459`
- current Contract baseline recheck: **success**
- V6 / V7 Projection evaluation: **success**
- rich / low-impact canonical source: 2件
- Projection profile: light / audit
- semantic question: 6件
- negative case: 7件

このRunが確認するのはevaluation-harness scoped Executable Evidenceです。実利用者の理解可能性やproduction UXを直接確認したものではありません。

### Release Evidence

**Not Yet Verified**

### Operational Evidence

**Not Yet Verified**

### Adoption / Outcome Evidence

**Not Yet Verified**

本番で動くことと、利用者・組織の判断が改善することも分けます。

```text
Operational success != user-value realization
```

## 11. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

current Contract / Profile / runtime / Adapter fixtureで一部境界を検査済みです。一方、historical M47 digest mapping、実Provider mapping変更をまたぐhistorical reconstruction、長期間の実運用履歴、実利用での再判断への寄与は未検証です。

### V2 Semantic Separation

Recommendation / Decision / Authority等の分離に加え、Adapter mappingがDecision / Authority / Executionへ昇格しないこともsynthetic sliceで検査済みです。productionの責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

lineage / exact binding invariantとmapping provenanceの保持は一部検査済みです。mapping versionの変更を実際の長期運用で跨ぐEvidenceはありません。

### V4 Provider Independence

cross-provider Contract fixtureに加え、異なるProvider-specific schemaから同じCapability Observationへ収束するsynthetic Adapter sliceを検査済みです。実Providerの交換・廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / partial knowledgeに加え、Adapter入力欠落を`unknown`として保持し、`false`や`0`を捏造しないことを検査済みです。それが実際の誤判断回避へ寄与したOutcome Evidenceはありません。

### V6 Human / AI Readability

rich canonical sourceから生成したaudit Projectionとmachine-readable representationについて、Decision、unresolved、basis、Responsibility、Authorization Evidence state、Provenanceの6 semantic questionsが一致することをharnessで確認しました。light ProjectionでもDecision、未解決事項、Authorization Evidence stateを前景化し、詳細の存在とaudit導線を保持します。

ただし、これはstatic / synthetic評価です。実利用者が実務上必要な時間と負担で理解できるか、異なるAI実装が同じ意味を安定して読めるかというOperational / Adoption Evidenceはありません。

### V7 Progressive Explicitness

low-impactの最小Decisionはlight Projectionで成立し、basis / Responsibility等の最大詳細を一律必須にしません。high-impactのrich Decisionはaudit Projectionを要求し、lightだけで完了扱いにするとnegative caseとして失敗します。

これによりProgressive Explicitnessのevaluation-harness scoped Executable Evidenceは得られましたが、実運用でのimpact判定、入力負担、見落とし率等は未検証です。

### V8 Execution Independence

SOZA semantic runtimeをexecution dispatchから分離し、Provider固有schemaをAdapter-localに保つsynthetic sliceも成立しています。異なるproduction Execution Provider間で意味を維持したEvidenceはありません。

## 12. CoverageをKPIにしない

この文書は成熟度スコア表ではありません。

次の読み方をしません。

- REQリンクが多いValue Axisほど重要である。
- Contractやfixtureが多いほどProduct Valueが高い。
- CIが多く通るほど利用者価値が高い。
- Executable Evidenceが増えればOperational / Outcomeも自動的に増える。

追跡の目的は、**どこまで確認したかと、どこから先をまだ主張してはいけないかを見失わないこと**です。

## 13. 更新規則

Product Value、REQ、SCN、ADR、Architecture、Contract、Profile、runtime、Provider Adapter、Projection evaluationのいずれかが変わった場合、この文書を必要に応じて更新します。

ただし、下位実装の都合に合わせてProduct Valueを後付けで変更しません。上位仮説を変える必要がある場合はADR-0018のProduct Value再基線化規則に従います。

## 14. 自然な日本語ドラフト

V1〜V8、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、current Architecture、4 Contract family、Representation Profile、first semantic runtime slice、synthetic Provider Adapter slice、V6/V7 Projection evaluation harness、actual CI結果へ戻って追跡を再確認しました。その後、Design / Executable / Release / Operational / Adoption・OutcomeのEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。