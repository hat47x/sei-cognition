# Local Model Probe — Run Manifest / Preflight

更新日: 2026-09-20  
状態: **Evaluation-only**  
関連: Issue #375 / #389

## 1. 根幹

actual local model比較では、model名だけでなく**どの環境・runtime・量子化・context条件で実行したか**を残さなければ、latency / memory / failureを比較できない。

```text
same fixture
  + same mode
  + model/runtime/host condition
  -> actual result
```

この文書と`modelpreflight` CLIは、resultの再現性を支えるためのevaluation metadataであり、Product semanticsではない。

## 2. 何を記録するか

- observed_at
- execution_kind (`preflight` / 後続actual run)
- `run_id` — preflightとactual telemetryを結ぶ実験単位ID
- `source_git_sha` — 実行sourceのexact 40-char Git SHA
- host OS / arch / logical CPU / Go version
- runtime endpoint readiness / HTTP status / latency
- runtime name / version
- `--runtime-pid`指定時の実行中runtime executable basename / size / SHA-256
- `--runtime-pid` + `--model-file`併用時のruntime model mapping correlation
- `--runtime-props-endpoint`指定時のruntime-reported model metadata / supplied-file correlation
- `--runtime-metrics-endpoint`指定時のruntime-specific metrics samples
- model identifier
- operator-supplied local model artifactのfile name / size / SHA-256（`--model-file`指定時）
- quantization
- context size
- thread count
- fixture
- probe mode
- notes

将来GPU / accelerator / RAM / peak RSS等を追加してよいが、Universal Contractへは持ち込まない。

## 3. preflight

```bash
cd evaluation/sparse-associative-cognition/prototype-go

go run ./cmd/modelpreflight \
  --run-id <stable-run-id> \
  --source-git-sha <40-char-exact-source-sha> \
  --endpoint http://127.0.0.1:8080/health \
  --runtime llama.cpp \
  --runtime-version <version> \
  --model Qwen3.5-0.8B \
  --model-file /path/to/model.gguf \
  --expected-model-sha256 <optional-known-digest> \
  --quantization <quant> \
  --context-size 4096 \
  --threads 8 \
  --fixture decision-with-unknown \
  --mode workspace
```

JSONをそのまま実験記録へ保存する。

## 4. node差を隠さない

個人PC、idle workstation、stable serverでは条件が異なる。

```text
same model result
  on different node
  != same execution evidence
```

したがって、SEI Cognitionが将来Distributed Execution Fabric経由でjobを配置する場合も、cognitive qualityとexecution qualityを分けて記録する。

## 5. Evidence境界

`endpoint reachable`はmodel qualityを意味しない。

```text
preflight success
  != inference success
  != reasoning success
  != Product Value
```

actual probe結果は`modelprobe`のevaluation reportとこのrun manifestを組にして扱う。

### 5.1 actual invocation telemetry

actual inferenceでは、syntheticなcall planと実際のendpoint呼び出しを分離して記録する。

```bash
go run ./cmd/modelprobe \
  --mode staged \
  --fixture all \
  --model <model-id> \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --run-id <same-stable-run-id> \
  --source-git-sha <same-40-char-exact-source-sha> \
  --telemetry-json <new-output-path>
```

`--telemetry-json`は既存fileを上書きしない。actual runではfixtureごとに次を区別する。

- planned model invocation;
- actual HTTP invocation attempt;
- successful model result;
- attempted invocation failure;
- routingによるexplicit skip;
- planned callなのにHTTP attemptへ到達しなかったexecution shortfall.

run summaryはplanned/actual call数、success/failure/skip、latency、token usage、plan-execution mismatchを別フィールドで保持する。途中のendpoint failureがあってもtelemetry modeでは残りfixtureを観測してsummaryを保存し、run自体はnon-zeroで終了する。

特に、planned callが実行前に失敗した場合を「call avoidance」と数えない。actual avoided callはexplicit route skipだけから算出する。

