# SOZA Realization / Provider Exchange

更新日: 2026-09-02  
状態: **Current Realization / Provider Exchange Design Baseline**

## 1. この文書の役割

この文書は、PMS-06「実際のMethod / Providerを交換しても判断記憶が保たれる」を進めるために、**何を交換可能とみなし、交換後にも何をcanonicalな判断記憶として守るか**をProduct levelで定めます。

SOZAにとって重要なのは、特定のAI、Prompt、process、SaaS、TEI、custom codeを長く使い続けることではありません。それらが入れ替わった後にも、当時のIntent、Observation、Method Application、Recommendation、Decision、Responsibility、Provenance、Unknown / Conflictを、その時点の意味を壊さず読み直せることです。

## 2. 交換してよいものと、交換で失ってはならないもの

### 交換してよいもの

- Cognitive Method Realization
- AI model / Prompt / code-assisted tool
- Capability Provider
- Provider Adapter
- external SaaS / TEI / custom code
- process topology
- Realization固有のwire protocol
- artifact repositoryや配布経路

### 交換で黙って変えてはならないもの

- Method Definitionの意味
- Method ApplicationがどのRealizationを使ったか
- Capability Definitionのidentity
- Capability ObservationがどのProvider / mappingから来たか
- RecommendationとDecisionの区別
- historical Decisionのbasis
- historical Responsibility
- 当時残っていたUnknown / Conflict
- Provenance / residual

```text
Realization exchange
  != Semantic Revision by itself

Provider exchange
  != Capability identity change by itself

new Recommendation
  != historical Decision rewrite
```

## 3. Cognitive Method exchange

同じCognitive Method Definitionに、複数のRealizationを持てます。

```text
Method Definition
   ├─ Realization A
   └─ Realization B
```

Method Applicationは、必要な場合に`realization_ref`を保持します。

Realization AとBが異なる出力を返しても、それぞれを異なるMethod Application / Recommendationとして扱います。後からRealization Bを使ったことを理由に、Realization Aを用いて作られた過去Decisionを現在版へ書き換えません。

Method Realizationの交換に、同じ結論を返すことは要求しません。守るべきなのは、**どのRealizationを使い、何を入力し、何を出力し、何を残差として残したかを区別して保持できること**です。

外部repositoryで配布されるSkillやPrompt pack等をRealizationとして使う場合も、repository名、commit、path等をCognitive MethodのUniversal fieldへ直接持ち込みません。取得元の情報はProvenanceとして保持し、Method Definition / Realizationの意味とartifact取得方式を分離します。

## 4. Provider exchange

同じCapabilityに複数Providerを対応させられます。

```text
Capability
   ├─ Provider A
   └─ Provider B
```

Provider固有stateは、そのままSOZA Universal Provider Stateへ統合しません。Provider Adapterを介し、その判断文脈で必要な観測だけをCapability Observationへmappingします。

ProviderをAからBへ変えても、Capability identityを自動的に変更しません。また、新しいProvider Observationが得られても、過去Decisionがbasisとして使ったAのObservationをBへ差し替えません。

TEIもこの原則の例外ではありません。TEI固有の`activeApplications`、`databases`、`dataReadiness`等はTEI側の表現として扱い、SOZAのUniversal Provider schemaへ昇格させません。

## 5. Evidence ladder

