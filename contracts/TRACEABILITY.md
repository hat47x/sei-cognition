# SOZA Contract Traceability

更新日: 2026-09-01  
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
| `soza.semantic-interchange/v1alpha1` | REQ-0001, 0002, 0003, 0018, 0019, 0020 | SCN-0001, 0003, 0005, 0006, 0008, 0010, 0015 | ADR-0007, 0008, 0009, 0014, 0021 | Durable Semantic Core; portable interchange; Persistence |

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

synthetic Provider Adapterは、このContractを出力境界として利用します。Provider-specific input schemaそのものはUniversal Contractにしません。

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
- bundle-local Exact Binding整合の一部
- original exchange bytesをreadだけで書き換えない境界

ADR-0026では、現在Decision basis中心のbundle-local Exact Binding比較をknown Contract横断へ一般化する設計をAcceptedしました。実装はISSUE-000049で追跡し、未実装範囲をcurrent PASSへ先取りしません。

## 4. Representation Profileとの境界

```text
Semantic Contract != Representation Profile != verifier implementation
```

ADR-0023に基づくcurrent/future Exact Binding向けProfile:

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
| SCN-0005 Cognitive MethodとRealizationを交換する | Cognitive MethodでDefinition / Realization / Applicationを分離し、Exact Referenceを保持する |
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

```text
Schema valid != Semantic conformance complete
```

Contract Definitionがsemantic normative sourceです。Schema、checker、Go structの都合からContract意味を後付けで変更しません。

## 7. Contract fixture-scoped Executable Evidence

current Contract checkerは31 fixtureを検査します。

GitHub Actions `Contract Conformance`:

- Run ID: `33467838961`
- conclusion: **success**
- fixture count: **31**

主な検査対象:

- Capability Observation F1〜F7
- Recommendation-only / unresolved Decision
- same-logical lineage invariant
- exact-binding mismatch
- partial knowledge
- unknown nested Contract → `not_verified`
- Cognitive Method C1〜C8
- Method ApplicationへのDecision / Assurance / Pattern field混入拒否
- Method / Application required-reference欠落拒否
- unknown Cognitive Method version → opaque / `not_verified`

fixture PASSはContract全意味領域の完全coverageではありません。

## 8. semantic runtimeとの接続

Go semantic runtimeはread / validate / reconstructに限定します。

current Cognitive Method first sliceでは、次をactual testで確認しています。

- C1〜C7 standalone documentのtyped load
- C8 current Semantic Interchange内Method Applicationのtyped load
- original Interchange bytesのlossless export
- Realization省略を勝手に補わない
- Exact-bound Method / Realization Referenceを保持する
- Pattern inputをPatternのReferenceとして保持する
- output / residual refsを保持する
- unknown Cognitive Method versionをopaque + `not_verified`にする
- Method ApplicationをDecisionへ昇格させない

Semantic Runtime Conformance:

- Run ID: `33467838941`
- conclusion: **success**

```text
Cognitive Method typed read PASS
  != Method execution verified
  != Method quality / Assurance verified
```

### Representation Verifier Registry

runtime Registryはcurrent Profileをin-processで解決します。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

代表Run:

- `33452115728`: **success**

Payload取得不能とdigest mismatchを分離し、unknown Profileを`not_verified`へ保ちます。Verifier実装はProfile authorityではありません。

## 9. Provider Adapterとの接続

actual repositoryにはsynthetic Provider A / B Adapter sliceがあります。

```text
runtime/go/provideradapter/
fixtures/providers/synthetic/
```

主な確認範囲:

- 異なるProvider-specific input shape
- status interpretation / unit conversion
- mapping provenance / source state reference
- missing → `unknown`
- Provider-specific fieldのUniversal Capability Observationへの非漏洩
- Adapter outputのDecision / Authority / Executionへの非昇格

代表Run:

- `33349604842`: **success**
- `33349801993`: **success**

```text
synthetic Adapter PASS
  != production Provider interoperability
```

## 10. Exact Binding bundle consistencyの次段

current runtimeには、bundle内のexact-bound recordとDecision basisのExact Binding不一致を検出する実装があります。

Cognitive Method Contract追加により、Exact BindingはMethod / Realization / input等にも現れ得ます。ADR-0026はこの共通意味を整理し、ISSUE-000049で次を実装対象にしました。

```text
known typed Contract
  → typed Exact Reference extraction
  → common bundle-local consistency check
```

ただし、これはpayload bytesの再hashではありません。

```text
bundle-local consistency
  != content verification
  != Verification Outcome
```

ISSUE-000049がOpenであるため、この一般化をcurrent Executable Evidenceとしてはまだ主張しません。

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
- 31-fixture Contract Conformance
- Go semantic runtimeによるcurrent known Contract read / validate / reconstruct
- Cognitive Method typed runtime slice
- current Representation Profiles / in-process verifier
- synthetic Provider Adapter

### Not Yet Verified / intentionally outside this scope

- Contract全意味領域の完全coverage
- Method executor / Prompt / agent / human procedure execution
- Cognitive Method quality / conclusion truth / Assurance
- ISSUE-000049のcross-Contract Exact Binding一般化実装
- production Provider / TEI interoperability
- production Storage migration
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

## 12. Coverageの読み方

Contract family数、fixture数、Requirement link数、CI件数をProduct Valueの点数へ変換しません。

追跡の目的は、**どの意味境界をどこまで検査したかと、どこから先をまだ主張してはいけないかを明確にすること**です。

## 13. 自然な日本語レビュー

REQ / SCN、ADR-0001〜0026、Reference Architecture、5 Contract Definition、31 fixture、2 Representation Profile、Go semantic runtime、Cognitive Method first slice、synthetic Provider Adapter、actual CIへ戻って追跡を再確認しました。その後、Cognitive Methodの新しいExecutable Evidenceと、ISSUE-000049でまだ未実装のcross-Contract consistency、production / Release以降の未検証範囲を分離し、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
