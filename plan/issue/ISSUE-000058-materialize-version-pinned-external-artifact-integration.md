# ISSUE-000058: version固定した実外部artifact integrationを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0017, ADR-0019, ADR-0021, ADR-0024, ADR-0025**  
Updated: 2026-09-02

## Goal

PMS-06のE3「real external integration」へ進む前段として、SEI repository内で作ったreference processではなく、別repositoryで独立にversion管理されている実Cognitive Method / Provider artifactを取得・検証し、取得元のidentityとProvenanceを失わずにcurrent SEI semanticsへ結び付けられることを確認する。

この段階をE3aと呼ぶ。

```text
E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 operational portability
```

E3aはE3全体の完了ではない。

## Resolution

E3aでは、外部artifactの取得・identity検証と、live process / service invocationを分離した。

`runtime/go/externalartifact`でversion固定したsource bytesを検証し、`runtime/go/externalintegration`で検証済みartifactを既存Cognitive Method / Capability Observation boundaryへ戻す構成を実体化した。

新しいUniversal Contractは追加していない。外部repository、commit、path、Git blob identityは取得・Provenanceのための情報として扱い、Method Definition、Capability、Decision等のsemantic identityへ昇格させていない。

## なぜartifact段階を分けたか

E2では別OS processを実際に起動したが、そのprocess自体はSEI repository内で作ったreference Realizationだった。

次の段階ではSEIとは独立して変更されるsourceを扱う必要がある。一方、production AI API、private repository credential、TEI live process、rate limit、SLA等を一つのtestへ同時に混ぜると、semantic portabilityとnetwork / authentication上の問題を切り分けにくい。

そこでE3aでは、まず次を独立に確認した。

1. 外部repositoryとcommitでsourceを固定する。
2. 取得したbytesが想定したsource artifactと一致することを検証する。
3. source repository / commit / path / blob identityをProvenanceとして保持する。
4. 外部固有schemaをUniversal Contractへ持ち込まず、既存semantic boundaryへ戻す。
5. source identity不一致時にはcanonical stateを変更しない。

## 対象1 — cultural-substrate-weaving

外部Cognitive Method artifactとして、次を使用した。

