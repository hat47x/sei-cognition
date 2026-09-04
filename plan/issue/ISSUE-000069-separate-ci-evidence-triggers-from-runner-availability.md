# ISSUE-000069: CI実証の自動起動責務とrunner利用不能を分離する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Product Milestone: **PMS-06 / PMS-07**  
Updated: 2026-09-03

## Goal

GitHub Actionsのrunner割当など、repositoryの外側にある実行環境の問題と、SOZA repository内の検査設計上の問題を分けて扱えるようにする。

このIssueを開始した時点では、actual external Providerやactual modelを動かすworkflowを自動起動していた。そのため、PR差分の意味に応じて必要な実証だけを選び、runner未割当をSOZAのtest failureやProduct Evidence failureへ読み替えないことが中心課題だった。

現在はPR #70でGitHub Actions workflow群を`develop/v0.2.0`から外している。したがって、本Issueの最終状態では「current workflowを常時運用すること」ではなく、**実証責務と外部実行基盤の可用性を分離する原則を正本へ残し、将来Actions等を再導入するときの条件を明確にすること**を完了条件とする。

## Background

PR #60統合後、複数のGitHub Actions jobがほぼ同時にfailureした。通常のtest failureと異なり、問題になったjobの多くはcheckoutやtestへ到達せず、`runner_id = 0`、`steps = []`のまま終了していた。

同じ時刻帯には`hat47x/tei-platform`でも類似の現象が見られた。そのため、SOZAのtest本文が失敗したとは判断しなかった。

一方、調査を進めるとrepository側にも改善点があった。外部実証workflowの`pull_request.paths`が責務より広く、scenario-localなtest変更だけでも複数の重い実証を選ぶ場合があった。また、Local Package Artifactも実際のbuild依存より広い範囲を監視していた。

そこで、次の二つを別々に扱った。

```text
runner assignment / hosted execution availability
  = repository外の実行条件

which verification should run for a semantic change
  = repository内の検査責務
```

## Established principles

### 1. step開始前のfailureはtest failureではない

jobが生成されても`runner_id = 0`、`steps = []`のまま終了した場合、repository内の検査本文を実行したFAILとは扱わない。

```text
workflow run created
  != runner assigned
  != steps executed
  != test failed
  != Product Evidence failed
```

### 2. `pull_request.paths`はPR全体の差分で判定される

`pull_request.paths`は最新commitだけを見る仕組みではない。PRのbaseからheadまでに残る差分全体が判定対象になる。

したがって、runtime変更を含むPRへ後から文書commitだけを追加しても、PR全体にruntime差分が残っていれば対応workflowは対象になり得る。

この性質を「文書commitなら必ず重い実証が走らない」と説明しない。

### 3. scenario-localな変更と共有依存を分ける

PR #61では、外部実証の起動範囲をscenario-localなtestと共有実装へ分けた。

例:

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

scenario-localな変更だけなら、その実証だけを対象にする。一方、共有mappingや直接依存する共有packageが変わった場合は、依存する実証を取りこぼさない。

### 4. Local Package Artifactは実際のbuild依存を見る

当時の`cmd/soza-package-probe`は、主に次へ依存していた。

```text
cmd/soza-package-probe
  → packagingprobe
  → semanticruntime
```

そのため、`runtime/go/**`全体を無条件に再build対象とするのではなく、package artifactへ実際に影響する範囲へ起動条件を限定した。build本文やAcceptanceは弱めていない。

### 5. CI failureはpush停止条件ではない

CIや外部実行環境のfailureは観測・修正対象だが、後続の調査や修正commitをpushできなくする条件にはしない。

```text
commit
  → push
  → available verificationで観測
  → 必要なら修正
  → 再push
```

merge、release、Evidence確定に必要なgateは、通常の開発pushとは別に定義する。

## Evidence from the historical Actions period

### scenario-local selection

PR #63のruntime交換固有差分だけだったhead `55bfcfb45e6e19210e925923565700a075ab006d`では、Runtime Version Exchange E3bだけが対象になり、M1a / M1b / actual二モデル交換は対象にならなかった。

### shared mapping selection

`kj_atlas.go`のような共有mappingを変更した場合は、依存するM1a、M1b、actual二モデル交換が再び選ばれた。これは共有責務に対する意図した回帰選択として扱った。

### docs-only independent PR

PR #64では、差分を`plan/document_review_registry.yaml`だけに限定した。Plan integrity Run `33672679058`だけが生成され、actual external executionやLocal Package Artifactは生成されなかった。

Plan integrity Job `100389847417`自体は`steps = []`で終了したため、Plan integrity本文がPASSしたとは扱っていない。

### Local Package Artifact dependency selection

workflow自身を変更した場合はLocal Package Artifactが選ばれ、`livemethodintegration`だけの差分では選ばれず、`semanticruntime`差分ではRun `33695770498`が生成された。正側・負側の選択をrun生成レベルで確認した。

### shared `semanticruntime` dependency selection

PR #65では`semanticruntime`だけを変更するprobeを行い、Semantic Runtime Conformanceに加えて、直接依存する各actual実証とLocal Package Artifactが選ばれることを確認した。

PR #65はtrigger選択の確認だけを目的としたため、mergeせず閉じた。

