# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-04

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
- parent backend tree: `7d71ac2b4d32bef90f3a481ade1b4c92ddddd084`
- minimal runtime surface tree: `208bea71eef4afed3ddfd3fabb36b0969d167a90`
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

固定metadataは`runtime/integration/runtime_version_exchange_artifacts.json`へ機械可読に保持する。manifest loaderはruntime名、version、Linux / amd64 platform、size、SHA-256、asset名に加え、取得URLが`github.com/ollama/ollama`の対応versionの公式Release assetと一致することも検証する。

`prepare_runtime_version_exchange_archives.py`はdownload / verify-only / prepositioned再利用を同じsize / SHA-256境界へ戻す。準備先はSOZA repository外とし、output directory、archive target、`.part`に関するsymlinkや不正な既存pathを実際の大容量download前に拒否する。

```text
official acquisition origin
  = acquisition boundary
  != artifact identity

artifact identity
  = actual bytes / fixed SHA-256
```

Linux / amd64は本probeの実行条件であり、SOZA全体のplatform supportを限定する意味ではない。

## KJ Atlas source identity

通常のworking treeは、固定commit objectを保持しているrepositoryとして利用できる。一方、ignored `.env`、binary extension、bytecode cache等まで含めると、working treeそのものをbyte-completeなruntime source identityとはみなせない。

```text
pinned commit object available
  = fixed sourceを再構成できる

working tree path
  != strict runtime source identity
```

strict Evidenceでは`export_kj_atlas_runtime_source.py`を使い、固定commit objectから次の追跡済みruntime surfaceだけをexportする。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

`verify_kj_atlas_runtime_source.py`はblob / tree identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証する。verifierの結果fileは入力bundleの外へ出し、検証処理自身がsourceを変更しない。exporterのidentity出力もcheckoutと完成bundleから分離する。

```text
source acquisition
  != source identity
```

checkoutから開始する場合、verified runnerまたはstrict入口はcheckoutを固定commit objectの取得元として扱い、working treeそのものをlow-level harnessへ渡さない。actual runtime sourceは固定commit objectから生成し、再検証したverified bundleである。

`run_runtime_version_exchange.sh`はverified backend bundle専用とし、direct checkoutや暗黙の`_external/kj-atlas` fallbackを受け付けない。

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
fixed runtime archive preparation outside SOZA repository
  ↓
fixed KJ Atlas commit object available | verified source bundle
  ↓
existing model store verification | prepared model target
  ↓
verified runner
  ↓
side-effect-free preflight
  ↓ ready only
strict entrypoint
  ↓
verified-bundle-only low-level harness
  ↓
actual Ollama /api/tags
  ↓
actual A/B inference
  ↓
run-isolated Evidence preservation
  ↓
runner observation
  ↓
Evidence + Provenance verification
  ↓
Requirement / Contract assessment + quality review
```

artifact準備、focused local regression、preflight、strict実行、Evidence + Provenanceの機械検証、Requirement / Contract再照合、成果品質評価は別の段階として扱う。

```text
failure Evidence preserved
  != runtime exchange PASS

focused local checks PASS
  != actual runtime A/B inference PASS
```

### Preflight

`check_runtime_version_exchange_preflight.py`はruntime / model processを起動せず、artifactもdownloadしない。

主に次を診断する。

- Linux / amd64
- required command
- SOZA Git working tree / cleanliness
- KJ Atlas固定commit objectの取得可能性、またはverified bundle identity
- work / Evidence / runtime archive / model path境界
- 事前配置runtime archiveのsource分離、symlink、official size / actual SHA-256
- 事前配置model storeのsourceとの双方向包含、manifest / blob identity
- local port availability
- work filesystemのfree bytes

checkoutの現在HEADやignored fileはstrict runtime source identityの判定には使わない。checkoutは固定commit objectを取得できるrepositoryであることを確認する。

事前配置runtime archiveはsource tree配下やsymlinkをsize / SHA-256計算前に拒否する。model storeはsource配下へ置けないだけでなく、model store自身がSOZAまたはKJ Atlas sourceを親directoryとして包含する配置も拒否する。これはstrict入口のpath overlap停止線と同じ意味である。

free bytesは観測値であり、十分なdisk容量の証明にはしない。

```text
preflight ready
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

#### Structured blocked preflight

verified runner内のpreflightが構造化された`blocked`結果を返した場合、strict入口、model preparation、runtime取得を開始しない。

blocked判定後にrun専用Evidence directoryを作成し、少なくとも次を保存する。

- `runtime-exchange-preflight.json`
- `runtime-exchange-preflight-observation.json`
- Evidence + Provenance verification report（Evidence directoryの外）

