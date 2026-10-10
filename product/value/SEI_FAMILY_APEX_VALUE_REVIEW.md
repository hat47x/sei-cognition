# SEI Family Integration Apex — Product Value Review

更新日: 2026-09-27  
状態: **Product Value Review — Design only / proposed rebaseline via ADR-0035 / No new Value Axis established**

## 1. この文書の役割

この文書は、井（SEI Cognition）を、hat47xの製品ファミリーと将来の製品群を束ねる「統合の頂点」に置けるかを検討した評価の記録です。

Product Valueを改めて評価し、個人・組織・社会での有用性、基盤モデルの進歩に対する頑健さ、境界の設計を検討しました。そのうえで、仮説ごとに**何を既存の価値へ統合し、何をProduct hypothesisとして残し、何を設計言語に留めるか**を判断しています。

このReview自体は、新しいValue Axis、Universal型、Stable Requirementを定義しません。Contract versionも変えません。ここでの採否は提案であり、ADR-0035とISSUE-000085を通じて製品の所有者が判断します。

先に結論を示します。

- SEIの既存文書は、意味の区別、反証の可能性、証拠の段階づけの点で非常に堅い設計です。
- 一方で、SEIの自己像は「耐久的な意味の台帳」と「認知資源を配るCognitive Control Plane」に割れています。頂点に置くなら、まずこの分裂を解く必要があります。
- 解き方の提案は、**制御の仕組みは交換できるRealizationとし、制御の判断の意味だけをCoreに残す**ことです。
- 「頂点」には、抽象・時間・統合の三つの意味を採り、指揮・所有・可用性の三つの意味は採りません。この定義なら、SEI自身の「central AI brainではない」という原則と両立します。
- 価値の中心は、判断と認識の「コミットメント」の記録にあると言い直せます。これは宣言と記録によって成立する事実であり、後からどれほど賢いモデルが読んでも推論では復元できません。したがって基盤モデルが強くなるほど、この中心の価値は上がると考えます。

## 2. 評価の前提

この評価は、次の前提のもとで書いています。

- SEIの既存のProduct文書は、趣旨と他製品との棲み分けだけを与えて生成AIが起草したものです。**人による価値評価は、まだ行われていません。**
- 本書も生成AIによる評価です。製品の所有者がレビューし、採否を判断する前の段階にあります。
- 評価の材料は、`product/`、`contracts/`、`evaluation/`の主要文書の原文と、兄弟製品の文書（読み取りのみ）、2026-09時点の外部の状況です。
- 外部の事実は2026-09-27時点のものです。二次情報に基づく項目には「要確認」と書き、一次資料で確かめてから使う必要があります。

本書では、各記述の出所を次の四つに分けます。

| 区分 | 意味 |
|---|---|
| 明示 | リポジトリの文書に書かれている |
| 推論 | 文書の比較から導いた |
| 提案 | 本書からの提案 |
| 比喩由来 | 神経系の比喩から生じた問い。対象で確かめるまで、設計の根拠にしない |

## 3. 評価の方法

各仮説を、Brand World Review（`SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md`）と同じ順序で確認します。

```text
仮説
  ↓
利用者・組織にとってのbenefit
  ↓
欠けたときのfailure
  ↓
過剰に適用したときのcounterexample
  ↓
current V1〜V8 / Decision Continuityとの重複
  ↓
最も自然な文書配置
  ↓
現時点の判断
```

判断は次のいずれかとします。

- **Integrate** — 既存のValue / Vision / Shape / Principleの説明を深める（提案）。
- **Keep as Product hypothesis** — 独立した価値の可能性があるが、Evidenceが足りない。
- **Test by composition** — 新しい型を足す前に、既存契約の組合せで表せるかを試す。
- **Design language only** — 設計を考える語彙に留め、規範へ持ち込まない。
- **Reject** — 採らない。

## 4. 現状の評価 — 強み

| # | 強み | 根拠 |
|---|---|---|
| S1 | 意味の区別の体系（Observation ≠ Recommendation ≠ Decision ≠ Authority ≠ Execution、Unknown ≠ No、not_verified ≠ failed）が一貫している。家族の他の製品が、提案と決定の分離という同じ形へ独立に収束していることは、この区別の妥当性の傍証になる（推論） | `README.md` §1、`SEI_VALUE_MODEL.md` §5 |
| S2 | 反証の文化がある。自分が不要になる条件まで書いている（「Raw ContextでもUnknown / Conflict / Decision basisが同程度に保持されるなら、Workspaceを縮小する」）。こうした製品は珍しい | `evaluation/cognitive-workspace-comparison/README.md` §2、`SEI_DECISION_CONTINUITY.md` §8 |
| S3 | 評価時点から10〜50倍先を見る「動く地平線」と、code / prompt sheddingの原則がある。基盤モデルの進歩に対する基本姿勢は、すでに用意されている | `SEI_VALUE_MODEL.md` §9、`SEI_PRODUCT_PRINCIPLES.md` §16 / §18、ADR-0001 |
| S4 | 依存が少ない（Goの外部依存は`gowebpki/jcs`だけ）。v0.2.0はtag、source commit、package digestを照合してreleaseしている | `runtime/go/go.mod`、`release/v0.2.0/` |
| S5 | Capability ≠ Providerを守り、rule、classifier、SACS、SLM、LLM、人という異種の認知を最初から前提にしている | `SEI_PRODUCT_SHAPE.md` §3.3 |

## 5. 現状の評価 — 弱みとリスク

深刻度は、SEIを家族の頂点に置いたときの影響の大きさで付けています。

### W1 — 自己像が二つに割れている（深刻度: 高）

Product文書は「意味の台帳」を描き、routingはProfileやProviderの局所に留めるとしています（`SEI_PRODUCT_SHAPE.md` §8.3）。評価文書は「attention / routing / escalationを担うCognitive Control Plane」を描いています（`EMERGENT_COGNITIVE_ARCHITECTURE.md` §1）。頂点の役割は、どちらにも読めてしまいます。

対応: 制御の仕組みはRealization、制御の判断の意味はCoreとする（ADR-0035、提案）。

### W2 — 最初のスライスが、最も代替されやすい価値を主に測っている（深刻度: 高）

一人で再開する速さは、各ベンダーの記憶機能が伸びるほど差が縮みます。主な指標は、誤帰属、AI提案の誤った昇格、プロバイダ交換後の継続に置くべきです。E1〜E8とH2の設計にはこれらがすでに含まれていますが、人手レビューでの重みづけをはっきりさせたいところです。

