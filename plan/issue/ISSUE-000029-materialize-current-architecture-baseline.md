# ISSUE-000029: current SOZA Reference Architectureをactual repositoryへ実体化する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

ADR-0021に従い、current Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0021から、current SOZA Reference Architectureをactual repositoryへ実体化する。

historical M48 / M49 / M50 Architectureの意味核を再評価するが、Milestone identity、field set、package layout、algorithm、Evidence stateをcurrent正本へ自動継承しない。

## Required outputs

初期Design baseline:

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

## Required architecture concerns

少なくとも次をcurrent viewで整理する。

1. Durable Semantic Core
2. Inquiry / Epistemic State
3. Cognitive Method
4. Decision Memory
5. Capability Definition / Observation / Choice
6. Responsibility / Authority boundary
7. Semantic Reference / Revision / Exact Binding
8. Profile / Policy
9. Federation / Selective Disclosure
10. Provider / Adapter
11. Projection
12. Persistence
13. Evidence / Assurance boundary

これらを一対一のruntime componentとして固定しない。

## Historical inputs

優先的に再評価する旧文書:

- `CORE_BOUNDARY_REVIEW_v1.md`
- `REVISION_SUPERSESSION_SEMANTICS_v1.md`
- `SEMANTIC_PERSISTENCE_CONTRACT_v1.md`
- `EXACT_BINDING_VERIFICATION_BOUNDARY_v1.md`
- `BINDING_VERIFICATION_OUTCOME_v1.md`
- `CLAIM_INTERPRETATION_BOUNDARY_v1.md`
- `PROGRESSIVE_SEMANTIC_EXPLICITNESS_v1.md`
- `BOUNDED_SUBJECT_RESPONSIBILITY_v1.md`
- `BOUNDED_FEDERATION_PROFILE_v1.md`
- `M49_DECISION_MEMORY_BOUNDARY_v1.md`
- `M49_DECISION_REFERENCE_ROLES_v1.md`
- `M50_CAPABILITY_CHOICE_BOUNDARY_v1.md`
- `M50_CAPABILITY_REALIZATION_OPTIONS_v1.md`

## Required decisions already fixed by ADR

Architectureは次を再決定しない。

- Universal Claimを便宜で追加しない。
- Global Principal ontologyを追加しない。
- ResponsibilityからAuthorityを推定しない。
- Capability != Provider。
- Matching != Decision != Authority != Execution。
- Recommendation != Decision != Authority != Action Intent != Execution。
- Provider-specific realizationをUniversal CapabilityRealizationへ統合しない。
- TEI内部SchemaをSOZA Coreへコピーしない。
- Pattern != Cognitive Method。
- Method Application != Assurance。
- logical refとexact historical bindingを分ける。
- binding verificationの`not_verified`と`failed`を分ける。
- Progressive Semantic ExplicitnessをProfile / Policy駆動とする。

新しい判断が必要ならIssue / ADRへ戻す。

## Acceptance

### Semantic / Design Acceptance

- [ ] current architecture canonical filesがactual treeに存在する。
- [ ] REQ-0001〜0022が少なくとも一つのarchitecture concernへ追跡できる。
- [ ] ADR-0001〜0021の主要境界と矛盾しない。
- [ ] Milestone identityをcurrent architectureへ埋め込んでいない。
- [ ] architecture concernとruntime componentを同一視していない。
- [ ] historical candidateの採用・統合・非採用をmappingから追える。
- [ ] Contractへ落とす必要がある境界とArchitecture説明に留める境界を区別できる。
- [ ] 全文を自然な日本語で再ドラフトし、最終意味監査を行っている。

### Executable Acceptance

本Issueでは要求しない。Architecture文書が存在することをruntime implementationのEvidenceとしない。

## Dependencies

- ADR-0021
- ISSUE-000022
- ISSUE-000026

## Natural Japanese review

current / historical / architecture / runtimeの境界を混同しないよう作業条件を整理した後、意味とEvidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。完了時に再度、最終意味監査を行う。
