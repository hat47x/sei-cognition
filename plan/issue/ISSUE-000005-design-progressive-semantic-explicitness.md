# ISSUE-000005: Progressive Semantic Explicitnessを設計する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0005**  
Updated: 2026-08-31

## Goal

軽量な作業を過度に官僚化せず、高影響・高不確実な作業では必要な意味境界を省略しない仕組みを設計する。

## Investigation

下書き整形、read-only research、外部送信、SaaS設定変更、金銭支出、法的・安全上高影響な操作、Conflictを残したDecision等を比較した。

固定levelや単一risk scoreでは異質な意味を潰しやすく、AI自身のconfidenceだけに省略判断を委ねるのも不適切と判断した。

## Resolution

Universal Coreは意味境界を定義し、案件ごとの必須Artifact / relationはProfile + Policy + Profile Resolutionで決める。ProfileはCoreの意味を緩和せず、DecisionやAuthorityを自動昇格させない。

この判断は、historical M49で検討していたDecision Memoryにも適用され、current `sei.decision-memory/v1alpha1`の意味境界へ引き継がれている。current Contractではcontext / basis / recommendation / unresolved / rationale / responsibility等を必要に応じて保持できるが、すべての案件へ最大量の記録を強制しない。

本IssueがResolvedであることは、このProgressive Semantic Explicitnessの設計原則が確定したことを意味する。Profile / Policy obligation resolutionをproduction runtimeで全面実装済みであることは意味しない。

## Current evidence

- Design boundary: Satisfied
- Decision Memory Contractでのoptional representation: Satisfied
- Profile / Policy obligation resolutionのProduction Executable Evidence: Not Yet Verified
- Release / Operational Evidence: Not Yet Verified

## Natural Japanese review

ADR-0005、current Decision Memory Contract、Requirements、first runtime baselineへ戻って内容を照合した。その後、Progressive Semantic Explicitnessの意味、未実装範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
