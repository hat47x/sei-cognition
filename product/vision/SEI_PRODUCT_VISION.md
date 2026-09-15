# SEI Product Vision

更新日: 2026-09-16  
状態: **Product Vision Baseline — Brand World Discovery reflected**

## 1. この文書の役割

この文書は、SEIが長期的にどのような利用状態を実現したいかを示します。

`SEI_PRODUCT_VALUE.md`が「なぜSEIが存在するか」を、`SEI_VALUE_MODEL.md`が「何を優先して守り、どう評価するか」を定めるのに対し、Product Visionは、それらの価値が実際の利用世界でどのような姿として現れるかを記述します。

特定の型、API、画面、AIモデル、実行方式を将来像として固定する文書ではありません。

また、`SEI_BRAND_WORLD_SOURCE.md`で記録した「井」のブランド世界は、本書を考えるための探索源の一つですが、Product Visionのauthorityではありません。象徴から仕様を直接導くのではなく、利用者や組織にとって意味のある状態として説明できるものだけを本書へ反映します。

## 2. 目指す状態

SEIが目指すのは、AIが高度化した世界で、組織や個人が「自動化できること」を増やすだけでなく、**何を見て、何を問い、何を根拠に、どこまでをAIや外部システムへ委ね、何を自ら判断したのか**を失わずに扱える状態です。

実行技術が変わっても、意思決定の意味と来歴を持ち運べることを重視します。

その結果、利用者は過去の判断を単なるログとして眺めるのではなく、当時の前提へ戻り、新しいEvidenceを加え、必要であれば別の手段や判断を選び直せます。

同時に、すべての認知活動が最初からDecisionへ到達するわけではありません。

実務では、まだ何を問うべきか十分に定まっていない段階、確証のない違和感だけがある段階、複数のObservationが集まり始めているがRecommendationへ進むには早い段階があります。

SEIは、そのような途中状態をすぐに「答え」へ変えることを目指しません。Question、Observation、Unknown、Conflict、Hypothesis等として外在化できたものを、意味差と来歴を失わず扱い、後から別の人間やAIが問い直せる状態を目指します。

## 3. 判断の前から、認知の続きを失わない

current Product Valueでは、Decision Continuityを、時間・Surface・AI・情報が変わっても、過去を捏造せず判断仕事の続きを始められることとして重視しています。

このVisionでは、そのさらに手前も視野に入れます。

まだDecisionが存在しないInquiryでも、時間が空いたり、担当者やAI sessionが変わったりすると、次のものが失われることがあります。

- そもそも何が気になっていたのか。
- どのObservationが最初の問いにつながったのか。
- 何がまだ分からなかったのか。
- どのHypothesisは未検証のままだったのか。
- 何を次に確かめようとしていたのか。

SEIは、あらゆる思考断片を保存することを目指しません。private chain-of-thoughtや一時的なworking memoryを正本へ変えることもしません。

目指すのは、主体が共有・再利用する価値があると判断して外在化した認知対象について、**Decisionになる前であっても、後から文脈を失わず探索を再開できる可能性を保つこと**です。

この状態を独立したProduct Valueとみなすべきか、Decision Continuityを含むより広いCognitive Continuityとして整理すべきかは、actual Scenarioとhuman reviewを通して今後検証します。本書では、長期的な利用世界としてこの方向を明示するに留めます。

## 4. 個人や一つのAI sessionへ閉じない共有認知基盤

SEIは、一人の利用者だけのsecond brainや、一つのAI modelのmemoryとして完結することを長期像にはしません。

組織の認知活動では、問い、Observation、Decision basis、Unknown、reopen condition等が、特定の担当者や一つのAI sessionに閉じると、引継ぎや再検討のたびに大きな再構成負担が生じます。

SEIは、これらを適切なboundaryのもとで、人間とAIが後から利用できる**共有認知資産**として持続させることを目指します。

ただし、共有することと無制限に公開することは同じではありません。

Selective Disclosure、Product Access、Responsibility、Authority、Provenance等を保ち、必要な主体が必要な範囲へ到達できることを重視します。

```text
shared cognition
  != everybody sees everything
  != open to everyone
  != shared Authority
```

共有できることは、全員へ開くことでも、権限を共有することでもありません。一人の利用者や一つのAI sessionで得た認知成果が、そのsessionの寿命だけで消えず、許された別の人間やAIへ引き継げる。そのときもProvenance、historical context、Responsibility、Access boundaryを失わない。この状態を目指します。

この意味でSEIが目指すのは、中央の巨大な知識庫でも組織の「中央の頭脳」でもなく、**異なる主体がそれぞれの責任を保ったまま同じ認知資産へ近づける、境界を失わないCognitive Infrastructure**です。

## 5. AIが強くなるほど、薄くできる層と残す層を分ける

SEIは、現在の技術制約を恒久的な製品構造へ固定しません。

