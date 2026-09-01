# SOZA Product Interaction

更新日: 2026-09-01  
状態: **Current Product Interaction Design Baseline**

## 1. この文書の役割

この文書は、SOZAを最初に利用可能な製品として人間とAIが扱うとき、**どのような仕事を、どの意味境界を保ったまま、一続きに行える必要があるか**を定めます。

ここで定めるのは、特定のWeb画面、desktop framework、CLI構文、HTTP endpoint、MCP tool名ではありません。UIやprotocolより先に、利用者が何をできる必要があるかと、その操作がどのcanonical meaningへ接続するかを定めます。

```text
Product Interaction
  = usable work operations over canonical meaning
  != UI layout
  != chat transcript
  != workflow state machine
  != agent orchestration
```

SOZAのProduct Interactionは、`SOZA_PRODUCT_SHAPE.md`のWork / Interaction Surfaceを具体化するProduct-level baselineです。portable semantic agreementが必要になった場合だけContractへ、重要なArchitecture判断はADRへ、実装方式はRuntime / Adapterへ落とします。

## 2. first usable interactionで守る中心

最初のInteractionで重要なのは、人間とAIに同じ見た目を与えることではありません。入口や表現が異なっても、**同じcanonicalな判断文脈へ戻れること**です。

```text
human view != AI view
human view -> canonical meaning
AI view    -> canonical meaning
```

画面、会話、prompt、worklist、canvas、CLI出力などはProjectionになり得ますが、それ自体を唯一の意味上の正本にはしません。

特に次を守ります。

- 人間向けUIだけにDecisionやUnknownの意味を閉じ込めない。
- AI向けpromptやconversation historyだけにObservationやRecommendationの意味を閉じ込めない。
- Projectionを作り直してもcanonical artifactを失わない。
- AIのprivate chain-of-thoughtをInteraction成立条件にしない。
- actorが人間かAIかという種別だけからAuthority、Responsibility、信頼度を推定しない。
- 低影響な仕事へ最大詳細を強制せず、必要なときだけ詳細へ降りられるようにする。

## 3. 新しいUniversalな「作業単位」は追加しない

最初のInteractionを実装するためだけに、`Case`、`Session`、`Workspace`、`Thread`などをUniversal Coreへ追加しません。

利用者が画面上で一つの「案件」や「作業」を開くことはあり得ますが、そのまとまりはProduct / Projection上のworking setとして扱えます。耐久的な意味は、既存のInquiry、Observation、Unknown / Conflict、Cognitive Method Application、Recommendation、Decision、Responsibility、Reference、Lineage等へ置きます。

```text
workspace / session / thread
  = interaction convenience
  != automatically a Universal semantic entity
```

複数domainで独立した意味上の必要性が実証された場合だけ、別途Requirement / ADRを通して再検討します。

## 4. 利用者が行う最小の仕事

first usable interactionでは、少なくとも次の仕事を自然につなげられる必要があります。これは固定workflowではなく、利用可能な操作のまとまりです。

### 4.1 始める・開く

利用者は、問い、目的、短い文脈など、現在分かっている最小限からInquiryを始められます。

既存のInquiryやDecisionを開き直し、当時のbasis、Unknown / Conflict、残差、reopen condition等から続きを始めることもできます。

最初から最大field setを入力させません。

### 4.2 情報を加える

人間、AI、外部Provider等から得たObservationやEvidenceを追加できます。

出所、発見経路、Interpretation、EvidenceUse等を区別する必要がある場合は、後から追える形で明示できます。単純な案件では不要な詳細を一律必須にしません。

### 4.3 分からないこと・食い違いを残す

Unknown、Conflict、保留事項を「入力不足のエラー」として消さず、そのまま判断文脈へ残せます。

Decisionを行っても、未解決事項が自動的にresolvedへ変わることはありません。

### 4.4 方法を適用した記録を残す

必要な場合、調査、比較、統合、検査等に用いたCognitive Method Applicationを記録できます。

Interaction SurfaceはMethodの実行UIを一種類に固定しません。Prompt、人間手順、外部tool等のRealizationが変わっても、必要なinput / output / residualをcanonical meaningへ戻せることを優先します。

### 4.5 提案する

人間またはAIはRecommendationを追加できます。

Recommendationを追加したことだけでDecision、Authority、Executionが成立したことにはしません。

### 4.6 決める

必要な主体はDecisionを記録できます。

その際、案件の影響度に応じて、basis、主要なConstraint、未解決事項、Responsibility等を必要な粒度で残せます。高影響な判断で必要な意味をlight viewの都合だけで削りません。

