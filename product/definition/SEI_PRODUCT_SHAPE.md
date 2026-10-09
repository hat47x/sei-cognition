# SEI Product Shape

更新日: 2026-10-02  
状態: **Current Product Shape Baseline — resume-first / heterogeneous cognition / product-family boundary reflected。§6.5 / §8.3 / §8.5の統合の頂点、制御の意味の境界、参考対応表は、ADR-0035（Proposed）による再基線化の提案**

## 1. この文書の役割

この文書は、SEI Cognitionを一つの製品として見たときに、**誰が、どのような認知・判断仕事のために使い、どこまでをSEIが担い、どこからをCognitive Method / Capability Provider / 隣接Productへ委ねるか**という製品外形を定めます。

`SEI_PRODUCT_VALUE.md`や`SEI_VALUE_PROPOSITION.md`が「なぜSEIが存在するか」を定めるのに対し、本書は、その価値を利用者が一続きの仕事として受け取るために、SEIがどのSurface、責務、境界を持つべきかを整理します。

特定のUI framework、API protocol、Storage、deployment方式、AI model、認知アルゴリズム、分散実行方式をここで固定しません。また、本書だけを根拠にUniversal Core、Stable Requirement、Value Axisを増やしません。

Product Shapeは次の高さにあります。

```text
Product Value
  ↓
Product Shape / Product Interaction
  ↓
Requirement / Acceptance Scenario
  ↓
Architecture / Contract
  ↓
Implementation / Evidence
```

したがって、本書で「製品としてこうあるべき」と整理した内容も、独立したfailureが確認され、既存Requirementでは表せない場合にだけStable Requirementへ昇格させます。

## 2. 一文で表すSEI

SEIは、人間・AI・外部システムが関わる認知・判断仕事について、**問い、Observation、Evidence、Unknown / Conflict、Cognitive Method、Recommendation、Decision、Responsibility、Capability、Provenance、残差を、特定のAI・実行手段・sessionから独立した意味として保ち、後から読み直し、問い直し、続きから再開できるようにする認知・意思決定基盤**です。

SEIの中心は「すべてを自ら考えること」でも「すべてを自ら実行すること」でもありません。

```text
SEI
  = durable cognitive / decision meaning
  + resumable cognitive context
  + bounded interoperability

SEI
  != central AI brain
  != workflow engine
  != model runtime
  != distributed compute fabric
  != universal execution provider
```

AIや実行技術が高度化しても、SEIが残すべきなのは現在の実装方式ではなく、**何を見て、何をまだ分からないとし、どの手段で考え、何を判断し、何が後から変わったかを再構成できる意味**です。

## 3. 製品として支える主要な仕事

SEIの利用を固定workflowへ閉じません。ただし、製品として価値が一続きに成立するため、少なくとも次の仕事を自然につなげられることを目指します。

### 3.1 問いを始める・問い直す・再開する

利用者は、完全なontologyや全項目を埋めてから作業を始める必要はありません。

最初に持っているものが、明確なQuestionではなく、違和感、弱いObservation、未整理な目的であっても構いません。SEIは、それらをすぐTruthやDecisionへ整形せず、必要な意味境界へ段階的に外在化できる入口を持ちます。

また、時間が空いた後には、chat transcriptや画面stateを再現することではなく、canonical meaningから次へ戻れることを重視します。

- いま何を問うているか。
- すでに何をDecisionしたか。
- そのDecisionは何をbasisとしていたか。
- 何がUnknown / Conflict / residualとして残っているか。
- Decision後に何が変わったか。
- どの条件でreview / reopenすべきか。
- 次に確認する価値が高いものは何か。

これはISSUE-000073のDecision Continuityと、ISSUE-000078のpre-decision Inquiry Continuity探索へ接続します。

### 3.2 Observation、Evidence、不確実性を扱う

人間、AI、外部Provider等から得た情報を、出所、取得経路、Interpretation、Evidenceとしての位置づけと必要に応じて分けて扱います。

```text
Observation
  != Hypothesis
  != Recommendation
  != Decision
```

分からないことをNoへ、Conflictを最新値へ、未整理な素材をAIの流暢な説明へ黙って変換しません。

