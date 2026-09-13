# ISSUE-000077: ブランド世界をProduct Value探索の源泉として検証し、上位価値文書へ最適に反映する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018**  
Updated: 2026-09-13

## Goal

SEI Cognitionのブランド設計を通して言語化されてきた「井」の世界観を、外見上のブランド表現だけに閉じず、**SEIが利用者や組織へどのような価値を届けるべきかを考えるための、豊かな上流探索源として保存・検証し、Product Value関連文書へ最も適切な形で反映できる状態にする。**

このIssueの目的は、井戸、水、深層、静けさ、共有財産といった象徴を、そのままProduct RequirementやUniversal ontologyへ変換することではない。ブランド世界が照らしている利用者価値、まだ十分に言語化されていないProduct hypothesis、既存Value Modelの盲点や弱い部分を発見し、それぞれを現実の利用状況、反証可能なScenario、既存Product Valueとの整合へ戻して検討する。

最終的には、ブランド世界から得られた洞察を一つの宣伝文句へまとめるのではなく、次の問いへ答えられる状態を目指す。

- SEIは、なぜ単なるAI agent、知識管理、意思決定ログ、workflow基盤ではなく、**Cognitive Infrastructure**として存在する価値があるのか。
- 現在のProduct Value / Value Model / Product Visionが、その価値を十分に捉えているか。
- ブランド世界から新しく見えてきた価値のうち、長期的に守るべきものは何か。
- 何がProduct Visionとして記述すべき将来像で、何がProduct Valueとして守るべき価値で、何がPrinciple、Value Proposition、Milestone、Interaction hypothesisとして扱うべきか。
- 逆に、象徴としては美しくても製品上の規範へ昇格させるべきでないものは何か。
- それらを自然で豊かな日本語として残し、今後の生成AI・人間双方が、実装都合へ流されずProduct Valueへ立ち戻れる源泉にできるか。

このIssueは「ブランド文書を一つ追加した」だけではResolvedにしない。ブランド世界をProduct Value探索へ接続する方法を確立し、既存上位文書を実際に読み直し、必要な文書の新規起票・改稿・No Change判断まで完了させることをResolution条件とする。

## Background

### 1. current Product baselineとの関係

currentの`SEI_PRODUCT_VALUE.md`では、SEIを、人間・AI・組織・プロジェクトなどの主体が、何を観察し、何をまだ分かっていないと認め、何を問い、何を根拠として、どのように判断したかを失わずに扱うための認知・意思決定基盤として定義している。

その中核には、Unknown / Conflict / Hypothesisを安易に確定値へ潰さないこと、Recommendation / Decision / Authority / Action Intent / Executionを分けること、判断の意味と来歴を残すこと、CapabilityとProviderを分けること、人間とAIが同じcanonical meaningへ戻れることがある。

さらに、複数のValue Axisが一つの実務の中で同時に成立した結果として、Decision Continuityを「時間・Surface・AI session等をまたいでも、過去を捏造せず判断仕事の続きを始められること」と整理している。

これらはSEIの重要なProduct Value baselineであり、本Issueはこれをブランド思想で置き換えない。

一方、ブランド設計を深める過程では、既存文書の「意味を保存する」「判断を継続する」という軸だけでは捉えきれていない可能性のある、別の角度からの価値が見えてきた。

それは、SEIを「記録を正しく残す仕組み」としてだけでなく、**組織がまだ十分に形を得ていないものへ安全に近づき、人間とAIが共有可能な認知対象として扱えるようにする場**として見る視点である。

この視点が実際のProduct Valueを豊かにするのか、既存V1〜V8の別表現に過ぎないのか、あるいはブランド上の比喩に留めるべきなのかは、まだ確定していない。本Issueでは、そこを早急に結論づけず、上流のProduct探索として扱う。

### 2. ブランド世界の中心 — 井は「考える主体」ではなく境界装置である

