# ISSUE-000073 — Decision Continuity 実行準備状態

更新日: 2026-10-10  
状態: **Current Execution Readiness / Scoped Executable Evidence Available / Human Evidence Pending**

## 1. この文書の役割

この文書は、ISSUE-000073で進めているresume-first Product Sliceについて、Candidate Requirement監査、Stable Requirementへのformalization、E1〜E8 prototype、Evidence runner / verifier / capture、H1 / H2 human reviewの現在位置を一つにまとめるcurrent-state文書です。

実行手順の詳細は、機械実行とhuman reviewで入口を分けます。

- E1〜E8: 本書のcapture / runner / verifier手順
- H1 / H2: `DECISION_CONTINUITY_HUMAN_REVIEW.md`

既存の`DECISION_CONTINUITY_REQUIREMENT_AUDIT_2026-09-16.md`は、formalization前に行った監査時点のDesign Evidenceとして保持します。後から得た結論でその監査記録を書き換えません。

```text
historical Requirement audit
  != current Stable Requirement baseline
  != Executable Evidence
  != human Product Evidence
```

## 2. Requirement formalizationの現在地

CR-73.1〜CR-73.10を一件ずつ再照合した結果、すべてを新しいStable Requirementへ昇格させる判断は採りませんでした。

CR-73.1〜73.7および73.10は、既存REQ / SCNで表現できるsemantic boundary、Product / Policy localな責務、またはH1 / H2で観測すべきhuman outcomeへ戻しています。

一方、CR-73.8 Meaning-preserving commitとCR-73.9 Stale-write protectionについては、既存REQだけではsuccessful canonical commitのfailure boundaryを直接禁止しきれないと判断しました。両者は別々のUniversal mechanismへ分けず、一つの規範へ統合しています。

- **REQ-0023 — Canonical commitの整合性**
- **SCN-0019 — 途中失敗・stale draftを含むcanonical commit**

このformalizationで要求しているのは、successful commitとして公開されるcanonical meaningの整合性です。transaction、atomic replace、generation、digest、snapshot token等の実現方式をUniversal semanticsへ固定していません。

```text
REQ-0023 / SCN-0019
  != Universal Transaction entity
  != Universal Snapshot entity
  != Semantic Revision = concurrency version
```

Design Evidenceに加え、2026-10-09のactual E6 / E7 runでpartial commitとstale writeのfailure behaviorを確認しました。したがってREQ-0023 / SCN-0019には、Local Single-Node上のProduct-local probeに限定したScoped Executable Evidenceがあります。Production永続層や他Storage profileへは一般化しません。

## 3. E1〜E8 prototypeの現在地

`runtime/go/interactionprobe`には、E1〜E8へ対応するprototype / test sourceがあります。

- E1 — canonical-only resume
- E2 — AI correction / dismissal
- E3 — AI unavailable
- E4 — progressive explicitness
- E5 — working-set rebuild
- E6 — semantic commit fault injection
- E7 — stale draft
- E8 — external AI context boundary

sourceやtest名が存在することはExecutable Evidenceではありません。実行結果を固定するため、次のrunnerを用います。

```text
tools/run_issue_000073_resume_first_evidence.py
```

runnerはGo 1.25.xを要求し、`GOTOOLCHAIN=local`で`runtime/go/interactionprobe`を実行します。

さらに、次の条件を満たさないcheckoutではE1〜E8を実行せず`blocked`とします。

- readableなGit HEADがある。
- checkout外で独立に取得したcanonical expected HEADとactual HEADが完全一致する。
- working treeがcleanである。
- runner自身、`go.mod` / `go.sum`、主要test sourceがHEADと一致する。
- required sourceが欠けていない。
- active Go toolchainが1.25.xである。

低いGo versionやdirty checkoutで得たPASSをISSUE-000073のEvidenceへ読み替えません。

## 4. Evidence verifier

runnerが出力したJSONも自己申告のまま受理しません。次のvalidatorで、recorded tested commitへ戻って再検証します。

```text
tools/verify_issue_000073_resume_first_evidence.py
```

validatorは少なくとも次を確認します。

1. Evidence format / Issue / stop lineが期待値と一致する。
2. `status=pass`であり、clean checkoutとして記録されている。
3. recorded `repository.head`が実際のGit commitとして解決できる。
4. recorded `head_tree`がそのcommitのtreeと一致する。
5. Go 1.25.xが記録されている。
6. 実行commandが`go test -count=1 -json ./interactionprobe`で、`GOTOOLCHAIN=local`である。
7. runnerが列挙した各source bindingについて、recorded HEAD上のblobと一致する。
8. 各sourceのSHA-256をrecorded HEADのbytesから再計算し、一致する。
9. E1〜E8の全experimentが`pass`である。
10. 各experimentに必要な個別testがすべて`pass`である。

