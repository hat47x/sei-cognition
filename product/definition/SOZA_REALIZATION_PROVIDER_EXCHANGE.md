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

E3bでは、version固定artifactを読むだけでなく、SOZAとは独立した外部process / serviceを実際に呼びます。

一度にproduction integrationまで固定せず、現在はEvidenceを次の作業上のスライスへ分けています。

```text
E3b-P1 public live Provider service
  → E3b-P2 actual TEI process / service
  → E3b-M1 external Cognitive Method live execution
```

P1 / P2 / M1はEvidenceの収集範囲を明示するための区分であり、SOZAのUniversal ontologyではありません。

#### E3b-P1 — public live Provider service

ISSUE-000060では、public GitHub REST APIの固定commit取得面をreference Providerとして実際に呼びました。

- repository: `hat47x/cultural-substrate-weaving`
- expected commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`

live responseのcommit identityが期待値と一致した場合だけ、外部serviceへ到達できたことと期待revisionを確認できたことをcurrent Capability Observationへmappingします。GitHub固有の`node_id`、URL、response shape等はUniversal Contractへ転写しません。

また、revision mismatch、HTTP failure、timeout / cancellationではCapability Observationを生成しないことをローカル再現可能なtestで確認しました。

PR #37の最終head `ce56cf44426b2d061bf3bd57bbc7524f77736b4a`では、Plan integrity、External Integration E3a、Semantic Runtime Conformance、Local Package Artifact、External Integration E3b、Release Candidate Gateの6系統がすべてsuccessしました。

さらに、PR #37をmergeした`develop/v0.2.0` commit `655662d9b39718046c66862d370969a9a2a8b985`でも、次のpush workflowがすべてsuccessしています。

- External Integration E3a Run `33571264348`
- Plan integrity Run `33571264398`
- Local Package Artifact Run `33571264381`
- External Integration E3b Run `33571264402`
- Semantic Runtime Conformance Run `33571264359`
- Release Candidate Gate Run `33571264355`

この範囲については**Scoped Executable Evidence available**です。

ただし、v0.2.0 Release Candidateのsupported scopeはE3aまでです。Release Candidate Gateの回帰成功を理由に、E3b-P1をv0.2.0のsupported release scopeへ追加しません。

#### E3b-P2へ進むための外部実行境界

`hat47x/tei-platform`の実体を確認したところ、Go製CLI `cmd/tei`が存在し、`deployment-provider-plan`、`deployment-reconcile`、`deployment-simulate`等のJSON出力面が既に実装されています。

そのため、SOZA向けに新しいTEI protocolを作るのではなく、既存TEI CLIをProvider固有の外部processとして扱う方向を優先します。

一方、TEI repositoryはprivateです。SOZAの標準`GITHUB_TOKEN`が別private repositoryを読めるとは仮定しません。ISSUE-000061では次を分離しました。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

`runtime/go/teiintegration`では、外部から明示的に与えられたexecutableを使って`deployment-provider-plan`を呼べるreference Adapterを実装しました。Provider Plan JSONはAdapter-local DTOとしてstrictに検査し、TEI固有のExecutor、Observation route、Evidence route、Plugin Runtime等をUniversal fieldへ転写しません。

helper subprocessによるdeterministic testで、この外部実行ファイル注入境界にはScoped Executable Evidenceがあります。ただし、**helper subprocessのPASSはactual TEI CLI executionのEvidenceではありません**。

actual `hat47x/tei-platform`のsourceまたはbinaryが明示的に与えられる環境で実行できた時点で、E3b-P2のEvidenceを別に収集します。

#### E3b-M1 — 未検証

`cultural-substrate-weaving`にはversion管理されたSkill、platform adapter、build / validation基盤がありますが、現在のrepository調査では、Methodを独立processとして実行してRecommendationを返す標準runnerは確認できていません。

SOZA側が便宜的なrunnerを作って「実Cognitive Methodを実行した」とみなすことはしません。既存の実runnerまたは実際のhost integrationを特定できてからE3b-M1を設計します。

**Not Yet Verified.**

### E4 — operational portability

実運用でRealization / Providerを交換し、利用者が判断記憶を継続利用できることを確認します。

**Not Yet Verified.**

## 6. 外部artifact identityとsemantic identityを分ける

E3aでは、取得したartifactが本当に想定したsourceであるかを確認するため、repository、commit、path、Git blob identityを使います。また、検証済みbytesについてSHA-256も記録します。

E3b-P1では、live serviceから返された固定revisionが期待するrevisionと一致することを確認します。

ISSUE-000061では、TEI executable pathや実行引数をAdapter-local configurationとして扱い、binary取得経路やcredential解決をsemantic identityから分離します。

```text
repository / commit / path / blob identity
  != Method Definition identity
  != Capability identity
  != Decision identity

executable path / credential / process command
  != Capability identity
  != semantic authority
