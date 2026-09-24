# Local-First Cognition — Compute Placement

更新日: 2026-09-24  
状態: **Evaluation / placement policy**  
関連: Issue #371 / #375 / #543 / #546

## 1. 目的

SEI Cognitionの計算資源を、常時稼働する軽量認知と、必要時だけ起動する重い認知へ分離する。

```text
always-on CPU
  -> deterministic / symbolic
  -> fly-inspired sparse associative cognition
  -> typed local student
  -> bounded local SLM
  -> burst GPU comparator / training
  -> hosted teacher / stronger model / human
```

GPUを常時認知の前提にはしない。GPUは「モデルを大きくするため」ではなく、CPU側の境界を測るための短時間resourceとして使う。

## 2. CPUを正本とする層

### deterministic / symbolic

対象:
- exact rule;
- policy eligibility;
- schema validation;
- hard stop line;
- source/provenance verification.

ここは学習modelへ委譲しない。

### fly-inspired sparse associative cognition

Issue #371で実装・評価したSACS系を置く。

用途:
- candidate recall;
- novelty / known-vs-novel signal;
- salience / attention candidate;
- sparse signature;
- retrieval前段.

期待する性質:
- CPU / local / offline;
- sparse memory;
- deterministic reproducibility;
- low latency.

```text
sparse activation
  != semantic truth
  != confidence authority
```

### typed local student

Issue #543のJev teacher -> LightGBM studentで扱う。

Choice / Score / Noulに相当するbounded decisionを、task-specific featureから安価に提案する。

必須境界:
- teacher fidelityとtask correctnessを分離;
- calibrated confidenceとSEI confidenceを分離;
- OOD / low confidence / high stakesは上位routeへ戻す;
- studentはDecision authorityを持たない.

Jevと同じAPIや内部modelを再現することを目標にしない。再利用するのはtyped decision primitiveとprobability-bearing outputの考え方である。

## 3. CPU local SLM

Issue #375のfirst actual pathを使う。

first tier:
- Qwen3.5-0.8B Q4_0;
- llama.cpp;
- raw / workspace / stagedを同じexact sourceで比較.

目的:
- bounded Cognitive Workspaceによりsub-1Bで十分なproblem classを見つける;
- staged routeで不要なmodel callを避けられる範囲を測る.

0.8Bが失敗しても直ちに4Bへ上げない。

先に:
- selected evidence;
- missing evidence;
- decomposition;
- output contract;
- routing

を再点検する。

## 4. Burst GPU

GPUへ送る候補は、常時CPU routeで不足した処理だけに限定する。

優先用途:
1. 同一0.8BをGPUで実行し、hardware effectをmodel effectから分離する;
2. 4B級local comparator;
3. small neural student / adapterの短時間training;
4. batch embedding / feature extraction;
5. cross-model evaluation.

GPUを使わない用途:
- SACS常時実行;
- LightGBM常時推論;
- deterministic policy;
- low-rate typed routingでCPUが十分なcase.

### llama.cpp GPU handoff

GPU nodeではCUDA対応 `llama-server` を事前配置し、既存launcherへ渡す。

```bash
GPU_LAYERS=<N> \
RUNTIME_BINARY_PATH=/path/to/cuda-enabled-llama-server \
RUNTIME_VERSION=<observed-version> \
MODEL_FILE_PATH=/path/to/model.gguf \
bash evaluation/local-model-probe/bootstrap_go125_first_actual.sh
```

`GPU_LAYERS` は要求値をEvidenceへ残すだけで、GPU offload成功そのものの証明ではない。server logやhost側telemetryで確認する。

first GPU runでもmodel / fixture / source / evaluatorを変えない。CPU/GPU差だけを観測する。

### CPU/GPU pair gate

hardware effectをmodel effectから分離する比較では、両runを独立にverifyした後、pair verifierを通す。

```bash
PAIR_VERIFICATION_OUTPUT=/path/to/cpu-gpu-pair.json \
bash evaluation/local-model-probe/verify_cpu_gpu_pair.sh \
  /path/to/cpu/run-evidence.sha256 \
  /path/to/gpu/run-evidence.sha256
```

pair gateはsource SHA / observed model artifact / runtime revision / quantization / context / threads / fixtureを固定する。logical CPU数やCPU/GPU runtime binary digestの差は隠さずexecution-environment Evidenceとして残す。current v2 gateでは、digest検証済みserver logから実際のlayer offloadも確認する。

```text
positive GPU_LAYERS request
  != observed GPU offload

verified llama.cpp log
  + offloaded N/M layers to GPU
  + N > 0
  = observed layer-offload Evidence

observed layer offload
  != GPU utilization percentage
  != model-quality delta
  != deployment choice
```

## 5. Hosted teacher / external reasoner

Jev等のhosted teacherは:
- initial typed labels;
- boundary / disagreement cases;
- audit sample;
- local studentがabstainしたcase

へ限定する。

常時runtimeにしない。

```text
local student confidence low
  or OOD
  or high-stakes floor
    -> teacher / stronger reasoner / human
```

teacher responseはground truthではない。actual outcome / human adjudication / external truthと分離して保持する。

## 6. External GPU serviceの使い方

provider固有機能をrepository contractにしない。

選定基準:
- Linux x86_64;
- exact checkoutを保持できる;
- model/runtime bytesを固定できる;
- short-lived instance;
- artifactを回収できる;
- idle時に課金を止められる;
- secretをrepositoryへ残さない.

Colab等のnotebook serviceでは、notebook自体を正本にしない。正本はrepositoryのlauncherとEvidence artifactである。

Runpod / Modal等の従量環境でも同じ。

```text
provider notebook / VM
  = execution surface

repository launcher
  + exact source
  + artifact hashes
  + returned Evidence
  = experiment identity
```

## 7. 個人利用での費用制御

月額GPUを前提にしない。

運用原則:
- first actual 0.8BはCPUでも成立するため、GPU契約前にCPU baselineを取得;
- GPUは1回のmatrix + 必要なrerunだけ;
- 4B比較は0.8B failure analysis後;
- trainingはsmall student / adapterに限定;
- persistent volumeはmodel cacheが本当に再利用される場合だけ保持;
- Evidence回収後はinstanceを停止/破棄;
- provider料金は実行直前に確認し、research artifactへ固定価格を埋め込まない.

## 8. 昇格順

```text
T0 deterministic / symbolic
  -> T1 SACS / sparse cognition
  -> T2 LightGBM / linear typed student
  -> T3 CPU sub-1B local SLM
  -> T4 burst GPU same-model verification
  -> T5 2–4B comparator
  -> T6 hosted teacher / stronger external model / human
```

固定pipelineではない。stakes / novelty / latency / locality / privacy / current-fact requirementに応じてrouteする。

## 9. 次の実測

最優先:
1. exact current source;
2. Go 1.25.14;
3. pinned CPU llama.cpp b10964;
4. Qwen3.5-0.8B Q4_0;
5. first actual raw/workspace/staged matrix;
6. returned Evidence verification.

次に、同一merged sourceからCPU baselineを取得し、同一modelをCUDA対応runtime + explicit `GPU_LAYERS` で再実行する。両Evidence bundleを `verify_cpu_gpu_pair.sh` へ通してcomparabilityを確認してから、CPUとの差を記述する。

4Bへ進むのはその後とする。
