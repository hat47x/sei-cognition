# SOZA Realization / Provider Exchange

更新日: 2026-09-03  
状態: **Current Realization / Provider Exchange Design Baseline — E3b-P2 / M1b / historical reconstruction reflected, runtime-version exchange pending**

## 1. この文書の役割

この文書は、PMS-06「実際のMethod / Providerを交換しても判断記憶が保たれる」を進めるために、**何を交換可能とみなし、交換後にも何をcanonicalな判断記憶として守るか**をProduct levelで定めます。

SOZAにとって重要なのは、特定のAI、Prompt、process、SaaS、TEI、custom codeを長く使い続けることではありません。それらが入れ替わった後にも、当時のIntent、Observation、Method Application、Recommendation、Decision、Responsibility、Provenance、Unknown / Conflictを、その時点の意味を壊さず読み直せることです。

交換可能性は「別実装でも動いた」という一点では判断しません。実行手段を交換したあとも、どの実現を使い、何が起き、何が未検証で、過去の判断がどのbasisに基づいていたかへ戻れることを重視します。

## 2. 交換してよいものと、交換で失ってはならないもの

### 交換してよいもの

- Cognitive Method Realization
- AI model / Prompt / code-assisted tool
- inference runtime
- Capability Provider
- Provider Adapter
- external SaaS / TEI / custom code
- process topology
- Realization固有のwire protocol
- artifact repositoryや配布経路
- artifactの取得経路や実行場所

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
- 過去Applicationが参照していたExact Realization revision

```text
Realization exchange
  != Semantic Revision by itself

Provider exchange
  != Capability identity change by itself

runtime / model exchange
  != historical Application rewrite

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

AI modelを含むRealizationでも同じです。model tag、model artifact digest、inference runtime、runtime artifact digest等は実行の再構成に必要なidentity / Provenanceになり得ますが、それらをCognitive Method Definitionのsemantic identityと同一視しません。

同じlogical Realizationのhistorical revisionを区別する必要がある場合は、既存Cognitive Method ContractのExact Bindingを使います。

```text
same logical Realization
  + different execution revision
  → different Exact Binding

Exact Binding difference
  != different Method Definition automatically
```

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
  → E4 Operational portability
```

これは技術の価値序列ではありません。何を実際に確認できたかを混同しないためのEvidence上の区分です。

実行場所もEvidenceの意味と分けます。

```text
local test / repository checker / external runner / historical GitHub Actions
  = possible execution surfaces
  != Evidence meaning by themselves
```

current baselineではGitHub Actionsを常設していません。過去のActions Runは、その時点で実際に得られたEvidenceとして保持しますが、現在のProduct成立条件や再検証手段とは分離します。

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

private repositoryへのlive accessを常設の検証条件へ暗黙に要求せず、このPASSをlive TEI integrationとは扱いません。

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

ISSUE-000065では、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定しました。historical TEI-side Workflow Run `33589084290`ではactual `cmd/tei`をbuildして`deployment-provider-plan`を実行し、得られたactual artifactをcurrent SOZA Adapterから別OS processとして起動しました。その範囲でstrict decode、Capability Observation mapping / validation、Provider固有情報の非漏出を確認しています。

したがって、E3b-P2は**fixed-artifact scopeでScoped Executable Evidence available**です。

未検証として残るのは、特定automation providerからprivate repositoryを取得できるかではなく、より一般に次の領域です。

- private artifact acquisitionに必要なcredential lifecycle
- artifact取得・配布・更新policy
- 任意TEI versionへ交換したときの互換性
- production integration
- E4 Operational portability

historical RunがGitHub Actions上で成立したことはEvidenceとして保持しますが、GitHub Actions自体をP2のProduct条件にはしません。

### 6.3 E3b-M1a — live KJ Atlas process + deterministic model stub

ISSUE-000064では、public repository `hat47x/kj-atlas`を固定commitで取得し、KJ Atlas FastAPI backendとKJ Atlas同梱のdeterministic model stubをSOZAとは別processとして実際に起動しました。

- repository: `hat47x/kj-atlas`
- commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- entry point: `POST /ai/suggest-card-groups`

KJ Atlas自身のHTTP endpointからactual grouping responseを取得し、SOZAのreference Adapterへ戻します。

