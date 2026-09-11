# SOZA Value Proposition

更新日: 2026-09-11  
状態: **Current Product Value Proposition Baseline — Decision Continuity reflected**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを**利用者がどのような問題を解くために使い、どのような価値を受け取る製品なのか**という観点から表現します。

`SOZA_PRODUCT_VALUE.md`が長期的に失ってはならない価値を定め、`SOZA_VALUE_MODEL.md`がV1〜V8として評価軸を定めるのに対し、本書はそれらを利用場面へ接続します。

Decision Continuityは新しいValue Axisではなく、V1〜V8が実際の利用者の一つの判断仕事で成立したときに現れるcross-axis Product Outcomeです。詳細は`SOZA_DECISION_CONTINUITY.md`を参照します。

## 2. 一言でいう価値

SOZAが利用者へ届けたい最も短い約束は、次です。

> **あとで戻っても、別のAIを使っても、情報が変わっても、過去を捏造せず判断の続きを始められる。**

そのためにSOZAは、単なる会話履歴やログではなく、問い、Observation、Unknown / Conflict、Recommendation、Decision、basis、Responsibility、Provenance、Revision等の耐久的な意味を外在化します。

## 3. 主に解く問題

SOZAが主に対象とするのは、**複数の人間、AI、外部サービス、既存システムが関与し、途中で情報・手段・前提が変化し得る判断仕事**です。

この種の仕事では、結果だけを保存しても、後から次の問いに答えられなくなることがあります。

- 当時、何を事実として見ていたのか。
- 何が不明または対立したままだったのか。
- どの資料やObservationを根拠にしたのか。
- AIや他者の提案と、最終Decisionはどこで分かれていたのか。
- 誰がどの文脈でResponsibilityやAuthorityを担っていたのか。
- なぜそのCapability / Providerを選んだのか。
- 後から何が変わり、判断を見直す必要が生じたのか。
- 数日後に戻ったとき、どこまで進んでいたのか。
- 今知っていることを、当時から知っていたかのように記憶していないか。

通常のログ、チャット履歴、ワークフロー履歴、ドキュメント置き場は、それぞれ重要です。ただし、それらだけでは「判断の意味」を実行方式や会話の流れから独立して残しにくい場合があります。

SOZAは、その隙間を埋めます。

## 4. 中核となる価値提案

### 4.1 判断の続きを取り戻せる

利用者は、履歴を最初から読み直さなくても、現在の問い、Decision、主要basis、未解決事項、Decision後の変化、reopen conditionへ戻れる状態を目指します。

目的は、過去を完全に再演することではありません。**その時点で何が見えており、何を受け入れて判断し、その後何が変わったかを必要な精度で再構成し、続きを始められること**です。

これは単なる「記憶機能」ではありません。chat history、UI state、AI contextを失ってもcanonical meaningから再構成できることを重視します。

### 4.2 分からないことを消さずに進める

SOZAは、UnknownやConflictが残っていること自体を失敗とみなしません。

期限や外部条件のために不確実なままDecisionする場合でも、何が未解決だったかを残し、後から新しいEvidenceを加えて再開できます。

未解決を保存する価値は、監査だけではありません。「次に何を調べるか」「何が変われば見直すか」を未来へ渡すことにあります。

### 4.3 AIへ広く委ねても、提案と決定を混同しない

AIの能力が高まるほど、調査、比較、要約、Recommendation、場合によっては委任されたDecisionまで広く任せられます。

そのときも、Recommendation、Decision、Authority、Action Intent、Executionの意味差を必要に応じて維持し、**どこまでを誰に委ねたか**を後から読める状態を価値とします。

AIが誤った場合は、suggestionを修正・再分類・却下できることを重視します。AIが使えないときも、判断記憶の基本操作まで停止させません。

### 4.4 手段を交換しても判断の意味を持ち運べる

Prompt、AIモデル、Skill、workflow engine、SaaS、TEI、custom code、Storage等は変わり得ます。

