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
same verified KJ Atlas runtime surface
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
- source / runtime archive / model artifactの取得経路はProvenanceであり、artifact identityそのものではない。
- Method outputをRecommendation / Decisionへ自動昇格しない。
- GitHub Actions、runner ID、workflow run IDをMethodの意味やruntime交換成立条件にしない。

GitHub Actionsはcurrent baselineで完全停止している。workflowの復元、過去runの再実行、runner監視は行わず、必要な検証はrepository-localなtest、checker、probeをローカルで個別に実行する。過去のActions Runはhistorical Evidenceとしてのみ保持する。

## ISSUE-000067 / 000068 / 000071との接続

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

ISSUE-000071は成果品質の評価境界を確立したIssueである。human reviewやKJ-method outcome qualityがSatisfiedになったことを意味しない。本Issueでもexecution conformanceと成果品質を混同しない。

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

installerによるglobal installは使わず、Ollama公式GitHub ReleaseのLinux / amd64 archiveを別々のruntime rootへ展開し、binaryを直接起動する。

| revision | asset | official size | fixed SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesである。

sizeは明らかなfile取り違えを大きなSHA-256計算より前に拒否するための早期guardであり、artifact identityの正本ではない。identityはactual bytesのSHA-256で固定する。

```text
archive size match
  != artifact identity verified

archive size match
  + exact SHA-256 match
  = fixed runtime archive identity guard
```

MLX / ROCm等の別assetは、同じversion名でも別bytes / 別digestである。本Issueの固定artifactへ置き換えない。

固定artifact metadataは`runtime/integration/runtime_version_exchange_artifacts.json`を機械可読な正本とし、`prepare_runtime_version_exchange_archives.py`でdownload / verify-only / prepositioned再利用を同じsize / SHA-256境界へ戻す。

Linux / amd64は本probeの実行条件であり、SOZA全体のplatform supportをLinux / amd64へ限定する意味ではない。

## KJ Atlas source identity

### clean checkoutだけではstrict Evidenceにしない

KJ Atlasは`.env`、`*.so`、`__pycache__`、`*.pyc`、`*.egg-info`等をGit管理外にできる。したがって、HEADが固定commitで通常の`git status`がcleanでも、working treeに存在するignored fileまで固定commit identityへ含まれるとは限らない。

```text
HEAD = pinned commit
  + normal Git clean
  != byte-complete runtime source identity
```

### strict Evidenceでは固定commit objectへ戻す

strict Evidenceでは、`export_kj_atlas_runtime_source.py`を使い、固定commit objectから追跡済みruntime surfaceだけをexportする。

対象は次の4要素である。

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

`verify_kj_atlas_runtime_source.py`は、固定blob / tree identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証する。

```text
source acquisition
  != source identity
```

checkoutから開始する場合も、strict入口はworking treeをそのまま実行sourceへしない。固定commit objectから一時verified bundleを作り、low-level harnessへ渡す。

## Pinned model artifact identity

固定modelは`qwen2.5:0.5b`で、期待full digestは次である。

`a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`

Ollama `v0.32.13` / `v0.32.14`のsourceでは、model listに現れるdigestはmodel manifest raw bytesのSHA-256を基礎にしている。

事前配置model storeを使う場合は`verify_runtime_version_exchange_model_store.py`で、runtime起動前に次を静的再検証する。

- 固定model manifest path
- manifest raw bytesのSHA-256
- manifestが参照するconfig / layer blobのdeclared size
- 各blobのactual SHA-256
- symlinkやstore外参照がないこと
- 検証結果の`--output`がmodel store内を書き換えないこと

この静的検証はactual Ollama API観測の代替ではない。A / Bのactual実行では、両runtimeの`/api/tags`から同じ期待full digestを改めて観測する。

```text
static model store verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

work-local model storeを使う場合は、必要に応じてartifactを取得した後、同じexpected full digestへ戻す。

## 実行経路

current standard pathは次である。

```text
fixed runtime archive planning / preparation
  ↓
