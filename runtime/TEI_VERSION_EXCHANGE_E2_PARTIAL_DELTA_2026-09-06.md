# TEI Version Exchange E2 Partial Delta — 2026-09-06

## 位置づけ

本書は `TEI_VERSION_EXCHANGE_CURRENT_READINESS_2026-09-06.md` の後に追加された、revision B E2 partial Evidence経路とGitHub-hosted workflow attempt 3の観測だけをまとめるcurrent deltaである。

Stable Requirement、Universal Contract、comparison axis、quality judgement、ISSUE-000072 Resolution条件は変更しない。

```text
E2 partial path available
  != revision B E2 PASS
  != E3 SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

## E2 partial Evidence入口

PR #289〜#291により、E3 Go toolchainがまだ用意できない環境でも、GitHub acquisitionからrevision BのE2だけを先行回収できる入口を追加した。

入口:

`runtime/integration/run_tei_revision_b_e2_from_github.py`

この経路はfull E2→E3 one-shotを弱めない。E2に必要な条件だけをsource acquisition前に確認し、E3 Go / current SOZA Adapter preflightは意図的に実行しない。

E2 precondition:

```text
host                   = Linux/amd64
E2 Go executable       = exact go1.23.2 linux/amd64
controlled Go target   = linux/amd64
reference input        = exact revision A fixed input
Evidence output        = inputから分離したsafe path
source temporary parent= safe existing directory
```

成功時の停止線:

```text
result = e2_bundle_verified_e3_not_run
```

partial bundle / reportはfull canonical artifactと別名であり、既存output collision / dangling symlinkはprivate source acquisition前に検査する。

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
  != SOZA Adapter incompatibility
```

machine-readable observation:

`runtime/evidence/tei-version-exchange-workflow-attempt3-20260906/observation.json`

## Current execution container

current containerにはhistorical E2用 `go1.23.2 linux/amd64` が存在するため、E3 Go不足だけを理由にE2を止める必要はなくなった。

一方、private `hat47x/tei-platform` sourceをcontainerへ渡すtransportはまだ成立していない。

- process environmentに `GITHUB_TOKEN` / `GH_TOKEN` はない。
- GitHub connectorはprivate Git Dataを読めるが、そのcredentialをcontainer processへ移送しない。
- connectorが返す短寿命raw download URLも、current containerのDNS/network boundaryから直接取得できなかった。
- HAT47X Remote Desktopは今回も未接続だった。

このtransport制約をProduct failureへ読み替えない。

```text
current container E2 Go ready
  + E2 partial runner implemented
  + private source transport unavailable
  = E2 actual Not Yet Verified
```

## 次の実質的な作業

優先順位は次の通り。

1. private source transportを持つLinux/amd64環境が利用可能になれば、E2 partialを先にactual実行する。
2. E2 bundleが得られたらsource / binary / Provider Plan identityを固定し、ISSUE-000072 E2を評価する。
3. E3 Go >= current `runtime/go/go.mod`を持つ環境でcanonical E3 live compatibilityへ進む。
4. actual結果取得後にpost-run Resolution audit、Requirement / Scenario再照合、自然な日本語の最終意味監査を行う。

追加synthetic hardeningをactual Evidenceの代替にしない。
