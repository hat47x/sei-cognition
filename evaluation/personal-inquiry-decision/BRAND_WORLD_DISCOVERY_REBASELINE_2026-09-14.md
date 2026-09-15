# Brand World Discovery Rebaseline — Personal Inquiry Continuity

更新日: 2026-09-14  
状態: **Evaluation Rebaseline — No Parallel Harness / No New Stable Requirement**  
関連: `plan/issue/ISSUE-000077-integrate-brand-world-into-product-value-discovery.md` / `plan/issue/ISSUE-000078-verify-pre-decision-inquiry-continuity.md`

## 1. この文書の役割

SEI Cognitionのブランド世界をProduct Value探索へ接続した結果、Decision成立前の長期的なInquiryを中断・再開できることが、独立して確かめる価値のあるProduct hypothesisとして改めて見えてきた。

一方、current repositoryにはすでに`evaluation/personal-inquiry-decision/`が存在し、**Personal Inquiry Continuity**という名前で、この問題をかなり深いところまで扱っている。

この文書は、ISSUE-000077 / ISSUE-000078から生まれた問いと、既存Personal Inquiry Continuity系列を照合し、重複したevaluation frameworkを新しく作らずに済むかを判断するための再基線化記録である。

結論を先に示す。

> **Decision成立前のInquiry Continuityは新しく発見された問題ではない。current Personal Inquiry ContinuityはすでにDecisionを必須とせず、open Inquiryの再開、historical integrity、raw chat / final noteとの比較、AI handoff、capture burdenまでをProduct hypothesisとして持っている。**

したがって、ISSUE-000078の目的を達成するために別のfixture体系、別のProfile、別のCandidate Requirement群を新設しない。

ISSUE-000078は、Brand World Discoveryによって同じ問題が別経路から再発見されたことを利用して、**既存Personal Inquiry Continuityの仮説・validation protocolに不足がないかを再監査し、actual Evidence取得へ収束させるIssue**として扱うのが最も自然である。

```text
Brand World Discovery
  → Inquiry Continuityを再発見
  → existing Personal Inquiry Continuityへ戻る
  → gap / contradiction / omitted angleを監査
  → existing validationを使ってactualに確かめる

not:
Brand World Discovery
  → 新しいparallel evaluation stackを作る
```

## 2. 既存Personal Inquiry Continuityがすでに持っている中心

`README.md`は、このevaluationの目的を「一人の利用者が自分の長期的な問いを中断・再開する場面で、SEIが本当に役立つか」と定義している。

しかも、Decisionは中心要素の一つではあるが、Inquiryの成立条件ではない。

```text
Personal Inquiry Continuity
  contains Decision Memory when Decision exists
  != Decision tracker only
  != chat archive
  != note-taking app
  != task manager
```

この境界は、ISSUE-000077のDiscovery Reviewで改めて見つかった「Decisionがまだ存在しないInquiryのcontinuity」と直接一致する。

したがって、今回のブランド世界から得た洞察を理由に、`Inquiry`を新しいUniversal semantic entityとして追加したり、Decision Continuityとは別のProfileを最初から新設したりする必要はない。

既存系列はすでに、content memoryだけでは足りず、当時の認識状態と再開支援を分けなければならないことを問題の中心に置いている。

## 3. Durable Inquiry MemoryとCognitive Resumption Support

`COGNITIVE_RESUMPTION_MODEL.md`では、Personal Inquiry Continuityを二つに分けている。

```text
Durable Inquiry Memory
  = 後から意味を誤読しないための記録

Cognitive Resumption Support
  = 中断後にmental contextへ戻るためのcue / projection
```

この二層分離は、Brand World Discoveryで言語化した「井」と中央の空白をProductへ翻訳するときにも重要である。

ブランド上、井は深層にあるものをすべて地表へ引き上げる装置ではない。必要なときにアクセスできる入口である。

同様にProduct上も、canonicalな意味をすべて常時表示する必要はない。

Durable Inquiry Memoryは、Observation、Hypothesis、Unknown、Conflict、Decision、basis、provenance等を意味上壊さず保持する。

Resumption Projectionは、その正本を読み、利用者が続きを始めるためのorientation、delta、resume anchor等を選択的に提示する。

```text
accurate durable meaning
  != everything visible all the time

compact resume cue
  != historical authority
```

この構造は、Brand Worldで言う「quiet infrastructure」と非常に親和性が高い。

ただし、その親和性を理由に新しいArchitectureを追加しない。既存モデルがactual利用で十分かを先に確かめる。

## 4. ISSUE-000078との重複監査

ISSUE-000078は、DecisionがないInquiryを対象に、少なくとも次のfailureを検証対象としている。

- original concernを失う。
- later informationをinitial stateへ誤帰属する。
- ObservationとHypothesisを混同する。
- Unknown / Conflictを取り落とす。
- AI summaryが複数の解釈を一つへ潰す。
- 元chatがないと再開できない。
- capture burdenがbenefitを上回る。
- raw chat / noteと比べても価値差がない。

