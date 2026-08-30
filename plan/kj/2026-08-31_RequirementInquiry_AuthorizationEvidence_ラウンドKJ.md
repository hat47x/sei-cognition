# Requirement InquiryとAuthorization EvidenceのラウンドKJ統合

更新日: 2026-08-31  
状態: **Decision-preparation KJ / ADR source**

## 0. 目的

TEI設計系列のKJ統合で残った次の二つの空白を、SOZA既存ADRへ戻しながら検討する。

- G01: Stable Question ID、Requirement Decision、Decision Impactをどこが所有するか。
- G04: TEI等のProviderが行ったAuthorization評価をSOZAのDecision Memoryからどう参照するか。

文化的体系は、今回も分類軸には用いない。問い・境界・時間差・再帰関係の見落としを探す補助線としてのみ用いる。

---

# 第1ラウンド　生カード

問い: **過去の設計質問を再利用しつつ、新しいEvidenceでは再審査できるために、何を耐久的意味として残す必要があるか。**

### Q001

設計時の確認質問はchat turnではなく、意味のあるQuestionとして後から参照できる必要がある。

### Q002

質問文の言い回しを改善しただけで、意味上別のQuestionへ変えてはならない。

### Q003

一方、問いの意味や対象が変わった場合は、同じQuestion IDへ押し込まず別のlogical identityまたはsemantic revisionとして扱う必要がある。

### Q004

AIが回答候補を推定したことと、利用者・組織が回答をDecisionしたことを同一視しない。

### Q005

「一度回答した質問を聞き返さない」はUI上の絶対規則ではなく、同じ前提下で既存Decisionを再利用する最適化である。

### Q006

新しいEvidenceやConstraintが過去Decisionと衝突した場合、黙って上書きせず再審査を起動できる必要がある。

### Q007

再審査の起点は、過去Decisionそのものを削除するのではなく、何が変わったため再検討が必要になったかを辿れることが重要である。

### Q008

質問catalogや典型業務の確認観点は、Questionそのものの履歴とは別であり、Cognitive MethodやTEI Design Knowledgeとして交換・改訂できる。

### Q009

TEI Editor固有の「このダイアログを出した」「このsessionではdismissした」という状態をSOZA CoreのDecision Memoryへ持ち込む必要はない。

### Q010

Requirementに関するDecisionも、Recommendation / Decision / Responsibility / Semantic Lineageの既存境界を再利用できる。

### A001

SOZAのDecisionが存在しても、TEIやSaaS等で実行権限が成立したことにはならない。

### A002

ProviderがAuthorizationを`allowed`と判定しても、それだけでSOZA側のDecisionが存在したことにはならない。

### A003

誰がDecisionを担ったかというResponsibilityと、実行時にAuthorityが成立したことは別である。

### A004

認証・認可方式はProviderごとに異なり、legacy password、OIDC、RBAC、ABAC、resource-specific policy等をSOZA Coreへ統一Schemaとして持ち込むべきではない。

### A005

Entry AuthorizationとResource / Subject Authorizationは異なる時点・対象で評価され得るため、一つのbooleanへ潰すと監査情報を失う。

### A006

Authorization評価結果を後から検証する場合、当時のpolicyや対象、時点、Provider側のevaluation reference等を必要な粒度で特定できることが重要である。

### A007

現在のpolicyで拒否されることと、過去の実行時点で許可されていたことは両立し得る。

### A008

Providerが返したsuccess acknowledgementだけでは、認可がどのscopeに対して成立したかを示す十分なEvidenceとは限らない。

### A009

Authorization Providerが一時的に利用不能な場合、`not evaluated / unknown`を自動的に`denied`へ変換すると認識状態を失う。

### A010

SOZAが必要とするのはAuthorization engineそのものではなく、Decision / Executionの監査に必要な外部評価結果を参照し、来歴を辿れることだと考えられる。

---

# 第2ラウンド　初期束ね

## B01　Question identityと質問文を分ける

- Q001-Q003

質問の意味上のidentityと、そのとき人間へ見せた文言・UIを分離する。

## B02　AI候補とRequirement Decisionを分ける

- Q004,Q010

AIの候補はRecommendation、採用・不採用・保留はDecisionとして既存境界を使える。

