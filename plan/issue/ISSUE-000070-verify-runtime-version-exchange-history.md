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

既存境界を維持する。

- Method Definitionは「何を行うMethodか」を表す。
- Method Realizationは「どの実現機構で実行するか」を表す。
- 同じ実現機構のversion差は、同じlogical Realizationに属するhistorical revisionとしてExact Bindingで固定できる。
- Method Applicationは、実行時に利用したRealization revisionをExact Referenceで保持できる。
- runtime / model固有情報は、必要なProvenance / realization-local metadataとして保持する。
- source / artifactの取得経路はProvenanceであり、それ自体をRealization identityにはしない。
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

model artifact digestは、Actual Model Artifact Exchange E3b Run `33670697154`でOllama `0.32.14`から実際に観測したartifact identityである。

A / Bのdigestが一つの実行内で互いに等しいだけでは固定条件成立とみなさない。両方がこの期待digestに一致することを要求する。

交換するのはOllama runtime versionだけとする。

- revision A: `0.32.13`
- revision B: `0.32.14`

## Pinned runtime artifacts

Linux amd64 archiveの実bytesを固定SHA-256で識別し、別々の一時directoryへ展開してbinaryを直接起動する。

- `v0.32.13 / ollama-linux-amd64.tar.zst`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- `v0.32.14 / ollama-linux-amd64.tar.zst`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

2026-09-03の静的再監査では、両digestがOllama公式GitHub Release metadataの各asset digestと一致することを確認した。これはruntime交換をactualに実行したExecutable Evidenceではない。

archiveはdownloadしても事前配置してもよい。どちらでも実際に利用するbytesのSHA-256を計算し、固定値へ一致させる。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual archive bytes + fixed SHA-256

acquisition path
  != artifact identity
```

## KJ Atlas source identity

### clean checkoutだけではstrict Evidenceにならない

KJ Atlasは`.env`、`*.so`、`__pycache__`、`*.pyc`、`*.egg-info`等をGit管理外にできる。`Settings`も`.env`を読み得る。

したがって、HEADが固定commitで通常の`git status`がcleanであっても、working treeに存在するignored fileまで固定commit identityへ含まれるわけではない。

```text
HEAD = pinned commit
  + normal Git clean
  != byte-complete runtime source identity
```

このため、`--kj-atlas-dir`によるdirect checkout executionは互換・開発用経路として残すが、本IssueをResolvedにするstrict runtime-version-exchange Evidenceには使わない。

### strict Evidenceでは固定commit objectからexportする

`runtime/integration/export_kj_atlas_runtime_source.py`を使い、Git working treeではなく固定commit objectから追跡済みruntime surfaceだけをexportする。

対象は次の4要素である。

- `pyproject.toml`
- `alembic.ini`
- `alembic/`
- `src/`

exporterは`git archive`へ固定commitを明示する。working treeにignored `.env`、binary extension、bytecode cache等が存在してもexport対象にはならない。HEADが後続commitへ進んでいても、固定commit objectがrepository内に存在すれば同じsurfaceへ戻れる。

export後は`verify_kj_atlas_runtime_source.py`でGit object identityを再計算する。

固定identityは次のように区別する。

```text
fixed KJ Atlas commit
  4f28c13abe4176503c6fed863383a2d1db2299e9

parent backend tree
  7d71ac2b4d32bef90f3a481ade1b4c92ddddd084

minimal runtime surface tree
  208bea71eef4afed3ddfd3fabb36b0969d167a90
```

`parent backend tree`は固定commit内の親文脈であり、`minimal runtime surface tree`は実際に実行へ持ち込む4要素だけのtree identityである。

```text
parent backend tree
  != runtime surface tree
```

verifierは次を検査する。

- `pyproject.toml` blob
- `alembic.ini` blob
- `alembic/` tree
- `src/` tree
- runtime surface tree
- 予期しないtop-level要素がないこと
- symlinkがないこと
- runtime source fileに実行bitがないこと

固定commitの`pyproject.toml`はREADMEやlicense等をbuild metadataとして参照せず、setuptools package探索は`src`を基準とする。したがって今回のpackage buildに必要なsource境界をこの4要素で構成できる。

strict Evidenceのsource経路は次とする。

```text
KJ Atlas Git repository
  ↓ fixed commit object
