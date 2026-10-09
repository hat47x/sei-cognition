# SEIが目指す将来像

更新日: 2026-10-10  
状態: **将来像の設計基準。ブランド世界から得た知見を反映済み。§4.1と§11.1は、ADR-0035（Proposed）による再基線化の提案であり、採否（ISSUE-000085）が決まるまで現行の基準として断定しない。**

## 1. この文書の役割

この文書は、SEIが長期的にどのような利用状態を実現したいかを示します。

`SEI_PRODUCT_VALUE.md`ではSEIが存在する理由を、`SEI_VALUE_MODEL.md`では守る価値の優先関係と評価方法を定めます。本書では、それらの価値が実際の利用場面でどのような状態として現れるかを説明します。

特定の型、API、画面、AIモデル、実行方式を将来像として固定する文書ではありません。

また、`SEI_BRAND_WORLD_SOURCE.md`で記録した「井」のブランド世界は、本書を考えるための探索源の一つですが、将来像を定める権威にはなりません。象徴から仕様を直接導くのではなく、利用者や組織にとって意味のある状態として説明できるものだけを本書へ反映します。

## 2. 目指す状態

SEIが目指すのは、AIが高度化した世界で、組織や個人が「自動化できること」を増やすだけでなく、**何を見て、何を問い、何を根拠に、どこまでをAIや外部システムへ委ね、何を自ら判断したのか**を失わずに扱える状態です。

実行技術が変わっても、意思決定の意味と来歴を持ち運べることを重視します。

その結果、利用者は過去の判断を単なるログとして眺めるのではなく、当時の前提へ戻り、新たな検証根拠を加え、必要であれば別の手段や判断を選び直せます。

同時に、すべての認知活動が、最初から判断（Decision）に至るわけではありません。

実務では、まだ何を問うべきか十分に定まっていない段階、確証のない違和感だけがある段階、複数の観察（Observation）が集まり始めていても、提案（Recommendation）へ進むには早い段階があります。

SEIは、そのような途中状態をすぐに「答え」へ変えることを目指しません。問い（Question）、観察、未確定事項（Unknown）、対立（Conflict）、仮説（Hypothesis）などとして外に取り出せたものを、意味差と来歴を失わず扱い、後から別の人間やAIが問い直せる状態を目指します。

## 3. 判断の前から、認知の続きを失わない

現在の製品価値の定義では、判断継続性（Decision Continuity）を、時間・操作画面・AI・情報が変わっても、過去を捏造せず判断仕事の続きを始められることとして重視しています。

本書では、判断が成立する前の段階も視野に入れます。

まだ判断が存在しない問い（Inquiry）についても、時間が空いたり、担当者やAIとの対話が変わったりすると、次のものが失われることがあります。

- そもそも何が気になっていたのか。
- どの観察が最初の問いにつながったのか。
- 何がまだ分からなかったのか。
- どの仮説は未検証のままだったのか。
- 何を次に確かめようとしていたのか。

SEIは、あらゆる思考断片を保存することを目指しません。非公開の推論過程や一時的な作業記憶を正本にすることもしません。

目指すのは、主体が共有・再利用する価値があると判断して外在化した認知対象について、**Decisionになる前であっても、後から文脈を失わず探索を再開できる可能性を保つこと**です。

この状態を独立した製品価値とみなすべきか、Decision Continuityを含むより広い認知の継続性（Cognitive Continuity）として整理すべきかは、実際の利用場面と人間による確認を通して今後検証します。本書では、長期的な利用世界としてこの方向を明示するに留めます。

## 4. 個人や一つのAIとの対話に閉じない共有認知基盤

SEIは、一人の利用者だけの第二の脳や、一つのAIモデルの記憶として完結することを長期的な目標にはしません。

組織の認知活動では、問い、Observation、Decision basis、Unknown、reopen condition等が、特定の担当者や一つのAIとの対話に閉じると、引継ぎや再検討のたびに大きな再構成負担が生じます。

SEIは、これらを適切な境界のもとで、人間とAIが後から利用できる**共有認知資産**として持続させることを目指します。

ただし、共有することと無制限に公開することは同じではありません。

選択的な情報開示、製品の利用権限、責任、実行権限、来歴などを保ち、必要な主体が必要な範囲へ到達できることを重視します。

```text
shared cognition
  != everybody sees everything
  != open to everyone
  != shared Authority
```

共有できることは、全員へ開くことでも、権限を共有することでもありません。一人の利用者や一つのAI sessionで得た認知成果が、そのsessionの寿命だけで消えず、許された別の人間やAIへ引き継げる。そのときもProvenance、historical context、Responsibility、Access boundaryを失わない。この状態を目指します。

この意味でSEIが目指すのは、巨大な中央知識庫でも、組織全体の「中央の頭脳」でもなく、**異なる主体がそれぞれの責任を保ったまま同じ認知資産へ近づける、境界を失わない認知基盤（Cognitive Infrastructure）**です。

### 4.1 社会の水準での姿（仮説・提案）

