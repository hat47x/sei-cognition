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

## Evidence state

受入Scenarioとplanning fixtureは作成済みだが、これはproduction executable evidenceではない。

M49 Go type、wire schema、persistence、Authority crossingを実装したことにはならない。

したがって、本Issueの`Resolved`は**planning / semantic boundaryが確定したこと**を示し、production implementationの完了を示さない。

## Follow-up

参照役割はISSUE-000011 / ADR-0011、明示量はISSUE-000012 / ADR-0005へ分離した。

actual production implementationはrepository baseline materializationとM48 integration確認後の別作業として扱う。

## Natural Japanese review

StatusとEvidence状態を分離したうえで、M49 planning closureとADR-0010へ戻して内容を照合し、意味、条件、未実装範囲を変えず、自然な日本語となることを最重要視して全文を再確認した。最終意味監査も実施済み。
