# ISSUE-000064: live external Cognitive Method executionを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0021, ADR-0025**  
Updated: 2026-09-02

## Goal

PMS-06のE3bについて、SEIとは別repositoryで開発されているCognitive Method実装を別processとして実際に起動し、その処理結果をSEIの既存Cognitive Method Applicationへ戻せることを確認する。

最初の対象にはpublic repository `hat47x/kj-atlas`を用いる。KJ Atlasが既に提供している`POST /ai/suggest-card-groups`をSEI専用interfaceへ変更せず利用し、固定revisionのKJ Atlas backendをHTTP processとして起動する。

CIで利用する生成器はKJ Atlas repositoryに含まれる決定的model stubである。このため、KJ Atlas本体の実処理経路をliveに通したことと、実外部AI modelを利用したことを分ける。

```text
E3b-M1a live KJ Atlas process + deterministic model stub
  → E3b-M1b live external model-backed KJ execution
```

M1a / M1bはEvidence範囲を区別するための作業上の名称であり、SEIの新しいProduct ontologyやUniversal Contractではない。

## Issue番号の整理

並行開発によって、v0.2.0 release系列が先にcurrent `develop/v0.2.0`へ統合された。現在の正本では次の番号を用いる。

```text
ISSUE-000061
  = external TEI executable injection boundary
  != actual E3b-P2 TEI execution

ISSUE-000062
  = v0.2.0 actual release publication workflow

ISSUE-000063
  = v0.2.0 actual Release Evidence

ISSUE-000064
  = E3b-M1a KJ Atlas live Cognitive Method execution
  != E3b-M1b external model-backed execution
```

Release Evidence系列の成果を上書きせず、本IssueをCognitive Method側の独立したEvidence軸として扱う。

## Resolution

E3b-M1aの範囲について、**Scoped Executable Evidence available**と判断する。

専用GitHub ActionsからKJ Atlasを固定commitで取得し、KJ Atlas FastAPI backendとKJ Atlas同梱のdeterministic model stubをSEIとは別processとして実際に起動する。そのうえで、KJ Atlas自身の`POST /ai/suggest-card-groups`をHTTP経由で呼び、actual responseをSEIのreference Adapterへ戻す。

実行元は次へ固定する。

- repository: `hat47x/kj-atlas`
- commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- entry point: `POST /ai/suggest-card-groups`

この経路では、KJ Atlasのrequest model、LLM input IR、SafeMode、local model routing、response filteringを実際に通す。`doc.cards`で`holdState = held`としたカードが`excludedCardIds`へ除外されることも検査する。

KJ Atlas固有responseはSEIのUniversal Contractへ昇格させない。JSONの意味内容をopaqueな`not_verified` Method outputとして保持し、source repository、commit、entry point、result digestはopaqueなProvenanceとして残す。既存Cognitive Method Applicationは`realization_ref`、`output_refs`、`provenance_refs`からそれらを参照する。

