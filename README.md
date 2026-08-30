# 綜座 / SOZA

更新日: 2026-08-31  
状態: **Product / Requirements / Planning Baseline — development in progress**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で増やすことではありません。実行手段が変わっても残る、意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 現在の開発branch

通常の開発は、次の形式のbranchで進めます。

```text
develop/vX.Y.Z
```

現在の開発branchは`develop/v0.1.0`です。

`main`は安定した基線のために保持し、開発中の変更を直接積み上げないことを原則とします。branch運用の詳細は`plan/DEVELOPMENT_WORKFLOW.md`を参照してください。

## 2. 現在の正本

2026-08-31時点で、`develop/v0.1.0`には次の上位層が実体化されています。

```text
product/
requirements/
plan/
```

一方、current baselineとしての`architecture/`、`contracts/`、`runtime/`、`tools/`は、まだこのbranchへ実体化を終えていません。

過去のM48〜M50 candidateや旧Semantic Platformの実装資産は参照資料として利用できますが、current actual repositoryに存在するEvidenceと同一視しません。

## 3. 最初に読む文書

### Product Value

1. `product/value/SOZA_PRODUCT_VALUE.md`
2. `product/value/SOZA_VALUE_MODEL.md`
3. `product/value/SOZA_VALUE_ACCEPTANCE.md`
4. `product/vision/SOZA_PRODUCT_VISION.md`
5. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

### Requirements

6. `requirements/README.md`
7. `requirements/PRODUCT_REQUIREMENTS.md`
8. `requirements/ACCEPTANCE_SCENARIOS.md`
9. `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

### Planning / Decisions

10. `plan/README.md`
11. `plan/DEVELOPMENT_WORKFLOW.md`
12. `plan/DOCUMENT_AUTHORING_STANDARD.md`
13. `plan/registry.yaml`

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
- CapabilityとProviderを同一視しない。
- actorの種類だけからAuthorityやTrustを推定しない。
- ProviderやStorageが変わっても、Decisionの意味を変えない。
- private chain-of-thoughtの保存を耐久的意味の前提にしない。
- Design EvidenceをExecutable / Release / Operational Evidenceへ自動昇格させない。

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

`SOZA_VALUE_ACCEPTANCE.md`では、これらについてDesign、Executable、Release、Operational Evidenceを分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
```

## 6. Current Requirements baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenarioは`SCN-0001`〜`SCN-0017`まで実体化されています。

旧candidateの`SOZA-PR-*`、`SOZA-NFR-*`、`SOZA-AS-*`はhistorical provenanceとして保持し、新しいIDへ機械的にrenameしていません。対応は`requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`で確認できます。

RequirementがAcceptedであることと、actual implementationで実証済みであることは別です。

```text
Requirement Accepted != Executable Evidence Satisfied
```

Requirements Design baselineは実体化済みですが、registryの機械検査はISSUE-000027で後続整備します。

## 7. SOZAとTEI

鼎（TEI）はSOZAそのものではありません。SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

SOZAは、関連製品であるという理由だけでTEIを優先しません。TEI固有のApplication、Database、Release、Deployment等のschemaをSOZA Universal Coreへ複製せず、必要な情報をCapability Observation等の明示的な境界から扱う方針です。

詳細はADR-0014、ADR-0019を参照してください。

## 8. 現在のPlan

`plan/registry.yaml`では、2026-08-31時点でADR-0020、ISSUE-000027まで管理しています。

主な未完了項目は次のとおりです。

- ISSUE-000009 — portable Exact Binding verificationの安定化
- ISSUE-000015 — 既存開発文書の自然な日本語による全面監査
- ISSUE-000021 — design history provenance監査（Deferred）
- ISSUE-000022 — repository baseline全体の実体化
- ISSUE-000024 — Capability Observation fixtureの実体化
- ISSUE-000027 — Requirements / Scenario registry checkerの実装

Statusの詳細は、READMEではなく`plan/registry.yaml`と各Issue本文を正とします。

## 9. 文書品質

SOZAでは、開発文書の自然な日本語を設計品質の一部として扱います。

文書の内容・構造・技術的一貫性を整えた後に、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設けます。その後、意味が変わっていないことを再監査します。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。既存文書の再監査はISSUE-000015で継続しています。

## 10. 次の実体化

当面の優先順位は次のとおりです。

1. Product Value / Vision / Principlesの精緻化と整合維持
2. ADR / Issue / Requirementsの精緻化
3. Requirements registry checkerの実体化
4. current Architecture / Contractsの再構成
5. current runtime / fixtures / toolsの実体化
6. actual repository上でのExecutable Evidence構築
7. release / operational evidence

過去candidateを一括コピーして現在の正本にするのではなく、Product Valueと現在のADRへ再照合しながら段階的に実体化します。

## 11. Releaseについて

現在の`develop/v0.1.0`は開発中のbaselineです。**releaseやoperational evidenceを主張する状態ではありません。**

`main`へ統合する際は、上位文書、Requirements、Architecture / Contracts、Executable Evidenceの整合を確認し、実際に得られたEvidenceを超えない範囲で状態を更新します。
