# SOZA Product Shape

更新日: 2026-09-01  
状態: **Current Product Shape Baseline**

## 1. この文書の役割

この文書は、SOZAを一つの製品として見たときに、**誰が何のために使い、どこからどこまでをSOZAが担い、どこを外部のCapability Providerへ委ねるか**という外形を定めます。

`SOZA_PRODUCT_VALUE.md`や`SOZA_VALUE_PROPOSITION.md`が価値を定めるのに対し、本書は、その価値が製品としてどのような利用面と境界を持つべきかを整理します。

特定のUI framework、API protocol、Storage、deployment方式、AI modelをここで固定しません。また、この文書だけを根拠に新しいUniversal Core概念を追加しません。必要な意味差はRequirement、Scenario、ADRを通して検討します。

## 2. 一文で表すSOZA

SOZAは、人間・AI・外部システムが関わる判断仕事について、**問い、Observation、Evidence、Unknown / Conflict、Cognitive Method、Recommendation、Decision、Responsibility、Capability、Provenance、残差を、実行手段から独立した意味として残し、後から読み直し、続きから再開できるようにする認知・意思決定基盤**です。

SOZAの中心は「何でも自ら実行すること」ではありません。

```text
SOZA
  = durable cognitive / decision meaning
  != workflow engine
  != agent runtime
  != execution provider
```

## 3. 製品として支える主要な仕事

SOZAの利用は固定workflowへ閉じませんが、製品として少なくとも次の仕事を自然につなげられることを目指します。

### 3.1 問いを始める・再開する

利用者は、すべての項目を埋めてから作業を始めるのではなく、問い、目的、主要な文脈など、現在分かっている範囲からInquiryを始められます。

過去のInquiryやDecisionを読み直し、残されたUnknown、Conflict、reopen condition等から続きを始めることもできます。

### 3.2 Observation、Evidence、不確実性を集める

人間、AI、外部Provider等から得た情報を、出所や取得経路、Interpretation等と必要に応じて分けて扱います。

分からないことをNoへ、Conflictを最新値へ黙って変換しません。

### 3.3 Cognitive Methodを適用する

調査、比較、統合、評価等に用いたCognitive Methodを、そのPrompt、code、Skill、人間手順等のRealizationから分けて扱います。

Method Applicationは、Recommendation、Decision、Assuranceを自動的に意味しません。

### 3.4 RecommendationとDecisionを扱う

AIや人間がRecommendationを作成し、必要な主体がDecisionを行います。

案件によってはAIへDecisionを委任して構いません。ただし、Recommendation、Decision、Authority、Responsibility等を必要な粒度で読み分けられる状態を保ちます。

### 3.5 Capability / Providerを選び、外部実行へつなぐ

SOZAは、必要なCapabilityを人間、AI、SaaS、TEI、workflow engine、custom code等へ委ねられます。

Provider selectionやAction Intentを意味として扱えても、SOZA自身がすべての実行runtimeを所有することは要求しません。

### 3.6 実行後のObservationを戻す

外部実行のreceipt、状態変化、Business Outcome等を必要に応じてSOZAへ戻し、新しいObservationとして次のInquiryやDecision reviewへ利用できます。

```text
Execution success
  != Decision correctness
  != Business Outcome success
```

実行結果によって以前の判断が自動的に正しかったことにはしません。

### 3.7 過去へ戻り、判断を読み直す

時間が経過し、Evidence、Provider、AI model、担当者、組織構成が変わっても、当時のDecisionとbasisを必要な精度で読み直せることを製品上の重要な出口とします。

## 4. 論理的なProduct Surface

以下は、利用者や外部システムから見た**論理的な面**です。一つのprocessやdeployment unitへ固定するものではありません。

### 4.1 Work / Interaction Surface

人間やAIがInquiryを始め、Evidenceを追加し、Methodを適用し、Recommendation / Decisionを作成・レビューする入口です。

将来、Web UI、desktop UI、CLI、MCP、API、AI chat integration等の複数Realizationを持ち得ます。

このSurfaceの表示状態や会話履歴だけをcanonical semantic authorityにはしません。

### 4.2 Canonical Semantic Access Surface

SOZAが耐久的に保持する意味を、機械から読み書きできる境界です。

Semantic Contract、Reference、Representation Profile等との整合を保ち、人間向け画面やAI向けProjectionから同じcanonical meaningへ戻れることを目指します。

protocol、transport、SDK形態は別途決定します。

### 4.3 Integration Surface

Provider、Storage、Cognitive Method Realization、外部実行基盤等を接続する面です。

Provider固有schemaをUniversal Coreへ押し込まず、Adapter、Profile、Reference等を通して必要な意味だけを接続します。

### 4.4 Projection / Review Surface

日常利用向けのlight view、監査向けのaudit view、人間向けsummary、AI向けstructured view等を提供する面です。

Projectionはcanonical authorityではなく、必要に応じて元の意味へ戻れることを前提とします。

### 4.5 Evidence / Governance Surface

Product Value、Requirement、Decision、変更来歴、Evidenceの高さ等を追跡し、どこまで実証済みかを確認する面です。

これは「すべての利用者が開発用Plan文書を読む」ことを意味しません。製品内部・運用上必要なEvidence traceabilityを、実装や利用形態に応じて適切に露出させます。

## 5. SOZAの内側と外側

### SOZAが所有する意味

少なくとも次のような耐久的意味と、その相互関係をSOZAの中心に置きます。

- Inquiry / Questionに必要な文脈
- Observation / Evidence / Unknown / Conflict
- Cognitive MethodのDefinition / Applicationに必要な意味
- Recommendation / Decision
- Responsibility / Authorityに関わる文脈
- CapabilityとProviderの区別
- Provenance / Reference / Revision / Semantic Lineage
- Decision後に残るresidual / reopen information

