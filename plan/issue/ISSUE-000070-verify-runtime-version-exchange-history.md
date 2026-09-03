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
- runtime archive、model artifact、KJ Atlas sourceをどの経路で入手したかはProvenanceであり、artifact / source identityそのものではない。
- Method outputをRecommendation / Decisionへ自動昇格しない。
- GitHub Actions、runner ID、workflow run IDはCognitive Methodの意味やruntime交換成立条件にしない。

GitHub Actionsは当面完全に停止する。workflowの追加・復元、historical runの再実行、runner監視を本Issueの実証手段には使わない。必要な確認はrepository-local harness、checker、test、probeをローカルで個別に実行する。

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

これはruntime交換をactualに実行したExecutable Evidenceではない。

current harnessはこの固定artifactに合わせてLinux / amd64だけを受理する。これはSOZA全体のplatform supportをLinux / amd64へ限定する意味ではなく、今回の交換実験に使うartifact条件を実行前に固定するprobe-localな制約である。

runtime archiveはharnessがOllama公式GitHub Releaseから取得しても、別経路で事前配置してもよい。ただし、どちらの経路でも実際に利用するarchive bytesのSHA-256を計算し、上記固定値へ一致させる。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual archive bytes + fixed SHA-256

acquisition path
  != artifact identity
```

## KJ Atlas source identity

KJ Atlas sourceは、次の二経路を受理する。

1. 固定commitのclean Git checkout。
2. 固定commitから切り出し、Git object identityを再検証できる最小runtime source bundle。

Git checkoutの存在自体を実験成立条件にはしない。一方で、bundle pathやfile名だけを固定sourceの根拠にも使わない。

### Git checkout mode

checkout modeでは次を確認する。

- working treeがcleanである。
- HEADが固定commit `4f28c13abe4176503c6fed863383a2d1db2299e9`である。
- 固定commit objectをrepository内で参照できる。
- package installはactual checkoutを直接build対象にせず、harness所有のwork directoryへ作ったcopyから行う。
- live Go test直前にもcheckoutがcleanなままであることを再確認する。

これにより、package buildが生成するmetadata等を、実際に使ったKJ Atlas sourceの未記録変更として混入させない。

### Verified runtime bundle mode

`--kj-atlas-backend-bundle`では、固定commitの`03_Implement/backend`から実行に必要な次の4要素だけを持ち込む。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

固定identityは次のように区別する。

```text
fixed KJ Atlas commit
  4f28c13abe4176503c6fed863383a2d1db2299e9

parent backend tree
  7d71ac2b4d32bef90f3a481ade1b4c92ddddd084

minimal runtime surface tree
  208bea71eef4afed3ddfd3fabb36b0969d167a90
```

`parent backend tree`は、固定commit内でruntime surfaceを切り出した親文脈である。`minimal runtime surface tree`は、実際にbundleへ持ち込む4要素だけからGit object規則で再構成したtree identityである。

```text
parent backend tree
  != runtime surface tree
```

`runtime/integration/verify_kj_atlas_runtime_source.py`は、Git blob / tree object IDをsource bytesとdirectory構造から再計算し、次を検査する。

- `pyproject.toml` blob
- `alembic.ini` blob
- `alembic/` tree
- `src/` tree
- 4要素だけから再構成したruntime surface tree
- 予期しないtop-level要素が存在しないこと
- symlinkが混入していないこと
- runtime source fileへ実行bitが付いていないこと

bundle modeでは、検証済みの外部bundleを直接build・実行しない。harness所有のwork directoryへ実行用copyとpackage install用copyを別々に作り、両方を再検証する。live test開始時にはGo側guardから実行用copyを再度検証する。

`--kj-atlas-dir`と`--kj-atlas-backend-bundle`は同時に指定できない。

```text
source acquisition
  = clean-git-checkout | verified-runtime-bundle

source identity
  = pinned commit context + verified source bytes

source acquisition path
  != Method Realization identity by itself
