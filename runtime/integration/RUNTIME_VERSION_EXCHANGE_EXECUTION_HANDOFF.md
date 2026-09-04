# Runtime Version Exchange — Actual A/B Execution Handoff

更新日: 2026-09-05  
対象: ISSUE-000070

## 目的

この文書は、Ollama `0.32.13` / `0.32.14` のactual runtime交換を、取得工程と実行工程を分離して行うための最短handoffです。

ここで準備するのは固定artifactだけです。準備成功をactual inference、historical reconstruction、成果品質、E4 Operational portabilityの成立へ読み替えません。

現在どこまで実装され、どこからが未検証かを先に確認する場合は、`RUNTIME_VERSION_EXCHANGE_CURRENT_STATE.md`を参照します。意味上のGoalとResolution Criteriaは`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。

## 1. 前提

actual runtime archiveはLinux / amd64固定です。SOZAとKJ AtlasはcleanなGit checkoutを利用し、KJ Atlas checkoutには固定commit object `4f28c13abe4176503c6fed863383a2d1db2299e9` が存在する必要があります。

artifact、Evidence、workはSOZA / KJ Atlas repository外へ置きます。

以下では例として同じ外部parentを利用します。

```bash
export SOZA_RUNTIME_EXCHANGE_ROOT="$HOME/soza-runtime-exchange"
export SOZA_RUNTIME_EXCHANGE_INPUTS="$SOZA_RUNTIME_EXCHANGE_ROOT/inputs"
export SOZA_RUNTIME_EXCHANGE_EVIDENCE="$SOZA_RUNTIME_EXCHANGE_ROOT/evidence-$(date -u +%Y%m%dT%H%M%SZ)"
export SOZA_RUNTIME_EXCHANGE_VERIFY="$SOZA_RUNTIME_EXCHANGE_EVIDENCE-verification.json"
```

`$SOZA_RUNTIME_EXCHANGE_INPUTS`は再利用可能な固定artifact置き場です。Evidenceとverification outputはrunごとに新しいpathを使います。

## 2. 固定runtime A/B archiveとmodel storeを先に準備する

```bash
python3 runtime/integration/prepare_runtime_version_exchange_inputs.py \
  --root "$SOZA_RUNTIME_EXCHANGE_INPUTS"
```

この入口は既存helperを順に利用します。

- Ollama `0.32.13` / `0.32.14` official Linux/amd64 archiveを固定size / SHA-256で準備または再検証する。
- `qwen2.5:0.5b`の固定Ollama manifest / blobを準備または再検証する。
- 既に正しいartifactが存在する場合は再利用する。
- runtime process、KJ Atlas process、actual inferenceは開始しない。

成功時JSONの`verifiedRunnerInputs`に、次のactual runへ渡す3 pathと`requirePrepositionedArtifacts=true`が出ます。

```text
modelDir
runtimeAArchive
runtimeBArchive
requirePrepositionedArtifacts
```

既存artifactをnetworkなしで再確認する場合:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_inputs.py \
  --root "$SOZA_RUNTIME_EXCHANGE_INPUTS" \
  --verify-only
```

## 3. 標準入口からactual A/Bを実行する

事前配置済みrootからactual実行へ進む標準入口は`run_runtime_version_exchange_prepositioned.py`です。

```bash
python3 runtime/integration/run_runtime_version_exchange_prepositioned.py \
  --artifact-root "$SOZA_RUNTIME_EXCHANGE_INPUTS" \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir "$SOZA_RUNTIME_EXCHANGE_EVIDENCE" \
  --verification-output "$SOZA_RUNTIME_EXCHANGE_VERIFY"
```

この入口はactual processを開始する前に、`prepare_runtime_version_exchange_inputs.py --verify-only`と同じ固定artifact再検証を行います。その結果からmodel store、runtime A、runtime Bのpathを取得し、`--require-prepositioned-artifacts`を付けて標準verified runnerへ委譲します。

利用者がA/B archive file名やmodel pathを手で再構成しないことを目的とします。runtime / model identityの検証規則を新しく持たず、既存helperとverified runnerへ戻します。

```text
prepositioned root
  → static fixed-artifact verification
  → verified runner
  → side-effect-free preflight
  → strict entrypoint
  → actual A/B
  → Evidence + Provenance verification
```

既存verified KJ Atlas runtime bundleから開始する場合は、`--kj-atlas-dir`の代わりに`--kj-atlas-backend-bundle`を指定できます。

## 4. 手動preflightとverified runnerを使う場合

標準入口がblockedしたときに個々のpathやpreflight結果を診断する場合は、下位入口を直接利用できます。

### 副作用なしpreflight

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive "$SOZA_RUNTIME_EXCHANGE_INPUTS/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst" \
  --runtime-b-archive "$SOZA_RUNTIME_EXCHANGE_INPUTS/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst" \
  --model-dir "$SOZA_RUNTIME_EXCHANGE_INPUTS/ollama-models" \
  --evidence-dir "$SOZA_RUNTIME_EXCHANGE_EVIDENCE" \
  --require-prepositioned-artifacts \
  --json
```

`result=ready`になったことを確認します。blockedの場合はactual processを開始せず、blockerを解消します。

### verified runner

```bash
python3 runtime/integration/run_runtime_version_exchange_with_verification.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --model-dir "$SOZA_RUNTIME_EXCHANGE_INPUTS/ollama-models" \
  --evidence-dir "$SOZA_RUNTIME_EXCHANGE_EVIDENCE" \
  --verification-output "$SOZA_RUNTIME_EXCHANGE_VERIFY" \
  --require-prepositioned-artifacts \
  -- \
  --runtime-a-archive "$SOZA_RUNTIME_EXCHANGE_INPUTS/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst" \
  --runtime-b-archive "$SOZA_RUNTIME_EXCHANGE_INPUTS/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst"
```

標準verified runnerは実行直前にもpreflightを再実行します。したがって手動preflightとactual runの間で状態が変化した場合も、そのままstrict実行へ進めません。

## 5. 完了判定

process exit code 0だけでは完了扱いにしません。verification outputが`ready-to-review`となり、ISSUE-000070のResolution Criteriaに沿って少なくとも次を確認します。

- runtime A actual binary version = `0.32.13`
- runtime B actual binary version = `0.32.14`
- A/B archive actual SHA-256が固定値と一致
- A/B `/api/tags`のmodel digestが同一固定値と一致
- A/BでMethod inputとprompt SHA-256が同一
- A/Bでactual inferenceが成立
- runtime revisionだけが異なるExact Bindingとして記録される
- B追加後もAのMethod Application / Provenance / outputが変化しない
- portable reconstructionがA/B両方を当時のbasisで再構成できる
- Recommendation / Decisionへの意味昇格が起きていない

その後にRequirement / Contractと照合し、自然な日本語とProduct Valueの観点から人間レビューを行います。

```text
artifact preparation PASS
  != preflight ready
  != actual A/B inference PASS
  != verifier ready-to-review
  != ISSUE-000070 Resolved
  != outcome quality Satisfied
  != E4 Operational portability
```

## 6. repository-local orchestration test

事前配置入力準備と上位runnerの接続だけをactual networkなしで検査する場合:

```bash
python3 runtime/integration/test_issue70_prepositioned_inputs.py
python3 runtime/integration/test_issue70_prepositioned_runner.py
```

これらのtestは取得helperそのもののdigest検査やactual A/B実行を置き換えません。既存archive/model helper testに加えて、準備入口が新規準備・既存再利用・verify-onlyを正しく委譲すること、上位runnerが固定artifact pathを取り違えずverified runnerへ渡すことを検査します。