## B03　「聞き返さない」をDecision Memoryの再利用として読む

- Q005-Q007

同じ前提なら既存Decisionを再利用し、新Evidenceではlineageとbasisを残して再Decisionする。

## B04　質問catalogとEditor sessionを耐久意味から分ける

- Q008,Q009

質問を生む知識・Methodと、UI session状態をQuestion / Decisionの正本へ混ぜない。

## B05　Decision / Responsibility / Authorizationを分ける

- A001-A003

認知・判断上の責任と、実行時Authorityを分離する。

## B06　Authorizationの固有方式と評価Evidenceを分ける

- A004,A006,A010

SOZAは認可方式を所有せず、必要な外部評価結果を参照する。

## B07　認可の多段性と時間差を保つ

- A005,A007

Entry / Resourceの別評価、past / current policy差を一つへ潰さない。

## B08　Authorization evaluationの認識状態を正直にする

- A008,A009

acknowledgementを十分なEvidenceとせず、未評価を拒否と混同しない。

---

# 第3ラウンド　核融合法

8束の表札を外して核を取り出し、4核へ融合した。

## N01　Questionは耐久的な意味資産、質問文とUIは交換可能な表現である

- from: B01,B04
- residual: 質問catalogはMethod / Design Knowledgeとして別に改訂できる。

## N02　設計質問への回答は既存Decision Memoryで扱い、再質問ではなく再判断として履歴を伸ばす

- from: B02,B03
- residual: AI推定はRecommendationでありDecisionではない。

## N03　AuthorizationはProviderが評価し、SOZAはDecision / Responsibilityから独立した外部Evidenceとして必要な来歴を参照する

- from: B05,B06
- residual: SOZAはAuthorization engineを所有しない。

## N04　認可結果は対象・scope・時点・評価状態を失わない

- from: B07,B08
- residual: Entry / Resource分離、past / current分離、not evaluated != deniedを保持する。

## 戻し照合

20枚へ戻したところ、初回融合ではQ002「質問文だけの改善」とA008「success acknowledgement不足」が弱くなっていた。

N01へ「presentation revision != question semantic revision」、N04へ「acknowledgement != sufficient authorization evidence」を追記することで回復した。

補正後の主要意味核欠落: **0件**

---

# 第4ラウンド　本質追及

問い: **SOZAが所有すべきものと、TEI / Providerへ残すものをどう分けるか。**

## I1　Question / Decisionの意味履歴はSOZA側で耐久化する

SOZAは、Questionのlogical identity、関連Recommendation / Decision、basis、unresolved、Responsibility、Semantic Lineageを再利用する。

新しいUniversal `RequirementDecision`型を作らなくても、通常DecisionがQuestionを対象・contextとして参照できれば意味を保てる可能性が高い。

## I2　質問catalogと表示・sessionはMethod / Authoring側へ置く

どの問いをいつ候補提示するかはCognitive MethodやTEI Design Knowledge / Authoring Profileが担える。

質問文、表示タイミング、dismiss状態、chat turnはSOZA Decision Memoryの正本にしない。

## I3　AuthorizationはSOZAのDecisionから独立したProvider boundaryで成立する

SOZA Decisionは実行の意味上の採用判断であって、Provider Authorizationではない。

Authorization Providerは自らのauthoritative policy / credential / resource stateを使って評価する。

## I4　SOZAが保持するのはAuthorization評価の監査可能な参照である

SOZAは認可方式を統一せず、必要な場合に、誰／何が、いつ、どのscope / resourceに対して、どのProvider評価を参照したかをObservation / Assurance / EvidenceUse等から辿れるようにする。

---

# 第5ラウンド　A型図解

```text
Cognitive Method / TEI Design Knowledge
       │ question candidate
       ▼
Question logical identity ───── presentation / wording
       │                              │
       │ AI proposes                  └─ replaceable authoring detail
       ▼
Recommendation
       │ human/org decides
       ▼
Decision ── basis / unresolved / responsibility
       │
       │ new evidence / changed constraint
       └──────────────→ successor Decision
                         via Semantic Lineage

Decision
   │ does not grant authority
   ▼
Provider crossing
   │
   ├─ Entry Authorization evaluation
   └─ Resource / Subject Authorization evaluation
              │
              ▼
      evaluation Observation / Assurance
              │
              └────→ Decision / Execution audit evidence
```