PMS-06では、交換可能性のEvidenceを次の段階に分けます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 operational portability
```

この段階は、技術の価値序列ではありません。何を実際に確認できたかを混同しないためのEvidence上の区分です。

### E1 — Contract / in-process synthetic

- Cognitive Method Definition / Realization / Applicationを型として分離できる。
- synthetic Provider A / BをAdapterで交換できる。

**Scoped Executable Evidence available.**

### E2 — out-of-process reference exchange

- Method Realizationを別OS processとして交換する。
- Provider state sourceを別OS processとして交換する。
- 出力をcurrent Contract / Adapterへ戻す。
- 交換後もhistorical Decisionを変更しない。

ISSUE-000057で**Scoped Executable Evidence available**です。

最終PR headではSemantic Runtime Conformance Run `33526188215`、Plan integrity Run `33526188237`、Local Package Artifact Run `33526188216`がsuccessしました。

### E3a — version固定した実外部artifact integration

E2のprocessはSOZA repository内で作ったreference Realizationでした。E3aでは、SOZAとは別repositoryで独立にversion管理される実artifactを扱います。

確認する中心は次です。

1. 外部repositoryとcommitによりsourceを固定できる。
2. 取得したbytesが期待するsource artifactと一致することを確認できる。
3. source repository / commit / path / blob identityをProvenanceとして保持できる。
4. 外部固有schemaをUniversal Contractへ持ち込まず、既存semantic boundaryへ戻せる。
5. source identity不一致時にcanonical stateを変更しない。

ISSUE-000058では二つの実外部artifactを使っています。

#### cultural-substrate-weaving

外部Cognitive Method側では、public repository `hat47x/cultural-substrate-weaving`の日本語版`weave` Skillを使います。

- commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`
- source path: `plugins/cultural-substrate-weaving-ja/skills/weave/SKILL.md`
- Git blob SHA-1: `4d1cd77a3561c4da58bc030936f28ae2386a81ce`

External Integration E3a Run `33528003902`では、GitHub Actionsからcommit固定のartifactを実際に取得し、Git blob identityとpinned snapshotのbyte一致を確認しました。その後、verified artifactを既存`MethodRealization`へ結び付けられることをGo testで確認しています。

ただし、これはSkill artifactを取得・検証してRealizationへ結び付けられたというEvidenceです。SkillをLLM上で実行し、Method Applicationや有用なRecommendationを得たことまでは示しません。

#### TEI

Capability Provider側では、private repository `hat47x/tei-platform`のobserved deployment stateを使います。

- commit: `3a20c59ce14929afa1e091e1418a2eb66f0ff32d`
- source path: `reference/observed/production.deployment-state.json`
- Git blob SHA-1: `ff3c60a8d9873f6aeb38549104ef6bb484404d17`

取得時にsource artifactと同じGit blob identityであることを確認したpinned snapshotをSOZA側のE3a fixtureとして保持し、TEI固有schemaをreference Adapterでcurrent Capability Observationへmappingします。

TEI repositoryはprivateです。SOZA CIの標準`GITHUB_TOKEN`へ別private repositoryのread権限を暗黙に要求しないため、E3aの必須CIではlive private fetchを行っていません。したがって、このPASSをlive TEI integrationとは扱いません。

### E3b — live external process / service integration

次の段階では、version固定artifactを読むだけでなく、SOZAとは独立した外部process / serviceを実際に呼びます。

対象候補には次があります。

- TEI CLIの既存JSON出力面
- external Cognitive Method runner
- AI / SaaS / custom service

この段階では、credential、network failure、timeout、rate limit、version change等の現実の境界も扱います。

**Not Yet Verified.**

### E4 — operational portability

実運用でRealization / Providerを交換し、利用者が判断記憶を継続利用できることを確認します。

**Not Yet Verified.**

## 6. 外部artifact identityとsemantic identityを分ける

E3aでは、取得したartifactが本当に想定したsourceであるかを確認するため、repository、commit、path、Git blob identityを使います。また、検証済みbytesについてSHA-256も記録します。

ただし、これらは取得・Provenanceのための情報です。

```text
repository / commit / path / blob identity
  != Method Definition identity
  != Capability identity
  != Decision identity
```

GitHubやGitを使っていること自体をSOZA Universal Coreへ持ち込みません。他のartifact storeへ交換できる余地を残します。

外部sourceのProvenanceは、current E3a probeではopaqueな`external-artifact-provenance` recordとして保持します。これは新しいUniversal Contractを意味しません。SOZAがそのmetadataを理解済みの普遍的意味として宣言するのではなく、source由来を失わず残すためのreference Realizationです。

## 7. Acceptanceの中心

交換の成功を「異なるRealization / Providerが同じ文字列を返した」とは定義しません。

次を中心に検査します。

