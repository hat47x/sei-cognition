# ADR-0032: 製品ファミリーにおける「統合の頂点」としてのSEIと、制御の意味の境界を定める

Status: **Proposed**  
Related Issues: **ISSUE-000080, ISSUE-000081, ISSUE-000082, ISSUE-000083**  
Updated: 2026-09-27

## Context

### 何を判断する必要があるか

hat47xの製品ファミリーは、2026-09時点でSEI Cognition、SUI Sensemaking、TEI、EKI Fabric、Cultural Substrate Weaving（CSW）、Markdown Matrix Injector（MMI）、vs-bear-simulatorの7リポジトリになりました。各製品はそれぞれの領域で、提案と決定を分ける仕組みを独自に実装しています。SUIの承認イベント、TEIの共有受理境界、EKIの署名付きAuthority Decision、vs-bearの採否記録、MMIの権限面、CSWの帰属ラベルがその例です。

これまでの`product/value/SEI_PRODUCT_VALUE.md` §3.10と`product/vision/SEI_PRODUCT_VISION.md` §11は、SUI / TEI / EKIを「連携し得る隣接Product」とし、固定pipelineにしないこと、関連製品を特権化しないことを定めてきました。この境界は正しいものの、家族全体に対してSEIがどのような役割を担うのかは書かれていません。

本ADRでは、次の二つを判断します。

1. SEIを家族の「頂点」と呼ぶとき、どの意味を採り、どの意味を採らないか。
2. SEIの自己像が二つに割れている問題を、どう解くか。

### 自己像の分裂

Product文書は、SEIを耐久的な意味の台帳として描いています。`product/definition/SEI_PRODUCT_SHAPE.md` §8.3は、model router、classifier cascade、cost optimizer等の具体的なrouting mechanismをProduct / Profile / Provider-localに留めるとしています。

一方、`evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md` §1は、SEIを「認知資源の選択・配分・継続を担うCognitive Control Plane」として描き、attention / routing / escalationを中核に含めています。

どちらもEvaluation-onlyの仮説を含む文書ですが、家族の頂点という役割を加えると、「SEIは記録の層なのか、制御の層なのか」という読みの揺れが大きくなります。

### 基盤モデルの進歩

2026-09時点では、主要なAIベンダーが会話の記憶を製品機能として広げ、モデル選択や編成もプラットフォームの機能として提供されつつあります。文脈の圧縮、要約の生成、安価な想起、節約のためのルーティングといった、モデルの弱さを補う仕組みは、進歩とともに薄くなる可能性が高いと考えます。一方、誰が何を決め、何を任せ、何を未解決と認めたかという記録は、後から推論で復元できません。この差をProduct Valueの書き方へ反映する必要があります。

### Product Value / Requirement / 既存ADRとの関係

- V1〜V8の意味は変更しません。Decision Continuityも新しいValue Axisにはしません。
- REQ-0001〜REQ-0023、SCN-0001〜SCN-0019は変更しません。
- 5つのSemantic Contractはすべて`v1alpha1`のままです。version変更は行いません。
- ADR-0001（動く地平線）、ADR-0014（SEI / TEI Product Boundary）、ADR-0018（Product Valueの権威関係と評価境界）、ADR-0021（Architecture / Contractの権威関係と版管理）は維持します。本ADRはこれらを書き換えず、その上に家族全体での役割を加えます。
- ADR-0018 §7により、Product Valueの意味に関わる書き方の変更は明示的な再基線化として扱います。

### 現在確認できているEvidence

判断の材料は、2026-09-27に行った価値と境界の評価です。その記録は`product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md`にあります。

この評価には重要な前提があります。SEIの既存のProduct文書は、趣旨と棲み分けだけを与えて生成AIが起草したものであり、人による価値評価はまだ行われていません。今回の評価も生成AIによるもので、製品の所有者によるレビューを受ける前の段階です。

したがって、本ADRを支えるのはDesign Evidenceだけです。

### 未確認事項

