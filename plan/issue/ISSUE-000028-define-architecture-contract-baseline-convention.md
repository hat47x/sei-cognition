# ISSUE-000028: current Architecture / Contracts基線の正本・責務・版管理規約を定める

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

current `requirements/`の次段として、`architecture/`と`contracts/`をactual repositoryへ実体化する前に、それぞれが何を正本とし、ADR / Requirement / Implementationとどう責務を分けるかを定める。

historical candidateのArchitecture / Contractを無検査で復元せず、current REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0020から再導出できる規約を作る。

## Historical inputs

Library上のhistorical candidateには、たとえば次が存在する。

### Architecture

- `CORE_BOUNDARY_REVIEW_v1.md`
- `SEMANTIC_PERSISTENCE_CONTRACT_v1.md`
- `REVISION_SUPERSESSION_SEMANTICS_v1.md`
- `CLAIM_INTERPRETATION_BOUNDARY_v1.md`
- `PROGRESSIVE_SEMANTIC_EXPLICITNESS_v1.md`
- `BOUNDED_SUBJECT_RESPONSIBILITY_v1.md`
- `BOUNDED_FEDERATION_PROFILE_v1.md`
- `M49_DECISION_MEMORY_BOUNDARY_v1.md`
- `M50_CAPABILITY_CHOICE_BOUNDARY_v1.md`
- その他M48〜M50 planning / implementation review

### Contracts

- `INQUIRY_EPISTEMIC_ARTIFACTS_v1.md`
- `M47_M48_COMPATIBILITY_PORT_v1.md`
- `SEMANTIC_PORTABLE_BUNDLE_v1.md`
- `PORTABLE_EXACT_BINDING_REPRESENTATION_v1alpha1.md`
- representation profile候補
- semantic interchange schema候補

これらにはcurrent Product Valueと整合する意味核が多くある一方、Milestone名、当時の型候補、JCS / Go等の実装選択、old evidence stateも混在する。

## Questions

1. Architecture文書は何を正本とし、ADRとどう分けるか。
2. Architectureにstable IDを付けるか、名前付きcurrent viewとして扱うか。
3. Contractはどの条件で新設するか。
4. Contractのlogical identityとversionをどう管理するか。
5. Markdown contractとmachine-readable schemaのどちらを意味上の正本とするか。
6. representation-only changeとsemantic breaking changeをどう分けるか。
7. M48 / M49 / M50等のhistorical milestone文書をcurrent architectureへどう移すか。
8. Core / Profile / Provider / Adapter / Projectionの配置をどこまでArchitectureで固定するか。
9. Product Value V1〜V8 → REQ → ADR → Architecture / Contractの追跡をどう残すか。
10. Design EvidenceとExecutable Contract conformanceをどう分けるか。

## Constraints

- ArchitectureをADRの代替Decision logにしない。
- Contractを設計思想の説明文書に肥大化させない。
- current canonical filenameへM48 / M49 / M50等のMilestone identityを埋め込まない。
- historical schema / package / field名をcurrent正本へ自動継承しない。
- JCS、SHA-256、Go、JSON等の現実装候補を、Product Value上不可欠という理由なしにUniversal meaningへ昇格させない。
- Architecture documentの存在をExecutable Evidenceとしない。
- Contract schemaの存在をruntime conformance PASSとしない。
- current Design baseline作成後、必ず自然な日本語全文再ドラフトと最終意味監査を行う。

## Required deliverables

- Architecture / Contract responsibility boundary
- current canonical directory layout
- Architecture current viewの更新規則
- Contract logical identity / versioning rule
- Markdown normative semantics / machine-readable schemaの権威関係
- historical candidate adoption rule
- Product Value / REQ / ADR traceability rule
- Design / Executable Evidence separation
- ADR

## Acceptance

### Semantic / Design Acceptance

- [ ] ArchitectureとADRの責務境界が決まっている。
- [ ] ArchitectureとContractの責務境界が決まっている。
- [ ] Contract identity / version ruleが決まっている。
- [ ] machine-readable schemaの権威関係が決まっている。
- [ ] historical candidateの再利用規則が決まっている。
- [ ] milestone identityをcurrent正本へ持ち込まない規則が決まっている。
- [ ] V1〜V8からArchitecture / Contractまで追跡できる規則が決まっている。
- [ ] Evidence階層を混同しない規則が決まっている。
- [ ] 自然な日本語全文再ドラフトと最終意味監査が完了している。

### Executable Acceptance

本Issueでは要求しない。current Architecture / Contractsの実体化とconformance toolは後続Issueへ分離する。

## Dependencies

- ADR-0018
- ADR-0020
- ISSUE-000022
- ISSUE-000026

## Natural Japanese review

historical candidateとcurrent Product / Requirements / ADRの境界を整理した後、未決事項を勝手に確定せず、自然な日本語となることを最重要視して全文を再ドラフトした。ADR確定時に再度、最終意味監査を行う。
