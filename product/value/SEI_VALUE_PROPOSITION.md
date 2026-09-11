# SEI Value Proposition

更新日: 2026-09-01  
状態: **Current Product Value Proposition Baseline**

## 1. この文書の役割

この文書は、SEIのProduct Valueを**利用者がどのような問題を解くために使い、どのような価値を受け取る製品なのか**という観点から表現します。

`SEI_PRODUCT_VALUE.md`が長期的に失ってはならない価値を定め、`SEI_VALUE_MODEL.md`がV1〜V8として評価軸を定めるのに対し、本書はそれらを利用場面へ接続します。

新しいValue AxisやUniversal Core概念を追加する文書ではありません。Value Axisの意味、優先関係、Acceptanceの正本は既存文書を維持します。

## 2. 主に解く問題

SEIが主に対象とするのは、**複数の人間、AI、外部サービス、既存システムが関与し、途中で情報・手段・前提が変化し得る判断仕事**です。

この種の仕事では、結果だけを保存しても、後から次の問いに答えられなくなることがあります。

- 当時、何を事実として見ていたのか。
- 何が不明または対立したままだったのか。
- どの資料やObservationを根拠にしたのか。
- AIや他者の提案と、最終Decisionはどこで分かれていたのか。
- 誰がどの文脈でResponsibilityやAuthorityを担っていたのか。
- なぜそのCapability / Providerを選んだのか。
- 後から何が変わり、判断を見直す必要が生じたのか。

通常のログ、チャット履歴、ワークフロー履歴、ドキュメント置き場は、それぞれ重要です。ただし、それらだけでは「判断の意味」を実行方式や会話の流れから独立して残しにくい場合があります。

SEIは、その隙間を埋めます。

## 3. 中核となる価値提案

### 3.1 後から判断へ戻れる

利用者は、過去のDecisionを現在の状態だけから推測するのではなく、当時のEvidence、Unknown、Conflict、Constraint、Recommendation、Responsibility、参照Artifactへ戻れます。

目的は、過去を完全に再演することではありません。**その時点で何が見えており、何を受け入れて判断したかを、必要な精度で再構成できること**です。

### 3.2 分からないことを消さずに進める

SEIは、UnknownやConflictが残っていること自体を失敗とみなしません。

期限や外部条件のために不確実なままDecisionする場合でも、何が未解決だったかを残し、後から新しいEvidenceを加えて再開できます。

### 3.3 AIへ広く委ねても、提案と決定を混同しない

AIの能力が高まるほど、調査、比較、要約、Recommendation、場合によっては委任されたDecisionまで広く任せられます。

そのときも、Recommendation、Decision、Authority、Action Intent、Executionの意味差を必要に応じて維持し、**どこまでを誰に委ねたか**を後から読める状態を価値とします。

### 3.4 手段を交換しても判断の意味を持ち運べる

Prompt、AIモデル、Skill、workflow engine、SaaS、TEI、custom code、Storage等は変わり得ます。

SEIは、これらのRealizationやProviderを交換しても、Intent、Observation、Decision、Responsibility、Provenance等の耐久的な意味を持ち運べることを価値とします。

### 3.5 軽く始め、必要な場面だけ深くできる

利用開始時に完全なontologyや監査項目をすべて入力することを前提にしません。

低影響な場面では、問い、主要なObservation、未解決点、Decision等から始められます。影響や不可逆性が高まる場面では、basis、Responsibility、Exact Binding、Authority、Provenance等を厚くできます。

軽い利用と厳密な利用を別製品へ分けるのではなく、同じcanonical meaningへ戻れる連続した利用体験を目指します。

## 4. 主な利用者・関与者

SEIでは、利用者種別を固定的な権限モデルへ直結させません。ただし、製品設計上は少なくとも次の関与者を想定します。

### 判断を担う人・組織

Decisionを行い、必要なResponsibilityやAuthorityを担います。すべての案件で人間が最終Decisionを行うことを必須にはしません。

