# ISSUE-000061: 実TEI CLIを受け入れる外部process境界を準備する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Updated: 2026-09-02

## Goal

PMS-06のE3b-P2「live TEI process / service integration」へ進む前段として、**SEIがTEIの取得方法やprivate repositoryのcredential方式を意味契約へ取り込まず、外部から与えられた`tei` executableを別OS processとして呼び、そのProvider固有JSONをcurrent Capability Observationへ戻せる境界**を実体化する。

このIssueでは、実TEIをSEI CIから取得・実行できたことまでは完了条件にしない。TEI repositoryはprivateであり、SEIの標準`GITHUB_TOKEN`に別repositoryのread権限があるとは仮定できないためである。

```text
E3b-P1 public live Provider service
  → ISSUE-000061 external executable injection boundary
  → E3b-P2 actual TEI CLI execution
```

ISSUE-000061のPASSはE3b-P2のPASSではない。

## 背景

ISSUE-000060では、public GitHub REST APIを実際に呼び、live responseからcurrent Capability Observationへ必要最小限の意味だけをmappingできることを確認した。

次の候補を調査したところ、TEIには既にGo製CLI `cmd/tei`があり、少なくとも次のJSON出力面が実装されている。

- `world`
- `observed-index`
- `deployment-start`
- `deployment-provider-plan`
- `deployment-reconcile`
- `deployment-simulate`

とくに`deployment-provider-plan`は、durable deployment runとenvironmentからExecutor / Observation / Evidence Providerのroutingを導出し、JSONで返す既存面である。SEI向けに新しいTEI protocolを作らず、Provider固有の実行面として扱える。

一方、`hat47x/tei-platform`はprivate repositoryである。SEI CIから暗黙にcloneできることを前提にすると、credential方式がintegration semanticsへ混入し、再現性も利用環境依存になる。

そのため、このIssueでは次を分離する。

```text
TEI executable acquisition / credential
  != TEI process invocation
  != Provider-specific JSON interpretation
  != SEI Capability Observation
```

## 対象surface

最初の境界ではTEI CLIの`deployment-provider-plan`を対象にする。

SEI側は、TEI executableのpathとTEI固有入力pathを明示的に受け取る。repository clone、GitHub token、binary distributionはAdapterの外側に置く。

TEIから受け取るJSONはProvider固有DTOとして閉じ、SEI Universal Contractへそのfield setを追加しない。

最初のmappingでは、少なくとも次を観測できる。

- 外部`tei` processが正常終了し、有効なProvider Plan JSONを返したこと。
- Provider Planとして認識できる情報が存在したこと。

Executor、Observation route、Evidence route、Plugin Runtime等のTEI内部fieldをCapability ObservationのUniversal fieldへ複製しない。

## 必須検査

1. executable pathを外部から注入できる。
2. `deployment-provider-plan`を別OS processとして実行する。
3. workspace / durable run / solution / version / plugin lock等のTEI固有引数をAdapter-local configurationとして扱う。
4. 正常なProvider Plan JSONだけを受理する。
5. unknown top-level field、malformed JSON、複数JSON値を黙って受理しない。
6. process exit failure時にCapability Observationを生成しない。
7. timeout / cancellation時にCapability Observationを生成しない。
8. TEI固有fieldをcurrent Capability Observationへそのまま漏らさない。
9. mapping後のCapability Observationがcurrent validatorを通る。
10. executable取得方法、GitHub credential、private repository cloneをUniversal Contractへ追加しない。
11. deterministic testではhelper processを使い、actual TEI executionと区別する。
12. このIssueのPASSをE3b-P2、Operational、Release、Adoption / Outcome Evidenceへ昇格させない。

## Resolution

`runtime/go/teiintegration`に、外部から明示的に与えられたTEI executableを呼び出すreference Adapterを実装した。

Adapterは`deployment-provider-plan`を対象とし、次を外部から注入できる。

- executable path
- executableの前置引数
- workspace path
- durable run path
- solution ID / version
- plugin lock path
- optional expected revision

これにより、install済み`tei` binaryだけでなく、呼出側が明示的に用意したwrapperや`go run .../cmd/tei`相当の実行面にも対応できる。ただし、どのようにTEI source / binaryを取得したかはAdapterの意味契約に含めない。

Provider Plan JSONはAdapter-local DTOとしてstrictにdecodeする。unknown top-level field、malformed JSON、複数JSON値、認識できるProvider Plan情報がない応答、incomplete routeを拒否する。

process exit failure、timeout / cancellationではCapability Observationを生成しない。成功時もTEI固有のExecutor、Observation route、Evidence route、Plugin Runtime等をUniversal fieldへ転写せず、次の最小観測だけをcurrent Capability Observationへ戻す。

