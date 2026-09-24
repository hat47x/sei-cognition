# Local Model Probe — Cognitive Workspace vs Raw Context

更新日: 2026-09-20  
状態: **Evaluation-only Probe Harness**  
関連: Issue #375 / #385 / #383

## 1. 根幹の趣旨

SEI Cognitionが狙うのは、単に小さいmodelへ置き換えることではない。

```text
Durable Semantic State
  -> bounded Cognitive Workspace
  -> cognitive route
  -> smallest sufficient reasoner
```

によって、認知境界を壊さずにmodelへ渡す問題を狭くし、必要な場合だけ強いreasonerへ上げられるかを実測する。

このprobeは、そのためのtransportとmeasurement entry pointである。

実際に比較するmodel tierと実験順は[`MODEL_MATRIX.md`](./MODEL_MATRIX.md)で整理する。first actual runのpinned runtime/model入力と取得後の実行手順は[`FIRST_ACTUAL_RUN_INPUTS.md`](./FIRST_ACTUAL_RUN_INPUTS.md)に固定する。既定のLinux x86_64 archive経路では `bash evaluation/local-model-probe/run_first_actual.sh` で取得・digest検証・runtime起動・matrix実行までを一続きで実行できる。事前配置済みruntime/modelがある場合は `RUNTIME_BINARY_PATH` / `MODEL_FILE_PATH` で外部downloadを避けられる。 Go 1.25が未配置のLinux x86_64 nodeでは `bootstrap_go125_first_actual.sh` がofficial go1.25.14 archiveをroot不要でmaterializeし、exact toolchain identityをsidecarとmatrix hostへ結ぶ。

## 2. 比較する3 mode

### raw

同一fixtureのflattened raw contextをmodelへ送る。

staged routerが本来modelを呼ばないcaseでも、比較baselineとして明示的に送る。

したがって結果には`boundary_bypassed_for_baseline=true`が付き得る。

### workspace

同じmodelへbounded Cognitive Workspaceを送る。

これによりmodel sizeを変えず、context shapingだけの効果を比較できる。

### staged

SEI Cognitionのroutingを尊重する。

- deterministic -> modelを呼ばない
- current external fact -> modelを呼ばずexternal evidenceへ戻す
- high novelty -> modelを呼ばずevidence expansionへ戻す
- bounded local reasoning -> local modelを呼ぶ

`staged`が実運用候補、`raw` / `workspace`は比較実験条件である。

## 3. output contract

modelへhidden chain-of-thoughtは要求しない。

返すのはexternally inspectableなJSONのみ。

```json
{
  "proposal": "...",
  "supporting_refs": ["obs-1"],
  "decision_basis_refs": [],
  "preserved_unknown_refs": ["unk-1"],
  "preserved_conflict_refs": [],
  "recommendation_ref": "",
  "decision_ref": "",
  "need_more_evidence": false,
  "claims": [
    {
      "text": "material claim",
      "supporting_refs": ["obs-1"]
    }
  ]
}
```

このJSONは`cognitiveeval.EvaluateOutput`へ渡される。

## 4. localhost runtime boundary

probeは特定runtimeをUniversal semanticsへ持ち込まない。

第一probe interfaceはOpenAI-compatible Chat Completionsとする。

デフォルト:

```text
http://127.0.0.1:8080/v1/chat/completions
```

llama.cppの現行`llama-server` / `llama serve`はこのendpointを提供するため、一Realizationとして利用できる。

参考:
- https://github.com/ggml-org/llama.cpp
- https://github.com/ggml-org/llama.cpp/tree/master/tools/server

## 5. dry-run

model未導入でもprobe planを確認できる。

```bash
cd evaluation/sparse-associative-cognition/prototype-go

go run ./cmd/modelprobe \
  --mode staged \
  --fixture all \
  --dry-run
```

見る点:
- route
- should_invoke_model
- baseline boundary bypass
- request chars
- actual prompt material

## 6. llama.cpp例

runtime/model installそのものはこのrepositoryの責任外とする。

例として現行llama.cppでは、GGUF modelをserveしてOpenAI-compatible endpointを立てられる。

```bash
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF
```

その後:

```bash
go run ./cmd/modelprobe \
  --mode workspace \
  --fixture decision-with-unknown \
  --model local-model
```

raw baseline:

```bash
go run ./cmd/modelprobe \
  --mode raw \
  --fixture decision-with-unknown \
  --model local-model
```