また、KJ Atlasのgrouping候補をRecommendationやDecisionへ自動昇格させない。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision
```

## 実装

### SEI reference Adapter

`runtime/go/livemethodintegration`に、KJ Atlas grouping responseをcurrent semantic boundaryへ戻すreference Adapterとtestを置く。

検査する主な境界は次のとおり。

- 必須の`groups`がないresponseを拒否する。
- group labelやcard IDの空値を拒否する。
- KJ Atlas固有responseをUniversal fieldへ展開しない。
- external resultをopaqueな`not_verified` Method outputとして保持する。
- source identityとresult digestをopaque Provenanceとして保持する。
- Cognitive Method ApplicationからRealization / output / Provenanceを参照する。
- grouping候補をRecommendation / Decisionへ自動昇格させない。
- invalid resultやduplicate targetでcanonical stateを部分更新しない。

### live external Method workflow

`.github/workflows/external-method-integration-e3b.yml`では次を実行する。

1. SEIをcheckoutする。
2. KJ Atlasを固定commitでcheckoutする。
3. KJ Atlas backendをinstallする。
4. SQLiteへAlembic migrationを適用する。
5. deterministic model stubを別processとして起動する。
6. KJ Atlas FastAPI backendを別processとして起動する。
7. `POST /ai/suggest-card-groups`をactual HTTPで呼ぶ。
8. held cardの除外とgrouping responseを確認する。
9. SEI側のmapping boundary testを実行する。
10. actual external resultをCognitive Method Applicationへmappingする。

## 実証中に得た補正

### KJ Atlas current request contract

初回live runでは、KJ Atlasの起動後にactual grouping requestがHTTP 422で拒否された。原因は、top-level `cards`の要素へ`holdState`を渡していたことだった。

current KJ Atlasでは`holdState`を`doc.cards`側で表現するため、top-level cardから取り除き、`doc.cards`には残した。これはKJ Atlas側のSafeModeやIR契約を弱める変更ではなく、SEI reference probeをcurrent contractへ合わせた補正である。

### opaque JSONの意味保存

次の実行ではactual HTTP groupingが成功した一方、SEI側testがCanonicalStoreから再読したJSONについて空白や改行までbyte-for-byte一致することを要求していた。

今回守るべき境界は、外部responseをUniversal意味として推測せず`not_verified`として保持し、JSONの意味内容を失わないことである。空白まで同一のsource bytesをSemantic Interchangeへ保存することではない。

そのためtestはJSON意味等価を確認するようにした。将来source bytesそのもののExact Bindingが必要になった場合は、opaque payloadとは別のartifact / binding要件として検討する。

## Executable Evidence

### 再基線化前のlive Evidence

再基線化前のPR #41でも、KJ Atlas取得、install、migration、model/backend process起動、actual grouping、SEI mapping boundary test、actual result mappingまでを専用workflowで実行し、成功した。

代表的な成功Runは次のとおり。

- External Method Integration E3b Run `33584876930`
- External Method Integration E3b Run `33585078576`

### current developへの再基線化後

並行作業でv0.2.0 Release Evidenceが先に`develop/v0.2.0`へ統合されたため、PR #41はcurrent develop commit `5abc9abdd16456b60ebb1f006d65377c1ca51d29`から作り直した。

再基線化後のbehavior-complete head `0313f707a352dec7bec0eb40f8e3a980e74c9eae`では、次のPR workflowがすべてsuccessした。

- External Method Integration E3b Run `33587455439`
- Plan integrity Run `33587455472`
- Semantic Runtime Conformance Run `33587455445`
- External Integration E3a Run `33587455452`
- External Integration E3b Run `33587455442`
- Local Package Artifact Run `33587455447`
- V6 V7 Projection Evaluation Run `33587455441`
- Release Candidate Gate Run `33587455459`

専用M1a Run `33587455439`では、KJ Atlas checkout、backend install、Alembic migration、model/backend process起動、actual grouping、SEI mapping boundary test、actual result mappingまでの主要stepがすべてsuccessした。

Release Candidate Gate Run `33587455459`ではGate 1〜9がsuccessし、公開済みv0.2.0に対する`prepare-v0-2-0-release`と`publish-v0-2-0`はともにskipされた。したがって、M1aの回帰検査によって既存v0.2.0を再publicationしていない。

このRun群は、M1aの意味上の成立範囲を広げるものではなく、current repositoryとの統合回帰が成立したことを示す。

## v0.2.0との関係

v0.2.0 Local Reference Product Baselineについては、`release/v0.2.0/RELEASE_EVIDENCE.md`によりRelease Evidenceが別途Satisfiedとなっている。

本Issueはrelease後に追加するM1aのScoped Executable Evidenceであり、v0.2.0のsupported scopeを変更しない。v0.2.0でsupportを主張するRealization / Provider exchangeの範囲は、Release AcceptanceとRelease Notesどおり**E3aまで**である。

```text
post-release E3b-M1a Evidence exists
  != v0.2.0 supported scope expanded

v0.2.0 Release Evidence Satisfied
  != E3b-M1a included in that release
