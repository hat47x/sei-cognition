# SOZA Realization / Provider Exchange

更新日: 2026-09-01  
状態: **Current Realization / Provider Exchange Design Baseline**

## 1. この文書の役割

この文書は、PMS-06「実際のMethod / Providerを交換しても判断記憶が保たれる」を進めるために、**何を交換可能とみなし、交換後にも何をcanonicalな判断記憶として守るか**をProduct levelで定めます。

SOZAにとって重要なのは、特定のAI、Prompt、process、SaaS、TEI、custom codeを長く使い続けることではありません。それらが入れ替わっても、当時のIntent、Observation、Method Application、Recommendation、Decision、Responsibility、Provenance、Unknown / Conflictを読み直せることです。

## 2. 交換してよいものと、交換で失ってはならないもの

### 交換してよいもの

- Cognitive Method Realization
- AI model / Prompt / code-assisted tool
- Capability Provider
- Provider Adapter
- external SaaS / TEI / custom code
- process topology
- Realization固有のwire protocol

### 交換で黙って変えてはならないもの

- Method Definitionの意味
- Method ApplicationがどのRealizationを使ったか
- Capability Definitionのidentity
- Capability ObservationがどのProvider / mappingから来たか
- RecommendationとDecisionの区別
- historical Decisionのbasis
- historical Responsibility
- 当時残っていたUnknown / Conflict
- Provenance / residual

```text
Realization exchange
  != Semantic Revision by itself

Provider exchange
  != Capability identity change by itself

new Recommendation
  != historical Decision rewrite
```

## 3. Cognitive Method exchange

同じCognitive Method Definitionに、複数のRealizationを持てます。

```text
Method Definition
   ├─ Realization A
   └─ Realization B
```

Method Applicationは、必要な場合に`realization_ref`を保持します。

Realization AとBが異なる出力を返しても、それは異なるMethod Application / Recommendationとして記録します。後からRealization Bを使ったことを理由に、Realization Aを用いて作られた過去Decisionを現在版へ書き換えません。

Method Realizationの交換は、同じ結論を返すことを要求しません。要求するのは、**どのRealizationを使い、何を入力し、何を出力し、何を残差として残したかを区別して保持できること**です。

## 4. Provider exchange

同じCapabilityに複数Providerを対応させられます。

```text
Capability
   ├─ Provider A
   └─ Provider B
```

Provider固有stateは、そのままSOZA Universal Provider Stateへ統合しません。Provider Adapterを介して、必要な範囲だけをCapability Observationへmappingします。

ProviderをAからBへ変えても、Capability identityを自動的に変更しません。また、新しいProvider Observationが得られても、過去Decisionがbasisとして使ったAのObservationをBへ差し替えません。

## 5. Process boundaryの位置づけ

ISSUE-000057では、SOZA runtimeとは別のOS processとして動くreference Provider / Method Realizationを使います。

これは、同一process内のsynthetic実装より一段強い交換Evidenceを得るための**reference execution profile**です。

```text
out-of-process reference PASS
  != production external Provider proven
```

process間のJSON、command-line flag、binary layoutはprobe-localなRealizationです。これらをSemantic Contractや正式なProduct Interaction protocolへ昇格させません。

## 6. Evidence ladder

PMS-06では、交換可能性のEvidenceを少なくとも次の段階に分けます。

### E1 — Contract / in-process synthetic

- Cognitive Method Definition / Realization / Applicationを型として分離できる。
- synthetic Provider A / BをAdapterで交換できる。

current repositoryでは成立済みです。

### E2 — out-of-process reference exchange

- Method Realizationを別OS processとして交換する。
- Provider state sourceを別OS processとして交換する。
- 出力をcurrent Contract / Adapterへ戻す。
- 交換後もhistorical Decisionを変更しない。

ISSUE-000057の対象です。

### E3 — real external integration

- 実AI / 実SaaS / TEI / external custom service等を接続する。
- credential、network failure、rate limit、version change等を含む現実の交換条件を扱う。

**Not Yet Verified.**

### E4 — operational portability

- 実運用でRealization / Providerを交換し、利用者が判断記憶を継続利用できる。

**Not Yet Verified.**

## 7. Acceptanceの中心

交換の成功を「どちらでも同じ文字列が返った」とは定義しません。

次を中心に検査します。

1. 同じMethod Definitionに異なるRealization Refを結べる。
2. 同じCapabilityに異なるProvider Refを結べる。
3. Realization / ProviderごとのProvenanceを保持できる。
4. 新しいRecommendationを過去Decisionへ自動反映しない。
5. 新しいProvider Observationを過去basisへ自動差し替えしない。
6. failed Realization / Providerがcanonical sourceを中途半端に変更しない。
7. process / binary / vendorのidentityをsemantic identityへ短絡させない。

## 8. Requirement / Scenario

現時点では、新しいStable Requirement / Scenarioを追加しません。

主な既存正本は次です。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

out-of-process化はEvidenceを厚くするための実証であり、それ自体を新しいProduct Requirementにはしません。

## 9. 現時点で固定しないこと

- production AI Provider
- production SaaS / TEI integration protocol
- gRPC / HTTP / MCP / stdio等の正式Realization protocol
- process isolationを全Realizationへ強制すること
- Plugin SDKの正式仕様
- Provider discovery / marketplace
- retry / circuit breaker / queue方式
- secret management
- billing / rate limit model
- production Provider SLA

## 10. Evidence状態

- Contract / synthetic exchange: **Scoped Executable Evidence available**
- out-of-process reference exchange: **Implementation prepared / CI Evidence pending**
- real external AI / SaaS / TEI exchange: **Not Yet Verified**
- Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 11. 関連文書

- `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/issue/ISSUE-000057-materialize-out-of-process-realization-provider-exchange.md`
- `../../plan/adr/ADR-0013-capability-realization-boundary.md`
- `../../plan/adr/ADR-0017-reference-model-cognitive-method-boundary.md`
- `../../plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`
- `../../plan/adr/ADR-0025-cognitive-method-portable-contract-boundary.md`

## 12. Natural Japanese review

Product Value、PMS-06、REQ-0001 / 0004 / 0005 / 0007 / 0021、SCN-0005 / 0014 / 0018、Cognitive Method Contract、Provider Adapter、end-to-end journey harnessへ戻り、Realization / Provider交換で何を変えてよく、何を判断記憶として維持する必要があるかを整理した。同じ出力を返すことをportableの条件にはせず、Method DefinitionとRealization、CapabilityとProvider、RecommendationとDecision、現在のObservationとhistorical basisを分離したまま再構成できることを中心に置いている。また、out-of-process reference profileをproduction外部連携へ過大評価せず、process-local protocolをUniversal Contractへ昇格させない。そのうえで、意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。