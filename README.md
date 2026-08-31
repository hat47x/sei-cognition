# 綜座 / SOZA

更新日: 2026-08-31  
状態: **Product / Requirements / Architecture / Contract Baseline — development in progress**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で増やすことではありません。実行手段が変わっても残る意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 現在の開発branch

通常の開発は、次の形式のbranchで進めます。

```text
develop/vX.Y.Z
```

現在の開発branchは`develop/v0.1.0`です。

`main`は安定した基線のために保持し、開発中の変更を直接積み上げないことを原則とします。branch運用の詳細は`plan/DEVELOPMENT_WORKFLOW.md`を参照してください。

## 2. 現在の正本

2026-08-31時点で、`develop/v0.1.0`には次のcurrent baselineがあります。

```text
product/
requirements/
architecture/
contracts/
plan/
```

正本関係は概ね次のとおりです。

```text
Product Value / Value Model / Value Acceptance
  ↓
Requirements / Acceptance Scenarios
  ↓
ADR
  ↓
Reference Architecture
  ↓
Contract Definition
  ↓
Schema / Validator / Fixture
  ↓
Runtime / Provider Integration
```

下位から反証が得られた場合は上位へ戻って再検討します。ただし、既存実装を維持するためだけにProduct Valueを書き換えません。

過去のM48〜M50 candidateや旧Semantic Platformの実装資産は参照資料として利用できますが、current actual repositoryのEvidenceへ自動継承しません。

## 3. 最初に読む文書

### Product

1. `product/README.md`
2. `product/value/SOZA_PRODUCT_VALUE.md`
3. `product/value/SOZA_VALUE_MODEL.md`
4. `product/value/SOZA_VALUE_ACCEPTANCE.md`
5. `product/value/SOZA_VALUE_TRACEABILITY.md`
6. `product/vision/SOZA_PRODUCT_VISION.md`
7. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

### Requirements

8. `requirements/README.md`
9. `requirements/PRODUCT_REQUIREMENTS.md`
10. `requirements/ACCEPTANCE_SCENARIOS.md`
11. `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

### Architecture

12. `architecture/README.md`
13. `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
14. `architecture/TRACEABILITY.md`
15. `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

### Contracts

16. `contracts/README.md`
17. `contracts/CONTRACT_CATALOG.md`
18. `contracts/TRACEABILITY.md`
19. `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
20. `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
21. `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
22. `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
23. `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`
24. `contracts/history/HISTORICAL_CONTRACT_MAPPING.md`

### Planning / Decisions

25. `plan/README.md`
26. `plan/DEVELOPMENT_WORKFLOW.md`
27. `plan/DOCUMENT_AUTHORING_STANDARD.md`
28. `plan/registry.yaml`

個別の設計判断は`plan/adr/`、未完了作業や調査は`plan/issue/`を参照してください。

## 4. Product Valueの中心

SOZAでは、少なくとも次を重要な意味差として扱います。

```text
Observation
  != Interpretation / Hypothesis
  != Recommendation
  != Decision
  != Authority
  != Action Intent
  != Execution