### 3.3 異種のCognitive Methodを利用する

SEIは、認知手段を生成AIだけへ限定しません。

たとえば次のような手段を、必要に応じてCognitive Method / Capability Providerとして利用できます。

- 決定論的rule / heuristic
- 従来型classifier
- embedding / retrieval
- sparse associative cognition
- local lightweight model / SLM
- external general-purpose model
- domain-specific model
- human procedure / expert review
- SUI Sensemaking等の外部sensemaking system

重要なのは、これらを同一アルゴリズムへ揃えることではありません。

```text
heterogeneous cognition
  → common semantic boundary
  != common internal mechanism
```

どのMethod / Realization / Providerを使い、何が出力され、どこまで確かだったかを後から読み分けられることを重視します。

Method outputはRecommendationやDecisionへ自動昇格しません。

### 3.4 RecommendationとDecisionを扱う

AIや人間がRecommendationを作り、必要な主体がDecisionを行います。

案件によってはAIへDecisionを委任して構いません。ただし、少なくとも次の意味差を必要な粒度で復元できることを保ちます。

```text
Recommendation
  != Decision
  != Authority
  != Responsibility
  != Action Intent
  != Execution
```

AI suggestionは、Product Interaction上ではprovisionalな状態を取り得ます。provisional suggestionが存在することだけでcanonical Decisionへ書き込みません。

### 3.5 Capability / Providerを選び、外部実行へつなぐ

SEIは、必要なCapabilityを人間、AI、SaaS、TEI、workflow engine、custom code等へ委ねられます。

SEIが所有するのは、主に次の意味です。

- 何のCapabilityが必要だったか。
- どのConstraint / Evidence / Decisionで選んだか。
- どのProvider / Realizationを使ったか。
- 実行後に何をObservationとして受け取ったか。

一方、CPU / GPU / NPU、worker選択、placement、retry、queue、resource scheduling等をSEIのUniversal Coreへ持ち込みません。EKI Fabricのような分散実行基盤へ委ねる場合も同じです。

```text
meaning of requested capability
  != compute placement
```

### 3.6 実行後のObservationを戻す

外部実行のreceipt、状態変化、Business Outcome等を必要に応じてSEIへ戻し、新しいObservationとして次のInquiryやDecision reviewへ利用できます。

```text
Execution success
  != Decision correctness
  != Business Outcome success
```

実行に成功したことだけから、以前のRecommendationやDecisionが正しかったとは扱いません。

### 3.7 過去へ戻り、変更を読み分ける

時間が経過し、Evidence、Provider、AI model、担当者、組織構成が変わっても、当時のDecisionとbasisを必要な精度で読み直せることを重要な出口とします。

Decision後に得たObservationを、当時のbasisへ遡及混入させません。

```text
post-decision information
  != historical decision basis
```

また、別の人間やAIへ引き継ぐ場合も、共有可能性とResponsibility / Access boundaryを分離します。

## 4. 論理的なProduct Surface

以下は、利用者や外部システムから見た**論理的な面**です。一つのprocess、deployment unit、protocolへ固定するものではありません。

### 4.1 Work / Interaction Surface

人間やAIがInquiryを始め、Observationを追加し、Methodを適用し、Recommendation / Decisionを作成・レビューし、過去の仕事を再開する入口です。

Web UI、desktop UI、CLI、MCP、API、AI chat integration等の複数Realizationを持ち得ます。

このSurfaceの会話履歴、recent list、form draft、working set membership、projection cache等をcanonical semantic authorityにはしません。

### 4.2 Canonical Semantic Access Surface

SEIが耐久的に保持する意味を、機械から読み書きできる境界です。

Semantic Contract、Reference、Representation Profile等との整合を保ち、人間向け画面、AI向けProjection、異種Methodから同じcanonical meaningへ戻れることを目指します。

protocol、transport、SDK形態は別途決定します。

### 4.3 Cognitive Method / Provider Integration Surface

rule、classifier、associative cognition、local model、external model、人間手順、SUI等の異種Cognitive Method / Providerを接続する面です。

Provider固有schema、model-specific metadata、algorithm-specific internal stateをUniversal Coreへ押し込みません。必要なMethod identity、Application、Observation、Provenance等の境界だけをSEIへ戻します。