fixed KJ Atlas source preparation
  ↓
side-effect-free preflight
  ↓
strict entrypoint
  ↓
low-level repository-local harness
  ↓
actual Ollama /api/tags
  ↓
actual A/B inference
  ↓
Evidence read-back
```

### Local preflight

`check_runtime_version_exchange_preflight.py`はruntime / model processを起動せず、artifactもdownloadしない。

主に次を診断する。

- Linux / amd64
- required command
- SOZA Git working tree / cleanliness
- KJ Atlas checkoutまたはverified bundleの入力条件
- verified bundleのGit object identity
- work / Evidence / model path境界
- 事前配置runtime archiveのofficial size / actual SHA-256
- 事前配置model storeのmanifest / blob identity
- local port availability
- work filesystemのfree bytes

free bytesは観測値であり、十分なdisk容量の証明にはしない。

```text
disk free-space observation
  != enough capacity proven
```

`--require-prepositioned-artifacts`ではruntime archiveとmodel storeの事前配置を要求できる。`--json`ではfixed artifact metadata、pinned source identity、`ready` / `blocked`、blocker ID、各checkを構造化して返す。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

### Strict entrypoint

strict Evidenceへ進む標準入口は`runtime/integration/run_runtime_version_exchange_strict.py`である。

このentrypointは次を担う。

1. checkout指定時は固定commit objectからverified runtime bundleをexportする。
2. bundle指定時は固定Git object identityを再検証する。
3. 事前配置model store指定時は、Ollama起動前にmanifest / blob bytesを静的検証する。
4. 元checkout / verified bundle / model storeを入力として保護し、Evidence / work directoryとの重なりを拒否する。
5. source / model / Evidence / workのidentity / safety optionをlow-level harnessへ迂回上書きできないようにする。
6. low-level harnessを`bash`経由で起動する。
7. harnessがEvidence directoryを作成した場合、source export provenanceとstatic model verificationを同じrun Evidenceへ保存する。

custom work directoryが必要な場合はstrict入口自身の`--work-dir`で指定する。

```text
strict entrypoint verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

### Low-level repository-local harness

actual実験本文は`runtime/integration/run_runtime_version_exchange.sh`に置く。strict Evidenceでは原則としてstrict入口から利用する。

low-level harnessは概ね次を行う。

1. Linux / amd64とSOZA source条件を確認する。
2. verified KJ Atlas runtime bundleを再検証する。
3. runtime A / B archiveを取得または事前配置pathから参照し、actual size / SHA-256を固定値と照合する。
4. actual binary versionを確認する。
5. A / Bで同じmodel storeを利用し、両方の`/api/tags` full digestを固定値へ一致させる。
6. 同じMethod inputをA / Bへ通し、actual inference countersとKJ Atlas resultを保存する。
7. A / Bのprompt SHA-256が同一であることを確認する。
8. live Go testでExact Binding、historical Application不変性、portable reconstruction、negative controlを確認する。
9. 成否にかかわらず、そこまで生成されたEvidenceをrun専用directoryへ保存する。

```text
repository-local harness
  = reproducible execution boundary
  != GitHub Actions required
  != specific runner required
```

## Acquisition boundary

runtime archiveはdownload / prepositionedの両経路を許可する。どちらもactual bytesの固定SHA-256へ戻す。

model storeもwork-local / prepositionedの両経路を許可する。prepositioned storeは静的identity検証を通し、actual runtimeでもfull digestを観測する。不足している事前配置storeをharnessから暗黙更新しない。

```text
acquisition / storage mode
  = Provenance

artifact identity
  = actual bytes / fixed digest

acquisition path
  != artifact identity
```

## Local execution safety

repository-local化に伴い、次を停止線とする。

