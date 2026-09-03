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
- runtime archiveやmodel artifactをどの経路で入手したかは、実行状況を追うためのProvenanceであり、artifact identityそのものではない。
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

installerによるglobal installは使わず、Linux amd64 archiveの実bytesを固定SHA-256で識別し、別々の一時directoryへ展開してbinaryを直接起動する。

- `v0.32.13 / ollama-linux-amd64.tar.zst`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- `v0.32.14 / ollama-linux-amd64.tar.zst`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

2026-09-03の静的再監査では、両digestがOllama公式GitHub Release metadataの各asset digestと一致することを確認した。また、公式Linux installerの展開方式と`${root}/bin/ollama`というlayout前提が整合することを確認した。

これはsource identityの静的確認であり、runtime交換をactualに実行したExecutable Evidenceではない。

current harnessはこの固定artifactに合わせてLinux / amd64だけを受理する。これはSOZA全体のplatform supportをLinux / amd64へ限定する意味ではなく、今回の交換実験に使うartifact条件を実行前に固定するためのprobe-localな制約である。

runtime archiveはharnessがOllama公式GitHub Releaseから取得しても、別経路で事前配置してもよい。ただし、どちらの経路でも実際に利用するarchive bytesのSHA-256を計算し、上記固定値へ一致させる。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual archive bytes + fixed SHA-256

acquisition path
  != artifact identity
```

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

PR #70ではGitHub Actions workflowをcurrent `develop/v0.2.0`から撤去した。そこで、runtime交換のactual実行本文をautomation providerから切り離し、repository同梱の次のharnessへ移した。

- `runtime/integration/run_runtime_version_exchange.sh`

harnessは次を一続きに実行する。

1. Linux / amd64の実行環境であることを確認する。
2. SOZAとKJ Atlasのworking treeがcleanで、KJ Atlas checkoutが固定commitであることを確認する。
3. 専用Python virtual environmentへ固定KJ Atlas backendを導入する。
4. Ollama `0.32.13` / `0.32.14`のarchiveを取得または事前配置pathから参照し、**実測SHA-256を保存したうえで**固定値と照合する。
5. 同じmodel storageで`qwen2.5:0.5b`を利用し、A / B双方のmodel digestが固定値と一致することを確認する。
6. 同じ3-card Method inputをA / Bへ通し、actual inference countersとKJ Atlas responseを確認する。
7. A / Bのprompt SHA-256が同一であることを確認する。
8. `livemethodintegration`の通常testを実行する。
9. runtime交換live testを実行し、historical Applicationとportable reconstructionを検査する。
10. 成否にかかわらず、そこまで生成されたEvidenceをrun専用directoryへ保存する。

実行場所やartifact取得経路は意味上の条件にしない。

```text
repository-local harness
  = reproducible execution boundary
  != GitHub Actions required
  != specific runner required

prepositioned artifact
  = another acquisition path
  != weaker identity verification
