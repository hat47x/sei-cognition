# ISSUE-000027: Requirements / Scenario registryの整合性検査をactual repositoryへ実装する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0020**  
Updated: 2026-08-31

## Goal

current `requirements/PRODUCT_REQUIREMENTS.md`と`requirements/ACCEPTANCE_SCENARIOS.md`について、stable ID、参照、Value Axis、状態語彙の基本整合性をactual repository上で再現可能に検査する。

このIssueはRequirementsの意味内容を決めるものではない。ADR-0020とISSUE-000026で確定したDesign baselineに対するExecutable Acceptanceを担当する。

## Required checks

最低限、次を検査する。

1. `REQ-\d{4}`のIDが重複していない。
2. `SCN-\d{4}`のIDが重複していない。
3. Requirementから参照するSCN IDがcurrent Scenario registryに存在する。
4. Scenarioから参照するREQ IDがcurrent Requirement registryに存在する。
5. V1〜V8以外のValue Axisを誤記していない。
6. Requirement statusがADR-0020の許容状態に収まる。
7. Acceptance stateがValue Acceptanceの許容状態に収まる。
8. historical `SOZA-PR-*` / `SOZA-NFR-*` / `SOZA-AS-*`をcurrent canonical IDとして使用していない。
9. Milestone名をREQ / SCN identityへ埋め込んでいない。
10. canonical file間の参照切れを検出できる。

## Preferred implementation

初期実装は、依存を増やさず再実行しやすい小さな検査ツールを優先する。

候補:

```text
plan/scripts/check_requirements_registry.py
```

Markdownを完全なASTへ変換すること自体を目的にしない。current文書の安定した見出し・metadata規約を検査できればよい。

将来Requirement registryをmachine-readable sourceへ移した場合は、本ツールを置換してよい。

## Required negative fixtures

少なくとも次を一時入力またはtest fixtureで検出できることを確認する。

- REQ ID重複
- SCN ID重複
- 存在しないREQ参照
- 存在しないSCN参照
- 不正Value Axis
- historical IDのcanonical混入

## Evidence boundary

ツールファイルが存在するだけではExecutable AcceptanceをSatisfiedにしない。

actual repository上で実行し、current registryに対するPASSとnegative caseに対する期待どおりのFAILを確認して初めてExecutable Evidenceとする。

```text
checker implementation != checker execution evidence
```

## Acceptance criteria

- [ ] actual repositoryにcheckerが存在する。
- [ ] current REQ / SCNの相互参照を検査できる。
- [ ] negative fixturesで不整合を検出できる。
- [ ] actual current baselineに対するPASSを再現できる。
- [ ] 検査結果をDesign / Executable / Release / Operational Evidenceと混同しない。
- [ ] checker説明文を自然な日本語で再ドラフトし、最終意味監査を行う。

## Dependencies

- ADR-0020
- ISSUE-000026
- ISSUE-000022

## Natural Japanese review

Design baselineとExecutable Acceptanceの責務を分離した後、検査対象とEvidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。実装完了時に再度、最終意味監査を行う。