SEI Cognitionの象徴として採る「井」は、単に水を蓄える容器ではない。

井戸の本質は、地表からは直接見えない水脈と、人が生活する地上との間に、繰り返し利用できる接点を設けることにある。井そのものが水を作るわけでも、共同体の代わりに何かを決めるわけでもない。そこに適切な構造があることで、必要なときに深部へ近づき、汲み上げ、観察し、共同体へ持ち帰ることができる。

この構造をSEIへ重ねると、次のような世界像が現れる。

```text
見えている世界 / すでに言語化された認知
                  ↓
                「井」
     ─────────────────────
         まだ十分に形を得ていない領域
```

下側にあるものを「真実」や「答え」と決めつけないことが重要である。そこには、断片的な観察、弱い兆候、未整理の経験、言葉になる前の違和感、組織内に散在する記憶、まだ検証されていない関係候補、Unknown、Conflict、Possibilityなどが混在し得る。

SEIの役割は、それらを権威的に解釈して正解へ変えることではない。問い、観察、Cognitive Method、人間の経験、AIの補助などを通して、**まだ曖昧なものを、来歴と不確実性を失わずに、扱える認知対象として表層へ持ち上げられる条件を整えること**にあるのではないか。この仮説をProduct Valueの観点から検討する。

### 3. 中央の空白 — SEIは「答えを置く中心」ではなく「問いを置ける余白」を支える

井桁の造形では、四本の線だけでなく、その線が囲む中央の空白が重要である。

一般的な`#`記号では線の交差そのものが記号性を持つ。しかしSEIの井桁では、線は中央の空間を成立させるための構造体として読むことができる。

この読みはProduct Valueへも重要な問いを投げかける。

SEIの価値は、中心に万能なAI、巨大な知識グラフ、単一の正解生成器を置くことなのか。それとも、組織の中に、まだ分からないことを分からないまま置き、問い直し、複数の主体が別の角度から近づける**認知上の余白**を耐久的に確保することなのか。

もし後者がSEIの長期価値なら、Unknown / Conflictを消さない既存原則、AI suggestionをDecisionへ黙って昇格させない境界、Progressive Explicitness、private chain-of-thoughtを正本にしない考え方は、個別仕様ではなく、より大きなProduct姿勢の一部として読み直せる可能性がある。

一方で「余白」は曖昧さを放置することとは異なる。必要なDecisionを避けるための口実にもしてはならない。曖昧さを正直に扱いながら、必要な時点では責任線を伴った判断へ進めることとの両立を検討する。

### 4. 水 — 完成済みKnowledgeではなくCognitive Potentialとして扱う

ブランド上の水を、単純にKnowledgeの象徴とみなすと、「地下に正解が完成しており、それをSEIが取り出す」という誤解を招く。

より適切なのは、水を**Cognitive Potential**の比喩として扱うことである。

そこには、情報、記憶、痕跡、弱いsignal、未解決の経験、まだ意味づけられていない関係、可能性が混ざっている。汲み上げた時点でも、それは自動的にEvidenceやTruthにはならない。

この視点は、SEIがObservation、Hypothesis、Unknown、Conflict、Evidence Use、Assurance等を分けて扱う現在の方向と親和性が高い。ただし、比喩の親和性だけから新しいUniversal型を作らない。Product Valueとして独立した意味があるかを、既存Value AxisとScenarioへ戻して評価する。

### 5. 静けさ — aestheticではなく「早すぎる収束を強制しない能力」

SEI Cognitionのブランドでは、派手な発光、巨大なAI脳、command center、全知のeyeなどを避け、静かな水面、弱い波紋、反射、深さを重視している。

この静けさを単なるVisual Toneとして終わらせない。

SEIにとっての静けさは、次のような製品上の態度と結び付く可能性がある。

