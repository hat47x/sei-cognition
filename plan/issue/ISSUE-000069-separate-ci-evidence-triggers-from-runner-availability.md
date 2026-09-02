# ISSUE-000069: CI実証の自動起動責務とrunner利用不能を分離する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Product Milestone: **PMS-06 / PMS-07**  
Updated: 2026-09-03

## Goal

GitHub Actionsのrunner割当など外部実行環境の問題と、SOZA repository内のworkflow設計上の問題を分けて扱える状態にする。

あわせて、外部Providerやactual modelを起動する実証workflowについて、**PRが最終的に含むどの意味変更に対して自動再実証が必要なのか**を明確にする。文書だけの独立PRでactual external executionを無条件に起動せず、scenario-local testだけの変更では無関係な実証を選ばず、共有実装を変更した場合は依存する実証を確実に選ぶ構成を目指す。

同じ原則をLocal Reference Packageにも適用する。package artifactをbuildする実際のGo依存と無関係なpackage変更で再buildせず、`soza-package-probe`の成立に必要な変更では確実に再検証する。

このIssueの完了条件は「CIを緑色に見せること」でも「workflow実行回数を最小化すること」でもない。runner未割当をsuccessとして扱わず、GitHub Actionsの実際のpath filter semanticsと実装依存を前提に、PR差分と検査責務を一致させる。

## Background

PR #60を`develop/v0.2.0`へ統合した後、複数のGitHub Actions workflowがほぼ同時にfailureした。

通常のtest failureであれば、checkoutやsetup、test等のstepが開始された後に失敗箇所を特定できる。しかし当初のSOZA側runでは、`Plan integrity`を含む対象jobがstepを一つも開始していなかった。再実行しても`steps=[]`のまま終了する状態が続いた。

同じ時刻帯には、別のprivate repositoryである`hat47x/tei-platform`でも複数jobが同様にstep開始前で終了していた。このため、当初の現象をSOZA固有のtest regressionやworkflow本文の失敗とは判断しなかった。

一方、調査の過程でrepository側にも二種類の粗さを確認した。

第一に、外部実証workflowには対応する実装責務より広い`paths`が指定されている箇所があり、ある実証だけに属するtestを追加しただけでも、M1a、M1b、actual二モデル交換など複数の重い実証が同時に対象になっていた。

第二に、`Local Package Artifact`は`runtime/go/**`全体を監視していたが、実際にbuildする`cmd/soza-package-probe`は`packagingprobe`と`semanticruntime`だけを利用し、`packagingprobe`も`semanticruntime`だけへ依存している。したがって`livemethodintegration`等の変更でLocal Reference Packageを再buildするのは依存関係に対して広すぎた。

これらとrunner割当問題は分けて扱う必要がある。

```text
runnerが割り当てられずstepを開始できない
  != SOZAのtest failure
  != Product Evidence failure

共有実装・Adapter・fixture・workflowの意味が変わった
  → 依存する実証を自動再実行する

特定実証だけのscenario-local testが変わった
  → その実証だけを自動対象にする

文書だけの独立PR
  → actual external execution用pathsには一致させない

Local Reference Packageのbuild依存が変わった
  → Local Package Artifactを再検証する

無関係なGo packageだけが変わった
  → Local Package Artifactを自動対象にしない
```

## `pull_request.paths`の重要な制約

GitHub Actionsの`pull_request.paths`は、最新commitだけではなく、**PRのbaseからheadまでの差分全体**を対象に判定される。

このため、runtime変更を既に含むPRへ後から文書commitだけを追加しても、PR全体にはruntime差分が残っている。対応するworkflowは再び対象になり得る。

```text
文書だけの独立PR
  → runtime系pathsに一致しない
  → actual external workflowは自動対象にならない

runtime変更を含むPRへ文書commitを追加
  → PR全体ではruntime差分が残る
  → 対応するworkflowは引き続き対象になる
```

