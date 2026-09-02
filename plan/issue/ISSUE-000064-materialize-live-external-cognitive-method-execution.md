# ISSUE-000064: live external Cognitive Method executionを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0021, ADR-0025**  
Updated: 2026-09-02

## Goal

PMS-06のE3bについて、**SOZAとは別repositoryで開発されているCognitive Method実装を別processとして実際に起動し、その処理結果をSOZAの既存Cognitive Method Applicationへ戻せること**を確認する。

最初の対象にはpublic repository `hat47x/kj-atlas`を使う。KJ Atlasが既に提供している`POST /ai/suggest-card-groups`をSOZA専用interfaceへ変更せず、version固定したKJ Atlas backendをHTTP processとして起動する。

CIで利用する生成器は、KJ Atlas repositoryに含まれる決定的model stubである。このため、KJ Atlas本体をliveに実行したことと、実外部AI modelを利用したことを明確に分ける。

```text
E3b-M1a live KJ Atlas process + deterministic model stub
  != E3b-M1b live external model-backed KJ execution
```

M1a / M1bはEvidenceの範囲を明らかにするための作業上の区分であり、新しいProduct ontologyやUniversal Contractではない。

## 並行作業からの再基線化

旧PR #41では、この作業を当時未使用だった`ISSUE-000063`として進めていた。その後、v0.2.0 Release Evidenceの正本化が先に完了し、current Planでは次が正式な番号体系となった。

```text
ISSUE-000061
  = external TEI executable injection boundary
  != actual E3b-P2 TEI execution

ISSUE-000062
  = v0.2.0 actual release publication workflow

ISSUE-000063
  = v0.2.0 actual Release Evidence

ISSUE-000064
  = E3b-M1a live KJ Atlas process execution
  != E3b-M1b external model-backed execution
```

旧PR #41に混在していた別方式のpost-release publication lifecycle変更は採用しない。current `develop/v0.2.0`で既に成立している`publish: false / publication_state: completed`とRelease Evidenceを保持したまま、M1aだけを最新developから再基線化した。

## Resolution

E3b-M1aの範囲について、**Scoped Executable Evidence available**と判断する。

専用GitHub ActionsからKJ Atlasを固定commitで取得し、KJ Atlas FastAPI backendとKJ Atlas同梱のdeterministic model stubをSOZAとは別processとして実際に起動した。そのうえで、KJ Atlas自身の`POST /ai/suggest-card-groups`をHTTP経由で呼び、actual responseをSOZAのreference Adapterへ戻した。

実行sourceは次へ固定している。

- repository: `hat47x/kj-atlas`
- commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- entry point: `POST /ai/suggest-card-groups`

この経路では、KJ Atlasのrequest model、LLM input IR、SafeMode、local model routing、response filteringを実際に通している。`doc.cards`で`holdState = held`としたカードが`excludedCardIds`へ除外されることも確認した。

KJ Atlas固有responseはSOZAのUniversal Contractへ昇格させない。JSON内容をopaqueな`not_verified` Method outputとして保持し、source repository、commit、entry point、result digestはopaqueなProvenanceとして残す。existing Cognitive Method Applicationは`realization_ref`、`output_refs`、`provenance_refs`からそれらを参照する。