staged:

```bash
go run ./cmd/modelprobe \
  --mode staged \
  --fixture all \
  --model local-model
```

## 7. model帯の比較

Issue #375では少なくとも次を比較する。

### sub-1B

用途仮説:
- extraction
- classification
- simple comparison
- short explanation

### 2–4B

用途仮説:
- bounded multi-step comparison
- contradiction analysis
- hypothesis / short planning

### stronger comparator

7–8B級または外部general-purpose modelを必要時だけ比較する。

重要なのはmodel familyではなく、同じfixture / mode / evaluatorで比較することである。

具体的なfirst candidatesは[`MODEL_MATRIX.md`](./MODEL_MATRIX.md)を参照する。

### Exact source identity

actual-run artifactで `source_git_sha` を記録する場合、current HEAD一致だけではなくclean working treeを要求する。tracked/staged/untracked changeがある状態では、同じSHAに異なる実行sourceが対応し得るためrunを開始しない。Git ignore対象のrun cacheはこの判定から除外される。

```text
HEAD match
  != exact source
unless working tree is clean
```

### Exact Go 1.25 runtime handoff

Issue #512と同じcanonical runtimeで外部actual runを行う場合:

```bash
bash evaluation/local-model-probe/bootstrap_go125_first_actual.sh
```

を使う。canonical identity:
- `go1.25.14`;
- Linux amd64;
- official archive `go1.25.14.linux-amd64.tar.gz`;
- SHA-256 `a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712`.

wrapperはsystem exact Go / pre-provisioned exact binary / pre-provisioned official archive / official downloadを同じidentityへ収束させ、`GOTOOLCHAIN=local` で自動toolchain差替えを止める。matrix top-level `host.go_version` / OS / archをreturned Evidence verifierがcross-checkする。

### Artifact schema versioning

current generated Evidence schemas:

```text
sei-cognition.local-model-run-manifest/v1
sei-cognition.actual-model-telemetry/v1
sei-cognition.local-model-probe-run/v1
sei-cognition.local-model-run-comparison/v1
sei-cognition.local-model-matrix-run/v1
sei-cognition.local-model-matrix-verification/v1
sei-cognition.local-model-compute-pair-verification/v1
sei-cognition.local-model-human-adjudication/v1
sei-cognition.local-model-human-adjudication-report/v1
sei-cognition.local-model-evidence-bundle/v1
```

current matrix artifact schema:

```text
sei-cognition.local-model-matrix-run/v1
```

`v1` はtop-level `host` Evidenceを必須化したschemaである。旧 `.../v0` はHost追加前のshapeなので、current validatorは同じ意味として読み替えず明示的にrejectする。

current matrix verification report:

```text
sei-cognition.local-model-matrix-verification/v1
```

first-run digest sidecarにも:

```text
# evidence_bundle_schema=sei-cognition.local-model-evidence-bundle/v1
```

を必須で入れる。schema commentがない旧sidecarをcurrent verifierへ暗黙upgradeしない。

```text
same schema name
  + changed required fields
  = prohibited implicit drift
```

### First-run evidence retention

`run_first_actual.sh` はmatrix outputだけでなくserver logもrun ID固有名で保存し、両fileの標準 `sha256sum -c` 互換sidecarを生成する。既存matrix/log/digest fileは上書きせず、3 output pathの衝突も拒否する。`modelmatrix` がnon-zeroでも生成済みartifact/logのdigestを保存してから元のexit codeを返す。

```text
matrix JSON
  + runtime server log
  + digest sidecar
  = transferable run Evidence set

digest match
  != inference quality
```

### Returned Evidence verification

外部環境からmatrix/log/sidecarを戻したら:

```bash
bash evaluation/local-model-probe/verify_first_actual.sh /path/to/run-evidence.sha256
```

を使う。scriptはhash対象をbasename-onlyに制限し、sidecarのmatrix/log labelとhash行を相互照合してから `sha256sum -c` を行う。その後 `cmd/modelmatrixverify` がstrict JSONとstatus別構造を検証する。

`EXPECTED_SOURCE_GIT_SHA` / `EXPECTED_MODEL_SHA256` を与えればrun identityを外部期待値へ固定できる。`EXPECTED_EVIDENCE_DIGESTS_SHA256` がある場合はsidecar自体のtransfer integrityも確認できる。