export_kj_atlas_runtime_source.py
  ↓ tracked runtime surface only
verify_kj_atlas_runtime_source.py
  ↓ verified runtime bundle
run_runtime_version_exchange.sh --kj-atlas-backend-bundle ...
```

source取得方法と実行source identityを分ける。

```text
source acquisition
  != source identity
```

## Exact Realization Reference

既存のKJ Atlas live mappingには、後方互換なoptional経路として`ApplyGroupingInput.RealizationReference`がある。

- 未指定時はlogical-only Realization Referenceを保持する。
- 指定時は`method_application.realization_ref`へ`semanticruntime.Reference`を保持する。
- logical identityが`RealizationRef`と一致しなければ、canonical stateを変更せず拒否する。

Exact Bindingを作るMethod Realization payloadと、portable Semantic Interchangeへ格納するRealization recordは同じ生成経路を使う。

共有mapping自体はActual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`でactualにPASSしている。ただし、この既存Evidenceをruntime version交換の成立証明には使わない。

## Repository-local execution harness

actual実行本文は`runtime/integration/run_runtime_version_exchange.sh`へ置く。

strict Evidenceでは、export済みverified bundleを`--kj-atlas-backend-bundle`で渡す。

harnessは次を一続きに行う。

1. Linux / amd64であることを確認する。
2. SOZA working treeと入力pathの安全境界を確認する。
3. KJ Atlas verified bundleのGit object identityを確認する。
4. bundleをexecution sourceとpackage install sourceへ分けてwork directoryへcopyし、双方を再検証する。
5. 専用Python virtual environmentへpackageを導入する。
6. Ollama `0.32.13` / `0.32.14` archiveを取得または事前配置pathから参照し、実測SHA-256を固定値へ照合する。
7. 同じmodel storageで`qwen2.5:0.5b`を利用し、A / B双方のfull model digestを固定値へ照合する。
8. 同じ3-card Method inputをA / Bへ通し、actual inference countersとKJ Atlas responseを確認する。
9. A / Bのprompt SHA-256が同一であることを確認する。
10. live Go test直前にexecution source、runtime version、runtime archiveを再確認する。
11. historical Applicationとportable reconstructionを検査する。
12. 成否にかかわらず、そこまで生成されたEvidenceをrun専用directoryへ保存する。

package buildの副作用をexecution sourceへ混ぜないため、execution copyとinstall copyは分離する。

```text
repository-local harness
  = reproducible execution boundary
  != GitHub Actions required
  != specific runner required
```

## Local preflight

`check_runtime_version_exchange_preflight.py`はactual runtimeを起動せず、実行前に解消できる不足を確認する。

strict Evidenceではexport済みbundleを`--kj-atlas-backend-bundle`で指定する。

preflightは主に次を診断する。

- host OS / architecture
- 必要command
- SOZA working tree
- KJ Atlas checkoutまたはbundleの入力条件
- checkout / bundle同時指定の拒否
- work / Evidence / model path境界
- 事前配置runtime archiveのdigest
- 事前配置model storageのdirectory境界
- local port

```text
preflight ready
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

最新developへ統合済みだったpreflight純粋ロジックの9件test PASSは保持する。一方、本Issueで追加したexporter / bundle拡張を含む最終branch全体のactual A/B実行はまだ完了していない。

## Source / artifact guard

live Go testでは、verified bundle modeについて次を再確認する。

- source commit
- parent backend tree
- runtime surface tree
- verification basis
- runtime A / B version log
- runtime A / B archive SHA-256

`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackせず、harnessが実際のpathを明示する。

pure-Go / Pythonの軽量testでは、source mode、Exact Binding、tamper、unknown digest、source verifier、preflight、harness interface等をactual runtimeなしで検査する。

## Required experiments

### E1 — strict source identity

固定KJ Atlas commit objectからruntime surfaceをexportし、verified bundleとしてharnessへ渡す。

