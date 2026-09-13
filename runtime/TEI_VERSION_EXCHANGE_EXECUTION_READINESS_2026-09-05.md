# TEI Version Exchange Execution Readiness — 2026-09-05

## 1. この文書の位置づけ

この文書は、PMS-06 / ISSUE-000072で進めているTEI executable version交換について、actual revision B実行の前に整備した検証経路と、まだ観測していない範囲を整理したものです。

ここでいう「ready」はactual Evidenceを得たという意味ではありません。exact revision Bのsource checkout、historical revision Aのfixed reference input、E2用Go、E3用Go、current SOZA checkoutを実行可能なLinux / amd64環境へ用意できたとき、build、Provider Plan実行、Evidence bundle検証、current SOZA Adapter live検査までをrepository-localに再現できる状態を指します。

関連文書の役割は次のように分けます。

- `plan/issue/ISSUE-000072-verify-tei-executable-version-exchange.md`: Goal、Constraints、Required experiments、Resolution Criteriaの正本。
- `runtime/TEI_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`: その時点までにactualに観測した履歴Evidenceの記録。
- `runtime/TEI_VERSION_EXCHANGE_TOOLCHAIN_READINESS_2026-09-05.md`: E2 / E3で別Go toolchainが必要な理由、user-local準備例、canonical combined runnerの実行例。
- `runtime/TEI_VERSION_EXCHANGE_FAILURE_STAGES_2026-09-05.md`: E2 / E3で外部観測可能なmachine-readable stageの境界。
- `runtime/TEI_VERSION_EXCHANGE_REQUIREMENT_PREAUDIT_2026-09-05.md`: actual結果を見る前に固定したRequirement / Scenario再照合基準。
- 本文書: actual実行前のcurrent execution path / readiness snapshot。

履歴Evidenceのactual観測値はEvidence文書を優先し、現在の実行経路・未実行状態は本書とtoolchain readinessを優先します。どの文書からも未観測のactual結果を推定しません。

```text
execution path ready
  != revision B build PASS
  != revision B Provider Plan observed
  != current SOZA Adapter live compatibility PASS
  != ISSUE-000072 Resolved
```

## 2. 比較軸の固定

revision A / Bは次です。

- revision A: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- revision B: `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`

version交換では、**executableのbuild sourceだけをAからBへ交換し、reference inputはAへ固定**します。

historical revision Aのfixed input identityは次です。

```text
reference/workspace tree
  5d596cfa5387b201cd733a07160307332d29a382

reference/order_rollout.durable-run.m0.21.start.json blob
  6fe7b1586fcfd17f23f3b659df5632b31a6baf1f

reference/workspace/.tei/plugin-lock.json blob
  0fa63ad634c72395781eaaae5ee0132f73d03541
```

AとBでは`reference/workspace` treeが異なります。そのため、B checkout内のreference inputをそのまま使うと、executable revisionだけでなくinput interpretationも同時に交換してしまいます。current runnerはexact B checkoutをbuild sourceとして必須にし、exact A fixed inputは次のどちらか一方から取得します。

- exact revision A checkout
- verified historical revision A Evidence bundle

historical bundle経路ではA source checkoutを復元したとは扱いません。bundle metadataのA source commit、historical binary / Provider Plan SHA-256、およびbundle内actual workspace / durable run / plugin lock bytesから再計算したGit object identityを固定既知値へ照合し、そのreference inputだけを一時領域へmaterializeします。

```text
exact B build source + exact A fixed input verified
  != revision B build PASS
  != Provider Plan execution PASS
```

## 3. source identityと静的Provider surface

`runtime/integration/verify_tei_execution_source_identity.py`はrevision Bについて次のGit object identityを固定しています。

```text
cmd tree
  ac4d4406dfa590a2078cf91217c4fe30797e7f8e

internal tree
  10d2bfea4932c308fa6537e3b081bc6ea5501205

reference tree
  57fafb742988ecb936b9ab261fa8a991e37ed5c7

go.mod blob
  f8763f8fb2d64d73f1b40b905f62b5e09c44493b

go.sum blob
  c7cd14781271dca2b014daf2f53d49d95b8e8826
```

