# ISSUE-000005: Progressive Semantic Explicitnessを設計する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0005**  
Updated: 2026-08-31

## Goal

軽量な作業を過度に官僚化せず、高影響・高不確実な作業では必要な意味境界を省略しない仕組みを設計する。

## Investigation

下書き整形、read-only research、外部送信、SaaS設定変更、金銭支出、法的・安全上高影響な操作、Conflictを残したDecision等を比較した。

固定levelや単一risk scoreでは異質な意味を潰しやすく、AI自身のconfidenceに省略判断を任せるのも不適切と判断した。

## Resolution

Universal Coreは意味境界を定義し、案件ごとの必須Artifact / relationはProfile + Policy + Profile Resolutionで決める。ProfileはCore意味を緩和せず、DecisionやAuthorityを自動昇格させない。

M49 Decision Memoryでも同じ機構を再利用する。判断はADR-0005へ確定したため、本IssueはResolvedとする。

## Natural Japanese review

Progressive Explicitness architectureと後続M49設計へ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
