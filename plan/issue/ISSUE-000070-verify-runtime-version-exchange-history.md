# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

同じCognitive Method、同じKJ Atlas source、同じMethod input、同じactual model artifactを使い、Ollama runtime versionだけを交換したときに、SOZAが先行Method Applicationの履歴を失わず保持できるかを実証する。

runtime version差は別のlogical Method Realizationへ分けない。同じ実現機構に属するhistorical revisionとして扱い、Cognitive Method Contractが既に持つExact Bindingで区別する。

```text
same Method Definition
same logical Method Realization
same KJ Atlas source
same Method input
same pinned model artifact
same model prompt

Ollama 0.32.13
  = Exact Realization revision A

Ollama 0.32.14
  = Exact Realization revision B
```

中心命題は次である。

```text
runtime version交換
  → new exact Realization revision
  != old historical Application rewritten
```

## Product / Contract boundary

この実証は、model名やruntime versionをUniversal Semantic Contractへ追加するためのものではない。

既存境界を維持する。

- Method Definitionは「何を行うMethodか」を表す。
- Method Realizationは「どの実現機構で実行するか」を表す。
- 同じ実現機構のversion差は、同じlogical Realizationに属するhistorical revisionとしてExact Bindingで固定できる。
- Method Applicationは、実行時に利用したRealization revisionをExact Referenceで保持できる。
- runtime / model固有情報は、必要なProvenance / realization-local metadataとして保持する。
- Method outputをRecommendation / Decisionへ自動昇格しない。
- GitHub Actions、runner ID、workflow run IDはCognitive Methodの意味やruntime交換成立条件にしない。

## ISSUE-000067 / ISSUE-000068との接続

ISSUE-000067では、Method Definition / Realization / Applicationを履歴として再構成する境界を検証した。

```text
実現機構が異なる
  → logical Realizationを分ける

同じRealizationのhistorical revisionを固定する
  → Exact Bindingを使う
```

ISSUE-000068では、KJ Atlas source、runtime、Method inputを固定し、actual model artifactだけを交換した。後続model実行を追加しても先行ApplicationのRealization、Provenance、outputを保持できることをScoped Executable Evidenceとして確認した。

本Issueでは交換軸をさらに狭める。

```text
ISSUE-000068
  model artifactを交換
  runtimeは固定

ISSUE-000070
  model artifactを固定
  runtime versionだけを交換
```

model交換とruntime revision交換を別の探索軸として扱う。

## Fixed conditions

次を固定する。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- KJ Atlas endpoint: `POST /ai/suggest-card-groups`
- model adapter: `runtime/integration/e3b_m1b_ollama_adapter.py`
- model: `qwen2.5:0.5b`
- model artifact digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- Method input: repository-local harness内の固定3-card input
- held card: `c-held`
- SOZA Method mapping: current `livemethodintegration`

model artifact digestは、Actual Model Artifact Exchange E3b Run `33670697154`でOllama `0.32.14`から実際に観測した`qwen2.5:0.5b`のartifact identityである。

A / Bのdigestが一つの実行内で互いに等しいだけでは固定条件成立とみなさない。両方がこの期待digestに一致することを要求する。同じmodel tagが将来別artifactを指した場合は、実験条件が変わったものとして停止する。

交換するのはOllama runtime versionだけとする。

- revision A: `0.32.13`
- revision B: `0.32.14`

## Pinned runtime artifacts

installerによるglobal installは使わず、GitHub ReleaseのLinux amd64 archiveを固定SHA-256で取得し、別々の一時directoryへ展開してbinaryを直接起動する。

- `v0.32.13 / ollama-linux-amd64.tar.zst`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- `v0.32.14 / ollama-linux-amd64.tar.zst`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

2026-09-03の静的再監査では、両digestがOllama公式GitHub Release metadataの各asset digestと一致することを確認した。また、公式Linux installerの展開方式と`${root}/bin/ollama`というlayout前提が整合することを確認した。

これはsource identityの静的確認であり、runtime交換をactualに実行したExecutable Evidenceではない。

## Exact Realization Reference

既存のKJ Atlas live mappingへ、後方互換なoptional経路として`ApplyGroupingInput.RealizationReference`を追加した。

- 未指定の場合
  - 従来どおりlogical-only Realization Referenceを保持する。
- 指定した場合
  - `method_application.realization_ref`へ`semanticruntime.Reference`を保持する。
  - logical identityが`RealizationRef`と一致しなければ、canonical stateを変更せず拒否する。

Exact Bindingを作るMethod Realization payloadと、portable Semantic Interchangeへ格納するRealization recordは同じ生成経路を使う。

