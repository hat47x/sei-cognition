# SEI Cognition — Emergent Cognitive Architecture

更新日: 2026-10-02  
状態: **Evaluation-only Architecture Hypothesis（§7.1 / §7.2 / §16の追記は ADR-0035 Proposed による提案・比喩由来の仮説）**  
関連: Issue #381 / #371 / #375 / #378

## 1. 根幹の趣旨

別チャットで進んできたTEI、SUI Sensemaking、ハエ脳由来の非LLM認知層、Personal Inquiry Continuity、local SLM、汎用LLM、組織内遊休計算資源、Distributed Execution Fabricの議論を横断すると、SEI Cognitionは単なる「組織AI基盤」や「LLM前処理器」ではなく、**認知資源の選択・配分・継続を担うCognitive Control Plane**として捉えるのが最も整合的である。

```text
SEI Cognition
  != central intelligence
  != one large model
  != workflow engine
  != distributed scheduler

SEI Cognition
  = durable cognitive state
  + bounded cognitive workspace
  + attention / routing / escalation
  + method / model coordination
  + outcome-informed adaptation
```

**【読み方の注記・ADR-0035 Proposed】** ここでいうCognitive Control Planeは、attention / routing / escalationの**仕組み**の集まりとして読みます。仕組みは交換可能なRealizationまたはProfileであり、SEIのProduct文書が描く「耐久的な意味の台帳」と矛盾しません。制御の判断の意味はCoreに残す意味として扱います（§7.1）。SEIは固定pipelineでも中央の頭脳でもありません。

中核価値は「賢い一回の応答」ではなく、個人・組織が日常系から例外系まで、**必要なときに必要な認知を起動し、認識状態を壊さず、行為と結果まで含めて学習可能な循環を維持すること**にある。

## 2. SUI / SEI / TEIの関係

別々の製品としてだけでなく、異なるplaneを担うと考える。

### 2.1 SUI Sensemaking — Sensemaking Plane

SUIは、まだ十分に構造化されていない素材から意味関係を立ち上げる。

- card / source / raw material
- affinity
- island / subcanvas
- provenance
- cross-canvas relation
- B型文章化
- residual / hold / critique

SUIの役割は「正解を返す」ことより、**素材が語る構造を壊さず、意味形成を助けること**にある。

### 2.2 SEI Cognition — Cognitive Control / Continuity Plane

SEI Cognitionは、SUIや各種Methodで得た意味を含め、認識状態を持続させる。

- Observation
- Interpretation / Hypothesis
- Evidence
- Unknown
- Conflict
- Recommendation
- Decision
- provenance
- revision / supersession
- residual / reopen condition

同時に、次に何をどう考えるかを配る。

- exact / symbolic
- SACS
- static semantic
- local SLM
- KJ / Temporal / Counterfactual / Graph / Simulator
- general-purpose LLM
- external retrieval / tool

### 2.3 TEI — Intent / Execution Plane

TEIは、認知で得たProposal / Decision / approved intentを実行可能な形へ落とす。

```text
Thinking
  != Decision
  != Authority
  != Action Intent
  != Execution
```

TEIが返すExecution Result / Business Outcomeは、再びSEI CognitionのObservationになる。

### 2.4 固定pipelineではなく閉ループ

```text
World / Material
   ↓
SUI Sensemaking
   ↓
SEI Cognition
   ↓
Decision / Authority boundary
   ↓
TEI Execution
   ↓
Outcome
   ↓
Observation / Revision
   ↺
```

単純なroutineではSUIを通らないこともあり、調査だけでTEIへ行かないこともある。したがって固定workflowではなくplaneの責任分離として扱う。

## 3. Durable Semantic StateとCognitive Workspaceを分ける

最重要の分離である。

### Durable Semantic State

長期に意味を守る。

- historical integrity
- provenance
- Unknown / Conflict preservation
- Recommendation / Decision separation
- Revision / Supersession
- provider independence

### Cognitive Workspace

その瞬間の認知に必要な小さなWorking Setを保持する。

