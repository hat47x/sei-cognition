# runtime integration probes

更新日: 2026-09-03

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

## 何を別々に判定するか

本probeでは、準備、実行、Evidenceの機械検証、Requirement / Contractの判断、成果品質を一つのPASSへまとめません。

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

失敗時にEvidenceを保存することも同様です。

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

固定artifact metadataは`runtime_version_exchange_artifacts.json`に機械可読な形でも保持しています。

## 標準実行経路

actual runtime交換へ進む標準入口は`run_runtime_version_exchange_with_verification.py`です。各責務は別toolとして保ちながら、標準実行では次の順に接続します。

```text
1. fixed runtime archiveを準備・再検証する
2. KJ Atlasの固定commit objectを取得できるsource repository、またはverified bundleを用意する
3. fixed model storeを既存storeから検証する、またはregistryから新規準備できるようにする
4. verified runnerを起動する
5. side-effect-free preflightを実行する
6. preflight readyの場合だけstrict entrypointへ進む
7. strict entrypointがsource / model / path境界を固定する
8. low-level harnessがactual A/B processを動かす
9. actual /api/tagsとA/B inferenceを確認する
10. run Evidenceとrunner observationを保存する
11. Evidence + Provenance verifierで保存済みrunを独立再検証する
12. Requirement / Contract再照合と成果品質評価へ進む
```

preflightやstrict executionが途中で失敗した場合も、作成可能な範囲のEvidenceを残します。ただし、未実行の後続工程を成立扱いにはしません。

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

## KJ Atlas sourceの準備

strict Evidenceでは、通常のworking treeをそのままruntime sourceとして信用しません。ignored `.env`、binary extension、bytecode cache等を実行surfaceへ混入させないため、固定commit objectから追跡済みruntime surfaceをexportします。

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

`verify_kj_atlas_runtime_source.py`は固定commit由来のGit object identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証します。

```text
source acquisition
  != source identity
```

`--kj-atlas-dir`をverified runnerまたはstrict入口へ渡す場合、checkoutは固定commit objectの取得元として扱われます。実際のruntime sourceは、そこから作ったverified bundleです。既存のverified bundleは`--kj-atlas-backend-bundle`で渡せます。

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

検証toolはmodel storeをread-only入力として扱います。

### registryから新しいstoreを準備する

```bash
python3 runtime/integration/prepare_runtime_version_exchange_model_store.py \
  --target-dir /path/to/new-ollama-models
```

このtoolはartifact manifestに固定した`registry.ollama.ai`のHTTPS endpointだけを利用します。固定manifest raw digestを確認し、参照blobをすべてsize / SHA-256で検証します。download中は同一filesystem上のstaging directoryを使い、全検証を通った場合だけ完成directoryへ昇格します。既存targetは上書きしません。

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

runtime archiveとmodel storeをすべて事前配置した状態を確認する場合:

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

preflightはhost、必要コマンド、固定commit objectの取得可能性またはverified source bundle、path、runtime archive identity、事前配置model store identity、local port、disk free bytesを診断します。checkoutの現在HEADやignored fileをstrict runtime source identityとはみなしません。

手動preflightは事前診断です。actual実行の標準runnerは同じpreflightを実行直前に必ず再実行します。

### preflightがblockedの場合

構造化された`blocked`結果を返した場合、verified runnerはstrict入口、model preparation、runtime取得を開始しません。そのrun専用Evidence directoryをblocked判定後に作り、次を保存します。

- `runtime-exchange-preflight.json`
- `runtime-exchange-preflight-observation.json`
- Evidence + Provenance verification report（Evidence directoryの外）

preflight observationには`strictStarted=false`を記録します。runnerの終了状態はnon-zeroのままです。

JSON自体を解釈できない等、構造化preflightとして扱えない異常ではEvidenceを捏造せず通常エラーとして停止します。

```text
blocked preflight Evidence preserved
  != strict execution started
  != runtime exchange PASS
```

## Strict entrypoint

`run_runtime_version_exchange_strict.py`はsource / model / pathのstrict境界を担います。actual実行では通常、verified runnerから利用します。

既存model storeを使う例:

```bash
python3 runtime/integration/run_runtime_version_exchange_strict.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory \
  -- \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst
```

model storeも新規準備する場合は、`--model-dir`の代わりに`--prepare-model-dir /path/to/new-ollama-models`を指定します。両者は同時指定できません。

strict入口は次を行います。

1. checkoutを指定した場合、固定commit objectからverified bundleをexportする。
2. bundleを指定した場合、その固定Git object identityを再検証する。
3. 既存model storeを指定した場合、manifest / blob bytesを静的再検証する。
4. modelを新規準備する場合、固定registryから取得し、完成storeを再検証する。
5. source、model store、Evidence、work directoryの重なりを拒否する。
6. identity / safety optionをlow-level harnessへ迂回上書きさせない。
7. verified bundleだけをlow-level harnessへ渡す。

strict入口によるsource exportやmodel準備・検証のProvenanceは、Evidence directoryが作られた範囲で保存します。

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

strict processが失敗し、その時点でEvidence directoryがまだ作られていない場合は、process終了後にverified runnerが新しいEvidence directoryを作成し、少なくとも次を残します。

- successful preflight report
- runner combined output log
- runner exit code / log SHA-256 / bytes
- source preparation mode
- `evidenceDirectoryCreatedBy=verified-runner-after-failure`
- Evidence + Provenance verification report

strict入口またはlow-level harnessがすでにEvidence directoryを作っていた場合は`evidenceDirectoryCreatedBy=strict-entrypoint`を記録します。

