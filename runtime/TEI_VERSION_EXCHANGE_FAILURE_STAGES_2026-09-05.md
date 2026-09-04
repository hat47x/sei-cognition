# TEI Version Exchange Failure Stages — 2026-09-05

## 1. この文書の位置づけ

PMS-06 / ISSUE-000072のactual revision B実行では、失敗を「TEI version交換 failure」という一語へまとめると、source取得・toolchain・build・Provider Plan process・output validation・SOZA Adapter compatibilityの境界を失います。

そこで、repository-local E2 / E3 runnerが**外部から確実に観測できる境界だけ**をmachine-readable stageとして返すよう整理しました。

これはactual revision Bが失敗したというEvidenceではありません。actual実行前に、将来のfailureを誤った層へ昇格させないためのExecutable-path instrumentationです。

```text
failure stage instrumentation ready
  != revision B failure observed
  != TEI incompatibility observed
  != SOZA Adapter incompatibility observed
```

## 2. E2 stage taxonomy

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

`revision_a_fixed_reference_identity`はhistorical revision Aのworkspace / durable run / plugin lock identityです。

この2つを分けることで、B source driftとA fixed input driftを同じ取得failureへまとめません。

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

## 3. E3 stage taxonomy

`runtime/integration/run_tei_bundle_adapter_compatibility.py`の`TEIAdapterStageError`は、current SOZA Adapter live検査を次の外部境界へ分けます。

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

成功時はこの順序を`completedStages`へ記録します。

### SOZA source / bundle / fixed input

`soza_runtime_layout`は、current `runtime/go` moduleと既存`teiintegration` live testの存在境界です。

`soza_source_identity`は、検査対象SOZA checkoutのHEAD / Git object identity / worktree cleanlinessです。

`bundle_identity_verification`は、B source / binary / Provider Plan identityを既存bundle verifierで再確認する境界です。

`bundle_staging`は、検証済みbundleからactual CLIとfixed reference inputだけを一時領域へ安全にstageする境界です。

`reference_input_identity`は、stagedされたhistorical A workspace / durable run / plugin lockのGit object identityをactual bytesから再確認する境界です。

これにより、bundle identity failure、safe staging failure、fixed input driftをAdapter incompatibilityへまとめません。

### SOZA toolchain / live test

`soza_go_toolchain`は、`GOTOOLCHAIN=local`のcurrent SOZA test environmentで`go version`を起動できる境界です。

`soza_teiintegration_live_test`は、既存`runtime/go/teiintegration.TestLiveTEIProviderPlan`を実行する**Go test process全体の境界**です。

既存live testの内部では、actual TEI CLI process、strict Provider Plan decode、Capability Observation mapping / validation、TEI固有field非漏出等を検査します。しかし、Go testのstdout / stderrに現れた文言だけから、repository-local runnerが次のような新しいsubstageを作ることはしません。

```text
external TEI process
strict decode
Capability Observation mapping
validator
provider field leakage check
```

たとえば出力に`strict decode`や`validator failure`とあっても、machine-readable stageは`soza_teiintegration_live_test`のままです。

```text
Go test output contains "validator"
  != machine-readable SOZA validator-stage Evidence
```

将来、`teiintegration`側がmachine-readable test result / error stageを正式に出力する場合だけ、そのactual contractを確認して細分化を再評価します。

## 4. process detailの保持境界

E2の`TEIEvidenceStageError`とE3の`TEIAdapterStageError`は、外部process failureについて次を保持できます。

- stage
- message
- command
- return code
- stdout tail
- stderr tail

E2のstdout / stderrはそれぞれ末尾16 KiB、E3はそれぞれ末尾32 KiBへ制限します。長大な外部process出力をEvidence reportへ無制限に取り込みません。

このdetailはdiagnostic / provenanceです。stdout / stderr文字列そのものをUniversal semanticsへ昇格させません。

## 5. combined E2 / E3 reportとの接続

`runtime/integration/run_tei_version_exchange_evidence.py`は、version交換全体の上位stageとrunner内部stageを分離します。

```text
stage = E2
substage = tei_cli_build
```

または、

```text
stage = E3
substage = soza_teiintegration_live_test
```

のように記録します。

stage-aware exceptionでは`detail`もJSON reportへ格納します。一方、通常の`ValueError` / `RuntimeError`等でmachine-readable substageがない場合は、例外文言からsubstageを作りません。

```text
known runner substage
  != inferred substage from exception text
```

E2が成立しE3だけが失敗した場合は、成立済みE2 bundleを保持したままE3 failureを別に記録します。

## 6. synthetic / focused checks

E2側には、少なくとも次のnegative controlを追加しています。

- B source identity failure → `revision_b_source_identity`
- A fixed input failure → `revision_a_fixed_reference_identity`
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
- SOZA Go process failure → `soza_go_toolchain`
- live test non-zero → `soza_teiintegration_live_test`
- live test出力に`strict decode` / `validator`があっても、その内部stageへ昇格しない
- process detail tailを32 KiBへ制限する
- success pathでは既存live testを実行し`completedStages`を得る

combined reportについても、E2 / E3の上位stageとstage-aware substageを別々に保持するnegative controlを追加しています。

current work containerではGitHub raw sourceを再取得できないため、branch上のunittest suite全体をこの環境へ再現してはいません。一方、E2 stage error、combined substage伝播、stderr非推測、output tail上限の中核ロジックについてfocused local check 4件を実行しPASSしました。E3側も同じ原則のstage modelとして実装し、branch testへnegative controlを追加しています。

この制約をactual Executable Evidenceへ読み替えません。

## 7. 現在の停止線

```text
stage-aware E2/E3 diagnostics implemented
  != actual revision B execution attempted

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
