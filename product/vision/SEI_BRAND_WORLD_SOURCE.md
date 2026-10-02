# SEI Cognition Brand World — Product Value Discovery Source

更新日: 2026-10-02  
状態: **Non-normative Product Value Discovery Source。§17の停止線への神経系の比喩の追加は、ADR-0032（Proposed）による提案**

## 1. この文書の役割

この文書は、SEI Cognitionの名称・象徴・Visual Identityを検討する過程で育ってきた「井」のブランド世界を、今後のProduct Value探索へ再利用できるだけの文脈を保って記録するための原資料です。

ここに書かれている比喩や象徴は、Product Value、Requirement、Architecture、Contractを直接決める規範ではありません。

SEIでは、ブランド上の象徴が豊かであることと、製品として守るべき価値が成立していることを分けます。

```text
Brand world
  = Product Valueを考えるための探索源
  != Product Value authority
  != Requirement authority
  != Universal ontology
```

一方で、ブランドを外見だけの装飾として扱うこともしません。名称や造形を深く考える過程では、実装や既存文書からはいったん距離を置くため、プロダクトの存在理由や利用者へ届けたい状態が別の角度から見えてくることがあります。

この文書の目的は、そのような洞察を短い広告コピーへ圧縮せず、後から人間や生成AIがProduct Valueを検討するときに、なぜその問いが生まれたのかまで辿れる形で残すことです。

## 2. SEI Cognitionという名前

SEI Cognitionの象徴には、易の井卦に由来する「井」を置きます。

ただし、卦をソフトウェアの仕様分類表として使用しません。卦は、SEIがソフトウェア群の中でどのような位置を占めるかを示唆する象徴層です。

利用者が製品を識別するときは`SEI Cognition`という完全修飾名を中心にし、「井」や`SEI`だけを覚えることを要求しません。

ブランドにおける「井」は、特定の宗教的・占術的解釈を利用者へ求めるものでもありません。むしろ、長い時間をかけて人間社会の中で形成されてきた「井戸」という具体的な物と、その構造から得られる直観を、プロダクトの位置づけを考える補助線として扱います。

## 3. 井は、知識を溜める箱ではない

井戸を単純に「水を蓄える容器」と捉えると、SEIはKnowledge StoreやData Lakeのような製品に見えます。

しかし、井戸の特徴は、水を所有することよりも、**地表から直接は触れられない水脈へ、共同体が繰り返しアクセスできる構造を設けること**にあります。

井そのものが水を生み出すわけではありません。水脈のすべてを地上へ持ち上げるわけでもありません。必要なときに近づき、深さを測り、汲み上げ、必要な量を使い、また戻ることができます。

この構造をSEI Cognitionへ重ねると、SEIは「すべてを知っている中央AI」ではなく、**まだ十分に表層化されていないものへ、人間やAIが安全に近づくための共有認知基盤**として捉えられます。

```text
すでに見えているもの
すでに言葉になっているもの
すでに整理された判断材料
          ↓
        「井」
────────────────────
まだ十分に形を得ていないもの
断片的な観察 / 違和感 / 記憶 / 未解決 / 関係候補
```

下側に「真実」や「正解」が完成済みで存在すると考えないことが重要です。

そこにあるのは、Observationになり得る断片、まだ検証されていないHypothesis、Unknown、Conflict、弱いsignal、未整理の経験、後から意味を持つかもしれない痕跡などです。

SEIが行うべきことは、それらを神秘的な深層知として権威化することではありません。扱える形で外在化された時点から、由来、不確実性、意味の違いを失わず、後から問い直せるようにすることです。

## 4. 表層と深層のあいだにあるGateway

ブランド世界では、井を**surface / depth boundary**として読みます。

表層は、現在の利用者や組織がすでに言葉・記録・判断対象として扱える領域です。

深層は、心理学上の無意識を厳密に意味するものではありません。ここではより広く、まだ十分に言語化されていないもの、組織の一部にしか見えていないもの、後から意味が現れるかもしれないもの、既存の分類にまだ収まっていないものを象徴します。

この境界は一方向ではありません。

