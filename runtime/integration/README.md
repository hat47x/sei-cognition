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
same verified KJ Atlas runtime surface
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

固定artifact metadataの機械可読な正本として`runtime_version_exchange_artifacts.json`を置き、事前配置archiveの準備には`prepare_runtime_version_exchange_archives.py`を利用できます。取得経路とartifact identityは分けます。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual archive bytes + fixed SHA-256

acquisition path
  != artifact identity
```

## KJ Atlas source identity

KJ Atlasの固定commitは次です。

```text
repository
  hat47x/kj-atlas

commit
  4f28c13abe4176503c6fed863383a2d1db2299e9
```

### clean checkoutだけではstrict Evidenceにならない

KJ Atlasは`.env`、`*.so`、`__pycache__`、`*.pyc`、`*.egg-info`などをGit管理外にできます。`Settings`も`.env`を読み得ます。

したがって、HEADが固定commitで通常の`git status`がcleanであっても、ignored fileまで固定commit identityに含まれるわけではありません。

```text
HEAD = pinned commit
  + normal Git clean
  != byte-complete runtime source identity
```

`run_runtime_version_exchange.sh --kj-atlas-dir ...`は互換・開発用として残しますが、ISSUE-000070をResolvedにするstrict runtime-version-exchange Evidenceには使いません。

### 固定commit objectからruntime surfaceをexportする

`export_kj_atlas_runtime_source.py`はworking treeをcopyせず、repository内の固定commit objectへ`git archive`を実行します。

実行へ持ち込むのは次の4要素だけです。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

checkoutにignored `.env`、binary extension、bytecode cache、build artifactが存在していてもexport対象には入りません。HEADが後続commitへ進んでいても、固定commit objectがrepository内に存在する限り、同じruntime surfaceへ戻れます。

固定identityは次のように区別します。

```text
fixed KJ Atlas commit
  4f28c13abe4176503c6fed863383a2d1db2299e9

parent backend tree
  7d71ac2b4d32bef90f3a481ade1b4c92ddddd084

minimal runtime surface tree
  208bea71eef4afed3ddfd3fabb36b0969d167a90
```

`parent backend tree`は固定commit内の親文脈です。`minimal runtime surface tree`は、実際に実行へ持ち込む4要素だけをGit object規則で再構成したidentityです。

```text
parent backend tree
  != runtime surface tree
```

`verify_kj_atlas_runtime_source.py`は、次を実測します。

- `pyproject.toml` blob
- `alembic.ini` blob
- `alembic/` tree
- `src/` tree
- runtime surface tree

さらに、予期しないtop-level要素、symlink、実行bit付きsource fileを拒否します。path名や「固定commit由来」という申告だけではbundleを受理しません。

固定commitの`pyproject.toml`はREADMEやlicense等をbuild metadataとして参照せず、setuptools package探索は`src`を基準としています。そのため、この4要素で今回必要なpackage build境界を構成できます。

手動でexportする場合は次のようにします。

```bash
python3 runtime/integration/export_kj_atlas_runtime_source.py \
  --checkout-dir /path/to/kj-atlas \
  --output-dir /path/to/new-kj-atlas-runtime-bundle
```

出力先は新しいdirectoryでなければならず、KJ Atlas repository配下には作成できません。

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
- `cp`

`curl`は外部archiveの取得だけでなく、localhost上のOllama / model adapter / KJ Atlas API確認にも使うため、runtime archiveやmodel artifactを事前配置した場合も必要です。

KJ Atlas repositoryをsource取得元として使う場合、固定commit objectがrepository内に存在する必要があります。strict Evidenceではworking tree自体を実行しないため、HEADを固定commitへ移動することは必須ではありません。

```bash
git clone https://github.com/hat47x/kj-atlas.git _external/kj-atlas
git -C _external/kj-atlas cat-file -e 4f28c13abe4176503c6fed863383a2d1db2299e9^{commit}
```

## ローカルpreflight

actual runtimeを起動する前に、`check_runtime_version_exchange_preflight.py`で副作用のない診断を行えます。

strict Evidenceでは、export済みverified bundleを指定します。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle
```

