# SOZA Realization / Provider Exchange

更新日: 2026-09-02  
状態: **Current Realization / Provider Exchange Design Baseline — E3b-P2 fixed-artifact / E3b-M1b reflected**

## 1. この文書の役割

この文書は、PMS-06「実際のMethod / Providerを交換しても判断記憶が保たれる」を進めるために、**何を交換可能とみなし、交換後にも何をcanonicalな判断記憶として守るか**をProduct levelで定めます。

SOZAにとって重要なのは、特定のAI、Prompt、process、SaaS、TEI、custom codeを長く使い続けることではありません。それらが入れ替わった後にも、当時のIntent、Observation、Method Application、Recommendation、Decision、Responsibility、Provenance、Unknown / Conflictを、その時点の意味を壊さず読み直せることです。

## 2. 交換してよいものと、交換で失ってはならないもの

### 交換してよいもの

- Cognitive Method Realization
- AI model / Prompt / code-assisted tool
- Capability Provider
- Provider Adapter
- external SaaS / TEI / custom code
- process topology
- Realization固有のwire protocol
- artifact repositoryや配布経路

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

Realization AとBが異なる出力を返しても、それぞれを別のMethod Applicationとして追跡します。後からRealization Bを使ったことを理由に、Realization Aを使って作られた過去Decisionを現在版へ書き換えません。

Method Realizationの交換に、同じ結論を返すことは要求しません。守るべきなのは、**どのRealizationを使い、何を入力し、何を出力し、どのProvenanceや残差があったかを区別して保持できること**です。

外部repositoryで配布されるSkillやPrompt pack等をRealizationとして使う場合も、repository名、commit、path等をCognitive MethodのUniversal fieldへ直接持ち込みません。取得元はProvenanceとして保持し、Method Definition / Realizationの意味とartifact取得方式を分離します。

AI modelを含むRealizationでも同じです。model tagやinference runtimeは実行の再構成に必要なProvenanceになり得ますが、それらをCognitive Method Definitionのsemantic identityと同一視しません。

## 4. Provider exchange

同じCapabilityに複数Providerを対応させられます。

```text
Capability
   ├─ Provider A
   └─ Provider B
```

Provider固有stateは、そのままSOZA Universal Provider Stateへ統合しません。Provider Adapterを介し、その判断文脈で必要な観測だけをCapability Observationへmappingします。

ProviderをAからBへ変えても、Capability identityを自動的に変更しません。また、新しいProvider Observationが得られても、過去Decisionがbasisとして使ったAのObservationをBへ差し替えません。

TEIもこの原則の例外ではありません。TEI固有のExecutor、Observation route、Evidence route、Plugin Runtime、deployment state等はTEI側の表現として扱い、SOZAのUniversal Provider schemaへ昇格させません。

## 5. Evidence ladder