```

## Exact Realization Reference

既存のKJ Atlas live mappingへ、後方互換なoptional経路として`ApplyGroupingInput.RealizationReference`を追加した。

- 未指定の場合は従来どおりlogical-only Realization Referenceを保持する。
- 指定した場合は`method_application.realization_ref`へ`semanticruntime.Reference`を保持する。
- logical identityが`RealizationRef`と一致しなければ、canonical stateを変更せず拒否する。

Exact Bindingを作るMethod Realization payloadと、portable Semantic Interchangeへ格納するRealization recordは同じ生成経路を使う。

このmappingではExact Referenceを保持するためMethod Application recordを直接`CanonicalStore.Add`へ渡すが、semantic validationを迂回しない。`CanonicalStore.Add`はtyped recordを`semanticruntime.LoadStandalone`で再検証してから保存する。

共有mapping自体はActual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`で`go test ./livemethodintegration -count=1`を含めactualにPASSしている。したがってExact Reference mappingにはExecutable Evidenceがあるが、この既存Evidenceをruntime version交換の成立証明には使わない。

## Repository-local execution harness

runtime交換のactual実行本文はautomation providerから切り離し、repository同梱の次のharnessへ置く。

- `runtime/integration/run_runtime_version_exchange.sh`

harnessは次を一続きに実行する。

1. Linux / amd64の実行環境であることを確認する。
2. SOZAがcleanであることを確認し、KJ Atlas sourceをcheckoutまたはverified bundleとして検証する。
3. KJ Atlas package install用copyをwork directoryへ作り、専用Python virtual environmentへ導入する。
4. Ollama `0.32.13` / `0.32.14`のarchiveを取得または事前配置pathから参照し、実測SHA-256を保存して固定値と照合する。
5. 同じmodel storageで`qwen2.5:0.5b`を利用し、A / B双方のmodel digestが固定値と一致することを確認する。
6. 同じ3-card Method inputをA / Bへ通し、actual inference countersとKJ Atlas responseを確認する。
7. A / Bのprompt SHA-256が同一であることを確認する。
8. `livemethodintegration`の通常testを実行する。
9. source、runtime artifact、versionをGo側でも再確認したうえでruntime交換live testを実行し、historical Applicationとportable reconstructionを検査する。
10. 成否にかかわらず、そこまで生成されたEvidenceをrun専用directoryへ保存する。

実行場所、source取得経路、artifact取得経路は、それ自体を意味上のidentityにしない。

```text
repository-local harness
  = reproducible execution boundary
  != GitHub Actions required
  != specific runner required

prepositioned artifact
  = another acquisition path
  != weaker identity verification
```

## Artifact acquisition boundary

実験成立に必要なのは固定したruntime / model artifactそのものであり、実行時に外部ネットワークから取得できることではない。

runtime archiveは次の二経路を許可する。

- harnessがOllama公式GitHub Releaseから取得する。
- `--runtime-a-archive` / `--runtime-b-archive`で事前配置済みarchiveを指定する。

どちらも同じ実測SHA-256検証へ通す。事前配置pathやファイル名だけを根拠に固定artifactとはみなさない。

model storageも次の二経路を許可する。

- harness所有のwork-local model storageを使い、固定artifactがなければ`ollama pull`した後にfull digestを検査する。
- `--model-dir`で既存model storageを指定し、固定full digestのartifactが既に存在するときだけ利用する。不足していてもharnessから自動pullしない。

Evidence identityにはruntime archiveの`archiveAcquisition`とmodelの`storageMode`を残す。これは再実行時に取得状況へ戻るためのProvenanceであり、Realization identityを分けるfieldではない。

KJ Atlas sourceについても、`git-checkout`または`verified-runtime-bundle`という取得経路と、実際に検証したsource identityを分けてEvidenceへ残す。

これらの経路は外部取得依存を減らせるが、KJ Atlas backendのPython依存関係まで含めた完全offline実行を保証するものではない。

## Local execution safety

repository-local化に伴い、次を明示的な停止線とする。