### 4.4 Execution / Capability Integration Surface

TEI、SaaS、workflow engine、custom code、人間作業、外部組織、EKI上で動作するworker等へCapabilityを接続する面です。

Execution Providerの内部topologyやresource placementを、SEI semantic identityへ同化させません。

### 4.5 Projection / Review Surface

日常利用向けlight view、resume projection、監査向けaudit view、人間向けsummary、AI向けstructured view等を提供する面です。

Projectionはcanonical authorityではなく、必要に応じて元の意味へ戻れることを前提とします。

### 4.6 Evidence / Governance Surface

Product Value、Requirement、Decision、変更来歴、Evidenceの高さ等を追跡し、どこまで実証済みかを確認する面です。

これは、利用者が開発用Plan文書を常時読むことを意味しません。製品・運用上必要なEvidence traceabilityを、利用形態に応じて適切に露出させます。

## 5. SEIが所有するものと、所有しないもの

### 5.1 SEIが中心として所有する意味

少なくとも次の耐久的意味と、その相互関係をSEIの中心に置きます。

- Inquiry / Questionに必要な文脈
- Observation / Evidence / Unknown / Conflict
- Cognitive MethodのDefinition / Applicationに必要な意味
- Recommendation / Decision
- Responsibility / Authorityに関わる文脈
- CapabilityとProviderの区別
- Provenance / Reference / Revision / Semantic Lineage
- Decision後に残るresidual / reopen information

具体的なfield setはContractの正本に従います。本書の列挙から自動的に新しいrecord typeを作りません。

### 5.2 原則として外部へ委ねるもの

次は必要であっても、SEIが恒久的に一体所有することを前提にしません。

- workflow scheduling
- queue / retry / worker management
- agent turn orchestration
- general-purpose document storage
- identity provider / enterprise directory
- model hosting
- GPU / NPU / worker placement
- distributed compute scheduling
- provider-specific monitoring
- BI / dashboard engine
- domain-specific Pattern catalog
- Cognitive Method内部のアルゴリズム状態

SEIはこれらと統合できますが、それらを内包しなければ成立しない製品にはしません。

## 6. 隣接Productとの境界

SEI Cognition、SUI Sensemaking、TEI、EKI Fabricは連携できますが、一つの固定pipelineや単一製品として定義しません。

### 6.1 SUI Sensemaking

SUIは、未整理な材料を集め、関係、まとまり、仮説、emergenceを形成し、sensemakingを進める製品として位置づけられます。

SEIは、SUIの内部キャンバスや関係表現を自らのUniversal Coreへ複製しません。SUIの成果がSEIへ戻る場合は、必要なObservation、Method Application、Artifact Reference、Provenance等の境界から扱います。

### 6.2 TEI

TEIは、業務上の意味をformal modelとして保持し、実装・実行可能なCapabilityへ接続する製品です。

SEIでは今後、**Work / Interaction Surface、Projection / Review Surface、Evidence / Governance Surface等のApplication Planeを実装するとき、TEIを第一候補とします。** Web / Desktop UI、設定・方針編集、review / resume projection、管理面等を個別frameworkで増やす前に、TEIのApplication / Projection / Target / Capabilityで実現できるかを確認します。

一方、次はTEIへ無理に移しません。

- SEI Universal Coreのsemantic meaning
- Cognitive Method本体
- local model / classifier / associative cognition等の専門runtime
- provider-specific low-level integration
- performance / device constraintが強いkernel処理
- headless / embedded利用でTEI Application surfaceを必要としない経路

TEIで不足が見つかった場合も、SEI固有要求を直接TEI Coreへ追加せず、既存TEI機能 → reusable Plugin / Adapter / Capability → native asset / custom implementation → cross-application EvidenceがあるCore gap候補、の順で扱います。

したがって、

```text
SEI Product / Semantic authority
  != TEI implementation authority

SEI Application Plane
  -> TEI-first

SEI Cognitive / Semantic Kernel
  -> native / Provider-specific allowed
```

という境界を維持します。

