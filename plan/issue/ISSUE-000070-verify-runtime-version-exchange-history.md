# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

ISSUE-000067 / ISSUE-000068で確認したhistorical reconstruction境界が、**model artifactを固定したruntime version交換**でも機能するかを検証する。

KJ Atlasのsource revision、Method surface、Method input、model artifactを同一に保ち、Ollama runtimeだけを`0.32.13`から`0.32.14`へ交換する。その上で、後続Applicationを追加しても、先行Applicationが参照するRealization revision、Provenance、outputが書き換わらないことを確認する。

今回の重要な前提は、`0.32.13`と`0.32.14`を別々のlogical Method Realizationとして扱わないことである。両者は同じKJ Atlas + Ollama実現機構のversion差なので、**同じlogical Realizationに属する異なるExact revision**として扱う。

```text
same Method Definition
same logical Method Realization
same KJ Atlas source
same Method input
same model artifact
same model prompt

Exact Realization revision A
  = Ollama 0.32.13
  → Application A

Exact Realization revision B
  = Ollama 0.32.14
  → Application B

Application B added
  != Application A rebound to revision B
  != Provenance A rewritten
  != output A rewritten
```

## Background

ISSUE-000066では、Ollama `0.32.14`上の`qwen2.5:0.5b`を用い、actual inferenceからKJ Atlas response受理、SOZA Cognitive Method Applicationへのmappingまでを確認した。

ISSUE-000067ではhistorical reconstructionの最小境界を調べ、次を確認した。

- 実現機構そのものが異なる場合はlogical Realizationを分けられる。
- 同じRealizationのhistorical revisionを固定する必要がある場合はExact Bindingを使える。
- model / runtime等の具体的な実行条件は、必要な範囲でProvenanceへ残せる。

M1aのdeterministic model stubとM1bのactual model-backed executionは実現機構が異なるため、別logical Realizationとして整理した。一方、今回比較するOllama `0.32.13`と`0.32.14`は同一実現機構のversion差である。このため、A/Bを別logical Realizationへ分けるだけでは、ISSUE-000067のH1で確認したExact Binding境界をactual integrationへ接続したことにならない。

ISSUE-000068では、Ollama `0.32.14`を固定したまま`qwen2.5:0.5b`と`qwen2.5:1.5b`のactual model artifactを交換し、historical Applicationを保持できることを実証した。ただしruntime version自体は固定していた。

本Issueでは、model artifactを固定したままruntime revisionだけを交換し、同じlogical Realizationの異なるExact revisionをApplicationへ固定できるかを確認する。

## 比較対象とruntime取得境界

比較対象は、Ollamaの次の二つのstable releaseとする。

- `0.32.13`
- `0.32.14`

runtimeはinstallerを実行してglobal installするのではなく、各GitHub ReleaseのLinux amd64 artifactを固定SHA-256で取得し、それぞれ別の一時ディレクトリへ展開する。

- `0.32.13 / ollama-linux-amd64.tar.zst`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- `0.32.14 / ollama-linux-amd64.tar.zst`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

この方式により、global install、systemd service設定、既存binaryの上書き等を実験条件から外し、固定したruntime artifactそのものを比較する。

model artifactは`qwen2.5:0.5b`へ固定する。二つのruntimeは同じmodel storageを参照し、model tagだけでなく、各runtimeから観測したmodel digestが一致することを確認する。

## Exact Realization revisionの作り方

Cognitive Method Contractは、過去Applicationの再構成に特定版Realizationが重要な場合、`realization_ref`へExact Bindingを利用できるとしている。

今回のprobeでは、次の実装情報を参照するMethod Realization documentをruntimeごとに構成し、そのdocumentのraw-bytes SHA-256をRealization revisionのExact Bindingとして用いる。

- 固定KJ Atlas source / entry point
- 固定model name / model ID
- 対象Ollama runtime version
- 対象Ollama release artifact SHA-256

A/BのMethod Realizationは同じLogical Referenceを持つが、runtime versionとruntime artifactが異なるためExact Bindingは異なる。

```text
Logical Realization identity
  = MR-KJ-ATLAS-RUNTIME-EXCHANGE

revision A exact binding
  != revision B exact binding
```

modelやruntimeをUniversal Contractの固定fieldへ追加するものではない。version固有情報はimplementation metadataとprobe-local Provenanceへ残し、Applicationは既存`realization_ref`のExact Referenceを使う。

## Questions

