# runtime integration probes

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

probeの成立条件をGitHub Actionsや特定runnerへ結び付けません。手動実行、開発端末、外部runner、将来のCIなど、実行面が変わっても同じ固定条件と検査境界へ戻れることを優先します。

```text
what must be verified
  != where it is executed
```

## Runtime version exchange

`run_runtime_version_exchange.sh`は、ISSUE-000070のruntime version交換実験をrepository-localに実行します。

固定するものは次です。

- KJ Atlas source
- Method input
- `qwen2.5:0.5b`のmodel artifact digest
- model prompt

交換するのはOllama runtimeだけです。

- revision A: `0.32.13`
- revision B: `0.32.14`

固定しているOllama archiveはLinux / amd64用です。そのためcurrent harnessもLinux / amd64を対象にします。これはSOZA全体のplatform support方針ではなく、ISSUE-000070で使う固定実験artifactの境界です。

## KJ Atlas sourceの扱い

KJ Atlasの固定commitは次です。

```text
repository
  hat47x/kj-atlas

commit
  4f28c13abe4176503c6fed863383a2d1db2299e9
```

runtime交換の厳密なEvidenceでは、Git working treeをそのまま実行sourceとして使いません。

KJ Atlasは`.env`、`*.so`、`__pycache__`、`*.pyc`、`*.egg-info`などをGit管理外にできます。`Settings`も`.env`を読み得ます。したがってworking treeが通常の`git status`でcleanでも、ignored fileまで固定commit identityに含まれるわけではありません。

```text
clean Git checkout
  != byte-complete runtime surface identity
```

そのため、固定commit objectから追跡済みruntime surfaceだけをexportし、その出力をGit object identityで再検証してからharnessへ渡します。

### 1. 固定commitからruntime sourceをexportする

`export_kj_atlas_runtime_source.py`を使います。

```bash
python3 runtime/integration/export_kj_atlas_runtime_source.py \
  --checkout-dir /path/to/kj-atlas \
  --output-dir /path/to/new-kj-atlas-runtime-bundle
```

exporterはworking treeをcopyしません。repository内の固定commit objectへ`git archive`を実行し、次の4要素だけを書き出します。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

したがって、checkoutにignored `.env`やcache、build artifactが存在していてもexport対象には入りません。HEADが後続commitへ進んでいても、固定commit objectがrepository内に存在する限り、対象commitを明示して同じsurfaceを再構成します。

出力先は新しいdirectoryでなければならず、KJ Atlas repository配下には作成できません。

### 2. runtime surface identityを検証する

exporterは生成後に`verify_kj_atlas_runtime_source.py`を実行します。同じverifierは、外部から事前配置されたbundleにも利用できます。

固定identityは次のように分けます。

```text
fixed KJ Atlas commit
  4f28c13abe4176503c6fed863383a2d1db2299e9

parent backend tree
  7d71ac2b4d32bef90f3a481ade1b4c92ddddd084

minimal runtime surface tree
  208bea71eef4afed3ddfd3fabb36b0969d167a90
```

`parent backend tree`は、固定commit内でruntime surfaceを切り出した親文脈です。`minimal runtime surface tree`は、実際に持ち込む4要素だけからGit object規則で再構成したtree identityです。

```text
parent backend tree
  != runtime surface tree
```

verifierは次を実測します。

- `pyproject.toml` blob
- `alembic.ini` blob
- `alembic/` tree
- `src/` tree
- 4要素から再構成したruntime surface tree

さらに、予期しないtop-level要素、symlink、実行bit付きsource fileを拒否します。bundle pathやfile名だけを固定sourceの根拠にはしません。

固定KJ Atlasの`pyproject.toml`はREADMEやlicense等をbuild metadataとして参照しておらず、setuptools package探索も`src`を基準にしています。そのため、この4要素で今回必要なpackage build境界を構成できます。

## 厳密なruntime交換実行

### checkoutを起点に一度で実行する

KJ Atlas repositoryを手元に置ける場合は、`run_runtime_version_exchange_from_checkout.py`をstrict Evidence用の入口とします。

