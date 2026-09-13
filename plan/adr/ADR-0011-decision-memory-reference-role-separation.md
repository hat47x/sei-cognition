# ADR-0011: Decision Memoryの参照役割を意味上分離する

Status: **Accepted**  
Related Issue: **ISSUE-000011**  
Updated: 2026-08-31

## Context

Decisionが複数のArtifactを参照するとき、それらを無印の`refs[]`へ平坦化すると、「案件の背景として見ていたもの」「実際に判断根拠として考慮したもの」「未解決のまま残したもの」を後から区別できなくなる。

一方で、参照役割を巨大な固定taxonomyへすると、wire formatや実装上の都合が意味設計を支配しやすい。

## Decision

Decision Memoryでは、少なくとも次の意味役割を区別できるようにする。

- `context` — Decisionを理解するための枠組み、対象、Goal / Intent等。判断根拠として採用したとは限らない。
- `basis` — Decision形成時に、判断材料として明示的に考慮したArtifact。
- `recommendation` — 採用、不採用、保留等の判断対象となったRecommendation。
- `unresolved` — Decision時点でも未解決のまま残っていたUnknown、Conflict、Question等。

これらは意味上の役割であり、特定のGo field名やwire enumを恒久的に固定するための決定ではない。

### 一つのArtifactが複数の役割を持ってよい

参照役割は排他的taxonomyではない。たとえばConstraintが`context`かつ`basis`であってよい。Recommendationが実際の判断材料になった場合は、`recommendation`かつ`basis`として扱ってもよい。

### basisとEvidenceUseを同一視しない

Decision basisにはConstraint、Goal、Recommendation、Assurance、Method output等も含まれ得る。

```text
Decision Basis Role != EvidenceUse
```

既存のEvidenceUseをbasisとして参照することはできるが、すべてのbasisをEvidenceUseへ変換することは要求しない。

### unresolvedとして参照しても元の状態を変えない

Unknown等を`unresolved`として参照したことだけで、その真偽や解消状態を変更しない。

### Recommendationへの参照は採用を意味しない

DecisionがRecommendationを参照したことだけから、`accepted=true`等を推論しない。採用、不採用、保留等はDecisionのsemantic contentまたは明示されたrelationから読み取る。

### 歴史再構成に必要なexact contentを保持する

Decision Memoryが当時の判断を再構成すると主張する場合、当時参照した可変Artifactについては、必要に応じてExactArtifactBinding等で内容を特定できなければならない。

## Current realization

current `sei.decision-memory/v1alpha1`では、`context_refs`、`basis_refs`、`recommendation_refs`、`unresolved_refs`を別の参照集合として表現できる。

first semantic runtimeもこの区別を保ったまま読み込む。current fixtureでは、Recommendationだけが存在してDecisionへ至らない状態と、unresolved refを残したDecisionの双方を正常な状態として扱えることを確認している。

これは参照役割のcurrent wire realizationであり、将来のmajor Contract変更でも同じfield名を恒久固定するという意味ではない。

## Consequences

- 同じDecision statementでも、どのような材料と未解決事項の下で判断したかを区別しやすい。
- EvidenceUse、Responsibility、Semantic Lineage、Authorization等と役割を分担できる。
- 実装は意味境界を保つ範囲で、queryやserializationの形を改善できる。

## Revisit conditions

現在の参照役割では、実際の複数ScenarioでDecision時点の背景、根拠、Recommendation、未解決事項を十分に再構成できないことが確認された場合に再検討する。

## Natural Japanese review

current Decision Memory Contract、fixture、first semantic runtimeへ戻ってDecisionを照合した。その後、旧Milestone名に依存した説明をcurrent realizationへ置き換え、参照役割の意味差、非排他性、EvidenceUseとの分離を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後にEvidence強度を含めて意味監査を実施済みである。
