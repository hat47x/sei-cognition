# runtime integration probes

更新日: 2026-09-03

このディレクトリには、SOZAと外部Cognitive Method / model runtimeの接続を実際に確かめるためのintegration資産を置きます。

ここで重要なのは、**何を検証するか**と**どこで実行するか**を分けることです。current `develop/v0.2.0`ではGitHub Actions workflowを常設していません。必要な検証はrepository-localなtest、checker、probeをローカル等から個別に実行します。過去のActions Runはhistorical Evidenceとして残しますが、現在の成立条件にはしません。

```text
what must be verified
  != where it is executed
```

## Runtime version exchange

`run_runtime_version_exchange.sh`は、ISSUE-000070のruntime version交換実験をrepository-localに実行するharnessです。

この実験では、次を固定します。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- KJ Atlas endpoint: `POST /ai/suggest-card-groups`
- Method input: harness内の固定3-card input
- model: `qwen2.5:0.5b`
- model artifact digest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`
- model prompt

交換するのはOllama runtime versionだけです。

- revision A: `0.32.13`
- revision B: `0.32.14`

```text
same Method Definition
same logical Method Realization
same KJ Atlas source
same Method input
same pinned model artifact
same model prompt

runtime revision A != runtime revision B
```

確認したい中心命題は、runtime versionを交換した後も先行Method ApplicationのExact Reference、Provenance、outputを変更せず保持できることです。

```text
runtime version exchange
  → new exact Realization revision
  != historical Application rewrite
```

## 固定runtime artifact

現在のprobeはLinux / amd64用のOllama公式archiveを固定します。

| revision | official asset | size | SHA-256 |
| --- | --- | ---: | --- |
| A / `0.32.13` | `ollama-linux-amd64.tar.zst` | `1421793186` bytes | `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1` |
| B / `0.32.14` | `ollama-linux-amd64.tar.zst` | `1421191399` bytes | `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f` |

圧縮archive 2本の合計は`2842984585` bytesです。

公式asset名はA / Bで同じなので、ローカル準備時には次のversion付きfile名へ分けます。

- `ollama-0.32.13-linux-amd64.tar.zst`
- `ollama-0.32.14-linux-amd64.tar.zst`

sizeは、明らかに異なるfileを大きなSHA-256計算の前に拒否するための早期guardです。artifact identityの正本は実bytesのSHA-256です。

```text
archive size match
  != artifact identity verified

archive size match
  + exact SHA-256 match
  = fixed runtime archive identity guard
```

MLX / ROCm等の別assetは、同じversion名でも別bytes / 別digestです。小さいという理由だけで本実験の固定artifactへ置き換えません。

Linux / amd64はISSUE-000070のprobe-local条件です。SOZA全体のplatform supportをLinux / amd64へ固定する意味ではありません。

## ローカル実行までの流れ

actual A / B実行までを、次の順に分けます。

```text
1. fixed runtime archiveの計画確認
2. fixed runtime archiveの準備・再検証
3. fixed KJ Atlas checkoutの準備
4. side-effect-free preflight
5. actual A / B harness
6. Evidenceの読み戻し
```

途中の工程が成功しても、その後の工程まで成功したとは扱いません。

## 1. runtime archiveの計画確認

固定artifact metadataは`runtime_version_exchange_artifacts.json`に機械可読な形でも置いています。現在のmanifestには、固定KJ Atlas commit、runtime A / Bのversion・公式asset名・ローカル保存名・size・SHA-256・公式URL、および固定model identityを記録しています。

取得前に、networkアクセスやfile作成を行わず計画だけを確認できます。

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives \
  --plan
```

構造化して確認する場合は`--json`を付けます。

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives \
  --plan \
  --json
```

`--plan`の成功は、archiveを取得済みであることを意味しません。

## 2. runtime archiveの準備・再検証

networkへ到達できる環境では、固定archiveを次で準備できます。

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives
```

このtoolは、download中のbytesを最終fileへ直接書きません。まず`.part`へ保存し、sizeとSHA-256の両方が固定値に一致した場合だけ最終fileへ原子的に昇格します。

既に正しいarchiveが存在する場合は、networkを使わず再検証して再利用します。既存fileが固定条件に一致しない場合は上書きしません。また、`.part`が残っている場合も暗黙に再開・上書きせず停止します。途中状態を利用者が確認できるようにするためです。

network取得を行わず、既存fileだけを確認する場合は`--verify-only`を使います。

```bash
python3 runtime/integration/prepare_runtime_version_exchange_archives.py \
  --output-dir /path/to/runtime-archives \
  --verify-only
```

AまたはBだけを扱う場合は`--runtime a`または`--runtime b`を指定できます。

