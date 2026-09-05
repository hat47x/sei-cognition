# TEI Version Exchange Actual Orchestration

更新日: 2026-09-05

## 位置づけ

`run_tei_version_exchange_actual.py`は、ISSUE-000072のactual E2 / E3を一つのrepository-local入口から順に実行し、成功・失敗のどちらでも新しいJSONへ結果を保存する薄いorchestratorです。

既存runnerの意味や判定条件は変更しません。

```text
run_tei_revision_b_prepositioned.py
  = E2の正本

run_tei_bundle_adapter_compatibility.py
  = E3の正本

run_tei_version_exchange_actual.py
  = E2 → E3の順序とresult保存を束ねる補助入口
```

```text
orchestrator ready
  != revision B build PASS
  != Provider Plan observed
  != Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

## 目的

actual環境でE2またはE3が不成立だった場合、端末上の一時的な表示だけに依存せず、既存runnerが持つstage情報を構造化したまま保存します。

E2が成立してE3で止まった場合は、E2結果も同じresult JSONへ保持します。

result JSONの主な状態は次です。

```text
result = ready_to_review
  → E2 / E3ともrunner上は成立

result = failed, phase = E2
  → E2のどこかで停止

result = failed, phase = E3
  → E2成立後、E3のどこかで停止
```

`ready_to_review`はIssue解決や成果品質の判定ではありません。

## 上書きしない

historical Evidenceを保護するため、orchestratorは次を既存fileへ上書きしません。

- `--output-archive`
- `--result-file`

両者に同じpathを指定することも拒否します。

したがって再実行する場合はrunごとに新しいfile名を使います。

## 標準実行例

```bash
export TEI_B_REPO=/path/to/tei-revision-b
export TEI_A_REPO=/path/to/tei-revision-a
export SOZA_REPO=/path/to/soza
export TEI_B_BUNDLE=/path/to/evidence/tei-revision-b-linux-amd64.tar.gz
export TEI_EXCHANGE_RESULT=/path/to/evidence/tei-version-exchange-result.json

SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

python3 "$SOZA_REPO/runtime/integration/run_tei_version_exchange_actual.py" \
  --source-repo "$TEI_B_REPO" \
  --reference-source-repo "$TEI_A_REPO" \
  --output-archive "$TEI_B_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --expected-soza-head "$SOZA_HEAD" \
  --result-file "$TEI_EXCHANGE_RESULT" \
  --json
```

E2ではexact revision Bをbuild source、exact revision Aをfixed reference inputとして別々に渡します。E3では生成済みbundleをcurrent SOZA Adapterへ接続します。

## failure JSON

既存runnerがstage付き例外を返した場合、`failure`へそのまま保存します。

例:

```json
{
  "result": "failed",
  "phase": "E2",
  "failure": {
    "stage": "tei_cli_build",
    "message": "external process returned non-zero status",
    "returnCode": 2,
    "stderrTail": "..."
  }
}
```

process出力は既存runner側の上限に従います。stderr文言だけからworkspace / validation / strict decode等の内部substageを推定して昇格させません。

```text
observed failure stage
  = runnerが直接観測した停止点
  != inferred internal cause
```

## 成功時の境界

成功時はE2とE3の結果を同一JSONへ保存し、`result = ready_to_review`とします。

ただし、ここで確認できるのはfixed A/B条件に対するactual execution conformanceです。

```text
ready_to_review
  != arbitrary TEI version compatibility
  != formal executable distribution
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

また、model / Cognitive Method outcome qualityやDecision correctnessとは無関係です。

## テスト

`test_run_tei_version_exchange_actual.py`では少なくとも次を確認します。

- E2 / E3成功時に両結果を保存する。
- E2 stage failureを保存し、E3を開始しない。
- E3 stage failure時にE2結果を保持する。
- 既存result JSONを上書きしない。
- 既存Evidence bundleを上書きしない。
- bundleとresult JSONに同じpathを指定できない。

このunit testはsynthetic orchestration testであり、actual revision B Executable Evidenceではありません。
