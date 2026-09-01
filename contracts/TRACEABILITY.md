# SOZA Contract Traceability

更新日: 2026-09-02  
状態: **Current Contract Traceability Baseline**

## 1. 目的

この文書は、current Semantic ContractがProduct Requirement、Acceptance Scenario、ADR、Reference Architectureのどの境界を規範化し、どこまでactual Executable Evidenceを得ているかを追跡します。

```text
Contract exists
  != Schema exists
  != Fixture PASS
  != Runtime verified in scope
  != Release / Operational / Outcome verified
```

## 2. current Contract family

| Contract | 主なRequirement | 主なScenario | 主なADR | Architecture concern |
|---|---|---|---|---|
| `soza.semantic-reference/v1alpha1` | REQ-0001, 0003, 0005, 0008, 0009, 0018 | SCN-0003, 0008, 0010 | ADR-0003, 0007, 0008, 0009, 0021, 0023 | Reference / Revision / Exact Binding; Persistence |
| `soza.decision-memory/v1alpha1` | REQ-0005, 0006, 0008, 0014, 0015, 0017 | SCN-0001, 0003, 0009, 0016 | ADR-0010, 0011, 0015, 0016, 0021 | Decision Memory; Responsibility / Authority boundary |
| `soza.capability-observation/v1alpha1` | REQ-0002, 0007, 0013, 0016, 0021, 0022 | SCN-0002, 0010, 0011, 0012 | ADR-0012, 0013, 0014, 0019, 0021, 0024 | Capability Understanding; Provider / Adapter |
| `soza.cognitive-method/v1alpha1` | REQ-0003, 0004, 0015, 0016, 0021 | SCN-0005, 0015 | ADR-0017, 0021, 0022, 0025 | Cognitive Method; Reference / Provenance |
| `soza.semantic-interchange/v1alpha1` | REQ-0001, 0002, 0003, 0018, 0019, 0020 | SCN-0001, 0003, 0005, 0006, 0008, 0010, 0015 | ADR-0007, 0008, 0009, 0014, 0021, 0026 | Durable Semantic Core; portable interchange; bundle-local consistency |

Architecture concernをすべて独立Contractへ変換しません。Contract化の有無は意味の重要度ではなく、portable version boundaryを独立して持つ必要性で判断します。

## 3. Contractが直接規範化する主な意味境界

### Semantic Reference

- Logical Reference
- Exact Historical Binding metadata
- Semantic Lineage / supersession
- Verification Outcome
- Representation Profile identity

```text
Logical Reference != Exact Historical Binding
binding metadata != payload verification
```

### Decision Memory

- RecommendationとDecisionの分離
- context / basis / recommendation / unresolved等のReference role
- rationale
- contextual Responsibility
- DecisionにAuthority / Executionを内包させない境界

```text
Recommendation != Decision != Authority != Action Intent != Execution
```

### Capability Observation

- CapabilityとProviderの分離
- observed stateとproposed stateの分離
- observation time
- Unknown / Conflict / Withheld
- mapping provenance
- Provider-specific contextの隔離

```text
Provider state != Capability interpretation != Decision
```

### Cognitive Method

- Method Definition / Realization / Applicationの分離
- Method / Realization / input / output / residual / provenance等のReference role
- Realization未記録を否定事実へ変えない境界
- Patternをdomain-specific knowledgeのReferenceとして扱う境界
- Method ApplicationをRecommendation / Decision / Assuranceへ昇格させない境界
- private chain-of-thoughtに依存しない外在化

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance

Pattern != Cognitive Method
```

### Semantic Interchange

- 異なるContract recordのportable bundle
- current known Contractのtyped nested validation
- unknown nested Contractのopaque保持
- partial knowledge
- envelope / payload Contract identity整合
- known typed Contract横断のbundle-local Exact Binding整合
- original exchange bytesをreadだけで書き換えない境界

ADR-0026 / ISSUE-000049により、Decision basis専用だったExact Binding比較をknown Contractのtyped Reference roleへ一般化しました。

```text
known typed Contract
  → typed Exact Reference extraction
  → logical identityごとの複数Exact Binding index
  → common bundle-local consistency check
```

この検査はpayload bytesの再hashではありません。

## 4. Representation Profileとの境界

```text
Semantic Contract != Representation Profile != verifier implementation
```

current/future Exact Binding向けProfile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

JCS ProfileのauthorityはRFC 8785とSOZA Profile Definitionです。current Go libraryは交換可能な実装であり、Profile authorityではありません。

historical M47 digest mappingはISSUE-000034のResolved方針どおりcurrent Profileから推定せず、回収不能な範囲を`not_verified`として保持します。

## 5. Acceptance Scenarioとの主な対応

| Scenario | Contract上の主な検証対象 |
|---|---|
| SCN-0001 根拠が割れている判断 | Interchange / Decision MemoryがUnknown / Conflict / provenanceを潰さない |
| SCN-0002 同じIntent、異なるCapability Provider | Capability ObservationでProvider-neutralな状態を扱う |
| SCN-0003 新しいEvidenceでDecisionを見直す | Decision Memory + Semantic Referenceで当時basisとlineageを保持する |
| SCN-0005 Cognitive MethodとRealizationを交換する | Cognitive MethodでDefinition / Realization / Applicationを分離し、必要なExact Referenceを保持する |
| SCN-0006 Projectionを作り直す | Interchange / canonical sourceをProjection authorityから分離する |
| SCN-0008 Storageを交換する | Reference / InterchangeがStorage identityに意味を固定しない |
| SCN-0009 RecommendationからExecutionまで | Decision MemoryがRecommendation / Decisionを分離する |
| SCN-0010 可変Artifact更新後に再構成する | Exact Binding / Verification Outcome / Decision basisを分離する |
| SCN-0011 Providerがdegraded / 未観測 | Capability ObservationがUnknown / observed stateを保持する |
| SCN-0012 Selective Disclosure | Capability ObservationがWithheld / provider-specific contextを保持する |
| SCN-0015 PatternとCognitive Methodを分離する | PatternをMethod input Referenceとして保持し、Method / Decisionへ自動昇格させない |
| SCN-0016 Decision後も残差を渡す | Decision unresolved refs / Method residual refsを保持できる |

## 6. machine-readable representation

actual repositoryには5 Contract familyのJSON Schemaがあります。

```text
contracts/schemas/v1alpha1/
  semantic-reference.schema.json
  decision-memory.schema.json
  capability-observation.schema.json
  cognitive-method.schema.json
  semantic-interchange.schema.json