Evidence JSON自体を後からrepositoryへcommitしてHEADが進んでも、validatorはrecorded tested commitを参照します。そのため、Evidence保存commitとtested commitを同一commitに見せかける必要はありません。

```text
commit T: actual test対象
  ↓ runner
Evidence JSON records T
  ↓
commit T+1: Evidence JSONを保存
  ↓ verifier
Git object T + source blobsを再検証
```

## 5. runner / verifier / capture workflow self-test

runner preflightについては、stdlibだけでsynthetic Git repositoryを作るself-testを持ちます。

```text
tools/test_run_issue_000073_resume_first_evidence.py
```

現在固定している主な境界は次です。

- canonical expected HEAD不一致をblockedにする。
- dirty checkoutをblockedにする。
- required source binding欠落をblockedにする.
- Go 1.25.x未満をblockedにする。

2026-09-18にcurrent runner sourceへ対してactual実行し、PASSを確認しました。

```text
PASS: ISSUE-000073 evidence runner preflight self-tests
```

validatorについてもstdlibだけでsynthetic Git repositoryを作るself-testを追加しています。

```text
tools/test_verify_issue_000073_resume_first_evidence.py
```

現在確認したcase:

- cleanなPASS recordを受理する。
- Evidence保存後にHEADが進んでもrecorded tested HEADを検証できる。
- source SHA-256改ざんを拒否する。
- `expected_head != head`または`head_matches_expected != true`を拒否する。
- dirtyと記録されたEvidenceを拒否する。
- E8 failを拒否する。
- repositoryに存在しないtested HEADを拒否する。
- Go 1.24.xを拒否する。

2026-09-18にcurrent verifier sourceへ対してactual実行し、PASSを確認しました。

```text
PASS: ISSUE-000073 evidence verifier self-tests
```

runner / verifier self-testのcurrent source bindingとactual実行結果は、次のmachine-readable Evidenceへまとめて固定しています。

```text
evaluation/personal-inquiry-decision/evidence/issue-000073/runner-verifier-selftests-2026-09-18.json
```

実行環境はPython 3.13.5 / git 2.47.3です。Python host固有のspreadsheet-runtime warmup警告がstderrへ出ましたが、`py_compile`、runner preflight self-test、verifier self-testはいずれもexit code 0で、self-testは期待するPASS stdoutを返しました。この環境警告をrepository test failureへ読み替えません。

また、runner → verifier → Evidence保存を一命令でfail-closedに連結するcapture入口を追加しています。

```text
tools/capture_issue_000073_resume_first_evidence.py
```

captureは次を守ります。

- runnerがblocked / failならverifierへ進まず、raw診断Evidenceだけを保存する。
- runnerのexit codeだけをEvidence stateとして信用せず、readable JSON recordとの整合を要求する。
- runnerがzero exitでも`status=pass` recordを出していなければfailとする。
- runnerがrecordを生成できない異常終了ではverifierへ進まず、wrapper自身も例外終了せずfail-closedにする。
- verifier failureをPASSへ昇格させない。
- 既存Evidenceを暗黙に上書きせず、意図的な再実行では`--replace`を要求する。
- `--replace`中にrunner record生成自体が失敗した場合、旧Evidence / verificationを残して新runと誤認させない。
- 一時artifactをcheckout外へ置き、capture自身がrunnerのclean-tree preconditionを壊さない。
- verified E1〜E8をH1 / H2 / Product Valueへ自動昇格しない。

2026-09-18に、PR #428でfail-closed境界を補強したcurrent sourceに対して、`py_compile`とcapture workflow self-testをactual実行しました。

```text
Python 3.13.5
git version 2.47.3
PASS: ISSUE-000073 capture workflow self-tests
```

実行対象は、次のsource blobへ固定しています。

```text
tools/capture_issue_000073_resume_first_evidence.py
  git blob: 70c936314e4810b7f038f86b86e7b2d32cb9f8cb
  sha256: d33f6551c7e8307be45f603ac92c3a505ab9b5d19f1b7d2f2412496054a864e6

tools/test_capture_issue_000073_resume_first_evidence.py
  git blob: 65c7a0c7379184636d1ddfb1bd113ce55f40d710
  sha256: f48012a3eb1295cc0b7479779f0fd159e398e99a4dd55f9aa1dc7edf04359dc8
```

