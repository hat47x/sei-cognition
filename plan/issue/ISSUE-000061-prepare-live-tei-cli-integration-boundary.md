# ISSUE-000061: 実TEI CLIを受け入れる外部process境界を準備する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Updated: 2026-09-02

## Goal

PMS-06のE3b-P2「live TEI process / service integration」へ進む前段として、**SOZAがTEIの取得方法やprivate repositoryのcredential方式を意味契約へ取り込まず、外部から与えられた実`tei` executableを別OS processとして呼び、そのProvider固有JSONをcurrent Capability Observationへ戻せる境界**を実体化する。

このIssueでは、実TEIをSOZA CIから取得・実行できたことまでは完了条件にしない。TEI repositoryはprivateであり、SOZAの標準`GITHUB_TOKEN`に別repositoryのread権限があるとは仮定できないためである。

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

とくに`deployment-provider-plan`は、durable deployment runとenvironmentからExecutor / Observation / Evidence Providerのroutingを導出し、JSONで返す既存面である。SOZA向けに新しいTEI protocolを作らず、Provider固有の実行面として扱える。

一方、`hat47x/tei-platform`はprivate repositoryである。SOZA CIから暗黙にcloneできることを前提にすると、credential方式がintegration semanticsへ混入し、再現性も利用環境依存になる。

そのため、このIssueでは次を分離する。

```text
TEI executable acquisition / credential
  != TEI process invocation
  != Provider-specific JSON interpretation
  != SOZA Capability Observation
```

## 対象surface

最初の境界ではTEI CLIの`deployment-provider-plan`を対象にする。

SOZA側は、TEI executableのpathとTEI固有入力pathを明示的に受け取る。repository clone、GitHub token、binary distributionはAdapterの外側に置く。

TEIから受け取るJSONはProvider固有DTOとして閉じ、SOZA Universal Contractへそのfield setを追加しない。

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

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

主な既存正本は次で足りると考える。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

実TEIを接続した時点で、既存Requirementでは表現できない独立したProduct failureが確認された場合だけCandidate Requirementへ戻る。

## Non-goals / 未検証範囲

- SOZA CIからprivate TEI repositoryを自動cloneすること
- cross-repository credential方式を標準化すること
- TEI binaryの配布・署名方式を決めること
- TEI CLI schemaをSOZA Universal Contractにすること
- TEIをSOZAの特別扱いされたProvider ontologyにすること
- actual TEI CLI executionのEvidenceをこのIssueだけで成立させること
- E3b-P2全体の完了
- external Cognitive Methodのlive実行
- E4 Operational portability
- Product Release / Release Evidence
- Adoption / Outcome Evidence

## 完了条件

- [ ] TEI CLI external process Adapterを実装する。
- [ ] executable pathとTEI固有入力を明示的に注入できるようにする。
- [ ] success / malformed / unknown field / process failure / timeoutをtestへ落とす。
- [ ] Provider固有fieldの非漏出をtestへ落とす。
- [ ] current Capability Observation validatorを通す。
- [ ] current runtime regressionを含むCIをsuccessさせる。
- [ ] E3b-P1の最終Evidence記録を最新merge後CIへ同期する。
- [ ] 上流計画へ、P2を「実行面」と「取得・credential境界」に分離する方針を反映する。
- [ ] plan registry / document review registryを同期する。
- [ ] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。

## Evidence state

- Design Evidence: **In Progress**
- E3b-P1 public live Provider service: **Scoped Executable Evidence available**
- external TEI executable injection boundary: **Not Yet Verified**
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

PMS-06、ISSUE-000057 / 000058 / 000060、current Capability Observation Contract、Provider Adapter、`hat47x/tei-platform`の`cmd/tei`とReference Workspace、TEI CIで実行されている既存CLI面を照合した。TEIには実際に呼び出せるJSON CLI面がある一方、private repository取得をSOZAの意味契約や必須CIへ暗黙に持ち込むべきではないため、executable acquisitionとprocess invocationを分離した。ISSUE-000061ではこの境界自体だけをExecutable Evidence化し、actual TEI executionはE3b-P2として明示的に未検証のまま残す。意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。