- Unknownを`No`へ急いで畳まない。
- Conflictを最新値へ上書きしない。
- ObservationをTruthへ早まって昇格させない。
- AIが強いRecommendationを出しても、DecisionやAuthorityとの境界を消さない。
- 判断に必要な時間や問い直しの余地を、UIや自動化の都合だけで奪わない。
- 利用者へ大量の情報を押し付けるのではなく、必要な意味へ段階的に降りられるようにする。

すなわち「quiet infrastructure」は、反応速度が遅いという意味ではなく、**組織を不用意に一つの結論へ押し流さず、必要な認知差を保ったまま前へ進める基盤**というProduct hypothesisになり得る。

この価値が既存V5 Uncertainty Preservation、V7 Progressive Explicitness等で十分表現されているか、それともProduct Vision / Principleに統合した方が利用者世界を正確に表せるかを検討する。

### 6. 四方向性と公共性 — 中央集権ではなくShared Accessibility

「井」の四方向を、Human / AI / Data / Methodのような固定4分類へ割り当てない。

四方向性は、**どこからでも近づけること**の象徴として扱う。

SEIは特定AI model、特定部署、特定の専門職だけが所有する「中央の頭脳」ではなく、人間、AI、Cognitive Method、documents、systems、Observation等の異質な主体・情報源が、責任とaccess boundaryを保ちながら同じ認知基盤へ接続できることを目指す。

ここでいう公共性は、すべての情報を全員へ公開することではない。SEIにはProduct Access、semantic Responsibility / Authority、Selective Disclosure等の境界がある。したがって検討すべきなのは「無制限な公開」ではなく、**認知資源が一個人・一AI session・一Providerの私有状態へ閉じず、適切な権限のもとで組織の共有財産として持続できること**である。

この観点から、`cognitive commons`というProduct hypothesisを検討する。ただし`commons`を法的・制度的な意味へ過度に一般化せず、どのような利用者価値と失敗パターンを表しているかをScenarioで確認する。

### 7. 人間とAIは井を利用する主体であり、井そのものではない

SEIをcentral AI brainとして描かないことは、Visual Identity上だけの判断ではない。

SEIが長期的なCognitive Infrastructureであるなら、AI modelが交換されても、人間の担当者が変わっても、Cognitive Methodが変わっても、認知上の意味と来歴が継続できる必要がある。

```text
Human ─────┐
AI ────────┤
Method ────┤
Document ──┼── SEI Cognition
System ────┤
History ───┘
```

AIは重要な利用主体・Provider・Method realizationになり得るが、SEIの意味上の中心そのものにはしない。

この視点はProvider IndependenceやExecution Independenceと整合する。一方で、今後AIが大幅に高度化したときにも、SEI独自のProduct Valueとして何が残るかを考える重要な手掛かりにもなる。

### 8. SEI / SUI / TEIの象徴関係

関連製品群では、卦を機械的な分類体系ではなく、各ソフトウェアの位置づけを示唆する象徴層として扱う。

現時点の象徴的な読みは次の通りである。

```text
井 / SEI Cognition
  depth / access / cognition

萃 / SUI Sensemaking
  gathering / relation / emergence

鼎 / TEI
  transformation / realization / execution
```

これを固定pipelineやUniversal workflowへしない。

ただしProduct Value探索では、次の循環を考える手掛かりとして利用できる。

```text
まだ十分に形を得ていないもの
        ↓
SEI: 認知可能な素材として扱える条件をつくる
        ↓
SUI: 素材を集め、関係と構造を立ち上げる
        ↓
TEI等: 意味・Intentを実現可能なCapabilityへ接続する
        ↓
実行・現実世界の変化
        ↓
新しいObservationとしてSEIへ戻る
```

実際の利用では順序が前後し、SUIやTEI以外のMethod / Providerも使われる。この象徴関係を、関連製品の特権化や必須依存関係の根拠にはしない。

## Product Value discovery hypotheses

本Issueでは、少なくとも次の仮説を検討対象とする。これらはcurrent Product Valueへの追加を決定したものではない。

### H77.1 — Cognitive Commons

SEIの価値の一部は、認知資源を一個人、一AI session、一Providerの一時状態へ閉じず、適切なaccess / responsibility boundaryのもとで、人間とAIが後から共有・再利用・問い直しできる組織の共有資産として保つことにあるのではないか。

### H77.2 — Surface / Depth Interface

SEIは、すでに明示されたKnowledgeを保存するだけでなく、まだ十分に言語化・構造化されていない観察や違和感を、Truthへ早まって昇格させず、扱える認知対象へ持ち上げる境界として価値を持つのではないか。

### H77.3 — Deliberate Non-closure

SEIは、すべてを最短で結論へ収束させることではなく、Unknown / Conflict / Hypothesis / alternate interpretationを必要な期間保持し、判断時には未解決のまま残したものも含めて責任あるDecisionへ進めることで価値を生むのではないか。

### H77.4 — Durable Cognitive Aperture

SEIの中核価値は「多くの情報を保持すること」だけではなく、時間・担当者・AI・Surfaceが変わっても、問いを置き直し、過去の認識へ戻り、新しい観察を加えられる認知上の入口を持続させることにあるのではないか。

Decision Continuityが「判断仕事の続きを始められること」を扱うのに対し、この仮説は、その続きを始めるための認知上の入口や問いの余地が、そもそも共有基盤として維持されていることに焦点を置く。独立したProduct Valueか、Decision Continuityの一側面かを検証する。

### H77.5 — Quiet Infrastructure

SEIの使いやすさは、情報やAI suggestionを大量に提示することではなく、必要なものを必要な時に汲み上げられ、通常時には認知負荷を増やしすぎない「静かな基盤」であることによって高まるのではないか。

これはUI aestheticではなく、Progressive Explicitness、attention burden、notification / recommendation pressure、resume負担、human correction burden等として検証可能なProduct hypothesisへ落とせるかを確認する。

### H77.6 — Shared but not Unbounded

「共有財産」であることと「無制限に誰でも読めること」を分離し、共有可能性、Provenance、Responsibility、Selective Disclosure、Access Controlが両立するときに初めて、組織のCognitive Commonsとして価値が成立するのではないか。

## Questions

1. ブランド世界で言語化された価値のうち、current `SEI_PRODUCT_VALUE.md` / V1〜V8 / Decision Continuityですでに十分に表現されているものは何か。
2. 既存文書では弱い、あるいは見落とされている独立したProduct Valueはあるか。
3. `cognitive commons`はProduct Valueとして独立させるべきか、Human / AI Readability、Decision Continuity、Provider Independence等の横断的な利用状態として表現すべきか。
4. 「表層と深層の境界」は、具体的な利用者Scenarioではどのようなfailure / benefitとして現れるか。単なる詩的比喩に留まる部分はどこか。
5. 「中央の空白」「問いを置ける余白」は、Unknown Preservation、Open Question、Progressive Explicitness、Interaction Designへどのように接続するか。
6. 「静けさ」を、単なるVisual ToneではなくProduct品質として扱う場合、何を観測すればよいか。attention burden、forced convergence、recommendation pressure、capture overhead等のうち何が本質か。
7. 水をCognitive Potentialと読むことは、Observation / Hypothesis / Evidence / Unknown等の既存意味境界を説明しやすくするか。それとも不要な比喩を持ち込むか。
8. 組織内の共有財産という価値を強めるとき、privacy、Selective Disclosure、Responsibility、Authority、Access Controlと矛盾しない表現は何か。
9. SEI / SUI / TEIの象徴的関係からProduct Value上の有用な問いを得られるか。その関係を固定pipelineや関連製品の特権化へ変えずに済むか。
10. current Product Visionの「薄く耐久的な意味基盤」という長期像と、「深層へ開く共同利用可能なCognitive Infrastructure」という世界像は、どこで統合し、どこで区別すべきか。
11. Product Value文書の改善が必要な場合、`SEI_PRODUCT_VALUE.md`、`SEI_VALUE_MODEL.md`、`SEI_PRODUCT_VISION.md`、`SEI_PRODUCT_PRINCIPLES.md`、`SEI_VALUE_PROPOSITION.md`、Product Interaction / Milestoneのどこへ何を書くのが最も自然か。
12. ブランド世界を今後の価値探索に利用し続けるために、ブランド原典をどの文書として保存し、規範文書とのauthority差をどう明示すべきか。

## Constraints

- ブランド世界は**Product Value discovery source**であり、それ自体をProduct Value authority、Requirement authority、Universal ontologyにはしない。
- 「井」「水」「無意識」「深層」「余白」等の象徴から、型、field、workflow、UI、storage structureを直接演繹しない。
- 「無意識」という語を心理学的・医学的事実として一般化しない。ブランド上は、まだ十分に言語化・表層化されていない領域を示す比喩として慎重に扱う。
- `cognitive commons`を、全情報の無制限公開や権限境界の撤廃と同一視しない。
- SEIをcentral AI brain、all-seeing intelligence、single source of truthとして再定義しない。
- AI、Human、Method、Providerの一つを自動的にAuthorityへ結び付けない。
- Unknown / Conflict / Hypothesis / Observation等のcurrent semantic distinctionを、ブランド上の分かりやすさのために潰さない。
- SUI / TEIとの象徴的親和性を、必須依存、固定workflow、Provider優先の理由にしない。
- 新しいValue Axis、Stable Requirement、Universal型を増やすこと自体を成果にしない。既存文書で十分ならNo Changeまたは既存概念の再説明を正当な結論とする。
- 画像生成結果やロゴ造形上の偶然をProduct Requirementへ持ち込まない。
- Product文書へ採用する価値は、ブランドとして美しいかではなく、利用者世界のbenefit / failure、長期耐久性、既存Valueとの差、反証可能性によって判断する。
- 自然な日本語による豊かな叙述を優先するが、詩的表現によって要求強度やEvidenceの高さを曖昧にしない。

## Investigation method

### Step 1 — Brand-world sourceを独立して保存する

ここまでのブランド議論を、広告コピーではなくProduct Value探索へ利用できる原資料として再構成する。

最低限、次を含める。

- 井は地表と見えない水脈の間にあるgateway / access pointであること。
- 中央のnegative spaceは、全知のcoreではなく問いと可能性のためのapertureとして読むこと。
- 水は完成済みKnowledgeよりCognitive Potentialとして読むこと。
- 静けさは、早すぎる収束を強制しないProduct attitudeへ接続し得ること。
- 四方向性は固定分類ではなくshared accessibilityとして読むこと。
- SEIは共同体の代わりに考えるのではなく、共同体がより深く考えるための基盤であること。
- Human / AI / Method / System等は井を利用する主体であり、井そのものではないこと。
- SEI / SUI / TEIの象徴的関係を、固定pipelineではなくProduct landscapeを考える補助線として扱うこと。

この原資料には、何が象徴的解釈で、何がcurrent Product baselineで、何が未検証Product hypothesisかを明示する。

### Step 2 — current Product文書へ逆照合する

少なくとも次を全文で読み直す。

- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_PROPOSITION.md`
- `product/value/SEI_VALUE_MODEL.md`
- `product/value/SEI_DECISION_CONTINUITY.md`
- `product/value/SEI_VALUE_ACCEPTANCE.md`
- `product/vision/SEI_PRODUCT_VISION.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `product/definition/*`
- `product/interaction/*`
- `product/roadmap/*`

ブランド世界にある語を探すのではなく、**利用者世界の意味がすでにどこまで表現されているか**を確認する。

### Step 3 — KJ的に価値候補を統合する