machine-readable Evidenceは次へ保存します。

```text
evaluation/personal-inquiry-decision/evidence/issue-000073/capture-workflow-selftest-2026-09-18.json
```

このPASSはcapture workflowの受入れ経路だけに限定したExecutable Evidenceです。E1〜E8自体のGo Executable Evidence、H1 / H2 human review、Decision Continuity Product Valueには昇格させません。

## 6. actual E1〜E8実行手順

Go 1.25.xが利用可能なclean checkoutでは、通常はcapture入口を使います。

```text
git status --porcelain=v1
python tools/capture_issue_000073_resume_first_evidence.py --expected-head <canonical-commit-sha>
```

hostにGo 1.25.xがない場合は、2026-10-07に追加したbootstrap入口から同じcaptureへ接続できます。

```text
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>
```

bootstrapは、明示された`GO_BINARY_PATH`、host上のGo 1.25.x、または固定済みGo 1.25.14 Linux / amd64 archiveの順に利用可能なtoolchainを選びます。自動取得用archiveは次のidentityへ固定しています。

```text
go1.25.14.linux-amd64.tar.gz
sha256:a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712
```

事前配置済みtoolchain / archiveも利用できます。

```text
GO_BINARY_PATH=/path/to/go \
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>

GO_TOOLCHAIN_ARCHIVE_PATH=/path/to/go1.25.14.linux-amd64.tar.gz \
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>
```

toolchainは既定でcheckout外のcacheへ置きます。archive digest不一致、不完全な既存cache、dirty working treeはfail-closedにし、低いGoで代替PASSを作りません。bootstrap自身はE1〜E8の判定を持たず、最終的な実行・Evidence保存・再検証は既存capture / runner / verifierへ委ねます。

追加したscriptのexact Git blob `8ec0d66aca9b16657c170f784ca2642ecdb309d8`について、`bash -n`、事前配置Go 1.25.xからcaptureへの引数受け渡し、dirty-tree拒否、直接`--go`指定による迂回拒否をsynthetic Git repositoryで実行し、いずれもPASSを確認しました。machine-readable recordは`evidence/issue-000073/go125-bootstrap-mechanics-2026-10-07.json`です。これはbootstrap mechanicsだけのScoped Executable Evidenceであり、固定archiveのmaterializationやE1〜E8 actual executionには昇格させません。


### private GitHubへ接続できない実行nodeへのexact-source handoff

実行nodeがprivate GitHubへ接続できなくても、source snapshotを別identityへ置き換えずに既存captureへ進めるよう、clean canonical checkoutからGit bundleを作る入口を用意しています。

```text
tools/prepare_issue_000073_external_execution_bundle.py
```

canonical checkout側:

```text
python3 tools/prepare_issue_000073_external_execution_bundle.py \
  --expected-head <canonical-commit-sha> \
  --output-dir <outside-repository-directory>
```

出力は`.gitbundle`、manifest、`SHA256SUMS`の3点です。preparerはactual HEADと独立に与えたexpected HEADの一致、clean working tree、repository外outputを要求し、`git bundle verify`後にだけhandoff artifactを確定します。

外部nodeではbundleからcloneして同じcommit SHAへ戻り、その後にGo 1.25.x bootstrap / captureを実行します。

```text
git clone <bundle>.gitbundle sei-cognition-e73
git -C sei-cognition-e73 rev-parse HEAD
cd sei-cognition-e73
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>
```

2026-10-09にはpreparerとself-testのexact committed Git blobをmaterializeし、synthetic Git repositoryで次の5件をactual実行して5/5 PASSしました。

- bundleからcloneした先がexact source HEADへ戻り、cleanである。
- expected HEAD不一致を拒否する。
- dirty sourceを拒否する。
- source repository内のoutput directoryを拒否する。
- 既存handoff artifactは`--replace`なしで上書きしない。

machine-readable recordは`evidence/issue-000073/external-execution-bundle-mechanics-2026-10-09.json`です。このPASSはhandoff mechanicsだけに限定します。このセッションではactual SEI checkoutからbundleを作成しておらず、外部nodeでreal bundleをcloneしてE1〜E8を実行してもいません。

