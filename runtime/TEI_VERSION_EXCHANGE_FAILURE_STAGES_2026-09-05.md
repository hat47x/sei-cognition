# TEI Version Exchange Failure Stages — 2026-09-05

## 1. この文書の位置づけ

PMS-06 / ISSUE-000072のactual revision B実行では、失敗を「TEI version交換failure」という一語へまとめると、source取得・toolchain・build・Provider Plan process・output validation・SEI Adapter compatibilityの境界を失います。

そこで、repository-local E2 / E3 runnerが**外部から確実に観測できる境界だけ**をmachine-readable stageとして返すよう整理しました。

これはactual revision Bが失敗したというEvidenceではありません。actual実行前に、将来のfailureを誤った層へ昇格させないためのExecutable-path instrumentationです。

```text
failure stage instrumentation ready
  != revision B failure observed
  != TEI incompatibility observed
  != SEI Adapter incompatibility observed
```

## 2. stage開始前のconfiguration rejection

E2 / E3のmachine-readable stageへ入る前に、actual Evidenceを安全に開始できるpath configurationかを確認します。

combined runner `runtime/integration/run_tei_version_exchange_evidence.py`は、`--output-dir`を作成する前に次を拒否します。

- output path自身または既存ancestorがsymlinkである。
- output directoryがrevision B source checkout配下にある。
- exact A checkout取得時、output directoryがrevision A fixed-reference checkout配下にある。
- output directoryがSEI checkout配下にある。
- output directoryがこれらinput checkoutを包含する。
- historical A Evidence bundle取得時、入力bundleがoutput directory配下に含まれる。
- 既存pathがdirectoryではない。

standalone E2 `run_tei_revision_b_prepositioned.py`も、final archiveについて次を副作用前に拒否します。

- output path自身または既存ancestorがsymlinkである。
- output archiveがrevision B source / SEI repository配下にある。
- exact A checkout取得時、output archiveがrevision A reference checkout配下にある。
- output archiveが既に存在し、暗黙上書きになる。

これらはTEI processやSEI Adapterを開始した結果ではないため、`TEIEvidenceStageError` / `TEIAdapterStageError`へ昇格させません。

```text
Evidence output path rejected
  = pre-stage configuration rejection
  != revision_b_source_identity failure
  != tei_cli_build failure
  != deployment_provider_plan_execution failure
  != sei_teiintegration_live_test failure
```

configuration rejection時にmachine-readable E2 / E3 substageを作らないこと自体が、root causeを過大に推定しないための境界です。

## 3. E2 stage taxonomy

`runtime/integration/run_tei_revision_b_prepositioned.py`の`TEIEvidenceStageError`は、次のstageを区別します。

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

成功時は同じ順序を`completedStages`へ記録します。

### source / fixed input

`revision_b_source_identity`はexact revision Bのbuild source identityです。

`revision_a_fixed_reference_identity`はhistorical revision Aのworkspace / durable run / plugin lock identityです。exact A checkoutを使う場合はGit HEAD / object identity / working-tree purityを検証します。verified historical A Evidence bundleを使う場合は、bundle metadataのA source commit、historical binary / Provider Plan SHA-256、およびactual reference bytesから再計算したGit object identityを固定値へ照合し、reference inputだけを一時領域へmaterializeします。

取得経路が違ってもfixed input identity検証という外部境界は同じなので、新しいE2 stageは作りません。historical bundleのidentity verificationやmaterializationが成立しない場合も`revision_a_fixed_reference_identity`で停止します。

```text
fixed input acquisition path differs
  != new machine-readable E2 stage required
```

この2つを分けることで、B source driftとA fixed input driftを同じ取得failureへまとめません。一方、A fixed inputのcheckout取得 / historical bundle取得の違いはAcquisition Provenanceとして保持し、Capability identityへ昇格させません。

### platform / toolchain / build

`execution_platform`はhistorical Linux / amd64条件です。

`tei_go_toolchain`はhistorical Evidenceと同じGo `1.23.2`を確認するstageです。

`tei_cli_build`は`go build -trimpath -ldflags='-s -w' ./cmd/tei`のprocess boundaryです。

build processがnon-zeroなら、command、return code、stdout / stderr tailをstage detailへ保持できます。ただし、compiler stderrの内容から別のProduct failureへ自動分類しません。

### Provider Plan process

`deployment_provider_plan_execution`は、actual B binaryへexact-A fixed reference inputを与えて`deployment-provider-plan`を起動する**process全体の境界**です。

ここで重要なのは、TEI内部の次のようなsubstageをstderr文言から推測しないことです。

```text
workspace load
validation
durable run check
plugin lock resolution
Provider Plan generation internals
```