ブランド世界から生まれた洞察を、既存V1〜V8や文書章立てへ機械的に分類しない。

まず、利用者にとって何が起きるのか、何が失われるのか、何が嬉しいのかという意味のまとまりを保ったカード / claimとして扱う。近いものを統合し、矛盾や残余を残したうえで、より大きなProduct Value構造を形成する。

ここで重要なのは、ブランド体系をKJの外部分類枠として使わないことである。井の象徴は探索対象を広げるcueとして使い、最終的なProduct Value構造はSEIの実際のProduct materialから立ち上げる。

### Step 4 — Benefit / Failure / Counterexampleへ変換する

各価値候補について、少なくとも次を記述する。

```text
symbolic insight
  ↓
user / organizational benefit hypothesis
  ↓
observable failure if absent
  ↓
counterexample / overreach risk
  ↓
existing Value / Requirement coverage
  ↓
proper document placement
```

例:

```text
「静かな井」
  ↓
利用者へ常時AI suggestionを押し付けず、必要時に認知資源へ到達できる
  ↓
重要なUnknownが大量notificationや自動Recommendationに埋もれ、早すぎるDecisionへ誘導される
  ↓
単にUIを静かな色にすることはProduct Valueではない
  ↓
V5 / V7 / Product Interactionで既に十分かを確認
```

### Step 5 — 文書の役割を先に決める

新しい文章を書き始める前に、内容をどの高さの文書へ置くか決める。

```text
Brand-world source
  = Product Value探索の原資料 / 非規範

Product Vision
  = 価値が実現した利用世界の将来像

Product Value
  = SEIが存在する理由と守る価値

Value Model
  = 価値の優先関係・成立条件・failure

Value Proposition
  = 利用者へ伝える価値の焦点

Product Principles
  = 下位設計で繰り返し適用する判断原則

Milestone / Interaction hypothesis
  = 価値を反証可能にする利用状態・探索単位

Requirement
  = 独立した規範上の必要性が実証された後
```

同じ思想を複数文書へ重複コピーしない。各文書が必要とする粒度へ翻訳する。

### Step 6 — Alternative readingを必ず作る

一つのブランド解釈だけでProduct Valueを確定しない。

少なくとも次の対立解釈を検討する。

- 深層へアクセスする基盤 vs 既知の判断を保存する基盤
- Cognitive Commons vs privacy / bounded access
- 静かな基盤 vs proactive assistance
- 非収束性 vs decision latency
- 余白を守る vs structure不足
- shared cognition vs clear Responsibility
- poetic coherence vs practical product differentiation

価値の豊かさを守りつつ、Productとしてのtrade-offを見えなくしない。

### Step 7 — 必要なProduct文書を起票・改稿する

Step 1〜6を経て必要性が確認できたものだけを、適切な上位文書へ反映する。

候補には次を含むが、すべてを作ることを前提にしない。

- Brand-world source文書の新規作成。
- `SEI_PRODUCT_VISION.md`の再ドラフト。
- `SEI_PRODUCT_VALUE.md`の価値定義追加・再統合。
- `SEI_VALUE_MODEL.md`の価値階層・failure / trade-off見直し。
- `SEI_VALUE_PROPOSITION.md`の利用者向け価値表現見直し。
- `SEI_PRODUCT_PRINCIPLES.md`の追加・統合。
- Product Interaction / Milestoneでの検証hypothesis追加。
- 新規文書不要 / No Changeという結論。

### Step 8 — Natural Japanese synthesis

各文書は、ブランド語彙を断片的に貼り付けるのではなく、文書全体の役割に沿って全文を読み直す。

そのうえで、背景、価値、限界、他の価値との関係が自然に流れるように再構成し、**自然な日本語となることを最重要視して、必要な範囲で全文をドラフトし直す。**

短い標語だけを増やして「価値が深まった」とみなさない。読者がSEIの存在理由を自分の言葉で再構成できるだけの文脈を残す。

