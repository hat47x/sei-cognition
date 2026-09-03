# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

同じCognitive Method、同じKJ Atlas source、同じMethod input、同じactual model artifactを使い、Ollama runtime versionだけを交換したときに、SOZAが先行Method Applicationの履歴を失わず保持できるかを実証する。

runtime version差は別のlogical Method Realizationへ分けず、同じ実現機構に属するhistorical revisionとして扱う。revisionの違いは、Cognitive Method Contractが既に持つExact Bindingで固定する。

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
- runtime / model固有情報は必要なProvenance / realization-local metadataとして保持し、Universal ontologyへ先取りしない。
- Method outputをRecommendation / Decisionへ自動昇格しない。

## ISSUE-000067 / ISSUE-000068との接続

ISSUE-000067では、Method Definition / Realization / Applicationを履歴として再構成するためのH1 / H2境界を検討した。

ISSUE-000068では、KJ Atlas source、runtime、Method inputを固定し、actual model artifactだけを交換した。先行Applicationを後続model実行後も保持できることを確認した一方、modelが変われば生成内容や言語適合性も変わり得ることが観測された。

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
- Method input: dedicated workflow内の固定3-card input
- held card: `c-held`
- SOZA Method mapping: current `livemethodintegration`

model artifact digestは、Actual Model Artifact Exchange E3b Run `33670697154`でOllama `0.32.14`から実際に観測した`qwen2.5:0.5b`のartifact identityである。

A / Bのdigestが一つのrun内で互いに等しいだけでは固定条件成立とみなさない。両方がこの期待digestに一致することを要求する。将来同じmodel tagが別artifactを指した場合は、実験条件が変わったものとして停止する。

交換するのはOllama runtime versionだけとする。

- revision A: `0.32.13`
- revision B: `0.32.14`

## Pinned runtime artifacts

installerによるglobal installは使わず、GitHub ReleaseのLinux amd64 archiveを固定SHA-256で取得し、別々の一時directoryへ展開してbinaryを直接起動する。

- `v0.32.13 / ollama-linux-amd64.tar.zst`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- `v0.32.14 / ollama-linux-amd64.tar.zst`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

2026-09-03の静的再監査では、両digestがOllama公式GitHub Release metadataの各asset digestと一致することを確認した。

また、公式Linux installerはarchiveをinstall rootへ展開し、その配下の`bin/ollama`を利用する構成である。dedicated workflowの`${root}/bin/ollama`という展開前提はこのlayoutと整合する。

ただし、これらはsource identity / workflow designの確認であり、runtime交換をactualに実行したExecutable Evidenceではない。

## Exact Realization Reference

既存のKJ Atlas live mappingは、従来`LogicalReference`だけをRealization参照として受け取っていた。

本Issueでは後方互換なoptional経路として`ApplyGroupingInput.RealizationReference`を追加した。

- 未指定の場合
  - M1a / M1bの従来どおりlogical-only Realization Referenceを保持する。
- 指定した場合
  - `method_application.realization_ref`へ`semanticruntime.Reference`を保持する。
  - logical identityが`RealizationRef`と一致しなければ、canonical stateを変更せず拒否する。

Exact Bindingを作るMethod Realization payloadと、portable Semantic Interchangeへ格納するRealization recordは同じ生成経路を使う。bindingだけを別途再生成してpayloadとずれる二重実装にはしていない。

## Required experiments

### E1 — runtime artifact identity

両runtime archiveを固定URLから取得し、固定SHA-256を検証する。

PASS条件:

- Aが`0.32.13`として起動する。
- Bが`0.32.14`として起動する。
- archive digestが固定値と一致する。

### E2 — same pinned model artifact

両runtimeで`qwen2.5:0.5b`を取得し、APIが返すmodel digestを確認する。

PASS条件:

- A / Bのmodel digestが同一である。
- A / Bのmodel digestが、固定した期待artifact identity `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`と一致する。
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

runtime versionとruntime artifact digestを含むMethod Realization documentからExact Bindingを決定的に作る。

PASS条件:

- A / Bは同じlogical Realizationを持つ。
- A / BはいずれもExact Bindingである。
- A / BのExact Bindingは異なる。

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

二つのMethod Realization revision recordと二つのApplication recordを、一つのSemantic Interchangeへ格納する。

PASS条件:

- `semanticruntime.LoadInterchange`がbundle-local Exact Binding検証を通過する。
- Application AのExact Referenceをrevision Aへ解決できる。
- Application BのExact Referenceをrevision Bへ解決できる。

negative controlとしてApplication Bのdigestを存在しないrevisionへ差し替える。

PASS条件:

- `LoadInterchange`がnegative bundleを拒否する。

```text
exact-looking reference retained
  != historical revision resolvable

Application exact reference
  + matching Realization revision record
  + bundle-local Exact Binding validation
  → portable historical reconstruction boundary
```

### E7 — no semantic promotion

runtime交換後もMethod outputをRecommendation / Decisionへ自動昇格しない。

