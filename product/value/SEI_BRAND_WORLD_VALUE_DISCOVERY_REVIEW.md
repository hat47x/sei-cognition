# SEI Brand World Product Value Discovery Review

更新日: 2026-09-14  
状態: **Product Value Discovery Review — Design Baseline / No new Value Axis established**

## 1. この文書の役割

この文書は、`product/vision/SEI_BRAND_WORLD_SOURCE.md`に保存したブランド世界から生まれたProduct hypothesisを、currentのProduct Value、V1〜V8、Decision Continuity、Product Vision、Product Principlesへ逆照合し、**何を新しい価値として扱うべきか、何を既存価値へ統合すべきか、何をブランド上の比喩に留めるべきか**を検討するためのReviewです。

このReview自体は新しいValue Axisを定義しません。

現時点の結論を先に示すと、ブランド世界から得られた洞察の大部分はcurrent Product Valueを否定するものではなく、むしろ既存のV1〜V8やDecision Continuityを別の角度から深く説明します。

一方で、ひとつ重要な未確定領域が見えています。

それは、SEIが現在強く表現している「Decision Continuity」に対して、**Decisionが成立する前のInquiry、Observation、Unknown、違和感、未整理な関係候補を、時間・主体・AI sessionをまたいで持続させる価値**が、Productとして十分に言語化されているかという問いです。

このReviewでは、この領域を直ちに新しいValue Axisへ昇格させず、`pre-decision cognitive continuity`または`Inquiry Continuity`に相当するProduct hypothesisとして残します。

## 2. Reviewの前提

current Product Valueでは、SEIを次のような認知・意思決定基盤として捉えています。

- Observation、Unknown、Conflict、Hypothesis等の意味差を失わない。
- Recommendation、Decision、Authority、Action Intent、Executionを混同しない。
- 過去を現在の知識で書き換えない。
- Providerや実行方式を交換してもIntent、Decision、Responsibility、Provenance等を持ち運ぶ。
- 人間とAIが同じcanonical meaningへ戻れる。
- 軽い利用から厳密な利用へ連続的に深められる。

また、V1〜V8が一つの判断仕事で同時に成立した利用者成果をDecision Continuityとして整理しています。

```text
Decision Continuity
  = 時間が空いても
  + SurfaceやAIが変わっても
  + 新しい情報が増えても
  + 不確実性が残っていても
  過去を捏造せず、判断仕事の続きを始められること
```

ブランド世界のReviewでは、これらを一度白紙に戻しません。

新しい表現が魅力的であることではなく、**既存baselineでは説明しにくい利用者benefitまたはfailureが独立して存在するか**を判断基準にします。

## 3. Review方法

各hypothesisについて、次の順で確認します。

```text
ブランド上の洞察
  ↓
利用者・組織にとってのbenefit
  ↓
欠けたときのfailure
  ↓
過剰適用したときのcounterexample
  ↓
current V1〜V8 / Decision Continuityとの重複
  ↓
最も自然な文書配置
  ↓
現時点の判断
```

現時点の判断は、次のいずれかとします。

- **Integrate** — 既存Value / Vision / Principleの説明を深める。
- **Keep as Product hypothesis** — 独立価値の可能性があるがEvidence不足。
- **No new Product Value** — current baselineで十分に表現されている。
- **Brand-only** — Product規範へ持ち込まずブランド世界に留める。

## 4. H77.1 — Cognitive Commons

### 4.1 ブランド上の洞察

井戸は共同体が利用するInfrastructureであり、SEIも一個人、一AI session、一Providerだけの認知状態へ閉じない共有基盤として価値を持つのではないか、という仮説です。

### 4.2 利用者benefit

この仮説が成立すると、利用者は次の価値を得ます。

- 担当者が変わっても、問い、Observation、Decision basis、Unknownを読み直せる。
- AI modelやsessionが変わっても、前のAIの会話履歴だけに依存せず仕事を続けられる。
- 個人の頭の中やprivate noteに閉じていた判断文脈を、適切なboundaryのもとで組織資産へ移せる。
- 結論だけでなく、未解決や問いそのものも共有できる。

### 4.3 欠けたときのfailure

- 重要な判断文脈が特定担当者の記憶へ閉じる。
- AIを交換すると前提と問いが失われる。
- 組織としては同じ問題を繰り返し調べる。
- Decisionだけが残り、なぜそうなったか、何が未解決だったかが共有されない。

### 4.4 Counterexample / 過剰適用

`commons`を強調しすぎると、次の誤りが生じます。

