# runtime integration probes

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

ここにあるprobeは、GitHub Actionsや特定のrunnerを意味上の成立条件にしません。手動実行、開発端末、外部runner、将来のCIなど、どの実行面から呼び出しても同じ固定条件と検査境界を再現できることを優先します。

```text
what must be verified
  != where it is executed
```

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

実行開始時にOSとCPU architectureを確認し、対象外の環境ではruntime artifactを扱う前に停止します。これはSOZA全体のplatform support方針ではなく、ISSUE-000070で使う固定実験artifactの境界です。

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
- `cp`

`curl`はOllama release archiveの取得だけでなく、localhost上のOllama / model adapter / KJ Atlas API確認にも使います。そのため、runtime archiveやmodel artifactを事前配置した場合も必要です。

SOZAは未commit変更のないcleanなGit checkoutである必要があります。KJ Atlas sourceには、次の二つの経路を用意しています。

1. 固定commitのclean Git checkoutを使う。
2. 固定commitから切り出した最小runtime source bundleを使う。

どちらの経路でも、実際に使うsource identityを検査してから実験を開始します。

#### clean Git checkoutを使う

KJ Atlasを固定commitへcheckoutします。

```bash
git clone https://github.com/hat47x/kj-atlas.git _external/kj-atlas
git -C _external/kj-atlas checkout 4f28c13abe4176503c6fed863383a2d1db2299e9
```

repositoryや認証方式に応じて、既存checkoutを`--kj-atlas-dir`で指定しても構いません。checkout modeでは、working treeがcleanであること、HEADが固定commitであること、固定commit objectをGit repository内で参照できることを確認します。

#### 最小runtime source bundleを使う

Git checkoutを実行面へ持ち込めない場合は、`--kj-atlas-backend-bundle`で最小runtime source bundleを指定できます。

bundleに含めるtop-level要素は次の4つだけです。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

これらはKJ Atlas固定commit `4f28c13abe4176503c6fed863383a2d1db2299e9` の `03_Implement/backend`から切り出したものです。

固定identityは次のように区別します。

```text
fixed KJ Atlas commit
  4f28c13abe4176503c6fed863383a2d1db2299e9

parent backend tree
  7d71ac2b4d32bef90f3a481ade1b4c92ddddd084

minimal runtime surface tree
  208bea71eef4afed3ddfd3fabb36b0969d167a90
```

`parent backend tree`は固定commit内でruntime surfaceを切り出した親文脈です。`minimal runtime surface tree`は、実際にbundleへ持ち込む4要素だけからGit object規則で再構成したtree identityです。README、tests、scriptsなどを含む親backend全体と最小runtime surfaceは同じtreeではありません。

```text
parent backend tree
  != runtime surface tree
```

`verify_kj_atlas_runtime_source.py`は、bundleの各file / directoryからGit blob / tree object IDを再計算し、次を検査します。

- `pyproject.toml` blob
- `alembic.ini` blob
- `alembic/` tree
- `src/` tree
- 4要素だけから再構成したruntime surface tree
- 予期しないtop-level要素が存在しないこと
- symlinkや実行bit付きsource fileが混入していないこと

したがって、bundle pathやfile名が合っているだけでは受理しません。source bytes、directory構造、Gitが意味を持つfile modeまで固定identityと一致させます。

bundle modeでは、検証した外部bundleを直接build・実行しません。harness所有のwork directoryへ、実行用copyとpackage install用copyを別々に作り、両copyを再検証します。package buildによって`*.egg-info`などが生成されても、実行sourceのidentityを変えないためです。live test開始時にはGo側guardから実行用copyをもう一度検証します。

`--kj-atlas-dir`と`--kj-atlas-backend-bundle`を同時には指定できません。

### 実行

SOZA repository rootから次を実行します。

```bash
runtime/integration/run_runtime_version_exchange.sh
```