### runner assignmentの実例

Run `33670697154` / Job `100383296117`ではGitHub-hosted runnerが実際に割り当てられ、actual model実行、`go test ./livemethodintegration -count=1`、historical Application保持testまで全stepがsuccessした。

この実例があるため、hosted runnerが常に利用不能だったとは扱わない。

### cross-OS allocation probe

一方、PR #68の最小probeではcheckoutもrepository testも行わず、Ubuntu / Windows / macOSの3種類のhosted runnerへ1 stepだけを要求した。

Run `33700247624`では3 jobすべてがassignment前に終了した。

- Ubuntu Job `100477777560`: `runner_id = 0`, `steps = []`
- Windows Job `100477777950`: `runner_id = 0`, `steps = []`
- macOS Job `100477777990`: `runner_id = 0`, `steps = []`

これにより、当時の現象をLinux固有、Ollama固有、SOZA test本文固有とする説明は弱くなった。ただし、billing、quota、repository policy、GitHub service-side condition等の具体原因は確定していない。

PR #68は診断目的だけで使用し、workflowを`develop/v0.2.0`へ統合していない。

## Current baseline after PR #70

PR #70では、散在していたv0.2系の非workflow成果をcurrent `develop/v0.2.0`へ回収する一方、`.github/workflows`の14本を削除した。

この変更により、旧Resolution条件にあった「PR #61で統合したcurrent trigger setをrunner上で再回帰する」という前提そのものがcurrent repositoryからなくなった。

重要なのは、未確認だった回帰を「successした」と読み替えないことである。

```text
old workflow regression
  = not completed

old workflow set removed from current baseline
  → old regression condition is no longer applicable to current baseline
  != regression success retroactively proven
```

したがって、当時のtrigger設計とrunner診断はhistorical Evidenceとして保持し、現在の開発規約ではworkflow / runnerをProduct ValueやEvidence意味の正本にしない。

## Resolution

本IssueをResolvedとする。

確認した内容は次のとおり。

1. runner未割当とrepository test failureを分離した。**完了**
2. `pull_request.paths`がPR全体差分で判定されることを文書化した。**完了**
3. scenario-local変更で無関係なactual実証を選ばない境界をrun生成レベルで確認した。**完了**
4. shared mapping変更では依存するactual実証を選ぶことを確認した。**完了**
5. docs-only独立PRではactual external executionを選ばないことをPR #64で確認した。**完了**
6. Local Package Artifactを実際のbuild依存へ寄せ、正側・負側の選択を確認した。**完了**
7. `semanticruntime`共有依存の正側選択をPR #65で確認した。**完了**
8. runner未割当をSOZA Product / Evidence failureとして誤記しない境界を確立した。**完了**
9. cross-OS probeにより、当時のfailureが3 OS共通でrunner assignment前に発生していたことを確認した。**完了**
10. PR #61由来のworkflow群をrunner上で全面回帰する条件は、PR #70で当該workflow群をcurrent baselineから外したため**現行方針では非適用**とする。未実行だった回帰をPASSへ読み替えない。

このResolutionはGitHub-hosted runnerの具体的な障害原因を解明したという意味ではない。また、将来Actionsを再導入した場合に旧trigger設計がそのまま妥当だと保証するものでもない。

## Reopen conditions

次の場合は再開する。

- GitHub Actionsまたは同等の自動実証基盤をcurrent baselineへ再導入する。
- runner / external execution failureをProduct Evidence failureと混同する運用が再発する。
- 自動実証を導入した際、scenario-local変更で無関係な重い実証が選ばれる。
- 共有実装変更で必要な実証が選ばれない。
- Packagingの実依存とartifact検査の起動範囲が再び乖離する。
- push、merge、release、Evidence確定のgateが無自覚に同一視される。
- CI使用量を減らすためにProduct Value、Acceptance、検査本文を弱める変更が入る。
- historical cross-OS Evidenceから、根拠なく特定のbilling / quota / GitHub障害原因を断定する。

## Current verification policy

current baselineでは、検証手段を意味上の正本にしない。

```text
repository tool / local execution / external runner / future CI
  = verification mechanisms

Product Value / Requirement / Contract / Evidence claim
  = semantic authority
```

GitHub Actionsを使わない期間も、repository同梱test、fixture、checker、保存Evidenceを保守する。actual外部実行が必要な主張は、利用可能な実行環境で実際に確認できた高さまでだけ記録する。

## Natural Japanese review

当初の文書は、GitHub Actionsをcurrent baselineとして運用する前提で、triggerの精密化とrunner復旧後の全面回帰を一続きの完了条件にしていた。その後PR #70でActions自体をcurrent baselineから外したため、前提の変化を本文へ反映した。

旧workflowについて確認できたtrigger選択、実際に完走したRun `33670697154`、3 OSともassignment前に終了したcross-OS probeは、いずれも当時の観測として残した。一方、未実行の全面回帰を成功扱いにはしていない。

現在は「CIを使うかどうか」と「何を検証しなければならないか」を分け、pushを止めずに検証と修正を進める開発規約へ接続した。意味、Evidence強度、未確認事項を変えず、現在のrepository方針として自然に読めることを最重要視して全文を再ドラフトした。