- repository: `hat47x/cultural-substrate-weaving`
- commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`
- source path: `plugins/cultural-substrate-weaving-ja/skills/weave/SKILL.md`
- Git blob SHA-1: `4d1cd77a3561c4da58bc030936f28ae2386a81ce`

これは別repositoryで実際に配布されている日本語版`weave` Skill artifactである。

public repositoryであるため、External Integration E3a workflowではcommit固定のraw artifactをGitHub Actionsから実際に取得した。そのうえで、Git blob identityとSEI側のpinned snapshotがbyte-for-byteで一致することを確認した。

verified artifactはexisting `MethodRealization`へ結び付けた。repository / commit / path等の取得情報はCognitive Method Contractへ直接埋め込まず、opaqueなexternal artifact provenanceを`implementation_ref`から参照する形にした。

このEvidenceは、Skill artifactを取得・検証してRealizationへ結び付けられたことを示す。SkillをLLM上で実行し、Method Applicationや有用なRecommendationを生成したことまでは示さない。

## 対象2 — TEI

外部Capability Provider側のartifactとして、次を使用した。

- repository: `hat47x/tei-platform`
- commit: `3a20c59ce14929afa1e091e1418a2eb66f0ff32d`
- source path: `reference/observed/production.deployment-state.json`
- Git blob SHA-1: `ff3c60a8d9873f6aeb38549104ef6bb484404d17`

TEI自身が保持するobserved deployment stateを使った。TEI固有の`activeApplications`、`databases`、`dataReadiness`等はSEI Universal schemaにはしていない。

reference AdapterはTEI固有schemaを内部で読み、必要な観測だけをcurrent Capability Observationへ変換する。Provider identityは`tei-platform`として残し、source artifact provenanceとmapping provenanceも保持する。

TEI repositoryはprivateである。SEI CIの標準`GITHUB_TOKEN`へ別private repositoryのread権限を暗黙に要求しないため、E3aの必須CIではlive private fetchを行わない。取得時にsource artifactと同じGit blob identityであることを確認したpinned snapshotを用いてmappingを検査した。

したがって、TEI側のE3a PASSはlive TEI integrationを意味しない。private repository acquisitionやTEI CLI / serviceのlive invocationはE3b以降で扱う。

## 実装した境界

### `runtime/go/externalartifact`

- repository / commit / path / Git blob SHA-1をDescriptorとして受ける。
- Git blob identityが一致しないbytesを拒否する。
- 検証済みbytesについてSHA-256も記録する。
- source metadataをopaqueな`external-artifact-provenance` recordとして保持する。
- Git / GitHub固有概念をUniversal semantic entityにはしない。

Git blob identityを再現するためにSHA-1を使うが、SEIの新しいRepresentation Profileや一般用途のdigest方式としてSHA-1を採用したわけではない。検証済みbytesには別途SHA-256も保持する。

### `runtime/go/externalintegration`

- 外部Cognitive Method artifact → current `MethodRealization`
- TEI observed deployment state → current `Capability Observation`

TEI固有fieldはAdapter内部に閉じ、current Capability Observationへは必要な観測とProvenanceだけを返す。

## 必須検査の結果

1. **cultural-substrate-weavingのpinned Skillがsource Git blob identityと一致する** — Satisfied。
2. **public sourceをCIでcommit固定して実取得し、snapshotとbyte一致する** — Satisfied。
3. **verified Skill artifactをexisting Method Realizationへ結び付けられる** — Satisfied。
4. **repository / commit / path等をCognitive Method Contractへ直接漏らさない** — Satisfied。
5. **TEI pinned observed-state snapshotがsource Git blob identityと一致する** — Satisfied。
6. **TEI固有stateをcurrent Capability Observationへmappingできる** — Satisfied。
7. **mapped Observationがcurrent validatorを通る** — Satisfied。
8. **TEI固有input field名をCapability Observationへ漏らさない** — Satisfied。
9. **artifact identity不一致時にcanonical stateを変更しない** — Satisfied。
10. **public live fetch成功をprivate TEI live integrationやproduction portabilityへ昇格させない** — Evidence boundaryとして維持した。

## CI Evidence

初期E3a head `aafbad6d5598ca883a957bc426c8edc68119cdcb`で、外部artifact取得とsemantic mappingの成立を確認した。

- External Integration E3a Run `33528003902` — success
- Plan integrity Run `33528003813` — success
- Local Package Artifact Run `33528003781` — success
- Semantic Runtime Conformance Run `33528003760` — runtime-conformance job success

External Integration E3a Run `33528003902`では、次の全stepがsuccessした。

- version固定したpublic Cognitive Method artifactのlive fetch
- public artifactのGit blob identity検証
- pinned snapshotとのbyte-for-byte比較
- TEI pinned source snapshotのGit blob identity検証
- external artifact / semantic mapping boundaryのGo test

PRの作業中に`develop/v0.2.0`へcross-contract Exact Bindingの変更が統合されたため、その最新baseを親としてE3a差分を載せ直した。併せて、Plan integrityが検出した既存registryのファイル名不一致をactual treeに合わせて修正した。E3a以外の並行変更は取り込んだまま保持している。

その後のclosure head `afdd51056635ae7b7d3d16f8c53732895fdea1d8`では、次の4系統がすべてsuccessした。

- External Integration E3a Run `33529803952` — success
- Semantic Runtime Conformance Run `33529803957` — success
- Plan integrity Run `33529803963` — success
- Local Package Artifact Run `33529804070` — success

Plan integrity Run `33529803963`では、ADR / Issue / registry整合、Document Review Registry coverageを含む全stepがsuccessしている。

この結果から、最新`develop/v0.2.0`との整合を保ったclosure状態でも、E3aには限定されたExecutable Evidenceがあると判断する。

## Requirement / Scenario再監査

新しいStable Requirement / Scenarioは追加しない。

今回のProduct failureは既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

外部repositoryからartifactを取得したという実装事実は、それ自体では新しいProduct Requirementではない。

また、repository / commit / path / blob identityを新しいUniversal Contractへ固定する必要性も確認されなかった。これらはcurrent E3aの取得・Provenance Realizationとして保持する。

E3bでcredential、network failure、version交換等を扱った結果、既存Requirementでは防げない独立したProduct failureが確認された場合にのみOpen Question / Candidate Requirementへ戻す。

## Non-goals / 未検証範囲

- cultural-substrate-weaving SkillのLLM実行品質評価
- external Method Applicationのlive実行
- AI model / Promptのproduction選定
- TEI CLI / serviceのlive invocation
- private TEI repositoryのlive acquisition
- private repository credential方式の固定
- GitHubを唯一のartifact sourceにすること
- Git commit / path / blobをUniversal semantic identityにすること
- external artifact用Universal Contractを追加すること
- gRPC / HTTP / MCP / stdio等の正式integration protocol選定
- production retry / circuit breaker / secret management / SLA
- E4 Operational portability
- Release / Adoption / Outcome Evidence

```text
E3a PASS
  != external Method execution PASS
  != live private-repository acquisition PASS
  != live TEI process / service integration PASS
  != production credential / network / rate-limit portability
  != E3b PASS
  != E4 Operational portability
  != Release / Adoption / Outcome Evidence