checkoutを直接診断する互換経路も残しています。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas
```

このcheckout診断で`ready`になっても、ignored fileまで固定したstrict source verificationとは扱いません。

preflightはprocessを起動せず、runtime archiveやmodelをdownloadしません。主に次を確認します。

- hostがLinux / amd64か。
- 必要コマンドを利用できるか。
- SOZA repositoryがcleanか。
- KJ Atlas checkoutまたはverified bundleの入力条件を満たすか。
- checkoutとbundleを同時指定していないか。
- verified bundleのGit object identityが固定値に一致するか。
- work / Evidence / external model pathがsource配下を指していないか。
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
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

`--json`を付けると、`ready` / `blocked`、blocker ID、固定artifact metadata、固定source metadata、各checkを構造化JSONで取得できます。固定source metadataは`pinnedSourceIdentity`として示し、実測済みsourceと混同しません。verified bundleを指定した場合の実測結果は各bundle checkに現れます。

preflightが`ready`でも、model storage内のfull model digestは確認済みとは扱いません。model identityは固定Ollama runtimeを実際に起動した後、Ollama APIから観測したfull digestで確認します。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

## strict Evidenceのactual実行

### checkoutを起点に一度で実行する

KJ Atlas repositoryを手元に置ける場合は、`run_runtime_version_exchange_from_checkout.py`をstrict Evidence用の入口とします。

```bash
python3 runtime/integration/run_runtime_version_exchange_from_checkout.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --source-export-identity /path/to/new-source-export-identity.json \
  -- \
  --evidence-dir /path/to/new-evidence-directory
```

このentrypointはworking treeをharnessへ渡しません。固定commit objectからverified runtime bundleを生成し、内部で次の経路へ戻します。

```text
KJ Atlas Git repository
  ↓ fixed commit object
export_kj_atlas_runtime_source.py
  ↓ tracked runtime surface only
verify_kj_atlas_runtime_source.py
  ↓ verified runtime bundle
run_runtime_version_exchange.sh --kj-atlas-backend-bundle ...
```

生成したbundle自体も監査用に残す場合は、まだ存在しないpathを`--source-bundle-dir`で指定します。

```bash
python3 runtime/integration/run_runtime_version_exchange_from_checkout.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --source-bundle-dir /path/to/new-kj-atlas-runtime-bundle \
  --source-export-identity /path/to/new-source-export-identity.json \
  -- \
  --evidence-dir /path/to/new-evidence-directory
```

`--source-export-identity`は、checkoutからbundleを作った取得Provenanceを別JSONとして残すための任意指定です。既存file、KJ Atlas repository配下、verified runtime bundle配下はexport前に拒否します。

entrypointからharnessへ`--kj-atlas-dir`または別の`--kj-atlas-backend-bundle`を重ねて渡すことも拒否します。sourceの選択を一つに固定するためです。

### 事前にexportしたbundleを使う

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle \
  --evidence-dir /path/to/new-evidence-directory
```

固定runtime archiveとmodel storageを事前配置している場合は次のように指定します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-backend-bundle /path/to/new-kj-atlas-runtime-bundle \
  --runtime-a-archive /path/to/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory
```

`--model-dir`を指定した場合も、model tagだけでは受理しません。Ollama APIから観測したfull model digestが固定値と一致する必要があります。

既存model storageに固定artifactがなければ、harnessはそのdirectoryへ勝手に`ollama pull`せず停止します。harness自身が作るwork-local storageでは、固定artifactが存在しない場合に取得を試み、取得後に同じfull digestを検査します。

## pathとprocessの安全境界

`--work-dir`と`--evidence-dir`には、まだ存在しない新しいpathを指定します。

一つのEvidence directoryを一つのrunだけへ対応させることで、失敗した新runに前回runの後半ファイルが残り、一つの実行結果に見える状態を避けます。

work / Evidence / external model directoryはSOZAまたはKJ Atlas source配下へ置けません。実体pathへ正規化した後に判定します。

verified bundleをharnessへ渡した後も、外部入力をそのままbuild・実行しません。harness所有のwork directoryへ次の二つを分けてcopyし、双方を再検証します。

- execution source
- package install source

package buildが`*.egg-info`等を生成してもexecution sourceへ混ざらないようにするためです。

固定portを使うprocessは、起動前にportが空いていることを確認し、起動後もharness自身が開始したPIDの生存を確認します。別processのhealth responseを今回の実行identityへ取り込まないためです。

Go側artifact guardへ渡すsource mode、KJ Atlas execution source、source verifier、runtime archive、version logのpathはharnessがすべて明示します。`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしません。

