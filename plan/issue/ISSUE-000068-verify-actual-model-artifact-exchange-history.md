# ISSUE-000068: actual model artifact交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-02

## Goal

ISSUE-000067で整理したhistorical reconstruction境界を、実際のmodel artifact交換でも保てるかを検証する。

今回は、KJ Atlasのsource revision、Method surface、入力、inference runtimeを固定したまま、二つのactual model artifactを実際に推論させる。後続のmodel実行を記録した後でも、先に記録したMethod ApplicationのRealization、Provenance、outputが書き換わらず、当時の実行条件を取り違えずに読み直せることを確認する。

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

一方、ここまでのactual model-backed Evidenceは一つのmodel artifactによる実行である。後から別のactual model artifactを追加しても、先行Applicationの履歴が変化しないことはまだactual executionで確認していない。

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

最初の実験対象は次とする。

- `qwen2.5:0.5b`
- `qwen2.5:1.5b`

model tagだけをidentityとして信用せず、Ollamaが返すmodel digestも実行Evidenceとして取得する。

### 4. live mappingでは二つのRealizationを区別する

今回のprobeでは、二つのmodel artifactを使った実行を別のprobe-local Realizationとして記録する。

これは「model tagが違えば常に別Realizationでなければならない」というUniversal ruleではない。current live mappingで二つの実行条件を誤って一つへ畳み込まず、historical Applicationを確実に区別するための実験上の表現である。

同一Realization内のrevisionとして扱う必要があるScenarioについては、ISSUE-000067 H1で確認したExact Bindingを引き続き使える。

### 5. Provenanceへ実行条件を残す

current `ExecutionIdentity`をそのまま使い、少なくとも次をApplicationから辿れるProvenanceへ残す。

- execution profile
- runtime / runtime version
- model tag
- observed model digest

KJ Atlas source repository / commit / entry pointとMethod result digestは、既存Provenance payloadで保持する。

prompt digestは、二回の実験条件が同じであることを確認するintegration Evidenceとして比較するが、このIssueだけを根拠にUniversal Contractやcurrent `ExecutionIdentity`へ新しいfieldを追加しない。

### 6. 先行Applicationの不変性を検査する

Application Aを記録した後、Application Bを同じCanonicalStoreへ追加する。その前後でApplication Aについて次を比較する。

- Method Reference
- Realization Reference
- Provenance Reference
- Provenance payload
- output payload

Bの追加後もAが完全に同じ意味を保持していることを確認する。

## Evidenceとして確認すること

- [ ] 固定revisionのKJ Atlasを同じMethod surfaceと同じ入力で二回実行する。
- [ ] `qwen2.5:0.5b`と`qwen2.5:1.5b`の両方でactual inferenceが発生する。
- [ ] 二つのmodel digestが異なることを確認する。
- [ ] 二回のKJ Atlas呼び出しでmodelへ渡されたprompt digestが一致する。
- [ ] 両方のKJ Atlas responseがcurrent parserを通る。
- [ ] 二つの実行を別Realization / ApplicationとしてSOZAへ記録する。
- [ ] 各Applicationから対応するruntime / model identityを辿れる。
- [ ] 後続Application追加後も先行ApplicationのRealization / Provenance / outputが変化しない。
- [ ] Method outputをRecommendation / Decisionへ自動昇格させない。
- [ ] model / runtime固有fieldをUniversal Cognitive Method Contractへ追加しない。
- [ ] 対象CIをsuccessさせる。

## Requirement / Contract監査

このIssueの開始時点では、新しいStable Requirement / Scenarioを追加しない。

主に次の既存要件の実証として扱う。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

実交換の結果、既存Requirementとcurrent Contractでは守れない独立したProduct failureが確認された場合にだけ、Candidate RequirementまたはContract変更を検討する。

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

二つのactual model artifactを同じ固定KJ Atlas Method条件で実行し、両方をSOZAへ別Applicationとして記録した後でも、先行ApplicationのRealization、Provenance、outputが不変であることをactual CIで確認できた時点で、今回のScoped Executable Evidenceを成立とする。

そのうえでRequirement / Contract変更の要否を再監査し、上流計画へ結果を反映してからResolvedとする。

modelの取得だけが成功した場合、processが起動しただけの場合、actual inferenceが発生しなかった場合、またはKJ Atlas responseをSOZAへmappingできなかった場合はResolvedにしない。

## Reopen / escalation条件

Resolved後も、次の場合は再検討する。

- model artifact交換によって先行Applicationの来歴が書き換わる。
- current Provenanceでは、どのmodel artifactを使ったかを一意に読み直せない。
- 別Realizationとして分けても複数domainで重要な意味が失われる。
- 同一Realization内のrevisionをExact Bindingで扱うScenarioで実交換Evidenceが必要になる。
- runtime version交換時に、今回とは異なる意味欠落が確認される。

## 自然な日本語レビュー

ISSUE-000066 / 000067、current Cognitive Method Contract、Semantic Reference / Exact Binding、`runtime/go/livemethodintegration`、M1b Ollama Adapter、上流計画のReal Method / Provider Portability節を照合した。

今回の問いを「任意のmodelが交換可能か」という大きすぎる主張へ広げず、同じKJ Atlas、同じ入力、同じOllama runtimeの下で二つのactual model artifactを交換したときにhistorical Applicationが壊れないか、という一段小さい実証へ限定している。また、prompt digestやmodel digestを観測することと、それらをUniversal Contract fieldへ昇格させることを分離した。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトした。