# TEI Version Exchange Current Delta — 2026-09-07

## 位置づけ

本書は、`TEI_VERSION_EXCHANGE_E2_PARTIAL_DELTA_2026-09-06.md` の後に得られたcurrent execution / transport観測をまとめるdeltaである。

Stable Requirement、Universal Contract、comparison axis、supported scope、quality judgement、ISSUE-000072 Resolution条件は変更しない。

比較軸は引き続き次を固定する。

```text
revision B executable source
  = 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision A fixed reference input
  = 48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
```

operator向けactual手順の正本は次である。

`runtime/TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`

## 1. bootstrap/final-source transportはfixed revision Bとしてrejectした

current containerへprivate sourceを渡す補助経路として、revision B commit内の`bootstrap/final-source` 62 chunkをGitHub connector経由で再構成した。

観測:

- 62 / 62 chunkを取得した。
- 各chunkのactual bytesをlocal `git hash-object`でGitHub側blob SHAへ再照合し、不一致は0だった。
- concatenated payloadはstrict Base64 decodeに成功した。
- XZ完全復号に成功した。
- 復号結果は258-member tarで、absolute path、`..` traversal、symlink / hardlink、device entryは観測しなかった。

したがってconnector-mediated transport bytes自体のintegrityは確認できた。

しかし、展開sourceをfixed revision B execution-source identityへ戻すと一致しなかった。

代表例:

```text
go.mod
  observed blob = 8a50045f...
  revision B    = f8763f8fb2d64d73f1b40b905f62b5e09c44493b

cmd/tei/main.go
  observed blob = 233be1fd...
  revision B    = 6a27b98b7f6dbe4e66d1261edfc847402cd608a5

cmd tree
  observed      = 696368eb...
  revision B    = ac4d4406dfa590a2078cf91217c4fe30797e7f8e

internal tree
  observed      = 837d498e...
  revision B    = 10d2bfea4932c308fa6537e3b081bc6ea5501205

reference tree
  observed      = 25470d5b...
  revision B    = 57fafb742988ecb936b9ab261fa8a991e37ed5c7
```

さらに、fixed revision Bで期待する`go.sum`、`cmd/tei/source_index.go`、`cmd/tei/validation_output.go`も展開payloadには存在しなかった。

よって、このpayloadはactual revision B inputとしてrejectする。

```text
bootstrap transport integrity PASS
  != bootstrap payload == revision B
  != exact-B checkout
  != E2 build PASS
```

machine-readable Evidence:

`runtime/evidence/tei-bootstrap-source-identity-rejection-20260907/observation.json`

## 2. source-safe / materializeはcanonical acquisitionの代替へ昇格させない

`bootstrap/source-safe`を確認すると、少なくとも観測したhead / tail entryのblob SHAは`final-source`で使われていたblob群と重なっている。

したがって、`source-safe`というdirectory名だけを根拠に独立したfixed-B source transportとは扱わない。

`bootstrap/materialize`には別の5-part payloadが存在し、`part-00`先頭はBase64/XZ形式として読める。しかしcurrent containerからconnectorが返すsigned raw URLへ直接接続する試行はDNS name resolution failureで停止した。

そのためmaterialize payloadの全byte transport / decode / fixed-B identityは未検証であり、actual B inputへは昇格させない。

```text
materialize payload exists
  != materialize bytes acquired
  != materialize payload identity verified
  != revision B source acquired
```

bootstrap領域の追加探索をactual Evidenceの代替にしない。canonical source取得経路は引き続き次を正とする。

- self-contained local Git object databaseからのexact-B checkout preparation
- GitHub Git Data APIからのcontent-addressed exact-B reconstruction

## 3. GitHub-hosted workflow attempt 4もProduct stageへ到達しなかった

Run `33913500170` のfailed jobを再実行したattempt 4を観測した。

```text
run attempt       = 4
run started       = 2026-09-06T16:46:19Z
run updated       = 2026-09-06T16:46:25Z
job               = actual-tei-cli
job id            = 101522401332
job created       = 2026-09-06T16:46:21Z
job started       = 2026-09-06T16:46:21Z
job completed     = 2026-09-06T16:46:24Z
label              = ubuntu-latest
runner id          = 0
runner name        = empty
steps              = 0
artifacts          = 0
```

今回もrevision B checkout、Go setup、TEI build、Provider Plan executionのstep開始を観測していない。runner assignmentも観測できていない。

したがってfailure分類は引き続きGitHub-hosted job-start層に留める。

```text
zero-step hosted job failure
  != TEI build failure
  != Provider Plan failure
  != SOZA Adapter incompatibility
```

machine-readable Evidence:

`runtime/evidence/tei-version-exchange-workflow-attempt4-20260907/observation.json`

具体的root cause名は推定しない。

## 4. current execution environment

current containerではhistorical E2用toolchainは成立している。

```text
host            = Linux / x86_64
E2 Go           = go1.23.2 linux/amd64
```

一方、private revision B source transportは成立していない。

- process environmentに`GITHUB_TOKEN` / `GH_TOKEN`はない。
- GitHub connectorのprivate repository credentialはcontainer processへ移送しない。
- signed raw URLを使ったdirect downloadもcurrent containerのDNS name resolutionで停止した。
- Remote Desktop Commanderには2026-09-07 current check時点で接続deviceがない。
- GitHub-hosted attempt 4もstep 0 / runner未割当観測で終了した。

これらはexecution-environment blockerであり、Product failureではない。

```text
E2 Go ready
  + repository-side E2 partial path ready
  + private exact-B source transport unavailable
  = E2 actual Not Yet Verified
```

## 5. 次に行うactual作業

適切なLinux/amd64 execution environmentまたはprivate source transportが利用可能になった時点では、追加bootstrap探索やsynthetic hardeningよりactual E2 partialを優先する。

標準順序:

1. `TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`に従い、GitHub Git Data APIまたはself-contained local sourceからexact revision Bを取得する。
2. exact revision A fixed input + exact Go 1.23.2でE2 partialをactual実行する。
3. `verify_tei_version_exchange_e2_bundle.py`でexact-B / exact-Aへacquisition-independentにstrict再検証する。
4. actual binary SHA-256 / Provider Plan SHA-256を観測値として固定する。
5. current SOZA要件を満たすE3 Goが利用可能なら、保存済みE2 partialからE3だけをresumeする。
6. canonical report / GitHub wrapper reportをResolution auditへ接続する。

## 6. Current state

```text
revision B Git object identity                    = fixed
repository-side exact-B acquisition path         = implemented
repository-side E2 partial path                  = implemented
exact-B / exact-A strict E2 bundle verification  = implemented
later E3 resume                                  = implemented
report-pair reconcile                            = implemented

bootstrap/final-source as B input                = rejected
current container E2 Go 1.23.2                   = available
current container private source transport       = unavailable
Remote Desktop execution                         = unavailable
GitHub-hosted attempt 4 Product step             = not observed

revision B actual build                          = Not Yet Verified
revision B Provider Plan                         = Not Yet Observed
current SOZA Adapter compatibility               = Not Yet Verified
qualityJudgement                                 = not_evaluated
ISSUE-000072                                     = Open
```

## 停止線

```text
transport investigation completed
  != revision B actual source acquired
  != revision B E2 PASS
  != Provider Plan PASS
  != E3 SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

Stable Requirement、Universal Contract、comparison axis、supported scopeは変更しない。
