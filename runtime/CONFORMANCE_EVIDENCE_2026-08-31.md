# Semantic Runtime / Provider Adapter Conformance Evidence — 2026-08-31

状態: **Fixture-scoped Executable Evidence — PASS**  
対象branch: `develop/v0.1.0`

## 1. Scope

本書は、current Contractから再導出した最初のSemantic Runtime sliceと、synthetic Provider Adapter sliceについて、actual repository上で再現したExecutable Evidenceを記録する。

対象:

```text
runtime/go/semanticruntime/
runtime/go/provideradapter/
```

本Evidenceは、Production Provider integration、Authorization / Action execution、Release Evidence、Operational Evidenceを意味しない。

## 2. Semantic Runtime boundary

最初のruntime sliceは次を中心とする。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
```

current runtimeは、Semantic Interchange、Semantic Reference、Decision Memory、Capability Observationを読み込み、known Contractを検査し、unknown nested Contractを既知として扱わず`not_verified`相当として保持する。

また、RecommendationとDecision、DecisionとAuthority、Unknownとfalse、`not_verified`と`failed`を同一視しない。

## 3. Provider Adapter boundary

Provider Adapterは、Provider固有stateからCapability Observationへの観測変換境界として扱う。

```text
Provider-owned state
  + observation context
        ↓
Adapter / Mapping
        ↓
Capability Observation
```

synthetic Provider A / Bは異なる入力Schemaを持つ。

Provider A:

```text
health
delay_ms
service_ref
```

Provider B:

```text
ready
response_seconds
endpoint
```

これらのProvider固有field setをSOZA Universal ontologyにはしていない。

## 4. Executable paths

current runtime / adapter実装:

```text
runtime/go/semanticruntime/model.go
runtime/go/semanticruntime/loader.go
runtime/go/semanticruntime/loader_test.go
runtime/go/provideradapter/adapter.go
runtime/go/provideradapter/synthetic.go
runtime/go/provideradapter/adapter_test.go
```

Provider fixture:

```text
fixtures/providers/synthetic/
```

CI:

```text
.github/workflows/runtime-conformance.yml
```

CIは同じcheckoutで次を順に実行する。

1. current Contract checker dependencyを導入する。
2. `tools/check_contract_conformance.py`でcurrent Contract fixtureを再検査する。
3. `runtime/go`で`go test ./...`を実行する。

## 5. Current Contract fixture result

最新確認Runでも、Contract checkerは17 fixtureすべてについて期待結果と実結果が一致した。

含まれる主な境界:

- F1〜F7 Capability Observation scenarios
- DecisionへAuthority fieldを混入したSchema violation
- `observed_at`欠落
- same-logical-id lineage without exact endpoints
- Semantic Interchange内のExact Binding mismatch
- unknown nested Contract version → `not_verified`
- Verification Outcome `not_verified / failed`
- Recommendation without Decision
- Decision with unresolved state
- partial knowledge interchange

```text
fixture_count = 17
passed = true
```

## 6. Semantic Runtime evidence

runtime testではcurrent Contract fixtureを直接利用し、少なくとも次を確認している。

- Semantic Interchange v1alpha1を読み込める。
- F1〜F7を適切なtop-level Contractとして読み込める。
- Recommendation without Decisionを保持できる。
- unresolved stateを残したDecisionを保持できる。
- Unknown / Withheldを保持したpartial knowledgeを扱える。
- same-logical-id lineageでexact endpointが必要な場合に違反を拒否できる。
- bundle内recordとDecision basisのExact Binding不一致を拒否できる。
- unknown nested Contractを完全検証済みとして扱わない。
- original Semantic Interchange bytesを読込み時に勝手にnormalizeせず再exportできる。

## 7. Synthetic Provider Adapter evidence

synthetic Provider A / Bについて次を確認している。

- 異なるProvider-specific input shapeを別々の型として扱う。
- 同じCapabilityに対するObservationへmappingできる。
- Provider identityは別々に保持する。
- availabilityをProvider固有statusからObservationへmappingできる。
- `delay_ms`と`response_seconds`を比較可能な`latency` / `ms`へmappingできる。
- mapping definitionを`mapping_provenance`から追跡できる。
- source snapshotを`source_state_ref`から追跡できる。
- missing readiness / latencyを`false`や`0`へ捏造せず`unknown`として保持する。
- Provider-specific target referenceを`provider_target_ref`として保持する。
- Adapter出力をcurrent Capability Observation runtime validationへ通せる。
- Adapter出力からRecommendation / Decision / Authority / Execution / universal suitability scoreを生成しない。
- Provider A/B固有の入力field名をCapability Observationの出力field setへ直接漏らさない。

Provider-specific contextをopaque referenceやextensionとして保持すること自体は禁止しない。禁止しているのは、Provider固有SchemaをUniversal field setへ昇格させることである。

## 8. GitHub Actions evidence

### First semantic runtime closure

- Run ID: `33348972805`
- Head SHA: `834c3f2a8bd911829743c1582ef09f098c776a54`
- workflow: `Semantic Runtime Conformance`
- conclusion: **success**

このRunでfirst semantic runtime sliceのContract checker / Go testが連続PASSした。

### Synthetic Provider Adapter slice

- Run ID: `33349604842`
- Head SHA: `4450ea1acf41615a3679a65e266c008a460c5c33`
- workflow: `Semantic Runtime Conformance`
- conclusion: **success**

Go test:

```text
ok  github.com/hat47x/soza/runtime/go/provideradapter
ok  github.com/hat47x/soza/runtime/go/semanticruntime
```

### Provider schema leakage hardening

- Run ID: `33349801993`
- Head SHA: `bff2522e9be004d48274d4743e7756130648169a`
- workflow: `Semantic Runtime Conformance`
- conclusion: **success**

このRunでは、Provider A/B固有field名がCapability Observationの出力Schemaへ直接現れないことを確認する追加testを含めた状態で、Contract checkerと全Go testが連続PASSした。

## 9. Evidence boundary

今回直接確認したのは、current Contract fixtureを基準にしたfirst semantic runtimeとsynthetic Provider AdapterのExecutable Evidenceである。

```text
Runtime / Adapter CI PASS
  != all SOZA runtime requirements complete
  != TEI production adapter
  != SaaS production interoperability
  != Authorization enforcement
  != Action execution
  != release readiness
  != operational evidence
```

current Representation Profileのfixture-scoped Executable Evidenceは別途成立しているが、Production-grade Verifier Registryをruntimeへ完全統合したことまでは本Evidenceから主張しない。

historical M47 digestのRepresentation Profileも未確認であり、ISSUE-000034で独立して扱う。

## 10. Natural Japanese review

actual GitHub Actionsの実ログ、current Contract fixture、Semantic Runtime実装、synthetic Provider Adapter実装とtestを相互照合し、直接確認できた範囲と未検証範囲を分離した。その後、意味、数値、Evidence強度、Provider / Capability / Decision / Authority / Executionの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
