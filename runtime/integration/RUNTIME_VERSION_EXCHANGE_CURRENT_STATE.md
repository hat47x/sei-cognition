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
  = Verified for the fixed scope

runtime-version-exchange Scoped Executable Evidence
  = available

ISSUE-000070
  = Resolved
```

2026-09-05にexecution ID `local-20260904T193531Z-7855`で標準経路を完走しました。独立Evidence + Provenance verifierは107 checkすべてを`ok`とし、blockerなしで`ready-to-review`を返しました。その後、Application A不変性、same logical / different Exact Binding、portable reconstruction、no semantic promotion、Requirement / Contractを再照合し、ISSUE-000070をResolvedとしました。

詳細は`../RUNTIME_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`、保存Evidenceは`../evidence/runtime-version-exchange-local-20260904T193531Z/`を参照します。

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

## Actual runの観測

actual runでは、計画に固定した2本のruntime archiveを実バイトで取得し、size / SHA-256を一致させました。固定model storeもmanifest raw bytesと5 blobのsize / SHA-256を再検証しています。

- A actual binary: Ollama `0.32.13`
- B actual binary: Ollama `0.32.14`
- A / B actual model digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- A / B prompt SHA-256: `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`
- A / B actual inference: PASS
- live historical Application test: PASS
- Evidence + Provenance verification: `ready-to-review`

以前の作業環境で外部artifactを配置できなかった観測は、当時の取得境界としてIssueに残します。今回の成功で過去の未実行を遡ってPASSにはしません。

## 次にEvidence強度が上がる条件

ISSUE-000070の固定scopeは完了しました。次の探索は、今回のPASSを過大評価せず、別の軸へ移します。

- actual human reviewによるmodel / KJ-method outcome quality評価
- fixed 2 revisionを越えるruntime / model / Method / Provider portability
- private artifact acquisition / credential lifecycle
- fully offline execution条件
- E4 Operational portability
- 次releaseでsupportする範囲とRelease Evidence

```text
fixed Ollama 0.32.13 / 0.32.14 exchange PASS
  != arbitrary runtime version portability
  != fully offline execution guaranteed
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```
