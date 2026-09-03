# KJ Atlas runtime source bundle

更新日: 2026-09-03

この文書は、`ISSUE-000070`のruntime version交換実験で使うKJ Atlas sourceを、固定Git checkoutとは別の形で安全に受け渡すための手順をまとめます。

本機能の目的は、source identityの検証を弱めることではありません。実行環境にKJ Atlasの完全なGit working treeを持ち込めない場合でも、固定commitから切り出した最小runtime surfaceをGit object identityで再検証し、同じ実験条件へ戻れるようにすることです。

```text
source acquisition
  = fixed Git checkout | verified runtime bundle

source identity
  = pinned Git object identities

acquisition path
  != Method Realization identity
```

## 固定するsource identity

対象repositoryとcommitは次です。

- repository: `hat47x/kj-atlas`
- source commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- parent backend tree: `7d71ac2b4d32bef90f3a481ade1b4c92ddddd084`
- runtime surface tree: `208bea71eef4afed3ddfd3fabb36b0969d167a90`

runtime bundleへ持ち込むのは、backend全体ではなくactual runtimeに必要な次のsurfaceです。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

個々の主要objectも固定しています。

- `pyproject.toml` blob: `29d9427889a29cb8efcef10c59da5228c82147af`
- `alembic.ini` blob: `05ace092c712dfda73634ef70e7bcb52eb74c712`
- `alembic/` tree: `fbecd06d167e162609ae8b844dda3c7585479960`
- `src/` tree: `4c0b786a81bded22eab5d308289dc55a91cf8324`

parent backend treeとruntime surface treeは同じものではありません。前者は固定commit上のbackend全体のidentity、後者は今回の実行に持ち込む最小surfaceのidentityです。

## なぜfileのSHA-256ではなくGit object identityを使うのか

このbundleは、固定Git commitから切り出したsourceであることを確認したい資産です。そのため、Git自身が用いるblob / tree object IDを再構成し、固定commitで観測したobject identityへ戻します。

`verify_kj_atlas_runtime_source.py`は、file bytesだけでなくdirectory構造とfile modeを含めてtree identityを再構成します。

次の状態は受理しません。

- source fileのbytesが変わっている。
- 予期しないtop-level fileやdirectoryが追加されている。
- symlink / hard linkが混入している。
- 通常source fileに実行bitが付いている。
- 必要なfile / treeが欠けている。
- runtime surface treeが固定値と一致しない。

```text
same path names
  != verified source identity

same file count
  != verified source identity

matching pinned Git object identities
  = verified runtime source boundary
```

## 固定checkoutからbundleを作る

固定commit objectを持つKJ Atlas repositoryが利用できる場合は、`export_kj_atlas_runtime_source.py`でbundleを作れます。

```bash
python3 runtime/integration/export_kj_atlas_runtime_source.py \
  --checkout-dir /path/to/kj-atlas \
  --output-dir /path/to/new-kj-atlas-runtime-bundle \
  --identity-output /path/to/new-source-export-identity.json
```

exporterはworking treeをそのままcopyしません。`git archive`で固定commit objectから対象surfaceを取り出します。このため、working treeへ`.env`、bytecode、build artifact等が存在していても、それらをbundleへ混入させません。

出力directoryは新規pathだけを受け付け、KJ Atlas repository配下への出力を拒否します。生成後は同じverifierでbundleを再検証し、失敗した場合は不完全な出力を残さないようにします。

## 受け取ったbundleを検証する

既にbundleを受け取っている場合は、actual runtimeを起動する前に次で検証できます。

```bash
python3 runtime/integration/verify_kj_atlas_runtime_source.py \
  --backend-dir /path/to/kj-atlas-runtime-bundle
```

検証結果をJSONとして保存する場合は`--output`を使います。

```bash
python3 runtime/integration/verify_kj_atlas_runtime_source.py \
  --backend-dir /path/to/kj-atlas-runtime-bundle \
  --output /path/to/source-identity.json
```

検証成功はsource identityを確認したことだけを意味します。

```text
source bundle verification PASS
  != Python package installation PASS
  != KJ Atlas API startup PASS
  != Ollama runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## preflightで使う

`check_runtime_version_exchange_preflight.py`は、固定checkoutとverified runtime bundleを排他的なsource modeとして扱います。

bundleを使う場合は次のように指定します。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-backend-bundle /path/to/kj-atlas-runtime-bundle
```