### 重要な非同一性

```text
Question wording != Question semantic identity
AI answer proposal != Requirement Decision
previous answer reuse != permanent suppression of inquiry
Decision != Responsibility != Authorization != Execution
Authorization acknowledgement != sufficient Evidence
not evaluated != denied
past authorization != current authorization
```

---

# 第6ラウンド　B型文章化

設計時にAIが確認質問をする仕組みを、単なるEditorの便利機能として扱うと、一度答えた内容がchat履歴の消失とともに失われる。逆に、質問ダイアログやsession状態をSOZA Coreへ持ち込むと、現在のUI実装が耐久的な意味モデルへ入り込む。

必要なのは、問いの意味と表示方法を分けることである。たとえば「変更履歴を残すか」という問いは、文言を自然に直しても同じ問いであり得る。一方、対象や前提が変わり問いの意味が変わったなら、別Questionまたは明示的なrevisionとして扱う。AIが回答候補を作った場合はRecommendationであり、利用者や組織が採用・不採用・保留を決めたときにDecisionになる。

この整理を採ると、「一度した質問を聞き返さない」というUXも、永久的な質問禁止ではなく、同じ前提のもとでは過去Decisionを再利用するという意味になる。新しいEvidenceやConstraintが現れたときは、過去回答を削除したり黙って上書きしたりせず、何が変わったかをbasisとして後継Decisionを作れる。質問catalogや表示タイミングはCognitive MethodやTEI Authoring側で改善してよく、SOZAのDecision Memoryとは分離できる。

Authorizationも同様に、判断と実行の間にある独立境界として扱う。SOZAでCapabilityを選ぶDecisionがあっても、TEIやSaaSで実行するAuthorityは成立しない。逆にProviderがある操作を許可できる状態でも、その操作を行うDecisionが存在するとは限らない。

認可方式そのものはProviderへ残す。legacy password、OIDC、RBAC、ABAC、resource policy等をSOZAへ統一Schemaとして持ち込まない。一方、後から監査するときには、実行時点でどのProviderがどのscopeやresourceについて何を評価したかを辿れる必要がある。Entry AuthorizationとResource Authorizationは別評価になり得て、現在のpolicyと過去のpolicyも異なり得る。評価できなかったことを拒否へ、Providerのsuccess acknowledgementを十分な認可Evidenceへ自動変換してはならない。

したがってSOZAが所有すべき中心はAuthorization engineではなく、外部評価をObservation / Assurance / EvidenceUse等として必要な文脈から参照し、Decision / Executionの来歴へ結べることにある。

---

# 第7ラウンド　Decision preparation

## D1 Requirement Inquiry

次をADR候補とする。

- Universal `RequirementDecision`型を新設せず、既存Question / Recommendation / Decision / SemanticLineageを再利用する。
- Questionはlogical identityを持ち、presentation wordingと分ける。
- question catalog / trigger logicはCognitive Method / Authoring Profile側へ置く。
- AI回答候補はRecommendation、利用者・組織の回答はDecision。
- 同じ前提では既存Decisionを再利用できる。
- 新Evidenceでは既存Decisionを上書きせず、successor Decisionを作る。
- Universal `DecisionImpact`型も現時点では追加せず、Derivation / basis / Question / SemanticLineageで再審査理由を表せるかを先に試す。

## D2 Authorization Evidence

次をADR候補とする。

- Authorization engine / policy ontologyをSOZA Coreへ追加しない。
- Decision / Responsibility / Authorization / Executionを分離する。
- ProviderのAuthorization evaluationは、必要に応じてObservation / Assurance / EvidenceUseとして参照する。
- Universal `AuthorizationResult` Artifactは現時点では追加しない。
- Entry / Resource、past / current、verified / not evaluated等の意味を一つのbooleanへ潰さない。
- exact historical reconstructionが必要な場合はProvider evaluation referenceやpolicy bindingをExactArtifactBinding等で辿れる設計を許す。

この二判断をADR-0015 / ADR-0016候補へ進める。
