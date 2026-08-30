# ADR-0010: Decision Memoryの最小Semantic Boundaryを定める

Status: **Accepted**  
Related Issue: **ISSUE-000010**  
Updated: 2026-08-31

## Context

SOZAは、最終結果だけでなく、あるDecisionが何を根拠とし、何を未解決のまま残していたかを後から再構成できる必要がある。

M48までにObservation、Unknown、Conflict、Hypothesis、EvidenceUse、Derivation、Responsibility、Semantic Lineage等の下地は整った。一方、Decision Memoryを実装順序から設計すると、RecommendationをDecisionへ自動昇格させたり、DecisionをAuthorizationやExecution triggerへ変えたりする危険がある。

## Decision

### RecommendationとDecisionを別の意味として扱う

Recommendationは選択肢・提案であり、Decisionは何を採る、採らない、保留する等を判断した記録である。

```text
Recommendation != Decision
```

RecommendationはDecisionの必須前段ではない。RecommendationなしのDecisionも、Decisionへ至らないRecommendationも正常な状態として扱う。

### Decision時点のbasisと未解決状態を再構成できる

Decisionは、必要に応じてGoal、Intent、Constraint、Observation、Hypothesis、Recommendation等の参照を辿れるようにする。

Decision時点で残っていたUnknown、Conflict、Question等も保持できなければならない。

```text
Decision exists
  != Unknown resolved
  != Conflict resolved
```

### rationaleは外在化された説明とする

人間やAIが後からレビューできる短い判断説明を保持できる。ただし、モデル内部のtoken-by-token reasoningやprivate chain-of-thoughtを保存・復元することは要求しない。

### ResponsibilityとAuthorityを分ける

誰または何がDecisionを担ったかは`ResponsibilityStatement`で結ぶ。Decision型へGlobal Principal、role hierarchy、Authorizationを埋め込まない。

```text
Responsibility != Authorization
Decision != Authority != Action Intent != Provider Execution
```

### Decision revisionには既存Semantic Lineageを使う

後のObservation等によりD1からD2へ判断が変わる場合、旧Decisionをlatest-winsで消さず、ADR-0003のSemantic Lineageを再利用する。

## Consequences

- AI提案と組織Decisionの責任線を分けられる。
- 不確実性を残したDecisionを正直に記録できる。
- 過去Decisionを現在の知識で上書きしにくい。
- Decisionの具体wire schemaやpersistenceは別途実装設計が必要になる。

## Implementation status

このADRは意味境界をAcceptedとするが、M49 production Go type、wire schema、persistence、Authority crossingが実装済みであることを意味しない。

## Natural Japanese review

M49 acceptance planningとDecision Memory architectureへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