これらは既存Personal Inquiry Continuityの問題設定と大きく重なる。

特に`VALUE_VALIDATION_PROTOCOL.md`には、すでに次の仮説がある。

### H1 — Reorientation Value

長く中断したInquiryでも、元chatや全sourceを大量に再読せず現在地へ戻れるか。

### H2 — Historical Integrity Value

当時知っていたこととlater Evidenceを混同しないか。

### H3 — Inquiry Continuity Value

Decisionへ到達していないopen Inquiryでも途中状態を保持して再開できるか。

### H4 — AI Portability Value

元conversationなしで別AI / toolへ続きを渡せるか。

### H5 — Friction Sustainability

そのbenefitを得るためのcapture / correction burdenが継続可能か。

つまりISSUE-000078のProduct hypothesisは、existing H3を中心にH1〜H5を横断して再検討するものと理解するのが自然である。

## 5. 比較設計も新設する必要はない

ISSUE-000078では、raw chat、chronological note、SEI canonical meaning + derived Projectionの比較を想定した。

既存`VALUE_VALIDATION_PROTOCOL.md`も、すでに次を比較対象としている。

```text
B0 — Chat-only
B1 — Final-note
P1 — SEI Personal Profile
```

さらに、

- short-cycle dogfooding
- baseline comparison
- cross-AI / cross-session handoff
- voluntary reuse

というEvaluation Stageも用意されている。

したがって、別の`E78.*` harnessを一式作るより、existing B0 / B1 / P1およびE0〜E4のどこにISSUE-000078由来の観測点を追加すべきかを監査する。

この方針により、同じProduct Valueを二つの名前で別々に評価し、後からEvidenceを統合できなくなることを避ける。

## 6. False Continuityという重要な既存概念

Brand World Discoveryでは、「静かな基盤」や「中央の余白」を考える過程から、AIが流暢なsummaryや次の問いを大量に提示することが、必ずしもProduct Valueではないと整理した。

既存Personal Inquiry Continuityには、この問題を扱うための**False Continuity**という概念がすでにある。

```text
fast resume
+ wrong historical state
= failure
```

これはISSUE-000078で重視した、

```text
resume is fast
  != resume is historically correct
```

と同じ中心を持つ。

したがって、Inquiry Continuityの評価で新しい総合scoreを作る必要はない。

既存のHistorical Integrity、Unknown / Conflict Preservation、Recommendation / Decision Integrity、Correction Trust等を維持しながら、Brand World由来の問いを補助観測へ加える方がよい。

## 7. Brand World Discoveryが既存系列へ新しく持ち込むもの

大部分は既存系列と重なるが、Brand World Discoveryには、既存文書を再監査する価値のある角度もある。

### 7.1 Quiet Infrastructureをattentionの問題として見る

既存Personal Inquiry Continuityはcapture burdenやresumption burdenを扱っている。

しかしBrand World Discoveryでは、それに加えて、**AIが生成できるものを常時前面へ出しすぎること自体が認知負荷になり、original concernやUnknownを覆い隠す可能性**を強く意識した。

したがって、existing validationへ追加を検討する観測点として、次がある。

- recommendation / next-question候補を大量提示した場合、original concernを保持しやすいか。
- 必要時だけ候補へ降りる場合との違いはあるか。
- proactive assistanceによってUnknown発見が増えるのか、それともAIが作った問いへ注意が移るのか。
- warningやmaterialなchangeまで「静けさ」の名で見えにくくしていないか。

これは新しいProduct Valueではなく、H1 / H3 / H5およびProduct Interaction qualityの追加観測である。

### 7.2 Cognitive CommonsはPersonal Profileの外側にある

Brand World Discoveryでは、認知成果が一人や一AI sessionへ閉じず、適切なboundaryのもとで共有資産になることをCognitive Commonsとして整理した。

一方、current Personal Inquiry Continuityはfirst validationをsingle-userの低〜中影響Inquiryへ意図的に絞っている。

したがって、ここでteam sharingやorganization-wide knowledge commonsを先取りしてはいけない。

Personal Profileで検証すべきなのは、まず、

- 別AI / sessionへ意味を渡せるか。
- original chatがなくても読み直せるか。
- export / importでmeaningを壊さないか。

という**handoff可能性**である。

人間同士・部署間のbounded sharing、Selective Disclosure、Responsibilityを含むCognitive Commonsのactual評価は、その後の別Product scopeとして扱う。

### 7.3 「井の深層」はevaluation objectではない

Surface / Depthの比喩から、言語化前の違和感やweak signalを扱いたくなるが、SEIは非外在化の心理状態を直接記録できない。

Personal Inquiry Continuityで扱う対象は、利用者が何らかの形で外在化したQuestion、Observation、Hypothesis、Unknown、Artifact reference等からである。

したがって、`depth`や`latent`という新しいsemantic typeを追加しない。

## 8. current Requirement候補との関係

