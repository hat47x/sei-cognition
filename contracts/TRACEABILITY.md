# SOZA Contract Traceability

更新日: 2026-09-02  
状態: **Current Contract Traceability Baseline**

## 1. 目的

この文書は、current Semantic ContractがProduct Requirement、Acceptance Scenario、ADR、Reference Architectureのどの境界を規範化し、actual repositoryでどこまでExecutable Evidenceを得ているかを追跡します。

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
| `soza.semantic-reference/v1alpha1` | REQ-0001, 0003, 0005, 0008, 0009, 0018 | SCN-0003, 0008, 0010 | ADR-0003, 0007, 0008, 0009, 0021, 0023, 0026 | Reference / Revision / Exact Binding; Persistence |
| `soza.decision-memory/v1alpha1` | REQ-0005, 0006, 0008, 0014, 0015, 0017 | SCN-0001, 0003, 0009, 0016 | ADR-0010, 0011, 0015, 0016, 0021, 0026 | Decision Memory; Responsibility / Authority boundary |
| `soza.capability-observation/v1alpha1` | REQ-0002, 0007, 0013, 0016, 0021, 0022 | SCN-0002, 0010, 0011, 0012 | ADR-0012, 0013, 0014, 0019, 0021, 0024, 0026 | Capability Understanding; Provider / Adapter |
| `soza.cognitive-method/v1alpha1` | REQ-0003, 0004, 0015, 0016, 0021 | SCN-0005, 0015 | ADR-0017, 0021, 0022, 0025, 0026 | Cognitive Method; Reference / Provenance |
| `soza.semantic-interchange/v1alpha1` | REQ-0001, 0002, 0003, 0018, 0019, 0020 | SCN-0001, 0003, 0005, 0006, 0008, 0010, 0015 | ADR-0007, 0008, 0009, 0014, 0021, 0026 | Durable Semantic Core; portable interchange; Persistence |

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
- context / basis / recommendation / unresolved / responsibility等のReference role
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
- source / provenance / mapping Reference
- Provider-specific contextの隔離

```text
Provider state != Capability interpretation != Decision
```

### Cognitive Method

- Method Definition / Realization / Applicationの分離
- Method / Realization / input / output / residual / provenance等のReference role
- Realization未記録を否定事実へ変えない境界
- Patternをdomain-specific knowledgeへのReferenceとして扱う境界
- Method ApplicationをRecommendation / Decision / Assuranceへ昇格させない境界

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
- known Contract横断のbundle-local Exact Binding整合
- original exchange bytesをreadだけで書き換えない境界

## 4. bundle-local Exact Binding整合

ADR-0026 / ISSUE-000049により、Decision `basis_refs`専用だった比較をknown Contract横断の共通規則へ一般化しました。

```text
known typed Contract
  → typed Exact Reference extraction
  → common bundle-local consistency check
```

bundle envelopeのExact Bindingは次の形で保持します。

```text
logical identity
  → [exact binding A, exact binding B, ...]
```

同一logical identityに複数revisionがあってもlatest-winsで潰しません。known typed Referenceがexactであり、同じlogical identityのexact-bound recordがbundle内にある場合、そのうち一つとbinding全体が一致する必要があります。

一方、次はこの規則ではFAILにしません。

- bundle内に同じlogical identityがないexternal Exact Reference
- logical-only Reference
- unknown Contract payload内のexact-looking JSON

```text
bundle-local consistency
  != content verification
  != Verification Outcome
  != external Artifact existence guarantee
```

## 5. Representation Profileとの境界

```text
Semantic Contract != Representation Profile != verifier implementation
```

current/future Exact Binding向けProfile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

JCS ProfileのauthorityはRFC 8785とSOZA Profile Definitionです。Go libraryやchecker実装をProfile authorityにはしません。

historical M47 digest mappingはISSUE-000034の方針どおりcurrent Profileから推定せず、回収不能な範囲を`not_verified`として保持します。

## 6. Acceptance Scenarioとの主な対応

