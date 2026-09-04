# Runtime Version Exchange — Current Execution State

更新日: 2026-09-05  
対象: ISSUE-000070

## この文書の役割

この文書は、ISSUE-000070のactual runtime version交換について、現在どこまで実装され、どこからが未検証かを短く確認するための運用上のsnapshotです。

意味上のGoal、Fixed conditions、Resolution Criteriaは`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。実行手順は`RUNTIME_VERSION_EXCHANGE_EXECUTION_HANDOFF.md`を正とします。本書はそれらを置き換えません。

## 現在のEvidence状態

```text
fixed source / runtime / model identity machinery
  = implemented

fixed artifact preparation
  = implemented

prepositioned artifact root static re-verification
  = implemented

prepositioned root → verified runner orchestration
  = implemented

preflight → strict entrypoint → low-level harness
  = implemented

Evidence + Provenance verification
  = implemented

actual Ollama 0.32.13 / 0.32.14 A/B execution
  = Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet

ISSUE-000070
  = Open
```

`focused local checks`、helper test、artifact metadata照合、preflight、failure Evidence保存の成功をactual runtime交換の成立へ読み替えません。

## 現在の標準実行経路

固定artifactを取得できるLinux / amd64環境では、まずrepository外の一つのrootへruntime A/B archiveと固定model storeを準備します。

```bash
python3 runtime/integration/prepare_runtime_version_exchange_inputs.py \
  --root "$SOZA_RUNTIME_EXCHANGE_INPUTS"
```

この入口は、既存のruntime archive preparation helperとmodel store preparation / verifierを利用し、成功時に`verifiedRunnerInputs`を返します。

actual A/B実行では、個別のruntime archive pathやmodel pathを手で再構成せず、そのrootを上位入口へ渡します。

```bash
python3 runtime/integration/run_runtime_version_exchange_prepositioned.py \
  --artifact-root "$SOZA_RUNTIME_EXCHANGE_INPUTS" \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir "$SOZA_RUNTIME_EXCHANGE_EVIDENCE" \
  --verification-output "$SOZA_RUNTIME_EXCHANGE_VERIFY"
```

上位入口はactual processを始める前に固定artifact rootをnetworkなしで再検証し、machine-readableな`verifiedRunnerInputs`だけからmodel store、runtime A、runtime Bを標準verified runnerへ渡します。`--require-prepositioned-artifacts`は上位入口が強制します。

```text
external fixed-artifact root
  ↓
prepare_runtime_version_exchange_inputs.py
  ↓
verified prepositioned inputs
  ↓
run_runtime_version_exchange_prepositioned.py
  ↓ static verify-only revalidation
run_runtime_version_exchange_with_verification.py
  ↓
side-effect-free preflight
  ↓ ready only
strict entrypoint
  ↓
verified-bundle-only low-level harness
  ↓
actual Ollama /api/tags + A/B inference
  ↓
run-isolated Evidence
  ↓
Evidence + Provenance verifier
  ↓
ready-to-review | not-sufficient
```

手動preflightや下位verified runnerを直接使う経路は、blocked時の診断や個別境界の確認に残します。通常のhandoffでは、利用者がA/B archive file名を再入力する必要はありません。

## 公式Release metadataの再確認

2026-09-05にOllama公式GitHub Release APIを再確認し、ISSUE-000070で固定しているLinux / amd64 archiveのsizeとdigestが現在の公式Release metadataと一致することを確認しました。

| revision | size | GitHub Release asset digest |
| --- | ---: | --- |
| Ollama `0.32.13` | `1421793186` bytes | `sha256:0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| Ollama `0.32.14` | `1421191399` bytes | `sha256:c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

この再確認は取得元metadataの監査であり、actual archive bytesを取得・検証したことにはなりません。artifact identityの成立条件は、実行時に準備したactual bytesのSHA-256を固定値へ一致させることです。

```text
official Release metadata match
  != actual archive bytes acquired
  != actual binary version observed
  != actual A/B inference PASS
```

## 現作業環境での観測

2026-09-05、ChatGPT側の実行containerではLinux / amd64、Python、Go、Git、zstdと約30GBの空き容量を確認できています。一方、このcontainerからはactual実証に必要な約2.84GBの固定runtime archiveと固定model storeを通常の外部download経路で配置できませんでした。

同日、Remote Desktop Commander経由でユーザー管理端末`HAT47X`を確認し、WSL2の`Ubuntu-22.04`がLinux / x86_64で稼働していること、root filesystemに約884GBの空き容量があること、GitHubへHTTP 200で外部到達できることを実測しました。`git`、`python3`、`curl`、`tar`、`sha256sum`、`mktemp`、`cp`はWSL内で確認済みです。`go`と`zstd`はWSL内ではまだ確認できていないため、actual実行前にpreflight要件として確認またはuser-local配置が必要です。

このWSL2環境により、固定artifactを取得してactual A/Bを実行できる具体的なLinux / amd64候補が確認できました。ただし環境確認後にRemote Desktop Commander接続が切断され、固定artifactの取得、固定model storeの準備、preflight、actual Ollama A/B起動にはまだ進んでいません。

GitHub connectorから公式Release metadataを読めることや、WSL2実行候補の存在を確認したことは、binary bytesが配置されたことやactual runtime交換Evidenceが得られたことを意味しません。過去のrelevant GitHub Actions Runにも再利用できるworkflow artifactは残っていません。

現在の未実行理由は、repository側の実装不足ではなく、actual実行候補へのremote接続が継続していないという運用上の状態です。これをSOZAのProduct failureやruntime交換失敗とは扱いません。

## 次にEvidence強度が上がる条件

次の前進は追加のguard実装ではなく、上記WSL2等の固定artifactを取得可能なLinux / amd64環境で標準経路をactualに一度通すことです。

Evidence + Provenance verifierが`ready-to-review`へ到達した後も、それだけでISSUE-000070をResolvedにはしません。Application AのReference / Provenance / output不変性、same logical / different Exact Binding、portable historical reconstruction、no semantic promotion、Requirement / Contract再照合、自然な日本語最終監査まで確認します。

```text
artifact preparation PASS
  != preflight ready
  != actual A/B inference PASS
  != ready-to-review
  != ISSUE-000070 Resolved
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```