上から下へは、問いを置き、調べ、観察し、深く見る動きがあります。

下から上へは、違和感、弱いsignal、新しい関係候補、忘れられていた記憶などが、扱える認知対象として立ち上がってくる動きがあります。

```text
Inquiry descends.
Possibility emerges.
```

ただし、SEIがprivate chain-of-thought、無意識的内容、言語化前の内部状態そのものを直接保持できると想定しません。

製品として扱えるのは、主体がObservation、Question、Hypothesis、Artifact、Method output等として外在化できるものからです。

したがって「深層」はデータモデル上の領域ではなく、**Product Valueを考えるための境界比喩**です。

## 5. 井桁の中央にある空白

井桁のアイコンは、二本の縦線と二本の横線から構成できます。

しかし、SEIのブランドで本当に重要なのは線だけではありません。四本の線が囲む**中央の空白**です。

通常の`#`では、線の交差そのものが記号として前面に出ます。

SEIでは逆に、線を中央の空間を成立させるInfrastructureとして読みます。

```text
線     = structure / support
中央   = aperture / access / possibility
```

この中央を、万能AI、central processor、single source of truthのような「答えが存在する中心」にしません。

むしろ、まだ答えのない問いを置くことができ、複数の主体が別の方向から近づき、必要であれば後から戻ってこられる**認知上の余白**として扱います。

これはSEIのProduct Valueに対し、一つの重要な問いを投げかけます。

SEIは、組織が早く答えを出すためのシステムなのか。それとも、必要なときには答えを出しつつ、まだ分からないものを分からないまま保持し、後から問い直せる場所を失わないためのInfrastructureでもあるのか。

現在のUnknown / Conflict preservationやRecommendation / Decision分離は、この問いと強く響き合います。

ただし、「余白を守る」ことをDecision回避や曖昧さの放置と同一視しません。必要なDecisionは、未解決事項を明示したうえで行える必要があります。

## 6. 水はKnowledgeよりCognitive Potentialに近い

ブランド上、水をKnowledgeの象徴とだけ捉えると、地下に完成済みの知識が蓄えられ、それを汲み上げれば正しい答えが得られるという印象になります。

SEIには、その理解は適しません。

水はむしろ、**Cognitive Potential**を象徴します。

そこには、情報、記憶、痕跡、弱いsignal、未解決の経験、まだ意味づけられていない関係、可能性が混ざっています。

汲み上げたものがObservationになることもあれば、Hypothesisとして保留されることもあります。別のEvidenceによって否定されることもあります。

SEIが価値を持つのは、その曖昧さを消してしまうからではなく、曖昧なものを必要な粒度で外在化し、後から別の主体やMethodが読み直せるようにするからではないか、というProduct hypothesisがここから生まれます。

## 7. 静けさ

SEI CognitionのVisual Identityでは、派手な発光、巨大なAI brain、command center、全知のeye、過剰なnetwork glowを中心に置かない方向を採ります。

井戸のように、普段は必要以上に目立たず、必要なときに近づけるものを目指します。

この静けさは、上品な見た目を作るためだけのaestheticではありません。

Product Valueへ読み替えると、次のような態度を示唆します。

- Unknownを早く`No`へ変えない。
- Conflictを最新値で消さない。
- AIが多数のRecommendationを生成できても、提示量そのものを価値としない。
- ObservationをTruthへ急いで昇格させない。
- 利用者のattentionを常時奪わない。
- 必要なときには深いdetailへ降りられるが、通常時には過剰な明示性を要求しない。
- 人間が自分で問い直す余地を、proactive AIの都合だけで埋めない。

したがって、ブランド上の「quiet」は「遅い」「消極的」という意味ではありません。

**早すぎる収束を強制せず、必要な認知差を保ったまま前へ進めること**を示唆します。

一方、静かさを強調しすぎて重要なwarningやreview conditionまで見えなくするなら、Productとして失敗です。

静けさとproactive assistanceの間にはtrade-offがあります。

## 8. 波紋

井戸の水面に生じる弱い波紋は、ブランド上の補助モチーフです。