### Step 9 — Meaning / authority audit

最後に、ブランドから来た比喩が規範へ過剰昇格していないかを監査する。

- Product hypothesisを成立事実として書いていないか。
- Design insightをAdoption / Outcome Evidenceとして扱っていないか。
- 比喩からUniversal型を直接導いていないか。
- current Product Valueと矛盾する場合、暗黙に上書きせずRebaseline判断を行っているか。
- 新しい価値を追加した結果、既存Value Axisとの二重評価が生じていないか。
- 「共有」「公共」「深層」「静けさ」等の語が、読み手ごとに全く異なる意味へ広がらないだけの説明を付けているか。

## Required scenarios / experiments

本Issueの中心は上流文書探索であり、直ちにruntime実装を要求しない。ただしProduct Valueへ昇格させる候補は、少なくとも次のScenarioへ落として反証可能性を確認する。

1. **Latent observation scenario**  
   利用者がまだ確証のない違和感を持っている。SEIがそれをTruthやDecisionへ強制せず、Observation / Question / Hypothesis等として適切な形で外在化し、後から他のEvidenceと結び付けられるか。

2. **Shared cognitive resource scenario**  
   一人の利用者や一つのAI sessionで得られた認知成果が、Provenanceとaccess boundaryを保ったまま、別の人間・AIへ継続利用可能か。

3. **Quiet assistance scenario**  
   AIが多数の候補を生成できる状況で、SEIが大量提示そのものを価値とせず、利用者が必要な問い・Unknown・Decisionへ戻るための認知負荷を下げられるか。

4. **Non-closure scenario**  
   ConflictやUnknownが残っている状態でDecisionが必要になったとき、未解決を消さずに判断でき、後から何を未解決のまま受け入れたか読めるか。

5. **Bounded commons scenario**  
   shared cognitionを実現しながら、一部ObservationやEvidenceにはSelective Disclosureが必要である。共有価値とAccess / Responsibilityが両立するか。

6. **Model replacement scenario**  
   AI modelやCognitive Methodを交換しても、井としての共有認知基盤へ戻り、以前の問い・観察・未解決点を別の主体が読み直せるか。

7. **Alternative solution comparison**  
   raw chat、shared note、wiki、knowledge graph、decision log等の単純代替と比べ、SEI固有の追加構造がどの価値差を生み、その負担を正当化するか。

これらは最初からStable Acceptance Scenarioへ追加しない。まずProduct hypothesisの質を確かめ、既存Scenarioで十分かを監査する。

## Deliverables

最低限、次を成果物とする。

1. **ブランド世界をProduct Value探索源として保存する文書**  
   象徴、Product hypothesis、current baseline、非規範部分を明確に分離し、ここまでの議論の豊かさを失わない自然な日本語で記述する。

2. **Product Value Discovery Review**  
   H77.1〜H77.6および追加候補について、既存V1〜V8 / Decision Continuityとの重複、独立性、benefit、failure、counterexample、文書配置を比較する。

3. **必要と判断したProduct上位文書の起票・改稿**  
   `SEI_PRODUCT_VALUE.md`、`SEI_VALUE_MODEL.md`、`SEI_PRODUCT_VISION.md`、`SEI_VALUE_PROPOSITION.md`、`SEI_PRODUCT_PRINCIPLES.md`等から必要なものを選び、重複を避けて最適な構造へ反映する。

4. **No Changeを含む判断記録**  
   象徴としては有用でもProduct Valueへは採用しなかった洞察について、捨てた理由が後から分かるようにする。

5. **Follow-up exploration**  
   human review、prototype、Interaction experiment等が必要な価値仮説は、このIssue内でStable Requirementへ急がず、独立したIssue / Candidate Requirementとして起票する。

6. **Traceability / documentation registry更新**  
   current正本へ反映した範囲を追跡可能にし、追加・更新したMarkdown文書をDocument Review Registryへ反映する。

