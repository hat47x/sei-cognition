# ISSUE-000029: current SEI Reference Architectureをactual repositoryへ実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

ADR-0021に従い、current Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、Accepted ADRからcurrent SEI Reference Architectureをactual repositoryへ実体化する。

historical M48 / M49 / M50 Architectureの意味核を再評価するが、Milestone identity、field set、package layout、algorithm、Evidence stateをcurrent正本へ自動継承しない。

## Resolution

### 1. current Architecture canonical filesを実体化した

```text
architecture/
  README.md
  SEI_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

### 2. Milestoneから意味構造へ再編した

historical M48 / M49 / M50で分かれていた設計を、Durable Semantic Core、Inquiry / Epistemic State、Cognitive Method、Decision Memory、Capability、Responsibility / Authority、Semantic Reference / Exact Binding、Profile / Policy、Federation、Provider / Adapter、Projection、Persistence、Evidence / Assurance等のarchitecture concernへ統合した。

これらを固定runtime componentとして扱わない。

### 3. historical意味核と後発ADRをcurrent Architectureへ統合した

Unknown / Conflict、Recommendation / Decision / Authority / Execution、Decisionとuncertainty、Pattern / Cognitive Method、Capability Definition / Observation / Matching / Decision / Provider、logical identity / exact binding / semantic revision / storage revision等の意味差をcurrent構造へ反映した。

あわせてSEI / TEI Product Boundary、Provider-neutral Capability Observation、adapter / mapping provenance、V1〜V8 traceability、Contract / Representation Profile、Evidence階層を追加・強化した。

### 4. REQ-0001〜REQ-0022のArchitecture追跡を確認した

`architecture/TRACEABILITY.md`で、全current Requirementが少なくとも一つのarchitecture concernへ追跡できることを確認した。

これはimplementation可能性の証明ではなく、Design baseline上でRequirementが脱落していないことの確認である。

### 5. historical mappingを保存した

`architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`で主要historical ArchitectureをIntegrated / Split / Partially integrated / Historical evidence only / Contract or Representation candidate等へ分類した。

old Milestone、field set、package、algorithm、local PASSはcurrentへ自動継承していない。

## Acceptance

- [x] current Architecture canonical filesがactual treeに存在する。
- [x] REQ-0001〜0022が少なくとも一つのarchitecture concernへ追跡できる。
- [x] Accepted ADRの主要境界と矛盾しない。
- [x] Milestone identityをcurrent Architectureへ埋め込んでいない。
- [x] architecture concernとruntime componentを同一視していない。
- [x] historical candidateの採用・統合・非採用をmappingから追える。
- [x] Contractへ落とす境界とArchitecture説明に留める境界を区別できる。
- [x] 全文を自然な日本語で再ドラフトし、最終意味監査を行った。

## Current evidence state

- Architecture Design Baseline: **Satisfied**
- Architecture → Contract traceability: **Satisfied — ISSUE-000030**
- Contract / Fixture conformance: **Satisfied within ISSUE-000031 scope**
- first semantic runtime: **Satisfied within ISSUE-000033 scope**
- synthetic Provider Adapter: **Satisfied within ISSUE-000036 scope**
- full Requirement implementation coverage: **Not Yet Verified**
- Release / Operational: **Not Yet Verified**

Architecture文書自体がExecutable Evidenceなのではない。後続Contract / Runtimeがcurrent Architectureと整合する範囲をactual CIで確認できるようになった、という位置づけである。

## Follow-up

- ISSUE-000030 — current Contract baseline（Resolved）
- ISSUE-000031 — Contract conformance（Resolved）
- ISSUE-000033 — first semantic runtime（Resolved）
- ISSUE-000036 — synthetic Provider Adapter（Resolved）
- ISSUE-000034 — historical M47 digest recovery（Blocked）
- ISSUE-000015 — 全開発文書監査

## Natural Japanese review

current Architecture 4文書、REQ / ADR traceability、後続Contract / Runtime / Provider Adapter Evidenceへ戻って再照合した。Design baselineと後続Executable Evidenceを同一視せず、意味、規範強度、Evidence状態を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
