# Runtime Version Exchange — Current Execution State

更新日: 2026-09-05  
対象: ISSUE-000070

## この文書の役割

この文書は、ISSUE-000070のactual runtime version交換について、現在どこまでEvidenceが成立しているかを短く確認するための運用上のsnapshotです。

意味上のGoal、Fixed conditions、Resolution Criteriaは`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。実行手順は`RUNTIME_VERSION_EXCHANGE_EXECUTION_HANDOFF.md`を正とします。本書はそれらを置き換えません。

## 現在のEvidence状態

2026-09-05、historical branch `codex/issue-000070-actual-evidence` からexecution `local-20260904T193531Z-7855` のactual Evidenceをcurrent developへ回収しました。

```text
fixed KJ Atlas source identity
  = Verified

Ollama 0.32.13 / 0.32.14 actual archive bytes / binary version
  = Verified

fixed qwen2.5:0.5b model artifact identity
  = Verified statically and by A/B actual /api/tags observation

same fixed Method input / same prompt digest
  = Verified

actual A/B inference
  = Verified

same logical Realization / different Exact Binding
  = Verified

historical Application A immutability
  = Verified

portable historical reconstruction / negative control
  = Verified

Evidence + Provenance verification
  = ready-to-review; 107 ok / 0 blocked

runtime-version-exchange Scoped Executable Evidence
  = available

ISSUE-000070
  = Resolved
```

raw Evidenceは次に保存しています。

- `runtime/evidence/runtime-version-exchange-local-20260904T193531Z/`
- `runtime/RUNTIME_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`
- `runtime/integration/RUNTIME_VERSION_EXCHANGE_RECOVERED_EVIDENCE_2026-09-05.md`
- `runtime/RUNTIME_VERSION_EXCHANGE_CURRENT_CONTRACT_REVALIDATION_2026-09-05.md`

## actual executionの主要観測

actual runはSOZA commit `ae9f631b7d570a6c3853bb71b794d501761fdf63`で実行されました。

runner observation:

- execution ID: `local-20260904T193531Z-7855`
- `completed = true`
- `exitCode = 0`
- `preflightResult = ready`
- `evidenceDirectoryCreatedBy = strict-entrypoint`
- `qualityJudgement = not_evaluated`
- combined log SHA-256: `4fb5833f8522ad65ab6552629a4982175337b73431d0d4e2913f8ffea827f48d`

runtime exchange:

| axis | revision A | revision B |
| --- | --- | --- |
| Ollama | `0.32.13` | `0.32.14` |
| archive SHA-256 | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |
| model | `qwen2.5:0.5b` | `qwen2.5:0.5b` |
| model digest | `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67` | same |
| prompt SHA-256 | `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33` | same |
| `ollama_done` | `true` | `true` |
| `prompt_eval_count` | `196` | `196` |
| `eval_count` | `78` | `78` |

生成文そのものの一致はPASS条件ではありません。

## current canonical baselineとの再照合

回収直後は、historical runの保存済みverificationをcurrent canonical verifier / current Contractへまだ再照合していない可能性を保守的な未完了事項として残していました。

その後、actual run commitとcurrent developをGit object identityで比較し、次が同一objectであることを確認しました。

- ISSUE-000070 Resolution Criteria
- core Evidence verifier
- Evidence + Provenance verifier
- fixed artifact manifest
- Product Requirements
- Acceptance Scenarios
- Cognitive Method / Semantic Reference / Semantic Interchangeを含むrelevant Contract baseline

したがって、保存済み`ready-to-review`結果が「現在とは異なる古いverifier / manifest / Contractだけに対する結果」という懸念は成立しません。

Requirement / Contract再照合と自然な日本語最終監査も完了し、新しいStable Requirement / Acceptance Scenario / Universal Contract fieldは不要と判断しました。

詳細は`runtime/RUNTIME_VERSION_EXCHANGE_CURRENT_CONTRACT_REVALIDATION_2026-09-05.md`を参照します。

## 標準実行経路

再現・追加検証を行う場合の標準入口は引き続き変えません。

固定artifact準備:

```bash
python3 runtime/integration/prepare_runtime_version_exchange_inputs.py \
  --root "$SOZA_RUNTIME_EXCHANGE_INPUTS"
```

actual A/B実行:

```bash
python3 runtime/integration/run_runtime_version_exchange_prepositioned.py \
  --artifact-root "$SOZA_RUNTIME_EXCHANGE_INPUTS" \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir "$SOZA_RUNTIME_EXCHANGE_EVIDENCE" \
  --verification-output "$SOZA_RUNTIME_EXCHANGE_VERIFY"
```

保存済みEvidenceの標準再検証:

```bash
python3 runtime/integration/verify_runtime_version_exchange_provenance.py \
  --evidence-dir /path/to/evidence-directory \
  --output /path/to/new-verification.json
```

repository-local focused regression:

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py
```

これらの入口は、今回のhistorical actual Evidence回収後も再現性やreopen条件の監査に利用できます。

## Remote Desktopとの関係

`HAT47X` / WSL2は、固定artifactを取得して独立にactual runを再現できる具体的なLinux / amd64候補として確認済みですが、現在Remote Desktop接続はofflineです。

これは今後の独立reproductionや追加runを妨げる運用上の状態ではありますが、すでに回収・検証済みのactual Evidenceを無効化せず、ISSUE-000070のResolutionを妨げません。

```text
HAT47X offline
  != recovered actual Evidence invalid
  != Ollama incompatibility
  != ISSUE-000070 reopen condition
```

## 成果品質との境界

今回成立したのは、固定scopeでのruntime version交換とhistorical reconstructionに関するScoped Executable Evidenceです。

- model output quality: Not Evaluated
- language suitability: Not Evaluated
- KJ-method outcome quality: Not Evaluated
- Recommendation correctness: Not Evaluated
- Decision correctness: Not Evaluated
- E4 Operational portability: Not Established

```text
ISSUE-000070 Resolved
  != arbitrary runtime version portability
  != other runtime implementation portability
  != fully offline execution guaranteed
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```
