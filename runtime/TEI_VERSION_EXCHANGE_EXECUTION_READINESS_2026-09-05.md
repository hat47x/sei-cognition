# TEI Version Exchange Execution Readiness — 2026-09-05

## 1. この文書の位置づけ

この文書は、PMS-06 / ISSUE-000072で進めているTEI executable version交換について、actual revision B実行の前に整備した検証経路と、まだ観測していない範囲を整理したものです。

ここでいう「ready」は、actual Evidenceを得たという意味ではありません。exact revision Bのsource checkoutと、historical revision Aのfixed reference inputを実行可能なLinux / amd64環境へ用意できたとき、取得・build・Provider Plan実行・current SOZA Adapter検査までをrepository-localに再現できる状態を指します。

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

AとBでは`reference/workspace` treeが異なります。そのため、B checkout内の同じpathを使うだけでは「TEI executable revisionだけを交換した比較」になりません。現在のrunnerは、exact B checkoutをbuild source、exact A checkoutをfixed reference sourceとして別々に受け取ります。

```text
exact B build source + exact A fixed input verified
  != revision B build PASS
  != Provider Plan execution PASS
```

## 3. revision B execution-source identity

`runtime/integration/verify_tei_execution_source_identity.py`は、revision Bについて次のGit object identityを固定しています。

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

同verifierは、対象境界に未commit変更やuntracked fileがないことも確認します。revision A fixed inputについては、前節のworkspace / durable run / plugin lock identityを別のexpected object setとして検証します。

この検査はsource identityです。binary bytesやruntime結果を導出しません。

## 4. Provider Plan surfaceの静的Evidence

`runtime/TEI_PROVIDER_SURFACE_STATIC_COMPATIBILITY_2026-09-05.md`では、A / BのProvider Plan出力surfaceと、その前段を分けて確認しています。

静的に強い連続性を確認した領域:

```text
cmd/tei/main.go
  = exact same Git blob

internal/deployment
  = exact same Git tree

internal/environment
  = exact same Git tree

internal/releaseplan
  = exact same Git tree

internal/plugin/runtime
  = exact same Git tree

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

したがって、既知のProvider Plan出力surfaceとdeployment中核には静的連続性がありますが、fixed reference inputをBのworkspace / validation経路がactualに受理することは推定しません。

```text
same Provider Plan output surface
  != same input interpretation
  != revision B actual execution PASS
