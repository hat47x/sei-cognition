# SOZA Product Milestones

更新日: 2026-09-02  
状態: **Current Deadline-free Product Milestone Baseline**

## 1. この文書の役割

この文書は、SOZAをどの順序で製品として成立させていくかを、日付や期限ではなく**成立条件とEvidenceの高さ**で示します。

Milestoneは開発管理上の目印です。SOZAのUniversal ontologyでも、利用者の業務workflowでも、特定versionに結び付いたrelease scheduleでもありません。

```text
Product Value
  → Product Milestone
  → Open Question / Experiment
  → Requirement / Acceptance Scenario
  → Issue / ADR
  → Architecture / Contract
  → Implementation / Evidence
```

未定の領域をMilestone文書だけからRequirementへ昇格させません。意味境界や必要性がまだ明らかでない場合は、議論、資料検討、prototype、fixture、実証実験等を先に行い、独立した規範上の必要性が確認できた場合だけRequirementへ反映します。

## 2. Milestoneの読み方

各Milestoneでは、少なくとも次を分けます。

- **Outcome** — 製品として何が成立している必要があるか。
- **Minimum Evidence** — 成立を判断する最低限のEvidence。
- **Current state** — 現在どこまで確認できているか。
- **Open questions** — 現時点では固定しない領域。

Milestoneには依存関係がありますが、すべてを直列に完了させる必要はありません。上位価値を壊さない範囲で、実証に必要な作業は並行できます。

## 3. PMS-00 — Product Valueと製品境界が正本化されている

### Outcome

SOZAが何のために存在し、何を価値として守り、何を自らの恒久的中心にしないかを説明できます。

少なくとも次が相互に矛盾せず読める状態を求めます。

- Product Value
- Value Proposition
- Value Model / Acceptance
- Product Vision
- Product Principles
- Product Shape
- SOZA / TEI / external Providerの境界

### Minimum Evidence

Design Evidence。

### Current state

**Established at Design level.**

下位実装やCIの存在だけを理由に、Operational / Adoption Evidenceへは昇格させません。

## 4. PMS-01 — 耐久的なsemantic substrateを機械的に扱える

### Outcome

判断仕事に必要な意味のうち、現在正本化されている範囲を、特定UIやStorageへ閉じ込めずに読み、検証し、再構成できます。

代表例はSemantic Reference、Decision Memory、Capability Observation、Cognitive Method、Semantic Interchange、Representation Profileです。

### Minimum Evidence

対象ContractごとのExecutable Evidence。

### Current state

**Scoped Executable Evidence available.**

Contract単体のPASSは、製品全体が利用可能であることを意味しません。

## 5. PMS-02 — 一つの判断仕事をend-to-endで再構成できる

### Outcome

次の代表的なProduct Journeyを、一続きの意味として検査できます。

```text
Inquiry
  → Observation / Evidence / Unknown / Conflict
  → Cognitive Method Application
  → Recommendation
  → Decision / Responsibility
  → external Capability / Execution
  → resulting Observation
  → historical review / reopen
```

この順序を固定workflowとして要求しません。重要なのは、複数の意味境界を同時に扱っても、RecommendationとDecision、過去のbasisと後から得たObservation、CapabilityとProvider等が混ざらないことです。

### Minimum Evidence

代表variantを含むfixture-scoped Executable Evidence。

### Current state

**Scoped Executable Evidence available.**

SCN-0018とend-to-end Semantic Product Journey harnessで、normal / uncertain / collaborative / provider replacement / no-execution等を限定範囲で検査しています。

## 6. PMS-03 — 人間とAIが最初のusable interactionから同じcanonical meaningへ触れられる

### Outcome

人間とAIが、同じcanonicalな判断文脈へ別の入口やProjectionから触れ、Inquiryの開始・再開、Observation追加、Recommendation / Decision確認、historical review等を一続きに行えます。

低影響な利用では最大詳細を強制せず、必要な場合だけaudit detailへ降りられることを求めます。

### Minimum Evidence

Interaction boundaryのDesign Evidenceと、最小prototypeまたはconformanceによるExecutable Evidence。

### Current state

**Design baseline established / scoped Executable Evidence available.**

