# ISSUE-000026: current Product Requirements / Acceptance Scenariosをactual repositoryへ実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

ADR-0020に従い、current Product Valueから再導出したProduct RequirementsとAcceptance Scenariosを`requirements/`へ実体化する。

historical candidateの意味核は再利用するが、旧ID、Milestone構造、Evidence状態をそのままcurrent baselineへ継承しない。

## Inputs

### Current normative inputs

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- ADR-0001〜ADR-0020

### Historical candidate inputs

Libraryから次を回収し、current baselineへ照合した。

- `requirements/PRODUCT_REQUIREMENTS_v1.md`
- `requirements/ACCEPTANCE_SCENARIOS_v1.md`
- `requirements/PRODUCT_REQUIREMENT_CANDIDATE_EVIDENCE_v1.yaml`
- bundle manifest
- M49 / M50 acceptance candidate群

historical Product Requirementsには`SOZA-PR-001`〜`SOZA-PR-018`とNFR 10件、Acceptance Scenario 8件が存在した。

## Resolution

### 1. current canonical filesを実体化した

actual repositoryへ次を追加した。

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

current Requirementは22件となったが、**22という件数自体を将来の制約にはしない。**

主な追加・独立化:

- REQ-0019 Human / AI Readability
- REQ-0020 Evidence claim integrity
- REQ-0022 Provider-neutral Capability Observation

Moving Future Horizonは利用者世界のRequirementではなく設計評価規則と判断し、current REQへ残さずADR-0001 / Product Principlesへ置いた。

### 3. Acceptance ScenarioをSCN-0001〜SCN-0017へ再構成した

historical `SOZA-AS-001`〜`008`の意味核をSCN-0001〜0008へ移し、後発ADRを検証するScenarioを追加した。

追加した主なScenario:

- Recommendation → Decision → Authority → Execution
- exact historical binding
- Provider partial degradation / observation gap
- Provider Selective Disclosure
- simple UI / canonical meaning
- Execution Provider replacement
- Pattern / Cognitive Method separation
- Decision後のresidual / reopen
- Evidence claim height audit

### 4. historical mappingを独立保存した

`requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`で、旧PR / NFR / ASからcurrent REQ / SCNへの統合・分離・上位移管を記録した。

旧IDをcurrent identityとして再利用していない。

### 5. historical Evidenceをcurrentへ継承していない

historical candidateの`direct`、`partial`、`design_only`、local PASS等はcurrent actual repositoryのEvidenceへ自動変換していない。

current baselineでは、Product / ADR / Requirement文書で確認できるDesign Acceptanceのみを記録した。

Executable / Release / Operational Acceptanceはactual evidenceがない限り`Not Yet Verified`としている。

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

Design baselineの完了条件から分離し、`ISSUE-000027`へ移した。

- current Requirement / Scenario registry checker
- REQ / SCN ID重複検査
- 相互参照切れ検査
- Value Axis検査
- negative fixture

したがって本Issueを`Resolved`としても、RequirementsのExecutable AcceptanceがSatisfiedになったことを意味しない。

## Evidence state at closure

- Requirements Design Baseline: **Satisfied**
- Requirements Registry Executable Check: **Not Yet Verified** — ISSUE-000027
- Release Acceptance: **Not Yet Verified**
- Operational Acceptance: **Not Yet Verified**

## Dependencies / Follow-up

- ADR-0020
- ISSUE-000022 — repository baseline全体
- ISSUE-000027 — requirements registry checker
- ISSUE-000015 — 全開発文書の自然な日本語監査

## Natural Japanese review

実体化したREQ / SCN / historical mappingへ戻ってAcceptanceを一件ずつ照合し、Design baselineとExecutable checkerの責務を分離した。その後、意味、Evidence状態、未完了範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
