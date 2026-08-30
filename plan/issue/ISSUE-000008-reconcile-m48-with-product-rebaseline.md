# ISSUE-000008: M48をProduct Rebaselineと整合させる

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0002, ADR-0003, ADR-0004, ADR-0005, ADR-0007, ADR-0008, ADR-0009**  
Updated: 2026-08-31

## Goal

旧M48 feasibility設計をProduct Value / Requirements / Accepted ADRへ戻して再評価し、現在依存の実装都合をCoreへ残さず、保持すべき意味境界を再基線化する。

## Work completed

Planning / architecture段階では、少なくとも次を再整理した。

- Universal ClaimをCoreへ追加しない。
- Logical identity、Exact Binding、Semantic Lineage、storage revisionを分離する。
- BoundedSubjectRefとcontextual Responsibilityを採用する。
- Progressive Semantic ExplicitnessをProfile / Policyへ分ける。
- Semantic Persistenceをstorage-neutralにする。
- Exact BindingのRepresentation ContractとVerification Outcomeを分離する。
- private chain-of-thought、workflow state、provider executionをM48 Coreへ持ち込まない。

M47 Cognitive MethodのDefinition / Realization / Application境界も、歴史的な参照基線として維持する。

## Resolution

M48をProduct Rebaselineへ**意味上整合させる作業**は、Accepted ADRとreference architectureへ分解できたためResolvedとする。

当初のblockerだった「actual `soza` repositoryが存在しない」は、2026-08-31時点では解消している。

ただし、current Architecture / Requirementsがactual repositoryへ実体化されても、runtime、contracts、fixtures、tools等の全層が揃ったことにはならない。残件はISSUE-000022、ISSUE-000009、ISSUE-000030等で独立追跡する。

このResolutionはM48 production implementation、M47 regression、release、operational evidenceの完了を意味しない。

## Follow-up boundary

- semantic reconciliation: **完了**
- repository materialization: **ISSUE-000022で継続**
- portable Exact Binding verification: **ISSUE-000009で継続**
- current Contract baseline: **ISSUE-000030で継続**
- production implementation / operational evidence: **未完了**

ResolvedというStatusは、semantic reconciliationが完了したことだけを表す。

## Natural Japanese review

旧blockerと現在のrepository状態を分離し、StatusとEvidenceの高さを別の意味として整理した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
