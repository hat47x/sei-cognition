# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

同じCognitive Method、同じKJ Atlas source、同じMethod input、同じactual model artifactを使い、Ollama runtime versionだけを交換したときに、SOZAが先行Method Applicationの履歴を失わず保持できるかを実証する。

runtime version差は別のlogical Method Realizationへ分けない。同じ実現機構に属するhistorical revisionとして扱い、既存Cognitive Method ContractのExact Bindingで区別する。

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

- Method Definitionは「何を行うMethodか」を表す。
- Method Realizationは「どの実現機構で実行するか」を表す。
- 同じ実現機構のversion差は、同じlogical Realizationに属するhistorical revisionとしてExact Bindingで固定できる。
- Method Applicationは、実行時に利用したRealization revisionをExact Referenceで保持できる。
- runtime / model固有情報は、必要なProvenance / realization-local metadataとして保持する。
- runtime archiveやmodel artifactの取得経路はProvenanceであり、artifact identityそのものではない。
- Method outputをRecommendation / Decisionへ自動昇格しない。
- GitHub Actions、runner ID、workflow run IDをMethodの意味やruntime交換成立条件にしない。

## ISSUE-000067 / ISSUE-000068との接続

ISSUE-000067では、Method Definition / Realization / Applicationを履歴として再構成する境界を確認した。

```text
実現機構が異なる
  → logical Realizationを分ける

同じRealizationのhistorical revisionを固定する
  → Exact Bindingを使う
```

ISSUE-000068では、KJ Atlas source、runtime、Method inputを固定し、actual model artifactだけを交換した。後続Applicationを追加しても先行ApplicationのRealization、Provenance、outputを保持できることをScoped Executable Evidenceとして確認した。

本Issueでは交換軸をさらに狭める。

```text
ISSUE-000068
  model artifactを交換
  runtimeは固定

ISSUE-000070
  model artifactを固定
  runtime versionだけを交換
```

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

model artifact digestはActual Model Artifact Exchange E3b Run `33670697154`でOllama `0.32.14`からactualに観測したidentityである。

A / Bのdigestが互いに等しいだけでは固定条件成立としない。両方がこの期待full digestに一致することを要求する。同じmodel tagが将来別artifactを指した場合は、実験条件が変わったものとして停止する。

交換するのはOllama runtime versionだけである。

- revision A: `0.32.13`
- revision B: `0.32.14`

## Pinned runtime artifacts

installerによるglobal installは使わず、Ollama公式GitHub ReleaseのLinux / amd64 archiveを別々の一時directoryへ展開し、binaryを直接起動する。

| revision | asset | official size | fixed SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesである。

2026-09-03の再監査では、sizeとdigestをOllama公式Release metadataへ照合した。MLX / ROCm等の別assetは同じversion名でも別bytes / 別digestであり、本Issueの固定artifactへ置き換えない。

sizeは明らかな取り違えを大きなSHA-256計算より前に拒否するための早期guardである。artifact identityの正本はactual bytesのSHA-256とする。

```text
archive size match
  != artifact identity verified

archive size match
  + exact SHA-256 match
  = fixed runtime archive identity guard
```

current harnessはこの固定artifactに合わせLinux / amd64だけを受理する。これはSOZA全体のplatform supportをLinux / amd64へ限定する意味ではない。

## Exact Realization Reference

KJ Atlas live mappingは、後方互換なoptional経路として`ApplyGroupingInput.RealizationReference`を受け取れる。

- 未指定時は従来どおりlogical-only Realization Referenceを保持する。
- 指定時は`method_application.realization_ref`へ`semanticruntime.Reference`を保持する。
- logical identityが`RealizationRef`と一致しなければcanonical stateを変更せず拒否する。

Exact Bindingを作るMethod Realization payloadと、portable Semantic Interchangeへ格納するRealization recordは同じ生成経路を使う。

このmappingはActual Model Artifact Exchange E3b Run `33670697154`で`go test ./livemethodintegration -count=1`を含めactualにPASSしている。ただし、この既存Evidenceをruntime version交換の成立証明には使わない。

## Repository-local execution harness

PR #70でGitHub Actions workflowをcurrent baselineから外したため、actual実験本文はrepository同梱の次のharnessを正とする。

- `runtime/integration/run_runtime_version_exchange.sh`

harnessは概ね次を行う。

