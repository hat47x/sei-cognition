# Organization Cognitive Fabric — Idle Compute as Cognitive Capacity

更新日: 2026-09-12  
状態: **Evaluation-only Distributed Cognition Design**  
関連: Issue #376 / Issue #378 / `README.md` / `../distributed-execution-fabric/README.md`

## 1. 根幹の趣旨

組織には、常時100%使われていない計算資源が存在する。

- developer workstation
- desktop GPU
- build / analysis server
- shared GPU server
- VDI / lab machine
- edge server
- on-prem compute node

SEI Cognitionでは、これらを単なる余剰capacityではなく、**policyの範囲内で一時的に利用できる認知capacity**として扱える可能性を評価する。

ただし、この文書はdistributed schedulerを設計するものではない。

```text
Organization Cognitive Fabric
  = how cognition uses organizational capacity

Distributed Execution Fabric
  = how jobs are placed / run / retried / preempted
```

実行面はTEI / SUIとも共有し得る別境界へ分離し、既存OSSを優先する。

## 2. Cognitive Fabricが所有するもの

SEI Cognition側で扱うのは、認知上のjob意味である。

```text
Cognitive Job
  objective
  bounded evidence / context refs
  cognitive method / capability need
  epistemic constraints
  expected proposal role
  data sensitivity
  acceptable latency
  whether parallel exploration is useful
```

一方、worker discoveryやGPU scheduling、retry、preemptionは共通Execution Fabricへ渡す。

## 3. 何を分散するか

最初に「modelを分散する」と考えない。

第一候補は、問題を独立性の高いCognitive Jobへ分けることである。

### 3.1 Hypothesis fan-out

- 仮説Aを評価する
- 仮説Bを評価する
- counterexampleを探す
- riskを探す
- analogous caseを探す

### 3.2 Source pre-analysis

- document単位の要点候補
- log partition単位のanomaly候補
- repository area単位のchange analysis
- evidence候補のrole extraction

### 3.3 Multi-model / Multi-method cross-check

- local SLM A
- local SLM B
- deterministic method
- specialized cognitive method
- general LLM critique

### 3.4 Background Cognition

- overnight re-analysis
- semantic index rebuild
- stale Inquiryの再点検
- alternative plan exploration
- historical consistency check

この種のjobは、interactive latencyを要求しないため遊休資源と相性がよい。

## 4. 向かないjob

- hard real-time control
- worker lossで全体が無効になる巨大同期処理
- foreground userへ継続的負荷を与える処理
- raw confidential dataを広範囲の端末へ複製する処理
- canonical stateをworker local memoryだけへ置く処理

## 5. Job-level Distributionを第一候補にする

```text
Problem
  ↓
Decompose
  ↓
Fan-out
  ├─ hypothesis A
  ├─ hypothesis B
  ├─ factual check
  ├─ counterexample
  ├─ risk analysis
  └─ alternative plan
  ↓
Fan-in
  ↓
Agreement / Conflict / Residual
  ↓
stronger reasoner only if needed
```

この方式は、heterogeneousな遊休端末へ載せやすく、worker churnにも比較的強い。

## 6. Model-level Distributionは別問題

一つのmodel inferenceを複数GPU / nodeへ分散する場合には、次のような技術がある。

- tensor parallel
- pipeline parallel
- expert parallel
- prefill / decode disaggregation

これはstable GPU serverやorganization edgeで有効になり得る。

randomなemployee workstation群を使う第一方式にはしない。

```text
job-level distributed cognition
  != distributed model inference
```

## 7. Foreground First

業務端末では、利用者の作業を常に優先する。

```text
employee workload
  > background cognitive job
```

SEI CognitionからExecution Fabricへ渡したいconstraint候補:

- low priority
- preemptible
- resumable where practical
- battery / thermal restrictions
- acceptable execution window
- locality / trust constraints

実際にuser activityやresource loadをどう検知してjobを退避するかは、HTCondor等のbackend capabilityへ委ねる。

