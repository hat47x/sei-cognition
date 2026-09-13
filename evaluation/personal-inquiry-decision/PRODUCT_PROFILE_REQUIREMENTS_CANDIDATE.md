# Personal Inquiry Continuity Profile — Candidate Requirements

更新日: 2026-09-10  
状態: **Candidate Product Profile / Requirement Deepening — Not Stable Requirement**  
関連: GitHub Issue #359 / PR #358 / `README.md`

## 1. この文書の役割

この文書は、PR #358で導入した `Personal Inquiry / Decision Workspace` 仮説を、将来 `requirements/` 配下の正式なProduct Requirementへ反映できる粒度まで分解するための候補要件書である。

現時点では、ここに記載した `PIC-*` をSEI全体のStable Requirementとは扱わない。

```text
Candidate Product Profile Requirement
  != Stable Product Requirement
  != Universal Semantic Contract
  != UI specification
  != implementation decision
```

この文書の目的は、個人レベルでSEIのProduct Valueを実際に確認できる最小の製品像を明確化し、そのために既存REQ-0001〜REQ-0022で十分な部分と、独立した追加Requirementが必要になり得る部分を切り分けることである。

## 2. 中心仮説の更新

前段では仮称を `Personal Inquiry / Decision Workspace` としたが、深掘りの結果、個人向けの中心価値はDecision管理だけでは狭すぎる。

個人の長期的な調査・比較・設計・学習では、問いがDecisionへ閉じず、長期間openなまま成熟することがある。したがって中心を次へ置く。

> **時間、AI、資料、作業環境が変わっても、一つのInquiryについて「何を見て、何がまだ分からず、何を考え、何を決め、何が変わったか」を失わず、短い再定位から続きを始められること。**

設計上の仮称を **Personal Inquiry Continuity Profile** とする。

Decision MemoryはこのProfileの重要な一部だが、InquiryをDecisionへ強制的に収束させない。

```text
Personal Inquiry Continuity
  contains Decision Memory when Decision exists
  != Decision tracker only
  != chat archive
  != note-taking app
  != task manager
```

## 3. Target Job

### 3.1 Primary Job

利用者は、数日から数か月以上にわたり、AI conversation、Web、文書、コード、メモ等を行き来しながら一つの問いを考える。

その途中で作業を中断したり、AIモデルや会話threadを変えたり、別の資料を追加したりしても、後から次へ戻りたい。

1. 何を考えていたか。
2. 何が重要だと見ていたか。
3. 何がまだ分からない、または食い違っていたか。
4. どの提案や仮説が存在したか。
5. 何かを決めていたなら、何を何に基づいて決めたか。
6. その後、何が新しく分かったか。
7. 今どこから再開すべきか。

### 3.2 Secondary Job

保存したInquiry contextを、特定のAI会話履歴へ依存せず別のAI、人間、toolへ渡し、同じ意味境界を保ったまま続きを始める。

### 3.3 適合する題材

first value validationでは、次のような低〜中影響で反復的な個人判断・個人探究を主対象とする。

- 個人プロジェクトの技術・ツール・方式選定
- 学習テーマや教材の比較
- 機器、サービス、作業環境の比較検討
- 趣味、旅行、創作、調査の計画
- 長期的な設計課題や個人研究

### 3.4 first profileの非対象

- 医療、法務、重大な金融判断等、専用の安全設計を要するhigh-stakes用途
- 多人数承認、法的権限、職務分掌が製品価値の中心となる業務
- 汎用全文書管理
- 汎用タスク管理
- 常時稼働するagent orchestration
- workflow throughput最適化
- 「何でも覚える」ライフログ

## 4. 利用者が意識する概念とcanonical meaningを分ける

個人利用者へUniversal Contract用語を直接操作させることを前提にしない。

人間向けSurfaceでは、たとえば次の自然な概念を使える。

| 利用者から見た概念 | canonical meaningへの接続例 | 備考 |
|---|---|---|
| 問い | Inquiry / Question context | UI上の「案件」をUniversal entityにしない |
| 見つけたこと | Observation / Evidence / Interpretation候補 | 自動分類をTruthにしない |
| まだ分からない | Unknown | 空欄と区別する |
| 食い違い | Conflict | latest winsで消さない |
| 考え・仮説 | Interpretation / Hypothesis | Observationと混ぜない |
| AIの提案 | Recommendation | Decisionへ自動昇格しない |
| 自分が決めたこと | Decision | basis / residualへ戻れる |
| 後で見直す条件 | residual / reopen information | 固定workflow stateにしない |
| その後分かったこと | later Observation / Evidence | historical basisへ遡及混入しない |

