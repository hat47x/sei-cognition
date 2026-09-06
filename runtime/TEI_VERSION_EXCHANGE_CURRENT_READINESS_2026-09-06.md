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
- PR #269以降、optionalなcheckout preparation provenanceは`--report-output`でsource/output checkout外の新規pathへno-overwrite保存できる。
- preparation report publishに失敗した場合は、その呼び出しで作成したB checkoutも撤去する。

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

credential付きrequestはfixed repository prefixへ限定し、redirectはfollowしません。PR #273以降、取得途中の`git init` / `hash-object -w` / `mktree` / checkout等も後述のcontrolled Git environmentを使い、ambient object directory等へread/writeを逸らしません。

```text
GitHub API acquisition path
  != source identity

acquired bytes
  -> local Git object reconstruction
  -> fixed object identity verification
  -> canonical exact-B checkout verification
```

### 2.3 Git source identity / materialization共通のcontrolled environment

PR #271 / #273 / #274 により、local checkout、local preflight、GitHub acquisition、canonical source verifierが、literal repository / Git object graphを変え得るprocess-level Git overrideから分離されました。

共通helper:

`runtime/integration/git_object_environment.py`

除外する主なenvironment override:

```text
GIT_DIR
GIT_WORK_TREE
GIT_COMMON_DIR
GIT_OBJECT_DIRECTORY
GIT_ALTERNATE_OBJECT_DIRECTORIES
GIT_INDEX_FILE
GIT_NAMESPACE
GIT_REPLACE_REF_BASE
GIT_GRAFT_FILE
GIT_CONFIG_COUNT
GIT_CONFIG_PARAMETERS
GIT_CONFIG_KEY_*
GIT_CONFIG_VALUE_*
```

加えて、次を固定します。

```text
GIT_NO_REPLACE_OBJECTS=1
GIT_DEFAULT_HASH=sha1
```

PR #277では、E3のcurrent SOZA source baselineも同じcontrolled Git environmentへ揃え、`git_object_environment.py`自身をSOZA Evidence source boundaryへ含めました。これにより、TEI source側だけでなくE3 live test前後のSOZA source identityもambient object directory / replace semantics / process-level Git config injectionから分離します。

これはhost全体をfully hermeticにする主張ではありません。ISSUE-000072の固定SHA-1 Git object graph、source checkout identity、materialized source bytesへ直接影響するprocess-level overrideを対象にします。system / global / repository configそのものを一般に無効化するものでもありません。

negative controlでは、通常Gitではambient `GIT_OBJECT_DIRECTORY`やreplace refによりobject解決が変わること、また`GIT_CONFIG_COUNT/KEY/VALUE`でrepositoryの`core.autocrlf=false`を`true`へ上書きできることを確認しました。controlled environmentではliteral repo object graphとrepository valueへ戻ることを確認しています。

```text
controlled Git source identity
  != hostile host fully hermetic
  != revision B actual build PASS
```

### 2.4 non-Git content directory verifier

PR #251 の

`runtime/integration/verify_tei_execution_source_directory_identity.py`

は、non-Git directoryのactual bytes / executable modeから`cmd` / `internal` / `reference` treeと`go.mod` / `go.sum` blob identityを再構成できます。

これはacquisition-independentな補助検査であり、canonical E2のexact Git checkout要件の代替ではありません。

## 3. GitHub acquisitionからcanonical E2→E3までのone-shot入口

PR #256 / #258 により、GitHub取得と既存canonical runnerを薄いwrapperで接続しました。

入口:

`runtime/integration/run_tei_version_exchange_from_github.py`

PR #280以降、one-shot wrapper自身も既存の副作用なしGitHub preflightを必ず先行させます。

```text
same side-effect-free preflight
  -> ready
  -> GitHub Git Data API acquisition
  -> exact-B detached checkout
  -> canonical source verification
  -> existing canonical E2
  -> existing canonical E3
```

