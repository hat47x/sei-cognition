# ISSUE-000069: CI実証の自動起動責務とrunner利用不能を分離する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018, ADR-0020, ADR-0021**  
Product Milestone: **PMS-06 / PMS-07**  
Updated: 2026-09-02

## Goal

GitHub Actionsが実行できない外部環境上の問題と、SOZA repository内のworkflow設計上の問題を分けて扱える状態にする。

あわせて、外部Providerやactual modelを起動する実証workflowについて、**何が変わったときに自動再実証が必要なのか**を明確にし、Issue本文や上流計画、監査台帳だけの更新によって重い実証が無条件に再実行されない構成へ整理する。

このIssueの完了条件は「CIを緑色に見せること」ではない。GitHub-hosted runnerが利用できない状態をsuccessとして扱わず、runnerが利用可能になった後に、変更したtriggerで必要なworkflowが実際に起動・完走することを確認する。

## Background

PR #60を`develop/v0.2.0`へ統合した後、複数のGitHub Actions workflowがほぼ同時にfailureした。

通常のtest failureであれば、checkoutやsetup、test等のstepが開始された後に失敗箇所を特定できる。しかし今回のSOZA側runでは、`Plan integrity`を含む対象jobがstepを一つも開始していない。再実行しても`steps=[]`のまま数秒でfailureした。

同じ時刻帯には、別のprivate repositoryである`hat47x/tei-platform`でも複数jobが同様にstep開始前でfailureしていた。このため、今回の現象をSOZA固有のtest regressionやworkflow本文の失敗とは判断しない。

一方、調査の過程で別の問題も確認した。SOZAの外部実証workflowには、実装やfixtureが変わっていないにもかかわらず、Issue本文、上流計画、`plan/registry.yaml`、文書監査台帳等の変更だけでactual external executionが再実行されるものがあった。

この二つは分けて扱う必要がある。

```text
GitHub-hosted runnerを利用できない
  != SOZAのtest failure
  != Evidence failure

実装・Adapter・fixture・workflowの意味が変わった
  → 対応する実証を自動再実行する

Issue / 上流計画 / Evidence説明 / 監査台帳だけが変わった
  → 文書・整合性検査で扱う
  → actual再実証が必要なら明示的に起動する
```

## Questions

1. 外部実証workflowを自動起動すべき変更範囲は、どのruntime / Adapter / fixture / workflowに限定できるか。
2. 既に成立したScoped Executable Evidenceの説明文や計画文書を更新しただけの場合、actual model取得や外部process起動を再実行する必要があるか。
3. PR時の広いrelease candidate検査と、merge後pushでの再検査をどこまで分離できるか。
4. GitHub-hosted runnerが割り当てられない状態を、repository内のCI失敗と混同せず記録するには何を残すべきか。
5. runner復旧後、trigger変更が既存Evidenceを弱めていないことをどのworkflowで確認するか。

## Constraints

- GitHub-hosted runner未割当をCI successとして扱わない。
- workflowを単に無効化して赤い状態を隠さない。
- E3a、E3b-P1、E3b-P2、E3b-M1a、E3b-M1b、actual二モデル交換で既に得られたEvidenceの意味や高さを変更しない。
- actual external executionの処理本文、SOZA mapping、historical reconstruction test、Release Gateの受入条件を、実行量削減だけを理由に弱めない。
- `workflow_dispatch`等による明示的な再実証経路を必要なworkflowで残す。
- CI使用量や課金方式をUniversal Product Requirementへ持ち込まない。
- post-releaseのExecutable Evidenceをv0.2.0 supported scopeへ遡及的に追加しない。

## Required scenarios / experiments

### E1 — runner未割当の再現

軽量な`Plan integrity`を再実行する。

PASS条件:

- runnerが割り当てられ、少なくともworkflow stepが開始される。

BLOCKED条件:

- jobは生成されるがstepが一つも開始されず終了する。

このBLOCKEDはSOZAのPlan integrity内容のFAILとは数えない。

### E2 — trigger構文の受理