- 家族の統合の頂点という役割が、利用者や組織にとって実際に価値を持つか。
- 委任、注意の範囲、期待、消去と系譜の4つの空白が、既存Contractの組合せでは表せない独立した失敗を生むか。
- 兄弟製品の実在の記録をSEIの語で読むとき、意味の損失が起きるか。
- 社会の水準での有用性。現時点ではすべて仮説です。

### 本ADRで固定しないもの

- 新しいValue Axis、Universal型、Stable Requirement、Contract version。
- 家族共通のprotocol、schema、orchestration。
- 兄弟製品への義務や依存。
- 神経系の比喩から導いた型やfield。

## Decision

### 1. 「頂点」の三つの意味を採る

SEIを家族の頂点と呼ぶときは、次の三つの意味に限ります。

| 頂点の意味 | 内容 | 設計上の帰結 |
|---|---|---|
| 抽象の頂点 | Observation、Decision、Authority等、最も一般的な意味を持つ。各製品に固有の意味を、そこへ翻訳できる | 家族の判断の意味論の対応表を、SEIが参考文書として持つ。各製品の意味の正本は各製品に残る |
| 時間の頂点 | 家族の中で最も長く生きる記録を持つ。製品、モデル、組織より長く残る | Contractを安定させる経路、10年単位で読める書き出し形式、ハッシュ方式を更新できることを検討する |
| 統合の頂点（任意の合流） | 製品をまたいだ認知を、時間を通して再構成できる場所になる | 求心と遠心のプロファイルを候補として持つ。製品はSEIへ送ってもよいが、送らなくても成り立つ |

### 2. 指揮・所有・可用性の頂点は採らない

次の三つの意味は採りません。

- **指揮の頂点** — SEIから他の製品へ向かう信号は、すべて依頼です。受け取った製品が、自らの権限で判断します。SEIのRecommendationがTEIのAuthorizationになることはありません。
- **所有の頂点** — SEIが持つのは、参照とコミットメントと対応表だけです。他の製品の意味やデータの正本は持ちません。
- **可用性の頂点** — どの製品の局所ループも、SEIの稼働を必要としません。本ADRでは、この局所ループを神経系の比喩にならって「反射弓」と呼びます。

```text
SEI = 抽象の頂点 + 時間の頂点 + 統合の頂点（任意の合流）
SEI != 指揮の頂点 / 所有の頂点 / 可用性の頂点
```

既存の原則はすべて維持します。SEIはcentral AI brainではありません。`SUI -> SEI -> TEI -> EKI`のような固定pipelineやstackでもありません。関連製品に優先度、信頼、Authorityを与えません（`product/principles/SEI_PRODUCT_PRINCIPLES.md` §22）。

「神経系の頂点」という言い方は、内部の設計言語に留めます。ブランド表現では、巨大なAI brainやcommand centerを視覚の中心に置かない方針（`product/vision/SEI_BRAND_WORLD_SOURCE.md` §7）を維持します。

### 3. 制御の仕組みはRealizationとし、制御の判断の意味をCoreに残す

自己像の分裂は、次の規則で解きます。

**routing、escalation、attentionの配分、cascade等の制御の仕組みは、交換可能なRealizationまたはProfileとします。一方、制御の判断の意味——何を見て、何を意図的に見送り、どのMethodやProviderをなぜ選び、何を保留し、何を上位へ回したか——は、Coreに記録すべき意味として扱います。**

```text
control mechanism
  = Realization / Profile（交換可能）

meaning of a control decision
  = Coreに残す意味

router choice != semantic confidence
```

`EMERGENT_COGNITIVE_ARCHITECTURE.md`のCognitive Control Planeは、この規則のもとで、交換可能なRealizationの集まりとして読みます。そこで行われた選択は、意味としてCoreへ残ります。

「Coreに残す」とは、新しいUniversal型を直ちに追加することではありません。まず、既存のDecision Memory、Cognitive Method Application、Capability Choiceの組合せで表せるかを試します。とくに「何を意図的に見送ったか」という注意の範囲は、現在の契約で受け皿が明確でないため、ISSUE-000081で検証します。

### 4. 家族の意味論の対応表を、SEIが持つ参考文書とする

`product/definition/SEI_FAMILY_SEMANTIC_MAP.md`を、家族の判断の意味論、証拠段階の翻訳、求心・遠心プロファイルの候補をまとめた参考文書として置きます。

