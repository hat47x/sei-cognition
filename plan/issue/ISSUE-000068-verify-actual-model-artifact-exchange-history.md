# ISSUE-000068: actual model artifact交換後もMethod Applicationの履歴を保てるか検証する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-02

## Goal

ISSUE-000067で整理したhistorical reconstruction境界が、実際のmodel artifact交換でも機能するかを検証する。

KJ Atlasのsource revision、Method surface、入力、inference runtimeを固定したまま二つのactual model artifactを実行し、後続Applicationを追加しても、先行ApplicationのRealization、Provenance、outputが書き換わらないことを確認する。

```text
same KJ Atlas source
same Method surface
same Method input
same Ollama runtime

  + model artifact A
  → Application A

  + model artifact B
  → Application B

Application B added
  != Application A rebound to B
  != provenance A rewritten
  != output A rewritten
```

## 背景

ISSUE-000066では、Ollama `0.32.14`上の`qwen2.5:0.5b`を使い、actual inferenceからKJ Atlas response受理、SOZA Cognitive Method Applicationへのmappingまでを確認した。

ISSUE-000067では、historical reconstructionについて次の境界を確認した。

```text
実現機構が異なる
  → logical Realizationを分ける

同じRealization内のhistorical revisionを固定する必要がある
  → Exact Bindingを使う

model / runtime等の具体的な実行条件
  → 必要な範囲でProvenanceへ残す
```

ただし、ISSUE-000067までのactual model-backed Evidenceは、一つのmodel artifactによる実行だった。別のactual model artifactを後から追加しても、先行Applicationの来歴を保持できるかは未検証だった。

## 実証方法

KJ Atlas側は次を固定した。

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`
- Method input: 二回とも同一
- Ollama runtime: `0.32.14`

model artifactだけを次の二つへ交換した。

- `qwen2.5:0.5b`
- `qwen2.5:1.5b`

model tagだけを同一性の根拠とせず、Ollamaが返すmodel digestも実行Evidenceとして取得した。また、二回の実行でmodelへ渡されたpromptが同一であることを、prompt SHA-256の一致で確認した。

SOZA側では二つの実行を別のprobe-local Realization / Applicationとして記録した。これは「model artifactが異なれば常に別Realizationにする」というUniversal ruleではない。今回の実交換で二つの実行条件を取り違えないためのprobe-localな表現である。

同一Realization内のrevisionとして扱うべきScenarioについては、ISSUE-000067 H1で確認したExact Bindingを引き続き利用できる。

## 実装

次を追加した。

- `.github/workflows/actual-model-artifact-exchange-e3b.yml`
- `runtime/go/livemethodintegration/model_artifact_exchange_test.go`

新workflowでは、同じOllama processへ二つのmodel artifactを取得し、別々の薄いAdapterとKJ Atlas processを介して同一入力を実行する。その後、通常のMethod mapping boundary testとhistorical Application不変性testを続けて実行する。

AdapterやUniversal Contractは変更していない。ISSUE-000066で使用した既存Ollama Adapterと、ISSUE-000067で確立したcurrent `ExecutionIdentity` / Provenance境界を再利用した。

## actual CI結果

PR #58のbehavior headで新設workflowを実行した。

- Workflow: `Actual Model Artifact Exchange E3b`
- Run: `33633385583`
- Job: `100258107852`
- Result: **success**

### model artifact A

- model: `qwen2.5:0.5b`
- model digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- prompt evaluation count: `196`
- evaluation count: `78`
- Ollama done: `true`

### model artifact B

- model: `qwen2.5:1.5b`
- model digest: `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- prompt evaluation count: `196`
- evaluation count: `108`
- Ollama done: `true`

二つのmodel digestは異なり、prompt digestは一致した。したがって、同じMethod入力と同じruntime条件の下でmodel artifactだけを交換し、両方でactual inferenceが発生したことを確認できた。

## historical Application不変性

専用test `TestLiveKJAtlasActualModelArtifactExchangePreservesHistoricalApplication`をactual workflow内で実行し、PASSした。

Application Aを記録した後にApplication Bを追加し、その前後でAについて次が変化しないことを確認した。

- Method Reference
- Realization Reference
- Provenance Reference
- Provenance payload
- output payload

さらに、次も確認した。

- A / Bは同じMethod Definitionを指す。
- A / Bは別のprobe-local Realizationを指す。
- 各Provenanceには対応するmodel digestと同じOllama runtime versionが残る。
- Bの追加によってAのmodel identityはBへ再束縛されない。
- Method outputをRecommendation / Decisionへ自動昇格させない。

この結果、今回の範囲では、model artifactを交換しても先行Applicationのhistorical recordを保持できることが確認できた。

## Method responseについて観測したこと

両方のresponseはcurrent KJ Atlas response boundaryを通過した。

Aは二枚の対象cardを一つのgroupへまとめ、日本語のlabel / rationaleを返した。

Bは同じ二枚のcardを別groupへ分け、構造上はKJ Atlasが受理できるresponseを返した。一方、label / rationaleは中国語だった。

