# TEI GitHub-hosted Job Start Delta — 2026-09-06

## 位置づけ

本書は、`SOZA E3b-P2 TEI Evidence` workflow attempt 1〜3がjob step開始前にfailureとなった事象について、同じ`hat47x/tei-platform` repository内の独立workflowとhistorical successを照合したcurrent deltaである。

原因名を推定する文書ではない。GitHub Actions、特定CI provider、特定execution hostをISSUE-000072のProduct semanticsやResolution条件へ昇格させない。

## 観測1 — TEI Evidence workflow attempt 3

Run `33913500170` attempt 3:

```text
workflow       = SOZA E3b-P2 TEI Evidence
runner         = ubuntu-latest
job            = actual-tei-cli
job id         = 101467596158
run started    = 2026-09-06T10:01:06Z
run updated    = 2026-09-06T10:01:10Z
conclusion     = failure
steps          = 0
artifacts      = 0
job log blob   = unavailable
```

workflow定義では、通常のGitHub-hosted `ubuntu-latest` jobを使っている。revision B checkout、Go setup、build、Provider Plan executionはいずれもjob stepであり、今回そのstep開始自体を観測していない。

## 観測2 — 独立workflowでも同じzero-step failure

Run `34025808221`:

```text
workflow       = Verify business-procedure cross-view reference
workflow path  = .github/workflows/business-procedure-cross-view-reference.yml
head SHA       = 403945d2c02195feaa41875cb37b859ec767cff7
runner         = ubuntu-latest
job            = verify
job id         = 101466442426
created        = 2026-09-06T09:51:19Z
updated        = 2026-09-06T09:51:23Z
conclusion     = failure
steps          = 0
```

このworkflowはTEI E3b-P2 Evidenceとは別の目的・別のworkflow file・別のjobである。したがって、少なくともTEI Evidence workflow内のbuild commandやProvider Plan commandだけを原因とする説明では、2026-09-06の観測全体を説明できない。

```text
independent workflow A: zero-step failure
independent workflow B: zero-step failure

  -> cross-workflow GitHub-hosted job-start common surface observed
  != root cause identified
```

## 観測3 — historical positive control

GitHub APIで2026-09-06に確認した最新successful runはRun `33634416735`である。

```text
workflow       = 一時的にQuery result mapping Validationを共通入口へ接続
created        = 2026-09-02T13:13:13Z
updated        = 2026-09-02T13:13:24Z
job            = connect
job id         = 100261564372
conclusion     = success
completed steps observed = 6
```

したがって、このprivate repositoryでGitHub-hosted jobが歴史上一度も開始できなかったわけではない。少なくとも2026-09-02には実stepを伴うsuccessful runが成立していた。

## 言えること / 言えないこと

現在言えること:

- 2026-09-06には異なる複数workflowでGitHub-hosted jobがstep 0 failureとなっている。
- 両workflowのjobは`ubuntu-latest`を指定している。
- TEI Evidence workflow attempt 3ではTEI source checkout / build / Provider Plan processへ到達していない。
- 2026-09-02には同repositoryでsuccessful hosted runを観測できる。

現在言えないこと:

- billingが原因である。
- repository Actions policyが原因である。
- GitHub側障害が原因である。
- workflow syntax / action versionが原因である。
- TEI Productが原因である。

これらの具体的root causeはmachine-readableなjob-start reasonを取得できるまで`unobserved`とする。

## ISSUE-000072への意味

このcross-workflow観測は、attempt 3のfailureをより狭く分類するためのExecution Environment Evidenceであり、E2/E3 Product Evidenceの高さを上げない。

```text
cross-workflow zero-step failure observed
  != revision B actual executable observed
  != revision B build failure
  != Provider Plan incompatibility
  != current SOZA Adapter incompatibility
```

したがって、repository-local / E2 partial経路を維持し、private revision B sourceを取得できる適切なLinux/amd64環境が利用可能になった時点でactual E2を優先する方針は変えない。

machine-readable observation:

`runtime/evidence/tei-github-hosted-job-start-cross-workflow-20260906/observation.json`

## 停止線

```text
GitHub-hosted common job-start surface implicated
  != root cause identified
  != Product failure
  != E2 PASS
  != E3 PASS
  != ISSUE-000072 Resolved
```

Stable Requirement、Universal Contract、comparison axis、supported scope、quality judgementは変更しない。