この対応表は次の性質を持ちます。

- SEIは翻訳しますが、統合はしません。
- 各製品は、自らの意味、要求、非目標について引き続き正本です。
- どの製品にも必須の依存を作りません。関係が深いことは、依存の理由になりません。
- 各製品との対応は、すべて候補です。Contractでも共通protocolでもありません。

```text
translation != unification
product affinity != required dependency
mapping candidate != agreed contract
```

### 5. 価値の中心を「判断と認識のコミットメント」の台帳として言い直すことを提案する

Product Valueの中心を、次の一文で言い直すことを提案します。

> SEIは、人とAIと組織が交わす「判断と認識のコミットメント」を、手段が入れ替わっても失われない形で記録し、そこから判断の続きを始められるようにする。

コミットメントには、決定、委任、未解決の受容、根拠の束縛、期待、見直しの約束、注意の範囲が含まれます。このうち決定、未解決の受容、根拠の束縛、見直しの約束は現在の契約で扱えます。委任、期待、注意の範囲、そして消去と系譜の両立は、ISSUE-000081で既存契約の組合せを試します。

この言い直しは新しいValue Axisではありません。V1〜V8の意味も変えません。既存の中心を、人と組織が互いに何を約束したかという観点から読み直すものです。

価値の一言の約束（`product/value/SEI_VALUE_PROPOSITION.md` §2）には、「AIにどこまで任せたかを、あとから自分たちの言葉で確かめられる。」を加えることを提案します。既存の約束は変更しません。

### 6. 基盤モデルの進歩に対する頑健さを台帳で扱う

各仕組みに、制度・容量・経済物理のどれに由来するかという正当化の札を付け、縮小する条件を先に書く台帳を、ISSUE-000083で維持します。新しい世代の基盤モデルが出たときの再評価は、ADR-0001の「動く地平線」を実際に動かすきっかけとして扱います。その記録では`historical PASS != current PASS`を守ります。

### 7. ADR-0018に基づく再基線化として扱う

本ADRはProduct Value、Vision、Shape、Value Propositionの書き方に影響するため、ADR-0018 §7の手続きに従います。

#### 変更理由と反証の状況

変更理由は、評価で見つかった次の弱みです。

- W1: 自己像が記録の層と制御の層に割れている。
- W2: 最初の実用スライスの主な指標が、ベンダーの記憶機能に最も代替されやすい価値（一人で再開する速さ）に寄っている。
- W3: AIの自律化に向けて、委任、注意の範囲、期待、消去と系譜の受け皿が明確でない。
- W4: 最も長く生きるべき記録を扱うContractが、すべてpre-stableである。
- W5: 価値が「≠」による区別と否定で語られることが多く、利用者の仕事として肯定形で語る部分が少ない。
- W6: 社会の水準の価値が、Vision上の仮説としても書かれていない。
- W8: 家族の統合について、最小限の求心プロファイルもまだない。

既存のProduct Valueを反証するEvidenceは見つかっていません。今回の変更は、既存の主張を否定するものではなく、役割の明確化と言い直しです。ただし評価そのものが生成AIによるものであり、人による価値評価を経ていないため、すべて仮説として扱います。

#### 影響する文書