Evidence保存先を明示する場合は次のようにします。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir /path/to/new-evidence-directory
```

最小runtime source bundleを使う場合は次のようにします。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/kj-atlas-backend-runtime-bundle \
  --evidence-dir /path/to/new-evidence-directory
```

固定runtime archiveとmodel storageも事前配置している場合は、次のように指定できます。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/kj-atlas-backend-runtime-bundle \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory
```

事前配置は検証条件を緩める仕組みではありません。runtime archiveは取得済みbytesから実測SHA-256を計算し、download経路と同じ固定値へ照合します。`--model-dir`を指定した場合も、`qwen2.5:0.5b`というtagだけでは受理せず、Ollama APIから観測したfull model digestが固定値と一致することを要求します。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual bytes / full digest

acquisition path
  != artifact identity
```

`--model-dir`で指定した既存model storageに固定model artifactがなければ、harnessはそのdirectoryへ勝手に`ollama pull`せず停止します。harness自身が作成したwork-local model storageでは、固定artifactがまだ存在しない場合に限って`ollama pull`を行い、取得後に同じfull digestを検査します。

この事前配置経路とsource bundle経路を組み合わせることで、KJ AtlasのGit checkout、Ollama release archive、model artifactの取得方法を、実験の意味上のidentityから切り離せます。ただし、KJ Atlas backendのPython依存関係など、実行に必要なすべての依存物まで完全にoffline化することは保証しません。

`--work-dir`を指定する場合は、**まだ存在しない新しいpath**を指定します。harnessがそのdirectoryを自分で作成し、通常終了時には削除します。既存directoryをそのまま作業領域として再利用しないことで、利用者の既存ファイルを上書き・削除する可能性を避けます。作業directoryを残したい場合は`--keep-work`を指定します。

`--evidence-dir`も、runごとに**まだ存在しない新しいpath**を指定します。既存Evidence directoryを再利用すると、前回runの未上書きファイルと今回runのファイルが混在し、実行identityを誤認するおそれがあるためです。harnessは既存pathを拒否し、一つのEvidence directoryに一つのrunだけを対応させます。

work / Evidence / external model directoryをSOZAまたはKJ Atlas source配下には置けません。pathは実体pathへ正規化し、source配下を指す場合は停止します。

### 実行中のidentity確認

scriptは専用Python virtual environmentを作り、KJ Atlas sourceを検証し、固定Ollama archiveを取得または事前配置pathから参照した後、次を順に確認します。

1. KJ Atlas sourceが、固定commitのclean checkout、または固定Git object identityへ一致するruntime source bundleであることを確認する。
2. bundle modeでは、実行用copyとinstall用copyを作成し、両方のruntime surface identityを再確認する。
3. A / Bそれぞれのruntime archiveについて実測SHA-256を計算し、固定値と照合する。
4. 実際に起動したbinaryが期待するOllama versionを返すことを確認する。
5. A / Bで同じmodel storageを使い、`qwen2.5:0.5b`のactual model digestが固定値と一致することを確認する。
6. 同じMethod inputをA / Bへ通し、actual inference countersとKJ Atlas responseを確認する。
7. A / Bのprompt SHA-256が同一であることを確認する。
8. `runtime/go/livemethodintegration`の通常testとruntime交換live testを実行する。

Ollama、SOZA model adapter、KJ Atlasには固定local portを使います。各processを起動する前にportが空いていることを確認し、起動後もharness自身が開始したPIDが生存していることを確認します。既に動いている別processのhealth responseを、今回のruntime交換実験の実行事実として誤認しないためです。

live testへ渡すKJ Atlas source mode、実行source path、source verifier、runtime A / B archive、version logのpathは、harnessがすべて明示します。Go側artifact guardは`GITHUB_WORKSPACE`や固定`/tmp`配置へ暗黙に戻りません。bundle modeでは、Go側からsource verifierを再実行して実際の実行source copyを検査します。

