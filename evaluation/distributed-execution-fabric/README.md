# Distributed Execution Fabric — Shared Evaluation Boundary

更新日: 2026-10-02  
状態: **Evaluation-only Shared Infrastructure Boundary**  
関連: Issue #378 / Issue #376

## 1. 根幹の趣旨

SEI Cognition、TEI、SUIでは、扱う意味や目的は異なるが、次のような実行上の問題を共有し得る。

- CPU / GPU / memory能力に応じたjob配置
- 複数workerへのfan-out
- batch / background execution
- preemption / retry
- idle workstationのopportunistic利用
- stable server / GPU nodeへの重い処理配置
- data locality / trust zone制約
- artifact input / output transfer
- execution status / provenance

これらを各Productで個別実装しない。

```text
SEI Cognitive Job semantics
TEI Runtime / Build / Analysis Job semantics
SUI Sensemaking / Analysis Job semantics
                 ↓
       product-specific adapter
                 ↓
Distributed Execution Fabric
                 ↓
existing scheduler / runtime
```

Distributed Execution Fabricは、各Productの意味論を所有しない。

## 2. まず既存部品を使う

初期方針は明確にする。

```text
existing component first
  -> thin adapter if needed
  -> shared wrapper only if repeated gap exists
  -> new scheduler / new OSS only as last resort
```

分散schedulerは成熟した領域であり、worker discovery、retry、resource accounting、preemption、security、job history等を独自実装するコストは大きい。

新規OSSの価値は、既存schedulerを置き換えることではなく、複数Productが共通利用できる**薄いjob/capability/placement abstraction**にgapがある場合にのみ検討する。

## 3. 共通Job Envelope候補

```text
ExecutionJob
  id
  job_class
  input_refs
  output_contract
  required_capabilities
  resource_requirements
  data_classification
  trust_zone
  locality_constraints
  latency_class
  priority
  preemptibility
  resumability
  retry_policy
  deadline / ttl if any
  product_metadata_ref
```

重要なのは、`product_metadata_ref`の内容をFabricが解釈しないことである。

```text
Fabric knows execution constraints
  != Fabric knows product semantics
```

## 4. Fabricが知らないもの

### SEI Cognition

- Observation / Unknown / Conflict
- Recommendation / Decision
- cognitive truth / authority
- Inquiry history

### SUI

- cardの意味
- 島 / 表札
- KJ法上の統合判断
- singleton / residualの意味

### TEI

- business model semantics
- screen / workflow meaning
- application metadata authority
- domain transaction semantics

Fabricのjob successは、Product上のsemantic successを意味しない。

## 5. Deployment classを分ける

一つのschedulerで全条件を満たす前提を置かない。

### A. Idle Workstation Pool

特徴は次のとおりです。
- availabilityが不安定
- foreground userが最優先
- worker churnが多い
- heterogeneous
- preemptionが重要

第一候補: **HTCondor**。

HTCondorはidle desktop workstationsの未使用CPUを利用する用途を明示的に持ち、keyboard / mouse activity等でmachineが利用不能になった場合のjob移行やdata transferを備える。

### B. Stable AI / Application Cluster

特徴は次のとおりです。
- server / GPU nodeが比較的安定
- task graph / actor / model serving
- accelerator-aware scheduling
- application内fan-out / fan-in

第一候補: **Ray**。

Rayはtask / actorとCPU / GPU / custom resource requirementを持ち、distributed AI applicationとの親和性が高い。

### C. General Workload Cluster

特徴は次のとおりです。
- batchとserviceが混在
- container / process workload
- GPU / device placement
- priority / preemption

候補: **Nomad**等。

ただし2026-09時点のNomad Community EditionはBusiness Source Licenseであり、厳密な意味で「Apache/MIT/BSD系OSSだけを採用する」条件では別扱いとする。

### D. Data / Python Analytical Graph

候補: **Dask**。

Python dataframe / array / task graphが中心なら強いが、idle desktop harvestingやgeneral product runtimeの共通schedulerとしては範囲が狭い。

### E. Traditional HPC

候補: **Slurm**等。

stable compute clusterやbatch HPCには強いが、foreground employee workstationのopportunistic利用とは性格が異なる。

## 6. 初期Fit Matrix

| 観点 | HTCondor | Ray | Nomad | Dask | Slurm系 |
|---|---|---|---|---|---|
| idle workstation | **強い** | 弱〜中 | 中 | 弱 | 弱 |
| foreground復帰時の退避思想 | **強い** | 要追加設計 | priority/preemptionは強いがdesktop-idle特化ではない | 要追加設計 | cluster前提 |
| heterogeneous CPU/GPU | 中〜強 | **強い** | **強い** | 中 | **強い** |
| AI fan-out / actor | 中 | **強い** | 実行基盤寄り | 中〜強 | batch寄り |
| model serving連携 | 外部 | **強い** | 外部 | 外部 | 外部 |
| batch HT computing | **強い** | 強い | 強い | 強い | **強い** |
| data transfer | **強い** | object store / app設計 | artifact外部設計 | scheduler依存 | shared FS前提が多い |
| Product-agnostic | **高い** | 高いがPython/AI色あり | **高い** | Python analytics色強い | HPC色強い |
| License | Apache-2.0 | Apache-2.0 | BSL/BUSL | BSD-3-Clause | implementation依存 |

この表は採用決定ではなく、評価開始点である。

## 7. 推奨する二層構造

現時点では、一つの技術へ統一するより二層が自然である。