- 全員がすべてを読めるべきだと考える。
- privacyやSelective Disclosureを共有の敵とみなす。
- 個人の一時的な思考やprivate chain-of-thoughtまで共有資産化しようとする。
- sharedであることを理由にResponsibilityを曖昧にする。

したがって、価値があるのは`unbounded sharing`ではなく、**bounded, durable sharing**です。

### 4.5 current Valueとの重複

この価値はかなりの部分がすでに次へ含まれます。

- V4 Provider Independence
- V6 Human / AI Readability
- V8 Execution Independence
- Decision ContinuityのTemporal / Realization continuity
- Product Access / Selective Disclosure / Responsibility分離

一方、current Product Valueは「共有財産としての認知基盤」という社会的な利用状態を前面には出していません。

### 4.6 判断

**Integrate。新しいValue Axisにはしない。**

`Cognitive Commons`はV1〜V8とは別の評価軸というより、複数の既存価値が組織利用で成立したときのProduct Vision上の姿として扱うのが自然です。

Product VisionとValue Propositionで、「個人や一AI sessionへ閉じない」「適切なboundaryのもとで共有資産になる」という説明を強める余地があります。

## 5. H77.2 — Surface / Depth Interface

### 5.1 ブランド上の洞察

井を、すでに言語化された表層と、まだ十分に形を得ていない認知領域の間にあるGatewayとして読む仮説です。

### 5.2 利用者benefit

- 確証のない違和感を、Truthへ変えずに残せる。
- 「まだ分からないが気になる」をQuestionやHypothesisとして外在化できる。
- 後から別のEvidenceやMethodによって意味が立ち上がる余地を残せる。
- 完成済みKnowledgeだけでなく、認知形成の途中を扱える。

### 5.3 欠けたときのfailure

- 確定できないObservationが記録されない。
- 重要な弱いsignalが「まだ根拠不足」として消える。
- AIが曖昧な入力を強引に分類・要約し、元の違和感が失われる。
- 組織が、後から重要になる初期兆候を辿れない。

### 5.4 Counterexample / 過剰適用

- SEIが無意識や非言語的内容を直接扱えると誤解する。
- 何でも曖昧なまま保存し、情報量だけが増える。
- 具体性のない「気配」をUniversal entityにする。
- Evidenceのない主張を「深層から来た洞察」として権威化する。

### 5.5 current Valueとの重複

V5 Uncertainty Preservation、V7 Progressive Explicitness、Observation / Hypothesis / Unknownのsemantic distinctionでかなり表現できます。

またProduct Principlesには、観測・解釈・提案・判断を混ぜないこと、不確実性を正直に保持することがすでにあります。

### 5.6 判断

**No new Product Value。ただしProduct Vision上の説明を深める候補。**

`Surface / Depth`をdata modelへ持ち込む必要はありません。

SEIが扱えるのは外在化された認知対象からであり、「まだ十分に形を得ていないものを、意味差を失わず扱える形へ持ち上げる」というProduct姿勢として説明するのが適切です。

## 6. H77.3 — Deliberate Non-closure

### 6.1 ブランド上の洞察

井の中央の空白や静けさから、すべてを最短で一つの結論へ収束させず、Unknown / Conflict / Hypothesisを必要な期間保てることに価値があるのではないか、という仮説です。

### 6.2 利用者benefit

- 不確実なままでも、何が未解決かを失わずDecisionできる。
- 複数の解釈を残し、後からEvidenceによって見直せる。
- AIの自信ある回答に引きずられず、未解決を認識できる。

### 6.3 欠けたときのfailure

- UnknownがNoへ変換される。
- Conflictが最新値で上書きされる。
- AI Recommendationが事実上のDecisionになる。
- 早く画面を「完了」にするために重要な不確実性が消える。

### 6.4 Counterexample / 過剰適用

- いつまでもDecisionしないことを美徳とする。
- 未解決事項を整理せず蓄積する。
- high-impactな判断で必要なclosureまで避ける。

### 6.5 current Valueとの重複

これはV5 Uncertainty Preservation、V2 Semantic Separation、Product Principle 4、不確実性を残したまま前へ進めるProduct Valueにほぼ直接含まれています。

### 6.6 判断

**No new Product Value。current baselineで十分。**

ただし`Deliberate Non-closure`という言葉は、V5の設計意図を説明する補助的なProduct languageとして有用です。

## 7. H77.4 — Durable Cognitive Aperture

### 7.1 ブランド上の洞察

