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

さらにGit履歴を確認すると、`bootstrap/materialize`のlatest observed staging commitは`6edeb3a05eecac90ee340665a78c515e24eca2f6`（2026-08-30T01:21:09Z、`Stage compact TEI M0.22.1 source tail 2/3`）である。そこからfixed revision Bまではcompare上1,834 commits進んでおり、fixed-Bの`cmd/tei/main.go`はこの区間で1,152行のadded fileとして現れる。

これはmaterialize payloadの個々のdecoded bytesがrevision Bと不一致であることを、未復号のまま証明するものではない。一方で、historical M0.22.1 staging payloadをfixed-Bのcanonical source acquisition候補として扱う根拠も与えない。したがってfull-byte transport / decodeを追加bootstrap探索の優先課題へ戻さず、actual B inputへは昇格させない。

```text
materialize payload exists
  + historical M0.22.1 staging provenance observed
  + fixed-B source evolved afterwards
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
controlled GOOS = linux
controlled GOARCH = amd64
```

また、historical revision A GitHub Actions artifact `9831112092` をcurrent containerへ取得し、repository-localに保存された期待identityへ再照合した。

```text
artifact ZIP SHA-256
  expected = 1ee8bf4112d9ae97e1f66b3165f70278663951e9dd4bd6020b465471f563a287
  observed = 1ee8bf4112d9ae97e1f66b3165f70278663951e9dd4bd6020b465471f563a287

inner Evidence bundle SHA-256
  expected = 6c1728abe75f9d3486dbe4676621c553d07e07e345cd09ec837e8d632f484f52
  observed = 6c1728abe75f9d3486dbe4676621c553d07e07e345cd09ec837e8d632f484f52
```

bundle内にはexact-A固定比較に必要なhistorical reference bytesが存在する。

- `reference/workspace`
- `reference/order_rollout.durable-run.m0.21.start.json`
- `reference/workspace/.tei/plugin-lock.json`

同bundleのhistorical binaryをcurrent containerで再実行した。

```text
exit code                    = 0
stderr bytes                 = 0
stdout bytes                 = 8226
binary SHA-256               = 31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154
Provider Plan SHA-256        = 39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950
stdout == bundled plan bytes = true
```

よって、current containerではrevision A fixed reference inputのactual bytesとhistorical executableのportable re-executionを利用できる。

machine-readable Evidence:

`runtime/evidence/tei-revision-a-current-container-reexecution-20260907/observation.json`

一方、private revision B source transportは成立していない。

- process environmentに`GITHUB_TOKEN` / `GH_TOKEN`はない。
- GitHub connectorのprivate repository credentialはcontainer processへ移送しない。
- signed raw URLを使ったdirect downloadもcurrent containerのDNS name resolutionで停止した。
- Remote Desktop Commanderには2026-09-07 current check時点で接続deviceがない。
- GitHub-hosted attempt 4もstep 0 / runner未割当観測で終了した。

さらにfixed-B `go.mod`は`github.com/lib/pq v1.12.3`を要求するが、current containerのGo module cacheにはこのmodule versionが存在しない。したがって、source bytesだけを手作業で移送しても、current network制約下ではcanonical E2 build前提がまだ完結しない。

これらはexecution-environment blockerであり、Product failureではない。

```text
E2 Go ready
  + revision A fixed input ready and re-executed
  + repository-side E2 partial path ready
  + private exact-B source transport unavailable
  + required B build dependency not cached locally
  = E2 actual Not Yet Verified
```

## 5. 次に行うactual作業

適切なLinux/amd64 execution environmentまたはprivate source/dependency transportが利用可能になった時点では、追加bootstrap探索やsynthetic hardeningよりactual E2 partialを優先する。

標準順序:

1. `TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`に従い、GitHub Git Data APIまたはself-contained local sourceからexact revision Bを取得する。
2. current containerで取得・再実行済みのhistorical A Evidence bundleと同一identityのexact-A fixed input + exact Go 1.23.2でE2 partialをactual実行する。
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
bootstrap/materialize as canonical B route       = not accepted
current container E2 Go 1.23.2                   = available
revision A historical artifact                   = acquired and identity-verified
revision A fixed input bytes                      = available in current environment
revision A portable re-execution                  = verified
current container private B source transport      = unavailable
current container B build dependency cache        = incomplete
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
revision A current-environment re-execution PASS
  + transport investigation completed
  != revision B actual source acquired
  != revision B E2 PASS
  != Provider Plan PASS
  != E3 SOZA Adapter compatibility PASS
  != ISSUE-000072 Resolved
```

Stable Requirement、Universal Contract、comparison axis、supported scopeは変更しない。