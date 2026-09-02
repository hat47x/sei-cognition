# ISSUE-000062: live external Cognitive Method executionを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0021, ADR-0025**  
Updated: 2026-09-02

## Goal

PMS-06のE3bについて、外部Provider serviceを実際に呼び出したE3b-P1からさらに進み、**SOZAとは別repositoryで開発されているCognitive Method実装を別processとして実際に起動し、その処理結果をSOZAの既存Cognitive Method Applicationへ戻せること**を確認する。

最初の対象にはpublic repository `hat47x/kj-atlas`を使う。KJ Atlasがすでに持つ`/ai/suggest-card-groups`をSOZA専用interfaceへ変更せず利用し、version固定したKJ Atlas backendをHTTP processとして起動する。

一方、CIで利用する生成器はKJ Atlas repositoryに含まれる決定的mock LLMである。このため、「KJ Atlas本体をliveに実行したこと」と「実外部AI modelを使ったこと」を分ける。

```text
E3b-M1a live KJ Atlas process + deterministic model stub
  → E3b-M1b live external model-backed KJ execution
```

M1a / M1bはEvidenceを段階的に確認するための作業上の区分であり、新しいProduct ontologyやUniversal Contractではない。

## Issue番号の整理

本作業はPR #38の開始時点では`ISSUE-000061`として進めていた。その後、並行して進行したPR #39が先に`develop/v0.2.0`へmergeされ、current planでは`ISSUE-000061`が「live TEI CLI integration boundary」の正本として確定した。

同一Issue IDを異なる意味へ割り当てないため、本作業のcurrent IDを`ISSUE-000062`へ改番する。旧PR headや旧CI logに現れる`ISSUE-000061`は改番前の歴史的な参照としてのみ扱い、current plan上の`ISSUE-000061`とは同一視しない。

## Resolution

`runtime/go/livemethodintegration`に、version固定したKJ AtlasのresponseをSOZAの既存Cognitive Method Applicationへ結び付けるreference Adapterを追加した。

専用`External Method Integration E3b` workflowでは、`hat47x/kj-atlas`を固定commitからcheckoutし、SQLite schemaをmigrationしたうえで、KJ Atlas repositoryに含まれるdeterministic model stubとFastAPI backendをSOZAとは別processとして起動する。その後、KJ Atlas自身の`POST /ai/suggest-card-groups`をHTTP経由で実際に呼び出した。

KJ Atlas固有の`groups`、`excludedCardIds`、`truncated`はUniversal Contractへ昇格させず、responseをopaqueな`not_verified` Method outputとして保持する。source repository、source commit、entry point、result digestもopaqueなProvenanceとして保持し、Cognitive Method Applicationから参照する。

```text
KJ Atlas response shape
  != SOZA Universal Cognitive Method Contract

grouping suggestion
  != Recommendation
  != Decision
```

通常のGo testでは、Recommendation / Decisionへの非昇格、invalid result、空のgroup label / card ID、duplicate targetを検査し、failure時にcanonical stateへ部分追加しないことを確認した。

live integrationでは、人間がreview済みのカード3件をKJ Atlasへ渡し、`doc.cards`側で`held`としたカードが`excludedCardIds`へ入り、grouping候補から除外されることまで確認した。これはhealth checkだけではなく、KJ Atlasのcurrent request model、LLM input IR、SafeMode、local model routing、response filteringを含む実処理経路を通している。

ただし、生成内容そのものはdeterministic model stubによるため、実外部AI modelの接続や認知的品質を実証したとは扱わない。

## 実装中に確認した境界

### 1. KJ Atlas current request contractとの不一致

最初のlive runでは、top-level `cards`へ`holdState`を渡したためHTTP 422となった。KJ Atlasのcurrent contractでは`holdState`は`doc.cards`側で表現するため、top-level cardから削除し、SafeMode用の`doc.cards`には保持した。

これはKJ Atlas側契約を弱めた修正ではなく、SOZA reference probeをcurrent contractへ合わせたものである。

### 2. opaque JSONの表現と意味内容

次のrunではactual HTTP grouping自体は成功したが、CanonicalStoreから再読したJSONについて、元responseの空白や改行までbyte-for-byte一致することをtestが要求していたため失敗した。

今回守るべき境界は、KJ Atlas responseをUniversal意味として推測せず`not_verified`のopaque outputとして保持し、JSON内容を失わないことである。空白まで同一のsource bytesを保存することではない。そのため、JSON意味等価を検査するtestへ修正した。

source bytesの完全同一性が将来必要になれば、Semantic Interchange上のopaque payloadとは別に、明示的なartifact / exact-binding要件として検討する。

## Closure CI Evidence

PR #38の改番前検査点 `44adf21ebfa38d976560514360eebdbbf08cbc25` では、本作業Issueを`In Progress`から`Resolved`へ同期する前の状態で、次の実装・回帰系CIがすべて**success**した。

