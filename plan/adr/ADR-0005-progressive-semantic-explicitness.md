# ADR-0005: Progressive Semantic ExplicitnessをProfile / Policyで実現する

Status: **Accepted**  
Related Issues: **ISSUE-000005, ISSUE-000012**  
Updated: 2026-08-31

## Context

SOZAの意味境界は重要だが、すべての作業に同じ厚さの記録を要求すると、実用性を損なう。

低影響で可逆な下書き修正と、金銭・法務・安全・外部変更を伴う判断では、必要な記録の厚さが異なってよい。一方で、「AIが十分に自信を持っている」という理由だけで重要な境界を省略すると、監査可能性や責任の来歴が静かに失われる。

## Decision

Progressive Semantic Explicitnessを採用する。

Universal Coreには意味語彙と不変条件を置き、案件ごとに必須とするArtifact / relationは、**Profile + Policy + Profile Resolution**によって組み立てる。

Coreには、次のようなUniversal fieldや単一尺度を追加しない。

- `risk_score`
- `explicitness_level`
- `requires_approval`
- fixed workflow level

Profileは追加できるが、Coreの意味を緩和したり上書きしたりしてはならない。

```text
Profile追加
  != RecommendationのDecision昇格
  != DecisionのAuthority昇格
```

複数のProfileを適用する場合、同じ義務を重複して要求することは避ける。一方、互いに両立しない義務がある場合は、Profile Resolutionの段階でその競合を表面化させる。

Decision Memoryでも同じ仕組みを用い、basis、unresolved、rationale、responsibility、exact historical input等について、どこまで明示を要求するかをobligation bundleとして選べるようにする。新しいUniversal Decision levelは作らない。

## Consequences

- 軽量な作業を過度に官僚化しにくい。
- 高影響の案件では、Policyに基づいて必要な意味境界を明示的に要求できる。
- 異質な意味を一つのrisk scoreへ押し込まずに済む。
- Profile / Policyの設計と、なぜそのProfileが適用されたかを説明できるResolutionが必要になる。

## Revisit conditions

Profile / Policy方式では高影響案件に必要な境界を安全に要求できない、または低影響案件の負担を十分に抑えられないことが実際の利用で繰り返し確認された場合に再検討する。

## Natural Japanese review

current Progressive Semantic Explicitness architecture、Profile / Policy境界、Decision Memory Contractへ戻ってDecisionを照合した。その後、Universal risk scoreや固定levelを導入しない判断、ProfileがCoreを緩和しない条件、Resolutionの責務を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