```

GitHub、Git、HTTP、CLIを使っていること自体をSOZA Universal Coreへ持ち込みません。他のartifact store、Provider service、process surfaceへ交換できる余地を残します。

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
9. live serviceやprocessの通信・終了成功そのものをsemantic authorityへ昇格させない。
10. acquisition / credential policyをProviderのUniversal semanticsとして固定しない。

## 8. 現在確認できているE3 Executable Evidence

### E3a

External Integration E3a Run `33528003902`では、次がすべてsuccessしました。

- version固定したpublic Cognitive Method artifactのlive fetch
- 取得したartifactのGit blob identity検証
- pinned snapshotとのbyte-for-byte一致
- TEI pinned snapshotのsource Git blob identity検証
- external artifact verification boundaryのGo test
- external Cognitive Method artifactからcurrent `MethodRealization`へのbinding test
- TEI固有observed stateからcurrent Capability Observationへのmapping test
- artifact identity mismatch時のcanonical非改変test

### E3b-P1

PR #37の最終headとmerge後`develop/v0.2.0`の双方で、External Integration E3bを含む6系統のCIがsuccessしました。merge後のRun IDは次です。

- External Integration E3a Run `33571264348`
- Plan integrity Run `33571264398`
- Local Package Artifact Run `33571264381`
- External Integration E3b Run `33571264402`
- Semantic Runtime Conformance Run `33571264359`
- Release Candidate Gate Run `33571264355`

External Integration E3bでは、ローカル再現可能なsuccess / revision mismatch / HTTP failure / timeout / field non-leakage testに加え、public GitHub REST APIへのactual live callと固定commit identityの確認を実行しました。

### E3b-P2 preparation boundary

ISSUE-000061では、test binaryをhelper subprocessとして実際に別OS processで起動し、外部executable注入、TEI Provider Plan相当JSONのstrict decode、process failure、timeout、Provider固有field非漏出、current Capability Observation validationを検査しました。

これは**external TEI executable injection boundaryのScoped Executable Evidence**です。

```text
helper subprocess PASS
  != actual TEI CLI execution PASS
  != E3b-P2 PASS
```

E3b全体を成立とはしません。

```text
E3a PASS + E3b-P1 PASS + TEI injection boundary PASS
  != external Method execution PASS
  != live private-repository acquisition PASS
  != actual TEI process / service PASS
  != production credential / network / rate-limit portability
  != E3b全体 PASS
  != E4 Operational portability
  != Product Release / Release Evidence
  != Adoption / Outcome Evidence
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

E2のout-of-process化、E3aの外部artifact取得、E3b-P1のpublic live Provider invocation、ISSUE-000061の外部executable注入境界は、これらのRequirementに対するEvidenceを厚くするための実証です。Git repository、HTTP、GitHub REST API、TEI CLIという現在の実装方式だけを理由に、新しいProduct Requirementを作りません。

今後actual E3b-P2 / M1を実行したとき、既存Requirementでは表現できない独立したProduct failureが見つかった場合には、Open Question / Candidate Requirementへ戻して再検討します。

## 10. 現時点で固定しないこと

- production AI Provider
- production SaaS / TEI integration protocol
- gRPC / HTTP / MCP / stdio等の正式Realization protocol
- process isolationを全Realizationへ強制すること
- Plugin SDKの正式仕様
- Provider discovery / marketplace
- GitHubを唯一のartifact source / Provider serviceとすること
- private repository credential方式
- TEI binaryの取得・配布・署名方式
- retry / circuit breaker / queue方式
- secret management
- billing / rate limit model
- production Provider SLA

## 11. Evidence状態

- E1 Contract / in-process synthetic: **Scoped Executable Evidence available**
- E2 out-of-process reference exchange: **Scoped Executable Evidence available**
- E3a version-pinned external artifact integration: **Scoped Executable Evidence available** — External Integration E3a Run `33528003902`
- E3b live external process / service integration: **Partial**
  - E3b-P1 public live Provider service: **Scoped Executable Evidence available** — merge後 External Integration E3b Run `33571264402`
  - external TEI executable injection boundary: **Scoped Executable Evidence available with helper subprocess**
  - E3b-P2 actual TEI process / service: **Not Yet Verified**
  - E3b-M1 live external Cognitive Method execution: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 12. 関連文書

- `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../runtime/LIVE_EXTERNAL_PROVIDER_EVIDENCE_2026-09-02.md`
- `../../plan/issue/ISSUE-000057-materialize-out-of-process-realization-provider-exchange.md`
- `../../plan/issue/ISSUE-000058-materialize-version-pinned-external-artifact-integration.md`
- `../../plan/issue/ISSUE-000060-materialize-first-live-external-provider-integration.md`
- `../../plan/issue/ISSUE-000061-prepare-live-tei-cli-integration-boundary.md`
- `../../plan/adr/ADR-0013-capability-realization-boundary.md`
- `../../plan/adr/ADR-0017-reference-model-cognitive-method-boundary.md`
- `../../plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`
- `../../plan/adr/ADR-0025-cognitive-method-portable-contract-boundary.md`

## 13. Natural Japanese review

Product Value、PMS-06、v0.2.0 Release Acceptance、REQ-0001 / 0004 / 0005 / 0007 / 0021、SCN-0005 / 0014 / 0018、Cognitive Method Contract、Capability Observation Contract、Provider Adapter、ISSUE-000057 / 000058 / 000060 / 000061、E2のactual process test、E3aで使用した`cultural-substrate-weaving`とTEIの外部source、PR #37の最終headとmerge後`develop/v0.2.0`のE3b-P1 Evidence、`hat47x/tei-platform`の実CLIとprivate repository条件、ISSUE-000061のhelper subprocess testへ戻り、Realization / Provider交換で何を変えてよく、何を判断記憶として維持する必要があるかを再監査した。E3bをpublic live Provider、actual TEI、live external Cognitive Methodへ作業上分割し、さらにTEIについてsource / binary acquisition、credential、process invocation、Provider固有JSON解釈、SOZA mappingを分離した。これにより、最初のnetwork invocation成功やhelper process成功をactual TEI、production portability、Product Releaseへ広げていない。また、GitHubやTEIだけを特別なProvider ontologyとして扱わず、外部固有responseをAdapter境界の内側に保った。意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。