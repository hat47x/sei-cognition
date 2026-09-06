# TEI E2 Partial Actual Runbook — 2026-09-06

## 1. 目的

ISSUE-000072のactual revision B E2を、E3 Go toolchainの準備状況から独立して回収するためのoperator向け手順です。

このrunbookは既存production runnerを組み合わせるだけで、Stable Requirement、Universal Contract、comparison axis、quality judgement、Resolution条件を変更しません。

```text
E2 partial actual success
  = exact revision B executable build
  + exact revision A fixed input
  + deployment-provider-plan execution
  + independently verifiable Evidence bundle

E2 partial actual success
  != E3 SOZA Adapter compatibility PASS
  != arbitrary TEI version compatibility
  != ISSUE-000072 Resolved
```

E2取得後、E3 Goが後日利用可能になった場合は、保存済みpartial EvidenceからE2/source acquisitionを再実行せずE3だけをresumeできます。

## 2. 前提

actual開始前に、次を別々の事実として確認します。

```text
host                    = Linux / amd64
SOZA checkout           = actualに使うcurrent checkout
E2 Go executable        = exact go1.23.2 linux/amd64
controlled Go target    = linux / amd64
revision A fixed input  = exact checkout または historical Evidence bundle
GitHub credential       = GITHUB_TOKEN または GH_TOKEN
Evidence output         = SOZA / A inputとは分離したfresh directory
```

credential値そのものは表示・記録しません。

例:

```bash
SOZA_REPO=/path/to/soza
TEI_GO=/path/to/go1.23.2/bin/go
E2_DIR=/path/to/evidence/tei-e2-partial-20260906

SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

uname -s
uname -m
"$TEI_GO" version
```

期待値:

```text
Linux
x86_64
... go1.23.2 linux/amd64
```

`GITHUB_TOKEN` / `GH_TOKEN`の値はechoしません。存在確認が必要な場合も値を出力しない方法を使います。

## 3. revision A fixed inputを選ぶ

E2 partial runnerは次のどちらか一方を受け取ります。

### A. historical Evidence bundle

```bash
TEI_A_BUNDLE=/path/to/historical-a-bundle.tar.gz
```

### B. exact revision A checkout

```bash
TEI_A_REPO=/path/to/exact-revision-a-checkout
```

revision A固定commitは次です。

```text
48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
```

runnerはsource acquisition前に既存canonical verifierでA fixed input identityを再検証します。

## 4. E2 partialをactual実行する

fresh Evidence directoryを使い、標準手順では`--overwrite`を付けません。

### historical A bundleを使う場合

```bash
python3 "$SOZA_REPO/runtime/integration/run_tei_revision_b_e2_from_github.py" \
  --reference-evidence-bundle "$TEI_A_BUNDLE" \
  --output-dir "$E2_DIR" \
  --tei-go-executable "$TEI_GO" \
  --json
```

### revision A checkoutを使う場合

```bash
python3 "$SOZA_REPO/runtime/integration/run_tei_revision_b_e2_from_github.py" \
  --reference-source-repo "$TEI_A_REPO" \
  --output-dir "$E2_DIR" \
  --tei-go-executable "$TEI_GO" \
  --json
```

source acquisition前に少なくとも次を検査します。

- output collision / dangling symlink
- exact revision A fixed input identity
- E2 Go = exact `go1.23.2 linux/amd64`
- controlled Go target = Linux/amd64
- source temporary parent safety

その後に初めてGitHub Git Data APIからexact revision B sourceをcontent-addressedに取得します。

## 5. E2成功時に保存するartifact

E2 partialの固定artifact名は次です。

```bash
E2_BUNDLE="$E2_DIR/tei-e3b-p2-revision-b-e2-partial.tar.gz"
E2_REPORT="$E2_DIR/tei-revision-b-e2-github.json"
```

成功reportの期待値:

```text
schema = soza.tei-revision-b-e2-github-run/v1
result = e2_bundle_verified_e3_not_run
qualityJudgement = not_evaluated
```

revision B固定source commit:

```text
1a7028d444fcae60a1c4f2f2d247456f4c7c35be
```

この時点でbinary SHA-256 / Provider Plan SHA-256は、事前期待値を置かずactual observationとして初めて固定します。

## 6. bundleをacquisition-independentに再検証する

E2 runner成功後、同じbundle bytesを既存independent verifierへ戻します。

```bash
python3 "$SOZA_REPO/runtime/integration/verify_tei_evidence_bundle.py" \
  "$E2_BUNDLE" \
  --expected-source-commit 1a7028d444fcae60a1c4f2f2d247456f4c7c35be \
  --json
```

