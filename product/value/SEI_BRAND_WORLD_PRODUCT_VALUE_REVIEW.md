# SEI Brand World — Product Value Discovery Review

更新日: 2026-09-14  
状態: **Product Value Discovery Review — Design synthesis / Outcome Evidence pending**

## 1. この文書の役割

この文書は、`SEI_BRAND_WORLD_DISCOVERY_SOURCE.md`に保存した「井」のブランド世界から生まれたProduct hypothesisを、current Product Value、V1〜V8、Decision Continuity、Vision、Principlesへ逆照合し、**何をProduct文書へ採用し、何を既存概念へ統合し、何を非規範の探索語として残すか**を判断した記録です。

ブランドとの象徴的一貫性は採用条件ではありません。各候補を次の順で確認します。

```text
symbolic insight
  ↓
user / organizational benefit
  ↓
observable failure
  ↓
counterexample / trade-off
  ↓
existing Product Value coverage
  ↓
proper document placement
```

このReview自体も、actual user valueを実証するEvidenceではありません。

## 2. 結論の概要

H77.1〜H77.6を逆照合した結果、**新しいValue Axisを追加しない**ことを採ります。

ブランド世界が照らした内容の多くは、current V1〜V8、Decision Continuity、Product Access、Progressive Explicitnessにすでに意味上の根を持っています。一方、既存文書では利用世界として弱く表現されていた三つの側面がありました。

1. **まだ十分に形を得ていないものを、早まってTruthへ昇格させず認知対象へできること。**
2. **認知成果を一人・一AI・一Providerの一時状態へ閉じず、Access / Responsibilityを保って共有・継続利用できること。**
3. **AIや情報を常時押し付けず、利用者の認知帯域を不用意に奪わないこと。**

これらは、新しいontologyよりもProduct Value / Value Proposition / Vision / Principlesの表現を深めることで扱うのが自然です。

```text
brand discovery
  → Product Value language deepened
  → Product Vision broadened
  → Product Principles sharpened
  != V9 added
  != new Universal type added
```

## 3. H77.1 — Cognitive Commons

### 仮説

認知成果を一個人、一AI session、一Providerの一時状態へ閉じず、適切なaccess / responsibility boundaryのもとで共有可能な資産として持続させることに価値があるのではないか。

### 利用者・組織benefit

- 担当交代後も、問い、未解決、basis、Decisionへ戻れる。
- AI model / Providerが変わっても、前の認知成果を別の主体が利用できる。
- 同じ調査や判断をsessionごとにゼロからやり直す負担を減らせる。
- 一人の頭の中やchatに埋もれた重要なUnknown / Conflictを組織で問い直せる。

### failure

- 重要な認知成果が担当者退職やchat消失で読めなくなる。
- 別AIへ切り替えるたびにcontextを手作業で再構成する。
- shared noteへ転記した結果、Recommendation / Decision / historical basis等の意味差が消える。

### counterexample / trade-off

共有を強めすぎると、privacy、Selective Disclosure、Access Control、Responsibilityが壊れます。また、すべてを共有資産化するcapture burdenがbenefitを上回る仕事もあります。

### existing coverage

主にV1 Historical Reconstruction、V4 Provider Independence、V6 Human / AI Readability、V8 Execution Independence、Decision Continuity、およびProduct Access boundaryで広くcoverageされています。

### 判断

**新しいValue Axisにはしない。**

ただし、current Product Value / Visionは「後から読める」ことを個々の判断文脈として強く書いている一方、認知資産が一主体の一時状態へ閉じないという組織的な利用状態は弱いので、Value / Proposition / Visionで明示的に強めます。

`Cognitive Commons`という語自体は探索語として有用ですが、法的・制度的な意味へ広がりやすいため、normative nameには採用しません。

## 4. H77.2 — Surface / Depth Interface

### 仮説

SEIはすでに明示されたKnowledgeを保存するだけでなく、まだ十分に言語化・構造化されていない観察や違和感を、Truthへ早まって昇格させず扱える認知対象へ持ち上げる境界として価値を持つのではないか。

### benefit

- 「何か気になるが、まだ説明できない」を捨てずに残せる。
- AIが流暢な説明を作っても、弱いsignalを確定したfactとして扱わずに済む。
- 後からEvidenceが増えたとき、初期の違和感や問いと接続できる。
- Knowledge managementより前の探索段階からSEIを使える。

### failure