```

Schemaで自然に表せないcross-record / semantic invariantは`tools/check_contract_conformance.py`で検査します。

Contract Definitionがsemantic normative sourceです。Schema、checker、Go structの都合からContract意味を後付けで変更しません。

## 7. Contract fixture-scoped Executable Evidence

current Contract checkerは39 fixtureを検査します。

代表CI:

- Contract Conformance Run `33527512045`: **success**
- Semantic Runtime Conformance Run `33527512016`: **success**

主な検査対象:

- Capability Observation F1〜F7
- Cognitive Method C1〜C8
- Recommendation-only / unresolved Decision
- same-logical lineage invariant
- partial knowledge
- unknown nested Contract → `not_verified`
- Cognitive Method `method_ref` / `realization_ref`のbundle-local Exact Binding整合
- Capability Observation source refのbundle-local Exact Binding整合
- 同一logical identityの複数Exact Binding保持
- external Exact Referenceの非FAIL
- logical-only Referenceの非昇格
- unknown Contractのexact風fieldを非推測解析

fixture PASSはContract全意味領域の完全coverageではありません。

## 8. semantic runtimeとの接続

Go semantic runtimeはread / validate / reconstructを中核とし、workflow / agent execution engineにはしません。

current bundle-local consistencyでは、`RecordValidated`になったknown typed ContractだけからExact Referenceを抽出します。

対象:

- Decision / RecommendationのReference role
- Cognitive Method Definition / Realization / ApplicationのReference role
- Capability Observationのsource / provenance / mapping role
- Semantic ReferenceのExact Binding / lineage / verification binding

同じlogical identityに複数のexact-bound recordが存在する場合は候補をすべて保持し、参照がいずれか一つと完全一致すれば受理します。

```text
same logical identity
  != same exact revision
```

bundle内に同じlogical identityのexact-bound recordが存在しない場合、この検査だけを理由にFAILとしません。外部payloadの取得・digest再計算はPayload Source / Verifier Registryへ委ねます。

unknown Contractはopaque + `not_verified`のままとし、JSON field名からExact Referenceを推測しません。

## 9. Representation Verifier / Payload Sourceとの責務分離

```text
bundle-local consistency
  != payload acquisition
  != digest verification
  != Verification Outcome
```

- Verifier Registry代表Run `33452115728`: **success**
- Payload Source代表Run `33457416359`: **success**

bundle-local検査がPASSしても、参照先bytesを実際に取得・再hashできたとは主張しません。

## 10. Provider Adapterとの接続

synthetic Provider A / B AdapterはCapability Observationを出力境界として利用します。

代表Run:

- `33349604842`: **success**
- `33349801993`: **success**

Provider-specific input schemaそのものはUniversal Contractにしません。

## 11. Evidence状態

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Established within stated scope

- 5 current Contract Design baseline
- 5 JSON Schema
- 39-fixture Contract Conformance
- Go semantic runtimeによるcurrent known Contract read / validate / reconstruct
- known typed Contract横断のbundle-local Exact Binding consistency
- Cognitive Method typed runtime slice
- current Representation Profiles / in-process verifier
- synthetic Provider Adapter

### Not Yet Verified / intentionally outside this scope

- Contract全意味領域の完全coverage
- external payload acquisitionを含むcross-bundle verification
- Method executor / Prompt / agent / human procedure execution
- Cognitive Method quality / conclusion truth / Assurance
- production Provider / TEI interoperability
- production Storage migration
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

## 12. Coverageの読み方

Contract family数、fixture数、Requirement link数、CI件数をProduct Valueの点数へ変換しません。

追跡の目的は、**どの意味境界をどこまで検査したかと、どこから先をまだ主張してはいけないかを明確にすること**です。

## 13. 自然な日本語レビュー

REQ / SCN、ADR-0001〜0026、Reference Architecture、5 Contract Definition、current 39 fixture、2 Representation Profile、Go semantic runtime、Payload Source、Verifier Registry、actual CIへ戻って追跡を再確認しました。ISSUE-000049で実装したcross-Contract consistencyをExecutable Evidenceへ反映する一方、bundle-local整合をpayload verificationやproduction成立へ読み替えないよう境界を明示しています。そのうえで、意味とEvidence強度を変えず、自然な日本語となることを重要視して全文を再ドラフトし、最終意味監査を実施済みです。
