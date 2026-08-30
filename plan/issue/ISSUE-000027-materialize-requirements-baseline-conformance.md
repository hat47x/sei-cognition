# ISSUE-000027: Requirements baselineの整合検査をactual repositoryへ実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## 目的

`requirements/`に実体化したcurrent Product RequirementsとAcceptance Scenariosについて、ID重複、参照切れ、Value Axis参照、Evidence状態等の基本整合をactual repository上で再現可能に検査できるようにします。

ISSUE-000026で完了するDesign baselineと、Executable Acceptanceを分離するための後続Issueです。

## 背景

current Requirements baselineには、次が揃っています。

- `requirements/README.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

Requirementは`REQ-0001`〜`REQ-0022`、Scenarioは`SCN-0001`〜`SCN-0017`まで実体化されています。

一方、現在のactual repositoryには`tools/`がまだなく、Requirements registryを機械的に検査するcurrent toolは存在しません。Design文書が整っていることだけを理由にExecutable AcceptanceをSatisfiedとは扱いません。

## 必須検査

少なくとも次を検査します。

1. `REQ-0001`形式のIDが重複していない。
2. `SCN-0001`形式のIDが重複していない。
3. Requirement一覧と本文のREQ ID集合が一致する。
4. Scenario一覧と本文のSCN ID集合が一致する。
5. Requirementから参照するSCNが存在する。
6. Scenarioから参照するREQが存在する。
7. V1〜V8以外のValue Axisを誤って参照していない。
8. Requirement StatusがADR-0020で定めた語彙に従う。
9. Design / Executable / Release / OperationalのEvidence状態が、許可された語彙に従う。
10. Accepted Requirementを理由にExecutable Acceptanceを自動的にSatisfiedへしていない。
11. current canonical文書とhistorical mappingを混同していない。

## 推奨出力

初期実装では、たとえば次の形で十分です。

```text
tools/check_requirements_baseline.py
generated/requirements_baseline_conformance.json
```

ただし、`tools/`や`generated/`の最終構成はISSUE-000022のrepository baseline実体化と整合させます。

## Acceptance

### Design Acceptance

- [x] 検査対象となるcanonical Requirements文書が存在する。
- [x] ADR-0020でID、Status、Evidenceの規則が定義されている。
- [x] current REQ / SCNとhistorical mappingが分離されている。

### Executable Acceptance

- [ ] current repositoryにRequirements checkerが存在する。
- [ ] checkerがcurrent Requirements baselineへ対してPASSする。
- [ ] REQ重複を導入したnegative fixtureまたは同等の試験でFAILする。
- [ ] SCN参照切れを導入したnegative fixtureまたは同等の試験でFAILする。
- [ ] 不正Value Axisまたは不正Evidence状態を検出できる。
- [ ] 検査結果を再現可能なEvidenceとして残せる。

Release / Operational Acceptanceは本Issueの完了条件にはしません。

## Dependencies

- ADR-0018
- ADR-0020
- ISSUE-000022
- ISSUE-000026
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`

## 対象外

- Requirementの意味そのものをcheckerへ埋め込むこと
- Requirementを単一スコアで評価すること
- Product Valueの妥当性を自動判定すること
- historical candidateの旧PASSをcurrent Evidenceとして読み替えること

## 自然な日本語ドラフト

Design baselineとExecutable Acceptanceを混同しないよう目的と完了条件を整理した後、意味、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。最終意味監査も実施しています。
