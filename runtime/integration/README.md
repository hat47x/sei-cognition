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

### 現在の実行対象

固定しているOllama archiveはLinux / amd64用です。そのため、current harnessはLinux / amd64環境だけを対象にします。

実行開始時にOSとCPU architectureを確認し、対象外の環境ではruntime artifactを取得する前に停止します。これはSOZA全体のplatform support方針ではなく、ISSUE-000070で使う固定実験artifactの境界です。

### 事前準備

次のコマンドを利用できる環境を用意します。

- `git`
- `python3`
- `go`
- `curl`
- `zstd`
- `tar`
- `sha256sum`
- `uname`
- `mktemp`

SOZAとKJ Atlasは、どちらも未commit変更のないcleanなGit checkoutである必要があります。SOZA repositoryでは`_external/`をlocal external checkoutとして`.gitignore`していますが、KJ Atlas側のworking treeはKJ Atlas自身のrepositoryで別途検査します。

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

`--work-dir`を指定する場合は、**まだ存在しない新しいpath**を指定します。harnessがそのdirectoryを自分で作成し、通常終了時には削除します。既存directoryをそのまま作業領域として再利用しないことで、利用者の既存ファイルを上書き・削除する可能性を避けます。作業directoryを残したい場合は`--keep-work`を指定します。

work / Evidence directoryをSOZAまたはKJ Atlas repository配下には置けません。pathは作成前に実体pathへ正規化し、source repository配下を指す場合は停止します。

### 実行中のidentity確認

scriptは専用Python virtual environmentを作り、固定Ollama archiveを取得した後、次を順に確認します。

1. A / Bそれぞれのruntime archiveについて実測SHA-256を計算し、固定値と照合する。
2. 実際に起動したbinaryが期待するOllama versionを返すことを確認する。
3. A / Bで同じmodel storageを使い、`qwen2.5:0.5b`のactual model digestが固定値と一致することを確認する。
4. 同じMethod inputをA / Bへ通し、actual inference countersとKJ Atlas responseを確認する。
5. A / Bのprompt SHA-256が同一であることを確認する。
6. `runtime/go/livemethodintegration`の通常testとruntime交換live testを実行する。

Ollama、SOZA model adapter、KJ Atlasには固定local portを使います。各processを起動する前にportが空いていることを確認し、起動後もharness自身が開始したPIDが生存していることを確認します。既に動いている別processのhealth responseを、今回のruntime交換実験の実行事実として誤認しないためです。

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- 実験identity
  - SOZA commit
  - KJ Atlas commit
  - execution host OS / architecture
  - expected runtime / model artifact identity
- 固定Method request
- A / Bのruntime version log
- A / Bの**実測runtime archive SHA-256**
- A / Bのmodel digest / tags
- model inference Evidence
- KJ Atlas result
- Adapter / KJ Atlas / Ollama log

途中で失敗した場合も、そこまで生成されたファイルを保存します。たとえばruntime archiveのdigest不一致で停止した場合でも、実際に計算したdigestをEvidence directoryへ残せます。

```text
Evidence directoryが作られた
  != runtime exchange PASS

runtime archive digestが一致した
  != actual inference succeeded

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
