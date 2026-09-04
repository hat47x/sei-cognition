# TEI Version Exchange Failure Stages — 2026-09-05

## 1. この文書の位置づけ

PMS-06 / ISSUE-000072のactual revision B実行では、失敗を「TEI version交換 failure」という一語へまとめると、source取得・toolchain・build・Provider Plan process・output validation・SOZA Adapter compatibilityの境界を失います。

そこで、repository-local E2 runnerが外部から確実に観測できる境界だけをmachine-readable stageとして返すよう整理しました。

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

## 3. process detailの保持境界

`TEIEvidenceStageError`は、外部process failureについて次を保持できます。

- stage
- message
- command
- return code
- stdout tail
- stderr tail

stdout / stderrはそれぞれ末尾16 KiBへ制限します。長大な外部process出力をEvidence reportへ無制限に取り込みません。

このdetailはdiagnostic / provenanceです。stderr文字列そのものをUniversal semanticsへ昇格させません。

## 4. combined E2 / E3 reportとの接続

`runtime/integration/run_tei_version_exchange_evidence.py`は上位stageを次のように保持します。

```text
stage = E2
substage = tei_cli_build
```

のように、version交換全体の段階とE2内部stageを分離します。

stage-aware exceptionでは`detail`もそのままJSON reportへ格納します。一方、通常の`ValueError`等でmachine-readable substageがない場合は、無理にsubstageを作りません。

```text
known E2 substage
  != inferred substage from exception text
```

E3については、current Adapter runnerが現在持つbundle / fixed input / SOZA source / toolchain / live-test境界をそのまま利用します。E3内部をこの変更だけで新しいtaxonomyへ作り替えません。

## 5. synthetic / focused checks

branch上には、少なくとも次のnegative controlを追加しました。

- B source identity failure → `revision_b_source_identity`
- A fixed input failure → `revision_a_fixed_reference_identity`
- Go version mismatch → `tei_go_toolchain`
- build non-zero → `tei_cli_build` + return code / stderr
- Provider Plan process non-zero → `deployment_provider_plan_execution`
- stderrにvalidationという語があっても内部`validation` stageへ昇格しない
- unknown Provider Plan field → `provider_plan_validation`
- process detail tailを16 KiBへ制限する
- success pathではfinal bundleと`completedStages`を得る
- combined reportでE2 / substageを別々に保持する

current work containerではGitHub raw sourceを再取得できないため、branch上のunittest suite全体をこの環境へ再現してはいません。一方、stage error、combined substage伝播、stderr非推測、output tail上限の中核ロジックはfocused local check 4件を実行しPASSしました。

この制約をactual Executable Evidenceへ読み替えません。

## 6. 現在の停止線

```text
stage-aware E2 diagnostics implemented
  != actual revision B execution attempted

E2 substage captured
  != root cause proven inside TEI

Provider Plan process failure
  != workspace-load failure
  != validation failure
  != plugin-lock incompatibility
  unless machine-readable Evidence establishes that boundary

E2 failure
  != E3 Adapter failure

failure diagnostics
  != Release Evidence
  != Operational Evidence
  != ISSUE-000072 Resolved
```

Stable Requirement、Universal Contract、Capability Observation fieldは変更しません。actual B Evidenceが得られた時点で、このstage taxonomyを使って観測結果を記録します。