- `availability = true`
- `provider_plan_resolved = true`

mapping provenanceは`tei-deployment-provider-plan-to-capability-observation/reference-v1`として区別する。

## Executable Evidence

`runtime/go/teiintegration/tei_cli_test.go`では、test binaryをhelper subprocessとして起動し、実際に別OS processを経由して次を検査した。

- executable / argumentsを明示的に注入できる。
- success responseをcurrent Capability Observationへmappingできる。
- mapping結果がcurrent validatorを通る。
- TEI固有field / valueがCapability Observationへ漏れない。
- unknown top-level fieldを拒否する。
- malformed JSONを拒否する。
- 複数JSON値を拒否する。
- 空のProvider Planを拒否する。
- process failure時にObservationを生成しない。
- timeout時にObservationを生成しない。
- 必須のTEI固有入力が欠けた場合はprocess起動前に拒否する。

文書同期前の検査点 `64537c156c2cec255f06a28a9fda6594674658f5` では、次がsuccessした。

- Plan integrity Run `33572094543`
- External Integration E3a Run `33572094551`
- Local Package Artifact Run `33572094571`
- External Integration E3b Run `33572094573`
- Semantic Runtime Conformance Run `33572094600`

Release Candidate Gate Run `33572094580`はGate 1〜8がsuccessし、OpenだったISSUE-000061をGate 9が意図どおりblockした。これは実装不備ではなく、未解決Issueをcandidateから排除する既存policyが正常に機能した結果である。

このhelper subprocess Evidenceは**external executable injection boundaryのScoped Executable Evidence**であり、actual `hat47x/tei-platform`のbinaryを実行したEvidenceではない。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

主な既存正本は次で今回の境界を表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

実TEIを接続した時点で、既存Requirementでは表現できない独立したProduct failureが確認された場合だけCandidate Requirementへ戻る。

## Non-goals / 未検証範囲

- SEI CIからprivate TEI repositoryを自動cloneすること
- cross-repository credential方式を標準化すること
- TEI binaryの配布・署名方式を決めること
- TEI CLI schemaをSEI Universal Contractにすること
- TEIをSEIの特別扱いされたProvider ontologyにすること
- actual TEI CLI executionのEvidenceをこのIssueだけで成立させること
- E3b-P2全体の完了
- external Cognitive Methodのlive実行
- E4 Operational portability
- Product Release / Release Evidence
- Adoption / Outcome Evidence

## 完了条件

- [x] TEI CLI external process Adapterを実装する。
- [x] executable pathとTEI固有入力を明示的に注入できるようにする。
- [x] success / malformed / unknown field / process failure / timeoutをtestへ落とす。
- [x] Provider固有fieldの非漏出をtestへ落とす。
- [x] current Capability Observation validatorを通す。
- [x] current runtime regressionを含むCIをsuccessさせる。
- [x] E3b-P1の最終Evidence記録を最新merge後CIへ同期する。
- [x] 上流計画へ、P2を「実行面」と「取得・credential境界」に分離する方針を反映する。
- [x] plan registry / document review registryを同期する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。

## Evidence state

- Design Evidence: **Satisfied for the current boundary**
- E3b-P1 public live Provider service: **Scoped Executable Evidence available**
- external TEI executable injection boundary: **Scoped Executable Evidence available with helper subprocess**
- E3b-P2 actual TEI CLI execution: **Not Yet Verified**
- E3b-M1 live external Cognitive Method execution: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- 実TEIのProvider Planを現在のAdapter-local DTOでは意味を壊さず読めない。
- executable acquisition方式をsemantic identityへ取り込まないと成立しないことが判明する。
- process failureとsemanticなUnknown / Conflictを現在の境界では区別できない。
- TEI CLI version差を追跡するため、current provenance / Referenceでは不足すると判明する。
- actual E3b-P2実行で、helper process testでは見えなかった独立したProduct failureが確認される。

## Natural Japanese review

PMS-06、ISSUE-000057 / 000058 / 000060、current Capability Observation Contract、Provider Adapter、`hat47x/tei-platform`の`cmd/tei`とReference Workspace、TEI CIで実行されている既存CLI面、今回のhelper subprocess testを照合した。TEIには実際に呼び出せるJSON CLI面がある一方、private repository取得をSEIの意味契約や必須CIへ暗黙に持ち込むべきではないため、executable acquisition、credential、process invocation、Provider固有JSON解釈、SEI mappingを分離した。今回成立したのは外部実行ファイルを受け入れる境界のScoped Executable Evidenceであり、helper processをactual TEI executionへ読み替えていない。E3b-P2は明示的に未検証のまま残す。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。