sidecarだけを同梱しても第三者署名やorigin authenticityにはならない。これはEvidence bundle integrity validatorであり、model quality validatorではない。

### CPU/GPU paired Evidence verification

same-model CPU baselineとGPU runをhardware effect比較へ使う場合は、個々のbundle verification後にpair gateを通す。

```bash
PAIR_VERIFICATION_OUTPUT=/path/to/cpu-gpu-pair.json \
bash evaluation/local-model-probe/verify_cpu_gpu_pair.sh \
  /path/to/cpu/run-evidence.sha256 \
  /path/to/gpu/run-evidence.sha256
```

`verify_cpu_gpu_pair.sh` はsource SHA、GGUF identity、runtime revision、quantization、context size、threads、fixture setを同一条件として固定する。CPU側はGPU offload要求なし、GPU側はpositive `GPU_LAYERS` requestを必須とする。

`gpu_layers_requested` はlauncher requestでありGPU利用の実測証明ではない。pair reportのlatency deltaも記述的Evidenceであり、model品質やdeployment choiceへ自動昇格させない。
## 8. 現在取得するmeasurement

- route
- model invocation / skip
- request chars
- response chars
- total latency
- HTTP status
- providerが返すtoken usage（存在する場合）
- Unknown preservation
- Conflict preservation
- Recommendation / Decision separation
- historical basis violation
- unsupported claim
- invalid evidence ref
- need-more-evidence appropriateness

取得可能:
- response header latency
- request開始からresponse完了までのtransport total latency
- `--stream`時のfirst-token latency（最初の非空content delta受信時刻を操作的定義とする）
- Linux `--runtime-pid`指定時のruntime process RSS / peak RSS
- Linux `--runtime-pid`指定時の実行中runtime executable basename / size / SHA-256（`/proc/<pid>/exe`）
- Linuxで `--runtime-pid` と `--model-file` を併用した場合のmodel file process mapping（`/proc/<pid>/maps` のsame-filesystem-object照合）
- `--runtime-props-endpoint`指定時のruntime-reported model metadata / supplied-file correlation
- `--runtime-metrics-endpoint`指定時のruntime-specific Prometheus metrics（llama.cppではprompt/generation累積tokens、KV cache usage ratio / tokens、context token high-water mark）
- `--model-file`指定時のlocal model artifact file name / size / SHA-256

まだ取得しないもの:
- tokenizer内部の厳密な単一token生成時刻
- model weight単独memory
- KV cache単独memory
- GPU VRAM
- energy

model weight単独memory、KV cache単独memory bytes、GPU VRAM、energyは引き続き未取得である。KV cache usage ratio / token countを取得できても、bytesへ換算してこれらを取得済みとは扱わない。

### Streaming latency

actual比較でTTFTを取る場合は `modelmatrix --stream` を指定する。OpenAI-compatible SSE streamの最初の**非空 `choices[].delta.content`**をfirst tokenの操作的観測点とする。

保存値:

- `response_header_latency_ms`: request開始からHTTP response header受信まで;
- `first_token_observed`: content deltaを実際に観測したか;
- `first_token_latency_ms`: request開始から最初の非空content deltaまで;
- `total_latency_ms`: request開始からfull bodyまたはSSE `[DONE]`まで.

```text
first content delta latency
  ~= operational TTFT
  != tokenizer-internal exact token timestamp

transport total latency
  != local evaluator processing time
```

streamingを指定しないrunでは `first_token_observed=false` のままとし、0msをTTFT観測値として扱わない。SSEがcontentを返しても `[DONE]`なしで終了した場合はincomplete responseとしてfail-closedにする。

### Runtime process RSS

Linuxでlocal runtime serverのPIDが分かる場合、`modelmatrix --runtime-pid <pid>` により `/proc/<pid>/status` の `VmRSS` / `VmHWM` をmatrix開始時と各mode後に記録できる。

```text
VmRSS
  = sampling時点のruntime process RSS

VmHWM
  = そのprocess起動以来のRSS high-water mark
```

これはmodel weight単独量、KV cache単独量、GPU VRAMではない。shared server processで別requestや別modelを処理した履歴があれば `VmHWM` に混入し得るため、dedicated runtime processを比較runごとに使う方がよい。

PID未指定は `not-requested`、非Linuxは `unsupported`、読取不能は `unavailable` / `partial` として記録し、0 byteを観測値として捏造しない。