対応: ISSUE-000073と`SEI_DECISION_CONTINUITY.md` §8で主指標と副次指標を分ける（提案）。

### W3 — AI自律化の時代に向けた4つの空白（深刻度: 中〜高）

委任（範囲・付与・撤回）、注意の範囲（何を見なかったか）、期待（正しければ何が起きるはずか）、消去と系譜の両立です。Value Proposition §4.3は「どこまでを誰に委ねたかを後から読める」と約束していますが、契約上の受け皿が明確ではありません。

対応: ISSUE-000086で、既存契約の組合せで表せるかを試す。

### W4 — 寿命と成熟度の差（深刻度: 中）

5つのSemantic Contractは、すべて`v1alpha1`です。家族で最も長く生きるべき記録が、最も長い互換性の約束を持っていません。

対応: `contracts/CONTRACT_CATALOG.md`に、安定化の経路を提案節として置く（ISSUE-000088）。

### W5 — 価値が「≠」で語られがち（深刻度: 中）

「一言でいう価値」は優れています。一方、本文の多くは区別と否定で書かれており、利用者の仕事として肯定形で語る部分が少なくなっています。

対応: Value Propositionの約束に肯定形の一文を加え、コミットメントの台帳という言い直しを置く（提案）。

### W6 — 社会の水準の価値が弱い（深刻度: 中）

Cognitive Commonsを独立したValue Axisにしなかった判断そのものは妥当です。ただし頂点に置くなら、少なくともVision上の仮説として社会像を持つべきです。現在のValue Propositionでは、社会の水準がほぼ空白です。

対応: Vision §4に社会像を仮説として書く。新しい軸にはしない。

### W7 — 証拠の仕組みが製品より重くなるリスク（深刻度: 中）

運用と利用成果のEvidenceはまだなく、H1 / H2の人手レビューは未実施です。検証の仕組みを増やすより、実際の人手レビューを一度通すほうが得られる情報は大きいと考えます。

対応: 本書の提案でも、新しい検証の仕組みは最小限に留め、H1 / H2の実施を優先する。

### W8 — 家族統合の標準が未成立（深刻度: 中）

`SEI_PRODUCT_SHAPE.md` §8.5は、実際の統合の失敗から必要な境界だけを見つけるとしています。方針は正しいのですが、頂点の役割には最小限の求心プロファイルが必要です。

対応: 参考の対応表を置き、実在の記録から求心プロファイルを導く（ISSUE-000087）。

### 名前についての注意

「神経系の頂点」は、内部の設計言語に留めるのがよいと考えます。ブランド文書は、巨大なAI brain、command center、全知の目を視覚の中心に置かない方針です（`../vision/SEI_BRAND_WORLD_SOURCE.md` §7）。（推論）

## 6. 「頂点」の定義

「頂点」という言葉は、少なくとも6つの意味に読めます。採る意味と採らない意味を分けると、SEIの既存原則を壊さずに家族の頂点へ置けます。（提案）

| 頂点の意味 | 採否 | 理由 | 設計上の帰結 |
|---|---|---|---|
| 抽象の頂点 | 採る | Observation、Decision、Authority等、最も一般的な意味を持つ。各製品に固有の意味を、そこへ翻訳できる | 家族の判断の意味論の対応表をSEIが持つ。各製品の意味の正本は各製品に残る |
| 時間の頂点 | 採る | 家族の中で最も長く生きる記録を持つ。製品、モデル、組織より長く残る | Contractを安定させる経路、10年単位で読める書き出し形式、ハッシュ方式を更新できること |
| 統合の頂点 | 採る（任意の合流） | 製品をまたいだ認知を、時間を通して再構成できる唯一の場所になる | 求心と遠心のプロファイル。製品は送ってもよいが、送らなくても成り立つ |
| 指揮の頂点 | 採らない | 他の製品へ命令し、流れを通過させ、関門になる。単一障害点になり、各製品の独立性と「central brainではない」という原則を壊す | SEIからの遠心の信号は、すべて依頼とする。受け取った製品が自らの権限で判断する |
| 所有の頂点 | 採らない | 他の製品の意味やデータの正本を持つ。「各リポジトリが正本」という既存の境界と矛盾する | SEIが持つのは、参照とコミットメントと対応表だけにする |
| 可用性の頂点 | 採らない | SEIが止まると家族が止まる。反射弓の原則に反する | どの製品の局所ループも、SEIの稼働を必要としない |

```text
SEI = 抽象の頂点 + 時間の頂点 + 統合の頂点
SEI != 指揮の頂点 / 所有の頂点 / 可用性の頂点
```

### 既存文書との調整

Vision §4 / §9の「中央の頭脳ではない」と、Vision §11 / Shape §6の「固定pipelineではない」は、どちらも維持します。変わるのは、SEIが家族に対して持つ役割の書き方です。「連携し得る隣接Productの一つ」から、「翻訳と記憶を担う統合の層」へ一段はっきりさせます。

関連製品を優遇しない原則（Principles §22）も維持します。対応表と求心プロファイルは公開された参考資料であり、特定の製品に権限を与えるものではないからです。（提案）

## 7. 神経系モデル（比喩）

製品の所有者から示された「神経系の頂点」という見方を、比喩として使います。

比喩から出た問いには**比喩由来**と印を付け、SEIの既存文書が裏づける対応と分けます。この扱いは、SEIのブランド文書の停止線（`../vision/SEI_BRAND_WORLD_SOURCE.md` §17「比喩から型やfieldを直接作らない」）と、CSWの帰属の規律に従っています。CSWでは、体系から生成された候補（`framework_generated`）と、対象で支持されたもの（`target_supported`）を区別します（`hat47x/cultural-substrate-weaving:AGENTS.md`）。神経系モデルから出た問いは、すべて前者として扱います。

### 7.1 全体の形

