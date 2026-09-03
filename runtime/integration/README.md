# runtime integration probes

更新日: 2026-09-03

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

ここにあるprobeは、GitHub Actionsや特定のrunnerを意味上の成立条件にしません。手動実行、開発端末、外部runner、将来のCIなど、どの実行面から呼び出しても同じ固定条件と検査境界へ戻れることを優先します。

```text
what must be verified
  != where it is executed
```

current `develop/v0.2.0`ではGitHub Actions workflowを常設していません。過去のActions Runはhistorical Evidenceとして保持しますが、現在のprobe実行条件にはしません。

## Runtime version exchange

`run_runtime_version_exchange.sh`は、ISSUE-000070のruntime version交換実験をrepository-localに実行するharnessです。

この実験では、次を固定します。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- KJ Atlas endpoint: `POST /ai/suggest-card-groups`
- Method input: harness内の固定3-card input
- model: `qwen2.5:0.5b`
- model artifact digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- model prompt

交換するのはOllama runtime versionだけです。

- revision A: `0.32.13`
- revision B: `0.32.14`

```text
same Method Definition
same logical Method Realization
same KJ Atlas source
same Method input
same pinned model artifact
same model prompt

runtime revision A != runtime revision B
```

この実験の中心は、runtime versionを交換した後も先行Method ApplicationのExact Reference、Provenance、outputを変更せず保持できるかを確認することです。

## 固定runtime artifact

現在のprobeはLinux / amd64用のOllama公式archiveを固定します。

| revision | asset | size | SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesです。

sizeは、明らかに異なるfileを大きなSHA-256計算の前に拒否するための早期guardです。artifact identityの正本は実bytesのSHA-256です。

```text
archive size match
  != artifact identity verified

archive size match
  + exact SHA-256 match
  = fixed runtime archive identity guard
```

MLX / ROCm等の別assetは、同じversion名であっても別bytes / 別digestです。小さいという理由だけでこの実験の固定artifactへ置き換えません。

Linux / amd64という制約はISSUE-000070のprobe-local条件です。SOZA全体のformal platform support matrixをLinux / amd64へ固定するものではありません。

## 事前準備

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

`curl`は外部archiveの取得だけでなく、localhost上のOllama / model adapter / KJ Atlas API確認にも使うため、runtime archiveやmodel artifactを事前配置した場合も必要です。

SOZAとKJ Atlasは、どちらも未commit変更のないcleanなGit checkoutである必要があります。KJ Atlasは固定commitをcheckoutします。

```bash
git clone https://github.com/hat47x/kj-atlas.git _external/kj-atlas
git -C _external/kj-atlas checkout 4f28c13abe4176503c6fed863383a2d1db2299e9
```

既存checkoutを利用する場合は`--kj-atlas-dir`で明示できます。

## ローカルpreflight

actual runtimeを起動する前に、`check_runtime_version_exchange_preflight.py`で副作用のない診断を行えます。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas
```

preflightはprocessを起動せず、runtime archiveやmodelをdownloadしません。主に次を確認します。

- hostがLinux / amd64か。
- 必要コマンドを利用できるか。
- SOZA / KJ AtlasがGit working treeか。
- 両working treeがcleanか。
- KJ Atlas HEADが固定commitか。
- work / Evidence / external model pathがsource repository配下を指していないか。
- 新規pathが必要な場所で既存pathを再利用していないか。
- 事前配置runtime archiveのsizeとSHA-256が固定値に一致するか。
- 事前配置model storageが安全な場所に存在するか。
- 固定local port `11434` / `8001` / `8101`が空いているか。
- work領域を置くfilesystemの空き容量がどの程度あるか。

空き容量は診断値として記録します。固定runtime archive 2本の圧縮bytes合計との比較材料にはできますが、展開後runtime、Python virtual environment、work-local model storageには追加容量が必要です。

```text
disk free-space observation
  != enough capacity proven
```

事前配置artifactだけで開始できるかを確認する場合は、次のようにします。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

`--json`を付けると、`ready` / `blocked`、blocker ID、固定artifact metadata、各checkを構造化JSONで取得できます。

preflightが`ready`でも、model storage内のfull model digestは確認済みとは扱いません。model identityは固定Ollama runtimeを実際に起動した後、Ollama APIから観測したfull digestで確認します。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

preflight自身の境界は次で検査します。

```bash
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
```

current testは、固定archive size / digest、事前配置必須時の停止、path境界、disk観測の非昇格、harnessとの固定identity一致、Evidenceの停止線を扱います。

## actual harnessの実行

SOZA repository rootから実行します。

```bash
runtime/integration/run_runtime_version_exchange.sh
```

KJ Atlas checkoutとEvidence保存先を明示する例です。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir /path/to/new-evidence-directory
```

固定runtime archiveとmodel storageを事前配置している場合は次のように指定します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory
```

事前配置は検証条件を弱める仕組みではありません。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual archive bytes + fixed SHA-256

acquisition path
  != artifact identity
```

