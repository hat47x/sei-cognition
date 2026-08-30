# ADR-0014: SOZAとTEIのProduct Boundaryを分離する

Status: **Accepted**  
Related Issue: **ISSUE-000016**  
Updated: 2026-08-31

## Context

SOZAとTEIは、業務意味、AI、Capability、実行を扱うため強く関連する。

しかし、両者が近いからといって一つの製品境界へ統合すると、SOZAの認知・意思決定意味と、TEIの実行可能な業務システム実現境界が混ざる。

過去の「渡辺幸三の業務システム設計」系列と現行TEI実装では、TEIは次の方向へ整理されている。

- Authoring / Canonical Semantic / Binding & Realization / Implementation & Executionを分ける。
- ApplicationとDatabaseを独立対象として扱う。
- 一つのApplicationが複数Databaseを利用できる。
- native SQL、Go、外部Provider等を、無理に独自DSLへ変換しない。
- command acceptedとactual state changedを分け、Observation / Evidenceで実状態を確認する。
- Plugin / Provider / Deployment / Runtimeの安全境界を実装する。

SOZA側では、次を耐久的中心として再基線化している。

- Inquiry / Question
- Observation / Unknown / Conflict / Hypothesis
- EvidenceUse / Assurance / Provenance
- Cognitive Method
- Recommendation / Decision / Rationale
- Responsibility
- Capability discovery / choice
- Semantic Lineage / Decision Memory

## Decision

### 1. SOZAとTEIを別Product Boundaryとして維持する

両者は関連するが、一方を他方の内部moduleとはみなさない。

```text
SOZA
  cognitive / inquiry / decision semantics

        ↓ explicit capability/provider crossing

TEI
  executable business capability realization
```

### 2. SOZAはTEI固有の実行lifecycleをUniversal Coreとして所有しない

SOZA Coreへ、TEI固有の次の概念をそのままコピーしない。

- Application Release
- Database Release
- Database Migration lifecycle
- Deployment Run
- Runtime Lease / Fencing
- Plugin packaging
- Provider-specific execution protocol

SOZAがこれらを参照する必要がある場合は、Capability、Artifact reference、Observation、Evidence等の境界から読む。

### 3. TEIはSOZAのDecision / Authorityを暗黙に代行しない

SOZAでRecommendationやDecisionが存在しても、それだけでTEI実行権限は成立しない。

```text
SOZA Decision
    != TEI Authorization
    != TEI Provider Execution
```

実行へ進む場合は、Profile / Policy / Authorization / Provider boundary等、必要な明示境界を通る。

### 4. TEIをCapability Choiceで特権化しない

TEIはSOZAから見ればCapability Providerの一つである。

人間、SaaS、外部組織、AI、custom code等と同じ判断面で比較できなければならない。

関連製品であること、同じ開発者が関与していること、統合しやすいことだけを理由にTEIへ優先度・信頼・Authorityを付与しない。

### 5. Observation / EvidenceはTEIからSOZAへ戻せる

TEIで実行された結果や観測された状態は、SOZAのInquiry、Decision review、Capability Observation等の入力になり得る。

ただし、

```text
TEI runtime state != SOZA epistemic truth
```

である。

Observationの出所、時点、対象、Assurance等を保持し、必要な認知・判断手続きを経て利用する。

### 6. release / evidence claimを分離する

TEI側のtest、release、operational evidenceによって、SOZA側の未実装Requirementを実装済みとみなさない。

逆も同様である。

各repository / Product Boundaryで、

- design evidence
- executable evidence
- release evidence
- operational evidence

を独立して扱う。

### 7. SOZAとTEIは独立利用可能であることを保つ

TEIはSOZAを必須Runtime dependencyにしない。

SOZAもTEIを必須Providerにしない。

統合したときに価値が高まっても、相互依存を製品の存在条件にはしない。

## Consequences

### Positive

- SOZAの耐久的中心がworkflow / deployment実装へ引きずられにくい。
- TEIは実行基盤として必要な具体性を保てる。
- TEI以外のCapability Providerを中立に扱える。
- 各Productのrelease / evidence claimが明確になる。
- AI・Provider技術が変わってもSOZAのDecision Memoryを保ちやすい。

### Costs

- 統合時にはArtifact reference、Capability mapping、Observation / Evidence adapter等が必要になる。
- 同じ概念に見えるものでも、SOZAとTEIで異なる意味境界を維持する必要がある。
- 開発者は「近い製品だから一つのtypeを共有する」という近道を避ける必要がある。

## Revisit conditions

Product Boundaryそのものは長期原則とする。

具体的な統合Contractは、TEIとSOZA双方のactual implementationが揃った段階で別ADR / Issueとして再検討する。

統合Contractを追加しても、本ADRの独立Product Boundaryを自動的にSupersedeしない。

## Evidence

- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`
- SOZA Product Value / Vision / Principles
- ADR-0012 Capability Choice
- ADR-0013 Capability Realization boundary
- 現行`hat47x/tei-platform`のArchitecture / Plugin / Deployment実装

## Natural Japanese review

内容と境界を確定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
