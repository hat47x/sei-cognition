# ISSUE-000008: historical M48をProduct Rebaselineと整合させる

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0002, ADR-0003, ADR-0004, ADR-0005, ADR-0007, ADR-0008, ADR-0009**  
Updated: 2026-08-31

## Goal

historical M48 feasibility設計をProduct Value / Requirements / Accepted ADRへ戻して再評価し、当時の実装都合をcurrent Coreへ固定せず、保持すべき意味境界を再基線化する。

ここでいうM48は設計史上のMilestone labelであり、current Architectureや実装フェーズの正本ではない。

## Work completed

少なくとも次をcurrent設計へ再統合した。

- Universal ClaimをCoreへ追加しない。
- Logical identity、Exact Binding、Semantic Lineage、storage revisionを分離する。
- Bounded Subjectとcontextual Responsibilityを採用する。
- Progressive Semantic ExplicitnessをProfile / Policyへ分ける。
- Semantic Persistenceをstorage-neutralにする。
- Exact BindingのSemantic Contract、Representation Profile、Verification Outcomeを分離する。
- private chain-of-thought、workflow state、Provider executionをDurable Semantic Coreへ持ち込まない。

historical M47 Cognitive MethodのDefinition / Realization / Application境界も、設計系譜として参照しつつcurrent Cognitive Method境界へ統合した。

## Resolution

historical M48をProduct Rebaselineへ**意味上整合させる作業**は、current Product Value、Requirements、Accepted ADR、Reference Architecture、Contractへ分解・再統合できたためResolvedとする。

当初のblockerだったactual `sei` repository不在は解消済みである。さらにISSUE-000022でcurrent repository baselineを実体化し、Product / Requirements / Architecture / Contracts / Fixtures / Representation Profiles / first Runtime / Toolsまでactual treeへ配置した。

したがって、旧文書にあった「runtime、contracts、fixtures、tools等がまだ揃っていない」という前提はcurrent状態では採用しない。

## Current evidence state

- Historical M48 semantic reconciliation: **Satisfied**
- Current repository baseline materialization: **Satisfied — ISSUE-000022**
- Contract / fixture-scoped Executable Evidence: **Satisfied within current scope**
- first semantic runtime Executable Evidence: **Satisfied within read / validate / reconstruct scope**
- historical M47 digest Profile mapping: **Not Yet Verified — ISSUE-000034**
- Release / Operational Evidence: **Not Yet Verified**

```text
historical M48 design reconciled
  != historical M48 implementation promoted as current
  != Release readiness
```

旧candidateのpackage、field、algorithm、local PASSはcurrentへ自動継承しない。current Evidenceはcurrent Contract / fixture / runtime / CIから取り直したものだけを用いる。

## Natural Japanese review

historical M48の意味核、current Product Value、Requirements、Architecture、Contract、ISSUE-000022のrepository baseline、current CI Evidenceへ戻って再照合した。その後、歴史的Milestoneとcurrent正本の境界、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
