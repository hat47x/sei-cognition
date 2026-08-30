# ADR-0011: Decision Memoryの参照役割を意味上分離する

Status: **Accepted**  
Related Issue: **ISSUE-000011**  
Updated: 2026-08-31

## Context

Decisionが複数のArtifactを参照するとき、それらを無印の`refs[]`へ平坦化すると、「案件の背景として見ていたもの」と「実際に判断根拠として考慮したもの」と「未解決のまま残したもの」を区別できなくなる。

一方、参照役割を固定的な巨大taxonomyへすると、実装形式が意味設計を支配する。

## Decision

Decision Memoryでは、少なくとも次の意味役割を区別可能にする。

- `context` — Decisionを理解するための枠組み・対象・Goal / Intent等。必ずしも判断根拠として採用したとは限らない。
- `basis` — Decision形成時に明示的に考慮したArtifact。
- `recommendation` — 採用・不採用・保留等の対象となったRecommendation。
- `unresolved` — Decision時点でも未解決のまま残っていたUnknown、Conflict、Question等。

この決定はGo field名やwire enumを固定するものではない。内包field、relation record、hybrid等の実現方式はactual implementationで決める。

### 一つのArtifactが複数役割を持てる

役割は排他的taxonomyではない。Constraintが`context`かつ`basis`であってよく、Recommendationが実際に考慮されたなら`recommendation`かつ`basis`であってよい。

### basisとEvidenceUseを同一視しない

Decision basisにはConstraint、Goal、Recommendation、Assurance、Method output等も入り得る。

```text
Decision Basis Role != EvidenceUse
```

既存EvidenceUseをbasisとして参照できるが、すべてのbasisをEvidenceUseへ変換することは要求しない。

### unresolved参照は状態を変更しない

Unknown等を`unresolved`として参照しても、その真偽や解消状態は変わらない。

### Recommendation参照は採用を意味しない

DecisionがRecommendationを参照したことだけから`accepted=true`等を推論しない。採否はDecisionのsemantic contentまたは明示relationで表す。

### 歴史再構成には必要なexact contentを保持する

Decision Memoryが当時の判断を再構成すると主張する場合、当時参照した可変Artifactの内容を必要に応じてExactArtifactBinding等で特定できなければならない。

## Consequences

- 同じDecision textでも、異なる判断経路を区別しやすい。
- EvidenceUse、Responsibility、Semantic Lineage、Authorization等の既存relationと役割分担できる。
- 実装はquery ergonomicsやserializationを見ながら選べる。

## Natural Japanese review

M49 Decision Reference Rolesとacceptance planningへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
