# ISSUE-000012: M49 Decision MemoryのProgressive Explicitnessを具体化する

Status: **Resolved**  
Priority: **4**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0011**  
Updated: 2026-08-31

## Goal

Decision Memoryへ常に最大量の記録を要求せず、監査・安全・高影響案件では必要な情報をProfile / Policyから要求できるようにする。

## Resolution

新しいUniversal Decision levelやnumeric risk scoreは追加しない。

ADR-0005のProfile / Policy機構をM49でも再利用し、Decision Memoryの明示量をobligation bundleとして選ぶ。

候補には、Decision Artifact、basis、考慮したRecommendation、存在するunresolved、rationale、responsibility、exact historical inputs、replacement時のlineage等を含む。

ProfileはCore boundaryを緩和せず、Profile適用や要件充足からAuthorityを推定しない。`unresolved` obligationも存在しないUnknownを捏造することを要求しない。

planning fixtureまで完了したため、本IssueはResolvedとする。production implementationは開始していない。

## Natural Japanese review

ADR-0005とM49 planning fixtureへ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
