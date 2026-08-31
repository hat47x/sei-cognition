# ISSUE-000036: synthetic Provider Adapter vertical sliceを実装する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0019, ADR-0022, ADR-0024**  
Updated: 2026-08-31

## Goal

ADR-0024に従い、異なるProvider-specific input schemaを持つsynthetic ProviderをProvider Adapter経由でcurrent Capability Observationへ変換し、actual runtime / fixture / CIでExecutable Evidenceを得る。

最初からTEI production APIへ接続せず、Provider-specific schemaをUniversal Coreへ漏らさないこと、mapping provenanceを失わないこと、Unknownをnegative factへ変換しないことを先に検証する。

## Resolution

### 1. Provider Adapter runtime boundaryを実体化した

actual treeへ次を追加した。

```text
runtime/go/provideradapter/
  adapter.go
  synthetic.go
  adapter_test.go
```

`Adapter` interfaceやGo package名はcurrent implementationであり、semantic authorityではない。

Adapter outputの意味はADR-0024と`soza.capability-observation/v1alpha1`を正とする。

### 2. 異なるinput shapeを持つProvider A / Bを実装した

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

両Providerを一つのUniversal `ProviderState`構造へ変換してから処理していない。

それぞれのProvider固有stateを各Adapterが直接解釈し、出力だけをcurrent Capability Observationへ収束させる。

### 3. status interpretationとunit conversionをmappingとして扱った

Provider Aの`health=green`、Provider Bの`ready=true`を、共通の`availability` conditionへ変換できる。

Provider Bの`response_seconds=0.24`は`latency=240ms`へ変換する。

このunit conversionやstatus interpretationはraw Provider factそのものではなく、Adapter mappingによる解釈である。

### 4. missing値をnegative/default値へ変換しない

Provider Aで`health`や`delay_ms`が欠けている場合、Provider Bで`ready`や`response_seconds`が欠けている場合、`false`や`0`を生成しない。

current Capability Observationでは`state=unknown`として外在化する。

```text
missing != false
not observed != unavailable
```

### 5. Provider-specific referenceを保持した

Provider Aの`service_ref`、Provider Bの`endpoint`は、SOZA Universal fieldへ展開せず`provider_target_ref`として保持する。

Provider A / Bのinput schema identityは`extensions.provider_context`へ置き、Universal Capability Observation field setへ昇格させていない。

### 6. mapping provenanceとsource state referenceを保持した

各Observationに、Adapterごとのmapping definitionを`mapping_provenance.mapping_ref`として記録する。

また、どのProvider source snapshotを材料としたかを`source_state_ref`から追跡できる。

これにより、後からmappingが変わった場合でも、「どのProvider stateを、どのmappingで解釈したか」を再読できる境界を作った。

### 7. Adapter outputをcurrent Capability Observation runtime validationへ接続した

`ValidateObservation()`はAdapter出力をJSON representationへ落とし、既存`semanticruntime.LoadStandalone()`へ渡す。

```text
Adapter produced output
  → current Capability Observation runtime validation
  → validated record
```

Adapter専用の緩い検証規則を別に作っていない。

### 8. semantic escalationを防ぐtestを追加した

Adapter outputに次が生成されないことを明示的に確認する。

- Recommendation
- Decision
- Authority
- Execution
- universal suitability score

```text
Adapter mapping != Decision != Authority != Execution
```

### 9. synthetic Provider fixtureをactual treeへ追加した

```text
fixtures/providers/synthetic/
  README.md
  provider-a-green.json
  provider-a-missing.json
  provider-b-ready.json
  provider-b-missing.json
```

fixture READMEでは、Provider固有fieldがSOZA Universal Contractの候補ではなく、異質なProvider inputを検査するためのsynthetic stateであることを明示した。

### 10. Runtime CIへProvider Adapter testを統合した

`.github/workflows/runtime-conformance.yml`へ`fixtures/providers/**`をtrigger対象として追加した。

CIでは同じjobで次を実行する。

```text
current Contract fixture checker
  + Go semantic runtime tests
  + Provider Adapter tests
```

actual GitHub Actions:

- workflow: `Semantic Runtime Conformance`
- run: **#4**
- Run ID: **33349604842**
- commit: `4450ea1acf41615a3679a65e266c008a460c5c33`
- conclusion: **success**

Contract fixture checkerと、semantic runtime / Provider Adapterを含む`go test ./...`の両方が成功した。

## Acceptance

### Executable Acceptance

- [x] Provider Adapter runtime boundaryがactual treeに存在する。
- [x] synthetic Provider A / Bの異なるinput shapeを扱える。
- [x] A / Bからvalid Capability Observationを生成できる。
- [x] mapping provenanceを保持できる。
- [x] source state referenceを保持できる。
- [x] missing値をnegative defaultへ変換しない。
- [x] Provider-specific contextをUniversal field setへ漏らさない。
- [x] AdapterがDecision / Authority / Executionを生成しない。
- [x] current Capability Observation validationと同じ意味境界へ接続できる。
- [x] actual branch CIがsuccessする。
- [x] 文書とfixture説明を自然な日本語で再ドラフトし、最終意味監査を行った。

## Evidence boundary at closure

本Issueで得られたのはsynthetic Provider Adapter sliceのExecutable Evidenceである。

```text
synthetic Adapter CI PASS
  != TEI production adapter
  != SaaS production interoperability
  != Provider operational evidence
  != release readiness
```

Provider A / Bのfield名やmappingはfixture用であり、SOZAのUniversal Provider ontologyではない。

## Follow-up

production Provider adapterが必要になった場合は、ADR-0024の境界を維持し、対象Providerごとに独立したIssueで扱う。

TEIを最初のproduction Providerとして採用する場合も、SOZA関連製品であるという理由だけで特権化せず、同じCapability Observation Contract / mapping provenance / Evidence境界を適用する。

## CI handling

本Issueの実装commitではCI failureは発生せず、run #4で直接successを確認した。

今後もCI failureを検出した時点で原因を解消し、successを確認してから次の作業へ進む。

## Natural Japanese review

実装コード、synthetic fixture、runtime test、CI結果へ戻ってAcceptanceを一項目ずつ照合した後、production Provider integrationを先取りせず、意味、規範強度、Evidence境界を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