同verifierはGit object identityだけでなく、対象execution boundaryにtracked変更、untracked entry、gitignored entryがないことも確認します。PR #226でstatus観測へ`--ignored=matching`を加え、`.git/info/exclude`等でignoredにした`.go` fileやhistorical reference inputも「statusに出ないから許可」とは扱わないようにしました。

repository-local synthetic Git検査では、clean checkout、tracked変更、untracked `.go`、ignored `.go` + ignored reference input、HEAD mismatchの5ケースを実行し、cleanだけをverifiedとして他を拒否することを確認しています。

```text
Git object identity matched
  + tracked / untracked / ignored execution boundary clean
  = source identity precondition satisfied
  != revision B build PASS
```

revision A fixed inputは、checkout取得時には前節のworkspace / durable run / plugin lock identityを別のexpected object setとして検証し、working-tree側にignored entryを含む追加入力を混入させません。historical bundle取得時には同じ3 object identityをactual bundle bytesから再計算して固定値へ照合します。

この検査はsource / fixed-input identityです。revision B binary bytesやruntime結果を導出しません。

`runtime/TEI_PROVIDER_SURFACE_STATIC_COMPATIBILITY_2026-09-05.md`では、A / BのProvider Plan出力surfaceとその前段を分けて比較しています。

静的に強い連続性を確認した領域:

```text
cmd/tei/main.go
  = exact same Git blob

internal/deployment
internal/environment
internal/releaseplan
internal/plugin/runtime
internal/core
  = exact same Git tree
```

一方、次はA / Bで変化しています。

```text
internal/workspace
internal/validation
internal/ir
top-level internal/plugin
```

したがって既知のProvider Plan出力surfaceとdeployment中核には静的連続性がありますが、fixed reference inputをBのworkspace / validation経路がactualに受理することは推定しません。

```text
same Provider Plan output surface
  != same input interpretation
  != revision B actual execution PASS
```

## 4. E2 / E3のrunner境界

### E2 — revision B bundle生成

`runtime/integration/run_tei_revision_b_prepositioned.py`は、GitHub Actionsを使わず、prepositionedされたexact B checkoutとexact A fixed inputからEvidence bundleを生成します。

入力:

- `--source-repo`: exact revision B。build sourceとしてのみ使用する。
- `--reference-source-repo` **または** `--reference-evidence-bundle`: exact revision A fixed inputの取得元。mutually exclusiveでどちらか一方を使う。
- `--output-archive`: 生成するEvidence bundle。revision B / SOZA repository配下、およびcheckout取得時のrevision A checkout配下ではない、新しいnon-symlink pathを使う。

主な処理:

1. output archive path / ancestor symlink、入力checkoutやSOZA repository配下への配置、既存archiveの暗黙上書きを副作用前に拒否する。
2. B execution-source Git identity、exact HEAD、tracked / untracked / ignored entryの不存在を確認する。
3. A fixed reference inputを取得方式ごとに検証する。checkout取得時はA Git identity / exact HEAD / working-tree purityを確認する。historical bundle取得時はA source commit、historical binary / Provider Plan SHA-256、actual reference bytesから再計算したworkspace / durable run / plugin lock Git object identityを固定値へ照合し、一時領域へmaterializeする。
4. Linux / amd64とE2用Go `1.23.2`を確認する。
5. historical Evidenceと同じbuild条件でB CLIをbuildする。
6. B binaryへAのworkspace / durable run / plugin lockを与え、`deployment-provider-plan`を実行する。
7. Provider Planの既知surfaceを確認する。
8. B binary SHA-256、Provider Plan SHA-256、A reference identity、A input acquisition modeをmetadataへ記録する。historical bundle取得時は入力bundle SHA-256もProvenanceとして記録する。
9. Evidence bundleを生成し、`verify_tei_evidence_bundle.py`でreference bytesを含めて再検証してからfinal archiveへ配置する。

build時は`GOWORK=off`、`GOENV=off`とし、外部`GOFLAGS` / `GOOS` / `GOARCH`を持ち込みません。

### E3 — current SOZA Adapter live検査