1. Linux / amd64であることを確認する。
2. SOZA / KJ Atlasのworking treeがcleanで、KJ Atlasが固定commitであることを確認する。
3. 固定KJ Atlas backend用Python environmentを用意する。
4. runtime A / B archiveを取得または事前配置pathから参照し、actual SHA-256を固定値と照合する。
5. A / Bで同じmodel storageを使い、model full digestが固定値と一致することを確認する。
6. 同じMethod inputをA / Bへ通し、actual inference countersとKJ Atlas resultを保存する。
7. A / Bのprompt SHA-256が同一であることを確認する。
8. `livemethodintegration`の通常testとruntime交換live testを実行する。
9. historical Application不変性、Exact Binding、portable reconstruction、negative controlを確認する。
10. 成否にかかわらず、そこまで生成されたEvidenceをrun専用directoryへ保存する。

```text
repository-local harness
  = reproducible execution boundary
  != GitHub Actions required
  != specific runner required
```

### artifact acquisition boundary

runtime archiveは次の二経路を許可する。

- harnessがOllama公式Releaseから取得する。
- `--runtime-a-archive` / `--runtime-b-archive`で事前配置済みarchiveを指定する。

どちらもactual bytesの固定SHA-256へ戻す。事前配置path、file名、sizeだけを根拠に固定artifactとはみなさない。

model storageも次の二経路を許可する。

- harness所有のwork-local storageを使い、不足時に`ollama pull`した後でfull digestを検査する。
- `--model-dir`で既存storageを指定し、固定full digestのartifactが既に存在するときだけ利用する。不足してもharnessから自動pullしない。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual bytes / full digest

acquisition path
  != artifact identity
```

### local execution safety

repository-local化に伴い、次を停止線とする。

- SOZA / KJ Atlasに未commit変更があれば開始しない。
- `--work-dir` / `--evidence-dir`は新しいpathだけを受け付ける。
- work / Evidence / external model directoryをSOZAまたはKJ Atlas repository配下に置かない。
- fixed local port `11434` / `8001` / `8101`が使用中なら開始しない。
- health responseだけでなくharness自身が起動したPIDの生存を確認する。
- 事前配置runtime archiveはfile実在とactual identityを検査する。
- 事前配置model storageに固定model artifactがなければ暗黙更新しない。
- 一つのEvidence directoryを一つのrunだけへ対応させる。

## Local preflight

actual runtimeを起動する前に、次で副作用のない診断を行う。

- `runtime/integration/check_runtime_version_exchange_preflight.py`
- `runtime/integration/test_check_runtime_version_exchange_preflight.py`

preflightはruntime / model processを起動せず、artifactをdownloadしない。

現在の診断範囲は次である。

- Linux / amd64
- required command
- SOZA / KJ Atlas Git working tree / cleanliness
- fixed KJ Atlas commit
- work / Evidence / model path境界
- 事前配置runtime archiveのofficial sizeとactual SHA-256
- 事前配置model storage directory
- local port availability
- work領域を置くfilesystemのfree bytes

free bytesは観測値として残す。固定archive 2本の圧縮bytes合計との比較材料にはできるが、展開後runtime、Python environment、work-local model storageには追加容量が必要であるため、preflightはdisk容量が十分だとは断定しない。

```text
disk free-space observation
  != enough capacity proven
```

`--require-prepositioned-artifacts`ではruntime archiveとmodel storageの事前配置を要求できる。`--json`では固定artifact metadata、`ready` / `blocked`、blocker ID、各checkを構造化して返す。

model storage directoryの存在だけではmodel digestを検証済みとみなさない。full digestはOllama actual起動後にAPIから確認する。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

preflightの純粋ロジックと固定identity境界について、この作業セッションでは12件のローカルtestを実行し、すべてPASSした。actual runtimeを起動したEvidenceではない。

## Artifact guard / lightweight regression

Go側live guardは、`SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1`のときだけactual KJ Atlas commit、runtime version log、runtime archive digest等を再確認する。実行器が対象pathをすべて明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。

pure-Go controlでは少なくとも次を検査する。

- exact version token
- fixed artifact digest mismatch
- required live guard path
- Raw Bytes SHA-256 Exact Binding verification
- payload改変時の`verification_failed`
- Exact Bindingの決定性
- runtime version / runtime artifact / model artifact identity差によるBinding差

`runtime/integration/test_run_runtime_version_exchange.py`はactual runtimeを取得せず、shell syntax、固定identity、明示path、Evidence directory、事前配置artifact検査、model storage非自動更新等のinterface境界を検査する。

```text
harness / preflight test PASS
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Required experiments

### E1 — runtime artifact identity

PASS条件:

- Aが`0.32.13`としてactual起動する。
- Bが`0.32.14`としてactual起動する。
- A / Bのactual archive SHA-256が固定値と一致する。
- download / prepositionedのどちらでも同じidentity検査へ戻る。
- actual digestをEvidenceから読み直せる。