`Workspace`、`Case`、`Thread`、`Session`等はProduct / Projection上のworking setとして実現できるが、このProfileのためだけにUniversal Coreへ追加しない。

## 5. 設計原則

### 5.1 Inquiry-first / Decision-optional

InquiryはDecisionがなくても成立する。

「Decisionが無い」ことと「未完了で失敗した」ことを同一視しない。

### 5.2 Capture first, semantic commitment later

利用者はまず自然な文章や参照を追加できる。意味分類が必要な場合は段階的に明示する。

入力時の摩擦を減らすためにAIやrule-based処理が分類候補を出してよいが、それをcanonical truthへ黙って昇格させない。

### 5.3 Historical integrity over convenient rewriting

現在の要約を便利に更新できても、過去Decisionや過去時点の認識状態を書き換えない。

### 5.4 Reorientation before exhaustive recall

製品の第一出口は「すべてを検索できること」ではなく、**短い情報から現在地へ戻れること**とする。

### 5.5 AI is an accelerator, not semantic dependency

LLMはcapture支援、比較、Cognitive Method、Recommendation、要約、handoff生成等に使えるが、保存済み判断記憶を読むための必須依存にしない。

### 5.6 Local personal control before collaboration complexity

first profileではsingle-user local利用を成立させる。network、team membership、enterprise IdPを最低利用条件にしない。

## 6. Candidate Requirements

以下の `PIC-*` はProfile内での規範候補である。

優先度は次を使う。

- **MUST-PROFILE** — first usable personal profileの価値検証に必要。
- **SHOULD-PROFILE** — Product Valueを強めるが、最初の実証を阻害するなら遅延可能。
- **LATER** — first value gate通過後に評価する。

### PIC-001 — Minimal Inquiry Start

**Priority:** MUST-PROFILE

利用者は、原則として一つの自然文の問いだけからInquiryを開始できなければならない。

開始時点でGoal、Constraint、Responsibility、Source、Exact Binding等の最大field setを要求してはならない。

必要な意味は後から追加・詳細化できること。

**意図:** Progressive Explicitnessを個人利用の開始摩擦へ具体化する。

### PIC-002 — Decisionを要求しないInquiry Continuity

**Priority:** MUST-PROFILE

InquiryはDecisionが一度も記録されていなくても、Observation、Unknown、Conflict、Hypothesis、Method Application、Recommendation、residual等を保持し、後から再開できなければならない。

製品Surfaceは「Decisionなし」を自動的に未完了エラーへ変換してはならない。

### PIC-003 — Friction-bounded Capture

**Priority:** MUST-PROFILE

利用者は、文章、URL参照、ファイル由来の要点、AI会話からの要点等を、追加のたびにSEI Contract型名を選択せず投入できなければならない。

意味分類が必要な場合、Surfaceまたは支援機構は候補を提示できるが、分類負担を利用者へ全面的に転嫁しない。

### PIC-004 — Provisional Semantic Extraction

**Priority:** SHOULD-PROFILE

AIまたはheuristic処理が自然文やchat transcriptからObservation、Unknown、Conflict、Hypothesis、Recommendation、Decision等の候補を抽出する場合、抽出結果がsource自体や利用者の確定判断と同一でないことを保持できなければならない。

少なくとも、利用者またはPolicyが未確認の自動抽出をDecisionへ黙って昇格させてはならない。

この候補層をUniversal Contractとして要求するものではない。

### PIC-005 — Source / Claim Separation

**Priority:** MUST-PROFILE

外部資料、AI回答、利用者メモ等を取り込むとき、必要な場合に「資料が何を述べたか」と「SEI利用者またはAIがそれをどう解釈したか」を区別して後から辿れること。

sourceの存在だけを、その内容のTruthやAssuranceとみなしてはならない。

### PIC-006 — First-class Unknown / Conflict

**Priority:** MUST-PROFILE

Unknown、Conflict、保留事項を空欄、未入力、最新値、confidence最大値へ黙って平坦化してはならない。

DecisionまたはRecommendationが存在しても、未解決状態は独立して残せなければならない。

### PIC-007 — Recommendation / Decision Separation

**Priority:** MUST-PROFILE

AIまたは人間によるRecommendationと、利用者が採用したDecisionを別identityとして扱えなければならない。

