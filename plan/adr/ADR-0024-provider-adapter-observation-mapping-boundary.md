# ADR-0024: Provider Adapterを観測変換境界として扱う

Status: **Accepted**  
Related Issues: **ISSUE-000035, ISSUE-000036**  
Updated: 2026-08-31

## Context

SEIのcurrent baselineでは、ProviderとCapabilityを分離し、Provider内部状態をそのままCapabilityの意味へ昇格させない。

ADR-0019と`sei.capability-observation/v1alpha1`では、Provider固有の状態からProvider-neutralなCapability Observationへ変換するとき、field mapping、unit conversion、status interpretation、aggregation等が単なるformat変換ではなく、意味上の解釈を含み得ることを定めた。

```text
Provider state != Capability interpretation != Decision
```

Provider Adapterを設ける場合にも、すべてのProviderを一つの共通state schemaへ押し込めると、Provider IndependenceのためのAdapterが新しいglobal Provider ontologyになり得る。

そこで、Provider Adapterをどの意味境界として扱うかを明示する。

## Decision

### 1. Provider AdapterはProvider固有stateからCapability Observationへの一方向の解釈境界とする

概念上の基本関係を次とする。

```text
Provider-owned state
  + observation context
        ↓
Adapter / Mapping
        ↓
Capability Observation
        ↓
Matching / Decision may consume
```

AdapterはProvider内部SchemaをSEI Coreへ移植する場所ではない。

Provider固有stateを読み取り、current Capability Observation Contractで必要な意味だけを外在化する。

### 2. Provider固有stateの共通Universal schemaを新設しない

人間、SaaS、AI service、TEI、custom code、外部組織等は、内部状態の表現が大きく異なり得る。

SEIは、それらを一つのUniversal `ProviderState` field setへ正規化することを要求しない。

```text
Provider-specific input schema != SEI Universal ontology
```

Adapter runtime APIがraw bytes、typed object、API response等のいずれを受け取るかは実装上の選択であり、semantic authorityではない。

### 3. Adapterの出力はCapability Observation Contractで検証する

Adapterが生成した結果は、少なくともcurrent `sei.capability-observation/v1alpha1`の意味境界を満たさなければならない。

```text
Adapter produced output
  != validated Capability Observation
```

Adapter出力を既存Contract validatorまたは同等のruntime validationへ通したうえで、validated observationとして扱う。

Adapter都合でContractを弱めない。

### 4. mapping provenanceを解釈の一部として保持する

Adapterが次の処理を行う場合、単なる透明なformat変換とは扱わない。

- field mapping
- unit conversion
- enum / category normalization
- status interpretation
- aggregation
- derived condition
- missing-value interpretation

生成したCapability Observationには、必要な範囲で`mapping_provenance`を残す。

最低限、どのmapping definition / versionを用いたかを後から識別できるようにする。

### 5. Decision basisとして重要なmappingはhistoricalに固定できるようにする

Adapter mappingが変更されると、同じProvider stateから異なるCapability Observationが生成される可能性がある。

重要なDecisionがそのObservationをbasisとして利用した場合、Profile / Policyはmapping versionのlogical referenceだけでなく、必要に応じてExact Bindingを要求できる。

```text
same Provider state
  + different mapping
  → may produce different interpretation
```

現在のmappingへ追随して過去Observationを再計算することを、historical reconstructionの既定動作にはしない。

### 6. source stateへの戻り道を失わない

SEI Universal CoreへProvider state全量を複製することは要求しない。

一方、Capability ObservationがどのProvider stateを材料にしたかを、必要な範囲で追跡できるようにする。

少なくとも次のいずれかを残せる設計とする。

- Provider-specific source state reference
- provenance reference
- exact source binding（必要な場合）

sourceを保持できない場合は、その事実をraw factの不存在と混同しない。

### 7. missing / unknownをnegative factへ変換しない

Provider stateにfieldがない、APIが応答しない、権限上取得できない等の場合、Adapterは便宜的なdefault値から`available=false`等を作ってはならない。

```text
missing != false
not observed != unavailable
withheld != unknown
```

Provider固有の欠落理由をすべてUniversal taxonomyへする必要はないが、意味を失わず`unknown`、`withheld`、Provenance等へ外在化できる余地を維持する。

### 8. 共通facetは比較のために使えてもUniversal closed taxonomyにはしない

複数Providerを比較するため、`availability`、latency、cost等の共通condition keyへmappingすることは許す。

ただし、それらを全Capabilityへ適用される閉じたUniversal field setへ固定しない。

Provider固有情報はextensionまたはProvider-specific referenceとして残せる。

### 9. AdapterはMatching / Recommendation / Decision / Authority / Executionを所有しない

Adapterは観測変換境界である。