- 構造化できない入力を捨てるため、弱いsignalが失われる。
- AIが曖昧なObservationを一つの整った結論へ過剰要約する。
- 「未整理」を`Unknown`一語へ潰し、何を問い直すべきか分からなくなる。

### counterexample / trade-off

曖昧な素材を大量に保持するとnoiseが増え、再利用やattention allocationが難しくなります。何でも「深層のsignal」として重く扱うと、誤検知や認知負荷を増やします。

### existing coverage

V2 Semantic SeparationとV5 Uncertainty Preservationが意味上の安全性をすでに担います。Inquiry / Observation / Hypothesis等のcurrent semanticsも存在します。

### 判断

**独立したValue Axisや`Depth`型は不要。**

一方、SEIが「判断後の記録」だけでなく、問いがまだ形を得ていない探索初期から使えるという利用価値はProduct Value / Proposition / Visionで強める価値があります。

採用する中心表現は「深層」そのものではなく、**未確定なものを未確定なまま外在化し、後から問い直せること**です。

## 5. H77.3 — Deliberate Non-closure

### 仮説

Unknown / Conflict / Hypothesis / alternate interpretationを必要な期間保持し、未解決を消さず責任あるDecisionへ進めることに価値があるのではないか。

### benefit

- AIや組織が早すぎる一つの物語へ収束することを防ぐ。
- Decision時に何を未解決のまま受け入れたかを後から確認できる。
- 新Evidenceが来たとき、捨てられたalternate interpretationを再検討できる。

### failure

- Conflictが最新値で上書きされる。
- Unknownが入力不足として消える。
- Recommendationが多数派だからという理由でDecisionへ昇格する。

### counterexample / trade-off

非収束性を価値化しすぎると、必要なDecisionを遅らせ、Responsibility回避の口実になります。

### existing coverage

V5 Uncertainty Preservation、V2 Semantic Separation、Product Principle 4、Decision Memoryですでに強くcoverageされています。

### 判断

**Product Valueの新規項目にはしない。Value Modelも変更しない。**

ただしProduct Principlesでは、単に「不確実性を保存する」だけでなく、**早すぎる収束を強制しないが、必要なDecisionは避けない**という両側の停止線を明示します。

## 6. H77.4 — Durable Cognitive Aperture

### 仮説

時間・担当者・AI・Surfaceが変わっても、問いを置き直し、過去の認識へ戻り、新しいObservationを加えられる認知上の入口を持続させることが価値ではないか。

### benefit

- 完了したDecisionだけでなく、Decisionに至らないInquiryも再開できる。
- 「最後の会話」ではなく「最後の忠実な認識状態」へ戻れる。
- 別のAIや将来の自分が、同じ問いを別の角度から続けられる。

### failure

- final Decisionだけ残り、なぜその問いが生じたかが消える。
- chat threadが消えるとInquiry自体を再開できない。
- current summaryしか残らず、過去の認識状態を問い直せない。

### counterexample / trade-off

すべてのInquiryを永久保存する必要はありません。retention / deletion agency、capture burden、不要な古い問いの蓄積とのtrade-offがあります。

### existing coverage

Decision ContinuityとPersonal Inquiry Continuityの探索が中心をすでに扱っています。V1 / V3 / V6 / V7 / V8も支えます。

### 判断

**Decision Continuityの隣接した利用世界表現としてVisionへ統合し、独立Value Axisにはしない。**

「aperture」は有用な設計比喩ですが、Universal semantic entityにはしません。

## 7. H77.5 — Quiet Infrastructure

### 仮説

SEIの使いやすさは、AI suggestionや情報を大量に提示することではなく、必要なときに必要な認知へ到達でき、通常時にはattention burdenを増やしすぎないことにあるのではないか。

### benefit

- 判断仕事そのものよりSEIの操作・通知に注意を奪われにくい。
- AIの生成量を「支援量」と取り違えない。
- low-impactな利用では軽く使え、必要なときだけ深く降りられる。
- materialな変化やConflictには適切な強さで気付ける。

### failure

- suggestion / alert / follow-upが多すぎて、利用者が本来の問いを見失う。
- 「AIができるから」という理由だけでproactive interventionを増やす。
- audit detailを常時前面に出しcapture / review taxを高める。

### counterexample / trade-off

静けさを過度に優先すると、materialな変化、安全上のsignal、reopen conditionを見逃します。利用者がproactive helpを望む場面もあります。