Recommendationを編集してDecisionに見せかけたり、Recommendationの存在をDecision成立として扱ってはならない。

### PIC-008 — Lightweight Decision Memory

**Priority:** MUST-PROFILE

個人の低〜中影響Decisionでは、過剰な監査入力を要求せず、少なくとも必要に応じて次へ戻れること。

- Decision statement
- principal basis
- unresolved state at decision time
- major constraint / assumption if material
- revisit / reopen condition if known

すべてを常時必須fieldにはしないが、Surfaceが「結論だけ」を唯一のDecision memoryとして保存する設計にしてはならない。

### PIC-009 — Non-retroactive Decision Basis

**Priority:** MUST-PROFILE

Decision後に得たObservation、Evidence、Interpretation等を、そのDecision作成時のbasisへ遡及的に混入してはならない。

後から過去Decisionを表示するとき、current stateとhistorical basisを区別できること。

### PIC-010 — Reorientation Projection

**Priority:** MUST-PROFILE

再度Inquiryを開いたとき、元chatや全sourceを最初から読み直さなくても、light Projectionから少なくとも次へ到達できなければならない。

1. 何を考えているInquiryか。
2. 現在重要なObservation / Evidenceは何か。
3. 何がUnknown / Conflict / residualとして残るか。
4. 主なHypothesis / Recommendation / Decisionは何か。
5. Decisionがある場合、主要basisは何か。
6. Decision後または前回確認後に何が変化したか。
7. どの条件で再検討すべきか。

この問い集合はUI固定layoutではなく、reorientationの意味要件である。

### PIC-011 — Detail-on-demand

**Priority:** MUST-PROFILE

light Projectionから、必要な場合だけsource、provenance、revision、exact binding、Method Application等のdetailへ降りられること。

light viewの簡潔さを理由にcanonical meaningを削除してはならない。

### PIC-012 — Change-since-Decision / Change-since-Review

**Priority:** SHOULD-PROFILE

利用者が過去Decisionまたは以前のreview時点からInquiryを再開するとき、その後追加・変更・撤回された重要な情報を区別して把握できること。

差分表示のUI方式は固定しない。

### PIC-013 — Reopen without Rewriting

**Priority:** MUST-PROFILE

新Evidenceや条件変化によって再検討するとき、過去Decisionを削除・上書きするのではなく、元Decisionと新しいInquiry / review / Decisionの関係を辿れること。

### PIC-014 — Chat-independent Readability

**Priority:** MUST-PROFILE

元のAI chat thread、Prompt、利用モデル、providerが利用不能でも、保存されたcanonical meaningから、人間がInquiryの現在地と過去Decisionを読めなければならない。

private chain-of-thoughtを再構成条件にしてはならない。

### PIC-015 — Portable AI Handoff Projection

**Priority:** SHOULD-PROFILE

保存したInquiryから、別のAIまたはtoolが続きを扱うためのstructured / human-readable Projectionを生成できること。

Handoffは少なくとも可能な範囲で次を混同しない。

- observation / source claim
- interpretation / hypothesis
- unknown / conflict
- recommendation
- decision
- historical basis
- later evidence

Handoff Projection自体をcanonical authorityにしない。

### PIC-016 — Bulk Conversation / Note Intake

**Priority:** SHOULD-PROFILE

既存のchat transcript、長いメモ、調査ノート等を一括投入し、sourceとして保持しながら、必要なsemantic candidateへ分解する支援経路を持てること。

利用者に過去会話を一文ずつ手動再入力させることを標準利用経路にしてはならない。

AIが利用不能な場合でも、raw source参照を保存し、後から手動または別Realizationで構造化できる余地を保つ。

### PIC-017 — Inquiry Discovery and Resume

**Priority:** MUST-PROFILE

複数のInquiryを保存した後、利用者が以前のInquiryを見つけて再開できなければならない。

最低限、recent listまたは同等のnavigationを持つこと。keyword search、semantic recall、tagging等の方式はProfileの要件として固定しない。

関連Inquiryの自動想起やSparse Associative Cognitive SubstrateはLATER候補とする。

### PIC-018 — Local Standalone Read / Write

**Priority:** MUST-PROFILE

first personal profileは、外部AI、外部SaaS、常時network接続なしでも、保存済みInquiryを開き、読取り、手動でObservation / Unknown / Decision等を追加し、再保存できること。

このProfile要件はSEI全体をlocal-only製品へ固定するものではない。

### PIC-019 — Portable Export / Import

