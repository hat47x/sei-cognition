# Failure behavior local checks

`run_local_checks.py`は、ISSUE-000072のrepository-local regression入口です。

実行対象は次の4件です。

- case catalog validator test
- deterministic failure probe test
- local runner自身のtest
- `runtime/go/provideradapter`のGo test

repository rootから次を実行します。

```bash
python evaluation/failure-behavior/run_local_checks.py
```

このrunnerがPASSしても、actual Provider failure、actual deployment failure、Operational Evidenceの成立は意味しません。