```bash
python3 runtime/integration/run_runtime_version_exchange_from_checkout.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --source-export-identity /path/to/new-source-export-identity.json \
  -- \
  --evidence-dir /path/to/new-evidence-directory
```

このentrypointはcheckoutのworking treeをharnessへ渡しません。固定commit objectからverified runtime bundleを生成し、内部で次の形へ変換します。

```text
KJ Atlas Git repository
  ↓ fixed commit object
export_kj_atlas_runtime_source.py
  ↓ verified runtime bundle
run_runtime_version_exchange.sh --kj-atlas-backend-bundle ...
```

生成したbundle自体も残したい場合は、まだ存在しないpathを`--source-bundle-dir`で指定します。

```bash
python3 runtime/integration/run_runtime_version_exchange_from_checkout.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --source-bundle-dir /path/to/new-kj-atlas-runtime-bundle \
  --source-export-identity /path/to/new-source-export-identity.json \
  -- \
  --evidence-dir /path/to/new-evidence-directory
```

`--source-export-identity`は、checkoutからbundleを作った取得Provenanceを別JSONとして残すための任意指定です。既存file、KJ Atlas repository配下、verified runtime bundle配下は拒否します。

entrypointからharnessへ`--kj-atlas-dir`または別の`--kj-atlas-backend-bundle`を重ねて渡すことも拒否します。sourceの選択を一つに固定するためです。

### 事前にexportしたbundleを使う

export済みbundleをpreflightへ渡します。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle
```

その後、同じbundleでharnessを実行します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle \
  --evidence-dir /path/to/new-evidence-directory
```

固定runtime archiveとmodel storageを事前配置している場合は次のように指定できます。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory
```

`run_runtime_version_exchange.sh`には従来の`--kj-atlas-dir`も残しています。ただし、これはcheckoutのcommit / cleanlinessを確認する互換・開発用経路です。ignored fileまで含むbyte-complete source identityを固定しないため、ISSUE-000070をResolvedにするruntime-version-exchange Evidenceには使いません。

## runtime / model artifact

固定runtime archiveは次です。

- Ollama `0.32.13`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- Ollama `0.32.14`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

固定modelは次です。

- model: `qwen2.5:0.5b`
- full digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`

runtime archiveはdownloadしても事前配置しても構いません。どちらでも実際に使うbytesのSHA-256を計算し、固定値へ一致させます。

`--model-dir`で既存model storageを使う場合もtagだけでは受理しません。Ollama起動後にAPIからfull model digestを観測して固定値へ照合します。固定artifactが存在しない場合、既存storageへharnessが勝手に`ollama pull`することはありません。

```text
acquisition path
  != artifact identity
```

## work / Evidence directory

`--work-dir`と`--evidence-dir`には、まだ存在しない新しいpathを指定します。

一つのEvidence directoryには一つのrunだけを対応させます。途中失敗したrunへ前回runの未上書きファイルが残り、今回生成されたEvidenceのように見えることを防ぐためです。

work / Evidence / external model directoryをSOZAまたはKJ Atlas source配下には置けません。

Ollama、SOZA model adapter、KJ Atlasには固定local port `11434` / `8001` / `8101`を使います。起動前にportが空いていることを確認し、ready判定でもharness自身が起動したPIDの生存を確認します。

## Local preflight

`check_runtime_version_exchange_preflight.py`はactual processを起動せず、runtime archiveやmodelを取得せずに、実行前に解消できる不足を確認します。

主な確認対象は次です。

- Linux / amd64であること
- 必要commandが利用できること
- SOZA repositoryがcleanであること
- KJ Atlas checkoutまたはverified bundleの入力条件
- checkout / bundleを同時指定していないこと
- work / Evidence / model pathの境界
- 事前配置runtime archiveの実測SHA-256
- 事前配置model storageのdirectory境界
- local portの空き

strict Evidence経路では、export後の`--kj-atlas-backend-bundle`をpreflightへ指定します。checkoutの通常clean判定は準備診断には利用できますが、byte-complete runtime source identityの代替にはしません。

