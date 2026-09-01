# ISSUE-000057: out-of-process Realization / Provider exchange probeを実体化する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0017, ADR-0019, ADR-0024, ADR-0025**  
Updated: 2026-09-01

## Goal

PMS-06について、同一process内のsynthetic Adapterやtyped Contractの検査から一段進み、**SOZA runtimeとは別のOS processとして動くCognitive Method RealizationとProvider state sourceを交換しても、同じcanonicalな判断記憶を保てること**をreference probeで確認する。

production AI、外部SaaS、TEIをCI必須依存にはせず、まずprocess boundaryそのものを実証する。

## 背景

current repositoryには、次のExecutable Evidenceがある。

- `soza.cognitive-method/v1alpha1`でMethod Definition / Realization / Applicationを分離できる。
- `provideradapter.Adapter`でProvider固有stateからCapability Observationへmappingできる。
- synthetic Provider A / Bを交換できる。
- SCN-0018 harnessでProvider replacementを含む一続きの判断経路を検査できる。

一方、これらの多くは同一process内のfixture / Adapter / harnessである。

PMS-06を進めるには、少なくとも「Realizationを別processへ追い出してもcanonical meaningへ戻せる」ことを確認する必要がある。

## Probe boundary

```text
SOZA canonical runtime
        │
        ├─ process call ─> Method Realization A / B
        │                    │
        │                    └─ recommendation candidate / residual summary
        │
        └─ process call ─> Provider state source A / B
                             │
                             └─ Provider-specific state
                                      │
                                      ▼
                                 Provider Adapter
                                      │
                                      ▼
                             Capability Observation
```

process間のJSON入出力はreference probeのRealization-local protocolであり、Universal Semantic Contractではない。

## 必須検査

1. Provider A / Bを別OS processとして起動できる。
2. A / Bが異なるProvider固有state shapeを返せる。
3. それぞれを別Provider identityとして、同じCapabilityへmappingできる。
4. Capability Observationはcurrent Contract validatorを通る。
5. 同じMethod Definitionに対して、二つのMethod Realizationを別OS processで実行できる。
6. Method Applicationに各`realization_ref`を保持できる。
7. Realization A / Bが異なるRecommendationを生成しても、RecommendationとDecisionを同一視しない。
8. Provider / Methodを交換した後も、交換前Decisionのbasis、Recommendation、Responsibility、unresolvedを変更しない。
9. failed Provider / Method processからcanonical recordを生成しない。
10. process-local protocolやbinary identityをUniversal semantic identityへ昇格させない。

## Requirement / Scenario監査

まず既存の次を利用する。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

reference processを導入したことだけを理由に、新しいStable Requirement / Scenarioは追加しない。

既存Requirementでは表現できない独立したProduct failureが確認された場合だけ上流へ戻す。

## Non-goals

- production AI API integration
- external SaaS credential / rate limit / SLA integration
- TEI production integration
- production network protocolの標準化
- process-local JSONをUniversal Contractへすること
- Realization出力を自動Decisionへ昇格させること
- Release / Operational / Adoption Evidence

## 完了条件

- [x] Method Applicationから`realization_ref`を保持できるreference interaction pathを用意する。
- [x] reference Provider A / Bのprocess state sourceを実体化する。
- [x] reference Method A / Bを別processとして実体化する。
- [x] current Provider Adapter / Capability Observation validatorへ戻す。
- [x] Provider / Method交換後のhistorical Decision非改変をtestへ落とす。
- [x] failed processがcanonical sourceを変更しないnegative caseをtestへ落とす。
- [ ] CIで再現可能なExecutable Evidenceを得る。
- [ ] PMS-06 / Product / Evidence文書へ結果を同期する。
- [ ] Stable Requirement / Scenario追加の要否を再監査する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied for probe plan**
- Executable Evidence: **Not Yet Verified for the new out-of-process probe**
- real external AI / SaaS / TEI Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

PMS-06、REQ-0001 / 0004 / 0005 / 0007 / 0021、SCN-0005 / 0014 / 0018、ADR-0013 / 0017 / 0019 / 0024 / 0025、current Cognitive Method runtimeとProvider Adapterを照合し、同一process内のsynthetic交換から別OS processのRealization交換へEvidenceを一段進める課題として整理した。reference processのJSONやbinary構成をUniversal Contractへ先取りせず、RecommendationとDecision、ProviderとCapability、Method DefinitionとRealizationの境界を維持している。そのうえで、目的、検査条件、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。