- SOZAに未commit変更がある場合は開始しない。
- checkout modeのKJ Atlasに未commit変更がある場合は開始しない。
- checkout modeではpackage install後もactual checkoutがcleanなままかlive test直前に再確認する。
- bundle modeではsource bytesを外部入力時、実行用copy作成後、install用copy作成後、live test直前に検証する。
- `--work-dir`は既存directoryを受け付けず、harness自身が新しく作成したdirectoryだけを一時作業領域として扱う。
- `--evidence-dir`も既存directoryを受け付けず、一つのdirectoryに一つのrunだけを対応させる。
- work / Evidence / external model directoryがSOZAまたはKJ Atlas source配下を指す場合は拒否する。
- 固定local port `11434` / `8001` / `8101`が使用中なら開始しない。
- Ollama / model adapter / KJ Atlasのready判定では、health responseだけでなくharness自身が起動したPIDの生存も確認する。
- 事前配置runtime archiveはfile実在と実測digestを確認し、不一致なら展開しない。
- 事前配置model storageに固定model digestが存在しなければ、自動取得せず停止する。

Evidence directoryをrunごとに分離し、途中失敗したrunへ前回runの未上書きファイルが混在することを防ぐ。

## Local preflight

actual runtimeを起動する前に、ローカル環境で解消できる不足を副作用なく検出するため、次を使う。

- `runtime/integration/check_runtime_version_exchange_preflight.py`
- `runtime/integration/test_check_runtime_version_exchange_preflight.py`

preflightはruntime / model processを起動せず、artifactをdownloadしない。次を診断する。

- hostがLinux / amd64か。
- harnessが必要とするcommandが利用可能か。
- SOZAがGit working treeでcleanか。
- KJ Atlas sourceがclean checkoutまたはverified runtime bundleとして固定identityを満たすか。
- `--kj-atlas-dir`と`--kj-atlas-backend-bundle`が同時指定されていないか。
- work / Evidence pathがsource配下を指していないか、既存pathを誤って再利用しないか。
- 事前配置runtime archiveを指定した場合、実測SHA-256が固定値と一致するか。
- 事前配置model storageを指定した場合、directoryが存在し安全な位置にあるか。
- Ollama / model adapter / KJ Atlas用local portが空いているか。

`--require-prepositioned-artifacts`を指定すると、runtime archiveとmodel storageが事前配置済みであること自体をpreflight条件にできる。`--json`では`ready` / `blocked`、blocker ID、各checkの状態、KJ Atlas sourceの固定identityを構造化して返す。

model storageのdirectoryが存在するだけでは固定model artifactを検証済みとはみなさない。full model digestはOllamaをactualに起動した後、APIから観測して確認する。download経路を許可した通常preflightでも、まだ取得していないruntime archiveは`deferred`として扱う。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

最新developで追加されたpreflightの純粋ロジックと固定identity境界については、9件のローカルtestがPASSしている。本変更ではsource bundle経路を同じpreflight interfaceへ追加したが、追加後の最終branch全体についてactual runtimeはまだ起動していない。

## Artifact / source guard

runtime交換のlive testを開始する前に、Go側でも実際の実験条件を再確認する。

`runtime_version_artifact_guard_test.go`は、`SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1`のときだけ次を検査する。

### checkout mode

- harnessが明示したKJ Atlas checkoutのactual commitが固定commitと一致する。
- fixed commit objectを参照できる。
- working treeがlive test直前もcleanである。

### bundle mode

- harnessが明示した実行sourceをPython verifierで再検証する。
- source commitが固定値と一致する。
- 親backend treeが固定値と一致する。
- runtime surface treeが固定値と一致する。
- verification basisが`pinned-git-object-identities`である。

### runtime artifacts

- harnessが明示したruntime A / Bのversion logが、それぞれ`0.32.13` / `0.32.14`を示す。
- harnessが明示したruntime archive bytesのSHA-256が固定値と一致する。

current live guardは`GITHUB_WORKSPACE`や固定`/tmp`配置へ暗黙に戻らない。実行器が検証対象pathとsource modeをすべて明示する。

通常のunit testではexternal runtimeを要求しない。guard / Exact Binding controlでは少なくとも次を固定する。

