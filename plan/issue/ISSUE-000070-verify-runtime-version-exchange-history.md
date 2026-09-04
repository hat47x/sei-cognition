# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Resolved**
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-05

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

GitHub Actionsはcurrent baselineで完全停止している。workflowの復元、過去runの再実行、runner監視は行わず、必要なtest、checker、probeをrepository-localに実行する。過去のActions Runはhistorical Evidenceとしてのみ保持する。

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

圧縮archive 2本の合計は`2842984585` bytesである。sizeはfile取り違えをSHA-256計算前に止める早期guardであり、artifact identityの正本ではない。identityはactual bytesのSHA-256で固定する。

固定metadataは`runtime/integration/runtime_version_exchange_artifacts.json`へ機械可読に保持する。manifest loaderはruntime名、version、Linux / amd64 platform、size、SHA-256、asset名、対応versionのOllama公式GitHub Release URLを検証する。

`check_runtime_version_exchange_manifest_consistency.py`はartifact manifest、preflight、low-level harness、Go側の固定値を横断照合する。`runtime_version_exchange_official_release_snapshot.json`にはGitHub Release APIから取得した公式Release側の観測を保存している。snapshot上の`immutable=false`を含め、Release metadataは取得元の監査材料であり、actual bytesのidentity保証には使わない。

```text
official acquisition origin
  = acquisition boundary / Provenance
  != artifact identity

artifact identity
  = actual bytes / fixed SHA-256
```

`prepare_runtime_version_exchange_archives.py`はdownload / verify-only / prepositioned再利用を同じsize / SHA-256境界へ戻す。準備先はSOZA repository外とし、output directory、archive target、`.part`のsymlinkや不正な既存pathを大容量download前に拒否する。

Linux / amd64は本probeの実行条件であり、SOZA全体のplatform supportを限定する意味ではない。

## KJ Atlas source identity

working treeは固定commit objectを保持するrepositoryとして利用できるが、working treeそのものをstrict runtime source identityとはみなさない。

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

`verify_kj_atlas_runtime_source.py`はblob / tree identity、runtime surface tree、予期しないtop-level要素、symlink、実行bit等を再検証する。verifierの結果fileは入力bundleの外へ出し、検証自身がsourceを変更しない。exporterのidentity出力もcheckoutと完成bundleから分離する。

source exporterはtarの一時展開先を完成bundleと同じ側へ固定し、親processの`TMPDIR`をsource bytesの配置先にしない。copyまたは最終identity検証の途中で失敗した場合はpartial bundleを除去し、未検証artifactを完成物として残さない。

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

```text
prepared model store PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

A / Bのactual実行では、両runtimeの`/api/tags`から同じ期待full digestを改めて観測する。

## Current execution path

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

checkoutの現在HEADやignored fileはstrict runtime source identityの判定には使わない。free bytesは観測値であり、十分なdisk容量の証明にはしない。

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

preflight observationにはpreflight exit code、blocker、`strictStarted=false`、`qualityJudgement=not_evaluated`を記録する。runnerはnon-zeroのまま終了する。構造化JSONとして扱えない異常ではEvidenceを推測で作らず通常エラーとして停止する。

### Strict entrypoint

`run_runtime_version_exchange_strict.py`はstrict Evidenceの標準入口である。

責務:

1. checkout指定時は固定commit objectからverified runtime bundleをexportする。
2. bundle指定時は固定Git object identityを再検証する。
3. 事前配置runtime archiveのsymlink、不存在、SOZA/source/modelとのoverlap、A/B同一pathを拒否する。
4. 事前配置runtime archiveのactual size / SHA-256を、source exportやmodel準備より前に固定manifestへ照合する。
5. `--model-dir`指定時は既存storeを静的検証する。
6. `--prepare-model-dir`指定時は固定registryから新規storeを準備し、静的再検証する。
7. source、model store、Evidence、work directoryの双方向overlapを拒否する。
8. identity / safety optionをlow-level harnessへ迂回上書きできないようにする。
9. verified bundleだけをlow-level harnessへ渡す。
10. Evidence directoryが作成された範囲で、source export、model preparation、static model verificationを同じrun Evidenceへ保存する。

`--work-dir`を省略しても親processの`TMPDIR`へ委ねない。Evidence directoryと同じparentへ`<evidence-name>-work`を新規pathとして決定し、low-level harnessの`--work-dir`とchild環境の`TMPDIR`へ同じpathを渡す。

checkout起点の一時verified source bundleも`<evidence-name>-source/backend`へ明示配置し、親`TMPDIR`を使わない。この一時source rootはrun終了後に除去し、source export ProvenanceだけをEvidenceへ残す。

```text
strict entrypoint verification PASS
  != actual Ollama /api/tags observation PASS
  != actual runtime A/B inference PASS