1. 同じmodel artifactを使い、Ollama runtime versionだけを交換しても、KJ Atlasの既存Method surfaceをactual inferenceまで実行できるか。
2. 二つのruntimeで観測されるmodel digestとprompt digestを同一に保てるか。
3. 同じlogical Realizationの二つのruntime revisionを、異なるExact BindingとしてApplicationへ保持できるか。
4. runtime BのApplication追加後も、runtime AのApplicationが持つExact Realization Reference、Provenance、outputを変更せず保持できるか。
5. current `ExecutionIdentity.RuntimeVersion`とopaque Provenanceから、各Applicationの実行条件を読み直せるか。
6. runtime version交換のためにUniversal Cognitive Method Contractへ新しいfieldを追加する必要があるか。
7. 実証結果から新しいStable Requirement / Scenarioが本当に必要になるか。

## Constraints

- KJ Atlas repository / commitを二実行で同一にする。
- `POST /ai/suggest-card-groups`のMethod surfaceを同一にする。
- Method inputを同一にする。
- modelは`qwen2.5:0.5b`へ固定する。
- model digestの一致を実測する。
- modelへ渡されたprompt digestの一致を実測する。
- actual inference countersを両runtimeで確認する。
- runtime binaryはrelease artifact digestで固定する。
- A/BのRealization Logical Referenceを同一にする。
- A/BのRealization Exact Bindingが異なることを確認する。
- runtime version以外の差を可能な限り増やさない。
- runtime名やversionをUniversal Contractの固定fieldへ新たに追加しない。
- responseが構造上受理できても、model出力品質、言語適合性、KJ法としての成果品質をPASS扱いしない。
- runtime version交換のPASSをarbitrary runtime portabilityやE4 Operational portabilityへ昇格させない。
- v0.2.0 supported scopeを遡及的に拡張しない。

## Required scenarios / experiments

### R1 — runtime Aでactual inferenceを実行する

固定SHA-256で検証したOllama `0.32.13` artifactを専用ディレクトリから直接起動し、`qwen2.5:0.5b`を実行する。

次を記録する。

- runtime version
- runtime artifact digest
- model name
- model digest
- prompt SHA-256
- prompt evaluation count
- evaluation count
- KJ Atlas response

PASS条件:

- 起動binaryが`0.32.13`として観測できる。
- actual inference countersが正の値を持つ。
- KJ Atlas responseがcurrent Adapter boundaryを通過する。

### R2 — runtime Bで同じmodel artifactを実行する

固定SHA-256で検証したOllama `0.32.14` artifactへ交換し、同じ`qwen2.5:0.5b`を実行する。

PASS条件:

- 起動binaryが`0.32.14`として観測できる。
- runtime A / Bのmodel digestが一致する。
- runtime A / Bのprompt digestが一致する。
- actual inference countersが正の値を持つ。
- KJ Atlas responseがcurrent Adapter boundaryを通過する。

生成文そのものの一致はPASS条件にしない。

### R3 — Exact Realization revisionとhistorical Applicationを保持する

runtime Aの結果を記録するとき、同じlogical Realizationのrevision AをExact ReferenceとしてApplication Aへ保持する。その後、runtime Bに対応するrevision BをApplication Bへ保持する。

PASS条件:

- A / Bは同じMethod Definitionを指す。
- A / BのRealization Referenceは同じLogical Referenceを持つ。
- A / BのRealization ReferenceはいずれもExact Bindingである。
- A / BのRealization exact content digestは異なる。
- A / BのProvenanceには対応するruntime versionが残る。
- A / Bのmodel IDは一致する。
- B追加後もAのMethod Reference、Exact Realization Reference、Provenance payload、output payloadが変化しない。
- 二つのRealization revision recordと二つのApplicationを同じSemantic Interchangeへ格納し、既存`LoadInterchange`のbundle-local Exact Binding検査を通過する。
- Applicationが存在しないRealization digestを参照するnegative controlは`LoadInterchange`で拒否される。
- Method outputをRecommendation / Decisionへ自動昇格しない。

ISSUE-000067 H1では、同一logical Realizationの複数Exact revisionをportable bundle上で解決できることを確認済みである。本Issueでは、そのExact Referenceをactual KJ Atlas integrationのMethod Applicationへ保持し、対応するRealization revisionとともにportable Semantic Interchangeへ戻せるところまで接続する。

### R4 — Requirement / Contract再監査

R1〜R3の結果を既存REQ / SCNへ照合する。

優先して次を再監査する。

- REQ-0001
- REQ-0004
- REQ-0021
- SCN-0005
- SCN-0015

既存境界で十分なら、新しいStable Requirement / Scenarioは追加しない。

## 実装

runtime交換probeに先立ち、live KJ Atlas mappingへ任意のExact Realization Referenceを保持できる経路を追加した。