## Resolution

次をすべて満たしたときにResolvedとする。

- ここまでのブランド世界を、短いブランドコピーへ圧縮せず、Product Value探索に利用できる十分に豊かな文章としてrepositoryへ保存した。
- その文書がBrand authorityとProduct Value authorityを混同していない。
- H77.1〜H77.6を含む価値候補をcurrent Product Value / V1〜V8 / Decision Continuityへ逆照合した。
- 各候補について、利用者benefit、failure、counterexample、既存coverage、文書配置を検討した。
- 必要なProduct上位文書を実際に起票・改稿し、不要な場合はNo Change理由を記録した。
- 新しいValue Axis / Requirement / Universal型を追加した場合は、その独立必要性をブランド比喩以外のScenario / Evidenceで説明できる。
- 自然な日本語を最重要視した全文再ドラフトを行い、象徴の豊かさと技術的な意味境界の双方を維持した。
- `plan/registry.yaml`、`plan/document_review_registry.yaml`、必要な上流計画との整合を確認した。

このIssueがResolvedであることは、追加したProduct hypothesisがAdoption / Outcome Evidenceまで実証されたことを意味しない。Product文書としての統合と、実利用での成立確認を分離する。

## Reopen conditions

Resolved後も、次の場合は再開または後続Issueを起票する。

- 実利用で、ブランド世界から導いたProduct Value表現が利用者の実際の価値と大きくずれていることが分かった。
- `cognitive commons`、quiet infrastructure、surface / depth interface等に、既存V1〜V8では説明できない独立したProduct failureが繰り返し観測された。
- 逆に、新たに追加した価値概念が既存Valueとの重複であることが実証された。
- privacy、security、Access Control、Responsibilityとの衝突により、共有財産としての表現を再設計する必要が生じた。
- AI能力の大幅な変化によって、現在のCognitive Infrastructure像の一部が不要または過剰になった。
- SEI / SUI / TEIの製品境界が変わり、現在の象徴関係がProduct理解を誤らせるようになった。
- ブランドアイデンティティ自体が大きく変更され、Product Value探索源としての前提を見直す必要が生じた。

## Verification

本Issueの初期段階ではruntime checkerのPASSを主Evidenceとしない。

確認の中心は次である。

- current Product文書との意味整合。
- Value候補の重複・独立性監査。
- Benefit / Failure / Counterexampleの具体性。
- 文書authorityの分離。
- 自然な日本語としての可読性と文脈の豊かさ。
- Brand metaphorからRequirement / Universal ontologyへの不当な飛躍がないこと。
- Document Review Registry coverage。

```text
rich brand narrative
  != Product Value established

Product Value document updated
  != Product Value validated in actual use

symbolic coherence
  != Requirement necessity
```

## Natural Japanese review

本Issueは、ブランド世界の豊かさを失わず、同時にProduct Value文書として扱える精度へ落とすこと自体を重要な品質目標とする。

そのため、最初から短い箇条書きへ圧縮せず、背景と意味の連続性を十分に文章化した。特に、井を「知識を溜める容器」ではなく地表と深部をつなぐ境界装置として読むこと、中央の空白を全知のcoreではなく問いと可能性のための余白として読むこと、水を完成済みKnowledgeではなくCognitive Potentialとして扱うこと、静けさを早すぎる収束を強制しないProduct態度へ接続すること、四方向性を固定分類ではなくshared accessibilityとして読むことを、互いに独立した比喩ではなく一つのブランド世界として連続的に記述した。

同時に、これらをProduct Valueへ自動昇格させない停止線を明示した。Product Value、Value Model、Vision、Principles、Requirementのauthority差、既存V1〜V8 / Decision Continuityとの重複可能性、privacy / Access / Responsibilityとのtrade-off、SUI / TEIを特権化しない境界を確認している。

文書全体を、意味、要求強度、留保、Evidenceの高さを変えず、**自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とする。