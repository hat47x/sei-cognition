# Organization Cognitive Fabric — Idle Compute as Cognitive Capacity

更新日: 2026-09-12  
状態: **Evaluation-only Distributed Cognition Design**  
関連: Issue #376 / `README.md`

## 1. 根幹の趣旨

組織には、常時100%使われていない計算資源が存在する。

- developer workstation
- desktop GPU
- build / analysis server
- shared GPU server
- VDI / lab machine
- edge server
- on-prem compute node

SEI Cognitionでは、これらを単なる余剰capacityとしてではなく、**policyの範囲内で一時的に借りられる認知capacity**として利用できる可能性を評価する。

ただし、業務端末や遊休資源はavailabilityが不安定である。

したがって、Organization Cognitive Fabricはproduction critical pathを支える固定clusterではなく、**preemptible / opportunistic / capability-awareな認知job pool**として設計する。

## 2. 何を分散するか

最初に「modelを分散する」と考えない。

分散単位は Cognitive Job とする。

```text
Cognitive Job
  ├─ objective
  ├─ input references / bounded payload
  ├─ required capability
  ├─ data classification
  ├─ locality constraint
  ├─ expected cost
  ├─ latency class
  ├─ preemptibility
  ├─ resumability
  └─ output contract
```

これにより、一つの巨大modelを複数不安定端末へ跨がせる以外の選択ができる。

## 3. 向くjob

### 3.1 Embarrassingly Parallelな認知

- 10個の仮説を独立評価する
- 複数planを別model / Methodで評価する
- 多数documentを独立pre-analyzeする
- test case / counterexample候補を大量生成する
- code / log / incident片を別々に分類する

この種のjobはworker lossに強い。

### 3.2 Background Cognition

- overnight document enrichment
- repository change analysis
- semantic index rebuild
- long-running comparison
- historical re-evaluation
- stale Inquiryのreorientation material更新候補

interactive latencyを要求しないため、遊休資源と相性がよい。

### 3.3 Ensemble / Cross-check

- 同一Working Setを複数modelへ送る
- specialized MethodとLLMを並行実行する
- independent critiqueを作る
- minority hypothesisを保持する

単一model出力へ収束しすぎるのを防ぐ用途がある。

### 3.4 Search / Exploration

- candidate method exploration
- architecture alternatives
- counterfactual search
- parameter / scenario sweep

探索幅を計算資源へ交換できるproblemに向く。

## 4. 向かないjob

- hard real-time control
- 利用者操作へ直結する低latency必須処理
- 途中worker lossで全体が無効になる巨大同期job
- raw confidential dataを端末横断させる必要がある処理
- endpointへ長時間高負荷を強いる処理
- canonical stateをworker local memoryだけへ置く処理

## 5. Placementの基本形

```text
Cognitive Job
  ↓
Capability Requirements
  ↓
Policy Filter
  ↓
Eligible Resource Set
  ↓
Cost / Latency / Locality / Energy ranking
  ↓
Placement
  ↓
Execution
  ↓
Validated Result / Proposal
```

### Capability Requirements例

- CPU architecture
- RAM
- VRAM
- supported model runtime
- static semantic encoder
- SACS
- local SLM class
- larger model class
- network bandwidth
- confidential-compute capability

### Policy Filter例

- data classification
- user / department boundary
- allowed device class
- offline-only
- no raw source export
- geographical / network segment locality
- working-hours prohibition

## 6. Resource advertisement

workerは「私はGPUです」とだけ通知しない。

候補:

```text
Resource Advertisement
  device_class
  trust_zone
  cpu_capacity
  memory_available
  accelerator_type
  accelerator_memory_available
  supported_runtimes
  cached_models
  current_load
  thermal_state
  power_state
  foreground_priority
  expected_idle_window
  preemption_latency
```

これらはoperational dataであり、Universal semantic meaningではない。

## 7. Foreground First

業務端末ではforeground利用を常に優先する。

```text
employee workload
  > cognitive background job
```

worker条件候補:

- CPU loadが一定以下
- GPU foreground processなし
- AC power接続時のみ
- battery threshold以上
- thermal headroomあり
- user active時はheavy job停止
- business-hour policyに従う

jobはpreemptibleを基本とし、checkpointまたはsmall independent unitへ分割する。

## 8. 分散推論の二方式を分ける

### A. Job-level Distribution

複数workerが独立jobを実行する。

```text
hypothesis A -> worker 1
hypothesis B -> worker 2
critique     -> worker 3
source scan  -> worker 4
```

first choiceはこちらとする。

