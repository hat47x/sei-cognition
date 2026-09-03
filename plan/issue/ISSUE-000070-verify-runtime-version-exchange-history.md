# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

同じCognitive Method、同じKJ Atlas source、同じMethod input、同じactual model artifact、同じmodel promptを使い、Ollama runtime versionだけを交換したときに、SOZAが先行Method Applicationの履歴を失わず保持できるかを実証する。

runtime version差は別のlogical Method Realizationへ分けず、同じ実現機構に属するhistorical revisionとしてExact Bindingで区別する。

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
  != historical Application rewrite
```

## Product / Contract boundary

この実証は、model名やruntime versionをUniversal Semantic Contractへ追加するためのものではない。

- Method Definitionは「何を行うMethodか」を表す。
- Method Realizationは「どの実現機構で実行するか」を表す。
- 同じ実現機構のversion差はhistorical revisionとしてExact Bindingで固定する。
- Method Applicationは実行時のExact Referenceを保持する。
- runtime / model固有情報はProvenance / realization-local metadataとして保持する。
- source / runtime / model artifactの取得経路はProvenanceであり、artifact identityではない。
- Method outputをRecommendation / Decisionへ自動昇格しない。
- GitHub Actions、runner ID、workflow run IDをMethodの意味やruntime交換成立条件にしない。

GitHub Actionsはcurrent baselineで完全停止している。workflowの復元、過去runの再実行、runner監視は行わず、必要な検証はrepository-localなtest、checker、probeをローカルで個別に実行する。過去のActions Runはhistorical Evidenceとしてのみ保持する。

## Related work

ISSUE-000067ではMethod Definition / Realization / Applicationを履歴として再構成する境界を確認した。ISSUE-000068ではruntimeを固定してmodel artifactだけを交換し、先行ApplicationのRealization、Provenance、outputを保持できることをScoped Executable Evidenceとして確認した。

本Issueでは交換軸をさらに狭める。

```text
ISSUE-000068
  model artifactを交換
  runtimeは固定

ISSUE-000070
  model artifactを固定
  runtime versionだけを交換
```

ISSUE-000071は成果品質の評価境界を確立したIssueであり、human reviewやKJ-method outcome qualityがSatisfiedになったことを意味しない。本Issueでもexecution conformanceと成果品質を分離する。

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

model artifact digestはActual Model Artifact Exchange E3b Run `33670697154`でOllama `0.32.14`からactualに観測したidentityである。A / Bのdigestが互いに等しいだけでは成立とせず、両方がこの期待full digestへ一致することを要求する。

交換するruntime revisionは次の2つだけである。

- revision A: Ollama `0.32.13`
- revision B: Ollama `0.32.14`

## Pinned runtime artifacts

Linux / amd64用のOllama公式archiveを固定する。

| revision | asset | official size | fixed SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesである。

sizeはfile取り違えをSHA-256計算前に止める早期guardであり、artifact identityの正本ではない。identityはactual bytesのSHA-256で固定する。

固定metadataは`runtime/integration/runtime_version_exchange_artifacts.json`へ機械可読に保持する。`prepare_runtime_version_exchange_archives.py`はdownload / verify-only / prepositioned再利用を同じsize / SHA-256境界へ戻す。

Linux / amd64は本probeの実行条件であり、SOZA全体のplatform supportを限定する意味ではない。

## KJ Atlas source identity

通常のclean checkoutだけでは、ignored `.env`、binary extension、bytecode cache等まで固定commit identityへ含まれるとは限らない。

```text
HEAD = pinned commit
  + normal Git clean
  != byte-complete runtime source identity
```

strict Evidenceでは`export_kj_atlas_runtime_source.py`を使い、固定commit objectから次の追跡済みruntime surfaceだけをexportする。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

固定identity:

- source commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- parent backend tree: `7d71ac2b4d32bef90f3a481ade1b4c92ddddd084`
- minimal runtime surface tree: `208bea71eef4afed3ddfd3fabb36b0969d167a90`

`verify_kj_atlas_runtime_source.py`はblob / tree identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証する。

```text
source acquisition
  != source identity