`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028で、first usable Product Interactionをcanonical meaning上の操作境界として正本化しています。

ISSUE-000053では、human-oriented Surfaceとmachine-oriented Surfaceを同じcanonical sourceへ接続し、次を限定範囲で確認しました。

- machine側が追加したObservation / Recommendationをhuman側から再読できる。
- human側Decisionをmachine側がDecisionとして再読できる。
- RecommendationとDecisionを同一recordへ平坦化しない。
- Unknown / Conflictを失わない。
- Projection生成でcanonical sourceを変更しない。
- Surface-local stateを破棄してもcanonical recordを失わない。
- chat / UIだけの情報をcanonical Recommendation / Decisionへ昇格させない。
- post-decision Observationでhistorical Decision basisを書き換えない。
- machine SurfaceであることからResponsibilityを推定しない。

Semantic Runtime Conformance Run `33504002579`で、current Contract fixture再検査と`runtime/go`全体の`go test ./...`がsuccessしました。

```text
reference interaction probe PASS
  != production UX proven
  != supported protocol finalized
  != packaged product proven
  != Operational / Adoption Evidence
```

### Open questions

- productionで最初にsupportedとするhuman-facing Surface
- productionで最初にsupportedとするAI-facing access Surface
- Web / desktop / CLI / API / MCP等のsupported combination
- human usabilityを損なわずlight / auditを往復する具体UX
- Packaging / DeploymentとInteraction Surfaceの組み合わせ

これらは現時点でRequirementとして先取りしません。

## 7. PMS-04 — 配布・保存・再開が可能な最小製品単位が成立する

### Outcome

SOZAを実際に起動・配布し、canonical stateを保存し、後から再び開ける最小packageが成立します。

semantic boundaryとdeployable unitを混同せず、StorageやProviderを後から交換できる余地を保ちます。

### Minimum Evidence

Packaging / DeploymentのDesign Evidenceと、最小packageのExecutable Evidence。

### Current state

**Design baseline established / Minimum scoped Executable Evidence available.**

`product/packaging/SOZA_PRODUCT_PACKAGING.md`とADR-0029で、Local Single-Node Packageを最初のPackaging Profileとして正本化しました。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

ISSUE-000054では、filesystem Persistenceとbuild可能なGo executableを用い、process終了後の再読、copy / restore、Persistence交換、unknown Contractの`not_verified`保持、invalid state拒否等を限定範囲で確認しました。Semantic Runtime Conformance Run `33508376230`とPlan integrity Run `33508376256`はsuccessしています。

ISSUE-000055ではLinux / amd64向けのLocal Reference Packageを生成し、二重buildのbyte一致、build identity、決定的archive、checksum、展開後の独立process save / reloadを検査しました。Local Package Artifact Run `33509521544`ではworkflow artifact ID `9801021136`、digest `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`が記録されています。同一headのPlan integrity Run `33509521580`とSemantic Runtime Conformance Run `33509521596`もsuccessしました。

```text
PMS-04 Minimum scoped Evidence available
  != Product Release
  != formal platform support matrix
  != executable version upgrade proven
  != crash durability proven
  != actual production Storage migration proven
  != Release / Operational / Adoption Evidence
```

### Open questions

- Product Releaseとして最初にsupportするOS / architecture
- production向けarchive / installer / package manager / signing方式
- executable version upgrade後のresume
- productionで最初にsupportedとするhuman / AI Product Interaction Surface
- server-side StorageをいつRDB / object storeへ進めるか
- team / multi-user deployment topology
- online migration、production backup SLA、HA / replication
- container / cloud-managed distribution

これらはLocal Reference PackageのPASSだけを理由にRequirementへ固定しません。Releaseとして何をsupportするかはPMS-07で改めてEvidenceを要求します。

## 8. PMS-05 — identity・authorization・collaborationを製品として安全に扱える

### Outcome

semanticなResponsibility / Authorityと製品access controlを混同せず、single-userからteam / external collaborationへ進めます。

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

Selective Disclosureを扱う場合も、withheldとunknown等の意味差を失いません。

### Minimum Evidence

security / collaboration boundaryのDesign Evidenceと、対象範囲のExecutable Evidence。

### Current state

**Design baseline established / scoped Product Access separation Executable Evidence available / production IdP・team security pending.**

`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`とADR-0030でProduct Identity / Access / Collaboration boundaryを正本化し、ISSUE-000056の`runtime/go/accessprobe`で次を限定範囲で確認しました。

- 旧・新IdP相当identityを同じBounded Subjectへbindingできる。
- identity交換後もhistorical DecisionのResponsibility Refを書き換えない。
- semantic Responsibilityが存在してもProduct permissionがなければreadを拒否する。
- Product `administer` permissionを与えてもsemantic Responsibilityを生成しない。
- human / AI / serviceというactor kindだけからpermissionを推定しない。
- `not_evaluated`と`denied`を区別する。
- Selective Disclosureで非開示recordを`withheld`として扱う。
- Disclosure Projection生成前後でcanonical sourceを変更しない。

このEvidenceは責務分離を支持しますが、production OIDC / IAM、formal RBAC / ABAC、credential / session lifecycle、production Selective Disclosure securityを実証するものではありません。

### Candidate Requirement

次をCandidate Requirementとして保持します。

> SOZAの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出せず、認証identityとの対応を含むProduct Access Policyで独立に評価できる必要がある。

reference probeで用いたpermission vocabulary、Product Access Scopeの粒度、Identity Binding lifecycleはRealization依存であるため、新しいStable Requirement / Scenarioにはまだ昇格させません。

### Open questions

- 最初にsupportedとするauthentication方式
- Product Access Scopeの正式名称・granularity・lifecycle
- Product permission vocabularyとPolicy model
- hosted / team deploymentのmembership・invitation lifecycle
- production Selective Disclosureのsecurity boundary
- security audit eventのretention / tamper resistance
- enterprise IdP / directory integration
- encryption / key management

```text
Product Access probe PASS
  != production authentication proven
  != production authorization policy proven
  != production collaboration security proven
  != Release / Operational / Adoption Evidence