SOZAは、これらのRealizationやProviderを交換しても、Intent、Observation、Decision、Responsibility、Provenance等の耐久的な意味を持ち運べることを価値とします。

Provider交換可能性は技術的な美しさのためだけではありません。利用者が一つのAIや実行基盤へ判断文脈ごと閉じ込められず、仕事を続けられるためにあります。

### 4.5 軽く始め、必要な場面だけ深くできる

利用開始時に完全なontologyや監査項目をすべて入力することを前提にしません。

低影響な場面では、問い、主要なObservation、未解決点、Decision等から始められます。影響や不可逆性が高まる場面では、basis、Responsibility、Exact Binding、Authority、Provenance等を厚くできます。

軽い利用と厳密な利用を別製品へ分けるのではなく、同じcanonical meaningへ戻れる連続した利用体験を目指します。

重要なのは、detailを増やせることだけではありません。**detailを増やさないと価値が出ない製品にしないこと**です。

## 5. SOZAの差別化仮説

SOZAはchat、note、wiki、issue tracker、workflow、audit logを置き換えることを価値としません。それらはSOZAが参照・接続する重要なArtifact / Surface / Providerになり得ます。

差別化仮説は、これらに対して別のProduct guaranteeを置くことです。

```text
raw history / documents / logs
  + canonical semantic distinction
  + historical integrity
  + resumable projection
  → durable decision context
```

たとえばraw chatは会話の流れを豊かに残せますが、後日RecommendationとDecisionを分けたり、Decision後の情報を当時basisから分離したりする責務が利用者側へ残る場合があります。

SOZAはその再構成責務の一部をProductとして引き受けます。

ただし、この差別化は仮説です。raw chatやsimple noteと比べて再開負担・誤帰属・修正負担を実質的に減らせないなら、追加構造そのものを価値とはみなしません。

## 6. 主な利用者・関与者

SOZAでは、利用者種別を固定的な権限モデルへ直結させません。ただし、製品設計上は少なくとも次の関与者を想定します。

### 判断を担う人・組織

Decisionを行い、必要なResponsibilityやAuthorityを担います。すべての案件で人間が最終Decisionを行うことを必須にはしません。

### 調査・分析・設計を担う人

Evidenceを集め、問いを深め、Cognitive Methodを適用し、Recommendationや設計案を作ります。

### レビュー・監査を担う人

過去のDecision、basis、変更来歴、未解決事項、Authority等を読み直します。

### 将来の自分

Decision Continuityのfirst Product Sliceでは、数日後・数週間後の同じ利用者も重要な「別の読み手」とみなします。

当時のworking memoryやAI conversationへ依存せず、過去の自分が何を知り、何を決め、何を残したかへ戻れることを重視します。

### AI

調査、整理、比較、Method Application、Recommendation、委任された範囲のDecision等を担い得ます。actor種別だけからAuthorityや信頼を推定しません。

### 外部システム・Capability Provider

情報取得、計算、業務処理、実行等を担います。SOZA自身の内部構造へ同化させるのではなく、必要な境界から接続します。

## 7. 価値が特に大きくなりやすい場面

SOZAは、次の条件が複数重なるほど価値を出しやすいと考えます。

- AIや外部サービスを複数利用する。
- 数日から数年後にDecisionを読み直す必要がある。
- 中断、並行作業、引継ぎが多い。
- 担当者、AIモデル、Provider、組織構成が途中で変わり得る。
- Evidenceが不完全または相互にConflictする。
- RecommendationとDecisionを分ける必要がある。
- 監査、説明責任、再検討、引継ぎが重要である。
- 実行結果を受けて、前提や判断を更新する循環がある。
- 「現在は知っているが、当時は知らなかった」ことを取り違えるコストが高い。

言い換えると、SOZAは**判断寿命・文脈変動・再訪頻度・不確実性・誤再構成コスト**が高いほど価値を出しやすい製品です。

## 8. SOZAを第一選択にしなくてもよい場面

次のような仕事では、SOZAを導入する価値が小さい可能性があります。

