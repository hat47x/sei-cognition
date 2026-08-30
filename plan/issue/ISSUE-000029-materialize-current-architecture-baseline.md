# ISSUE-000029: current SOZA Reference Architectureをactual repositoryへ実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

ADR-0021に従い、current Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0021から、current SOZA Reference Architectureをactual repositoryへ実体化する。

historical M48 / M49 / M50 Architectureの意味核を再評価するが、Milestone identity、field set、package layout、algorithm、Evidence stateをcurrent正本へ自動継承しない。

## Resolution

current Architecture Design baselineとして、actual repositoryへ次を実体化した。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

Reference Architectureでは、次の主要なarchitecture concernをcurrent Product / Requirements / ADRから再構成している。

- Durable Semantic Core
- Inquiry / Epistemic State
- Cognitive Method
- Decision Memory
- Capability Definition / Observation / Choice
- Responsibility / Authority boundary
- Semantic Reference / Revision / Exact Binding
- Profile / Policy
- Federation / Selective Disclosure
- Provider / Adapter
- Projection
- Persistence
- Evidence / Assurance boundary

これらを一対一のruntime componentとして固定しない。

historical candidateの採用・統合・非採用は`architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`から追跡できる。

## Acceptance

### Semantic / Design Acceptance

- [x] current architecture canonical filesがactual treeに存在する。
- [x] REQ-0001〜REQ-0022をarchitecture concernへ追跡できる入口がある。
- [x] ADR-0001〜ADR-0021の主要境界と矛盾しないcurrent viewがある。
- [x] Milestone identityをcurrent architectureへ埋め込んでいない。
- [x] architecture concernとruntime componentを同一視していない。
- [x] historical candidateの採用・統合・非採用をmappingから追える。
- [x] Contractへ落とす必要がある境界とArchitecture説明に留める境界を区別できる。
- [x] 全文を自然な日本語で再ドラフトし、最終意味監査を行っている。

### Executable Acceptance

本Issueでは要求しない。

Architecture文書がactual treeに存在することはDesign Evidenceであり、runtime implementationやExecutable Acceptanceを意味しない。

```text
Architecture baseline exists != Runtime conformance PASS
```

## Follow-up

- ISSUE-000030 — current Contract baselineの実体化
- ISSUE-000022 — repository baseline全体のmaterialization

## Reopen conditions

- current Requirements / Accepted ADRの重要な変更でReference Architectureが不整合になる。
- actual implementationから、現在のArchitecture concern分離では意味を保てない反証が得られる。
- Product ValueからArchitectureまでのtraceabilityが維持できなくなる。

## Natural Japanese review

actual Architecture tree、REQ-0001〜REQ-0022、ADR-0021、historical mappingを照合して完了条件を確認した後、Design EvidenceとExecutable Evidenceを混同せず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
