# runtime integration probes

更新日: 2026-09-03

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

current `develop/v0.2.0`ではGitHub Actionsを停止しています。workflowの作成・復元・再実行・runner監視は行わず、必要なtest、checker、probeをローカルで個別に実行します。過去のActions Runはhistorical Evidenceとして保持しますが、現在の成立条件にはしません。

```text
what must be verified
  != where it is executed
```

## Runtime version exchange

ISSUE-000070では、同じCognitive Method、同じKJ Atlas source、同じMethod input、同じmodel artifact、同じmodel promptを使い、Ollama runtime versionだけを交換します。

固定条件は次のとおりです。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- KJ Atlas endpoint: `POST /ai/suggest-card-groups`
- model: `qwen2.5:0.5b`
- model artifact digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- revision A: Ollama `0.32.13`
- revision B: Ollama `0.32.14`

```text
same Method Definition
same logical Method Realization
same verified KJ Atlas runtime surface
same Method input
same pinned model artifact
same model prompt

runtime revision A != runtime revision B
```

確認したい中心命題は、runtime versionを交換しても先行Method ApplicationのExact Reference、Provenance、outputを変更せず保持できることです。

```text
runtime version exchange
  → new exact Realization revision
  != historical Application rewrite
```

## 固定runtime artifact

本probeはLinux / amd64用のOllama公式archiveを固定します。

| revision | official asset | size | SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesです。sizeは明らかなfile取り違えをSHA-256計算の前に拒否するための早期guardであり、artifact identityの正本ではありません。identityはactual bytesのSHA-256で固定します。

```text
archive size match
  != artifact identity verified
```

固定artifact metadataは`runtime_version_exchange_artifacts.json`に機械可読な形でも保持しています。

## 標準実行経路

strict Evidenceへ進む標準経路は次のとおりです。

```text
1. fixed runtime archiveを準備・再検証する
2. fixed KJ Atlas source identityを準備する
3. fixed model storeを既存storeから検証する、またはregistryから新規準備する
4. side-effect-free preflightを行う
5. strict entrypointから実行する
6. low-level repository-local harnessがactual processを動かす
7. actual /api/tagsとA/B inferenceを確認する
8. Evidenceを読み戻す
```

各工程の成功を、まだ実行していない後続工程の成功へ読み替えません。

## Runtime archiveの準備

取得前の計画確認:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives \
  --plan
```

固定archiveの準備:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives
```

既存fileだけをnetworkなしで再検証する場合:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives \
  --verify-only
```

準備toolはdownload中のbytesを`.part`へ書き、sizeとSHA-256が固定値に一致した場合だけ最終fileへ昇格します。既存fileや途中fileを暗黙に上書きしません。

```text
archive preparation success
  != actual Ollama A/B inference PASS
```

## KJ Atlas sourceの準備

strict Evidenceでは、通常のclean checkoutだけをbyte-completeなruntime source identityとはみなしません。ignored `.env`、binary extension、bytecode cache等を実行surfaceへ混入させないため、固定commit objectから追跡済みruntime surfaceをexportします。

対象は次の4要素です。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

明示的にverified bundleを作る場合:

```bash
python3 runtime/integration/export_kj_atlas_runtime_source.py \
  --checkout-dir /path/to/kj-atlas \
  --output-dir /path/to/new-kj-atlas-runtime-bundle
```

`verify_kj_atlas_runtime_source.py`は固定commit由来のblob / tree identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証します。

```text
source acquisition
  != source identity
```

strict入口へ`--kj-atlas-dir`を渡す場合は、入口自身が固定commit objectから一時verified bundleを作ります。既存のverified bundleは`--kj-atlas-backend-bundle`で渡せます。

## 固定model storeの検証と準備

### 既存storeを使う

既存のOllama model storeを使う場合は`verify_runtime_version_exchange_model_store.py`で静的に再検証できます。

```bash
python3 runtime/integration/verify_runtime_version_exchange_model_store.py \
  --model-dir /path/to/ollama-models
```

検証対象は次です。

- `qwen2.5:0.5b`の固定manifest path
- manifest raw bytesのSHA-256
- manifestが参照するconfig / layer blobのdeclared size
- 各参照blobのactual SHA-256
- symlinkやmodel store外参照がないこと

検証toolはmodel storeをread-only入力として扱い、`--output`もmodel store内へ書き込めません。

### registryから新しいstoreを準備する

固定model storeが手元にない場合は、`prepare_runtime_version_exchange_model_store.py`で`registry.ollama.ai`から新しいstoreを準備できます。

```bash
python3 runtime/integration/prepare_runtime_version_exchange_model_store.py \
  --target-dir /path/to/new-ollama-models
```

このtoolは固定manifest raw digestを最初に確認し、manifestが参照するblobをすべてsize / SHA-256で検証します。download中は同一filesystem上のstaging directoryを使い、全検証を通った場合だけ完成directoryへ昇格します。既存targetを上書きしません。失敗時は未完成stagingを除去します。

取得先はartifact manifestに固定した`registry.ollama.ai`のHTTPS endpointへ限定します。

```text
prepared model store PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

