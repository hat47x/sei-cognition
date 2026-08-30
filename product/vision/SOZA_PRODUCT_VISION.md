# SOZA Product Vision

更新日: 2026-08-31  
状態: **Product Vision Baseline**

## 1. この文書の役割

この文書は、SOZAが長期的にどのような利用状態を実現したいかを示します。

`SOZA_PRODUCT_VALUE.md`が「なぜSOZAが存在するか」を、`SOZA_VALUE_MODEL.md`が「何を優先して守り、どう評価するか」を定めるのに対し、Product Visionは、それらの価値が実際の利用世界でどのような姿として現れるかを記述します。

特定の型、API、画面、AIモデル、実行方式を将来像として固定する文書ではありません。

## 2. 目指す状態

SOZAが目指すのは、AIが高度化した世界で、組織や個人が「自動化できること」を増やすだけでなく、**何を見て、何を問い、何を根拠に、どこまでをAIや外部システムへ委ね、何を自ら判断したのか**を失わずに扱える状態です。

実行技術が変わっても、意思決定の意味と来歴を持ち運べることを重視します。

その結果、利用者は過去の判断を単なるログとして眺めるのではなく、当時の前提へ戻り、新しいEvidenceを加え、必要であれば別の手段や判断を選び直せます。

## 3. AIが強くなるほど、薄くできる層と残す層を分ける

SOZAは、現在の技術制約を恒久的な製品構造へ固定しません。

評価のたびに、その時点の現実からおおむね10〜50倍程度先までを見渡し、現在のAIや実行基盤が大幅に強くなってもSOZAが守る必要のある意味差かを問い直します。この距離は固定倍率のbenchmarkではなく、現在の制約への過適合を避けるための移動する思考基準です。

```text
その時点の現実
  ↓
現在の技術・実務を確認する
  ↓
10〜50倍程度先まで展望する
  ↓
それでも失ってはいけない意味差を確認する
  ↓
Core / Profile / Provider / Realization等へ配置する
  ↓
技術進歩後、新しい現在地から再評価する
```

将来も残すべきなのは、現在の型名そのものではありません。認識、問い、不確実性、根拠、提案、判断、責任、能力、来歴など、主体が自らの判断を再構成するために必要な**意味上の区別**です。

具体的な型をUniversal Coreへ置くかどうかは、Product Visionから直接決めず、Value Model、Scenario、Requirement、ADRを通じて判断します。

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

重要なのは、これらを捨てることではなく、**交換したときにSOZAの判断記憶まで壊れないこと**です。

## 5. 到達したい五つの利用状態

### 5.1 判断が時間を越えて読める

過去のDecisionについて、当時のEvidence、Unknown、Constraint、Authority、参照Artifactを後から辿れます。

現在の知識で過去を書き換えるのではなく、「当時はなぜその判断が合理的だったのか、あるいは何が不足していたのか」を再構成できます。

### 5.2 AIへ広く委ねても責任線を失わない

SOZAは、人間を形式的な承認ボタンへ縮小することも、AIを常に補助者へ固定することも目指しません。

AIへの委任範囲は広がって構いません。ただし、Recommendation、Decision、Authority、Action Intent、Execution等の意味差を、能力向上を理由に無自覚に潰しません。

### 5.3 手段を交換してもIntentとDecisionが残る

人間、AI、SaaS、外部組織、TEI、custom codeなど、Capability Providerは交換・併用できます。

Providerを変更した結果、過去のIntentやDecisionまで別の意味へ読み替えられる状態を避けます。

### 5.4 不確実なままでも安全に前へ進める

Unknown、Conflict、Hypothesisが存在するからといって、すべての判断を停止する必要はありません。

不確実性を残したまま必要なDecisionを行い、何を未解決のまま受け入れたのかを後から確認できる状態を目指します。

### 5.5 軽い利用から厳密な利用へ連続的に移れる

利用者は、SOZAを使うために巨大なontologyを最初から設計する必要がありません。

日常的で低影響な作業では必要最小限の意味境界だけを扱い、影響、不可逆性、不確実性、外部性などが高まる場面では、ProfileやPolicyによって必要な記録を厚くできます。

簡略な表示や入力を採用しても、必要な場合にcanonicalな意味へ戻れることを重視します。

## 6. 人間・AI・外部システムの関係

案件ごとに、主体と役割の組み合わせは変化して構いません。

たとえば、次のような組み合わせを扱えます。

- AIがRecommendationを作る。
- 人間または組織がDecisionを担う。
- Policyにより一定範囲のDecisionをAIへ委任する。
- 外部ProviderがExecutionを担う。
- 実行結果をObservationとしてSOZAへ戻す。

SOZAが固定したいのは役割分担そのものではなく、**その案件で実際にどの境界が採用されたかを後から読み取れること**です。

## 7. 実行基盤との関係

SOZAから見れば、Camunda等のworkflow/BPM、AI agent runtime、TEI、SaaS、人間作業、外部組織は、必要に応じて利用できるCapability Providerです。

SOZA自身が実行安定化の全領域を所有する必要はありません。生成AIが十分に賢くなり、現在のオーケストレーターの多くが不要になった場合でも残る認知・判断の意味構造を主に扱います。

## 8. TEIとの関係

鼎（TEI）は、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

SOZAは、関連製品であるという理由だけでTEIを優先しません。Intent、Constraint、Observation、Evidence等に基づき、他のProviderと同じ判断面で扱えることを目指します。

また、TEIの内部構造をSOZA Universal Coreへコピーせず、必要なCapability、Observation、Evidence、Artifact referenceを明示的な境界から読み取ります。

## 9. SOZAが目指さない将来像

SOZAは、次の状態を長期目標にはしません。

- すべての業務をSOZA内部で実行する巨大な統合基盤
- あらゆる判断を単一スコアで自動決定するシステム
- AIの内部推論を全量保存する監視基盤
- 特定AIモデルや特定Providerを中心に世界を表現する基盤
- 利用者に最初から完全なontology入力を要求するシステム
- 過去の判断を最新状態へ常に上書きする「現在だけ」の記録基盤

## 10. 長期像

SOZAの長期像は「最大の実行基盤」ではありません。

**実行方法が何度入れ替わっても、主体が自分たちの認識と判断を失わず、過去を検証し、現在を問い直し、次の手段を選び直せるための、薄く耐久的な意味基盤**であることを目指します。

この長期像が実現しているかは、`SOZA_VALUE_MODEL.md`のV1〜V8を用いて、単一スコアではなく複数の観点から継続的に検証します。

## 11. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `plan/adr/ADR-0001-moving-future-horizon.md`
- `plan/adr/ADR-0014-soza-tei-product-boundary.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 12. 自然な日本語ドラフト

Value Modelとの意味整合を確認し、将来像と具体的な型候補が混在しないよう構造を整理した後、意味、強度、留保、技術的境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
