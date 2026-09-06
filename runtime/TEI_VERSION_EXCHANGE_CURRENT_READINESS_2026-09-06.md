# TEI Version Exchange Current Readiness — 2026-09-06

## 1. 位置づけ

本書は、`TEI_VERSION_EXCHANGE_EXECUTION_READINESS_2026-09-05.md` の後に追加された revision B source acquisition / actual orchestration / environment preflight の現在地をまとめる current delta です。

historical Evidence、Stable Requirement、Universal Contract、supported scope、quality judgementを更新する文書ではありません。actual revision Bのbuild / Provider Plan / current SOZA Adapter live testがまだ成立していないことを維持します。

```text
repository-side actual path implemented
  != revision B source acquired in an actual run
  != revision B build PASS
  != Provider Plan execution PASS
  != SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

比較軸は引き続き次です。

```text
revision B executable source
  = 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision A fixed reference input
  = 48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
```

## 2. revision B source取得経路

### 2.1 既存local cloneからのexact checkout

PR #250 / #252 / #254 により、self-containedな既存TEI Git object databaseにfixed revision B commit objectが存在する場合、元working treeを変更せず独立exact-B checkoutを作成できます。

入口:

`runtime/integration/prepare_tei_revision_b_checkout.py`

主な境界:

- revision Bがbranch/tag/refからreachableである必要はない。
- fixed revision B commit objectがlocal object databaseに存在すればよい。
- source clone / output cloneともGit alternates依存を許可しない。
- detached exact-B checkout作成後、canonical source verifierでHEAD / fixed object set / boundary purityを確認する。

```text
local B commit object available
  -> independent exact-B checkout preparation possible
```

### 2.2 GitHub Git Data APIからのcontent-addressed取得

PR #253 / #257 により、local cloneへrevision B objectがない場合でも、GitHub Git Data APIを取得経路としてexact-B sourceを再構成できます。

入口:

`runtime/integration/prepare_tei_revision_b_source.py`

処理:

1. `GITHUB_TOKEN`または`GH_TOKEN`をenvironmentからのみ取得する。
2. Git treeをtree-by-treeに辿り、各responseで`truncated=false`を要求する。
3. blob bytesをBase64 decodeし、local `git hash-object`でdeclared SHAへ再照合する。
4. child objectからtreeを再構成し、tree SHAを再照合する。
5. GitHub commit verification payload/signatureからsigned raw commit objectを再構成し、fixed revision B commit SHAへ照合する。
6. exact root treeからdetached HEAD / index / working treeを展開する。
7. canonical source verifierへ戻し、exact HEAD / execution-source objects / working-tree purityを確認する。

credential付きrequestはfixed repository prefixへ限定し、redirectはfollowしません。

```text
GitHub API acquisition path
  != source identity

acquired bytes
  -> local Git object reconstruction
  -> fixed object identity verification
  -> canonical exact-B checkout verification
```

### 2.3 non-Git content directory verifier

PR #251 の

`runtime/integration/verify_tei_execution_source_directory_identity.py`

は、non-Git directoryのactual bytes / executable modeから`cmd` / `internal` / `reference` treeと`go.mod` / `go.sum` blob identityを再構成できます。

これはacquisition-independentな補助検査であり、canonical E2のexact Git checkout要件の代替ではありません。

## 3. GitHub acquisitionからcanonical E2→E3までのone-shot入口

PR #256 / #258 により、GitHub取得と既存canonical runnerを薄いwrapperで接続しました。

入口:

`runtime/integration/run_tei_version_exchange_from_github.py`

```text
GitHub Git Data API acquisition
  -> exact-B detached checkout
  -> canonical source verification
  -> existing canonical E2
  -> existing canonical E3
```

wrapperはE2/E3の判定ロジックを複製しません。source acquisition Provenanceだけを別reportへ保持し、canonical E2/E3のstage vocabulary / comparison axis / Evidence bundle / failure semanticsは既存runnerを正とします。

credential値や一時source pathはwrapper reportへ保存しません。wrapper report publishはunique temporary file + flush/fsync + publish直前path再検査 + atomic replaceを使用します。

## 4. actual開始前preflight

PR #260 により、actual source取得を始める前に不足条件を一括確認する副作用なしpreflightを追加しました。

入口:

`runtime/integration/preflight_tei_version_exchange_from_github.py`

検査対象:

- Linux / amd64
- `GITHUB_TOKEN` / `GH_TOKEN`の存在（値は出力しない）
- exact revision A fixed reference input identity
  - Git checkoutの場合はcanonical Git verifier
  - historical Evidence bundleの場合は既存bundle verifier
- current SOZA source identity / boundary purity / optional expected HEAD
- E2 Go `go1.23.2` exact match
- E3 Goがcurrent `runtime/go/go.mod`のdirective以上であること
- Evidence output pathのstatic safety / existing canonical outputs

preflightはGitHub APIへ接続せず、revision B sourceをmaterializeせず、Evidence outputを作成しません。また最初のfailureで停止せず、全checkを実行して`blockedChecks`へ不足をまとめます。

```text
preflight ready
  != source acquisition PASS
  != E2 PASS
  != E3 PASS
