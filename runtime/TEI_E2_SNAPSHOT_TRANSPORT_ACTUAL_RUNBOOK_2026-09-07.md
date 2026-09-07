# TEI E2 Snapshot Transport Actual Runbook — 2026-09-07

## 1. 目的

ISSUE-000072 の actual revision B E2 を、GitHub credential / private repository access を持つ環境と、actual build を行う Linux/amd64 環境へ分離して回収するための operator 向け手順である。

この経路は、既存の canonical source acquisition identity を変更しない。

```text
source acquisition
  = github-git-data-api-content-addressed

cross-environment source transport
  = preacquired-github-git-data-snapshot
```

snapshot は新しい source acquisition ではない。GitHub Git Data API から取得した blob / tree / signed commit response と bounded provenance を credential-free JSON として運び、offline 側で Git object identity を再計算して exact revision B を再構成する。

```text
snapshot transport ready
  != revision B actual build PASS
  != Provider Plan PASS
  != E3 SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

## 2. 固定比較軸

revision B executable source:

```text
1a7028d444fcae60a1c4f2f2d247456f4c7c35be
```

revision A fixed reference input:

```text
48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
```

Stable Requirement、Universal Contract、comparison axis、supported scope、quality judgement、Resolution 条件は変更しない。

## 3. 二段構成

### Stage T1 — online capture

private `hat47x/tei-platform` を GitHub Git Data API で読める環境で行う。

必要条件:

```text
SOZA checkout       = PR #312 / #313 取り込み後の current checkout
GitHub credential   = GITHUB_TOKEN または GH_TOKEN
source output       = fresh path、SOZA repository 外
snapshot output     = fresh path、SOZA repository 外
capture report      = source / snapshot と分離
```

credential 値そのものは表示・記録しない。

例:

```bash
SOZA_REPO=/path/to/soza
TEI_B_SOURCE=/path/to/transport-stage/tei-revision-b
TEI_B_SNAPSHOT=/path/to/transport-stage/tei-revision-b-git-data.json
CAPTURE_REPORT=/path/to/transport-stage/tei-revision-b-capture.json

python3 "$SOZA_REPO/runtime/integration/capture_tei_revision_b_git_data_snapshot.py" \
  --source-output "$TEI_B_SOURCE" \
  --snapshot-output "$TEI_B_SNAPSHOT" \
  --report-output "$CAPTURE_REPORT"
```

capture runner は次を行う。

1. GitHub Git Data API から fixed revision B の tree / blob / signed commit を取得する。
2. 取得 blob bytes を `git hash-object` 相当で再計算する。
3. tree entry から tree object identity を再計算する。
4. GitHub commit verification payload / signature から signed commit object を再構成する。
5. exact revision B HEAD / expected execution-source objects / working-tree purity を canonical verifier で確認する。
6. materializer が実際に消費した Git Data response のみを snapshot に保存する。
7. runtime credential bytes を snapshot へ保存しない。

成功時も、ここでは E2 build / Provider Plan を PASS 扱いしない。

## 4. snapshot の transport

Stage T1 から E2 実行環境へ運ぶ主入力は次である。

```text
TEI_B_SNAPSHOT
TEI_A_BUNDLE または exact revision A checkout
```

capture report に記録された snapshot SHA-256 は transfer 後の byte identity 確認に使用できる。

snapshot の top-level は固定 schema で検証され、repository / revision B commit / root tree / original acquisition provenance が固定値と一致しない場合は materialization 前に reject される。

snapshot 自身を信頼境界にしない。offline 側でも blob / tree / signed commit identity を再計算する。

## 5. Stage T2 — offline exact-B reconstruction + E2 partial

actual E2 を行う Linux/amd64 環境では、GitHub credential は不要である。

必要条件:

```text
host                    = Linux / amd64
SOZA checkout           = PR #312 / #313 取り込み後の current checkout
E2 Go executable        = exact go1.23.2 linux/amd64
revision A fixed input  = historical Evidence bundle または exact-A checkout
TEI_B_SNAPSHOT          = Stage T1 で生成・transfer 済み
Evidence output         = fresh directory、SOZA / A input / snapshot と分離
```

historical A bundle を使う場合:

```bash
SOZA_REPO=/path/to/soza
TEI_GO=/path/to/go1.23.2/bin/go
TEI_B_SNAPSHOT=/path/to/input/tei-revision-b-git-data.json
TEI_A_BUNDLE=/path/to/historical-a-bundle.tar.gz
E2_DIR=/path/to/evidence/tei-e2-partial-snapshot-20260907

