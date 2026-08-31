# ADR-0013: Capability Realization / OfferingをUniversal Coreへ追加しない

Status: **Accepted**  
Related Issues: **ISSUE-000014, ISSUE-000020, ISSUE-000035, ISSUE-000036**  
Updated: 2026-08-31

## Context

ADR-0012では、Capability DefinitionとProvider identityを分離した。

```text
Capability != Provider
```

実際にCapabilityを提供する形には、Plugin、Provider Binding、external process、SaaS、人間作業、Database Provider等、Providerごとに異なる構造が現れる。

一方で、これらをすべてSOZA共通の`CapabilityRealization`へ統一しなければ意味を保てない、というEvidenceは得られていない。

Cognitive MethodではDefinition / Realizationを分離する意味があるが、あるdomainで有効な構造を類推だけでCapabilityへ一般化すると、Provider固有のdeployment、contract、offer、session、pricing等をUniversal Coreへ引き込みやすい。

## Decision

### 1. Universal `CapabilityRealization`を現時点では追加しない

SOZA Coreでは、Capability DefinitionとProvider / Provider-specific contextを分離したまま扱う。

必要な場合は、Capabilityを提供する具体的な条件や状態を、Provider / Profile側のArtifact、reference、Observation等として表す。

```text
Capability Definition
    != Provider
    != Provider-specific Offering / Binding / Deployment
```

### 2. Capabilityの意味をProviderへ埋め込まない

Providerが変わってもCapability Definitionのlogical identityを維持できることを優先する。

Provider固有のversion、availability、cost、latency、deployment、contract等を、Capability Definitionそのものへ書き込まない。

### 3. Provider固有のOfferingをUniversal ontologyへ昇格させない

SaaSの契約プラン、TEI Plugin、human service、external organizationの提供条件等は、具体的な形が大きく異なる。

共通して扱いたい情報があっても、まずProfile / Provider boundaryで表現する。複数の異質なProviderで同じ意味が繰り返し必要になることを確認する前に、Universal typeは作らない。

### 4. Observationは必要に応じてProvider contextを持てる

「このCapabilityが現在利用可能か」と、「このProviderによるこの提供形態が現在利用可能か」は同じではない。

Provider-specificなavailability、cost、latency等をCapability Definitionへ混ぜないため、Capability Observationは必要に応じてProvider referenceやProvider-specific target referenceを持てるようにする。

### 5. Federationの`Offer`とCapability Offeringを自動統合しない

Federation Profileの`Offer`は、主体間の協調・交換に関する意味を持つ。

Capability提供のcommercial / deployment / provider-specific Offeringとは目的が異なるため、同じ語を使えるという理由だけで、一つのUniversal Artifactへ統合しない。

### 6. Cognitive MethodのRealization構造をそのままコピーしない

Cognitive MethodのDefinition / Realization分離は、そのdomainで必要な意味境界として維持する。

Capabilityにも同じ構造が必要になった場合は、Capability側の具体的なScenarioとEvidenceから独立に判断する。

## Current realization

current `soza.capability-observation/v1alpha1`では、ObservationのtargetとしてCapability referenceに加え、必要に応じてProvider referenceとProvider-specific target referenceを保持できる。

また、synthetic Provider Adapter sliceでは、Provider A / Bの異なる入力SchemaをUniversal `CapabilityRealization`へ変換せず、それぞれのAdapterから同じCapability Observation境界へmappingできることを確認している。

```text
Provider-specific state
  → Adapter / Mapping
  → Capability Observation

!= Universal CapabilityRealization
```

このExecutable Evidenceは、Universal Realization型を作らなくてもProvider固有stateとCapability意味を分離できることを支持する。ただし、将来すべてのProviderでRealization identityが不要であると証明したものではない。

## Revisit conditions

次のうち複数が、異なるProvider種別をまたぐ実際のScenarioで繰り返し確認された場合は、本ADRを再検討する。

- realization自体にstable logical identityが必要になる。
- realizationのsemantic revisionをCapability Definitionと独立して追跡する必要がある。
- 同じrealizationを複数Providerへ再bindする必要がある。
- realization単位のObservation / Assurance / Responsibilityが必要になる。
- Provider contractやdeployment instanceでは表現できない意味が繰り返し残る。
- 人間、SaaS、TEI等をまたいで共通のrealization意味が実務上必要になる。

一つの製品や一つのProviderだけで必要になったことを、Universal Core化の十分な根拠にはしない。

## Consequences

### Positive

- Capability CoreをProvider実装詳細から独立させやすい。
- TEI、SaaS、人間、外部組織等を同じCapability判断面へ置きやすい。
- 別domainのDefinition / Realization構造を不用意に一般化せずに済む。
- Provider / Profile側で実務上必要なOffering情報を表現できる余地を保てる。

### Costs

- Provider-specific状態を比較するProjectionでは、Capability DefinitionとProvider contextを組み合わせる必要がある。
- 将来、独立したRealization identityが必要になった場合は、新しいADRとmigrationが必要になる可能性がある。

## Natural Japanese review

current Capability Observation Contract、ADR-0024、synthetic Provider AdapterのExecutable Evidenceへ戻ってDecisionを照合した。その後、検討手法や特定実装系列をDecisionの正本にせず、Universal CapabilityRealizationを追加しない理由と再検討条件をcurrent Evidenceに基づいて整理した。意味を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