KJ Atlas固有responseはSOZA Universal Cognitive Method Contractへ昇格させません。JSONの意味内容をopaqueな`not_verified` Method outputとして保持し、source repository、commit、entry point、result digestをopaque Provenanceとして残します。

既存Cognitive Method Applicationは、Realization / output / Provenanceを参照します。また、grouping候補をRecommendationやDecisionへ自動昇格させません。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision
```

historical PR #41では、KJ Atlas checkout、backend install、migration、model/backend process起動、actual grouping、SOZA mapping boundary、actual result mappingまでを専用workflowで実行し、成功しています。

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

historical Workflow Run `33596839607`では、actual model取得、KJ Atlas backend起動、actual `POST /ai/suggest-card-groups`、SOZA Method mappingまでをskipなしで実行しました。Ollamaからは`prompt_eval_count = 196`、`eval_count = 78`が記録され、process起動だけでなくprompt評価とtoken生成を伴うactual inferenceが確認できました。

KJ Atlasはactual model outputを受理し、二つの対象cardを一つのgroup候補として返し、held cardを`excludedCardIds`へ分離しました。そのresultはM1aと同じSOZA mapping boundaryからCognitive Method Applicationへ戻しています。

```text
actual model inference succeeded
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation
  != Decision
```

したがって、E3b-M1bは**actual model-backed executionの範囲でScoped Executable Evidence available**です。

ISSUE-000071では、この実行成立と成果品質を一つのPASSへ潰さない評価境界を確立しました。execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeを分離し、golden groupingやAIによる単一quality scoreを意味上の正解にはしていません。

```text
M1b execution PASS
  != human review completed
  != KJ-method outcome quality satisfied
```

## 7. historical reconstructionとversion交換

E3bが成立した後は、「別の実現を呼べたか」だけでなく、交換前後の履歴をどこまで再構成できるかを検査しています。

### 7.1 ISSUE-000067 — Definition / Realization / Applicationの再構成

ISSUE-000067では、Method Definition、logical Realization、historical Realization revision、Method Applicationを分離しました。

```text
different realization mechanism
  → different logical Realization

same mechanism / different historical revision
  → same logical Realization
  + different Exact Binding
```

この境界により、後続versionを使ったからといって過去Applicationを現在revisionへ付け替えない構造を確認しています。

### 7.2 ISSUE-000068 — model artifact exchange

ISSUE-000068では、KJ Atlas source、runtime、Method inputを固定し、actual model artifactだけを交換しました。

後続modelによるApplicationを追加しても、先行ApplicationのRealization、Provenance、outputを保持できることをScoped Executable Evidenceとして確認しています。

```text
model artifact exchange PASS
  != arbitrary model compatibility
  != model quality equivalence
```

### 7.3 ISSUE-000070 — runtime version exchange

ISSUE-000070では交換軸をさらに狭め、同じKJ Atlas source、同じMethod input、同じactual model artifactの下でOllama runtime versionだけを交換します。

- revision A: Ollama `0.32.13`
- revision B: Ollama `0.32.14`
- model: `qwen2.5:0.5b`
- fixed model artifact digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`

repository-local harness、fixed runtime artifact guard、Exact Binding control、run単位のEvidence保存、preflightは実装済みです。

一方、current harnessによるactual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していません。したがってISSUE-000070はOpenであり、runtime-version-exchange Scoped Executable Evidenceは**Not Yet Verified**です。

```text
preflight ready
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

GitHub Actionsや特定runnerの復旧はResolution条件にしません。actual実験の意味はrepository-local harnessと固定artifact identityへ戻します。

## 8. 外部source identityとsemantic identityを分ける

外部integrationでは、repository、commit、path、blob identity、result digest、service revision、executable path、inference runtime、model tag、artifact digest等を追跡に使うことがあります。

しかし、それらはSOZAのsemantic identityそのものではありません。

```text
repository / commit / path / blob identity
  != Method Definition identity
  != Capability identity
  != Decision identity

executable path / credential / process command
  != Capability identity
  != semantic authority

model tag / runtime version / artifact digest
  != Cognitive Method Definition identity
  != Recommendation
  != Decision
