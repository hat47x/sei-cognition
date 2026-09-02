# ISSUE-000065: 実TEI CLIをSOZAのProvider Adapterから実行する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Updated: 2026-09-02

## Goal

PMS-06のE3b-P2として、`hat47x/tei-platform`の固定revisionから実際に作成したTEI CLIを別OS processとして起動し、TEIの`deployment-provider-plan`応答をSOZAのcurrent Capability Observationへ戻せることを、再現可能なScoped Executable Evidenceとして確認する。

このIssueで確認するのは、ISSUE-000061で準備した外部実行ファイルの受け入れ境界が、helper subprocessだけでなく**実際のTEI CLIでも成立するか**である。

```text
ISSUE-000061
  external executable injection boundary
          ↓
ISSUE-000065 / E3b-P2
  fixed-artifact actual TEI CLI execution
          ↓
current Capability Observation
```

この成立を、TEIそのものをSOZAのUniversal Contractへ取り込む根拠にはしない。

## 固定した外部revision

今回の実証では、TEIを次のrevisionへ固定した。

- Repository: `hat47x/tei-platform`
- Commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI: `cmd/tei`
- Command: `deployment-provider-plan`
- Reference Workspace: `reference/workspace`
- Durable Run: `reference/order_rollout.durable-run.m0.21.start.json`
- Solution: `order_rollout`
- Version: `2026.8.27`
- Plugin Lock: `reference/workspace/.tei/plugin-lock.json`

固定revisionは実証対象を再現可能にするためのEvidence条件であり、SOZAがTEIのversioning方式を支配するという意味ではない。

## 取得・資格情報と意味契約を分離する

TEI repositoryはprivateであるため、sourceを取得する環境によってはrepository-scoped credentialが必要になる。

ただし、次は一つの問題として扱わない。

```text
private repositoryを取得する方法
  != TEI executableを起動する方法
  != TEI固有JSONを解釈する方法
  != SOZA Capability Observationの意味
```

SOZA側のcredential-aware workflowは、`TEI_REPOSITORY_TOKEN`を利用できる場合だけprivate repositoryをcheckoutする。資格情報がないrunではactual TEI stepを実行せず、そのrunをE3b-P2の成功へ読み替えない。

一方、E3b-P2のProduct上の問いは「GitHub Actionsからprivate repositoryを取得できるか」ではなく、**固定した実TEI CLIをSOZAのProvider Adapter境界へ渡したときにも意味の分離が保たれるか**である。このため、取得経路とactual execution Evidenceを分離して評価する。

## 実装した検査境界

`runtime/go/teiintegration/tei_live_test.go`には、actual TEI専用のintegration testがある。

通常の`go test ./...`ではこのtestをskipし、`SOZA_E3B_TEI_LIVE=1`と必要な外部pathを明示した場合だけ実行する。

実行時には、少なくとも次を確認する。

1. 固定revisionからbuildした実TEI executableを起動できる。
2. `deployment-provider-plan`が正常終了し、認識可能なProvider Plan JSONを返す。
3. current `teiintegration.CLI`が応答をstrictにdecodeできる。
4. mapping後のCapability Observationがcurrent validatorを通る。
5. `availability = true`を観測できる。
6. `provider_plan_resolved = true`を観測できる。
7. TEI固有fieldをUniversal Capability Observationへ漏らさない。
8. 固定したsource stateをProvenanceとして追跡できる。

また、actual TEIが返したProvider Plan bytesを`runtime/go/teiintegration/testdata/tei-provider-plan-48a7ca1f.json`として固定し、通常CIではactual process起動とは別に、current strict decoder / validatorとの互換性を継続検査する。

```text
actual TEI process execution Evidence
  != actual-output compatibility regression test
```

## 最初のcredential-aware probe

PR #44のProbe commit `348bdfa5d3cac97af3e0d12d2959d948922e7ceb`に対するWorkflow Run `33589190828`では、deterministic process-boundary testはsuccessした。

一方、`TEI_REPOSITORY_TOKEN`を利用できなかったため、次はすべてskipされた。

- pinned TEI revisionのcheckout
- actual `cmd/tei` build
- TEI Reference Workspace validation
- SOZA Adapter経由のactual `deployment-provider-plan`実行

したがって、このrunはE3b-P2のScoped Executable Evidenceには数えない。

```text
Run 33589190828 success
  + deterministic boundary success
  + actual TEI steps skipped
  != E3b-P2 actual execution Evidence
```

この履歴は`runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md`に残す。

## `develop/v0.2.0`統合後の回帰確認

