# ISSUE-000010: M49 Decision Memoryの受入境界を定義する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0010**  
Updated: 2026-08-31

## Goal

M49 production実装へ入る前に、Decision Memoryで守るべき意味差を固定し、Decisionをworkflow、Authority、Executionの入口へ肥大化させない。

## Resolution

Planning levelで、次を受入境界として確定した。

```text
Recommendation != Decision != Authority != Action Intent != Execution
```

Decisionはcontext / basisを参照でき、Decision時点に残っていたUnknown / Conflict / Question等を未解決のまま保持できる。外在化rationaleを許すがprivate chain-of-thoughtを要求しない。Decision maker等の責任はResponsibilityStatementで表し、後続Decisionは既存Semantic Lineageで追跡する。

RecommendationなしのDecision、Decisionへ至らないRecommendationも許す。

意味境界はADR-0010へ確定したため、本IssueはResolvedとする。

## Evidence state

受入Scenarioとplanning fixtureはhistorical / local planning materialとして作成済みだが、これはactual repositoryのproduction executable evidenceではない。

M49 Go type、wire schema、persistence、Authority crossingを実装したことにはならない。

```text
Planning boundary accepted != production implementation complete
```

## Follow-up

参照役割はISSUE-000011 / ADR-0011、明示量はISSUE-000012 / ADR-0005へ分離した。

actual production implementationはrepository baseline materializationとM48 integration確認後の別作業として扱う。

ResolvedというStatusは、Decision Memoryのplanning boundaryが確定したことだけを表す。

## Natural Japanese review

M49 planning closure、ADR-0010、現在のEvidence levelへ戻して内容を照合し、Statusと実装状態を分離した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
