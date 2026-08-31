# ISSUE-000038: Requirements入口とAcceptance ScenarioのEvidence現在地を再整合する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

`requirements/README.md`と`requirements/ACCEPTANCE_SCENARIOS.md`を、current repositoryの実体とProduct Valueの5段階Evidence境界へ再整合する。

特に、旧baseline時点の「Architecture / Contract / Runtime / Toolsがまだ存在しない」という記述と、Scenarioごとの旧4段階Evidence表現を解消する。

## Resolution

### 1. Requirements入口をactual repositoryへ合わせた

`requirements/README.md`で、現在存在するArchitecture、Contract、Representation Profile、Go semantic runtime、synthetic Provider Adapter、checker / CIを明示した。

Requirement / Scenario / Test Caseの役割は維持し、fixture PASSをRequirementやScenario全体の達成へ自動昇格させない境界を追加した。

### 2. Evidenceを5段階へ統一した

Requirements層でも次を共通語彙とした。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

ScenarioのCurrent Evidenceでは、Release、Operational、Adoption / Outcomeを独立して表示する。

### 3. SCN-0001〜SCN-0017をactual Evidenceへ戻して監査した

fixture、Contract Conformance、Representation Profile、first semantic runtime、synthetic Provider AdapterをScenarioの期待へ一件ずつ戻し、実際に検査できた部分だけを`Partially Satisfied`等へ反映した。

主な更新例:

- SCN-0002 — F5とsynthetic Provider A / BによるProvider分離
- SCN-0007 / 0012 — `withheld` / `unknown`とpartial knowledge
- SCN-0009 — Recommendation / Decision / Authority / Execution境界の一部
- SCN-0010 — historical exact basis、mismatch rejection、`verified / failed / not_verified`
- SCN-0011 — partial degradation、observation gap、missing値の`unknown`保持
- SCN-0016 — Decision後のunresolved reference保持

### 4. 未検証Scenarioを無理に上げていない

次のような領域はExecutableを`Not Yet Verified`のまま維持した。

- 軽量案件 / 高影響案件のProfile・Policy実行
- Cognitive Method / Realization交換
- Projection作り直し
- actual Storage migration
- Execution Provider交換
- Pattern / Cognitive Method runtime

synthetic Capability Observation Providerの交換を、Execution Provider交換のEvidenceとは扱わない。

### 5. SCN-0017をcurrent mixed-evidence状態へ更新した

旧SCN-0017は「current Architecture / Runtime / Toolsが存在しない」状態を前提としていたため、現在のrepositoryと矛盾していた。

Scenarioの核である「Evidenceの高さを越えた達成主張を監査する」を維持しつつ、一部にExecutable Evidenceがあり、別の領域はDesignに留まる現在の混在状態へ状況を更新した。

### 6. Scenario identityとfixture identityを分離した

```text
Scenario != Fixture != Test implementation
```

F1 / F4やsynthetic Provider Adapter testがSCN-0011の一部期待を検査していても、fixture IDをScenario IDへ昇格させない。

## Acceptance

- [x] Requirements READMEの旧repository不存在記述を解消した。
- [x] Requirements READMEへ5段階Evidenceを反映した。
- [x] SCN-0001〜SCN-0017のCurrent Evidenceをactual repositoryへ再照合した。
- [x] Release / Operational / Adoption・Outcomeを独立表示した。
- [x] fixture PASSをScenario全体のSatisfiedへ自動昇格させていない。
- [x] production Provider / Storage / Executionの未検証境界を維持した。
- [x] SCN-0017の意味核を維持したまま、現在のrepository状態へ更新した。
- [x] V1〜V8、REQ ID、SCN IDを変更していない。
- [x] 新ADRを追加せず、ADR-0018 / ADR-0020の既存境界を適用した。
- [x] 自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を行った。

## Evidence boundary

本IssueはRequirements層の文書とEvidence現在地を再整合する。

```text
Scenario evidence aligned
  != Scenario fully satisfied
  != production interoperability
  != release readiness
  != operational success
  != user-value realization
```

## Natural Japanese review

Product Value、Product Requirements、ADR-0018 / ADR-0020、current Contract / Representation Profile / Runtime、Capability Observation F1〜F7、synthetic Provider Adapterのactual Evidenceへ戻ってScenarioごとに照合した。その後、意味、期待、失敗条件、Evidence強度、留保を変えず、自然な日本語となることを最重要視して`requirements/README.md`と`ACCEPTANCE_SCENARIOS.md`を全文再ドラフトし、最終意味監査を実施済みです。
