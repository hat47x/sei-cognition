# ADR-0012: Capability ChoiceのSemantic Boundaryを定める

Status: **Accepted**  
Related Issue: **ISSUE-000013**  
Updated: 2026-08-31

## Context

SOZAは、人間、AI、SaaS、外部組織、TEI、custom code等を、同じIntentに対する異質なCapability候補として扱える必要がある。

このとき、Capabilityの定義、現在の状態、適合評価、選択判断、Authority、Executionを一つへまとめると、現在利用できない手段を存在しないことにしたり、Matching結果を自動実行へ昇格させたりする危険がある。

## Decision

### Capability DefinitionとObservationを分離する

Capability Definitionは「何を可能にする手段か」を表す耐久的な意味資産である。

Capability Observationは、そのCapabilityまたは提供候補について、ある時点で観察されたavailability、condition、cost、latency、auditability等を表す。

```text
Capability Definition != Capability Observation
```

現在利用不能というObservationがあってもDefinitionを削除しない。Observationがないことも「利用不能」を意味しない。

### Matchingは説明可能な適合関係でありDecisionではない

MatchingはIntent、Constraint、contextとCapabilityを照合し、なぜ候補になり得るか、何が不足・競合・未確認かを外在化する。

```text
Matching != Recommendation != Decision != Authority != Execution
```

Matching結果をそのまま採用・Authorizationへ昇格させない。

### Universal score / global rankingを持たない

異質な候補を単一numeric scoreへ正規化し、最大値を自動選択することをCore要件にしない。比較軸やdomain-specific評価はProfile / Policy / Methodで追加できる。

### Capability ChoiceはDecision境界で扱う

実際にCapabilityを採る、採らない、組み合わせる、保留する判断はDecisionとして扱う。

現時点では独立Universal `CapabilitySelection` Artifactを作らない。

一つのIntentから必ず一件だけ選ぶことも要求しない。複数Capabilityの組み合わせ、条件付き候補、選択保留、Matchingだけで終わる状態を許す。

### CapabilityとProviderを分離する

```text
Capability != Provider
```

Capabilityは「何を可能にするか」、Providerは「誰／何がそれを実現するか」である。Decision時点でCapabilityだけを選びProviderを未確定にしてもよい。

TEI、AI、人間、SaaS等のkindから優先度、信頼、Authorityを推定しない。SOZAとの関連が深いことを理由にTEIを優遇しない。

### Unknownをincompatibleへ潰さない

```text
not observed != unavailable
unknown compatibility != incompatible
```

M48のUnknown / Conflict / Observation境界を再利用する。

### 過去Choiceを当時の状態で再構成する

後からDefinitionやObservationが変わっても、過去Decisionが何を根拠に選んだかを書き換えない。必要な可変ArtifactにはExactArtifactBindingを使い、Decision revisionにはSemantic Lineageを再利用する。

### Choiceは実行権限ではない

```text
Capability Choice Decision
  != Authorization
  != Action Intent
  != Provider Execution
```

Capabilityを提供・管理・選定・監督する責任は、必要に応じて既存`ResponsibilityStatement`を使う。

## Deferred implementation choices

次は意味境界ではなく実現方式であるため、actual implementationまで固定しない。

- Capability Definitionの最終field set
- Observationのproperty model
- Matching resultのrepresentation / status vocabulary
- Decisionからchosen Capabilityを指す具体形
- candidate setの表現
- domain-specific comparison facet

Provider realization / offeringのUniversal型要否はADR-0013で別途判断した。

## Consequences

- 人間・AI・SaaS・TEI等を中立に比較しやすい。
- stale ObservationやProvider変更でCapability identityが壊れにくい。
- MatchingをPlanner authorityへ肥大化させない。
- UI / ProjectionはDefinition、Observation、Matching、Choiceを組み立てる必要がある。

## Natural Japanese review

M50 Capability Choice planning、ADR-0013、SOZA↔TEI境界へ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