```text
井 SEI — 統合・記憶・抑制・メタ認知
  判断と認識のコミットメントの台帳
  （決定・委任・未解決・根拠・期待・見直し・注意の範囲）
  制御の仕組みはRealizationとして交換可能。制御の判断の意味だけを持つ

求心（感覚）— 製品からSEIへ
  SUI: 未整理な材料の知覚 / 承認イベント
  MMI: 表の正本の観測 / Source Identity Contract v1による出所のdigest
  vs-bear: 身体化された体験 / 採否記録・Providerの試行
  CSW: 想像・代替の見方 / 帰属ラベル
  TEI（観測）: 実行後のObservation / 受理判断
  EKI（内受容）: 資源・電力・利用者の在席 / 署名付きAuthority Decision

遠心（運動）— SEIから製品へ（依頼のみ）
  TEI（業務Action）: Action Intent → TEIが自らの権限で実行する
  EKI（計算配置）: 認知jobの意味 → workload contract。配置はEKIが決める
  SUI・CSW（問いの種）: 問いと材料を渡す。意味形成は各製品が行う
  外部AI・将来の製品: MCP・A2A経由の文脈提供。書き込みは提案として受ける

反射弓 — SEIを経由しない局所のループ（SEIが止まっても動く）
  SUI: LLMなし（SUI_LLM_PROVIDER=none）でも主な価値が動く
  EKI: 端末の局所governorが中央schedulerに優先する
  TEI: Driverと共有受理境界で単独に完結する
  vs-bear: 既定は決定論のcontroller。モデルは進路±0.18radの範囲だけ
```

求心・遠心の各経路は、SEIが製品へ義務を課すものではありません。すべて候補であり、詳しくは`../definition/SEI_FAMILY_SEMANTIC_MAP.md` §6〜§7に置きます。

### 7.2 機能の対応

| 神経系の機能 | 家族での担い手 | SEIでの実体 | 区分 |
|---|---|---|---|
| 外受容（感覚） | SUI（未整理な材料）、MMI（構造化された資料）、vs-bear（身体化された体験） | Observation、Method Application、Artifact Referenceとして受ける | 明示（Shape §6.1） |
| 内受容と恒常性 | EKI（計算資源、電力、利用者の在席） | 資源についてのCapability Observation | 比喩由来 — 注意の配分に内受容の信号を使うか |
| 想像・代替案の生成 | CSW（体系から出た候補）、背景認知 | 出所つきのHypothesis、Proposal Pool | 比喩由来 |
| 運動（遠心） | TEI（業務Action）、EKI（計算配置） | Action Intent（実行命令ではない） | 明示（Vision §11） |
| 反射弓 | 各製品の局所ループ | 関与しない | 明示（EKI principles、SUIのLLMなし動作） |
| 海馬（時間の索引つき記憶） | — | Decision Memory、Exact Binding、Revision lineage | 明示。記憶の索引理論（Teyler & DiScenna 1986）との対応 |
| 作業記憶・グローバルワークスペース | — | Cognitive Workspace（評価仮説） | 明示（EMERGENT §3） |
| 葛藤の監視 | — | Conflictの保持、Cognitive Challenge Path | 明示（EMERGENT §16）。葛藤監視の理論（Botvinick ほか 2001）との対応 |
| 抑制制御（行動の前に止まる） | — | Recommendation ≠ Decision ≠ Execution | 明示 |
| メタ認知（知らないことを知る） | — | Unknown ≠ No、unresolved refs | 明示 |
| 予測と予測誤差 | TEI・EKIからの実行結果 | reopen condition（一部） | 比喩由来 — 判断のときに「正しければ起きるはずのこと」を残し、外れた観測で見直しを起こすか |
| 神経修飾（予期された不確実性と予期しない不確実性） | — | Unknownと、Conflict・novelty | 比喩由来 — 二つを別の注意信号として扱うか（Yu & Dayan 2005）。前者は予定された再訪へ、後者はChallenge Pathへ |
| 相補的学習系（速いエピソードと遅い意味） | EKIの夜間の背景計算 | DecisionとPattern / Cognitive Methodの区別、背景認知 | 比喩由来 — エピソードからパターンを抽出するとき、エピソードを書き換えない（McClelland ほか 1995） |
| 血液脳関門 | — | Locality-first、device can compute ≠ device may see all data | 明示（EMERGENT §12） |

### 7.3 判断

**Design language only。** 神経系モデルは、設計を考える語彙と非規範のsourceに留めます。比喩由来の問いは、`EMERGENT_COGNITIVE_ARCHITECTURE.md` §7 / §16に評価仮説として置き、対象で確かめるまで要件にしません。

## 8. 病理から見た失敗の型

神経系の病理は、頂点が陥りやすい失敗の型を考える手がかりになります。多くはSEIの既存の失敗パターン（`SEI_VALUE_MODEL.md` §7）と重なります。新しく見えてくるのは、「分離脳」「発作」「委任外の動作」です。

| 病理 | 設計上の失敗 | SEIでの対応 | 状態 |
|---|---|---|---|
| 作話 | AIの流暢な要約が、当時の根拠に混ざる | V1・V3、post-decision information ≠ historical basis | 既存 |
| 病態失認 | 欠けているものに気づかない（Unknownの消去） | V5 | 既存 |
| 後知恵 | 判断後の情報で、当時を読み替える | V3 | 既存 |
| 保続 | 見直し条件がなく、古い判断が惰性で続く | reopen condition（REQ-0014） | 既存。期待の記録で強められる可能性がある |
| 他人の手徴候 | 決定のない実行、委任の範囲外の実行 | Decision ≠ Execution | 一部。委任の記録が空白（ISSUE-000086） |
| 分離脳 | 製品ごとに認識が食い違い、統合されない | 求心プロファイル、判断の意味論の対応表 | 新規。ISSUE-000087で観測する |
| 発作 | 通知と提案の嵐が注意を奪う | Quiet Infrastructure、attentionを一級の資源として扱う | 仮説。観測が必要 |
| 自己免疫 | 統制が正当な信号まで拒む（過剰な関門） | Progressive Explicitness | 既存。観測が必要 |

判断: **Keep as failure hypothesis。** 分離脳と発作は、観測されるまで失敗の仮説として保持します。

## 9. プロダクト価値の再定式化

現行の価値文書を置き換えるのではなく、その中心を一文で言い直し、層に分けて示します。（提案）

> SEIは、人とAIと組織が交わす「判断と認識のコミットメント」を、手段が入れ替わっても失われない形で記録し、そこから判断の続きを始められるようにする。

### 9.1 コミットメントの種類

| コミットメント | 意味 | 現行の契約 |
|---|---|---|
| 決定 | 何を決めたか | `sei.decision-memory`（既存） |
| 委任 | 誰に、どの範囲で、いつまで判断を任せたか。いつ撤回したか | 空白。Responsibility・Authority evidence refの組合せで表せるかを試す |
| 未解決の受容 | 何を分からないまま受け入れて進んだか | unresolved refs（既存） |
| 根拠の束縛 | 何を、どの版で根拠にしたか | Exact Binding（既存） |
| 期待 | 判断が正しければ、何が観測されるはずか | 空白。reopen conditionの一部として試す |
| 見直しの約束 | 何が起きたら開き直すか | reopen condition（既存） |
| 注意の範囲 | 何を見て、何を意図的に見送ったか。誰が、どの手段で絞り込んだか | 空白。Cognitive Envelopeの選択記録を広げられるかを試す |

