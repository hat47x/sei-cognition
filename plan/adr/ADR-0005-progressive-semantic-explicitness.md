# ADR-0005: Progressive Semantic ExplicitnessをProfile / Policyで実現する

Status: **Accepted**  
Related Issues: **ISSUE-000005, ISSUE-000012**  
Updated: 2026-08-31

## Context

SOZAの意味境界は重要だが、すべての作業へ同じ重い記録を要求すると利用不能になる。

低影響で可逆な下書き修正と、金銭・法務・安全・外部変更を伴う判断では、必要な記録の厚さが異なってよい。一方、「AIが十分自信を持っている」という理由だけで重要な境界を省略すると、監査可能性や責任線が静かに失われる。

## Decision

Progressive Semantic Explicitnessを採用する。

Universal Coreには意味語彙と不変条件を置き、案件ごとに必須とするArtifact / relationは、**Profile + Policy + Profile Resolution**で組み立てる。

Coreへ次のUniversal fieldや単一尺度を追加しない。

- `risk_score`
- `explicitness_level`
- `requires_approval`
- fixed workflow level

Profileは追加可能だが、Coreの意味を緩和・上書きしてはならない。

```text
Profile追加
  != RecommendationのDecision昇格
  != DecisionのAuthority昇格
```

Profileを複数適用する場合、同じ義務の重複は避け、相互に両立しない義務はresolution時に露出させる。

M49 Decision Memoryでも同じ機構を再利用し、basis、unresolved、rationale、responsibility、exact historical input等の明示量をobligation bundleとして選べるようにする。新しいUniversal Decision levelは作らない。

## Consequences

- 軽量な作業を官僚化しにくい。
- 高影響案件ではPolicyに基づいて必要な境界を要求できる。
- 一つのrisk scoreへ異質な意味を潰さずに済む。
- Profile / Policyの設計と説明可能なresolutionが必要になる。

## Revisit conditions

Profile / Policy方式では高影響案件の必須境界を安全に要求できない、または低影響案件の負担を十分に抑えられないことがactual useで反復して確認された場合に再検討する。

## Natural Japanese review

Progressive Semantic Explicitness architecture baselineとM49 specializationへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