固定runtime archiveやmodel storageも事前配置している場合は、従来どおり同時に指定できます。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-backend-bundle /path/to/kj-atlas-runtime-bundle \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

preflightはbundleをSOZA repository配下に置くことを拒否し、fixed Git object identityをactualに再計算して確認します。

## actual harnessで使う

verified bundleを直接使う場合は、`--kj-atlas-backend-bundle`を指定します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/kj-atlas-runtime-bundle \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --evidence-dir /path/to/new-evidence-directory
```

`--kj-atlas-dir`と`--kj-atlas-backend-bundle`は併用しません。どのsource modeを使ったかはEvidenceへ残します。

harnessは受け取ったbundleを直接build対象にしません。まず検証済みsourceからwork領域へ実行用copyとpackage install用copyを作り、それぞれを再検証してから利用します。package build等の副作用で受領bundleそのものを変えないためです。

Go側live guardもsource modeを受け取り、actual live test直前に再確認します。

- `git-checkout`では、固定commit objectとclean working treeを再確認します。
- `verified-runtime-bundle`では、Python verifierを再実行し、source commit、parent backend tree、runtime surface tree、verification basisを確認します。

## checkoutからactual harnessまで一続きに実行する

固定checkoutは持っているが、working treeそのものをactual runtimeへ渡したくない場合は、`run_runtime_version_exchange_from_checkout.py`を使えます。

```bash
python3 runtime/integration/run_runtime_version_exchange_from_checkout.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --source-bundle-dir /path/to/new-kj-atlas-runtime-bundle \
  --source-export-identity /path/to/new-source-export-identity.json \
  -- \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --evidence-dir /path/to/new-evidence-directory
```

このentrypointは、checkoutから固定commitのruntime bundleをexportした後、harnessへは`--kj-atlas-backend-bundle`だけを渡します。呼び出し側が別の`--kj-atlas-dir`や`--kj-atlas-backend-bundle`をharness引数として重ねることは拒否します。

## ローカルの軽量検査

source bundle境界は、actual Ollama runtimeを必要としない次のtestで確認できます。

```bash
python3 runtime/integration/test_verify_kj_atlas_runtime_source.py
python3 runtime/integration/test_export_kj_atlas_runtime_source.py
python3 runtime/integration/test_run_runtime_version_exchange_from_checkout.py
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
python3 runtime/integration/test_run_runtime_version_exchange.py
```

Go側source guardは`runtime/go/livemethodintegration/runtime_version_source_guard_unit_test.go`で、source mode未指定、未知mode、path不足、tree identity drift、未知verification basis等を拒否します。

これらの軽量testが通っても、actual A / B inferenceが成立したことにはなりません。

## Evidenceの扱い

actual harnessは、従来のEvidenceに加えてKJ Atlas source identity JSONを保存します。少なくとも次へ戻れる状態を目指します。

- source acquisition mode
- pinned source commit
- parent backend tree
- runtime surface tree
- verification basis
- actual実行に使ったsource mode

取得経路が違っても、固定source identityが同じなら、それだけを理由に別logical Method Realizationへ分けません。

```text
Git checkout
  | export from pinned commit
  | prepositioned verified bundle
  v
same pinned runtime source identity

!= different Method Definition
!= automatically different logical Method Realization
```

## 停止線

source bundleは、`ISSUE-000070`の実行面を持ち運びやすくするためのprobe-localな仕組みです。

```text
verified KJ Atlas runtime source bundle
  != arbitrary KJ Atlas version portability
  != arbitrary source bundle format support
  != runtime A/B exchange PASS
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation correctness
  != Decision correctness
```

現時点では新しいStable Requirement、Acceptance Scenario、Universal Contract fieldを追加しません。actual runtime交換で既存Contractに表現できない欠落が観測された場合にのみ再検討します。

## 自然な日本語レビュー

この文書では、sourceの取得方法、source identityの検証、actual実行、Evidence、成果品質を一つの成功条件へまとめないことを重視しました。

「Git checkoutがないから検証を弱める」のではなく、「固定commitから必要なruntime surfaceを切り出し、そのbytes・directory構造・file modeをGit object identityへ戻して再検証する」という境界を中心に記述しています。

また、source bundleを新しいUniversal Contractへ先取りせず、`ISSUE-000070`のprobe-localな取得・実行手段として扱っています。actual Ollama `0.32.13` / `0.32.14`交換が未完了であることは変えていません。