反対に、strict processがexit code 0なのにEvidence directoryを作らなかった場合は成功として扱いません。Evidenceの欠落そのものをエラーとして停止します。

```text
strict process exit 0
  + Evidence directory missing
  = reject
```

失敗runに対してもpost-run verifierを実行しますが、元のstrict exit codeはnon-zeroのまま保持します。verification reportが作られたことを実行成功には読み替えません。

## 保存済みEvidenceを再検証する

### Evidence + Provenanceの標準検証

標準の独立再検証は`verify_runtime_version_exchange_provenance.py`を使います。

```bash
python3 runtime/integration/verify_runtime_version_exchange_provenance.py \
  --evidence-dir /path/to/evidence-directory \
  --output /path/to/new-verification.json
```

このverifierは、core execution Evidenceの検証に加えて次を再検証します。

- 保存済みpreflightが`ready`であり、blockerがないこと
- preflightのfixed artifact条件がcurrent artifact manifestと一致すること
- preflightのpinned source identityがcurrent固定値と一致すること
- checkout起点の場合、fixed commit objectからのsource export Provenanceがactual source identityと一致すること
- verified bundle直入力の場合、checkout source-export fileが混入していないこと

完全なrunだけが`ready-to-review`になり得ます。blocked preflightや途中失敗のpartial Evidenceは、保存されていても`not-sufficient`です。

### core mechanical verifier

`verify_runtime_version_exchange_evidence.py`はcore execution条件だけを検証する下位verifierです。主な対象は次です。

- fixed KJ Atlas runtime source identity
- runtime A / Bのactual versionとarchive SHA-256
- A / Bそれぞれの`/api/tags` fixed model full digest
- fixed 3-card Method inputとheld card
- same prompt SHA-256
- `ollama_done=true`、`prompt_eval_count>0`、`eval_count>0`
- KJ Atlas resultの最低限の構造境界
- runner exit code、completion marker、combined log SHA-256 / bytes
- `qualityJudgement=not_evaluated`

生成文の内容一致や成果品質は、どちらのmechanical verifierにも含めません。

```text
Evidence + Provenance verification ready-to-review
  != Requirement / Contract assessment complete
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != ISSUE-000070 Resolved
```

## Low-level repository-local harness

`run_runtime_version_exchange.sh`がactual A / B processを動かします。現在はverified KJ Atlas backend bundleを必須とし、direct checkoutを受け付けません。checkout起点ではverified runnerまたはstrict入口で固定commit objectからbundleへ変換してから利用します。

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

- source、model store、work、Evidence、verification outputを相互に分離する。
- work / Evidence / verification outputには新しいpathを使う。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- Evidenceをmodel storeやsource配下へ書かない。
- fixed port `11434` / `8001` / `8101`の空きをpreflightとactual harnessで確認する。
- health responseだけでなく、harness自身が起動したPIDの生存を確認する。
- Go live guardへ必要pathを明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。
- verification outputをEvidence directory内へ置かず、検証結果で検証対象そのものを変更しない。

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
python3 runtime/integration/test_run_runtime_version_exchange_with_verification.py
python3 runtime/integration/test_runtime_version_exchange_blocked_preflight_evidence.py
python3 runtime/integration/test_verify_runtime_version_exchange_evidence.py
python3 runtime/integration/test_verify_runtime_version_exchange_provenance.py
python3 runtime/integration/test_runtime_version_exchange_provenance_wiring.py
```

```text
local helper test PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Evidenceの読み方

runの進行度によって、Evidence directoryに存在するfileは異なります。

### preflightでblockedしたrun

少なくとも次を保存します。

- `runtime-exchange-preflight.json`
- `runtime-exchange-preflight-observation.json`

strict executionは開始していないため、runner observationやA/B actual Evidenceは存在しません。これは欠落ではなく、そのrunがpreflightで停止したことを表します。ただしcomplete Evidenceではないため、verifier resultは`not-sufficient`です。

### strict開始後に失敗したrun

可能な範囲で次を保存します。

- successful preflight report
- runner combined output log
- runner observation
- strict入口が作成済みだったsource / model Provenance
- low-level harnessが生成済みだった途中Evidence

strictがEvidence directory作成前に失敗しても、verified runnerが失敗後にdirectoryを作ってrunner logとobservationを保存します。

### complete run

上記に加えて、次へ戻れることが必要です。

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

このREADMEを、current no-Actions baseline、固定runtime / source / model identity、artifact準備、preflight、strict entrypoint、bundle-only low-level harness、failure Evidence保存、core Evidence verifier、Provenance verifier、成果品質評価境界へ戻って全文再監査しました。

現在は、preflightで止まったrun、strict開始後に止まったrun、complete runを同じ「成功／失敗」の二値へ押し込まず、どこまで進んだかをEvidenceから読める構成にしています。失敗情報を残すことと、実証が成立したと判断することは明確に分けています。

また、checkoutは固定commit objectの取得元として利用できますが、low-level harnessへworking treeを直接渡す経路は廃止しました。strict Evidenceで実行するsourceは、固定Git object identityを再検証したruntime bundleです。

保存済みrunの標準検証は、core execution条件に加えてpreflightとsource acquisitionまで見る`verify_runtime_version_exchange_provenance.py`としました。core verifierは独立した下位境界として残し、双方のPASSをRequirement / Contract判断や成果品質へ自動昇格させません。

actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedです。実装済みの準備・安全策・失敗Evidence保存と、未完了のactual A/B実行を自然な日本語として明確に読み分けられることを最重要視しています。