archive sizeは早期guardであり、E1成立条件をSHA-256から置き換えない。

### E2 — same pinned model artifact

PASS条件:

- A / Bのmodel digestが同一である。
- A / Bのmodel digestが固定full digestと一致する。
- model tagだけで同一性を推論しない。
- 事前配置storageでもfull digest一致を要求する。

### E3 — same prompt / actual inference

PASS条件:

- A / Bに同じprompt SHA-256が記録される。
- `ollama_done = true`。
- `prompt_eval_count > 0`。
- `eval_count > 0`。
- KJ Atlas response boundaryが両resultを受理する。

生成文そのものの一致は要求しない。

### E4 — same logical Realization / different Exact Binding

PASS条件:

- A / Bは同じlogical Realizationを持つ。
- A / BはそれぞれExact Bindingを持つ。
- A / BのExact Bindingは異なる。
- 同じidentityからは同じBindingを再構成できる。
- runtime / model artifact identityを変えるとBindingも変わる。
- acquisition modeだけの違いを別logical Realizationへしない。

### E5 — historical Application immutability

PASS条件:

- Application AのExact Reference / Provenance / outputがB追加後も変わらない。
- Application Bはrevision BのExact Referenceを保持する。
- 両Applicationは同じMethod Definitionを指す。
- 両Provenanceは同じ固定model artifactを指す。
- 各Provenanceからruntime revisionへ戻れる。

### E6 — portable historical reconstruction

PASS条件:

- Realization payloadをRaw Bytes SHA-256 Profileで検証できる。
- `semanticruntime.LoadInterchange`がbundle-local Exact Binding検証を通る。
- Application A / Bを対応するrevisionへ解決できる。
- payload改変を拒否する。
- unknown revision digestを参照するnegative bundleを拒否する。

### E7 — no semantic promotion

runtime交換後もMethod outputをRecommendation / Decisionへ自動昇格しない。

### E8 — execution surface independence

- actual実験本文がrepository同梱資産として残る。
- fixed identityがscript / guardへ明示される。
- download / prepositionedを同じidentity検証へ通せる。
- host / source / acquisition状況をEvidenceへ残せる。
- GitHub Actions、runner ID、取得経路をMethod / Realization identityに含めない。

### E9 — Evidence preservation

一つのrun専用Evidence directoryから、存在する範囲で次へ戻れることを要求する。

- execution ID
- SOZA commit
- KJ Atlas commit
- host OS / architecture
- runtime A / B version / expected digest / acquisition mode
- expected model digest / storage mode
- `qualityJudgement = not_evaluated`
- Method request
- A / B actual runtime digest / version log
- A / B model tags / digest
- A / B inference Evidence / KJ Atlas result
- process log

```text
Evidence preserved
  != runtime exchange PASS
  != output quality satisfied
```

## Existing Evidence

### Exact Reference mapping / fixed model source

Actual Model Artifact Exchange E3b Run `33670697154`はactualに完走し、model full digest、prompt digest、`go test ./livemethodintegration -count=1`、historical Application保持を確認した。

このEvidenceはExact Reference mappingと今回固定するmodel artifact identityを支えるが、runtime version交換そのもののEvidenceではない。

### Historical GitHub Actions exploration

過去のruntime交換workflow試作ではGitHub-hosted runnerが`runner_id=0 / steps=[]`等で割り当て前に終了する状態を観測した。PR #70ではcurrent baselineからGitHub Actions workflowを撤去し、ISSUE-000069では検証内容と実行場所を分離する境界をResolvedとした。

runner復旧やActions再導入は本IssueのResolution条件ではない。

### Current execution environment observation

2026-09-03の現作業環境ではLinux / amd64、主要Python依存、Go等を利用でき、`/tmp`には約32GBのfree spaceを観測した。一方、この環境にはSOZA / KJ Atlasの固定Git checkoutとOllama binary / model artifactが事前配置されていない。

また、historical Run `33670697154`には再利用可能なActions artifact保存がなかった。

これは環境固有の観測であり、SOZAのProduct failureではない。actual A / Bが成立したEvidenceにもならない。

## Current implementation state

current developには次がある。

- Exact Realization Reference mapping
- logical identity mismatchの無変更失敗test
- fixed runtime / model identity
- runtime execution identity guard
- Exact Binding verification / determinism / negative control
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- repository-local runtime exchange harness
- clean-tree / path / port / PID safety guard
- run-isolated Evidence directory
- download / prepositioned runtime archive経路
- work-local / prepositioned model storage経路
- acquisition / storage mode Provenance
- local preflight
- official archive size early guard
- disk free-space observational diagnostic
- preflight unit test 12件PASS

