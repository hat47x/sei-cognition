# ISSUE-000013: Capability Choiceの受入境界を定義する

Status: **Resolved**  
Priority: **3**  
Related ADRs: **ADR-0012, ADR-0013**  
Updated: 2026-08-31

## Goal

人間、SaaS、外部組織、AI、TEI、custom code等の異質な手段を、SOZAが中立に比較・選択するための意味境界を、実装前にpressure testする。

## Resolution

Planning levelで次を固定した。

```text
Capability Definition != Observation != Matching
Matching != Decision
Capability != Provider
Capability Choice Decision != Authority != Execution
Unknown != incompatible
```

Universal score、automatic best-candidate ranking、TEI preference、exactly-one choiceをCoreへ導入しない。

MatchingだけでDecisionを作らない状態、複数Capabilityを組み合わせるDecision、Provider未確定のChoice、Unknownが大きくChoiceを保留する状態を正常に扱う。

過去Choiceは当時のObservation / Definition等へ必要に応じてexact-bindし、後日の変更で書き換えない。

意味境界はADR-0012へ、Capability Realization / Offeringを現時点でUniversal Coreへ追加しない判断はADR-0013へ確定したため、本IssueはResolvedとする。

## Evidence state

planning fixture 12件で境界を検査したが、これはhistorical / local planning evidenceである。

SOZA-PR-007は`design_only`を維持し、actual repositoryのlocal executable evidence、operational evidence、adoption / outcome evidenceが得られたことを意味しない。

```text
Planning fixture PASS != actual executable conformance
```

## Follow-up

Provider-neutral Capability Observationの意味境界はADR-0019でさらに具体化した。

actual contract / fixtureはISSUE-000025で扱い、ISSUE-000022のrepository baseline materializationが進むまでBlockedとする。

ResolvedというStatusは、Capability Choiceのplanning boundaryが確定したことだけを表す。

## Natural Japanese review

M50 planning closure、ADR-0012 / ADR-0013 / ADR-0019、現在のEvidence levelへ戻して内容を照合し、Statusと実装状態を分離した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