preflightが`blocked`の場合、wrapper report path準備、source用temporary directory作成、GitHub source acquisition、Evidence output作成より前に停止します。standalone preflightはoperatorがactual前に`blockedChecks`を確認する入口として残し、one-shotを直接起動しても同じpreflightを飛ばせない構成にしています。

wrapperはE2/E3の判定ロジックを複製しません。source acquisition Provenanceだけを別reportへ保持し、canonical E2/E3のstage vocabulary / comparison axis / Evidence bundle / failure semanticsは既存runnerを正とします。

credential値や一時source pathはwrapper reportへ保存しません。wrapper report publishはunique temporary file + flush/fsync + publish直前path再検査 + atomic replaceを使用します。

PR #261では、wrapperの内側で正本となる`run_tei_version_exchange_evidence.py`のcanonical Evidence report publishにも同じ考え方を適用しました。固定`.tmp`名を使わず、同一directoryのunique temporary fileへwrite + flush/fsyncした後、final pathを再検査してatomic replaceします。E2/E3 stage semantics、bundle、comparison axisは変更していません。

PR #278では、E2でactual build / Provider Plan / bundle verificationを終えた後の最終Evidence archive publishを、output filesystem上のunique temporary file + flush/fsync + publish直前path再検査 + `os.link()`によるno-overwrite publishへ変更しました。actual実行中に同名file / symlinkが現れても暗黙上書きやsymlink追随をしません。

PR #281では、canonical bundle / canonical report / GitHub wrapper reportの出力pathをactual開始前preflightでsymlink検査へ揃えました。dangling symlinkも`--overwrite`で削除して続行せず、canonical runnerとGitHub preflightの両方でactual開始前に拒否します。

PR #283では、GitHub one-shotがrevision B sourceをmaterializeするtemporary parentもpreflight境界へ上げました。temporary parentがSOZA repository、revision A checkout、Evidence directoryの内部にある場合や、path自身またはancestorがsymlinkの場合はsource acquisition前に拒否します。preflight後もactual source acquisition直前に同じhelperを再実行し、検証済みparentを`TemporaryDirectory(dir=...)`へ明示します。

PR #284では、temporary parentのpreflightで`tempfile.gettempdir()`を使わないよう修正しました。Pythonの`gettempdir()`は初回解決時にcandidate directoryへtemporary fileをcreate/write/deleteして利用可否をprobeするため、「副作用なしpreflight」と両立しません。現在はLinux actual scopeに合わせて`TMPDIR` → `TEMP` → `TMP` → `/tmp`の順で候補を選び、存在・directory・symlink境界・write/traverse accessをread-onlyで確認します。actual runで初めて検証済みparent配下へtemporary directoryを作成します。

## 4. actual開始前preflight

actual source取得・checkout preparationを始める前に不足条件を一括確認する副作用なしpreflightは、取得経路ごとに分かれます。

### 4.1 GitHub acquisition経路

PR #260 の入口:

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
- canonical bundle / report / wrapper report pathがsymlinkまたはsymlink ancestor経由でないこと
- revision B source temporary parentのstatic safety
  - `TMPDIR` → `TEMP` → `TMP` → `/tmp`の順で候補を選ぶ
  - SOZA repository / revision A checkout / Evidence directory配下を拒否する
  - path自身またはancestorのsymlinkを拒否する
  - existence / directory / write-traverse accessをfile createなしで確認する

preflightはGitHub APIへ接続せず、revision B sourceをmaterializeせず、Evidence outputを作成しません。また最初のfailureで停止せず、全checkを実行して`blockedChecks`へ不足をまとめます。PR #284以降、`source_temp_parent` checkもcandidate directoryへprobe fileを作らないため、この副作用なし境界と一致します。