```text
archive preparation success
  = fixed runtime archive bytesを準備・再検証できた
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

準備tool自身の境界は次で検査します。

```bash
python3 runtime/integration/test_prepare_runtime_version_exchange_archives.py
```

このtestは、manifestとpreflight / harness / Go側固定identityの整合、A / Bのローカルfile名分離、既存fileの再利用、`.part`を介した原子的昇格、途中fileの非上書き等を確認します。

## 3. KJ Atlas checkoutの準備

SOZAとKJ Atlasは、どちらも未commit変更のないcleanなGit checkoutである必要があります。KJ Atlasは固定commitへ合わせます。

```bash
git clone https://github.com/hat47x/kj-atlas.git _external/kj-atlas
git -C _external/kj-atlas checkout 4f28c13abe4176503c6fed863383a2d1db2299e9
```

既存checkoutを使う場合は、preflight / harnessの`--kj-atlas-dir`で明示できます。

harnessはKJ Atlasのrepository identityを名前だけで信用せず、actual HEADを固定commitへ照合します。

## 4. ローカルpreflight

actual processを起動する前に、`check_runtime_version_exchange_preflight.py`で副作用のない診断を行えます。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas
```

preflightはruntime / model processを起動せず、artifactをdownloadしません。主に次を確認します。

- hostがLinux / amd64か。
- 必要コマンドを利用できるか。
- SOZA / KJ AtlasがGit working treeでcleanか。
- KJ Atlas HEADが固定commitか。
- work / Evidence / external model pathがsource repository配下を指していないか。
- 新規pathが必要な場所で既存pathを再利用していないか。
- 事前配置runtime archiveのsizeとSHA-256が固定値に一致するか。
- 事前配置model storageが安全な場所に存在するか。
- local port `11434` / `8001` / `8101`が空いているか。
- work領域を置くfilesystemにどの程度のfree bytesがあるか。

空き容量は診断値です。固定archive 2本の圧縮bytes合計との比較材料にはできますが、展開後runtime、Python virtual environment、model storageには追加容量が必要です。

```text
disk free-space observation
  != enough capacity proven
```

runtime archiveとmodel storageをすべて事前配置した状態だけを確認する場合は、次のようにします。

```bash
python3 runtime/integration/check_runtime_version_exchange_preflight.py \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --require-prepositioned-artifacts
```

`--json`を付けると、`ready` / `blocked`、blocker ID、固定artifact metadata、各checkを構造化JSONで取得できます。

model storage directoryが存在するだけでは、固定model artifactを検証済みとは扱いません。model identityは固定Ollama runtimeをactualに起動した後、Ollama APIから観測したfull digestで確認します。

```text
preflight ready
  = actual probeを開始できるローカル条件が揃った
  != actual Ollama A/B inference PASS
  != fixed model digest verified
  != runtime-version-exchange Scoped Executable Evidence
```

preflight自身は次で検査します。

```bash
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
```

## 5. actual harnessの実行

runtime archiveをharness自身に取得させる場合は次を実行します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --evidence-dir /path/to/new-evidence-directory
```

準備toolで固定runtime archiveを揃えた場合は、そのpathを明示します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --evidence-dir /path/to/new-evidence-directory
```

固定model storageも事前配置している場合は`--model-dir`で明示します。

```bash
runtime/integration/run_runtime_version_exchange.sh \
  --kj-atlas-dir /path/to/kj-atlas \
  --runtime-a-archive /path/to/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst \
  --runtime-b-archive /path/to/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst \
  --model-dir /path/to/ollama-models \
  --evidence-dir /path/to/new-evidence-directory
```

事前配置は検証条件を弱める仕組みではありません。

```text
archive acquisition
  = downloaded | prepositioned

artifact identity
  = actual archive bytes + fixed SHA-256

acquisition path
  != artifact identity
```

`--model-dir`を指定した場合もmodel tagだけでは受理せず、Ollama APIから観測したfull model digestが固定値と一致することを要求します。既存model storageに固定artifactがなければ、harnessはそのdirectoryを暗黙に更新せず停止します。

harness自身が作成したwork-local model storageでは、固定artifactが存在しない場合に取得を試み、取得後に同じfull digestを検査します。

## pathとprocessの安全境界

`--work-dir`と`--evidence-dir`には、まだ存在しない新しいpathを使います。一つのEvidence directoryを一つのrunだけへ対応させ、前回runと今回runのEvidenceが混在しないようにします。

work / Evidence / external model directoryはSOZAまたはKJ Atlas repository配下へ置けません。実体pathへ正規化した後に判定します。

固定portを使うprocessは起動前にportが空いていることを確認し、起動後もharness自身が開始したPIDの生存を確認します。別processのhealth responseを今回の実行identityへ取り込まないためです。

