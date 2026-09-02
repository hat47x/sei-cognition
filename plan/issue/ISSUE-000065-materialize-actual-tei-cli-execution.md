# ISSUE-000065: 実TEI CLIをSOZAのProvider Adapterから実行する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Updated: 2026-09-02

## Goal

PMS-06のE3b-P2として、`hat47x/tei-platform`の固定revisionから実際に作成したTEI CLIを別OS processとして起動し、TEIの`deployment-provider-plan`応答をSOZAのcurrent Capability Observationへ戻せることを、再現可能なScoped Executable Evidenceとして確認する。

このIssueで確認するのは、ISSUE-000061で準備した「外部実行ファイルを受け入れる境界」がhelper subprocessだけでなく、**実際のTEI CLIでも成立するか**である。

```text
ISSUE-000061
  external executable injection boundary
          ↓
ISSUE-000065 / E3b-P2
  actual TEI CLI execution
          ↓
current Capability Observation
```

この成立を、TEIそのものをSOZAのUniversal Contractへ取り込む根拠にはしない。

## 固定する外部revision

最初の実証では、TEIを次のrevisionへ固定する。

- Repository: `hat47x/tei-platform`
- Commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI: `cmd/tei`
- Command: `deployment-provider-plan`
- Reference Workspace: `reference/workspace`
- Durable Run: `reference/order_rollout.durable-run.m0.21.start.json`
- Solution: `order_rollout`
- Version: `2026.8.27`
- Plugin Lock: `reference/workspace/.tei/plugin-lock.json`

固定revisionは実行再現性を確保するためのEvidence条件であり、SOZAがTEIのversioning方式を支配するという意味ではない。

## 取得・資格情報と意味契約を分離する

TEI repositoryはprivateである。そのため、実行にはrepositoryを取得できる資格情報が必要になる場合がある。

ただし、次は別の問題として扱う。

```text
private repositoryを取得する方法
  != TEI executableを起動する方法
  != TEI固有JSONを解釈する方法
  != SOZA Capability Observationの意味
```

SOZA側のlive workflowでは、repository-scoped credentialとして`TEI_REPOSITORY_TOKEN`を利用できる場合だけ固定revisionをcheckoutする。資格情報がない場合はactual TEI stepを実行せず、E3b-P2を未検証のまま残す。

資格情報の有無によってUniversal Contract、Capability identity、Observation field setを変えてはならない。

## 実装方針

`runtime/go/teiintegration/tei_live_test.go`に、actual TEI専用のintegration testを追加した。

通常の`go test ./...`ではこのtestをskipし、`SOZA_E3B_TEI_LIVE=1`と必要な外部pathを明示した場合だけ実行する。

実行時には次を確認する。

1. 固定revisionからbuildした実TEI executableを起動できる。
2. TEI Reference Workspace自身の`validate`が成功する。
3. `deployment-provider-plan`が正常終了し、認識可能なProvider Plan JSONを返す。
4. 既存`teiintegration.CLI`がその応答をstrictにdecodeできる。
5. mapping後のCapability Observationがcurrent validatorを通る。
6. `availability = true`を観測できる。
7. `provider_plan_resolved = true`を観測できる。
8. TEI固有の`executors`、`observations`、`evidence`、`pluginRuntime`をUniversal fieldへ漏らさない。
9. 固定したTEI revisionを`sourceStateRef`として追跡できる。

## CI / live probe

`.github/workflows/external-tei-integration-e3b-p2.yml`をE3b-P2専用workflowとする。

workflowは最初にISSUE-000061由来のdeterministic process-boundary testを実行する。その後、`TEI_REPOSITORY_TOKEN`が利用できる場合だけ次へ進む。

```text
checkout pinned TEI revision
  → build cmd/tei
  → validate TEI Reference Workspace
  → SOZA teiintegration.CLIから実TEIを起動
  → current Capability Observationを検証
```

資格情報が無いrunでは、deterministic boundaryが成功してもE3b-P2のPASSとは扱わない。workflow logにその境界を明記する。

PR時の検査だけでなく、`develop/v0.2.0`への統合後にも同じ専用workflowを自動実行する。これにより、PR上の境界検査と統合後のcurrent branchでの回帰確認を分けて記録する。

## 最初のprobe結果

PR #44のProbe commit `348bdfa5d3cac97af3e0d12d2959d948922e7ceb`に対するWorkflow Run `33589190828`で、最初のcredential-aware probeを実行した。

Run全体とdeterministic process-boundary testはsuccessした。一方、`TEI_REPOSITORY_TOKEN`を利用できなかったため、次はすべてskipされた。

- pinned TEI revisionのcheckout
- actual `cmd/tei` build
- TEI Reference Workspace validation
- SOZA Adapter経由のactual `deployment-provider-plan`実行

したがって、このrunはE3b-P2のScoped Executable Evidenceには数えない。

```text
Run 33589190828 success
  + deterministic boundary success
  + actual TEI steps skipped
  = E3b-P2 Not Yet Verified
```

確認結果は`runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md`へ記録した。

今回のprobeによりacquisition層の資格情報が現在の阻害点として観測されたが、「残る問題は資格情報だけである」とは断定しない。資格情報を供給した後に、actual TEIのCLI / JSON / process lifecycleで追加差分が現れる可能性は未検証である。