**Priority:** MUST-PROFILE

利用者は、特定のStorage instanceやUIへ恒久的に拘束されず、保存したInquiryの耐久的意味をmachine-readableな形でexportし、別環境で再読できなければならない。

可能であればhuman-readable Projectionも同時に得られることをSHOULDとする。

export format自体をUniversal Contractへ自動昇格させない。

### PIC-020 — Personal Retention Control

**Priority:** SHOULD-PROFILE

個人Profileでは、利用者が自分のlocal dataについて、少なくともInquiry単位またはProfile data全体を削除できる製品操作を持つことを候補とする。

これはsurviving canonical record内のhistorical revisionを黙って書き換えることとは異なる。

```text
explicit data deletion
  != semantic supersession
  != silent historical rewrite
```

retention / deletionをSEI全体のStable Requirementへ昇格させるかはsecurity / privacy要件と合わせて別途審査する。

### PIC-021 — Capture Time / Subject Time Separation

**Priority:** SHOULD-PROFILE

過去chatや資料を後から取り込む場合、「SEIへ記録した時刻」と「Observation / Decision等が実際に成立した時点」を同一視しないこと。

後日importした資料を、当時からSEIが認識していたかのように扱ってはならない。

### PIC-022 — Reversible Assistance

**Priority:** SHOULD-PROFILE

AIによる要約、分類、重要度選択、handoff生成等の支援は、利用者が元のcanonical / source contextへ戻り、誤りを修正できる形で提供すること。

AI summaryだけを唯一の保存内容にしない。

### PIC-023 — No Mandatory Generative AI

**Priority:** MUST-PROFILE

first personal profileの中核価値はLLM invocationが成功しなければ成立しない設計にしてはならない。

LLM failure、provider交換、offline利用時にも、manual capture、read、historical review、Decision memory、exportは成立すること。

### PIC-024 — No Composite Truth / Confidence Collapse

**Priority:** MUST-PROFILE

複数source、Unknown、Conflict、Recommendation等を単一confidence scoreへ集約し、そのscoreからTruthまたはDecisionを自動決定することをProfileの中心機構にしない。

rankingやretrieval scoreを使う場合も、それをsemantic truthと同一視しない。

### PIC-025 — Progressive Impact Depth

**Priority:** SHOULD-PROFILE

同じ個人Profileでも、低影響・可逆なInquiryには軽い記録で開始でき、不可逆性や影響が増す場合にはbasis、constraint、provenance等を厚くできること。

first value validationではhigh-stakes利用を対象外にするため、impact classification policyのproduction化はLATERとする。

## 7. first usable profileに必要なSurface operation

UI名やAPI名ではなく、少なくとも次の論理操作が必要になる。

```text
create inquiry
find / reopen inquiry
add free-form material
inspect / correct semantic candidates when available
record unknown / conflict
record recommendation
record decision when applicable
read reorientation projection
read supporting detail
add later evidence
review changes / reopen
export / import
explicitly delete personal data
```

これを固定workflow state machineにはしない。

InquiryによってはRecommendationもDecisionも存在しない。

## 8. 最小Projection群

first profileでは、画面数ではなくProjectionの役割を分ける。

### 8.1 Orientation Projection — MUST

目的: 数分以内ではなく**できるだけ少ない再読で**現在地へ戻す。

表示候補:

- inquiry question / short context
- important current observations
- unresolved unknown / conflict
- current hypothesis / recommendation
- latest decision if any
- major basis
- changes since decision / last review
- revisit condition

### 8.2 Evidence Detail Projection — MUST

目的: light viewの根拠へ降りる。

- source reference
- observation / interpretation separation
- provenance
- timestamps / historical binding
- revision / supersession

### 8.3 AI Handoff Projection — SHOULD

目的: 別AI / toolへconversation history依存なしに続きを渡す。

### 8.4 Timeline / Audit Projection — SHOULD

目的: historical integrity確認。

個人first profileで常時表示する必要はない。

## 9. 自動化と認知層の境界

### 9.1 deterministic / symbolicが担うもの

可能な範囲で次はdeterministicに扱う。

- identity / reference integrity
- timestamp ordering validation
- historical basisの非遡及
- known schema validation
- export / import integrity
- explicit revision / supersession関係

### 9.2 LLMが候補となるもの

- bulk chat / noteからのsemantic candidate抽出
- source要約
- comparison / Cognitive Method Realization
- Recommendation
- human-facing explanation
- AI handoff文章化