このmappingでは、Exact Referenceを保持するためMethod Application recordを直接`CanonicalStore.Add`へ渡す。これはsemantic validationの迂回ではない。`CanonicalStore.Add`はtyped recordを`semanticruntime.LoadStandalone`で再検証してから保存するため、従来の`MachineSurface.RecordMethodApplication`と同じContract検証境界を通る。

共有mapping自体はActual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`で`go test ./livemethodintegration -count=1`を含めactualにPASSしている。したがってExact Reference mappingにはExecutable Evidenceがあるが、この既存Evidenceをruntime version交換の成立証明には使わない。

## Repository-local execution harness

PR #70ではGitHub Actions workflowをcurrent `develop/v0.2.0`から撤去した。そこで、runtime交換のactual実行本文をautomation providerから切り離し、repository同梱の次のharnessへ移す。

- `runtime/integration/run_runtime_version_exchange.sh`

harnessは次を一続きに実行する。

1. KJ Atlas checkoutが固定commitであることを確認する。
2. 専用Python virtual environmentへ固定KJ Atlas backendを導入する。
3. Ollama `0.32.13` / `0.32.14`のarchiveを取得し、固定SHA-256を検証する。
4. 同じmodel storageで`qwen2.5:0.5b`を利用し、A / B双方のmodel digestが固定値と一致することを確認する。
5. 同じ3-card Method inputをA / Bへ通し、actual inference countersとKJ Atlas responseを確認する。
6. A / Bのprompt SHA-256が同一であることを確認する。
7. `livemethodintegration`の通常testを実行する。
8. runtime交換live testを実行し、historical Applicationとportable reconstructionを検査する。
9. 成否にかかわらず、そこまで生成されたEvidenceを通常directoryへ保存する。

実行場所は意味上の条件にしない。

```text
repository-local harness
  = reproducible execution boundary
  != GitHub Actions required
  != specific runner required
```

旧workflowで実装していたactual実験本文を、GitHub Actionsの存在と分離して保持することが目的である。

## Artifact guard

runtime交換のlive testを開始する前に、Go側でも実際の実験条件を再確認する。

`runtime_version_artifact_guard_test.go`は、`SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1`のときだけ次を検査する。

- 指定されたKJ Atlas checkoutのactual commitが固定commitと一致する。
- runtime A / Bのversion logが、それぞれ`0.32.13` / `0.32.14`を示す。
- 取得済みruntime archive bytesのSHA-256が固定値と一致する。

KJ Atlas path、runtime archive、version logはrepository-local harnessから明示できる。`GITHUB_WORKSPACE`はhistoricalな互換fallbackとしてのみ扱い、必須条件にしない。

通常のunit testではexternal runtimeを要求しない。

`runtime_version_artifact_guard_unit_test.go`では、PR #71で次を固定した。

- exact version tokenを受理する。
- `0.32.13`と`0.32.130`のようなnumeric suffixを取り違えない。
- exact artifact digestを受理する。
- artifact digest mismatchを拒否する。
- Realization payload bytesが宣言したRaw Bytes SHA-256 Exact Bindingで`verified`になる。
- payloadを改変すると`verification_failed`になる。
- 同一のRealization identityから同じExact Bindingを決定的に再構成できる。
- runtime version、runtime artifact digest、model artifact digestのいずれかを変えるとExact Bindingも変わる。

これにより、次を別々に検査する。

```text
actual execution identity guard
  != payload digest verification
  != bundle-local Exact Reference resolution