また、KJ Atlasのgrouping候補をRecommendationやDecisionへ自動昇格させない。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision
```

## 実装

### SOZA reference Adapter

`runtime/go/livemethodintegration`に、KJ Atlas grouping responseをcurrent semantic boundaryへ戻すreference Adapterとtestを追加した。

主な検査は次のとおり。

- 必須の`groups`がないresponseを拒否する。
- group labelやcard IDの空値を拒否する。
- KJ Atlas固有responseをUniversal fieldへ展開しない。
- external resultをopaqueな`not_verified` Method outputとして保持する。
- source identityとresult digestをopaque Provenanceとして保持する。
- Cognitive Method ApplicationからRealization / output / Provenanceを参照する。
- grouping候補をRecommendation / Decisionへ自動昇格させない。
- duplicate targetやinvalid resultでcanonical stateを部分更新しない。

### live external Method workflow

`.github/workflows/external-method-integration-e3b.yml`では次を実行する。

1. SOZAをcheckoutする。
2. KJ Atlasを固定commitでcheckoutする。
3. KJ Atlas backendをinstallする。
4. SQLiteへAlembic migrationを適用する。
5. deterministic model stubを別processとして起動する。
6. KJ Atlas FastAPI backendを別processとして起動する。
7. `POST /ai/suggest-card-groups`をactual HTTPで呼ぶ。
8. held cardの除外とgrouping responseを確認する。
9. SOZA側のmapping boundary testを実行する。
10. actual external resultをCognitive Method Applicationへmappingする。

## 実証中に確認した境界

### KJ Atlas current request contract

旧実証の初回live run `33571948264`では、KJ Atlasの起動まで成功したものの、actual grouping requestがHTTP 422で拒否された。

原因は、top-level `cards`の要素へ`holdState`を渡したことだった。KJ Atlasのcurrent requestでは`holdState`を`doc.cards`側で表現するため、top-level cardから取り除き、`doc.cards`には残した。

これはKJ Atlas側のSafeModeやIR契約を弱めた修正ではなく、SOZA reference probeをcurrent contractへ合わせた修正である。

### opaque JSONの意味保存

次の旧run `33572079736`ではactual HTTP groupingは成功したが、SOZA側testがCanonicalStoreから再読したJSONに元responseの空白や改行までbyte-for-byte一致することを要求していたため失敗した。

今回守るべき境界は、外部responseをUniversal意味として推測せず`not_verified`として保持し、JSONの意味内容を失わないことである。空白まで同一のsource bytesをSemantic Interchange上で保存することではない。

そのためtestをJSON意味等価の検査へ修正した。将来source bytesそのものの完全同一性が必要になった場合は、opaque payloadとは別にartifact / Exact Bindingの要求として検討する。

## current developからの再基線化Evidence

v0.2.0 Release Evidenceを含むactual `develop/v0.2.0` commit `5abc9abdd16456b60ebb1f006d65377c1ca51d29`から新しいbranchを作成し、PR #43の最初の検査点 `99401a36c30f810d67ccb70223c5fcfc5f601b6c`で再実行した。

次の6系統がすべて**success**した。

- External Method Integration E3b Run `33586593177`
- Semantic Runtime Conformance Run `33586593147`
- Local Package Artifact Run `33586593233`
- External Integration E3a Run `33586593241`
- External Integration E3b Provider Run `33586593190`
- Release Candidate Gate Run `33586593209`

専用M1a workflowでは、KJ Atlasの取得・install・migration・model/backend process起動・actual grouping・SOZA mapping boundary test・actual result mappingまでがすべてsuccessした。

Release Candidate Gate Run `33586593209`ではGate 1〜9がすべてsuccessした。v0.2.0は既にrelease済みであるため、`prepare-v0-2-0-release`と`publish-v0-2-0`はどちらも意図どおり**skipped**された。

```text
current-base M1a PASS
  + candidate regression PASS
  + publication skipped
  != v0.2.0 republished
```

## v0.2.0との関係

v0.2.0はcommit `c3640bdfcc43652b63a5b9941fd6b472312ec28f`をsourceとしてactual tag / GitHub Releaseまで公開済みであり、Local Reference Product BaselineのRelease Evidenceも`ISSUE-000063`でSatisfiedと評価済みである。

本Issueはrelease後に追加するScoped Executable Evidenceであり、v0.2.0のsupported scopeを変更しない。v0.2.0でsupportを主張するRealization / Provider exchangeの範囲はRelease AcceptanceとRelease Notesどおり**E3aまで**である。

```text
post-release E3b-M1a Evidence exists
  != v0.2.0 supported scope expanded
  != v0.2.0 Release Evidence expanded