## `develop/v0.2.0`統合後の回帰結果

PR #45でE3b-P2専用workflowに`develop/v0.2.0`へのpush triggerを追加し、merge commit `5167e7e6e3ffb8ed4f21030547f8e4c384ad1502`に対するWorkflow Run `33590170686`が実際に自動起動することを確認した。

このrunでは、deterministic process-boundary testと資格情報確認、Evidence境界の記録がsuccessした。`TEI_REPOSITORY_TOKEN`は引き続き利用できなかったため、actual TEIのcheckout、build、Reference Workspace validation、SOZA Adapter経由の実行はすべてskipされた。

したがって、次の二点を分けて扱う。

```text
merge後の専用workflow回帰確認
  = Satisfied

actual TEI CLI execution
  = Not Yet Verified
```

この結果により、「merge後のcurrent branchでも専用検査経路が動くこと」は確認できたが、E3b-P2のEvidence強度そのものは上がっていない。

## 必須Evidence

E3b-P2をSatisfiedへ移すには、少なくとも次を記録する。

- SOZA commit / workflow run
- TEI repositoryと固定commit
- 実行したTEI command surface
- actual TEI checkout stepが実行されたこと
- actual TEI buildが成功したこと
- TEI Reference Workspace validationが成功したこと
- `TestLiveTEIProviderPlan`がskipではなく実行され、成功したこと
- mapping後のcurrent Capability Observation validationが成功したこと
- Provider固有fieldの非漏出を確認したこと

資格情報が無いためactual stepがskipされたrunは、このEvidenceには数えない。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

今回のProduct failureは既存の次のRequirement / Scenarioで表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

実TEI接続によって既存Requirementでは表せない独立したProduct failureが見つかった場合だけ、Candidate Requirementとして上流へ戻す。

## Non-goals / 未検証範囲

- TEI repositoryのcredential方式をSOZA標準として固定すること
- `TEI_REPOSITORY_TOKEN`という名前をUniversal Contractへ取り込むこと
- TEI binaryの正式配布方式、署名方式、更新方式を決めること
- TEI CLI schemaをSOZA Universal Contractへ昇格させること
- TEIを唯一または特別なExecution Providerとして扱うこと
- E3b-M1bの外部model-backed Cognitive Methodを検証すること
- E4 Operational portabilityを検証すること
- v0.2.0のsupported scopeを遡及的に拡張すること
- Product Release / Release Evidenceを新たに成立させること
- Adoption / Outcome Evidenceを成立させること

## 完了条件

- [x] actual TEI専用integration testを追加する。
- [x] fixed TEI revisionをworkflowへ明示する。
- [x] private repository取得とSOZAの意味契約を分離する。
- [x] 資格情報が無いrunをE3b-P2成功として扱わない。
- [x] 最初のcredential-aware probe結果をEvidence文書へ記録する。
- [x] plan registry / document review registry / Product Milestone / 上流計画をcurrent probeへ同期する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。
- [x] merge後の`develop/v0.2.0`でE3b-P2専用workflowを含む回帰CIを確認する。
- [ ] fixed TEI revisionのcheckoutを実際に成功させる。
- [ ] actual `cmd/tei` buildを成功させる。
- [ ] TEI Reference Workspace validationを成功させる。
- [ ] actual `deployment-provider-plan`をSOZA Adapter経由で実行する。
- [ ] actual mapping結果をcurrent Capability Observation validatorへ通す。

## Evidence state

- Design Evidence: **Satisfied for the current boundary**
- ISSUE-000061 external TEI executable injection boundary: **Scoped Executable Evidence available with helper subprocess**
- Credential-aware acquisition probe: **Executed / actual TEI acquisition unavailable in Run 33589190828**
- Post-merge E3b-P2 workflow regression: **Satisfied in Run 33590170686 / actual TEI steps skipped**
- E3b-P2 actual TEI CLI execution: **Not Yet Verified**
- E3b-M1a live external Cognitive Method execution: **Scoped Executable Evidence available**
- E3b-M1b external model-backed Cognitive Method execution: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence for this change: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- 固定TEI revisionの`deployment-provider-plan`が現在のAdapter-local DTOでは読めない。
- actual TEIでのみ現れるtop-level fieldによりstrict decodeが失敗する。
- 実TEIのProvider Planが認識可能な情報を返さない。
- 実TEIのsource revisionをcurrent provenanceでは十分に追跡できない。
- private repository取得方式をsemantic identityへ混ぜないと成立しない。
- helper subprocessでは見えなかったprocess lifecycle、timeout、path解決、JSON出力の問題が確認される。

## Natural Japanese review

ISSUE-000061、PMS-06、current Capability Observation Contract、`runtime/go/teiintegration`、固定した`hat47x/tei-platform`の`cmd/tei`、Reference Workspace、TEI CIで用いられているdurable run、PR #44のWorkflow Run `33589190828`、PR #45統合後のWorkflow Run `33590170686`を照合した。

最初のprobeと統合後の回帰runはいずれも、actual TEI stepがskipされたためE3b-P2へ読み替えていない。一方、PR時だけでなく`develop/v0.2.0`へ統合した後にも専用workflowが自動起動し、deterministic境界が壊れていないことは独立した回帰結果として記録した。また、資格情報を供給すれば必ずactual executionが成功するとも推定していない。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。