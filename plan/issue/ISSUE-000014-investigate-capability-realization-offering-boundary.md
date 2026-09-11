# ISSUE-000014: Capability Realization / Offeringの境界を調査する

Status: **Resolved**  
Priority: **5**  
Related ADRs: **ADR-0012, ADR-0013**  
Updated: 2026-08-31

## Goal

Capability DefinitionとProviderの間に、SEI共通の`CapabilityRealization`または`CapabilityOffering`を置く必要があるかを判断する。

## Background

ADR-0012でCapabilityとProviderを分離した後、次の問題が残っていた。

- 同じCapabilityを複数Providerが実現できる。
- Providerごとにavailability、cost、latency、deployment等が異なる。
- historical M47 Cognitive MethodにはDefinition / Realization分離がある。
- Federationにも`Offer`という概念がある。

これらを一つのUniversal Artifactへまとめるべきかは、当初のEvidenceだけでは判断できなかった。

## Investigation

TEI設計系列と実装をラウンドKJ法で再検討した。

Provider固有の実現形はPlugin、Provider Binding、external process、SaaS、人間作業等と多様であり、一つの共通Realization型へ統一しなくてもCapabilityとProviderを分離したまま表現できると判断した。

また、Universal Realization identityを必要とする反復Scenarioも不足していた。

## Resolution

ADR-0013で、**Universal `CapabilityRealization` / `CapabilityOffering`を現時点ではSEI Coreへ追加しない**と決定した。

Provider固有のOffering、deployment、contract、availability等はProvider / Profile側で扱い、Capability Definitionへ混ぜない。

この判断はcurrent Capability Observation / Provider Adapter設計とも整合する。ISSUE-000036では異なるProvider-specific input shapeから同じCapability Observation Contractへmappingでき、Universal Realization型を追加せずにProvider-neutralな比較材料を作れることをsynthetic sliceで確認した。

ただし、synthetic Adapter PASSはproduction Provider間の実運用成立性を証明しない。

## Reopen conditions

ADR-0013に定めた複数の再検討条件が、異なるProvider種別をまたぐactual scenarioで確認された場合に再開する。

単一Provider固有の都合だけでは再開しない。

## Current result

- Universal `CapabilityRealization` / `CapabilityOffering`: **追加しない**
- ADR-0013: **Accepted**
- Provider-neutral Capability Observation: **実体化済み**
- synthetic Provider Adapter: **Executable Evidenceあり**
- Universal Realization schema: **意図的に作成していない**
- production multi-Provider interoperability: **Not Yet Verified**
- future review: **条件付き**

「implementation未開始」や「schema未固定」は、Universal Realization型を将来必ず実装するという意味ではない。現時点では、そもそもUniversal型を導入しないことがDecisionである。

## Natural Japanese review

ADR-0013、Capability Observation Contract、ADR-0024、synthetic Provider Adapter実装・CIへ戻って内容を照合した。その後、「型を実装していない」ことと「型を不要と判断した」ことを区別し、意味・再検討条件・Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
