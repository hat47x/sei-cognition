# TEI E2 Snapshot Transport Actual Runbook — 2026-09-07

## 1. 目的

ISSUE-000072のactual revision B E2を、GitHub credential / private repository accessを持つ環境と、actual buildを行うLinux/amd64環境へ分離して回収するためのoperator向け手順である。

この経路は、既存のcanonical source acquisition identityを変更しない。

```text
source acquisition
  = github-git-data-api-content-addressed

cross-environment source transport
  = preacquired-github-git-data-snapshot
```

snapshotは新しいsource acquisitionではない。GitHub Git Data APIから取得したblob / tree / signed commit responseとbounded provenanceをcredential-free JSONとして運び、offline側でGit object identityを再計算してexact revision Bを再構成する。

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

Stable Requirement、Universal Contract、comparison axis、supported scope、quality judgement、Resolution条件は変更しない。

## 3. 二段構成

### Stage T1 — online capture

private `hat47x/tei-platform` をGitHub Git Data APIで読める環境で行う。

必要条件は次のとおりです。

```text
SOZA checkout       = PR #312 / #313 取り込み後の current checkout
GitHub credential   = GITHUB_TOKEN または GH_TOKEN
source output       = fresh path、SOZA repository 外
snapshot output     = fresh path、SOZA repository 外
capture report      = source / snapshot と分離
```

credential値そのものは表示・記録しない。

例は次のとおりです。

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

capture runnerは次を行う。

1. GitHub Git Data APIからfixed revision Bのtree / blob / signed commitを取得する。
2. 取得blob bytesを `git hash-object` 相当で再計算する。
3. tree entryからtree object identityを再計算する。
4. GitHub commit verification payload / signatureからsigned commit objectを再構成する。
5. exact revision B HEAD / expected execution-source objects / working-tree purityをcanonical verifierで確認する。
6. materializerが実際に消費したGit Data responseのみをsnapshotに保存する。
7. runtime credential bytesをsnapshotへ保存しない。

成功時も、ここではE2 build / Provider PlanをPASS扱いしない。

## 4. snapshot の transport

Stage T1からE2実行環境へ運ぶ主入力は次である。

```text
TEI_B_SNAPSHOT
TEI_A_BUNDLE または exact revision A checkout
```

capture reportに記録されたsnapshot SHA-256はtransfer後のbyte identity確認に使用できる。

snapshotのtop-levelは固定schemaで検証され、repository / revision B commit / root tree / original acquisition provenanceが固定値と一致しない場合はmaterialization前にrejectされる。

snapshot自身を信頼境界にしない。offline側でもblob / tree / signed commit identityを再計算する。

## 5. Stage T2 — offline exact-B reconstruction + E2 partial

actual E2を行うLinux/amd64環境では、GitHub credentialは不要である。

必要条件は次のとおりです。

```text
host                    = Linux / amd64
SOZA checkout           = PR #312 / #313 取り込み後の current checkout
E2 Go executable        = exact go1.23.2 linux/amd64
revision A fixed input  = historical Evidence bundle または exact-A checkout
TEI_B_SNAPSHOT          = Stage T1 で生成・transfer 済み
Evidence output         = fresh directory、SOZA / A input / snapshot と分離
```

historical A bundleを使う場合。

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

exact revision A checkoutを使う場合。

```bash
TEI_A_REPO=/path/to/exact-revision-a-checkout

python3 "$SOZA_REPO/runtime/integration/run_tei_revision_b_e2_from_snapshot.py" \
  --snapshot "$TEI_B_SNAPSHOT" \
  --reference-source-repo "$TEI_A_REPO" \
  --output-dir "$E2_DIR" \
  --tei-go-executable "$TEI_GO" \
  --json
```

runnerはsource bytesを展開する前にA fixed input、E2 Go、output / snapshot path safetyを確認する。

その後、snapshotからexact revision B Git repositoryをtemporary pathへ再構成し、canonical source verificationを再度通したうえで既存E2 `produce_bundle()` へ渡す。

## 6. provenance の読み方

snapshot E2 reportでもcanonical source acquisition provenanceは維持される。

