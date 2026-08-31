# ISSUE-000036: synthetic Provider Adapter vertical sliceを実装する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0019, ADR-0022, ADR-0024**  
Updated: 2026-08-31

## Goal

ADR-0024に従い、異なるProvider-specific input schemaを持つsynthetic ProviderをProvider Adapter経由でcurrent Capability Observationへ変換し、actual runtime / fixture / CIでExecutable Evidenceを得る。

最初からTEI production APIへ接続せず、Provider-specific schemaをUniversal Coreへ漏らさないこと、mapping provenanceを失わないこと、Unknownをnegative factへ変換しないことを先に検証する。

## Initial implementation scope

current Go runtimeに、交換可能なProvider Adapter実装境界を追加する。

概念上の入力と出力:

```text
Observation context
  + Provider A-specific payload
  → Adapter A / Mapping A
  → soza.capability-observation/v1alpha1

Observation context
  + Provider B-specific payload
  → Adapter B / Mapping B
  → soza.capability-observation/v1alpha1
```

Go interface / package layoutは実装詳細であり、semantic authorityとしない。

## Required synthetic Providers

少なくとも2種類の異質なinput shapeを持たせる。

例:

### Provider A

```text
health = green | amber | red | unknown
delay_ms = integer?
service_ref = provider-specific string
```

### Provider B

```text
ready = boolean?
response_seconds = decimal?
endpoint = provider-specific string
```

同じCapabilityを観測しても、入力field名・単位・status意味が異なる状態を作る。

この例の具体field名をSOZA Contractへ昇格させない。

## Required mapping behavior

### M1. status interpretation

Provider Aの`health=green`やProvider Bの`ready=true`を、必要な共通conditionへmappingできる。

ただし、mapping結果はObservationであり、Decisionではない。

### M2. unit conversion

`response_seconds`等を比較可能な単位へ変換する場合、unit conversionがmappingの一部であることを後から追跡できる。

### M3. unknown preservation

`ready`やlatency fieldが欠落している場合、`false`や`0`を捏造しない。

必要に応じて`state=unknown`等として外在化する。

### M4. Provider-specific reference

Provider固有endpoint / service referenceをUniversal fieldへ展開せず、`provider_target_ref`またはextensionとして保持する。

### M5. mapping provenance

Adapter A / Bがそれぞれどのmapping definition / versionを使用したかを`mapping_provenance`から追跡できる。

### M6. source state reference

どのProvider source snapshotを材料にしたかを`source_state_ref`等から追跡できる。

### M7. Contract validation

生成したObservationをcurrent Capability Observation runtime validationへ通し、validated recordとして読み込める。

### M8. no semantic escalation

Adapter出力に次を含めない。

- Recommendation
- Decision
- Authority
- execution command
- universal suitability score

## Required tests

少なくとも次をactual testとして持つ。

1. Provider A positive mapping。
2. Provider B positive mapping。
3. 異なるunitから同じ比較単位へmappingできる。
4. missing readiness / latencyをnegative defaultへ変換しない。
5. Provider-specific target referenceを保持する。
6. mapping provenanceを保持する。
7. source state referenceを保持する。
8. 生成Observationがcurrent runtime validationを通る。
9. 同じCapabilityに対するA/B Observationを別Providerとして保持できる。
10. Adapter結果からDecision / Authorityが生成されない。

## CI

既存`Semantic Runtime Conformance`へ統合し、少なくとも次を同じbranchで確認する。

```text
Contract fixture checker PASS
Go semantic runtime tests PASS
Provider Adapter tests PASS
```

CI failureを検出した場合は、その時点で原因を解消し、successを確認してから次の作業へ進む。

## Acceptance

### Executable Acceptance

- [ ] Provider Adapter runtime boundaryがactual treeに存在する。
- [ ] synthetic Provider A / Bの異なるinput shapeを扱える。
- [ ] A / Bからvalid Capability Observationを生成できる。
- [ ] mapping provenanceを保持できる。
- [ ] source state referenceを保持できる。
- [ ] missing値をnegative defaultへ変換しない。
- [ ] Provider-specific contextをUniversal field setへ漏らさない。
- [ ] AdapterがDecision / Authority / Executionを生成しない。
- [ ] current Capability Observation validationと同じ意味境界へ接続できる。
- [ ] actual branch CIがsuccessする。
- [ ] 文書とfixture説明を自然な日本語で再ドラフトし、最終意味監査を行う。

### Evidence boundary

本Issueで得るのはsynthetic Provider Adapter sliceのExecutable Evidenceである。

```text
synthetic Adapter CI PASS
  != TEI production adapter
  != SaaS production interoperability
  != Provider operational evidence
  != release readiness
```

## Dependencies

- ADR-0019 — Provider-neutral Capability Observation
- ADR-0022 — first semantic runtime slice
- ADR-0024 — Provider Adapter observation mapping boundary
- `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
- `runtime/go/semanticruntime/`

## Natural Japanese review

synthetic Providerで先に検証する目的、mapping provenance、Unknown、Provider-specific reference、Decision境界を整理した後、production integrationを先取りせず、自然な日本語となることを最重要視して全文を再ドラフトした。実装完了時にactual Evidenceへ戻して再度最終意味監査を行う。
