# ISSUE-000068: actual model artifact交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-02

## Goal

ISSUE-000067で整理したhistorical reconstruction境界を、実際のmodel artifact交換でも保てるかを検証する。

KJ Atlasのsource revision、Method surface、入力、inference runtimeを固定したまま、二つのactual model artifactを実際に推論させる。後続のmodel実行を記録した後でも、先に記録したMethod ApplicationのRealization、Provenance、outputが書き換わらず、当時の実行条件を取り違えずに読み直せることを確認する。

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

ISSUE-000067では、historical reconstructionについて次の二段構えを実証した。

```text
実現機構が異なる
  → logical Realizationを分ける

同じRealization内のhistorical revisionを固定する必要がある
  → Exact Bindingを使う
```

また、modelやruntime等の具体的な実行条件は、Universal Cognitive Method Contractへ固有fieldを追加せず、必要な範囲でprobe-local Provenanceへ残せることを確認した。

一方、ISSUE-000067までのactual model-backed Evidenceは一つのmodel artifactによる実行だった。後から別のactual model artifactを追加しても、先行Applicationの履歴が変化しないことはactual executionでは未検証だった。

## Probe design

### 1. Method側の条件を固定する

KJ AtlasはM1bと同じ固定revisionとMethod surfaceを使う。

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`

二回の実行には同じ入力を与える。KJ Atlasがmodelへ渡したpromptについても、integration Evidence上のSHA-256が一致することを確認する。

### 2. inference runtimeを固定する

Ollama runtimeはM1bと同じ`0.32.14`へ固定する。

今回の目的はruntime交換ではなく、model artifact交換だけを分離して観測することである。

### 3. 二つのactual model artifactを実行する

実験対象は次とした。

- `qwen2.5:0.5b`
- `qwen2.5:1.5b`

model tagだけをidentityとして信用せず、Ollamaが返すmodel digestも実行Evidenceとして取得した。

### 4. live mappingでは二つのRealizationを区別する

今回のprobeでは、二つのmodel artifactを使った実行を別のprobe-local Realizationとして記録する。

これは「model tagが違えば常に別Realizationでなければならない」というUniversal ruleではない。current live mappingで二つの実行条件を誤って一つへ畳み込まず、historical Applicationを確実に区別するための実験上の表現である。

同一Realization内のrevisionとして扱う必要があるScenarioについては、ISSUE-000067 H1で確認したExact Bindingを引き続き利用できる。

### 5. Provenanceへ実行条件を残す

current `ExecutionIdentity`をそのまま使い、少なくとも次をApplicationから辿れるProvenanceへ残す。

- execution profile
- runtime / runtime version
- model tag
- observed model digest

KJ Atlas source repository / commit / entry pointとMethod result digestは、既存Provenance payloadで保持する。

prompt digestは、二回の実験条件が同じであることを確認するintegration Evidenceとして比較する。ただし、このIssueだけを根拠にUniversal Contractやcurrent `ExecutionIdentity`へ新しいfieldを追加しない。

### 6. 先行Applicationの不変性を検査する

Application Aを記録した後、Application Bを同じCanonicalStoreへ追加する。その前後でApplication Aについて次を比較する。

- Method Reference
- Realization Reference
- Provenance Reference
- Provenance payload
- output payload

Bの追加後もAが同じ意味を保持していることを確認する。

## 実装

次を追加した。

- `.github/workflows/actual-model-artifact-exchange-e3b.yml`
- `runtime/go/livemethodintegration/model_artifact_exchange_test.go`

新workflowでは、同じOllama processへ二つのmodel artifactを取得し、別々の薄いAdapterとKJ Atlas processを介して同一入力を実行する。その後、通常のMethod mapping boundary testとhistorical Application不変性testを続けて実行する。

AdapterやUniversal Contractは変更していない。ISSUE-000066で使用した既存Ollama Adapterと、ISSUE-000067で確立したcurrent `ExecutionIdentity` / Provenance境界を再利用している。

## actual CI結果

PR #58のbehavior headで新設workflowを実行した。

- Workflow: `Actual Model Artifact Exchange E3b`
- Run: `33633385583`
- Job: `100258107852`
- Result: **success**

### 固定した条件

- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`
- Ollama runtime: `0.32.14`
- Method input: 二回とも同一

### 観測したmodel artifact

#### A — qwen2.5:0.5b

- model digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- prompt evaluation count: `196`
- evaluation count: `78`
- Ollama done: `true`

#### B — qwen2.5:1.5b

- model digest: `65ec06548149b04c096a120e4a6da9d4017ea809c91734ea5631e89f96ddc57b`
- prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- prompt evaluation count: `196`
- evaluation count: `108`
- Ollama done: `true`

二つのmodel digestは異なり、prompt digestは一致した。したがって、同じMethod入力と同じruntime条件の下でmodel artifactだけを交換し、両方でactual inferenceが発生したことを確認できた。

## Method responseについて観測したこと

両方のresponseはcurrent KJ Atlas response boundaryを通過した。

Aは二枚の対象cardを一つのgroupへまとめ、日本語のlabel / rationaleを返した。

Bは同じ二枚のcardを別groupへ分け、構造としてはKJ Atlasが受理できるresponseを返した。一方、label / rationaleは中国語だった。

この違いは今回のFAILではない。今回検証しているのはhistorical Applicationを失わずmodel artifactを交換できるかであり、生成内容の良し悪しや言語適合性は評価対象ではない。

むしろ、次の区別をactual outputでも確認できた。

