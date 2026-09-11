# ADR-0012: Capability ChoiceのSemantic Boundaryを定める

Status: **Accepted**  
Related Issues: **ISSUE-000013, ISSUE-000020, ISSUE-000024**  
Updated: 2026-08-31

## Context

SOZAでは、人間、AI、SaaS、外部組織、TEI、custom code等を、同じIntentに対する異質なCapability候補として扱える必要がある。

このとき、Capabilityの定義、現在の状態、適合評価、選択判断、Authority、Executionを一つへまとめると、現在利用できない手段を「存在しない」ものとして扱ったり、Matching結果を自動実行へ昇格させたりする危険がある。

## Decision

### Capability DefinitionとObservationを分離する

Capability Definitionは、「何を可能にする手段か」を表す耐久的な意味資産である。

Capability Observationは、そのCapabilityや提供候補について、ある時点で観察されたavailability、condition、cost、latency、auditability等を表す。

```text
Capability Definition != Capability Observation
```

現在利用不能というObservationがあっても、Capability Definitionを削除しない。また、Observationがないことも「利用不能」を意味しない。

### Matchingは説明可能な適合関係でありDecisionではない

MatchingはIntent、Constraint、contextとCapabilityを照合し、なぜ候補になり得るか、何が不足・競合・未確認かを外在化する。

```text
Matching != Recommendation != Decision != Authority != Execution
```

Matching結果を、そのまま採用判断やAuthorizationへ昇格させない。

### Universal score / global rankingを持たない

異質な候補を単一のnumeric scoreへ正規化し、最大値を自動選択することをCore要件にはしない。比較軸やdomain-specificな評価方法は、必要に応じてProfile / Policy / Method側で追加できる。

### Capability ChoiceはDecision境界で扱う

実際にCapabilityを採る、採らない、組み合わせる、保留するという判断はDecisionとして扱う。

現時点では、独立したUniversal `CapabilitySelection` Artifactは作らない。

一つのIntentから必ず一件だけ選ぶことも要求しない。複数Capabilityの組み合わせ、条件付き候補、選択保留、Matchingだけで終わる状態を許す。

### CapabilityとProviderを分離する

```text
Capability != Provider
```

Capabilityは「何を可能にするか」、Providerは「誰／何がそれを実現するか」を表す。Decision時点でCapabilityだけを選び、Providerを未確定のまま残してもよい。

TEI、AI、人間、SaaS等のkindだけから優先度、信頼、Authorityを推定しない。SOZAとの関連が深いことを理由にTEIを優遇しない。

### Unknownをincompatibleへ潰さない

```text
not observed != unavailable
unknown compatibility != incompatible
```

現在のEpistemics / Capability Observation境界に従い、未観測・未知・不適合を区別する。

### 過去Choiceを当時の状態で再構成する

後からCapability DefinitionやObservationが変わっても、過去Decisionが何を根拠に選んだかを書き換えない。必要な可変ArtifactにはExactArtifactBindingを用い、Decision revisionにはSemantic Lineageを再利用する。

### Choiceは実行権限ではない

```text
Capability Choice Decision
  != Authorization
  != Action Intent
  != Provider Execution
```

Capabilityを提供、管理、選定、監督する責任は、必要に応じて既存のResponsibility境界から表す。

## Current realization

current repositoryでは、`sei.capability-observation/v1alpha1`、F1〜F7 fixture、first semantic runtime、synthetic Provider Adapter sliceまで実体化している。

これにより、少なくとも次をExecutable Evidenceとして確認している。

- Provider固有の状態をCapability Definitionそのものへ混ぜず、Capability Observationとして外在化できる。
- 同じCapabilityに対して異なるProviderのObservationを保持できる。
- Observationの欠落を`unavailable`へ変換しない。
- Provider Adapterのmapping結果をDecision / Authority / Executionへ自動昇格させない。
- Provider固有SchemaをUniversal Capability Observation field setへ昇格させない。

一方、UniversalなCapability Definition wire schema、Matching runtime、Capability Choice専用runtimeを完成したとは主張しない。Choiceは引き続きDecision境界から扱う。

## Deferred implementation choices

次は意味境界ではなく実現方式であるため、必要性を確認してから定める。

- Capability Definitionの具体的なwire representation
- Matching resultのrepresentation / status vocabulary
- Decisionからchosen Capabilityを指す具体形
- candidate setの表現
- domain-specific comparison facet

Provider realization / offeringのUniversal型要否はADR-0013で別途判断する。

## Consequences

- 人間・AI・SaaS・TEI等を中立的なCapability判断面へ置きやすい。
- stale ObservationやProvider変更によってCapability identityが壊れにくい。
- MatchingをPlanner authorityへ肥大化させにくい。
- UI / ProjectionではDefinition、Observation、Matching、Choiceを必要に応じて組み合わせる必要がある。

## Revisit conditions

現在の分離では、実際の複数ScenarioでCapability候補の比較、選択、過去Decisionの再構成に必要な意味を保てないことが確認された場合に再検討する。

## Natural Japanese review

current Capability Observation Contract、Provider Adapter、Decision Memory、SOZA / TEI境界へ戻ってDecisionを照合した。その後、旧Milestone名と未実体化時点の表現をcurrent Evidenceへ更新し、Capability Definition / Observation / Matching / Choice / Authority / Executionの意味差を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後にEvidence強度を含めて意味監査を実施済みである。