```

## 5. current execution environmentの実測

machine-readable Evidence:

`runtime/evidence/tei-version-exchange-current-container-readiness-20260906/environment.json`

PR #259時点のcurrent execution containerでは次を実測しています。

```text
platform                           = Linux / x86_64
Git                                = 2.47.3
E2 Go                              = go1.23.2 linux/amd64
E2 historical requirement         = satisfied
GITHUB_TOKEN                       = unset
GH_TOKEN                           = unset
E3 Go 1.25 executable              = not present
current SOZA runtime/go directive  = go 1.25
```

したがって、このcontainerでactual runを開始できない理由は少なくとも次の2点です。

```text
private GitHub credential / private-source transport
E3 Go 1.25 toolchain
```

これはProduct failureではありません。

```text
environment prerequisite missing
  != TEI version exchange incompatibility observed
```

## 6. 次回actual実行の標準手順

actual実行環境には次を準備します。

- current SOZA checkout
- revision A fixed input
  - exact revision A checkout、または
  - verified historical revision A Evidence bundle
- E2用Go 1.23.2
- E3用Go 1.25以上でcurrent `runtime/go/go.mod`を満たすexecutable
- private `hat47x/tei-platform`をread可能な`GITHUB_TOKEN`または`GH_TOKEN`
- SOZA / revision A checkout外のEvidence output directory

まずcurrent SOZA HEADを固定します。

```bash
SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"
```

historical revision A Evidence bundleを使う例:

```bash
python3 "$SOZA_REPO/runtime/integration/preflight_tei_version_exchange_from_github.py" \
  --reference-evidence-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$EVIDENCE_DIR" \
  --tei-go-executable "$TEI_GO" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

`result=ready`を確認した後、同じaxisでactual one-shot runnerを実行します。

```bash
python3 "$SOZA_REPO/runtime/integration/run_tei_version_exchange_from_github.py" \
  --reference-evidence-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$EVIDENCE_DIR" \
  --tei-go-executable "$TEI_GO" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

exact revision A checkoutを使う場合は、両commandで`--reference-evidence-bundle`を`--reference-source-repo "$TEI_A_REPO"`へ置き換えます。

## 7. actual runで初めて上げられるEvidence

preflight / source acquisition implementation / synthetic regressionだけでは、次を主張しません。

actual one-shot runが成功した場合に初めて、fixed scopeについて次を観測できます。

```text
revision B actual CLI build PASS
revision B + revision A fixed input Provider Plan execution PASS
Evidence bundle verification PASS
current SOZA Adapter live compatibility PASS
fixed_scope_e2_e3_verified
```

それでも次は別です。

```text
fixed_scope_e2_e3_verified
  != arbitrary TEI version compatibility
  != formal executable distribution
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
  != ISSUE-000072 automatically Resolved
```

actual結果取得後は、`TEI_VERSION_EXCHANGE_REQUIREMENT_PREAUDIT_2026-09-05.md`の事前基準へ戻ってRequirement / Scenarioを再照合します。build / toolchain / Provider Plan process / Adapter-local DTOの失敗だけを理由にStable RequirementやUniversal Contract fieldを追加しません。

## 8. current state

```text
revision B source identity
  = fixed

local exact-B checkout preparation
  = implemented

GitHub content-addressed exact-B acquisition
  = implemented

GitHub acquisition credential redirect boundary
  = enforced

GitHub acquisition -> canonical E2/E3 wrapper
  = implemented

wrapper report publish TOCTOU guard
  = implemented

actual-run preflight
  = implemented

current container E2 Go 1.23.2
  = available

current container private GitHub credential
  = not available

current container E3 Go >=1.25
  = not available

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

revision B current SOZA Adapter live compatibility
  = Not Yet Verified

ISSUE-000072
  = Open
```
