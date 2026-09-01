# ISSUE-000060: 最初のlive external Provider integrationを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Updated: 2026-09-02

## Goal

PMS-06のE3b「live external process / service integration」について、version固定したartifactを読む段階から一歩進み、**SOZAとは独立した外部serviceをネットワーク越しに実際に呼び出し、その結果をProvider固有の表現のままUniversal Contractへ持ち込まず、current Capability Observationへ戻せること**を確認する。

E3bを一度に完成させることは目的としない。最初のスライスでは、追加credentialを必要としないpublic serviceを使い、live invocationとsemantic mapping、通信失敗時のcanonical非改変を切り分けて検証する。

```text
E3a version-pinned external artifact integration
  → E3b-P1 public live Provider service
  → E3b-P2 live TEI process / service
  → E3b-M1 live external Cognitive Method execution
  → E4 operational portability
```

ここでP1 / P2 / M1はEvidenceを段階的に集めるための作業上の区分であり、新しいProduct ontologyやUniversal Contractではない。

## 背景

ISSUE-000058では、SOZAとは別repositoryで独立にversion管理される実artifactについて、source identityを検証し、既存のMethod Realization / Capability Observation境界へ結び付けた。

ただし、E3aで実際に外部通信したのはpublic artifactの取得までであり、外部Provider serviceから応答を受け、その応答を判断文脈のObservationへ変換するlive integrationは未検証である。また、TEI repositoryはprivateであり、SOZA CIの標準`GITHUB_TOKEN`へ別private repositoryの権限を暗黙に要求することはできない。

そのため、最初のE3bでは次を分離する。

1. publicな外部serviceを実際に呼べること。
2. live responseをProvider固有stateとして扱い、current Capability Observationへmappingできること。
3. HTTP failure、応答identity不一致、timeout等でcanonicalな意味記録を生成しないこと。
4. protocolやProvider固有fieldをUniversal semantic identityへ昇格させないこと。
5. live public serviceの成功をTEI live integration、external Method execution、Operational Evidenceへ拡張しないこと。

## 最初の外部service

最初のreference ProviderとしてGitHub REST APIのcommit取得面を使う。

対象は、ISSUE-000058でも外部Cognitive Method artifactとして利用したpublic repositoryの固定commitとする。

- repository: `hat47x/cultural-substrate-weaving`
- expected commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`

GitHubをSOZAの標準Providerとする意図はない。追加credentialなしでもCIから到達でき、固定revisionを問い合わせることで、変動する現在値とlive network invocationを混同せず検査できるため、最初のreference serviceとして採用する。

```text
GitHub REST response
  != SOZA Universal Provider State

repository / commit / HTTP
  != Capability identity
  != Decision identity
```

## 実装方針

`runtime/go/liveintegration`にreference client / Adapter境界を置く。

live responseからSOZA側へ持ち込むのは、対象Capabilityについて観測できた最小限の事実とProvenanceだけとする。GitHub固有のowner、node ID、URL、API response shape等はUniversal Contractへ追加しない。

最初のObservationでは、少なくとも次を区別する。

- 外部serviceへ到達し正常応答を得られたこと。
- 期待した固定revisionがその応答で確認できたこと。

Provider identityはProvider固有の参照として保持するが、それをCapability identityへ短絡させない。

## 必須検査

1. public GitHub REST APIをCIから実際に呼び、固定commitを取得できる。
2. live responseのcommit SHAが期待値と一致する場合だけCapability Observationを生成する。
3. 生成したCapability Observationがcurrent validatorを通る。
4. Provider固有response fieldがCapability Observationへそのまま漏れない。
5. HTTP failure時にCapability Observationを生成しない。
6. response identity不一致時にCapability Observationを生成しない。
7. timeout / cancellation時にCapability Observationを生成しない。
8. live integration用HTTP client / JSON responseをUniversal Contractへ昇格させない。
9. 既存Contract、runtime、Interaction、Packaging、Access、Provider Adapter、Release Candidate gateの回帰を壊さない。
10. E3b-P1のPASSをE3b全体、TEI live integration、external Method execution、Operational / Release / Adoption Evidenceへ昇格させない。

## Requirement / Scenario監査

現時点では新しいStable Requirement / Scenarioを追加しない。

今回の検査対象は、主として既存の次に対するEvidenceを厚くするものと考える。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

live network integrationで既存Requirementでは防げない独立したProduct failureが確認された場合に限り、Candidate Requirementへ戻して再検討する。

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

- [ ] live external Provider client / Adapter境界を実装する。
- [ ] success / identity mismatch / HTTP failure / timeoutをローカル再現可能なtestへ落とす。
- [ ] Provider固有fieldの非漏出をtestへ落とす。
- [ ] public serviceを実際に呼ぶ専用CIを追加する。
- [ ] live CIで固定commitの取得・mappingを確認する。
- [ ] current runtimeとv0.2.0 Release Candidate gateを含むCIをsuccessさせる。
- [ ] PMS-06 / Realization Provider Exchange文書へEvidenceを同期する。
- [ ] Stable Requirement / Scenario追加の要否を再監査する。
- [ ] Evidence文書とplan registry / document review registryを同期する。
- [ ] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。

## Evidence state

- Design Evidence: **In Progress**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available**
- E3a version-pinned external artifact integration: **Scoped Executable Evidence available**
- E3b-P1 public live Provider service: **Not Yet Verified on the current Release Candidate baseline**
- E3b-P2 live TEI process / service: **Not Yet Verified**
- E3b-M1 live external Cognitive Method execution: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- live Provider responseをcurrent Capability Observationでは意味を失わず表現できない。
- network failureとsemanticなUnknown / Conflictの区別に新しいProduct-level規範が必要と判明する。
- Provider identityやmapping provenanceをcurrent Referenceで保持できない。
- credential / timeout / rate limitの扱いが既存REQ / SCNでは防げないProduct failureを生む。
- E3b-P2 / M1へ進んだとき、P1のreference境界では再利用できない意味上の不足が確認される。

## Natural Japanese review

PMS-06、`product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、ISSUE-000057 / 000058 / 000059、v0.2.0 Release Candidate baseline、REQ-0001 / 0007 / 0021、SCN-0014 / 0018、ADR-0013 / 0019 / 0021 / 0024、current Provider AdapterとCapability Observation Contractを照合した。E3bを一度にproduction integrationへ広げず、最初のpublic live Provider serviceを独立した実証単位として切り出した。GitHub REST APIの採用理由をreference serviceとして限定し、GitHub固有概念をUniversal Coreへ持ち込まない境界、通信失敗とsemantic meaningの分離、Release Candidate Evidenceを含む上位Evidenceへの非昇格を明示した。意味・規範強度・未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。