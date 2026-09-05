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

AとBでは`reference/workspace` treeが異なります。そのため、B checkout内のreference inputをそのまま使うと、executable revisionだけでなくinput interpretationも同時に交換してしまいます。current runnerはexact B checkoutをbuild source、exact A checkoutをfixed reference sourceとして別々に受け取ります。

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

revision A fixed inputも、前節のworkspace / durable run / plugin lock identityを別のexpected object setとして検証し、working-tree側にignored entryを含む追加入力を混入させません。

この検査はsource identityです。binary bytesやruntime結果を導出しません。

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

`runtime/integration/run_tei_revision_b_prepositioned.py`は、GitHub Actionsを使わず、prepositionedされた2つのcheckoutからEvidence bundleを生成します。

入力:

- `--source-repo`: exact revision B。build sourceとしてのみ使用する。
- `--reference-source-repo`: exact revision A。fixed reference inputとしてのみ使用する。
- `--output-archive`: 生成するEvidence bundle。revision B / revision A / SOZA repository配下ではない、新しいnon-symlink pathを使う。

主な処理:

1. output archive path / ancestor symlink、入力checkoutやSOZA repository配下への配置、既存archiveの暗黙上書きを副作用前に拒否する。
2. B execution-source Git identity、exact HEAD、tracked / untracked / ignored entryの不存在を確認する。
3. A fixed reference input Git identity、exact HEAD、tracked / untracked / ignored entryの不存在を確認する。
4. Linux / amd64とE2用Go `1.23.2`を確認する。
5. historical Evidenceと同じbuild条件でB CLIをbuildする。
6. B binaryへAのworkspace / durable run / plugin lockを与え、`deployment-provider-plan`を実行する。
7. Provider Planの既知surfaceを確認する。
8. B binary SHA-256、Provider Plan SHA-256、A reference identityをmetadataへ記録する。
9. Evidence bundleを生成し、`verify_tei_evidence_bundle.py`で再検証してからfinal archiveへ配置する。

build時は`GOWORK=off`、`GOENV=off`とし、外部`GOFLAGS` / `GOOS` / `GOARCH`を持ち込みません。

### E3 — current SOZA Adapter live検査

`runtime/integration/run_tei_bundle_adapter_compatibility.py`は、E2で得たEvidence bundleをcurrent SOZA Adapterへ接続します。

主な処理:

1. Evidence bundleのB source / binary / Provider Plan identityを再検証する。
2. archive traversal、link / device、duplicate memberを拒否する。
3. `bin/tei`とA fixed reference inputだけを一時領域へstageする。
4. staged inputのtree / blob identityをactual bytesから再計算する。
5. current SOZAの`runtime/go`と関連runner / verifierのsource identityを記録し、対象境界の未commit変更やuntracked fileを拒否する。
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

実行例:

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

`EVIDENCE_DIR`はrevision B checkout、revision A checkout、SOZA checkoutの外側へ置き、いずれのcheckoutとも相互包含しないpathを使います。output path自身または既存ancestorがsymlinkの場合も開始前に拒否します。このconfiguration検査は`mkdir`より前に行います。

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

個別の`run_tei_revision_b_prepositioned.py` / `run_tei_bundle_adapter_compatibility.py`は、E2またはE3だけを切り分けて再実行・診断するときの下位入口として残します。通常のactual handoffではcombined runnerを使います。

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
  = fixed and repository-local verifier implemented

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

path-safety additions full suite in current environment
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

expanded branch unit suitesの一部はcurrent ChatGPT containerでrepository全体を再実行できず、stage instrumentation / path-safety追加後のfull suiteをこの環境で再実行したと主張しません。PR #226のsource-identity synthetic Git 5ケース、focused stage-model checks、focused Go requirement check、それ以前に実行済みのbaseline testを区別して記録します。

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