受け側は`tools/run_issue_000073_external_execution_bundle.py`へ一本化しています。runnerはbundle / manifest / SHA256SUMSを検証し、manifestのexact source HEADとbundleのadvertised HEADを照合してからcloneします。clone後にもHEAD、clean working tree、`git bundle verify`を確認し、既存bootstrap / captureを呼び出します。

```text
python3 tools/run_issue_000073_external_execution_bundle.py \
  --bundle <bundle.gitbundle> \
  --manifest <bundle.manifest.json> \
  --sha256sums <bundle.SHA256SUMS> \
  --work-dir <new-work-dir> \
  --result-dir <outside-work-dir-result>
```

result directoryには`e1-e8.json`、`e1-e8-verification.json`、bootstrap stdout / stderr、`external-run.json`を分離して保存します。bootstrapが実行前提不足を`blocked`として返した場合、verificationを生成したことにはせず、external runも`blocked`のまま残します。

preparer / receiver / self-testのexact committed blobを使ったsynthetic integrationでは、成功経路、same-size bundle改ざん拒否、manifestのexpected HEAD改変拒否、bootstrap blocked非昇格の4件をactual実行し4/4 PASSしました。Evidenceは`evidence/issue-000073/external-execution-runner-mechanics-2026-10-09.json`です。synthetic bootstrapによるmechanics testなのでactual E1〜E8へは昇格させません。

既定では次へ保存します。

```text
evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json
evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json
```

意図的に既存Evidenceを置き換える場合だけ`--replace`を指定します。`<canonical-commit-sha>`はcheckout自身から自己申告させず、GitHub等の独立したrepository正本から取得します。captureが`pass`になった場合でも、tested commitはEvidence JSON内の`repository.head` / `repository.expected_head`一致で固定し、後のEvidence保存commitと混同しません。

runner / verifierを個別に診断したい場合は、次を使えます。

```text
python tools/run_issue_000073_resume_first_evidence.py \
  --expected-head <canonical-commit-sha> \
  --output evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json

python tools/verify_issue_000073_resume_first_evidence.py \
  evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json \
  --json-out evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json
```

### 2026-09-18に観測した実行環境blockerと2026-10-07の取得経路更新

この作業セッションの実行環境では、host toolchainは次でした。

```text
go version go1.23.2 linux/amd64
```

Go自身のtoolchain自動取得でGo 1.25.0を起動できるかもactualに確認しました。

```text
GOTOOLCHAIN=go1.25.0+auto go version
```

しかし`proxy.golang.org`への名前解決 / 外向き通信が実行環境側で拒否され、Go 1.25.0 toolchainを取得できませんでした。

2026-09-18 19:53 JSTには、同じ取得経路の再試行ではなく、別経路としてGo公式配布先をdirect probeしました。

```text
curl -I --max-time 10 https://go.dev/dl/go1.25.0.linux-amd64.tar.gz
  -> curl: (6) Could not resolve host: go.dev

curl -I --max-time 10 https://dl.google.com/go/go1.25.0.linux-amd64.tar.gz
  -> curl: (6) Could not resolve host: dl.google.com
```

filesystem上のGo / Go 1.25.x candidateも走査し、確認できたのは`/usr/local/go/bin/go`のみでした。そのbinaryは`go1.23.2 linux/amd64`です。したがって、toolchain auto-downloadだけでなくofficial direct distribution経路も現在のexecution environmentでは利用できず、preinstalled Go 1.25.xも存在しません。

この結果はrepository test failureではなく、**actual E1〜E8実行に必要なtoolchainを現在の実行環境で用意できないenvironment blocker**として扱います。観測は`evidence/issue-000073/go-toolchain-acquisition-blocker-2026-09-18.json`へmachine-readableに固定しています。

2026-09-18の観測時点では、Go 1.23.2で代替PASSを作らず、E1〜E8 actual runを**Not Yet Verified**として保持しました。

2026-10-07には、repository内で後から固定されたGo 1.25.14 Linux / amd64 archive identityを用いる専用bootstrap入口を追加しました。この変更により、repository toolingとしては事前配置済みGo、事前配置済みarchive、またはnetworkが利用できる環境から既存captureへ到達できます。ただし、この時点では新入口によるE1〜E8 actual runは未取得でした。