```

## Evidence境界

```text
E3b-M1a PASS
  != live external AI/model quality proven
  != E3b-M1b PASS
  != actual E3b-P2 live TEI PASS
  != v0.2.0 supported scope expansion
  != Operational Evidence
  != Adoption / Outcome Evidence
```

model stubはKJ Atlasの実処理経路を決定的に通すためのfixtureであり、その生成内容の認知的品質をSEIのEvidenceへ昇格させない。

## Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しない。

今回確認するfailure boundaryは、既存の次のRequirement / Scenarioで表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの交換可能性
- REQ-0005 — historical Decision reconstruction
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

KJ Atlas、FastAPI、HTTP、SQLite、deterministic model stubという現在の実装方式だけを理由に、新Requirement、Scenario、Universal Contract、正式integration protocolを作らない。

## 完了条件

- [x] KJ Atlas resultを既存Cognitive Method Applicationへmappingするreference Adapterを実装する。
- [x] grouping resultをRecommendation / Decisionへ自動昇格しないtestを追加する。
- [x] invalid result / duplicate targetでcanonical stateを壊さないnegative testを追加する。
- [x] KJ Atlasを固定commitから取得して別processとして起動する専用CIを追加する。
- [x] 専用CIでKJ Atlas FastAPIからactual grouping resultを取得する。
- [x] actual resultをSEI Method Applicationへmappingする。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] ISSUE-000061〜000063の並行成果を保持し、M1aをISSUE-000064として再構成する。
- [x] v0.2.0 Release EvidenceとM1a Evidenceを分離する。
- [x] 最新`develop/v0.2.0`をbaseにしたbehavior-complete branchで8系統の回帰CIをsuccessさせる。
- [x] 自然な日本語を最重要視して全文を再ドラフトし、最終意味監査を行う。
- [ ] merge後`develop/v0.2.0`でM1a専用workflowを含む回帰CIを確認する。

## Evidence state

- Design Evidence: **Established for M1a scope**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available**
- E3a version-pinned external artifact integration: **Scoped Executable Evidence available**
- E3b-P1 public live Provider service: **Scoped Executable Evidence available**
- external TEI executable injection boundary: **Scoped Executable Evidence available with helper subprocess**
- E3b-P2 actual TEI CLI execution: **Not Yet Verified**
- E3b-M1a live KJ Atlas process + deterministic model stub: **Scoped Executable Evidence available**
- E3b-M1b live external model-backed KJ execution: **Not Yet Verified**
- v0.2.0 Release Evidence: **Satisfied separately for Local Reference Product Baseline**
- v0.2.0 supported scope: **E3aまで。変更しない**
- E4 Operational portability: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- merge後の`develop/v0.2.0`回帰がM1a変更に起因してfailureする。
- KJ Atlasのlive responseをopaque output + current Method Applicationでは意味を失わず保持できないことが判明する。
- KJ Atlas固有schemaをUniversal Contractへ持ち込まないと実用上成立しないことが確認される。
- grouping候補とRecommendation / Decisionを分離すると必要な追跡性が失われる。
- external Method failureとSEIのUnknown / Conflictとの関係に新しいProduct-level規範が必要になる。
- 実外部modelを使うM1bで、M1aとは異なる恒久的な意味境界が必要と判明する。

## Natural Japanese review

PMS-06、最新`develop/v0.2.0`のRealization / Provider Exchange、ISSUE-000057〜000063、v0.2.0 Release Acceptance / Release Evidence、ADR-0017 / 0021 / 0025、current Cognitive Method Contract、KJ Atlas固定commit、再基線化後のPR #41 actual workflow Evidenceを照合した。

Release Evidence系列を巻き戻さず、Cognitive Method側のM1aだけをISSUE-000064として独立させた。技術固有の実装語彙をUniversal semanticsへ持ち込まず、KJ Atlasのgrouping候補とRecommendation / Decisionの意味差、M1aとM1bのEvidence差、v0.2.0 supported scopeとの非包含関係が自然に読めるよう全文を組み直している。

意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