```

## 5. E2 — actual revision B bundle生成経路

`runtime/integration/run_tei_revision_b_prepositioned.py`は、GitHub Actionsを使わず、prepositionedされた2つのcheckoutからEvidence bundleを生成するrunnerです。

入力:

- `--source-repo`: exact revision B。build sourceとしてのみ使用する。
- `--reference-source-repo`: exact revision A。fixed reference inputとしてのみ使用する。
- `--output-archive`: 生成するEvidence bundle。

主な処理:

1. B execution-source Git identityとexact HEADを確認する。
2. A fixed reference input Git identityとexact HEADを確認する。
3. Linux / amd64、Go `1.23.2`を要求する。
4. historical Evidenceと同じ`go build -trimpath -ldflags='-s -w' ./cmd/tei`でB CLIをbuildする。
5. B binaryへAのworkspace / durable run / plugin lockを渡し、`deployment-provider-plan`を実行する。
6. Provider Planの既知top-level surfaceを確認する。
7. B binary SHA-256、Provider Plan SHA-256、A reference identityをmetadataへ記録する。
8. Evidence bundleを生成し、`verify_tei_evidence_bundle.py`で再検証してからfinal archiveへ配置する。

build時は`GOWORK=off`、`GOENV=off`とし、外部`GOFLAGS` / `GOOS` / `GOARCH`を持ち込みません。

このrunnerのsynthetic / fixed-input isolation検査はPASSしていますが、actual revision B checkoutを用いたbuild / Provider Plan実行はまだ行っていません。

## 6. E3 — current SOZA Adapter live検査経路

`runtime/integration/run_tei_bundle_adapter_compatibility.py`は、E2で得たEvidence bundleをcurrent SOZA Adapterへ接続するrunnerです。

主な処理:

1. `verify_tei_evidence_bundle.py`でB source / binary / Provider Plan identityを再検証する。
2. archive traversal、link / device、duplicate memberを拒否する。
3. `bin/tei`とA fixed reference inputだけを一時領域へstageする。
4. bundle metadataのA reference identityを固定値へ照合する。
5. staged workspaceのGit tree SHA、durable run / plugin-lockのGit blob SHAをactual bytesから再計算する。
6. current SOZAの`runtime/go`とEvidence runner / verifierのGit object identityを記録し、その境界に未commit変更やuntracked fileがないことを要求する。
7. `GOTOOLCHAIN=local`でSOZA側の使用toolchainを記録し、検査中の暗黙toolchain downloadを行わない。
8. 既存`runtime/go/teiintegration.TestLiveTEIProviderPlan`だけを実行する。

既存live testが確認する意味境界は次です。

- actual TEI CLIを別OS processとして起動できる。
- Provider Planをcurrent Adapter-local DTOでstrictにdecodeできる。
- current Capability Observation validatorを通る。
- `availability = true`を観測できる。
- `provider_plan_resolved = true`を観測できる。
- Provider固有の`executors` / `observations` / `evidence` / `pluginRuntime`をUniversal Capability Observationへ漏らさない。
- `SourceStateRef`をMapping Provenanceとして保持する。

runnerは、B source commit、A fixed input commit、bundle SHA-256を`SourceStateRef`へ含めます。また、どのSOZA source / toolchainで検査したかも結果へ残します。

runner自身のsynthetic testは8件PASSしています。

```text
Adapter live runner ready
  != actual revision B Adapter compatibility PASS
```

## 7. 現在のEvidence状態

```text
revision A fixed source / actual CLI
  = Scoped Executable Evidence available

revision A artifact re-acquisition / bundle identity re-verification
  = verified

revision B source identity
  = fixed to 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision B execution-source Git identity
  = fixed; repository-local verifier implemented

Provider Plan output surface A/B
  = strong static continuity observed

deployment / environment / releaseplan / plugin-runtime / core
  = exact source-tree continuity observed

workspace / validation / IR input interpretation
  = changed; actual fixed-input execution required

version-exchange comparison axis
  = exact-B build source + exact-A fixed reference input

prepositioned B Evidence runner
  = implemented; synthetic / fixed-input isolation checks passed

bundle → current Adapter live runner
  = implemented; 8 synthetic tests passed

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

## 8. actual実行時の順序

実行可能なLinux / amd64環境が利用できたら、次の順序で進めます。

```text
exact revision B checkout
exact revision A checkout
  ↓
verify source identities
  ↓
run_tei_revision_b_prepositioned.py
  ↓
verify generated Evidence bundle
  ↓
record B binary / Provider Plan digests
  ↓
clean SOZA checkout + local Go toolchain
  ↓
run_tei_bundle_adapter_compatibility.py
  ↓
record current Adapter / Capability Observation result
```

E2が失敗した場合、取得、source identity、Go toolchain、build、workspace load、validation、durable run、plugin lock、Provider Plan生成のどこで停止したかを分けて記録します。

E3が失敗した場合、bundle identity、A fixed input identity、SOZA source identity、SOZA toolchain、external process、strict decode、Observation mapping / validationのどこで停止したかを分けて記録します。

failureを別の層へ昇格させません。

## 9. 残る停止線

```text
static source continuity
  != actual execution

exact B source verified
  != B binary built

exact A fixed input verified
  != B accepts A input

B Evidence bundle produced
  != current SOZA Adapter compatibility verified

current SOZA Adapter compatibility verified for one fixed bundle
  != arbitrary TEI version compatibility
  != formal Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

actual B Evidenceを得る前に、新しいStable RequirementやUniversal TEI fieldを追加しません。GitHub ActionsもISSUE-000072の意味上の成立条件にはしません。
