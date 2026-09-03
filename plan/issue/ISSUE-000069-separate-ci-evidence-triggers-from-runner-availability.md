# ISSUE-000069: CI実証の自動起動責務とrunner利用不能を分離する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Product Milestone: **PMS-06 / PMS-07**  
Updated: 2026-09-03

## Goal

GitHub Actionsのrunner割当など外部実行環境の問題と、SOZA repository内のworkflow設計上の問題を分けて扱える状態にする。

あわせて、外部Providerやactual modelを起動する実証workflowについて、**PRが最終的に含むどの意味変更に対して自動再実証が必要なのか**を明確にする。

目標は単純な実行回数削減ではない。次を同時に満たす。

- 文書だけの独立PRでは、actual external executionを無条件に起動しない。
- scenario-local testだけの変更では、無関係な実証を選ばない。
- 共有実装や、その実証が直接依存する共有Go packageを変更した場合は、必要な実証を確実に選ぶ。
- Local Reference Packageは、実際のbuild依存が変わったときに再検証する。
- runner未割当をrepository内のtest failureやProduct Evidence failureとして扱わない。

このIssueの完了条件は「CIを緑色に見せること」でも「workflow実行回数を最小化すること」でもない。GitHub Actionsのpath filter semanticsと実装依存を前提に、**PR差分の意味と検査責務を一致させること**である。

## Background

PR #60を`develop/v0.2.0`へ統合した後、複数のGitHub Actions workflowがほぼ同時にfailureした。

通常のtest failureであれば、checkout、setup、test等のstepが開始された後に失敗箇所を特定できる。しかしSOZA側で繰り返し観測したjobは、`Plan integrity`を含めてstepを一つも開始せず、再実行しても`steps=[]`のまま終了する状態だった。

同じ時刻帯には、別のprivate repositoryである`hat47x/tei-platform`でも同様にstep開始前で終了するjobが確認された。そのため、この現象をSOZA固有のtest regressionやworkflow本文の失敗とは判断しなかった。

一方、調査の過程でrepository側にもtrigger設計上の課題が見つかった。

第一に、外部実証workflowには対応する実装責務より広い`paths`が指定されており、ある実証だけに属するtestを追加しただけでM1a、M1b、actual二モデル交換など複数の重い実証が同時に対象になっていた。

第二に、`Local Package Artifact`は`runtime/go/**`全体を監視していた。しかし実際にbuildする`cmd/soza-package-probe`は`packagingprobe`と`semanticruntime`を利用し、`packagingprobe`も`semanticruntime`へ依存する。`livemethodintegration`等の変更だけでLocal Reference Packageを再buildするのは、実依存に対して広すぎた。

第三に、triggerを各integration packageだけへ狭めた初期修正では、逆に共有依存を取りこぼす可能性が生じた。実装を再監査すると、たとえば次の直接依存がある。

```text
livemethodintegration
  → interactionprobe
  → semanticruntime

liveintegration
  → provideradapter
  → semanticruntime

teiintegration
  → provideradapter
  → semanticruntime

externalintegration
  → externalartifact
  → provideradapter
  → semanticruntime
```

したがって、「自分のpackageだけを見る」ことも正しくない。scenario-localな差分は分離しつつ、共有実装と直接依存する共有packageはtriggerへ含める必要がある。

これらのrepository側課題とrunner割当問題は分けて扱う。

```text
runnerが割り当てられずstepを開始できない
  != SOZAのtest failure
  != Product Evidence failure

scenario-local testだけが変わった
  → その実証だけを自動対象にする

共有実装・直接依存する共有packageが変わった
  → 依存する実証を自動再実行する

文書だけの独立PR
  → actual external execution用pathsには一致させない

Local Reference Packageのbuild依存が変わった
  → Local Package Artifactを再検証する
```

## `pull_request.paths`の重要な制約

GitHub Actionsの`pull_request.paths`は最新commitだけではなく、**PRのbaseからheadまでの差分全体**を対象に判定される。

