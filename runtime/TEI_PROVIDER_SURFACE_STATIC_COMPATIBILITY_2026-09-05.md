# TEI Provider Surface Static Compatibility — 2026-09-05

## 1. この文書の位置づけ

この文書は、ISSUE-000072で固定したTEI revision A / Bについて、actual revision B executableを取得・実行する前に確認できる**静的なProvider Plan surfaceの互換性**を記録します。

対象revisionは次です。

- revision A: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- revision B: `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`

GitHub compareではBはAより1748 commits aheadです。この差の大きさからrepository全体の同一性は前提にしません。一方、今回のfixed invocationで直接利用するProvider Plan surfaceについては、content-addressedなGit object identityを比較できます。

この確認はDesign / Static Evidenceです。revision Bのactual binary、actual Provider Plan output、current SOZA Adapterのlive互換性を証明するものではありません。

## 2. `deployment-provider-plan`入口のsource identity

A / Bの`cmd/tei/main.go`は、どちらも同じGit blob SHAを持っています。

```text
cmd/tei/main.go
  A blob: 6a27b98b7f6dbe4e66d1261edfc847402cd608a5
  B blob: 6a27b98b7f6dbe4e66d1261edfc847402cd608a5
```

このfileには`deployment-provider-plan` CLI入口と、Provider Planのtop-level JSON shapeが定義されています。

```go
type deploymentProviderPlan struct {
    Executors     []deploymentrouting.RoutedCommand `json:"executors,omitempty"`
    Observations  []providerRoute                   `json:"observations,omitempty"`
    Evidence      []providerRoute                   `json:"evidence,omitempty"`
    PluginRuntime *pluginruntime.EnvironmentPlan    `json:"pluginRuntime,omitempty"`
}
```

routeのtop-level elementもA / Bで同じsourceです。

```go
type providerRoute struct {
    Kind     string           `json:"kind"`
    Provider core.CanonicalID `json:"provider"`
    ActionID string           `json:"actionId,omitempty"`
}
```

したがって、少なくとも`deployment-provider-plan`のCLI入口と、`executors` / `observations` / `evidence` / `pluginRuntime`というtop-level JSON surfaceについて、AからBへのsource-level driftは観測されません。

## 3. 埋め込まれる主要型のsource identity

Provider Planの内部型についても、current SOZA Adapterとの境界に直接関係する主要fileをA / Bで比較しました。

```text
internal/deployment/routing/executor.go
  A/B blob: be6854ea5c3eb915e094b7a7cda3a10eb8a434b7

internal/plugin/runtime/model.go
  A/B blob: 7b4429c5015854efff8761d5b1c2358d9241a1ec
```

前者は`executors`の`deploymentrouting.RoutedCommand`、後者は`pluginRuntime`の`pluginruntime.EnvironmentPlan`を支えるsourceです。

さらに、`deployment-provider-plan`で直接利用する主要subtreeには、A / Bでtree全体が同一のものがあります。

```text
internal/deployment
  A/B tree: e398c3723b638eb033a4b3bb96a9964377734805

internal/environment
  A/B tree: e5b85c854f439566aaa12b4653d57cde599567aa

internal/releaseplan
  A/B tree: 69c2dee2f92056b3520a23c959218dbfbd4d4919

internal/plugin/runtime
  A/B tree: e306aab50112c28d656303e6cb1a192c8a16f9ef

internal/core
  A/B tree: 70a7f2219dcfeaff4cc0a7b1b324e656d8e6915a
```

この同一性は、A / Bで当該source bytesが同一であることを示します。ただし、workspace、durable run、plugin lock、environment等の入力から生成される**実際の値**まで同一であることは意味しません。

## 4. Provider Plan生成前段にはA/B差分が残る

`deployment-provider-plan`は、top-level JSONを組み立てる前に次の処理を通ります。

```text
workspace.Load
  ↓
validation.Validate
  ↓
loadCheckedDeploymentRun
  ↓
releaseplan.CompileWithDeployment
  ↓
deployment durable checks
  ↓
plugin runtime fingerprints / BuildPlan
  ↓
RouteCommands / observation / evidence binding
  ↓
Provider Plan JSON
```

このうち、すべてがA / Bで同一ではありません。

### A/Bでtreeが同一の主要領域

```text
internal/deployment
  e398c3723b638eb033a4b3bb96a9964377734805

internal/environment
  e5b85c854f439566aaa12b4653d57cde599567aa

internal/releaseplan
  69c2dee2f92056b3520a23c959218dbfbd4d4919

internal/core
  70a7f2219dcfeaff4cc0a7b1b324e656d8e6915a
```

したがって、durable deployment state machine、environment provider定義、release plan compilation実装そのものには、このA/B間でsource driftを観測していません。

### A/Bで変化している主要領域