```

### Low-level harness

actual実験本文は`run_runtime_version_exchange.sh`に置く。low-level harnessはverified KJ Atlas backend bundleを必須とし、checkoutを直接実行sourceにはしない。

actual runtime archive / binary version / `/api/tags` model digest / prompt digest / inference / Exact Binding / historical Application / portable reconstruction / negative controlを一続きに確認し、run専用Evidence directoryへ保存する。

### Verified runner / failure Evidence

actual実行時の標準入口は`run_runtime_version_exchange_with_verification.py`である。

runnerは次を行う。

1. side-effect-free preflightを実行する。
2. preflight `ready`の場合だけstrict入口を起動する。
3. strict実行のstdout / stderrをcombined logへ集約する。
4. exit code、combined log SHA-256 / bytes、source preparation、preflight resultをrunner observationへ記録する。
5. strict processが失敗し、Evidence directoryがまだ無い場合は、process終了後に新しいEvidence directoryを作成してrunner logとpreflightを保存する。
6. strict processがexit code 0なのにEvidence directoryが無い場合は成功扱いせず拒否する。
7. 保存できたrunについてEvidence + Provenance verifierを実行する。
8. verification reportはEvidence directoryの外へ保存する。

strict入口またはlow-level harnessがEvidence directoryを作成したcomplete runでは`evidenceDirectoryCreatedBy=strict-entrypoint`を要求する。strictがEvidence作成前に失敗し、verified runnerが失敗後にdirectoryを作った場合は`verified-runner-after-failure`として記録し、complete runへ昇格させない。

### Evidence + Provenance verification

保存済みrunの標準verifierは`verify_runtime_version_exchange_provenance.py`である。

`verify_runtime_version_exchange_evidence.py`によるcore execution Evidenceに加え、次を再検証する。

- saved preflightが`ready` / `blockers=[]`であること
- preflightのfixed artifact条件がcurrent artifact manifestと一致すること
- preflightのpinned source identityがcurrent固定値と一致すること
- checkout起点ではsource export Provenanceがactual source identityと一致すること
- verified bundle直入力ではcheckout source export fileが混入していないこと
- complete runのEvidence directoryがstrict入口側で作られたこと
- Evidence directory自身と必須Evidence fileがsymlinkでないこと

全機械条件とProvenance条件を満たすcomplete runだけが`ready-to-review`になり得る。blocked preflightや途中失敗のpartial Evidenceは`not-sufficient`である。

```text
Evidence + Provenance verification ready-to-review
  != Requirement / Contract assessment complete
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != ISSUE-000070 Resolved
```

## Acquisition boundary

runtime archiveはdownload / prepositionedを許可し、どちらもactual bytesの固定SHA-256へ戻す。新規downloadの入口は対応versionのOllama公式GitHub Release assetへ固定する。準備先はSOZA repository外とする。

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
- source exportの一時展開とstrict一時bundleを親`TMPDIR`へ置かない。
- source export失敗時にpartial bundleを残さない。
- runtime archive準備先をSOZA repository配下へ置かない。
- 事前配置runtime archiveはsource配下、symlink、A/B同一path、model storeとのoverlapを拒否し、actual bytesを再検証する。
- work / Evidence / prepared model target / verification outputは新しいpathだけを受け付ける。
- `--work-dir`省略時もstrict入口が明示work pathを決定する。
- source、model store、Evidence、work、verification outputを相互に分離する。
- model storeとSOZA/KJ Atlas sourceの双方向包含を拒否する。
- Evidenceをmodel store配下へ置かない。
- source/model verifierの結果fileを入力資産内部へ書かない。
- fixed local port `11434` / `8001` / `8101`が使用中ならactual processを開始しない。
- harness自身が起動したPIDを確認する。
- model storeはstatic identityとactual `/api/tags` full digestを区別する。
- 一つのEvidence directoryを一つのrunだけへ対応させる。
- exit code 0でもEvidence directoryが欠落していれば成功扱いしない。
- Go live guardは必要pathを明示し、`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしない。

