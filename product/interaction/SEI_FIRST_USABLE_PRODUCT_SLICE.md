# SEI First Usable Product Slice — Resume-first Decision Work

更新日: 2026-09-17  
状態: **Product Design Baseline / Decision Continuity Validation Slice — Requirement Formalization Reflected / Executable & Human Evidence Pending**

## 1. この文書の役割

この文書は、`SEI_PRODUCT_INTERACTION.md`で定義したcanonical meaning上の操作境界を、**最初に実用価値を確かめる一つのProduct Slice**へ絞り込みます。

対象は、Local Single-Node Package上で一人の利用者が一つの判断仕事を始め、中断し、後から戻り、AIの支援も受けながらDecisionと未解決事項を失わずに続けられる体験です。

Product Value側では、この体験が目指す横断的な成果を**Decision Continuity（判断継続性）**と定義します。Decision ContinuityはV9ではなく、V1〜V8が一つの利用者仕事で同時に成立した結果です。本Product Sliceは、その価値仮説を最小条件でactualに検証するためのinstrumentでもあります。

この文書は新しいUniversal Contractを定義しません。また、Web、desktop、CLI、HTTP、MCP、特定AI model等を恒久的なProduct Requirementとして固定しません。最初のprototypeでは具体的なRealizationを選べますが、ここで固定するのは**利用者が得るべき体験と、失ってはならない意味境界**です。

```text
First usable Product Slice
  = resume a decision context with meaning intact
  + correct / dismiss AI assistance
  + deepen detail only when needed
  + test Decision Continuity against simpler alternatives
  != semantic schema editor
  != chat transcript archive
  != autonomous agent shell
```

## 2. なぜresume-firstか

SEIはすでに、Decisionのhistorical reconstruction、Unknown / Conflict、Recommendation / Decision分離、Provider independence、Progressive Explicitnessを意味として定義しています。

しかし、利用者にとっての価値は「後から再構成可能なrecordが存在する」だけでは完結しません。実際には、数日後や数週間後、別のAI session、別の端末・画面stateから戻ったとき、利用者自身が次の問いに答えられる必要があります。

- 何を考えていたのか。
- どこまで分かっていたのか。
- 何を決めたのか。
- そのとき何を根拠にしたのか。
- 何を決めずに残したのか。
- その後、何が変わったのか。
- いま見直す必要があるのか。

この「戻れること」はV1 Historical Reconstructionを人間のProduct Experienceへ翻訳するだけでなく、V2 / V3 / V5 / V6 / V7を一つのtaskで統合し、V4 / V8による手段交換可能性まで含めて試す場になります。

SEIの最初の製品価値を、情報入力の豊富さやAIの自律性ではなく、**文脈喪失に耐える判断継続性**へ置きます。

ただし、resume-firstを自己目的化しません。raw chatやsimple noteで同程度に正しく再開でき、SEIだけ入力負担が増えるなら、このProduct Sliceの価値仮説は弱まります。

## 3. 対象利用者と最初の利用場面

最初のsliceはsingle-userを対象とします。

典型的には、一人の利用者が次のような判断仕事を扱います。

- 技術選択や設計方針を比較して決める。
- 調査結果が割れている論点を保留を含めて判断する。
- AIに調査や比較を委ね、提案を受けて自分で採否を決める。
- 一度決めた後、新しい情報が出たため再検討する。
- 数週間後に「なぜこの方針にしたか」を自分自身で読み直す。

最初から組織workflow、approval chain、team workspace、hosted SaaSを必須にしません。それらは重要ですが、まず**SEIの意味保存が実際の一人の認知負荷と誤再構成を減らすか**を検証します。

## 4. Product experienceの中心ループ

固定workflowではなく、最初のsliceで価値を確かめる代表的な循環を次とします。

```text
Start lightly
  ↓
Capture what is known / unknown
  ↓
Ask AI or another method when useful
  ↓
Review provisional suggestions
  ↓
Commit selected meaning
  ↓
Make / record a Decision when needed
  ↓
Leave residual / reopen conditions
  ↓
Time passes / new evidence arrives
  ↓
Resume from canonical meaning
  ↓
See what changed
  ↓
Review / revise / continue
```