したがって、`paths`だけで「同じPRの後続文書commitでは重い実証を再実行しない」ことは保証できない。PR #61では、**commit単位の実行最小化ではなく、PR全体が持つ意味変更と実証責務の一致**を設計目標とする。

同一PR/refで古い実行が不要になった場合は`concurrency.cancel-in-progress`を利用するが、これはPR全体のpath判定をcommit単位へ変える仕組みではない。

## Questions

1. 外部実証workflowを自動対象にすべき変更範囲は、どのruntime / Adapter / fixture / scenario-local test / workflowに限定できるか。
2. 文書だけの独立PRでは、既に成立したScoped Executable Evidenceをactual model取得によって毎回再実証する必要があるか。
3. 同一package内でも、共有実装と特定実証専用testの変更責務をどこまで分けられるか。
4. Local Package Artifactは、どのGo packageとmodule変更を実際のbuild依存として監視すべきか。
5. PR時の広いrelease candidate検査と、merge後pushでの再検査をどこまで分離できるか。
6. runnerが割り当てられない状態を、repository内のCI failureと混同せず記録するには何を残すべきか。
7. runner割当が一部だけ成立する不安定な状態で、どのEvidenceまで確定できるか。

## Constraints

- runner未割当をCI successとして扱わない。
- workflowを単に無効化して赤い状態を隠さない。
- E3a、E3b-P1、E3b-P2、E3b-M1a、E3b-M1b、actual二モデル交換、Local Reference Packageで既に得られたEvidenceの意味や高さを変更しない。
- actual external executionの処理本文、SOZA mapping、historical reconstruction test、Release Gate、Local Package Artifactの検査本文を、実行量削減だけを理由に弱めない。
- `workflow_dispatch`等による明示的な再実証経路を必要なworkflowで残す。
- `pull_request.paths`のPR全体差分というGitHubの挙動を、commit単位のfilterとして誤って説明しない。
- pathを狭めるときは、実際のbuild / test依存を確認して必要な変更を取りこぼさない。
- CI使用量や課金方式をUniversal Product Requirementへ持ち込まない。
- post-releaseのExecutable Evidenceをv0.2.0 supported scopeへ遡及的に追加しない。

## Required scenarios / experiments

### E1 — step開始前failureを実行本文のFAILと分ける

軽量な`Plan integrity`などを再実行し、jobがrunnerへ割り当てられるかを確認する。

判定:

- runnerが割り当てられstepが開始された場合、以降は実際のstep結果で判定する。
- jobは生成されたが`steps=[]`のまま終了した場合、repository内の検査本文を実行したFAILとは数えない。

### E2 — workflow定義とtriggerの受理

trigger変更を含むPRを作成し、GitHub Actionsがworkflow定義を受理することを確認する。

PASS条件:

- PR差分に応じて対象workflowのrunが生成される。

runner未割当の場合も、workflow定義・path選択とjob実行結果を分けて記録する。

### E3 — scenario-local testの選択性

同一package内の特定実証専用testだけを変更した場合、無関係なexternal actual workflowが対象にならないことを確認する。

PR #63のruntime交換固有差分だけだったhead `55bfcfb45e6e19210e925923565700a075ab006d`で次を確認した。

- Runtime Version Exchange E3b: **対象**
- M1a: **対象外**
- M1b: **対象外**
- Actual Model Artifact Exchange E3b: **対象外**

したがって、runtime交換専用testと既存Method実証の責務分離はrun生成レベルで確認済みである。

### E4 — 共有実装変更時の依存実証選択

shared KJ Atlas mappingのように複数実証から利用される実装を変更した場合、依存するM1a / M1b / actual二モデル交換等が再び対象になることを確認する。

PR #63でExact Realization Reference対応を`kj_atlas.go`へ追加した後、これらのworkflowが再び生成された。これは不要な連鎖起動ではなく、共有実装変更に対する意図した回帰選択である。

### E5 — 文書だけの独立PR

