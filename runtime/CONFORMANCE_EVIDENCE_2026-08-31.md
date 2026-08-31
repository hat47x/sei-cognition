# Semantic Runtime / Provider Adapter Conformance Evidence — 2026-08-31

状態: **Fixture-scoped Executable Evidence — PASS**  
対象branch: `develop/v0.1.0`

## 1. Scope

本書は、current Contractから再導出した最初のSemantic Runtime sliceと、synthetic Provider Adapter sliceについて、actual repository上で再現したExecutable Evidenceを記録します。

対象:

```text
runtime/go/semanticruntime/
runtime/go/provideradapter/
```

本書が直接扱うのは、current Contract fixtureを読み、意味境界を検査・再構成するruntimeと、Provider固有stateをCapability Observationへ写像するsynthetic Adapterの範囲です。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Production Provider integration、Authorization / Action execution、Release、Operational、Adoption / Outcomeは本Evidenceから主張しません。

## 2. Semantic Runtime boundary

最初のruntime sliceは次を中心とします。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
```

current runtimeはSemantic Interchange、Semantic Reference、Decision Memory、Capability Observationを読み込み、known Contractを検査します。

unknown nested Contractは既知として扱わず、完全検証できない状態として保持します。また、RecommendationとDecision、DecisionとAuthority、Unknownとfalse、`not_verified`と`failed`を同一視しません。

このsliceの存在から、SOZA全体のworkflow、Authorization、Action execution、Outcome評価まで実装済みとは読みません。

## 3. Provider Adapter boundary

Provider Adapterは、Provider固有stateからCapability Observationへの観測・解釈境界として扱います。

```text
Provider-owned state
  + observation context
        ↓
Adapter / Mapping
        ↓
Capability Observation
```

synthetic Provider A / Bは、意図的に異なる入力Schemaを持ちます。

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

これらのProvider固有field setをSOZA Universal ontologyにはしません。

Adapterは必要なObservationへ収束させますが、Provider固有stateそのものをCapability DefinitionやDecisionへ昇格させません。

## 4. Executable paths

current runtime / Adapter実装:

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

CIは同じcheckoutで、概ね次を順に実行します。

1. current Contract checker dependencyを導入する。
2. `tools/check_contract_conformance.py`でcurrent Contract fixtureを再検査する。
3. `runtime/go`で`go test ./...`を実行する。

これにより、runtime testだけが単独でgreenでも、前提となるContract fixtureが壊れている状態を見逃しにくくします。

## 5. Current Contract fixture result

current baselineでは17 fixtureについて、期待結果とactual checkerの結果が一致することを確認しています。

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

この結果はContract fixtureに限定したExecutable Evidenceであり、production interoperabilityではありません。

## 6. Semantic Runtime evidence

runtime testではcurrent Contract fixtureを直接利用し、少なくとも次を確認しています。

- Semantic Interchange v1alpha1を読み込める。
- F1〜F7を適切なtop-level Contractとして読み込める。
- Recommendation without Decisionを保持できる。
- unresolved stateを残したDecisionを保持できる。
- Unknown / Withheldを保持したpartial knowledgeを扱える。
- same-logical-id lineageでexact endpointが必要な場合に違反を拒否できる。
- bundle内recordとDecision basisのExact Binding不一致を拒否できる。
- unknown nested Contractを完全検証済みとして扱わない。
- original Semantic Interchange bytesを読込み時に勝手にnormalizeせず再exportできる。

この範囲はread / validate / reconstructの最初のvertical sliceであり、Storage migration、Authorization、Action execution、Projection等を横断するruntime coverageではありません。

## 7. Synthetic Provider Adapter evidence

synthetic Provider A / Bについて、少なくとも次を確認しています。

- 異なるProvider-specific input shapeを別々の型として扱う。
- 同じCapabilityに対するObservationへmappingできる。
- Provider identityを別々に保持する。
- availabilityをProvider固有statusからObservationへmappingできる。
- `delay_ms`と`response_seconds`を比較可能な`latency` / `ms`へmappingできる。
- mapping definitionを`mapping_provenance`から追跡できる。
- source snapshotを`source_state_ref`から追跡できる。
- missing readiness / latencyを`false`や`0`へ捏造せず`unknown`として保持する。
- Provider-specific target referenceを`provider_target_ref`として保持する。
- Adapter出力をcurrent Capability Observation runtime validationへ通せる。
- Adapter出力からRecommendation / Decision / Authority / Execution / universal suitability scoreを生成しない。
- Provider A / B固有の入力field名をCapability Observationの出力field setへ直接漏らさない。

Provider-specific contextをopaque referenceやextensionとして保持すること自体は禁止しません。禁止しているのは、Provider固有SchemaをUniversal field setへ無条件に昇格させることです。

## 8. GitHub Actions evidence

### First semantic runtime closure

- Run ID: `33348972805`
- Head SHA: `834c3f2a8bd911829743c1582ef09f098c776a54`
- workflow: `Semantic Runtime Conformance`
- conclusion: **success**

このRunでfirst semantic runtime sliceのContract checker / Go testが連続PASSしました。

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

このRunでは、Provider A / B固有field名がCapability Observationの出力Schemaへ直接現れないことを確認する追加testを含めた状態で、Contract checkerと全Go testが連続PASSしました。

### Documentation rebaseline後の回帰確認

Contracts / Representation Profile文書をcurrent baselineへ再監査した後にも、runtime semanticsが壊れていないことを確認しています。

- Run ID: `33389771449`: **success** — Contract family再基線化後
- Run ID: `33389973787`: **success** — Representation Profile再基線化後

これらは新しいruntime capabilityのEvidenceではなく、文書・規範整理後も既存のExecutable boundaryが回帰していないことの確認です。

## 9. Representation Profileとの関係

current Representation Profileについては、別Workflowでfixture / Go probeのscoped Executable Evidenceが成立しています。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

first semantic runtimeはExact Binding metadataやProfile identityを扱えますが、Production-grade Verifier Registryをruntimeへ完全統合したことまでは確認していません。

```text
runtime reads Profile identity
  != production verifier registry established
```

historical M47 digestのRepresentation Profileも未確認であり、ISSUE-000034で独立して扱います。

## 10. Evidence boundary

今回直接確認したのは、current Contract fixtureを基準にしたfirst semantic runtimeとsynthetic Provider AdapterのExecutable Evidenceです。

```text
Runtime / Adapter CI PASS
  != all SOZA runtime requirements complete
  != TEI production adapter
  != SaaS production interoperability
  != Authorization enforcement
  != Action execution
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current Evidence state:

- Design: **Satisfied** — ADR-0022 / ADR-0024、Architecture、Contract、runtime boundaryを定義済み。
- Executable: **Partially Satisfied** — first runtime / synthetic Adapterのtested scopeで再現可能。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

Executable Evidenceがあることを、runtime全体の完了や利用者価値へ読み替えません。

## 11. Natural Japanese review

actual GitHub Actions、current Contract fixture、Semantic Runtime実装、synthetic Provider Adapter実装とtest、Representation Profileのcurrent境界を相互照合しました。first closureのrun ID・実装範囲を保持したまま、後続の回帰CIと5段階Evidenceを追加し、直接確認できた範囲と未検証範囲を分離しています。その後、意味、数値、Evidence強度、Provider / Capability / Decision / Authority / Executionの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