評価のたびに、その時点の現実からおおむね10〜50倍程度先までを見渡し、現在のAIや実行基盤が大幅に強くなってもSEIが守る必要のある意味差かを問い直します。この距離は固定倍率のbenchmarkではなく、現在の制約への過適合を避けるための移動する思考基準です。

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

将来も残すべきなのは、現在の型名そのものではありません。認識、問い、不確実性、根拠、提案、判断、責任、能力、来歴など、主体が自らの判断や探索を再構成するために必要な**意味上の区別**です。

具体的な型をUniversal Coreへ置くかどうかは、Product Visionから直接決めず、Value Model、Scenario、Requirement、ADRを通じて判断します。

## 6. 交換可能にしていくもの

次のような仕組みは、必要であってもSEIの恒久的中心にしないことを基本とします。

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

重要なのは、これらを捨てることではなく、**交換したときにSEIの判断記憶や探索文脈まで壊れないこと**です。

## 7. 到達したい五つの利用状態

### 7.1 判断が時間を越えて読める

過去のDecisionについて、当時のEvidence、Unknown、Constraint、Authority、参照Artifactを後から辿れます。

現在の知識で過去を書き換えるのではなく、「当時はなぜその判断が合理的だったのか、あるいは何が不足していたのか」を再構成できます。

### 7.2 AIへ広く委ねても責任線を失わない

SEIは、人間を形式的な承認ボタンへ縮小することも、AIを常に補助者へ固定することも目指しません。

AIへの委任範囲は広がって構いません。ただし、Recommendation、Decision、Authority、Action Intent、Execution等の意味差を、能力向上を理由に無自覚に潰しません。

### 7.3 手段を交換してもIntentとDecisionが残る

人間、AI、SaaS、外部組織、TEI、custom codeなど、Capability Providerは交換・併用できます。

Providerを変更した結果、過去のIntentやDecisionまで別の意味へ読み替えられる状態を避けます。

### 7.4 不確実なままでも安全に前へ進める

Unknown、Conflict、Hypothesisが存在するからといって、すべての判断を停止する必要はありません。

不確実性を残したまま必要なDecisionを行い、何を未解決のまま受け入れたのかを後から確認できる状態を目指します。

### 7.5 軽い利用から厳密な利用へ連続的に移れる

利用者は、SEIを使うために巨大なontologyを最初から設計する必要がありません。

日常的で低影響な作業では必要最小限の意味境界だけを扱い、影響、不可逆性、不確実性、外部性などが高まる場面では、ProfileやPolicyによって必要な記録を厚くできます。

簡略な表示や入力を採用しても、必要な場合にcanonicalな意味へ戻れることを重視します。

## 8. 静かなInfrastructureとして利用できる

SEIは、利用者のattentionを常に占有する製品を目指しません。

高度なAIが多数のRecommendation、summary、alertを生成できるようになっても、出力量やproactiveさそのものをProduct Valueにはしません。

必要なときには、問い、Unknown、Decision basis、audit detailへ深く降りられる。一方、通常時には、本来の仕事よりSEIの入力・確認・通知が前面に出ない。そのような利用状態を目指します。

ここでいう「静か」は、重要なwarningを隠すことや、next actionを示さないことではありません。

むしろ、

- 不要なrecommendation pressureを増やさない。
- semantic detailを最初からすべて要求しない。
- AI suggestionをDecisionのように押し付けない。
- 必要なreview conditionは適切に見える。
- 利用者が自分で問い直す余地を保つ。

という、認知負荷と統制可能性の両立を意味します。

一方で、安全上重要なsignalや重大な変化まで「静けさ」のために隠してはなりません。静けさを設計上の既定値にするのではなく、attention burdenとproactive assistanceの価値を場面ごとに明示的に比較します。

このProduct qualityは、V7 Progressive ExplicitnessやProduct Interactionのhuman reviewを通して具体化します。独立したValue Axisとしては扱いません。

## 9. 人間・AI・外部システムの関係

案件ごとに、主体と役割の組み合わせは変化して構いません。

たとえば、次のような組み合わせを扱えます。

- AIがRecommendationを作る。
- 人間または組織がDecisionを担う。
- Policyにより一定範囲のDecisionをAIへ委任する。
- 外部ProviderがExecutionを担う。
- 実行結果をObservationとしてSEIへ戻す。

SEIが固定したいのは役割分担そのものではなく、**その案件で実際にどの境界が採用されたかを後から読み取れること**です。

また、人間、AI、Cognitive Method、Document、外部Systemは、SEIを利用する主体・入力源・Providerになり得ますが、そのいずれか一つをSEIそのものと同一視しません。

SEIはcentral AI brainではなく、それらが意味を失わず出会い、後から読み直せる共有基盤を目指します。

## 10. 実行基盤との関係