## Local focused regression

actual runtimeを起動しないrepository-local regressionの標準入口は`run_runtime_version_exchange_local_checks.py`である。

```bash
python3 runtime/integration/run_runtime_version_exchange_local_checks.py
```

`--stop-on-failure`、`--list`、`--only TEST_FILE`を利用できる。`--result-output`を指定するとSOZA repository外の新規JSONへmachine-readable resultを保存する。各testの既定timeoutは120秒で、`--timeout-seconds`で変更できる。

timeoutはexit code `124`、child起動失敗はexit code `127`相当として結果へ残す。runnerはGit commit / cleanlinessの観測とtest resultを分け、Git観測に失敗してもtest resultを捏造しない。

runnerは明示allowlistとcandidate discoveryを照合し、runtime version exchangeに関係する候補testが未登録のまま増えることを検出する。runner自身のself-testも対象に含む。親shellのlive実行用環境変数はfocused testへ暗黙継承しない。

machine-readable resultには次を明示する。

- `actualRuntimeExchangeEvidence=false`
- `qualityJudgement=not_evaluated`

```text
focused local checks PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

current focused allowlistには、source exporter、strict archive boundary、actual harnessが利用するGo packageのnon-live compile / testも含まれている。

2026-09-05にcleanなSOZA commit `ae9f631b7d570a6c3853bb71b794d501761fdf63`をLinux / amd64、Go 1.25.14、Python 3.11.2環境で検査し、focused runner 23 file / 301 testがPASSした。actual A / Bを起動しない検査であるため、この結果だけをruntime交換Evidenceへは昇格しない。

## Required experiments

### E0 — strict source identity

- fixed commit objectからruntime surfaceを再構成できる。
- ignored fileがbundleへ混入しない。
- runtime surface treeが固定値へ一致する。
- source tamper / unexpected top-level / symlink / executable bitを拒否する。
- A / Bが同じverified runtime surfaceを使う。
- low-level harnessへworking treeを直接渡す経路がない。
- 一時source配置や途中失敗によってworking sourceや未検証bundleを残さない。

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
- actual workと一時source bundleは親`TMPDIR`から独立して明示配置される。
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

2026-09-03から2026-09-04に観測した外部取得制約は、その時点の環境固有の事実として保持する。未実行をPASSへ読み替えなかったことも変更しない。

2026-09-05には別のrepository-local Linux / amd64実行環境で固定runtime archive 2本と固定model storeを実バイトで準備できた。標準prepositioned runnerをcleanなSOZA commit `ae9f631b7d570a6c3853bb71b794d501761fdf63`から実行し、execution ID `local-20260904T193531Z-7855`でactual Ollama `0.32.13` / `0.32.14` A / Bを完走した。

保存Evidenceと評価結果は`runtime/RUNTIME_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`および`runtime/evidence/runtime-version-exchange-local-20260904T193531Z/`を正とする。独立Evidence + Provenance verifierは107 checkすべてを`ok`とし、blockerなしで`ready-to-review`を返した。

## Current implementation state

current developには次がある。

- Exact Realization Reference / Exact Binding
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- fixed runtime artifact manifest / preparation helper
- artifact manifest横断整合checker
- official GitHub Release snapshot
- runtime archive official origin / platform / size / digest validation
- runtime archive repository外 preparation / symlink guard
- strict prepositioned archive actual bytes precheck
- KJ Atlas source exporter / verifier
- source verifier / exporter result-output separation
- source exporterの親`TMPDIR`非依存一時展開
- source export partial bundle cleanup
- model store preparation helper / static verifier
- side-effect-free preflight
- preflight archive source/symlink guard
- preflight / strict model-source双方向overlap guard
- strict runtime exchange entrypoint
- strict既定work path / child `TMPDIR`明示固定
- strict checkout一時source bundle明示配置 / cleanup
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
- actual harness Go package compile / test regression
- focused machine-readable result / Git observation分離
- per-test timeout / launch-error preservation
- live Go guard / negative control
- byte-preserving post-run Evidence archive

actual Ollama `0.32.13` / `0.32.14`交換は2026-09-05に完走し、固定runtime / model / prompt、actual inference、same logical / different Exact Binding、historical Application不変性、portable reconstructionを同じrunで確認した。

## Current Evidence state

```text
fixed source identity
  = verifier / exporter available