```

この式は、処理を細かく分割すること自体を目的としたものではありません。後から「何が観測で、何が解釈で、誰または何が何を判断し、どの権限で何が実行されたのか」を再構成できるようにするための境界です。

また、次の原則も重視します。

- `Unknown != No`
- `Conflict != latest-wins`
- `not observed != unavailable`
- CapabilityとProviderを同一視しない。
- actorの種類だけからAuthorityやTrustを推定しない。
- ProviderやStorageが変わってもDecisionの意味を変えない。
- private chain-of-thoughtの保存を耐久的意味の前提にしない。
- Design EvidenceをExecutable Evidenceへ自動昇格させない。
- Operational Successを利用者価値の実現と同一視しない。

## 5. Product Valueの評価

`SOZA_VALUE_MODEL.md`では、Product Valueを単一スコアへ還元せず、次の8軸で確認します。

- V1 — Historical Reconstruction
- V2 — Semantic Separation
- V3 — Revision Integrity
- V4 — Provider Independence
- V5 — Uncertainty Preservation
- V6 — Human / AI Readability
- V7 — Progressive Explicitness
- V8 — Execution Independence

一つの軸の強さで、別の重大な欠損を相殺しません。

`SOZA_VALUE_ACCEPTANCE.md`では、Evidenceの高さを次のように分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

本番で正常に動作することと、利用者・組織の判断や成果へ価値が届くことは別に検証します。

current下位文書との関係は`product/value/SOZA_VALUE_TRACEABILITY.md`から辿れます。

## 6. Current Requirements baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenarioは`SCN-0001`〜`SCN-0017`です。

旧candidateの`SOZA-PR-*`、`SOZA-NFR-*`、`SOZA-AS-*`はhistorical provenanceとして保持し、新しいIDへ機械的にrenameしていません。対応は`requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`で確認できます。

```text
Requirement Accepted != Executable Evidence Satisfied
Requirement != Acceptance Scenario != Test Case
```

Requirements Design baselineは実体化済みです。また、current registryについては専用checkerとnegative self-testがあり、actual GitHub Actionsで22 Requirement / 17 Scenarioの構造整合を再現可能に確認しています。

このPASSはRequirementの意味内容そのものの正当性やimplementation completenessを証明しません。

## 7. Current Architecture baseline

current Reference Architectureは、M48 / M49 / M50等のMilestone順ではなく、次のようなArchitecture concernへ再構成されています。

- Durable Semantic Core
- Inquiry / Epistemic State
- Cognitive Method
- Decision Memory
- Capability Definition / Observation / Choice
- Responsibility / Authority boundary
- Semantic Reference / Revision / Exact Binding
- Profile / Policy
- Federation / Selective Disclosure
- Provider / Adapter
- Projection
- Persistence
- Evidence / Assurance boundary

これらは意味設計上の関心領域であり、一対一のservice、Go package、databaseへ固定しません。

`architecture/TRACEABILITY.md`では、REQ-0001〜REQ-0022が少なくとも一つのcurrent Architecture concernへ追跡できることを確認しています。

## 8. Current Contract baseline

current Contractは、Architecture上の関心領域をすべてContract化せず、独立versioningと相互運用が必要な4 familyへ絞っています。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Semantic ContractとRepresentation Profileは分離します。

```text
Semantic Contract != Representation Profile
```

Markdown Contract Definitionをsemantic normative sourceとし、machine-readable schemaは検証可能なrepresentationとして扱います。

current actual repositoryには、4 ContractのJSON Schema、17 fixture、semantic validator、conformance workflowがあります。Contract v1alpha1のfixture-scoped Executable ConformanceはGitHub Actionsでsuccessしています。

ただし、次は未検証です。

- stable Representation Profile
- historical M47 digest mapping
- full runtime conformance
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

Contract fixtureのPASSを、SOZA全体のExecutable Acceptanceへ拡張しません。

## 9. SOZAとTEI

鼎（TEI）はSOZAそのものではありません。SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

SOZAは、関連製品であるという理由だけでTEIを優先しません。TEI固有のApplication、Database、Release、Deployment等のschemaをSOZA Universal Coreへ複製せず、必要な情報をProvider-neutralなCapability Observation等の明示的な境界から扱います。

詳細はADR-0014、ADR-0019を参照してください。

## 10. Planning integrity

`plan/registry.yaml`はADR / Issueの恒久ID、Status、関連を管理する台帳です。

並行開発で同一IDが競合した実例を受け、current repositoryには次を追加しています。

- `plan/scripts/check_plan_registry.py`
- `plan/scripts/next_plan_id.py`
- `.github/workflows/plan-integrity.yml`

checkerは、ID重複、registry漏れ、filename / heading / ID不一致、Status不一致、存在しない関連ID等を検出します。

```text
Plan integrity PASS != Product Value satisfied
```

採番helperは番号予約ではありません。並行branchではmerge前に最新developとの競合を再確認します。

## 11. 現在の主な未完了領域

個々のStatusは`plan/registry.yaml`と各Issue本文を正とします。

現在、特に残っている境界として次があります。

- ISSUE-000009 — Portable Exact Binding / stable Representation Profile / historical M47 digest mapping
- ISSUE-000015 — 既存開発文書の自然な日本語による全面監査
- ISSUE-000021 — design history provenance監査（Deferred）
- ISSUE-000022 — repository baseline全体の実体化

Requirements registry checker、Capability Observation F1〜F7、Contract schema / fixture / conformanceはcurrent actual repositoryへ実体化され、それぞれのIssueはResolvedへ進んでいます。

## 12. 文書品質

SOZAでは、開発文書の自然な日本語を設計品質の一部として扱います。

文書の内容、構造、技術的一貫性を整えた後に、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設けます。その後、意味が変わっていないことを再監査します。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。既存文書の再監査はISSUE-000015で継続しています。

## 13. 次の実体化

現在の主要な優先順位は、概ね次のとおりです。

1. Product Value / Requirements / ADR / Architecture / Contractの整合維持
2. Exact Binding Representation Profileの安定化
3. current runtime / Provider Adapter / persistence integrationの実体化
4. Contract以外のRequirementを含むExecutable Evidenceの拡張
5. release artifactに対するRelease Evidence
6. productionにおけるOperational Evidence
7. 実利用から得るAdoption / Outcome Evidence

過去candidateを一括コピーして現在の正本にするのではなく、Product Valueとcurrent REQ / ADR / Architecture / Contractへ再照合しながら段階的に実体化します。

## 14. Releaseについて

現在の`develop/v0.1.0`は開発中のbaselineです。releaseやoperational evidenceを主張する状態ではありません。

`main`へ統合する際は、上位文書、Requirements、Architecture、Contracts、Executable Evidenceの整合を確認し、実際に得られたEvidenceを超えない範囲で状態を更新します。

release後も、Release EvidenceとOperational Evidence、Adoption / Outcome Evidenceを区別します。

## 15. 自然な日本語レビュー

actual repositoryのProduct、Requirements、Architecture、Contract、Plan、current checker / conformance Evidenceへ戻って現在地を照合しました。そのうえで、過去candidate由来の記述や古い未完了状態をcurrent Evidenceと混同しないよう整理し、Design / Executable / Release / Operational / Adoption・Outcomeの境界を統一しました。最後に、意味、Evidence強度、未完了範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