| Scenario | Contract上の主な検証対象 |
|---|---|
| SCN-0001 | Interchange / Decision MemoryがUnknown / Conflict / provenanceを潰さない |
| SCN-0002 | Capability ObservationでProvider-neutralな状態を扱う |
| SCN-0003 | Decision Memory + Semantic Referenceで当時basisとlineageを保持し、bundle-local exact mismatchを拒否する |
| SCN-0005 | Cognitive MethodでDefinition / Realization / Applicationを分離し、Exact Referenceを保持・照合する |
| SCN-0006 | Interchange / canonical sourceをProjection authorityから分離する |
| SCN-0008 | Reference / InterchangeがStorage identityに意味を固定しない |
| SCN-0009 | Decision MemoryがRecommendation / Decisionを分離する |
| SCN-0010 | Exact Binding / Verification Outcome / Decision basisを分離し、可変Artifactのrevision取り違えを検出する |
| SCN-0011 | Capability ObservationがUnknown / observed stateを保持する |
| SCN-0012 | Capability ObservationがWithheld / provider-specific contextを保持する |
| SCN-0015 | PatternをMethod input Referenceとして保持し、Method / Decisionへ自動昇格させない |
| SCN-0016 | Decision unresolved refs / Method residual refsを保持できる |

## 7. machine-readable representationとfixture

actual repositoryには5 Contract familyのJSON Schemaがあります。

```text
contracts/schemas/v1alpha1/
```

Schemaで自然に表せないcross-record invariantは`tools/check_contract_conformance.py`で検査します。

current Contract checkerは36 fixtureを検査します。

- Contract Conformance Run `33527524514`: **success**
- Semantic Runtime Conformance Run `33527524668`: **success**

主な追加Evidence:

- Cognitive Method C9
- Method exact reference digest mismatch拒否
- Realization exact reference Profile version mismatch拒否
- Capability Observation exact source ref mismatch拒否
- unknown Contract exact-looking payloadの非推測
- same-logical multiple revisionの保持
- external exact / logical-only参照の境界

```text
Schema valid != Semantic conformance complete
fixture PASS != Contract全意味領域の完全coverage
```

## 8. semantic runtimeとの接続

Go semantic runtimeはread / validate / reconstructを基本責務とし、known Contractのtyped Reference roleからExact Referenceを抽出します。

実装:

```text
runtime/go/semanticruntime/loader.go
runtime/go/semanticruntime/bundle_exact_test.go
```

current runtimeはunknown Contractをopaque + `not_verified`へ保ち、未知payloadをfield名から推測走査しません。

### Representation Verifier Registry

runtime Registryはcurrent Profileをin-processで解決し、payloadが取得できた場合にdigestを再計算します。これはbundle-local consistencyとは別のEvidenceです。

```text
bundle-local consistency PASS
  != verifier PASS
```

## 9. Provider Adapterとの接続

synthetic Provider AdapterはProvider固有stateをCapability Observationへ写像します。

- status interpretation / unit conversion
- mapping provenance / source state reference
- missing → `unknown`
- Provider-specific fieldのUniversal fieldへの非漏洩
- Decision / Authority / Executionへの非昇格

```text
synthetic Adapter PASS
  != production Provider interoperability
```

## 10. Evidence状態

### Established within stated scope

- 5 current Contract Design baseline
- 5 JSON Schema
- 36-fixture Contract Conformance
- current known Contract typed read / validate / reconstruct
- known Contract横断のbundle-local Exact Binding consistency
- current Representation Profiles / in-process verifier
- synthetic Payload Source / Provider Adapter

### Not Yet Verified / intentionally outside this scope

- Contract全意味領域の完全coverage
- external Artifactの存在・取得可能性をbundle consistencyだけから保証すること
- Method quality / conclusion truth / Assurance
- production Provider / TEI interoperability
- production Storage migration
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

## 11. 自然な日本語レビュー

ADR-0026、ISSUE-000049、5 Contract Definition、36 fixture、Python Contract checker、Go semantic runtime、最新develop追随後のRun `33527524514` / `33527524668`へ戻って追跡関係を確認しました。Decision専用だった検査をknown typed Contractへ一般化した一方、payload verification、unknown Contract推測、external Artifact存在保証へ意味を広げていません。そのうえで、Requirement / Scenarioとの対応と5段階Evidenceの強度を保ち、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