runtime / Adapter / fixture / scenario-local test / workflowを変更せず、Issue、上流計画、Evidence説明、監査台帳だけを変更する独立PRを用意した場合、actual external execution用pathsに一致しないことを確認する。

PR #64をPR #61のheadから分岐し、差分を`plan/document_review_registry.yaml`だけに限定して検証した。

head `d292ce43298c537124739becb6963fdef848e39f`で生成されたworkflowは次の1本だけだった。

- Plan integrity Run `33672679058`

次は生成されなかった。

- External Integration E3a
- External Integration E3b
- External TEI Integration E3b P2
- External Method Integration E3b
- External Model-backed Method E3b M1b
- Actual Model Artifact Exchange E3b
- Local Package Artifact

したがって、文書だけの独立PRではactual external executionとLocal Package Artifactを選択しないことを**run生成レベルで確認済み**である。

Plan integrity Job `100389847417`自体は`steps=[]`のまま終了したため、Plan integrityの検査本文がPASSしたとは扱わない。trigger selectionとrunner executionを分けて記録する。

同じruntime変更PRへ文書commitを追加した場合は、PR全体差分にruntime変更が残るため本scenarioの対象外とする。

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

PR #63のような`livemethodintegration`のみの変更ではLocal Package Artifactを対象にせず、上記build依存を変更した場合は対象にすることを確認対象とする。

### E7 — runner割当成立後の回帰

runnerが割り当てられたworkflowについて、既存検査本文が実際にsuccessすることを確認する。

最低限、PR #61の変更対象について次を順次確認する。

- External Integration E3a
- External Integration E3b
- External TEI Integration E3b P2
- External Method Integration E3b
- External Model-backed Method E3b M1b
- Actual Model Artifact Exchange E3b
- Local Package Artifact
- Release Candidate Gate
- Plan integrity

PR #63 head `765eb189f97d7dba402cec864960cecb3a5a91a6`では、`Actual Model Artifact Exchange E3b` Run `33670697154` / Job `100383296117`だけはrunnerへ割り当てられ、全stepがsuccessした。

このrunでは、actual model実行、`go test ./livemethodintegration -count=1`、historical Application保持testまで成功している。したがって、少なくともshared mapping変更後のactual二モデル交換経路は回帰していない。

一方、同じheadのPlan integrity、M1a、M1b、runtime version交換等は`steps=[]`のまま終了し、個別再実行でも同じ状態が残った。現時点ではrunner利用可能性を全面復旧とは扱わない。

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

2026-09-03時点で、PR #61のworkflow変更はGitHubに受理されている。

scenario-local testのpath選択については、PR #63のhead `55bfcfb45e6e19210e925923565700a075ab006d`で期待どおりの選択性を確認した。その後shared mappingを変更すると依存workflowが再び選択され、PR全体の意味変更に応じたtriggerとして動作している。

文書だけの独立PRについてはPR #64で確認し、Plan integrityだけが生成され、actual external executionとLocal Package Artifactは一切生成されなかった。したがってE5はrun生成レベルで成立した。

Local Package Artifactについては、`soza-package-probe → packagingprobe → semanticruntime`という実依存を確認し、`runtime/go/**`全体からbuild依存範囲へtriggerを限定した。検査本文は変更していない。

runnerについては、当初の「ほぼ全面的にstep開始前で終了する状態」から変化が見られる。PR #63 head `765eb189f97d7dba402cec864960cecb3a5a91a6`のRun `33670697154`ではactual二モデル交換が全stepを完走した。

一方で、同じhead・同じ時間帯でも他workflowは`steps=[]`のまま終了している。そのため現在は次のように判定する。

```text
workflow trigger syntax accepted
  = confirmed

scenario-local trigger selection
  = confirmed

shared-change dependent trigger selection
  = confirmed

docs-only independent PR selection
  = confirmed in PR #64

Local Package Artifact dependency boundary
  = refined from actual Go imports; runtime execution not yet re-confirmed

runner assignment
  = partially available / unstable

actual two-model regression after shared mapping change
  = success in Run 33670697154

full PR #61 regression
  = not yet confirmed
```

