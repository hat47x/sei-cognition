# ISSUE-000013: Capability Choiceの受入境界を定義する

Status: **Resolved**  
Priority: **3**  
Related ADRs: **ADR-0012, ADR-0013**  
Updated: 2026-08-31

## Goal

人間、SaaS、外部組織、AI、TEI、custom code等の異質な手段を、SOZAが中立に比較・選択するための意味境界をpressure testする。

historical M50で検討した内容をcurrent Product / Requirementsへ再統合し、Milestone label自体はcurrent Architectureの正本にしない。

## Resolution

次を固定した。

```text
Capability Definition != Observation != Matching
Matching != Recommendation != Decision
Capability != Provider
Capability Choice Decision != Authority != Execution
Unknown != incompatible
```

Universal score、automatic best-candidate ranking、TEI preference、exactly-one choiceをCoreへ導入しない。

MatchingだけでDecisionを作らない状態、複数Capabilityを組み合わせるDecision、Provider未確定のChoice、Unknownが大きくChoiceを保留する状態を正常に扱う。

過去Choiceは当時のObservation / Definition等へ必要に応じてexact-bindし、後日の変更で黙って書き換えない。

Capability Realization / OfferingのUniversal型要否はISSUE-000014で検討し、ADR-0013で「現時点では追加しない」と確定した。

## Current evidence state

historical planning fixtureのEvidenceをcurrentへ自動継承せず、current repositoryの実績で読み替える。

- Capability Choice semantic boundary: **Satisfied — ADR-0012 / ADR-0013**
- Provider-neutral Capability Observation Contract / Schema: **Satisfied**
- Capability Observation F1〜F7 fixture-scoped Executable Evidence: **Satisfied**
- synthetic cross-Provider Adapter mapping: **Satisfied within ISSUE-000036 scope**
- Matching / Recommendation generationのExecutable Evidence: **Not Yet Verified**
- Capability Choice DecisionのProduction Executable Evidence: **Not Yet Verified**
- Release / Operational Evidence: **Not Yet Verified**

current Requirementでは主にREQ-0007、REQ-0021、REQ-0022へ接続する。

```text
Observation / Adapter PASS
  != Matching implemented
  != Choice Decision implemented
```

本Issueの`Resolved`はCapability Choiceの意味境界が確定したことを示す。current Observation / Adapter層にExecutable Evidenceが増えたことを理由に、MatchingやChoice Decisionまで実装済みとは主張しない。

## Natural Japanese review

ADR-0012 / ADR-0013、REQ-0007 / 0021 / 0022、Capability Observation Contract、F1〜F7、synthetic Provider Adapter Evidenceへ戻って内容を照合した。その後、historical planningとcurrent Evidenceを分け、意味・留保・未実装範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