## ローカルpreflight

actual processを起動する前に、副作用のない診断を行えます。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas
```

runtime archiveとmodel storeをすべて事前配置した状態を確認する場合:

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

preflightはruntime / model processを起動せず、artifactもdownloadしません。host、必要コマンド、source identity、path、runtime archive identity、事前配置model store identity、local port、disk free bytesを診断します。

`--model-dir`を指定した場合、directoryが存在するだけでは`ready`にせず、固定manifestと全参照blobを静的に再検証します。

```text
static model store verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS

preflight ready
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Strict entrypoint

strict Evidenceの標準入口は`run_runtime_version_exchange_strict.py`です。

### 既存model storeを使う場合

```bash
python3 runtime/integration/run_runtime_version_exchange_strict.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory \
  -- \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst
```

### model storeも同時に新規準備する場合

```bash
python3 runtime/integration/run_runtime_version_exchange_strict.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --prepare-model-dir /path/to/new-ollama-models \
  --evidence-dir /path/to/new-evidence-directory \
  -- \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst
```

`--model-dir`と`--prepare-model-dir`は同時に指定できません。`--prepare-model-dir`は新しいpathだけを受け付けます。source identity確認後に固定storeを準備し、完成storeをもう一度静的verifierへ通してからlow-level harnessへ渡します。

strict入口は、source、model store、Evidence、work directoryを相互に分離します。Evidenceをmodel store配下へ置くなど、検証作業が入力artifactを変更できる配置は拒否します。custom work directoryはstrict入口自身の`--work-dir`で指定します。

harnessがEvidence directoryを作成した場合、該当する範囲で次も保存します。

- source export provenance
- model store preparation result
- static model store verification

```text
strict entrypoint verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

## Low-level repository-local harness

`run_runtime_version_exchange.sh`がactual A / B processを動かします。strict Evidenceでは原則としてstrict入口から利用します。

low-level harnessは次を一続きに確認します。

1. verified KJ Atlas source identity
2. runtime A / B archiveのactual size / SHA-256
3. actual binary version `0.32.13` / `0.32.14`
4. A / BそれぞれのOllama `/api/tags` full model digest
5. 同じMethod inputによるactual inference
6. A / Bのprompt SHA-256一致
7. Exact Bindingとhistorical Application不変性
8. portable reconstructionとnegative control
9. run専用Evidenceの保存

生成文そのものの一致はPASS条件ではありません。

## Pathとprocessの安全境界

- work / Evidenceには新しいpathを使う。
- source、model store、work、Evidenceを重ねない。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- fixed port `11434` / `8001` / `8101`の空きを確認する。
- health responseだけでなく、harness自身が起動したPIDの生存を確認する。
- Go live guardへ必要pathを明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。

## ローカルの軽量検査

actual runtimeを起動せず確認できる境界は個別に実行します。

```bash
python3 runtime/integration/test_prepare_runtime_version_exchange_archives.py
python3 runtime/integration/test_prepare_runtime_version_exchange_model_store.py
python3 runtime/integration/test_verify_runtime_version_exchange_model_store.py
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
python3 runtime/integration/test_runtime_version_exchange_preflight_model_store.py
python3 runtime/integration/test_run_runtime_version_exchange_strict.py
python3 runtime/integration/test_run_runtime_version_exchange_strict_model_preparation.py
python3 runtime/integration/test_run_runtime_version_exchange.py
```

```text
local helper test PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- execution ID
- SOZA repository commit
- KJ Atlas source identity / source export provenance
- model store preparation result
- static model store verification
- host OS / architecture
- runtime A / B version、expected / actual archive digest、acquisition mode
- model name、expected digest、storage mode、A / B `/api/tags`
- `qualityJudgement = not_evaluated`
- 固定Method request
- A / B inference Evidence / KJ Atlas result
- Adapter / KJ Atlas / Ollama log

```text
Evidence preserved
  != runtime exchange PASS
  != output quality satisfied
```

## 成果品質との境界

このprobeが確認するのはruntime交換に伴うexecution identityとhistorical reconstructionです。actual KJ Atlas outputの意味上の品質は`evaluation/method-quality/`で別に扱います。

```text
runtime exchange PASS
  != arbitrary runtime portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation correctness
  != Decision correctness
  != E4 Operational portability
```

実験の意味とResolution条件は`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。

## 自然な日本語レビュー

このREADMEをcurrent no-Actions baseline、固定runtime / source / model identity、artifact準備tool、preflight、strict entrypoint、low-level harness、Evidence保存、成果品質評価境界へ戻って全文再ドラフトしました。

特に、既存model storeを静的検証する経路と、固定registryから新しいmodel storeを準備する経路を分けました。新規準備では、取得したmanifest / blobを検証し終えるまで完成storeとして公開しません。それでも、準備成功はactual Ollama API観測ではありません。

actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedです。準備・静的検証・preflight・strict入口と、未完了のactual A / B実行を明確に読み分けられることを最重要視しています。