ただし、current harnessによるactual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していない。

## Current Evidence state

```text
fixed runtime version / official archive size / official digest
  = statically verified

qwen2.5:0.5b expected model artifact identity
  = actual digest observed historically

Exact Realization Reference mapping
  = Scoped Executable Evidence available historically

repository-local harness / guards / preflight
  = implemented

preflight local regression
  = 12 tests PASS

actual runtime A/B acquisition or prepositioned load through current harness
  = Not Yet Verified

same pinned model digest / same prompt digest across runtime versions
  = Not Yet Verified

actual runtime-version exchange inference
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

ISSUE-000071はoutcome-quality評価境界の確立としてResolvedだが、human reviewやKJ-method outcome qualityがSatisfiedになったことを意味しない。本Issueでもexecution conformanceと成果品質を混同しない。

## Requirement / Contract assessment

現時点では新しいStable Requirement / Acceptance Scenario / Universal Contract fieldを追加しない。

actual実証後に少なくとも次へ再照合する。

- REQ-0001
- REQ-0004
- REQ-0021
- SCN-0005
- SCN-0015

既存Requirement / Contractで観測結果を十分に表せる場合はNo Changeとする。

## Resolution

次をすべて満たした時点でResolvedにできる。

1. repository-local harnessが固定runtime A / Bのactual bytesを利用し、SHA-256を固定値へ一致させる。
2. A / Bのactual binary versionを確認する。
3. A / B双方のmodel digestが固定artifact identityに一致し、same prompt digestもactual executionで確認する。
4. 両runtimeでactual inferenceが成立する。
5. Application A / Bがsame logical / different Exact Realization revisionを保持する。
6. Application AのReference / Provenance / outputがB追加後も不変である。
7. Realization payload verification、portable reconstruction、unknown revision negative controlがPASSする。
8. Recommendation / Decisionへの自動昇格がない。
9. run専用Evidence directoryから実験identity、取得状況、入力、A / B actual runtime digest、model Evidence、出力へ戻れる。
10. Requirement / Contract再照合と自然な日本語最終監査を行う。

archive size、preflight ready、disk free-space、GitHub-hosted runner復旧、GitHub Actions再導入、runtime/model artifactの実行時download可否は、それ単独ではResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revision交換でhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- Realization payloadとExact Bindingの不一致を検出できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを受理する。
- model tagが固定artifact identityと異なるartifactを指し、model交換が混入する。
- promptが交換軸へ混入する。
- 事前配置archiveをpath、file名、sizeだけで信用しSHA-256を省略できる。
- 事前配置model storageを暗黙に更新する。
- acquisition modeだけの違いを別Realization identityへする。
- 別processのhealth responseを今回のactual実行と誤認する。
- 既存work / Evidence directoryを上書き・混在できる。
- live guardが暗黙pathへfallbackしてsource / artifactを取り違える。
- runtime固有情報をUniversal semanticsへ先取りする。
- actual実験本文が特定automation providerにしか存在しなくなる。
- runtime交換successをmodel / KJ成果品質やE4へ過大評価する。

## Stop line

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

execution成立、historical reconstruction、成果品質を別の評価軸として扱う。

## 自然な日本語レビュー

ISSUE-000067 / 000068 / 000071、Cognitive Method Contract、Exact Binding、current KJ Atlas mapping、no-Actions baseline、repository-local harness、preflight、Ollama公式Release metadataへ戻って本Issueを再監査した。

固定runtime artifactについては、versionとdigestだけでなく公式asset sizeも確認した。sizeは明らかなfile取り違えをSHA計算前に止めるための補助guardとして使うが、identity判定をsizeへ弱めていない。actual bytesのSHA-256を引き続き正本とする。

preflightにはwork filesystemのfree bytes観測も加えた。ただし固定archive 2本の圧縮bytes合計だけでは、展開後runtime、Python environment、model storageまで含む必要容量を決められないため、disk観測だけを`ready`の十分性証明にはしていない。

また、artifactを実行時にdownloadできることと、固定artifactを実際に利用することを分けている。事前配置経路でも同じidentity検査へ戻し、既存model storageを暗黙に更新しない。

この作業セッションではpreflightのローカルtestを12件実行し、すべてPASSした。しかし、これはruntime A / Bを起動したEvidenceではない。actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedであり、本IssueはOpenのままとする。

意味、規範強度、Resolution条件、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
