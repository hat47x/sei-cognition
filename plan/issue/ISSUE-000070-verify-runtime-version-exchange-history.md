# ISSUE-000070: model artifactを固定したruntime version交換後もMethod Applicationの履歴を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

同じCognitive Method、同じKJ Atlas source、同じMethod input、同じactual model artifactを使い、Ollama runtime versionだけを交換したときに、SOZAが先行Method Applicationの履歴を失わず保持できるかを実証する。

このIssueでは、runtime version差を別のlogical Method Realizationとして扱わない。同じ実現機構のhistorical revisionとして扱い、Cognitive Method Contractが既に持つExact Bindingで区別する。

```text
same Method Definition
same logical Method Realization
same KJ Atlas source
same Method input
same model artifact
same model prompt

Ollama 0.32.13
  = Exact Realization revision A

Ollama 0.32.14
  = Exact Realization revision B
```

確認したい中心命題は次である。

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

これにより、model交換とruntime revision交換を別の探索軸として扱う。

## Fixed conditions

次を固定する。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- KJ Atlas endpoint: `POST /ai/suggest-card-groups`
- model adapter: `runtime/integration/e3b_m1b_ollama_adapter.py`
- model: `qwen2.5:0.5b`
- Method input: dedicated workflow内の固定3-card input
- held card: `c-held`
- SOZA Method mapping: current `livemethodintegration`

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

ただし、これはsource identity / workflow designの確認であり、runtime交換をactualに実行したExecutable Evidenceではない。

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

### E2 — same model artifact

両runtimeで`qwen2.5:0.5b`を取得し、APIが返すmodel digestを比較する。

PASS条件:

- A / Bのmodel digestが同一である。
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
- 両Provenanceは同じmodel artifactを指す。
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

runtime交換専用testだけの変更では、M1a / M1b / actual二モデル交換を自動対象にしない。

一方、runtime交換testが直接依存する共有packageを変更した場合はruntime交換workflowを再選択する。

current trigger対象には次を含める。

- `runtime/go/livemethodintegration/**`
- `runtime/go/interactionprobe/**`
- `runtime/go/semanticruntime/**`
- `runtime/integration/e3b_m1b_ollama_adapter.py`
- `runtime/go/go.mod`
- `runtime/go/go.sum`
- workflow自身

この考え方はISSUE-000069 / PR #61で整理した、scenario-local差分と共有依存を分ける原則に合わせる。

## Existing Evidence

### Exact Reference mapping

PR #63の先行head `765eb189f97d7dba402cec864960cecb3a5a91a6`では、Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`がactualに完走した。

このrunでは次がsuccessした。

- actual model artifact exchange
- `go test ./livemethodintegration -count=1`
- Exact Reference保持test
- logical identity不一致時の無変更失敗test
- `TestLiveKJAtlasActualModelArtifactExchangePreservesHistoricalApplication`

したがって、Exact Realization Reference mapping自体にはExecutable Evidenceがある。また、共有mapping変更後も既存actual二モデル交換のScoped Executable Evidenceは回帰していない。

これはruntime version交換のExecutable Evidenceではない。

### scenario-local trigger selection

PR #63のruntime交換固有差分だけだったhead `55bfcfb45e6e19210e925923565700a075ab006d`では、Runtime Version Exchange E3bだけが外部Method実証として生成され、M1a / M1b / actual二モデル交換は生成されなかった。

scenario-local testの責務分離はrun生成レベルで確認済みである。

### Local Package Artifact boundary

PR #61でLocal Package Artifactのtriggerを実build依存へ限定した。

PR #63の`livemethodintegration`差分ではLocal Package Artifactが生成されず、PR #65の`semanticruntime`差分では生成された。package artifactのtrigger境界とruntime交換Evidenceは別に扱う。

## Current implementation state

PR #63は最新PR #61 head `32a1cabeb6c66fd8d4f37e22c1e2cbfc142ebc43`の直上へ再基線化した。

再基線化時にruntime交換workflowへ`interactionprobe/**`と`semanticruntime/**`を追加し、PR #61で確立した共有依存trigger原則へ揃えた。

実験実装は次を含む。

- fixed runtime artifact acquisition
- artifact SHA-256 verification
- same model storage
- model digest comparison
- prompt digest comparison
- actual inference countersの検証
- Exact Realization revision生成
- Application A / BへのExact Reference保持
- historical Application / Provenance / output不変性検査
- portable Semantic Interchange reconstruction
- unknown revision digestのnegative control
- Recommendation / Decisionへの非昇格検査

## Current Evidence state

現時点では次のとおりである。

```text
workflow definition
  = implemented

pinned runtime artifact identity against official release metadata
  = statically verified

runtime archive layout assumption
  = statically cross-checked with official installer

scenario-local workflow selection
  = confirmed at run-generation level

Exact Realization Reference mapping
  = Executable Evidence available in Run 33670697154

existing actual two-model exchange after shared mapping change
  = Scoped Executable Evidence re-confirmed in Run 33670697154

runtime 0.32.13 / 0.32.14 artifact acquisition inside this workflow
  = Not Yet Verified

actual runtime-version exchange inference
  = Not Yet Verified

same model digest / same prompt digest across runtime versions
  = Not Yet Verified

portable reconstruction using actual runtime A/B evidence
  = implemented, Not Yet Verified

runtime-version-exchange Scoped Executable Evidence
  = not available yet
```

GitHub-hosted runnerは、Run `33670697154`のように割当が成立した例がある一方、その後も多数のjobが`steps=[]`のまま終了している。runner未割当をruntime交換testのFAILとして扱わない。

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
3. same model digestとsame prompt digestをactual executionで確認できる。
4. 両runtimeでactual inferenceが成立する。
5. Application A / Bがsame logical / different Exact Realization revisionを保持する。
6. Application AのReference / Provenance / outputがB追加後も不変である。
7. portable reconstructionとunknown revision negative controlがPASSする。
8. Recommendation / Decisionへの自動昇格がない。
9. current trigger setで必要なworkflow回帰がrunner上でsuccessする。
10. Requirement / Contract再照合と自然な日本語最終監査を行う。

## Reopen conditions

Resolved後も次の場合は再開する。

- runtime revisionを交換するとhistorical ApplicationのExact Referenceが失われる。
- same logical RealizationのrevisionをExact Bindingで区別できない。
- portable bundle内でApplicationのExact Referenceを対応revisionへ解決できない。
- unknown revision digestを参照するbundleを受理する。
- model artifactまたはpromptが交換軸に混入する。
- runtime固有情報をUniversal semanticsへ先取りする。
- 共有依存変更時にruntime交換workflowが選択されない。
- runtime交換successをmodel / KJ成果品質やE4へ過大評価する。

## Natural Japanese review

ISSUE-000067 / ISSUE-000068、Cognitive Method Contract、current live mapping、ISSUE-000069のCI trigger原則を再照合した。

「実現機構そのものの違い」と「同一実現機構のversion差」を分け、後者を一つのlogical Realizationに属するhistorical revisionとしてExact Bindingで固定する構造を維持している。

また、固定artifactのsource identity確認、Exact Reference mappingの既存Executable Evidence、runtime交換本体のactual未実証を一つの成功へまとめていない。

CIについてもscenario-local testと共有依存を分け、run生成の成否をruntime compatibilityのEvidenceへ読み替えない。

意味、規範強度、Evidence強度、未検証範囲を変えず、観測済みの事実、実装済みの設計、runner上で未確認の事項を自然に読み分けられるよう全文を再ドラフトした。
