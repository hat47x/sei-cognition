# SOZA Product Vision

更新日: 2026-08-31  
状態: **Product Vision Baseline**

## 1. 目指す状態

SOZAが目指すのは、AIが高度化した世界で、組織や個人が「自動化できること」を増やすだけでなく、**何を見て、何を問い、何を根拠に、どこまでをAIや外部システムへ委ね、何を自ら判断したのか**を失わずに扱える状態です。

さらに、過去の判断を当時の状態として読み直し、新しいEvidenceやConstraintが加わったときには、過去を消さずに問い直し、別の手段を選び直せることを重視します。

実行技術が変わっても、認識・判断・責任・来歴の意味を持ち運べることが、SOZAの長期的な中心です。

## 2. Product Valueから見た長期像

SOZAの長期像は、`SOZA_PRODUCT_VALUE.md`と`SOZA_VALUE_MODEL.md`の価値階層を時間軸へ延ばしたものです。

長期的にも守る順序は、概ね次のとおりです。

1. 判断の意味、不確実性、責任線、来歴を失わない。
2. 過去を再構成し、必要なら選び直せる。
3. Providerや実行技術が変わっても意味を維持する。
4. 人間とAIの双方が理解・利用できる。
5. そのうえで、操作性、性能、自動化、実装容易性を高める。

将来像を描くために、現在の利用可能性を無視するわけではありません。現在の具体的なScenarioで価値を確かめながら、現在の制約を恒久的な製品構造へ固定しないことを目指します。

## 3. AIが強くなるほど薄くできる層と、残す層を分ける

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
具体的なValue Scenarioへ戻して確認
  ↓
技術進歩後、新しい現在地から再評価
```

## 4. 将来も残す可能性が高いもの

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
- Authorityへの参照
- Capability
- Semantic Lineage
- 過去の判断を再構成するための記憶

これらは、特定のAIモデルや実行方式が変わっても、認知・判断・責任を扱うために区別する意味が残りやすいものです。

ただし、「将来も残りそう」という予想だけでCoreへ入れません。現在の具体Scenarioで意味差が必要か、複数domainや複数Providerでも同じ境界が成立するか、Core外の表現では不足するかを確認します。

## 5. 交換可能にしていくもの

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
- 特定Providerのavailability stateやauthorization schema
- 特定domainのReference Model / Pattern

これらは、外部Provider、Profile、Policy、Extension、Projection、domain-specific Design Knowledge、交換可能なRealizationへ置くことを優先します。

## 6. 人間・AI・外部システムの関係

SOZAは、人間を形式的な承認ボタンへ縮小することも、AIを常に補助者へ固定することも目指しません。

重要なのは、案件ごとに必要な境界を明示できることです。

- AIがRecommendationを作る。
- 人間または組織がDecisionを担う。
- Policyにより一定範囲のDecisionをAIへ委任する。
- Provider側で必要なAuthorizationが評価される。
- 外部ProviderがExecutionを担う。
- 結果をObservationとしてSOZAへ戻す。
- 新しいObservationをもとに、過去Decisionを維持・修正・撤回する。

これらの組み合わせは変化してよい一方、Recommendation、Decision、Responsibility、Authority、Execution等の意味差を無自覚に潰さないことを重視します。

## 7. 問いと判断を時間の中で扱う

SOZAは、一回の問い合わせに一回答を返すだけの仕組みを長期像とはしません。

同じQuestionが後から別のEvidenceに触れ、過去のDecisionが再審査され、以前は意味を持たなかったUnknownやConflictが重要になることがあります。

そのため、次を両立させます。

- 同じ前提なら過去のDecisionを再利用し、不要な聞き直しを減らす。
- 前提が変わったなら、過去を消さずに再び問える。
- Questionの表示文と意味上のidentityを分ける。
- 新旧DecisionをSemantic Lineageとして辿れる。

これは、AIと長期に協働するほど重要になる判断記憶の性質です。

## 8. 実行基盤との関係

SOZAから見れば、Camunda等のworkflow/BPM、AI agent runtime、TEI、SaaS、人間作業、外部組織は、必要に応じて利用できるCapability Providerです。

SOZA自身が実行安定化の全領域を所有する必要はありません。むしろ、生成AIが十分に賢くなり、現在のオーケストレーターの多くが中抜きされる時代にも残る層を主に扱います。

Provider内部の詳細な状態をSOZAへ複製するのではなく、判断に必要なObservation、Unknown、Evidence、Assurance等をProvider-neutralな境界で扱い、必要な監査時だけ具体的なProvider Evidenceへ降りられる形を目指します。

## 9. TEIとの関係

鼎（TEI）は、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

SOZAは、関連製品であるという理由だけでTEIを優先しません。Intent、Constraint、Observation、Evidence等に基づいて、他のProviderと同じ判断面で比較できることを目指します。

同時に、TEI内部のApplication、Database、Release、Environment等をSOZA Coreの概念へコピーしません。必要なときはProvider adapterやexact referenceを介して接続します。

## 10. 到達したい利用体験

利用者は、SOZAを使うために巨大なontologyを最初から設計する必要がありません。

日常的な軽い作業では必要最小限の意味境界だけを使い、影響・不可逆性・不確実性・外部性などが高まる場面では、PolicyやProfileにより必要な記録を厚くできます。

表面上の操作を簡潔にしても、canonicalな意味そのものを削除しないことを重視します。

高度な案件では、複数AI、複数人、複数組織、外部Providerをまたいでも、問い・根拠・判断・責任・来歴が連続して読める状態を目指します。Selective Disclosureが必要な場合も、見えていない情報を既知として扱わず、共有可能なEvidenceと未確認範囲を分けて判断できる状態を目指します。

## 11. 価値の実証も段階的に進める

SOZAのVisionが正しいと記述しただけでは、製品価値は実証されません。

長期的には、少なくとも次を区別してEvidenceを積み上げます。

```text
Value Definition
  ↓
Design / Requirement Coverage
  ↓
Executable Conformance
  ↓
Operational Evidence
  ↓
Adoption / Outcome Evidence
```

設計が整ったこと、local testが通ったこと、productionで動いたこと、利用者の判断が実際に改善したことは、それぞれ別の主張です。

SOZAは、自らがEvidenceを超えて強い価値主張をすることで、守ろうとしている認識上の誠実さを壊さないことを目指します。

## 12. 長期像

SOZAの長期像は「最大の実行基盤」でも、「すべての判断を自動化するAI」でもありません。

**実行方法が何度入れ替わっても、主体が自分たちの認識と判断を失わず、過去を検証し、現在を問い直し、次の手段を選び直せるための、薄く耐久的な意味基盤**であることを目指します。

その価値は、`SOZA_VALUE_SCENARIOS.md`のような具体的な場面へ戻し、Requirements・Acceptance Scenario・実運用Evidenceによって段階的に検証します。

## 13. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 14. 自然な日本語ドラフト

Value ModelとValue Scenarioとの整合を確認した後、意味、強度、留保、将来像の範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
