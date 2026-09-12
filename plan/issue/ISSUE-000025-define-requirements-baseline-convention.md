# ISSUE-000025: Product ValueからRequirements基線を再構成する規約を定める

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
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

## Resolution

ADR-0020で、Requirements baselineの意味規約をAcceptedとした。

### Stable identity

- Product Requirement: `REQ-0001`〜`REQ-9999`
- Acceptance Scenario: `SCN-0001`〜`SCN-9999`

IDにはValue Axis、Milestone、type、配置、statusを埋め込まない。

### Requirement / Scenario / Testの分離

```text
Requirement != Acceptance Scenario != Test Case
```

Requirementは「何が必要か」を、Scenarioは意味上の利用・検証状況を、Testは具体的なExecutable Evidenceを表す。

### Product Value traceability

Accepted Requirementは、原則としてV1〜V8または明示的なProduct Principle / external constraintへ追跡できるようにする。

### Status / Evidence separation

```text
Requirement Accepted != Executable Evidence Satisfied
```

Requirement statusと、Design / Executable / Release / Operational Acceptanceを分離する。

### Canonical entry point

初期baselineは次を正本入口とする。

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  history/
```

量が増えた場合は個別ファイルへ分割できるが、REQ / SCN IDは維持する。

### Historical candidate

historical candidateを再採用する場合はcurrent Product Valueへ再評価し、新しいREQ IDへmappingする。旧`VERIFIED`やPASSをcurrent Evidenceへ自動継承しない。

## Questionsへの回答

1. Requirement IDは`REQ-0001`形式の単一namespaceとする。
2. Requirement statusとEvidence statusを分離する。
3. Accepted Requirementは関係するV1〜V8または別の明示根拠へ追跡する。
4. Functional / NFR等はtype metadataとし、別namespaceへ分けない。
5. Acceptance Scenarioは`SCN-0001`形式で独立管理する。
6. Design / Executable / Release / Operational Acceptanceを分離する。
7. Requirementはwhat / why、ADRはarchitectural decisionを担う。
8. historical candidateはcurrent valueへ再照合した場合のみ再採用する。
9. MilestoneをREQ IDへ埋め込まない。
10. Product Value変更時は影響REQを上位から再監査する。

## Acceptance

### Semantic / Design Acceptance

- [x] Requirementのstable identity規則が決まっている。
- [x] statusとEvidence状態が分かれている。
- [x] V1〜V8追跡規則が決まっている。
- [x] Acceptance Scenarioの独立性が決まっている。
- [x] historical candidateの再採用条件が決まっている。
- [x] ADRとの責務境界が決まっている。
- [x] 自然な日本語ドラフト工程が組み込まれている。

### Executable Acceptance

本Issueでは要求しない。actual `requirements/`文書の実体化と検査は`ISSUE-000026`へ分離する。

## Dependencies

- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_MODEL.md`
- `product/value/SEI_VALUE_ACCEPTANCE.md`
- ADR-0018
- ADR-0020
- ISSUE-000022

## Natural Japanese review

ADR-0020へ戻って結論を照合した後、意味、強度、例外、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最終意味監査も実施済み。