```

checkoutから開始する場合も、strict入口はworking treeそのものを実行sourceへせず、固定commit objectからverified bundleを作る。

## Pinned model artifact identity

固定modelは`qwen2.5:0.5b`、期待full digestは次である。

`a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`

Ollama `v0.32.13` / `v0.32.14`では、model listに現れるdigestはmodel manifest raw bytesのSHA-256を基礎にする。

### 既存model storeを使う場合

`verify_runtime_version_exchange_model_store.py`で次を静的再検証する。

- 固定manifest path
- manifest raw bytesのSHA-256
- config / layer blobのdeclared size
- 全参照blobのactual SHA-256
- symlinkやstore外参照がないこと
- verifier outputがmodel storeを変更しないこと

### 新しいmodel storeを準備する場合

`prepare_runtime_version_exchange_model_store.py`はartifact manifestに固定した`registry.ollama.ai`のHTTPS endpointからmanifestと参照blobを取得する。

- targetは新しいpathだけを受け付ける。
- registry manifest raw SHA-256を固定model identityへ一致させる。
- 各blobをmanifestのsize / SHA-256へ一致させる。
- download中はstaging directoryを使う。
- 全検証を通った場合だけ完成directoryへ昇格する。
- 失敗時は未完成stagingを除去する。
- 完成storeは改めてstatic verifierへ通す。

strict入口では`--prepare-model-dir`を指定すると、この準備と再検証を行ってからlow-level harnessへ渡す。既存storeを指定する`--model-dir`とは排他的である。

```text
prepared model store PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

A / Bのactual実行では、両runtimeの`/api/tags`から同じ期待full digestを改めて観測する。

## Current execution path

標準経路は次である。

```text
fixed runtime archive preparation
  ↓
fixed KJ Atlas source preparation
  ↓
fixed model store verification | preparation
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
run-isolated Evidence preservation
  ↓
runner observation
  ↓
core mechanical Evidence verification
  ↓
saved preflight / source acquisition Provenance verification
  ↓
Requirement / Contract assessment + quality review
```

harnessのexit code 0、保存済みEvidenceの機械的な十分性、Provenanceの整合、Requirement / Contract再照合、成果品質評価は別の段階として扱う。

### Preflight

`check_runtime_version_exchange_preflight.py`はruntime / model processを起動せず、artifactもdownloadしない。

主に次を診断する。

- Linux / amd64
- required command
- SOZA Git working tree / cleanliness
- KJ Atlas checkoutまたはverified bundle identity
- work / Evidence / model path境界
- 事前配置runtime archiveのofficial size / actual SHA-256
- 事前配置model storeのmanifest / blob identity
- local port availability
- work filesystemのfree bytes

free bytesは観測値であり、十分なdisk容量の証明にはしない。

```text
preflight ready
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

`--require-prepositioned-artifacts`を使う場合、preflightはruntime A / B archiveと固定model storeが事前配置済みであることを要求する。このmodeはruntime / model artifactの取得方針を`prepositioned-only`へ絞るものであり、Python package解決を含む実行環境全体の完全offline動作を保証するものではない。

```text
prepositioned runtime / model artifacts
  != fully offline execution guaranteed
```

### Strict entrypoint

`run_runtime_version_exchange_strict.py`はstrict Evidenceの標準入口である。

責務:

1. checkout指定時は固定commit objectからverified runtime bundleをexportする。
2. bundle指定時は固定Git object identityを再検証する。
3. `--model-dir`指定時は既存storeを静的検証する。
4. `--prepare-model-dir`指定時は固定registryから新規storeを準備し、静的再検証する。
5. source、model store、Evidence、work directoryの重なりを拒否する。
6. identity / safety optionをlow-level harnessへ迂回上書きできないようにする。
7. low-level harnessを`bash`経由で起動する。
8. Evidence directoryが作成された場合、source export、model preparation、static model verificationを同じrun Evidenceへ保存する。

```text
strict entrypoint verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

### Low-level harness

actual実験本文は`run_runtime_version_exchange.sh`に置く。strict Evidenceでは原則としてstrict入口から利用する。

low-level harnessはverified KJ Atlas runtime bundleだけを実行sourceとして受け付け、actual runtime archive / binary version / `/api/tags` model digest / prompt digest / inference / Exact Binding / historical Application / portable reconstruction / negative controlを一続きに確認し、run専用Evidence directoryへ保存する。

### Post-run runner / mechanical verifier

actual実行時の標準入口は`run_runtime_version_exchange_with_verification.py`である。このrunnerはstrict入口を正本として呼び出し、source / model準備ロジックを重複実装しない。

runnerは次を行う。

1. strict入口へsource、model、work、Evidenceを明示的に渡す。
2. identity / safety optionを下位entrypointへ迂回上書きできないようにする。
3. actual処理へ進む前にside-effect-free preflightを実行する。
4. strict実行のstdout / stderrを一つのcombined logへ保存する。
5. exit code、combined log SHA-256 / bytes、source preparation、preflight resultをrunner observationへ記録する。
6. 成功したpreflight reportを`runtime-exchange-preflight.json`として同じrun Evidenceへ保存する。
7. Evidence directoryが生成された場合、成功・失敗にかかわらずpost-run verifierを実行する。
8. verification reportはEvidence directoryの外へ保存し、検証対象そのものを書き換えない。

post-run verificationは二層に分ける。

1. `verify_runtime_version_exchange_evidence.py`
   - 固定source / runtime / model / Method input / prompt
   - actual inference counter
   - KJ Atlas result境界
   - runner exit code
   - completion marker
   - combined log digest
   - `qualityJudgement=not_evaluated`
   をcore mechanical Evidenceとして再確認する。
2. `verify_runtime_version_exchange_provenance.py`
   - 上記core verifierを先に実行する。
   - 保存済みpreflightが`ready`かつ`blockers=[]`であることを再確認する。
   - preflightの固定runtime / model / KJ Atlas source identityをcurrent固定値へ戻す。
   - runner observationの`preflightResult`と保存済みpreflightを一致させる。
   - `sourcePreparation`を`verified-runtime-bundle`または`checkout-to-verified-runtime-bundle`へ限定する。
   - checkout起点では`runtime-exchange-source-export.json`を必須とし、固定commit objectからのexport結果をactual source identity fileへ一致させる。
   - verified bundle直入力ではcheckout source-export fileの混在を拒否する。

全機械条件とProvenance条件を満たした場合だけ`ready-to-review`、不足や不一致がある場合は`not-sufficient`とblocker IDを返す。

```text
strict harness exit code 0
  != core mechanical Evidence verification PASS

core mechanical Evidence verification PASS
  + saved preflight / source acquisition Provenance verification PASS
  = 保存済みrunが固定された機械条件と取得履歴の整合を満たし、レビュー可能である
  != Requirement / Contract assessment complete
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != ISSUE-000070 Resolved
```

## Acquisition boundary

runtime archiveはdownload / prepositionedを許可し、どちらもactual bytesの固定SHA-256へ戻す。

model storeは次の3経路を許可する。

- 既存prepositioned storeを静的検証して使う。
- strict入口から固定registryを使って新しいstoreを準備する。
- low-level harnessのwork-local storeで必要artifactを取得する。

どの経路でも最終的にfixed model identityへ戻す。取得経路はProvenanceでありRealization identityではない。

`--require-prepositioned-artifacts`は、このうちruntime archiveとmodel artifactについてnetwork fallbackを許さず、事前配置済み入力だけを使うためのacquisition policyである。Python package indexへの到達性など、artifact以外のhost実行条件までofflineに固定する意味は持たせない。

```text
acquisition / storage mode
  = Provenance

artifact identity
  = actual bytes / fixed digest

acquisition path
  != artifact identity

prepositioned-only artifact policy
  != fully offline execution guarantee
```

## Local execution safety

次を停止線とする。