## ローカルpreflight

actual runtime交換を開始する前に、`check_runtime_version_exchange_preflight.py`でローカル実行条件だけを副作用なく確認できます。

KJ Atlasのclean checkoutを使う場合は次のように実行します。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas
```

最小runtime source bundleを使う場合も、actual harnessと同じsource interfaceで確認できます。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-backend-bundle /path/to/kj-atlas-backend-runtime-bundle
```

`--kj-atlas-dir`と`--kj-atlas-backend-bundle`は排他的です。どちらも指定しない場合は、actual harnessと同じく`_external/kj-atlas`のcheckoutを確認します。

このpreflightはprocessを起動せず、runtime archiveやmodelを取得しません。主に次を確認します。

- hostが固定artifactの対象であるLinux / amd64か。
- harnessが必要とするコマンドが利用可能か。
- SOZAがGit working treeで、未commit変更がないか。
- checkout modeではKJ Atlas working treeがcleanで固定commitに一致するか。
- bundle modeではKJ Atlas minimal runtime sourceが固定Git object identityに一致するか。
- work / Evidence pathがsource配下を指していないか、既存pathを誤って再利用しないか。
- 事前配置runtime archiveを指定した場合、実測SHA-256が固定値と一致するか。
- 事前配置model storageを指定した場合、directoryが存在し安全な位置にあるか。
- Ollama / model adapter / KJ Atlasで使うlocal portが空いているか。

事前配置artifactだけで実行できる状態を確認したい場合は、次のようにします。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-backend-bundle /path/to/kj-atlas-backend-runtime-bundle \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

`--json`を付けると、`ready` / `blocked`、blocker ID、各checkの状態に加えて、固定KJ Atlas source commit、親backend tree、minimal runtime surface treeを構造化して取得できます。

preflightが`ready`でも、事前配置model storage内のfull model digestはまだ確認済みとは扱いません。model artifact identityは、固定Ollama runtimeを実際に起動した後、`/api/tags`から観測したfull digestで確認します。また、download経路を許可した通常preflightではruntime archiveの未取得状態を`deferred`として扱います。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

preflight自身の境界は次で確認します。

```bash
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
```

このtestは、固定archive digest検査、source modeの排他、source bundleの固定identity境界、事前配置必須時の停止、source path境界、harnessとの固定identity一致、Evidenceへの過大昇格を防ぐ停止線を検査します。

## Harnessの軽量検査

`test_run_runtime_version_exchange.py`と`test_verify_kj_atlas_runtime_source.py`は、actual modelやruntime archiveを取得せず、repository-local harness、source verifier、Go側live guardの接続条件を検査します。

```bash
python3 runtime/integration/test_verify_kj_atlas_runtime_source.py
python3 runtime/integration/test_run_runtime_version_exchange.py
```

確認するのは次です。

- Git tree SHAの再構成結果が実際の`git write-tree`と一致すること。
- 固定4要素から再構成したruntime surface treeが`208bea71eef4afed3ddfd3fabb36b0969d167a90`へ一致すること。
- runtime surface treeと親backend treeを同一視しないこと。
- source改変、予期しないtop-level file、実行bit付きsourceを拒否すること。
- shell syntaxが有効であること。
- `--help`をprobe起動なしで参照できること。
- shell側のOllama version / archive digestと、Go側でExact Bindingに使う固定値が一致すること。
- Python source verifierとGo側guardが、KJ Atlas commit、親backend tree、runtime surface treeの固定値を共有すること。
- harnessがKJ Atlas source mode、実行source、source verifier、runtime archive、version logのpathをlive guardへ明示すること。
- Go側live guardがGitHub Actions固有のworkspaceや固定`/tmp`へ暗黙fallbackしないこと。
- bundleを外部入力のままbuildせず、実行用copyとinstall用copyへ分離すること。
- Evidence directoryをrunごとの新しいpathへ分離する停止線が残っていること。
- 事前配置runtime archiveでも実測SHA-256を固定値へ照合すること。
- 事前配置model storageで固定artifactが見つからない場合、harnessが自動pullせず停止すること。
- archiveの取得経路と固定artifact identityを別のEvidence fieldとして保持すること。