preflight observationにはpreflight exit code、blocker、`strictStarted=false`、`qualityJudgement=not_evaluated`を記録する。runnerはnon-zeroのまま終了する。

JSON自体を解釈できない等、構造化preflightとして扱えない異常ではEvidenceを推測で作らず、通常エラーとして停止する。

```text
blocked preflight Evidence preserved
  != strict execution started
  != runtime exchange PASS
```

### Strict entrypoint

`run_runtime_version_exchange_strict.py`はstrict Evidenceの標準入口である。

責務:

1. checkout指定時は固定commit objectからverified runtime bundleをexportする。
2. bundle指定時は固定Git object identityを再検証する。
3. 事前配置runtime archiveを指定した場合はsymlink・不存在・SOZA/sourceとのpath overlapをharness起動前に拒否する。
4. `--model-dir`指定時は既存storeを静的検証する。
5. `--prepare-model-dir`指定時は固定registryから新規storeを準備し、静的再検証する。
6. source、model store、Evidence、work directoryの双方向の重なりを拒否する。
7. identity / safety optionをlow-level harnessへ迂回上書きできないようにする。
8. verified bundleだけをlow-level harnessへ渡す。
9. Evidence directoryが作成された範囲で、source export、model preparation、static model verificationを同じrun Evidenceへ保存する。

```text
strict entrypoint verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

### Low-level harness

actual実験本文は`run_runtime_version_exchange.sh`に置く。low-level harnessはverified KJ Atlas backend bundleを必須とし、checkoutを直接実行sourceにはしない。

actual runtime archive / binary version / `/api/tags` model digest / prompt digest / inference / Exact Binding / historical Application / portable reconstruction / negative controlを一続きに確認し、run専用Evidence directoryへ保存する。

標準Evidenceではlow-level harnessを直接呼ばず、preflightとstrict入口を含むverified runnerから利用する。

### Verified runner / failure Evidence

actual実行時の標準入口は`run_runtime_version_exchange_with_verification.py`である。source / model準備ロジックはstrict入口を正本とし、runner側で重複実装しない。

runnerは次を行う。

1. side-effect-free preflightを実行する。
2. preflight `ready`の場合だけstrict入口を起動する。
3. strict実行のstdout / stderrをcombined logへ集約する。
4. exit code、combined log SHA-256 / bytes、source preparation、preflight resultをrunner observationへ記録する。
5. strict processが失敗し、Evidence directoryがまだ無い場合は、process終了後に新しいEvidence directoryを作成してrunner logとpreflightを保存する。
6. strict processがexit code 0なのにEvidence directoryが無い場合は成功扱いせず拒否する。
7. 保存できたrunについてEvidence + Provenance verifierを実行する。
8. verification reportはEvidence directoryの外へ保存する。

strict入口またはlow-level harnessがEvidence directoryを作成した場合、runner observationには`evidenceDirectoryCreatedBy=strict-entrypoint`を記録する。strictがEvidence作成前に失敗し、verified runnerが失敗後にdirectoryを作った場合は`evidenceDirectoryCreatedBy=verified-runner-after-failure`を記録する。

```text
strict process exit 0
  + Evidence directory missing
  = reject

strict failure Evidence preserved
  != strict execution PASS
```

失敗runへverifierを実行しても元のstrict non-zero exit codeは保持する。

### Evidence + Provenance verification

保存済みrunの標準verifierは`verify_runtime_version_exchange_provenance.py`である。

このverifierは、`verify_runtime_version_exchange_evidence.py`によるcore execution Evidence検証に加え、次を再検証する。

- 保存済みpreflightが`ready` / `blockers=[]`であること。
- preflightのfixed artifact条件がcurrent artifact manifestと一致すること。
- preflightのpinned source identityがcurrent固定値と一致すること。
- checkout起点では、fixed commit objectからのsource export Provenanceがactual source identityと一致すること。
- verified bundle直入力では、checkout source export fileが混入していないこと。
- complete runのEvidence directoryがstrict入口側で作成されたこと。

Evidence directory自身と必須Evidence fileのsymlinkも拒否する。core verifierは、固定source / runtime / model / Method input / prompt、actual inference counter、KJ Atlas result境界、runner exit code、completion marker、combined log digest、`qualityJudgement=not_evaluated`を再確認する。

全機械条件とProvenance条件を満たすcomplete runだけが`ready-to-review`になり得る。blocked preflightや途中失敗のpartial Evidenceは、保存されていても`not-sufficient`である。

```text
Evidence + Provenance verification ready-to-review
  = 保存済みrunが固定された機械条件とProvenance条件を満たし、レビュー可能である
  != Requirement / Contract assessment complete
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != ISSUE-000070 Resolved
```

## Acquisition boundary

runtime archiveはdownload / prepositionedを許可し、どちらもactual bytesの固定SHA-256へ戻す。新規downloadの入口はmanifestで対応versionのOllama公式GitHub Release assetへ固定する。準備先はSOZA repository外とし、配置pathをartifact identityの代わりにはしない。

model storeは次の3経路を許可する。

- 既存prepositioned storeを静的検証して使う。
- strict入口から固定registryを使って新しいstoreを準備する。
- low-level harnessのwork-local storeで必要artifactを取得する。

どの経路でも最終的にfixed model identityへ戻す。取得経路はProvenanceでありRealization identityではない。

```text
acquisition / storage mode
  = Provenance