既存系列にはPIC-* Candidate Requirementがあり、`REQUIREMENT_GAP_AUDIT.md`や`RESEARCH_DERIVED_REQUIREMENT_REVIEW.md`でcurrent SEI Requirementとの重複・gapを監査している。

ISSUE-000078から新しいCandidate Requirement IDを増やす前に、必ずこの既存系列へ戻る。

特に次の順を守る。

```text
ISSUE-000078で見つけたfailure
  ↓
Personal Inquiry Continuityのexisting hypothesis / PIC-*へ照合
  ↓
current Stable REQ / SCNへ照合
  ↓
既存表現で不足するactual failureが再現した場合だけ
Candidate Requirementの改稿・追加を検討
```

ブランド世界と一致するからという理由でRequirementを増やさない。

## 9. ISSUE-000073との境界

ISSUE-000073は、current Product Value上のDecision Continuityを、first usable resume-first Product Sliceとしてactualに検証するlaneである。

Personal Inquiry Continuityはそれより広く、Decisionが存在しないopen Inquiryも含む。

二つを完全に別製品として扱う必要はないが、評価時には条件を分ける。

```text
ISSUE-000073
  Decision-centered resume-first Product Slice

Personal Inquiry Continuity / ISSUE-000078
  Decision may exist or may not exist
  long-running personal Inquiry continuity
```

相互に有用なfixtureやInteraction mechanismは再利用できる。

ただし、ISSUE-000073のPASSだけから「DecisionなしのInquiry Continuityも実証済み」とはしない。逆も同様である。

## 10. 今回の再基線化による判断

今回の監査では、次をcurrent判断とする。

```text
新しいInquiry Continuity evaluation directory   = 作らない
新しいUniversal Inquiry型                        = 作らない
新しいValue Axis                                = 作らない
新しいPIC requirement series                    = 先取りしない

existing Personal Inquiry Continuity            = 再利用する
existing H1〜H5                                 = 維持する
existing B0 / B1 / P1 comparison                = 再利用する
existing E0〜E4 validation stages               = 再利用する
False Continuity                                = 維持する

Brand World由来の追加観点
  = Quiet / proactive assistanceのattention effect
  + Cognitive Commonsとの将来境界の明示
```

## 11. ISSUE-000078の実質的な次の作業

ISSUE-000078の次の高情報量stepは、新しい設計文書を増やすことではない。

### Step 1 — existing validation coverage audit

`VALUE_VALIDATION_PROTOCOL.md`と`RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md`を、ISSUE-000078のfailure candidateと一対一で照合する。

不足がなければNo Changeとする。

### Step 2 — Quiet / proactive assistanceだけを追加候補として監査する

existing protocolでattention burdenやAI-generated next-question pressureを十分に観測できない場合だけ、小さなamendmentを追加する。

### Step 3 — actual dogfoodへ進む

Design文書を増やすのではなく、既存B0 / B1 / P1、E1 / E2 / E3を用いてactualなInquiryを評価する。

重要なのは、Decisionあり・なしの両方を含めることである。

### Step 4 — Outcomeを上位へ戻す

actual Evidenceから、

- current V1〜V8 / Decision Continuityで十分
- Decision Continuityの説明拡張が必要
- Cognitive Continuityという上位synthesisが有用
- Personal Inquiry Continuityを独立Product Profileとして強めるべき
- simple chat / noteで十分な範囲が大きい

のどれが妥当かを判断する。

## 12. 文書authority

この文書はEvaluation Rebaselineであり、Stable Product Requirementではない。

`SEI_BRAND_WORLD_SOURCE.md`は非規範の探索源、`SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md`はProduct Value discoveryのDesign Review、current Product Value / Value Model / Requirements / ADRはそれぞれの正本である。

```text
Brand World Source
  != Product Value authority

this Evaluation Rebaseline
  != Stable Requirement

existing evaluation protocol
  != Adoption / Outcome Evidence
```

actualなdogfoodとhuman reviewが行われるまで、Inquiry Continuityを実証済みProduct Valueとは書かない。

## 13. Natural Japanese review

この再基線化では、Brand World Discoveryから生まれたInquiry Continuityという言葉を新規性のある概念として扱わず、current repositoryにすでに存在するPersonal Inquiry Continuityへ戻って意味を照合した。

その結果、Decisionを必須としないこと、認識状態を壊さず再開すること、Durable Inquiry MemoryとResumption Projectionを分けること、chat / final noteとの比較、AI handoff、capture burden、False Continuityという中心論点はすでに十分に存在していることが分かった。

一方、Brand World Discoveryは無駄ではない。別の思考経路から同じProduct hypothesisへ到達したことで、SEI Cognitionの名称・VisionとPersonal Inquiry ContinuityのProduct探索が偶然ではなく、同じProduct Valueの異なる断面を見ている可能性が強まった。また、Quiet Infrastructureをattentionの問題としてより明示的に評価する余地と、Personal Profileの先にあるCognitive Commonsとの境界が見えた。

内容、authority、未検証範囲を整理した後、**重複を増やさず既存資産へ戻れる自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み**とする。