SEIはTEIをCapability Providerとして利用できますが、TEI固有のmodel structureやruntime identityをSEI semantic identityへ同化させません。またTEIが利用不能でも、Canonical Semantic AccessやCognitive Method integration等のheadlessな中心機能まで失う設計にはしません。

### 6.3 EKI Fabric

EKI Fabricは、異質で一時的な計算資源を安全に束ね、計算をどこで実行するかを扱う分散実行基盤です。

SEIのCognitive MethodやCapability ProviderがEKI上で実行されても、SEIはresource placementをProduct Valueの正本にはしません。

### 6.4 境界全体

```text
SUI
  = sensemaking / emergence

SEI
  = durable cognitive / decision meaning

TEI
  = formalized business capability / realization boundary

EKI
  = distributed compute placement / execution fabric
```

これは責務を完全分離するための壁ではありません。相互接続は積極的に認めます。

ただし、

```text
product affinity
  != required dependency
  != shared Universal Core
  != shared Evidence claim
```

を維持します。

各ProductのProduct Value、supported scope、Evidence claimは、それぞれのrepositoryを正本とします。

### 6.5 家族の統合の頂点（提案）

SEIは、家族に対して「翻訳と記憶を担う統合の層」の役割を持つことを提案します（ADR-0035、Proposed）。頂点と呼ぶのは、抽象の頂点（各製品に固有の判断の意味の翻訳先）、時間の頂点（最も長く生きる記録）、統合の頂点（任意の合流先）の三つの意味に限ります。指揮の頂点、所有の頂点、可用性の頂点は採りません。

Product Shapeの上では、これは次を意味します。

- SEIから他の製品へ向かう信号は、すべて依頼です。受け取った製品が自らの権限で判断します。
- SEIが持つのは、参照とコミットメントと対応表だけです。他の製品の意味やデータの正本は持ちません。
- どの製品の局所のループも、SEIの稼働を必要としません。SEIはその「反射弓」に入りません。
- 製品はSEIへ送ってもよいが、送らなくても成り立ちます。

固定pipeline、中央の頭脳、関連製品の特権化はしません。詳細は`../vision/SEI_PRODUCT_VISION.md` §11.1と`../value/SEI_FAMILY_APEX_VALUE_REVIEW.md`を参照します。

## 7. First Usable Product Shape

currentのfirst usable sliceでは、Local Single-Node Package上のsingle-userを基本条件として、Decision Continuityをactualに評価できる形へ絞ります。

これは将来のteam / hosted利用を否定するものではありません。最初にProduct Valueを反証可能にするためのscopeです。

最初のusable shapeでは、少なくとも次を一続きに成立させることを目標とします。

1. 短いInquiry / goalから始められる。
2. Observation、Unknown / Conflict、Recommendation、Decisionを必要な範囲で区別できる。
3. Cognitive Method / Providerを利用しても、そのoutputをDecisionへ黙って昇格させない。
4. AI suggestionをprovisionalに扱い、修正・却下・意味種別変更を経てcanonical commitできる。
5. canonical stateだけから有用なresume Projectionを再構成できる。
6. Decision当時のbasisと、Decision後に増えた情報を分けて読める。
7. AI / external Methodが利用不能でも、open / read / manual add / Decision / review / reopenを継続できる。
8. transient working-set stateを失ってもcanonical meaningを失わない。
9. stale draftや途中失敗を、成功したcanonical commitとして黙って露出しない。
10. external AIへ渡すcontextとcanonical write / Decision Authorityを分離する。
11. Provider、model、runtime等を交換した後でもhistorical meaningを読み直せる。
12. low-impactな利用では最大詳細を要求せず、必要になった場面だけ明示性を高められる。

CR-73.8 / CR-73.9で見つかった独立failureは、すでに**REQ-0023 — Canonical commitの整合性**と**SCN-0019**へformalizeされています。

一方、その他のInteraction品質やDecision Continuityの利用者価値は、既存Requirement、Product-local design、human Outcome評価へ戻しており、新しいStable Requirementを先取りしません。

## 8. Product Shape上の現在の未決事項

初期のProduct Shapeで未決だった領域の一部は、Product Interaction、Packaging、Product Access、Requirement auditによってDesign baselineまで進みました。現在残る主な未知は次です。