### E8 — CI trigger responsibility

scenario-local testと共有依存を分ける。

runtime交換専用testだけの変更では、Runtime Version Exchange E3bだけを外部Method実証として選び、M1a / M1b / actual二モデル交換を自動対象にしない。

model artifact交換専用testだけの変更では、Actual Model Artifact Exchange E3bを選び、Runtime Version Exchange E3b / M1a / M1bを自動対象にしない。

一方、runtime交換が直接依存する共有packageを変更した場合はRuntime Version Exchange E3bを再選択する。

Runtime Version Exchange E3bのcurrent trigger対象には次を含める。

- `runtime/go/livemethodintegration/**`
- `!runtime/go/livemethodintegration/model_artifact_exchange_test.go`
- `runtime/go/interactionprobe/**`
- `runtime/go/semanticruntime/**`
- `runtime/integration/e3b_m1b_ollama_adapter.py`
- `runtime/go/go.mod`
- `runtime/go/go.sum`
- workflow自身

この考え方はISSUE-000069 / PR #61で整理した、scenario-local差分と共有依存を分ける原則に合わせる。

## Existing Evidence

### Exact Reference mapping / fixed model artifact source

PR #63の先行head `765eb189f97d7dba402cec864960cecb3a5a91a6`では、Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`がactualに完走した。

このrunでは次がsuccessした。

- actual model artifact exchange
- `qwen2.5:0.5b` model digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`のactual観測
- model prompt digest `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`のactual観測
- `go test ./livemethodintegration -count=1`
- Exact Reference保持test
- logical identity不一致時の無変更失敗test
- `TestLiveKJAtlasActualModelArtifactExchangePreservesHistoricalApplication`

したがって、Exact Realization Reference mapping自体にはExecutable Evidenceがある。また、共有mapping変更後も既存actual二モデル交換のScoped Executable Evidenceは回帰していない。runtime交換workflowでは、このrunで観測した0.5b model digestを期待artifact identityとして固定した。

これはruntime version交換のExecutable Evidenceではない。

### scenario-local trigger selection

runtime交換専用差分だけだったhead `55bfcfb45e6e19210e925923565700a075ab006d`では、Runtime Version Exchange E3bだけが外部Method実証として生成され、M1a / M1b / actual二モデル交換は生成されなかった。

さらにPR #67では、`model_artifact_exchange_test.go`だけへ説明コメントを加えたhead `e8c85dc8b3de41aff6700e1a2bab144140152609`から次だけが生成された。

- Actual Model Artifact Exchange E3b — Run `33697970020`
- Semantic Runtime Conformance — Run `33697970044`

Runtime Version Exchange E3b / M1a / M1bは生成されなかった。

これにより、runtime交換専用testとmodel artifact交換専用testの双方について、scenario-localな責務分離をrun生成レベルで確認した。PR #67はmergeせず閉じている。

### shared dependency trigger selection

PR #66では、`semanticruntime`だけを変更する一時probe head `2144af136d230cd1ca6a8db733caae222b67f64b`からRuntime Version Exchange E3b Run `33696752851`が生成された。

したがって、共有`semanticruntime`変更時にruntime交換workflowを取りこぼさないこともrun生成レベルで確認済みである。PR #66はmergeせず閉じている。

### Local Package Artifact boundary

PR #61でLocal Package Artifactのtriggerを実build依存へ限定した。

PR #63の`livemethodintegration`差分ではLocal Package Artifactが生成されず、PR #65の`semanticruntime`差分では生成された。package artifactのtrigger境界とruntime交換Evidenceは別に扱う。

## Current implementation state

PR #63はPR #61 head `32a1cabeb6c66fd8d4f37e22c1e2cbfc142ebc43`をbaseとしている。

runtime交換workflowは、PR #61で確立したtrigger原則に合わせ、共有依存を取りこぼさずscenario-local test同士を不要に連鎖させない構成へ整理した。

実験実装は次を含む。

- fixed runtime artifact acquisition
- runtime artifact SHA-256 verification
- same model storage
- model tagに加え、既知のactual model digestへの固定
- A / Bそれぞれでの期待model digest検証
- prompt digest comparison
- actual inference countersの検証
- Exact Realization revision生成
- Application A / BへのExact Reference保持
- historical Application / Provenance / output不変性検査
- portable Semantic Interchange reconstruction
- unknown revision digestのnegative control
- Recommendation / Decisionへの非昇格検査

## Current Evidence state

current trigger整理後のPR #63 head `f4f504948f3af37554c2c849c82fd7cfebbf21c2`では、Runtime Version Exchange E3b Run `33697884915` / Job `100470627125`が生成された。

GitHub APIのjob metadataでは次を確認した。

- labels: `ubuntu-latest`
- `runner_id = 0`
- `runner_name = ""`
- `runner_group_id = 0`
- `runner_group_name = ""`
- `steps = []`
- 作成から約3秒でfailure終了

job log blobは生成されておらず、log取得要求も404となる。

このため、今回のfailureはworkflow本文のstepへ到達したtest failureとは扱わない。

また、PR #61の軽量Plan integrity Run `33696109434`も明示的に再実行したが、再実行Job `100470021380`は`steps=[]`のまま終了した。runner利用可能性は依然として回復済みとは扱えない。

公開GitHub Statusでは確認時点でActionsはOperationalだったため、今回の現象をGitHub全体障害と断定するEvidenceもない。account / allocation / service-side conditionを含め、具体原因は未確定のまま保持する。

現時点では次のとおりである。

```text
workflow definition
  = implemented / accepted by GitHub