中央の空白を、問いを置き直し、別の主体が後から戻ってこられる認知上の入口として読む仮説です。

### 7.2 利用者benefit

- Decisionに至る前のInquiryを中断しても戻れる。
- 「何を調べていたのか」「なぜ気になっていたのか」を後から再開できる。
- UnknownやQuestionが、Decisionの付属物としてではなく独自の継続対象として残る。
- 別の担当者やAIが、結論のない途中状態から探索を引き継げる。

### 7.3 欠けたときのfailure

ここにはcurrent Product Valueとの重要な差が見えます。

Decision Continuityは、Decisionのbasis、Decision後の変化、reopen condition等を中心に「判断仕事の続きを始められること」を扱います。

しかし実務では、まだDecisionが一度も成立していない探索も長期間続きます。

たとえば、

- 数週間にわたり違和感だけが蓄積している。
- 何を問うべきか自体がまだ定まっていない。
- 複数のObservationはあるが、Recommendationへ進むには早い。
- 調査を一度中断し、別の担当者が後から再開する。

この段階でchatやworking memoryを失うと、Decision historyが存在しないため、Decision ContinuityだけではProduct failureを十分に説明できない可能性があります。

### 7.4 Counterexample / 過剰適用

- あらゆる思考の断片を保存しようとする。
- fleetingな気づきまでcanonical authorityにする。
- Inquiry / Workspace / Session等を安易にUniversal Core entityへ追加する。
- 「続けられること」を理由に大量のcapture burdenを課す。

### 7.5 current Valueとの重複

V1 Historical Reconstructionは過去のDecision再構成に強く、V5はUnknown preservation、V6はreadability、V7はprogressive explicitnessを扱います。

Product Visionでは「何を見るか、何を問うか」も対象にしています。

一方、Product Value Propositionの中心的な短い約束は「判断の続きを始められる」であり、Decision Continuityの具体的評価もDecisionを中心に組まれています。

### 7.6 判断

**Keep as Product hypothesis。今回のReviewで最も重要な未確定点。**

現時点ではV9を追加せず、`Inquiry Continuity`または`Pre-decision Cognitive Continuity`として独立Scenarioを作り、raw chat / noteとの比較で実際に価値差があるか確認するのが最善です。

この仮説が成立した場合でも、最終的に新Value Axisが必要とは限りません。

Decision Continuityをより上位の`Cognitive Continuity`へ再構成し、その下にDecision / Inquiryのcross-axis outcomeを置く方が自然な可能性もあります。

ただし、それはactual Product failureが確認された後に判断します。

## 8. H77.5 — Quiet Infrastructure

### 8.1 ブランド上の洞察

SEIは常時存在感を主張するAIではなく、必要なときに認知資源へアクセスでき、通常時にはattentionを奪いすぎないInfrastructureであるべきではないか、という仮説です。

### 8.2 利用者benefit

- AI suggestionが多すぎて本来のQuestionを見失うことを減らす。
- high-detailなaudit情報を必要時だけ開ける。
- 作業の主役がSEI操作ではなく、本来の判断仕事になる。
- proactive assistanceを利用しつつ、自分で問い直す余地を保てる。

### 8.3 欠けたときのfailure

- 常時notificationやRecommendationが利用者のattentionを奪う。
- AI suggestionが多すぎてUnknownやConflictが埋もれる。
- semantic detailの入力がProduct利用の中心作業になる。
- 「便利なAI」が強すぎてRecommendation / Decision境界が実質的に見えなくなる。

### 8.4 Counterexample / 過剰適用

- proactive warningまで抑制する。
- high-riskなreview conditionを見えにくくする。
- 利用者に必要なnext actionを示さない。
- 「静か」を理由にdiscoverabilityを下げる。

### 8.5 current Valueとの重複

V7 Progressive Explicitness、ISSUE-000073のcapture / review burden、AI correction / graceful degradationと強く重なります。

### 8.6 判断

**Integrate as Product Interaction quality hypothesis。新しいValue Axisにはしない。**

`Quiet Infrastructure`はProduct Vision / Interaction designの質を考える強い言葉ですが、独立したUniversal Valueとして採点するより、attention burden、recommendation pressure、capture overhead等の具体的failureへ落として評価する方がよいです。

## 9. H77.6 — Shared but not Unbounded

### 9.1 ブランド上の洞察

共有井戸であることと、全情報を無制限に公開することを分離する仮説です。

### 9.2 利用者benefit