これに加えて、**消去と系譜の両立**（プライバシーのための削除と、履歴の保持）も受け皿が明確ではありません。4つの空白はISSUE-000086で扱います。

### 9.2 なぜ、モデルが強くなるほど価値が上がるのか

権限や決定は、「XはCにおいてYとみなす」という宣言と記録によって成り立つ制度的な事実です（Searle 1995）。自然界の事実とは違い、観察からは推論できません。

当時の認識も同じです。判断の後に情報が増えると、人は当時から知っていたように感じます（後知恵バイアス、Fischhoff 1975）。モデルも、時刻の索引がない資料からは、当時の認識を確実には切り分けられません。

したがって、その時点で記録されなかったコミットメントは、未来のどんなモデルにも復元できません。モデルが強くなり、AIが決める範囲が広がるほど、「誰が、何を、どの権限で決め、何を任せたか」の記録は重くなります。（推論）

### 9.3 価値の4層

| 層 | 内容 | モデルの進歩に対して | 持ち方 |
|---|---|---|---|
| 核 | コミットメントの台帳（Semantic Contract） | ↑ 増す | SEIが正本として持つ |
| 継続 | 再開と引継ぎ（Resume projection、Decision Continuity） | → 形は変わり、価値は残る | 要約の生成はProviderへ任せる。要約で何を混ぜてはいけないかはSEIが持つ |
| 統合 | 家族と外部製品の翻訳（求心・遠心プロファイル、対応表） | ↑ 製品が増えるほど増す | 対応表はSEIが持つ。変換は各製品の側で行ってもよい |
| 制御 | 注意、ルーティング、昇格（Cognitive Control Plane） | ↓ 仕組みは薄くなる | 仕組みはRealizationにする。制御の判断は核へ記録する |

### 9.4 一言の約束への追加

`SEI_VALUE_PROPOSITION.md` §2の約束に、次の一文を加えることを提案します。

> AIにどこまで任せたかを、あとから自分たちの言葉で確かめられる。

### 9.5 判断

**Integrate（提案）。** コミットメントの台帳は、Product Valueの表現として統合します。新しいValue AxisやUniversal型にはせず、V1〜V8の意味も変えません。

## 10. 基盤モデルの進歩に対する頑健さ

### 10.1 進歩の駆動力（2026-09時点）

| # | 駆動力 | いま観測されていること | SEIへの含意 |
|---|---|---|---|
| D1 | 文脈長の拡大 | 主要なモデルは約100万tokenで横ばい。それ以上の長さでの実効品質には議論がある | 生の履歴を読み直すコストは下がる。Workspaceを「容量のため」に正当化する理由は弱まるが、「権限と開示範囲のため」の理由は残る |
| D2 | ベンダー内蔵の記憶 | ChatGPTは過去の会話を背景で要約する記憶へ移行した（2026-06）。Claudeは記憶を全プランへ広げ、コピー＆ペーストによる取り込みと書き出しを用意した。Geminiは他社の記憶とチャット履歴の取り込みを追加した（2026-03、要確認） | 一人で再開する速さは、基盤側の機能になっていく。移行はテキストの写しであり、判断の根拠や来歴は運ばれない。SEIは「記憶」ではなく「判断の記録簿」として立つべき |
| D3 | 利用者所有の記憶の標準化 | Open Memory Protocolのv0.2草案は「過去の決定」と来歴の制御を含む。MacPawのPortable Memoryは削除の墓標を持つ | 最も近い競合であり、補完でもある。SEIの契約との対応を早めに公開し、書き出し先・取り込み元として扱う |
| D4 | 長時間・多主体の自律エージェント | MCPとA2AはLinux Foundation傘下のAgentic AI Foundationへ移った。MCPの2026-07-28版はTasksとExtensionsを持つ | 委任の記録と、エージェント間の依頼の記録が中心になる |
| D5 | 推論と自己検証の向上 | モデルが自分の不確実性を語れるようになってきている | モデルの不確実性の推定と、組織が「受け入れた未知」は別物。後者は推定ではなく約束である |
| D6 | ルーティングと編成の基盤化 | モデル選択や編成が、プラットフォームの機能として提供されていく | 制御層の仕組みは代替される。何を選び何を見送ったかという判断の記録は残る |
| D7 | 規制と監督の要請 | EU AI Act 12条（ログ）・14条（人による監督）・26条（導入者の義務）、ISO/IEC 42001 A.6.2.8（イベントログ）、日本のAI事業者ガイドライン第1.2版（2026-03-31）はエージェントについて権限設定、人間の判断の介在、操作履歴の定期確認を挙げる | 制度に由来する核への需要が増える。ただしSEIは適合を保証しない。高リスク義務の適用は2027-12-02へ延期されたとの情報がある（要確認） |
| D8 | モデルの世代交代と挙動の変化 | 主要なベンダーが数か月単位で世代を更新している | 当時どのモデルが何を出したかを束縛すること（V1）が重くなる |
| D9 | 合成コンテンツの増加 | C2PA 2.4がAI開示のassertionを追加した（2026-04） | Observationの出所の区分（人の観察、AIの生成、AIの要約）が重要になる |
| D10 | 説得力の高いAIと自動化バイアス | EU AI Act 14条4項(b)と、日本のガイドライン第1.2版が自動化バイアスを明示している | 提案と決定の分離に加えて、承認に実質があったかを測る必要がある |
| D11 | 端末上の小型モデル | ローカルで動く小型モデルが実用域に入っている | 局所で処理する方針（Locality-first）は実現しやすくなる。プライバシーと法に由来する理由は残る |

規制への言及は、需要を説明するためのものです。SEIが規制への適合を判定したり保証したりすることはありません。

### 10.2 仕組みごとの正当化と、進歩に対する向き

各仕組みを、なぜ必要なのかという正当化の種類で分けました。**制度**は権限、責任、時間、複数の主体に由来し、モデルが強くなっても残るか、強まります。**容量**はモデルの弱さを補うためのもので、薄くなります。**経済・物理**はコスト、電力、通信、プライバシーに由来し、一部は残ります。（推論）

