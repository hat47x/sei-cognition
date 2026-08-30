# ISSUE-000003: ArtifactをまたぐSemantic Revisionを設計する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0003**  
Updated: 2026-08-31

## Goal

Question、Observation、Hypothesis、Constraint、Capability、Method、Decision等の改訂を、storageのversion番号へ依存せず共通に追跡できる最小意味モデルを定める。

## Investigation

Observationの訂正、Hypothesisの精緻化、Constraint変更によるDecision見直し、Capability情報の陳腐化、Method Definitionの変更等を比較した。

単一`version`や巨大なrevision taxonomyではなく、logical identity、exact content binding、semantic lineage、representation / storage revisionを分離する構造が最も意味を保ちやすいと判断した。

## Resolution

Universal Semantic Lineageの最小語彙を`revises / supersedes / withdraws`とし、branch、merge、scope別の後継を許す。storage revisionからlineageを自動推定しない。

判断はADR-0003へ確定したため、本IssueはResolvedとする。

## Natural Japanese review

Revision architectureへ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