```text
Adapter mapping
  != Matching
  != Recommendation
  != Decision
  != Authority
  != Execution
```

Adapterが`available=true`を生成しても、それは候補採用や実行許可を意味しない。

Provider Adapterにbest-candidate selectionやTrust rankingを持ち込まない。

### 10. Adapter実装自体をsemantic authorityにしない

Go interface、package名、function signature等は交換可能なruntime implementationである。

```text
Adapter interface != Adapter semantic contract
```

同じmapping meaningを別言語・別libraryで実装できることを妨げない。

### 11. 最初のExecutable sliceはsynthetic heterogeneous Providersで検証する

最初からTEI production adapterを成立条件にはしない。

異なるProvider-specific input schemaを持つ少なくとも2つのsynthetic Providerを用い、同じCapabilityに対するObservationへmappingできることを確認する。

これにより、特定Providerの概念をUniversal Coreへ持ち込まずに、次を検証する。

- input schemaが異なってもcurrent Capability Observationへ変換できる。
- unit / status mappingをProvenance付きで扱える。
- missing stateをnegative factへ変換しない。
- Provider-specific contextをopaque reference / extensionとして保持できる。
- Provider kindからranking / Authorityを推定しない。

### 12. CIではAdapter outputとcurrent Contract fixture sourceを再照合する

Provider Adapter testは単なるunit testだけにしない。

生成結果をcurrent Capability Observationのruntime validationへ通し、既存Contractの意味境界を満たすことを確認する。

また、同じCI jobでcurrent Contract fixture checkerを実行し、Adapter実装の都合でContract側の境界が崩れていないことを確認する。

## Current realization and Evidence

ISSUE-000036でsynthetic Provider Adapter sliceをactual treeへ実体化した。

```text
runtime/go/provideradapter/
fixtures/providers/synthetic/
```

Provider A / Bは異なるinput field setを持ち、それぞれのAdapterがcurrent Capability Observationへmappingする。

Executable Evidenceでは、少なくとも次を確認している。

- A / Bの異なるinput shapeを共通`ProviderState`へ統合せず扱える。
- availabilityとlatencyを共通conditionへmappingできる。
- Provider Bの秒単位latencyをmsへ変換し、mapping provenanceを保持できる。
- source state referenceを保持できる。
- missing値を`false`や`0`へ変換せず`unknown`として残せる。
- Adapter outputをcurrent Capability Observation runtime validationへ通せる。
- Recommendation / Decision / Authority / Execution / universal suitability scoreを生成しない。
- Provider A/B固有の入力field名をCapability ObservationのUniversal output field setへ直接漏らさない。

`Semantic Runtime Conformance`では、current Contract checker 17 fixtureと`semanticruntime` / `provideradapter`のGo testを同じcheckoutで連続して実行し、successを確認している。

詳細は次を正本とする。

```text
runtime/CONFORMANCE_EVIDENCE_2026-08-31.md
```

これはsynthetic Provider Adapterのfixture-scoped Executable Evidenceであり、TEI / SaaS等のProduction adapter、Release Evidence、Operational Evidenceを意味しない。

## Consequences

### Positive

- Provider固有SchemaがSEI Universal Coreへ漏れにくい。
- Adapterによる解釈をraw Provider factと区別できる。
- mapping変更後も過去Decision basisを再構成しやすい。
- 異なるProviderを同じCapability候補として扱いつつ、内部Schemaを無理に統一せずに済む。
- Provider integrationを進めてもSEIの中心をExecution engineへ移さずに済む。

### Costs

- ProviderごとにAdapter / Mappingの設計と保守が必要になる。
- mapping provenanceを保持するため、単純なAPI response変換より記録が増える。
- 共通facetとProvider-specific extensionの境界をuse caseごとに確認する必要がある。
- mapping versionをhistoricalに固定すべき範囲をProfile / Policyで判断する必要がある。

## Revisit conditions

次の場合に再検討する。

- 多数Providerで同一のinput semanticsが繰り返し現れ、明示的なProvider Profile Contractを共有する方が自然になる。
- mapping provenanceだけではDecision historical reconstructionが不十分な事例が繰り返し現れる。
- Provider AdapterとCapability Matchingの境界が実ユースケースで継続的に不自然になる。
- human/manual Provider等、API stateを持たないProviderで別のObservation acquisition境界が必要になる。

## Natural Japanese review

current Product Value、Capability Observation Contract、Semantic Runtime、synthetic Provider Adapterのactual Evidenceへ戻ってDecisionを照合した。その後、「Provider Adapter境界はまだ存在しない」という設計時点の状態をCurrent realizationへ更新し、mapping provenance、Unknown、Decision、Authority、Executionの意味差を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後にEvidence強度を含めて意味監査を実施済みである。