2026-10-09には、事前配置済みGo 1.25.14を使い、tested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`でE1〜E8をactual実行しました。必須18 testはすべてpassし、`go test`全体も31 pass / 0 fail、verifierはfindings 0でPASSしました。これはbootstrap wrapperのpinned archive materialization経路ではなく、事前配置toolchainによるScoped Executable Evidenceです。

2026-10-10にはtested commitとcurrent developの実行対象source closureを再照合し、`interactionprobe` 22 file、`semanticruntime` 13 file、Go依存定義2 file、runner / verifier 2 fileの計39 fileが全て同一であることを確認しました。machine-readable recordは`evidence/issue-000073/e1-e8-current-source-closure-2026-10-10.json`です。これは新しいtest実行ではなく、既存PASSが未変更のcurrent source closureへ適用できることの確認です。

```text
2026-09-18 environment could not acquire Go 1.25.x
  != interactionprobe FAIL

bootstrap path available
  != E1-E8 actual PASS
  != H1 / H2 human review
  != Decision Continuity Product Value established
```

## 7. PASS後に更新してよいEvidence

capture内のrunnerとvalidatorがともにPASSした場合、E1〜E8については対象commitに限定したScoped Executable Evidenceとして扱えます。

特にE6 / E7については、REQ-0023 / SCN-0019が求める次のfailure behaviorに対するExecutable Evidence候補になります。

- mid-commit faultでpartial canonical stateをsuccessful commitとして公開しない。
- later validation failureで先行changeだけを公開しない。
- stale draftがnewer canonical stateを黙ってoverwriteしない。

ただし、次を自動的には更新しません。

```text
E1-E8 Executable PASS
  != H1 human resume usability observed
  != H2 counterfactual Product Value observed
  != capture / review overhead acceptable
  != Operational Evidence
  != Adoption / Outcome Evidence
  != ISSUE-000073 Resolved
```

## 8. H1 / H2の現在地

H1 actual resume usability reviewとH2 counterfactual Decision Continuity reviewは、実際の人間による観測が必要です。

現時点ではいずれも**Not Yet Observed**です。

具体的な実行手順は`DECISION_CONTINUITY_HUMAN_REVIEW.md`へ一本化しています。

### H1 — real Inquiryのactual resumption

H1では、`DOGFOOD_SURFACE.md`のactual Inquiry stateと`DOGFOOD_EVALUATION_RECORDING.md`のevaluation sidecarを再利用します。別のH1専用schemaやsession managerは作りません。

chat historyや内部schemaの知識へ戻らず、Orientationからcurrent question、Decision、historical basis、unresolved、post-decision changes、next review pointへ戻れるかを観測します。

暦上のgapだけではH1にしません。再開直前にcurrent concernやDecision basisへmaterialな再露出があった場合はclean resumptionとして数えず、架空の`resume_observation`を追加しません。

```text
calendar gap
  != cognitive gap

pre-orientation material exposure
  != H1 resumption Evidence
```

### H2 — matched counterfactual review

H2では、raw chat、chronological note、SEI Resume Projectionを同等素材で比較します。reviewer provenanceを最初のstimulus提示前に固定し、condition labelを伏せたbundle、global stage gate、Decision固有validationを用いて、post-decision materialやreference stateを先に見ないようにします。

正規入口は073/078で共有する`inquiry_continuity_review_runner.py`です。Decision専用runnerやsession managerは増やしません。初期sessionはexclusive-createし、同じpathへの再`init`を拒否します。provenance付きsessionについては低レベル`matched_review_session.py` CLIの`packets` / `record`も拒否し、Issue固有validationを迂回してstageを進めないようにします。complete reviewのEvidence exportも同じrunnerの`export-evidence`から行います。

例は次のとおりです。

```text
RUNNER=evaluation/personal-inquiry-decision/inquiry_continuity_review_runner.py
MANIFEST=evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json

python "$RUNNER" --manifest "$MANIFEST" --repo-root . init \
  /tmp/e73-review-session.json \
  --rotation R1 \
  --session-id e73-r1-reader-001 \
  --created-at <timestamp> \
  --reviewer-id <opaque-reviewer-id> \
  --prior-exposure <none-declared|known-material-exposure|unknown> \
  --response-authorship <human-direct|human-transcribed>

python "$RUNNER" --manifest "$MANIFEST" --repo-root . bundle \
  /tmp/e73-review-session.json

python "$RUNNER" --manifest "$MANIFEST" --repo-root . export-evidence \
  /tmp/e73-review-session.json \
  --output /tmp/e73-review-evidence.json
