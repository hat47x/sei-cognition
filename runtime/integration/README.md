# runtime integration probes

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

ここにあるprobeは、GitHub Actionsや特定runnerを意味上の成立条件にしません。手動実行、開発端末、将来の外部runnerなど、どの実行面から呼び出しても、同じ固定条件と検査境界を再現できることを優先します。

## Runtime version exchange

`run_runtime_version_exchange.sh`は、ISSUE-000070のruntime version交換実験をrepository-localに実行します。

固定するものは次です。

- KJ Atlas repository / commit
- Method input
- `qwen2.5:0.5b`のmodel artifact digest
- model prompt

交換するのはOllama runtimeだけです。

- revision A: `0.32.13`
- revision B: `0.32.14`

### 事前準備

次のコマンドを利用できる環境を用意します。

- `git`
- `python3`
- `go`
- `curl`
- `zstd`
- `tar`
- `sha256sum`

KJ Atlasは固定commitをcheckoutしておきます。

```bash
git clone https://github.com/hat47x/kj-atlas.git _external/kj-atlas
git -C _external/kj-atlas checkout 4f28c13abe4176503c6fed863383a2d1db2299e9
```

repositoryや認証方式に応じて、既存checkoutを`--kj-atlas-dir`で指定しても構いません。

### 実行

SOZA repository rootから次を実行します。

```bash
runtime/integration/run_runtime_version_exchange.sh
```

Evidence保存先を明示する場合は次のようにします。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir /path/to/evidence
```

scriptは専用Python virtual environmentを作り、固定Ollama archiveを取得・SHA-256検証した後、同じmodel storageと同じMethod inputをA / Bのruntimeへ通します。その後、`runtime/go/livemethodintegration`の通常testとruntime交換live testを実行します。

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- 実験identity
- 固定Method request
- A / Bのruntime version log
- A / Bのmodel digest / tags
- model inference Evidence
- KJ Atlas result
- Adapter / KJ Atlas / Ollama log

途中で失敗した場合も、そこまで生成されたファイルを保存します。

```text
Evidence directoryが作られた
  != runtime exchange PASS

runtime exchange PASS
  != arbitrary runtime portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation / Decision correctness
  != E4 Operational portability
```

実験の意味、Exact Realization revision、historical Application不変性、未検証範囲は`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。

## Ollama adapter

`e3b_m1b_ollama_adapter.py`は、KJ Atlasのlocal model境界からOllamaへ接続するintegration-only adapterです。model / runtime固有fieldをSOZA Universal Contractへ追加するための実装ではありません。
