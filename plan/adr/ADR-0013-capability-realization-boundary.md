# ADR-0013: Capability Realization / OfferingをUniversal Coreへ追加しない

Status: **Accepted**  
Related Issue: **ISSUE-000014**  
Updated: 2026-08-31

## Context

ADR-0012では、Capability DefinitionとProvider identityを分離した。

```text
Capability != Provider
```

その後、TEIの設計系列と現行実装をラウンドKJ法で再検討したところ、Capabilityを具体的に提供する方法には、Plugin、Provider Binding、external process、SaaS、人間作業、Database Provider等、Provider固有の形が繰り返し現れることを確認した。

一方、これらをすべてSOZA共通の`CapabilityRealization`へ統一しなければ意味を保てない、という証拠は現時点では得られていない。

M47 Cognitive MethodにはDefinition / Realizationの分離があるが、Methodで有効だった構造を類推だけでCapabilityへ一般化すると、Provider固有のdeployment、contract、offer、session、pricing等をUniversal Coreへ引き込みやすい。

## Decision

### 1. Universal `CapabilityRealization`を現時点では追加しない

SOZA Coreでは、Capability DefinitionとProvider / Provider-specific contextを分離したまま扱う。

必要な場合は、Capabilityを提供する具体的な条件や状態を、Provider / Profile側のArtifactまたはObservationとして表す。

```text
Capability Definition
    != Provider
    != Provider-specific Offering / Binding / Deployment
```

### 2. Capabilityの意味をProviderへ埋め込まない

Providerが変わってもCapability Definitionのlogical identityを維持できることを優先する。

Provider固有のversion、availability、cost、latency、deployment、contract等はCapability Definitionそのものへ書き込まない。

### 3. Provider固有のOfferingをUniversal ontologyへ昇格させない

SaaSの契約プラン、TEI Plugin、human service、external organizationの提供条件などは形が大きく異なる。

これらに共通する情報が必要な場合でも、まずProfile / Provider boundaryで扱う。共通性が反復して確認される前にUniversal typeを作らない。

### 4. Observationの対象粒度は必要に応じてProvider contextを持てる

「このCapabilityが現在利用可能か」と「このProviderによるこの提供形態が現在利用可能か」は異なる。

Provider-specific availability、cost、latency等をCapability Definitionへ混ぜないため、Observationは必要に応じてProviderまたはProvider-specific referenceを明示できる設計とする。

具体的なwire schemaはactual implementation時に決める。

### 5. Federationの`Offer`とCapability Offeringを自動統合しない

Federation Profileの`Offer`はprincipal間の協調意味を持つ。

Capability提供のcommercial / deployment / provider-specific Offeringとは目的が異なるため、同じ語が使えることだけを理由に一つのUniversal Artifactへ統合しない。

### 6. M47 Method Realizationをコピーしない

Cognitive MethodのDefinition / Realization分離はそのdomainで維持する。

Capabilityについて同じ形が必要になった場合は、Capability側の具体Scenarioから独立に再判断する。

## Revisit conditions

次のうち複数が、異なるProvider種別をまたぐactual scenarioで反復して確認された場合は、本ADRを再検討する。

- realization自体にstable logical identityが必要になる
- realizationのsemantic revisionをCapability Definitionと独立して追跡する必要がある
- 同じrealizationを複数Providerへ再bindする必要がある
- realization単位のObservation / Assurance / Responsibilityが必要になる
- Provider contractやdeployment instanceでは表現できない意味が繰り返し残る
- 人間、SaaS、TEI等をまたいで共通のrealization意味が実務上必要になる

一つの製品・一つのProviderだけで必要になったことを、Universal Core化の十分な根拠にはしない。

## Consequences

### Positive

- Capability CoreをProvider実装詳細から独立させやすい。
- TEI、SaaS、人間、外部組織等を同じCapability判断面へ置きやすい。
- M47のdomain固有構造を不用意に一般化しない。
- Provider / Profile側で実務的なOffering情報を自由に表現できる。

### Costs

- Provider-specific状態を比較するProjectionは、Capability DefinitionとProvider contextを組み立てる必要がある。
- 将来、独立Realization identityが必要になった場合は新しいADRとmigrationが必要になる可能性がある。

## Evidence

- ADR-0012 Capability Choice boundary
- ISSUE-000014の調査論点
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`
- TEI現行Plugin / Provider / Binding実装

## Natural Japanese review

内容・境界を確定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