## actual実行で確認すること

strict bundle経路のharnessは概ね次を一続きに確認します。

1. SOZA repositoryと入力pathの安全境界を確認する。
2. KJ Atlas verified bundleのGit object identityを確認する。
3. bundleをexecution sourceとpackage install sourceへ分け、双方を再検証する。
4. runtime A / B archiveを取得または事前配置pathから参照する。
5. A / Bのactual archive size / SHA-256を固定値と照合する。
6. archiveを別々のruntime rootへ展開する。
7. actual binary versionが`0.32.13` / `0.32.14`であることを確認する。
8. 両runtimeで同じ固定model artifact digestを確認する。
9. 同じMethod inputをKJ Atlasへ渡し、actual inference countersとresultを保存する。
10. A / Bのprompt SHA-256が同一であることを確認する。
11. live Go test直前にexecution sourceとruntime artifactを再確認する。
12. historical Application不変性、Exact Binding、portable reconstruction、negative controlを確認する。
13. 成否にかかわらず、そこまで得られたEvidenceをrun専用directoryへ保存する。

生成文そのものの一致はPASS条件ではありません。

## 軽量検査

actual runtimeやmodelを取得せず、source identity、preflight、harness interface、Go側guardの境界を次で確認できます。

```bash
python3 runtime/integration/test_verify_kj_atlas_runtime_source.py
python3 runtime/integration/test_export_kj_atlas_runtime_source.py
python3 runtime/integration/test_run_runtime_version_exchange_from_checkout.py
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
python3 runtime/integration/test_run_runtime_version_exchange.py
python3 runtime/integration/test_prepare_runtime_version_exchange_archives.py

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
- runtime archiveの固定size / digestと準備manifestの整合
- disk観測を容量充足証明へ昇格しないこと
- run単位のEvidence directory分離
- 事前配置model storageを暗黙更新しないこと

```text
lightweight boundary test PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- execution ID
- SOZA repository commit
- KJ Atlas source identity
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

checkoutからstrict entrypointを使った場合、`--source-export-identity`で保存したJSONは、固定commit objectからruntime bundleを取得した経路のProvenanceとしてEvidenceと併せて保管できます。この取得経路自体をMethod Realization identityには昇格させません。

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

このREADMEを、current no-Actions baseline、ISSUE-000070のrepository-local harness、固定runtime artifact、事前配置経路、preflight、KJ Atlas source identity、Evidence保存、成果品質評価境界へ戻って全文監査しました。

実験を動かす手順と、結果をどう評価できるかを一つの成功条件へまとめていません。特に、preflightの`ready`、archive size一致、disk空き容量、source export成功、harness interface testのPASSをactual runtime交換成立へ昇格させない構成にしています。

KJ Atlas sourceについては、通常のclean checkoutではignored `.env`等まで固定できないことを明示しました。strict Evidenceでは固定commit objectから追跡済みruntime surfaceだけをexportし、Git object identityを再検証します。checkoutを起点に実行する場合も専用entrypointを通し、working treeそのものをharnessへ渡しません。

runtime / model artifactでも、downloadか事前配置かという取得経路と、実際に使ったbytes / digestを分けています。事前配置したartifactも同じidentity検査へ通し、既存model storageを暗黙に更新しません。

actual Ollama `0.32.13` / `0.32.14`交換が未完了であることは変えていません。実装済みの安全策とactual A / BのNot Yet Verifiedを自然な日本語として読み分けられることを最重要視し、最終意味監査を行いました。