PR #280以降は`run_tei_version_exchange_from_github.py`もこのpreflightをsource acquisition前に再利用します。したがってstandalone preflightを先に実行する標準手順はoperatorが不足条件を確認するために維持しますが、one-shot actual path自体も`ready`を要求します。PR #283以降はpreflightが`ready`でもsource acquisition直前にtemporary parentを再検査し、unsafeへ変化していればacquisitionを開始しません。

### 4.2 local prepositioned経路

local Git object databaseを使う場合は次を使います。

`runtime/integration/preflight_tei_version_exchange_local.py`

検査対象:

- Linux / amd64
- source cloneがGit worktreeであること
- source cloneのGit object databaseがalternatesへ依存せずself-containedであること
- fixed revision B commit objectが存在すること
- revision B commitから見た`cmd` / `internal` / `reference` / `go.mod` / `go.sum` object identityが固定値へ一致すること
- exact revision A fixed reference input identity
- current SOZA source identity / boundary purity / optional expected HEAD
- E2 Go `go1.23.2` exact match
- E3 Goがcurrent `runtime/go/go.mod`のdirective以上であること
- future exact-B checkout outputが新規pathであり、source clone / SOZA / A checkout / Evidence outputと重ならないこと
- Evidence outputがsource clone / future B checkout / SOZA / A checkoutと重ならず、historical A bundleを包含しないこと

local preflightはcredentialもnetwork accessも要求しません。source cloneを変更せず、B checkoutもEvidence outputも作成しません。

```text
local preflight ready
  != revision B checkout prepared
  != E2 PASS
  != E3 PASS
```

両preflightとも、execution mechanismの違いをCapability identityへ持ち込みません。

### 4.3 E2 / E3 Go process-level build surface

PR #279では、同じsource / Go versionでも親processからbuild/test結果を変え得るprocess-level Go overrideを、E2 buildとE3 live testで対称に分離しました。

固定:

```text
GOWORK=off
GOENV=off
GOTOOLCHAIN=local
```

親environmentから除外:

```text
GOFLAGS
GOOS
GOARCH
GOAMD64
GOEXPERIMENT
CGO_ENABLED
```

`PATH`、`GOPROXY`、`GOMODCACHE`等のtool discovery / module acquisition設定はこの境界では維持します。したがってこれはmodule acquisitionやhost全体をhermeticにする主張ではありません。

```text
process-level Go build/test surface isolated
  != module acquisition hermetic
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

このcontainerでGitHub acquisition経路のactual runを開始できない理由は少なくとも次の2点です。

```text
private GitHub credential / private-source transport
E3 Go 1.25 toolchain
```

local prepositioned経路ならGitHub credentialは不要ですが、current containerにはrevision B commit objectを含むself-containedなTEI local source cloneも配置されていません。またE3 Go >=1.25不足はlocal経路でも共通です。

したがってcurrent containerでは、どちらの取得経路でもactual E2→E3には進めません。

これはProduct failureではありません。

```text
environment prerequisite missing
  != TEI version exchange incompatibility observed
```

## 6. 次回actual実行の標準手順

actual実行環境には共通して次を準備します。

- current SOZA checkout
- revision A fixed input
  - exact revision A checkout、または
  - verified historical revision A Evidence bundle
- E2用Go 1.23.2
- E3用Go 1.25以上でcurrent `runtime/go/go.mod`を満たすexecutable
- SOZA / revision A checkout外のEvidence output directory

まずcurrent SOZA HEADを固定します。

```bash
SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"
```

### 6.1 GitHub one-shot経路

追加でprivate `hat47x/tei-platform`をread可能な`GITHUB_TOKEN`または`GH_TOKEN`を準備します。

source temporary parentは`TMPDIR`、`TEMP`、`TMP`のうち最初に設定されたpath、いずれも未設定なら`/tmp`です。明示設定する場合はSOZA repository / revision A checkout / Evidence directoryの外側にあるexisting non-symlink directoryを使います。preflightで`source_temp_parent`がblockedになった場合は、この環境変数またはpath境界を確認します。

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

one-shot runner自身も同じ副作用なしpreflightを再実行し、`ready`でなければsource acquisitionより前に停止します。したがって上段のstandalone preflightは事前確認・blockedChecksの把握用であり、actual runner側の安全性をoperator手順だけへ依存させません。source temporary parentもactual source取得直前に再検査します。

### 6.2 local prepositioned経路

追加で、fixed revision B commit objectを含むself-containedなlocal TEI source cloneと、新規のB checkout output pathを準備します。

まず副作用なしpreflightを実行します。

```bash
python3 "$SOZA_REPO/runtime/integration/preflight_tei_version_exchange_local.py" \
  --source-repo "$TEI_SOURCE_CLONE" \
  --checkout-output "$TEI_B_REPO" \
  --reference-evidence-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$EVIDENCE_DIR" \
  --tei-go-executable "$TEI_GO" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