理由:
- heterogeneous resourceへ載せやすい
- preemptionしやすい
- network latencyへ強い
- worker churnへ強い

### B. Model-level Distribution

一つのmodel inferenceを複数GPU / nodeへ分割する。

- tensor parallel
- pipeline parallel
- expert parallel
- prefill / decode disaggregation

これはstable GPU nodeやorganization edgeに向く。

randomなemployee workstation群へ安易に適用しない。

## 9. Locality-first Data Handling

可能な限り、dataをcomputeへ動かすよりcomputeをdataへ寄せる。

例:

```text
confidential repository
  stays in department zone
      ↓
local worker computes features / proposal
      ↓
only bounded result crosses zone if policy permits
```

raw sourceを中央へ集めることを前提にしない。

wearable / home deviceでも同じ原則を利用できる。

## 10. Cognitive Fan-out / Fan-in

高度な認知演算では、一つの長い推論を強くするだけでなく、探索幅を増やす方法がある。

```text
Problem
  ↓
Decompose
  ↓
Fan-out
  ├─ factual check
  ├─ alternative hypothesis
  ├─ counterexample
  ├─ risk analysis
  ├─ analogy search
  └─ plan candidate
  ↓
Fan-in
  ↓
Conflict / Agreement / Residual
  ↓
stronger reasoner only if needed
```

SEI Cognitionのdurable semanticsがあることで、fan-out結果を単なる文章群ではなく、role付き候補として再統合できる可能性がある。

## 11. 汎用LLMとの協調

Organization Cognitive Fabricは汎用LLMの代替ではない。

むしろ、汎用LLMへ渡す前に次を行う。

- source pre-reading
- candidate fact extraction
- contradiction detection
- related historical case retrieval
- alternative generation
- relevant context selection
- missing evidence detection

汎用LLMへは、可能な限りboundedな問題と整理済み材料を渡す。

逆に、汎用LLMの出力を複数local workerでfact-check / policy-check / consistency-checkする後処理も考えられる。

## 12. Failure Model

遊休資源は消えることを正常系として扱う。

```text
worker disappeared
  != cognitive state lost
  != historical state rewritten
```

必要な性質:

- idempotent job
- bounded retry
- checkpoint where useful
- duplicate result detection
- worker lease / heartbeat
- result provenance
- no canonical state only on worker

## 13. Security Boundary

遊休計算資源利用は、単純なcluster enrollmentでは危険である。

最低限分けるもの:

- device identity
- device trust level
- user identity
- data classification
- job permission
- model / tool permission
- network zone
- result disclosure permission

```text
device can compute
  != device may see all data
```

## 14. Scheduling objective

単一scoreへ潰さない。

独立に見る候補:

- latency
- energy
- marginal cost
- privacy locality
- reliability
- model quality
- queue time
- interruption risk
- thermal impact

routine jobとdeep exploration jobでは最適配置が異なる。

## 15. 現行技術との関係

Ray Serve / Ray Serve LLM等は、multi-node、multi-model、custom routing、accelerator-aware placement、autoscalingを提供しているため、Organization Cognitive Fabricの一Realization候補になり得る。

vLLM / SGLang等のmodel-serving engineも候補である。

ただしSEI Cognitionの上位設計では、これらをContractへ昇格させない。

```text
Cognitive Job / Capability / Placement semantics
  != Ray
  != vLLM
  != specific cluster manager
```

## 16. 最初の評価slice

いきなり社内PCをcluster化しない。

第1段階:

1. fixed 2–3 local worker fixture
2. worker capability advertisement
3. low-priority batch job
4. synthetic preemption
5. restart / retry
6. sensitive / non-sensitive placement test
7. fan-out / fan-in result comparison

第2段階:

- one real idle workstation
- one stable local server
- model cache aware routing
- overnight cognition

第3段階で初めて複数department / heterogeneous endpointを検討する。

## 17. 成否を見る指標

- foreground interference
- successful preemption rate
- job completion under worker churn
- useful compute-hours recovered
- energy per completed cognitive job
- cloud / external LLM call reduction
- end-to-end reasoning quality
- fan-out diversity
- unsupported claim rate
- privacy policy violation count

重要なのは、idle compute利用率そのものをKPIにしないことである。

```text
more utilized compute
  != better cognition
```

## 18. 停止線

- idle resource != free authority
- candidate result != Truth
- ensemble majority != Decision
- model confidence != semantic confidence
- worker availability != required dependency
- cluster scheduler != cognitive policy authority
- device enrollment != data access permission
- distributed trace != required private chain-of-thought