PMS-06では、交換可能性のEvidenceを次の段階に分けます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 operational portability
```

これは技術の価値序列ではありません。何を実際に確認できたかを混同しないためのEvidence上の区分です。

### E1 — Contract / in-process synthetic

- Cognitive Method Definition / Realization / Applicationを型として分離できる。
- synthetic Provider A / BをAdapterで交換できる。

**Scoped Executable Evidence available.**

### E2 — out-of-process reference exchange

ISSUE-000057では、Method RealizationとProvider state sourceをSOZA runtimeとは別のOS processとして実行し、出力をcurrent Contract / Adapterへ戻しました。

Provider / Methodを交換してもhistorical Decisionを変更しないこと、異なるRecommendationをDecisionへ自動昇格しないこと等を確認しています。

**Scoped Executable Evidence available.**

### E3a — version固定した実外部artifact integration

ISSUE-000058では、SOZAとは別repositoryで独立にversion管理される実artifactを扱いました。

#### Cognitive Method artifact

`hat47x/cultural-substrate-weaving`の日本語版`weave` Skillを固定revisionで取得し、source identityとbytesを検証したうえでMethod Realizationへ結び付けました。

これはSkill artifactを取得・検証してRealizationへ結び付けられたというEvidenceです。SkillをLLM上で実行してMethod Applicationを得たことまでは示しません。

#### Capability Provider artifact

`hat47x/tei-platform`の固定revisionに対応するobserved deployment stateをpinned snapshotとして扱い、TEI固有schemaをreference Adapterでcurrent Capability Observationへmappingしました。

private repositoryへのlive accessを必須CIへ暗黙に要求しないため、このPASSをlive TEI integrationとは扱いません。

**Scoped Executable Evidence available.**

## 6. E3b — live external process / service integration

E3bでは、version固定artifactを読むだけでなく、SOZAとは独立した外部process / serviceを実際に呼びます。

一度にproduction integrationまで固定せず、現在はEvidenceを次へ分けています。

```text
E3b-P1 public live Provider service
E3b-P2 actual TEI process / service
E3b-M1a live KJ Atlas process + deterministic model stub
E3b-M1b live external model-backed KJ execution
```

P1 / P2 / M1a / M1bはEvidence範囲を明らかにするための作業上の名称であり、SOZAのUniversal ontologyではありません。

### 6.1 E3b-P1 — public live Provider service

ISSUE-000060では、public GitHub REST APIの固定commit取得面をreference Providerとして実際に呼びました。

live responseのrevision identityが期待値と一致する場合だけCapability Observationへmappingし、GitHub固有のURL、`node_id`、response shape等をUniversal Contractへ転写しません。

revision mismatch、HTTP failure、timeout / cancellationではCapability Observationを生成しないことも確認しています。

**Scoped Executable Evidence available.**

### 6.2 E3b-P2 — actual TEI process / service

ISSUE-000061では、actual TEI CLI integrationの前段として次を分離しました。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

`runtime/go/teiintegration`では、外部から明示的に与えられたexecutableを呼べるAdapter境界を実装しています。

helper subprocessによるdeterministic testにはScoped Executable Evidenceがありますが、**helper subprocessのPASSだけをactual TEI CLI executionのEvidenceとは扱いません**。

ISSUE-000065では、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定し、TEI側Workflow Run `33589084290`でactual `cmd/tei`をbuildして`deployment-provider-plan`を実行しました。得られたactual artifactをcurrent SOZA Adapterから別OS processとして起動し、strict decode、Capability Observation mapping / validation、Provider固有情報の非漏出を確認しています。

したがって、E3b-P2は**fixed-artifact scopeでScoped Executable Evidence available**です。SOZA Actionsからprivate repositoryを継続取得するcredential運用、任意TEI version互換性、production integrationは別の未検証範囲として残します。

### 6.3 E3b-M1a — live KJ Atlas process + deterministic model stub

ISSUE-000064では、public repository `hat47x/kj-atlas`を固定commitで取得し、KJ Atlas FastAPI backendとKJ Atlas同梱のdeterministic model stubをSOZAとは別processとして実際に起動しました。

- repository: `hat47x/kj-atlas`
- commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- entry point: `POST /ai/suggest-card-groups`

KJ Atlas自身のHTTP endpointからactual grouping responseを取得し、SOZAのreference Adapterへ戻します。

KJ Atlas固有responseはSOZA Universal Cognitive Method Contractへ昇格させません。JSONの意味内容をopaqueな`not_verified` Method outputとして保持し、source repository、commit、entry point、result digestをopaque Provenanceとして残します。

既存Cognitive Method Applicationは、Realization / output / Provenanceを参照します。

また、grouping候補をRecommendationやDecisionへ自動昇格させません。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision
```

PR #41では、KJ Atlas checkout、backend install、migration、model/backend process起動、actual grouping、SOZA mapping boundary、actual result mappingまでを専用workflowで実行し、成功しています。

**Scoped Executable Evidence available for M1a scope.**

### 6.4 E3b-M1b — live external model-backed KJ execution