```text
internal/workspace
  A: ff5bffdebeb421d1389094065bec8735e73ff93a
  B: a841df70c1e305c9317a8dd5098c5c8f7e8e800d

internal/validation
  A: cfa39e042d3bd632bde87f8d8c07f603bb470fa0
  B: a6d6e53566c9c6c6c5c727d7b090b5de1039c95a

internal/ir
  A: 1a5926d767b5d71287b356c1e431d8edc7557dbe
  B: e9eaec0ec032ba2944e691fdbc40ef8338af7999

internal/plugin
  A: b57adc3a51bf6a84d513c1602e6b0fac7ad9590d
  B: f24e8556d3efcb25c893670ba5b047d4bf4e064b
```

`workspace`では`loader.go`自体も変化しています。

```text
internal/workspace/loader.go
  A blob: 3e37f9ed25205660f8ad9c16106cfe6c1455c61d
  B blob: 948c3558b0f8ed8dd48d4a108ab2da6bffb379b0
```

Bにはcontract-query系などの新しいloader surfaceが追加されています。`validation`にも新しい検査が増え、中心の`validation.go`も変化しています。

```text
internal/validation/validation.go
  A blob: 271cb517d0fdc3be1d940e8c75e79425469ca26f
  B blob: 093cf00eb22eff60c0ba8bcd349b3c92dbbed909
```

一方で、deployment固有のvalidation fileはA / Bで同じblobです。

```text
internal/validation/deployment.go
  A/B blob: 013b139ee8d6432ba28f64bfc7ca268392cc06e5
```

plugin側はtop-level modelに`contract-query-executor` capability kindが追加されていますが、既存field構造、lock / resolve実装、`internal/plugin/runtime` subtreeは同一です。

```text
internal/plugin/model.go
  A: fe1f1deaa75f2fe322f9df4bd4745b77674e1590
  B: cb715c881b3c487cd8ad6a091a141ac62405dec4

internal/plugin/runtime
  A/B tree: e306aab50112c28d656303e6cb1a192c8a16f9ef
```

したがって、現時点の静的Evidenceは次のように読むのが妥当です。

```text
Provider Plan output surface
  = strong static continuity observed

Provider Plan core deployment / environment / releaseplan logic
  = exact source-tree continuity observed

workspace / validation / IR input interpretation
  = changed; actual fixed-input execution required

plugin runtime implementation
  = exact subtree continuity observed

plugin model accepted capability set
  = extended; actual fixed-input compatibility still required
```

これは重要な停止線です。**top-level JSON surfaceが同じことから、fixed reference inputがrevision Bでも必ず同じ経路を通って成功すると推定しません。**

## 5. current SOZA Adapterとの静的な整合

current SOZA `runtime/go/teiintegration/tei_cli.go`のblob SHAは次です。

```text
62025ae7eeae388d29e9602957b6f3833251e671
```

Adapter-local DTOは、TEI Provider Planのtop-levelを次の4 fieldとしてstrictにdecodeします。

```go
type providerPlan struct {
    Executors     []json.RawMessage `json:"executors,omitempty"`
    Observations  []providerRoute   `json:"observations,omitempty"`
    Evidence      []providerRoute   `json:"evidence,omitempty"`
    PluginRuntime json.RawMessage   `json:"pluginRuntime,omitempty"`
}
```

decoderは`DisallowUnknownFields()`を使うため、未知のtop-level fieldが追加されれば互換性failureとして停止します。一方、`executors`と`pluginRuntime`の内部は`json.RawMessage`として保持し、SOZA Universal ContractへTEI固有fieldを複製しません。

`observations` / `evidence`についてSOZAが直接解釈するProvider固有fieldは`kind`、`provider`、任意の`actionId`です。正常なProvider Planを受理した後、current Capability Observationへmappingする観測値は次の2点に限定されています。

```text
availability = true
provider_plan_resolved = true
```

したがって、今回確認したA / Bの**出力surface**はcurrent Adapter-local DTOと静的には整合しています。ただし、Bがfixed reference inputを受理してそのsurfaceへ実際に到達できるかは別のactual確認対象です。

## 6. 今回確認できたこと

```text
revision A → B
  1748 commits ahead

cmd/tei/main.go
  = exact same Git blob

internal/deployment
  = exact same Git tree

internal/environment
  = exact same Git tree

internal/releaseplan
  = exact same Git tree

plugin runtime
  = exact same Git tree

workspace / validation / IR
  = changed

current SOZA Adapter top-level DTO
  = executors / observations / evidence / pluginRuntime
```

このため、1748 commitsの差があるにもかかわらず、今回のfixed `deployment-provider-plan` invocationについて、**既知のProvider Plan出力surfaceとdeployment中核実装に大きな静的連続性がある**ことを確認できました。

同時に、workspace / validation / IRの入力解釈経路には差分が残るため、actual B実行が必要な理由もより明確になりました。

## 7. このEvidenceから言えないこと

次は未検証のままです。