GitHub側の具体的な原因を課金、budget、runner pool等のいずれかへ断定するEvidenceはないため、原因は未確定のまま保持する。

## Resolution

Open中。

次のうち1〜5と7は成立した。6は静的な依存監査まで完了しているが、trigger変更後のactual package workflow回帰が未確認である。8はrunner割当の不安定さにより未完了である。

1. PR #61で外部実証workflowの起動範囲が、共有実装とscenario-local実証の責務に沿って整理されている。**完了**
2. actual executionの処理本文やEvidence強度を弱めていないことを差分監査で確認している。**完了**
3. scenario-local testだけのPR差分では、無関係なactual external workflowが選択されないことを確認している。**完了**
4. shared実装変更では、依存するactual external workflowが選択されることを確認している。**完了**
5. 文書だけの独立PRでは、actual external execution用pathsに一致しないことを確認している。**完了: PR #64**
6. Local Package Artifactが実際のbuild依存変更で起動し、無関係なGo package変更では起動しないことを確認する。**部分完了: dependency / path設計済み、runner上の回帰未確認**
7. runner未割当期間やstep未開始failureをSOZA Product / Evidenceのfailureとして誤記していない。**完了**
8. runner割当が成立した状態で、PR #61の対象workflowについて必要な回帰実行がsuccessしている。**未完了**

6と8まで確認した時点でResolvedとする。

## Reopen conditions

Resolved後も、次の場合は再開する。

- triggerを狭めた結果、runtime / Adapter / fixtureの意味変更時に必要な実証が選択されない。
- scenario-local testだけの変更で無関係な重い実証が再び対象になる。
- 文書だけの独立PRでactual external workflowが無条件に対象になる。
- Local Package Artifactの実依存を変更したのにpackage workflowが対象にならない。
- 無関係なGo package変更だけでLocal Package Artifactが恒常的に対象になる。
- `workflow_dispatch`を含む再実証経路が失われる。
- release publicationに必要なpush / tag経路が起動しなくなる。
- CI使用量削減のために検証本文やAcceptanceが弱められる。
- runner環境の障害をProduct Evidenceの失敗として扱う運用が再発する。

## CI / verification

検証結果は次を分けて記録する。

```text
workflow definition accepted
  != workflow selected by PR diff
  != job assigned to a runner
  != workflow checks passed
```

`pull_request.paths`はPR全体のbase→head差分で評価されるため、同一PR内の後続commitごとの非起動をAcceptanceにはしない。

runnerが割り当てられないrunでは、差分監査によって検査本文を弱めていないことを確認する。ただし、この静的確認をCI successの代替Evidenceにはしない。

## Natural Japanese review

当初は「文書だけを更新したcommitなら重いworkflowを再実行しない」という読み方ができる記述があったが、GitHub Actionsの`pull_request.paths`はPR全体の差分で判定されるため、その表現を修正した。

現在の目的はcommit単位の実行抑制ではなく、文書だけの独立PR、scenario-local test、shared実装変更という**PR差分の意味**と実証責務を一致させることである。PR #64を使い、文書だけの独立PRではPlan integrityだけが選択されることも実測した。

Local Package Artifactについても「Goの変更なら全部再build」という粗い説明を避け、実際にbuildする`soza-package-probe`からimport依存をたどって起動範囲を整理した。検査本文を減らすのではなく、artifactに影響する変更と再build責務を一致させている。

runner状態については、「利用不能」から「復旧済み」へ単純に二値化していない。Run `33670697154`ではactual workflowが完走した一方、同じheadでもstep未開始のjobが残っているため、部分的・不安定な割当として記録した。

`steps=[]`という観測事実からSOZA固有test failureを推論せず、課金・budget・GitHub側障害等の具体原因も未確認のまま断定しない。

既存Evidenceの高さ、Release Evidence、Product Requirementを変更せず、意味、規範強度、Evidence強度を保ったまま自然な日本語として全文を再ドラフトした。