`result=ready`を確認した後に、exact-B checkoutを準備します。post-run acquisition provenanceも残す場合はhelper自身のsafe report outputを使います。

```bash
python3 "$SOZA_REPO/runtime/integration/prepare_tei_revision_b_checkout.py" \
  --source-repo "$TEI_SOURCE_CLONE" \
  --output-repo "$TEI_B_REPO" \
  --report-output "$CHECKOUT_PREPARATION_REPORT" \
  --json
```

`--report-output`はsource/output checkout外の新規non-symlink pathを要求します。report publishに失敗した場合、その呼び出しで作成したB checkoutも撤去します。

そのcheckoutをcanonical E2→E3 runnerへ渡します。

```bash
python3 "$SOZA_REPO/runtime/integration/run_tei_version_exchange_evidence.py" \
  --source-repo "$TEI_B_REPO" \
  --reference-evidence-bundle "$TEI_A_BUNDLE" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$EVIDENCE_DIR" \
  --tei-go-executable "$TEI_GO" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

exact revision A checkoutを使う場合は、各commandの`--reference-evidence-bundle`を`--reference-source-repo "$TEI_A_REPO"`へ置き換えます。

actual後のResolution auditは`TEI_VERSION_EXCHANGE_POST_RUN_AUDIT_2026-09-06.md`を正とします。GitHub経路とlocal経路で入口は異なりますが、Resolution条件1〜8の意味は変えません。

## 7. actual runで初めて上げられるEvidence

preflight / source acquisition implementation / synthetic regressionだけでは、次を主張しません。

actual runが成功した場合に初めて、fixed scopeについて次を観測できます。

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

local exact-B checkout preparation safe report output
  = implemented

local exact-B source preflight
  = implemented

GitHub content-addressed exact-B acquisition
  = implemented

GitHub acquisition credential redirect boundary
  = enforced

GitHub acquisition -> canonical E2/E3 wrapper
  = implemented

GitHub one-shot automatic preflight before acquisition
  = implemented

GitHub source temporary parent preflight / actual recheck
  = implemented

GitHub source temporary parent side-effect-free resolution
  = implemented; TMPDIR -> TEMP -> TMP -> /tmp, no gettempdir write probe

TEI source Git object / config environment isolation
  = implemented for canonical verifier, local preflight/preparation, and GitHub acquisition

E3 SOZA source Git environment isolation
  = implemented

E2/E3 process-level Go build/test environment isolation
  = implemented

E2 Evidence bundle no-overwrite / symlink-safe publish
  = implemented

canonical bundle/report/wrapper output symlink preflight
  = implemented

wrapper report publish TOCTOU guard
  = implemented

canonical Evidence report publish TOCTOU guard
  = implemented

GitHub actual-run preflight
  = implemented

local actual-run preflight
  = implemented

GitHub/local post-run Resolution audit
  = implemented

current container E2 Go 1.23.2
  = available

current container private GitHub credential
  = not available

current container self-contained TEI source clone with revision B
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