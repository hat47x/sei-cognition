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

この同一性は、A / Bで当該型のsource bytesが同一であることを示します。ただし、workspace、durable run、plugin lock、environment等の入力から生成される**実際の値**まで同一であることは意味しません。

## 4. current SOZA Adapterとの静的な整合

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

したがって、今回確認したA / Bのsource surfaceはcurrent Adapter-local DTOと静的には整合しています。

## 5. 今回確認できたこと

```text
revision A → B
  1748 commits ahead

cmd/tei/main.go
  = exact same Git blob

routing executor source
  = exact same Git blob

plugin runtime model source
  = exact same Git blob

current SOZA Adapter top-level DTO
  = executors / observations / evidence / pluginRuntime
```

このため、1748 commitsの差があるにもかかわらず、今回のfixed `deployment-provider-plan` invocationについて、**既知のtop-level Provider Plan source surfaceがA→Bで漂流している兆候は静的には見つかりませんでした**。

これはactual B実行前のriskを絞るEvidenceとして利用できます。

## 6. このEvidenceから言えないこと

次は未検証のままです。

- revision Bがactualにbuildできること
- revision B executable bytesとそのSHA-256
- fixed reference inputで`deployment-provider-plan` processが成功すること
- revision Bが実際に出力するProvider Plan JSONとそのSHA-256
- workspace / durable run / plugin lock / environment処理のruntime互換性
- routeやplugin runtimeに入るactual値の互換性
- current SOZA Adapterによるrevision B processのlive strict decode
- current Capability Observation validatorまでのend-to-end成立

したがって、停止線は次です。

```text
same Provider Plan source surface
  != same repository revision
  != same executable bytes
  != revision B build PASS
  != revision B Provider Plan execution PASS
  != current SOZA Adapter live compatibility PASS
  != ISSUE-000072 Resolved
```

## 7. 次のactual検証

actual実行可能なLinux / amd64環境が利用できたら、次を行います。

1. 固定revision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`からactual `cmd/tei`をbuildまたは固定artifactとして取得する。
2. actual binary SHA-256を記録する。
3. revision Aと同じfixed reference invocationで`deployment-provider-plan`を実行する。
4. actual Provider Plan SHA-256とProvider固有outputを記録する。
5. 取得したbundleを`verify_tei_evidence_bundle.py`で取得経路から独立して再検証する。
6. current `runtime/go/teiintegration`からactual B executableを別OS processとして起動し、strict decodeとCapability Observation mappingを確認する。
7. revision A Evidenceを変更せず、A / Bのsource / binary / output / acquisition Provenanceを別々に保持する。

このactual検証までは、新しいStable RequirementやUniversal TEI fieldを追加しません。