```

## Required experiments

### E1 — runtime artifact identity

両runtime archiveを固定URLから取得し、固定SHA-256を検証する。

PASS条件:

- Aが`0.32.13`として起動する。
- Bが`0.32.14`として起動する。
- archive digestが固定値と一致する。

### E2 — same pinned model artifact

両runtimeで`qwen2.5:0.5b`を利用し、APIが返すmodel digestを確認する。

PASS条件:

- A / Bのmodel digestが同一である。
- A / Bのmodel digestが固定した期待artifact identityと一致する。
- model tagだけで同一性を推論しない。

### E3 — same prompt / actual inference

同じMethod inputをKJ Atlasとmodel adapterへ通す。

PASS条件:

- A / Bのmodel evidenceに同じprompt SHA-256が記録される。
- `ollama_done = true`である。
- `prompt_eval_count > 0`である。
- `eval_count > 0`である。
- KJ Atlas response boundaryが両responseを受理する。

生成文そのものの一致はPASS条件にしない。

### E4 — same logical Realization / different Exact Binding

runtime version、runtime artifact digest、model artifact identityを含むMethod Realization documentからExact Bindingを決定的に作る。

PASS条件:

- A / Bは同じlogical Realizationを持つ。
- A / BはいずれもExact Bindingである。
- A / BのExact Bindingは異なる。
- 同じidentityから再構成したExact Bindingは同じになる。
- execution artifact identityを変えた場合はExact Bindingも変わる。

### E5 — historical Application immutability

runtime Aの結果をSOZAへ記録し、その後runtime Bの結果を追加する。

PASS条件:

- Application AのExact Realization Referenceが変わらない。
- Application AのProvenanceが変わらない。
- Application Aのoutputが変わらない。
- Application Bはrevision BのExact Referenceを保持する。
- 両Applicationは同じMethod Definitionを指す。
- 両Provenanceは同じ固定model artifactを指す。
- 各Provenanceから対応するruntime versionを読み直せる。

### E6 — portable historical reconstruction

二つのMethod Realization revision recordと二つのApplication recordを一つのSemantic Interchangeへ格納する。

PASS条件:

- Realization payloadをRaw Bytes SHA-256 Profileで検証できる。
- `semanticruntime.LoadInterchange`がbundle-local Exact Binding検証を通過する。
- Application AのExact Referenceをrevision Aへ解決できる。
- Application BのExact Referenceをrevision Bへ解決できる。
- payload改変はVerifierで拒否される。
- 存在しないrevision digestを参照するnegative bundleは`LoadInterchange`で拒否される。

```text
exact-looking reference retained
  != payload verified
  != historical revision resolvable

payload verification
  + matching Realization revision record
  + Application exact reference
  + bundle-local Exact Binding validation
  → portable historical reconstruction boundary
```

### E7 — no semantic promotion

runtime交換後もMethod outputをRecommendation / Decisionへ自動昇格しない。

### E8 — execution surface independence

runtime交換実験をGitHub Actions workflowに閉じ込めず、repository-local harnessから再現できる状態を保つ。

PASS条件:

- fixed experiment identityがscript内に明示されている。
- actual inferenceに必要な処理がrepository同梱資産として残る。
- harnessからlive Go testへ必要なKJ Atlas path、runtime log、archive path、model identityを渡せる。
- GitHub Actionsやrunner IDをMethod / Realization identityへ含めない。

### E9 — Evidence preservation

actual runtime交換の入力、実行条件、結果を一時ログだけに閉じない。

Evidence directoryへ、存在する範囲で次を保存する。

- experiment identity
  - execution ID
  - SOZA repository commit
  - KJ Atlas source commit
  - runtime A / B version / archive SHA-256
  - expected model digest
  - `qualityJudgement = not_evaluated`
- Method request
- A / B runtime version log
- A / B model digest / tags
- A / B inference Evidence
- A / B KJ Atlas result
- Adapter / KJ Atlas / Ollama log

途中で停止した場合も、そこまで生成されたEvidenceを残す。

```text
Evidence directory preserved
  != runtime exchange PASS
  != output quality satisfied
```

## Existing Evidence

### Exact Reference mapping / fixed model artifact source

Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`はrunner上でactualに完走した。

このrunでは、actual model artifact exchange、full model digest、prompt digest、`go test ./livemethodintegration -count=1`、historical Application保持を確認した。

したがって、Exact Reference mappingにはExecutable Evidenceがある。また、今回固定する`qwen2.5:0.5b`のmodel artifact identityはactual observationに基づく。

これはruntime version交換のExecutable Evidenceではない。

### Historical GitHub Actions exploration

PR #63の作業中には、runtime交換workflow、scenario-local trigger、shared dependency trigger、Evidence artifact保存を試作した。

一方、GitHub-hosted runnerは長期間`runner_id=0 / steps=[]`のまま割り当て前に終了した。PR #68の最小cross-OS probeではUbuntu / Windows / macOSのすべてで同じ現象を観測した。

この観測は、Linux固有、Ollama固有、SOZA test本文固有の説明を弱めるが、billing、quota、repository policy、GitHub service-side condition等の具体原因を確定しない。

PR #70ではcurrent `develop/v0.2.0`からGitHub Actions workflowを撤去した。ISSUE-000069も、検証内容と実行場所を分ける境界が確立したものとしてResolvedになった。したがって、runner復旧は本IssueのResolution条件ではない。過去のrun / trigger観測はhistoryとして保持するが、current actual実証はrepository-local harnessを正とする。

## Current implementation state

current implementationには次がある。

- Exact Realization Referenceを保持できるKJ Atlas mapping
- logical identity不一致時の無変更失敗test
- fixed runtime / model identity
- runtime execution identity guard
- artifact guard unit tests
- Realization payload Exact Binding verification
- Exact Binding決定性とidentity差分test
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- unknown revision digestのnegative control
- repository-local runtime exchange harness
- failure途中も保存できるfilesystem Evidence directory

