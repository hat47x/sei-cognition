# SEI Product Vision

更新日: 2026-09-14  
状態: **Product Vision Baseline — shared cognitive aperture / quiet infrastructure reflected**

## 1. この文書の役割

この文書は、SEIが長期的にどのような利用状態を実現したいかを示します。

`SEI_PRODUCT_VALUE.md`が「なぜSEIが存在するか」を、`SEI_VALUE_MODEL.md`が「何を優先して守り、どう評価するか」を定めるのに対し、Product Visionは、それらの価値が実際の利用世界でどのような姿として現れるかを記述します。

特定の型、API、画面、AIモデル、実行方式を将来像として固定する文書ではありません。

## 2. 目指す状態

SEIが目指すのは、AIが高度化した世界で、組織や個人が「自動化できること」を増やすだけでなく、**何を見て、何を問い、何を根拠に、どこまでをAIや外部システムへ委ね、何を自ら判断したのか**を失わずに扱える状態です。

実行技術が変わっても、意思決定の意味と来歴を持ち運べることを重視します。

その結果、利用者は過去の判断を単なるログとして眺めるのではなく、当時の前提へ戻り、新しいEvidenceを加え、必要であれば別の手段や判断を選び直せます。

さらにSEIを、完成済みKnowledgeやDecisionだけを置く場所にはしません。まだ言葉になりきらないObservation、問い、違和感、Hypothesis候補を、早まってTruthへ変えず、後から別の人間やAIが問い直せる**耐久的な認知の入口**として利用できる状態を目指します。

この入口は中央集権的な「AI脳」ではありません。人間、AI、Cognitive Method、Document、System等がそれぞれのResponsibilityとAccess boundaryを保ちながら近づける共有基盤です。

## 3. AIが強くなるほど、薄くできる層と残す層を分ける

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

将来も残すべきなのは、現在の型名そのものではありません。認識、問い、不確実性、根拠、提案、判断、責任、能力、来歴など、主体が自らの判断を再構成するために必要な**意味上の区別**です。

具体的な型をUniversal Coreへ置くかどうかは、Product Visionから直接決めず、Value Model、Scenario、Requirement、ADRを通じて判断します。

ここで「薄い」は「浅い」を意味しません。

```text
thin infrastructure
  != shallow cognition
```

Provider固有実装や現在のAI都合は薄く交換可能に保ちながら、その上で利用者が扱えるInquiry、historical context、uncertainty、shared cognitionは深くなり得ます。

## 4. 交換可能にしていくもの

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

重要なのは、これらを捨てることではなく、**交換したときにSEIの判断記憶や問いの継続性まで壊れないこと**です。

## 5. 到達したい八つの利用状態

### 5.1 判断が時間を越えて読める

過去のDecisionについて、当時のEvidence、Unknown、Constraint、Authority、参照Artifactを後から辿れます。

現在の知識で過去を書き換えるのではなく、「当時はなぜその判断が合理的だったのか、あるいは何が不足していたのか」を再構成できます。

### 5.2 AIへ広く委ねても責任線を失わない

SEIは、人間を形式的な承認ボタンへ縮小することも、AIを常に補助者へ固定することも目指しません。

AIへの委任範囲は広がって構いません。ただし、Recommendation、Decision、Authority、Action Intent、Execution等の意味差を、能力向上を理由に無自覚に潰しません。

### 5.3 手段を交換してもIntentとDecisionが残る

人間、AI、SaaS、外部組織、TEI、custom codeなど、Capability Providerは交換・併用できます。

Providerを変更した結果、過去のIntentやDecisionまで別の意味へ読み替えられる状態を避けます。

### 5.4 不確実なままでも安全に前へ進める

Unknown、Conflict、Hypothesisが存在するからといって、すべての判断を停止する必要はありません。

不確実性を残したまま必要なDecisionを行い、何を未解決のまま受け入れたのかを後から確認できる状態を目指します。

### 5.5 軽い利用から厳密な利用へ連続的に移れる

利用者は、SEIを使うために巨大なontologyを最初から設計する必要がありません。

日常的で低影響な作業では必要最小限の意味境界だけを扱い、影響、不可逆性、不確実性、外部性などが高まる場面では、ProfileやPolicyによって必要な記録を厚くできます。

簡略な表示や入力を採用しても、必要な場合にcanonicalな意味へ戻れることを重視します。

### 5.6 問いが形になる前から使える

利用者が最初に持っているものは、明確なQuestionやEvidenceではなく、「何かが違う」という弱いsignalや、まだ比較軸を言えない違和感である場合があります。

SEIは、その状態をすぐに整った結論へ変えるのではなく、Observation、Inquiry、Hypothesis、Unknown等の適切な意味へ徐々に外在化し、後から問い直せる状態を目指します。

「深いところに答えがある」と仮定するのではなく、**まだ形を得ていないものへ、安全に近づける入口を保つ**ことを重視します。

### 5.7 認知成果をboundedに共有できる

一人の利用者や一つのAI sessionで得た認知成果が、そのsessionの寿命だけで消えず、許された別の人間やAIへ引き継げます。

共有時にもProvenance、historical context、Responsibility、Access boundaryを失いません。

```text
shared cognition
  != open to everyone
  != shared Authority
```

SEIを組織の「中央の頭脳」にするのではなく、異なる主体がそれぞれの責任を保ったまま同じ認知資産へ近づける基盤を目指します。

### 5.8 必要以上に認知帯域を奪わない