trigger変更を含むPRを作成し、GitHub Actionsが各workflowをworkflow定義として受理することを確認する。

PASS条件:

- 対象workflowのrunが生成される。

runner未割当でjob本体が開始できない場合、workflow構文の受理と実行成功を分けて記録する。

### E3 — runner復旧後の回帰

runnerが利用可能になった後、PR #61の変更対象について実際にworkflowを実行する。

最低限、次を確認する。

- External Integration E3a
- External Integration E3b
- External TEI Integration E3b P2
- External Method Integration E3b
- External Model-backed Method E3b M1b
- Actual Model Artifact Exchange E3b
- Release Candidate Gate
- Plan integrity

PASS条件:

- 変更後triggerでも、関係するworkflow自身を変更したPRで必要なrunが起動する。
- 各workflowの既存検査本文がsuccessする。
- 文書だけの無関係な変更では、actual external executionを不要に再実行しない。

## Deliverables

- `.github/workflows/external-integration-e3a.yml`
- `.github/workflows/external-integration-e3b.yml`
- `.github/workflows/external-tei-integration-e3b-p2.yml`
- `.github/workflows/external-method-integration-e3b.yml`
- `.github/workflows/external-model-method-integration-e3b-m1b.yml`
- `.github/workflows/actual-model-artifact-exchange-e3b.yml`
- `.github/workflows/release-candidate.yml`
- 本Issue
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

## Current findings

2026-09-02時点で、PR #61のworkflow変更はGitHubに受理され、対象runが生成された。

しかし、`Actual Model Artifact Exchange E3b`を含むjobはstepを一つも開始せず終了した。さらに、その後に軽量な`Plan integrity`を再実行しても`steps=[]`のままfailureした。

したがって、現時点では次のように判定する。

```text
workflow trigger syntax accepted
  = confirmed

GitHub-hosted runner available
  = not confirmed

workflow body regression
  = not demonstrated

trigger変更後のfull CI success
  = blocked by execution environment
```

## Resolution

Open中。

次をすべて満たした時点でResolvedとする。

1. PR #61で自動実証workflowの起動範囲が意味変更へ限定されている。
2. actual executionの処理本文やEvidence強度を弱めていないことを差分監査で確認している。
3. GitHub-hosted runnerが利用可能な状態で、対象workflowの回帰実行がsuccessしている。
4. merge後の無関係な文書更新によって、重いactual external executionが無条件に再発しないことを確認している。
5. runner未割当期間をSOZA Product / Evidenceのfailureとして誤記していない。

## Reopen conditions

Resolved後も、次の場合は再開する。

- triggerを狭めた結果、runtime / Adapter / fixtureの意味変更時に必要な実証が起動しない。
- `workflow_dispatch`を含む再実証経路が失われる。
- release publicationに必要なpush / tag経路が起動しなくなる。
- CI使用量削減のために検証本文やAcceptanceが弱められる。
- runner環境の障害をProduct Evidenceの失敗として扱う運用が再発する。

## CI / verification

このIssue自身がGitHub-hosted runner利用不能の影響を受けるため、検証結果は次の三つを分けて記録する。

```text
workflow definition accepted
workflow job started
workflow checks passed
```

三つを同一視しない。

runnerが利用できない間は、差分監査によって「triggerとconcurrency以外の検証本文を変更していない」ことを確認する。ただし、この静的確認をCI successの代替Evidenceにはしない。

## Natural Japanese review

障害の原因を断定しすぎず、観測できた事実と推論を分けて記述した。特に、`steps=[]`という観測事実から「SOZA固有のtestが失敗した」とは読まない一方、課金・budget・GitHub側障害等の具体原因も、直接確認できていない段階では確定事項として書いていない。

また、「CI削減」を目的に検証を弱める文章にならないよう、重いactual external executionを**意味変更に対応して起動する**という責務分離として書き直した。既存Evidenceの高さ、Release Evidence、Product Requirementを変更せず、runner復旧後のactual回帰を完了条件に残している。
