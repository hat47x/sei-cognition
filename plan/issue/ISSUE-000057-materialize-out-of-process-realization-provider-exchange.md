# ISSUE-000057: out-of-process Realization / Provider exchange probeを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0017, ADR-0019, ADR-0024, ADR-0025**  
Updated: 2026-09-01

## Goal

PMS-06について、同一process内のsynthetic Adapterやtyped Contractの検査から一段進み、**SEI runtimeとは別のOS processとして動くCognitive Method RealizationとProvider state sourceを交換しても、同じcanonicalな判断記憶を保てること**をreference probeで確認する。

production AI、外部SaaS、TEIをCI必須依存にはせず、まずprocess boundaryそのものを実証する。

## Resolution

`runtime/go/realizationprobe`と二つのreference executableを実体化した。

```text
SEI canonical runtime
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

## 実装した要素

- `runtime/go/cmd/sei-reference-provider`
  - profile A / Bを別OS processとして実行する。
  - A / Bは異なるProvider固有state shapeを返す。
- `runtime/go/cmd/sei-reference-method`
  - `evidence-first` / `cautious`の二つのMethod Realizationを別OS processとして実行する。
  - 同じMethod Definitionに対し、異なるRecommendation候補を返す。
- `runtime/go/realizationprobe`
  - reference executableを実際にbuild・起動する。
  - Provider固有stateを既存Provider Adapterへ渡す。
  - Method outputをRecommendation / Method Applicationへ戻す。
  - historical Decision非改変とnegative caseを検査する。
- `runtime/go/interactionprobe`
  - existing Cognitive Method Contractにすでにある`realization_ref`をMethod Applicationへ渡せるようにした。
  - 既存Interaction Surface APIとProjection behaviorは維持した。

## 必須検査の結果

1. **Provider A / Bを別OS processとして起動できる** — Satisfied。
2. **A / Bが異なるProvider固有state shapeを返せる** — Satisfied。
3. **別Provider identityのまま同じCapabilityへmappingできる** — Satisfied。
4. **Capability Observationをcurrent validatorへ戻せる** — Satisfied。
5. **同じMethod Definitionに対する二つのMethod Realizationを別processで実行できる** — Satisfied。
6. **Method Applicationに各`realization_ref`を保持できる** — Satisfied。
7. **異なるRecommendationを生成してもDecisionと同一視しない** — Satisfied。
8. **Provider / Method交換後も交換前Decisionを変更しない** — Satisfied。Decisionのbasis、Recommendation、Responsibility、unresolvedを保持した。
9. **failed Provider / Method processからcanonical recordを生成しない** — Satisfied。失敗前後のcanonical digestが一致する。
10. **process-local protocolやbinary identityをUniversal semantic identityへ昇格させない** — Design / implementation boundaryとして維持した。

## CI Evidence

初期実装では、Contract fixture 31件はPASSした一方、Interaction probeの既存表示用型とAPIを全文置換時に落としたcompile regressionが見つかった。これは新しいRealization exchangeの意味設計ではなく、既存Surface APIの回帰であったため、既存`surface.go`を正として復元し、`realization_ref`対応だけを最小差分として残した。

修正後head `91a0ce468a1cbf30cc8ad4deab4392dc0f41250e`では、次がすべて**success**した。

- Semantic Runtime Conformance Run `33516101445`
- Plan integrity Run `33516101074`
- Local Package Artifact Run `33516100947`

Semantic Runtime Conformanceには、current Contract fixture 31件の再検査と`runtime/go`全体の`go test ./...`が含まれる。新しい`realizationprobe`に加え、Interaction、Access、Packaging、Provider Adapter、journey harness、semantic runtimeの回帰も同じRunで確認した。

その後、ISSUE-000057を`Resolved`へ揃え、plan registryを同期したclosure準備head `b102e6193d9b04648ae0b7fb5f30a89be9d5293f`でも、次の3系統がすべて**success**した。

- Plan integrity Run `33516659352`
- Semantic Runtime Conformance Run `33516659340`
- Local Package Artifact Run `33516659432`

この追加確認により、実装・上流文書・Issue status・plan registryを揃えた状態でも、E2 probeと既存回帰が同時に成立することを確認した。

## Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しない。

今回確認した失敗は、既存の次で十分に表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

out-of-process化はEvidenceを厚くするreference Realizationであり、それ自体を新しいProduct Requirementにはしない。

## PMS-06への反映

PMS-06のEvidence ladderを次のように整理した。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3 real external integration
  → E4 operational portability
```

今回のprobeによりE2にはScoped Executable Evidenceが成立した。

一方、reference executableはSEI repository内でbuildする評価用Realizationであり、実AI、実SaaS、TEI production instanceではない。したがってE3 / E4は引き続き未検証である。

## Non-goals / 未検証範囲

- production AI API integration
- external SaaS credential / rate limit / SLA integration
- TEI production integration
- production network protocolの標準化
- gRPC / HTTP / MCP / stdio等の正式Realization protocol選定
- process-local JSONをUniversal Contractへすること
- Realization出力を自動Decisionへ昇格させること
- production credential / secret management
- Operational portability
- Release / Adoption / Outcome Evidence

## 完了条件

- [x] Method Applicationから`realization_ref`を保持できるreference interaction pathを用意する。
- [x] reference Provider A / Bのprocess state sourceを実体化する。
- [x] reference Method A / Bを別processとして実体化する。
- [x] current Provider Adapter / Capability Observation validatorへ戻す。
- [x] Provider / Method交換後のhistorical Decision非改変をtestへ落とす。
- [x] failed processがcanonical sourceを変更しないnegative caseをtestへ落とす。
- [x] CIで再現可能なExecutable Evidenceを得る。
- [x] PMS-06 / Product文書へ結果を同期する。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied**
- E1 Contract / synthetic exchange: **Scoped Executable Evidence available**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available** — closure準備headを含むSemantic Runtime Conformance Run `33516659340`
- E3 real external AI / SaaS / TEI: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- real external Providerでprocess-local reference profileでは表現できない独立した意味不足が確認された。
- Method Realization version交換時にcurrent `realization_ref`だけではhistorical reconstructionを保てない。
- Provider交換時にCapability identityやmapping provenanceを保持できない。
- E3で既存REQ / SCNでは表現できないProduct failureが確認された。

## Natural Japanese review

PMS-06、`product/definition/SEI_REALIZATION_PROVIDER_EXCHANGE.md`、REQ-0001 / 0004 / 0005 / 0007 / 0021、SCN-0005 / 0014 / 0018、ADR-0013 / 0017 / 0019 / 0024 / 0025、current Cognitive Method runtime、Provider Adapter、`runtime/go/realizationprobe`のactual test、Semantic Runtime Conformance Run `33516101445`、closure準備head `b102e6193d9b04648ae0b7fb5f30a89be9d5293f`の3系統CIを照合した。同一process内のsynthetic交換から別OS processのreference exchangeへEvidenceを一段進めつつ、reference executableの成功を実AI / SaaS / TEI連携やOperational portabilityへ広げていない。RecommendationとDecision、ProviderとCapability、Method DefinitionとRealization、current Observationとhistorical basisの境界も維持した。そのうえで、目的、検査結果、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。