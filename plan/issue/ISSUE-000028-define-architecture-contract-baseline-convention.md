# ISSUE-000028: current Architecture / Contracts基線の正本・責務・版管理規約を定める

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

current `requirements/`の次段として、`architecture/`と`contracts/`をactual repositoryへ実体化する前に、それぞれが何を正本とし、ADR / Requirement / Implementationとどう責務を分けるかを定める。

historical candidateのArchitecture / Contractを無検査で復元せず、current REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0020から再導出できる規約を作る。

## Resolution

ADR-0021で、Architecture / Contractの権威関係と版管理境界をAcceptedとした。

### Architecture

- ArchitectureはAccepted Requirement / ADRを現在の構造・境界・関係として説明するcurrent design viewとする。
- 新しい重要DecisionをArchitecture本文だけで確定しない。必要ならIssue / ADRへ戻る。
- Architecture concernとruntime componentを同一視しない。
- current canonical filenameへM48 / M49 / M50等のMilestone identityを埋め込まない。
- Architecture文書に別の恒久連番体系を重ねず、重要Decisionのstable identityはADRが担う。

### Contract

- Contractは、複数implementation、Provider、Storage、version等をまたいで相互運用・検証が必要な境界だけを規範化する。
- Contractは`contract_id`とexplicit versionを持つ。
- semantic ContractとRepresentation Profileを分ける。
- human-readable Markdown Contract Definitionをsemantic normative sourceとし、machine-readable schemaは検証可能なrepresentationとして扱う。
- schemaにしか存在しないsemantic requirementを作らない。
- Markdownとschemaが矛盾した場合はContract inconsistencyとして扱い、黙って一方を正としない。

### Version / Evidence

- Contract versionとGit revision / Storage revisionを同一視しない。
- pre-stable versionでもhistorical basisとなった版を特定できるようにする。
- Contract file / schemaの存在をimplementation conformanceへ昇格させない。
- Design / Executable / Release / Operational Evidenceを分ける。

### Historical candidate

- 意味核、反例、設計系譜は再利用する。
- old Milestone、field set、package、algorithm、Evidence stateを自動継承しない。

## Questionsへの回答

1. Architectureはcurrent structural view、ADRはDecision logとする。
2. Architecture current viewには別のstable numeric IDを要求しない。
3. Contractはportable / verifiable agreementが必要な境界でのみ新設する。
4. Contractはlogical `contract_id`と明示versionを持つ。
5. human-readable Contract Definitionをsemantic normative sourceとし、schemaをmachine-verifiable representationとする。
6. semantic ContractとRepresentation Profileを分け、breaking semantic changeとrepresentation changeを区別する。
7. historical Milestone文書は`architecture/history/`等でprovenanceを残し、current filenameへMilestoneを継承しない。
8. Core / Profile / Provider / Adapter / ProjectionはArchitecture concernとして整理するがruntime topologyへ固定しない。
9. V1〜V8 → REQ → ADR → Architecture / Contractの追跡をcurrent baselineで持つ。
10. Design document / schemaの存在とExecutable conformanceを分ける。

## Acceptance

### Semantic / Design Acceptance

- [x] ArchitectureとADRの責務境界が決まっている。
- [x] ArchitectureとContractの責務境界が決まっている。
- [x] Contract identity / version ruleが決まっている。
- [x] machine-readable schemaの権威関係が決まっている。
- [x] historical candidateの再利用規則が決まっている。
- [x] milestone identityをcurrent正本へ持ち込まない規則が決まっている。
- [x] V1〜V8からArchitecture / Contractまで追跡できる規則が決まっている。
- [x] Evidence階層を混同しない規則が決まっている。
- [x] 自然な日本語全文再ドラフトと最終意味監査が完了している。

### Executable Acceptance

本Issueでは要求しない。

- Architecture実体化: ISSUE-000029
- Contract実体化: ISSUE-000030

## Dependencies / Follow-up

- ADR-0021
- ISSUE-000029
- ISSUE-000030

## Natural Japanese review

ADR-0021のDecisionへ戻って全QuestionsとAcceptanceを照合した後、規範強度、例外、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