| 仕組み | 正当化 | 向き | 扱い |
|---|---|---|---|
| Recommendation ≠ Decision ≠ Authority | 制度 | ↑ | 核 |
| 当時の根拠とExact Binding | 制度 | ↑ | 核 |
| UnknownとConflictの保持 | 制度（受け入れた未知は約束） | ↑ | 核 |
| Revisionの完全性（V3） | 制度 | ↑ | 核 |
| Providerからの独立（V4） | 制度・経済（供給の集中への備え） | ↑ | 核 |
| 限定された共有とSelective Disclosure | 制度・法 | ↑ | 核 |
| Progressive Explicitness | 人の注意は有限 | ↑ | 核の運用原則 |
| Cognitive Workspace（文脈の絞り込み） | 容量 → 開示範囲へ移す | → | 正当化を「何を見せてよいか」へ移す |
| 人とAIが読めること（V6） | AIの側は容量、人の側は制度 | → | AI向けの工夫は薄くし、人向けの読みやすさは残す |
| Locality-first、常時の軽量認知 | 経済・物理・法 | → | Profile・Realization |
| Resume projectionの生成 | 容量・利便 | ↓ | 生成はProviderへ任せる。混ぜてはいけないものの規則はSEIに残す |
| SACS（安価な想起） | 経済 | ↓ | Realization |
| コスト最適化のルーティング | 経済 | ↓ | Realization。選択の判断は核へ記録する |
| 型付きの閉選択（小型モデルの信頼性のため） | 容量 | ↓ | Realization |

### 10.3 頑健さを保つ7つの仕組み

- **R1 正当化の札と「脱皮台帳」** — 各仕組みに制度・容量・経済物理の札を付け、縮小する条件を先に書く。cognitive-workspace-comparisonの「Raw Contextでも同程度なら縮小する」を、仕組み全体へ広げる。
- **R2 モデルの世代ごとの再評価** — 新しい世代の基盤モデルが出たら、比較評価とE1〜E8を再実行し、`historical PASS != current PASS`として記録する。「動く地平線」（ADR-0001）を実際に動かすきっかけになる。
- **R3 核をコミットメントに絞る** — Universal Coreはコミットメントと参照だけにし、それ以外は投影、Profile、Realizationへ置く。
- **R4 承認の実質を測る** — 提案から決定までの時間、修正の有無、却下率などを、形だけの承認を見つける観測として持つ。自動化バイアスへの注意（EU AI Act 14条4項(b)）の裏づけにもなる。
- **R5 プロバイダ離脱訓練** — 主なLLMや記憶の提供元を定期的に切り替え、失われた意味を数える。V4のOperational Evidenceの候補になり、供給の集中への備えにもなる。
- **R6 出所の区分** — Observationの出所を、人の観察、センサー、AIの生成、AIの要約、外部資料（C2PAのmanifestがあればその参照）に分ける。
- **R7 長く読めることと暗号の更新** — JSON、JCS、人向けの投影で書き出せるようにする。ハッシュのProfileに版を持たせ、古い束縛を再検証した記録を残す。

### 10.4 観測された事例 — 外部リポジトリの履歴の書き換え

時間の頂点とR7に関わる事例が、すでに一つ観測されています。

ISSUE-000058（E3a）では、CSWの日本語版`weave` Skillを、commit `aa3651f3460a6db7dc70bd848f93b600f149ffe8`、path `plugins/cultural-substrate-weaving-ja/skills/weave/SKILL.md`、Git blob SHA-1 `4d1cd77a3561c4da58bc030936f28ae2386a81ce`で固定し、検証済みのbytesにはSHA-256も記録しました。

CSW側の報告では、2026-09-24頃にCSWが履歴を書き換え（`backup-before-author-rewrite-20260924`というtagが残されています）、このcommitはどのrefからも到達できなくなりました。一方、固定したblobはCSWの履歴に残っており、`af7aa55`で追加された形で見つかります。2026-09-27に手元のCSWのcloneでも、commitが存在せず、blobが`af7aa55`の履歴に残っていることを確かめました（読み取りのみ）。

つまり、**commitの識別子による束縛は切れた一方、内容（blob）による束縛は生き残りました。** SEIのE3aの記録は、commitだけでなくblobの識別子とSHA-256を保持していたため、設計としては持ちこたえています。これはSEIのContractの失敗ではなく、Design上の観測です。

この事例から、次を確認できます。

- 外部リポジトリへのExact Bindingは、commitやrevisionの識別子に**加えて**、内容のdigestを持つべきである。commitの識別子の代わりにするのではない。
- 過去の束縛は、定期的に再検証する必要がある。当時のPASSは現在のPASSではない（`historical PASS != current PASS`）。

この事例は、ISSUE-000088の頑健さの台帳に、観測された事例として記録します。記録済みのEvidenceのファイルそのものは変更しません。

判断: **Integrate as register（提案）。** R1〜R7はISSUE-000088の台帳として扱い、`SEI_PRODUCT_PRINCIPLES.md` §18、`evaluation/cognitive-workspace-comparison/README.md` §2、`SEI_VALUE_ACCEPTANCE.md`のV4、`contracts/CONTRACT_CATALOG.md`の提案節へ反映します。

## 11. 境界の設計

頂点が崩れやすいのは、外部の強い仕組みに意味を吸い取られるときと、自分が中心に膨らむときです。8つの境界で、SEIが持つものと相手に任せるものを分けました。（提案）