```text
preflight ready
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

## 実行中のsource分離

verified bundleをharnessへ渡した後も、外部入力をそのままbuild・実行しません。

harness所有のwork directoryへ次の二つを分けてcopyし、双方を再検証します。

- execution source
- package install source

package buildが`*.egg-info`等を生成してもexecution sourceへ混ざらないようにするためです。live Go test開始時には、execution sourceをもう一度verifierへ通します。

Go側guardは`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしません。harnessがsource mode、execution source、verifier、runtime archive、version logのpathを明示します。

## 軽量検査

actual Ollamaを起動しない境界検査として次を用意しています。

```bash
python3 runtime/integration/test_verify_kj_atlas_runtime_source.py
python3 runtime/integration/test_export_kj_atlas_runtime_source.py
python3 runtime/integration/test_run_runtime_version_exchange_from_checkout.py
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
python3 runtime/integration/test_run_runtime_version_exchange.py

cd runtime/go
go test ./livemethodintegration -count=1
```

確認対象には次を含みます。

- Git tree SHA再構成と`git write-tree`の一致
- pinned componentからruntime surface treeを再構成できること
- ignored `.env` / `.so` / `__pycache__`がcommit-object exportへ混入しないこと
- HEADが後続commitでも固定commit objectをexportできること
- source tamper / top-level drift / symlink / executable bitの拒否
- checkout entrypointがworking tree pathをharnessへ渡さず、verified bundle modeだけを使うこと
- source export identityの既存path / checkout配下 / bundle配下を副作用前に拒否すること
- preflight / harness / verifier / Go guardの固定identity整合
- runtime version / archive digestの整合
- Evidence directory分離
- 事前配置model storageを暗黙更新しないこと

```text
lightweight boundary test PASS
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- SOZA commit
- KJ Atlas source identity
- execution host OS / architecture
- runtime A / B versionとarchive digest
- runtime archive acquisition mode
- model name / expected full digest / storage mode
- 固定Method request
- runtime version log
- actual runtime archive SHA-256
- model tags / digest
- model inference Evidence
- KJ Atlas result
- Adapter / KJ Atlas / Ollama log

checkoutからstrict entrypointを使った場合、`--source-export-identity`で保存したJSONは、固定commit objectからruntime bundleを取得した経路のProvenanceとしてEvidenceと併せて保管できます。この取得経路自体をMethod Realization identityには昇格させません。

Evidence directoryが作成されたこと自体は、実験成功を意味しません。

```text
source identity verified
  != actual inference succeeded

runtime exchange PASS
  != arbitrary runtime portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation / Decision correctness
  != E4 Operational portability
```

実験の意味、Exact Realization revision、historical Application不変性、Resolution条件は`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。

## Ollama adapter

`e3b_m1b_ollama_adapter.py`は、KJ Atlasのlocal model境界からOllamaへ接続するintegration-only adapterです。model / runtime固有fieldをSOZA Universal Contractへ追加するための実装ではありません。

## Natural Japanese review

このREADMEでは、sourceを「どこから得たか」と「実際にどのbytesを実行したか」を分けました。

特にGit checkoutについて、通常のclean判定ではignored fileまで固定できないことを明示しました。厳密なEvidenceでは固定commit objectから追跡済みruntime surfaceだけをexportし、bundle verifierへ戻します。checkoutを起点に実行する場合も専用entrypointを通し、working treeそのものをharnessへ渡しません。これにより、ローカル状態を固定commit由来の実行sourceと誤認しないようにしています。

同様にruntime / model artifactでも、downloadか事前配置かという取得経路と、実際に使ったbytes / digestを分けています。

preflight、source verification、actual process execution、historical reconstruction、成果品質も別の責務として記述しました。actual Ollama `0.32.13` / `0.32.14`交換が未完了であることは変えず、実装済みの境界と未取得Evidenceを自然な日本語として読み分けられることを最重要視して再ドラフトしています。