artifact identity
  = actual bytes / fixed digest

acquisition path
  != artifact identity
```

## Local execution safety

次を停止線とする。

- SOZAに未commit変更があればactual harnessを開始しない。
- KJ Atlas sourceはfixed commit objectからverified bundleへ再構成するか、既存verified bundleを再検証する。
- low-level harnessへworking treeを直接渡さない。
- runtime archiveの準備先をSOZA repository配下へ置かない。
- 事前配置runtime archiveはsource配下とsymlinkをpreflight / strict入口で拒否する。
- work / Evidence / prepared model target / verification outputは新しいpathだけを受け付ける。
- source、model store、Evidence、work、verification outputを相互に分離する。
- model storeとSOZA/KJ Atlas sourceの双方向包含を拒否する。
- Evidenceをmodel store配下へ置き、read-only入力を変更できないようにする。
- source/model verifierの結果fileを入力資産内部へ書かない。
- fixed local port `11434` / `8001` / `8101`が使用中ならactual processを開始しない。
- harness自身が起動したPIDを確認する。
- 事前配置runtime archiveはactual size / SHA-256を検査する。
- model storeはstatic identityとactual `/api/tags` full digestを区別して確認する。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- exit code 0でもEvidence directoryが欠落していれば成功扱いしない。
- Go live guardは必要pathを明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。

## Local lightweight regression

actual runtimeを起動しないrepository-local regressionの標準入口は`run_runtime_version_exchange_local_checks.py`である。

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py
```

必要に応じて`--stop-on-failure`、`--list`、`--only TEST_FILE`を利用できる。runnerは実行対象を明示的なallowlistで管理し、runtime version exchangeに関係する候補testが増えたのに未登録のままになった場合も検出する。親shellのlive実行用環境変数はfocused testへ暗黙継承しない。

主な対象は次である。

- runtime / source / modelの固定identity consistency
- runtime archive preparation
- model store preparation / static verification
- source exporter / verifier
- preflight
- strict entrypoint
- blocked preflight Evidence preservation
- verified runner failure Evidence preservation
- core Evidence verifier
- Provenance verifier
- low-level harness interface
- Exact Binding / historical reconstructionのpure-Go control

focused runnerの対象には、manifest、preflight、low-level harness間でruntime version / digest / official size / Linux-amd64 platform / official Release URL等の固定条件が漂流していないことを確認するidentity consistency testも含む。

```text
focused local checks PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

本セッションではGitHub raw sourceを現在の実行containerへ取得する経路が利用できず、focused runnerの全testを実ファイルで一括実行した新しい結果は得ていない。これはactual runtime交換のProduct failureとは扱わず、実行済みと推定もしない。

## Required experiments

### E0 — strict source identity

- fixed commit objectからruntime surfaceを再構成できる。
- ignored fileがbundleへ混入しない。
- runtime surface treeが固定値へ一致する。
- source tamper / unexpected top-level / symlink / executable bitを拒否する。
- A / Bが同じverified runtime surfaceを使う。
- low-level harnessへworking treeを直接渡す経路がない。

### E1 — runtime artifact identity

- Aが`0.32.13`としてactual起動する。
- Bが`0.32.14`としてactual起動する。
- A / Bのactual archive SHA-256が固定値と一致する。
- acquisition経路にかかわらず同じidentity検査へ戻る。
- repository-local固定条件がofficial size / Linux-amd64 platform / official Release originについて漂流していない。

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
- checkoutはfixed commit objectの取得元に限定し、working treeをstrict runtime sourceへしない。
- low-level harnessはverified bundleだけを受け付ける。
- repository-local focused regressionがGitHub Actionsなしで実行可能な入口として残る。
- GitHub Actions、runner ID、取得経路をMethod / Realization identityに含めない。

### E9 — Evidence preservation

runが停止した地点に応じて、存在する範囲のEvidenceを失わない。

preflightでblockedした場合:

- structured preflight report
- preflight observation
- blocker / exit code
- `strictStarted=false`

strict開始後に失敗した場合:

- successful preflight report
- runner combined output log
- runner exit code / log SHA-256 / bytes
- source preparation mode
- その時点までstrict / low-level harnessが生成済みのEvidence

complete runではさらに次へ戻れることを要求する。

- execution ID
- SOZA commit
- KJ Atlas source identity / source export Provenance
- model store preparation / static verification
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
  != Evidence + Provenance verification PASS
  != runtime exchange PASS
  != output quality satisfied
```