```

## 9. PMS-06 — 実際のMethod / Providerを交換しても判断記憶が保たれる

### Outcome

synthetic fixtureだけでなく、実際のCognitive Method Realization、AI、外部SaaS、TEI、custom code等を接続し、実現手段を交換してもIntent、Decision、Responsibility、Provenance等が壊れないことを確認します。

交換前後で同じ出力を得ることは要求しません。異なる出力や観測が生じても、それぞれの由来を保ったままhistorical Decisionを当時のbasisで再構成できることを求めます。

### Minimum Evidence

複数の実Realization / Providerを用いたExecutable Evidence。必要に応じて限定されたOperational Evidenceも収集します。

### Current state

**Partial / E2 Scoped Executable Evidence available / E3a Scoped Executable Evidence available / E3b-P1 Scoped Executable Evidence available / E3b-P2・M1 pending.**

`product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`で、交換してよいRealization / Providerと、交換後にも判断記憶として守る意味を正本化しています。

Evidenceは次の段階に分けます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 operational portability
```

E3bは、何を実際に確認したかを混同しないため、現在の作業上は次へ分けています。

```text
E3b-P1 public live Provider service
  → E3b-P2 actual TEI process / service
  → E3b-M1 external Cognitive Method live execution
```

このP1 / P2 / M1はEvidenceの範囲を示すための区分であり、新しいProduct ontologyではありません。

### E2 — out-of-process reference exchange

ISSUE-000057では、SOZA runtimeとは別のOS processとしてreference Provider A / Bとreference Method Realization A / Bを実際にbuild・起動しました。

次を確認しています。

- 異なるProvider固有stateを別Provider identityとして保持し、同じCapabilityへmappingできる。
- mapping後のCapability Observationをcurrent validatorへ戻せる。
- 同じMethod Definitionに対し、異なるMethod Realizationを実行できる。
- Method Applicationごとに異なる`realization_ref`を保持できる。
- 異なるRecommendationを生成してもDecisionへ自動昇格しない。
- Provider / Method交換後も交換前Decisionを変更しない。
- failed external processがcanonical sourceを変更しない。

PR #29の最終headでは、Semantic Runtime Conformance Run `33526188215`、Plan integrity Run `33526188237`、Local Package Artifact Run `33526188216`がsuccessしました。

### E3a — version固定した実外部artifact integration

ISSUE-000058では、SOZA repository内で作ったreference processから一段進み、**SOZAとは別repositoryで独立にversion管理される実artifact**を扱いました。

外部Cognitive Method側には、public repository `hat47x/cultural-substrate-weaving`の日本語版`weave` Skillを使っています。External Integration E3a Run `33528003902`では、commit固定のartifactをGitHub Actionsから実際に取得し、Git blob identityとpinned snapshotのbyte-for-byte一致を確認しました。その後、verified artifactをexisting `MethodRealization`へ結び付け、repository / commit / path等をCognitive Method Contractへ直接漏らさないことをGo testで確認しています。

Capability Provider側には、private repository `hat47x/tei-platform`のversion固定したobserved deployment stateを使っています。取得時にsource Git blob identityを確認したpinned snapshotを用い、TEI固有の`activeApplications`、`databases`、`dataReadiness`等をAdapter内に閉じたまま、current Capability Observationへ必要な観測だけをmappingしました。

