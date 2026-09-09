# Failure behavior evaluation

このdirectoryは、ISSUE-000072で扱うRuntime / Provider failure behaviorについて、Universal Contractやproduction retry policyへ先取りせずに比較するためのevaluation-only資産を置く。

## Current assets

- `case_catalog.json`
  - transport、Provider admission、credential、artifact acquisition、artifact identity / integrity、runtime execution、semantic mapping、retryを比較するcase catalog。
- `validate_failure_behavior_case_catalog.py`
  - catalogが`evaluation-only` / `non-universal`であり、Provider固有error code、retry schedule、secret material等を固定していないことを検査する。
- `run_deterministic_failure_probe.py`
  - 外部serviceなしでcatalogの9 caseを発火し、deterministic reportを生成する。
- `run_local_checks.py`
  - catalog validator test、deterministic probe test、runner test、`runtime/go/provideradapter`のGo testをrepository-localにまとめて実行する。

## Local checks

repository rootから次を実行する。

```bash
python evaluation/failure-behavior/run_local_checks.py
```

check一覧だけを確認する場合:

```bash
python evaluation/failure-behavior/run_local_checks.py --list
```

最初の失敗で止める場合:

```bash
python evaluation/failure-behavior/run_local_checks.py --stop-on-failure
```

結果をJSONで保存する場合:

```bash
python evaluation/failure-behavior/run_local_checks.py \
  --result-output /tmp/soza-failure-behavior-local-checks.json
```

既存fileは上書きしない。

## Evidence boundary

local checksがPASSしても、確認できるのはrepository-localのdeterministic / fixture-scoped behaviorである。

```text
failure behavior local checks PASS
  != actual Provider failure Evidence
  != actual deployment failure Evidence
  != Operational Evidence
```

actual Providerのrate limit、credential rejection、artifact acquisition failure等を確認する場合は、別のactual probeとしてEvidenceを取得する。Provider固有status codeやsecretをこのevaluation catalogのUniversalな意味として扱わない。