- External Method Integration E3b Run `33572621975`
- Semantic Runtime Conformance Run `33572622165`
- Plan integrity Run `33572622330`
- External Integration E3a Run `33572622410`
- External Integration E3b Provider Run `33572621896`
- Local Package Artifact Run `33572622026`

同じ検査点のRelease Candidate Gate Run `33572621894`だけはGate 9でfailureとなった。原因は実装やconformanceの失敗ではなく、改番前の本作業Issueとplan registryが`In Progress`であり、v0.2.0 candidate policyが未解決Plan issueを正しくblockしたためである。

その後、本作業IssueをResolvedへ同期する過程でbase側に別の`ISSUE-000061`がmergeされたため、current base `c8c6fab583a60fc31f13348ccd2a895ef058eba2`を正として本作業を`ISSUE-000062`へ改番し、M1a成果を載せ直す。Release Candidate Gateはこの一意なResolved状態で再検査する。

このEvidence点を文書へ記録するcommit自身はSHAを変えるため、Evidence対象commitを常に文書HEADへ追従させる自己参照は行わない。

## Evidence境界

今回成立したのはE3b-M1aに限ったScoped Executable Evidenceである。

```text
E3b-M1a PASS
  != live external AI/model quality proven
  != E3b-M1b PASS
  != live TEI process/service PASS
  != production credential portability
  != Operational portability
  != Product Release / Release Evidence
  != Adoption / Outcome Evidence
```

mock LLMはKJ Atlasの実行経路を決定的に通すためのfixtureであり、その生成内容の認知的品質をSOZAのEvidenceへ昇格させない。

## Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しない。

今回の実証で確認したfailure boundaryは、既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの交換可能性
- REQ-0005 — historical Decision reconstruction
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

KJ Atlas、FastAPI、HTTP、SQLite、mock LLMという現在の実装方式だけを理由に新Requirementを作らない。

## 完了条件

- [x] KJ Atlas resultを既存Cognitive Method Applicationへmappingするreference Adapterを実装する。
- [x] grouping resultをRecommendation / Decisionへ自動昇格しないtestを追加する。
- [x] invalid result / duplicate targetでcanonical stateを壊さないnegative testを追加する。
- [x] KJ Atlasを固定commitから取得して別processとして起動する専用CIを追加する。
- [x] 専用CIでKJ Atlas FastAPIからactual grouping resultを取得する。
- [x] actual resultをSOZA Method Applicationへmappingし、current validatorを通す。
- [x] Semantic Runtime / Plan integrity等のcurrent regressionを維持する。
- [x] PMS-06 / Evidence文書へ結果を同期する。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] plan registry / document review registryを同期する。
- [x] 並行base更新によるIssue番号衝突を解消し、一意な`ISSUE-000062`へ改番する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。

## Evidence state

- Design Evidence: **Satisfied**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available**
- E3a version-pinned external artifact integration: **Scoped Executable Evidence available**
- E3b-P1 public live Provider service: **Scoped Executable Evidence available**
- E3b-M1a live KJ Atlas process + deterministic model stub: **Scoped Executable Evidence available** — External Method Integration E3b Run `33572621975`
- E3b-M1b live external model-backed KJ execution: **Not Yet Verified**
- E3b-P2 live TEI process / service: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- Resolved後の回帰CIがE3b-M1a変更に起因してfailureする。
- KJ Atlasのlive responseをopaque output + current Method Applicationでは意味を失わず保持できない。
- KJ Atlas固有schemaをUniversal Contractへ持ち込まないと実用上成立しないことが確認される。
- grouping候補とRecommendation / Decisionを分離すると必要な追跡性が失われる。
- external method failureとSOZAのUnknown / Conflictとの関係に新しいProduct-level規範が必要になる。
- 実外部modelを使うM1bで、M1aとは異なる恒久的な意味境界が必要と判明する。

## Natural Japanese review

PMS-06、`product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、ISSUE-000057 / 000058 / 000060 / 000061 / 000062、ADR-0017 / 0021 / 0025、current Cognitive Method Contract、`runtime/go/interactionprobe`、`runtime/go/livemethodintegration`、`runtime/LIVE_EXTERNAL_METHOD_EVIDENCE_2026-09-02.md`、KJ Atlasのcurrent backend README、`/ai/suggest-card-groups`のIR integration test、KJ session E2E、PR #38のactual workflow、PR #39で先行確定したTEI境界を照合した。KJ Atlas本体のlive実行とmock LLMの生成品質を分離し、外部Methodの結果をRecommendation / Decisionへ自動昇格させない境界を維持した。また、並行開発で生じたIssue番号衝突をcurrent baseへ戻って解消し、旧CI上の番号とcurrent正本の番号を混同しないよう来歴を残した。そのうえで、目的、実装結果、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