波紋は、一つの問い、一つのObservation、一つのDecisionが、周辺の認識へどのような影響を与えるかを示唆します。

重要なのは、波紋を「中央から全組織へ命令が伝播する」図にしないことです。

SEIはcommand distribution systemではありません。

波紋は、ある認知上の変化が別の問いを生み、別の人やAIが後から気づき、必要に応じて見直しにつながるような、**静かな影響の伝播**を表します。

## 9. 四方向性

「井」の形には四方向性があります。

これをHuman / AI / Data / Methodのような固定四分類へ割り当てません。

四方向性は、**どこからでも近づけること**を示す象徴です。

人間、AI、Cognitive Method、Document、System、過去のHistoryなど、異質な主体や情報源が同じ認知基盤へ接続できます。

```text
Human ─────┐
AI ────────┤
Method ────┤
Document ──┼── SEI Cognition
System ────┤
History ───┘
```

この図でも、SEIを中央権力として読むべきではありません。

重要なのは、異なる入口から来ても、意味の違い、Responsibility、Provenance、Access boundaryを保ったまま共有可能な認知対象へ到達できることです。

## 10. Cognitive Commons

井戸は歴史的に、共同体が利用する生活Infrastructureでもありました。

この性格から、SEIを**Cognitive Commons**として捉える仮説が生まれます。

個人のworking memory、個人用chat、一つのAI session、一つのProvider内部に閉じていた認知成果を、適切な形で外在化し、別の主体が後から利用できる。

ただし、「commons」を無制限な公開と同一視しません。

SEIでは、共有可能性と同時に、Selective Disclosure、Responsibility、Authority、Product Access、Provenanceが重要です。

したがって目指すのは、

> everybody sees everything

ではなく、

> **cognition can become a durable shared asset without losing its boundaries**

という状態です。

共有されるのは「正解」だけではありません。

問い、Unknown、Conflict、Decision basis、reopen conditionなども、適切なboundaryのもとで共有資産になり得ます。

## 11. 人間とAIは井を利用する

SEIをAIそのものとして描かないことは重要です。

AI modelが変わっても、Providerが変わっても、担当者が変わっても、組織が問い直せる基盤が残ることを目指します。

AIは、井を利用する強力な主体の一つです。

人間も同様です。

Cognitive Methodも、Documentも、外部Systemも、井の中核そのものではありません。

この関係は、SEIをcentral AI brainとして設計する誘惑を抑えます。

SEIの価値は、最も賢いモデルを所有することではなく、**モデルが入れ替わっても認知上の意味・来歴・問い直し可能性を失いにくいこと**にある、という現在のProduct Valueと接続します。

## 12. 「共同体の代わりに考えない」

SEIのブランド世界を一文で表すとき、重要なのは次です。

> **The well does not think for the community. It gives the community a place from which deeper understanding can be drawn.**

井戸は共同体の代わりに考えません。

SEIも、人間や組織のAgencyを奪うことを目的にしません。

AIへDecision Authorityを委任できる場合であっても、その委任やResponsibilityの意味を読めることが必要です。

SEIは「人間が必ず最終承認するシステム」を固定するのではなく、**誰または何が考え、提案し、判断し、実行したのかを失わない共有基盤**であることを目指します。

## 13. 組織内の日常Infrastructureとしての井

公共性を表現するとき、井の周囲に人々が集まり、象徴を見上げるモニュメント的な構図はSEIには合いません。

井は崇拝される中心ではなく、生活の中で必要なときに使われるInfrastructureです。

人はその近くを通り、別の仕事をし、必要なときだけ立ち寄ります。

誰も利用していない時間にも、井は維持されています。

この日常性は、SEIのProduct Experienceにも重要な問いを与えます。

利用者が常時SEIへ入力し続け、常時AIから提案を受け、常時複雑なsemantic structureを意識しなければ価値が出ないなら、「静かなInfrastructure」とは言いにくい。

必要なときに自然に使え、後から戻れ、重要な場面だけ厳密さを増せることが、SEIらしい利用状態なのではないかという仮説につながります。