`runtime/integration/run_tei_bundle_adapter_compatibility.py`は、E2で得たEvidence bundleをcurrent SOZA Adapterへ接続します。

主な処理:

1. Evidence bundleのB source / binary / Provider Plan identityを再検証する。
2. archive traversal、link / device、duplicate memberを拒否する。
3. `bin/tei`とA fixed reference inputだけを一時領域へstageする。
4. staged inputのtree / blob identityをactual bytesから再計算する。
5. current SOZAの`runtime/go`と関連runner / verifier / fixed-reference helperのsource identityを記録し、対象境界の未commit変更やuntracked / ignored entryを拒否する。
6. `GOTOOLCHAIN=local`で指定されたE3用Goを使用し、検査中の暗黙toolchain downloadを行わない。
7. 既存`runtime/go/teiintegration.TestLiveTEIProviderPlan`を実行する。

live testの意味境界は次です。

- actual TEI CLIを別OS processとして起動できる。
- Provider Planをcurrent Adapter-local DTOでstrictにdecodeできる。
- current Capability Observation validatorを通る。
- `availability = true`を観測できる。
- `provider_plan_resolved = true`を観測できる。
- Provider固有の`executors` / `observations` / `evidence` / `pluginRuntime`をUniversal Capability Observationへ漏らさない。
- `SourceStateRef`をMapping Provenanceとして保持する。

revision B actual互換性はまだNot Yet Verifiedです。

## 5. E2 / E3は別Go toolchainで実行する

E2 historical TEI buildとE3 current SOZA live testは、同じcommand名`go`でも同じtoolchain identityを前提にしません。

```text
E2 historical TEI build
  = Go 1.23.2

E3 current SOZA live test
  = current runtime/go/go.modを満たすGo 1.25系
  + GOTOOLCHAIN=local
```

actual実行では、E2用とE3用の`go` executableを別々に指定します。root権限やsystem packageを必須にせずuser-localへ準備する方法と固定archive SHA-256は`TEI_VERSION_EXCHANGE_TOOLCHAIN_READINESS_2026-09-05.md`を正とします。

canonical combined runnerはE3 live testへ進む前に、current `runtime/go/go.mod`の`go` directiveと、指定されたE3 Go executableのactual `go version`を直接比較します。observed versionがrequirement未満なら`soza_go_toolchain` stageで停止し、`soza_teiintegration_live_test`を開始しません。必要versionと観測versionはcomparison axisへ記録します。

したがって、後続`go test`のstderrにversion関連の文字列が出たことを根拠にtoolchain原因を推測しません。toolchain不成立はlive test開始前のmachine-readable stageで止めます。

```text
Go toolchains prepared
  != E3 Go requirement precheck PASS
  != revision B build PASS
  != Provider Plan observed
  != Adapter live compatibility PASS
```

## 6. canonical actual入口

actual E2 → E3の標準入口は次の1本です。

`runtime/integration/run_tei_version_exchange_evidence.py`

単一PATHの`go`をE2からE3へ使い回す旧orchestratorは削除済みで、actual handoffとして使用しません。

A fixed inputの取得方式は次のどちらか一方を選びます。

### exact A checkoutを使う場合

```bash
export TEI_B_REPO=/path/to/tei-revision-b
export TEI_A_REPO=/path/to/tei-revision-a
export SOZA_REPO=/path/to/soza
export EVIDENCE_DIR=/path/outside/checkouts/tei-version-exchange-evidence
export TEI_GO="$HOME/.local/opt/soza-tei-go/go1.23.2/bin/go"
export SOZA_GO="$HOME/.local/opt/soza-tei-go/go1.25.0/bin/go"

SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

python3 "$SOZA_REPO/runtime/integration/run_tei_version_exchange_evidence.py" \
  --source-repo "$TEI_B_REPO" \
  --reference-source-repo "$TEI_A_REPO" \
  --soza-repo-root "$SOZA_REPO" \
  --output-dir "$EVIDENCE_DIR" \
  --tei-go-executable "$TEI_GO" \
  --soza-go-executable "$SOZA_GO" \
  --expected-soza-head "$SOZA_HEAD" \
  --json
```