- current objective
- selected evidence
- relevant unknowns
- conflicts
- active constraints
- recent change
- candidate methods
- temporary proposals

```text
Cognitive Workspace
  != canonical durable state
```

Workspaceは再生成・圧縮・破棄できる。

この構造はGlobal Workspace / Blackboard型の「専門moduleが限定された共有空間を介して協調する」考え方と構造的に近い。ただしSEI Cognitionは意識モデルを目指さず、**有限な認知帯域の配分問題**として利用する。

## 4. Cognitive Envelope

Method / model / tool間にraw promptをそのまま渡すのではなく、boundedなCognitive Envelopeを作る。

候補は次のとおりです。

```text
Cognitive Envelope
  objective
  task_class
  scope
  selected_records[]
  unknowns[]
  conflicts[]
  constraints[]
  freshness_requirement
  stakes
  authority_boundary
  privacy / data_classification
  latency_budget
  energy_budget
  cost_budget
  allowed_tools
  allowed_actions
  expected_output_role
  provenance_refs[]
```

これはまだUniversal Contractではない。

目的は、provider/modelごとに巨大なcontextを再構築するのではなく、**問題に必要な意味だけをprovider-neutralに持ち運ぶ**ことである。

## 5. Always-on cognitionの意味

常時動くべきなのは生成LLMではない。

### 常時候補

- event detection
- state change detection
- schema / rule validation
- feature extraction
- privacy filtering
- SACS recall
- novelty signal
- stale evidence detection
- known-case matching
- route selection

### 必要時のみ

- local SLM
- large local model
- KJ deep restructuring
- distributed hypothesis exploration
- general-purpose LLM
- fresh Web / external retrieval

```text
continuous awareness
  != continuous deliberation
  != continuous generation
```

## 6. 認知の「代謝」として考える

常時認知層は、入力をすべて保存・推論するのではなく、日々流れ込む情報を少量の意味変化へ変換する。

```text
raw events
  ↓
local filtering
  ↓
features / deltas
  ↓
known pattern?
  ├─ yes -> lightweight update / ignore
  └─ no  -> novelty / conflict candidate
                ↓
           cognitive escalation
```

これは「認知の代謝」と呼べるが、正式用語とする必要はない。

重要なのは、**大半の入力を重い推論へ上げないこと**である。

## 7. Attentionをfirst-class resourceとして扱う

今後のrouterはmodel routingだけでは弱い。

SEI Cognitionが選ぶのは:

- 何を考えるか
- いつ考えるか
- どのMethodで考えるか
- どのmodelで考えるか
- どこで実行するか
- どのdataを見せるか
- いつ停止・エスカレーションするか

評価軸は単一scoreへ潰さない。

```text
quality
latency
energy
privacy
cost
freshness
stakes
novelty
availability
explainability
```

最近のLLM routing研究でも、弱いmodelから始めて品質が不足した場合に強いmodelへescalateするcascadeが有効であることが示されている。SEI Cognitionではその考え方をmodelだけでなくMethod / Tool / Compute Tierまで拡張する。

### 7.1 制御の仕組みと制御の判断の意味（提案 — ADR-0035）

上のrouterとCognitive Control Planeは、ADR-0035（Proposed）の規則で読みます。routing、escalation、attentionの配分といった**仕組み**は、交換可能なRealizationまたはProfileです。何を見て、何を意図的に見送り、どのMethodやモデルをなぜ選び、何を保留または上位へ回したかという**判断の意味**は、Coreに残す意味として扱います。

```text
control mechanism = Realization / Profile
meaning of a control decision = Coreに残す意味
router choice != semantic confidence
```

### 7.2 予期された不確実性と予期しない不確実性（比喩由来の仮説）

神経系の比喩から、次の問いが生じます。これは**比喩由来の仮説**（CSWの用語では`framework_generated`であり、対象で支持された`target_supported`ではない）であり、対象で確かめるまでは要件にも型にもしません。

