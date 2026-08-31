# SOZA Contract Traceability

更新日: 2026-09-01  
状態: **Current Contract Traceability Baseline**

## 1. 目的

この文書は、current ContractがProduct Requirement、Acceptance Scenario、ADR、Reference Architectureのどの境界を規範化し、どの範囲までExecutable Evidenceを得ているかを示します。

Contractが存在すること、schemaが存在すること、fixtureがPASSすること、本番で利用できることは同じではありません。

## 2. current Contract family

| Contract | 主なRequirement | 主なADR | Architecture concern |
|---|---|---|---|
| `soza.semantic-reference/v1alpha1` | REQ-0001, 0003, 0005, 0008, 0009, 0018 | ADR-0003, 0007, 0008, 0009, 0021, 0023 | Semantic Reference / Revision / Exact Binding; Persistence |
| `soza.decision-memory/v1alpha1` | REQ-0005, 0006, 0008, 0014, 0015, 0017 | ADR-0010, 0011, 0015, 0016, 0021 | Decision Memory; Responsibility / Authority |
| `soza.capability-observation/v1alpha1` | REQ-0002, 0007, 0013, 0016, 0021, 0022 | ADR-0012, 0013, 0014, 0019, 0021, 0024 | Capability Understanding / Choice; Provider / Adapter |
| `soza.semantic-interchange/v1alpha1` | REQ-0001, 0002, 0003, 0018, 0019, 0020 | ADR-0007, 0008, 0009, 0014, 0021 | Durable Semantic Core; Persistence; portable interchange |

current baselineでは、Architecture concernをすべて独立Contractへ変換しません。

## 3. Contractが直接規範化する主な意味境界

### Semantic Reference

- logical reference
- exact historical binding metadata
- semantic lineage / supersession
- verification outcome
- representation profile identity

### Decision Memory

- RecommendationとDecisionの分離
- context / basis / recommendation / unresolved等の参照役割
- rationale
- Responsibility参照
- DecisionにAuthorityを内包させない境界

### Capability Observation

- CapabilityとProviderの分離
- observed stateとproposed stateの分離
- `observed_at`
- Unknown / Withheld等のcondition state
- mapping provenance
- provider-specific contextの隔離

ADR-0024では、Provider Adapterが生成するObservationもこのContractで検証します。

```text
Adapter produced output != validated Capability Observation
```

Provider-specific input schemaそのものを新しいUniversal Contractにはしません。

### Semantic Interchange

- 異なるContract recordのbundle
- unknown nested Contractの保持
- partial knowledge
- exact-bound recordと参照側bindingの整合
- original exchange representationを読み込みだけで書き換えない境界

## 4. Representation Profileとの境界

Semantic Contractは、canonical bytesやhash algorithmをUniversalに固定しません。

```text
Semantic Contract != Representation Profile != verifier implementation
```

ADR-0023により、current/future Exact Binding向けに次のProfileを定義しています。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

JCS ProfileのauthorityはRFC 8785とSOZA Profile Definitionです。current Go libraryは交換可能なVerifier実装です。

historical M47 digest mappingは別途ISSUE-000034で追跡します。

## 5. Acceptance Scenarioとの主な対応

| Scenario | Contract上の主な検証対象 |
|---|---|
| SCN-0001 根拠が割れている判断 | Interchange / Decision MemoryがUnknown / Conflict / provenanceを潰さない |
| SCN-0002 同じ目的、異なるCapability | Capability ObservationをProvider kindで優遇しない |
| SCN-0003 後から判断が覆る | Decision Memory + Semantic Referenceで過去basisを保持する |
| SCN-0006 Projectionを作り直す | interchange representationをsemantic authorityにしない |
| SCN-0008 Storageを交換する | Semantic Reference / InterchangeがStorage identityへ依存しない |
| SCN-0009 RecommendationとDecisionが異なる | Decision Memoryが両者を分離する |
| SCN-0010 Decisionをsupersedeする | Semantic Lineageで旧Decisionを削除しない |
| SCN-0011 Capability情報が不足・競合する | Capability ObservationがUnknown / Conflictを保持する |
| SCN-0014 Providerを交換する | Capability / ProviderとSemantic Interchangeを分離する |
| SCN-0016 未解決のまま判断する | Decision作成でUnknown / Conflictを解消しない |

synthetic Provider Adapter sliceでは、とくにSCN-0002 / 0011 / 0014に関わる境界を、異質なProvider-specific inputでExecutable Evidenceへ落としています。

## 6. machine-readable representation

actual repositoryには4 ContractのJSON Schemaがあります。

```text
contracts/schemas/v1alpha1/
  semantic-reference.schema.json
  decision-memory.schema.json
  capability-observation.schema.json
  semantic-interchange.schema.json
```

Schemaで自然に表せないcross-record / semantic invariantは`tools/check_contract_conformance.py`で検査します。

```text
Schema valid != Semantic conformance complete
```

Contract Definitionがsemantic normative sourceです。SchemaやGo structの都合でContract意味を変更しません。

## 7. Contract fixture-scoped Executable Evidence

actual repositoryには17 fixtureがあります。

