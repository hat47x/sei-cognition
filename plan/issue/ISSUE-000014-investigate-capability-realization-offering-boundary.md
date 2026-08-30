# ISSUE-000014: Capability Realization / Offeringの境界を調査する

Status: **Resolved**  
Priority: **5**  
Related ADRs: **ADR-0012, ADR-0013**  
Updated: 2026-08-31

## Goal

Capability DefinitionとProviderの間に、SOZA共通の`CapabilityRealization`または`CapabilityOffering`を置く必要があるかを判断する。

## Background

ADR-0012でCapabilityとProviderを分離した後、次の問題が残っていた。

- 同じCapabilityを複数Providerが実現できる。
- Providerごとにavailability、cost、latency、deployment等が異なる。
- M47 Cognitive MethodにはDefinition / Realization分離がある。
- Federationにも`Offer`という概念がある。

これらを一つのUniversal Artifactへまとめるべきかは、当初のEvidenceだけでは判断できなかった。

## Investigation

TEI設計系列と現行実装をラウンドKJ法で再検討した。

確認できたのは、Provider固有の実現形が多様であり、Plugin、Provider Binding、external process、SaaS、人間作業等を一つの共通Realization型へ統一しなくても、CapabilityとProviderを分離したまま表現できることである。

また、現時点でUniversal Realization identityを必要とする反復Scenarioは不足している。

## Resolution

ADR-0013で、**Universal `CapabilityRealization` / `CapabilityOffering`を現時点ではSOZA Coreへ追加しない**と決定した。

Provider固有のOffering、deployment、contract、availability等はProvider / Profile側で扱い、Capability Definitionへ混ぜない。

## Reopen conditions

ADR-0013に定めた複数の再検討条件が、異なるProvider種別をまたぐactual scenarioで確認された場合に再開する。

単一Provider固有の都合だけでは再開しない。

## Result

- new Universal type: **追加しない**
- ADR: **ADR-0013 Accepted**
- implementation: **未開始**
- schema: **未固定**
- future review: **条件付き**

## Natural Japanese review

調査内容と結論を確定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