ただし、repository-local harnessによるactual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していない。

## Current Evidence state

```text
fixed runtime artifact identity against official release metadata
  = statically verified

qwen2.5:0.5b expected model artifact identity
  = actual digest observed in Run 33670697154

Exact Realization Reference mapping
  = Executable Evidence available in Run 33670697154

pure-Go Exact Binding controls
  = implemented in current develop via PR #71

repository-local runtime exchange harness
  = implemented; shell syntax checked on the source branch

runtime artifact / source / version live guard
  = implemented

actual runtime 0.32.13 / 0.32.14 acquisition through current harness
  = Not Yet Verified

actual runtime-version exchange inference through current harness
  = Not Yet Verified

same pinned model digest / same prompt digest across runtime versions
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

ISSUE-000071は評価境界の確立としてResolvedになったが、これはhuman reviewやKJ-method outcome qualityがSatisfiedになったことを意味しない。本Issueでもruntime交換のexecution conformanceと成果品質を混同しない。

## Requirement / Contract assessment

現時点では新しいStable Requirement / Acceptance Scenario / Universal Contract fieldを追加しない。

actual実証後に次へ再照合する。

- REQ-0001
- REQ-0004
- REQ-0021
- SCN-0005
- SCN-0015

既存Requirement / Contractで観測結果を十分に表せる場合はNo Changeとする。

## Resolution

次をすべて満たした時点でResolvedにできる。

1. repository-local harnessが固定runtime artifact A / Bを取得し、digestを検証できる。
2. A / Bのactual binary versionを確認できる。
3. A / B双方のmodel digestが固定artifact identityと一致し、same prompt digestもactual executionで確認できる。
4. 両runtimeでactual inferenceが成立する。
5. Application A / Bがsame logical / different Exact Realization revisionを保持する。
6. Application AのReference / Provenance / outputがB追加後も不変である。
7. Realization payload verification、portable reconstruction、unknown revision negative controlがPASSする。
8. Recommendation / Decisionへの自動昇格がない。
9. filesystem Evidence directoryから実験identity、入力、A / B出力、model Evidenceへ戻れる。
10. Requirement / Contract再照合と自然な日本語最終監査を行う。

GitHub-hosted runnerの復旧やGitHub Actions workflowの再導入はResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revisionを交換するとhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- Realization payloadと宣言Exact Bindingの不一致を検出できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを参照するbundleを受理する。
- model tagが固定artifact identityと異なるartifactを指し、model artifactが交換軸へ混入する。
- promptが交換軸へ混入する。
- runtime固有情報をUniversal semanticsへ先取りする。
- actual実験本文が特定automation providerにしか存在せず、repositoryから再実行できなくなる。
- runtime交換successをmodel / KJ成果品質やE4へ過大評価する。

## Stop line

runtime交換がPASSしても、次を意味しない。

```text
runtime 0.32.13 / 0.32.14 exchange PASS
  != arbitrary runtime version portability
  != other runtime implementation portability
  != model output quality satisfied
  != language suitability satisfied
  != KJ-method outcome quality satisfied
  != Recommendation correctness
  != Decision correctness
  != E4 Operational portability
```

execution成立、historical reconstruction、生成品質を別の評価軸として扱う。

## Natural Japanese review

ISSUE-000067 / ISSUE-000068、Cognitive Method Contract、Exact Binding、current KJ Atlas mapping、PR #70以降のno-Actions baseline、PR #71のExact Binding補強、ISSUE-000071で確立した成果品質評価境界を再照合した。

旧本文ではdedicated workflow、Actions artifact、runner復旧がcurrent実験手段として混在していた。これらをhistorical explorationへ移し、actual実験本文はrepository-local harnessへ戻した。これにより、GitHub Actionsを使わないことと、actual runtime交換を未実証のまま残すことを両立させている。

また、Exact Referenceを保持するためKJ Atlas mappingが`CanonicalStore.Add`へ直接recordを渡す点も再監査した。`CanonicalStore.Add`はtyped semantic documentを`semanticruntime.LoadStandalone`で再検証するため、MachineSurfaceを経由しないことをsemantic validationの回避とは扱わない。

実行artifactの固定、payload digest検証、bundle-local reference解決、Evidence保存を別の責務として記述し、一つのPASSへ圧縮していない。意味、規範強度、Evidence強度、未検証範囲を変えず、自然な日本語として読み通せることを最重要視して全文を再ドラフトした。