- 単純で短命な処理で、後から判断理由を読み直す必要がほぼない。
- deterministicな変換処理だけで完結し、判断や不確実性が存在しない。
- 既存システムの監査ログだけで必要な説明が十分に成立する。
- 主目的がworkflow throughputやjob schedulingの最大化である。
- raw note / chatだけで十分に再開でき、SOZAの意味構造が追加負担にしかならない。

SOZAは、すべての処理を自らの中へ取り込むことを価値としません。

## 9. 利用者に約束したいこと

製品としてのSOZAは、長期的に少なくとも次を約束できる状態を目指します。

1. **中断や環境変化の後でも、判断の続きを取り戻せること。**
2. **判断の文脈を失いにくく、過去と現在を取り違えにくいこと。**
3. **不確実性や異論を都合よく消さないこと。**
4. **AI・人間・Providerの役割を必要な粒度で読み分けられること。**
5. **手段を交換しても耐久的な意味を持ち運べること。**
6. **軽い利用から監査可能な厳密利用へ連続的に深められること。**
7. **AIが誤ったり利用不能でも、利用者が修正・継続できること。**

この約束は、単一のUI、API、Storage、AIモデル、workflow engineへ依存させません。

## 10. 価値の測定

利用者価値の評価は、実装量やCI件数だけでは行いません。

Adoption / Outcome Evidenceを収集できる段階では、たとえば次を検討します。

- 過去Decisionのbasisを再構成できた割合と、再構成に要する負担。
- 中断後にcurrent question / Decision / unresolved / changed-since-Decisionへ到達するまでの時間と操作。
- post-decision情報をhistorical basisへ誤帰属する割合・事例。
- RecommendationをDecisionとして誤読する割合・事例。
- ProviderやAI実装を交換した後も、重要な意味を引き継げたか。
- Unknown / Conflict / residualを保持したことが、後日の再検討に役立ったか。
- 人間とAIが同じcanonical dataから、必要な意味を読み取れたか。
- 利用者が過剰な入力負担なしに、必要なときだけ詳細化できたか。
- AI suggestionの修正・却下に必要な負担。
- raw chat / simple note等の妥当な代替と比べ、SOZAの追加構造に実質的な価値差があるか。
- その価値差がcapture / review overheadを上回るか。

初期評価では固定KPI thresholdを先取りしません。量的観測と質的な再開失敗例を組み合わせ、Product hypothesisのどこが成立し、どこが反証されたかを見ます。

ただし、これらを現時点で実証済みとは扱いません。現在はProduct Value / Design baselineであり、実利用者を通したDecision ContinuityのAdoption / Outcome Evidenceは`Not Yet Verified`です。

## 11. 関連文書

- `SOZA_PRODUCT_VALUE.md`
- `SOZA_VALUE_MODEL.md`
- `SOZA_VALUE_ACCEPTANCE.md`
- `SOZA_VALUE_TRACEABILITY.md`
- `SOZA_DECISION_CONTINUITY.md`
- `../interaction/SOZA_FIRST_USABLE_PRODUCT_SLICE.md`
- `../definition/SOZA_PRODUCT_SHAPE.md`
- `../vision/SOZA_PRODUCT_VISION.md`
- `../principles/SOZA_PRODUCT_PRINCIPLES.md`

## 12. Natural Japanese review

current Product Value、V1〜V8、resume-first Product Slice、Decision Continuity synthesis、Product Vision、Progressive Explicitness、Decision / Authority / Execution境界、Provider Independenceへ戻り、既存の意味を利用者から見た価値へ再接続した。

従来の「後から判断へ戻れる」を、単なるhistorical reconstructionではなく「中断やAI / Surface変更後にも判断の続きを始められる」価値へ深めた。同時に、速いresumeだけを成功とせず、historical誤帰属、Recommendation / Decision混同、capture overhead、AI correction / degradationまでProduct Value評価へ含めた。

Decision Continuityを新しいValue AxisやUniversal概念へ追加せず、既存V1〜V8のcross-axis Outcomeとして扱う境界を維持している。自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。