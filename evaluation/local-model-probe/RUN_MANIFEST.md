# Local Model Probe — Run Manifest / Preflight

更新日: 2026-09-12  
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
- host OS / arch / logical CPU / Go version
- runtime endpoint readiness / HTTP status / latency
- runtime name / version
- model identifier
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
  --endpoint http://127.0.0.1:8080/health \
  --runtime llama.cpp \
  --runtime-version <version> \
  --model Qwen3.5-0.8B \
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

## 6. 現在の実行環境で確認できたこと

2026-09-12時点の現在の作業環境では:

- Linux x86_64
- RAM約5.8 GiB
- swapなし
- local llama.cpp / Ollama runtime未導入

であり、actual inference Evidenceは取得していない。

この事実は「0.8Bが動かない」Evidenceではなく、**runtime未配置のため未実行**という環境制約である。