この検査は、harnessのinterfaceと固定identityのずれを早期に検出するためのものです。actual runtimeを起動していないため、runtime version交換のExecutable Evidenceにはなりません。

```text
harness / source verifier test PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- 実験identity
  - SOZA commit
  - KJ Atlas source mode
  - KJ Atlas commit
  - bundle modeでは親backend tree / runtime surface tree / component Git object ID
  - execution host OS / architecture
  - expected runtime / model artifact identity
  - runtime archive acquisition mode (`downloaded` / `prepositioned`)
  - model storage mode (`work-local` / `prepositioned`)
- `kj-atlas-source-identity.json`
- 固定Method request
- A / Bのruntime version log
- A / Bの**実測runtime archive SHA-256**
- A / Bのmodel digest / tags
- model inference Evidence
- KJ Atlas result
- Adapter / KJ Atlas / Ollama log

KJ Atlas sourceの取得方法をEvidenceへ残すのは、再実行時に実行条件へ戻れるようにするためです。`git-checkout`と`verified-runtime-bundle`を別のMethod Realizationへ自動昇格させるためではありません。bundle modeでは、実際に実行したruntime surface bytesが固定Git object identityへ一致したことを確認します。

runtime/model artifactの取得経路をEvidenceへ残すのも同じ理由です。`downloaded`と`prepositioned`を別のRealization identityへ昇格させるのではなく、実際のruntime identityを固定versionと実測archive digestで検証します。

途中で失敗した場合も、そこまで生成されたファイルを保存します。たとえばruntime archiveのdigest不一致で停止した場合でも、実際に計算したdigestをEvidence directoryへ残せます。

Evidence directoryはrunごとに新規作成するため、途中失敗したrunに前回runの後半Evidenceが残っているような状態を許しません。

```text
Evidence directoryが作られた
  != runtime exchange PASS

KJ Atlas source identityが一致した
  != actual inference succeeded

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

## Natural Japanese review

このREADMEでは、実験を動かす手順と、得られた結果をどう読めるかを一つの成功条件へまとめないようにしました。

repository-local harnessが固定する条件、ローカル実行で事故や実行identityの取り違えを避ける停止線、Go側artifact guardへ渡すpath、actual runtimeを使わない軽量検査の責務を順に整理しています。

ローカルpreflightも、実験そのものを小さく代替する仕組みではありません。process起動前に解消できる環境不足や固定source / artifact不一致を先に見つけ、actual probeを開始できる状態とactual inferenceが成立した状態を分けるための診断面として位置づけています。

KJ Atlas sourceについては、Git checkoutそのものを実験成立条件にせず、固定commit由来の最小runtime surfaceをGit object identityで再検証できる経路を追加しました。一方で、親backend treeと実際に実行する最小surface treeは明確に分け、最小bundleをbackend全体と同一視しません。

また、検証済みbundleをそのままbuild対象にせず、実行sourceとpackage install sourceを分離しました。build時の副作用が実行source identityへ混ざらず、live test直前にも実行sourceを再検証できることを重視しています。

runtime/model artifactについても、「どの経路から入手したか」と「どのbytes / digestを実際に使ったか」を分けています。downloadできる環境だけを実験成立条件にせず、事前配置したartifactも同じ固定digest検査へ通します。一方で、事前配置を理由にidentity検査を省略したり、既存model storageを暗黙に更新したりしません。

actual Ollama `0.32.13` / `0.32.14`交換が未完了であることは変えていません。実装済みの実行経路、preflight ready、まだ得られていないScoped Executable Evidenceを自然な日本語として読み分けられることを最重要視して再ドラフトしました。