どの段階も必須state machineではありません。RecommendationなしのDecisionも、Decisionせず調査を続ける状態も認めます。

## 5. 最初の起動時

### 5.1 最小入力で始める

最初の画面・Surfaceで、利用者へContract fieldを並べません。

最初に必要なのは、たとえば次の程度です。

- 何について考えるか。
- 必要なら短い目的・背景。

利用者がまだbasis、Responsibility、Exact Bindingを用意していないことを入力エラーにはしません。

```text
minimal start
  != permanently shallow record
```

後から意味が必要になった時点で詳細化します。

### 5.2 「案件」をUniversal型にしない

UI上では一件の判断仕事を一まとまりとして表示して構いません。本書では便宜上`working set`と呼びます。

working setは、複数のInquiry、Observation、Recommendation、Decision、Residual等へのProjection上のまとまりです。

```text
working set
  = product navigation / projection convenience
  != canonical semantic authority
  != Universal Workspace entity
```

working set metadataを失っても、canonical stateから再構成できる方向を標準とします。

## 6. Resume Brief

再開時の中心Surfaceを**Resume Brief**と呼びます。これは新しいSemantic Contractではなく、canonical meaningから派生するProduct Projectionです。

Resume Briefは固定field setへしませんが、少なくとも次の問いに短い距離で答えられることを目標にします。

### 6.1 Current question / goal

「いま何を考えているか」を表示します。

過去の会話タイトルや最新AI messageを代用せず、canonicalに残されたInquiry / Intent等へ戻れる必要があります。

### 6.2 Current Decision

Decisionがある場合、「何を決めたか」をRecommendationと区別して表示します。

Decisionが存在しない場合、AI suggestionや最有力案をDecision風に見せません。

### 6.3 Why / basis

Decisionに用いた主要basisへ一段で降りられるようにします。

light viewでは要約して構いませんが、audit detailからhistorical refs / Exact Binding等へ戻れる必要があります。

### 6.4 Still unresolved

Unknown、Conflict、residual、reopen conditionを、単なる未入力やwarning数へ潰さず示します。

### 6.5 What changed since the Decision

Decision後に得られたObservationやConflict、重要なRecommendation等を、当時basisと分けて示します。

```text
what changed since D1
  != rewrite basis of D1
```

この差がSEIのresume experienceで特に重要です。resumeが速くてもこの境界を壊すならProduct Value上の改善とは扱いません。

### 6.6 What may need review next

reopen condition、未解決事項、新しいObservation等から、見直し候補をProjectionとして提示できます。

これは自動Decisionではありません。「次に見る価値がありそうなもの」であり、AIを使う場合もRecommendation相当の支援に留めます。

## 7. AIはprovisionalな共同作業者として扱う

AIをfirst sliceへ統合する目的は、canonical meaningの所有者にすることではありません。

AIは、調査、要約、比較、Method Application、Recommendation候補、分類候補等を提供できます。しかし、AI responseをそのままcanonical recordへ流し込む構成は避けます。

### 7.1 Suggestion before commit

AI outputはまず`provisional suggestion`としてSurface上へ現れます。

provisional suggestionはProduct-localなdraft状態であり、SEI Universal Contractへ新しいDraft型を要求しません。

### 7.2 Semantic change preview

canonicalへcommitする前に、利用者または許可されたmachine clientが「何を何として残すか」を確認できるようにします。

```text
AI text
  ↓
proposed semantic changes
  - add Observation O7
  - add Recommendation R3
  - keep Conflict C2 unresolved
  ↓
validate / edit / dismiss
  ↓
canonical commit
```

一つの自然言語responseにObservationとRecommendationが混ざっている場合、単一の「AI回答」recordへ潰すのではなく、必要な意味差へ分ける余地を持ちます。

### 7.3 Correction and dismissal

利用者はAI suggestionを簡単に修正・再分類・却下できる必要があります。

UIは「AIが生成したので変更しにくい」という心理・操作コストを作らないことを目指します。

却下されたsuggestionを、発生済みDecisionやnegative factとしてcanonicalへ残しません。

## 8. AIがなくても成立する

SEIの中核価値はAI service availabilityへ依存させません。

AIが利用不能な場合でも、少なくとも次は可能であるべきです。

