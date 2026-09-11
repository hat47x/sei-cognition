# ISSUE-000007: Semantic Persistence Contractを定義する

Status: **Resolved**  
Priority: **7**  
Related ADRs: **ADR-0007**  
Updated: 2026-08-31

## Goal

Git、RDB、object store、event sourcing等の特定実装をSEI Coreへ固定せず、DecisionやMethod Application、Provenance、Semantic Lineageを長期に保持するための意味上の永続化契約を定める。

## Investigation

logical identity、exact content binding、lineage、provenance、schema migration、portable export、large binary、retention、physical deletion、concurrent update等を比較した。

## Resolution

SEIはstorage-neutralなsemantic persistence obligationsを定め、物理layout、transaction方式、MVCC、replication、backup等はProviderへ委ねる。

物理deleteとsemantic withdrawal、schema migrationとsemantic revision、storage sequenceとSemantic Lineageを同一視しない。

判断はADR-0007へ確定したため、本IssueはResolvedとする。

## Natural Japanese review

Persistence architectureへ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