## 14. SEI / SUI / TEIの象徴的な位置関係

関連製品では、卦をソフトウェア群の位置づけを示唆する象徴として利用します。

現時点では、次のように読むことができます。

```text
井 / SEI Cognition
  depth / access / cognition

萃 / SUI Sensemaking
  gathering / relation / emergence

鼎 / TEI
  transformation / realization / execution
```

SUI Sensemakingでは、多数の親和図法キャンバスが生成され、キャンバス自身もより大局的なnetworkの中に位置づけられ、部分をdrill-downして別のcanvasへ深める可能性があります。B型文章化された成果同士は、一般的なtext / semantic analysisによって関連を発見しやすくなります。

このためSUIは、素材が集まり、関係が立ち上がり、局所的な意味形成と大局的なnetworkが往復する領域を象徴します。

TEIは、意味やIntentを実行可能なCapabilityへ接続し、現実世界へ実現する側を象徴します。

SEIは、その前後を含めて、何を見るか、何を問うか、何がまだ分からないかを扱える認知基盤として位置づけられます。

ただし、これを固定pipelineにしません。

```text
SEI → SUI → TEI
```

が必須順序ではありません。

実行結果が新しいObservationとしてSEIへ戻ることもあります。SUI以外のCognitive Methodを使うこともあります。TEI以外のProviderを利用することもあります。

卦シリーズは、製品間依存を決めるContractではなく、**異なる役割を人間が直観的に考えるための象徴体系**です。

## 15. ブランドアイコンとProduct Valueの距離

井桁マークは、純粋なIconとして単体で成立することを目指します。

直線を基本にし、一般的な`#`、企業の格子mark、家紋的な井桁との混同を避けるため、中央のnegative space、縦方向の比率、線端、交差部などを慎重に設計します。

ただし、Iconの造形上の決定をProduct Requirementへ持ち込みません。

たとえば中央の空白が重要だからといって、Product UIに必ず中央空洞を置く必要はありません。

水の反射をブランドで使うからといって、Productのscreen themeを青緑にする必要もありません。

ブランド造形は、Product Valueを考えるための象徴を視覚化したものです。UIやArchitectureは、別のEvidenceと責務に基づいて設計します。

## 16. このブランド世界から生まれるProduct Valueの問い

この原資料から、少なくとも次の問いが生まれます。

1. SEIの価値は、判断が成立した後のcontinuityだけでなく、**判断になる前のInquiry / Observation / unresolved contextを持続させること**にもあるか。
2. 組織の認知成果を、一個人、一AI session、一Providerへ閉じないCognitive Commonsとして扱うことは、独立した利用者価値か。
3. まだ曖昧なものをTruthへ急いで変えず、扱える認知対象へ持ち上げることは、SEI固有のProduct Valueになり得るか。
4. Product Experienceとしての「静けさ」は、attention burden、recommendation pressure、forced convergenceを減らすという観測可能な価値へ変換できるか。
5. shared cognitionとprivacy / Selective Disclosure / Responsibilityは、どのように両立するときに価値となるか。
6. AIが大幅に高度化した将来でも、組織が問い、Observation、Decision basis、Unknownを自分たちの共有認知資産として持つ価値は残るか。
7. これらは既存V1〜V8 / Decision Continuityで十分に説明できるか。それともProduct Vision / Value Proposition / Principleに新しい表現が必要か。

これらの問いへの答えは、この文書では確定しません。

`product/value/SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md`で、current Product Valueとの重複、独立性、failure、counterexample、適切な文書配置を検討します。

## 17. この文書を使うときの停止線

今後、このブランド世界をProduct Value探索へ使うときは、次を守ります。

- 比喩から型やfieldを直接作らない。
- 「深層」があるから`Depth`というUniversal entityを作らない。
- 「四方向」があるから四つのactor分類を固定しない。
- 「水」があるからすべてをKnowledge Storeへ集約しない。
- 「共有井戸」があるからAccess Controlを弱めない。
- 「静けさ」があるからwarningやproactive assistanceを禁止しない。
- SUI / TEIとの象徴的な関係から必須依存を作らない。
- ブランドに共感できることをProduct Value Evidenceとしない。