### existing coverage

V7 Progressive Explicitnessは入力・表示の厚さを扱いますが、**attentionを有限な認知資源として不用意に占有しない**という設計姿勢はcurrent Product Principlesで十分に明文化されていません。

### 判断

**新Value Axisではなく、新しいProduct Principleとして採用する。**

Principleでは「quiet-by-default」という固定UI仕様にせず、認知pressureはbenefit / urgency / user controlにより正当化されるべきだと書きます。actual Interaction requirement化はhuman reviewやfailure Evidenceを待ちます。

## 8. H77.6 — Shared but not Unbounded

### 仮説

共有可能性、Provenance、Responsibility、Selective Disclosure、Access Controlが同時に成立するとき、初めて共有認知基盤として価値が生まれるのではないか。

### benefit

- 組織で認知成果を再利用しつつ、不要な情報拡散を避けられる。
- accessできる主体とDecision Authorityを混同しない。
- AIへ必要なcontextだけを渡し、canonical全体を無条件に送らずに済む。

### failure

- 「共有財産」を理由に全情報を全員・全AIへ開く。
- 読めることからResponsibility / Authorityを推定する。
- confidentialityのために共有を完全に諦め、認知成果が各sessionへ分断される。

### counterexample / trade-off

強すぎるaccess boundaryは再利用性を落とします。弱すぎるboundaryはprivacy / security / organizational trustを壊します。

### existing coverage

ADR-0006、ADR-0030、Product Access Architecture、V6、Decision Continuityのcontext egress設計等で意味上は広くcoverageされています。

### 判断

**新Value Axisにはしない。VisionとPrinciplesで「shared cognitionとaccess boundaryを同時に設計する」ことを明示する。**

## 9. 統合後のProduct Value構造

ブランド世界から得た洞察を統合すると、SEIの長期像は次のように読むことができます。

```text
SEI is thin as infrastructure,
but can open access to deep cognition.

It preserves meaning without forcing closure,
shares cognition without erasing boundaries,
and assists without monopolizing attention.
```

「薄く耐久的な意味基盤」と「深層へ開く共有可能な認知入口」は矛盾しません。

薄く保つべきなのは、Provider固有実装、現在のAI制約、不要なUniversal ontologyです。一方、SEIを通して利用者が扱える問い、認知材料、historical context、共有可能性は深くなり得ます。

```text
thin infrastructure
  != shallow cognition
```

## 10. 文書配置の判断

今回のReviewから、次の配置を採ります。

### `SEI_PRODUCT_VALUE.md`

- 未確定なものを早まってTruthへ昇格させず、問い直せる認知対象へ外在化できる価値を追加する。
- 認知成果を一人・一AI・一Providerの一時状態へ閉じないことを、bounded sharingとともに明示する。
- Value Axisは増やさない。

### `SEI_VALUE_PROPOSITION.md`

利用者向けには、次を加える。

- まだ答えになっていない違和感や問いから始められる。
- 人・AI・Providerが変わっても、許された範囲で認知成果を引き継げる。

### `SEI_PRODUCT_VISION.md`

長期利用状態として次を強める。

- durable cognitive aperture
- bounded shared cognition
- thin infrastructure / deep cognition
- quiet assistance

### `SEI_PRODUCT_PRINCIPLES.md`

次の原則を追加する。

1. 早すぎる収束を強制しないが、必要なDecisionを避けない。
2. 認知帯域を不用意に奪わない。
3. Shared cognitionとAccess boundaryを同時に設計する。

### No Change

次は今回変更しません。

- `SEI_VALUE_MODEL.md` — V1〜V8で意味上のcoverageが十分で、新しい独立axisの必要性がない。
- `SEI_VALUE_ACCEPTANCE.md` — Product ValueのEvidence高さと各V軸のAcceptanceは現状で十分。Quiet / shared / latent-materialのactual outcomeは後続experimentで観測する。
- `SEI_DECISION_CONTINUITY.md` — Durable Cognitive ApertureはDecision Continuityと近いが、今回のブランド統合だけでcross-axis Outcome定義を変更する必要はない。
- Stable Requirements / Acceptance Scenarios — 独立したProduct failureのactual Evidenceがまだない。
- Universal Contract / Architecture — ブランド探索だけから変更しない。

## 11. alternative readingとtrade-off

