# ADR-0019: Provider-neutralなCapability Observation境界を定める

Status: **Accepted**  
Related Issues: **ISSUE-000020, ISSUE-000024, ISSUE-000035, ISSUE-000036**  
Updated: 2026-08-31

## Context

ADR-0012ではCapability DefinitionとCapability Observationを分離し、ADR-0013ではProvider固有のOffering / Binding / DeploymentをUniversal `CapabilityRealization`へ統合しないことを決めた。ADR-0014では、SOZAとTEIを別Product Boundaryとして維持することを定めた。

SOZAがTEI、SaaS、人間、AI、外部組織等をCapability Providerとして扱うには、Provider内部の状態をすべて共通化しなくても、現在の利用可能性、条件、未確認点、Evidence等を読める必要がある。

Provider固有SchemaをSOZAへ持ち込むとProvider Independenceを失う。逆に、Provider状態を単純な`available / unavailable`だけへ圧縮すると、Unknown、degraded state、部分的制約、Evidence、historical basisを失う。

## Decision

### 1. SOZAはProvider-neutralなObservation envelopeを所有する

SOZAが所有するのはProvider内部Schemaそのものではなく、Capability判断に必要な観測結果を外在化するための意味境界である。

Observationは、必要に応じて次を参照できるようにする。

- 対象となるCapability Definition
- Providerまたはbounded provider reference
- Provider-specific context / offering / binding等へのReference
- 観測時点
- 観測されたproperty / condition
- Evidence / provenance
- Unknown / Conflict / Withheld等の認識状態
- exact historical binding

### 2. Provider内部SchemaはAdapter境界の外側に残す

Provider固有のApplication、Database、Environment、Release、Plugin、契約、API response等は、それぞれのProvider側の正本として維持する。

SOZAは、それらを必要に応じてReference、Observation、Evidenceとして読む。

```text
Provider internal state
    ↓ Adapter / Mapping
SOZA Capability Observation
    ↓ matching / inquiry / review
Recommendation or Decision
```

Provider内部の構造をSOZA Universal Coreへ複製しない。

### 3. Adapterは単なるformat変換ではなく解釈境界として扱う

Provider固有stateから、Capabilityが利用可能、制約付き、未確認等のどれに相当するかは、自明とは限らない。

そのため、field mapping、unit conversion、status interpretation、aggregation等を行う場合は、そのmappingを意味上の解釈として扱い、必要なProvenanceを残す。

重要なDecisionのbasisになった場合は、使用したmapping / adapter versionを後から特定できるようにする。

```text
Provider state != Capability interpretation
Capability interpretation != Decision
```

### 4. `not observed`を`unavailable`へ変換しない

観測できなかったこと、Providerが情報を開示しなかったこと、観測結果が競合したことを、単純な利用不能へ潰さない。

少なくとも、次の意味差を保てる設計とする。

- observed condition
- unknown / not observed
- conflicting observations
- withheld context

Provider-specificなstatus vocabularyをUniversal Coreへ固定する必要はない。

### 5. 比較用の正規化とsource provenanceを分ける

複数Providerを比較するために、availability、cost、latency、auditability等の共通facetへ正規化することはできる。

ただし、正規化値だけを残さず、元のProvider state / Observation、Evidence、mapping provenanceへ戻れるようにする。

```text
Normalized comparison facet != source observation
```

単一numeric scoreへの強制変換はCore要件としない。

### 6. Decision basisになった可変入力はhistoricalに再構成可能にする

Capability ChoiceのDecisionが、特定のProvider state、release、binding、contract、mapping等へ依存する場合は、後から現在版へ差し替えず、必要に応じてExactArtifactBindingまたは同等の検証可能な参照で固定できるようにする。

すべての観測へexact bindingを義務付けず、Decisionの影響、可変性、再構成必要性に応じてProgressive Semantic Explicitnessを適用する。

### 7. Selective Disclosureを許容する

Providerが内部topologyや契約情報を全量開示できない場合でも、Capability判断に必要なObservation / Evidenceだけを共有できるようにする。

非開示情報が存在する場合は、単なるUnknownと区別できるよう`Withheld`相当の意味を保持する。

内部詳細を開示しないこと自体を、信頼不足やCapability不存在へ自動変換しない。

### 8. SOZAはProvider runtime authorityを取得しない

Capability Observationを読めることは、Providerを操作するAuthorityを持つことを意味しない。

```text
Observation access
  != Authorization
  != Action Intent
  != Provider Execution
```

SOZA DecisionからProvider実行へ進む場合は、それぞれのAuthorization / Policy / Provider境界を別途通る。

## Current realization

current repositoryでは、次がactual treeへ実体化されている。

- `soza.capability-observation/v1alpha1` Contract Definition
- machine-readable schema
- F1〜F7を含むContract fixture
- Contract conformance checker
- first semantic runtimeのCapability Observation read / validate path
- ADR-0024に基づくsynthetic Provider Adapter A / B

synthetic Provider Adapterでは、異なるProvider-specific input schemaから同じCapability Observation境界へmappingし、次をExecutable Evidenceとして確認している。

- Provider identityとProvider-specific target referenceを保持できる。
- unit / status mappingのProvenanceを保持できる。
- source state referenceを保持できる。
- missing値を`false`や`0`へ捏造せず`unknown`として残せる。
- Provider固有の入力field setをUniversal Capability Observation field setへ昇格させない。
- Adapter outputをDecision / Authority / Executionへ自動昇格させない。

これはsynthetic Providerによるfixture-scoped Executable Evidenceであり、TEIやSaaS等のProduction Provider integration、Release Evidence、Operational Evidenceを意味しない。

## Consequences

### Positive

- Provider固有SchemaをSOZA Coreへ持ち込まず、Capability判断に必要な情報を扱える。
- TEI、SaaS、人間、AI等を同じ意味境界へ接続しやすい。
- Provider固有のUnknownや部分状態を失いにくい。
- Adapterの解釈変更後も過去Decisionを再構成しやすい。
- Selective DisclosureとProvider Independenceを両立しやすい。

### Costs

- ProviderごとにAdapter / Profile / Mappingの設計が必要になる。
- 比較Projectionではsource Observationとnormalized facetを組み合わせる必要がある。
- mapping自体のversion / Provenanceを管理する場面が生じる。

## Revisit conditions

次の場合に再検討する。

- 複数の異なるProviderで、現在のObservation envelopeでは表現できない同一の意味が繰り返し現れる。
- Adapter / Mapping境界ではhistorical reconstructionが実務上成立しない。
- Provider-neutral comparisonのためにUniversal Coreで共有すべき最小property vocabularyが、実際のScenarioから十分に収束する。

一つのProviderだけの都合を、Universal Core拡張の十分な理由にはしない。

## Natural Japanese review

current Capability Observation Contract、Contract fixture、Semantic Runtime、ADR-0024、synthetic Provider Adapter Evidenceへ戻ってDecisionを照合した。その後、未実体化時点のFollow-up記述をCurrent realizationへ置き換え、Provider state / interpretation / Decision / Authority / Executionの意味差を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後にEvidence強度を含めて意味監査を実施済みである。