PR #45でE3b-P2専用workflowを`develop/v0.2.0`へのpushでも起動するようにし、merge commit `5167e7e6e3ffb8ed4f21030547f8e4c384ad1502`に対するWorkflow Run `33590170686`で自動起動を確認した。

このrunでも資格情報が利用できずactual TEI stepはskipされたため、actual execution Evidenceには数えない。一方、統合後のcurrent branchでもdeterministic process境界とEvidence停止線が維持されていることは、独立した回帰結果として扱う。

## 後続のactual TEI実証

先行probeとは別に、TEI側で固定source commitを改めてcheckoutし、actual `cmd/tei`をbuild・実行してEvidence artifactを作成した。

- TEI Workflow: `SOZA E3b-P2 TEI Evidence`
- Workflow Run: `33589084290`
- Job: `actual-tei-cli`
- Result: **success**
- Evidence artifact ID: `9831112092`
- Artifact name: `tei-soza-e3b-p2-linux-amd64`
- Artifact digest: `sha256:1ee8bf4112d9ae97e1f66b3165f70278663951e9dd4bd6020b465471f563a287`

actual artifactの主要identityは次のとおりである。

```text
TEI source commit:
  48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67
actual TEI binary SHA-256:
  31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154
actual Provider Plan SHA-256:
  39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950
```

Run `33589084290`では、固定source identityの確認、actual `cmd/tei` build、actual `deployment-provider-plan`実行、Provider Plan検査、Evidence bundle / archive / artifact作成までskipされずsuccessした。

取得したartifactを再生し、同梱binaryについて次も確認した。

- `./bin/tei validate -workspace reference/workspace`がwarningを保持したまま`ok`で完了する。
- 同梱binaryで`deployment-provider-plan`を再実行できる。
- 再実行したProvider PlanのSHA-256が、同梱`provider-plan.json`のSHA-256と一致する。
- byte比較でも両Provider Planが一致する。

さらに、current `develop/v0.2.0`に正本化されている次の実装と同一Git blobをactual artifactへ向けて実行した。

- `runtime/go/teiintegration/tei_cli.go`
  - Git blob: `62025ae7eeae388d29e9602957b6f3833251e671`
- `runtime/go/teiintegration/tei_live_test.go`
  - Git blob: `929de9ea1b5d7d1c529ab6124b079c35bd4bb669`

`TestLiveTEIProviderPlan`をskipさせず実行し、actual `tei` process起動、strict decode、current Capability Observation mapping / validation、`availability = true`、`provider_plan_resolved = true`、source-state Provenance保持、Provider固有情報の非漏出を確認した。

詳細は`runtime/ACTUAL_TEI_CLI_EVIDENCE_2026-09-02.md`を正とする。

## Resolution

このIssueの目的である「固定revisionから得た実TEI CLIをSOZAのProvider Adapter境界で実行し、current Capability Observationへ戻せるか」について、fixed-artifact範囲のScoped Executable Evidenceが成立した。

```text
fixed TEI source / artifact
  + actual CLI build / validation / replay
  + SOZA Adapterからのactual process起動
  + strict decode / current validation
  + Provider固有情報の非漏出
  = E3b-P2 fixed-artifact Scoped Executable Evidence
```

このResolutionは、次を意味しない。

```text
E3b-P2 fixed-artifact PASS
  != SOZA Actions private-repository credential operation proven
  != arbitrary / future TEI version compatibility
  != production TEI integration
  != E4 Operational portability
```

private repositoryの継続取得、credential運用、正式なbinary配布・更新、TEI version交換は、後続のacquisition / deployment / portability探索として扱う。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

今回の境界は既存の次のRequirement / Scenarioで表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

実TEIを接続できたこと自体を、新しいUniversal TEI ContractやStable Requirementの根拠にはしない。

## Non-goals / 未検証範囲

- SOZA Actionsからprivate TEI repositoryを継続取得するcredential運用
- `TEI_REPOSITORY_TOKEN`という名前や特定Secret製品をSOZA標準へ固定すること
- arbitrary / future TEI versionとの互換性
- TEI binaryの正式な配布方式、署名方式、更新方式
- TEI CLI schemaをSOZA Universal Contractへ昇格させること
- TEIを唯一または特別なExecution Providerとして扱うこと
- production execution authorization
- E3b-M1b external model-backed Cognitive Method
- E4 Operational portability
- v0.2.0 supported scopeの遡及的拡張
- この変更に対する新しいRelease Evidence
- Adoption / Outcome Evidence