```text
synthetic planned skip
  != actual endpoint skip

endpoint failure / unattempted planned call
  != avoided model call

lower actual invocation count
  != task success
  != lower total system cost
```

preflight manifestとactual telemetry summaryは同じ `run_id` / `source_git_sha` を使用する。異なるsource revisionの結果を一つのrunとして結合しない。

### 5.2 run artifact

`--run-json`を指定すると、telemetryと成功したfixture resultを同一のevaluation-only artifactへ保存する。

```bash
go run ./cmd/modelprobe \\
  --mode workspace \\
  --fixture all \\
  --model <model-id> \\
  --run-id <workspace-run-id> \\
  --source-git-sha <exact-source-sha> \\
  --run-json workspace.json
```

`--telemetry-json`と併用してもよいが、同じpathは拒否する。どちらもexclusive-createであり既存Evidenceを上書きしない。途中failureがある場合も、保存可能な観測はartifactへ残し、runはnon-zeroで終了する。

raw / workspace / staged artifactの比較は`cmd/modelcompare`を使う。比較時にはmodelとexact source SHAの一致を必須とする。

### 5.3 matrix artifact

`cmd/modelmatrix`は3 modeのpreflight・run artifact・comparisonを一つのmatrix artifactへまとめる。

標準matrix入口では、source identityをcurrent Git HEADから実測する。`--source-git-sha`は任意の記録値ではなくexpected SHAとして扱い、指定時は`git rev-parse HEAD`との完全一致を要求する。未指定時はcurrent HEADを採用する。

`--model-file`を指定した場合、matrix開始前にファイルを一度だけ読み、SHA-256とsizeを固定する。同じidentityをmatrix本体と3 modeのpreflightへ保存する。`--expected-model-sha256`を併用した場合は不一致をinference前にfail-closedとする。保存するpath情報はbasenameだけで、環境固有の絶対pathはEvidenceへ持ち込まない。

ただし、このidentityはoperatorが実験入力として指定したlocal fileのexact bytesを示すものであり、runtime内部が実際にそのbytesをloadしたことをattestするものではない。

```text
model artifact SHA-256 match
  != runtime load attestation
```

statusは次の三つに限定する。

- `complete`: 3 modeがinvocation errorなしで完了し、comparisonを生成した;
- `blocked-preflight`: health endpointが到達不能、error、または非2xxでinference開始前に停止した;
- `incomplete-inference`: preflightは通ったが1件以上のactual invocationが失敗した.

`blocked-preflight` / `incomplete-inference`でも、取得済みpreflight・mode artifact・failureは捨てずに保存する。一方、partialなrunからcross-mode comparisonを生成しない。

### 5.6 human adjudication

complete matrixのtask successはmachine evaluatorだけで確定しない。human reviewは`HUMAN_ADJUDICATION.md`のsidecarとして別artifactへ保存し、exact source SHA / model identityへ結合する。

`modeladjudicate`はreview templateを未評価状態で生成し、人が全対象fixtureを記入した後にcoverage / identity / allowed valuesを検証する。staged skipはmodel answerが存在しないため対象外とする。

### 5.5 streamed latency

TTFTを必要とするactual matrixでは `--stream` を指定する。probeはOpenAI-compatible SSEの最初の非空content deltaをfirst-token観測点とし、`[DONE]`までをtransport total latencyとする。

streaming artifactでは次を別々に保持する。

- response header latency;
- first-token observed flag;
- first-token latency;
- transport total latency.

usageがstream responseに含まれないruntimeではtoken usageが0のままになり得る。これは0 token消費のEvidenceではなく、provider telemetry未提供として扱う。

### 5.4 runtime process memory / executable identity

Linuxでruntime server PIDが分かる場合は `modelmatrix --runtime-pid <pid>` を指定する。matrix artifactの `runtime_memory` に、matrix開始時とraw / workspace / staged後のprocess RSSを保存する。