### E10 — independent Evidence + Provenance verification

- verifierはrun専用Evidence directoryをread-only入力として扱う。
- Evidence directory自身と必須Evidence fileのsymlinkを拒否する。
- verification reportをEvidence directoryの外へ保存する。
- core verifierがfixed source / runtime / model / Method input / promptを再確認する。
- core verifierがactual inference counter、KJ Atlas result境界、runner completion / log digestを再確認する。
- Provenance verifierがsaved preflightとcurrent fixed artifact条件を再照合する。
- checkout起点のsource export Provenanceをactual source identityへ照合する。
- complete runではEvidence directory作成主体がstrict入口であることを確認する。
- missing / drift / symlink / non-strict source / quality promotionを`not-sufficient`として拒否する。
- blocked preflightやpartial failure Evidenceを`ready-to-review`へ昇格しない。
- complete runの全条件を満たした場合だけ`ready-to-review`を返す。

## Existing Evidence

Actual Model Artifact Exchange E3b Run `33670697154`はactualに完走し、model full digest、prompt digest、historical Application保持を確認した。このEvidenceは今回固定するmodel artifact identityを支えるが、runtime version交換そのもののEvidenceではない。

過去のruntime交換workflow試作ではGitHub-hosted runnerの割当前終了を観測した。current baselineではGitHub Actionsを撤去済みであり、runner復旧やActions再導入は本IssueのResolution条件ではない。

2026-09-03から2026-09-04にかけての現作業環境ではLinux / amd64、主要Python依存、Go、約30GB前後のローカル空き容量を観測した。一方、actual実証に必要な固定Ollama runtime / model artifactをこの実行containerへ取得する通常の外部DNS / raw download経路は利用できなかった。historical Actions Run `33670697154`にも再利用可能なworkflow artifactは残っていなかった。これらは環境固有の観測でありSOZAのProduct failureではない。

## Current implementation state

current developには次がある。

- Exact Realization Reference / Exact Binding
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- fixed runtime artifact manifest / preparation helper
- runtime archive official origin / platform / size / digest validation
- runtime archive repository外 preparation / symlink guard
- KJ Atlas source exporter / verifier
- source verifier / exporter result-output separation
- model store preparation helper / static verifier
- side-effect-free preflight
- preflight archive source/symlink guard
- preflight / strict model-source双方向overlap guard
- strict runtime exchange entrypoint
- verified-bundle-only low-level harness
- verified runner
- blocked preflight Evidence preservation
- strict失敗時のrunner Evidence preservation
- exit code 0 / Evidence欠落の拒否
- core Evidence verifier
- preflight / source acquisitionまで含むProvenance verifier
- Evidence directory / required Evidence file symlink guard
- source / runtime archive / model / Evidence / work / verification output path separation
- clean-tree / port / PID safety guard
- run-isolated Evidence directory
- download / prepositioned runtime archive経路
- prepositioned / prepared / work-local model store経路
- acquisition / storage mode Provenance
- archive size early guard / disk free-space observational diagnostic
- runtime/source/model identity consistency regression
- focused local check runner / allowlist drift detection
- live Go guard / negative control

actual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していない。

## Current Evidence state

