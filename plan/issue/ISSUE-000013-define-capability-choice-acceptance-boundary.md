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

## Evidence state

planning fixture 12件で境界を検査したが、SOZA-PR-007は`design_only`を維持する。local executable evidence、operational evidenceともに0として扱う。

Capability Realization / OfferingのUniversal型要否は後続ISSUE-000014で検討し、ADR-0013で「現時点では追加しない」と確定した。

したがって、本Issueの`Resolved`は**Capability Choiceのplanning / semantic boundaryが確定したこと**を示し、production implementationの完了を示さない。

## Natural Japanese review

StatusとEvidence状態を分離したうえで、M50 planning closure、ADR-0012 / ADR-0013へ戻して内容を照合し、意味、留保、未実装範囲を変えず、自然な日本語となることを最重要視して全文を再確認した。最終意味監査も実施済み。