- **予期された不確実性**（既に認めているUnknown）と、**予期しない不確実性**（想定外のConflictやnovelty）を、別の注意信号として扱えるか。前者は予定された再訪へ、後者はChallenge Path（§16）へ向ける。出典の着想はYu & Dayan (2005)。
- 判断の時点で「正しければ何が観測されるはずか」を**期待の記録**として残し、外れた観測を見直しの引き金にできるか。これは既存のreopen conditionで表せる可能性があり、ISSUE-000086で既存契約の組合せとして試す。

注意信号の具体的な形や、期待の記録のschemaは、ここでは定めません。

## 8. SACSの位置づけを再確認する

ハエ脳由来の議論から得た価値は「脳を再現すること」ではない。

有効だった抽象はは次のとおりです。

- sparse representation
- spreading activation的な候補想起
- competition
- inhibition
- novelty
- event-driven processing

したがってSACSは、Workspaceへ何を上げるかを決める**pre-attentive primitive**として置く。

```text
SACS activation
  != Truth
  != confidence
  != Unknown
  != Decision
```

SACSが強いのは「候補を安く絞ること」であり、「意味を確定すること」ではない。

## 9. local SLMと汎用LLMの分業

### local SLM

bounded Working Setについて:

- compare
- classify
- explain
- contradiction candidate
- hypothesis candidate
- short plan

を担う。

### general-purpose LLM

- broad cross-domain synthesis
- difficult language interpretation
- novel problem decomposition
- large-context reasoning
- fresh external retrievalとの統合

を担う。

重要なのは、汎用LLMを排除しないことである。

```text
cheap cognition first
  -> bounded local reasoning
  -> broad general reasoning when needed
```

## 10. Background Cognition / Incubation

Organization Cognitive Fabricと遊休計算資源の議論から、新しい役割が見える。

遊休computeはinteractive responseを速めるためだけでなく、**前景作業を邪魔しない背景認知**へ使える。

候補は次のとおりです。

- alternate hypothesis exploration
- counterexample generation
- stale assumption detection
- repository / document pre-reading
- cross-model critique
- scenario sweep
- unresolved Unknown再調査候補
- related historical case discovery

出力はProposal Poolとして扱う。

```text
background result
  != current belief
  != Decision
  != automatic notification
```

必要な時だけWorkspaceへ上げる。

## 11. 計算量は「同じ答えを何度も作る」より認知多様性へ使う

分散資源で同一promptを大量に回すだけでは価値が薄い。

より有効なのは、異なる役割を与えること。

```text
worker A -> supporting evidence
worker B -> counterexample
worker C -> alternative causal model
worker D -> risk
worker E -> historical analogy
worker F -> fresh-data gap
```

fan-inではAgreementだけでなくConflict / Minority Hypothesis / Residualを残す。

```text
ensemble majority
  != Truth
```

**computeをtoken量ではなく探索幅へ交換する**ことが、SEI Cognitionらしい分散認知になる。

## 12. Locality-first Cognition

wearable / home / organization edgeの議論から、dataを中央へ集めることを前提にしない。

```text
raw private data
  stays local
      ↓
local cognition
      ↓
bounded feature / event / semantic proposal
      ↓
upper tier if policy allows
```

これによりは次のとおりです。

- privacy
- bandwidth
- latency
- resilience

を改善できる。

```text
device can compute
  != device may see all data
```

は継続して重要な停止線とする。

## 13. Distributed Execution Fabricとの分離

SEI Cognitionは「どの認知jobが必要か」を決める。

Distributed Execution Fabricは「そのjobをどこで実行するか」を扱う。

```text
Cognitive Policy / Job Semantics
        ↓
Thin Job Envelope
        ↓
Distributed Execution Fabric
        ↓
HTCondor / Ray / other backend
```

FabricはTruth / Unknown / Decision / KJ relationを知らない。

この分離によりTEI / SUIも同じExecution Fabricを利用できる。

## 14. Outcomeから何を学ぶか

「学習」をmodel trainingだけに限定しない。

少なくとも3種類を分ける。

### Epistemic Learning

世界について何を知ったか。

- new evidence
- hypothesis revision
- conflict resolution
- decision outcome

### Cognitive Policy Learning