### 8.1 Decision Continuityをactualに成立させられるか

ISSUE-000073ではE1〜E8のprobe / runner / verifier / capture pathが整っていますが、actual Go 1.25.x executionとH1 / H2 human reviewは未完了です。

したがって、first usable Product ShapeはDesign上成立していても、実利用価値までEstablishedとは扱いません。

### 8.2 Decision前のInquiry Continuityに独立価値があるか

ISSUE-000078では、raw chat / chronological note / SEI canonical meaningを比較するevaluation scaffoldが整っています。

まだactual human resumption / correction / burden Evidenceは十分ではなく、Inquiry Continuityを独立Value AxisやStable Requirementへ昇格させません。

### 8.3 異種Cognitive Methodのselection / routingをどこまで製品責務にするか

複数のCognitive Method / Providerを利用できることと、SEIがUniversalなrouting policyを所有することは別です。

currentでは、selection理由、Method Application、Provenance、outputの意味を保持できることを重視し、model router、classifier cascade、cost optimizer等の具体routing mechanismはProduct / Profile / Provider-localに留めます。

actual利用から「routingの意味を外在化しなければ判断を再構成できない」という独立failureが確認された場合だけ、Requirement化を再検討します。

**【提案・ADR-0035】** この整理を、次の規則で明確にします。routing、escalation、attentionの配分、cascadeといった制御の**仕組み**は、交換可能なRealizationまたはProfileです。一方、制御の**判断の意味**——何を見て、何を意図的に見送り、どのMethodやProviderをなぜ選び、何を保留または上位へ回したか——は、Coreに記録すべき意味として扱います。

```text
control mechanism = Realization / Profile
meaning of a control decision = Coreに残す意味
```

「Coreに残す」ことは、新しいUniversal型を直ちに追加することではありません。既存のDecision Memory、Cognitive Method Application、Capability Choiceの組合せで表せるかを先に試します（とくに注意の範囲はISSUE-000086）。これにより、`evaluation/sei-cognition-orchestration/EMERGENT_COGNITIVE_ARCHITECTURE.md`のCognitive Control Planeは、交換可能なRealizationの集まりとして読めます。

### 8.4 single-userからcollaboration / hosted利用へどう拡張するか

Product Accessとsemantic Responsibility / Authorityの分離はDesign baselineがあります。

一方、team handoff、tenant、hosted operation、Selective Disclosureの実利用品質は別のEvidenceが必要です。

### 8.5 Product family integrationをどの粒度で標準化するか

SUI / TEI / EKIとの接続は可能ですが、共通protocolやcross-product orchestrationを標準化する必要性はまだ確定していません。

各Productの内部概念を共有ontologyへ寄せるより、actual integration failureから必要な境界だけを見つけます。

**【提案・ADR-0035】** 現在は、SEIが翻訳のために持つ参考の対応表`SEI_FAMILY_SEMANTIC_MAP.md`があります。これはContractでも共通protocolでもなく、各製品との対応はすべて候補です。標準が確立したわけではなく、必要な最小限の求心プロファイルは、実在の記録から導く方針です（ISSUE-000087）。

### 8.6 非機能要件

性能、可用性、耐久性、security、privacy、import / export、backup / recovery等は、actual deployment scopeごとに具体的Acceptanceが必要です。

semantic portabilityやlocal probeのPASSを理由に、これらを未定義のままproduction readyとは扱いません。

## 9. Requirementへ落とすときの方針

Product ShapeからRequirement IDを機械的に増やしません。

currentでは少なくともREQ-0001〜REQ-0023、SCN-0001〜SCN-0019へ戻り、既に包含されている意味と、新たに独立failureとして必要になった意味を分けます。

特に次は既存Requirementとの重複を先に監査します。

- 人間 / AIの同一canonical meaning利用 — REQ-0019、REQ-0011
- Progressiveな詳細化 — REQ-0010
- historical reconstruction — REQ-0001、REQ-0005、REQ-0006
- Provider中立性 — REQ-0007、REQ-0021、REQ-0022
- Storage独立性 — REQ-0018
- Canonical commit integrity — REQ-0023 / SCN-0019

