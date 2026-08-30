# ADR-0019: Provider-neutralなCapability Observation境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000020**  
Updated: 2026-08-31

## Context

SOZAは、IntentやConstraintに対して利用可能なCapabilityを探索・比較・選択する。その際、TEI、SaaS、人間、AI、外部組織など、性質の異なるProviderから現在状態を受け取る必要がある。

TEIを例にすると、Provider内部にはApplication、Database、Environment、Release、Plugin、Binding、Observed State等の具体的な対象が存在する。一つのApplicationがreadyでも、依存Databaseがread-onlyであったり、Migration Proposalが未採用であったり、EnvironmentへのBindingが未完了であったりする可能性がある。

これらをSOZA Universal Coreへそのまま複製すると、SOZAがTEI固有のlifecycleやschemaへ依存する。一方、Provider内部の一つのstatusを単純な`available=true/false`へ変換すると、Unknown、Conflict、条件付き利用可能性、根拠の違いを失う。

SOZAに必要なのは、Provider内部modelの複製ではなく、**Capabilityについて現在何が観察でき、何が未確認で、その判断材料がどのEvidenceに基づくか**をProvider-neutralに扱える境界である。

## Decision

### 1. Provider内部状態とSOZA Capability Observationを分離する

次を同一視しない。

```text
Provider Internal State != SOZA Capability Observation
```

TEIのApplication / Database / Environment / Release等、Provider固有のmodelはProvider側に残す。

SOZAは、Provider adapterを介して、Capability Choiceや監査に必要なObservation、Unknown、Conflict、Evidence、Provenance、Assurance等を受け取る。

### 2. Capability DefinitionとCapability Observationを分離する

Capability Definitionは「何を可能にするか」という比較的安定した意味を表す。

Capability Observationは「あるProviderが、ある時点・文脈で、そのCapabilityについてどのような状態として観察されたか」を表す。

```text
Capability Definition != Capability Observation
```

Providerの一時障害やEnvironment未Bindingによって、Capability Definitionそのものを書き換えない。

### 3. ObservationはAvailability Decisionそのものにしない

Provider adapterが返すObservationは、Capabilityを選択すべきか、実行すべきかというDecisionではない。

```text
Provider Observation != Capability Choice Decision
Provider status != universal availability truth
```

「利用できそうである」「一定条件なら利用可能である」といった解釈が必要な場合は、そのbasisを追跡できるRecommendation、Assurance、derived Observation等として表し、最終Decisionと分ける。

単一のProvider statusからSOZA Decisionを自動生成しない。

### 4. `unknown`、`conflict`、`not observed`を保持する

Provider側の情報が取得できない場合、それを自動的に`unavailable`へ変換しない。

複数のObservationが一致しない場合も、最新値だけでConflictを消さない。

```text
Not observed != unavailable
Unknown != unavailable
Conflict != latest-wins
```

Capability Choiceは、不確実性が残ったまま保留することも、不確実性を明示したうえで進めることもできる。

### 5. Provider-neutral Observationに必要な意味を定める

具体schemaは後続Issueで設計するが、意味境界として少なくとも次を表現できる必要がある。

- どのCapabilityについてのObservationか。
- どのProviderまたはProvider instanceについてのObservationか。
- どの時点・Environment・利用文脈で観察されたか。
- 何が観察されたか。
- 何がUnknownまたはConflictとして残ったか。
- どのEvidence / EvidenceUseに基づくか。
- どのProvenanceを持つか。
- どの程度のAssuranceで解釈できるか。
- 必要な場合、Provider固有のexact snapshotへ戻るための参照。

ここにTEI固有のApplication status、Database migration state、Plugin lifecycle等をUniversal enumとして持ち込まない。

### 6. Provider adapterは意味変換の来歴を隠さない

Provider adapterは単なるfield renameではない場合がある。

たとえば複数のTEI内部状態から「read capabilityに関する制約付きObservation」を組み立てる場合、どのsource state・規則・adapter versionに基づいて変換したかを、重要度に応じて後から辿れるようにする。

重要なDecisionでadapterによる解釈がmaterialだった場合、必要に応じて次をhistorical basisとして保持する。

- provider-specific source reference
- source snapshot / release / binding reference
- adapter / mapping revision
- derived Observation

