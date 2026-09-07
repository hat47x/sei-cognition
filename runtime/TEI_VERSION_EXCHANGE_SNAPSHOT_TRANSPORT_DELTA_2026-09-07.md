# TEI Version Exchange Snapshot Transport Delta — 2026-09-07

## 位置づけ

本書は `TEI_VERSION_EXCHANGE_CURRENT_DELTA_2026-09-07.md` の後に生じた snapshot transport 実装と current execution surface の変化だけを追記する delta である。

Stable Requirement、Universal Contract、comparison axis、supported scope、quality judgement、ISSUE-000072 Resolution 条件は変更しない。

固定比較軸:

```text
revision B executable source
  = 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision A fixed reference input
  = 48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
```

## 1. private source transport の分類を更新する

従来の current delta では、current container から private exact-B source を取得できないことを `private B source transport unavailable` と表現していた。

PR #312 / #313 取り込み後、この表現は二つの層へ分離する。

```text
repository-side transport implementation
  = available

actual snapshot bytes
  = Not Yet Acquired
```

実装済み経路:

- GitHub credentialを持つonline環境で canonical Git Data acquisition を行い、消費したresponseをcredential-free snapshotへ保存する。
- offline環境でsnapshot schema / provenanceを固定値へ照合する。
- snapshot内blob/tree/signed commitをGit object identityへ再計算する。
- exact revision B checkoutをcanonical verifierへ戻す。
- 同じpartial report schemaのままexisting E2 build / `deployment-provider-plan`へ接続する。
- source acquisition provenanceとcross-environment transport provenanceを分離する。

```text
source acquisition
  = github-git-data-api-content-addressed

source transport
  = preacquired-github-git-data-snapshot
```

## 2. merged implementation

### PR #312

snapshot producer / consumer を追加した。

- `runtime/integration/capture_tei_revision_b_git_data_snapshot.py`
- `runtime/integration/prepare_tei_revision_b_source_from_snapshot.py`
- associated boundary tests

PR #312 は 2026-09-07 に `develop/v0.2.0` へ merge 済み。

### PR #313

snapshotからexact-Bを再構成し、そのまま existing E2 partial contract へ接続する one-shot runner を追加した。

- `runtime/integration/run_tei_revision_b_e2_from_snapshot.py`
- associated boundary tests

PR #313 は PR #312 merge 後に `develop/v0.2.0` へ retarget し、2026-09-07 に merge 済み。

## 3. actual execution surface の再確認

repository-side implementation merge 後も、actual snapshot を生成できる execution surface は current check で得られていない。

### current container

`api.github.com` へのDNS解決を再確認したが、引き続き失敗した。

```text
getent hosts api.github.com
  = no result

curl https://api.github.com
  = DNS resolution timeout / failure
```

process environmentに `GITHUB_TOKEN` / `GH_TOKEN` も存在しない。

一方、E2 buildに固定したGoは利用できる。

```text
go version
  = go1.23.2 linux/amd64
```

したがって current container はE2 execution側としては利用可能だが、private GitHubからonline captureを行うsurfaceではない。

### Remote Desktop

Remote Desktop Commander では device `HAT47X` は登録されているが current status は `offline` である。

したがって current remote execution surface も利用できない。

### GitHub-hosted Actions

TEI repository の直近別workflow runも確認した。

```text
run id   = 34025808221
job      = verify
job id   = 101466442426
result   = failure
steps    = []
runner   = not assigned
```

これは別workflowでも GitHub-hosted job が Product step を開始できていない観測である。

既存 actual workflow Run `33913500170` の `actual-tei-cli` job は attempt 5 で次の状態だった。

```text
run attempt       = 5
run started       = 2026-09-07T00:26:26Z
run updated       = 2026-09-07T00:26:32Z
job               = actual-tei-cli
job id            = 101584981228
job created       = 2026-09-07T00:26:28Z
job started       = 2026-09-07T00:26:28Z
job completed     = 2026-09-07T00:26:31Z
label             = ubuntu-latest
runner id         = 0
runner name       = empty
steps             = 0
artifacts         = 0
```

machine-readable Evidence:

`runtime/evidence/tei-version-exchange-workflow-attempt5-20260907/observation.json`

その後のcurrent checkでは、同じRunが attempt 6 まで進んでいることを観測した。attempt 6を本作業で開始したとは扱わず、GitHub metadataから観測した事実だけを記録する。

```text
run attempt       = 6
run started       = 2026-09-07T02:01:44Z
run updated       = 2026-09-07T02:01:50Z
job               = actual-tei-cli
job id            = 101599002058
job created       = 2026-09-07T02:01:46Z
job started       = 2026-09-07T02:01:46Z
job completed     = 2026-09-07T02:01:49Z
label             = ubuntu-latest
runner id         = 0
runner name       = empty
steps             = 0
artifacts         = 0
```

