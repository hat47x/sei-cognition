# ISSUE-000060: 最初のlive external Provider integrationを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Updated: 2026-09-02

## Goal

PMS-06のE3b「live external process / service integration」について、version固定したartifactを読む段階から一歩進み、SEIとは独立した外部serviceをネットワーク越しに実際に呼び出し、その結果をProvider固有の表現のままUniversal Contractへ持ち込まず、current Capability Observationへ戻せることを確認する。

E3bを一度に完成させることは目的としない。最初のスライスでは、追加credentialを必要としないpublic serviceを使い、live invocationとsemantic mapping、通信失敗時のcanonical非改変を切り分けて検証する。

```text
E3a version-pinned external artifact integration
  → E3b-P1 public live Provider service
  → E3b-P2 live TEI process / service
  → E3b-M1 live external Cognitive Method execution
  → E4 operational portability
```

ここでP1 / P2 / M1はEvidenceを段階的に集めるための作業上の区分であり、新しいProduct ontologyやUniversal Contractではない。

## Resolution

`runtime/go/liveintegration`に、public GitHub REST APIの固定commit取得面を実際に呼び出すreference clientを追加した。

対象は、ISSUE-000058でも外部Cognitive Method artifactとして利用したpublic repositoryの固定commitである。

- repository: `hat47x/cultural-substrate-weaving`
- expected commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`

live responseのcommit SHAが期待値と一致した場合だけ、外部serviceへ到達できたことと期待revisionを確認できたことをcurrent Capability Observationへmappingする。GitHub固有の`node_id`、URL、API response shape等はUniversal Contractへ転写しない。

通常のGo testでは`httptest`を使い、success、revision mismatch、HTTP failure、timeout / cancellation、Provider固有fieldの非漏出、不正repository指定を外部networkなしで再現可能にした。専用`External Integration E3b` workflowではpublic GitHub REST APIを実際に呼び、固定commitの取得とmappingを確認する。

```text
GitHub REST response
  != SEI Universal Provider State

HTTP success
  != semantic authority

repository / commit / HTTP
  != Capability identity
  != Decision identity
```

## 必須検査の結果

1. **public GitHub REST APIをCIから実際に呼び、固定commitを取得できる** — Satisfied。
2. **live responseのcommit SHAが期待値と一致する場合だけCapability Observationを生成する** — Satisfied。
3. **生成したCapability Observationがcurrent validatorを通る** — Satisfied。
4. **Provider固有response fieldがCapability Observationへそのまま漏れない** — Satisfied。
5. **HTTP failure時にCapability Observationを生成しない** — Satisfied。
6. **response identity不一致時にCapability Observationを生成しない** — Satisfied。
7. **timeout / cancellation時にCapability Observationを生成しない** — Satisfied。
8. **HTTP client / JSON responseをUniversal Contractへ昇格させない** — Design / implementation boundaryとして維持した。
9. **既存Contract、runtime、Interaction、Packaging、Access、Provider Adapterの回帰を壊さない** — current-baseline CIで確認した。
10. **E3b-P1をE3b全体やOperational / Release Evidenceへ昇格させない** — Product Milestone、Realization / Provider Exchange、Evidence文書へ明示した。

## Closure CI Evidence

PR #37では、Issue本文とregistryをResolvedへ同期した検査点 `12621fe67a6fbc6226da5b37f56fcc39d5066faf` で次の6系統がすべてsuccessした。

- External Integration E3b Run `33570935966`
- Semantic Runtime Conformance Run `33570935849`
- Plan integrity Run `33570935878`
- External Integration E3a Run `33570935851`
- Local Package Artifact Run `33570935996`
- Release Candidate Gate Run `33570935867`

External Integration E3bでは、deterministic boundary testとpublic GitHub REST APIへのactual live callの両方が成功している。Release Candidate GateもGate 9まで通過し、ISSUE-000060のResolved状態とcandidate blockerの整合を確認した。

このEvidence点を文書へ記録するcommit自身はSHAを変えるため、Evidenceの対象commitを常に文書HEADへ追従させる自己参照は行わない。以後の文書同期commitについては同じCI群で回帰を確認する。

## Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しない。

今回のlive network integrationで確認したfailure boundaryは、既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

HTTP、GitHub、固定commitという現在の実装方式だけを理由に、新しいProduct Requirementを作らない。

## PMS-06への反映

E3bを次の作業上のスライスへ分けた。

```text
E3b-P1 public live Provider service
  → E3b-P2 live TEI process / service
  → E3b-M1 live external Cognitive Method execution