- SOZAに未commit変更があれば開始しない。
- strict source bundleが固定Git object identityと一致しなければ開始しない。
- `--work-dir` / `--evidence-dir`は新しいpathだけを受け付ける。
- source、model store、Evidence、work directoryを相互に分離する。
- Evidenceをmodel store配下へ置き、read-only入力を変更できないようにする。
- fixed local port `11434` / `8001` / `8101`が使用中なら開始しない。
- health responseだけでなくharness自身が起動したPIDの生存を確認する。
- 事前配置runtime archiveはactual size / SHA-256を検査する。
- 事前配置model storeはstatic identityとactual `/api/tags` full digestの両方を検査する。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- Go live guardは必要pathを実行器から明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。

## Artifact guard / lightweight regression

Go側live guardは`SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1`のときだけactual source / runtime artifactを再確認する。

pure-Go controlでは少なくとも次を検査する。

- exact version token
- fixed artifact digest mismatch
- required live guard path
- Raw Bytes SHA-256 Exact Binding verification
- payload改変時の`verification_failed`
- Exact Bindingの決定性
- runtime version / runtime artifact / model artifact identity差によるBinding差

Python側は、archive preparation、source exporter / verifier、model store verifier、preflight、strict entrypoint、low-level harness interfaceをactual runtimeなしで個別検査できる。

2026-09-03には、strict entrypointのpath分離を依存module stub付きでローカル個別実行し、`10 tests / OK`、return code 0を確認した。これはactual runtime A/B実証の代替ではない。

```text
local helper test PASS
  != actual runtime A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## Required experiments

### E0 — strict source identity

PASS条件:

- fixed commit objectからruntime surfaceを再構成できる。
- ignored fileがexport bundleへ混入しない。
- runtime surface treeが固定値へ一致する。
- source tamper / unexpected top-level / symlink / executable bitを拒否する。
- A / B実行が同じverified runtime surfaceを使う。

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

- prepositioned storeを使う場合、static manifest / blob identityが固定条件に一致する。
- A / Bのactual `/api/tags` model digestが同一である。
- A / Bのactual model digestが固定full digestと一致する。
- model tagだけで同一性を推論しない。

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
- A / Bはそれぞれ異なるExact Bindingを持つ。
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
- Application A / Bを対応revisionへ解決できる。
- payload改変を拒否する。
- unknown revision digestを参照するnegative bundleを拒否する。

### E7 — no semantic promotion

runtime交換後もMethod outputをRecommendation / Decisionへ自動昇格しない。

### E8 — execution surface independence

PASS条件:

- actual実験本文がrepository同梱資産として残る。
- fixed identityがscript / guardへ明示される。
- checkout working treeをstrict Evidenceの実行sourceにしない。
- source / runtime / model artifactの取得経路を同じidentity検証へ戻せる。
- host / source / acquisition状況をEvidenceへ残せる。
- GitHub Actions、runner ID、取得経路をMethod / Realization identityに含めない。

### E9 — Evidence preservation

一つのrun専用Evidence directoryから、存在する範囲で次へ戻れることを要求する。

- execution ID
- SOZA commit
- KJ Atlas source identity / source export provenance
- static model store verification
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

過去のruntime交換workflow試作では、GitHub-hosted runnerが割り当て前に終了する状態を観測した。PR #70ではcurrent baselineからGitHub Actions workflowを撤去し、ISSUE-000069では検証内容と実行場所を分離する境界をResolvedとした。

Actions再導入やrunner復旧は本IssueのResolution条件ではない。

### Current execution environment observation

2026-09-03の現作業環境ではLinux / amd64、主要Python依存、Go等を利用でき、`/tmp`には約32GBのfree spaceを観測した。一方、この環境にはactual実証に必要な固定Ollama runtime archive / model artifactが配置されておらず、外部DNS経由の取得も利用できなかった。

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
- runtime artifact manifest / preparation helper
- KJ Atlas runtime source exporter / verifier
- Ollama model store static verifier
- side-effect-free local preflight
- strict runtime exchange entrypoint
- repository-local low-level runtime exchange harness
- source / model / Evidence / work path separation
- clean-tree / port / PID safety guard
- run-isolated Evidence directory
- download / prepositioned runtime archive経路
- work-local / prepositioned model store経路
- acquisition / storage mode Provenance
- official archive size early guard
- disk free-space observational diagnostic
- verified bundle用live Go guard / negative control

ただし、current harnessによるactual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していない。

## Current Evidence state

```text
fixed KJ Atlas source identity
  = verifier / exporter available