どのMethod / model / routeがどのproblem classで有効だったか。

- local SLMで十分だったか
- general LLM escalationが必要だったか
- SACS recallが有効だったか
- KJ / graph / simulatorのどれが役立ったか

### Execution Learning

どのprovider / resourceが実行上どうだったか。

- latency
- failure
- cost
- resource contention
- preemption

これらを混ぜない。

```text
method efficacy
  != semantic truth

fast provider
  != better reasoning
```

## 15. Routerは将来「経験」から改善できる

初期はdeterministic policyでよい。

将来は次のとおりです。

```text
problem features
  + stakes
  + novelty
  + prior method outcomes
  + current resource state
      ↓
route policy
```

へ発展できる。

ただし、router optimizationの目的を単純なcost最小化にしない。

高価なmodelを減らすこと自体ではなく、**必要な認知品質を保ちながら、適切な場所へ適切な認知を配ること**が目的である。

## 16. Cognitive Challenge Path

novelty / contradiction / stale evidence / suspicious provider outputを「エラー」と即断せず、Challenge Pathを起動する。

候補は次のとおりです。

```text
trigger
  ↓
independent retrieval
  ↓
alternative method
  ↓
counterexample search
  ↓
freshness check
  ↓
conflict preserved
  ↓
human / stronger reasoner if needed
```

これは認知の健全性を保つ仕組みになり得る。

SACS noveltyはChallenge起動の一Signalになれるが、Unknownそのものではない。

**【比喩由来の仮説・ADR-0035】** 葛藤の監視（Botvinick et al. 2001）の考え方に近く、Conflictやnoveltyなど「予期しない不確実性」はChallenge Pathを起動する信号に、Unknownなど「予期された不確実性」は予定された再訪の対象にする、という分け方を試せます。また、期待の記録（§7.2）が外れた観測は、Challenge Pathまたはreopen conditionの入口になり得ます。いずれも評価仮説であり、Stable Requirementや型の根拠ではありません。エピソードからパターンを取り出すときにエピソードを書き換えない、という相補的学習系（McClelland et al. 1995）の着想も、Pattern / Cognitive MethodとDecisionの区別を考える手がかりに留まります。

## 17. Cognitive Commonsとしての組織価値

SEI Cognitionの共有財産性は、単に「全員が同じAIを使う」ことではない。

共有される価値はは次のとおりです。

- methods
- reusable evidence structures
- historical cases
- unresolved questions
- decisions and rationale
- provider capability observations
- learned routing efficacy
- organizational vocabulary / reference structures

である。

個人や部門のprivacy / access境界を保ちながら、再利用可能な認知資産を育てる。

これは「central intelligence」より**shared cognitive infrastructure**という位置づけに整合する。

## 18. Personal Inquiry Continuityとの接続

個人向けInquiryは、この全体構造の縮小版として見ることができる。

```text
Inquiry
  ↓
Durable Semantic State
  ↓
queryless Orientation / Workspace
  ↓
SACS / local SLM / general LLM
  ↓
Recommendation / Decision
  ↓
later evidence
  ↓
reorientation
```

したがってPersonal Inquiry Continuityは別製品思想ではなく、SEI Cognitionの基本原理を個人単位で検証するdogfood surfaceとして価値がある。

## 19. 新しい全体像

```text
                 ┌─────────────────────┐
                 │   Durable Semantic   │
                 │       State         │
                 └─────────┬───────────┘
                           │
           ┌───────────────▼───────────────┐
           │      Cognitive Workspace       │
           │ objective / evidence / unknown │
           │ conflict / constraints / delta │
           └───────────────┬───────────────┘
                           │
                 ┌─────────▼─────────┐
                 │ Cognitive Control │
                 │ attention / route │
                 │ budget / escalate │
                 └──────┬─────┬─────┘
                        │     │
          ┌─────────────┘     └──────────────┐
          ▼                                  ▼
  Lightweight Cognition              Heavy Cognition
 exact / symbolic / SACS      local SLM / Methods / LLM
          │                                  │
          └──────────────┬───────────────────┘
                         ▼
                 Proposal / Analysis
                         │
                 Decision / Authority
                         │
                         ▼
                        TEI
                         │
                     Execution
                         │
                      Outcome
                         │
                         └──────→ Observation / Revision
```