```

旧workflowで実装していたactual実験本文を、GitHub Actionsの存在と分離して保持することが目的である。

### artifact acquisition boundary

実験成立に必要なのは、固定したruntime/model artifactそのものであり、実行時に外部ネットワークから取得できることではない。

runtime archiveは次の二経路を許可する。

- harnessがOllama公式GitHub Releaseから取得する。
- `--runtime-a-archive` / `--runtime-b-archive`で事前配置済みarchiveを指定する。

どちらも同じ実測SHA-256検証へ通す。事前配置pathやファイル名だけを根拠に固定artifactとはみなさない。

model storageも次の二経路を許可する。

- harness所有のwork-local model storageを使う。固定model artifactがなければ`ollama pull`し、その後にfull digestを検査する。
- `--model-dir`で既存model storageを指定する。この場合は、固定full digestのmodel artifactが既に存在するときだけ利用し、不足していてもharnessから自動pullしない。

外部model storageを自動更新しないのは、検証対象として渡された事前配置artifactをharness自身が暗黙に変更しないためである。

Evidence identityにはruntime archiveの`archiveAcquisition`とmodelの`storageMode`を残す。これは再実行時に取得状況へ戻るためのProvenanceであり、Realization identityを分けるfieldではない。

この経路はOllama release archiveやmodel artifactの外部取得を省略できるが、KJ Atlas backendのPython依存関係などを含む完全なoffline実行を保証するものではない。

### local execution safety

repository-local化によって、workflow環境では暗黙に成立していた前提も明示する。

- SOZA / KJ Atlasに未commit変更がある場合は、実行bytesとcommit identityが一致しないため開始しない。
- `--work-dir`は既存directoryを受け付けず、harness自身が新しく作成したdirectoryだけを一時作業領域として扱う。
- `--evidence-dir`も既存directoryを受け付けず、一つのdirectoryに一つのrunだけを対応させる。
- work / Evidence / external model directoryがSOZAまたはKJ Atlas repository配下を指す場合は拒否する。
- 固定local port `11434` / `8001` / `8101`が使用中なら開始しない。
- Ollama / model adapter / KJ Atlasのready判定では、health responseだけでなくharness自身が起動したPIDの生存も確認する。
- 事前配置runtime archiveはfile実在を確認し、実測digestが一致しなければ展開しない。
- 事前配置model storageに固定model digestが存在しなければ、自動取得せず停止する。

Evidence directoryをrunごとに分離するのは、今回runが途中で停止した場合に、前回runの未上書きファイルが残って一つのEvidence集合に見えることを防ぐためである。

この停止線により、既に動いている別Ollama等のresponseを今回のruntime version交換Evidenceとして誤認したり、利用者が指定した既存作業directoryをcleanupで削除したり、複数runのEvidenceを混在させたり、事前配置artifactを暗黙に差し替えたりすることを避ける。

## Artifact guard

runtime交換のlive testを開始する前に、Go側でも実際の実験条件を再確認する。

`runtime_version_artifact_guard_test.go`は、`SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1`のときだけ次を検査する。

- harnessが明示したKJ Atlas checkoutのactual commitが固定commitと一致する。
- harnessが明示したruntime A / Bのversion logが、それぞれ`0.32.13` / `0.32.14`を示す。
- harnessが明示したruntime archive bytesのSHA-256が固定値と一致する。

current live guardは`GITHUB_WORKSPACE`や固定`/tmp`配置へ暗黙に戻らない。実行器が検証対象pathをすべて明示することで、実行面を変えたときにも別のsourceやartifactを誤って検査する余地を狭める。

通常のunit testではexternal runtimeを要求しない。

`runtime_version_artifact_guard_unit_test.go`では、次を固定する。

- exact version tokenを受理する。
- `0.32.13`と`0.32.130`のようなnumeric suffixを取り違えない。
- exact artifact digestを受理する。
- artifact digest mismatchを拒否する。
- live guard用pathが明示されている場合だけ、そのpathを利用できる。
- 必須pathが空ならlive guardを開始しない。
- `GITHUB_WORKSPACE`だけではKJ Atlas pathを補完しない。
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

### harness interfaceの軽量検査

`runtime/integration/test_run_runtime_version_exchange.py`は、actual runtimeやmodelを取得せず、harnessとGo側の固定境界がずれていないかを検査する。

確認対象は次である。

- shell syntaxが有効である。
- `--help`をprobe起動なしで参照できる。
- shell側のOllama version / archive digestがGo側の固定値と一致する。
- harnessがKJ Atlas checkout、A / B archive、A / B version logをlive guardへ明示する。
- Go側live guardに`GITHUB_WORKSPACE`や固定`/tmp`の暗黙fallbackが残っていない。
- Evidence directoryをrunごとの新しいpathへ分離する停止線が残っている。
- 事前配置runtime archiveでも実測SHA-256を固定値へ照合する。
- 事前配置model storageで固定artifactが見つからない場合、自動pullせず停止する。
- artifact取得経路と固定identityが別fieldとして保持される。

```text
harness interface test PASS
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Required experiments

### E1 — runtime artifact identity

両runtime archiveを固定URLから取得するか事前配置pathから参照し、実測SHA-256を固定値と照合する。

PASS条件:

- Aが`0.32.13`として起動する。
- Bが`0.32.14`として起動する。
- A / Bそれぞれの実測archive digestが固定値と一致する。
- download / prepositionedのどちらでも同じdigest検証を通る。
- 実測digestをEvidence directoryから読み直せる。