```

今回のprobeによりE3b-P1にはScoped Executable Evidenceが成立した。

一方、E3b全体は引き続きPartialであり、live TEI、external Cognitive Method、private credential、network degradation / rate limit、E4 Operational portabilityは未検証である。

v0.2.0 Release Candidateのsupported scopeはE3aまでであり、本Issueを理由にcandidate scopeを暗黙に拡張しない。

## Non-goals / 未検証範囲

- GitHubをproduction標準Providerとすること
- GitHub REST APIをUniversal integration protocolとすること
- private repository credential方式の固定
- live TEI CLI / service integration
- external Cognitive Methodのlive実行
- production retry / circuit breaker / queue設計
- production secret management
- rate limit policyの標準化
- formal Provider SDK / protocol
- E3b全体の完了
- E4 Operational portability
- Product Releaseの成立
- Release / Adoption / Outcome Evidence

## 完了条件

- [x] live external Provider client / Adapter境界を実装する。
- [x] success / identity mismatch / HTTP failure / timeoutをローカル再現可能なtestへ落とす。
- [x] Provider固有fieldの非漏出をtestへ落とす。
- [x] public serviceを実際に呼ぶ専用CIを追加する。
- [x] live CIで固定commitの取得・mappingを確認する。
- [x] current runtime regressionを含むCIをsuccessさせる。
- [x] PMS-06 / Realization Provider Exchange文書へEvidenceを同期する。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] Evidence文書とplan registry / document review registryを同期する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。
- [x] Resolved状態の検査点でv0.2.0 Release Candidate GateをGate 9までsuccessさせる。

## Evidence state

- Design Evidence: Satisfied
- E2 out-of-process reference exchange: Scoped Executable Evidence available
- E3a version-pinned external artifact integration: Scoped Executable Evidence available
- E3b-P1 public live Provider service: Scoped Executable Evidence available — External Integration E3b Run `33570935966`
- E3b-P2 live TEI process / service: Not Yet Verified
- E3b-M1 live external Cognitive Method execution: Not Yet Verified
- E4 Operational portability: Not Yet Verified
- Release Evidence: Not Yet Verified
- Adoption / Outcome Evidence: Not Yet Verified

## Reopen / escalation条件

- Resolved後の回帰CIがE3b変更に起因してfailureする。
- live Provider responseをcurrent Capability Observationでは意味を失わず表現できない。
- network failureとsemanticなUnknown / Conflictの区別に新しいProduct-level規範が必要と判明する。
- Provider identityやmapping provenanceをcurrent Referenceで保持できない。
- credential / timeout / rate limitの扱いが既存REQ / SCNでは防げないProduct failureを生む。
- E3b-P2 / M1へ進んだとき、P1のreference境界では再利用できない意味上の不足が確認される。

## Natural Japanese review

PMS-06、`product/definition/SEI_REALIZATION_PROVIDER_EXCHANGE.md`、v0.2.0 Release Acceptance、ISSUE-000057 / 000058 / 000059、REQ-0001 / 0007 / 0021、SCN-0014 / 0018、ADR-0013 / 0019 / 0021 / 0024、current Provider Adapter、Capability Observation Contract、`runtime/go/liveintegration`のactual test、PR #37のclosure Evidence点を照合した。E3bを一度にproduction integrationへ広げず、最初のpublic live Provider serviceを独立した実証単位として完了させた。GitHub REST APIはreference serviceに限定し、GitHub固有概念をUniversal Coreへ持ち込まない境界、通信失敗とsemantic meaningの分離、E3b-P1から上位Evidenceへの非昇格を維持した。また、v0.2.0 Release Candidateのsupported scopeをE3aから暗黙に広げていない。そのうえで、目的、実装結果、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