AIが人の代わりに調べ、提案し、場合によっては委任された範囲で決めるようになると、社会は「誰が何を決め、何を任せ、何を分からないまま進めたのか」を後から説明できる基盤を必要とするのではないか、という仮説を置きます。行政や公共の判断、研究の再現性、危機のときの判断、熟議のなかの少数意見、特定のAI供給元への依存、世代をまたぐ長期の判断といった場面が考えられます。

これは新しいValue Axisではなく、V1〜V8とCognitive Commons（個人や一つのAI sessionに閉じず、適切な境界のもとで持続的に共有される認知資産の状態。`../value/SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md` §4を参照）が、個人や組織を越えて成り立ったときの姿についての**Visionの仮説**です。Evidenceはまだありません。公共の利益という大義を理由に、Selective Disclosure、Responsibility、privacyを弱めることはしません。SEIが監視の拠点になることは、明示的な非目標です。場面の一覧と、確かめるべきEvidenceは`../value/SEI_FAMILY_APEX_VALUE_REVIEW.md` §12にあります。この仮説は、ADR-0035（Proposed）の未確認事項として扱い、採否はISSUE-000085で判断します。

## 5. AIが強くなるほど、薄くできる層と残す層を分ける

SEIは、現在の技術制約を恒久的な製品構造へ固定しません。

評価のたびに、その時点の現実からおおむね10〜50倍程度先までを見渡し、現在のAIや実行基盤が大幅に強くなってもSEIが守る必要のある意味差かを問い直します。この距離は固定の倍率を測る評価基準ではなく、現在の制約への過適合を避けるための移動する思考基準です。

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

具体的な型を汎用の中核へ置くかどうかは、本書から直接決めません。価値の評価模型、利用場面、要求、ADRを通して判断します。

## 6. 交換可能にしていくもの

次のような仕組みは、必要であってもSEIの恒久的な中核にしないことを基本とします。

- 業務の流れを表す有向非巡回グラフ
- 待ち行列
- 再試行と再試行までの待機
- 処理の実行先の割り当て
- AIエージェントのやり取りの振り分け
- 再開地点を保存する仕組みの実装方式
- 外部提供元のSDK固有の処理
- 指示文固有の処理の振り分け
- 特定モデル固有の補助構造
- 特定のデータベースやイベント履歴の保存方式

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

## 11. SUI・TEI・EKIとの関係

萃（SUI Sensemaking）、鼎（TEI）、益（EKI Fabric）はSEIと連携し得る隣接Productですが、SEIの内部moduleではありません。

```text
SUI = 未整理な材料から関係・仮説・構造・統合を形成し、意味形成を成熟させる
SEI = 認知・問い・不確実性・根拠・判断・Capability・来歴を継続可能な意味として保つ
TEI = 受入済みの業務・Application・Infrastructure knowledgeをformalizeし、構築・実行・Agent業務遂行へ接続する
EKI = 異質で一時的な計算資源を束ね、計算を適切な場所で実行する
```

SUIで形成されたObservationやHypothesisをSEIのInquiryへ接続する、SEIがTEIをCapability Providerとして利用する、SEIが必要とする認知処理をEKI上の資源へ配置するといった協調は可能です。

AI Business Actorを使う場合、TEIがBusiness Procedure / Action / Constraint / Authorization / Runtime Binding等のOperational Knowledgeを提供し、SEIは必要に応じてObservation / Question / Unknown / Recommendation / Decision等の認知・判断文脈を提供できます。AgentがTEIだけを読んで既定業務を遂行する構成も、SEIが判断文脈を補う構成も成立し得ます。

```text
SEI
  what to notice / question / decide
        ↓ optional
AI Business Actor
        ↓ reads
TEI
  what can be done / under which constraints and authority
        ↓
Execution
        ↓
Observation / Evidence
        └── SEIへ戻せる
```

この協調でも、Agent runtimeそのものをSEI Universal Coreへ取り込みません。

ただし、この関係を固定pipelineにはしません。SEIはSUI / TEI / EKIを使わなくても成立し、各ProductもSEI専用のsurface、Provider、runtimeとして特権化しません。関連製品であるという理由だけで、優先度、信頼、Authorityを与えないことを維持します。

また、SUIのsensemaking object、TEIのApplication / Database / Release、EKIのWorker / scheduler等の内部構造をSEI Universal Coreへコピーしません。必要なCognitive Method、Capability、Observation、Evidence、Artifact reference、Execution receipt等を、明示的な境界から読み取ります。

この分離により、認知手段や実行場所が変わってもSEIの意味を保ちながら、各Productがそれぞれの専門領域で独立に進化できます。

### 11.1 家族に対する統合の頂点としての役割（提案）

本提案を支える根拠はDesign Evidenceだけであり、Executable以上の段階の根拠は追加されていません（ADR-0035）。

上の関係を保ったまま、SEIが家族に対して持つ役割を、隣接Productの一つとしての役割から、家族の「頂点」としての役割へ、一段はっきり書きます（ADR-0035、Proposed）。この提案の採否は、ISSUE-000085で製品の所有者が判断します。

SEIを家族の「頂点」と呼ぶのは、次の三つの意味に限ります。