ここで再計算・再検証される主なidentity:

- revision B source commit
- executable bit
- binary SHA-256
- Provider Plan SHA-256
- archive SHA-256
- bundle内revision A fixed reference identity

```text
partial report success
  + independent bundle verification success
  = E2 actual Evidenceとして評価可能
```

ただし、まだE3は未実行です。

## 7. failureを分類する

### source acquisition前のrejection

A fixed input、Go toolchain、output path等の事前条件で拒否された場合は、revision B build failureとして扱いません。

```text
pre-source rejection
  != revision B source acquired
  != TEI build failure
  != Provider Plan failure
```

### E2 stageへ入った後のfailure

source acquisition後にE2で停止した場合、runnerは可能な範囲でpartial reportへ`e2_failed`と既存substageを保存します。

既存Evidenceを保全し、原因確認前に`--overwrite`で再実行しません。

```text
E2 failure with repository-local substage
  = actual stopping point Evidence
  != automatic Product incompatibility conclusion
```

## 8. E3を後日resumeする

E2 partialが成功した後、current SOZAのE3要件を満たすGo executableが利用可能になれば、保存済みE2を再利用します。

新しいfresh output directoryを用意します。

```bash
SOZA_GO=/path/to/go-for-current-soza/bin/go
E3_DIR=/path/to/evidence/tei-e2-partial-e3-resume-20260906
SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"
```

実行:

```bash
python3 "$SOZA_REPO/runtime/integration/run_tei_version_exchange_resume_from_e2_partial.py" \
  --partial-report "$E2_REPORT" \
  --bundle "$E2_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$E3_DIR" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

resume runnerは次を行います。

1. 指定されたactual bundle bytesをexact revision Bへ再検証する。
2. bundle内revision A fixed inputを再検証する。
3. bundleのbinary / Provider Plan / archive SHA-256がE2 partial reportと一致することを確認する。
4. 保存済みGitHub acquisition Provenanceをfixed repository / revision B / root treeへ照合する。
5. revision B source acquisitionとE2 build / Provider Planを再実行せず、既存E3 Adapter live compatibilityだけを実行する。
6. 結果を既存canonical report / GitHub wrapper reportへ戻す。

resume成功時:

```text
result = fixed_scope_e2_e3_verified
executionProvenance.mode = e2_partial_then_e3_resume
```

`executionProvenance`は実行経路の記録であり、Universal ContractやCapability identityではありません。

## 9. E3 resume後のcanonical artifact

固定名:

```bash
CANONICAL_REPORT="$E3_DIR/tei-version-exchange-evidence.json"
GITHUB_WRAPPER_REPORT="$E3_DIR/tei-version-exchange-github-acquisition.json"
```

E3 failureでも既存stage semanticsを保ったcanonical reportが生成されます。

```text
result = e2_verified_e3_failed
failure.stage = E3
```

E3 failureをE2の再実行理由にしません。

## 10. Resolution auditへ接続する

canonical reportが得られたら、既存Resolution auditへ接続します。

historical A bundleを利用可能なら、criteria 1 / 5のcurrent再検証も同時に行えます。

```bash
AUDIT_OUT=/path/to/evidence/tei-version-exchange-resolution-audit-20260906.json

python3 "$SOZA_REPO/runtime/integration/audit_tei_version_exchange_resolution.py" \
  --canonical-report "$CANONICAL_REPORT" \
  --historical-a-bundle "$TEI_A_BUNDLE" \
  --github-wrapper-report "$GITHUB_WRAPPER_REPORT" \
  --soza-repo-root "$SOZA_REPO" \
  --expected-soza-head "$SOZA_HEAD" \
  --output "$AUDIT_OUT"
```

historical A bundleを指定しない場合、audit criteria 1 / 5はmanual境界に残ります。

Resolution auditは1〜6を自動判定し、7〜8をmanual reviewとして残します。Issueを自動closeしません。

## 11. 最終停止線

```text
repository-side path
  = E2 partial acquisition/build/Provider Plan
  + independent bundle verification
  + later E3 resume
  + canonical Resolution audit

actual successful execution
  required before Evidence promotion

fixed_scope_e2_e3_verified
  != arbitrary TEI version compatibility
  != Release Evidence
  != Operational Evidence
  != automatic ISSUE-000072 resolution
```

適切なactual環境が利用可能になった時点では、追加synthetic hardeningより本runbookのactual実行を優先します。