### E2 — same pinned model artifact

両runtimeで`qwen2.5:0.5b`を利用し、APIが返すmodel digestを確認する。

PASS条件:

- A / Bのmodel digestが同一である。
- A / Bのmodel digestが固定した期待artifact identityと一致する。
- model tagだけで同一性を推論しない。
- 事前配置model storageを使う場合もfull digest一致を要求する。
- 事前配置model storageに固定artifactがなければ自動pullで内容を変更しない。

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
- archive acquisition modeだけを変えても、同じartifact bytesである限りRealization identityを別物として扱わない。

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

runtime交換実験をGitHub Actions workflowや特定artifact取得経路に閉じ込めず、repository-local harnessから再現できる状態を保つ。

PASS条件:

- fixed experiment identityがscript内に明示されている。
- actual inferenceに必要な処理がrepository同梱資産として残る。
- harnessからlive Go testへ必要なKJ Atlas path、runtime log、archive path、model identityを渡せる。
- runtime archiveをdownload / prepositionedの双方から同じdigest検証へ通せる。
- 事前配置model storageでも固定full digestを検証できる。
- 実験に使うOS / architectureとsource commitをEvidenceへ残せる。
- artifact acquisition / storage modeをProvenanceとして残せる。
- 起動前のport確認と起動PID確認によって、別processを今回の実行identityへ取り込まない。
- GitHub Actions、runner ID、artifact取得経路をMethod / Realization identityへ含めない。

### E9 — Evidence preservation

actual runtime交換の入力、実行条件、結果を一時ログだけに閉じない。

Evidence directoryへ、存在する範囲で次を保存する。

- experiment identity
  - execution ID
  - SOZA repository commit
  - KJ Atlas source commit
  - execution host OS / architecture
  - runtime A / B version / expected archive SHA-256
  - runtime A / B archive acquisition mode
  - expected model digest
  - model storage mode
  - `qualityJudgement = not_evaluated`
- Method request
- A / B runtime version log
- A / B **actual runtime archive SHA-256**
- A / B model digest / tags
- A / B inference Evidence
- A / B KJ Atlas result
- Adapter / KJ Atlas / Ollama log

途中で停止した場合も、そこまで生成されたEvidenceを残す。runtime archiveのdigest mismatchで停止した場合も、期待値だけでなく実際に計算したdigestを保存する。

一つのEvidence directoryは一つのrun専用とし、既存directoryへ追記しない。これにより、途中失敗したrunに前回runの後半Evidenceが残っているような混在を防ぐ。

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
- Linux / amd64の実行前guard
- SOZA / KJ Atlas clean-tree guard
- source repository配下を拒否するwork / Evidence / external model path guard
- 既存`--work-dir`を拒否し、harness所有の新規作業directoryだけをcleanupする境界
- 既存`--evidence-dir`を拒否し、Evidenceをrun単位に分離する境界
- local port availabilityと起動PIDの生存確認
- A / B runtime archiveの実測SHA-256保存
- live guardへ検査対象pathを明示する境界
- harness / Go固定identityの軽量整合test
- fixed runtime archiveのdownload / prepositioned両経路
- fixed model artifactのwork-local / prepositioned storage両経路
- 事前配置model storageを暗黙更新しない停止線
- acquisition / storage modeをEvidence identityへ残すProvenance
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
  = implemented

post-merge harness hardening
  = implemented

harness / Go fixed-identity consistency checks
  = implemented; actual runtime not required

runtime artifact / source / version live guard
  = implemented with explicit paths

run-isolated Evidence directory guard
  = implemented

prepositioned runtime/model artifact paths
  = implemented; actual A/B execution through these paths Not Yet Verified

actual runtime 0.32.13 / 0.32.14 acquisition or prepositioned load through current harness
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