python3 "$SOZA_REPO/runtime/integration/run_tei_revision_b_e2_from_snapshot.py" \
  --snapshot "$TEI_B_SNAPSHOT" \
  --reference-evidence-bundle "$TEI_A_BUNDLE" \
  --output-dir "$E2_DIR" \
  --tei-go-executable "$TEI_GO" \
  --json
```

exact revision A checkout を使う場合:

```bash
TEI_A_REPO=/path/to/exact-revision-a-checkout

python3 "$SOZA_REPO/runtime/integration/run_tei_revision_b_e2_from_snapshot.py" \
  --snapshot "$TEI_B_SNAPSHOT" \
  --reference-source-repo "$TEI_A_REPO" \
  --output-dir "$E2_DIR" \
  --tei-go-executable "$TEI_GO" \
  --json
```

runner は source bytes を展開する前に A fixed input、E2 Go、output / snapshot path safety を確認する。

その後、snapshot から exact revision B Git repository を temporary path へ再構成し、canonical source verification を再度通したうえで既存 E2 `produce_bundle()` へ渡す。

## 6. provenance の読み方

snapshot E2 report でも canonical source acquisition provenance は維持される。

```text
sourceAcquisition.mode
  = github-git-data-api-content-addressed
```

snapshot 利用は追加情報として保存する。

```text
sourceAcquisition.sourceTransport.mode
  = preacquired-github-git-data-snapshot

sourceAcquisition.sourceTransport.runtimeCredentialUsed
  = false
```

この分離により、later E3 resume が固定している existing source acquisition contract を変更しない。

```text
acquisition identity
  != transport mechanism
```

## 7. E2 成功時の artifact

既存 GitHub E2 partial と同じ固定名を使う。

```bash
E2_BUNDLE="$E2_DIR/tei-e3b-p2-revision-b-e2-partial.tar.gz"
E2_REPORT="$E2_DIR/tei-revision-b-e2-github.json"
```

成功 report:

```text
schema = soza.tei-revision-b-e2-github-run/v1
result = e2_bundle_verified_e3_not_run
qualityJudgement = not_evaluated
```

binary SHA-256 / Provider Plan SHA-256 は事前期待値を置かず、actual observation として初めて固定する。

## 8. strict bundle verification

E2 成功後は transport 方式に依存せず existing strict verifier へ戻す。

```bash
python3 "$SOZA_REPO/runtime/integration/verify_tei_version_exchange_e2_bundle.py" \
  "$E2_BUNDLE" \
  --json
```

ここで exact revision B source commit と exact revision A fixed reference input を repository-local expectations へ binding し、binary / Provider Plan / archive SHA-256 を actual bundle bytes から再計算する。

```text
E2 partial report success
  + exact-B / exact-A strict bundle verification success
  = E2 actual Evidenceとして評価可能
```

ただし E3 はまだ未実行である。

## 9. failure 分類

### T1 capture failure

GitHub credential / API / source reconstruction で停止した場合:

```text
T1 capture failure
  != revision B build failure
  != Provider Plan failure
```

### T2 pre-source rejection

snapshot schema / provenance、A fixed input、Go toolchain、path safety 等で停止した場合:

```text
T2 pre-source rejection
  != revision B build failure
  != Provider Plan failure
```

### T2 E2 failure

exact-B materialization後に build / Provider Plan へ入り停止した場合は、既存 repository-local E2 substage を actual stopping-point Evidence として保存する。

```text
actual E2 substage failure observed
  != automatic Product incompatibility conclusion
