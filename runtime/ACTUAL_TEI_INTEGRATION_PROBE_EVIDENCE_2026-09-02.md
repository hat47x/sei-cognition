# Actual TEI Integration Probe Evidence — 2026-09-02

## 1. この文書の位置づけ

この文書は、PMS-06 / E3b-P2で行ったactual TEI integration probeについて、**実際に確認できたことと、まだ確認できていないことを分けて記録するEvidence**です。

2026-09-02時点のprobeでは、実TEI CLIのScoped Executable Evidenceはまだ成立していません。private repositoryを取得する資格情報が利用できず、actual TEI checkout以降のstepが実行されていないためです。

```text
workflow success
  != actual TEI execution success
  != E3b-P2 Satisfied
```

一方、PR時だけでなく`develop/v0.2.0`への統合後にもE3b-P2専用workflowが自動実行されることは確認できました。これは検査経路の回帰確認であり、actual TEI実行のEvidenceとは分けて扱います。

## 2. Probe対象

固定したTEI側:

- Repository: `hat47x/tei-platform`
- Commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI: `cmd/tei`
- Intended command: `deployment-provider-plan`
- Reference Workspace: `reference/workspace`
- Intended Durable Run: `reference/order_rollout.durable-run.m0.21.start.json`

### 最初のcredential-aware probe

SOZA側:

- Repository: `hat47x/soza`
- PR: `#44`
- Probe commit: `348bdfa5d3cac97af3e0d12d2959d948922e7ceb`
- Workflow: `External TEI Integration E3b P2`
- Workflow Run: `33589190828`
- Job: `actual-tei-provider-plan`

### `develop/v0.2.0`統合後の回帰probe

SOZA側:

- Repository: `hat47x/soza`
- Trigger correction PR: `#45`
- Merge commit: `5167e7e6e3ffb8ed4f21030547f8e4c384ad1502`
- Workflow: `External TEI Integration E3b P2`
- Workflow Run: `33590170686`
- Event: `push`
- Job: `actual-tei-provider-plan`

## 3. 最初のprobeで実際に実行されたstep

Workflow Run `33589190828`では、次がsuccessしました。

1. SOZA repositoryのcheckout
2. Go 1.25.xのsetup
3. `runtime/go/teiintegration`のdeterministic process-boundary test
4. private TEI repositoryを取得できる資格情報があるかの確認
5. actual TEIを取得できなかった場合のEvidence境界の記録

この範囲では、ISSUE-000061で準備したexternal executable injection boundaryがcurrent branchでも壊れていないことを再確認しています。

## 4. 最初のprobeで実行されなかったstep

`TEI_REPOSITORY_TOKEN`が利用できなかったため、次はすべて**skipped**でした。

1. pinned TEI revisionのcheckout
2. actual `cmd/tei` build
3. pinned TEI Reference Workspaceの`validate`
4. SOZA Adapterからactual `deployment-provider-plan`を起動するlive test

したがって、次はまだEvidenceとして得られていません。

- actual TEI processがGitHub Actions runner上で起動できること
- actual TEI JSONをcurrent Adapter-local DTOがstrict decodeできること
- actual TEI responseから`availability = true`を得られること
- actual TEI responseから`provider_plan_resolved = true`を得られること
- actual TEI mapping結果がcurrent Capability Observation validatorを通ること
- helper subprocessでは現れなかったpath、lifecycle、timeout、JSON出力差がないこと

## 5. `develop/v0.2.0`統合後の回帰probe

PR #45で専用workflowに`develop/v0.2.0`へのpush triggerを追加した。これをmergeしたcommit `5167e7e6e3ffb8ed4f21030547f8e4c384ad1502`に対し、Workflow Run `33590170686`が`push` eventとして自動起動し、job全体がsuccessした。

このrunでは次がsuccessした。

1. SOZA repositoryのcheckout
2. Go 1.25.xのsetup
3. deterministic TEI process-boundary test
4. private TEI repositoryを取得できる資格情報があるかの確認
5. actual TEIを取得できなかった場合のEvidence境界の記録
6. workflow後処理を含むjob全体の完了

`TEI_REPOSITORY_TOKEN`は引き続き利用できなかったため、次はすべてskippedだった。

1. pinned TEI revisionのcheckout
2. actual `cmd/tei` build
3. pinned TEI Reference Workspaceの`validate`
4. SOZA Adapterからactual `deployment-provider-plan`を起動するlive test

したがって、このrunから得られた新しいEvidenceは**統合後にも専用検査経路が自動起動し、deterministic境界が壊れていないこと**です。actual TEIの取得・実行については新しいEvidenceを得ていません。

```text
post-merge workflow regression
  = Satisfied

actual TEI execution
  = Not Yet Verified
```

## 6. 今回分かったこと

2026-09-02のprobeから、少なくとも**現在のSOZA Actionsでは、別private repositoryのTEIを取得するためのrepository-scoped credentialが利用可能な状態にない**ことを、実行経路上の制約として扱う必要があります。

ただし、これはProduct RequirementやUniversal Contractの発見ではありません。

```text
private source acquisition constraint
  != Capability semantics
  != Provider identity
  != execution authorization semantics
  != universal credential model
```

現在観測できている阻害点はacquisition層にあります。とはいえ、資格情報を与えた後にactual TEI executionが成功することまでは確認していないため、「残る問題は資格情報だけである」とは断定しません。

## 7. 次の実証条件

E3b-P2をScoped Executable Evidenceへ進めるには、次のrunで少なくとも以下が必要です。

- SOZA Actionsから`hat47x/tei-platform`の固定revisionをreadできるrepository-scoped credentialを利用できること
- actual checkout stepがskipされずsuccessすること
- `go build -o /tmp/tei ./cmd/tei`がsuccessすること
- `/tmp/tei validate -workspace reference/workspace`がsuccessすること
- `TestLiveTEIProviderPlan`がskipされずsuccessすること

credentialの具体的な配布方式は、このEvidenceだけからSOZA標準へ固定しません。

## 8. Evidence state

- Design Evidence for E3b-P2 probe path: **Satisfied for the current boundary**
- Deterministic external-process boundary: **Scoped Executable Evidence available**
- E3b-P2 workflow after merge to `develop/v0.2.0`: **Regression confirmed in Run 33590170686**
- Private TEI acquisition in SOZA Actions: **Not Yet Verified / credential unavailable in observed runs**
- Actual TEI CLI execution through SOZA Adapter: **Not Yet Verified**
- E3b-P2: **Not Yet Verified**
- E3b-M1b: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence for this change: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 9. Natural Japanese review

ISSUE-000061、ISSUE-000065、`runtime/go/teiintegration`、E3b-P2専用workflow、最初のRun `33589190828`、PR #45統合後のRun `33590170686`を照合した。

両runともactual TEI checkout / build / validate / executionがskipされた事実を優先し、workflow全体のsuccessをE3b-P2成功へ読み替えていない。一方で、`develop/v0.2.0`への統合後にも専用workflowが自動起動し、deterministic境界を回帰確認できるようになったことは独立した事実として記録した。また、private repository取得の制約をSOZAのCapability意味論やcredential標準へ先取りせず、資格情報供給後に初めて現れ得るCLI / JSON / process lifecycle差も未検証のまま残している。

確認済みの事実、そこから言える範囲、まだ未検証の範囲を分け、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。