# ADR-0025: Cognitive Methodのportable Contract境界を独立させる

Status: **Accepted**  
Related Issue: **ISSUE-000043**  
Updated: 2026-09-01

## Context

SOZAのReference ArchitectureとADR-0017では、Cognitive Methodについて次の意味差をすでにAcceptedしている。

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance
```

REQ-0004はCognitive Methodを特定Prompt、Skill、model program、人間手順等の一つのRealizationと同一視しないことを要求し、REQ-0015はprivate chain-of-thoughtへ依存しないことを要求する。SCN-0005とSCN-0015は、この境界を具体的な交換・再構成Scenarioとして定義している。

一方、v0.1.0までのcurrent repositoryにはCognitive Method専用のportable Contractがなく、SCN-0005 / SCN-0015のExecutable Evidenceは`Not Yet Verified`である。

historical M47にはMethod関連資産が存在したが、current Contract CatalogとHistorical Contract Mappingが定めるとおり、旧field set、schema、digest規則、local PASSをcurrent authorityへ自動継承しない。ISSUE-000034でhistorical digest ruleを回収不能と確定したことも、current Method Contractを推測で復元する理由にはしない。

v0.2.0では、current Product Value / Requirements / ArchitectureからCognitive Method interoperabilityの最小境界を改めて定義する必要がある。

## Decision

### 1. `sei.cognitive-method/v1alpha1`を独立Contract familyとする

Cognitive MethodのDefinition、Realization、Applicationを実装間で交換し、historicalに再構成する必要があるため、次をcurrent pre-stable Contract familyとして独立させる。

```text
sei.cognitive-method/v1alpha1
```

これはhistorical M47 Contractの復元ではない。current Requirementsから新たに定義するContractである。

### 2. record typeは3種類に限定する

v1alpha1では次だけをportable record typeとする。

```text
method_definition
method_realization
method_application
```

#### Method Definition

Methodそのものの耐久的意味を表す。

最低限、次を扱えるようにする。

- logical identity
- 人間がMethodを識別するtitle
- purpose / semantic description
- 必要に応じたcontext / specificationへのReference
- extensions

固定step machine、Prompt文字列、特定AI model、特定domain PatternをMethod Definitionの必須構造にはしない。

#### Method Realization

あるMethodを現時点でどのように実現するかを表す交換可能な実現層である。

最低限、次を扱えるようにする。

- Realization自身のlogical identity
- 対象MethodへのReference
- 実現内容の外在化されたdescription
- Prompt、code、procedure、tool等の実装ArtifactへのReference
- extensions

`realization_kind`の固定Universal enumは作らない。必要ならExtension / Profile / referenced Artifact側で表す。

#### Method Application

特定のInquiryや作業でMethodを適用した事実と、後から再構成するための外在化された来歴を表す。

最低限、次を扱えるようにする。

- Application自身のlogical identity
- 使用したMethodへのReference
- 使用したRealizationへのReference（判明・必要な場合）
- context refs
- input refs
- output refs
- residual refs
- provenance refs
- contextual Responsibility refs
- applied_at（分かる場合）
- 外在化されたsummary / note
- extensions

### 3. Referenceはlogical / exactの両方を利用できる

Method、Realization、input、output等のReferenceには、current Semantic Reference ContractのReference境界を再利用する。

```text
Logical Reference != Exact Historical Binding
```

過去Applicationの再構成に特定版のMethod / Realization / inputが重要な場合だけExact Bindingを利用する。すべての低影響Applicationへexact bindingを強制しない。

### 4. RealizationはApplicationの必須条件にしない

Method Application時にMethod Definitionは特定できるが、利用したRealizationが不明・不要・外部管理である場合を許容する。

```text
realization not recorded
  != realization did not exist
  != method not applied
```

欠落を否定事実へ変換しない。

### 5. Method Applicationを後続意味へ昇格させない

Cognitive Method Contract自体に、Recommendation、Decision、Authority、Execution、Assuranceの成立を示すfieldを持ち込まない。

```text
Method Application
  != Recommendation
  != Decision
  != Authority
  != Execution
  != Assurance