```text
fixed source identity
  = verifier / exporter available

fixed runtime metadata / acquisition boundary
  = statically verified by repository-local definitions and tests

fixed model expected digest
  = actual historical observation available

model store preparation / static verification
  = helpers available

preflight / strict entrypoint / verified-bundle-only low-level harness
  = implemented

focused local check runner
  = implemented; new full run in this session not observed

failure Evidence preservation
  = structured preflight blocked / strict failure paths implemented

core Evidence + Provenance verification
  = implemented

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
10. complete runの専用Evidence directoryから実験identity、source identity / Provenance、model preparation / static verification、取得状況、入力、A / B actual runtime digest、model Evidence、出力、runner observation / combined output logへ戻れる。
11. complete runの保存済みEvidenceを独立Evidence + Provenance verifierへ通し、固定された機械条件とProvenance条件について`ready-to-review`を得る。
12. Requirement / Contract再照合と自然な日本語最終監査を行う。

archive preparation、model store preparation、static model verification、preflight ready、failure Evidence保存、strict entrypoint verification、focused local checks、helper / synthetic test、disk free-space、source export成功、GitHub Actions再導入、artifactの実行時download可否は、それ単独ではResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- historical ApplicationのExact Referenceがruntime交換で失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- payload / Binding不一致、unknown revision digestを受理する。
- working treeやignored runtime-affecting fileをstrict sourceへ直接混入できる。
- low-level harnessがdirect checkoutへfallbackできる。
- verified runtime surfaceのGit object identity不一致を受理する。
- source、model store、Evidence、work、verification outputを重ねて入力やEvidenceを検証副作用で変更できる。
- runtime archive準備先をSOZA repository配下へ置ける。
- 事前配置runtime archiveのsource配下配置やsymlinkをpreflight / strict入口で受理する。
- runtime archive manifestが非公式取得URL、platform drift、invalid size / digestを受理する。
- preflightがstrict入口で必ず拒否されるmodel/source overlapを見逃す。
- model manifest / blob bytesが固定identityと異なるstoreを受理する。
- fixed registry以外からprepared storeを暗黙に構成する。
- model tagだけでartifact identityを推論する。
- promptが交換軸へ混入する。
- archiveをpath、file名、sizeだけで信用してSHA-256を省略する。
- acquisition modeだけの違いを別Realization identityへする。
- 別processのhealth responseを今回のactual実行と誤認する。
- 既存work / Evidence directoryを上書き・混在できる。
- strict processがexit code 0でもEvidence欠落を成功扱いする。
- structured blocked preflightやstrict failureの診断を保存できず、失敗地点を追えない。
- partial failure Evidenceをcomplete runとして`ready-to-review`へ昇格する。
- Evidence directoryや必須Evidence fileのsymlinkを標準verifierが受理する。
- saved preflight / source acquisition Provenanceのdriftを標準verifierが見逃す。
- runtime/source/model固定条件のdriftをfocused identity consistency regressionが検出できない。
- live guardが暗黙pathへfallbackする。
- runner log改変、completion marker欠落、missing Evidence、identity driftをcore verifierが見逃す。
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

現在の実行経路を、runtime artifactの公式取得境界とrepository外準備、fixed commit objectまたはverified bundleによるsource準備、model store検証または新規準備、focused local regression、preflight、strict entrypoint、verified-bundle-only low-level harness、actual API / inference、run専用Evidence保存、runner observation、Evidence + Provenance独立検証、Requirement / Contract再照合の順に整理した。

取得元・配置path・artifact identityを混同しない。runtime archiveは公式Release URLを取得入口として固定しても、最終的なidentityはactual bytesのSHA-256へ戻す。KJ Atlas checkoutはfixed commit objectの取得元であり、working treeそのものをstrict runtime sourceにはしない。model storeもstatic manifest / blob identityとactual `/api/tags`観測を分離する。

preflightはstrict入口の明白なpath blockerを可能な範囲で事前に予測する。runtime archiveのsource配下配置やsymlink、model storeとsourceの双方向包含を事前に止めても、それはactual A / B実行の成立を意味しない。

失敗時のEvidenceは、成功を補強するためではなく、どこで何が成立しなかったかを失わないために保存する。structured preflight blockedではstrict executionを開始せず、strict開始後の失敗では可能な範囲のrunner /途中Evidenceを残す。いずれもpartial Evidenceを`ready-to-review`やruntime exchange PASSへ昇格しない。

保存済みrunの標準検証は、core execution条件に加えてsaved preflightとsource acquisitionまで見る`verify_runtime_version_exchange_provenance.py`とした。core `verify_runtime_version_exchange_evidence.py`は下位境界として残す。Evidence directoryや必須Evidence fileのsymlinkも拒否し、どちらのPASSもRequirement / Contract判断や成果品質へ自動昇格させない。

GitHub Actionsを使わないcurrent baselineでは、actual A/Bを起動しないrepository-local regressionを`run_runtime_version_exchange_local_checks.py`へ集約した。allowlistの登録漏れも検出するが、このrunnerのPASSもactual runtime exchange Evidenceの代替にはしない。本セッションでは実行containerへrepository sourceを取得できなかったため、新しい一括実行結果を得たとは記録しない。

GitHub Actionsは完全停止を維持する。actual Ollama `0.32.13` / `0.32.14`交換はNot Yet Verifiedであり、本IssueはOpenのままとする。

意味、規範強度、Resolution条件、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して再ドラフトした。
