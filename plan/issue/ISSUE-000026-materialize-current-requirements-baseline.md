# ISSUE-000026: current Product Requirements / Acceptance Scenariosをactual repositoryへ実体化する

Status: **In Progress**  
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

Libraryで次を回収済み。

- `requirements/PRODUCT_REQUIREMENTS_v1.md`
- `requirements/ACCEPTANCE_SCENARIOS_v1.md`
- `requirements/PRODUCT_REQUIREMENT_CANDIDATE_EVIDENCE_v1.yaml`
- `requirements/PRODUCT_REQUIREMENT_EVIDENCE_BRIDGE_v1.md`
- M49 / M50 acceptance candidate群

historical Product Requirementsには`SOZA-PR-001`〜`SOZA-PR-018`とNFR 10件が存在する。

## Migration principle

### 1. 件数を保存しない

18件＋10件という旧構成を維持すること自体を目的にしない。

重複するNFRはcurrent Requirementへ統合し、現在のValue Modelで新たに明示された境界は必要に応じて追加する。

### 2. 旧IDをcurrent IDとして再利用しない

current baselineは`REQ-0001`形式を使用する。

旧`SOZA-PR-*` / `SOZA-NFR-*`はhistorical provenanceとしてmapping文書へ残す。

### 3. Evidenceを継承しない

historical candidateの`direct`、`partial`、`design_only`、`VERIFIED`、local PASS等をcurrent actual repositoryのEvidenceへ自動変換しない。

current baselineでは、Product / ADR文書により確認できるDesign Acceptanceだけを評価し、Executable / Release / Operational Acceptanceはactual evidenceがない限り`Not Yet Verified`とする。

### 4. MilestoneをRequirementへ持ち込まない

M48 / M49 / M50はhistorical implementation planningとしてprovenanceへ残せるが、current REQのidentityや意味にはしない。

## Planned current requirement bundles

少なくとも次の意味核をcurrent REQへ再構成する。

1. durable semantic continuity
2. epistemic state / uncertainty preservation
3. provenance / discovery / derivation separation
4. Cognitive Method independence
5. Decision historical reconstruction
6. Recommendation / Decision / Authority / Execution separation
7. Capability / Provider neutrality
8. route / responsibility provenance
9. revision / supersession integrity
10. progressive semantic explicitness
11. Projection non-authority
12. bounded collaboration / selective disclosure
13. actor kindからauthority等を推定しない
14. unresolved residual / reopen condition preservation
15. private chain-of-thought independence
16. Observation / Interpretation boundary
17. contextual Responsibility
18. storage independence
19. human / AI readability
20. Evidence claim integrity
21. replaceable realization / execution independence
22. provider-neutral Capability Observation

これは作業開始時の束であり、自然なKJ的統合・重複監査により必要なら増減できる。件数を固定しない。

## Required outputs

- `requirements/README.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

## Acceptance

### Semantic / Design Acceptance

- [ ] current REQがProduct Value V1〜V8またはProduct Principleへ追跡できる。
- [ ] historical requirementの意味核とcurrent REQの対応を追える。
- [ ] old Evidence stateをcurrentへ自動継承していない。
- [ ] RequirementとADRの責務が混ざっていない。
- [ ] Milestone名がREQ identityへ入っていない。
- [ ] SCNがREQと独立IDになっている。
- [ ] current ADR-0019までの新しい境界をScenarioへ反映している。
- [ ] 全文を自然な日本語で再ドラフトし、最終意味監査を行っている。

### Executable Acceptance

- [ ] current Requirement / Scenario registryを検査するactual toolがrepositoryに存在する。
- [ ] REQ / SCN ID重複、参照切れ、Value Axis参照を検査できる。

Executable Acceptanceは、まずDesign baselineを実体化した後に別sliceとして進めてもよい。Design文書の完成だけでExecutable AcceptanceをSatisfiedにしない。

## Dependencies

- ADR-0020
- ISSUE-000022
- ISSUE-000015

## Natural Japanese review

current / historical / evidenceの三層を混同しないよう構造を整理した後、条件や意味を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。作業完了時に最終意味監査を再実施する。