- `ApplyGroupingInput.RealizationReference`
  - optional
  - `semanticruntime.Reference`をそのまま受け取る
  - 従来の`RealizationRef`とLogical identityが一致することを確認する
- logical-onlyの既存M1a / M1b経路
  - 変更しない
- Exact Referenceを指定した場合
  - 既存Cognitive Method Contractの`method_application.realization_ref`へそのまま保持する
  - model / runtime固有fieldをContractへ追加しない
- `exact_realization_reference_test.go`
  - Exact Reference保持
  - logical identity不一致時の無変更失敗
- `runtime_version_exchange_test.go`
  - 同じlogical Realizationの二つのExact revisionを生成する
  - A / BのApplicationへ対応するExact Referenceを固定する
  - B追加後のAの不変性を検査する
  - Realization revision recordとApplicationをportable Semantic Interchangeへ戻し、bundle-local Exact Binding整合を再検査する
  - 存在しないrevision digestを参照するnegative bundleが拒否されることを確認する

この変更は、`CanonicalStore`へ同一logical identityの複数Realization recordを格納する機能を追加するものではない。live mappingではApplicationが外部またはportableなRealization revisionをExact Referenceで指せることを確認し、複数revisionの交換・再構成には既存Semantic Interchangeを使う。

## Deliverables

- `.github/workflows/runtime-version-exchange-e3b.yml`
- `runtime/go/livemethodintegration/kj_atlas.go`
- `runtime/go/livemethodintegration/exact_realization_reference_test.go`
- `runtime/go/livemethodintegration/runtime_version_exchange_test.go`
- 本Issue
- 必要に応じた上流計画・Product文書・Evidence文書の更新
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

実証が成立する前に、上流文書へ「runtime version portability成立」と書かない。

## 現在の実行状態

PR #63では専用workflowがGitHubに受理されている。

初期Run `33643122574` / Job `100290947896`、固定runtime artifact方式へ変更後のRun `33666463441` / Job `100369330195`、PR #61最新headへ再基線化した後のRun `33669068265` / Job `100377886730`はいずれも、GitHub-hosted runnerが割り当てられずworkflow step開始前に終了した。

Exact Reference対応とportable reconstruction testを追加したhead `765eb189f97d7dba402cec864960cecb3a5a91a6`では、runner割当が部分的に成立した。`Actual Model Artifact Exchange E3b` Run `33670697154` / Job `100383296117`は全stepを完走し、次を確認した。

- digest固定したOllama `0.32.14`の取得と起動: **success**
- `qwen2.5:0.5b` / `qwen2.5:1.5b`のactual model取得と推論: **success**
- `go test ./livemethodintegration -count=1`: **success**
  - 新規`exact_realization_reference_test.go`を含むため、Exact Reference保持とlogical identity不一致時の無変更失敗をExecutable Evidenceとして確認した。
- 既存`TestLiveKJAtlasActualModelArtifactExchangePreservesHistoricalApplication`: **success**
  - shared mapping拡張後も、既存のactual二モデル交換とhistorical Application保持が回帰していない。

一方、同じheadのruntime交換専用Run `33670697013`はjobが生成されたもののstep開始前に終了した。個別再実行でも`queued`になった後、`steps=[]`のままfailureした。M1aやPlan integrityの個別再実行でも同様の挙動が残っている。

したがって、runnerは全面的に利用不能なのではなく、**同一時点でも割当が成立するjobと成立しないjobが混在する不安定な状態**として観測する。step未開始のfailureをruntime version交換そのもののFAILには数えない。

また、PR #61で実証workflowの起動責務を精密化した後、runtime交換固有testだけを追加したheadではM1a、M1b、actual二モデル交換のrunが生成されなかった。shared mapping自体を変更した現在は、それらが回帰対象として再び選択される。これはtrigger責務の意図どおりである。

現時点のEvidence状態は次のとおりである。

