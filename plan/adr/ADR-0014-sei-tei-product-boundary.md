# ADR-0014: SEIとTEIのProduct Boundaryを分離する

Status: **Accepted**  
Related Issues: **ISSUE-000016, ISSUE-000020, ISSUE-000035, ISSUE-000036**  
Updated: 2026-08-31

## Context

SEIとTEIは、業務上の意味、AI、Capability、実行を扱うため、相互に連携し得る。

しかし、関係が深いことを理由に一つのProduct Boundaryへ統合すると、SEIが扱う認知・意思決定の意味と、TEIが担う実行可能な業務システムの実現境界が混ざる。

SEIでは、次のような意味を耐久的な中心として扱う。

- Inquiry / Question
- Observation / Unknown / Conflict / Hypothesis
- EvidenceUse / Assurance / Provenance
- Cognitive Method
- Recommendation / Decision / Rationale
- Responsibility
- Capability discovery / choice
- Semantic Lineage / Decision Memory

TEIは、これらの意味を実行へ接続する際のCapability Providerになり得るが、SEIそのものではない。

## Decision

### 1. SEIとTEIを別のProduct Boundaryとして維持する

両者は連携できるが、一方を他方の内部moduleとはみなさない。

```text
SEI
  cognitive / inquiry / decision semantics

        ↓ explicit capability/provider crossing

TEI
  executable business capability realization
```

### 2. SEIはTEI固有の実行lifecycleをUniversal Coreとして所有しない

SEI Coreへ、TEI固有の次のような概念をそのままコピーしない。

- Application Release
- Database Release
- Database Migration lifecycle
- Deployment Run
- Runtime Lease / Fencing
- Plugin packaging
- Provider-specific execution protocol

SEIがこれらを参照する必要がある場合は、Capability、Artifact reference、Observation、Evidence等の境界から扱う。

### 3. TEIはSEIのDecision / Authorityを暗黙に代行しない

SEIにRecommendationやDecisionが存在しても、それだけでTEIの実行権限は成立しない。

```text
SEI Decision
    != TEI Authorization
    != TEI Provider Execution
```

実行へ進む場合は、Profile / Policy / Authorization / Provider boundary等、必要な明示境界を通る。

### 4. TEIをCapability Choiceで特権化しない

TEIは、SEIから見ればCapability Providerの一つである。

人間、SaaS、外部組織、AI、custom code等と同じ判断面で比較できなければならない。

関連する製品であること、開発主体が近いこと、統合しやすいことだけを理由に、TEIへ優先度、信頼、Authorityを付与しない。

### 5. Observation / EvidenceはTEIからSEIへ戻せる

TEIで実行された結果や観測された状態は、SEIのInquiry、Decision review、Capability Observation等の入力になり得る。

ただし、

```text
TEI runtime state != SEI epistemic truth
```

である。

Observationの出所、時点、対象、Assurance等を保持し、必要な認知・判断手続きを経て利用する。

### 6. release / Evidence claimを分離する

TEI側のtest、release、operational evidenceによって、SEI側の未実装Requirementを実装済みとみなさない。

逆も同様である。

各Product Boundaryで、

- Design Evidence
- Executable Evidence
- Release Evidence
- Operational Evidence

を独立して扱う。

### 7. SEIとTEIは独立利用可能であることを保つ

TEIはSEIを必須Runtime dependencyにしない。

SEIもTEIを必須Providerにしない。

統合したときに価値が高まる場合があっても、相互依存をProductの存在条件にはしない。

## Current realization

current SEI repositoryでは、Capability Observationとsynthetic Provider AdapterをTEI非依存でExecutable Evidence化している。

これは、SEIのProvider境界がTEI固有Schemaを前提にしなくても成立することを直接確認するためである。

production TEI adapterはまだ本ADRの成立条件には含めていない。将来TEIを接続する場合も、ADR-0024のProvider Adapter / mapping provenance境界を適用する。

## Consequences

### Positive

- SEIの耐久的中心がworkflow / deployment実装へ引きずられにくい。
- TEIは実行基盤として必要な具体性を保てる。
- TEI以外のCapability Providerを中立に扱える。
- 各Productのrelease / Evidence claimを分離できる。
- AIやProvider技術が変わってもSEIのDecision Memoryを保ちやすい。

### Costs

- 統合時にはArtifact reference、Capability mapping、Observation / Evidence adapter等が必要になる。
- 同じ概念に見えるものでも、SEIとTEIで異なる意味境界を維持する必要がある。
- 「近い製品だから一つのtypeを共有する」という実装上の近道を避ける必要がある。

## Revisit conditions

Product Boundaryそのものは長期原則とする。

具体的な統合Contractは、SEIとTEI双方で必要性とactual Evidenceが揃った段階で、別のADR / Issueとして検討する。

統合Contractを追加しても、本ADRの独立Product Boundaryを自動的にSupersedeしない。

## Natural Japanese review

current SEI Product Value、Capability Observation、Provider Adapter、Evidence boundaryへ戻ってDecisionを照合した。その後、過去のTEI実装詳細を本ADRの根拠として列挙する構成を改め、長期に残すべきProduct Boundaryへ焦点を戻した。SEIとTEIの独立性、非特権化、Decision / Authorization / Execution分離を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