このため、runtime変更を既に含むPRへ後から文書commitだけを追加しても、PR全体にはruntime差分が残る。対応するworkflowは再び対象になり得る。

```text
文書だけの独立PR
  → runtime系pathsに一致しない
  → actual external workflowは自動対象にならない

runtime変更を含むPRへ文書commitを追加
  → PR全体ではruntime差分が残る
  → 対応するworkflowは引き続き対象になり得る
```

したがって、`paths`だけで「同じPRの後続文書commitでは重い実証を再実行しない」ことは保証できない。PR #61では、commit単位の実行最小化ではなく、PR全体が持つ意味変更と実証責務の一致を設計目標とする。

同一PR/refで古い実行が不要になった場合は`concurrency.cancel-in-progress`を利用する。ただし、これはPR全体のpath判定をcommit単位へ変える仕組みではない。

## Constraints

- runner未割当をCI successとして扱わない。
- workflowを単に無効化して赤い状態を隠さない。
- E3a、E3b-P1、E3b-P2、E3b-M1a、E3b-M1b、actual二モデル交換、Local Reference Packageで既に得られたEvidenceの意味や高さを変更しない。
- actual external execution、SOZA mapping、historical reconstruction、Release Gate、Local Package Artifactの検査本文を、実行量削減だけを理由に弱めない。
- `workflow_dispatch`等による明示的な再実証経路を必要なworkflowで残す。
- `pull_request.paths`をcommit単位のfilterとして説明しない。
- pathを狭める場合は、直接依存する共有packageまで確認し、必要な回帰を取りこぼさない。
- CI使用量やGitHub側の実行条件をUniversal Product Requirementへ持ち込まない。
- post-releaseのExecutable Evidenceをv0.2.0 supported scopeへ遡及的に追加しない。
- runner割当失敗の具体原因を、観測していないbilling、quota、budget、runner pool、GitHub障害等へ推定しない。

## Required scenarios / experiments

### E1 — step開始前failureを実行本文のFAILと分ける

jobが生成されても`steps=[]`のまま終了した場合、repository内の検査本文を実行したFAILとは数えない。

runnerが割り当てられstepが開始された場合だけ、以降のstep結果でworkflow本文を評価する。

### E2 — workflow定義とtriggerの受理

trigger変更を含むPRで、PR差分に応じたworkflow runが生成されることを確認する。

workflow定義・path選択と、runner上の実行結果を分けて記録する。

### E3 — scenario-local testの選択性

PR #63のruntime交換固有差分だけだったhead `55bfcfb45e6e19210e925923565700a075ab006d`で、次を確認した。

- Runtime Version Exchange E3b: **対象**
- M1a: **対象外**
- M1b: **対象外**
- Actual Model Artifact Exchange E3b: **対象外**

したがって、runtime交換専用testと既存Method実証の責務分離はrun生成レベルで確認済みである。

### E4 — 共有mapping変更時の依存実証選択

PR #63でExact Realization Reference対応を`kj_atlas.go`へ追加すると、M1a、M1b、actual二モデル交換が再び生成された。

`kj_atlas.go`は複数実証が利用する共有mappingであるため、この再選択は不要な連鎖起動ではなく、意図した回帰選択である。

### E5 — 文書だけの独立PR

PR #64をPR #61のheadから分岐し、差分を`plan/document_review_registry.yaml`だけに限定して検証した。

head `d292ce43298c537124739becb6963fdef848e39f`で生成されたworkflowはPlan integrity Run `33672679058`だけだった。次は生成されなかった。

- External Integration E3a
- External Integration E3b
- External TEI Integration E3b P2
- External Method Integration E3b
- External Model-backed Method E3b M1b
- Actual Model Artifact Exchange E3b
- Local Package Artifact

したがって、文書だけの独立PRではactual external executionとLocal Package Artifactを選択しないことを**run生成レベルで確認済み**である。