### verified historical A Evidence bundleを使う場合

```bash
export TEI_B_REPO=/path/to/tei-revision-b
export TEI_A_BUNDLE=/path/to/historical/tei-e3b-p2-linux-amd64.tar.gz
export SOZA_REPO=/path/to/soza
export EVIDENCE_DIR=/path/outside/checkouts/tei-version-exchange-evidence
export TEI_GO="$HOME/.local/opt/soza-tei-go/go1.23.2/bin/go"
export SOZA_GO="$HOME/.local/opt/soza-tei-go/go1.25.0/bin/go"

SOZA_HEAD="$(git -C "$SOZA_REPO" rev-parse HEAD)"

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

`EVIDENCE_DIR`はrevision B checkoutとSOZA checkoutの外側へ置き、checkout取得時はrevision A checkoutとも相互包含しないpathを使います。historical bundle取得時は入力bundleをEvidence directory配下へ置きません。output path自身または既存ancestorがsymlinkの場合も開始前に拒否します。このconfiguration検査は`mkdir`より前に行います。

既存Evidenceを暗黙に上書きしません。同じoutput directoryへ意図的に再実行するときだけ`--overwrite`を明示します。`--overwrite`時は旧bundle / reportを実行開始前に除去するため、新しいE2が失敗した後に旧bundleだけが残り、新runの成果に見える状態を作りません。

combined reportは少なくとも次を区別します。

```text
e2_failed
  = E2 bundle生成まで成立していない

e2_bundle_verified_e3_not_run
  = E2成立後、E3開始前のinterim state

e2_verified_e3_failed
  = E2 bundleは成立したがE3 current Adapter live検査は不成立

fixed_scope_e2_e3_verified
  = exact-B executable + exact-A fixed input + 記録されたSOZA sourceについてE2/E3が成立
```

`fixed_scope_e2_e3_verified`もISSUE解決やarbitrary TEI version compatibilityを意味しません。

個別の`run_tei_revision_b_prepositioned.py` / `run_tei_bundle_adapter_compatibility.py`は、E2またはE3だけを切り分けて再実行・診断するときの下位入口として残します。`prepare_tei_fixed_reference_input.py`はhistorical A Evidence bundleをfixed input acquisitionへ使う場合の検証・materialize helperです。通常のactual handoffではcombined runnerを使います。

## 7. stage-aware failure Evidence

E2 / E3 failureは、自然言語logの文字列から内部原因を推測せず、runnerが機械的に発行する外部stageまでをEvidenceとして扱います。

Evidence output pathのconfiguration rejectionはこれらstageより前に行います。checkout overlap、symlink chain、existing standalone archive等の拒否を、E2 build failureやE3 Adapter failureへ読み替えません。

```text
pre-stage path configuration rejection
  != E2 failure
  != E3 failure
```

E2で記録できる主なstage:

```text
revision_b_source_identity
revision_a_fixed_reference_identity
execution_platform
tei_go_toolchain
tei_cli_build
deployment_provider_plan_execution
provider_plan_capture
provider_plan_validation
reference_input_packaging
evidence_metadata_write
evidence_bundle_packaging
evidence_bundle_verification
evidence_bundle_publish
```

E3で記録できる主なstage:

```text
soza_runtime_layout
soza_source_identity
bundle_identity_verification
execution_platform
bundle_staging
reference_input_identity
soza_go_toolchain
soza_teiintegration_live_test
```

外部process failureではcommand、return code、stdout / stderr tailをboundedに保存します。ただし、出力に`validation`、`plugin lock`、`strict decode`、`validator`等の語が含まれていても、それだけでmachine-readable substageへ昇格しません。

特に次を区別します。

```text
E2 deployment_provider_plan_execution
  != workspace load
  != validation
  != durable run
  != plugin lock

E3 soza_teiintegration_live_test
  != strict decode
  != mapping
  != Capability Observation validator
```

TEIまたは`teiintegration`側から正式なmachine-readable error contractが得られた場合にだけ、より内側のsubstageを追加します。

```text
observed repository-local stage
  != inferred internal root cause
  != Provider incompatibility judgement