pinned runtime artifact identity against official release metadata
  = statically verified

runtime archive layout assumption
  = statically cross-checked with official installer

qwen2.5:0.5b expected model artifact identity
  = actual digest observed in Run 33670697154 and pinned in workflow

pinned model digest enforcement
  = implemented / accepted by GitHub, not yet runner-executed

scenario-local workflow selection
  = confirmed in both directions

shared semanticruntime trigger selection
  = confirmed in PR #66

Exact Realization Reference mapping
  = Executable Evidence available in Run 33670697154

existing actual two-model exchange after shared mapping change
  = Scoped Executable Evidence re-confirmed in Run 33670697154

runtime 0.32.13 / 0.32.14 artifact acquisition inside this workflow
  = Not Yet Verified

actual runtime-version exchange inference
  = Not Yet Verified

same pinned model digest / same prompt digest across runtime versions
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

CI failureは修正対象だがpushを停止する条件にはしない。runner未割当を含む赤いrunが残っていても、原因調査、実験条件の強化、修正commitは通常どおりpushする。merge、Evidence確定、IssueのResolved判定に必要なgateは別に扱う。

## Requirement / Contract assessment

現時点では新しいStable Requirement / Acceptance Scenario / Universal Contract fieldを追加しない。

actual実証後に次へ再照合する。

- REQ-0001
- REQ-0004
- REQ-0021
- SCN-0005
- SCN-0015

既存Requirement / Contractで観測結果を十分に表せる場合はNo Changeとする。

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

## Resolution

Open中。

次をすべて満たした時点でResolvedとする。

1. fixed runtime artifact A / Bをactual runner上で取得・digest検証できる。
2. A / Bのruntime versionをactual binaryから確認できる。
3. A / B双方のmodel digestが固定した期待artifact identityと一致し、same prompt digestもactual executionで確認できる。
4. 両runtimeでactual inferenceが成立する。
5. Application A / Bがsame logical / different Exact Realization revisionを保持する。
6. Application AのReference / Provenance / outputがB追加後も不変である。
7. portable reconstructionとunknown revision negative controlがPASSする。
8. Recommendation / Decisionへの自動昇格がない。
9. current trigger setで必要なworkflow回帰がrunner上でsuccessする。
10. Requirement / Contract再照合と自然な日本語最終監査を行う。

trigger選択性はrun生成レベルで確認済みだが、actual runtime exchangeが未実行のためResolvedにはしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revisionを交換するとhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを参照するbundleを受理する。
- model tagが固定した期待artifact identityと異なるartifactを指し、model artifactが交換軸へ混入する。
- promptが交換軸へ混入する。
- runtime固有情報をUniversal semanticsへ先取りする。
- 共有依存変更時にruntime交換workflowが選択されない。
- model artifact交換専用testだけの変更でruntime交換workflowが再び選択される。
- runtime交換successをmodel / KJ成果品質やE4へ過大評価する。

## Natural Japanese review

ISSUE-000067 / ISSUE-000068、Cognitive Method Contract、current live mapping、ISSUE-000069のCI trigger原則を再照合した。

「実現機構そのものの違い」と「同一実現機構のversion差」を分け、後者を一つのlogical Realizationに属するhistorical revisionとしてExact Bindingで固定する構造を維持している。

また、「同じmodel」をtag名や一回のA / B比較だけで済ませず、既にactual runで観測したmodel digestを期待artifact identityとして固定した。これにより、runtimeだけを交換するという実験条件をrunを跨いでも明示できる。

CIについては、runtime交換専用test、model artifact交換専用test、共有依存をそれぞれ分けた。PR #66 / #67によって正側と負側のrun生成を実測し、検査本文を弱めずにtrigger責務だけを精密化している。

さらに、`failure`という表示だけでrepository test failureと読まないよう、`runner_id=0`、`steps=[]`、log未生成という観測事実まで明示した。公開statusに障害表示がないことから具体原因を逆に推定することもせず、原因は未確定のまま保っている。

固定artifactのsource identity確認、Exact Reference mappingの既存Executable Evidence、trigger選択、runner未割当、runtime交換本体のactual未実証を一つの成功や失敗へまとめていない。

意味、規範強度、Evidence強度、未検証範囲を変えず、観測済みの事実、実装済みの設計、runner上で未確認の事項を自然に読み分けられるよう全文を再ドラフトした。