この停止線は、**神経系の比喩にも同じように適用します**（ADR-0032、Proposed）。SEIを家族の「神経系の頂点」と見る見方は、内部の設計言語であり、これも比喩から型やfieldを作りません。

- 「求心」「遠心」「反射弓」「海馬」といった対応から、Universal型やcontract fieldを直接作らない。
- 神経系の病理（分離脳、発作等）を、観測なしに実在の失敗として扱わない。
- 比喩から生じた問いは、CSWの帰属の規律（`framework_generated`と`target_supported`を区別する。`hat47x/cultural-substrate-weaving:AGENTS.md`）にならい、対象で確かめるまで`framework_generated`、つまり体系から生成された候補として扱う。
- 文書が裏づける対応と比喩由来の問いを、表の中で分けて示す（`../value/SEI_FAMILY_APEX_VALUE_REVIEW.md` §7）。
- ブランドの視覚表現では、巨大なAI brainやcommand centerを中心に置かない（§7）。

代わりに、象徴が照らした問いを、利用者のbenefit、failure、counterexample、actual Scenarioへ変換します。

## 18. 対立する読みを残す

ブランド世界を一つの解釈へ閉じないため、少なくとも次の対立を今後も保持します。

| 一方の読み | 反対側の問い |
|---|---|
| 深層へアクセスする | 既知の判断を正確に保持する方が重要な場面もある |
| Cognitive Commons | privacy / bounded accessを損なわないか |
| 静かな基盤 | proactive assistanceを弱めないか |
| 非収束性 | Decision latencyや責任回避につながらないか |
| 余白を守る | structure不足で再利用不能にならないか |
| shared cognition | Responsibilityが曖昧にならないか |
| 象徴的一貫性 | 実際のProduct differentiationがあるか |

SEIのProduct Valueは、この対立を隠すのではなく、実際のScenarioとEvidenceへ戻って選び直せる必要があります。

## 19. authorityとEvidence

本書が成立させるのは、ブランド世界をProduct探索へ再利用できるsourceの保存です。

```text
Brand source preserved: Yes
Product Value implication: hypothesis / review required
Stable Requirement: no change by this document
Universal Contract: no change by this document
Executable Evidence: none added
Adoption / Outcome Evidence: none added
```

本書自体を根拠に、Product Valueがactual useで成立したとは主張しません。

## 20. 関連文書

- `../value/SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md` — 本sourceから生じた価値候補の採否・配置判断
- `../value/SEI_PRODUCT_VALUE.md` — Product Value authority
- `../value/SEI_VALUE_MODEL.md` — V1〜V8と価値の優先関係
- `../value/SEI_VALUE_PROPOSITION.md` — 利用者に届く価値表現
- `SEI_PRODUCT_VISION.md` — 価値が実現した将来の利用状態
- `../principles/SEI_PRODUCT_PRINCIPLES.md` — 下位設計で反復する原則
- `../../plan/issue/ISSUE-000077-integrate-brand-world-into-product-value-discovery.md`
- `../../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 21. Natural Japanese review

この文書は、ブランド世界を後から参照可能な原資料として残すため、短い箇条書きだけでなく、井、中央の空白、水、静けさ、四方向性、公共性、人間・AIとの関係、SUI / TEIとの位置関係が一つの世界像として連続するように記述しました。

同時に、詩的な整合性によってProduct上の必要性を過大評価しないよう、各節でProduct Valueとの距離と停止線を明示しています。

「無意識」「深層」は心理学上の断定ではなく、まだ十分に言語化・表層化されていない領域を考えるための比喩として限定しました。水も完成済みKnowledgeではなくCognitive Potentialとして扱い、SEIが汲み上げた内容をTruthへ自動昇格させるような読みを避けています。

2026-10-02には、§17の停止線が神経系の比喩にも適用されることを提案として明記し、CSWの帰属の規律を参照しました。本書の非規範性は変えていません。

内容と構造を整えた後、意味、留保、非規範性を変えず、**自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とします。
