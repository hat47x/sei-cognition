# ISSUE-000037: Requirement Evidenceを5段階へ再整合する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020**  
Updated: 2026-08-31

## Goal

Product Valueで正式化したEvidence境界を、current Product Requirementsへ一貫して反映する。

監査開始時点では、`requirements/PRODUCT_REQUIREMENTS.md`のRequirementごとのEvidence欄に`Release / Operational`をまとめた旧表記が残り、synthetic Provider Adapter sliceがExecutable Evidenceへ到達した後も、REQ-0007、REQ-0016、REQ-0021、REQ-0022の一部記述がその到達点を十分に反映していなかった。

本Issueでは、Requirementの意味・Status・受入れ強度を変えず、Evidenceの高さと現在地だけをactual repositoryへ再整合した。

## Resolution

### 1. Evidenceを5段階で分離した

current `requirements/PRODUCT_REQUIREMENTS.md`では、少なくとも次を別々に扱う。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Requirementの採用状態とEvidenceの高さも分離している。

```text
Requirement Accepted
  != Design Evidence Satisfied
  != Executable Evidence Satisfied
  != Release Evidence Satisfied
  != Operational Evidence Satisfied
  != Adoption / Outcome Evidence Satisfied
```

`Release / Operational`を一つの状態へまとめない。

### 2. 未検証領域を昇格させていない

文書整合だけを理由に`Not Yet Verified`を`Satisfied`へ上げていない。

とくに次は引き続き未検証である。

- production Provider integration / interoperability
- production Storage migration
- release artifactでのRequirement Acceptance
- production operationでのOperational Acceptance
- 実利用によるAdoption / Outcome Acceptance

```text
fixture / runtime CI PASS
  != whole Requirement satisfied
  != Provider production integration
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### 3. synthetic Provider Adapterの限定Executable Evidenceを反映した

ADR-0024 / ISSUE-000036で得られたfixture-scoped Executable Evidenceを、少なくとも次へ反映した。

- REQ-0007 — Capability / Providerの中立性
- REQ-0016 — ObservationとInterpretationの区別
- REQ-0021 — Realization / Executionの交換可能性
- REQ-0022 — Provider-neutralなCapability Observation

反映した主な事実は次である。

- Provider A / Bの異なるProvider-specific input shapeをAdapter-localに保持できる。
- 同じCapabilityについて異なるProvider identityのObservationへ変換できる。
- status interpretation / unit conversionをmappingとして扱える。
- mapping provenance / source state referenceを保持できる。
- missing値をnegative defaultへ変換せず`unknown`として保持できる。
- Provider-specific fieldをUniversal Capability Observation schemaへ漏らさない。
- Adapter outputをRecommendation / Decision / Authority / Executionへ自動昇格させない。

synthetic Provider A / Bの成功を、TEI / SaaS production interoperabilityへ拡張していない。

### 4. 初回成立Evidenceとcurrent confirmationを分けて保持した

Requirements正本では、Evidenceが最初に成立した履歴として次を残している。

- Semantic Runtime Conformance #3 — Run ID `33348972805`
- synthetic Provider Adapter initial success #4 — Run ID `33349604842`
- Provider-specific field locality hardening #5 — Run ID `33349801993`

これらを最新runへ機械的に置き換えない。初回成立の来歴として意味があるためである。

そのうえで、Product Value traceability baselineを`develop/v0.1.0`へ統合したmerge commit `a8298c7d368031bbddb59efaf63871b00460fb82`について、次のpost-merge CIがすべてsuccessしたことをcurrent confirmationとして確認した。

- Plan integrity #64 — Run ID `33384622267`
- Semantic Runtime Conformance #8 — Run ID `33384622262`
- Contract Conformance #22 — Run ID `33384622298`

したがって、5段階Evidence境界とProduct Value traceabilityの統合後にも、Plan / Contract / Runtimeの既存Executable Evidenceが回帰していないことを確認できる。

このconfirmationもRelease / Operational / Adoption・Outcome Evidenceではない。

### 5. Requirement Status / Design Acceptanceを不要に変更していない

REQ-0001〜REQ-0022のRequirement ID、Status、Value Axis、Design Acceptanceを、Evidence表記の整合だけを理由に変更していない。

今回の作業はRequirementの意味変更ではなく、Evidence vocabularyとactual到達状態の再整合である。

## Acceptance

- [x] `PRODUCT_REQUIREMENTS.md`のEvidence階層が5段階で統一されている。
- [x] REQ-0001〜REQ-0022のStatus / Design Acceptanceを不要に変更していない。
- [x] REQ-0007 / 0016 / 0021 / 0022へsynthetic Provider Adapterの限定Executable Evidenceを反映している。
- [x] production Provider integrationを未検証として維持している。
- [x] Release / Operational / Adoption・Outcomeを個別に`Not Yet Verified`として追跡できる。
- [x] 初回成立runと、Product Value統合後のcurrent confirmation runを区別して追跡できる。
- [x] post-mergeのPlan integrity / Semantic Runtime / Contract CIがすべてsuccessしている。
- [x] 自然な日本語による再ドラフトと最終意味監査を実施した。

## Evidence boundary at closure

本Issueの完了は、Requirements文書とactual Evidenceの整合を意味する。

```text
Requirement Evidence alignment complete
  != whole Requirement implementation complete
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

また、CI runが新しく成功したこと自体をProduct Valueの新しいOutcomeとは数えない。

## Natural Japanese review

Product Valueの5段階Evidence境界、current Product Requirements、ADR-0024 / ISSUE-000036のsynthetic Provider Adapter Evidence、Product Value traceability merge後のactual CIを相互に照合した。Requirement本文の意味、Status、Value Axis、Design Acceptance、未検証領域を変えず、初回成立Evidenceとcurrent confirmationも区別したうえで、自然な日本語となることを最重要視して本Issueを再ドラフトし、最終意味監査を実施済みです。