```text
actual inference succeeded
  + response shape accepted
  + historical Application preserved
  != model output quality satisfied
  != KJ-method outcome quality satisfied
```

したがって、model出力品質とKJ法としての成果品質をsemantic execution conformanceから分離する停止線を維持する。

## historical Application不変性

専用test `TestLiveKJAtlasActualModelArtifactExchangePreservesHistoricalApplication`をactual workflow内で実行し、**PASS**した。

Application Aを記録した後にApplication Bを追加し、その前後でAについて次が変化しないことを確認した。

- Method Reference
- Realization Reference
- Provenance Reference
- Provenance payload
- output payload

また、次も確認した。

- A / Bは同じMethod Definitionを指す。
- A / Bは別のprobe-local Realizationを指す。
- 各Provenanceには対応するmodel digestと同じOllama runtime versionが残る。
- Bの追加によってAのmodel identityはBへ再束縛されない。
- Method outputをRecommendation / Decisionへ自動昇格させない。

## Evidenceとして確認したこと

- [x] 固定revisionのKJ Atlasを同じMethod surfaceと同じ入力で二回実行した。
- [x] `qwen2.5:0.5b`と`qwen2.5:1.5b`の両方でactual inferenceが発生した。
- [x] 二つのmodel digestが異なることを確認した。
- [x] 二回のKJ Atlas呼び出しでmodelへ渡されたprompt digestが一致した。
- [x] 両方のKJ Atlas responseがcurrent parserを通った。
- [x] 二つの実行を別Realization / ApplicationとしてSOZAへ記録した。
- [x] 各Applicationから対応するruntime / model identityを辿れる。
- [x] 後続Application追加後も先行ApplicationのRealization / Provenance / outputが変化しないことを確認した。
- [x] Method outputをRecommendation / Decisionへ自動昇格させなかった。
- [x] model / runtime固有fieldをUniversal Cognitive Method Contractへ追加しなかった。
- [x] 新設workflowをsuccessさせた。

## 回帰CI

同じbehavior headで次もsuccessした。

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

今回の追加によって、既存M1bやSemantic Runtime、Release Candidate境界を回帰させていない。

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

## Evidence state

- single actual model-backed execution: **Scoped Executable Evidence available**
- H1 / H2 historical reconstruction boundary: **Scoped Executable Evidence available**
- two actual model artifact exchange with historical Application preservation: **Scoped Executable Evidence available — Run `33633385583`**
- arbitrary model portability: **Not Yet Verified**
- runtime version portability: **Not Yet Verified**
- model output quality: **Not Yet Verified**
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

次も今回の対象外とする。

- 二つのmodelから同じ生成文を得ること
- 生成結果の優劣を判定すること
- model tagやOllama固有fieldをUniversal identityへ固定すること
- 全ApplicationへExact Bindingを一律に必須化すること
- production model distribution / credential policyを決めること
- v0.2.0 supported scopeを遡及的に拡張すること

## Completion condition

actual executionとhistorical不変性の実装・実証条件は満たした。

残る作業は、この結果をUpstream Product Development Planと文書監査台帳へ同期し、次の探索点を「二つのmodelを一度交換すること」から、runtime version交換、より広いmodel / Provider交換、生成品質評価、E4 Operational portabilityへ移すことである。

この上流同期と最終CI確認後にPlan Registryと本IssueをResolvedへ揃える。

## 現在Openで残す理由

実装・actual CI・Requirement / Contract再監査は完了したが、上流計画への反映をまだ終えていないためOpenを維持する。

上流計画では、少なくとも次を明示する。

- 同じKJ Atlas / Method input / Ollama runtimeで二つのactual model artifactを交換し、historical Applicationを保持できた。
- current Realization + Provenance境界で今回必要な意味を保持できた。
- 生成結果が異なり、実際に言語適合性の差も観測されたため、semantic execution成功を生成品質へ昇格させない。
- arbitrary model portability、runtime version portability、E4は引き続き未検証である。

## Reopen / escalation条件

Resolved後も、次の場合は再検討する。

- model artifact交換によって先行Applicationの来歴が書き換わる。
- current Provenanceでは、どのmodel artifactを使ったかを一意に読み直せない。
- 別Realizationとして分けても複数domainで重要な意味が失われる。
- 同一Realization内のrevisionをExact Bindingで扱うScenarioで実交換Evidenceが必要になる。
- runtime version交換時に、今回とは異なる意味欠落が確認される。

## 自然な日本語レビュー

ISSUE-000066 / 000067、current Cognitive Method Contract、Semantic Reference / Exact Binding、`runtime/go/livemethodintegration`、M1b Ollama Adapter、Run `33633385583`の実測Evidence、上流計画のReal Method / Provider Portability節を照合した。

今回の問いを「任意のmodelが交換可能か」という大きすぎる主張へ広げず、同じKJ Atlas、同じ入力、同じOllama runtimeの下で二つのactual model artifactを交換したときにhistorical Applicationが壊れないか、という一段小さい実証に限定した。prompt digestやmodel digestを観測することと、それらをUniversal Contract fieldへ昇格させることも分離している。

さらに、actual outputの違いから、execution / mappingの成立と生成品質を分ける必要性が実データでも明瞭になった。1.5B側のresponseが構造上は受理できても日本語利用場面にそのまま適切とは言えない例を得たため、semantic execution Evidenceをmodel qualityやKJ-method outcome qualityへ昇格させない停止線を維持した。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトし、実装完了時点の意味監査を行った。