1. repository-local harnessが固定runtime artifact A / Bを取得または事前配置pathから参照し、実測digestを保存したうえで固定値と一致することを確認できる。
2. A / Bのactual binary versionを確認できる。
3. A / B双方のmodel digestが固定artifact identityと一致し、same prompt digestもactual executionで確認できる。
4. 両runtimeでactual inferenceが成立する。
5. Application A / Bがsame logical / different Exact Realization revisionを保持する。
6. Application AのReference / Provenance / outputがB追加後も不変である。
7. Realization payload verification、portable reconstruction、unknown revision negative controlがPASSする。
8. Recommendation / Decisionへの自動昇格がない。
9. run専用filesystem Evidence directoryから実験identity、artifact取得状況、入力、A / Bの実測runtime digest、出力、model Evidenceへ戻れる。
10. Requirement / Contract再照合と自然な日本語最終監査を行う。

GitHub-hosted runnerの復旧、GitHub Actions workflowの再導入、runtime/model artifactの実行時download可否はResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revisionを交換するとhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- Realization payloadと宣言Exact Bindingの不一致を検出できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを参照するbundleを受理する。
- model tagが固定artifact identityと異なるartifactを指し、model artifactが交換軸へ混入する。
- promptが交換軸へ混入する。
- 事前配置runtime archiveをpathやファイル名だけで信用し、実測digest検査を省略できる。
- 事前配置model storageに固定artifactがないとき、harnessが暗黙にpullして検証対象を変更する。
- artifact acquisition modeだけの違いを別Realization identityとして扱う。
- 別processのhealth responseを今回のactual runtime実行として誤認できる。
- 利用者が指定した既存作業directoryをharnessが上書き・削除できる。
- 複数runのEvidenceが同じdirectoryへ混在し、一つの実行identityとして読めてしまう。
- live guardが実行器から渡されたpath以外を暗黙に参照し、source / artifact identityを取り違えられる。
- runtime固有情報をUniversal semanticsへ先取りする。
- actual実験本文が特定automation providerにしか存在せず、repositoryから再実行できなくなる。
- runtime交換successをmodel / KJ成果品質やE4へ過大評価する。

## Stop line

runtime交換がPASSしても、次を意味しない。

```text
runtime 0.32.13 / 0.32.14 exchange PASS
  != arbitrary runtime version portability
  != other runtime implementation portability
  != fully offline execution guaranteed
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

PR #76でactual実験本文をrepository-local harnessへ戻した後、ローカル実行特有の前提も再監査した。source treeのcleanliness、専用作業領域、実行platform、process起動環境を明示し、別processのhealth responseや利用者所有directoryを今回の実験へ誤って取り込まないようにした。また、runtime archiveについて期待digestだけでなく実測digestもEvidenceへ残すことで、途中失敗時の事実へ戻れるようにした。

さらに、harnessとGo側live guardの間で検査対象pathを暗黙のworkspaceや`/tmp`へ委ねないようにした。KJ Atlas checkout、runtime archive、version logは実行器が明示し、軽量testでshell側とGo側の固定runtime identityがずれていないことも確認できる構造にした。この軽量testはactual inferenceの代替にはしない。

Evidence保存先もrunごとの新しいdirectoryに限定した。途中失敗した新runへ過去runのファイルが残り、実際には生成されていない後半Evidenceまで今回のものとして読める状態を避けるためである。

今回さらに、runtime/model artifactを「実行時にdownloadできること」と「固定artifactを実際に使うこと」へ分けた。runtime archiveはdownloadと事前配置のどちらでも同じ実測SHA-256へ戻し、modelもtagではなくfull digestで固定する。既存model storageを使う場合は不足artifactをharnessが暗黙に取得せず、検証対象を外から与えた状態のまま扱う。

取得経路は再現時の状況を知るためEvidenceへ残すが、Realization identityそのものには昇格させない。これにより、特定runnerだけでなく特定のdownload可否にも実験意味を閉じ込めない一方、artifact identityの検証強度は下げない。

これらはruntime交換が成功したというEvidenceではない。実行identityを取り違えず、失敗時にも観測事実を残すための実験基盤の補強である。actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedとして維持している。

実行artifactの固定、artifact取得経路、payload digest検証、bundle-local reference解決、Evidence保存を別の責務として記述し、一つのPASSへ圧縮していない。意味、規範強度、Evidence強度、未検証範囲を変えず、自然な日本語として読み通せることを最重要視して全文を再ドラフトした。