```

exportはcompleted sessionだけを受理し、human-review observationとsemantic auditを別collectionとして保持します。review provenanceも同じbundleへ残しますが、申告metadata自体を盲検やhuman authorshipの独立証明にはしません。synthetic reviewをH1 actual resumptionやProduct Valueへ昇格させません。

H2 shared runnerのDecision regression testは、clean checkoutで次のcaptureから実行・Evidence保存できます。

```text
python3 tools/capture_issue_000073_h2_runner_selftest.py --expected-head <canonical-commit-sha>
```

captureはclean committed HEADに加えて、checkout外で取得したcanonical commit SHAを`--expected-head`で必須指定し、actual HEADとの完全一致を要求します。さらにmatched-set manifest / 3 fixtureを含む13 required sourceのHEAD blob一致を検証し、`test_decision_continuity_review_runner.py`のexit codeとstdout / stderrをmachine-readable recordへ固定します。既存recordの置換は`--replace`を明示した場合だけ許可します。

2026-09-18の本Issue作業では、R1相当のphase1 materialがprovenance固定前に一度提示されましたが、human responseは固定されませんでした。この提示はH2 observationには数えません。同じreaderで後続reviewを行う場合は`known-material-exposure`として記録し、clean blinded reviewとは呼びません。

```text
H2 evidence bundle
  != H1 actual resumption
  != actual capture burden
  != Product Value established
```

synthetic fixtureやAI生成回答をhuman observationとして代用しません。また、同じ人がreference stateを事前に見たcaseをblind reviewとして扱いません。

2026-09-18の追加監査では、current `decision_continuity_counterfactual_matched_set_v1.json`と3 fixtureをGitHub上の正本bytesから再照合し、manifest schema / Issue、各fixtureの単一Decision、basis / Recommendation / unresolved参照、reference stateとの一致、post-decision id境界、A/B/C condition、R1〜R3の割当構造がすべて整合していることを確認しました。これは**static source audit**であり、Pythonの`decision_continuity_preflight.py`またはfocused unittestをactual実行したEvidenceではありません。

同じdriftを今後自動検出できるよう、`test_decision_continuity_review_runner.py`にはcurrent repositoryのDecision manifest / fixtureを`load_context → new_session → reviewer_bundle`で開くintegration caseを追加しました。source追加だけをtest PASSとは扱いません。

2026-09-18には、tested commit `42872959a13746eb5fd87f1fe10233ccd55caac0` のH2 Decision regression関連12 sourceをGitHub正本からmaterializeし、各fileのGit blob SHA-1がtested commitと完全一致することを確認したうえで、`python3 -m unittest -v test_decision_continuity_review_runner.py`をactual実行しました。8 tests / 8 PASS、exit code 0です。tested commit以降からdevelop `af3e959e0dabee9b3a5ea60018c2f11e662efcb8`まで、対象12 sourceに差分がないことも確認しています。

この実行はexact blob-validated materialization上のExecutable Evidenceであり、native Git clean checkout上で`capture_issue_000073_h2_runner_selftest.py`を通したactual captureではありません。そのためfocused regression本体のPASSとcapture未実行を分離して保持します。machine-readable recordは`evidence/issue-000073/h2-decision-review-runner-regression-2026-09-18.json`です。

## 9. 現在のEvidence状態

| 項目 | 状態 |
|---|---|
| Product / Architecture Design | Satisfied for current design scope |
| Candidate Requirement audit | Completed as Design Evidence |
| REQ-0023 / SCN-0019 formalization | Accepted / Design Satisfied |
| E1〜E8 test source | Available |
| Evidence runner preflight self-test | **PASS on canonical-HEAD-bound current source (2026-09-18); delta Evidence recorded** |
| Evidence verifier self-test | **PASS on canonical-HEAD-bound current source (2026-09-18); delta Evidence recorded** |
| One-command capture workflow self-test | Historical full PASS retained; **canonical-HEAD deltaは8 case actual + same-output focused preflight actualで確認** |
| E1〜E8 actual Go 1.25.x run | **PASS — 2026-10-09, tested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`, go1.25.14 linux/amd64, required 18/18 pass, full package 31 pass / 0 fail, verifier findings 0** |
| E1〜E8 current-source applicability | **PASS — 2026-10-10, 39 / 39 source-closure blob一致。existing actual PASSは未変更のcurrent source closureへ適用可能。新しいtest実行ではない** |
| Go 1.25.x execution path | **Pre-provisioned go1.25.14 actual path PASS。Repository bootstrapは利用可能。2026-09-18 blockerはhistorical Environment Evidenceとして保持し、pinned archive materialization経路だけはNot Yet Verified** |
| Go 1.25 bootstrap mechanics | **PASS for exact-script syntax / pre-provisioned Go forwarding / dirty-tree guard / direct --go bypass guard; archive materialization Not Yet Verified** |
| External exact-source handoff mechanics | **PASS — exact committed blobs, 5/5 synthetic Git bundle tests (2026-10-09); actual handoff execution is a reproducibility/portability follow-up, not an ISSUE-000073 resolution blocker now that direct actual E1〜E8 PASS exists** |
| External handoff receiver mechanics | **PASS — exact committed blobs, 4/4 synthetic integration tests (2026-10-09); actual external handoff execution remains optional supporting Evidence** |
| REQ-0023 / SCN-0019 Executable Evidence | **PASS at Product-local probe scope through E6 / E7 (2026-10-09); not generalized to other Storage profiles or Production persistence** |
| H1 actual human review | **Not Yet Observed** |
| H2 counterfactual human review | **Not Yet Observed** |
| H2 provenance-first shared runner / evidence-export tooling | Available; init is exclusive-create and low-level packets/record bypass is rejected; current Decision manifest / 3 fixture / R1-R3 structural contract was re-audited on 2026-09-18 and an actual-repository integration test source was added; Python focused test executionはexact blob-validated materialization上で8 tests / 8 PASSをactual確認済み; native clean-HEAD captureとactual human sessionはpending; prior R1 exposure is not a completed observation |
| H2 shared runner Decision regression test | **PASS — exact blob-validated materialization, 8 tests / 8 PASS (2026-09-18); machine-readable Evidence recorded** |
| H2 Decision regression Evidence capture workflow self-test | **PASS on canonical-HEAD / fixture-bound current source (2026-09-18); machine-readable Evidence recorded** |
| H2 shared runner Decision regression actual capture | **Not Yet Verified** |
| Decision Continuity Product Value | **Not Established** |
| Operational Evidence | **Not Yet Verified** |
| Adoption / Outcome Evidence | **Not Yet Verified** |