- SOZAに未commit変更があれば開始しない。
- verified source bundleが固定Git object identityと一致しなければ開始しない。
- work / Evidence / prepared model targetは新しいpathだけを受け付ける。
- source、model store、Evidence、work directoryを相互に分離する。
- mechanical verification outputもsource、model store、Evidence、work directoryから分離する。
- Evidenceをmodel store配下へ置き、read-only入力を変更できないようにする。
- fixed local port `11434` / `8001` / `8101`が使用中なら開始しない。
- harness自身が起動したPIDを確認する。
- 事前配置runtime archiveはactual size / SHA-256を検査する。
- model storeはstatic identityとactual `/api/tags` full digestを区別して確認する。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- Go live guardは必要pathを明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。

## Local lightweight regression

actual runtimeを起動せず、次の境界を個別に検査できる。

- runtime archive preparation
- model store preparation
- model store static verification
- source exporter / verifier
- preflight
- strict entrypoint
- post-run runner / core mechanical Evidence verifier / Provenance verifier
- low-level harness interface
- Exact Binding / historical reconstructionのpure-Go control

2026-09-03にはstrict entrypointのpath分離について、依存moduleをstub化したローカル個別実行で`10 tests / OK`、return code 0を確認した。

また、post-run Evidence検証について、current artifact manifestと同じ構造を使ったsynthetic回帰でcore verifier 12件、runner 7件の計`19 tests / OK`を確認した。これはactual Ollama A / B実行ではない。

PR #114で追加したpreflight / source acquisition Provenance verifierとそのfocused regressionは実装済みである。ただしcurrent ChatGPT実行環境からprivate repository branchをローカル実行環境へmaterializeできないため、この追加suiteはactualには未実行である。未実行をPASSやfailureへ読み替えない。

```text
local helper test PASS
  != actual runtime A/B inference PASS

new helper test not executed
  != helper test failure
  != helper test PASS
```

## Required experiments

### E0 — strict source identity

- fixed commit objectからruntime surfaceを再構成できる。
- ignored fileがbundleへ混入しない。
- runtime surface treeが固定値へ一致する。
- source tamper / unexpected top-level / symlink / executable bitを拒否する。
- A / Bが同じverified runtime surfaceを使う。

### E1 — runtime artifact identity

- Aが`0.32.13`としてactual起動する。
- Bが`0.32.14`としてactual起動する。
- A / Bのactual archive SHA-256が固定値と一致する。
- acquisition経路にかかわらず同じidentity検査へ戻る。

### E2 — same pinned model artifact

- prepositioned / prepared storeはstatic manifest / blob identityが固定条件に一致する。
- A / Bのactual `/api/tags` digestが同一である。
- A / Bのactual digestが固定full digestと一致する。
- model tagだけで同一性を推論しない。

### E3 — same prompt / actual inference

- A / Bに同じprompt SHA-256が記録される。
- `ollama_done = true`。
- `prompt_eval_count > 0`。
- `eval_count > 0`。
- KJ Atlas response boundaryが両resultを受理する。

生成文そのものの一致は要求しない。

### E4 — same logical Realization / different Exact Binding

- A / Bは同じlogical Realizationを持つ。
- A / Bは異なるExact Bindingを持つ。
- 同じidentityから同じBindingを再構成できる。
- runtime / model artifact identityを変えるとBindingも変わる。
- acquisition modeだけの差を別logical Realizationへしない。

### E5 — historical Application immutability

- Application AのExact Reference / Provenance / outputがB追加後も変わらない。
- Application Bはrevision BのExact Referenceを保持する。
- 両Applicationは同じMethod Definitionを指す。
- 両Provenanceは同じ固定model artifactを指す。

### E6 — portable historical reconstruction

- Realization payloadをRaw Bytes SHA-256 Profileで検証できる。
- `semanticruntime.LoadInterchange`がExact Binding検証を通る。
- Application A / Bを対応revisionへ解決できる。
- payload改変とunknown revision digestを拒否する。

### E7 — no semantic promotion

runtime交換後もMethod outputをRecommendation / Decisionへ自動昇格しない。

### E8 — execution surface independence