fixed runtime metadata / acquisition boundary
  = repository-local checker / tests / official Release snapshot available

fixed model expected digest
  = actual historical observation available

model store preparation / static verification
  = helpers available

preflight / strict entrypoint / verified-bundle-only low-level harness
  = implemented

focused local check runner
  = 23 files / 301 tests PASS

failure Evidence preservation
  = structured preflight blocked / strict failure paths implemented

core Evidence + Provenance verification
  = implemented

actual runtime A/B binary / archive digest / model / prompt / inference
  = Verified for fixed Ollama 0.32.13 / 0.32.14 scope

portable reconstruction using actual runtime A/B evidence
  = Verified

runtime-version-exchange Scoped Executable Evidence
  = available
```

## Requirement / Contract assessment

REQ-0001、REQ-0004、REQ-0021、SCN-0005、SCN-0015へactual Evidenceを再照合した。runtime revision交換後も先行Applicationの意味と来歴を保持でき、Method / Realization / Application、logical / exact、Method output / Recommendation / Decisionの既存境界で結果を表現できた。

評価結果は**No Change**である。新しいStable Requirement、Acceptance Scenario、Universal Contract fieldは追加しない。runtime名、version、archive digest、model digest、prompt digestはRealization-local metadata / Provenance / Evidenceに留める。各Requirement / Scenarioは固定2 revisionのscopeを越えるproduction全体の成立を意味しないため、Executable Evidenceを`Partially Satisfied`に維持する。

## Resolution

2026-09-05のactual run、独立Evidence + Provenance verification、Requirement / Contract再照合、自然な日本語最終監査により、次をすべて満たした。

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

archive preparation、model store preparation、static model verification、preflight ready、failure Evidence保存、strict entrypoint verification、source export成功、focused local checks、helper / synthetic test、manifest consistency、official Release snapshot、disk free-space、GitHub Actions再導入、artifactの実行時download可否は、それ単独ではResolution条件にしない。

このResolutionは固定KJ Atlas source、固定model artifact、固定prompt、Ollama `0.32.13` / `0.32.14`の限定scopeに対するものです。成果品質、任意runtime互換性、fully offline execution、E4、Release / Operational / Adoption・Outcome Evidenceは未検証のままです。

## Reopen conditions

Resolved後も次の場合は再開する。

- historical ApplicationのExact Referenceがruntime交換で失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- payload / Binding不一致、unknown revision digestを受理する。
- working treeやignored runtime-affecting fileをstrict sourceへ直接混入できる。
- low-level harnessがdirect checkoutへfallbackできる。
- verified runtime surfaceのGit object identity不一致を受理する。
- source exporterが親`TMPDIR`へ固定source bytesを展開する。
- source export失敗後にpartial / 未検証bundleを完成artifactとして残す。
- strict入口がworkまたは一時source bundleの配置を親`TMPDIR`へ委ねる。
- source、model store、Evidence、work、verification outputを重ねて入力やEvidenceを検証副作用で変更できる。
- runtime archive準備先をSOZA repository配下へ置ける。
- 事前配置runtime archiveのsource配下配置、symlink、A/B同一path、model overlapをpreflight / strict入口で受理する。
- 事前配置archiveをpathやsizeだけで信用し、strict入口でactual SHA-256を再検証しない。
- runtime archive manifestが非公式取得URL、platform drift、invalid size / digestを受理する。
- artifact manifest、preflight、harness、Go固定条件のdriftを横断checkerが見逃す。
- preflightがstrict入口で拒否されるmodel/source overlapを見逃す。
- model manifest / blob bytesが固定identityと異なるstoreを受理する。
- fixed registry以外からprepared storeを暗黙に構成する。
- model tagだけでartifact identityを推論する。
- promptが交換軸へ混入する。
- acquisition modeだけの違いを別Realization identityへする。
- 別processのhealth responseを今回のactual実行と誤認する。
- 既存work / Evidence directoryを上書き・混在できる。
- strict processがexit code 0でもEvidence欠落を成功扱いする。
- structured blocked preflightやstrict failureの診断を保存できず、失敗地点を追えない。
- partial failure Evidenceをcomplete runとして`ready-to-review`へ昇格する。
- Evidence directoryや必須Evidence fileのsymlinkを標準verifierが受理する。
- saved preflight / source acquisition Provenanceのdriftを標準verifierが見逃す。
- focused runnerが候補testの未登録、timeout、launch errorを成功扱いする。
- focused resultをactual runtime exchange Evidenceや成果品質評価へ昇格する。
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

現在の実行経路を、runtime artifactの固定条件と公式取得境界、fixed commit objectまたはverified bundleによるsource準備、model store検証または新規準備、focused local regression、preflight、strict entrypoint、verified-bundle-only low-level harness、actual API / inference、run専用Evidence保存、runner observation、Evidence + Provenance独立検証、Requirement / Contract再照合の順に整理した。

取得元・配置path・artifact identityを混同しない。runtime archiveは公式Releaseを取得入口としても最終identityをactual bytesのSHA-256へ戻す。KJ Atlas checkoutはfixed commit objectの取得元であり、working treeそのものをstrict runtime sourceにはしない。sourceの一時展開やstrict内部bundleも親`TMPDIR`から分離し、失敗時のpartial bundleを残さない。model storeもstatic manifest / blob identityとactual `/api/tags`観測を分離する。

preflightやfocused regressionで明白な問題を早く止めても、それだけではactual A / B実行の成立を意味しない。今回もfocused checksとは別にactual processを完走し、保存Evidenceを独立verifierへ通した。focused resultには引き続き`actualRuntimeExchangeEvidence=false`と`qualityJudgement=not_evaluated`を残し、timeoutやlaunch errorも成功へ丸めない。

失敗時のEvidenceは、成功を補強するためではなく、どこで何が成立しなかったかを失わないために保存する。partial Evidenceを`ready-to-review`やruntime exchange PASSへ昇格しない。

GitHub Actionsは完全停止を維持する。repository-local actual runでOllama `0.32.13` / `0.32.14`交換とhistorical reconstructionが成立し、固定されたResolution Criteriaを満たしたため、本IssueをResolvedとする。

生成されたgrouping resultは構造上受理されたが、labelやrationaleの成果品質・日本語品質は評価していない。`qualityJudgement=not_evaluated`を維持し、ISSUE-000071で分離したhuman outcome reviewへ先回りしない。

意味、規範強度、Resolution条件、Evidence強度、未検証範囲を変えず、actualに成立した範囲だけを更新し、自然な日本語となることを最重要視して再ドラフトした。
