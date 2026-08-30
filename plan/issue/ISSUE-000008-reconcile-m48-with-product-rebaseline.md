# ISSUE-000008: M48をProduct Rebaselineと整合させる

Status: **Resolved — semantic reconciliation complete; repository materialization separated**  
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

ただし、現在のGitHub repositoryには旧candidate bundleが参照していたruntime、contracts、fixtures、tools等の全ファイルがまだ揃っていない。この不足を本Issueの再open理由にはせず、**ISSUE-000022**でrepository baseline materializationとして独立追跡する。

このResolutionはM48 production implementation、M47 regression、release、operational evidenceの完了を意味しない。

## Natural Japanese review

旧blockerと現在のrepository状態を分離した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
