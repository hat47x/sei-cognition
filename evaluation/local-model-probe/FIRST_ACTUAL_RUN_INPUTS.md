# Local Model Probe — First Actual Run Inputs

更新日: 2026-09-21  
状態: **Evaluation-only pinned acquisition recipe**  
関連: Issue #375 / `RUN_MANIFEST.md` / `MODEL_MATRIX.md`

## 1. 目的

Issue #375 のfirst actual sub-1B runを、runtime/model探索からやり直さず再現できるようにする。

これはproduction dependency lockではない。

```text
pinned first-run input
  != adopted runtime
  != adopted model
  != production support matrix
```

## 1.1 One-command launcher

既定のpinned archive取得経路はLinux x86_64 + Go 1.25以上を対象とする。repository rootから次を実行できる。

```bash
bash evaluation/local-model-probe/run_first_actual.sh
```

launcherは次を順に行う。

1. pinned llama.cpp archive / Qwen GGUFを未取得時だけdownload;
2. runtime/model SHA-256を起動前に検証;
3. llama-serverをdedicated processとして起動;
4. health readyを待機;
5. runtime PID / metrics / props / model-file identityを付けて`modelmatrix --stream`を実行;
6. matrix JSONとserver logをrun ID固有名で保存;
7. matrix/logのSHA-256 sidecarを生成;
8. 終了時にruntime processをcleanup.

既定のwork directoryはrepository rootの `.local-model-run/qwen35-08-q4-0` で、Git管理対象外とする。

既定では1 runにつき次の3 Evidence fileを作る。

```text
<RUN_ID_PREFIX>-matrix.json
<RUN_ID_PREFIX>-llama-server.log
<RUN_ID_PREFIX>-evidence.sha256
```

3 fileのどれかが既に存在する場合はrun開始前に停止し、過去Evidenceを上書きしない。digest sidecarはmatrix/logのSHA-256とbasenameだけを保持し、local absolute pathは記録しない。

環境変数で `WORK_DIR` / `THREADS` / `PORT` / `RUN_ID_PREFIX` / `OUTPUT` / pinned URL等をoverrideできる。ただしdigestを変更した場合は、そのrunを既定pinned inputと同一視しない。

### 事前配置済みartifactを使う

外部GPU VM、Colab、mounted storage等ですでにruntime/modelが存在する場合はdownload経路を使わずに実行できる。

```bash
RUNTIME_BINARY_PATH=/path/to/llama-server \
RUNTIME_VERSION=<actual-runtime-version> \
MODEL_FILE_PATH=/path/to/Qwen3.5-0.8B-Q4_0.gguf \
MODEL_SHA256=57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf \
MODEL_ALIAS=qwen35-0.8b-q4_0 \
QUANTIZATION=Q4_0 \
bash evaluation/local-model-probe/run_first_actual.sh
```

この経路では:
- runtime archiveのdownload/extractは行わない;
- model downloadも行わない;
- model fileのexpected SHA-256検証は**必須のまま**;
- runtime binaryのactual SHA-256は必ず観測・表示し、matrix側でも `/proc/<pid>/exe` から記録する;
- known runtime binary digestがある場合は `RUNTIME_BINARY_SHA256=<digest>` を与えると起動前にfail-closedできる.

`RUNTIME_BINARY_SHA256` 未指定の事前配置runtimeは、binary identityを観測できても既定pinned runtime archive由来とは主張しない。

既定archive経路だけがUbuntu/Linux x86_64 assetに固定される。事前配置runtime経路ではlauncherがarchive architectureを仮定しないが、current model mapping / RSS Evidenceを最大限取得するにはLinuxを推奨する。

launcher自体はdownload成功やinference成功を保証しない。current ChatGPT execution environmentではGo 1.23.2のため、network取得前にGo 1.25 gateで停止することを確認している。

## 2. Runtime candidate

first CPU execution candidate:

- runtime: llama.cpp
- release: `v0.4.1`
- build tag: `b10964`
- source commit: `b29c606e28a01b1bc8c1351026a0fa6e616bf6c4`
- asset: `llama-b10964-bin-ubuntu-x64.tar.gz`
- asset SHA-256:
  `9abf88aea48a55d0f80edb1ee20220b186848cca0b4e919d71518cfd7ca67443`