GitHub Actions `Contract Conformance`:

- Run ID: `33346472419`
- fixture count: 17
- conclusion: **success**

主な検査対象にはCapability Observation F1〜F7、Recommendation-only、unresolved Decision、Schema / semantic negative case、unknown nested Contractの`not_verified`、partial knowledge等を含みます。

## 8. Representation Profile Executable Evidence

GitHub Actions:

- Run ID: `33347989530`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

key order / whitespace、duplicate key、unsafe integer、Unicode normalization、raw bytes、`verified / failed / not_verified`等の境界を検査しています。

これはcurrent/future Profileのfixture-scoped Executable Evidenceであり、historical M47 digestの識別Evidenceではありません。

## 9. semantic runtimeとの接続

ADR-0022に基づくGo first runtime sliceは、Contract checkerと同じfixture sourceを使います。

GitHub Actions `Semantic Runtime Conformance` #3:

- Run ID: `33348972805`
- Contract fixture checker: **PASS**
- Go semantic runtime tests: **PASS**

runtimeはread / validate / reconstructに限定し、Action execution、Provider production integration、Authorization enforcement等を本Evidenceへ含めません。

### Representation Verifier Registry

ISSUE-000038では、ADR-0008 / ADR-0009 / ADR-0023で既に決定済みのRepresentation Profile検証境界を、first semantic runtimeへ最小実装として接続しました。

actual implementation:

```text
runtime/go/semanticruntime/verifier.go
runtime/go/semanticruntime/verifier_test.go
```

runtime Registryは次のcurrent Profileを解決します。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Go testでは`fixtures/representation-profiles/`の既存Profile fixtureを直接再利用し、少なくとも次を確認しています。

- JCS canonicalization後のdigest一致 → `verified`
- digest mismatch → `failed`
- duplicate key等の不正representation → `failed`
- unsafe large integerを暗黙丸めしない → `failed`
- NFC / NFDを勝手にnormalizeしない
- raw UTF-8 / binary bytesのdigest一致 → `verified`
- unknown Profile → `not_verified`
- payload unavailable → `not_verified`
- verificationによってExact Bindingをmutateしない

Semantic Runtime Conformance:

- Run ID: `33452115728`
- Head SHA: `9941f49a5af3b5443f3cfaca3b263e07989d3ba4`
- Contract fixture recheck: **success**
- Go runtime / Provider Adapter / Representation Verifier tests: **success**

```text
in-process Profile verification PASS
  != external payload acquisition verified
  != production verifier operation
```

Verifier implementationはProfile authorityではありません。JCS側はADR-0023で採用したProfile Definition / RFC 8785に従い、Go dependencyは再現可能なversionとchecksumで固定しています。

## 10. Provider Adapterとの接続

ADR-0024ではProvider Adapterを、Provider固有stateからCapability Observationへの観測変換境界として定義しています。

actual repositoryにはsynthetic Provider A / BのAdapter sliceがあります。

```text
runtime/go/provideradapter/
fixtures/providers/synthetic/
```

検査している主な境界:

- Provider A / Bの異なるinput shape
- status interpretation / unit conversion
- mapping provenance
- source state reference
- missing値の`unknown`保持
- Provider-specific target reference
- Provider固有fieldのCapability Observation schemaへの非漏洩
- Adapter outputのDecision / Authority / Executionへの非昇格
- current Capability Observation runtime validationへの接続

Semantic Runtime Conformance:

- Run #4 / `33349604842`: **success**
- Run #5 / `33349801993`: **success** — Provider-specific field非漏洩の追加hardeningを含む

ISSUE-000036はResolvedです。

```text
synthetic Adapter PASS
  != production Provider interoperability
```

## 11. Requirement coverageの読み方

current Contractが直接扱うRequirementが多くても、Contract数やfixture数をProduct ValueのKPIにはしません。

Architecture / Profile / Provider側に留める方が自然なRequirementもあります。

Provider Adapterについても、Provider-specific inputのUniversal schemaを新設しません。

## 12. Evidence状態

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Satisfied / established within stated scope

- current Contract Design baseline
- 4 Contract JSON Schema
- 17-fixture Contract conformance
- current Representation Profile Design baseline
- Profile fixture / Go probe conformance
- Contract fixtureを読むfirst semantic runtime slice
- current JCS / raw-bytes Profileを解決するin-process Runtime Verifier Registry
- Provider Adapter observation mapping Design boundary
- synthetic Provider Adapter slice conformance

### Not Yet Verified

- historical M47 digest mapping — ISSUE-000034
- external source / object storage等からのpayload acquisition
- large objectのproduction streaming verification
- production Provider / TEI interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

## 13. 自然な日本語レビュー

REQ、SCN、ADR-0001〜0024、Architecture、4 Contract Definition、Representation Profile、17 Contract fixture、Profile fixture、first semantic runtime、synthetic Provider Adapter、ISSUE-000038のRuntime Verifier Registry、actual CI結果へ戻って追跡を再確認しました。その後、in-processで成立したExecutable Evidenceと、external payload acquisition / production operation以降の未検証範囲を分離し、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