```text
sourceAcquisition.mode
  = github-git-data-api-content-addressed
```

snapshot利用は追加情報として保存する。

```text
sourceAcquisition.sourceTransport.mode
  = preacquired-github-git-data-snapshot

sourceAcquisition.sourceTransport.runtimeCredentialUsed
  = false
```

この分離により、later E3 resumeが固定しているexisting source acquisition contractを変更しない。

```text
acquisition identity
  != transport mechanism
```

## 7. E2 成功時の artifact

既存GitHub E2 partialと同じ固定名を使う。

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

binary SHA-256 / Provider Plan SHA-256は事前期待値を置かず、actual observationとして初めて固定する。

## 8. strict bundle verification

E2成功後はtransport方式に依存せずexisting strict verifierへ戻す。

```bash
python3 "$SOZA_REPO/runtime/integration/verify_tei_version_exchange_e2_bundle.py" \
  "$E2_BUNDLE" \
  --json
```

ここでexact revision B source commitとexact revision A fixed reference inputをrepository-local expectationsへbindingし、binary / Provider Plan / archive SHA-256をactual bundle bytesから再計算する。

```text
E2 partial report success
  + exact-B / exact-A strict bundle verification success
  = E2 actual Evidenceとして評価可能
```

ただしE3はまだ未実行である。

## 9. failure 分類

### T1 capture failure

GitHub credential / API / source reconstructionで停止した場合。

```text
T1 capture failure
  != revision B build failure
  != Provider Plan failure
```

### T2 pre-source rejection

snapshot schema / provenance、A fixed input、Go toolchain、path safety等で停止した場合。

```text
T2 pre-source rejection
  != revision B build failure
  != Provider Plan failure
```

### T2 E2 failure

exact-B materialization後にbuild / Provider Planへ入り停止した場合は、既存repository-local E2 substageをactual stopping-point Evidenceとして保存する。

```text
actual E2 substage failure observed
  != automatic Product incompatibility conclusion
```

failure reportは成功時と同じ固定名を使う。

```bash
E2_FAILURE_REPORT="$E2_DIR/tei-revision-b-e2-github.json"
```

`result=e2_failed` のpartial reportはfull canonical report schemaではないため、成功用 `audit_tei_version_exchange_resolution.py` へ直接渡さない。PR #323以降はfailure-only adapterへ戻す。

historical A bundleを使った場合の標準例:

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

原因確認前に `--overwrite` で既存Evidenceを上書きしない。

## 10. E3 resume 以降

E2 partial成功後は、既存の正本手順へ戻る。

- `run_tei_version_exchange_resume_from_e2_partial.py`
- 必要時 `reconcile_tei_e2_partial_resume_reports.py`
- `audit_tei_version_exchange_resolution.py`

E2 partial failureの場合はE3へ進まず、Section 9のfailure-only Resolution auditへ戻る。

snapshot transportを使ったことを理由にE2を再実行しない。

## 11. 2026-09-07 current execution surface

2026-09-07 current checkでは、repository-side pathは正本へ取り込まれている一方、actual snapshot bytesを生成できるexecution surfaceはまだ観測できていない。

```text
PR #312 snapshot producer / consumer       = merged
PR #313 snapshot -> E2 partial one-shot    = merged
PR #323 E2 partial failure Resolution audit = merged
current container DNS to api.github.com    = unavailable
Remote Desktop HAT47X                      = offline
recent TEI GitHub-hosted workflow job      = steps=[]
actual exact-B snapshot                    = Not Yet Acquired
```

recent hosted jobのzero-step failureはTEI build / Provider Plan failureへ昇格させない。

またfixed-B exact sourceではsource-level compile contradictionがStatic Evidenceとして観測済みだが、canonical actual E2 build failureへは昇格させない。actual E2がbuild stageで停止した場合はSection 9のfailure-only auditへ戻す。

したがってcurrent blockerは次のように表現する。

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

actual online capture surfaceが利用可能になった時点では、追加bootstrap探索やsynthetic hardeningよりStage T1 → T2のactual実行を優先する。