同じPIDから `/proc/<pid>/exe` も一度観測し、実際に動いているruntime executableのbasename / size / SHA-256を `runtime_process` として保存する。これはruntime binary identityであり、processがどのmodel bytesをloadしたかの証明ではない。

```text
runtime executable SHA-256
  != loaded model identity
```

### Runtime model mapping

Linuxで `--runtime-pid` と `--model-file` を同時指定すると、matrixは `/proc/<pid>/maps` を読み、hash済みmodel fileと同じfilesystem objectがprocess address spaceへmapされているかを `runtime_model_mapping` に記録する。照合にはabsolute path文字列ではなく `os.SameFile` 相当のdevice/inode identityを使い、Evidenceにはbasenameだけを保存する。

状態:

- `not-requested`: PIDまたはmodel fileが未指定;
- `observed`: 同じfilesystem objectのmappingを1件以上観測;
- `not-observed`: `/proc/<pid>/maps` は読めたが対象mappingを観測しなかった;
- `unavailable`: model file statまたはprocess maps読取に失敗;
- `unsupported`: 非Linux.

`not-observed` はruntime/model failureではない。runtimeがmmapを使わない場合や観測時点の差でも成立し得る。

```text
hashed model file + same-file process mapping
  = stronger load-correlation evidence
  != proof that runtime parsed every byte
  != proof that this is the only loaded model
  != semantic use / task success
```

### Runtime-specific metrics

`modelmatrix --runtime-metrics-endpoint <url>` を指定すると、matrix開始時と各mode後にPrometheus text endpointを補助Evidenceとしてsampleする。llama.cppではserverを `--metrics` 付きで起動し `/metrics` を指定できる。

collectorは次の既知metricだけを保存する。

- `llamacpp:prompt_tokens_total`;
- `llamacpp:tokens_predicted_total`;
- `llamacpp:kv_cache_usage_ratio`;
- `llamacpp:kv_cache_tokens`;
- `llamacpp:n_tokens_max`.

endpoint未指定は `not-requested`、取得不能や非2xxは `unavailable`、途中から失敗した場合は `partial` とし、0値を観測値として捏造しない。metrics Evidenceの失敗だけでtransport/evaluator matrixを失敗扱いにはしない。

```text
runtime metric token counter
  != provider usage telemetry

KV cache usage ratio / tokens
  != KV cache memory bytes
  != model weight memory
```

shared runtimeに別requestが混ざれば累積counterへ混入するため、dedicated processを推奨する。

### Runtime-reported props

`modelmatrix --runtime-props-endpoint <url>` はruntime自身のread-only properties endpointを補助観測する。llama.cppの `GET /props` では `model_path` / `model_alias` / `role` / context size等が返る。

Evidenceへはruntime報告model pathの**basenameだけ**を保存する。`--model-file` が同時指定され、runtime報告pathを同じhost filesystemからstatできる場合は、両者をsame-file identityで照合する。

状態:

- `not-requested`: endpoint未指定;
- `observed`: props取得成功（same-fileがfalseの場合も観測値として保持）;
- `partial`: propsは取得できたがreported pathのlocal stat等ができない;
- `unavailable`: HTTP / JSON取得失敗.

```text
runtime-reported model path
  + operator-supplied model SHA-256
  + same-file match
  = stronger local load-correlation evidence

but

runtime props match
  != model parsing completeness
  != successful inference
  != semantic correctness
```

remote/container-separated runtimeではreported pathをprobe hostからstatできない場合があるため、その場合は `partial` をfailureへ読み替えない。

同じhostで明示的に別fileだと確認できた場合だけ、matrixは `blocked-model-identity` としてactual invocationを開始しない。

## 8.1 run artifact / comparison

actual runでは、標準出力だけでなく比較可能なrun artifactを保存できる。

```bash
go run ./cmd/modelprobe \\
  --mode raw \\
  --fixture all \\
  --model <model-id> \\
  --run-id <raw-run-id> \\
  --source-git-sha <exact-source-sha> \\
  --run-json raw.json
```

`workspace` / `staged`も同じsource SHA・同じmodelで別run artifactを作る。artifactは、run identity、telemetry、成功したfixture resultを一つに束ねる。existing fileは上書きしない。

3 modeが揃ったら:

```bash
go run ./cmd/modelcompare \\
  --raw raw.json \\
  --workspace workspace.json \\
  --staged staged.json \\
  --output comparison.json
```