```text
workflow definition accepted by GitHub
  = confirmed

scenario-local workflow selection
  = confirmed at run-generation level

Exact Realization Reference mapping
  = Executable Evidence available in Run 33670697154

existing actual two-model exchange after shared mapping change
  = Scoped Executable Evidence re-confirmed in Run 33670697154

pinned runtime artifact acquisition design for 0.32.13 / 0.32.14
  = defined, not yet executed in the runtime-exchange workflow

portable reconstruction after actual runtime exchange
  = implemented, not yet executed with runtime A/B evidence

actual Ollama 0.32.13 execution
  = Not Yet Verified

actual Ollama 0.32.14 execution in the runtime-exchange workflow
  = Not Yet Verified

same model digest / same prompt digest across runtime versions
  = Not Yet Verified

historical Application preservation after runtime exchange
  = Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

runner割当が成立した時点で、専用runtime交換workflowをactualに完走させてからR1〜R4を判定する。

## Resolution

Open中。

次をすべて満たした時点でResolvedを検討する。

1. `0.32.13` / `0.32.14`の固定runtime artifactをdigest検証して起動できる。
2. 両runtimeで同じmodel artifactによるactual inferenceが成立する。
3. model digestとprompt digestの一致を確認する。
4. 同じlogical Realizationの異なるExact BindingをA / Bへ保持できる。
5. runtime B追加後もruntime AのExact Realization Reference、Provenance、outputが不変である。
6. 二つのRealization revisionとApplicationをportable Semantic Interchangeとして再構成し、Exact Binding整合を確認できる。
7. current Provenanceから各Applicationのruntime versionを読み直せる。
8. logical-only既存M1a / M1b経路が回帰していない。
9. Requirement / Contractの要否を再監査し、必要な変更だけを正本化する。
10. 上流計画と自然な日本語監査台帳を実測Evidenceへ同期する。

GitHub-hosted runnerが利用できずactual workflowを開始できない場合は**Blocked / Not Yet Verified**として残し、設計・workflow定義だけをExecutable Evidenceへ昇格させない。

## Reopen conditions

Resolved後も、次の場合は再開する。

- runtime version交換によって先行Applicationの来歴が書き換わる。
- 同じlogical RealizationのExact revisionをApplicationへ保持できない。
- Exact Referenceを追加した結果、既存logical-only integrationが壊れる。
- portable bundle内でApplicationのExact Realization Referenceを対応revisionへ解決できない。
- model digestが同じでもruntime交換後にhistorical reconstructionに必要な情報が不足する。
- current Provenanceではruntime versionを一意に読み直せない。
- 別のruntime version系列でcurrent境界が成立しない。
- CanonicalStore自体に複数Realization revisionを保持する必要がProduct requirementとして生じる。
- 別runtime implementationや別Providerで追加の意味差が見つかる。

## CI / verification

専用workflowはruntime / Adapter / shared mapping / runtime交換test / workflow自身の意味変更時に自動実行できる構成とし、明示的な再実証用に`workflow_dispatch`も残す。

CI結果は次を分けて記録する。

```text
workflow definition accepted
  != job assigned to a runner
  != Exact Reference mapping tests passed
  != runtime artifact acquired
  != actual runtime exchange executed
  != runtime-version-exchange Scoped Executable Evidence available
```

Exact Reference対応はshared mappingを変更するため、runtime交換専用workflowだけでなく、M1a / M1b / actual二モデル交換の既存回帰も確認対象とする。Run `33670697154`では、package全体とactual二モデル交換についてはsuccessを確認した。M1a / M1bとruntime交換専用workflowは、runner割当が成立したrunで改めて確認する。

## Natural Japanese review

ISSUE-000067 / 000068とCognitive Method Contractを再照合し、旧案にあった「runtime A / Bを別probe-local Realizationとして記録する」という表現を修正した。

M1a / M1bのように実現機構そのものが異なる場合と、Ollama `0.32.13` / `0.32.14`のような同一実現機構のversion差を分けている。後者ではlogical identityを増やさず、既存Exact Bindingでhistorical revisionを固定する。

また、「同じmodel」はmodel tagだけでなくmodel digestで、「同じ入力」はKJ AtlasへのMethod inputだけでなくmodel prompt digestでも確認する。runtimeは固定release artifactのdigestまで検証する。

Exact ReferenceをApplicationへ残すだけではhistorical reconstructionの実証として弱いため、対応する二つのRealization revisionと二つのApplicationをportable Semantic Interchangeへ戻し、既存`LoadInterchange`でbundle-local Exact Bindingを再検証する工程を加えた。存在しないrevision digestを参照するnegative controlも設けている。

生成文そのものの一致は要求しない。runtime version交換によって生成内容が変化した場合でも、それをhistorical reconstructionのFAILと直結させず、execution成立、履歴保持、model / Method品質を別の評価軸として扱う。

GitHub Actionsについては、Run `33670697154`のようにrunner割当が成立して全stepが完走するrunと、同じheadでも`steps=[]`のまま終了するrunが混在している。したがって「runner全面停止」とも「CI全面復旧」とも断定せず、観測できたこと、実装として成立したこと、actualに未検証のことを分けて記述した。

意味、規範強度、Evidence強度を変えず、自然な日本語として読み直した。