## 8. Locality-first

可能な限り、dataをcomputeへ動かすよりcomputeをdataへ寄せる。

```text
confidential source
  stays in authorized zone
      ↓
eligible worker runs locally
      ↓
bounded result only crosses boundary if allowed
```

これはwearable / home device / department serverでも共通する。

## 9. Security Boundary

```text
device can compute
  != device may see all data
```

少なくとも次を分ける。

- device identity
- device trust level
- user / organization identity
- data classification
- job execution permission
- model / tool permission
- result disclosure permission

Execution Fabricのresource registrationだけでdata accessを与えない。

## 10. Failure Model

遊休workerは消えることを正常系として扱う。

```text
worker disappeared
  != cognitive state lost
  != historical state rewritten
```

Product側のdurable stateはworkerへ預けない。

必要なexecution特性は共通Fabricへ要求する。

- idempotent where possible
- bounded retry
- checkpoint hint
- duplicate result handling
- provenance envelope

## 11. Cognitive Fan-in

分散結果は多数決でTruthにしない。

```text
5 workers agree
  != Truth
  != Decision
```

fan-inでは、次を分けて保持する。

- agreement
- disagreement
- unsupported claim
- unresolved conflict
- missing evidence
- method / model provenance

必要なら、その整理済み結果だけをより強いgeneral-purpose LLMへ渡す。

## 12. 汎用LLMとの協調

遊休資源は、汎用LLMを排除するためではなく、**汎用LLMを高価値な推論へ集中させる前後処理**に使える。

前処理は次のとおりです。
- source pre-reading
- related case recall
- contradiction candidate detection
- context selection
- hypothesis generation
- missing evidence detection

後処理は次のとおりです。
- claim consistency check
- policy check
- independent critique
- source linkage verification

## 13. TEI / SUIとの共通化境界

TEIやSUIでもparallel / background executionは利用し得る。

したがって、次はSEI Cognition固有にしない。

- worker registry
- queue
- resource matching
- CPU/GPU placement
- preemption
- retry
- artifact transfer
- job status

SEI Cognition固有なのは、何をCognitive Jobとして分解し、結果をどのsemantic roleで扱うかである。

## 14. Existing Component First

社内遊休端末にはHTCondorを第一評価候補とする。

理由は次のとおりです。
- idle workstation harvestingを明示的に扱う
- foreground activityでmachine availabilityが変わる環境に適する
- job matching / migration / data transferの蓄積がある
- Apache-2.0

AI application fan-outやmodel worker coordinationにはRayを第一評価候補とする。

一つに統一することを目的にしない。

詳細比較は`../distributed-execution-fabric/README.md`へ置く。

## 15. 最初の評価slice

SEI Cognition側ではschedulerを作らず、Cognitive Jobの利用価値だけを見る。

候補は次のとおりです。

1. 一つの問題を3〜5 independent jobsへ分解
2. local adapterでbaseline実行
3. HTCondor adapterでidle-worker simulation
4. Ray adapterでfan-out simulation
5. worker interruptionを発生させる
6. fan-inでConflict / Agreement / Residualを再構成
7. stronger LLMへ渡すcontext量とqualityを比較

## 16. 成否を見る指標

- foreground interference
- worker churn下のjob completion
- useful compute-hours recovered
- cloud / external LLM call reduction
- context size reduction before general LLM
- end-to-end reasoning quality
- fan-out diversity
- unsupported claim rate
- privacy policy violation count

idle compute利用率そのものはKPIにしない。

```text
more utilized compute
  != better cognition
```

## 17. 停止線

- idle resource != free authority
- candidate result != Truth
- ensemble majority != Decision
- model confidence != semantic confidence
- worker availability != required dependency
- cluster scheduler != cognitive policy authority
- device enrollment != data access permission
- distributed trace != required private chain-of-thought
- SEI Cognition != distributed scheduler product
