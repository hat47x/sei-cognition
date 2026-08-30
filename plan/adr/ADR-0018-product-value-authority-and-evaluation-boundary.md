# ADR-0018: Product Valueの権威関係と評価境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000023**  
Updated: 2026-08-31

## Context

SOZAでは、Product ValueをRequirements、ADR、Architecture、Implementationより上位に置いている。

一方、設計が具体化するにつれて、性能、操作性、Provider統合、実装容易性などの局所最適が、判断の意味、不確実性、責任、来歴といった上位価値と衝突する可能性がある。

また、Product Valueを抽象的な理念のままにすると、下位設計が実際に価値と整合しているかを検証しにくい。逆に、設計文書やlocal testが整っただけで「Product Valueを実証した」と扱うと、SOZA自身がEvidenceを超えた主張を行うことになる。

そこで、Product Valueの権威関係、具体Scenarioへの展開、Evidence level、変更手続きを明示する。

## Decision

### 1. Product Valueを下位設計の正当化基準とする

概念上の依存方向は、次を原則とする。

```text
Product Value
  → Value Model
  → Vision / Principles
  → Value Scenarios
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Implementation / Evidence
```

ImplementationやArchitectureから得た反証によって上位仮説を見直すことはできる。ただし、既存実装を維持するためだけにProduct Valueを後付けで変更しない。

### 2. 価値衝突時は意味保存を先に守る

設計上の価値が衝突する場合、原則として次の順に優先する。

1. 判断の意味、不確実性、責任線、来歴を失わないこと。
2. 過去を再構成し、後から選び直せること。
3. 特定Providerや実行方式から意味を独立させること。
4. 人間とAIの双方が理解・利用できること。
5. 操作性、性能、自動化率、実装容易性を最適化すること。

下位価値を犠牲にすること自体を目的としない。上位価値を破壊しない範囲で、下位価値を最大化する。

上位価値を完全には満たせない制約がある場合は、何を失うか、なぜ必要か、どの範囲へ影響するか、どの条件で再検討するかをADRへ明示する。

### 3. Product Valueの充足は複数の検証軸で判断する

少なくとも次の観点を使う。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence
- V9 Evidence Calibration

単一の総合点やUniversal Scoreへ還元しない。

V9では、設計上の整合、local fixture、actual repository conformance、production operation、adoption / outcome evidenceを区別する。

### 4. Product Valueを代表Scenarioへ戻して確認する

抽象的な原則だけで重要な設計を正当化しない。

`product/value/SOZA_VALUE_SCENARIOS.md`は、Product Valueが具体的な判断場面でどの意味差として現れるかを確認する橋渡しとして扱う。

Value ScenarioはRequirementやAcceptance Scenarioそのものではない。各Scenarioから、複数場面に共通する耐久的な意味をRequirementsへ抽出し、設計上の選択が必要な箇所をIssue / ADRへ渡す。

Core境界、高影響なDecision、Provider境界、Evidence claimを変更する場合は、既存Value Scenarioまたは同等の具体Scenarioへ戻して意味差を確認する。

### 5. 価値定義と価値実証を分離する

少なくとも次を別のEvidence levelとして扱う。