### 9.3 Sparse Associative Cognitive Substrateが将来候補となるもの

- 過去Inquiry / Artifactの関連候補想起
- partial queryからのcandidate recall
- novelty cue
- attention candidate selection

ただし、これらはfirst personal value gateの成立条件にしない。

```text
recall activation != relevance truth
novelty signal != SEI Unknown
retrieval rank != Recommendation != Decision
```

## 10. 非機能候補

### PIC-NF-001 — Personal-scale responsiveness

first profileでは、localなInquiry open / save / light Projection生成が、人間の通常操作を妨げるような長い外部処理待ちに依存しないこと。

具体latency thresholdは実装probeで測定してから決める。

### PIC-NF-002 — Offline durability

正常なsave完了後にprocessを終了・再起動しても、保存したInquiryを再読できること。

crash consistency / fsync保証等はPackaging / Persistenceの正式NFRで別途扱う。

### PIC-NF-003 — Inspectability

保存内容は、製品内部のopaque embeddingやmodel stateだけに依存せず、少なくともSEIのportable semantic dataとして検査可能であること。

### PIC-NF-004 — Dependency proportionality

first personal profileを利用するために、enterprise infrastructureやGPUを必須にしない。

## 11. 価値上の失敗条件

以下は機能が動いていてもProfile上の失敗とする。

- chat transcriptを保存しただけで「Inquiry continuityが成立した」と扱う。
- AI summaryだけを保存し、Unknownやhistorical basisを失う。
- 「Decision」を必須の完了状態にする。
- Recommendationを利用者Decisionとして表示する。
- later evidenceをpast basisへ混ぜる。
- sourceとInterpretationを分けられない。
- すべての入力でsemantic type選択を強制する。
- SEIを使うために特定LLM subscriptionを必須にする。
- local personal useなのにteam / IdP setupを開始条件にする。
- retrieval similarityをTruthまたはConfidenceとして表示する。
- portable exportがなく、local databaseだけが唯一の意味上の正本になる。

## 12. first profileの「削る勇気」

Product Value検証を明瞭にするため、少なくとも初期版では次を作らなくてもよい。

- rich collaborative editor
- realtime collaboration
- RBAC / enterprise SSO
- approval workflow
- provider marketplace
- autonomous agent loop
- general-purpose browser automation
- full knowledge graph visualization
- general-purpose vector database UI
- universal tagging taxonomy
- calendar / task management suite
- built-in chat productの完全代替

特に、SEI自身がAI chat UIを所有しなければならないとは要求しない。

むしろ外部chatをsource / providerとして利用し、SEIを**conversationより長く生きるInquiry memory**として成立させられるかを優先して検証する。

## 13. Requirement昇格時の候補構造

このProfileを正式文書へ移す場合、PICをそのまま25個のStable Requirementへ増殖させない。

現時点では、次の4群へ圧縮できる可能性が高い。

### Group A — Inquiry Resumability

PIC-001 / 002 / 010 / 011 / 012 / 017

### Group B — Low-friction Semantic Capture

PIC-003 / 004 / 005 / 016 / 021 / 022

### Group C — Decision Historical Integrity

PIC-006 / 007 / 008 / 009 / 013 / 024 / 025

### Group D — Personal Portability / Independence

PIC-014 / 015 / 018 / 019 / 020 / 023

既存Requirementへ完全に包含される群は、新規REQを追加せず、Product Profile / Acceptance Scenarioとして具体化する方がよい。

## 14. 未解決課題

1. `Inquiry Resumability`はREQ-0014等の組合せで十分か、それともProduct Requirementとして独立させるべきか。
2. `Friction-bounded Capture`はpure UX requirementか、Product Value成立条件としてstable化すべきか。
3. AI Handoff ProjectionをREQ-0019 Human / AI ReadabilityのAcceptanceだけで扱うか、独立Requirementにするか。
4. Personal Retention ControlをSEI全体のprivacy / security Requirementへ昇格させるか。
5. bulk transcript intakeでraw sourceをどの程度保持するか。copyright、privacy、storage costとどう折り合うか。
6. `important current observations`の選択をmanual / deterministic / LLM / sparse recallのどこへ置くか。
7. 「前回review時点」のidentityをProduct-local stateとするか、durable semantic eventとして必要か。
8. Inquiry間のrelationをいつUniversal意味へ上げる必要が生じるか。

これらはprototypeとdogfooding Evidenceを得る前にUniversal化しない。
