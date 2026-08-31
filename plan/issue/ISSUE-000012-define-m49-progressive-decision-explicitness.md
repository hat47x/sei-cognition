# ISSUE-000012: historical M49 Decision MemoryのProgressive Explicitnessを具体化する

Status: **Resolved**  
Priority: **4**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0011**  
Updated: 2026-08-31

## Goal

Decision Memoryへ常に最大量の記録を要求せず、監査・安全・高影響案件では必要な情報をProfile / Policyから要求できるようにする。

historical M49はこの検討が行われた設計史上のMilestone labelであり、current実装フェーズを意味しない。

## Resolution

新しいUniversal Decision levelやnumeric risk scoreは追加しない。

ADR-0005のProfile / Policy機構をDecision Memoryでも再利用し、明示量をobligation bundleとして選べる設計とする。

候補には、Decision、basis、考慮したRecommendation、存在するunresolved、rationale、responsibility、exact historical inputs、replacement時のlineage等を含む。

ProfileはCore boundaryを緩和せず、Profile適用や要件充足からAuthorityを推定しない。`unresolved` obligationも、存在しないUnknownを捏造することを要求しない。

この判断はcurrent Decision Memory Contractへ継承され、各参照やrationale等を必要に応じて表現できる。ただしcurrent v1alpha1 Schemaでfieldがoptionalであることだけを、Profile / Policy obligation resolutionがproduction実装済みであることとはみなさない。

## Current evidence

- Progressive Explicitness Design boundary: **Satisfied**
- Decision Memory v1alpha1での段階的な表現余地: **Satisfied**
- Profile / Policy obligation resolutionのProduction Executable Evidence: **Not Yet Verified**
- Release / Operational Evidence: **Not Yet Verified**

## Natural Japanese review

ADR-0005、ADR-0010 / 0011、current Decision Memory Contract / Schemaへ戻って内容を照合した。その後、historical Milestoneとcurrent正本、表現上のoptional性とPolicy実行を区別し、意味・条件・Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