## 10. 次の停止線

E1〜E8のScoped Executable Evidenceは成立し、current source closureも未変更であることを確認しました。したがって、次の高情報量Evidenceはmachine rerunではなくhuman Product Evidenceです。

優先順位は次です。

1. materialなpre-orientation exposureのないreal InquiryでH1 actual resumptionを実施し、Orientationだけから現在地へ戻れるかを観測する。
2. H2 matched reviewをprovenance-first shared runnerからhuman readerで少なくとも一rotation実施し、completed sessionからEvidence bundleをexportする。clean blinded reviewが必要なら、割当materialへ未露出のreaderを使う。既知または不明のexposureは隠さずmetadataへ残す。
3. H1対象Inquiryのcapture / review overheadを既存sidecarで前向きに観測し、resume benefitを相殺していないか読む。後知恵でburden値を埋めない。
4. H1 / H2の結果をraw chat / chronological note等の単純baselineと比較し、Question 1〜4、8、10とDecision Continuity Product hypothesisを再評価する。
5. 条件6〜8の観測が揃った時点でISSUE-000073のResolutionを判断する。価値差が弱い、またはoverheadが上回る結果も正当な反証Evidenceとして扱う。
6. H2のnative clean-HEAD captureやexternal Git-bundle actual runは再現性を高める補助Evidenceとして並行実施できるが、human review開始をブロックしない。
7. E1〜E8は`interactionprobe` / `semanticruntime` / Go依存定義 / runnerの意味が変わった場合に再実行する。source closureが同一である限り、PASS維持だけを目的とする再実行は優先しない。

synthetic回答をhuman observationとして代用しません。pre-orientation exposureがあるsessionをclean blinded reviewへ読み替えず、速いorientationがhistorical correctnessを損なう場合も成功へ丸めません。

## 11. Natural Japanese review

2026-09-17の更新では、E1〜E8の入口をrunner / verifierの個別手順だけでなく、fail-closedなone-command captureへ一本化しました。個別runner / verifierは診断用として残し、Evidence保存の標準経路を増やしていません。

2026-09-18には、runnerがJSON recordを生成しない異常終了や、exit code 2だけでblockedと誤認する経路、failed `--replace`で旧PASS Evidenceが残る経路を追加で閉じました。補強後のcurrent sourceをactualに`py_compile` / self-test実行し、capture workflowについてPASSを確認しました。この結果はsource blobと実行環境をmachine-readable Evidenceへ固定していますが、E1〜E8 actual Go 1.25.x runとは分離しています。