具体的なfield setはContractの正本に従います。本書の列挙から自動的に新しいrecord typeを作りません。

### 原則として外部へ委ねるもの

次は必要であっても、SOZAが恒久的に一体所有することを前提にしません。

- workflow scheduling
- queue / retry / worker management
- agent turn orchestration
- business application execution
- general-purpose document storage
- identity provider / enterprise directory
- model hosting
- provider-specific monitoring
- BI / dashboard engine
- domain-specific Pattern catalog

SOZAはこれらと統合できますが、それらを内包しなければ成立しない製品にはしません。

## 6. Minimum Usable Product Shape

具体的なpackageやUIを決める前でも、「製品として最低限何が一続きに成立すべきか」は定義できます。

最初のusable shapeでは、少なくとも次を満たすことを目標とします。

1. 一つのInquiry / Decision contextを作成し、後から再び開ける。
2. 人間とAIが、同じcanonical meaningを別のProjectionから読み書きできる。
3. Observation / Evidenceに加え、UnknownやConflictを失わずに保持できる。
4. Cognitive Method Application、Recommendation、Decisionを必要に応じて区別できる。
5. Decisionのbasis、主要なResponsibility、未解決残差を後から辿れる。
6. 外部Providerへ処理を委ねても、SOZAのDecision identityをProvider run IDへ従属させない。
7. 実行結果をObservationとして戻し、次のreviewやInquiryへ接続できる。
8. Provider、AI model、実行runtime等を交換した後でも、canonical recordを再読できる。
9. 低影響案件では最大詳細を強制せず、必要になったときに詳細化できる。

これはv0.2.0で全項目をExecutable Evidenceまで満たしているという主張ではありません。現時点ではProduct ShapeとしてのDesign baselineです。

## 7. 製品化に向けてまだ決める必要があること

現在のsemantic baselineから、実際に配布・利用できる製品へ進むには、少なくとも次を別Issueで決める必要があります。

### 7.1 最初のInteraction boundary

- 人間が最初に触る入口は何か。
- AIはどのprotocolから同じcanonical contextへアクセスするか。
- UI / CLI / API / MCP等のどこまでを最初のsupported surfaceとするか。
- simple viewとaudit viewをどう往復するか。

### 7.2 Packaging / Deployment

- library、service、CLI、reference UI等をどのように組み合わせるか。
- single-user / team / server利用をどの順序で扱うか。
- Storageをembeddedとexternalのどちらから始めるか。
- deployable unitとsemantic boundaryを混同しないための境界をどう置くか。

### 7.3 Identity / Authorization / Collaboration

SOZAのsemanticなResponsibility / Authorityと、製品へのlogin、access control、tenant / workspace等は別問題です。

外部IdP、組織境界、共有、Selective Disclosureを含め、製品security boundaryとして別途定義する必要があります。

### 7.4 最初のend-to-end golden journey

semantic fixtureの集合だけでなく、利用者が一続きの仕事として価値を確認できるScenarioを定義する必要があります。

候補は次の流れです。

```text
Inquiry
  → Observation / Unknown / Conflict
  → Cognitive Method Application
  → Recommendation
  → Decision / Responsibility
  → external Capability / Execution
  → resulting Observation
  → historical review / reopen
```

この流れを固定workflow ontologyにはしません。Acceptance用の代表Scenarioとして利用します。

### 7.5 非機能要件

性能、可用性、耐久性、security、privacy、import / export、backup / recovery等は、actual product deploymentを定める段階で具体的なAcceptanceが必要です。

semantic portabilityを理由に、これらを未定義のままproduction readyとは扱いません。

## 8. Requirementへ落とすときの方針

Product ShapeからRequirement IDを機械的に増やしません。

まず既存REQ-0001〜REQ-0022とSCN-0001〜SCN-0017へ戻り、既に包含されている意味と、新たに製品外形として必要になった意味を分けます。

特に次は既存Requirementとの重複が大きいため、追加前に照合します。

- 人間 / AIの同一canonical meaning利用 — REQ-0019、REQ-0011
- Progressiveな詳細化 — REQ-0010
- 実行手段の交換可能性 — REQ-0021、REQ-0001
- Provider中立性 — REQ-0007、REQ-0022
- Storage独立性 — REQ-0018

新しいREQ / SCNが必要な場合は、Product Shapeから直接実装仕様へ飛ばず、Issueで重複監査とAcceptance境界を定めてからstable IDを付与します。

## 9. Evidence状態

- Product Shape Design Evidence: **Established by this baseline**
- End-to-end Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

個別Contract / runtime / evaluationに既存Executable Evidenceがあっても、Minimum Usable Product Shape全体のend-to-end Evidenceへは自動昇格させません。

## 10. 関連文書

- `../value/SOZA_PRODUCT_VALUE.md`
- `../value/SOZA_VALUE_PROPOSITION.md`
- `../value/SOZA_VALUE_MODEL.md`
- `../value/SOZA_VALUE_ACCEPTANCE.md`
- `../vision/SOZA_PRODUCT_VISION.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/adr/ADR-0014-soza-tei-product-boundary.md`
- `../../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../../plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`

## 11. Natural Japanese review

current Product Value、Value Proposition、Vision、REQ-0001〜0022、SCN-0001〜0017、SOZA / TEI境界、Provider Independence、Progressive Explicitness、現在のContract / runtime Evidenceへ戻り、製品としての主要な仕事、論理Surface、内外境界、Minimum Usable Product Shapeを整理した。既存semantic ontologyを拡張せず、未決のInteraction、Packaging、Identity / Authorization、golden journey、非機能要件は別Issueへ送る形とした。その後、意味、規範強度、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