source identity不一致時にはcanonical sourceを変更しないnegative caseも検査しています。

### E3b-P1 — public live Provider service

ISSUE-000060では、artifact取得だけではなく、SOZAとは独立したpublic serviceをネットワーク越しに実際に呼びました。

最初のreference Providerには、GitHub REST APIの固定commit取得面を使っています。

- repository: `hat47x/cultural-substrate-weaving`
- expected commit: `aa3651f3460a6db7dc70bd848f93b600f149ffe8`

live responseのcommit SHAが期待値と一致する場合だけ、外部serviceへ到達できたことと期待revisionを確認できたことをcurrent Capability Observationへmappingします。GitHub固有のresponse fieldはUniversal Contractへ転写しません。

ローカル再現可能なtestでは、successに加えてrevision mismatch、HTTP failure、timeout / cancellation、Provider固有fieldの非漏出を検査しました。

PR #37の最終head `ce56cf44426b2d061bf3bd57bbc7524f77736b4a` では、Plan integrity、External Integration E3a、Semantic Runtime Conformance、Local Package Artifact、External Integration E3b、Release Candidate Gateの6系統がすべてsuccessしました。

PR #37をmergeしたactual `develop/v0.2.0` commit `655662d9b39718046c66862d370969a9a2a8b985`でも、次のpush workflowがすべてsuccessしています。

- External Integration E3a Run `33571264348`
- Plan integrity Run `33571264398`
- Local Package Artifact Run `33571264381`
- External Integration E3b Run `33571264402`
- Semantic Runtime Conformance Run `33571264359`
- Release Candidate Gate Run `33571264355`

これにより、E3b-P1には統合後の`develop/v0.2.0`でも再現できるScoped Executable Evidenceがあると判断します。

ただし、v0.2.0 Release Candidateのsupported scopeはE3aまでです。Release Candidate Gateの回帰成功を理由に、E3b-P1をv0.2.0のsupported release scopeへ追加しません。

```text
E3a PASS + E3b-P1 PASS
  != external Method execution PASS
  != live private-repository acquisition PASS
  != actual TEI process / service PASS
  != production credential / network / rate-limit portability
  != E3b全体 PASS
  != E4 Operational portability
  != Product Release / Release Evidence
  != Adoption / Outcome Evidence
```

### E3b-P2へ進むための準備境界

E3b-P1の後、`hat47x/tei-platform`の実体を確認したところ、TEIにはGo製CLI `cmd/tei`があり、`deployment-provider-plan`、`deployment-reconcile`、`deployment-simulate`等のJSON出力面が既に存在します。

そのため、SOZA専用のTEI wire protocolを新設するのではなく、既存TEI CLIをProvider固有の外部processとして扱う方向を優先します。

一方、TEI repositoryはprivateです。SOZAの標準`GITHUB_TOKEN`が別private repositoryを読めるとは仮定しません。ISSUE-000061では、E3b-P2の前段として次を分離します。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

`runtime/go/teiintegration`では、外部から明示的に与えられた`tei` executableを呼び出せる境界を作り、Provider Plan JSONをAdapter内でstrictに検査したうえで、必要最小限の観測だけをCapability Observationへ戻します。

この境界のdeterministic testではhelper processを使います。helper processのPASSは、**actual TEI executableを実行したEvidenceではありません**。実TEI sourceまたはbinaryが明示的に与えられる環境で実行できた時点で、E3b-P2のEvidenceを別途収集します。

### E3b-M1の現在地

`cultural-substrate-weaving`にはversion管理されたSkill、platform adapter、build / validation基盤がありますが、現在のrepository調査では、Methodを独立processとして実行してRecommendationを返す標準runnerは確認できていません。

そのため、SOZA側が便宜的なrunnerを作り、それを「実Cognitive Methodのlive execution」とみなすことはしません。既存の実runnerまたは実際のhost integrationを特定できてから、E3b-M1の実験系を設計します。

### Open questions

- actual TEI executableをどの環境から、どのEvidence付きでSOZA integration testへ渡すか
- private repository credentialを使う必要がある場合、その処理をacquisition / deployment policyへどう閉じ込めるか
- TEI CLI version交換時に必要なProvenance / Exact Bindingの水準
- E3b-M1で利用する実Cognitive Method runnerまたはhost integration
- TEIと非TEI Providerをどの組み合わせで比較するか
- timeout以外のnetwork degradationやrate limitをどこまでProduct acceptanceへ含めるか
- production Realization protocolを標準化する必要が本当にあるか
- artifact source / live ProviderをGitHub以外へ交換したときのProvenance境界
- E4のOperational portabilityを何で測るか