現在のProvider状態で過去Observationを再計算して、当時の判断を置き換えない。

### 7. 通常判断と詳細監査を二層に分ける

通常のCapability Choiceで、Provider内部topologyを全量取得・保存することを要求しない。

SOZA側では、判断に必要なProvider-neutral ObservationとEvidence referenceを扱う。

一方、重要Decisionの監査、障害調査、historical reconstruction等では、権限がある範囲でProvider-specific exact snapshotへ降りられることを認める。

```text
Provider-neutral decision surface
  → evidence / exact reference
  → provider-specific detail when needed and authorized
```

### 8. Selective Disclosureを前提にする

組織やProviderによっては、内部topology、policy、顧客情報、契約情報等をSOZAへ全面開示できない。

SOZAは、必要なObservation・Evidence・Assuranceだけを共有する形を認める。

非開示部分については、既知であるかのように補完せず、必要ならUnknownとして残す。

```text
Selective Disclosure != fabricated completeness
Hidden detail != negative evidence
```

### 9. TEIを特権化しない

この境界はTEI連携を起点に整理したが、TEI専用規則にはしない。

同じCapabilityをSaaS、人間、AI、別の業務基盤が提供する場合も、同じProvider-neutralなObservation面で比較できることを目指す。

TEIとの関係が近いことを、matching、Assurance、Priority、Authorityの根拠にしない。

## Alternatives considered

### A. TEI内部schemaをSOZA Coreへ複製する

採用しない。SOZAがTEI lifecycleへ依存し、Provider交換可能性を損なう。

### B. 全Providerを共通の`available / unavailable`へ正規化する

採用しない。条件付き利用、Unknown、Conflict、未評価、複数scope等の重要な認識状態を失う。

### C. Provider内部状態をSOZA Decisionへ直接接続する

採用しない。ObservationとDecision、Provider stateとCapability semanticsを混同する。

### D. Provider内部topologyを常に完全保存する

採用しない。Selective Disclosure、情報最小化、Provider independenceを損なう。必要な監査時にexact referenceへ降りる二層構造を採る。

### E. Provider詳細を一切保持しない

採用しない。重要なDecisionを後から再構成できず、adapterによる意味変換も監査できなくなる。

## Consequences

### Positive

- SOZA CoreへTEI固有schemaを持ち込まずにCapability Choiceを支援できる。
- Provider交換時も同じ判断面を維持しやすい。
- Unknown / Conflict / Selective Disclosureを正直に保てる。
- 通常利用では情報量を抑え、必要な監査時だけProvider詳細へ降りられる。
- 過去Decision時に使ったProvider Evidenceとadapter解釈を再構成しやすくなる。
- TEIとSaaS等を同じProvider-neutralな基準で比較できる。

### Costs / Risks

- Providerごとのadapter設計と保守が必要になる。
- provider-neutralな最小Observation schemaを過度に抽象化すると、判断に必要な意味を失う可能性がある。
- adapterが複雑な解釈を担う場合、そのversion・mapping・provenance管理が必要になる。
- Selective Disclosure下では、十分なEvidenceが得られずDecisionを保留する場面が増える可能性がある。
- UIではProvider-neutralな要約と詳細Evidenceへのdrill-downを分ける必要がある。

## Revisit conditions

次の場合に再検討する。

- 複数Providerで、現在のProvider-neutral Observationでは重要な意味差を表現できないことが繰り返し確認される。
- adapter layerが実質的にProvider lifecycle engineを再実装する状態になる。
- Provider固有状態の一部が、複数domain・複数Providerで同じUniversal semanticsを持つことが実証される。
- historical reconstructionに必要なexact referenceが、Selective DisclosureやProvider retention policyにより継続的に成立しない。

## Evidence

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md` Scenario 05 / 06 / 10
- ADR-0012: Capability Choice semantic boundary
- ADR-0013: Capability Realization boundary
- ADR-0014: SOZA / TEI Product boundary
- ADR-0018: Product Value authority and evaluation boundary
- `plan/kj/2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md`
- ISSUE-000020

## Natural Japanese review

KJ統合と既存Capability / Provider境界へ戻してDecisionを確定した後、意味、強度、留保、Provider-neutral性を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