- working setを開く。
- Resume Briefを読む。
- audit detailへ降りる。
- manual Observation / Evidenceを追加する。
- Unknown / Conflictを残す。
- Recommendation / Decisionを人間が記録する。
- residual / reopen conditionを確認する。
- historical review / reopenを行う。

AI unavailableはObservationされ得るruntime stateですが、案件上のNoやDecision failureにはしません。

## 9. Progressive Explicitnessを操作として設計する

Progressive Explicitnessを「詳細画面を用意する」だけで満たしたことにはしません。

first sliceでは、各操作で**必要な意味だけを前面に出し、なぜ追加情報が必要なのかを利用者が理解できること**を目指します。

例は次のとおりです。

- 最初のInquiry: 短い問いだけで開始可能。
- Recommendationを採る: basisの確認を促せる。
- Decisionを記録する: 案件に応じてunresolved / Responsibility等を確認できる。
- audit / export: Exact BindingやProvenanceへ降りられる。

high-impactかどうかを一つのUniversal risk scoreへ固定しません。Product / Policy側で詳細化条件を決められる余地を残します。

## 10. Canonical commitの体験

利用者が「保存」したと思った状態と、canonical semantic stateがずれると、SEIの信頼性を損ないます。

そのためfirst sliceでは、semantic changeを次のように扱う方向を採ります。

```text
interaction intent
  ↓
provisional draft
  ↓
semantic change plan
  ↓
validation / policy / concurrency check
  ↓
commit
  ↓
new canonical state
  ↓
projection rebuild
```

`semantic change plan`はfirst sliceのApplication-layer概念であり、現時点でUniversal Contractへ追加しません。

### 10.1 Partial commitを正常に見せない

一操作で複数recordを追加・更新する場合、途中失敗で意味上半端な状態を「保存しました」と見せません。

このfailure boundaryは、CR-73.8 / CR-73.9のRequirement auditを経て、**REQ-0023 — Canonical commitの整合性**と**SCN-0019 — 途中失敗・stale draftを含むcanonical commit**へformalize済みです。

ただし、transaction、atomic replace、append protocol、compensation等のactual mechanismはProduct / Persistence-localな実現方式のままです。REQ-0023 / SCN-0019はUniversal transaction ontologyを要求せず、actual E6 / E7 executionが未検証である間はDesign EvidenceをExecutable Evidenceへ昇格させません。

### 10.2 Stale draftを黙って上書きしない

人間やAIが古いProjectionから作ったdraftをcommitするとき、その後canonical stateが変わっていればreject / rebase / explicit conflictのいずれかへ進みます。

concurrency tokenはsemantic identityではありません。

```text
runtime snapshot version
  != Semantic Revision
```

## 11. External AIへ渡すcontext

Local Single-Nodeの価値には、canonical dataをローカルに保持できることも含まれます。external AIを使う場合、canonical data全体を暗黙に送らない設計を基本とします。

Interaction layerは、taskに必要なcontextを選択し、outbound setを検査可能にします。

最低限、次を区別します。

```text
canonical data retained locally
selected context sent to AI
AI provider state
AI response returned as provisional suggestion
```

AI providerへ送ったことから、Providerにcanonical authorityやDecision Authorityが生じることはありません。

privacy / security上の正式要件はProduct Access / deployment policyと合わせて後続検証します。

## 12. First prototype realization

human usabilityをactualに検証するため、最初のprototype Realizationとして次を有力候補とします。

```text
Local Single-Node Go runtime
  + local human-facing browser UI
  + structured local machine / AI access boundary
  + local durable canonical data
  + optional external AI adapter
```

local browser UIは、短い反復でhuman reviewしやすく、Go runtime / local packageと同じhostに置きやすい利点があります。

ただしこれはprototype選択です。

```text
local browser prototype
  != Web UI is Universal Requirement
  != hosted service required
```

desktop shell、CLI、MCP等を将来追加・交換しても、本書のProduct Experienceを維持できることを優先します。

## 13. Product quality acceptance

first sliceの品質は、画面数やAI turn数ではなく、次の観点で評価します。

### Q1 — Orientation

中断後、chat historyやschema知識なしに「どこまで進んでいるか」を把握できるか。

### Q2 — Historical integrity