| # | 相手 | SEIが持つもの | 相手に任せるもの | 接続の仕方 |
|---|---|---|---|---|
| B1 | 基盤モデル | 出力の役割（RecommendationかHypothesisか）、どのモデルの出力かの束縛 | 推論、要約、生成 | Cognitive MethodのRealizationとして接続する。private chain-of-thoughtは保存しない（REQ-0015）。ベンダーが示す推論の要約はRationaleに近いが、根拠ではない |
| B2 | ベンダーの記憶 | 判断の記録簿（system of record） | 好み、事実、利便のためのキャッシュ | SEIからベンダーへは、撤回できる投影を渡す。ベンダーからSEIへは、出所つきのObservationとして受け、レビューを経る。Open Memory ProtocolとPortable Memoryには対応表を用意する |
| B3 | エージェントとプロトコル | 委任、依頼と結果の意味 | 通信、実行、監視 | MCPはCanonical Semantic Access Surfaceの実現の一つとし、読み取りと提案に限る。決定は明示された権限の経路で行う。A2Aのエージェント間の依頼は、委任の記録とMethod Applicationへ写す。OTel GenAIの規約（まだDevelopment段階）は取り込まず、trace IDをExecution receiptとして参照する。SEIの記録の作法はAgent Skillとして配れる |
| B4 | 兄弟製品 | 対応表、求心・遠心プロファイル | 各製品に固有の意味と権限 | 反射弓には入らない。他の製品の領域で権限を与えない |
| B5 | 規制と標準 | 記録と監督のEvidenceを出せる形 | 適合の判定、認証 | EU AI Act 12・14・26条、ISO/IEC 42001 A.6.2.8、日本のガイドラインの権限設定と操作履歴の確認に対応できる出力を持つ。W3C PROV-Oへ写す（`wasAttributedTo`、委任は`actedOnBehalfOf`） |
| B6 | 時間 | 家族で最も長い互換性の約束 | — | `sei.semantic-reference`と`sei.decision-memory`を最初にv1へ上げる経路を検討する。書き出し形式とハッシュの更新手順を持つ。過去のPASSを現在のPASSとして扱わない |
| B7 | SEI自身の自律性 | 背景認知の結果を提案として置く | — | SEIは自分に権限を与えない。背景の結果を信念、決定、通知へ自動で昇格させない（「井戸は共同体の代わりに考えない」） |
| B8 | プライバシーと消去 | 参照とコミットメント、消去の墓標 | 生データ（端末や元のシステムに留める） | 消去では内容を消し、存在と系譜を残す（redaction ≠ revision）。頂点が監視の拠点になることを、明示的に非目標とする |

外部の近い取り組みとして、Zep / Graphitiは「当時何が信じられていたか」を二つの時間軸を持つ知識グラフで扱います。Cloverpopは判断の記録を閉じたSaaSとして提供し、Foundation Capitalは「decision traces」を投資の論点にしています。どれも、推奨、決定、権限、実行を別々の一級の記録として型づけてはいません。SEIとの差はここにあると考えます。（推論）

判断: **Integrate as proposed architecture section。** B1〜B8は`architecture/SEI_REFERENCE_ARCHITECTURE.md`へ提案節として記録し、外部標準との対応は`contracts/EXTERNAL_STANDARD_MAPPING.md`に参考資料として置きます。

## 12. 個人・組織・社会での有用性（仮説）

具体的な場面と、SEIが引き受けること、家族の他の製品との協働、確かめるべき証拠を並べました。**すべて仮説であり、Evidenceはまだありません。** 社会の水準は、Vision上の仮説として扱います。家族の他の製品との協働も任意であり、依存ではありません。

| 水準 | 場面 | SEIが引き受けること | 家族の協働（任意） | 確かめるべき証拠 |
|---|---|---|---|---|
| 個人 | 数週間から数年続く判断（進路、住まい、学習、研究テーマ） | 当時の根拠と未解決を保ち、未来の自分が書き換えずに再開できる | SUI（材料の整理）、CSW（見方を開く） | 再開時の誤帰属。再開の速さは副次的な指標 |
| 個人 | AIベンダーを乗り換える | 思考の文脈を持ち運ぶ（個人の認知の主権） | — | 乗り換え訓練で失われた意味の数 |
| 個人 | 自分の判断の癖を知る | 期待と結果を並べ、判断の質と結果の質を分けて振り返る | — | 「結果論」を避けられた振り返りの事例 |
| 個人 | 個人のAIエージェントへの委任（予約、購買、調査） | 委任の範囲を記録し、範囲内の決定と範囲外の提案を読み分ける | TEI（業務Action） | 範囲外の実行を後から検出できたか |
| 個人 | 家族の長い判断（介護方針、相続の準備） | 限られた範囲で共有し、誰が何を決めたかを残す | SUI | 共有後の誤読、開示範囲の侵害がないか |
| 組織 | 異動、退職、委託先の交代 | 判断の根拠と未解決を、人から切り離して引き継ぐ | TEI（業務の意味） | 引継ぎ後の再調査時間、誤った前提での再判断 |
| 組織 | 判断の振り返り（ポストモーテム） | 当時の認識で判断を評価し、運と判断を分ける | MMI（数表を正本のまま根拠にする） | 後知恵の混入が減ったか |
| 組織 | AIエージェント運用の監督 | 提案、委任、決定、実行を分けた記録を、監督のEvidenceとして出せる | TEI（AI Business Actor）、EKI | 監督者が記録だけで委任の範囲を説明できたか |
| 組織 | モデルやベンダーの移行 | 過去の判断の意味を保ったまま手段を替える | EKI（実行場所の移行） | 移行後に過去の判断を読み直せたか（V4のOperational Evidence候補） |
| 組織 | 部門をまたぐ未解決の管理 | 認めた未知と見直し条件を横断して持つ | SUI | 見直し条件が実際に発火し、役立ったか |
| 組織 | 背景認知（夜間の反例探索、前提の陳腐化の検知） | 結果を提案として置き、信念や決定へ自動で昇格させない | EKI（遊休計算）、CSW | 提案の採用率と注意の負担 |
| 社会 | 行政・公共でのAI活用 | AIの提案と職員の決定、委任の範囲を区別して残し、住民へ説明できる | TEI（長く使われる公共システム） | 説明にかかった負担、開示と秘匿の両立 |
| 社会 | 研究の再現性 | 事前の期待と、否定的な結果・未解決を残す | CSW（Living Labの規律） | 事前登録と比べた記録の負担 |
| 社会 | 危機・災害時の判断 | 不確実なままの判断を、後から後知恵なしに検証できる | vs-bear（市民対応の文脈を体験で伝える） | 事後検証での誤帰属 |
| 社会 | 熟議と合意形成 | 少数意見と未解決を消さずに、合意を記録する | SUI | 少数意見が後の判断で参照されたか |
| 社会 | AI供給の集中に対する回復力 | 判断の文脈を特定のベンダーに閉じ込めない | EKI（公益のための計算） | 移行できることの実証 |
| 社会 | 世代をまたぐ判断（インフラの保全、長期計画） | 数十年後に「なぜその時そう決めたか」へ戻れる | TEI | 記録形式が長く読めること |

### 12.1 過剰に適用したときのcounterexample

- 社会的な意義を、Evidenceの代わりに使う。
- 公共や組織での利用を理由に、個人や部門のプライバシーを弱める。頂点が監視の拠点になる（B8で非目標とする）。
- 危機や高リスクの場面で、SEIの記録を安全上の指示や法的判断の代わりに見せる。vs-bearが「安全指導ではない」という規律を持つように、SEIも高リスク領域での表示に同じ慎重さが要る。
- 家族の協働の列を、製品間の必須の依存として読む。