- source mode未指定・未知modeを拒否する。
- checkout modeでpath未指定を拒否する。
- bundle modeでsource / verifier path未指定を拒否する。
- bundle verifierのsource commit / 親backend tree / runtime surface tree driftを拒否する。
- exact version tokenを受理し、`0.32.13`と`0.32.130`を取り違えない。
- exact artifact digestを受理し、mismatchを拒否する。
- Realization payload bytesが宣言したRaw Bytes SHA-256 Exact Bindingで`verified`になる。
- payloadを改変すると`verification_failed`になる。
- 同一identityから同じExact Bindingを決定的に再構成できる。
- runtime version、runtime artifact digest、model artifact digestのいずれかを変えるとExact Bindingも変わる。

```text
actual execution identity guard
  != payload digest verification
  != bundle-local Exact Reference resolution
```

## Lightweight boundary tests

actual runtimeやmodelを取得しない軽量検査として、次を用意する。

- `runtime/integration/test_verify_kj_atlas_runtime_source.py`
- `runtime/integration/test_check_runtime_version_exchange_preflight.py`
- `runtime/integration/test_run_runtime_version_exchange.py`
- `runtime/go/livemethodintegration/runtime_version_source_guard_unit_test.go`

主な確認対象は次である。

- Git tree SHA再構成が`git write-tree`と一致する。
- 固定4要素から再構成したruntime surface treeが`208bea71eef4afed3ddfd3fabb36b0969d167a90`へ一致する。
- 親backend treeとruntime surface treeを同一視しない。
- source改変、予期しないtop-level file、symlink、実行bit差を拒否する。
- harness / preflight / Python verifier / Go guardで固定source identityが一致する。
- shell側とGo側のruntime version / archive digestが一致する。
- checkout / bundle inputを混在できない。
- bundleは実行用copyとinstall用copyへ分離する。
- checkoutでもpackage installはwork領域のcopyから行い、actual checkoutをbuild対象にしない。
- harnessがsource mode、source path、verifier、runtime archive、version logをlive guardへ明示する。
- `GITHUB_WORKSPACE`や固定`/tmp`への暗黙fallbackがない。
- run専用Evidence directoryを要求する。
- 事前配置runtime archiveでも実測SHA-256を固定値へ照合する。
- 事前配置model storageに固定artifactがなければ自動pullしない。
- artifact取得経路と固定identityを別fieldとして保持する。

```text
lightweight boundary test PASS
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
- 事前配置model storageでもfull digest一致を要求する。
- 事前配置model storageに固定artifactがなければ自動pullで内容を変更しない。

### E3 — same source / prompt / actual inference

同じKJ Atlas source identityと同じMethod inputをmodel adapterへ通す。

PASS条件:

- source modeにかかわらず、実行したKJ Atlas sourceが固定identityへ検証される。
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
- source acquisition modeやarchive acquisition modeだけを変えても、同じsource / artifact bytesである限りRealization identityを別物として扱わない。

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

runtime交換実験をGitHub Actions、特定source取得経路、特定artifact取得経路に閉じ込めず、repository-local harnessから再現できる状態を保つ。

PASS条件:

- fixed experiment identityがrepository同梱資産に明示されている。
- KJ Atlas sourceをclean checkoutまたはverified runtime bundleとして固定identityへ戻せる。
- runtime archiveをdownload / prepositionedの双方から同じdigest検証へ通せる。
- 事前配置model storageでも固定full digestを検証できる。
- source / artifact acquisition modeをProvenanceとして残せる。
- 実験に使うOS / architectureとsource commitをEvidenceへ残せる。
- 起動前のport確認と起動PID確認によって、別processを今回の実行identityへ取り込まない。
- GitHub Actions、runner ID、source / artifact取得経路をMethod / Realization identityへ含めない。

### E9 — Evidence preservation

actual runtime交換の入力、実行条件、結果を一時ログだけに閉じない。

Evidence directoryへ、存在する範囲で次を保存する。

- experiment identity
  - execution ID
  - SOZA repository commit
  - KJ Atlas source mode / source commit
  - bundle modeでは親backend tree / runtime surface tree / component Git object ID
  - execution host OS / architecture
  - runtime A / B version / expected archive SHA-256
  - runtime A / B archive acquisition mode
  - expected model digest
  - model storage mode
  - `qualityJudgement = not_evaluated`
- `kj-atlas-source-identity.json`
- Method request
- A / B runtime version log
- A / B actual runtime archive SHA-256
- A / B model digest / tags
- A / B inference Evidence
- A / B KJ Atlas result
- Adapter / KJ Atlas / Ollama log

途中で停止した場合も、そこまで生成されたEvidenceを残す。一つのEvidence directoryは一つのrun専用とし、既存directoryへ追記しない。

```text
Evidence directory preserved
  != runtime exchange PASS
  != output quality satisfied