current informationとhistorical Decision basisを混同せず読めるか。

### Q3 — Correction cost

AIが誤ったとき、semantic意味差を保ちながら短い操作で修正・却下できるか。

### Q4 — Input burden

最初の有用保存までに不要な詳細入力を要求していないか。

### Q5 — Degradation

AI / external Providerが停止しても、判断記憶の基本操作が利用可能か。

### Q6 — Trustworthy commit

利用者がcommitした意味とcanonical stateが一致し、partial / stale changeが黙って成功していないか。

### Q7 — Net continuity value

SEIによる再構成・誤帰属防止・AI correctionの価値が、capture / review / explicitnessの追加負担を上回るか。

単に機能が多い、記録が詳しい、Resume Briefがきれい、という理由ではSatisfiedにしません。

初期human reviewでは固定SLAや数値thresholdを先取りしません。time-to-orientation、first useful saveまでの必須入力、AI correctionの操作数、audit detailへ降りる頻度等を観測し、どこにProduct Value上の失敗が生じるかを先に確認します。

## 14. Counterfactual Product Value review

first sliceを自己完結的に評価しません。ISSUE-000073では、可能な範囲で次のcounterfactualを持ちます。

```text
A: raw chat / chronological note等の単純baselineから再開
B: SEI canonical meaning + Resume Briefから再開
```

比較対象は製品競争の勝敗を決めるためではなく、SEI固有の意味構造が実際にどのfailureを減らすかを確認するために置きます。

### 観測するもの

- current questionを正しく説明できるか。
- DecisionをRecommendationと混同しないか。
- unresolvedを発見できるか。
- Decision後のObservationを当時basisへ誤帰属しないか。
- resumeまでの時間、操作、主観的mental effort。
- AI suggestionの修正・却下負担。
- first useful saveまでのcapture burden。
- 継続利用したいか。その理由は何か。

### 解釈

```text
faster resume
  + worse historical accuracy
  = Decision Continuity improvementではない
```

raw chat / simple noteで十分である、あるいはSEIのcapture overheadが大きすぎるという結果も正当なProduct Evidenceです。その場合はUIを正当化するためにValue definitionを緩めず、Product hypothesisや対象領域を狭めます。

## 15. Candidate Requirementとexisting Requirementの関係

本書の設計は、多くの部分をcurrent Requirementの組み合わせとして説明できます。

- REQ-0001 — transient surfaceを失っても耐久的意味を引き継ぐ。
- REQ-0005 — historical Decisionを当時basisで再構成する。
- REQ-0006 — AI RecommendationをDecision等へ混同しない。
- REQ-0010 — minimal startから必要に応じて詳細化する。
- REQ-0011 — Resume Brief / working setをcanonical authorityにしない。
- REQ-0014 — residual / reopen conditionを後続reviewへ渡す。
- REQ-0015 — private chain-of-thoughtを必要としない。
- REQ-0019 — human / AIが同じcanonical meaningへ戻る。
- REQ-0023 — one Product Interactionとしてcommitするcanonical meaningの整合性を保ち、partial / staleなsuccessful commitを許さない。

2026-09-16のRequirement auditでは、Candidate Requirementを一律にStable化しませんでした。

- **CR-73.1〜73.7、CR-73.10** — existing Requirement / Scenario、Product / Projection-local設計、またはH1 / H2で観測するhuman Outcomeへ戻せるため、新しいStable Requirementは追加しない。
- **CR-73.8 + CR-73.9** — partial commitとstale writeはmechanismは異なるものの、どちらもsuccessful canonical commitの意味整合性を壊す独立failureであるため、**REQ-0023**へ統合し、**SCN-0019**でAcceptance化した。

```text
REQ-0023 / SCN-0019
  != Universal Transaction entity
  != Universal Snapshot entity
  != Semantic Revision = concurrency version
```

external AI context selection / egress visibilityやcanonical-only resumeのProduct experienceについても、current Contractへmechanismを先取りしません。Decision Continuityやcounterfactual valueそのものを新しいStable Requirementへ機械的に変換せず、actual E1〜E8とH1 / H2から残る独立failureだけを再監査します。

## 16. 非目標

first sliceでは次を完成条件にしません。

