# ISSUE-000037: RequirementsのEvidence層をProduct Value基線へ再整合する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

`requirements/PRODUCT_REQUIREMENTS.md`のEvidence表現を、Product Valueで正式化した5段階のEvidence境界へ再整合する。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

あわせて、first semantic runtime sliceとsynthetic Provider Adapterで既に得られているExecutable Evidenceを、Requirementの意味や達成度を過大に引き上げない範囲で現在地へ反映する。

## Resolution

### 1. Requirementの採用状態とEvidenceの高さを分離した

REQ-0001〜REQ-0022の`Status: Accepted`は変更していない。

RequirementがAcceptedであることから、Executable、Release、Operational、Adoption / Outcomeの成立を推定しない。

### 2. 5段階Evidenceを全Requirementへ適用した

従来まとめて記載していた`Release / Operational`を分離し、各Requirementの`Current Evidence`を次の5段階へ統一した。

- Design
- Executable
- Release
- Operational
- Adoption / Outcome

2026-08-31時点でRelease、Operational、Adoption / Outcomeは、いずれも自動的にSatisfiedへ上げていない。

### 3. synthetic Provider Adapterの既存Evidenceを反映した

ADR-0024 / ISSUE-000036で既に成立したfixture-scoped Executable Evidenceを、主に次へ反映した。

- REQ-0007 — Capability / Providerの中立性
- REQ-0016 — ObservationとInterpretationの分離
- REQ-0021 — Realization / Executionの交換可能性
- REQ-0022 — Provider-neutralなCapability Observation

反映したのは、異なるsynthetic Provider A / Bのinput shape、status interpretation、unit conversion、missing値の`unknown`保持、mapping provenance、source state reference、Provider-specific fieldの非漏洩、Decision / Authority / Executionへの非昇格等である。

### 4. production Provider integrationへは昇格させていない

```text
synthetic Provider Adapter CI PASS
  != production Provider interoperability
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

TEI / SaaS等のproduction Provider接続、実Storage移行、実Execution Provider交換は未検証のまま保持した。

### 5. REQ-0020を5段階Evidenceへ明示的に揃えた

REQ-0020「Evidenceを超える達成主張をしない」は、Design / Executable / Release / Operationalだけでなく、Adoption / Outcomeまで区別する表現へ更新した。

CI成功をreleaseやproduction成立へ昇格させず、production成立を利用者価値の実現へも自動昇格させない。

### 6. current CI参照を現在地へ再基線化した

Requirements本文では、少なくとも次のactual Evidenceを区別して参照する。

- first semantic runtime slice: Semantic Runtime Conformance #3 / Run ID `33348972805`
- synthetic Provider Adapter first success: #4 / Run ID `33349604842`
- Provider-specific field非漏洩hardening: #5 / Run ID `33349801993`

Product Value文書のmerge後CIが成功していることは文書整合の回帰確認であり、新しいRequirement capabilityそのもののEvidenceとは扱わない。

## Acceptance

- [x] REQ-0001〜REQ-0022の採用Statusを変更していない。
- [x] 全RequirementでDesign / Executable / Release / Operational / Adoption・Outcomeを区別した。
- [x] synthetic Provider Adapterの既存Evidenceを該当Requirementへ反映した。
- [x] production Provider integrationをSatisfiedへ上げていない。
- [x] Release / Operational / Adoption・OutcomeをSatisfiedへ上げていない。
- [x] V1〜V8を変更せず、新しいValue Axisを追加していない。
- [x] ADR-0018 / ADR-0020の既存境界を適用し、新ADRを増やしていない。
- [x] Evidenceの意味・強度を変えず、自然な日本語となることを最重要視してRequirements全文を再ドラフトした。
- [x] 最終意味監査を行った。

## Evidence boundary

本IssueのclosureはRequirements文書とEvidence表示の再整合を意味する。

```text
Requirements documentation aligned
  != new runtime capability created
  != release readiness
  != production operation verified
  != user-value realization verified
```

## Natural Japanese review

Product Value、Value Acceptance、ADR-0018、ADR-0020、current Contract / Representation Profile / Runtime、ADR-0024 / ISSUE-000036のsynthetic Provider Adapter Evidenceへ戻って照合した。その後、Requirementの要求強度、Status、留保、Evidenceの高さを変えず、自然な日本語となることを最重要視して`PRODUCT_REQUIREMENTS.md`を全文再ドラフトし、最終意味監査を実施済みです。