Plan integrity Job `100389847417`自体は`steps=[]`のまま終了したため、Plan integrity本文のsuccessとは扱わない。

### E6 — Local Package Artifactのbuild依存選択

`Local Package Artifact`がbuildする`cmd/soza-package-probe`のimportを確認した。

```text
cmd/soza-package-probe
  → packagingprobe
  → semanticruntime

cmd/soza-package-probe
  → semanticruntime
```

この実依存に合わせ、自動起動条件を次へ限定した。

- `runtime/go/cmd/soza-package-probe/**`
- `runtime/go/packagingprobe/**`
- `runtime/go/semanticruntime/**`
- `runtime/go/go.mod`
- `runtime/go/go.sum`
- `runtime/package/reference/**`
- `fixtures/contracts/v1alpha1/boundary/**`
- `.github/workflows/local-package-artifact.yml`

build、二重build一致、build identity、deterministic archive、checksum、展開後resumeの検査本文は変更していない。

正側・負側のpath選択も確認した。

- PR #61でworkflow自身を変更した場合: Local Package Artifactが生成された。
- PR #63の`livemethodintegration`差分: Local Package Artifactは生成されなかった。
- PR #65の`semanticruntime`差分: Local Package Artifact Run `33695770498`が生成された。

したがってbuild依存に対するtrigger選択はrun生成レベルで確認済みである。artifact build本文の再実行successはrunner復旧後に確認する。

### E7 — 共有Go dependencyの正側選択

初期のtrigger精密化では、integration packageそのものだけを主な対象にしていた。しかしimportをたどると、共有package変更を取りこぼす可能性があった。

そこでPR #61で次を追加した。

- E3a: `provideradapter/**`, `semanticruntime/**`
- E3b: `provideradapter/**`, `semanticruntime/**`
- TEI P2: `provideradapter/**`, `semanticruntime/**`
- M1a: `interactionprobe/**`, `semanticruntime/**`
- M1b: `interactionprobe/**`, `semanticruntime/**`
- actual二モデル交換: `interactionprobe/**`, `semanticruntime/**`

検査本文には変更を加えていない。

そのうえでPR #65をPR #61のheadから分岐し、`runtime/go/semanticruntime/ci_trigger_dependency_probe_test.go`だけを追加した。内容はpackage宣言と説明コメントだけであり、production semanticsは変更していない。

そのheadから次のrunが生成された。

- Semantic Runtime Conformance — `33695770360`
- Local Package Artifact — `33695770498`
- External Model-backed Method E3b M1b — `33695770472`
- External TEI Integration E3b P2 — `33695770629`
- External Integration E3a — `33695770369`
- External Integration E3b — `33695770446`
- External Method Integration E3b — `33695770625`
- Actual Model Artifact Exchange E3b — `33695770389`

これにより、`semanticruntime`という共有依存を変更したときに、直接依存するactual実証とLocal Package Artifactを取りこぼさないことを**run生成レベルで確認済み**である。

PR #65はtrigger probeとして目的を満たしたため、mergeせず閉じた。

### E8 — runner割当成立後の回帰

runnerが割り当てられたworkflowについて、既存検査本文が実際にsuccessすることを確認する。

最低限、PR #61の変更対象について次を確認する。

- External Integration E3a
- External Integration E3b
- External TEI Integration E3b P2
- External Method Integration E3b
- External Model-backed Method E3b M1b
- Actual Model Artifact Exchange E3b
- Local Package Artifact
- Release Candidate Gate
- Plan integrity

過去にはrunner割当が成立した実例がある。

PR #63の先行headではActual Model Artifact Exchange E3b Run `33670697154` / Job `100383296117`がrunnerへ割り当てられ、全stepがsuccessした。このrunではactual model実行、`go test ./livemethodintegration -count=1`、historical Application保持testまで成功している。

一方、その後は多くのjobが`steps=[]`のまま終了している。したがって、runner利用可能性を「過去も現在も全面停止」または「全面復旧」のどちらにも単純化しない。