```

GitHub、Git、HTTP、CLI、FastAPI、SQLite、Ollamaを使っていること自体をUniversal Coreへ持ち込みません。他のartifact store、Provider service、process surface、model runtimeへ交換できる余地を残します。

ただし、過去Applicationが「どの実行revisionを使ったか」を再構成するために必要なidentityは、ProvenanceやExact Bindingとして保持します。semantic identityとhistorical execution identityを同一視しないことが重要です。

artifact acquisition modeも同様です。

```text
download / prepositioned
  = acquisition provenance
  != artifact identity
  != logical Realization identity
```

## 9. 外部Method outputとRecommendation / Decisionを分ける

外部Cognitive Methodから返る結果は、それだけでRecommendationやDecisionではありません。

たとえばKJ Atlasのgrouping候補は、カードをどうまとめられそうかというMethod outputです。そこからどのRecommendationを作り、何をDecisionとするかは別の意味境界です。

```text
Method output
  → may inform Recommendation
  != Recommendation automatically
  != Decision automatically
```

この分離により、Method Realizationやmodel、runtimeを交換したときに異なるgroupingや解釈候補が返っても、過去Decisionを自動的に書き換えずに保持できます。

## 10. failure時の境界

external integrationでは、少なくとも次を分けます。

- source identity mismatch
- artifact digest mismatch
- acquisition failure
- credential failure
- process start / network failure
- model artifact acquisition failure
- inference failure / timeout
- Provider / Method固有responseのinvalid shape
- Adapter mapping failure
- semantic validation failure
- Exact Binding verification failure
- historical reference resolution failure
- outcome-quality未評価

failureを一つのgeneric errorへ潰さない一方、外部system固有のerror vocabularyをUniversal Contractへ先取りしません。

KJ Atlas M1a / M1bのreference mappingでは、invalid responseやduplicate targetでcanonical stateを部分更新しないことを検査します。これはsingle-thread reference probeの安全策であり、production transaction semanticsを定義するものではありません。

また、`not_verified`と`failed`を同一視しません。

```text
not executed / not evaluated
  != failed

preflight PASS
  != actual execution PASS

structure PASS
  != outcome quality PASS
```

## 11. Releaseとの関係

v0.2.0 Local Reference Product Baselineについては、`release/v0.2.0/RELEASE_EVIDENCE.md`でRelease EvidenceがSatisfiedとなっています。

ただし、v0.2.0でsupportを主張するRealization / Provider exchangeの範囲はE3aまでです。

E3b-P1、E3b-P2 fixed-artifact、E3b-M1a、E3b-M1b、後続のhistorical reconstructionやmodel exchangeのScoped Executable Evidenceは、そのrelease後に存在するcurrent repository Evidenceとして扱います。

```text
post-release E3b Evidence
  != v0.2.0 supported scope expanded
  != v0.2.0 Release Evidence expanded