attempt 6でもrunner assignment、revision B checkout、Go setup、TEI build、Provider Plan executionのstep開始を観測していない。したがってfailure分類は引き続き GitHub-hosted job-start 層に留める。

machine-readable Evidence:

`runtime/evidence/tei-version-exchange-workflow-attempt6-20260907/observation.json`

```text
hosted attempt 6 zero-step observation
  != revision B checkout failure
  != TEI build failure
  != Provider Plan failure
  != SOZA Adapter incompatibility
```

同じjob-start surfaceの即時再試行をactual executionの代替にはしない。

### historical bootstrap payload の境界

TEI repository内の `bootstrap/final-source` / `bootstrap/publish` 等も再確認したが、これらは2026-08-30の `Complete verified TEI M0.22.1 source payload` 等で形成されたhistorical bootstrapである。

固定revision Bは2026-09-04のcommit `1a7028d444fcae60a1c4f2f2d247456f4c7c35be` であり、root treeは `630d3e9e2acaea70312bee19cf8a0f7235655cd6` である。

したがってhistorical bootstrap payloadを復元しただけでは、exact-B source acquisitionにもactual exact-B snapshot acquisitionにもならない。

```text
historical M0.22.1 bootstrap restored
  != exact revision B source acquired
  != exact-B Git Data snapshot acquired
  != revision B actual E2
```

bootstrap内容をactual-B sourceとして扱うこと、またその復元完了をT1 online captureの代替として数えることは禁止する。何らかの復元ベースとして利用する場合でも、最終的にfixed-B Git object identityへ再構成・照合されない限りactual-B Evidenceには昇格させない。

## 4. operator path

snapshot transport 専用のactual手順は次を正本とする。

`runtime/TEI_E2_SNAPSHOT_TRANSPORT_ACTUAL_RUNBOOK_2026-09-07.md`

標準順序:

```text
T1 online capture
  ↓
credential-free Git Data snapshot
  ↓
T2 offline exact-B reconstruction
  ↓
exact Go 1.23.2 + exact-A fixed input
  ↓
actual E2 build / deployment-provider-plan
  ↓
exact-B / exact-A strict bundle verification
  ↓
later E3 resume
  ↓
Resolution audit
```

T1 と T2 を同一hostで行う必要はない。

## 5. Current state

```text
revision B Git object identity                    = fixed
repository-side direct Git Data acquisition      = implemented
repository-side snapshot capture                 = implemented + merged
repository-side snapshot materialization         = implemented + merged
snapshot -> E2 partial one-shot                   = implemented + merged
repository-side E2 partial path                   = implemented
exact-B / exact-A strict E2 bundle verification  = implemented
later E3 resume                                  = implemented
report-pair reconcile                            = implemented

revision A historical artifact                   = acquired and identity-verified
revision A fixed input bytes                      = available in current container
revision A portable re-execution                  = verified
current container E2 Go 1.23.2                   = available

actual exact-B snapshot                           = Not Yet Acquired
current online capture execution surface          = unavailable
current container GitHub DNS                      = unavailable
Remote Desktop HAT47X                             = offline
latest TEI hosted actual attempt                  = 6
latest TEI hosted Product step                    = not observed
latest TEI hosted runner assignment               = not observed
historical M0.22.1 bootstrap as exact-B source    = rejected

revision B actual build                           = Not Yet Verified
revision B Provider Plan                          = Not Yet Observed
current SOZA Adapter compatibility                = Not Yet Verified
qualityJudgement                                  = not_evaluated
ISSUE-000072                                      = Open
```

## 6. 次に行うactual作業

次に GitHub private repository access を持つ online execution surface が利用可能になった時点では、追加の transport 設計を行わず、次の順序を優先する。

1. `capture_tei_revision_b_git_data_snapshot.py` で actual snapshot を生成する。
2. capture report の snapshot SHA-256 を記録する。
3. snapshot を Linux/amd64 E2環境へ transfer する。
4. `run_tei_revision_b_e2_from_snapshot.py` で actual E2 partial を実行する。
5. `verify_tei_version_exchange_e2_bundle.py` で exact-B / exact-A strict verification を行う。
6. binary SHA-256 / Provider Plan SHA-256 を actual observation として固定する。
7. current SOZA E3要件が成立する環境で later E3 resume を行う。
8. canonical report / wrapper report を Resolution audit へ接続する。

## 停止線

```text
transport implementation merged
  + offline E2 path merged
  + A fixed input ready
  + E2 Go ready
  + hosted attempt 6 zero-step observation
  + historical bootstrap boundary clarified
  != actual exact-B snapshot acquired
  != revision B actual E2 PASS
  != Provider Plan PASS
  != E3 SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

追加bootstrap探索やsynthetic hardeningをactual executionの代替にしない。