## 完了条件

- [x] actual TEI専用integration testを追加する。
- [x] fixed TEI revisionを明示する。
- [x] private repository取得とSOZAの意味契約を分離する。
- [x] 資格情報が無いrunをactual TEI成功として扱わない。
- [x] 最初のcredential-aware probe結果をEvidence文書へ記録する。
- [x] merge後の`develop/v0.2.0`でE3b-P2専用workflowの回帰起動を確認する。
- [x] fixed TEI sourceを実際にcheckoutし、source identityを確認する。
- [x] actual `cmd/tei` buildを成功させる。
- [x] TEI Reference Workspace validationを成功させる。
- [x] actual `deployment-provider-plan`を実行する。
- [x] actual artifactをSOZA Adapter経由で別OS processとして実行する。
- [x] actual mapping結果をcurrent Capability Observation validatorへ通す。
- [x] Provider固有情報がUniversal Capability Observationへ漏れないことを確認する。
- [x] actual Provider Plan bytesをdigest付きfixtureとして通常CIへ追加する。
- [x] plan registry / document review registry / Product Milestone / 上流計画をactual Evidenceへ同期する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。
- [x] Resolution反映後のPR headで対象CIをsuccessさせる。

## Resolution反映後のCI

Resolutionと台帳同期を含むPR head `afd34174ba17c8459c3546272ac8a37593b80b2d`では、次の9系統がすべてsuccessした。

- Plan integrity Run `33597150206`
- Semantic Runtime Conformance Run `33597150208`
- External Integration E3a Run `33597150186`
- External Integration E3b Run `33597150242`
- External TEI Integration E3b P2 Run `33597150191`
- External Method Integration E3b Run `33597150205`
- V6 V7 Projection Evaluation Run `33597150252`
- Local Package Artifact Run `33597150228`
- Release Candidate Gate Run `33597150279`

Release Candidate GateはGate 1〜9がsuccessし、既に公開済みのv0.2.0に対するrelease preparation / publicationは意図どおりskipされた。

External TEI Integration E3b P2のsuccessは、SOZA Actionsでprivate repository credential経路のactual stepが実行されたという意味ではない。fixed-artifact actual execution Evidenceは、TEI側Run `33589084290`と取得済みartifactを用いたSOZA Adapter実証として別に記録する。

## Evidence state

- Design Evidence: **Satisfied for the current boundary**
- ISSUE-000061 external TEI executable injection boundary: **Scoped Executable Evidence available**
- Initial credential-aware probe: **Executed / actual TEI steps skipped in Run 33589190828**
- Post-merge E3b-P2 workflow regression: **Satisfied in Run 33590170686 / actual TEI steps skipped**
- E3b-P2 fixed-artifact actual TEI CLI execution: **Scoped Executable Evidence available**
- SOZA Actions private-repository acquisition / credential operation: **Not Yet Verified**
- arbitrary / future TEI version compatibility: **Not Yet Verified**
- E3b-M1a live KJ Atlas + deterministic model stub: **Scoped Executable Evidence available**
- E3b-M1b external model-backed Cognitive Method: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence for this change: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- actual TEIのProvider Planをcurrent Adapter-local DTOでは意味を壊さず読めなくなる。
- TEI version交換時に、current Provenance / Exact Bindingでは実行時sourceを十分に追跡できない。
- executable acquisition方式をsemantic identityへ取り込まないと成立しないことが判明する。
- fixed-artifact probeでは見えなかったprocess lifecycle、timeout、path解決、JSON出力差がproduction候補で確認される。
- Provider固有情報をUniversal Capability Observationへ漏らさずにmappingできなくなる。

## Natural Japanese review

ISSUE-000061、PMS-06、current Capability Observation Contract、`runtime/go/teiintegration`、固定した`hat47x/tei-platform` source、PR #44のRun `33589190828`、PR #45統合後のRun `33590170686`、TEI側Run `33589084290`、Evidence artifact、actual Provider Plan、actual SOZA Adapter実行結果を照合した。

最初のcredential-aware probeと統合後のSOZA workflowではactual TEI stepがskipされた事実を残し、その成功をactual executionへ読み替えていない。一方、その後に別経路で固定sourceからactual binaryを生成し、Reference Workspace validation、Provider Plan再実行、SOZA Adapter経由のactual process実行まで確認できたため、fixed-artifact範囲だけをScoped Executable Evidenceへ進めた。

credential運用、任意version互換性、production integration、E4、Release、Adoption / Outcome Evidenceは未検証のまま分離している。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
