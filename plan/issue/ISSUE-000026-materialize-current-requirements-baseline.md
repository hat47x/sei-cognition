# ISSUE-000026: current Product Requirements / Acceptance Scenariosをactual repositoryへ実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

ADR-0020に従い、current Product Valueから再導出したProduct RequirementsとAcceptance Scenariosを`requirements/`へ実体化する。

historical candidateの意味核は再利用するが、旧ID、Milestone構造、Evidence状態をそのままcurrent baselineへ継承しない。

## Resolution

### 1. current canonical filesを実体化した

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  history/
    HISTORICAL_REQUIREMENT_MAPPING.md
```

### 2. Product RequirementをREQ-0001〜REQ-0022へ再構成した

旧18 Product Requirements＋10 NFRという件数を保存せず、重複を統合し、後発のProduct Value / ADRで明確になった意味境界を追加した。

22という件数自体を将来の制約にはしない。

Moving Future Horizonは利用者世界のRequirementではなく設計評価規則と判断し、REQへ残さずADR-0001 / Product Principlesへ置いた。

### 3. Acceptance ScenarioをSCN-0001〜SCN-0017へ再構成した

historical Scenarioの意味核を移しつつ、Recommendation → Decision → Authority → Execution、exact historical binding、Provider partial degradation、Selective Disclosure、simple UI / canonical meaning、Execution Provider replacement、Pattern / Cognitive Method separation、residual / reopen、Evidence claim height等の後発境界を追加した。

### 4. historical mappingを独立保存した

`requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`で、旧PR / NFR / ASからcurrent REQ / SCNへの統合・分離・上位移管を記録した。

旧IDをcurrent identityとして再利用していない。

### 5. historical Evidenceをcurrentへ継承していない

historical candidateの`direct`、`partial`、`design_only`、local PASS等はcurrent actual repositoryのEvidenceへ自動変換していない。

その後、current actual Evidenceが増えるたびに`requirements/PRODUCT_REQUIREMENTS.md`を再基線化し、Design / Executable / Release / Operationalを分離したまま更新している。

## Acceptance

### Semantic / Design Acceptance

- [x] current REQがProduct Value V1〜V8またはProduct Principleへ追跡できる。
- [x] historical requirementの意味核とcurrent REQの対応を追える。
- [x] old Evidence stateをcurrentへ自動継承していない。
- [x] RequirementとADRの責務が混ざっていない。
- [x] Milestone名がREQ identityへ入っていない。
- [x] SCNがREQと独立IDになっている。
- [x] ADR-0019を含む後発境界をScenarioへ反映している。
- [x] 全current Requirements文書を自然な日本語で再ドラフトし、最終意味監査を行った。

### Executable Acceptance

ISSUE-000027でRequirements Registry checker、negative self-test、GitHub Actionsを実装し、current REQ / SCNの構造整合をactual repositoryで再現した。

GitHub Actions `Requirements Registry Conformance`では22 Requirements / 17 Scenariosのregistry checkがsuccessしている。

ただし、このPASSはRequirementの意味内容や実装coverageを証明しない。

## Current evidence state

- Requirements Design Baseline: **Satisfied**
- Requirements Registry Structural Executable Evidence: **Satisfied — ISSUE-000027**
- RequirementごとのExecutable implementation coverage: **current `PRODUCT_REQUIREMENTS.md`で保守的に個別管理**
- Release Acceptance: **Not Yet Verified**
- Operational Acceptance: **Not Yet Verified**

```text
Registry PASS
  != all Requirements implemented
```

## Dependencies / Follow-up

- ADR-0020
- ISSUE-000027 — Requirements Registry checker（Resolved）
- ISSUE-000022 — repository baseline（Resolved）
- ISSUE-000015 — 全開発文書の自然な日本語監査

## Natural Japanese review

current REQ / SCN / historical mapping、Requirements Registry checker、GitHub Actions、再基線化済み`PRODUCT_REQUIREMENTS.md`へ戻ってAcceptanceを再照合した。その後、Design baseline、registry構造Evidence、Requirement実装coverageを分離し、意味、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