1. 同じMethod Definitionに異なるRealization Refを結べる。
2. 同じCapabilityに異なるProvider Refを結べる。
3. Realization / ProviderごとのProvenanceを保持できる。
4. 新しいRecommendationを過去Decisionへ自動反映しない。
5. 新しいProvider Observationを過去basisへ自動差し替えしない。
6. failed Realization / Provider / artifact verificationがcanonical sourceを中途半端に変更しない。
7. process / binary / vendor / repositoryのidentityをsemantic identityへ短絡させない。
8. 外部固有fieldをUniversal Contractへ漏らさない。

## 8. 現在確認できているE3a Executable Evidence

External Integration E3a Run `33528003902`では、次がすべてsuccessしました。

- version固定したpublic Cognitive Method artifactのlive fetch
- 取得したartifactのGit blob identity検証
- pinned snapshotとのbyte-for-byte一致
- TEI pinned snapshotのsource Git blob identity検証
- external artifact verification boundaryのGo test
- external Cognitive Method artifactからcurrent `MethodRealization`へのbinding test
- TEI固有observed stateからcurrent Capability Observationへのmapping test
- artifact identity mismatch時のcanonical非改変test

同じ初期headでは、Plan integrity Run `33528003813`とLocal Package Artifact Run `33528003781`もsuccessし、Semantic Runtime Conformance Run `33528003760`のruntime-conformance jobもsuccessしました。

このEvidenceから、E3aの限定範囲についてはScoped Executable Evidenceがあると判断します。

一方、E3全体を成立とはしません。

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

## 9. Requirement / Scenario

現時点では、新しいStable Requirement / Scenarioを追加しません。

主な既存正本は次です。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Cognitive Methodの独立性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0007 — Capability / Providerの中立性
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive MethodとRealizationを交換する
- SCN-0014 — Execution Providerを交換する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

E2のout-of-process化やE3aの外部artifact取得は、これらのRequirementに対するEvidenceを厚くするための実証です。Git repositoryやartifact取得という現在の実装方式だけを理由に、新しいProduct Requirementを作りません。

E3bで既存Requirementでは表現できない独立したProduct failureが見つかった場合には、Open Question / Candidate Requirementへ戻して再検討します。

## 10. 現時点で固定しないこと

- production AI Provider
- production SaaS / TEI integration protocol
- gRPC / HTTP / MCP / stdio等の正式Realization protocol
- process isolationを全Realizationへ強制すること
- Plugin SDKの正式仕様
- Provider discovery / marketplace
- GitHubを唯一のartifact sourceとすること
- private repository credential方式
- retry / circuit breaker / queue方式
- secret management
- billing / rate limit model
- production Provider SLA

## 11. Evidence状態

- E1 Contract / in-process synthetic: **Scoped Executable Evidence available**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available**
- E3a version-pinned external artifact integration: **Scoped Executable Evidence available** — External Integration E3a Run `33528003902`
- E3b live external process / service integration: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 12. 関連文書

- `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/issue/ISSUE-000057-materialize-out-of-process-realization-provider-exchange.md`
- `../../plan/issue/ISSUE-000058-materialize-version-pinned-external-artifact-integration.md`
- `../../plan/adr/ADR-0013-capability-realization-boundary.md`
- `../../plan/adr/ADR-0017-reference-model-cognitive-method-boundary.md`
- `../../plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`
- `../../plan/adr/ADR-0025-cognitive-method-portable-contract-boundary.md`

## 13. Natural Japanese review

Product Value、PMS-06、REQ-0001 / 0004 / 0005 / 0007 / 0021、SCN-0005 / 0014 / 0018、Cognitive Method Contract、Capability Observation Contract、Provider Adapter、ISSUE-000057 / 000058、E2のactual process test、E3aで使用した`cultural-substrate-weaving`とTEIの外部source、External Integration E3a Run `33528003902`へ戻り、Realization / Provider交換で何を変えてよく、何を判断記憶として維持する必要があるかを再監査した。E3をartifact integrationとlive process / service integrationに分けることで、semantic portabilityとrepository認証・network条件を混同していない。また、TEIだけを特別なProvider ontologyとして扱わず、外部Cognitive Methodと同じくProvenanceを持つ交換可能なRealizationとして位置付けた。外部sourceのbytesそのものはEvidenceとして改稿せず、SOZAが作成する説明・設計文書について、意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。