### 4.7 実行後の結果を戻す

外部Capability / Providerで実行した結果を、新しいObservationとして判断文脈へ戻せます。

実行成功を過去Decisionの正しさへ自動変換しません。また、実行後に得たObservationを過去Decisionのbasisへ遡って混入させません。

### 4.8 読み直す・再開する

利用者はlight viewから現在の主要点を把握し、必要になったときだけaudit detailへ降りられます。

後日、新しいEvidenceや環境変化が生じた場合は、過去Decisionを削除せず、残差や新しいObservationからInquiry / reviewを再開できます。

## 5. light viewとaudit detail

日常利用では、canonical recordの全fieldを常時表示しません。

### light viewで優先するもの

案件に応じて、たとえば次を簡潔に見せます。

- 何を考えているのか。
- 現在重要なObservationやRecommendationは何か。
- Decisionがある場合、何を決めたのか。
- まだ分からないこと、食い違っていることは何か。
- 後から見直す必要がある条件や残差は何か。

これは固定field listではありません。低影響な利用へ過剰な表示・入力を強制しないためのProjection方針です。

### audit detailで確認できるもの

必要な場合、少なくとも次へ降りられる余地を持たせます。

- Decision basis
- Provenance / discovery / derivation
- Responsibility / Authorityに関わる文脈
- Revision / Semantic Lineage
- Exact Bindingが必要な可変Artifact
- Unknown / Conflict / withheld等の認識状態
- Cognitive Method Applicationの主要input / output / residual

```text
light view
  != incomplete canonical storage

audit detail
  != separate source of truth
```

light / auditは同じcanonical meaningから作るProjectionとして扱います。

## 6. 人間向け入口

人間向けSurfaceでは、semantic modelの型名を覚えなければ使えない製品にしません。

利用者の自然な仕事として「問いを始める」「情報を加える」「分からない点を残す」「提案を見る」「決める」「後で読み直す」といった操作を前面に出し、必要な意味明示性を裏側でcanonical artifactへ接続します。

ただし、分かりやすさのために意味差を消してはいけません。たとえばRecommendationとDecisionを一つの「回答」へ潰したり、Unknownを空欄として捨てたりしません。

## 7. AI向け入口

AI向けSurfaceでは、人間向け画面を画面操作させることを必須にしません。AIが必要なcanonical contextを構造化して読み、許可された操作を通してObservation、Method Application、Recommendation等を追加できる境界を持てます。

AI向けSurfaceは、次を満たす必要があります。

- 取得したProjectionからcanonical referenceへ戻れる。
- 書き込み時に、何をObservation、Recommendation、Decision等として記録するかを明示できる。
- private chain-of-thoughtの提出を要求しない。
- AIであることだけを理由にDecision権やAuthorityを付与しない。
- human-facing UIだけに存在する隠れた意味へ依存しない。

protocolはHTTP API、MCP、local process、SDK等を候補としますが、本baselineでは固定しません。

## 8. Human / AI parityの意味

Human / AI parityは、両者へ同じUIを提供することではありません。

次の性質を満たすことを指します。

1. 同じcanonical artifactを参照できる。
2. 同じ意味上の区別を失わない。
3. 一方が追加した耐久的意味を、他方が別Projectionから再読できる。
4. 一方だけにしか存在しない会話履歴や画面状態を、判断再構成の必須条件にしない。
5. actor kindからAuthority / Responsibilityを自動推定しない。

人間とAIで入力支援や表示形式が異なることは許容します。

## 9. first interactionの論理操作境界

protocol名やfunction名を固定せず、実装が少なくとも次の論理操作を提供できることを求めます。

```text
start / open
read light projection
read audit / structured projection
add observation / evidence
record unknown / conflict
record method application
record recommendation
record decision
return resulting observation
review history / reopen
```

これらはUniversal workflow stateではありません。必要な操作が存在することを示すProduct Interaction上の分類です。

一つの汎用`append anything` APIだけでも内部実装は可能ですが、利用者やAIが意味種別を誤って混同しないよう、Surface上では意味差を確認できることを優先します。

## 10. protocolとUIの扱い

現時点では、Web UI、desktop UI、CLI、HTTP API、MCPのいずれもProduct標準として確定しません。

ただし、Interaction boundaryを実証するreference probeでは、次の二つの入口を意図的に分けて試す価値があります。

- **human-oriented probe** — 人間が最小入力から開始し、light / auditを往復できる簡素なtext / CLI相当の入口。
- **machine-oriented probe** — AIやtoolが構造化された操作を行うJSON / process相当の入口。