```

## 8. 現在のEvidence状態

```text
revision A fixed source / actual CLI
  = Scoped Executable Evidence available

revision A artifact re-acquisition / bundle identity re-verification
  = verified

revision B source identity
  = fixed to 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision B execution-source Git identity
  = fixed; repository-local verifier implemented

source working-tree purity
  = tracked changes / untracked / ignored entries rejected; PR #226 synthetic Git cases 5 passed

revision A fixed reference input identity
  = fixed; checkout verifier and historical-bundle external identity verifier implemented

historical A Evidence bundle fixed-input acquisition path
  = implemented; dedicated tests committed; full suite not re-run in current environment

Provider Plan output surface A/B
  = strong static continuity observed

workspace / validation / IR input interpretation
  = changed; actual fixed-input execution required

version-exchange comparison axis
  = exact-B build source + exact-A fixed reference input

prepositioned B Evidence runner
  = implemented; earlier synthetic / fixed-input isolation checks passed

E2 stage-aware diagnostics
  = implemented; focused stage-model checks 4 passed

bundle → current Adapter live runner
  = implemented; baseline synthetic tests passed before stage instrumentation

E3 stage-aware diagnostics
  = implemented; focused stage-model checks 4 passed

E3 Go directive precheck
  = implemented; focused version-comparison model check passed

E2 / E3 separate Go toolchains
  = identified and explicit in canonical combined runner

toolchain-split combined runner
  = implemented; baseline 7 synthetic tests passed before later stage-instrumentation additions

Evidence output / checkout separation guard
  = implemented; path-safety negative controls committed

path-safety / historical-bundle additions full suite in current environment
  = Not Re-run

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

revision B current SOZA Adapter live compatibility
  = Not Yet Verified

formal TEI executable distribution
  = Not Yet Defined

credential lifecycle / Operational portability
  = Not Yet Verified
```

expanded branch unit suitesの一部はcurrent ChatGPT containerでrepository全体を再実行できず、stage instrumentation / path-safety / historical-bundle acquisition追加後のfull suiteをこの環境で再実行したと主張しません。PR #226のsource-identity synthetic Git 5ケース、focused stage-model checks、focused Go requirement check、それ以前に実行済みのbaseline testを区別して記録します。

## 9. actual後のRequirement / Scenario再照合

actual Bの成功・失敗を見てからRequirementの意味を後付けしないため、`runtime/TEI_VERSION_EXCHANGE_REQUIREMENT_PREAUDIT_2026-09-05.md`で事前判定基準を固定しています。

主な再照合対象:

- REQ-0001 — durable meaning continuity
- REQ-0007 — Capability / Provider neutrality
- REQ-0021 — replaceable Realization / Execution
- SCN-0014 — Execution Provider exchange
- SCN-0018 — end-to-end Product Journey
- adjacent REQ-0022 — provider-neutral Capability Observation

build / toolchain / Provider Plan process / Adapter-local DTO failureだけを理由に、新しいStable RequirementやUniversal Contract fieldを追加しません。historical Aを保持するためにProvider revisionをCapability identityへ昇格させなければならない、TEI version固有fieldをUniversal Coreへ入れないと意味を保持できない、などの独立したProduct failureがactualに確認された場合だけCandidate Requirementを再検討します。

```text
actual incompatibility observed
  != new Stable Requirement automatically required
```

## 10. 残る停止線

```text
static source continuity
  != actual execution

exact B source verified
  != B binary built

exact A fixed input verified
  != B accepts A input

historical A fixed-input acquisition path implemented
  != canonical B execution performed

Evidence output path safety implemented
  != actual process started

Go toolchains prepared
  != E3 Go requirement precheck PASS
  != E2/E3 PASS

B Evidence bundle produced
  != current SOZA Adapter compatibility verified

fixed_scope_e2_e3_verified
  != arbitrary TEI version compatibility
  != formal executable distribution
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
  != ISSUE-000072 Resolved