- actual実験本文がrepository同梱資産として残る。
- source / runtime / model取得経路を同じidentity検証へ戻せる。
- GitHub Actions、runner ID、取得経路をMethod / Realization identityに含めない。

### E9 — Evidence preservation

run専用Evidence directoryから、存在する範囲で次へ戻れることを要求する。

- execution ID
- SOZA commit
- KJ Atlas source identity / source export provenance
- model store preparation / static verification
- successful preflight report
- runner source preparation / preflight result
- host OS / architecture
- runtime A / B version / digest / acquisition mode
- model expected / actual digest / storage mode
- fixed Method request
- A / B inference Evidence / KJ Atlas result
- process log
- runner observation / combined output log
- `qualityJudgement = not_evaluated`

```text
Evidence preserved
  != mechanical Evidence + Provenance verification PASS
  != runtime exchange PASS
  != output quality satisfied
```

### E10 — independent mechanical Evidence / Provenance verification

- verifierはrun専用Evidence directoryをread-only入力として扱う。
- verification reportをEvidence directoryの外へ保存する。
- core verifierでfixed source / runtime / model / Method input / promptを再確認する。
- `ollama_done=true`、positive eval counter、KJ Atlas result境界を再確認する。
- runner exit code、completion marker、combined output SHA-256 / bytesを再確認する。
- Provenance verifierで保存済みpreflightの`ready`、固定artifact / source identityを再確認する。
- runnerの`preflightResult`と保存済みpreflightを一致させる。
- source preparation種別を限定し、checkout起点ではsource export provenanceをactual source identityへ一致させる。
- missing / drift / symlink / non-strict source / quality promotion / Provenance不整合を`not-sufficient`として拒否する。
- 全機械条件とProvenance条件を満たした場合だけ`ready-to-review`を返す。

## Existing Evidence

Actual Model Artifact Exchange E3b Run `33670697154`はactualに完走し、model full digest、prompt digest、historical Application保持を確認した。このEvidenceは今回固定するmodel artifact identityを支えるが、runtime version交換そのもののEvidenceではない。

過去のruntime交換workflow試作ではGitHub-hosted runnerの割当前終了を観測した。current baselineではGitHub Actionsを撤去済みであり、runner復旧やActions再導入は本IssueのResolution条件ではない。

2026-09-03の現作業環境ではLinux / amd64、主要Python依存、Go、約32GBの`/tmp` free spaceを観測した。一方、actual実証に必要な固定Ollama runtime / model artifactをこの環境へ取得する外部DNS経路は利用できなかった。これは環境固有の観測でありSOZAのProduct failureではない。

## Current implementation state

current developには次がある。

- Exact Realization Reference / Exact Binding
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- fixed runtime artifact manifest / preparation helper
- KJ Atlas source exporter / verifier
- model store preparation helper / static verifier
- side-effect-free preflight
- strict runtime exchange entrypoint
- post-run verified runner
- core mechanical Evidence verifier
- saved preflight / source acquisition Provenance verifier
- repository-local low-level harness
- source / model / Evidence / work / verification output path separation
- clean-tree / port / PID safety guard
- run-isolated Evidence directory
- download / prepositioned runtime archive経路
- prepositioned / prepared / work-local model store経路
- prepositioned-only runtime / model artifact acquisition policy
- acquisition / storage / source preparation Provenance
- archive size early guard / disk free-space observational diagnostic
- live Go guard / negative control

actual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していない。

## Current Evidence state