SEIから見れば、Camunda等のworkflow/BPM、AI agent runtime、TEI、SaaS、人間作業、外部組織は、必要に応じて利用できるCapability Providerです。

SEI自身が実行安定化の全領域を所有する必要はありません。生成AIが十分に賢くなり、現在のオーケストレーターの多くが不要になった場合でも残る認知・判断の意味構造を主に扱います。

## 11. TEI・SUIとの関係

鼎（TEI）は、SEIから利用し得るCapability Providerの一つです。萃（SUI Sensemaking）は、認知素材を集め、関係や構造を立ち上げる隣接Product / Method familyとして接続し得ます。

```text
SEI = 何を見るか、何を問うか、何を残すか、何を判断するか
SUI = 集めた素材から関係・まとまり・emergenceを扱う一つの手段
TEI = 実行可能な業務Capabilityを実現する一つの手段
```

SEIは、関連製品であるという理由だけでTEIやSUIを優先しません。Intent、Constraint、Observation、Evidence等に基づき、他のMethod / Providerと同じ判断面で扱えることを目指します。

この関係を固定pipelineにはしません。SEIはSUI / TEIを使わなくても成立し、SUI / TEIもSEI専用Providerとして特権化しません。象徴的な親和性は、必須依存やProvider優先の根拠にはしません。

また、SUI / TEIの内部構造をSEI Universal Coreへコピーせず、必要なCognitive Method、Capability、Observation、Evidence、Artifact referenceを明示的な境界から読み取ります。

## 12. SEIが目指さない将来像

SEIは、次の状態を長期目標にはしません。

- すべての業務をSEI内部で実行する巨大な統合基盤
- あらゆる判断を単一スコアで自動決定するシステム
- AIの内部推論を全量保存する監視基盤
- 特定AIモデルや特定Providerを中心に世界を表現する基盤
- 利用者に最初から完全なontology入力を要求するシステム
- 過去の判断を最新状態へ常に上書きする「現在だけ」の記録基盤
- すべての認知断片を保存し続けるlife-log基盤
- 共有を理由にprivacy、Selective Disclosure、Responsibilityを弱める情報集約基盤
- まだ未確定な認知材料を、AIによって常に一つの結論へ収束させる基盤
- AI suggestionやnotificationを大量に提示すること自体を価値とするattention-consumingなProduct

## 13. 長期像

SEIの長期像は「最大の実行基盤」でも「最も賢い中央AI」でもありません。

**実行方法やAIが何度入れ替わっても、主体が自分たちの認識、問い、不確実性、判断を失わず、過去を検証し、現在を問い直し、次の手段を選び直せるための、薄く耐久的な共有認知基盤**であることを目指します。

その基盤では、すでにDecisionになったものだけでなく、外在化されたQuestion、Observation、Unknown等も、必要な範囲で時間や主体を越えて読み直せます。

ここで「薄い」は「浅い」を意味しません。

```text
thin infrastructure
  != shallow cognition
```

薄く交換可能に保つべきなのは、Provider固有実装、現在のAI都合、不要なUniversal ontologyです。その上で利用者が扱えるInquiry、historical context、uncertainty、共有可能性は深くなり得ます。SEIは答えを置く中心ではなく、問いと認知状態へ繰り返し戻れる入口として働きます。

同時に、すべてを一か所へ集めたり、すべてを全員へ見せたり、すべてを永続化したりすることは目指しません。意味を持続させることと、境界を保つことを両立させます。

この長期像が実現しているかは、`SEI_VALUE_MODEL.md`のV1〜V8を用いて、単一スコアではなく複数の観点から継続的に検証します。

Decision以前のInquiry Continuityについては、現時点では独立したValue Axisを追加せず、Product hypothesisとしてactual Scenarioとhuman reviewから必要性を確かめます。

## 14. 関連文書

- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_MODEL.md`
- `product/value/SEI_DECISION_CONTINUITY.md`
- `product/value/SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md`
- `product/vision/SEI_BRAND_WORLD_SOURCE.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `plan/issue/ISSUE-000077-integrate-brand-world-into-product-value-discovery.md`
- `plan/adr/ADR-0001-moving-future-horizon.md`
- `plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 15. 自然な日本語ドラフト

Brand World SourceとProduct Value Discovery Reviewを通じて、ブランド上の比喩とProduct Visionへ反映すべき利用状態を分離しました。

その結果、井戸、水、中央の空白といった象徴語そのものを本書の規範へ持ち込むのではなく、判断前のInquiryを失わないこと、個人や一AI sessionへ閉じない共有認知基盤であること、共有とSelective Disclosureを両立すること、人間・AI・Methodが利用するInfrastructureであること、過剰なattentionを要求しないことを将来像として反映しました。

V1〜V8やDecision Continuityの意味を変えず、Inquiry Continuityについては未検証Product hypothesisのまま残しています。

内容と構造を整えた後、意味、強度、留保、技術的境界を変えず、**自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とします。