fixed runtime version / official size / official digest
  = statically verified

qwen2.5:0.5b expected model artifact identity
  = actual digest observed historically

prepositioned model store static verification
  = verifier available

Exact Realization Reference mapping
  = historical Scoped Executable Evidence available

preflight / strict entrypoint / low-level harness
  = implemented

strict entrypoint path boundary
  = 10 local tests PASS with stubbed dependencies

actual runtime A/B binary / digest / model / prompt / inference
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

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

1. fixed KJ Atlas commit objectから生成したverified runtime surfaceをA / B双方が利用し、runtime surface treeを固定値へ一致させる。
2. repository-local harnessが固定runtime A / Bのactual bytesを利用し、SHA-256を固定値へ一致させる。
3. A / Bのactual binary versionを確認する。
4. A / B双方のactual model digestが固定artifact identityに一致し、same prompt digestもactual executionで確認する。
5. 両runtimeでactual inferenceが成立する。
6. Application A / Bがsame logical / different Exact Realization revisionを保持する。
7. Application AのReference / Provenance / outputがB追加後も不変である。
8. Realization payload verification、portable reconstruction、unknown revision negative controlがPASSする。
9. Recommendation / Decisionへの自動昇格がない。
10. run専用Evidence directoryから実験identity、source identity、static model verification、取得状況、入力、A / B actual runtime digest、model Evidence、出力へ戻れる。
11. Requirement / Contract再照合と自然な日本語最終監査を行う。

archive size、static model verification、preflight ready、strict entrypoint verification、disk free-space、source export成功、GitHub Actions再導入、runtime/model artifactの実行時download可否は、それ単独ではResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revision交換でhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- Realization payloadとExact Bindingの不一致を検出できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを受理する。
- KJ Atlas sourceをpath名、clean status、HEAD commitだけで信用し、ignored runtime-affecting fileを実行へ混入できる。
- verified runtime surfaceのGit object identity不一致を受理する。
- source、model store、Evidence、work directoryを重ね、入力を実行副作用で変更できる。
- model manifest / blob bytesが固定identityと異なる事前配置storeを受理する。
- model tagが固定artifact identityと異なるartifactを指し、model交換が混入する。
- promptが交換軸へ混入する。
- 事前配置archiveをpath、file名、sizeだけで信用しSHA-256を省略できる。
- 事前配置model storeを暗黙に更新する。
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

ISSUE-000067 / 000068 / 000071、Cognitive Method Contract、Exact Binding、current KJ Atlas mapping、no-Actions baseline、repository-local runtime資産へ戻って本Issueを全文再監査した。

現在の標準経路を、artifact準備、source identity固定、preflight、strict entrypoint、low-level harness、actual API / inference、Evidence読み戻しの順に整理した。準備段階の成功を、まだ実行していないactual A / Bの成功へ読み替えない。

KJ Atlas sourceは固定commit objectからverified runtime surfaceへ戻す。事前配置model storeはmanifest raw bytesと参照blobを静的に検証する。どちらもactual execution identityを強くするための前段であり、runtime A / B成立そのものではない。

strict entrypointでは、元sourceとmodel storeを入力として保護し、Evidence / work directoryとの重なりを拒否する。これにより、検証対象を検証作業自身が変更する経路を避ける。

GitHub Actionsは引き続き完全停止している。actual Ollama `0.32.13` / `0.32.14`交換はNot Yet Verifiedであり、本IssueはOpenのままとする。

意味、規範強度、Resolution条件、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して再ドラフトした。
