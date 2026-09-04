# runtime integration probes

更新日: 2026-09-04

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

current `develop/v0.2.0`ではGitHub Actionsを停止しています。workflowの作成・復元・再実行・runner監視は行わず、必要なtest、checker、probeをrepository-localに実行します。過去のActions Runはhistorical Evidenceとして保持しますが、現在の成立条件にはしません。

```text
what must be verified
  != where it is executed
```

## Runtime version exchange

ISSUE-000070では、同じCognitive Method、同じKJ Atlas source、同じMethod input、同じmodel artifact、同じmodel promptを使い、Ollama runtime versionだけを交換します。

固定条件は次のとおりです。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- parent backend tree: `7d71ac2b4d32bef90f3a481ade1b4c92ddddd084`
- runtime surface tree: `208bea71eef4afed3ddfd3fabb36b0969d167a90`
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

## 判定を分離する

準備、preflight、strict実行、Evidence検証、Requirement / Contract判断、成果品質を一つのPASSへまとめません。

```text
artifact preparation PASS
  != preflight ready

preflight ready
  != strict execution PASS

strict execution PASS
  != Evidence + Provenance verification PASS

Evidence + Provenance verification PASS
  != ISSUE-000070 Resolved
  != model output quality satisfied
  != KJ-method outcome quality satisfied
```

失敗情報を保存できたことも、runtime交換の成立とは別です。

```text
failure Evidence preserved
  != runtime exchange PASS
```

## 固定runtime artifact

本probeはLinux / amd64用のOllama公式archiveを固定します。

| revision | official asset | size | SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesです。sizeは明らかなfile取り違えをSHA-256計算の前に拒否する早期guardであり、artifact identityの正本ではありません。identityはactual bytesのSHA-256で固定します。

固定metadataは`runtime_version_exchange_artifacts.json`へ機械可読に保持します。manifest loaderはruntime名、version、Linux / amd64 platform、size、SHA-256、asset名、対応versionのOllama公式GitHub Release URLを検証します。

`check_runtime_version_exchange_manifest_consistency.py`は、このartifact manifestとpreflight、low-level harness、Go側の固定値が同じidentityを参照していることを横断確認します。`runtime_version_exchange_official_release_snapshot.json`には、GitHub Release APIから確認した公式Release側の観測を保存します。Release snapshotは取得元の監査材料であり、actual archive bytesの代わりにはしません。

```text
official acquisition origin
  = acquisition boundary / Provenance
  != artifact identity

artifact identity
  = actual bytes / fixed SHA-256
```

## 標準実行経路

actual runtime交換へ進む標準入口は`run_runtime_version_exchange_with_verification.py`です。

```text
1. fixed runtime archiveをrepository外へ準備・再検証する
2. KJ Atlasの固定commit objectを取得できるrepository、またはverified bundleを用意する
3. fixed model storeを既存storeから検証する、またはregistryから新規準備できるようにする
4. verified runnerを起動する
5. side-effect-free preflightを実行する
6. preflight readyの場合だけstrict entrypointへ進む
7. strict entrypointがsource / runtime archive / model / work / Evidence境界を固定する
8. low-level harnessがactual A/B processを動かす
9. actual `/api/tags`とA/B inferenceを確認する
10. run Evidenceとrunner observationを保存する
11. Evidence + Provenance verifierで保存済みrunを独立再検証する
12. Requirement / Contract再照合と成果品質評価へ進む
```

preflightやstrict executionが途中で失敗した場合も、作成可能な範囲のEvidenceを残します。ただし、未実行の後続工程を成立扱いにはしません。

## Runtime archiveの準備

runtime archiveはSOZA repositoryの外に置きます。計画表示の段階から同じ出力先境界を適用します。

取得前の計画確認:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/outside/soza/runtime-archives \
  --plan
```

固定archiveの準備:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/outside/soza/runtime-archives
```

既存fileだけをnetworkなしで再検証する場合:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/outside/soza/runtime-archives \
  --verify-only