- official attestation:
  https://github.com/ggml-org/llama.cpp/attestations/47376843
- release source:
  https://github.com/ggml-org/llama.cpp/releases/tag/b10964

取得後:

```bash
echo "9abf88aea48a55d0f80edb1ee20220b186848cca0b4e919d71518cfd7ca67443  llama-b10964-bin-ubuntu-x64.tar.gz" | sha256sum -c -
mkdir -p llama-runtime
tar -xzf llama-b10964-bin-ubuntu-x64.tar.gz -C llama-runtime
find llama-runtime -type f -name llama-server -print
```

GitHub attestation verificationが利用可能なら、SHA-256確認とは別に実施してよい。

## 3. Model candidate

first model artifact:

- repository: `ggml-org/Qwen3.5-0.8B-GGUF`
- file: `Qwen3.5-0.8B-Q4_0.gguf`
- quantization: `Q4_0`
- Hugging Face表示size: approximately 563 MB
- SHA-256:
  `57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf`
- model repository license: Apache-2.0
- source:
  https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF/blob/main/Qwen3.5-0.8B-Q4_0.gguf

取得後:

```bash
echo "57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf  Qwen3.5-0.8B-Q4_0.gguf" | sha256sum -c -
```

model fileのexact local sizeは `modelmatrix --model-file` が実測してmatrix artifactへ保存する。

## 4. Runtime startup

dedicated runtime processをrunごとに起動する。

例:

```bash
LLAMA_SERVER="$(find llama-runtime -type f -name llama-server -print -quit)"

"$LLAMA_SERVER" \
  --model ./Qwen3.5-0.8B-Q4_0.gguf \
  --alias qwen35-0.8b-q4_0 \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 4096 \
  --threads 8 \
  --metrics \
  > llama-server.log 2>&1 &

RUNTIME_PID=$!
```

actual hardwareに合わせてthreadsは変更してよいが、matrix artifactへ記録する。

## 5. Matrix execution

repository rootのexact source checkoutで:

```bash
cd evaluation/sparse-associative-cognition/prototype-go

go run ./cmd/modelmatrix \
  --run-id-prefix qwen35-08-q4-0-first \
  --source-git-sha "$(git rev-parse HEAD)" \
  --runtime llama.cpp \
  --runtime-version b10964 \
  --runtime-pid "$RUNTIME_PID" \
  --runtime-metrics-endpoint http://127.0.0.1:8080/metrics \
  --runtime-props-endpoint http://127.0.0.1:8080/props \
  --model qwen35-0.8b-q4_0 \
  --model-file /absolute/path/to/Qwen3.5-0.8B-Q4_0.gguf \
  --expected-model-sha256 57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf \
  --quantization Q4_0 \
  --context-size 4096 \
  --threads 8 \
  --stream \
  --output qwen35-08-q4-0-matrix.json
```

`--runtime-pid`により、Linuxでは:

- runtime process RSS / VmHWM;
- `/proc/<pid>/exe` executable basename / size / SHA-256;
- `/proc/<pid>/maps` によるhash済みGGUF fileのsame-filesystem-object mapping correlation;
- llama.cpp `/props` が報告するmodel path / aliasと、`--model-file`のsame-file correlation;
- llama.cpp `/metrics` のprompt/generation累積token数、KV cache usage ratio / tokens、context token high-water mark（利用可能なものだけ）;

を同じmatrixへ保存する。

## 6. Evidence stop lines

```text
download SHA-256 match
  != successful model load

runtime executable SHA-256
  != loaded model identity

KV cache usage ratio / tokens
  != KV cache memory bytes
  != model weight memory

operator-supplied model file SHA-256
  != runtime model-load attestation

same-file mapping observed
  != proof that runtime parsed every model byte
  != proof that no other model is loaded

runtime `/props` same-file match
  != proof of successful inference
  != proof of semantic use

runtime `/props` explicit same-file mismatch
  -> block before health check / inference

health endpoint ready
  != inference success

matrix complete
  != human task success
  != model adoption
```

runtime logはmodel load診断には利用できるが、model result qualityとは分離する。

## 7. Current environment boundary

このChatGPT execution environmentではshell DNSからGitHubへ到達できないため、上記runtime/modelのactual downloadは未実行である。

このtransport制約は:

```text
download unavailable here
  != runtime unavailable in general
  != model failure
```

として扱う。