- Product: `SEI_PRODUCT_VALUE.md` §1 / §3.10 / §7、`SEI_PRODUCT_VISION.md` §4 / §11、`SEI_PRODUCT_SHAPE.md` §6 / §8.3 / §8.5、`SEI_VALUE_PROPOSITION.md` §2 / §6 / §7、`SEI_DECISION_CONTINUITY.md` §8、`SEI_VALUE_ACCEPTANCE.md`（V4）、`SEI_PRODUCT_PRINCIPLES.md` §18、`SEI_BRAND_WORLD_SOURCE.md` §17
- 新規の参考文書: `SEI_FAMILY_APEX_VALUE_REVIEW.md`、`SEI_FAMILY_SEMANTIC_MAP.md`、`contracts/EXTERNAL_STANDARD_MAPPING.md`
- Architecture / Contract: `architecture/SEI_REFERENCE_ARCHITECTURE.md`（提案節）、`contracts/CONTRACT_CATALOG.md`（提案節）
- Evaluation: `evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md` §1 / §7 / §16、`evaluation/cognitive-workspace-comparison/README.md` §2、`evaluation/distributed-execution-fabric/README.md`
- Plan: ISSUE-000073、ISSUE-000079、`plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
- Requirement / Scenario: 変更なし
- Contract version: 変更なし
- 既存ADR: Supersedeするものはありません

#### 過去の判断との互換性

- 過去のDecision、記録、Evidenceはそのまま有効です。data migrationは発生しません。
- V1〜V8、Decision Continuity、Evidenceの5段階の意味は変わりません。
- 「隣接Product」という位置づけは維持したうえで、家族に対する役割を具体化します。
- 兄弟製品には何の義務も生じません。SEIの対応表がなくても、各製品はこれまでどおり成り立ちます。
- 既存のEvidenceの高さは変わりません。

#### Revisit条件

下の「Revisit conditions」に示します。

## Alternatives considered

### A. SEIを家族の中央制御面にする

SEIが他の製品へ指示を出し、流れを通過させ、関門になる案です。

採りません。SEIが単一障害点になり、各製品の独立性を壊します。SEI自身の「central AI brainではない」という原則とも、各リポジトリが正本であるという境界とも矛盾します。さらに、routingや編成はプラットフォームの機能として代替されつつあるため、制御の仕組みに価値の中心を置くと、基盤モデルの進歩とともに価値が薄れます。SEIからの信号が命令になれば、TEIのAuthorityのような他製品の権限も侵します。

### B. SEIを単なる隣接製品の一つに留める

現状を維持する案です。

独立性を保つ点は優れているため、その部分は本ADRでも引き継ぎます。しかし、この案のままでは自己像の分裂（W1）と、家族統合の受け皿の欠如（W8）が残ります。各製品が独立に実装した提案と決定の分離を読み合わせる費用は、場当たり的に負担されることになります。また、家族で最も長く生きる記録を持つという時間の頂点の役割が、Contractの安定化の方針へ反映されません。

### C. 家族共通のUniversal ontologyやprotocolを先に標準化する

採りません。`SEI_PRODUCT_SHAPE.md` §8.5は、実際の統合の失敗から必要な境界だけを見つける方針を定めています。現時点で共通ontologyを作ると、各製品が正本であるという境界を弱め、失敗の観測より先に構造を固定することになります。

### D. 4つの空白を、直ちにUniversal型として追加する

採りません。ADR-0018 §6とProduct Principles §11に従い、既存の概念の組合せ、Reference、Profileで表せるかを先に確かめます。独立した失敗が観測されない限り、Universal型は増やしません。

## Consequences

### Positive

- 記録の層か制御の層かという自己像の揺れが解け、Product文書と評価文書を同じ規則で読めるようになる。
- 家族に対するSEIの役割を、特権や依存を作らずに説明できる。
- 基盤モデルが強くなるほど価値が上がる部分と、薄くなる部分を分けて説明できる。
- 利用者向けに、肯定形で価値を語る一文が加わる。
- Contractの安定化、再評価、プロバイダ離脱訓練を、頑健さの台帳として一か所で追える。

### Costs / Risks

- 参考文書と台帳が増え、兄弟製品が変わるたびに対応表の保守が必要になる。
- 「頂点」という言葉が、中央の頭脳や指揮系統として誤読されるおそれがある。採らない三つの意味を明示し、ブランド表現の方針を維持することで抑える。
- 対応表がContractや依存として誤読されるおそれがある。各行を候補と明記し、Contract化しないことを文書に書く。
- 社会の場面が、Evidenceとして誤読されるおそれがある。すべて仮説として扱う。
- 神経系の比喩が、型やfieldの根拠として使われるおそれがある。比喩由来の問いには印を付け、対象で確かめるまで要件にしない。

新しいCore要素は追加しません。家族の対応表と頑健さの台帳は参考資料であり、兄弟製品との統合の失敗が観測されず、どの製品もこの対応表を使わないことが続く場合は、縮小または廃止を検討します。

## Revisit conditions

次の場合に再検討します。

- 製品の所有者によるレビューで、統合の頂点という位置づけ、またはコミットメントの台帳という言い直しが退けられた。
- ISSUE-000081で、既存契約の組合せでは表せない独立した失敗が観測された。その場合はCandidate Requirementと新しいADRへ進む。
- ISSUE-000082で、兄弟製品の実在の記録を意味の損失なしに読めないことが分かった。あるいは損失がまったく起きず、対応表を保つ必要がないことが分かった。
- ある製品の局所ループが、SEIの稼働に依存していることが見つかった。
- 制御の仕組みを所有しなければ、制御の判断の意味を記録できないことが分かった。
- ベンダーの記憶機能や利用者所有の記憶の標準が、判断の根拠、来歴、提案と決定と権限の区別まで運ぶようになり、SEIとの差が縮んだ。
- ISSUE-000073のH1 / H2で、誤帰属やプロバイダ交換後の継続に改善が見られなかった。
- 新しい世代の基盤モデルでの再評価で、制度に由来するとした仕組みまで薄くなることが観測された。

## Evidence

本ADRを支えるのは**Design Evidence**だけです。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

- `product/value/SEI_FAMILY_APEX_VALUE_REVIEW.md` — 2026-09-27の評価記録
- `product/definition/SEI_FAMILY_SEMANTIC_MAP.md` — 家族の意味論の対応表（参考）
- `product/value/SEI_PRODUCT_VALUE.md`、`product/vision/SEI_PRODUCT_VISION.md`、`product/definition/SEI_PRODUCT_SHAPE.md`
- `evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md`
- 兄弟製品の文書（読み取りのみ）: `hat47x/sui-sensemaking:01_Plans/adr/ADR-0086-sensemaking-artifact-identity-provenance-authority-events.md`、`hat47x/tei-platform:docs/status.md`、`hat47x/eki-fabric:product/principles.md`、`hat47x/vs-bear-simulator:docs/M5_DECISION_GATE.md`、`hat47x/markdown-matrix-injector:01_Plans/adr/ADR-0018-cognitive-assistance-plane.md`、`hat47x/cultural-substrate-weaving:AGENTS.md`
- 外部の状況（2026-09時点。二次情報に基づく項目は「要確認」として扱う）: 評価記録の§10を参照

Executable、Release、Operational、Adoption / OutcomeのEvidenceは、本ADRから何も追加していません。

## Follow-up

- ISSUE-000080 — Product Value / Vision / Shape / Value Propositionの再基線化を、所有者が項目ごとに判断できる形にまとめる。
- ISSUE-000081 — 委任、注意の範囲、期待、消去と系譜の4つの空白を、既存契約の組合せで試す。
- ISSUE-000082 — TEIの受理記録とSUIの承認イベントという実在の記録から、家族の求心プロファイルを導く。
- ISSUE-000083 — 基盤モデルの進歩に対する頑健さの台帳を維持する。

本ADRの受け入れは、製品の所有者がブランチをmergeすることを関門とします。ADRがAcceptedになることと、後続Issueの検証が完了することは別です。

## Natural Japanese review

2026-09-27の評価記録、Product Value、Vision、Shape、Value Proposition、Product Principles、ADR-0001 / 0014 / 0018 / 0021、Emergent Cognitive Architecture、兄弟製品の該当文書を照合し、頂点の三つの意味と採らない三つの意味、制御の仕組みと制御の判断の意味の分離、家族の対応表の位置づけ、コミットメントの台帳という言い直し、頑健さの台帳をDecisionとして整理しました。

そのうえで、V1〜V8、Requirement、Contract versionを変えないこと、兄弟製品に依存や義務を作らないこと、すべてがDesign Evidenceに留まること、評価自体が人のレビュー前であることを固定し、自然な日本語となることを最重要視して全文を再ドラフトしました。英語の名詞を長く連ねた箇所は日本語の説明へ置き換え、式には本文の説明を添えています。最後に、Decision、採らない選択肢、Revisit条件、Evidenceの高さが再ドラフトの前後で変わっていないことを再監査しました。