新しいREQ / SCNが必要な場合は、Product Shapeから直接実装仕様へ飛ばず、Issueで次を確認してからstable IDを付与します。

1. 利用者または意味上の独立failureが存在するか。
2. 既存REQ / SCNの組合せでは表せないか。
3. 特定implementationを越えて意味差が残るか。
4. Acceptanceを観測可能に書けるか。
5. Product Valueへどのように接続するか。

「既存Requirementで十分」「Product-local designでよい」「human Outcome評価で見るべき」という結論も正当です。

## 10. Evidence状態

current Product Shapeについて、Evidence高さを次のように分離します。

- Product Shape Design Evidence: **Available**
- Product Value / Product Family boundary Design Evidence: **Available**
- first usable resume-first Product Slice Design Evidence: **Available**
- ISSUE-000073 runner / verifier / capture acceptance tooling: **Scoped Executable Evidence available**
- E1〜E8 actual Go 1.25.x execution: **Not Yet Verified**
- REQ-0023 / SCN-0019 actual Executable Evidence: **Not Yet Verified**
- Decision Continuity human H1 / H2 Outcome review: **Not Yet Observed**
- Inquiry Continuity actual human value: **Not Yet Established**
- heterogeneous Cognitive Method routing portability: **Not Yet Verified as a general guarantee**
- cross-product SUI / TEI / EKI integration standard: **Not Established**（参考の対応表は存在するが、標準ではない）
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
Design boundary clarified
  != executable behavior verified
  != product value observed
  != operational readiness
```

## 11. 関連文書

- `../value/SEI_PRODUCT_VALUE.md`
- `../value/SEI_VALUE_PROPOSITION.md`
- `../value/SEI_VALUE_MODEL.md`
- `../value/SEI_DECISION_CONTINUITY.md`
- `../vision/SEI_PRODUCT_VISION.md`
- `../interaction/SEI_PRODUCT_INTERACTION.md`
- `../interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `SEI_REALIZATION_PROVIDER_EXCHANGE.md`
- `../../architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`
- `../../plan/issue/ISSUE-000078-verify-pre-decision-inquiry-continuity.md`
- `../../plan/adr/ADR-0014-sei-tei-product-boundary.md`
- `../../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../../plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`
- `SEI_FAMILY_SEMANTIC_MAP.md`
- `../value/SEI_FAMILY_APEX_VALUE_REVIEW.md`
- `../../plan/adr/ADR-0035-family-integration-apex-and-control-meaning-boundary.md`

## 12. Natural Japanese review

2026-09-18時点のProduct Value、Value Proposition、Vision、Decision Continuity、Brand World Product Value Review、ISSUE-000073 / 000078、REQ-0001〜0023、SCN-0001〜0019、Product Interaction、Interaction Working-Set Architecture、Product Access、Realization / Provider Exchange、SUI / TEI / EKIとのProduct Boundaryを逆照合しました。

従来のProduct Shapeは、InquiryからDecision、外部実行、historical reviewまでの基本外形を正しく持っていました。一方、その後に明確化された三点――**異種Cognitive Methodを生成AIへ限定しないこと、resume-firstなfirst usable Product Slice、隣接ProductとSEIの意味上の責務境界**――が十分に反映されていませんでした。

今回の再基線化では、それらを既存Product Valueへ統合しつつ、新しいValue Axis、Universal型、Stable Requirementを追加していません。CR-73.8 / 73.9だけは既存監査結果に従ってREQ-0023 / SCN-0019を正本とし、その他のInteraction仮説はactual execution / human review待ちのまま保持しました。

また、SUI / TEI / EKIとの親和性を固定pipelineや必須依存へ変えず、Cognitive Method / Capability / compute placementの三つの交換境界を分離しました。

2026-10-02には、ADR-0035（Proposed）に沿って、家族に対する統合の頂点（§6.5）、制御の仕組みと制御の判断の意味の分離（§8.3）、参考の対応表の存在（§8.5）を提案として加えました。固定pipeline、中央の頭脳、関連製品の特権化をしない境界と、統合標準が未確立であることは変えていません。

意味、要求強度、Evidenceの高さ、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