たとえばstderrに`validation failed`と書かれていても、repository-local Evidence stageは`deployment_provider_plan_execution`のままです。

```text
stderr contains "validation"
  != machine-readable TEI validation-stage Evidence
```

TEI側が将来machine-readable stage / error contractを提供した場合は、そのactual contractを確認してから細分化を再評価します。

### output / bundle

processがexit 0でも、Provider Plan JSONが既知Adapter-local surfaceとして読めない場合は`provider_plan_validation`です。

archive作成・再検証・final配置は、それぞれ`evidence_bundle_packaging` / `evidence_bundle_verification` / `evidence_bundle_publish`として分けます。

このため、Provider Planが成立した後のEvidence packaging failureをTEI Provider incompatibilityへ読み替えません。

## 4. E3 stage taxonomy

`runtime/integration/run_tei_bundle_adapter_compatibility.py`の`TEIAdapterStageError`は、current SEI Adapter live検査を次の外部境界へ分けます。

```text
sei_runtime_layout
sei_source_identity
bundle_identity_verification
execution_platform
bundle_staging
reference_input_identity
sei_go_toolchain
sei_teiintegration_live_test
```

成功時はこの順序を`completedStages`へ記録します。

### SEI source / bundle / fixed input

`sei_runtime_layout`は、current `runtime/go` moduleと既存`teiintegration` live testの存在境界です。

`sei_source_identity`は、検査対象SEI checkoutのHEAD / Git object identity / worktree cleanlinessです。canonical E2→E3でactual Provider Plan実行前に使うfixed-reference helperもこのSEI Evidence source surfaceへ含めます。

`bundle_identity_verification`は、B source / binary / Provider Plan identityを既存bundle verifierで再確認する境界です。

`bundle_staging`は、検証済みbundleからactual CLIとfixed reference inputだけを一時領域へ安全にstageする境界です。

`reference_input_identity`は、stagedされたhistorical A workspace / durable run / plugin lockのGit object identityをactual bytesから再確認する境界です。

これにより、bundle identity failure、safe staging failure、fixed input driftをAdapter incompatibilityへまとめません。

### SEI toolchain / live test

`sei_go_toolchain`は、`GOTOOLCHAIN=local`のcurrent SEI test environmentで`go version`を起動できるだけでなく、current `runtime/go/go.mod`の`go` directiveをactual toolchainが満たすことまで確認する境界です。directiveを読めない、`go version`を解釈できない、またはactual Goがdirective未満の場合は、`go test`を開始せずこのstageで停止します。

この判定はstandalone E3 runner `run_tei_bundle_adapter_compatibility.py`を正本とします。combined runner `run_tei_version_exchange_evidence.py`も同じE3 runnerを呼び、成功時はそこで観測した`seiGoRequirement` / `seiGoVersion`をcomparison axisへ戻します。

```text
actual Go < current go.mod requirement
  = sei_go_toolchain failure
  != sei_teiintegration_live_test failure
```

`sei_teiintegration_live_test`は、既存`runtime/go/teiintegration.TestLiveTEIProviderPlan`を実行する**Go test process全体の境界**です。

既存live testの内部では、actual TEI CLI process、strict Provider Plan decode、Capability Observation mapping / validation、TEI固有field非漏出等を検査します。しかし、Go testのstdout / stderrに現れた文言だけから、repository-local runnerが次のような新しいsubstageを作ることはしません。

```text
external TEI process
strict decode
Capability Observation mapping
validator
provider field leakage check
```

たとえば出力に`strict decode`や`validator failure`とあっても、machine-readable stageは`sei_teiintegration_live_test`のままです。

```text
Go test output contains "validator"
  != machine-readable SEI validator-stage Evidence
```

将来、`teiintegration`側がmachine-readable test result / error stageを正式に出力する場合だけ、そのactual contractを確認して細分化を再評価します。

## 5. process detailの保持境界

E2の`TEIEvidenceStageError`とE3の`TEIAdapterStageError`は、外部process failureについて次を保持できます。

- stage
- message
- command
- return code
- stdout tail
- stderr tail

E2のstdout / stderrはそれぞれ末尾16 KiB、E3はそれぞれ末尾32 KiBへ制限します。長大な外部process出力をEvidence reportへ無制限に取り込みません。

このdetailはdiagnostic / provenanceです。stdout / stderr文字列そのものをUniversal semanticsへ昇格させません。

## 6. combined E2 / E3 reportとの接続

`runtime/integration/run_tei_version_exchange_evidence.py`は、version交換全体の上位stageとrunner内部stageを分離します。

```text
stage = E2
substage = tei_cli_build
```

または、