この差は今回のFAILではない。今回検証したのはhistorical Applicationを失わずにmodel artifactを交換できるかであり、生成内容の良し悪しや言語適合性は別の評価対象である。

むしろ、actual outputから次の区別が明瞭になった。

```text
actual inference succeeded
  + response shape accepted
  + historical Application preserved
  != model output quality satisfied
  != language suitability satisfied
  != KJ-method outcome quality satisfied
```

したがって、model出力品質と言語適合性、KJ法としての成果品質はsemantic execution conformanceとは別の評価系として扱う。

## 回帰CI

behavior headでは、新設workflowに加えて次もsuccessした。

- Plan integrity Run `33633385366`
- Semantic Runtime Conformance Run `33633385403`
- External Method Integration E3b Run `33633385608`
- External Model-backed Method E3b M1b Run `33633385726`
- External Integration E3a Run `33633385367`
- External Integration E3b Run `33633385354`
- External TEI Integration E3b P2 Run `33633385409`
- Local Package Artifact Run `33633385410`
- Release Candidate Gate Run `33633385374`
  - Gate 1〜9: success
  - 公開済みv0.2.0のprepare / publish: skip

今回の追加によって、既存M1b、Semantic Runtime、Release Candidate境界を回帰させていない。

## Requirement / Contract再監査

actual二モデル交換を実行した後も、新しいStable Requirement / ScenarioやUniversal Contract fieldを追加する必要は確認されなかった。

今回のProduct failureと解決境界は、既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

model tag、model digest、Ollama version、prompt digest等をUniversal Cognitive Method fieldへ昇格させず、current integration / Provenance境界で今回必要な意味を保持できた。

したがって、Requirement / Contractは **No Change** とする。

## Resolution

ISSUE-000068の実装・実証・上流同期は完了した。

確認できたことは次のとおりである。

1. 同じKJ Atlas source、Method surface、Method input、Ollama runtimeの下で二つのactual model artifactを実際に推論できる。
2. model artifactを交換しても、後続Application追加後に先行ApplicationのRealization、Provenance、outputを保持できる。
3. current Realization + Provenance境界で今回必要な実行条件を追跡でき、Universal Contractへmodel / runtime固有fieldを追加する必要はない。
4. actual executionとhistorical preservationが成立しても、生成結果や言語適合性は別に変化し得る。
5. model / KJ成果品質はsemantic execution Evidenceから分離して評価する必要がある。

上流計画では、次の探索点を二モデル交換そのものから、runtime version交換、より広いmodel / Provider交換、生成品質評価、E4 Operational portabilityへ移した。

文書監査台帳もISSUE-000068まで同期し、本Issueと上流計画を自然な日本語として全文再確認した。

## Evidence state

- single actual model-backed execution: **Scoped Executable Evidence available**
- H1 / H2 historical reconstruction boundary: **Scoped Executable Evidence available**
- two actual model artifact exchange with historical Application preservation: **Scoped Executable Evidence available — Run `33633385583`**
- arbitrary model portability: **Not Yet Verified**
- runtime version portability: **Not Yet Verified**
- model output quality: **Not Yet Verified**
- language suitability across model artifacts: **Not Yet Verified**
- KJ-method outcome quality: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

## Non-goals / 停止線

```text
actual two-model exchange PASS
  != arbitrary model portability
  != runtime version portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

次も今回のResolutionには含めない。

- 二つのmodelから同じ生成文を得ること
- 生成結果の優劣を判定すること
- model tagやOllama固有fieldをUniversal identityへ固定すること
- 全ApplicationへExact Bindingを一律に必須化すること
- production model distribution / credential policyを決めること
- v0.2.0 supported scopeを遡及的に拡張すること

## Reopen / escalation条件

次の場合は再検討する。

- model artifact交換によって先行Applicationの来歴が書き換わる。
- current Provenanceでは、どのmodel artifactを使ったかを一意に読み直せない。
- 別Realizationとして分けても複数domainで重要な意味が失われる。
- 同一Realization内のrevisionをExact Bindingで扱うScenarioで実交換Evidenceが必要になる。
- runtime version交換時に、今回とは異なる意味欠落が確認される。
- より広いmodel familyやProvider交換でcurrent境界が成立しない。

## 自然な日本語レビュー

ISSUE-000066 / 000067、current Cognitive Method Contract、Semantic Reference / Exact Binding、`runtime/go/livemethodintegration`、M1b Ollama Adapter、Run `33633385583`の実測Evidence、Upstream Product Development Plan、Document Review Registryを照合した。

今回の結論を「任意のmodelが交換可能」と広げず、同じKJ Atlas、同じ入力、同じOllama runtimeの下で二つのactual model artifactを交換したときにhistorical Applicationを保持できた、という実証範囲に限定している。prompt digestやmodel digestを観測することと、それらをUniversal Contract fieldへ昇格させることも分離した。

actual outputの違いから、execution / mappingの成立と生成品質を分ける必要性も実データで明瞭になった。構造上受理できるresponseであっても日本語利用場面にそのまま適切とは限らないため、semantic execution Evidenceをmodel qualityやKJ-method outcome qualityへ昇格させない停止線を維持した。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトし、最終意味監査を実施した。