### E9 — hosted runner labelを変えてallocation層を切り分ける

repository test本文、Ollama、Linux固有処理からrunner割当問題を切り離すため、一時PR #68で最小workflowを実行した。

workflowはcheckoutもrepository testも行わず、次の3種類のGitHub-hosted runnerについて、割当後にrunner OS / archを表示する1 stepだけを持つmatrixとした。

- `ubuntu-latest`
- `windows-latest`
- `macos-latest`

Run `33700247624`では、3 jobすべてが同じ時刻帯に生成されたが、約4秒でstep開始前に終了した。

- Ubuntu Job `100477777560`
  - `runner_id = 0`
  - `runner_name = ""`
  - `steps = []`
- Windows Job `100477777950`
  - `runner_id = 0`
  - `runner_name = ""`
  - `steps = []`
- macOS Job `100477777990`
  - `runner_id = 0`
  - `runner_name = ""`
  - `steps = []`

この観測により、現在の現象は少なくとも次だけでは説明できない。

- `ubuntu-latest`固有のrunner image問題。
- Linux shell固有の問題。
- Ollamaやmodel取得処理の問題。
- SOZA repository内のtest本文が失敗したこと。

3 OSで共通してrunner assignment前に終了しているため、個別OSのworkflow本文より上流にあるGitHub-hosted runnerの共通allocation条件、またはそれ以前の共通条件を疑う材料が増えた。

ただし、このEvidenceだけからbilling、spending limit、quota、repository policy、GitHub service-side condition等の具体原因を一つへ確定しない。

PR #68は診断だけを目的とし、観測後にworkflowファイルを削除して**mergeせずclose**した。したがって、diagnostic workflowは`develop/v0.2.0`へ入っていない。

```text
ubuntu + windows + macos
  all runner_id=0 / steps=[]

→ OS固有・Linux固有・repository test本文固有の説明は弱くなる
→ hosted runner allocationの共通条件を疑う材料が増える
!= specific root cause proven
```

## Deliverables

- `.github/workflows/external-integration-e3a.yml`
- `.github/workflows/external-integration-e3b.yml`
- `.github/workflows/external-tei-integration-e3b-p2.yml`
- `.github/workflows/external-method-integration-e3b.yml`
- `.github/workflows/external-model-method-integration-e3b-m1b.yml`
- `.github/workflows/actual-model-artifact-exchange-e3b.yml`
- `.github/workflows/local-package-artifact.yml`
- `.github/workflows/release-candidate.yml`
- 本Issue
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

## Current findings

2026-09-03時点で、workflow triggerの設計については次を確認できた。

```text
workflow trigger syntax accepted
  = confirmed

scenario-local trigger selection
  = confirmed

shared mapping trigger selection
  = confirmed

docs-only independent PR selection
  = confirmed in PR #64

Local Package Artifact dependency selection
  = positive / negative pathともrun生成レベルでconfirmed

shared semanticruntime dependency selection
  = confirmed in PR #65

historical GitHub-hosted runner assignment
  = actual success exists in Run 33670697154

current hosted runner allocation
  = unavailable in cross-OS probe for ubuntu / windows / macos

specific allocation root cause
  = unknown

full PR #61 regression on current trigger set
  = not yet confirmed
```

runner問題の切り分けは「不安定」という一語より具体化できた。過去にはactual runner assignmentが成立した一方、現在のcross-OS probeでは3 OSすべてがassignment前に終了している。

具体原因をbilling、budget、quota、runner pool、service-side condition等のいずれかへ断定するEvidenceはないため、原因は未確定のまま保持する。

## Resolution

Open中。

trigger設計とrunner切り分けについて、次を完了した。

