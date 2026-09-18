# TEI Version Exchange E2 Partial Delta — 2026-09-06

## 位置づけ

本書は `TEI_VERSION_EXCHANGE_CURRENT_READINESS_2026-09-06.md` の後に追加された、revision B E2 partial Evidence経路、E2からE3への後日resume経路、interrupted report-pair reconciliation、exact-B / exact-A strict bundle verification、GitHub-hosted workflow attempt 3の観測をまとめるcurrent deltaである。

Stable Requirement、Universal Contract、comparison axis、quality judgement、ISSUE-000072 Resolution条件は変更しない。

```text
E2 partial / strict re-verification / later E3 resume path available
  != revision B E2 PASS
  != E3 SEI Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

operator向けactual手順は次を正とする。

`runtime/TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`

## E2 partial Evidence入口

PR #289〜#292により、E3 Go toolchainがまだ用意できない環境でも、GitHub acquisitionからrevision BのE2だけを先行回収できる入口を追加した。

入口:

`runtime/integration/run_tei_revision_b_e2_from_github.py`

この経路はfull E2→E3 one-shotを弱めない。E2に必要な条件だけをsource acquisition前に確認し、E3 Go / current SEI Adapter preflightは意図的に実行しない。

E2 precondition:

```text
host                    = Linux/amd64
E2 Go executable        = exact go1.23.2 linux/amd64
controlled Go target    = linux/amd64
reference input         = exact revision A fixed input
Evidence output         = inputから分離したsafe path
source temporary parent = safe existing directory
```

PR #292以降は、exact revision A fixed inputのactual identityもrevision B source acquisitionより前に既存canonical checkで検証する。

- exact A checkoutではHEAD / fixed Git object identity / working-tree purityを確認する。
- historical A Evidence bundleではbundle metadataだけを信頼せず、actual reference bytesを既存fixed identityへ照合する。
- A fixed input不整合時はE2 Go probe、B source acquisition、Evidence directory作成より前に停止する。

成功時の停止線:

```text
result = e2_bundle_verified_e3_not_run
```

partial bundle / reportはfull canonical artifactと別名であり、既存output collision / dangling symlinkはprivate source acquisition前に検査する。

```text
E2 partial bundle
  = tei-e3b-p2-revision-b-e2-partial.tar.gz

E2 partial report
  = tei-revision-b-e2-github.json
```

## E2 bundleをexact B + exact Aへstrict再検証する

PR #301 / #302により、E2 partial成功後のacquisition-independent再検証を、revision B source commitだけでなくrevision A fixed reference inputの外部固定identityへもbindingする専用入口へ揃えた。

入口:

`runtime/integration/verify_tei_version_exchange_e2_bundle.py`

この入口はgeneric bundle verifierの検証ロジックを複製せず、次を外部期待値として渡す。

```text
revision B source commit
  = 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision A fixed reference input
  source commit
  workspace tree
  durable-run blob
  plugin-lock blob
```

revision A側の正本は既存`prepare_tei_fixed_reference_input.py`の`EXPECTED_REFERENCE`である。

binary SHA-256 / Provider Plan SHA-256はactual E2で初めて観測する値なので事前固定しない。strict verifierはactual bytesから再計算し、bundle metadataとの一致を確認する。

```text
E2 partial report success
  + exact-B / exact-A strict bundle verification success
  = E2 actual Evidenceとして評価可能
```

ただし、この検証PASSだけをE3 Adapter compatibilityやISSUE-000072 Resolutionへ昇格させない。

## E2 partialからE3を後日resumeする経路

PR #295により、E2 partial Evidenceを一度保存した後、revision B source acquisitionやE2 build / Provider Plan executionを再実行せず、current SEI AdapterのE3だけを後日実行してcanonical Evidenceへ戻せるようになった。

入口:

`runtime/integration/run_tei_version_exchange_resume_from_e2_partial.py`

入力は保存済みpartial reportとbundleを別々に指定する。partial report内に記録された過去のbundle pathへ依存しないため、Evidenceを別directoryへ保管・移送した後でも、指定されたactual bundle bytesを正本として再検証できる。

resume前に次を確認する。

- partial reportが`e2_bundle_verified_e3_not_run`である。
- actual bundle source commitがexact revision Bである。
- bundle内fixed reference bytesがexact revision A identityへ一致する。
- binary / Provider Plan / archive SHA-256がpartial reportのE2 observationへ一致する。
- 保存済みGitHub acquisition Provenanceのrepository / B commit / root tree / credential source / canonical source verification状態が固定境界と整合する。
- E2のcomparison axisとGo provenanceを保持する。

resumeでは次を行わない。

```text
revision B source acquisition
E2 TEI build
E2 deployment-provider-plan execution
```

E3は既存`run_tei_bundle_adapter_compatibility.py`をそのまま使用する。

E3成功時は既存canonical schemaへ戻る。

```text
schema = sei.tei-version-exchange-evidence-run/v1
result = fixed_scope_e2_e3_verified
```

E3失敗時も既存stage semanticsを保つ。

```text
result = e2_verified_e3_failed
failure.stage = E3
```

さらにGitHub acquisition wrapper reportも既存schemaで再構成するため、成功またはstage-aware failureの結果を既存`audit_tei_version_exchange_resolution.py`へ渡せる。

resumeであることはExecution Provenanceとしてのみ保持する。

```text
executionProvenance.mode = e2_partial_then_e3_resume
```

これはCapability identity、Universal Contract、TEI Provider ontologyへ昇格させない。

```text
E2 partial Evidence
  -> exact-B / exact-A bundle identity re-verification
  -> existing E3 Adapter live runner
  -> canonical version-exchange report
  -> GitHub acquisition wrapper report
  -> existing Resolution audit