E3b-P1やISSUE-000061の境界testだけを理由に、新しいStable Requirement、Universal Contract、正式integration protocolへ固定しません。

## 10. PMS-07 — release可能な製品として成立する

### Outcome

Product Valueを満たす最小supported scopeが明確で、配布物、versioning、migration、security、failure handling、release acceptanceを含めてrelease候補を再現可能に評価できます。

### Minimum Evidence

Release Evidence。

### Current state

**Actual v0.2.0 develop Release Candidate Evidence available / Release Evidence Not Yet Verified.**

`release/v0.2.0/RELEASE_ACCEPTANCE.md`では、同一candidate sourceに対してPlan、Requirements、Contract、Representation Profile、JCS probe、semantic runtime、Projection、Local Reference Package、candidate policyをまとめて検査するRelease Candidate Gateを定義し、actual `develop/v0.2.0`上のcandidate Evidenceまで記録しています。

これはRelease前のExecutable Evidenceを一つのcandidateへ束ねた記録です。actual tag / release identity / released artifactとの結び付きがない限り、Release Evidenceへ昇格しません。

PMS-06のE3b-P1とISSUE-000061の外部process境界は、current v0.2.0 supported scope外で進める追加のScoped Executable Evidenceです。これらのPASSを、既存candidate scopeの拡張やProduct Release成立へ自動反映しません。

## 11. PMS-08 — 実運用と利用者成果からProduct Valueを検証できる

### Outcome

実際の利用環境で、SOZAが単に動作しただけでなく、判断の再構成、引継ぎ、再検討、Provider交換、不確実性保持等に役立ったかを検証できます。

### Minimum Evidence

Operational Evidence、および対象価値に応じたAdoption / Outcome Evidence。

### Current state

**Not Yet Verified.**

## 12. 横断Milestone — Moving Rebaseline

PMS-00〜08とは別に、主要な技術変化・利用知見・反証Evidenceが得られた場合は、評価時点の現在から10〜50倍程度先を見渡すMoving Future Horizonで上位文書を再監査します。

これは最後に一度だけ行う工程ではありません。どのMilestoneでも、下位Evidenceが上位仮説を反証した時点でProduct Value / Vision / Principlesへ戻ります。

## 13. 未定領域の扱い

未定領域には、次の三状態を明確に認めます。

- **Open Question** — まだ何を要求すべきか自体が分からない。
- **Candidate Requirement** — 議論や実証から必要性が見えたが、重複・耐久性・適用範囲を未監査。
- **Stable Requirement** — Product Valueから独立した規範上の必要性を説明でき、既存REQとの重複を監査し、Acceptanceを定義できる。

Open Questionを直接Stable Requirementへ飛ばしません。

## 14. Natural Japanese review

Product Value、Value Proposition、Product Shape、Product Interaction、Product Packaging、Product Identity / Access / Collaboration、Realization / Provider Exchange、v0.2.0 Release Acceptance、REQ-0001〜0022、SCN-0005 / 0007 / 0008 / 0010 / 0012 / 0013 / 0014 / 0018、ADR-0024 / 0025 / 0028 / 0029 / 0030、ISSUE-000046 / 000047 / 000053〜000061、current Go runtime、Interaction / Packaging / Product Access / Realization exchange / External Integration E3a / E3b-P1 / actual v0.2.0 candidate Evidence、`hat47x/tei-platform`の実CLIとprivate repository条件へ戻ってMilestone全体を再監査した。PMS-03はscoped Interaction Executable Evidence、PMS-04はLocal Reference PackageによるMinimum scoped Executable Evidence、PMS-05はProduct Access責務分離のDesignとscoped Executable Evidence、PMS-06はE2、E3a、E3b-P1までを成立済みとして整理した。E3b-P1はPR #37の最終headだけでなくmerge後`develop/v0.2.0`でも6系統のCIがsuccessしている。一方、ISSUE-000061のhelper process testはactual TEI executionへ昇格させず、TEI executable acquisition、credential、process invocation、Provider固有JSON、SOZA mappingを分離した準備境界として位置付けた。PMS-07ではactual develop Release Candidate EvidenceをRelease Evidenceから分離し、current v0.2.0 supported scopeがE3aまでであることも維持した。external Methodのlive実行、actual TEI process / service、private credential portability、Operational portability、actual Product Release、Adoption / Outcome Evidenceは未検証のままである。意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