### 12.2 判断

**Keep as Product hypothesis。** 個人の場面の一部は既存のDecision Continuityで検証できます。組織と社会の場面は、`SEI_VALUE_PROPOSITION.md` §6 / §7と`../vision/SEI_PRODUCT_VISION.md` §4へ仮説として加え、新しいValue Axisにはしません。

## 13. 家族の判断の意味論

家族の各製品は、それぞれの領域で提案と決定の分離を独立に実装しています。SEIはこれらを統合せず、翻訳します。

対応表、証拠段階の翻訳表、求心・遠心プロファイルの候補は、`../definition/SEI_FAMILY_SEMANTIC_MAP.md`に参考文書として置きました。各行の状態はすべて候補です。

証拠段階を並べてみると、7つの製品のどれにも、OperationalとAdoption / OutcomeのEvidenceがまだありません。これは家族全体に共通する空白です。

判断: **Integrate as informative map。** 実在の記録からの導出は、ISSUE-000087で行います。

## 14. 仮説ごとの採否

本Review時点の判断は次のとおりです。いずれも提案であり、製品の所有者のレビューを経て確定します。

```text
新Value Axis追加                        = No
V1〜V8変更                              = No
Universal型追加                         = No
Stable Requirement（REQ / SCN）追加      = No
Contract version変更                    = No
統合の頂点（三つを採り、三つを採らない）    = Product Vision / Shapeへ統合（提案、ADR-0035）
自己像の分裂（W1）                       = 制御の仕組みはRealization、制御の判断の意味はCore（提案、ADR-0035）
commitment ledger                       = Product Value表現として統合（提案）
一言の約束への追加文                      = Value Propositionへ追加（提案）
4つの空白                               = ISSUE-000086で組合せ試験
家族の意味論の対応表                      = 参考文書（SEI_FAMILY_SEMANTIC_MAP.md）。各行は候補
求心・遠心プロファイル                    = 候補として保持。ISSUE-000087で実在の記録から導出
neural model                            = 設計言語 / 非規範source
比喩由来の問い                            = 評価仮説（EMERGENT §7 / §16）。対象で確かめるまで要件にしない
分離脳・発作                             = failure hypothesis（観測が必要）
社会像                                   = Product Vision上の仮説
組織・社会の場面                          = Value Proposition上の仮説
頑健さの仕組みR1〜R7                      = ISSUE-000088で台帳化（提案）
境界B1〜B8                               = Reference Architectureの提案節
外部標準との対応                          = 参考資料（contracts/EXTERNAL_STANDARD_MAPPING.md）
Contractの安定化経路                     = Contract Catalogの提案節（version変更なし）
外部リポジトリへの束縛                     = commit等の識別子に加えて内容digestを持ち、定期的に再検証する（観測事例あり、ISSUE-000088）
H1 / H2の主指標                          = 誤帰属・誤った昇格・交換後の継続を主、再開の速さを副（提案）
プロバイダ離脱訓練                         = V4のOperational Evidence候補（未取得）
Change 2の再開条件（ISSUE-000079）         = 成立を記録。実行はまだ
```

## 15. 段階の見通し（提案）

SEIのMilestoneと同じく、期限を持たず、Evidenceで進む段階として考えます。各段階の最後に、次へ進むための関門を置きます。

| 段階 | 内容 | 関門 |
|---|---|---|
| Stage 0 — 定義する | 頂点の定義をVisionとShapeへ入れる。ADR-0035で自己像を統一する。対応表を参考文書として置く。Change 2の再開条件の成立を記録する | 既存の原則（central brainではない、固定pipelineではない、関連製品を優遇しない）と矛盾しないことを、レビューで確かめる |
| Stage 1 — 実在の記録から始める | TEIの受理記録とSUIの承認イベントを対応づける（ISSUE-000087）。H1 / H2人手レビューを一度通す | 対応づけで意味の損失が具体的に観測されるか、されないか。どちらも正当な結果として扱う |
| Stage 2 — 外へ開く | MCPの読み取り面を検討する（書き込みは提案だけ）。プロバイダ離脱訓練を行う。外部標準との対応を公開する | 離脱訓練で失われた意味の数と、その種類 |
| Stage 3 — 委任と期待を確かめる | TEIのAI Business Actorとvs-bearの限定権限を題材に、委任と期待を既存契約で表せるか試す（ISSUE-000086） | 既存契約では表せない独立の失敗が観測された場合に限り、Candidate Requirementへ進む |
| Stage 4 — 組織で共有する | チームやホスト型での利用、限定された共有、EKI上の背景認知 | 共有後の誤読、注意の負担、開示範囲の侵害 |
| Stage 5 — 社会で試す | 公共部門や研究の場での試行。判断の説明責任と、少数意見・未解決の保持を実地で確かめる | 第三者による利用成果のEvidence |

## 16. 採る方向と反対側の停止線

| 採る方向 | 反対側の停止線 |
|---|---|
| 家族の統合の頂点 | 指揮、所有、可用性の頂点にしない |
| 翻訳する対応表 | 家族共通のontologyや必須の依存にしない |
| 制御の判断を記録する | 制御の仕組みをSEIの正本にしない |
| コミットメントの台帳 | 4つの空白を、独立の失敗なしにUniversal型へしない |
| 神経系モデルで考える | 比喩から型やfieldを作らない。比喩由来の行は要件にしない |
| 規制の需要を踏まえる | 適合を保証しない |
| 社会での有用性を描く | 社会的な価値を証拠として扱わない |
| 長く読める記録 | 監視の拠点にならない。消去の求めに応えられる |

本書は正本ではありません。SEIの価値、要求、非目標の正本は、それぞれの文書にあります。兄弟製品についても、各リポジトリが正本です。

## 17. 反映先

本Reviewの提案は、次の文書へ反映しました。どれも未mergeブランチ上の提案です。