```text
Product Job
   ↓
Shared Execution Adapter Boundary
   ├─ Opportunistic Pool Adapter -> HTCondor
   ├─ AI Task/Actor Adapter       -> Ray
   ├─ General Cluster Adapter     -> Nomad / Kubernetes等
   └─ Local Adapter               -> in-process / local subprocess
```

つまり、共通化するのはscheduler実装ではなく**job要求の最小共通境界とadapter contract**である。

## 8. HTCondorを第一候補にする領域

社内遊休端末を使う目的には、HTCondorを最初に実証する価値が高い。

理由は次のとおりです。
- idle workstation harvestingが中心ユースケースの一つ
- resource/job matchingが柔軟
- worker disappearanceを前提にできる
- shared filesystem必須でない
- Apache-2.0
- decades-long high-throughput computing実績

SEI Cognitionの`foreground first`と思想が近い。

ただしAI model cache / GPU serving / low-latency actor interactionは別途評価が必要である。

## 9. Rayを第一候補にする領域

Rayは、次のようなProduct内分散に向く。

- SUIの複数候補分析
- SEI Cognitionのhypothesis fan-out
- local/organization model inference orchestration
- TEIのAI-assisted generation / analysis workers
- long-running actor / shared model worker

CPU / GPUだけでなくcustom logical resourceを宣言できるため、`model:qwen-small`、`trust:dept-a`等をresource abstractionへ載せる検討余地がある。

ただしProduct security semanticsをRay resource名そのものへ固定しない。

## 10. SchedulerとModel Servingを分ける

```text
job scheduling
  != model serving
```

たとえば、HTCondor / Ray / Nomadがworker placementを担っても、worker内部では次を使える。

- llama.cpp
- vLLM
- SGLang
- ONNX Runtime
- custom Go process
- static encoder

逆にvLLMのdistributed inferenceを使う場合でも、Product-level job lifecycle全体をvLLMへ持たせる必要はない。

## 11. Shared OSSを新設する場合の条件

別OSSを作るなら、次の条件を満たすgapが実測されてからにする。

1. TEI / SUI / SEIの少なくとも2系統で同じadapter logicが繰り返される
2. HTCondor / Ray等のnative job modelへ直接依存するとProduct couplingが強すぎる
3. 共通Job Envelopeが安定する
4. schedulerではなくadapter/control-planeの薄い層で価値が出る
5. existing OSSへのupstream contributionでは解決しにくい

候補の役割は、たとえば次程度に限定する。

```text
shared fabric library / service
  - submit
  - cancel
  - status
  - capability match
  - artifact ref handoff
  - preemption hint
  - provenance envelope
  - backend adapters
```

自前でdistributed consensus、cluster membership、GPU scheduling等を再実装しない。

## 12. セキュリティ境界

共通Fabricがあるからといって、Product間でdata accessを共有しない。

```text
worker registered
  != authorized for TEI data
  != authorized for SUI cards
  != authorized for SEI personal/organizational context
```

Product側が作ったexecution authorizationを、Fabricはplacement constraintとして受け取る。

## 13. 最初の検証順

### Phase 1 — Existing components only

- HTCondor: idle workstation simulation
- Ray: 2–3 node task / actor fan-out
- local adapter: zero-network baseline

### Phase 2 — Common envelope

同一logical jobをbackend adapterだけ切り替えて実行する。

### Phase 3 — Cross-product fixtures

- SEI Cognition: hypothesis / document pre-analysis
- SUI: independent card-cluster candidate scoring
- TEI: generated artifact validation / batch analysis

### Phase 4 — New shared OSS decision

重複adapter codeとoperational gapを見てから決める。

## 13.1 実在する後継製品 `hat47x/eki-fabric`（2026-10-02追記・提案）

この評価で扱った共通のExecution Fabricは、その後、独立した製品`hat47x/eki-fabric`（益 / EKI Fabric）として具体化されています（Architecture Baseline 0.1、protocolのconformance test、M0へ移行中。成熟度の正本はEKIのリポジトリです）。EKIは、計算を安全かつ合理的に実行可能な資源へ配置し、その実行を検証可能に扱う境界を所有します。

したがって、本評価の次の位置づけを改めます。

- 本評価の§3の共通Job Envelopeは、**EKIへの入力としての提案**であり、EKIの契約を決めるものではありません。EKI側では、利用側の意味をresource requirement、data locality、trust / isolation requirement、deadline、preemption、result verificationなどのworkload contractへ投影して受け取ります（`hat47x/eki-fabric:product/value.md`）。SEIのCognitive Envelope（privacy、latency、energy、costの予算、データ分類）との一方向の対応は、EKI側の`hat47x/eki-fabric:research/sei-cognition-mapping.md`で、EKIの未mergeブランチ`docs/family-apex-backflow-20260927`上に提案されています。
- **SEIはschedulingを所有しません。** どのjobが必要かという認知jobの意味を決めますが、どこで実行するかはEKIが決めます。
- EKIの端末の局所governor（利用者の復帰、電力、熱などを中央のschedulerより優先する）は、家族の「反射弓」の手本です。SEIはこのループに入りません。
- 7節の既存OSSの比較（HTCondor、Ray等）は、評価の記録として残します。採用の決定ではありません。

SEIとEKIの関係は、必須の依存ではありません。EKIなしでもSEIは成り立ち、SEIなしでもEKIは成り立ちます。

## 14. 現時点の判断

現段階では、**新しいdistributed scheduler OSSを作る理由はない**。

最有力は次である。

```text
idle endpoint harvesting -> HTCondor
AI/app distributed jobs  -> Ray
stable generic cluster   -> existing workload scheduler
Product-independent boundary -> very thin adapter/envelope
```

この組合せで不足する実測gapが現れた場合だけ、別OSS化を再検討する。