```

ISSUE-000070が将来Resolvedになっても、そのEvidenceを理由に既存v0.2.0のsupported scopeを遡及的に変更しません。

## 12. 現在のEvidence表

| 範囲 | Current Evidence | 主なIssue | 現在の非主張 |
| --- | --- | --- | --- |
| E1 Contract / synthetic | Scoped Executable Evidence | ISSUE-000043等 | production Realization |
| E2 out-of-process reference exchange | Scoped Executable Evidence | ISSUE-000057 | external independent artifact |
| E3a version-pinned external artifact | Scoped Executable Evidence | ISSUE-000058 | live Provider / Method execution |
| E3b-P1 public live Provider | Scoped Executable Evidence | ISSUE-000060 | actual TEI / external Method |
| external TEI executable injection boundary | Scoped Executable Evidence | ISSUE-000061 | actual TEI / credential lifecycle |
| E3b-P2 actual TEI | Fixed-artifact Scoped Executable Evidence | ISSUE-000065 | private artifact credential lifecycle / arbitrary version / Operational portability |
| E3b-M1a live KJ Atlas + model stub | Scoped Executable Evidence | ISSUE-000064 | actual model-backed execution / model quality |
| E3b-M1b live external model-backed Method | Scoped Executable Evidence | ISSUE-000066 | model・KJ-method quality / arbitrary model・runtime version / Operational portability |
| historical Method reconstruction boundary | Scoped Executable Evidence | ISSUE-000067 | arbitrary realization portability |
| actual model artifact exchange | Scoped Executable Evidence | ISSUE-000068 | arbitrary model compatibility / quality equivalence |
| runtime version exchange | Harness / guards / preflight implemented, actual A/B Not Yet Verified | ISSUE-000070 | runtime-version-exchange Scoped Executable Evidence |
| Method outcome-quality evaluation boundary | Evaluation boundary established | ISSUE-000071 | human review completion / outcome quality satisfied |
| E4 Operational portability | Not Yet Verified | — | — |

## 13. 次の探索点

次に固定せず調べる領域は次です。

- ISSUE-000070のactual Ollama `0.32.13` / `0.32.14`交換を固定artifact条件で完走できるか
- fixed-artifact Evidenceを維持しながら、private artifact credential lifecycleをacquisition / deployment policyへどう閉じ込めるか
- TEI executableの配布・更新経路をどの段階で正式化するか
- fixed revision以外のTEI version交換でも同じ意味境界を保てるか
- actual human reviewからCognitive Method成果品質をどう評価し、execution conformanceと分離して保持するか
- model / Method / Provider / runtime交換をまたぐhistorical reconstructionをどこまで一般化できるか
- formal integration protocolを本当に標準化する必要があるか
- E4 Operational portabilityを何で評価するか

## 14. Requirement化の境界

E2〜E3bの実証で使ったGitHub、HTTP、CLI、FastAPI、SQLite、Ollama等を、そのままStable Requirementへ昇格させません。

新しいStable Requirementが必要なのは、特定実装を越えて残る意味差が確認された場合です。

M1a / M1b、historical reconstruction、model artifact exchangeで確認した境界は、現時点では既存のCognitive Method交換可能性、historical Decision reconstruction、Realization / Execution交換のRequirement / Scenarioで表現できます。これらで表せない独立したProduct failureが確認されていないため、新しいREQ / SCNは追加しません。

ISSUE-000070のactual runtime交換で、現在のProvenance / Exact Bindingでは過去Applicationを十分に区別・再構成できないことが分かった場合は、その時点でCandidate Requirementとして上流へ戻します。

成果品質についても、ISSUE-000071で評価境界を設けたこと自体をStable Requirement追加の根拠にはしません。human reviewや実利用から、特定実装を越えて必要なProduct上の意味差が確認された場合に改めて検討します。

## 15. 自然な日本語レビュー

PMS-06、ADR-0017 / 0021 / 0025、ISSUE-000057〜000071、current Cognitive Method / Capability Observation Contract、E3a / E3b Provider Evidence、v0.2.0 Release Evidence、KJ Atlas固定commitのM1a / M1b actual integration、固定TEI artifactのactual execution、historical reconstruction、actual model artifact exchange、runtime version exchange harness、成果品質評価境界を照合しました。

そのうえで、外部artifactを取得したEvidence、public Providerをliveに呼んだEvidence、TEI executable注入境界、fixed-artifact actual TEI execution、KJ Atlasをdeterministic model stubでlive実行したM1a、actual inference modelへ置き換えたM1bを一つの段階へ潰さず、それぞれ何を確認したかが自然に読めるよう整理しました。

さらに、M1b成立後に進んだ履歴再構成をProduct境界へ戻しました。異なる実現機構はlogical Realizationを分け、同じ実現機構のhistorical revisionはExact Bindingで区別します。model artifact交換では先行Applicationを保持できた一方、runtime version交換はharness、guard、preflightまで整ったもののactual A / B実行は未完了です。この差を維持し、ISSUE-000070をOpenのまま扱っています。

成果品質についても、actual inferenceが成立したこと、構造検査を通ること、人間が成果を妥当と評価すること、Product Valueや利用成果へつながることを分離しました。ISSUE-000071のResolvedをhuman review完了やKJ法としての品質Satisfiedへ読み替えていません。

GitHub Actionsについては、過去Runが支えるhistorical Evidenceを保持しつつ、current Product条件や再検証手段から切り離しました。private TEIの未検証論点も、特定automation providerのcredential問題ではなく、private artifact acquisition / credential lifecycleという一般的なProduct運用境界へ戻しています。

意味、規範強度、supported scope、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