比較器は次を確認する。

- raw / workspace / stagedのmodeが正しいこと;
- 3 artifactのmodelが同じこと;
- 3 artifactの`source_git_sha`が完全一致すること;
- resultとtelemetryのinvocation / skip状態が矛盾しないこと.

出力は単一scoreを作らない。mode別aggregateと、shared fixtureだけを使った`workspace - raw`の記述的deltaを別々に出す。stagedのskipはtask successへ読み替えない。

```text
run comparison
  = same-source / same-model descriptive evidence
  != human adjudication
  != model adoption decision
  != Product Value
```

## 8.2 one-shot matrix run

runtimeが用意されている環境では、preflightから3 mode比較までを一つの入口で実行できる。

```bash
go run ./cmd/modelmatrix \\
  --run-id-prefix qwen08-first \\
  --source-git-sha <expected-exact-source-sha> \\
  --runtime llama.cpp \\
  --runtime-version <version> \\
  --model <model-id> \\
  --model-file /path/to/model.gguf \\
  --expected-model-sha256 <optional-known-digest> \\
  --quantization <quant> \\
  --context-size 4096 \\
  --threads 8 \\
  --output qwen08-matrix.json
```

matrix runnerは実行開始前に `git rev-parse HEAD` を取り、`--source-git-sha` が指定されていれば完全一致を要求する。未指定ならcurrent HEADをsource identityとして採用する。Git repositoryとしてHEADを検証できない環境ではactual matrixを開始しない。

`--model-file`指定時はlocal fileのSHA-256 / sizeもinference前に固定する。`--expected-model-sha256`不一致はfail-closedとする。ただしこれは指定fileのidentityであってruntime load attestationではない。

実行順は固定される。

```text
preflight(raw)
  -> raw
preflight(workspace)
  -> workspace
preflight(staged)
  -> staged
all complete
  -> descriptive comparison
```

`--runtime-props-endpoint` と `--model-file` のsame-file照合が明示的にfalseなら、health checkより前に `blocked-model-identity` として停止する。propsが `partial` / `unavailable` の場合はmismatchを推定しない。

health endpointが2xxでなければ、そのmodeのinferenceを開始せず `blocked-preflight` としてartifactを保存する。inference failureがある場合も各modeの観測を保持するが、cross-mode comparisonは作らず `incomplete-inference` とする。

`complete`は「3 modeのtransport/evaluator実行が成立し比較artifactを生成できた」という意味に限定する。task successやmodel採用を意味しない。

## 9. 実験順

最初から多数modelを回さない。

```text
1. dry-run
2. one sub-1B model
   raw vs workspace vs staged
3. failure caseを確認
4. Working Set / decomposition改善
5. 2–4B model
6. sub-1Bとの差を見る
7. 必要ならstronger comparator
```

小型modelの失敗を見たとき、直ちにmodelを大型化しない。

まず:
- evidence selection
- task decomposition
- prompt/output contract
- missing evidence
- route

を確認する。

## 10. 成功条件

有望な結果は「小型modelが大モデルと同じ文章を書くこと」ではない。

例えば:

```text
Workspace
  -> Unknown / Conflict / historical boundaryを保つ
  -> rawよりunsupported claimが少ない
  -> sub-1Bまたは2–4Bで十分なcaseが増える
  -> stagedで不要なmodel callを避ける
```

であれば価値がある。

逆に、Workspaceがraw contextと同等以下であれば、SEI-specific context shapingを縮小または再設計する。

## 10.1 human adjudication

machine evaluatorの結果だけでtask successを確定しない。complete matrix取得後は[`HUMAN_ADJUDICATION.md`](./HUMAN_ADJUDICATION.md)のsidecarを使い、actual model outputが存在するfixtureだけを人が評価する。

```text
machine semantic checks
  + independent human adjudication
  -> separate Evidence views
```

review templateは全entryを`unassessed`で生成し、AIがpass/failを先取りしない。validated reportもmode別countを保持するだけでoverall scoreを生成しない。

## 11. 停止線

```text
model output != Truth
model output != Decision
well-formed JSON != correct reasoning
shorter context != better cognition
fewer LLM calls != Product Value
larger model != first remedy
current external fact != model memory
high novelty != permission to guess
```

このprobeはactual model Evidenceを取得する入口であり、それ自体をOutcome Evidenceとはみなさない。