このprobeは製品UI選定ではありません。同じinteraction coreへ異なるSurfaceを載せてもcanonical meaningが保たれるかを確認する実験です。

```text
reference probe surface
  != supported production surface decision
```

実証後、human usability、AI integration、Packaging / Deploymentとの整合を見て、最初のsupported surfaceを別途判断します。

## 11. Requirement / Acceptance監査

今回のInteraction boundaryは、現時点では新しいProduct Requirementを必要としません。

主な根拠は既存Requirementで表現されています。

- REQ-0001 — 技術やUIが変わっても意味を引き継ぐ。
- REQ-0005 — Decisionを後から再構成する。
- REQ-0006 — Recommendation / Decision / Authority / Executionを分ける。
- REQ-0010 — 低影響案件へ最大詳細を強制しない。
- REQ-0011 — Projectionを意味上の正本にしない。
- REQ-0014 — 残差と再開条件を保持する。
- REQ-0015 — private chain-of-thoughtへ依存しない。
- REQ-0019 — 人間とAIの双方が意味を読める。

Acceptanceについても、SCN-0013「簡略UIとcanonical meaningを両立する」とSCN-0018「Inquiryから実行後の再検討までを一続きに扱う」を組み合わせることで、Design上の必要性は表現できます。

そのため、Interactionを理由に新しいREQ / SCN IDを機械的に追加しません。reference probeで既存Scenarioでは表現できない失敗が見つかった場合だけ、追加を再検討します。

## 12. reference probeのExecutable Evidence条件

PMS-03をExecutable Evidenceへ進めるため、後続probeでは少なくとも次を検査します。

1. 人間向け入口と機械向け入口が同じcanonical sourceを利用する。
2. 最小入力からInquiry相当の文脈を開始でき、後から詳細化できる。
3. AI側が追加したObservation / Recommendationを、人間側が別Projectionから再読できる。
4. 人間側が記録したDecisionを、AI側がRecommendationへ読み替えずに取得できる。
5. Unknown / Conflictを未入力やfalseへ平坦化しない。
6. light Projectionを削除・再生成してもcanonical sourceが変化しない。
7. audit Projectionからbasis / provenance / responsibility等へ降りられる。
8. hidden reasoning transcriptなしで一連の操作を成立させる。
9. 実行後Observationを追加しても、過去Decisionのbasisを改変しない。
10. actor kindからAuthority / Responsibilityを推定しない。

このprobeのPASSは、production UIの使いやすさやPMS-03全体のOperational / Adoption Evidenceを意味しません。

```text
interaction probe PASS
  != production UX proven
  != supported protocol finalized
  != packaged product proven
  != user-value outcome proven
```

## 13. 現時点で決めないこと

このbaselineでは、次をまだ固定しません。

- Web / desktop / CLIのどれを最初の主要human-facing surfaceにするか。
- HTTP API / MCP / SDKのどれを最初の主要AI-facing surfaceにするか。
- login / workspace / tenant等のIdentity / Collaboration設計。
- production Storage。
- UI visual design。
- impact levelを判定するproduction Policy / Profile。
- agent orchestrationやworkflow engine。

Packaging / DeploymentはISSUE-000046、Identity / Authorization / CollaborationはISSUE-000047で別途扱います。

## 14. Evidence状態

- Product Interaction Design Evidence: **Established by this baseline**
- Executable Evidence: **Not Yet Verified for first usable interaction**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

current V6 / V7 Projection evaluationやSCN-0018 harnessには関連するscoped Executable Evidenceがありますが、それらをfirst usable interactionの実証へ自動昇格させません。

## 15. 関連文書

- `../definition/SOZA_PRODUCT_SHAPE.md`
- `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/issue/ISSUE-000045-define-first-usable-product-interaction-boundary.md`
- `../../plan/adr/ADR-0028-product-interaction-canonical-operation-boundary.md`
- `../../plan/issue/ISSUE-000053-materialize-first-product-interaction-reference-probe.md`

## 16. Natural Japanese review

Product Value、Product Shape、PMS-03、REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019、SCN-0013 / 0018、current Projection evaluationとend-to-end Semantic Product Journeyへ戻り、利用者の仕事とcanonical meaningの関係からInteraction boundaryを組み直しました。UI、conversation、session等を意味上の正本へ昇格させず、人間とAIが異なる入口から同じ意味へ戻れることを中心に据えています。そのうえで、意味、要求強度、未決事項、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。