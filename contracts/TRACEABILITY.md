# SOZA Contract Traceability

更新日: 2026-08-31  
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

ADR-0024では、Provider Adapterが生成するObservationもこのContractで検証する方針をAcceptedしています。

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

Provider Adapter sliceでは、とくにSCN-0002 / 0011 / 0014に関わるDesign boundaryを、synthetic heterogeneous ProviderでExecutable Evidenceへ落とす予定です。

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

主な検査対象:

- Capability Observation F1〜F7
- Recommendation without Decision
- Decision with unresolved state
- DecisionへのAuthority field埋め込み拒否
- capability `observed_at`欠落のSchema rejection
- same-logical-id lineage without exact endpointsのsemantic rejection
- bundle内exact recordとDecision basisのdigest不一致検出
- unknown nested Contractを`not_verified`として扱う
- `failed`と`not_verified`を分ける
- partial-knowledge interchange

GitHub Actions `Contract Conformance`:

- Run ID: `33346472419`
- fixture count: 17
- conclusion: **success**

このEvidenceはcurrent v1alpha1 fixtureのtested boundaryに限定します。

## 8. Representation Profile Executable Evidence

Profile fixture / verifier probeについて次を確認しています。

GitHub Actions:

- Run ID: `33347989530`
- `profile-fixtures`: **success**
- `jcs-go-probe`: **success**

主な境界:

- key order / whitespace差のcanonical一致
- duplicate key rejection
- unsafe integerの暗黙丸め拒否
- Unicode normalization非適用
- raw bytesのdigest再現
- `verified / failed / not_verified`の分離

これはcurrent/future Profileのfixture-scoped Executable Evidenceであり、historical M47 digestの識別Evidenceではありません。

## 9. runtimeとの接続

ADR-0022に基づくGo first runtime sliceは、Contract checkerと同じfixture sourceを使います。

GitHub Actions `Semantic Runtime Conformance`:

- Run ID: `33348972805`
- Head SHA: `834c3f2a8bd911829743c1582ef09f098c776a54`
- Contract fixture checker: **PASS**
- Go runtime tests: **PASS**
- conclusion: **success**

runtimeはread / validate / reconstructに限定し、Action execution、Provider production integration、Authorization enforcement等を本Evidenceへ含めません。

## 10. Provider Adapterとの接続

ADR-0024ではProvider Adapterを、Provider固有stateからCapability Observationへの観測変換境界として定義しています。

Adapterによるfield mapping、unit conversion、status interpretation、missing-value interpretation等は意味上の解釈を含み得るため、mapping provenanceを保持します。

Adapterの出力はcurrent Capability Observation validationへ接続しますが、Adapter自体がMatching / Decision / Authority / Executionを所有することは認めません。

ISSUE-000036は**Open**です。したがって、現在のEvidenceはDesignまでであり、synthetic Adapter CI PASSはまだ主張しません。

## 11. Requirement coverageの読み方

current Contractが直接扱うRequirementが多くても、Contract数やfixture数をProduct ValueのKPIにはしません。

Architecture / Profile / Provider側に留める方が自然なRequirementもあります。

たとえば次は、current baselineで独立Semantic Contractを追加する必要が確定していません。

- REQ-0004 Cognitive Method
- REQ-0010 Progressive Explicitness
- REQ-0011 Projection非権威
- REQ-0012 Bounded Collaboration / Selective Disclosure

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
- Provider Adapter observation mapping Design boundary

### Not Yet Verified

- synthetic Provider Adapter Executable Evidence — ISSUE-000036
- historical M47 digest mapping — ISSUE-000034
- production-grade Runtime Verifier Registry / Adapter integration
- production Provider / TEI interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

## 13. 自然な日本語レビュー

REQ、SCN、ADR-0001〜0024、Architecture、4 Contract Definition、Representation Profile、17 fixture、Contract Conformance、first semantic runtime slice、Provider Adapter observation mapping boundaryへ戻って追跡を再確認しました。その後、Design / Executableの成立範囲と、Release / Operational / Adoption・Outcomeの未検証範囲を分離し、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