ISSUE-000066では、M1aと同じKJ Atlas revisionとMethod surfaceを保ち、model processだけを実際に推論するartifactへ置き換えました。

最初の実証条件は次です。

- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Inference runtime: Ollama `0.32.14`
- Model: `qwen2.5:0.5b`
- Observed model ID: `a8b0c5157701`
- KJ Atlas model boundary: `POST /generate`

integration-only AdapterはKJ Atlasのpromptを変更せず、Ollamaのtransportへ変換するだけに限定しています。group labelやcard ID等の意味内容をAdapter側で生成・補正しません。

先行Workflow Run `33596839607`では、actual model取得、KJ Atlas backend起動、actual `POST /ai/suggest-card-groups`、SOZA Method mappingまでをskipなしで実行しました。Ollamaからは`prompt_eval_count = 196`、`eval_count = 78`が記録され、process起動だけでなくprompt評価とtoken生成を伴うactual inferenceが確認できました。

KJ Atlasはactual model outputを受理し、二つの対象cardを一つのgroup候補として返し、held cardを`excludedCardIds`へ分離しました。そのresultはM1aと同じSOZA mapping boundaryからCognitive Method Applicationへ戻しています。

```text
actual model inference succeeded
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation
  != Decision
```

したがって、E3b-M1bは**actual model-backed executionの範囲でScoped Executable Evidence available**です。model品質、KJ法としての成果品質、任意model / runtime version互換性は別の未検証範囲として残します。

## 7. 外部source identityとsemantic identityを分ける

外部integrationでは、repository、commit、path、blob identity、result digest、service revision、executable path、inference runtime、model tag等を追跡に使うことがあります。

しかし、それらはSOZAのsemantic identityそのものではありません。

```text
repository / commit / path / blob identity
  != Method Definition identity
  != Capability identity
  != Decision identity

executable path / credential / process command
  != Capability identity
  != semantic authority

model tag / runtime version
  != Cognitive Method Definition identity
  != Recommendation
  != Decision
```

GitHub、Git、HTTP、CLI、FastAPI、SQLite、Ollamaを使っていること自体をUniversal Coreへ持ち込みません。他のartifact store、Provider service、process surface、model runtimeへ交換できる余地を残します。

一方、modelやruntimeの交換をまたいで過去Applicationを再構成する際に、どこまでのidentityをDurable Provenanceとして保持すべきかは、今後のversion交換実証で検討します。

## 8. 外部Method outputとRecommendation / Decisionを分ける

外部Cognitive Methodから返る結果は、それだけでRecommendationやDecisionではありません。

たとえばKJ Atlasのgrouping候補は、カードをどうまとめられそうかというMethod outputです。そこからどのRecommendationを作り、何をDecisionとするかは別の意味境界です。

```text
Method output
  → may inform Recommendation
  != Recommendation automatically
  != Decision automatically
```

この分離により、Method Realizationやmodelを交換したときに異なるgroupingや解釈候補が返っても、過去Decisionを自動的に書き換えずに保持できます。

## 9. failure時の境界

external integrationでは、少なくとも次を分けます。

- source identity mismatch
- acquisition failure
- credential failure
- process start / network failure
- model artifact acquisition failure
- inference failure / timeout
- Provider / Method固有responseのinvalid shape
- Adapter mapping failure
- semantic validation failure

failureを一つのgeneric errorへ潰さない一方、外部system固有のerror vocabularyをUniversal Contractへ先取りしません。

KJ Atlas M1a / M1bのreference mappingでは、invalid responseやduplicate targetでcanonical stateを部分更新しないことを検査します。これはsingle-thread reference probeの安全策であり、production transaction semanticsを定義するものではありません。

## 10. Releaseとの関係

v0.2.0 Local Reference Product Baselineについては、`release/v0.2.0/RELEASE_EVIDENCE.md`でRelease EvidenceがSatisfiedとなっています。

ただし、v0.2.0でsupportを主張するRealization / Provider exchangeの範囲はE3aまでです。

