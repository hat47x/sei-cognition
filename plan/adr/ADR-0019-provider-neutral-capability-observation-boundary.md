# ADR-0019: Provider-neutralなCapability Observation境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000020**  
Updated: 2026-08-31

## Context

ADR-0012では、Capability DefinitionとCapability Observationを分離した。

ADR-0013では、Provider固有のOffering / Binding / DeploymentをUniversal `CapabilityRealization`へ統合しないことを決めた。

ADR-0014では、SOZAとTEIを別Product Boundaryとして維持し、TEI固有のApplication、Database、Release、Deployment等をSOZA Universal Coreへコピーしないことを定めた。

一方、SOZAがTEI、SaaS、人間、AI、外部組織等をCapability Providerとして比較するには、Provider内部の状態をすべて知らなくても、現在の利用可能性、条件、未確認点、Evidence等を読める必要がある。

ここでTEI固有SchemaをSOZAへ持ち込むとProvider Independenceを失う。逆に、Provider状態を単純な`available / unavailable`だけへ圧縮すると、Unknown、degraded state、部分的制約、Evidence、historical basisを失う。

## Decision

### 1. SOZAはProvider-neutralなObservation envelopeを所有する

SOZAが所有するのは、Provider内部Schemaそのものではなく、Capability判断に必要な観測結果を外在化するための意味境界である。

概念上、Observationは少なくとも次を参照できる。

- 対象となるCapability Definition
- Providerまたはbounded provider reference
- 必要に応じたProvider-specific context / offering / binding等へのReference
- 観測時点
- 観測されたproperty / condition
- Evidence / provenance
- Unknown / Conflict / Withheld等の認識状態
- 必要に応じたexact historical binding

具体的なwire field名やproperty vocabularyは、このADRでは固定しない。

### 2. Provider内部Schemaはadapter境界の外側に残す

TEIのApplication、Database、Environment、Release、Plugin Lock、Migration、Deployment等はTEI側の正本として維持する。

SOZAは、それらを必要に応じてReference、Observation、Evidenceとして読む。

```text
Provider internal state
    ↓ adapter / observation profile
SOZA Capability Observation
    ↓ matching / inquiry / review
Recommendation or Decision
```

Provider内部の構造をSOZA Universal Coreへ複製しない。

### 3. adapterは単なるデータ変換ではなく、解釈境界として扱う

たとえばTEIで「Application Releaseは存在するがEnvironmentへ未Binding」「Databaseの一部がread-only」「Migration proposalが未採用」といった状態から、Capabilityが利用可能、制約付き、未確認等のどれに相当するかは自明ではない。

そのため、Provider状態からCapability Observationへの写像は、必要に応じてProfile、Mapping Definition、Cognitive Method等として外在化する。

重要なDecisionのbasisになった場合は、使用したmapping / adapter versionを後から特定できるようにする。

```text
Provider state != Capability interpretation
Capability interpretation != Decision
```

### 4. `not observed`を`unavailable`へ変換しない

観測できなかったこと、Providerが情報を開示しなかったこと、観測結果が競合したことを、単純な利用不能へ潰さない。

少なくとも意味として、次を区別できる設計を維持する。

- observed condition
- unknown / not observed
- conflicting observations
- withheld context

Provider-specificなstatus vocabularyをUniversal Coreへ固定する必要はない。

### 5. 比較用の正規化とraw provenanceを分ける

複数Providerを比較するために、availability、cost、latency、auditability等の共通facetへ正規化することはできる。

ただし、正規化値だけを残さず、元のProvider Observation、Evidence、mapping provenanceへ戻れるようにする。

```text
Normalized comparison facet != source observation
```

単一numeric scoreへの強制変換はADR-0012およびProduct Principlesに従いCore要件としない。

### 6. Decision basisになった可変入力はhistoricalに再構成可能にする

Capability ChoiceのDecisionが、特定のProvider state、release、binding、contract、mapping等へ依存する場合は、後から現在版へ差し替えず、必要なArtifactをExactArtifactBindingまたは同等の検証可能な参照で固定できるようにする。

すべての観測にexact bindingを義務付けない。Decisionの影響、可変性、再構成必要性に応じてProgressive Semantic Explicitnessを適用する。

### 7. Selective Disclosureを許容する

Providerが内部topologyや契約情報を全量開示できない場合でも、Capability判断に必要なObservation / Evidenceだけを共有できるようにする。

非開示情報が存在する場合は、単なるUnknownと区別できるよう`Withheld`相当の意味を保持する。

内部詳細を開示しないこと自体を、信頼不足やCapability不存在へ自動変換しない。

### 8. SOZAはProvider runtime authorityを取得しない

Capability Observationを読めることは、Providerを操作するAuthorityを持つことを意味しない。

```text
Observation access
  != Authorization
  != Action Intent
  != Provider Execution
```

SOZA DecisionからTEI等のProvider実行へ進む場合は、それぞれのAuthorization / Policy / Provider境界を別途通る。

## TEIへの適用

TEIをSOZAから読む場合、次を原則とする。

- TEI Application / Database等のcanonical schemaはTEI側に残す。
- TEI adapterはSOZAが必要とするCapability Observationへ必要最小限の情報を写像する。
- Databaseがread-onlyである等の状態を、無条件にCapability全体の`unavailable`へ変換しない。
- Migration proposalが未採用であることをactual state changedとみなさない。
- Releaseが存在してもEnvironment Bindingがなければ、対象Environmentで利用可能と自動判断しない。
- Observation Providerが利用不能な場合、その状態自体をUnknown / observation gapとして残せるようにする。
- Decisionのbasisとなったrelease / binding / Plugin Lock等は必要に応じてhistorical bindingを保持する。

## Consequences

### Positive

- TEI固有SchemaをSOZA Coreへ持ち込まずCapability判断に必要な情報を扱える。
- TEI、SaaS、人間、AI等を同じ意味境界で比較しやすくなる。
- Provider固有のUnknownや部分状態を失いにくい。
- adapterの解釈変更後も過去Decisionを再構成しやすい。
- Selective DisclosureとProvider Independenceを両立しやすい。

### Costs

- Providerごとにadapter / profile / mappingが必要になる。
- 比較Projectionはraw Observationとnormalized facetを組み立てる必要がある。
- mapping自体のversion / provenanceを管理する場面が生じる。
- actual wire schemaとportable fixtureは別途実装・検証が必要になる。

## Revisit conditions

次の場合に再検討する。

- 複数の異なるProviderで、現在のObservation envelopeでは表現できない同一の意味が反復する。
- adapter / mappingをProfile側に置くことでhistorical reconstructionが実務上成立しない。
- Provider-neutral comparisonのために、Universal Coreで共有すべき最小property vocabularyがactual scenarioから十分に収束する。

一つのProviderだけの都合を、Universal Core拡張の十分な理由にはしない。

## Evidence

- `product/value/SOZA_VALUE_MODEL.md` V1 / V2 / V3 / V4 / V5 / V7 / V8
- ADR-0006: Selective Disclosure
- ADR-0008: Exact Binding verification boundary
- ADR-0012: Capability Choice semantic boundary
- ADR-0013: Capability Realization boundary
- ADR-0014: SOZA / TEI Product boundary
- ISSUE-000020のrequired scenarios

## Follow-up

actual schema、provider-neutral fixture、TEI adapter fixture、cross-provider comparison fixtureはISSUE-000024で実体化する。

## Natural Japanese review

既存ADRとValue Modelを照合して意味境界を確定した後、条件、留保、技術的意味を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