| ID | 反映先 | 内容 |
|---|---|---|
| SEI-1 | `SEI_PRODUCT_VALUE.md` §1 / §3.10 / §7 | コミットメントの台帳、モデルが強くなるほど価値が上がる理由、家族の統合の頂点 |
| SEI-2 / SEI-4 | `../vision/SEI_PRODUCT_VISION.md` §4 / §11、`../definition/SEI_PRODUCT_SHAPE.md` §6 / §8.3 / §8.5 | 社会像の仮説、統合の頂点、制御の意味の境界、参考の対応表 |
| SEI-3 | `SEI_VALUE_PROPOSITION.md` §2 / §6 / §7 | 約束への追加文、組織と社会の場面（仮説） |
| SEI-5 | ADR-0035、ISSUE-000085 | 再基線化 |
| SEI-6 | ISSUE-000086 | 4つの空白の組合せ試験 |
| SEI-7 | ISSUE-000087 | 実在の記録からの求心プロファイル |
| SEI-8 | ISSUE-000079 | Change 2の再開条件の成立 |
| SEI-9 | ISSUE-000073、`SEI_DECISION_CONTINUITY.md` §8 | 主指標と副次指標 |
| SEI-10 | `SEI_VALUE_ACCEPTANCE.md`（V4） | プロバイダ離脱訓練 |
| SEI-11 | `../../contracts/CONTRACT_CATALOG.md` | 安定化の経路（提案） |
| SEI-12 | `../../evaluation/cognitive-workspace-comparison/README.md` §2、`../principles/SEI_PRODUCT_PRINCIPLES.md` §18 | 脱皮台帳と正当化の札 |
| SEI-13 | `../../architecture/SEI_REFERENCE_ARCHITECTURE.md` | 境界B1〜B8（提案） |
| SEI-14 | `../../contracts/EXTERNAL_STANDARD_MAPPING.md` | 外部標準との対応（参考） |
| SEI-15 | `../../evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md` §7 / §16 | 予期された不確実性と予期しない不確実性、期待の記録（比喩由来の仮説） |
| SEI-16 | `../../evaluation/distributed-execution-fabric/README.md` | eki-fabricとの関係 |
| SEI-17 | `../definition/SEI_FAMILY_SEMANTIC_MAP.md` | 家族の意味論の対応表（参考） |
| SEI-18 | `../vision/SEI_BRAND_WORLD_SOURCE.md` §17 | 神経系の比喩にも同じ停止線を適用 |

## 18. Evidence状態

```text
Product Value review: Design review available（AI評価。人によるレビュー前）
Product Value / Vision / Shape / Proposition integration: proposed rebaseline（ADR-0035 Proposed）
Family semantic map: informative Design record / all sibling mappings are candidates
Executable Evidence: no new Evidence from this review
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

本Reviewは設計上の評価であり、これ自体がactual useでの価値成立を示すものではありません。社会の水準の記述はすべて仮説です。

## 19. 関連文書

- `SEI_PRODUCT_VALUE.md`
- `SEI_VALUE_MODEL.md`
- `SEI_VALUE_PROPOSITION.md`
- `SEI_VALUE_ACCEPTANCE.md`
- `SEI_DECISION_CONTINUITY.md`
- `SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md` — 本書の評価方法の手本
- `../vision/SEI_PRODUCT_VISION.md`
- `../vision/SEI_BRAND_WORLD_SOURCE.md`
- `../definition/SEI_PRODUCT_SHAPE.md`
- `../definition/SEI_FAMILY_SEMANTIC_MAP.md`
- `../principles/SEI_PRODUCT_PRINCIPLES.md`
- `../../architecture/SEI_REFERENCE_ARCHITECTURE.md`
- `../../contracts/CONTRACT_CATALOG.md`
- `../../contracts/EXTERNAL_STANDARD_MAPPING.md`
- `../../evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md`
- `../../plan/adr/ADR-0035-family-integration-apex-and-control-meaning-boundary.md`
- `../../plan/issue/ISSUE-000085-rebaseline-family-integration-apex.md`
- `../../plan/issue/ISSUE-000086-test-commitment-gaps-by-composition.md`
- `../../plan/issue/ISSUE-000087-derive-family-afferent-profile-from-sibling-records.md`
- `../../plan/issue/ISSUE-000088-maintain-model-progress-robustness-register.md`

### 主な外部資料

- Searle, J. R. (1995). *The Construction of Social Reality*. Free Press.
- Fischhoff, B. (1975). Hindsight ≠ foresight. *Journal of Experimental Psychology: Human Perception and Performance*, 1(3). DOI: `10.1037/0096-1523.1.3.288`.
- Teyler, T. J., & DiScenna, P. (1986). The hippocampal memory indexing theory. *Behavioral Neuroscience*, 100(2). DOI: `10.1037/0735-7044.100.2.147`.
- Botvinick, M. M., et al. (2001). Conflict monitoring and cognitive control. *Psychological Review*, 108(3). DOI: `10.1037/0033-295X.108.3.624`.
- Yu, A. J., & Dayan, P. (2005). Uncertainty, neuromodulation, and attention. *Neuron*, 46(4). DOI: `10.1016/j.neuron.2005.04.026`.
- McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. *Psychological Review*, 102(3). DOI: `10.1037/0033-295X.102.3.419`.
- W3C PROV-O: `https://www.w3.org/TR/prov-o/`
- Open Memory Protocol: `https://github.com/The-AI-Disclosures-Project/Open-Memory-Protocol`
- C2PA 2.4: `https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html`
- EU AI Act 12・14・26条: `https://artificialintelligenceact.eu/article/12/`（13 / 14 / 26も同じ形式）
- AI事業者ガイドライン 第1.2版: `https://www.meti.go.jp/shingikai/mono_info_service/ai_shakai_jisso/pdf/20260331_1.pdf`

これらの研究や規制を、SEIのRequirementへ直接輸入しません。外部資料とSEIのProduct Evidenceを分け、必要な場合は一次資料で確かめてから使います。

## 20. Natural Japanese review

このReviewでは、統合の頂点という言葉の魅力ではなく、SEIの既存の原則と矛盾しないか、利用者と組織にとって独立した価値やfailureがあるかを確かめることを重視しました。

強みS1〜S5と弱みW1〜W8を根拠の文書とともに示し、頂点の六つの意味を採る三つと採らない三つに分けました。神経系モデルは、文書が裏づける対応と比喩由来の問いを表の中で分け、比喩由来の問いを要件にしない停止線を置いています。価値の再定式化、頑健さ、境界、有用性の場面は、いずれも提案または仮説として扱い、採否を一か所にまとめました。

内容、採否、未検証の範囲を固定した後、英語の名詞を連ねた表現を日本語の説明へ置き換え、表の各行が一文で読めるように整えました。そのうえで、**自然な日本語として背景から結論まで無理なく追えることを最重要視して全文を再ドラフトし、新しいValue AxisやRequirementを追加していないこと、Evidenceの高さがDesignに留まることが変わっていないことを最終監査しました。**