```

準備toolは次を停止線にします。

- `--output-dir`をSOZA repository配下へ置かない。
- output directory自身がsymlinkなら拒否する。
- 既存output pathが通常directoryでなければ拒否する。
- 既存archive targetがsymlinkなら拒否する。
- `.part`を暗黙に再利用・上書きしない。
- `.part`がsymlinkなら拒否する。
- download中は`.part`へ書き、sizeとSHA-256が固定値に一致した場合だけ最終fileへ昇格する。

準備済みarchiveをactual実行へ渡す場合も、preflightとstrict入口がsource treeとの分離、symlink、regular file、固定size / SHA-256を再確認します。strict入口は重いsource exportやmodel準備より前に、事前配置archiveのactual bytesを固定manifestへ照合します。

## KJ Atlas sourceの準備

strict Evidenceではworking treeをruntime sourceとして直接信用しません。ignored `.env`、binary extension、bytecode cache等を実行surfaceへ混入させないため、固定commit objectから追跡済みruntime surfaceだけをexportします。

対象は次です。

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

`verify_kj_atlas_runtime_source.py`は固定commit由来のGit object identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証します。verifierの結果fileは入力bundleの外へ出し、検証自身が入力sourceを変更しないようにします。exporterのidentity出力もcheckoutや完成bundleから分離します。

source exporterは、tarの一時展開先を最終bundleと同じ側のparentへ置き、親processの`TMPDIR`を一時source配置へ使いません。copyや最終identity検証の途中で失敗した場合は未完成のoutput bundleを除去し、「存在するが未検証」のsource artifactを残しません。

```text
source acquisition
  != source identity
```

`--kj-atlas-dir`をverified runnerまたはstrict入口へ渡す場合、checkoutは固定commit objectの取得元として扱われます。実際のruntime sourceは、そこから作ったverified bundleです。既存verified bundleは`--kj-atlas-backend-bundle`で渡せます。

low-level harness `run_runtime_version_exchange.sh`はverified bundle専用です。direct checkoutや暗黙の`_external/kj-atlas` fallbackは持ちません。

## 固定model storeの検証と準備

### 既存storeを使う

```bash
python3 runtime/integration/verify_runtime_version_exchange_model_store.py \
  --model-dir /path/to/ollama-models
```

主な検証対象は次です。

- `qwen2.5:0.5b`の固定manifest path
- manifest raw bytesのSHA-256
- manifestが参照するconfig / layer blobのdeclared size
- 各参照blobのactual SHA-256
- symlinkやmodel store外参照がないこと

検証toolはmodel storeをread-only入力として扱います。結果fileをmodel store配下へ書き込むことも拒否します。

### registryから新しいstoreを準備する

```bash
python3 runtime/integration/prepare_runtime_version_exchange_model_store.py \
  --target-dir /path/to/new-ollama-models
```

このtoolはartifact manifestに固定した`registry.ollama.ai`のHTTPS endpointだけを利用します。固定manifest raw digestを確認し、参照blobをsize / SHA-256で検証します。download中はstaging directoryを使い、全検証を通った場合だけ完成directoryへ昇格します。既存targetは上書きしません。

```text
prepared model store PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

## ローカルpreflight

actual processを起動せず、副作用のない診断だけを単独で行えます。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas
```

すべて事前配置した状態を確認する場合:

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

preflightはhost、必要コマンド、固定commit objectの取得可能性またはverified source bundle、path、runtime archive identity、事前配置model store identity、local port、disk free bytesを診断します。checkoutの現在HEADやignored fileをstrict runtime source identityとはみなしません。

事前配置runtime archiveは、固定size / SHA-256の前にsource tree配下にないこととsymlinkでないことを確認します。model storeとsourceは一方向だけでなく、互いを包含する配置も拒否します。

手動preflightは事前診断です。標準verified runnerはactual実行直前に同じpreflightを再実行します。

### preflightがblockedの場合

構造化された`blocked`結果を返した場合、verified runnerはstrict入口、model preparation、runtime取得を開始しません。blocked判定後にrun専用Evidence directoryを作り、次を保存します。

- `runtime-exchange-preflight.json`
- `runtime-exchange-preflight-observation.json`
- Evidence + Provenance verification report（Evidence directoryの外）

preflight observationには`strictStarted=false`を記録し、runnerはnon-zeroのまま終了します。JSON自体を解釈できない等、構造化preflightとして扱えない異常ではEvidenceを推測で作らず通常エラーとして停止します。

## Strict entrypoint

`run_runtime_version_exchange_strict.py`はsource / runtime archive / model / work / Evidenceのstrict境界を担います。actual実行では通常verified runnerから利用します。

```bash
python3 runtime/integration/run_runtime_version_exchange_strict.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory \
  -- \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst
```

model storeも新規準備する場合は`--model-dir`の代わりに`--prepare-model-dir`を指定します。

strict入口は次を行います。

1. checkout指定時は固定commit objectからverified bundleをexportする。
2. bundle指定時は固定Git object identityを再検証する。
3. 事前配置runtime archiveのsymlink、不存在、source/SOZA/modelとのoverlap、A/B同一pathを拒否する。
4. 事前配置runtime archiveのactual size / SHA-256を固定manifestへ照合する。
5. 既存model storeはmanifest / blob bytesを静的再検証する。
6. model新規準備時は固定registryから取得し、完成storeを再検証する。
7. source、model store、Evidence、workの双方向overlapを拒否する。
8. identity / safety optionをlow-level harnessへ迂回上書きさせない。
9. verified bundleだけをlow-level harnessへ渡す。

`--work-dir`を省略しても親processの`TMPDIR`へ委ねません。Evidence directoryと同じparentへ`<evidence-name>-work`を新規pathとして決め、low-level harnessの`--work-dir`とchild環境の`TMPDIR`へ同じpathを明示します。

checkout起点の一時verified source bundleも`<evidence-name>-source/backend`へ明示配置し、親`TMPDIR`を使いません。この一時source rootはrun終了後に削除し、source export ProvenanceだけをEvidenceへ保存します。

## 実行と独立再検証を一続きに行う

標準入口:

```bash
python3 runtime/integration/run_runtime_version_exchange_with_verification.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory \
  --verification-output /path/to/new-verification.json \
  -- \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst
```

model storeを新規準備する場合は`--prepare-model-dir`を使います。既存verified source bundleを使う場合は`--kj-atlas-backend-bundle`を指定します。

preflightが`ready`ならstrict入口を起動します。strict実行のstdout/stderrは一つのrunner logへ集約し、SHA-256とbytesをrunner observationへ保存します。

strict processが失敗しEvidence directoryがまだ無い場合は、process終了後にverified runnerが新しいEvidence directoryを作成し、successful preflight、combined log、exit code、log SHA-256 / bytes、source preparation modeを残します。strict入口またはlow-level harnessが既にEvidence directoryを作っていた場合は`evidenceDirectoryCreatedBy=strict-entrypoint`を記録します。

strict processがexit code 0なのにEvidence directoryを作らなかった場合は成功扱いしません。

```text
strict process exit 0
  + Evidence directory missing
  = reject
```

失敗runに対してもpost-run verifierを実行しますが、元のnon-zero exit codeは保持します。

## 保存済みEvidenceの再検証

### Evidence + Provenanceの標準検証

```bash
python3 runtime/integration/verify_runtime_version_exchange_provenance.py \
  --evidence-dir /path/to/evidence-directory \
  --output /path/to/new-verification.json
```

標準verifierはcore execution Evidenceに加えて次を再検証します。

- saved preflightが`ready`でblockerがないこと
- saved fixed artifact条件がcurrent artifact manifestと一致すること
- pinned source identityがcurrent固定値と一致すること
- checkout起点ならsource export Provenanceがactual source identityと一致すること
- verified bundle直入力ならcheckout source-export fileが混入していないこと
- complete runのEvidence directoryがstrict入口側で作られたこと
- Evidence directory自身と必須Evidence fileがsymlinkでないこと

complete runだけが`ready-to-review`になり得ます。blocked preflightや途中失敗のpartial Evidenceは`not-sufficient`です。

### core mechanical verifier

`verify_runtime_version_exchange_evidence.py`はcore execution条件を検証する下位verifierです。

主な対象:

- fixed KJ Atlas runtime source identity
- runtime A / B actual version / archive SHA-256
- A / B `/api/tags` fixed model full digest
- fixed 3-card Method input / held card
- same prompt SHA-256
- `ollama_done=true`、`prompt_eval_count>0`、`eval_count>0`
- KJ Atlas resultの最低限の構造境界
- runner exit code、completion marker、combined log SHA-256 / bytes
- `qualityJudgement=not_evaluated`

生成文の内容一致や成果品質はmechanical verifierの対象にしません。

## Low-level repository-local harness

`run_runtime_version_exchange.sh`がactual A / B processを動かします。verified KJ Atlas backend bundleを必須とし、direct checkoutを受け付けません。

low-level harnessは次を一続きに確認します。

1. verified KJ Atlas source identity
2. runtime A / B archive actual SHA-256
3. actual binary version `0.32.13` / `0.32.14`
4. A / B `/api/tags` full model digest
5. 同じMethod inputによるactual inference
6. A / B prompt SHA-256一致
7. Exact Bindingとhistorical Application不変性
8. portable reconstructionとnegative control
9. run専用Evidence保存

生成文そのものの一致はPASS条件ではありません。標準Evidenceではlow-level harnessを直接呼ばず、preflightとstrict入口を含むverified runnerから利用します。

## Pathとprocessの安全境界

- source、runtime archive、model store、work、Evidence、verification outputを意図しない形で重ねない。
- runtime archive準備先はSOZA repository外とする。
- 事前配置runtime archiveはpreflightとstrict入口でsource treeとの分離とactual bytesを再確認する。
- model storeとsourceは双方向の包含を拒否する。
- work / Evidence / verification outputには新しいpathを使う。
- strict入口はworkとcheckout起点の一時source bundleを親`TMPDIR`から分離する。
- source exporterの一時展開もoutput bundle側へ固定し、途中失敗時はpartial bundleを残さない。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- Evidenceをmodel storeやsource配下へ書かない。
- source/model verifierの結果fileを入力資産の内部へ書かない。
- fixed port `11434` / `8001` / `8101`の空きをpreflightとactual harnessで確認する。
- health responseだけでなくharness自身が起動したPIDの生存を確認する。
- Go live guardへ必要pathを明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。
- verification outputをEvidence directory内へ置かない。

## ローカルのfocused regression

actual runtimeを起動せず、ISSUE-000070周辺のrepository-local regressionをまとめる標準入口は`run_runtime_version_exchange_local_checks.py`です。

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py
```

