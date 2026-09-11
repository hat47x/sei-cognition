# ADR-0010: Decision Memoryの最小Semantic Boundaryを定める

Status: **Accepted**  
Related Issue: **ISSUE-000010**  
Updated: 2026-08-31

## Context

SEIでは、最終結果だけでなく、あるDecisionが何を根拠とし、何を未解決のまま残していたかを、後から再構成できる必要がある。

Observation、Unknown、Conflict、Hypothesis、EvidenceUse、Derivation、Responsibility、Semantic Lineage等の認識・来歴の境界があっても、Decision Memoryを実装都合から設計すると、RecommendationをDecisionへ自動昇格させたり、DecisionをAuthorizationやExecution triggerへ変えたりする危険がある。

そこで、Decision Memoryが最低限守る意味境界を先に定める。

## Decision

### RecommendationとDecisionを別の意味として扱う

Recommendationは選択肢や提案であり、Decisionは何を採る、採らない、保留する等を判断した記録である。

```text
Recommendation != Decision
```

RecommendationはDecisionの必須前段ではない。RecommendationなしのDecisionも、Decisionへ至らないRecommendationも正常な状態として扱う。

### Decision時点のbasisと未解決状態を再構成できる

Decisionは、必要に応じてGoal、Intent、Constraint、Observation、Hypothesis、Recommendation等の参照を辿れるようにする。

また、Decision時点で残っていたUnknown、Conflict、Question等も保持できなければならない。

```text
Decision exists
  != Unknown resolved
  != Conflict resolved
```

### rationaleは外在化された説明とする

人間やAIが後からreviewできる、明示された判断説明を保持できるようにする。ただし、モデル内部のtoken-by-token reasoningやprivate chain-of-thoughtを保存・復元することは要求しない。

### ResponsibilityとAuthorityを分ける

誰または何がDecisionを担ったかは`ResponsibilityStatement`等の関係で結ぶ。Decision型へGlobal Principal、role hierarchy、Authorizationを埋め込まない。

```text
Responsibility != Authorization
Decision != Authority != Action Intent != Provider Execution
```

### Decision revisionには既存Semantic Lineageを使う

後のObservation等によってD1からD2へ判断が変わる場合、旧Decisionをlatest-winsで消さず、ADR-0003のSemantic Lineageを再利用する。

## Consequences

- AIによる提案と、人間・組織・その他の主体が担うDecisionの責任線を分けられる。
- 不確実性を残したまま行ったDecisionを、後から正直に再構成できる。
- 過去Decisionを現在の知識で上書きしにくい。
- Decisionを実行へつなぐ場合でも、AuthorityやAction Intent等の別境界を維持する必要がある。

## Current realization and Evidence

current repositoryでは、次が実体化されている。

- `sei.decision-memory/v1alpha1` Contract Definition
- machine-readable schema
- positive / negative boundary fixture
- Contract conformance checker
- first semantic runtimeのDecision / Recommendation read model

current fixture / runtimeでは、少なくとも次をExecutable Evidenceとして確認している。

- Recommendation without Decisionを正常な状態として扱える。
- unresolved refsを残したDecisionを扱える。
- Decisionへ`authority` fieldを直接持ち込むrepresentationを拒否する。
- Semantic Interchange内のDecision basisとExact Bindingの不一致を検出できる。

ただし、これはProductionでのAuthority crossing、Action execution、Release Evidence、Operational Evidenceが完成したことを意味しない。

## Revisit conditions

Decision Memoryの現在の意味境界では、実際の複数Scenarioで判断時点の根拠・未解決事項・責任・改訂来歴を再構成できないことが確認された場合に再検討する。

## Natural Japanese review

current Decision Memory Contract、fixture、first semantic runtime、Responsibility / Authority境界へ戻ってDecisionを照合した。その後、RecommendationとDecisionの分離、不確実性の保存、private chain-of-thoughtを要求しない条件を変えず、旧Milestone依存の説明と未実体化時点のImplementation statusをactual repositoryの現在地へ更新した。最後に自然な日本語となることを最重要視して全文を再ドラフトし、Evidence強度を含めて意味監査を実施済みである。