E3b-P1、E3b-P2 fixed-artifact、E3b-M1a、E3b-M1bのScoped Executable Evidenceは、そのrelease後に存在するcurrent repository Evidenceとして扱います。

```text
post-release E3b Evidence
  != v0.2.0 supported scope expanded
  != v0.2.0 Release Evidence expanded
```

## 11. 現在のEvidence表

| 範囲 | Current Evidence | 主なIssue | 現在の非主張 |
| --- | --- | --- | --- |
| E1 Contract / synthetic | Scoped Executable Evidence | ISSUE-000043等 | production Realization |
| E2 out-of-process reference exchange | Scoped Executable Evidence | ISSUE-000057 | external independent artifact |
| E3a version-pinned external artifact | Scoped Executable Evidence | ISSUE-000058 | live Provider / Method execution |
| E3b-P1 public live Provider | Scoped Executable Evidence | ISSUE-000060 | actual TEI / external Method |
| external TEI executable injection boundary | Scoped Executable Evidence | ISSUE-000061 | actual TEI / credential operation |
| E3b-P2 actual TEI | Fixed-artifact Scoped Executable Evidence | ISSUE-000065 | credential operation / arbitrary version / Operational portability |
| E3b-M1a live KJ Atlas + model stub | Scoped Executable Evidence | ISSUE-000064 | actual model-backed execution / model quality |
| E3b-M1b live external model-backed Method | Scoped Executable Evidence | ISSUE-000066 | model・KJ-method quality / arbitrary model・runtime version / Operational portability |
| E4 operational portability | Not Yet Verified | — | — |

## 12. 次の探索点

次に固定せず調べる領域は次です。

- fixed-artifact Evidenceを維持しながら、private repository credentialをacquisition / deployment policyへどう閉じ込めるか
- TEI executableの配布・更新経路をどの段階で正式化するか
- TEI CLI version交換時のProvenance / Exact Binding水準
- model / runtime version交換時に、historical Method Applicationを十分に再構成するためのProvenance水準
- model出力品質とCognitive Methodとしての成果品質を、semantic execution Evidenceからどう独立に評価するか
- formal integration protocolを本当に標準化する必要があるか
- E4 Operational portabilityを何で評価するか

## 13. Requirement化の境界

E2〜E3bの実証で使ったGitHub、HTTP、CLI、FastAPI、SQLite、Ollama等を、そのままStable Requirementへ昇格させません。

新しいStable Requirementが必要なのは、特定実装を越えて残る意味差が確認された場合です。

M1a / M1bで確認した境界は、現時点では既存のCognitive Method交換可能性、historical Decision reconstruction、Realization / Execution交換のRequirement / Scenarioで表現できます。ISSUE-000066のactual model接続でも、それらで表せない独立したProduct failureは確認されなかったため、新しいREQ / SCNを追加しません。

model / runtime version交換を行った結果、現在のProvenanceでは過去Applicationを十分に区別できないことが分かった場合は、その時点でCandidate Requirementとして上流へ戻します。

## 14. 自然な日本語レビュー

PMS-06、ADR-0017 / 0021 / 0025、ISSUE-000057〜000066、current Cognitive Method / Capability Observation Contract、E3a / E3b Provider Evidence、v0.2.0 Release Evidence、KJ Atlas固定commitのM1a / M1b actual integration結果、固定TEI artifactのactual execution結果を照合しました。

そのうえで、外部artifactを取得したEvidence、public Providerをliveに呼んだEvidence、TEI executable注入境界、fixed-artifact actual TEI execution、KJ Atlasをdeterministic model stubでlive実行したM1a、actual inference modelへ置き換えたM1bを一つの段階へ潰さず、それぞれ何を確認したかが自然に読めるよう整理しました。

M1bについては、actual inferenceの成立と生成品質を明確に分けています。実モデルを通せたことを「良いgroupingができた」「KJ法として十分である」「RecommendationやDecisionが成立した」と読み替えない停止線も維持しました。

意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。