1. 外部実証workflowの起動範囲をscenario-local変更、共有実装、直接依存する共有packageへ整理した。**完了**
2. actual executionの処理本文やEvidence強度を弱めていないことを差分監査した。**完了**
3. scenario-local testだけのPR差分では、無関係なactual external workflowが選択されないことを確認した。**完了**
4. shared mapping変更では、依存するactual external workflowが選択されることを確認した。**完了**
5. 文書だけの独立PRではactual external execution用pathsに一致しないことをPR #64で確認した。**完了**
6. Local Package Artifactについて、build依存の正側・負側選択を確認した。**完了**
7. `semanticruntime`共有依存変更時のactual実証選択をPR #65で確認した。**完了**
8. runner未割当期間やstep未開始failureをSOZA Product / Evidenceのfailureとして誤記していない。**完了**
9. checkoutやtestを持たないcross-OS probeで、Ubuntu / Windows / macOSすべてがrunner assignment前に終了することを確認し、OS固有・repository test本文固有の可能性を切り分けた。**完了**

残る条件は次である。

10. runner割当が成立した状態で、PR #61で統合したcurrent trigger setについて必要な回帰実行がsuccessしている。**未完了**

10を確認した時点でResolvedとする。

## Reopen conditions

Resolved後も、次の場合は再開する。

- triggerを狭めた結果、runtime / Adapter / fixture / 直接依存する共有packageの意味変更時に必要な実証が選択されない。
- scenario-local testだけの変更で無関係な重い実証が再び対象になる。
- 文書だけの独立PRでactual external workflowが無条件に対象になる。
- Local Package Artifactの実依存を変更したのにpackage workflowが対象にならない。
- 無関係なGo package変更だけでLocal Package Artifactが恒常的に対象になる。
- `workflow_dispatch`を含む再実証経路が失われる。
- release publicationに必要なpush / tag経路が起動しなくなる。
- CI使用量削減のために検証本文やAcceptanceが弱められる。
- runner環境の障害をProduct Evidenceの失敗として扱う運用が再発する。
- cross-OS allocation Evidenceを根拠なく特定のbilling / quota / GitHub障害原因へ読み替える。

## CI / verification

検証結果は必ず次を分けて記録する。

```text
workflow definition accepted
  != workflow selected by PR diff
  != job assigned to a runner
  != workflow checks passed
```

`pull_request.paths`はPR全体のbase→head差分で評価されるため、同一PR内の後続commitごとの非起動をAcceptanceにはしない。

runnerが割り当てられないrunでは、差分監査によって検査本文を弱めていないことを確認できる。ただし、この静的確認をCI successの代替Evidenceにはしない。

また、CI failureは修正対象だがpushを停止する条件とはしない。原因調査・修正・追加観測のためのcommitはpushし続け、merge / release / Evidence確定に必要なgateとは分ける。

## Natural Japanese review

当初は「文書だけを更新したcommitなら重いworkflowを再実行しない」という読み方ができる記述があったが、GitHub Actionsの`pull_request.paths`はPR全体の差分で判定されるため修正した。

さらに、単にpathを狭めるだけでは共有依存を取りこぼすことが分かったため、各実証のGo importをたどり、scenario-local test、共有mapping、`interactionprobe`、`provideradapter`、`semanticruntime`の責務を分け直した。PR #65で`semanticruntime`変更時の正側選択まで確認している。

Local Package Artifactについても「Goの変更なら全部再build」という粗い説明を避け、`soza-package-probe`から実依存をたどって起動範囲を整理した。

runner状態は「利用不能」から「復旧済み」へ単純に二値化していない。過去のRun `33670697154`ではactual workflowが完走した一方、PR #68の最小cross-OS probeではUbuntu / Windows / macOSのすべてがrunner assignment前に終了した。これにより、現在の現象をLinuxやSOZA test本文に帰属させる説明は弱くなったが、具体的な外部原因までは断定していない。

既存Evidenceの高さ、Release Evidence、Product Requirement、v0.2.0 supported scopeを変更せず、観測済みの事実、trigger設計、runner allocationの切り分け、runner上で未確認の事項を自然に読み分けられるよう全文を再ドラフトした。