- 組織の共有認知資産を持ちながら、sensitiveなEvidenceの境界を保てる。
- ResponsibilityやAuthorityを共有によって曖昧にしない。
- 別の主体が必要な範囲だけを読める。

### 9.3 欠けたときのfailure

- shared cognitionを実現するためにprivacyを犠牲にする。
- Accessを絞ると今度は引継ぎ不能になる。
- 「共有されたDecision」だけが残り、参照可能なbasisが主体ごとに分断される。

### 9.4 current Valueとの重複

Product Identity / Access / Collaboration、Selective Disclosure、Responsibility / Authority分離ですでに重要な境界が存在します。

### 9.5 判断

**No new Product Value。Cognitive Commonsの成立条件として統合。**

共有可能性とboundaryの両立を、Product VisionでCognitive Commonsを説明するときの必須条件として扱うのが自然です。

## 10. 横断比較

| Hypothesis | current coverage | 独立性 | 現時点の判断 |
|---|---|---|---|
| Cognitive Commons | V4 / V6 / V8、Access、Decision Continuity | 中 | Visionへ統合。新Value Axisなし |
| Surface / Depth Interface | V5 / V7、Observation / Hypothesis / Unknown | 低〜中 | Vision説明を深める。Universal化しない |
| Deliberate Non-closure | V2 / V5 | 低 | current baselineで十分 |
| Durable Cognitive Aperture | V1 / V5 / V6 / V7、Decision Continuity | **中〜高** | Inquiry Continuity hypothesisとして継続探索 |
| Quiet Infrastructure | V7、Interaction burden | 中 | Interaction quality hypothesisへ統合 |
| Shared but not Unbounded | Access / Selective Disclosure / Responsibility | 低 | Cognitive Commonsの成立条件 |

この比較から、ブランド世界は新しいValueを六つ追加する根拠にはなりません。

むしろ、既存Valueの背後にある一貫したProduct姿勢を可視化し、**唯一、Decision以前の認知継続という弱い部分を発見した**ことに価値があります。

## 11. Product文書へ何を反映するか

### 11.1 Product Vision

Product Visionには、次を追加する価値があります。

1. SEIは判断結果だけでなく、**問いがまだ判断へ至っていない段階から、認知対象を共有可能にする基盤**を目指すこと。
2. 個人や一AI sessionに閉じず、適切なboundaryのもとでCognitive Commonsとして持続すること。
3. SEIをcentral AI brainではなく、Human / AI / Methodが利用する共有Infrastructureとして明確にすること。
4. 「静けさ」を、必要な時に深く扱え、通常時には過剰なattention burdenを課さない利用状態として記述すること。

ただし、`Surface / Depth`、井戸、水などのブランド比喩自体をProduct Visionの規範文へ大量に持ち込む必要はありません。

### 11.2 Product Value

current Product Valueは、Observation、問い、不確実性、判断、来歴をすでに広く扱っています。

現時点で新しいValue Axisを追加する根拠はありません。

ただし「判断の記憶」だけでなく、**判断前のInquiryが持続できること**がactual Product failureとして確認された場合は、Product Value本文の「判断継続性」中心の説明を再監査する必要があります。

### 11.3 Value Model

V1〜V8は維持します。

新しいV9は作りません。

Inquiry Continuityが成立する場合でも、まずV1 / V5 / V6 / V7のcross-axis outcomeとして説明可能かを検討します。

### 11.4 Value Proposition

利用者向けの一言の約束は現在、

> あとで戻っても、別のAIを使っても、情報が変わっても、過去を捏造せず判断の続きを始められる。

となっています。

これは強い表現なので、今回のDesign Reviewだけで直ちに変更しません。

一方、Inquiry Continuityが実証された場合は、`判断`だけでなく`問いや判断仕事`を含む表現への拡張を検討します。

### 11.5 Product Principles

新しいPrincipleを増やすより、既存の次の原則がブランド世界の意味を十分に担っています。

- 観測・解釈・提案・判断を混ぜない。
- 不確実性を正直に保持する。
- Progressive Semantic Explicitness。
- Providerを交換可能にする。
- human-readableを設計品質として扱う。

`Quiet Infrastructure`は、今後Product Interaction Principleが必要になった場合の候補として保持します。

## 12. 今回のReviewから起票すべき後続探索

最も価値が高い後続は、**Decision以前の認知継続性を反証可能にする探索**です。

仮称を`Inquiry Continuity`とします。

検証したいProduct failureは次です。