```

## Existing Evidence

### Exact Reference mapping / fixed model artifact source

Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`はactualに完走した。

このrunでは、actual model artifact exchange、full model digest、prompt digest、`go test ./livemethodintegration -count=1`、historical Application保持を確認した。

したがってExact Reference mappingにはExecutable Evidenceがあり、今回固定する`qwen2.5:0.5b`のmodel artifact identityもactual observationに基づく。ただし、これはruntime version交換のExecutable Evidenceではない。

### Historical GitHub Actions exploration

PR #63の作業中にはruntime交換workflow、scenario-local trigger、shared dependency trigger、Evidence artifact保存を試作した。一方、GitHub-hosted runnerは長期間`runner_id=0 / steps=[]`のまま割り当て前に終了し、PR #68の最小cross-OS probeでもUbuntu / Windows / macOSのすべてで同じ現象を観測した。

この履歴は保存するが、具体的な外部原因は確定しない。

現在はGitHub Actionsを当面完全停止している。workflowの追加・復元、過去runの再実行、runner監視は行わず、current actual実証はrepository-local harnessとローカル個別検査を正とする。

### Local preflight

最新developへ統合済みのpreflight純粋ロジックと固定identity境界について、9件のローカルtestがPASSしている。

これはactual Ollama A / B inferenceを開始したEvidenceではなく、runtime交換実験を開始する前の診断面に限定したExecutable Evidenceである。

本変更で追加したverified runtime bundle経路とcheckout source汚染防止については、軽量testを追加しているが、最終収束branch全体のactual Ollama交換はまだ実行していない。

## Current implementation state

current implementationには次がある。

- Exact Realization Referenceを保持できるKJ Atlas mapping
- logical identity不一致時の無変更失敗test
- fixed runtime / model identity
- runtime execution identity guard
- Realization payload Exact Binding verification
- Exact Binding決定性とidentity差分test
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- unknown revision digestのnegative control
- repository-local runtime exchange harness
- Linux / amd64の実行前guard
- KJ Atlas clean checkout mode
- KJ Atlas verified runtime bundle mode
- 親backend tree / runtime surface treeの分離
- Git blob / tree object IDを再構成するsource verifier
- checkout / bundle双方でpackage install sourceとactual execution sourceを分離する境界
- live test直前のsource再検証
- source repository配下を拒否するwork / Evidence / external model path guard
- 既存work / Evidence directoryを再利用しない境界
- local port availabilityと起動PIDの生存確認
- A / B runtime archiveの実測SHA-256保存
- live guardへ検査対象pathを明示する境界
- fixed runtime archiveのdownload / prepositioned両経路
- fixed model artifactのwork-local / prepositioned storage両経路
- 事前配置model storageを暗黙更新しない停止線
- source / artifact acquisition modeをEvidenceへ残すProvenance
- failure途中も保存できるrun専用filesystem Evidence directory
- side-effect-free local preflight
- preflight / harness / source verifier / Go guardの固定identity一致test

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
  = implemented

repository-local runtime exchange harness
  = implemented

local preflight boundary tests
  = 9 tests PASS; actual runtime not started

KJ Atlas clean checkout source guard
  = implemented

KJ Atlas verified runtime bundle source guard
  = implemented; actual A/B execution through this path Not Yet Verified

parent backend tree / runtime surface tree separation
  = implemented and fixed in source verifier / Go guard

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

