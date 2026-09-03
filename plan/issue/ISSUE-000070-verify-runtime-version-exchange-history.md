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
- runtime / model固有情報は、必要なProvenance / realization-local metadataとして保持する。
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

A / Bのdigestが一つのrun内で互いに等しいだけでは固定条件成立とみなさない。両方がこの期待digestに一致することを要求する。同じmodel tagが将来別artifactを指した場合は、実験条件が変わったものとして停止する。

交換するのはOllama runtime versionだけとする。

- revision A: `0.32.13`
- revision B: `0.32.14`

## Pinned runtime artifacts

installerによるglobal installは使わず、GitHub ReleaseのLinux amd64 archiveを固定SHA-256で取得し、別々の一時directoryへ展開してbinaryを直接起動する。

- `v0.32.13 / ollama-linux-amd64.tar.zst`
  - SHA-256: `0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1`
- `v0.32.14 / ollama-linux-amd64.tar.zst`
  - SHA-256: `c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f`

2026-09-03の静的再監査では、両digestがOllama公式GitHub Release metadataの各asset digestと一致することを確認した。また、公式Linux installerの展開方式と、dedicated workflowが利用する`${root}/bin/ollama`というlayout前提が整合することを確認した。

これはsource identity / workflow designの確認であり、runtime交換をactualに実行したExecutable Evidenceではない。

## Exact Realization Reference

既存のKJ Atlas live mappingへ、後方互換なoptional経路として`ApplyGroupingInput.RealizationReference`を追加した。

- 未指定の場合
  - M1a / M1bと同じlogical-only Realization Referenceを保持する。
- 指定した場合
  - `method_application.realization_ref`へ`semanticruntime.Reference`を保持する。
  - logical identityが`RealizationRef`と一致しなければ、canonical stateを変更せず拒否する。

Exact Bindingを作るMethod Realization payloadと、portable Semantic Interchangeへ格納するRealization recordは同じ生成経路を使う。bindingだけを別途再生成してpayloadとずれる二重実装にはしていない。