AIが大量のsuggestionを生成できること、常時notificationできること、あらゆるdetailを表示できることを、そのまま良いProduct Experienceとはみなしません。

通常時には利用者が本来の問いや仕事へ集中でき、必要なときにはbasis、Conflict、reopen condition、materialな変化へ深く降りられる状態を目指します。

一方で、安全上重要なsignalや重大な変化まで「静けさ」のために隠してはなりません。proactive assistanceの価値とattention burdenを明示的に比較します。

## 6. 人間・AI・外部システムの関係

案件ごとに、主体と役割の組み合わせは変化して構いません。

たとえば、次のような組み合わせを扱えます。

- AIがRecommendationを作る。
- 人間または組織がDecisionを担う。
- Policyにより一定範囲のDecisionをAIへ委任する。
- 外部ProviderがExecutionを担う。
- 実行結果をObservationとしてSEIへ戻す。
- 一人が残したInquiryを、別の人間やAIが許可された範囲で引き継ぐ。

SEIが固定したいのは役割分担そのものではなく、**その案件で実際にどの境界が採用されたかを後から読み取れること**です。

人間、AI、Method、Systemのどれか一つをSEIそのものと同一視しません。SEIは、異質な主体が同じcanonical meaningへ接続するための基盤です。

## 7. 実行基盤との関係

SEIから見れば、Camunda等のworkflow/BPM、AI agent runtime、TEI、SaaS、人間作業、外部組織は、必要に応じて利用できるCapability Providerです。

SEI自身が実行安定化の全領域を所有する必要はありません。生成AIが十分に賢くなり、現在のオーケストレーターの多くが不要になった場合でも残る認知・判断の意味構造を主に扱います。

## 8. TEI・SUIとの関係

鼎（TEI）は、SEIから利用し得るCapability Providerの一つです。萃（SUI Sensemaking）は、認知素材を集め、関係や構造を立ち上げる隣接Product / Method familyとして接続し得ます。

```text
SEI = 何を見るか、何を問うか、何を残すか、何を判断するか
SUI = 集めた素材から関係・まとまり・emergenceを扱う一つの手段
TEI = 実行可能な業務Capabilityを実現する一つの手段
```

この関係を固定pipelineにはしません。SEIはSUI / TEIを使わなくても成立し、SUI / TEIもSEI専用Providerとして特権化しません。

Intent、Constraint、Observation、Evidence等に基づき、他のMethod / Providerと同じ判断面で扱えることを目指します。

また、SUI / TEIの内部構造をSEI Universal Coreへコピーせず、必要なCognitive Method、Capability、Observation、Evidence、Artifact referenceを明示的な境界から読み取ります。

## 9. SEIが目指さない将来像

SEIは、次の状態を長期目標にはしません。

- すべての業務をSEI内部で実行する巨大な統合基盤
- あらゆる判断を単一スコアで自動決定するシステム
- AIの内部推論を全量保存する監視基盤
- 特定AIモデルや特定Providerを中心に世界を表現する基盤
- 利用者に最初から完全なontology入力を要求するシステム
- 過去の判断を最新状態へ常に上書きする「現在だけ」の記録基盤
- まだ未確定な認知材料を、AIによって常に一つの結論へ収束させる基盤
- 「共有」の名のもとにAccess / Responsibilityを消す基盤
- 利用者のattentionを常時占有するAI command center

## 10. 長期像

SEIの長期像は「最大の実行基盤」でも「中央のAI脳」でもありません。

**実行方法が何度入れ替わっても、主体が自分たちの認識と判断を失わず、まだ答えになっていない問いへ戻り、過去を検証し、現在を問い直し、許された別の主体と認知成果を引き継ぎ、次の手段を選び直せるための、薄く耐久的な意味基盤**であることを目指します。

基盤自体は薄く交換可能に保ちながら、そこから利用者が近づける認知の深さは制限しません。SEIは答えを置く中心ではなく、問いと認知状態へ繰り返し戻れるdurable cognitive apertureとして働きます。

この長期像が実現しているかは、`SEI_VALUE_MODEL.md`のV1〜V8を用いて、単一スコアではなく複数の観点から継続的に検証します。今回のVision拡張によって新しいValue Axisを追加しません。

## 11. 関連文書

- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_MODEL.md`
- `product/value/SEI_VALUE_PROPOSITION.md`
- `product/value/SEI_BRAND_WORLD_DISCOVERY_SOURCE.md`
- `product/value/SEI_BRAND_WORLD_PRODUCT_VALUE_REVIEW.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `plan/adr/ADR-0001-moving-future-horizon.md`
- `plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 12. 自然な日本語ドラフト

Value Model、Product Value、Decision Continuity、ブランド世界のdiscovery source / Product Value Review、Product Principles、Product Shapeへ戻り、Product Visionとして何を利用世界の将来像へ置くべきかを再検討した。

従来の「薄く耐久的な意味基盤」を維持しながら、「薄い基盤」と「深い認知」を対立させない構造へ拡張した。SEI自身のUniversal CoreやProvider固有実装は薄く保ちつつ、利用者がまだ形になっていない問いへ近づき、boundedに認知成果を共有し、必要以上にattentionを奪われずに思考を継続できる世界を追加した。

井、深層、静けさ等のブランド比喩をそのままRequirementへ持ち込まず、利用世界として説明できる部分だけをVisionへ翻訳した。V1〜V8の意味やEvidence状態を変更せず、自然な日本語として全文を再監査した。