同時にmatrix開始時に `/proc/<pid>/exe` を読み、`runtime_process`へ実行中executableのbasename / size / SHA-256を保存する。絶対pathは保存せず、sourceとして `/proc/<pid>/exe` だけを記録する。

記録値:

- PID / process name;
- source path (`/proc/<pid>/status`);
- timestamp / stage / mode;
- `VmRSS`由来のcurrent RSS bytes;
- `VmHWM`由来のpeak RSS bytes;
- matrix内のmax observed RSS / peak RSS;
- read errorがあればerror text.

状態:

- `not-requested`: PID未指定;
- `observed`: requested sampleをerrorなく取得;
- `partial`: 一部sample取得後に読取失敗;
- `unavailable`: sampleを一件も取得できない;
- `unsupported`: 非Linuxなど現行sampler対象外.

`VmHWM` はprocess起動以来のhigh-water markであり、このmatrix runだけのpeakとは限らない。dedicated runtime processを推奨する。memory Evidenceが未取得でもtransport/evaluator matrixは `complete` になり得るため、Issue #375のmemory完了条件は別途確認する。

`runtime_process`のSHA-256は実行中binaryのidentityを強くするが、loaded model fileやruntime内部stateをattestしない。

```text
runtime process executable identity
  != model-load attestation
```

### 5.8 runtime model mapping correlation

Linuxでmatrixへ `--runtime-pid` と `--model-file` の両方が渡された場合、最初のpreflight時に `/proc/<pid>/maps` を読み、model fileと同じfilesystem objectのmappingが存在するかを補助観測する。

保存するのはstatus / timestamp / PID / model basename / `/proc/<pid>/maps` source / matching mapping countであり、local absolute model pathは保存しない。

```text
model artifact SHA-256
  + same-filesystem-object mapping
  > model nameだけのEvidence

ただし

same-file mapping observed
  != runtime parsed every model byte
  != exclusive model load
  != successful inference
```

mapping未観測はruntimeがmmapを使わない可能性もあるため、model failureへ読み替えない。

### 5.9 runtime-reported props

`modelmatrix --runtime-props-endpoint <url>` はruntime自身が公開するread-only propertiesを一度取得する。llama.cppの `GET /props` ではruntime-selected `model_path` / `model_alias` / `role` / context sizeを観測できる。

absolute `model_path` はEvidenceへ保存せずbasenameだけを残す。`--model-file` が同じhostから参照可能なら、runtime報告pathとoperator-supplied pathをsame-file identityで照合する。

```text
runtime-reported same-file match
  + model artifact SHA-256
  > model identifier stringだけのEvidence

ただし

props match
  != successful inference
  != semantic use
```

runtimeが別container/hostにありreported pathをlocal statできない場合は `partial` とし、false mismatchを作らない。

### 5.7 runtime-specific metrics

`modelmatrix --runtime-metrics-endpoint <url>` はoptionalなPrometheus text endpointをmatrix開始時と各mode後にsampleする。llama.cppの場合は `llama-server --metrics` の `/metrics` を利用できる。

保存対象はprompt/generation累積token数、KV cache usage ratio / token count、context token high-water markのうちendpointが公開した値だけである。endpoint failureは `unavailable` / `partial` として保存し、matrixのtransport/evaluator statusとは分離する。

```text
KV cache token count / usage ratio
  != KV cache memory bytes

runtime metrics available
  != memory acceptance
```

```text
matrix complete
  != semantic correctness
  != human adjudication PASS
  != memory / energy acceptance
  != model adoption
```

## 6. 現在の実行環境で確認できたこと

2026-09-12時点の現在の作業環境では:

- Linux x86_64
- RAM約5.8 GiB
- swapなし
- local llama.cpp / Ollama runtime未導入

であり、actual inference Evidenceは取得していない。

この事実は「0.8Bが動かない」Evidenceではなく、**runtime未配置のため未実行**という環境制約である。