```text
stage = E3
substage = sei_teiintegration_live_test
```

のように記録します。

stage-aware exceptionでは`detail`もJSON reportへ格納します。一方、通常の`ValueError` / `RuntimeError`等でmachine-readable substageがない場合は、例外文言からsubstageを作りません。

```text
known runner substage
  != inferred substage from exception text
```

E2が成立しE3だけが失敗した場合は、成立済みE2 bundleを保持したままE3 failureを別に記録します。

output path configurationはcombined reportのE2 / E3 execution stateより前の入力条件です。path validationで拒否した場合、E2 / E3が開始したというreportを推測生成しません。

## 7. synthetic / focused checks

E2側には、少なくとも次のnegative controlを追加しています。

- B source identity failure → `revision_b_source_identity`
- A fixed input failure → `revision_a_fixed_reference_identity`
- historical A Evidence bundle identity / materialization failure → `revision_a_fixed_reference_identity`
- Go version mismatch → `tei_go_toolchain`
- build non-zero → `tei_cli_build` + return code / stderr
- Provider Plan process non-zero → `deployment_provider_plan_execution`
- stderrにvalidationという語があっても内部`validation` stageへ昇格しない
- unknown Provider Plan field → `provider_plan_validation`
- process detail tailを16 KiBへ制限する
- success pathではfinal bundleと`completedStages`を得る

E3側には次のnegative controlを追加しています。

- bundle verifier failure → `bundle_identity_verification`
- A fixed input failure → `reference_input_identity`
- SEI Go process failure → `sei_go_toolchain`
- current `go.mod`より古いSEI Go → `sei_go_toolchain`、live test未開始
- live test non-zero → `sei_teiintegration_live_test`
- live test出力に`strict decode` / `validator`があっても、その内部stageへ昇格しない
- process detail tailを32 KiBへ制限する
- success pathではcurrent Go requirement / observed versionと既存live testの成立を得る

combined reportについても、E2 / E3の上位stageとstage-aware substageを別々に保持するnegative controlを追加しています。E3のGo要件判定ロジック自体はcombined側へ複製せず、standalone E3 runnerの結果またはstage-aware failureをそのまま利用します。

PR #223では、stage開始前のpath-safety negative controlも追加しました。

- standalone E2 input checkout / SEI repository内出力を拒否し、source verifier / processを開始しない。
- standalone E2 existing archive / symlink archiveを拒否し、既存bytesを変更しない。
- combined runner input checkout内output、input checkoutを包含するoutput、symlink outputを拒否し、E2 / E3 runnerを開始しない。

PR #239では、historical A Evidence bundleをfixed input acquisitionとして使う専用negative controlを追加しました。

- legacy A bundleのactual reference bytesを外部固定Git object identityへ照合する。
- reference byte drift / incomplete expectationを拒否する。
- fixed input materializationのlink / overwrite境界を拒否する。
- E2のhistorical bundle取得経路を既存`revision_a_fixed_reference_identity` stageへ収束させる。
- combined runnerがacquisition modeをcomparison axisへ記録する。
- fixed-reference helperをE3 SEI source identity boundaryへ含める。

current work containerではbranch上のunittest suite全体を再現してはいません。E2 stage error、combined substage伝播、stderr非推測、output tail上限の中核ロジックについてfocused local check 4件を以前に実行しPASSしました。E3側も同じ原則のstage modelとして実装し、branch testへnegative controlを追加しています。PR #223 / #239で追加したpath-safety / historical-bundle testをcurrent environmentでfull suiteとして再実行したとは主張しません。

この制約をactual Executable Evidenceへ読み替えません。

## 8. 現在の停止線

```text
stage-aware E2/E3 diagnostics implemented
  + pre-stage Evidence path safety implemented
  + historical A fixed-input acquisition path implemented
  != actual revision B execution attempted

Evidence path configuration rejected
  != E2 failure
  != E3 failure

historical A bundle acquisition rejected at revision_a_fixed_reference_identity
  != revision B build failure
  != Provider Plan failure
  != new internal TEI substage

E2 substage captured
  != root cause proven inside TEI

Provider Plan process failure
  != workspace-load failure
  != validation failure
  != plugin-lock incompatibility
  unless machine-readable Evidence establishes that boundary

E3 substage captured
  != strict-decode failure proven
  != Observation validator failure proven
  unless machine-readable Evidence establishes that boundary

E2 failure
  != E3 Adapter failure

failure diagnostics
  != Release Evidence
  != Operational Evidence
  != ISSUE-000072 Resolved
```

Stable Requirement、Universal Contract、Capability Observation fieldは変更しません。actual B Evidenceが得られた時点で、このstage taxonomyを使って観測結果を記録します。