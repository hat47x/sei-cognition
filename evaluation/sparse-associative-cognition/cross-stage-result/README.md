# Cross-stage Result Artifact

状態: **Draft / No Human Benchmark Result**  
更新日: 2026-09-18

## 1. 目的

このdirectoryは、authorized cross-stage evaluation runの実行結果を、run artifactを書き換えずに別のimmutable artifactとして記録するためのcontractを定義する。

現在の `result.json` は空のdraft templateである。

human-adjudicated dataset / freeze bundle / evaluation runがまだdraft / lockedであるため、実semantic benchmark resultは存在しない。

```text
preregistration
  ↓
frozen bundle
  ↓
authorized run
  ↓
execution attempt
  ↓ success only
result artifact
  ↓
interpretation artifact
  ↓
future decision artifact
```

result artifactは最後の「判断」ではなく、再検証可能な測定記録である。

interpretationは `../cross-stage-interpretation/` の別artifactへ分離し、result自身へwinner・recommendation・B5 decisionを埋め込まない。

### Interpretationとの分離

```text
result measurement
  != interpretation
  != decision
```

測定値の意味づけをresult artifactへ書き戻さず、interpretation側も非決定的artifactとして扱う。

## 2. State

### draft

checked-in templateは次を維持する。

- `generated_at = null`
- `results_generated = false`
- `result_digest = ""`
- metricなし
- raw evidenceなし

### completed

completed resultは、少なくとも次にbindされる。

- authorized runのexact `run_digest`
- valid preregistration
- valid frozen bundle
- authorized runのtrack / variant / capacity / stress identity
- authorized runのenvironment
- executor ref + exact Git commit
- raw output digest
- environment capture digest

## 3. Metric completeness

completed resultは、authorized runでrequestedされたmetricを**exactly once**記録する。

metricを黙って落とさない。

### measured

- finite numeric value
- canonical unit
- `sample_count >= 1`
- unavailable reasonは空

### unavailable

- `value = null`
- `unit = ""`
- `sample_count = 0`
- non-empty reason

```text
unavailable
  != zero
  != missing
```

測定不能を0として埋めると、後段の解釈で実値と区別できなくなるため禁止する。

## 4. Metric role

retrievalはpreregistrationのcategoryを保持する。

- quality -> `quality`
- robustness -> `robustness`
- resource -> `resource`
- diagnostics -> `diagnostic`

familiarity / routingは `track-metric` とする。

特にretrieval diagnosticをqualityへ昇格させない。

```text
diagnostic measurement
  != semantic quality score
```

## 5. Raw Evidence

completed resultには最低限、

- `raw-output`
- `environment-capture`

を必要とする。

任意で `runner-log` を追加できる。

各entryはstable refとSHA-256 content digestを持つ。

raw file本文をresult artifactへ埋め込まず、参照とdigestでbindする。

## 6. Environment

`observed_environment` はauthorized runで事前固定されたenvironmentとexact一致する必要がある。

異なる環境で実行された場合は、既存runの結果として受理せず、新しいrun authorizationが必要である。

## 7. Execution identity

completed resultは次を持つ。

- executor ref
- 40桁lowercase Git commit SHA
- started_at
- completed_at
- exit_code

時刻は秒精度UTC `YYYY-MM-DDTHH:MM:SSZ`。

completed resultでは `exit_code=0` を要求する。

失敗したexecutionを成功結果として包装しない。失敗実行は `../cross-stage-attempt/execution_attempt.json` のexecution-attempt artifactへ分離する。

## 8. Immutability

completed resultはcanonical `result_digest` を持つ。

canonicalization:

- UTF-8 JSON
- key sort
- compact separator
- `result_digest` 自身だけ除外
- SHA-256

completed後にmetric、raw Evidence、run binding、environment、execution metadataを変更するとdigest mismatchになる。

## 9. Strict schema

top-level fieldとnested fieldは登録済みkeyだけを許可する。

したがってresultへ、

- `winner`
- `best_variant`
- `b5_decision`
- `production_default`
- `composite_score`

等を追加するとschema validationで拒否される。

result artifactは測定記録であり、意思決定artifactではない。

## 10. Validation

current draft:

```bash
python validate_result.py
```

期待値:

```text
Cross-stage result validated; current result remains draft/empty
```

completed validationでは、resultだけでなく、

- preregistration
- frozen bundle
- authorized run
- full unlock state

を再検証する。

### Actual runtime verification

2026-09-18にGitHub正本とGit blob SHAが一致する一時再構成環境でPython 3.13.5を用いて実行した。

- `validate_result.py`: PASS / current result remains draft/empty
- result unit tests: 24 / 24 PASS
- evaluation-run unit tests: 20 / 20 PASS
- freeze-kit unit tests: 18 / 18 PASS
- preregistration unit tests: 27 / 27 PASS
- 合計: 89 tests PASS / 0 failures
- GitHub Actions: 未使用

machine-readable Evidence:

`result_runtime_evidence_2026-09-18.json`

このPASSはresult contractとcross-stage integrationのExecutable Evidenceであり、human-adjudicated benchmark result、current result completion、semantic interpretation、B5 decision、production adoptionを意味しない。

## 11. 停止線

```text
result artifact != benchmark interpretation
measured metric != semantic truth
diagnostic metric != semantic score
unavailable metric != zero
result artifact != variant winner
result artifact != B5 gate decision
result artifact != production adoption
synthetic completed-result test != human-adjudicated benchmark result
```

実human-adjudicated benchmarkがunlockされ、authorized runが実際に実行されるまで、checked-in `result.json` をcompletedへ変更しない。
