# ISSUE-000025: Product ValueからRequirements基線を再構成する規約を定める

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0018**  
Updated: 2026-08-31

## Goal

actual repositoryに存在しない`requirements/`を新たに実体化する前に、Product ValueからRequirementへ何をどのように導出し、Requirementの状態とEvidenceの状態をどう分けるかを定める。

過去candidate bundleのRequirementをそのまま正本へ戻すのではなく、現在のProduct Value、Value Model、Value Acceptance、ADRを基準として再構成できる規約を作る。

## Background

2026-08-31のactual tree監査では、`requirements/`がGitHub repositoryに存在しないことを確認した。

一方、repository READMEには過去candidateとして次の文書名が残る。

- `requirements/PRODUCT_REQUIREMENTS_v1.md`
- `requirements/ACCEPTANCE_SCENARIOS_v1.md`
- `requirements/M49_DECISION_MEMORY_ACCEPTANCE_v1.md`
- `requirements/M50_CAPABILITY_CHOICE_ACCEPTANCE_v1.md`
- その他historical requirement evidence文書

これらはhistorical candidateやLibrary資産として再利用候補になり得るが、current Product Valueへ再照合する前にactual requirement baselineとして扱ってはならない。

## Questions

1. Requirementのstable IDをどの形式で管理するか。
2. Requirement statusとEvidence statusをどう分離するか。
3. Product Value V1〜V8との追跡をどの粒度で必須にするか。
4. Functional / non-functional / semantic constraint等を別namespaceに分けるか。
5. Acceptance ScenarioをRequirement本文へ埋め込むか、独立IDで管理するか。
6. Design / Executable / Release / Operational Acceptanceをどう表すか。
7. RequirementとADRの責務境界をどう保つか。
8. historical candidate Requirementをcurrent baselineへ再採用する条件は何か。
9. Milestone名や実装順序をRequirement identityへ埋め込まないためにどうするか。
10. Product Value変更時にRequirementをどう再監査するか。

## Constraints

- Product Valueの文言をそのまま機能要件へコピーしない。
- V1〜V8を単一スコアへまとめない。
- Requirement statusとimplementation / evidence statusを混同しない。
- M48 / M49 / M50等の実装順序をRequirementの恒久identityへしない。
- TEI固有RequirementをSOZA Universal Requirementへ無条件に昇格させない。
- historical candidateの`VERIFIED`等をcurrent Evidenceへ自動継承しない。
- actual repositoryに存在しないfixtureやtestをAcceptance済みとしない。

## Required deliverables

- Requirements directory convention
- Requirement ID convention
- Acceptance Scenario ID convention
- Requirement status model
- Evidence / acceptance state model
- V1〜V8 traceability rule
- ADR / Requirement responsibility boundary
- historical candidate adoption rule
- natural Japanese document rule
- ADR

## Acceptance

### Semantic / Design Acceptance

- [ ] Requirementのstable identity規則が決まっている。
- [ ] statusとEvidence状態が分かれている。
- [ ] V1〜V8追跡規則が決まっている。
- [ ] Acceptance Scenarioの独立性が決まっている。
- [ ] historical candidateの再採用条件が決まっている。
- [ ] ADRとの責務境界が決まっている。
- [ ] 自然な日本語ドラフト工程が組み込まれている。

### Executable Acceptance

本Issueでは要求しない。actual `requirements/`文書の実体化と検査は後続Issueへ分離する。

## Dependencies

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- ADR-0018
- ISSUE-000022

## Natural Japanese review

論点と制約を整理した後、未決事項を勝手に確定せず、自然な日本語となることを最重要視して全文を再ドラフトした。Decision確定時に再度、最終意味監査を行う。