```

## Evidence境界

今回成立したのはM1aに限定されたScoped Executable Evidenceである。

```text
E3b-M1a PASS
  != live external AI/model quality proven
  != E3b-M1b PASS
  != actual E3b-P2 live TEI PASS
  != production credential portability
  != E4 Operational portability
  != Operational Evidence
  != Adoption / Outcome Evidence
```

model stubはKJ Atlasの実処理経路を決定的に通すためのfixtureであり、その生成内容の認知的品質をSOZAのEvidenceへ昇格させない。

## Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しない。

今回確認したfailure boundaryは、既存の次のRequirement / Scenarioで表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

KJ Atlas、FastAPI、HTTP、SQLite、deterministic model stubという現在の実装方式だけを理由に、新しいProduct Requirement、Scenario、Universal Contract、正式integration protocolを作らない。

## 完了条件

- [x] KJ Atlas resultを既存Cognitive Method Applicationへmappingするreference Adapterを実装する。
- [x] grouping resultをRecommendation / Decisionへ自動昇格しないtestを追加する。
- [x] invalid result / duplicate targetでcanonical stateを壊さないnegative testを追加する。
- [x] KJ Atlasを固定commitから取得して別processとして起動する専用CIを追加する。
- [x] 専用CIでKJ Atlas FastAPIからactual grouping resultを取得する。
- [x] actual resultをSOZA Method Applicationへmappingする。
- [x] v0.2.0 Release Evidence確定後の最新developから再基線化する。
- [x] Release Evidence用のISSUE-000063と衝突しないISSUE-000064へ再番号化する。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] current-baseでM1aと主要回帰CIをsuccessさせる。
- [x] M1a検査によって既存v0.2.0を再publishしないことを確認する。
- [x] 自然な日本語を最重要視した全文再ドラフトと最終意味監査を行う。

## Evidence state

- Design Evidence: **Established for M1a scope**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available**
- E3a version-pinned external artifact integration: **Scoped Executable Evidence available**
- E3b-P1 public live Provider service: **Scoped Executable Evidence available**
- external TEI executable injection boundary: **Scoped Executable Evidence available with helper subprocess**
- E3b-P2 actual TEI CLI execution: **Not Yet Verified**
- E3b-M1a live KJ Atlas process + deterministic model stub: **Scoped Executable Evidence available** — Run `33586593177`
- E3b-M1b live external model-backed KJ execution: **Not Yet Verified**
- v0.2.0 supported scope: **E3aまで。変更しない**
- v0.2.0 Release Evidence: **Satisfied for the released Local Reference Product Baseline; M1aは対象外**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

- merge後の`develop/v0.2.0`回帰がM1a変更に起因してfailureする。
- KJ Atlasのlive responseをopaque output + current Method Applicationでは意味を失わず保持できないことが判明する。
- KJ Atlas固有schemaをUniversal Contractへ持ち込まないと実用上成立しないことが確認される。
- grouping候補とRecommendation / Decisionを分離すると必要な追跡性が失われる。
- external Method failureとSOZAのUnknown / Conflictとの関係に新しいProduct-level規範が必要になる。
- 実外部modelを使うM1bで、M1aとは異なる恒久的な意味境界が必要と判明する。
- M1a追加によって既存`v0.2.0`を再publicationしようとする回帰が生じる。

## Natural Japanese review

PMS-06、current `develop/v0.2.0`のRealization / Provider Exchange、ISSUE-000057 / 000058 / 000060 / 000061 / 000062 / 000063、v0.2.0 Release Acceptance / Release Notes / Release Evidence、ADR-0017 / 0021 / 0025、current Cognitive Method Contract、`runtime/go/interactionprobe`、`runtime/go/teiintegration`、KJ Atlas固定commitのcurrent backend、旧PR #41と再基線化PR #43のactual workflow Evidenceを照合した。

Release Evidence用のISSUE-000063を上書きせず、Cognitive Method側のlive実行をISSUE-000064として独立させた。KJ Atlas本体のlive実行とdeterministic model stubの生成品質、Method outputとRecommendation / Decision、M1aのpost-release Executable Evidenceとv0.2.0のsupported release scopeをそれぞれ分離している。

以上の意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