```

actual B Evidenceを得る前に、新しいStable RequirementやUniversal TEI fieldを追加しません。GitHub ActionsもISSUE-000072の意味上の成立条件にはしません。

## 11. 2026-09-06 current delta

この節はPR #245 / #247 / #246 / #248後の追加境界を記録します。前節までの比較軸、stage vocabulary、停止線を変更せず、actual実行前に新たに固定できたsource acquisitionと実行前後identity観測を補足します。

### revision B source acquisitionの進展

exact revision Bについて、signed commit / execution tree identityに加え、取得境界を次まで進めました。

- PR #245: exact B commitへpinしたGitHub Contents APIからselected source bytesを取得し、固定Git blob identityへbindingした。
- `go.mod` / `go.sum` / `cmd/tei/source_index.go` / `cmd/tei/validation_output.go`は取得bytesからGit blob SHA-1を独立再計算し、固定値へ一致した。
- `cmd/tei/main.go`はexact B commitのsource bytesとblob referenceを取得済みだが、このEvidenceでは全bytes独立再ハッシュ成立とは数えない。
- PR #247: canonical verifierが見る`cmd` / `internal` / `reference` treeのrecursive listingがすべて`truncated=false`であることを確認した。
- したがってverifier境界内の全tracked leafについて、取得すべきpath / mode / blob SHAをcontent-addressedに列挙可能である。

```text
selected exact-B source bytes acquired
  + complete verifier-boundary leaf addressability
  != all tracked leaf bytes materialized
  != exact revision B checkout materialized
  != working-tree purity verified on a full checkout
  != revision B build PASS
```

canonical E2は引き続き、full exact-B checkoutとworking-tree purity verificationを実行前提とします。object reconstruction / selected-byte acquisitionだけをactual checkoutの代替とは扱いません。

### E2のpre/post execution identity

PR #246以降、E2はinitial identity verificationだけでは終了しません。Provider Plan processが成功し、JSON surfaceを検証した直後、fixed input packagingより前に次を再検証します。

- revision B source checkout: exact HEAD / fixed execution-source objects / tracked・untracked・ignored boundary purity
- revision A checkout取得時: exact HEAD / fixed workspace・durable run・plugin-lock objects / working-tree purity
- historical A Evidence bundle取得時: A checkoutは存在しないためpost-execution Git再検証は行わず、materialized fixed bytesと最終bundle byte verificationを維持する

成功resultはpre-execution observationとは別に`postExecutionIdentity`を保持します。failure stageは増やさず、既存`revision_b_source_identity` / `revision_a_fixed_reference_identity`へ収束します。

```text
pre-execution source identity verified
  + Provider Plan process completed
  + post-execution source identity reverified
  != immutable source snapshot proven
```

この再検証は、post-execution check時点に残るHEAD / object / working-tree driftを検出します。検査間に一時変更され、再検証前に完全復元された事象まで暗号学的に排除するものではありません。

### E3のpre/post live source identity

PR #248以降、E3もcurrent SOZA Evidence source surfaceをlive test前後の二点で観測します。

- pre-live: existing `sozaSource`
- post-live: `postLiveTestSozaSource`
- 対象は`runtime/go`、combined runner、E2/E3 runner、fixed-reference helper、path-safety helper、bundle/source verifierを含むcurrent 8-path boundary
- post-live driftは新stageを追加せず、既存`soza_source_identity`で停止する

```text
pre-live SOZA source identity verified
  + current Adapter live test completed
  + post-live SOZA source identity reverified
  != immutable SOZA source snapshot proven
```

### current Evidence stateの追記

```text
revision B selected source-byte acquisition
  = partial acquisition Evidence available; full checkout not materialized in current environment

revision B complete verifier-boundary leaf addressability
  = verified; all tracked leaf bytes are not yet materialized

E2 post-execution source/fixed-input revalidation
  = implemented; dedicated tests committed; full repository suite not re-run in current environment

E3 post-live SOZA source revalidation
  = implemented; dedicated tests committed; full repository suite not re-run in current environment

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

revision B current SOZA Adapter live compatibility
  = Not Yet Verified

ISSUE-000072
  = Open
```

このdeltaでもEvidenceの高さは上げません。GitHub Actionsをcurrent成立条件へ戻さず、actual B E2→E3が成立するまでは`fixed_scope_e2_e3_verified`を主張しません。