Go側artifact guardへ渡すKJ Atlas checkout、runtime archive、version logのpathはharnessがすべて明示します。`GITHUB_WORKSPACE`や固定`/tmp`へ暗黙fallbackしません。

## actual実行で確認すること

harnessは概ね次を一続きに確認します。

1. SOZA / KJ Atlas source identityとclean treeを確認する。
2. runtime A / B archiveを取得または事前配置pathから参照する。
3. A / Bのactual archive SHA-256を固定値と照合する。
4. archiveを別々のruntime rootへ展開する。
5. actual binary versionが`0.32.13` / `0.32.14`であることを確認する。
6. 両runtimeで同じ固定model artifact digestを確認する。
7. 同じMethod inputをKJ Atlasへ渡し、actual inference countersとresultを保存する。
8. A / Bのprompt SHA-256が同一であることを確認する。
9. SOZAの通常Method integration testとruntime-exchange live testを実行する。
10. historical Application不変性、Exact Binding、portable reconstruction、negative controlを確認する。
11. 成否にかかわらず、そこまで得られたEvidenceをrun専用directoryへ保存する。

生成文そのものの一致はPASS条件ではありません。

## ローカルの軽量検査

actual runtimeやmodelを取得せず、ローカルで確認できる境界は分けて実行できます。

```bash
python3 runtime/integration/test_prepare_runtime_version_exchange_archives.py
python3 runtime/integration/test_check_runtime_version_exchange_preflight.py
python3 runtime/integration/test_run_runtime_version_exchange.py
```

これらは、artifact preparation、preflight、harness interfaceの退行を検出するためのものです。

```text
local helper test PASS
  != actual Ollama A/B inference PASS
  != runtime-version-exchange Scoped Executable Evidence
```

## 6. Evidenceの読み方

Evidence directoryには、存在する範囲で次を保存します。

- execution ID
- SOZA repository commit
- KJ Atlas source commit
- host OS / architecture
- runtime A / B versionとexpected archive digest
- runtime archive acquisition mode
- model name / expected digest / storage mode
- `qualityJudgement = not_evaluated`
- 固定Method request
- A / B runtime version log
- A / B actual runtime archive SHA-256
- A / B model digest / tags
- A / B inference Evidence
- A / B KJ Atlas result
- Adapter / KJ Atlas / Ollama log

取得経路はProvenanceとして残しますが、それだけでRealization identityを分けません。

途中で停止した場合も、そこまで生成されたEvidenceを残します。

```text
Evidence preserved
  != runtime exchange PASS
  != output quality satisfied
```

## 成果品質との境界

このprobeが確認するのは、runtime交換に伴うexecution identityとhistorical reconstructionです。

actual KJ Atlas outputの意味上の品質は`evaluation/method-quality/`の評価境界で別に扱います。

```text
runtime exchange PASS
  != arbitrary runtime portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation correctness
  != Decision correctness
  != E4 Operational portability
```

実験の意味、Exact Realization revision、historical Application不変性、Resolution条件は`plan/issue/ISSUE-000070-verify-runtime-version-exchange-history.md`を正とします。

## Ollama adapter

`e3b_m1b_ollama_adapter.py`は、KJ Atlasのlocal model境界からOllamaへ接続するintegration-only adapterです。model / runtime固有fieldをSOZA Universal Contractへ追加するための実装ではありません。

## 自然な日本語レビュー

このREADMEを、current no-Actions baseline、ISSUE-000070、固定runtime / model identity、archive準備tool、preflight、repository-local harness、Evidence保存、ISSUE-000071の成果品質評価境界へ戻って全文監査しました。

手順は「固定条件を確認する」「artifactを準備する」「実行環境を診断する」「actual processを動かす」「Evidenceを読み戻す」に分けました。各段階の成功を、まだ実行していない後続段階の成功へ読み替えない構成にしています。

archive準備では、A / Bの公式asset名が同じであることから生じるローカルfile名衝突を避け、version付きfile名へ分離しました。また、途中downloadを最終fileとして扱わず、sizeとSHA-256が一致したbytesだけを昇格させます。ただし、この準備成功もactual runtime交換のEvidenceではありません。

preflightの`ready`、archive size一致、disk空き容量、各種軽量testのPASSもactual A / B成立へ昇格させません。artifact identityはactual bytes / full digestへ戻し、model identityはactual Ollama APIで確認します。

actual Ollama `0.32.13` / `0.32.14`交換は引き続きNot Yet Verifiedです。実装済みの準備・安全策と、未完了のactual A / B実行を自然な日本語として明確に読み分けられることを最重要視して再ドラフトしました。