同日、runner preflightとverifierについてもcurrent sourceを一時実行環境へ展開し、`py_compile`後にself-testをactual実行しました。両方ともexit code 0 / expected PASS stdoutを確認し、source blobと実行環境を別のmachine-readable Evidenceへ固定しました。これによりEvidence受入れ経路のPython self-test群はcurrent sourceに対して再確認済みですが、Go 1.25.xでinteractionprobeを実行したことにはしていません。

同日の実行環境確認では、host Goが1.23.2であることに加え、`GOTOOLCHAIN=go1.25.0+auto`によるGo 1.25.0取得も外向きDNS / network制限で成立しないことをactualに確認しました。このblockerをinteractionprobeのFAILとは扱わず、低いGoで代替PASSを作らない停止線を維持しています。

2026-10-07には、その後repository内で固定されたGo 1.25.14 Linux / amd64 archive identityを利用し、ISSUE-000073の既存captureへ接続するbootstrap入口を追加しました。toolchain materializationはcheckout外へ置き、archive digest不一致や不完全なcacheを暗黙に上書きせず停止します。この入口の追加はenvironment blockerを回避できる実行経路を増やしただけであり、E1〜E8を実際に実行したEvidenceには昇格させていません。

2026-10-09には、private GitHubへの接続可否とsource identityを分離するため、clean canonical checkoutをGit bundleとして外部nodeへ渡すhandoffを追加しました。preparer / self-testのexact committed blobで5件のmechanics testを実行し、同一HEADへのcloneと、expected HEAD不一致・dirty source・repository内output・暗黙上書きの拒否を確認しました。このhandoff経路自体のactual external runは未取得ですが、同じ日に別の事前配置go1.25.14環境でE1〜E8 actual PASSを取得したため、handoff actual runはISSUE-000073のResolutionをブロックしません。

同じhandoffを受け取るrunnerも追加し、transport checksum、manifest上のsource identity、bundle advertised HEAD、clone後のexact HEAD / clean state / bundle verificationを通過した後だけ既存bootstrap / captureへ進むようにしました。synthetic integrationの4件はexact committed sourceで4/4 PASSしました。blocked bootstrapはblockedのまま保存し、verificationを捏造しません。この結果もactual SEI E1〜E8実行には数えていません。

H1は既存dogfood stateとevaluation sidecarを利用し、real Inquiryのactual resumptionだけを観測します。H1専用のschemaやsession managerは増やしていません。H2は既存matched review基盤を利用し、073/078共通のreview runnerでstimulus提示前にreviewer provenanceを固定してからbundleを提示し、completed sessionのEvidence exportまで同じ経路を使います。2026-09-18にprovenance固定前のR1 material提示が一度発生したため、その提示を受けたreaderの後続sessionはknown exposureとして扱い、回答未固定の提示そのものはhuman Evidenceへ数えない停止線を追加しました。

同日、H2 shared runnerのDecision regression testをclean HEAD / source binding付きでactual実行できるcapture toolを追加しました。capture workflow自体のsynthetic self-testはactual PASSし、source blob / SHA-256 / Python / Git環境とともにmachine-readable Evidenceへ固定しています。capture workflow self-test自体のPASSはcapture受入れ経路だけのExecutable Evidenceです。2026-09-18の補強では、canonical expected HEAD不一致をblockedにし、manifest / 3 fixtureをsource bindingへ含めたcurrent capture sourceに対してself-testをactual再実行してPASSを確認しました。これとは別にDecision regression test本体はexact blob-validated materialization上で8 tests / 8 PASSをactual確認しましたが、native canonical checkout captureとH2 human observationは未取得です。

これにより、実行準備文書からmachine EvidenceとH1 / H2へ進む経路は一本化しつつ、environment blockerとrepository failure、real Inquiryとsynthetic matched review、human observationとsemantic audit、mechanicsとProduct Valueの意味差を維持しました。

自然な日本語として全文を再読し、REQ-0023 / SCN-0019のDesign Evidence、E1〜E8 Executable Evidence、H1 / H2 human observation、Adoption / Outcome Evidenceの高さを混同していないことを最終監査しました。

2026-10-10には、tested commitとcurrent developの実行対象closure 39 fileをGit blobで再照合し、全て同一であることを確認しました。これにより既存E1〜E8 PASSをcurrent source closureへ適用できることを固定し、次の停止線をH1 / H2 human Product Evidenceへ移しました。native H2 captureとexternal handoff actual runは再現性を高める補助Evidenceへ位置づけ、human reviewを待たせる前提にはしていません。