- revision Bがactualにbuildできること
- revision B executable bytesとそのSHA-256
- fixed reference workspaceをrevision Bの`workspace.Load`が受理すること
- fixed reference worldがrevision Bの`validation.Validate`を通ること
- fixed reference durable run / plugin lockがBでも整合すること
- fixed reference inputで`deployment-provider-plan` processが成功すること
- revision Bが実際に出力するProvider Plan JSONとそのSHA-256
- routeやplugin runtimeに入るactual値の互換性
- current SOZA Adapterによるrevision B processのlive strict decode
- current Capability Observation validatorまでのend-to-end成立

したがって、停止線は次です。

```text
same Provider Plan output surface
  != same input interpretation
  != same repository revision
  != same executable bytes
  != revision B build PASS
  != revision B Provider Plan execution PASS
  != current SOZA Adapter live compatibility PASS
  != ISSUE-000072 Resolved
```

## 8. 次のactual検証

actual実行可能なLinux / amd64環境が利用できたら、次を行います。

1. 固定revision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`からactual `cmd/tei`をbuildまたは固定artifactとして取得する。
2. actual binary SHA-256を記録する。
3. revision Aと同じfixed reference workspace / durable run / plugin lockを使用する。
4. Bのworkspace load / validation / durable run checkを含む同じ`deployment-provider-plan` invocationをactualに実行する。
5. actual Provider Plan SHA-256とProvider固有outputを記録する。
6. 取得したbundleを`verify_tei_evidence_bundle.py`で取得経路から独立して再検証する。
7. current `runtime/go/teiintegration`からactual B executableを別OS processとして起動し、strict decodeとCapability Observation mappingを確認する。
8. revision A Evidenceを変更せず、A / Bのsource / binary / output / acquisition Provenanceを別々に保持する。

このactual検証までは、新しいStable RequirementやUniversal TEI fieldを追加しません。

## 9. fixed invocationのfilesystem input / cwd境界

actual handoffのE2 runnerはB executableを`cwd=revision B source checkout`で起動します。このcwdが、明示したA fixed reference inputとは別の暗黙runtime inputになっていないかをexact revision B sourceで追加監査しました。

確認したsource:

```text
cmd/tei/main.go
  blob: 6a27b98b7f6dbe4e66d1261edfc847402cd608a5

internal/workspace/loader.go
  B blob: 948c3558b0f8ed8dd48d4a108ab2da6bffb379b0

go.mod
  blob: f8763f8fb2d64d73f1b40b905f62b5e09c44493b
```

revision Bの`cmd/tei/main.go`はstandard library以外のrepository-local packageを`tei/internal/...`からのみimportします。`go.mod`は`module tei` / `go 1.23.2`と`github.com/lib/pq` requirementだけで、local `replace`はありません。したがって、`cmd/tei` buildについて別のtop-level local module/treeが暗黙に参加するsource構成は観測していません。

`deployment-provider-plan` caseでは、Provider Plan生成までに使う外部pathはflagから渡された値です。

```text
-workspace
  → loadWorld(..., workspacePath)
  → workspace.Load(workspacePath)

-run
  → loadCheckedDeploymentRun(..., runPath, ...)
  → decodeJSONFile(runPath)

-plugin-lock
  → runtimeFingerprintsForEnvironment(..., pluginLockPath, ...)
  → decodeJSONFile(pluginLockPath)

-solution / -version
  → loaded World内のSolution Release selection
```

case本体、`loadWorld()`、`loadCheckedDeploymentRun()`、`runtimeFingerprintsForEnvironment()`の追跡範囲では、current working directoryから固定relative pathを組み立てる処理は観測していません。

`workspace.Load(root)`もmanifestと各source rootを、渡された`root`を基準に`filepath.Join(root, ...)`して読み込みます。Query authoringからnative SQL fileを参照できる経路についても、`resolveNativeSQLFile()`は次を検査します。

- absolute pathを拒否する。
- declarationからの論理relative pathがWorkspace外へescapeする場合は拒否する。
- `filepath.EvalSymlinks`後のreal pathでもWorkspace外へ出る場合は拒否する。
- `.sql`のregular fileだけを許可する。

したがって、**今回追跡したfixed `deployment-provider-plan`経路では、revision B source checkoutのcwdをA fixed reference inputとは別のfilesystem inputとして読むsource pathは静的に確認されませんでした。**

これは「cwdがどこでもactual結果は必ず同じ」というruntime証明ではありません。current E2はhistorical comparison条件を保つため引き続きB source checkoutをcwdとして使います。また、workspace / validation / IR自体はA/Bで変化しているため、exact A inputをBがactualに受理することは依然として実行確認が必要です。

```text
explicit fixed-input path flow observed
  + no repository-cwd filesystem read found on traced source path
  != cwd-independence proven for arbitrary TEI command
  != revision B build PASS
  != revision B Provider Plan execution PASS
  != current SOZA Adapter live compatibility PASS
  != ISSUE-000072 Resolved
```
