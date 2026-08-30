# SOZA Product Vision

更新日: 2026-08-31  
状態: **Product Vision Baseline**

## 1. 目指す状態

SOZAが目指すのは、AIが高度化した世界で、組織や個人が「自動化できること」を増やすだけでなく、**何を見て、何を問い、何を根拠に、どこまでをAIや外部システムへ委ね、何を自ら判断したのか**を失わずに扱える状態です。

実行技術が変わっても、意思決定の意味と来歴を持ち運べることを重視します。

## 2. AIが強くなるほど薄くできる層と、残す層を分ける

SOZAは、現在の技術制約を恒久的な製品構造へ固定しません。

評価のたびに、その時点の現実からおおむね10〜50倍程度先までを見渡し、現在のAIや実行基盤が大幅に強くなってもSOZAが所有すべき意味差かを問い直します。この距離は固定倍率のbenchmarkではなく、現在制約への過適合を避けるための移動する思考基準です。

```text
その時点の現実
  ↓
現在の技術・実務を確認
  ↓
10〜50倍程度先まで展望
  ↓
それでも失ってはいけない意味差を確認
  ↓
Core / Profile / Provider / Realizationへ配置
  ↓
技術進歩後、新しい現在地から再評価
```

## 3. 将来も残す可能性が高いもの

SOZAの恒久的中心として有力なのは、たとえば次の意味です。

- Goal
- Intent
- Constraint
- Question
- Observation
- Unknown
- Conflict
- Hypothesis
- Evidence / EvidenceUse
- Provenance
- Cognitive Method
- Recommendation
- Decision
- Rationale
- Responsibility
- Capability
- Semantic Lineage
- 過去の判断を再構成するための記憶

これらは、特定のAIモデルや実行方式が変わっても、認知・判断・責任を扱うために区別する意味が残りやすいものです。

ただし、「将来も残りそう」という予想だけでCoreへ入れません。現在の具体的な利用価値とScenarioによっても必要性を確認します。

## 4. 交換可能にしていくもの

次のような仕組みは、必要であってもSOZAの恒久的中心にしないことを基本とします。

- workflow DAG
- queue
- retry / backoff
- worker scheduling
- agent turn routing
- checkpointの実装方式
- provider SDK固有処理
- prompt固有のrouting
- 特定モデル固有の補助構造
- 特定DBやevent sourcing方式

これらは、外部Provider、Profile、Projection、交換可能なRealizationへ置くことを優先します。

## 5. 人間・AI・外部システムの関係

SOZAは、人間を形式的な承認ボタンへ縮小することも、AIを常に補助者へ固定することも目指しません。

重要なのは、案件ごとに必要な境界を明示できることです。

- AIがRecommendationを作る。
- 人間または組織がDecisionを担う。
- Policyにより一定範囲のDecisionをAIへ委任する。
- 外部ProviderがExecutionを担う。
- 結果をObservationとしてSOZAへ戻す。

これらの組み合わせは変化してよい一方、Recommendation、Decision、Authority、Execution等の意味差を無自覚に潰さないことを重視します。

## 6. 実行基盤との関係

SOZAから見れば、Camunda等のworkflow/BPM、AI agent runtime、TEI、SaaS、人間作業、外部組織は、必要に応じて利用できるCapability Providerです。

SOZA自身が実行安定化の全領域を所有する必要はありません。むしろ、生成AIが十分に賢くなり、現在のオーケストレーターの多くが中抜きされる時代にも残る層を主に扱います。

## 7. TEIとの関係

鼎（TEI）は、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

SOZAは、関連製品であるという理由だけでTEIを優先しません。Intent、Constraint、Observation、Evidence等に基づいて、他のProviderと同じ判断面で扱えることを目指します。

## 8. 到達したい利用体験

利用者は、SOZAを使うために巨大なontologyを最初から設計する必要がありません。

日常的な軽い作業では必要最小限の意味境界だけを使い、影響・不可逆性・不確実性・外部性などが高まる場面では、PolicyやProfileにより必要な記録を厚くできます。

一方、高度な案件では、複数AI、複数人、複数組織、外部Providerをまたいでも、問い・根拠・判断・責任・来歴が連続して読める状態を目指します。

## 9. 長期像

SOZAの長期像は「最大の実行基盤」ではありません。

**実行方法が何度入れ替わっても、主体が自分たちの認識と判断を失わず、過去を検証し、現在を問い直し、次の手段を選び直せるための薄く耐久的な意味基盤**であることを目指します。