1. KJ Atlas sourceをclean checkoutまたはverified runtime bundleとして固定identityへ検証できる。
2. repository-local harnessが固定runtime artifact A / Bを取得または事前配置pathから参照し、実測digestを保存したうえで固定値と一致することを確認できる。
3. A / Bのactual binary versionを確認できる。
4. A / B双方のmodel digestが固定artifact identityと一致し、same prompt digestもactual executionで確認できる。
5. 両runtimeでactual inferenceが成立する。
6. Application A / Bがsame logical / different Exact Realization revisionを保持する。
7. Application AのReference / Provenance / outputがB追加後も不変である。
8. Realization payload verification、portable reconstruction、unknown revision negative controlがPASSする。
9. Recommendation / Decisionへの自動昇格がない。
10. run専用filesystem Evidence directoryからsource identity、artifact取得状況、入力、A / Bの実測runtime digest、出力、model Evidenceへ戻れる。
11. Requirement / Contract再照合と自然な日本語最終監査を行う。

GitHub-hosted runnerの復旧、GitHub Actions workflowの再導入、runtime / model artifactの実行時download可否、preflightの`ready`だけではResolution条件を満たさない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revisionを交換するとhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- Realization payloadと宣言Exact Bindingの不一致を検出できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを参照するbundleを受理する。
- KJ Atlas source acquisition modeだけでsource identityを推論する。
- 親backend treeと最小runtime surface treeを同一identityとして扱う。
- bundle pathやfile名だけで固定sourceとみなす。
- source改変、予期しないtop-level要素、symlink、実行bit差をsource verifierが見逃す。
- package buildの副作用がactual execution sourceへ混入しても検出できない。
- model tagが固定artifact identityと異なるartifactを指し、model artifactが交換軸へ混入する。
- promptが交換軸へ混入する。
- 事前配置runtime archiveをpathやファイル名だけで信用し、実測digest検査を省略できる。
- 事前配置model storageに固定artifactがないとき、harnessが暗黙にpullして検証対象を変更する。
- source / artifact acquisition modeだけの違いを別Realization identityとして扱う。
- preflightがmodel storage directoryの存在だけで固定model digest検証済みと判定する。
- preflight `ready`をactual runtime交換PASSへ昇格できる。
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

ISSUE-000067 / ISSUE-000068、Cognitive Method Contract、Exact Binding、current KJ Atlas mapping、GitHub Actions完全停止後の開発運用、repository-local harness、local preflight、artifact / source guard、ISSUE-000071で確立した成果品質評価境界を再照合した。

今回、KJ Atlas sourceをGit checkoutそのものへ固定せず、固定commit由来の最小runtime surfaceをGit object identityで再検証できる経路を加えた。ただし親backend treeと実際に持ち込むruntime surface treeは別のidentityとして扱い、最小bundleをbackend全体と同一視しない。

source取得経路を増やす代わりに検証強度を下げないよう、checkout modeでは実行sourceをbuild対象から分離し、live test直前にもcleanlinessを再確認する。bundle modeでは外部入力、実行用copy、install用copy、live test直前の実行sourceを固定Git object identityへ戻す。

preflightもcheckout / bundleの二経路へ同期した。`ready`はactual probeを開始できる条件が揃ったことだけを表し、source identityの確認、runtime archive digest、actual model digest、actual inference、historical reconstructionを一つの成功条件へ圧縮しない。

GitHub Actionsの過去runはhistorical Evidenceとして保持するが、現在はworkflowの追加・復元・再実行・runner監視を行わない。必要な検証はローカルで個別に実行し、実行できない範囲は`Not Yet Verified`として残す。

これらはruntime交換が成功したというEvidenceではない。実行identityを取り違えず、失敗時にも観測事実を残し、actual A/B実行へ安全に進むための実験基盤である。actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedとして維持する。

実行sourceの固定、source取得経路、artifact取得経路、preflight、actual process identity、payload digest検証、bundle-local reference解決、Evidence保存を別の責務として記述した。意味、規範強度、Evidence強度、未検証範囲を変えず、自然な日本語として読み通せることを最重要視して全文を再ドラフトした。