- **抽象の頂点** — Observation、Decision、Authorityなど最も一般的な意味を持ち、各製品に固有の意味を翻訳できる。意味の正本は各製品に残る。
- **時間の頂点** — 家族の中で最も長く生きる記録を持つ。製品、モデル、組織より長く残る。
- **統合の頂点（任意の合流）** — 製品をまたいだ認知を、時間を通して再構成できる場所になる。製品は送ってもよいが、送らなくても成り立つ。

次の三つの意味は採りません。

- **指揮の頂点** — SEIから他の製品への信号は、すべて依頼です。受け取った製品が自らの権限で判断します。SEIのRecommendationが、TEIのAuthorizationになることはありません。
- **所有の頂点** — SEIが持つのは、参照とコミットメントと対応表だけです。他の製品の意味やデータの正本は持ちません。
- **可用性の頂点** — どの製品の局所のループも、SEIの稼働を必要としません。

```text
SEI = 抽象の頂点 + 時間の頂点 + 統合の頂点（任意の合流）
SEI != 指揮の頂点 / 所有の頂点 / 可用性の頂点
```

SEIはcentral AI brainではなく、固定pipeline（`SUI -> SEI -> TEI -> EKI`のstack）でもなく、関連製品に特権を与えません。「神経系の頂点」という言い方は内部の設計言語に留め、ブランドの表現では巨大なAI brainやcommand centerを視覚の中心に置きません。

制御の仕組み（routing、escalation、attentionの配分、cascade等）は、交換可能なRealizationまたはProfileとします。一方、制御の判断の意味（何を見て、何を意図的に見送り、どのMethodやProviderをなぜ選び、何を保留し、何を上位へ回したか）は、Coreに記録すべき意味として扱います（`../definition/SEI_PRODUCT_SHAPE.md` §8.3、ADR-0035 Decision 3）。「Coreに残す」とは、新しいUniversal型を直ちに追加することではありません。まず、既存のDecision Memory、Cognitive Method Application、Capability Choiceの組合せで表せるかを試します。とくに「何を意図的に見送ったか」という注意の範囲は、現在の契約で受け皿が明確でないため、ISSUE-000086で検証します（ADR-0035 Decision 3）。ADR-0035のConsequencesも、「新しいCore要素は追加しません。」と定めています。家族の判断の意味論の参考対応表は、提案中の参考文書として`../definition/SEI_FAMILY_SEMANTIC_MAP.md`にあります。

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
- `product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md`（提案。ADR-0035, Proposedに伴う2026-09-27の評価記録。Design only）
- `product/definition/SEI_FAMILY_SEMANTIC_MAP.md`（提案。ADR-0035 Decision 4に伴う参考の対応表。non-contract、各対応は候補）
- `product/vision/SEI_BRAND_WORLD_SOURCE.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `plan/issue/ISSUE-000077-integrate-brand-world-into-product-value-discovery.md`
- `plan/adr/ADR-0001-moving-future-horizon.md`
- `plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `plan/adr/ADR-0035-family-integration-apex-and-control-meaning-boundary.md`（提案。Proposed）
- `plan/issue/ISSUE-000085-rebaseline-family-integration-apex.md`（採否待ち）

## 15. 自然な日本語ドラフト

Brand World SourceとProduct Value Discovery Reviewを通じて、ブランド上の比喩とProduct Visionへ反映すべき利用状態を分離しました。

その結果、井戸、水、中央の空白といった象徴語そのものを本書の規範へ持ち込むのではなく、判断前のInquiryを失わないこと、個人や一AI sessionへ閉じない共有認知基盤であること、共有とSelective Disclosureを両立すること、人間・AI・Methodが利用するInfrastructureであること、過剰なattentionを要求しないことを将来像として反映しました。

V1〜V8やDecision Continuityの意味を変えず、Inquiry Continuityについては未検証Product hypothesisのまま残しています。

2026-10-02には、ADR-0035（Proposed）に沿って、社会の水準での姿を仮説として§4.1に、家族に対する統合の頂点（三つを採り三つを採らない）を§11.1に加えました。中央の頭脳ではないこと、固定pipelineではないこと、関連製品を特権化しないことは、そのまま維持しています。どちらも提案であり、根拠はDesign Evidenceだけです。

2026-10-10には、§11.1をADR-0035（Proposed）のDecision 1〜3と式、Consequencesと照合し、文言を揃えました。具体的には、式へ「（任意の合流）」を戻し、制御の判断に関する限定（新しいUniversal型を直ちに追加しないこと、新しいCore要素を追加しないこと）を加え、役割の説明から「統合の層」を外して「頂点」の語へ置き換え、§11.1の冒頭に根拠の段階（Design Evidenceのみ）を加えました。あわせて、状態行を、§4.1と§11.1が採否待ちの提案であることを明示する表現へ戻し、用語を main（7822812）の推敲語へ戻しました（検証根拠、実行権限、汎用の中核など）。Cognitive Commonsの定義元（`../value/SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md` §4）の参照、§4.1と§11.1の採否の参照先（ADR-0035、ISSUE-000085）、§14の提案文書への注記も、この版に含まれています。