PASS条件:

- working treeのignored fileがexport bundleへ混入しない。
- fixed commitから4要素を再構成できる。
- runtime surface treeが固定値へ一致する。
- source tamper / unexpected top-level / symlink / executable bitを拒否する。
- actual A / B実行の両方が同じverified runtime surfaceを使う。

### E2 — runtime artifact identity

A / Bそれぞれのactual archive digestを固定値へ照合し、実際のbinary versionを確認する。

### E3 — same pinned model artifact

A / Bのfull model digestが互いに同じで、固定期待digestにも一致することを確認する。tagだけで同一性を推論しない。

### E4 — same prompt / actual inference

A / Bでprompt SHA-256が一致し、`ollama_done = true`、`prompt_eval_count > 0`、`eval_count > 0`を確認する。KJ Atlas response boundaryが両responseを受理する。

生成文そのものの一致はPASS条件にしない。

### E5 — same logical Realization / different Exact Binding

A / Bが同じlogical Realizationを持ち、runtime revision差によって異なるExact Bindingを持つことを確認する。

source / artifactの取得経路だけの違いは別Realization identityへ昇格させない。

### E6 — historical Application immutability

runtime B追加後もApplication AのExact Realization Reference、Provenance、outputが変わらないことを確認する。

### E7 — portable historical reconstruction

二つのRealization revisionと二つのApplicationをSemantic Interchangeへ格納し、payload verification、bundle-local resolution、unknown revision negative controlを確認する。

### E8 — no semantic promotion

Method outputをRecommendation / Decisionへ自動昇格しない。

### E9 — Evidence preservation

run専用Evidence directoryから、少なくとも次へ戻れることを確認する。

- SOZA commit
- KJ Atlas verified source identity
- Method request
- runtime A / B version
- actual runtime archive digest
- model digest / tags
- inference Evidence
- KJ Atlas result
- process logs

```text
Evidence directory preserved
  != runtime exchange PASS
  != output quality satisfied
```

## Existing Evidence

### Exact Reference mapping / fixed model artifact

Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`では、actual model artifact exchange、full model digest、prompt digest、historical Application保持を確認した。

したがってExact Reference mappingと今回固定するmodel artifact identityには既存Executable Evidenceがある。ただし、runtime version交換のExecutable Evidenceではない。

### Historical GitHub Actions exploration

過去にはruntime交換workflow等を試作したが、GitHub-hosted runnerは割り当て前に終了する状態が続いた。具体的な外部原因は確定していない。

現在はGitHub Actionsを当面完全停止している。workflow追加・復元、過去run再実行、runner監視は行わず、current実証はrepository-local harnessとローカル個別検査を正とする。

### Local preflight

既存preflight境界には9件のローカルtest PASSがある。これはactual Ollama A / B inferenceを開始したEvidenceではない。

### Source exporter / verifier

固定commit objectからruntime surfaceだけをexportする実装とsynthetic Git testを追加した。実装中のローカル再現では、ignored `.env` / `.so` / `__pycache__`がexportへ混入しないこと、HEADが後続commitでも固定commit objectから同じsurfaceへ戻れることを確認した。

ただし、private repositoryの最終PR head全体をこの実行環境へmaterializeできていないため、PR head上の全軽量test PASSやactual KJ Atlas package install PASSへは昇格させない。

## Current implementation state

current branchには次がある。

- Exact Realization Reference mapping
- runtime / model固定identity
- historical Application / Provenance / output不変性test
- portable Semantic Interchange reconstruction
- unknown revision negative control
- repository-local runtime exchange harness
- local preflight
- KJ Atlas runtime source verifier
- fixed commit objectからのruntime source exporter
- parent backend tree / runtime surface treeの分離
- verified bundleのexecution / package-install copy分離
- source / runtime artifact live guard
- run-isolated Evidence directory
- prepositioned runtime / model artifact経路
- source / artifact acquisitionとidentityを分けるProvenance境界

ただし、repository-local harnessによるactual Ollama `0.32.13` / `0.32.14`交換はまだ完走確認していない。

## Current Evidence state

```text
fixed runtime artifact identity against official release metadata
  = statically verified