| 採る方向 | 反対側の停止線 |
|---|---|
| latent materialを扱える | noiseを無限に蓄積しない |
| non-closure | Decision avoidanceにしない |
| quiet assistance | material signalを見逃さない |
| cognitive sharing | privacy / access / Responsibilityを消さない |
| durable memory | deletion / retention agencyを失わない |
| deep cognition | opaque mysticismや「深層=真実」にしない |
| symbolic coherence | Product differentiationの実証を省略しない |

Product designでは、一方を常に最大化するのではなく、Scenarioごとにどのfailureが重大かを見ます。

## 12. follow-up exploration

今回の統合はDesign / Product Value synthesisです。actualな価値確認が必要な点は、Stable Requirementへ急がず後続探索へ残します。

### latent observation

弱い違和感や未整理Observationを軽いcaptureで残し、後からEvidenceと結び付けられるか。capture taxやnoise増加も同時に観測する。

### quiet assistance

同一taskで、suggestion-heavyなSurfaceとbounded / on-demandなSurfaceを比較し、orientation、task focus、missed material signal、correction burdenを観測する。

### bounded sharing

同じ認知状態について、異なるaccess scopeを持つ人間・AIが必要な意味へ到達でき、withheld contextをUnknownやNoへ誤変換しないかを確認する。

### proactive escalation

Quiet Infrastructureを理由に重要signalを隠さないため、Conflict、reopen condition、high novelty、safety-relevant observation等をどの条件で前面化すべきかを検証する。

これらは既存ISSUE-000073、Product Access、Cognitive Workspace等の探索と重なる部分を先に利用し、独立した規範上のgapが確認された場合だけ新Issue / Requirementへ進めます。

## 13. Resolution判断

ISSUE-000077のProduct Value discoveryとしては、次が成立します。

- ブランド世界を非規範sourceとして保存した。
- H77.1〜H77.6をbenefit / failure / counterexample / existing coverageへ逆照合した。
- 新Value Axisを追加しない判断を明示した。
- 採用する洞察をProduct Value / Proposition / Vision / Principlesへ配置した。
- Value Model / Acceptance / Decision Continuity / Stable Requirementを変更しない理由を残した。
- actual検証が必要な部分をDesign hypothesisとして分離した。

したがって、上位文書への統合作業が完了した時点でISSUE-000077は**documentation / Product synthesis scopeではResolved可能**です。

```text
ISSUE-000077 Resolved
  = brand-world Product Value synthesis completed
  != quiet assistance validated in users
  != cognitive commons Adoption proven
  != new Requirement necessary
```

## 14. Evidence状態

```text
Brand source preservation: Design record available
Product Value review: Design review available
Product Value / Vision / Principles integration: Design baseline update
Executable Evidence: no new Evidence from this review
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

## 15. 関連文書

- `SEI_BRAND_WORLD_DISCOVERY_SOURCE.md`
- `SEI_PRODUCT_VALUE.md`
- `SEI_VALUE_MODEL.md`
- `SEI_VALUE_ACCEPTANCE.md`
- `SEI_DECISION_CONTINUITY.md`
- `SEI_VALUE_PROPOSITION.md`
- `../vision/SEI_PRODUCT_VISION.md`
- `../principles/SEI_PRODUCT_PRINCIPLES.md`
- `../../plan/issue/ISSUE-000077-integrate-brand-world-into-product-value-discovery.md`

## 16. Natural Japanese review

ブランド世界をProductへ持ち込む際、象徴の魅力から規範を演繹するのではなく、H77.1〜H77.6を一つずつ利用者benefit、failure、counterexample、existing coverageへ戻して検討した。

その結果、Cognitive Commons、Surface / Depth Interface、Deliberate Non-closure、Durable Cognitive Aperture、Quiet Infrastructure、Shared but not Unboundedを新しいValue Axisとして並べるより、current V1〜V8とDecision Continuityを利用世界へ翻訳し直す方が整合的だと判断した。

一方、既存文書では「まだ形を得ていない認知材料を早まって確定せず扱うこと」「認知成果を一時状態へ閉じずboundedに共有すること」「認知帯域を不用意に奪わないこと」の表現が弱かったため、Product Value / Proposition / Vision / Principlesへ役割に応じて統合する。

Value ModelやStable Requirementを増やすことを進捗とせず、Design synthesisとactual Outcome Evidenceを分離した。自然な日本語として全体を読み直し、象徴の豊かさ、Product上の具体性、Evidence強度の三つが両立するよう最終監査した。