### 調査・分析・設計を担う人

Evidenceを集め、問いを深め、Cognitive Methodを適用し、Recommendationや設計案を作ります。

### レビュー・監査を担う人

過去のDecision、basis、変更来歴、未解決事項、Authority等を読み直します。

### AI

調査、整理、比較、Method Application、Recommendation、委任された範囲のDecision等を担い得ます。actor種別だけからAuthorityや信頼を推定しません。

### 外部システム・Capability Provider

情報取得、計算、業務処理、実行等を担います。SEI自身の内部構造へ同化させるのではなく、必要な境界から接続します。

## 5. 価値が特に大きくなりやすい場面

SEIは、次の条件が複数重なるほど価値を出しやすいと考えます。

- AIや外部サービスを複数利用する。
- 数か月から数年後にDecisionを読み直す必要がある。
- 担当者、AIモデル、Provider、組織構成が途中で変わり得る。
- Evidenceが不完全または相互にConflictする。
- RecommendationとDecisionを分ける必要がある。
- 監査、説明責任、再検討、引継ぎが重要である。
- 実行結果を受けて、前提や判断を更新する循環がある。

## 6. SEIを第一選択にしなくてもよい場面

次のような仕事では、SEIを導入する価値が小さい可能性があります。

- 単純で短命な処理で、後から判断理由を読み直す必要がほぼない。
- deterministicな変換処理だけで完結し、判断や不確実性が存在しない。
- 既存システムの監査ログだけで必要な説明が十分に成立する。
- 主目的がworkflow throughputやjob schedulingの最大化である。

SEIは、すべての処理を自らの中へ取り込むことを価値としません。

## 7. 利用者に約束したいこと

製品としてのSEIは、長期的に少なくとも次を約束できる状態を目指します。

1. **判断の文脈を失いにくいこと。**
2. **不確実性や異論を都合よく消さないこと。**
3. **AI・人間・Providerの役割を必要な粒度で読み分けられること。**
4. **手段を交換しても耐久的な意味を持ち運べること。**
5. **軽い利用から監査可能な厳密利用へ連続的に深められること。**

この約束は、単一のUI、API、Storage、AIモデル、workflow engineへ依存させません。

## 8. 価値の測定

利用者価値の評価は、実装量やCI件数だけでは行いません。

Adoption / Outcome Evidenceを収集できる段階では、たとえば次を検討します。

- 過去Decisionのbasisを再構成できた割合と、再構成に要する負担。
- ProviderやAI実装を交換した後も、重要な意味を引き継げたか。
- Unknown / Conflict / residualを保持したことが、後日の再検討に役立ったか。
- 人間とAIが同じcanonical dataから、必要な意味を読み取れたか。
- 利用者が過剰な入力負担なしに、必要なときだけ詳細化できたか。

ただし、これらを現時点で実証済みとは扱いません。現在はProduct Value / Design baselineであり、実利用者を通したAdoption / Outcome Evidenceは`Not Yet Verified`です。

## 9. 関連文書

- `SEI_PRODUCT_VALUE.md`
- `SEI_VALUE_MODEL.md`
- `SEI_VALUE_ACCEPTANCE.md`
- `SEI_VALUE_TRACEABILITY.md`
- `../definition/SEI_PRODUCT_SHAPE.md`
- `../vision/SEI_PRODUCT_VISION.md`
- `../principles/SEI_PRODUCT_PRINCIPLES.md`

## 10. Natural Japanese review

current Product Value、V1〜V8、Product Vision、Progressive Explicitness、Decision / Authority / Execution境界、Provider Independenceへ戻り、既存の意味を利用者から見た価値へ翻訳した。新しいValue AxisやUniversal概念を追加せず、対象になりやすい仕事、関与者、価値が小さい場面、将来のOutcome評価候補を整理した。その後、規範強度やEvidence状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