```text
fixed source identity
  = verifier / exporter available

fixed runtime metadata
  = statically verified

fixed model expected digest
  = actual historical observation available

model store preparation / static verification
  = helpers available

preflight / strict entrypoint / low-level harness
  = implemented

post-run runner / core mechanical Evidence verifier
  = implemented; synthetic 19-test regression available

saved preflight / source acquisition Provenance verifier
  = implemented; focused regression not yet executed in current environment

actual runtime A/B binary / archive digest / model / prompt / inference
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

## Requirement / Contract assessment

現時点では新しいStable Requirement / Acceptance Scenario / Universal Contract fieldを追加しない。actual実証後に少なくともREQ-0001、REQ-0004、REQ-0021、SCN-0005、SCN-0015へ再照合する。既存Requirement / Contractで十分に表せる場合はNo Changeとする。

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
10. run専用Evidence directoryから実験identity、source identity / source preparation、model preparation / static verification、preflight、取得状況、入力、A / B actual runtime digest、model Evidence、出力、runner observation / combined output logへ戻れる。
11. 保存済みEvidenceをcore mechanical verifierとProvenance verifierへ通し、固定された機械条件と保存済み取得履歴について`ready-to-review`を得る。
12. Requirement / Contract再照合と自然な日本語最終監査を行う。

archive preparation、model store preparation、static model verification、preflight ready、strict entrypoint verification、mechanical / Provenance verifierのsynthetic test、disk free-space、source export成功、GitHub Actions再導入、artifactの実行時download可否は、それ単独ではResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- historical ApplicationのExact Referenceがruntime交換で失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- payload / Binding不一致、unknown revision digestを受理する。
- ignored runtime-affecting fileをstrict sourceへ混入できる。
- verified runtime surfaceのGit object identity不一致を受理する。
- source、model store、Evidence、work、verification outputを重ねて入力やEvidenceを検証副作用で変更できる。
- model manifest / blob bytesが固定identityと異なるstoreを受理する。
- fixed registry以外からprepared storeを暗黙に構成する。
- model tagだけでartifact identityを推論する。
- promptが交換軸へ混入する。
- archiveをpath、file名、sizeだけで信用してSHA-256を省略する。
- acquisition modeだけの違いを別Realization identityへする。
- 別processのhealth responseを今回のactual実行と誤認する。
- 既存work / Evidence directoryを上書き・混在できる。
- live guardが暗黙pathへfallbackする。
- runner log改変、completion marker欠落、missing Evidence、identity driftをcore mechanical verifierが見逃す。
- 保存済みpreflightのblocker、fixed artifact drift、source identity driftをProvenance verifierが見逃す。
- runnerの`preflightResult`と保存済みpreflightの不一致を受理する。
- checkout起点なのにsource export provenanceを欠く、またはverified bundle直入力へcheckout source exportを混在させても受理する。
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

## 自然な日本語レビュー

ISSUE-000067 / 000068 / 000071、Cognitive Method Contract、Exact Binding、current KJ Atlas mapping、no-Actions baseline、repository-local runtime資産へ戻って全文を再監査した。

現在の実行経路を、runtime artifact準備、source identity固定、model store検証または新規準備、preflight、strict entrypoint、low-level harness、actual API / inference、run専用Evidence保存、runner observation、core mechanical Evidence verification、保存済みpreflight / source acquisition Provenance verification、Requirement / Contract再照合の順に整理した。

post-run検証は一つの大きな判定へ混ぜず、core execution Evidenceと実行前後のProvenanceを二層に分けた。新しいProvenance verifierは既存core verifierを先に実行するため、actual inference、runtime / model identity、runner log等の既存条件を弱めない。preflightの`ready`、runnerが記録したsource preparation、checkout起点のsource export履歴を追加で再確認しても、それ自体を成果品質やIssue Resolutionへ昇格させない。

`--require-prepositioned-artifacts`も、完全offline実行を意味する名称として扱わない。runtime A / B archiveとmodel artifactの取得経路をprepositioned-onlyへ限定するacquisition policyであり、Python package解決やhost環境までnetwork-freeであることの証明ではない。

model store準備経路は、取得方法を増やすためのものでありartifact identityを弱めるものではない。registryから取得したmanifest / blobは固定digestへ戻し、完成storeをstatic verifierへ再度通す。それでもactual `/api/tags`観測とA / B inferenceは別に必要である。

GitHub Actionsは完全停止を維持する。actual Ollama `0.32.13` / `0.32.14`交換はNot Yet Verifiedであり、本IssueはOpenのままとする。

意味、規範強度、Resolution条件、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して再ドラフトした。