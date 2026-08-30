# ISSUE-000029: current SOZA Reference Architectureをactual repositoryへ実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

ADR-0021に従い、current Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0021から、current SOZA Reference Architectureをactual repositoryへ実体化する。

historical M48 / M49 / M50 Architectureの意味核を再評価するが、Milestone identity、field set、package layout、algorithm、Evidence stateをcurrent正本へ自動継承しない。

## Resolution

### 1. current Architecture canonical filesを実体化した

actual repositoryへ次を追加した。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

### 2. Milestoneから意味構造へ再編した

historical M48 / M49 / M50で分かれていた設計を、current Architectureでは次のarchitecture concernとして統合した。

1. Durable Semantic Core
2. Inquiry / Epistemic State
3. Cognitive Method
4. Decision Memory
5. Capability Understanding / Choice
6. Responsibility / Authority boundary
7. Semantic Reference / Revision / Exact Binding
8. Profile / Policy
9. Federation / Selective Disclosure
10. Provider / Adapter
11. Projection
12. Persistence
13. Evidence / Assurance boundary

これらを固定runtime componentとして扱っていない。

### 3. historical意味核を再利用した

主に次をcurrent Architectureへ統合した。

- Coreは実現手段が変わっても残すべき意味差へ限定する。
- Unknown != No、Conflict != latest-wins。
- Recommendation != Decision != Authority != Execution。
- Decision creation != uncertainty resolution。
- Pattern != Cognitive Method。
- Method Application != Assurance。
- Capability Definition != Observation != Matching != Decision != Provider != Authority != Execution。
- logical identity != exact historical binding != semantic revision != storage revision。
- Progressive ExplicitnessはProfile / Policyで扱う。
- Federationはoptional Profileであり、全world model統合を要求しない。
- Storage / transport / crypto / queue / retry等のmechanicsをUniversal Coreへ持ち込まない。

### 4. 後発ADRを反映した

historical candidate以降に確定した次をcurrent Architectureへ追加・強化した。

- SOZA / TEI Product Boundary。
- Provider-neutral Capability Observation。
- Provider state != Capability interpretation != Decision。
- adapter / mapping provenance。
- Product Value V1〜V8からArchitectureまでのtraceability。
- human-readable Contract DefinitionとRepresentation Profileの分離。
- Design / Executable / Release / Operational Evidenceの分離。

### 5. REQ-0001〜REQ-0022のArchitecture追跡を確認した

`architecture/TRACEABILITY.md`で、全current Requirementが少なくとも一つのarchitecture concernへ追跡できることを確認した。

これはimplementation可能性の証明ではなく、Design baseline上でRequirementが脱落していないことの確認である。

### 6. historical mappingを保存した

`architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`で、主要historical Architectureについて、

- Integrated
- Split
- Partially integrated
- Historical evidence only
- Contract / Representation candidate

を区別した。

old Milestone、field set、package、algorithm、local PASSはcurrentへ自動継承していない。

## Acceptance

### Semantic / Design Acceptance

- [x] current architecture canonical filesがactual treeに存在する。
- [x] REQ-0001〜0022が少なくとも一つのarchitecture concernへ追跡できる。
- [x] ADR-0001〜0021の主要境界と矛盾しない。
- [x] Milestone identityをcurrent architectureへ埋め込んでいない。
- [x] architecture concernとruntime componentを同一視していない。
- [x] historical candidateの採用・統合・非採用をmappingから追える。
- [x] Contractへ落とす必要がある境界とArchitecture説明に留める境界を区別できる。
- [x] 全文を自然な日本語で再ドラフトし、最終意味監査を行った。

### Executable Acceptance

本Issueでは要求しない。

Architecture文書が存在することをruntime implementation、schema conformance、release、operational evidenceへ昇格させていない。

## Evidence state at closure

- Architecture Design Baseline: **Satisfied**
- Architecture → Contract: **Partially Satisfied** — ISSUE-000030
- Executable Architecture / Runtime Evidence: **Not Yet Verified**
- Release / Operational: **Not Yet Verified**

## Follow-up

- ISSUE-000030 — current Contract baseline
- ISSUE-000027 — Requirements registry checker
- ISSUE-000024 — Capability Observation fixture
- ISSUE-000009 — portable exact binding verification
- ISSUE-000022 — repository baseline全体

## Natural Japanese review

actual Architecture 4文書とREQ / ADR traceabilityを一件ずつ戻り照合し、Design baselineとContract / Executable未完了範囲を分離した。その後、意味、規範強度、Evidence状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