```

## 完了条件

- [x] E3a / E3bをE3の内部段階として定義する。
- [x] cultural-substrate-weavingとTEIからversion固定する実artifactを選ぶ。
- [x] pinned source snapshotをfixtureとして置く。
- [x] external artifact identity verification境界を実装する。
- [x] 外部Method artifactをcurrent Method Realizationへ結ぶreference mappingを実装する。
- [x] TEI observed stateをcurrent Capability Observationへ戻すreference Adapterを実装する。
- [x] identity mismatch時のcanonical非改変をtestへ落とす。
- [x] public Cognitive Method artifactをlive fetchする専用CIを追加する。
- [x] current runtime regressionを含めCIをsuccessさせる。
- [x] E3a EvidenceをProduct Milestone / Product定義へ同期する。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を完了する。

## Evidence state

- Design Evidence: Satisfied
- E2 out-of-process reference exchange: Scoped Executable Evidence available
- E3a version-pinned external artifact integration: Scoped Executable Evidence available — closure headのExternal Integration E3a Run `33529803952`
- E3b live external process / service integration: Not Yet Verified
- E4 Operational portability: Not Yet Verified
- Release Evidence: Not Yet Verified
- Adoption / Outcome Evidence: Not Yet Verified

## Reopen / escalation条件

- source artifact identityをcurrent provenance modelで区別できない。
- Method Realizationと外部artifact versionの関係をhistorically再構成できない。
- TEI固有stateからCapability Observationへ戻す際に、current Contractでは保持できない独立した意味不足が確認された。
- GitHub以外のartifact sourceを追加したとき、current probe-local DescriptorではProduct failureを防げない。
- E3bでcredential / network / version交換にsemanticな追加Requirementが必要と判明した。

## Natural Japanese review

PMS-06、`product/definition/SEI_REALIZATION_PROVIDER_EXCHANGE.md`、ISSUE-000057、REQ-0001 / 0004 / 0005 / 0007 / 0021、SCN-0005 / 0014 / 0018、ADR-0013 / 0017 / 0019 / 0021 / 0024 / 0025、current Cognitive Method Contract、Capability Observation Contract、`runtime/go/externalartifact`、`runtime/go/externalintegration`、`cultural-substrate-weaving`とTEIの実source artifact、初期E3a Runとclosure headの4系統CIへ戻り、E2から実外部integrationへ進む際の意味境界とEvidenceを再監査した。外部artifactの取得・identity検証とlive process / service invocationを分けることで、semantic portabilityとrepository認証・network条件を混同していない。cultural-substrate-weavingとTEIを同じ外部artifact境界に置き、TEIだけを特別なProvider ontologyへ昇格させない構造も維持した。また、並行して`develop/v0.2.0`へ統合されたExact Bindingの変更を失わず、planning registryもactual treeと整合する状態へ戻した。外部sourceのbytesそのものはEvidenceとして改稿せず、SEIが作成する本文について、目的、検査結果、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。