`--model-dir`を指定した場合も、model tagだけでは受理しません。Ollama APIから観測したfull model digestが固定値と一致する必要があります。

既存model storageに固定artifactがなければ、harnessはそのdirectoryへ勝手に`ollama pull`せず停止します。harness自身が作るwork-local storageでは、固定artifactが存在しない場合に取得を試み、取得後に同じfull digestを検査します。

## pathとprocessの安全境界

`--work-dir`と`--evidence-dir`には、まだ存在しない新しいpathを指定します。

一つのEvidence directoryを一つのrunだけへ対応させることで、失敗した新runに前回runの後半ファイルが残り、一つの実行結果に見える状態を避けます。

work / Evidence / external model directoryはSOZAまたはKJ Atlas repository配下へ置けません。実体pathへ正規化した後に判定します。

固定portを使うprocessは、起動前にportが空いていることを確認し、起動後もharness自身が開始したPIDの生存を確認します。別processのhealth responseを今回の実行identityへ取り込まないためです。

Go側artifact guardへ渡すKJ Atlas checkout、runtime archive、version logのpathはharnessがすべて明示します。`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしません。

## actual実行で確認すること

harnessは概ね次を一続きに確認します。

1. SOZA / KJ Atlas source identityとclean treeを確認する。
2. runtime A / B archiveを取得または事前配置pathから参照する。
3. A / Bのactual archive SHA-256を固定値と照合する。
4. archiveを別々のruntime rootへ展開する。
5. actual binary versionが`0.32.13` / `0.32.14`であることを確認する。
6. 両runtimeで同じ固定model artifact digestを確認する。
7. 同じMethod inputをKJ Atlasへ渡し、actual inference countersとresultを保存する。
8. A / Bのprompt SHA-256が同一であることを確認する。
9. SOZAの通常Method integration testとruntime-exchange live testを実行する。
10. historical Application不変性、Exact Binding、portable reconstruction、negative controlを確認する。
11. 成否にかかわらず、そこまで得られたEvidenceをrun専用directoryへ保存する。

生成文そのものの一致はPASS条件ではありません。

## Harnessの軽量検査

actual runtimeやmodelを取得せず、shell interfaceとGo側guardの接続条件を次で確認できます。

```bash
python3 runtime/integration/test_run_runtime_version_exchange.py
```

このtestは、shell syntax、`--help`、固定runtime version / digest、明示path、run単位のEvidence directory、事前配置artifactのdigest検査、model storageの非自動更新等を確認します。

```text
harness interface test PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- execution ID
- SOZA repository commit
- KJ Atlas source commit
- host OS / architecture
- runtime A / B versionとexpected archive digest
- runtime archive acquisition mode
- model name / expected digest / storage mode
- `qualityJudgement = not_evaluated`
- 固定Method request
- A / B runtime version log
- A / B actual runtime archive SHA-256
- A / B model digest / tags
- A / B inference Evidence
- A / B KJ Atlas result
- Adapter / KJ Atlas / Ollama log

取得経路はProvenanceとして残しますが、それだけでRealization identityを分けません。

途中で停止した場合も、そこまで生成されたEvidenceを残します。

```text
Evidence preserved
  != runtime exchange PASS
  != output quality satisfied
```

## 成果品質との境界

このprobeが確認するのはruntime交換に伴うexecution identityとhistorical reconstructionです。

actual KJ Atlas outputの意味上の品質は`evaluation/method-quality/`の評価境界で別に扱います。

```text
runtime exchange PASS
  != arbitrary runtime portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation correctness
  != Decision correctness
  != E4 Operational portability
```

実験の意味、Exact Realization revision、historical Application不変性、Resolution条件は`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。

## Ollama adapter

`e3b_m1b_ollama_adapter.py`は、KJ Atlasのlocal model境界からOllamaへ接続するintegration-only adapterです。model / runtime固有fieldをSOZA Universal Contractへ追加するための実装ではありません。

## 自然な日本語レビュー

このREADMEを、current no-Actions baseline、ISSUE-000070のrepository-local harness、固定artifact、事前配置経路、preflight、Evidence保存、ISSUE-000071の成果品質評価境界へ戻って全文監査しました。

実験を動かす手順と、結果をどう評価できるかを一つの成功条件へまとめていません。特に、preflightの`ready`、archive size一致、disk空き容量、harness interface testのPASSをactual runtime交換成立へ昇格させない構成にしました。

Ollama公式Release metadataで確認した固定archive sizeをpreflightへ反映し、事前配置fileの明らかな取り違えを早期に止められるようにしました。ただしsizeはSHA-256の代替ではありません。artifact identityは実bytesのdigestへ戻します。

また、runtime/model artifactの取得経路とidentityを分け、downloadできる環境だけを実験成立条件にしていません。事前配置したartifactも同じidentity検査へ通し、既存model storageを暗黙に更新しません。

actual Ollama `0.32.13` / `0.32.14`交換が未完了であることは変えていません。実装済みの安全策とactual A / BのNot Yet Verifiedを、自然な日本語として読み分けられることを最重要視して再ドラフトし、最終意味監査を実施しました。