- team / multi-user collaboration。
- hosted SaaS deployment。
- formal RBAC / ABAC。
- production IdP。
- autonomous long-running agent orchestration。
- universal workflow state machine。
- arbitrary Provider / model portability。
- TEI executable version exchangeの完了。
- production-grade backup / HA / replication。
- AI output qualityの一般的保証。

これらを後回しにするのは価値が低いからではなく、**PMS-03の利用者体験を最小の条件で検証し、意味基盤だけ強いが使い続けられない製品になることを避けるため**です。

## 17. Evidence状態

```text
Product Design: established by this baseline
Decision Continuity mapping: Design Evidence available
Candidate Requirement audit: completed as Design Evidence
REQ-0023 / SCN-0019 formalization: Accepted / Design Satisfied
E1-E8 prototype / test source: Available
Evidence runner / verifier / one-command capture: Available
E1-E8 actual Go 1.25.x execution: Not Yet Verified
REQ-0023 / SCN-0019 Executable Evidence: Not Yet Verified
H1 human usability Evidence: Not Yet Observed
H2 counterfactual Product Value Evidence: Not Yet Observed
Decision Continuity Product Value: Not Established
Release Evidence: Not Yet Verified for this slice
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

sourceや受入れtoolingが存在することをactual Executable PASSへ読み替えません。また、E1〜E8がPASSした場合でもH1 / H2のhuman observationやDecision Continuity Product Valueへ自動昇格させません。

currentの実行入口とtoolchain blockerは`../../evaluation/personal-inquiry-decision/DECISION_CONTINUITY_EXECUTION_READINESS_2026-09-16.md`を参照します。

## 18. 関連文書

- `SEI_PRODUCT_INTERACTION.md`
- `../value/SEI_DECISION_CONTINUITY.md`
- `../value/SEI_PRODUCT_VALUE.md`
- `../definition/SEI_PRODUCT_SHAPE.md`
- `../roadmap/SEI_PRODUCT_MILESTONES.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `../../evaluation/personal-inquiry-decision/DECISION_CONTINUITY_EXECUTION_READINESS_2026-09-16.md`
- `../../plan/adr/ADR-0005-progressive-semantic-explicitness.md`
- `../../plan/adr/ADR-0010-decision-memory-minimal-semantic-boundary.md`
- `../../plan/adr/ADR-0028-product-interaction-canonical-operation-boundary.md`
- `../../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

## 19. Natural Japanese review

Product Value、Decision Continuity synthesis、V1〜V8、Product Shape、Product Interaction、Local Single-Node Packaging、current Requirement / Scenario、ADR-0005 / 0010 / 0028 / 0029へ戻り、first sliceを「構造化recordを作れる製品」ではなく「文脈を失ったあとに正しく判断へ戻れる製品」として再監査した。

Resume Brief、working set、provisional suggestion、semantic change plan、snapshot tokenは、Product Experienceとprototypeを説明するための概念であり、Universal semantic entityへ昇格させていない。AIは価値を増幅するが、AI availabilityをSEIの基本的なopen / read / Decision / review成立条件にはしていない。

2026-09-16のRequirement auditでは、Candidate Requirementを一律にStable化せず、既存REQでは直接禁止できなかったpartial commitとstale writeだけを「successful canonical commitの整合性」という一つのREQ-0023へ統合し、SCN-0019でAcceptance化した。transaction、ETag、digest、snapshot token等の実現方式はProduct / Persistence-localのままとし、Semantic Revisionへ流用していない。

さらに、SEIだけを使ったusability reviewではProduct Valueを自己証明する危険があるため、raw chat / simple note等とのcounterfactual reviewを維持した。semantic integrity、resume負担、historical誤帰属、AI correction、capture taxを同時に観測し、追加構造に価値差がない結果もProduct hypothesisを修正するEvidenceとして受け取る。

E1〜E8のprototype / test sourceとrunner / verifier / captureが実装済みである現在地を反映したが、actual Go 1.25.x runは未検証、H1 / H2は未観測、Decision Continuity Product Valueは未成立のまま保持した。Design EvidenceをExecutable / human / Adoption Evidenceへ拡大解釈しない停止線を維持したうえで、自然な日本語として全文を再監査した。