最初の失敗で止める場合:

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py \
  --stop-on-failure
```

登録済みtestを確認する場合:

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py --list
```

特定testだけを実行する場合:

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py \
  --only test_export_kj_atlas_runtime_source.py \
  --only test_runtime_version_exchange_strict_archive_boundaries.py
```

機械可読な結果をrepository外へ保存する場合:

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py \
  --result-output /path/outside/soza/runtime-exchange-focused-result.json
```

各testの既定timeoutは120秒です。必要なら`--timeout-seconds`で変更できます。timeoutはexit code `124`、child起動自体の失敗はexit code `127`相当としてmachine-readable resultへ残します。`--stop-on-failure`はnon-zero、timeout、launch errorのいずれでも停止できます。

runnerは明示allowlistとcandidate discoveryを照合し、runtime version exchangeに関係するtestが未登録のまま増えることを検出します。runner自身のself-testもfocused checkへ含めます。

親shellの`SOZA_RUNTIME_EXCHANGE_*`、`SOZA_E3B_RUNTIME_EXCHANGE_*`、`OLLAMA_HOST`、`OLLAMA_MODELS`はfocused regressionへ暗黙継承しません。

結果JSONはrepository commit / cleanlinessの観測とtest resultを分けます。Git観測に失敗しても、その失敗をtest PASSへ偽装せず診断情報として保持します。結果には次の停止線を明示します。

- `actualRuntimeExchangeEvidence=false`
- `qualityJudgement=not_evaluated`

```text
focused local checks PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

### preflightでblockedしたrun

少なくとも次を保存します。

- `runtime-exchange-preflight.json`
- `runtime-exchange-preflight-observation.json`

strict executionは開始していないため、runner observationやA/B actual Evidenceは存在しません。complete Evidenceではなく、verifier resultは`not-sufficient`です。

### strict開始後に失敗したrun

可能な範囲で次を保存します。

- successful preflight report
- runner combined output log
- runner observation
- strict入口が作成済みだったsource / model Provenance
- low-level harnessが生成済みだった途中Evidence

strictがEvidence directory作成前に失敗しても、verified runnerが失敗後にdirectoryを作ってrunner logとobservationを保存します。

### complete run

少なくとも次へ戻れることが必要です。

- execution ID / SOZA repository commit
- verified KJ Atlas source identity / source acquisition Provenance
- runtime A / B actual version / archive SHA-256
- model name / expected digest / storage mode / A/B `/api/tags`
- fixed Method request
- A / B inference Evidence / KJ Atlas result
- model prompt SHA-256
- Exact Binding / historical Application再構成に必要なEvidence
- `qualityJudgement=not_evaluated`

mechanical verification reportはEvidence directoryの外へ保存します。

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

current no-Actions baseline、固定runtime / source / model identity、artifact manifest横断整合、公式Release snapshot、runtime archiveのrepository外準備、source export、model store、preflight、strict entrypoint、failure Evidence、core / Provenance verifier、focused local runnerへ戻って全文を再監査しました。

現在は、取得元、actual bytes、実行source、作業path、Evidence、成果品質を別の概念として扱っています。artifactの取得経路や配置場所をidentityの代わりにはせず、固定bytes / Git objectへ戻って検証します。

source acquisitionではworking treeを直接実行せず、固定commit objectからverified bundleを作ります。一時展開やstrict内部の一時bundleも親`TMPDIR`へ委ねず、明示した安全側のpathへ置きます。export途中に失敗した場合はpartial bundleを完成artifactとして残しません。

GitHub Actionsを使わない現在の開発では、actual A/Bを起動しないfocused regressionを専用runnerへ集約し、timeout、launch error、Git観測、machine-readable resultまで保存できるようにしています。ただし、そのPASSをactual runtime exchange Evidenceへ昇格しません。

actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedです。実装済みの準備・安全策・failure Evidence・focused regressionと、未完了のactual A/B実行を明確に読み分けられることを最重要視しています。