```

## interrupted report-pairをE3再実行なしで復旧する

PR #298〜#300により、resumeでE3 actualとcanonical report publishまでは完了したものの、後続GitHub wrapper reportのpublishだけが失敗した場合に、E3を再実行せずreport pairを復旧できるようにした。

入口:

`runtime/integration/reconcile_tei_e2_partial_resume_reports.py`

対象は次の限定状態である。

```text
canonical report exists
GitHub wrapper report missing
E2 partial report preserved
E2 bundle preserved
```

reconcileはpartial / bundle / canonical identityとresume provenanceを再照合し、欠落したwrapperだけを再構成する。revision B source acquisition、E2 build、Provider Plan、E3 Adapter live testは再実行しない。

既存wrapperが期待値と一致する場合は`already_consistent`でno-opとし、不一致の既存wrapperは上書きしない。

PR #300では、reconcileで再構成したwrapperが既存Resolution auditのcriterion 6へそのまま接続されることもfocused integration testで固定した。

```text
report pair reconciliation
  = interrupted publish recovery
  != E2 newly executed
  != E3 newly executed
  != Evidence promotion by itself
```

## GitHub-hosted workflow attempt 3

既存Run `33913500170` のfailed jobだけを2026-09-06に再実行した。

観測:

```text
run attempt       = 3
run started       = 2026-09-06T10:01:06Z
run updated       = 2026-09-06T10:01:10Z
job               = actual-tei-cli
job id            = 101467596158
job conclusion    = failure
job steps         = 0
artifacts          = 0
job log blob       = unavailable
```

したがって今回もactual TEI processへは到達していない。

```text
GitHub-hosted job start failure
  != revision B source checkout observed
  != TEI build failure
  != Provider Plan failure
  != SEI Adapter incompatibility
```

machine-readable observation:

`runtime/evidence/tei-version-exchange-workflow-attempt3-20260906/observation.json`

同日、別workflowでもzero-step failureが観測され、historical successful workflowでは実際にstepsが開始・完了していることも確認された。詳細は`TEI_GITHUB_HOSTED_JOB_START_DELTA_2026-09-06.md`へ分離する。この観測からroot cause名は推定しない。

## Current execution container

current containerにはhistorical E2用 `go1.23.2 linux/amd64` が存在するため、E3 Go不足だけを理由にE2を止める必要はなくなった。

一方、private `hat47x/tei-platform` sourceをcontainerへ渡すtransportはまだ成立していない。

- process environmentに `GITHUB_TOKEN` / `GH_TOKEN` はない。
- GitHub connectorはprivate Git Dataを読めるが、そのcredentialをcontainer processへ移送しない。
- connectorが返す情報を使っても、current containerの通常DNS/network境界からprivate sourceを直接取得する経路は成立していない。
- 特定hostやRemote Desktop接続をISSUE-000072の成立条件にはしない。

このtransport制約をProduct failureへ読み替えない。

```text
current container E2 Go ready
  + E2 partial / strict verification / later E3 resume path implemented
  + private source transport unavailable
  = E2 actual Not Yet Verified
```

## 次の実質的な作業

優先順位は次の通り。

1. private source transportを持つLinux/amd64環境が利用可能になれば、`TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`に従いE2 partialをactual実行する。
2. E2 partial bundleが得られたら`verify_tei_version_exchange_e2_bundle.py`でexact-B / exact-Aへstrict再検証し、actual binary / Provider Plan SHA-256を観測値として固定する。
3. E3 Go >= current `runtime/go/go.mod`を持つ環境が同時に利用できる場合はfull one-shotでE3まで進む。
4. E3 Goを後から用意する場合は、保存済みE2 partial report / bundleからresume runnerでE3だけを実行し、canonical report / GitHub wrapper reportへ戻す。
5. wrapper publishだけが中断した限定ケースではreconcileを使い、E3を再実行せずreport pairを復旧する。
6. canonical actual結果取得後にpost-run Resolution audit、Requirement / Scenario再照合、自然な日本語の最終意味監査を行う。

追加synthetic hardeningをactual Evidenceの代替にしない。