```

MethodのoutputがRecommendationや別Artifactである場合は`output_refs`から別Contract recordを参照できる。しかし、そのReferenceが存在することから採用Decisionや正しさを推定してはならない。

### 6. Pattern / Reference ModelをCognitive Method Contractへ統合しない

PatternやReference ModelはADR-0017どおりdomain-specific Design Knowledgeとして扱う。

Method ApplicationがPatternを探索・比較した場合、そのPatternはinput / context等へのReferenceとして扱える。

```text
Pattern referenced by Method
  != Pattern becomes Method
  != Pattern match becomes Decision
```

Pattern専用Universal field setやPattern match scoreを本Contractへ追加しない。

### 7. private chain-of-thoughtを要求しない

Method Applicationの適合条件として、AI内部の非公開推論列、token列、hidden state等を保存・復元することを要求しない。

外在化するのは、Method identity、主要input / output / residual、provenance、Responsibility、必要なsummary等である。

```text
portable Method Application
  != private reasoning transcript
```

### 8. Method revisionはSemantic Referenceのlineageを再利用する

Method DefinitionやRealizationの改訂のために専用version graphを新設しない。

logical identity、Exact Binding、Semantic Lineageをcurrent Semantic Reference Contractから再利用する。

Contract versionとMethod自身のsemantic revisionも区別する。

```text
Contract version
  != Method semantic revision
  != Realization revision
```

### 9. unknown Contract versionは従来どおりopaqueに保持する

Semantic Interchange内に未知の`sei.cognitive-method` versionが存在する場合、runtimeは既知versionとして解釈せず、payloadをopaqueに保持して`not_verified`とする。

既存のforward-compatible Interchange境界を弱めない。

## Consequences

### Positive

- SCN-0005 / SCN-0015をcurrent repositoryで直接検査できる入口ができる。
- PromptやAI modelを交換してもMethod identityとApplication historyを残せる。
- Pattern / Method / Recommendation / Decision / Assuranceの境界をExecutable Evidenceへ落とせる。
- private chain-of-thoughtに依存しない再構成を実装できる。
- historical M47の未回収digest ruleにcurrent Method workが拘束されない。

### Costs

- Contract familyが1つ増え、schema / fixture / runtime validator / traceabilityを保守する必要がある。
- Method Definitionを過度に構造化しないため、domain-specificな詳しい手順はReference / Extension側との組合せが必要になる。
- Applicationの完全再現と「主要な来歴を再構成できること」は別であり、後者をContractの目的として明示し続ける必要がある。

## Rejected alternatives

### historical M47 schemaをそのままcurrent Contractにする

却下する。historical assetは設計入力でありcurrent authorityではない。digest規則も回収不能である。

### PromptをMethod identityにする

却下する。REQ-0004 / V8に反する。

### Method ApplicationへRecommendation / Decision / Assuranceを埋め込む

却下する。意味上の自動昇格と責任線の混同を招く。

### Universalなstep / phase ontologyを必須化する

却下する。KJ法、人間手順、model program、将来の方法を一つの固定workflowへ押し込む必要はない。

## Revisit conditions

次の場合に再検討する。

- 複数の独立実装でMethod Definitionのportable procedure structureが不可欠と実証される。
- Realizationの種類に、Providerをまたいで安定したUniversal semantic distinctionが必要になる。
- Method Applicationだけでは表現できない反復的なsession / checkpoint意味が複数Scenarioで不可欠になる。
- Patternをdomain-specific knowledgeとして外に置くと複数domainで同じ重要意味を失うことが実証される。

## Evidence / follow-up

- REQ-0003, REQ-0004, REQ-0015, REQ-0016, REQ-0021
- SCN-0005, SCN-0015
- ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0022
- ISSUE-000043

本ADRはDesign Evidenceである。schema、fixture、runtime、CIが成立するまではCognitive MethodのExecutable EvidenceをSatisfiedへ引き上げない。

## Natural Japanese review

current Product Value、REQ-0003 / 0004 / 0015 / 0016 / 0021、SCN-0005 / 0015、ADR-0017、Reference Architecture、Contract Catalog、Historical Contract Mapping、current Semantic Reference / Decision Memory / runtime境界へ戻って設計を組み直した。historical M47を正本化せず、Definition / Realization / Applicationの意味差、Pattern分離、private chain-of-thought非依存、Exact Binding、未知version保持をcurrent要件から導出した。その後、意味、規範強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
