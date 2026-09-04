# Actual TEI Integration Probe Evidence — 2026-09-02

## 1. この文書の位置づけ

この文書は、PMS-06 / E3b-P2で行った最初のactual TEI integration probeについて、**実際に確認できたことと、まだ確認できていないことを分けて記録するEvidence**です。

今回のrunは、実TEI CLIのScoped Executable Evidenceを成立させていません。private repositoryを取得する資格情報が利用できず、actual TEI checkout以降のstepが実行されなかったためです。

```text
workflow success
  != actual TEI execution success
  != E3b-P2 Satisfied
```

## 2. Probe対象

SOZA側:

- Repository: `hat47x/soza`
- PR: `#44`
- Probe commit: `348bdfa5d3cac97af3e0d12d2959d948922e7ceb`
- Workflow: `External TEI Integration E3b P2`
- Workflow Run: `33589190828`
- Job: `actual-tei-provider-plan`

固定したTEI側:

- Repository: `hat47x/tei-platform`
- Commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI: `cmd/tei`
- Intended command: `deployment-provider-plan`
- Reference Workspace: `reference/workspace`
- Intended Durable Run: `reference/order_rollout.durable-run.m0.21.start.json`

## 3. 実際に実行されたstep

Workflow Run `33589190828`では、次がsuccessしました。

1. SOZA repositoryのcheckout
2. Go 1.25.xのsetup
3. `runtime/go/teiintegration`のdeterministic process-boundary test
4. private TEI repositoryを取得できる資格情報があるかの確認
5. actual TEIを取得できなかった場合のEvidence境界の記録

この範囲では、ISSUE-000061で準備したexternal executable injection boundaryがcurrent branchでも壊れていないことを再確認しています。

## 4. 実行されなかったstep

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

## 5. 今回分かったこと

今回のprobeから、少なくとも**現在のSOZA repository内だけでは、GitHub Actionsの標準tokenで別private repositoryのTEIを取得できるとは仮定できない**ことを、実行経路上の制約として扱う必要があります。

ただし、これはProduct RequirementやUniversal Contractの発見ではありません。

```text
private source acquisition constraint
  != Capability semantics
  != Provider identity
  != execution authorization semantics
  != universal credential model
```

今回の阻害点はacquisition層にあります。とはいえ、資格情報を与えた後にactual TEI executionが成功することまでは確認していないため、「残る問題は資格情報だけである」とも断定しません。

## 6. 次の実証条件

E3b-P2をScoped Executable Evidenceへ進めるには、次のrunで少なくとも以下が必要です。

- SOZA Actionsから`hat47x/tei-platform`の固定revisionをreadできるrepository-scoped credentialを利用できること
- actual checkout stepがskipされずsuccessすること
- `go build -o /tmp/tei ./cmd/tei`がsuccessすること
- `/tmp/tei validate -workspace reference/workspace`がsuccessすること
- `TestLiveTEIProviderPlan`がskipされずsuccessすること

credentialの具体的な配布方式は、このEvidenceだけからSOZA標準へ固定しません。

## 7. Evidence state

- Design Evidence for E3b-P2 probe path: **Satisfied for the current boundary**
- Deterministic external-process boundary: **Scoped Executable Evidence available**
- Private TEI acquisition in SOZA Actions: **Not Yet Verified / credential unavailable in this run**
- Actual TEI CLI execution through SOZA Adapter: **Not Yet Verified**
- E3b-P2: **Not Yet Verified**
- E3b-M1b: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence for this change: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 8. Natural Japanese review

ISSUE-000061、ISSUE-000065、`runtime/go/teiintegration`、E3b-P2専用workflow、実際のRun `33589190828`のstep結果を照合した。workflow全体がsuccessであっても、actual TEI checkout / build / validate / executionがskipされた事実を優先し、E3b-P2を成功扱いしていない。また、private repository取得の制約をSOZAのCapability意味論やcredential標準へ先取りしていない。確認済みの事実、そこから言える範囲、まだ未検証の範囲を分け、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
