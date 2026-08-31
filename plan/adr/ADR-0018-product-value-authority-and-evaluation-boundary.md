# ADR-0018: Product Valueの権威関係と評価境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000023**  
Updated: 2026-08-31

## Context

SOZAでは、Product ValueをRequirements、ADR、Architecture、Implementationより上位に置いている。

一方、設計が具体化するにつれて、性能、操作性、Provider統合、実装容易性などの局所最適が、判断の意味、不確実性、責任、来歴といった上位価値と衝突する可能性がある。

また、Product Valueを抽象的な理念のままにすると、下位設計が実際に価値を満たしているかを検証しにくい。さらに、設計・fixture・本番動作が確認できても、それだけで利用者や組織に価値が届いたとは限らない。

そこで、Product Valueの権威関係と、下位設計から実運用・Outcomeまでを評価するときの境界を明示する。

## Decision

### 1. Product Valueを下位設計の正当化基準とする

概念上の依存方向は、次を原則とする。

```text
Product Value
  → Value Model / Value Acceptance
  → Vision / Principles
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Contract
  → Implementation / Test / Evidence
```

ImplementationやArchitectureから得た反証によって上位仮説を見直すことはできる。ただし、既存実装を維持するためだけにProduct Valueを後付けで変更しない。

### 2. 価値衝突時は意味保存を先に守る

設計上の価値が衝突する場合、原則として次の順に優先する。

1. 判断の意味、不確実性、責任線、来歴を失わないこと。
2. 過去を再構成し、後から選び直せること。
3. 特定Providerや実行方式から意味を独立させること。
4. 人間とAIの双方が扱えること。
5. 操作性、性能、自動化率、実装容易性を最適化すること。

下位価値を犠牲にすること自体を目的としない。上位価値を破壊しない範囲で、下位価値を最大化する。

### 3. Product Valueの充足はV1〜V8を必要な範囲で個別に確認する

少なくとも次の観点を使う。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

単一の総合点やUniversal Scoreへ還元しない。一つの軸で高い成果が得られても、別の重大な欠損を相殺したことにはしない。

### 4. Evidenceの高さを分離する

Product Valueに関する主張では、少なくとも次を分ける。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

- **Design Evidence**は、意味境界や受入れ条件が設計として定義されていることを示す。
- **Executable Evidence**は、actual repository上のfixture、test、validator等で対象範囲を再現可能に確認したことを示す。
- **Release Evidence**は、実際に配布されたArtifactについて同じ性質を確認したことを示す。
- **Operational Evidence**は、実運用環境で期待した性質が成立していることを示す。
- **Adoption / Outcome Evidence**は、その性質が実際の判断、再検討、説明、移行、業務成果等へ意図した価値をもたらしたことを示す。

下位Evidenceだけで上位Evidenceを満たしたことにはしない。

### 5. 実行成功・運用成功を価値実現の代替証拠にしない

次はそれぞれ別の事実として扱う。

```text
Execution Success != Decision Validity
Method Application != Assurance
Recommendation != Decision
Provider Availability != Capability Semantics
Operational Success != Adoption / Outcome
```

実行が成功していても、判断の根拠や責任線が失われていればProduct Value上は失敗し得る。

また、SOZAが本番で安定して動作していても、利用者が必要な情報を実際に読み直せない、再判断に活用できない、記録負担が大きく利用されない、といった状態であればProduct Valueが十分に届いたとは言えない。

Outcomeは単一KPIへ固定しない。対象Scenarioに応じて、質的Evidence、具体事例、再判断結果、説明可能性、移行可能性、誤判断の回避等を組み合わせて評価できる。

### 6. Coreへの昇格はProduct Valueへの必要性で判断する

概念や型をSOZA Universal Coreへ追加する場合、少なくとも次を確認する。

- Providerが変わっても意味が残るか。
- 複数domainで同じ意味境界を持つか。
- 判断・責任・不確実性・来歴の再構成に必要か。
- Extension、Reference、Capability Provider、domain-specific knowledgeでは不足するか。

TEIとの関係が深いこと、現在の実装で便利であること、AIが扱いやすいことだけではCoreへの昇格理由としない。

### 7. Product Value変更は明示的な再基線化として扱う

Product ValueまたはValue Modelの意味を変更する場合は、通常の下位設計変更として処理しない。

少なくとも次を必要とする。

- 変更理由と反証Evidence
- 影響するRequirements / ADR / Architecture / Contractの特定
- 過去の判断との互換性または非互換性の説明
- Revisit条件
- 自然な日本語による全文再ドラフトと最終意味監査

Value AcceptanceのEvidence区分を精緻化する場合も、V1〜V8そのものの意味を変更していないかを確認する。評価方法の追加を、暗黙のProduct Value変更にしない。

### 8. Product Valueから下位Evidenceまで追跡可能にする

重要な価値境界について、少なくとも次を辿れるようにする。

```text
V1〜V8
  → REQ
  → SCN
  → ADR
  → Architecture concern
  → Contract / Implementation / Fixture
  → current Evidence state
```

この追跡は一対一対応を要求しない。また、coverage表を完成率やProduct Value scoreとして扱わない。

Product側の現行索引は`product/value/SOZA_VALUE_TRACEABILITY.md`を用いる。

## Consequences

### Positive

- 下位設計がProduct Valueに対して何を守るべきか明確になる。
- 性能や実装容易性を理由に意味境界が黙って削られることを防ぎやすい。
- Design文書やfixtureの存在だけでProduct Valueを実証済みと誤認しにくくなる。
- 本番稼働と実際の利用者価値を分けて検証できる。
- SOZA Universal Coreの膨張を抑えられる。
- TEIや将来のProviderと密接に連携しても、SOZAの製品境界を保ちやすい。
- Acceptance ScenarioやTestをProduct Valueへ遡って設計しやすくなる。

### Costs

- Evidenceを複数の高さに分けて管理する必要がある。
- 一部の実装ではcanonicalな意味保持と簡略UIを分ける必要がある。
- 性能上の制約がある場合、単純な省略ではなく明示的なtrade-off記録が必要になる。
- Adoption / Outcomeは対象Scenarioごとに異なるため、単一の自動判定へ還元しにくい。
- Product Value変更の手続きは、通常の実装変更より重くなる。

## Revisit conditions

次の場合に再検討する。

- 複数の実運用で、現在の価値優先規則が重大な運用不能を繰り返し生む。
- Product Value検証軸では重要な失敗を継続的に捕捉できない。
- Evidenceの5段階区分では、実際の価値検証上重要な差を反復して表現できない。
- 現在Universal Core外としている概念が、複数domain・複数Providerで同一の不可欠な意味境界を持つことが実証される。

## Evidence

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- ADR-0001: Moving Future Horizon
- ADR-0012 / ADR-0013: Capability / Provider境界
- ADR-0014: SOZA / TEI Product境界
- ADR-0017: Reference Model / Cognitive Method境界
- ADR-0020: Requirements traceability / Evidence境界
- ADR-0021: Architecture / Contract権威境界

## Natural Japanese review

Product Value、Value Model、Value Acceptance、current Requirements / Architecture / ContractのEvidence状態を照合し、V1〜V8の意味を変えずに評価境界をDesign / Executable / Release / Operational / Adoption・Outcomeまで精緻化した。その後、判断内容、技術的境界、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