```text
Decisionがまだ存在しない
  + Question / Observation / Unknownが数日〜数週間続く
  + AI sessionや担当者が変わる
  → それでも「何を気にしていて、何を見て、何がまだ分からないか」へ戻れるか
```

比較対象としては、raw chat、chronological note、issue tracker等が妥当です。

見るべき点は、

- original concernを正しく再構成できるか。
- ObservationとHypothesisを混同しないか。
- unresolved questionを見つけられるか。
- 後から得た情報で最初の違和感を書き換えないか。
- capture burdenが価値を上回らないか。
- AIがsummaryを作った場合も、元のuncertaintyを失わないか。

です。

この探索結果が、

- existing V1〜V8 / Decision Continuityで十分
- Decision Continuityの適用範囲を広げれば十分
- Cognitive Continuityという上位synthesisが必要
- 独立したInquiry Continuity outcomeが必要

のどれになるかは、先に決めません。

## 13. ブランド世界がProduct Valueへ与えた実質的な成果

今回のBrand World Reviewで得た成果は、「井」に対応する新しい機能一覧ではありません。

より重要なのは、次の三点です。

### 13.1 Product Valueを一つの世界像として再読できた

V1〜V8は個別評価軸として必要ですが、ブランド世界を通すと、それらがなぜ同時に必要なのかが見えやすくなります。

SEIは、全知の中心を作るのではなく、異なる主体が、確定しているものも未確定なものも、来歴と責任を失わず扱える共有認知基盤を目指している。

この世界像は、既存Product Valueを置き換えず、その背後にある一貫性を説明します。

### 13.2 「静けさ」を機能主義へ翻訳できた

静けさは色や雰囲気ではなく、forced convergence、attention burden、recommendation pressure、capture overheadを抑えるProduct qualityとして検討できることが分かりました。

### 13.3 Decision以前の継続性という弱点を発見した

ブランド世界で中央の空白、問い、深層へのaccessを考えたことで、current Product ValueがDecision後のcontinuityには強い一方、**Decisionがまだない探索状態のcontinuityをどこまでProduct guaranteeとして引き受けるのか**が十分に検証されていないことが見えました。

これが今回もっとも重要なProduct Value discoveryです。

## 14. 現時点のDecision

本Review時点では、次をcurrent判断とします。

```text
新Value Axis追加                = No
V1〜V8変更                      = No
Decision ContinuityをV9化       = No
Cognitive Commons               = Product Vision候補
Surface / Depth Interface       = Brand / Vision説明候補
Deliberate Non-closure          = current V5等で十分
Quiet Infrastructure            = Product Interaction quality hypothesis
Shared but not Unbounded        = Cognitive Commons成立条件
Inquiry Continuity              = Follow-up Product hypothesis
```

## 15. 次に行うこと

1. `SEI_PRODUCT_VISION.md`を、Cognitive Commons、pre-decision inquiry、Human / AI / Methodが利用するshared infrastructureという観点で再読し、必要な範囲だけ改稿する。
2. `SEI_VALUE_PROPOSITION.md`の短いpromiseは現時点では維持し、Inquiry Continuityのactual Evidence前に広げない。
3. Inquiry Continuityを検証するfollow-up Issueを起票する。
4. ISSUE-000073のresume-first human reviewと混同せず、Decision前の長期Inquiryを対象にしたcounterfactual comparisonを設計する。
5. Brand World Sourceと本ReviewをDocument Review Registryへ登録する。
6. ISSUE-000077のResolution criteriaのうち、brand-world sourceとProduct Value Discovery Reviewを完了状態へ更新する。ただし後続Product文書の改稿とNo Change記録が完了するまでIssueはOpenを維持する。

## 16. Natural Japanese review

このReviewでは、ブランド世界を褒める文章ではなく、Product Value上の独立性を厳しく確認することを重視しました。

特に、Cognitive Commons、Surface / Depth Interface、Deliberate Non-closure、Durable Cognitive Aperture、Quiet Infrastructure、Shared but not Unboundedをそれぞれ独立したValueとして並べるのではなく、利用者benefit、欠けたときのfailure、過剰適用したときのcounterexample、V1〜V8との重複を一つずつ確認しています。

その結果、ブランド世界の大半はcurrent baselineを豊かに説明するものであり、新しいValue Axisを増やす必要はないと判断しました。一方、Decision以前のInquiry Continuityは、current Product Valueで十分に反証されていない独立したProduct hypothesisとして残しました。

内容、規範強度、未検証範囲を固定した後、**自然な日本語として背景から結論まで無理なく追えることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とします。