qwen2.5:0.5b expected model artifact identity
  = actual digest observed in Run 33670697154

Exact Realization Reference mapping
  = Executable Evidence available in Run 33670697154

local preflight baseline
  = 9 tests PASS; actual runtime not started

verified runtime source bundle boundary
  = implemented

fixed-commit runtime source exporter
  = implemented; focused synthetic behavior locally reproduced

PR head full lightweight test suite
  = Not Yet Verified in the current execution environment

actual runtime 0.32.13 / 0.32.14 execution through verified bundle
  = Not Yet Verified

same pinned model digest / same prompt digest across runtime versions
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

ISSUE-000071は評価境界の確立としてResolvedになったが、human reviewやKJ-method outcome qualityがSatisfiedになったことを意味しない。本Issueでもexecution conformanceと成果品質を混同しない。

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

1. 固定KJ Atlas commit objectからexportしたruntime surfaceをverified bundleとして固定identityへ検証する。
2. strict A / B実行ではdirect checkoutではなく、そのverified runtime bundleを使う。
3. runtime A / B archiveのactual digestとbinary versionを確認する。
4. A / B双方のmodel digestが固定artifact identityと一致し、same prompt digestもactual executionで確認する。
5. 両runtimeでactual inferenceが成立する。
6. Application A / Bがsame logical / different Exact Realization revisionを保持する。
7. Application AのReference / Provenance / outputがB追加後も不変である。
8. Realization payload verification、portable reconstruction、unknown revision negative controlがPASSする。
9. Recommendation / Decisionへの自動昇格がない。
10. run専用Evidence directoryからsource identity、入力、actual runtime digest、model identity、出力、inference Evidenceへ戻れる。
11. Requirement / Contract再照合と自然な日本語最終監査を行う。

GitHub-hosted runnerの復旧、GitHub Actions workflowの再導入、runtime / model artifactの実行時download可否、preflightの`ready`、direct checkout executionだけではResolution条件を満たさない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revision交換でhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- portable bundleでApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを受理する。
- working treeのignored fileがstrict runtime sourceへ混入できる。
- source acquisition modeだけでsource identityを推論する。
- 親backend treeとruntime surface treeを同一視する。
- bundle pathやfile名だけで固定sourceとみなす。
- source tamper、symlink、実行bit差を見逃す。
- package buildの副作用がexecution sourceへ混入する。
- model tagだけでartifact identityを固定する。
- promptが交換軸へ混入する。
- 事前配置artifactでdigest検査を省略できる。
- 既存model storageをharnessが暗黙更新する。
- preflight `ready`をactual runtime交換PASSへ昇格する。
- 別processを今回runの実行identityとして誤認する。
- 複数runのEvidenceが同じdirectoryへ混在する。
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

execution成立、historical reconstruction、生成品質を別の評価軸として扱う。

## Natural Japanese review

ISSUE-000067 / ISSUE-000068、Cognitive Method Contract、Exact Binding、current KJ Atlas mapping、GitHub Actions完全停止後の開発運用、repository-local harness、local preflight、source / artifact guard、ISSUE-000071の成果品質評価境界を再照合した。

今回の重要な修正は、「固定commitのclean checkout」と「固定commit由来の実行bytes」を同一視しないことである。KJ Atlasでは`.env`やbinary / bytecode cache等をGit管理外にできるため、通常のclean判定だけではstrict source identityにならない。

そこでstrict Evidenceでは、working treeを直接実行せず、固定commit objectから追跡済みruntime surfaceだけをexportする。その出力を既存bundle verifierへ通し、execution sourceとpackage install sourceをさらに分離する。

これにより、Git repositoryは固定sourceを得るための取得面となり、実験に使う実際のsource bytesは一つのverified runtime surfaceへ収束する。

preflight、source export、source verification、actual process execution、historical reconstruction、成果品質も別責務として記述した。actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedである。

意味、規範強度、Evidence強度、未検証範囲を変えず、自然な日本語として読み通せることを最重要視して全文を再ドラフトした。