SUIはこのloopのSensemaking側へ深く接続し、Distributed Execution Fabricは下側の実行資源配置を支える。

## 20. 次に実証すべき仮説

### H1 — Workspace Compression

raw context全体よりbounded Cognitive Workspaceを使った方が、小型modelでも品質を保てるか。

### H2 — Routing Gain

always-general-LLMより、deterministic / SACS / local SLM / general LLM cascadeの方がqualityを落とさずcost / latency / privacyを改善できるか。

### H3 — Background Incubation Value

idle computeをalternate hypothesis / critiqueへ使うことで、後日のInquiry再開や組織判断が改善するか。

### H4 — Cognitive Diversity Value

同一modelの多数samplingより、異種Method / role分担fan-outの方がConflict / counterexample / residual発見に優れるか。

### H5 — Locality Value

raw dataを中央へ送るより、local feature / proposal化した方がprivacyを改善しつつ認知品質を維持できるか。

### H6 — Outcome-informed Routing

過去のMethod Application / outcomeを使うことで、static routingより適切なroute選択ができるか。

2026-09-18時点では、first executable sliceを `evaluation/sei-cognition-orchestration/prototype-go/cognitivepolicy/` へ追加した。

ここで学習対象にしているのはsemantic truthではなく、caller-ownedなproblem classごとの**route efficacy**だけである。

```text
Outcome Evidence
  ↓
route efficacy aggregation
  ↓
immutable candidate policy version
  ↓
explicit activation
```

candidateを生成しただけではactive routingを変更しない。既存versionはimmutableに保持し、明示activationとrollbackを分離した。

また、次をpolicy learningの外側に残している。

- allowed route
- minimum escalation floor
- Authority
- permission / data access
- semantic truth
- Recommendation / Decision correctness

execution failureもcognitive insufficiencyへ自動変換しない。Execution LearningとCognitive Policy Learningを別軸のまま保持する。

synthetic replayでは、routine problem classについてadapted / staticの両policyがsuccess rate 1.0を保ったまま、unnecessary escalation rateをstatic 1.0からadapted 0へ下げるfixtureを確認した。一方、distribution shiftを与えた別fixtureではadapted policyのsuccess rateが0.5、static policyが1.0となり、regret-against-static rate 0.5を観測した。

したがってcurrent Evidenceは、

```text
past route efficacy
  may reduce unnecessary escalation
  != future route guarantee
```

を支持するに留まる。

特に、cost / latency / escalation削減だけをrouter最適化の成功条件にしない。distribution-shift regret、safety floor preservation、policy version provenance、rollback reproducibilityを別々の評価軸として保持する。

詳細Evidenceは `outcome_informed_routing_evidence_2026-09-18.json` を参照する。

これは **limited synthetic executable evidence** であり、real problem class、Outcomeの評価主体、selection-bias補正、statistical confidence、drift / expiry、automatic rollback criteria、production routing policyはNot Yet Verifiedである。Stable Requirementへの昇格も行わない。

## 21. Requirement化を急がないもの

次は現時点ではArchitecture Hypothesisであり、Stable Requirementへ即時昇格しない。

- Cognitive Workspaceの具体schema
- Cognitive Envelope
- attention budget
- background incubation
- Challenge Path
- routing policy learning
- organization-wide Cognitive Commons

まずExecutable / Outcome Evidenceを取る。

## 22. 停止線

```text
workspace content != canonical truth
router choice != semantic confidence
novelty != Unknown
majority != Truth
proposal != Recommendation
Recommendation != Decision
Decision != Authority
scheduler success != cognitive success
resource availability != permission
background cognition != automatic notification
model improvement != product value
```

SEI Cognitionの価値は、モデルを賢く見せることではなく、**認知の連続性・多様性・適切な配分・意味境界を保つこと**に置く。
