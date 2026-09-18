# Cross-stage Execution Attempt Artifact

状態: **Draft / Not Started / No Benchmark Result**  
更新日: 2026-09-19

## 1. 目的

このdirectoryは、authorized cross-stage evaluation runの**実行試行そのもの**をresult artifactから分離して記録するcontractを定義する。

result contractはcompleted resultに `exit_code=0` を要求する。したがって、失敗した実行を成功resultへ包装してはならない。一方で、失敗試行にもrunner log、observed environment、executor identity、run bindingを残す必要がある。

```text
preregistration
  ↓
frozen bundle
  ↓
authorized run
  ↓
execution attempt   ← success / failureの双方を記録
  ↓ success only
future result artifact
```

現在の `execution_attempt.json` は空のdraft templateであり、実benchmark executionは開始していない。

## 2. 責務境界

execution-attempt artifactが記録するもの:

- exact authorized `run_digest`
- executor ref + exact Git commit
- observed execution environment
- started / completed time
- exit code
- succeeded / failed outcome
- runner-log / environment-capture / raw-outputのdigest-bound Evidence
- canonical attempt digest

記録しないもの:

- benchmark metric
- quality / semantic score
- winner / best variant
- interpretation
- B5 decision
- production default

```text
execution attempt != benchmark result
execution outcome != cognitive quality
```

## 3. State

### draft

checked-in templateは次を維持する。

- `attempt_id = cross-stage-attempt-template`
- run digestは空
- executor identityは空
- observed environmentは空
- `started_at = null`
- `completed_at = null`
- `exit_code = null`
- `outcome = not-started`
- raw Evidenceなし
- `results_generated = false`
- `attempt_digest = ""`

### completed

completed attemptは、上流のauthorized run / frozen bundle / preregistration unlockがvalidであることを再検証する。

ただしcompleted attemptは**result生成を意味しない**。

## 4. Success / Failure

`exit_code` と `outcome` の対応は固定する。

```text
exit_code == 0  -> outcome = succeeded
exit_code != 0  -> outcome = failed
```

`bool` はPython上で `int` のsubclassだが、exit codeとして受理しない。

失敗試行もimmutable completed artifactとして保存可能である。

```text
failed attempt
  != unavailable metric
  != zero metric
  != benchmark result
```

## 5. Raw Evidence

completed attemptでは常に次を要求する。

- `runner-log`
- `environment-capture`

successful attemptではさらに:

- `raw-output`

を要求する。

failureはraw output生成前に起こり得るため、failed attemptでは `raw-output` を必須にしない。

各entryは、

- registered kind
- canonical stable ref
- lowercase SHA-256 digest

を持つ。同一kind / refの重複は拒否する。

## 6. Run / Environment Binding

completed attemptの `run_binding.digest` はauthorized runのexact `run_digest` と一致しなければならない。

`observed_environment` もauthorized runで固定された、

- `os`
- `arch`
- `runtime`

とexact一致する必要がある。

環境が異なる場合は既存runのattemptとして受理せず、新しいrun authorizationが必要である。

## 7. Execution Identity

completed attemptは、

- canonical executor ref
- 40桁lowercase Git commit SHA

を持つ。

開始・終了時刻は秒精度UTC:

```text
YYYY-MM-DDTHH:MM:SSZ
```

とし、`started_at <= completed_at` を要求する。

## 8. Immutability

completed attemptはcanonical `attempt_digest` を持つ。

canonicalization:

- UTF-8 JSON
- key sort
- compact separator
- `attempt_digest` 自身だけ除外
- SHA-256

completed後にrun binding、executor、environment、時刻、exit code、raw Evidenceを変更するとdigest mismatchになる。

## 9. Strict schema

attempt artifactへ、

- `metrics`
- `winner`
- `best_variant`
- `b5_decision`
- `production_default`

などを追加するとschema validationで拒否される。

attempt artifactは実行履歴であって、測定結果や意思決定artifactではない。

## 10. Validation

focused contract tests:

```bash
python3 -m unittest -v test_validate_execution_attempt.py
```

2026-09-19のlocal authored-contract validationでは20 tests / 20 PASS、`py_compile` PASSを確認した。

このfocused testではupstream run/freeze/preregistration validatorの実runtime integrationはdependency injectionで代替している。GitHub正本sourceを再構成したfull integration runtime Evidenceは別sliceで固定する。

## 11. 停止線

```text
execution attempt != benchmark result
successful attempt != semantic interpretation
failed attempt != zero-valued metric
raw Evidence presence != semantic correctness
runtime success != variant winner
execution attempt != B5 gate decision
execution attempt != production adoption
```

human adjudication / freeze / run authorizationがunlockされるまで、checked-in `execution_attempt.json` をcompletedへ変更しない。