```text
Value Definition
  != Design / Requirement Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

上位文書が整ったことはDesign Coverageの入口であって、実装やproduction利用の証拠ではない。

local testのPASSをactual repositoryでのPASSへ、actual repository conformanceをoperational evidenceへ、production operationを利用者価値へ自動昇格させない。

各claimは、その時点で確認できるEvidence levelを明示する。

### 6. 実行成功を価値充足の代替証拠にしない

次はそれぞれ別の事実として扱う。

```text
Execution Success != Decision Validity
Method Application != Assurance
Recommendation != Decision
Provider Availability != Capability Semantics
```

実行が成功していても、判断の根拠や責任線が失われていればProduct Value上は失敗し得る。

### 7. Coreへの昇格はProduct Valueへの必要性で判断する

概念や型をSOZA Universal Coreへ追加する場合、少なくとも次を確認する。

- Providerが変わっても意味が残るか。
- 複数domainで同じ意味境界を持つか。
- 判断・責任・不確実性・来歴の再構成に必要か。
- Profile / Policy、Extension、Reference、Capability Provider、provider adapter、domain-specific knowledge、Cognitive Methodでは不足するか。

TEIとの関係が深いこと、現在の実装で便利であること、AIが扱いやすいことだけではCoreへの昇格理由としない。

### 8. Product Value変更は明示的な再基線化として扱う

Product ValueまたはValue Modelの意味を変更する場合は、通常の下位設計変更として処理しない。

少なくとも次を必要とする。

- 変更理由と反証Evidence
- 影響するValue Scenario / Requirements / ADR / Architectureの特定
- 過去の判断との互換性または非互換性の説明
- 新しいEvidence levelで何が確認され、何が未確認か
- Revisit条件
- 自然な日本語による全文再ドラフトと最終意味監査

Value Scenarioの追加だけでProduct Valueの意味が変わらない場合は、Product Value再基線化を必須としない。ただし、新しいScenarioによって既存価値の欠落が判明した場合は上位文書へ戻る。

## Alternatives considered

### A. Product Valueを抽象理念としてだけ保持する

採用しない。下位設計へ適用する基準と、価値を満たしたと主張する境界が曖昧になる。

### B. 単一のProduct Value Scoreを作る

採用しない。意味保存と性能、Provider Independenceと操作性など、性質の異なる価値を一つの数字へ潰すと、重大な失敗を平均値で隠す可能性がある。

### C. Requirements以下を実質的なProduct Value正本とする

採用しない。実装や局所要件の都合で、上位価値が静かに書き換わる危険がある。

### D. test PASSをProduct Value充足の主要指標とする

採用しない。testが検査できるのは定義された条件であり、operational behaviorやadoption / outcomeまで自動的には証明しない。

## Consequences

### Positive

- 下位設計がProduct Valueに対して何を守るべきか明確になる。
- 性能や実装容易性を理由に意味境界が黙って削られることを防ぎやすい。
- SOZA Universal Coreの膨張を抑えられる。
- TEIや将来のProviderと密接に連携しても、SOZAの製品境界を保ちやすい。
- Value Scenarioを介して、RequirementsとAcceptance Scenarioの漏れを検査しやすくなる。
- 設計・実装・運用・利用者価値のEvidence levelを誤って昇格させにくくなる。

### Costs / Risks

- 一部の実装ではcanonicalな意味保持と簡略UIを分ける必要がある。
- 性能上の制約がある場合、単純な省略ではなく明示的なtrade-off記録が必要になる。
- Product Value変更の手続きは、通常の実装変更より重くなる。
- Value ScenarioとRequirementsの対応を保守する作業が増える。
- Evidence levelを厳密に区別するため、進捗表現が保守的に見える場合がある。

## Revisit conditions

次の場合に再検討する。

- 複数の実運用で、現在の価値優先規則が重大な運用不能を繰り返し生む。
- Product Value検証軸では重要な失敗を継続的に捕捉できない。
- Value ScenarioからRequirementsへ安定して展開できず、別の中間表現が必要になる。
- 現在Universal Core外としている概念が、複数domain・複数Providerで同一の不可欠な意味境界を持つことが実証される。
- Evidence levelの区分が、実運用上の重要な中間状態を表現できないことが繰り返し確認される。

## Evidence

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- ADR-0001: moving future horizon
- ADR-0012 / ADR-0013: Capability / Provider境界
- ADR-0014: SOZA / TEI Product境界
- ADR-0017: Reference Model / Cognitive Method境界
- ISSUE-000023: Product Value governance formalization

## Natural Japanese review

Value ModelとValue Scenarioを含む上位文書との整合を確定した後、判断内容、技術的境界、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