```

failure report は成功時と同じ固定名を使う。

```bash
E2_FAILURE_REPORT="$E2_DIR/tei-revision-b-e2-github.json"
```

`result=e2_failed` の partial report は full canonical report schema ではないため、成功用 `audit_tei_version_exchange_resolution.py` へ直接渡さない。PR #323 以降は failure-only adapter へ戻す。

historical A bundle を使った場合の標準例:

```bash
SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"
E2_FAILURE_AUDIT=/path/to/evidence/tei-e2-partial-failure-resolution-audit.json

python3 "$SOZA_REPO/runtime/integration/audit_tei_version_exchange_e2_partial_failure_resolution.py" \
  --partial-report "$E2_FAILURE_REPORT" \
  --historical-a-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --expected-soza-head "$SOZA_HEAD" \
  --output "$E2_FAILURE_AUDIT" \
  --json
```

stage-aware E2 failureでhistorical A再検証も成立した場合、概ね次の状態になる。

```text
criterion 1 = satisfied
criterion 2 = blocked
criterion 3 = satisfied
criterion 4 = blocked
criterion 5 = satisfied
criterion 6 = blocked
criterion 7 = manual_review
criterion 8 = manual_review
resolutionCandidate = false
```

criterion 3はrepository-local E2 substageを観測できたことだけを表す。criterion 2はactual executable / bundle identityが成立していないため、criterion 4はE3未到達のため、criterion 6はactual artifact identity境界まで成立していないためblockedのままにする。

exact-A checkoutを使った場合、historical A bundleを同時に与えなければcriterion 1 / 5はmanual reviewとして残り得る。これを理由に別のartifactやrevisionへ無言で差し替えない。

```text
actual E2 build failure
  != revision B replacement
  != SOZA Adapter incompatibility
  != ISSUE-000072 Resolved
```

原因確認前に `--overwrite` で既存 Evidence を上書きしない。

## 10. E3 resume 以降

E2 partial 成功後は、既存の正本手順へ戻る。

- `run_tei_version_exchange_resume_from_e2_partial.py`
- 必要時 `reconcile_tei_e2_partial_resume_reports.py`
- `audit_tei_version_exchange_resolution.py`

E2 partial failureの場合はE3へ進まず、Section 9のfailure-only Resolution auditへ戻る。

snapshot transport を使ったことを理由に E2 を再実行しない。

## 11. 2026-09-07 current execution surface

2026-09-07 current check では、repository-side path は正本へ取り込まれている一方、actual snapshot bytes を生成できる execution surface はまだ観測できていない。

```text
PR #312 snapshot producer / consumer       = merged
PR #313 snapshot -> E2 partial one-shot    = merged
PR #323 E2 partial failure Resolution audit = merged
current container DNS to api.github.com    = unavailable
Remote Desktop HAT47X                      = offline
recent TEI GitHub-hosted workflow job      = steps=[]
actual exact-B snapshot                    = Not Yet Acquired
```

recent hosted job の zero-step failure は TEI build / Provider Plan failure へ昇格させない。

またfixed-B exact sourceではsource-level compile contradictionがStatic Evidenceとして観測済みだが、canonical actual E2 build failureへは昇格させない。actual E2がbuild stageで停止した場合はSection 9のfailure-only auditへ戻す。

したがって current blocker は次のように表現する。

```text
transport implementation ready
  + offline E2 execution path ready
  + E2 failure audit path ready
  + actual online capture surface unavailable
  = actual snapshot Not Yet Acquired
  = E2 actual Not Yet Verified
```

## 12. 停止線

```text
snapshot transport implementation merged
  + snapshot -> E2 partial implementation merged
  + partial failure -> Resolution audit implementation merged
  != actual snapshot generated
  != revision B actual build PASS / FAIL established
  != revision B Provider Plan PASS
  != current SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

actual online capture surface が利用可能になった時点では、追加bootstrap探索やsynthetic hardeningより Stage T1 → T2 の actual 実行を優先する。