この共有mappingは、Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`で`go test ./livemethodintegration -count=1`を含めactualにPASSしている。したがってExact Reference mapping自体にはExecutable Evidenceがある。

ただし、この既存Evidenceをruntime version交換の成立証明には使わない。

## Artifact guard

runtime交換のlive testを開始する前に、Go側でも実際の実験条件を再確認する。

`runtime_version_artifact_guard_test.go`は、`SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1`のときだけ次を検査する。

- `_external/kj-atlas`のactual checkout commitが固定commitと一致する。
- runtime A / Bのversion logが、それぞれ`0.32.13` / `0.32.14`を示す。
- 取得済みruntime archiveのSHA-256が固定値と一致する。

通常のunit testではexternal runtimeを要求しない。

さらに`runtime_version_artifact_guard_unit_test.go`で、external runtimeを使わず次を制御する。

- exact version tokenを受理する。
- `0.32.13`と`0.32.130`のようなnumeric suffixを取り違えない。
- exact artifact digestを受理する。
- artifact digest mismatchを拒否する。

新規unit test fileについては`gofmt -d`で差分がないことを確認済みである。package全体のrunner-backed実行は、runner利用可能性の回復後に確認する。

## Required experiments

### E1 — runtime artifact identity

両runtime archiveを固定URLから取得し、固定SHA-256を検証する。

PASS条件:

- Aが`0.32.13`として起動する。
- Bが`0.32.14`として起動する。
- archive digestが固定値と一致する。

### E2 — same pinned model artifact

両runtimeで`qwen2.5:0.5b`を利用し、APIが返すmodel digestを確認する。

PASS条件:

- A / Bのmodel digestが同一である。
- A / Bのmodel digestが、固定した期待artifact identity `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`と一致する。
- model tagだけで同一性を推論しない。

A / Bでは同じ`OLLAMA_MODELS`を利用する。これはmodel artifactを交換軸から外し、同じmodel storageを異なるruntime binaryで読み、推論できることを見るためである。各runtimeから`ollama pull`と`/api/tags`の確認を行い、固定digestと一致しない場合は停止する。

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

negative controlとしてApplication Bのdigestを存在しないrevisionへ差し替え、`LoadInterchange`が拒否することを要求する。

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

- runtime交換専用testだけの変更
  - Runtime Version Exchange E3bを選ぶ。
  - M1a / M1b / actual二モデル交換を自動対象にしない。
- model artifact交換専用testだけの変更
  - Actual Model Artifact Exchange E3bを選ぶ。
  - Runtime Version Exchange E3b / M1a / M1bを自動対象にしない。
- runtime交換が直接依存する共有packageの変更
  - Runtime Version Exchange E3bを再選択する。

Runtime Version Exchange E3bのtrigger対象には次を含める。

- `runtime/go/livemethodintegration/**`
- `!runtime/go/livemethodintegration/model_artifact_exchange_test.go`
- `runtime/go/interactionprobe/**`
- `runtime/go/semanticruntime/**`
- `runtime/integration/e3b_m1b_ollama_adapter.py`
- `runtime/go/go.mod`
- `runtime/go/go.sum`
- workflow自身

### E9 — Evidence bundle preservation

actual runtime交換の結果を一時的なActions logだけに閉じない。

workflow artifact `runtime-version-exchange-${run_id}-${run_attempt}`へ、巨大なruntime archive本体を除いて次を保存する。

- fixed experiment identity
  - workflow run / attempt
  - checked-out SOZA commit
  - KJ Atlas source commit
  - runtime A / B version
  - runtime A / B archive SHA-256
  - expected model digest
  - `qualityJudgement = not_evaluated`
- Method request
- A / B runtime version log
- A / B model digest / tags
- A / B inference Evidence
- A / B KJ Atlas result
- Adapter / KJ Atlas / Ollama log

`if: always()`で、途中失敗時にもそこまで生成されたファイルを可能な範囲で残す。

```text
Evidence bundle preserved
  = actual runの入力・条件・出力へ戻れる
  != runtime exchange PASS
  != output quality satisfied
```

artifactが存在すること自体をEvidence成立へ昇格させない。実験が途中で停止した場合は、欠落ファイルも含めてそのrunの状態として読む。

## Existing Evidence

### Exact Reference mapping / fixed model artifact source

Actual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`はrunner上でactualに完走した。

このrunでは次がsuccessした。

- actual model artifact exchange
- `qwen2.5:0.5b` full model digestのactual観測
- model prompt digest `cd3d5eeb64cddfbdce63d80b0451b19703f43bcd2d1b09d7188f6bd4d7de2d33`のactual観測
- `go test ./livemethodintegration -count=1`
- Exact Reference保持test
- logical identity不一致時の無変更失敗test
- historical Application保持test

このrunはExact Reference mappingとmodel artifact identityの入力Evidenceとして使うが、runtime version交換のExecutable Evidenceへは昇格させない。

### scenario-local trigger selection

runtime交換専用差分だけだった先行headでは、Runtime Version Exchange E3bだけが外部Method実証として生成され、M1a / M1b / actual二モデル交換は生成されなかった。

PR #67では`model_artifact_exchange_test.go`だけを変更するprobeを行い、Actual Model Artifact Exchange E3bとSemantic Runtime Conformanceは生成された一方、Runtime Version Exchange E3b / M1a / M1bは生成されなかった。

したがって、runtime交換専用testとmodel artifact交換専用testの双方について、scenario-localな責務分離をrun生成レベルで確認済みである。

### shared dependency trigger selection

PR #66では`semanticruntime`だけを変更するprobeからRuntime Version Exchange E3bが生成された。共有dependencyの正側選択もrun生成レベルで確認済みである。

### PR #61 integration

CI trigger責務を整理したPR #61は、2026-09-03に`develop/v0.2.0`へmerge commit `4b2609b7fd7906467e8cdf59805ce07a710b2f6a`として統合した。

本PRもそのdevelop基線をbranch履歴へ取り込み、runtime交換固有差分だけを保持している。

## Current implementation state

実装済みの範囲は次である。

- fixed runtime artifact acquisition
- runtime artifact SHA-256 verification
- actual version log verification
- artifact guardとそのunit control
- same model storage
- known actual model digestへの固定
- A / Bそれぞれでの期待model digest検証
- prompt digest comparison
- actual inference countersの検証
- Exact Realization revision生成
- Application A / BへのExact Reference保持
- historical Application / Provenance / output不変性検査
- portable Semantic Interchange reconstruction
- unknown revision digestのnegative control
- Recommendation / Decisionへの非昇格検査
- partial failureを含むEvidence bundle preservation

## Current runner / Evidence state

GitHub-hosted runnerは現在も安定して割り当てられていない。

Evidence bundle追加後のRun `33699821956`、artifact guard unit control追加後のRun `33700013855`はいずれもworkflowとして生成されたが、jobはstep開始前に終了した。Run `33699821956`は個別再実行も行ったが、再実行attemptも`steps=[]`のまま終了した。

このため、赤いrunをworkflow本文やGo testのFAILとして扱わない。

```text
workflow definition
  = implemented / accepted by GitHub

pinned runtime artifact identity against official release metadata
  = statically verified

runtime archive layout assumption
  = statically cross-checked

qwen2.5:0.5b expected model artifact identity
  = actual digest observed in Run 33670697154 and pinned

scenario-local workflow selection
  = confirmed in both directions

shared semanticruntime trigger selection
  = confirmed

Exact Realization Reference mapping
  = Executable Evidence available in Run 33670697154

runtime artifact guard unit file formatting
  = locally checked with gofmt

runtime 0.32.13 / 0.32.14 artifact acquisition in this workflow
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

CI failureは修正対象だがpushを停止する条件にはしない。runner未割当を含む赤いrunが残っていても、原因調査、実験条件の強化、修正commitは通常どおりpushする。

一方、actual runtime exchangeのEvidence確定と本IssueのResolved判定はrunner-backed実行を必要とする。

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
9. Evidence bundleから実行identity、入力、A / Bの出力へ戻れる。
10. current trigger setで必要なworkflow回帰がrunner上でsuccessする。
11. Requirement / Contract再照合と自然な日本語最終監査を行う。

trigger選択性と実験harnessは整備済みだが、actual runtime exchangeが未実行のためResolvedにはしない。

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
- Evidence bundleの存在を実験成功や成果品質へ読み替える。
- runtime交換successをmodel / KJ成果品質やE4へ過大評価する。

## Natural Japanese review

ISSUE-000067 / ISSUE-000068、Cognitive Method Contract、current live mapping、ISSUE-000069で確立したCI trigger原則を再照合した。

「実現機構そのものの違い」と「同一実現機構のversion差」を分け、後者を一つのlogical Realizationに属するhistorical revisionとしてExact Bindingで固定する構造を維持している。

また、「同じmodel」をtag名や一回のA / B比較だけで済ませず、既にactual runで観測したfull model digestを期待artifact identityとして固定した。runtime archiveもversion名だけでなくSHA-256まで固定し、live test開始時にはGo側のartifact guardでも再確認する。

actual実験が成立した際には、その事実をActions logだけへ閉じず、実験identity、request、A / Bのversion・model identity・inference Evidence・resultへ戻れる小さなEvidence bundleを残す。ただしartifactの存在自体をruntime交換の成功や成果品質へ昇格させない。

CIについては、scenario-local test、model artifact交換専用test、共有依存を分けてrun生成を実測した。runner未割当についても、`failure`という表示だけからrepository test failureを推定せず、step未開始という観測事実を保持する。

固定artifactのsource identity、既存Exact Reference mapping Evidence、trigger選択、実装済みharness、runner上で未確認のactual runtime交換を一つの成功や失敗へまとめず、自然な日本語として読み分けられるよう全文を再ドラフトした。
