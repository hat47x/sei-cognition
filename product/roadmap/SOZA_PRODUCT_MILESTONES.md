# SOZA Product Milestones

更新日: 2026-09-03  
状態: **Current Deadline-free Product Milestone Baseline — v0.2.0 Release Evidence / E3b-P2 / E3b-M1b / historical reconstruction / quality-evaluation boundary reflected**

## 1. この文書の役割

この文書は、SOZAをどの順序で製品として成立させていくかを、日付や期限ではなく**成立条件とEvidenceの高さ**で示します。

Milestoneは開発管理上の目印です。SOZAのUniversal ontologyでも、利用者の業務workflowでも、特定versionへ固定されたrelease scheduleでもありません。

```text
Product Value
  → Product Milestone
  → Open Question / Experiment / Human Review
  → Requirement / Acceptance Scenario
  → Issue / ADR
  → Architecture / Contract
  → Implementation / Evidence
```

未定領域をMilestone文書だけからRequirementへ昇格させません。意味境界や必要性がまだ明らかでない場合は、議論、資料検討、prototype、fixture、実証実験、人間レビュー等を先に行い、独立した規範上の必要性が確認できた場合だけRequirementへ反映します。

GitHub Actionsは当面完全に停止しています。Milestoneの成立条件は実行基盤から分離し、必要なchecker、test、probeはローカルで個別に実行します。

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

少なくともProduct Value、Value Proposition、Value Model / Acceptance、Vision、Principles、Product Shape、SOZA / TEI / external Providerの境界が相互に矛盾せず読める状態を求めます。

### Minimum Evidence

Design Evidence。

### Current state

**Established at Design level.**

下位実装や検証手段の存在だけを理由に、Operational / Adoption Evidenceへは昇格させません。

## 4. PMS-01 — 耐久的なsemantic substrateを機械的に扱える

### Outcome

判断仕事に必要な意味のうち、現在正本化されている範囲を、特定UIやStorageへ閉じ込めずに読み、検証し、再構成できます。

代表例はSemantic Reference、Decision Memory、Capability Observation、Cognitive Method、Semantic Interchange、Representation Profileです。

### Minimum Evidence

対象ContractごとのExecutable Evidence。

### Current state

**Scoped Executable Evidence available.**

current runtimeでは、known Contractのtyped read / validate / reconstruct、Representation Verifier Registry、Payload Source、Cognitive Method、Exact Binding consistency等を限定範囲で検査しています。

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

```text
journey harness PASS
  != production Product Journey validated
  != human interaction validated
```

## 6. PMS-03 — 人間とAIが最初のusable interactionから同じcanonical meaningへ触れられる

### Outcome

人間とAIが、同じcanonicalな判断文脈へ別の入口やProjectionから触れ、Inquiryの開始・再開、Observation追加、Recommendation / Decision確認、historical review等を一続きに行えます。

低影響な利用では最大詳細を強制せず、必要な場合だけaudit detailへ降りられることを求めます。

### Minimum Evidence

Interaction boundaryのDesign Evidenceと、最小prototypeまたはconformanceによるExecutable Evidence。

### Current state

**Design baseline established / scoped Executable Evidence available.**

`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028で、first usable Product Interactionをcanonical meaning上の操作境界として正本化しています。

ISSUE-000053のreference probeでは、人間向け・machine向けSurfaceが同じcanonical sourceを扱うこと、Recommendation / Decision分離、Unknown / Conflict保持、Projection非権威性、historical Decision basis非改変等を確認しました。

```text
reference interaction probe PASS
  != production UX proven
  != supported protocol finalized
  != Operational / Adoption Evidence
```

### Open questions

- productionで最初にsupportedとするhuman-facing Surface
- productionで最初にsupportedとするAI-facing access Surface
- Web / desktop / CLI / API / MCP等のsupported combination
- human usabilityを損なわずlight / auditを往復する具体UX

これらは現時点でRequirementとして先取りしません。

## 7. PMS-04 — 配布・保存・再開が可能な最小製品単位が成立する

### Outcome

SOZAを実際に起動・配布し、canonical stateを保存し、後から再び開ける最小packageが成立します。

semantic boundaryとdeployable unitを混同せず、StorageやProviderを後から交換できる余地を保ちます。

### Minimum Evidence

Packaging / DeploymentのDesign Evidenceと、最小packageのExecutable Evidence。

### Current state

**Design baseline established / Minimum scoped Executable Evidence available.**

`product/packaging/SOZA_PRODUCT_PACKAGING.md`とADR-0029で、Local Single-Node Packageを最初のPackaging Profileとして正本化しています。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

ISSUE-000054ではprocess終了後の再読、copy / restore、Persistence交換、unknown Contractの`not_verified`保持、invalid state拒否等を限定範囲で確認しました。

ISSUE-000055ではLinux / amd64向けLocal Reference Packageについて、二重buildのbyte一致、build identity、deterministic archive、checksum、展開後の独立process save / reloadを検査しました。

v0.2.0 releaseでは、このLocal Reference Packageをactual release assetとして配布し、release preparationで得たSHA-256とGitHub Release asset digestの一致まで確認しています。

```text
PMS-04 scoped Evidence available
  != formal platform support matrix
  != production Storage migration proven
  != crash durability proven
  != Operational Evidence
```

### Open questions

- Product Releaseとして今後正式にsupportするOS / architecture
- production向けinstaller / package manager / signing方式
- executable version upgrade後のresume
- team / multi-user deployment topology
- online migration、backup SLA、HA / replication

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

`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`とADR-0030で境界を正本化し、ISSUE-000056のreference probeではidentity交換後のResponsibility continuity、Product accessとsemantic Responsibilityの分離、`not_evaluated` / `denied`、Selective Disclosure等を限定範囲で確認しています。

### Candidate Requirement

> SOZAの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出せず、認証identityとの対応を含むProduct Access Policyで独立に評価できる必要がある。

reference probe固有のpermission vocabularyやscope粒度はRealization依存であるため、Stable Requirementへ先取りしません。

### Open questions

- 最初にsupportedとするauthentication方式
- Product Access Scopeの正式なgranularity / lifecycle
- formal RBAC / ABACの必要性
- hosted / team deploymentのmembership lifecycle
- production Selective Disclosure security
- encryption / key management

## 9. PMS-06 — 実際のMethod / Providerを交換しても判断記憶が保たれる

### Outcome

synthetic fixtureだけでなく、実際のCognitive Method Realization、AI、外部SaaS、TEI、custom code等を接続し、実現手段を交換してもIntent、Decision、Responsibility、Provenance等が壊れないことを確認します。

交換前後で同じ出力を得ることは要求しません。異なる出力や観測が生じても、それぞれの由来を保ったままhistorical Decisionを当時のbasisで再構成できることを求めます。

### Minimum Evidence

複数の実Realization / Providerを用いたExecutable Evidence。必要に応じて限定されたOperational Evidenceも収集します。

### Current state

**Partial / E2 + E3a + E3b-P1 + E3b-P2 fixed-artifact + E3b-M1a + E3b-M1b + historical reconstruction + actual model artifact exchangeまでScoped Executable Evidence available / runtime version exchange・E4 pending.**

Evidenceを次の段階に分けます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 Operational portability
```

E3bは、Provider側とCognitive Method側の異なるfailure boundaryを混同しないため、現在は次のように分けています。

```text
E3b
  ├─ P1 public live Provider service
  ├─ P2 actual TEI process / service
  │    ├─ preparation: external TEI executable injection boundary
  │    ├─ fixed-artifact actual TEI CLI execution [Scoped Evidence]
  │    └─ private artifact acquisition / credential lifecycle / arbitrary version [pending]
  └─ M1 live external Cognitive Method
       ├─ M1a live KJ Atlas process + deterministic model stub [Scoped Evidence]
       └─ M1b live external model-backed KJ execution [Scoped Evidence]
```

この区分はEvidenceの範囲を示すためのもので、新しいProduct ontologyではありません。

### E2 — out-of-process reference exchange

ISSUE-000057では、SOZA runtimeとは別のOS processとしてreference Provider A / Bとreference Method Realization A / Bを実際にbuild・起動し、Provider / Method交換後もhistorical Decisionを変更しないこと、異なるRecommendationをDecisionへ自動昇格しないこと等を確認しました。

### E3a — version固定した実外部artifact integration

ISSUE-000058では、SOZAとは別repositoryで独立にversion管理されるartifactを扱いました。

- Cognitive Method側: `hat47x/cultural-substrate-weaving`のversion固定artifact
- Capability Provider側: `hat47x/tei-platform`のversion固定observed deployment state

source identityを確認し、Provider / repository固有情報をUniversal Contractへ漏らさず、current Cognitive Method / Capability Observation boundaryへ戻すことを検査しています。

### E3b-P1 — public live Provider service

ISSUE-000060では、SOZAとは独立したpublic serviceをネットワーク越しに実際に呼びました。reference ProviderにはGitHub REST APIの固定commit取得面を利用し、期待revisionと一致する場合だけCapability Observationへmappingしています。

revision mismatch、HTTP failure、timeout / cancellation、Provider固有fieldの非漏出も検査しました。

### E3b-P2 — actual TEI process / service

ISSUE-000061では、actual TEI CLI integrationの前段として、TEI source / binary acquisition、credential resolution、external process invocation、Provider-specific JSON decoding、SOZA Capability Observation mappingを分離しました。

ISSUE-000065の最初のcredential-aware Run `33589190828`では、`TEI_REPOSITORY_TOKEN`を利用できずactual TEI stepがskipされました。この記録は`runtime/ACTUAL_TEI_INTEGRATION_PROBE_EVIDENCE_2026-09-02.md`へそのまま保持しています。

その後、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定し、historical TEI-side Run `33589084290`でactual `cmd/tei`をbuildして`deployment-provider-plan`を実行しました。生成したEvidence artifactについて、current SOZA Adapterからactual `tei` binaryを別OS processとして起動し、strict decode、Capability Observation mapping / validation、Provider固有情報の非漏出を確認しています。actual Provider Plan bytesはdigest付きfixtureとしてrepository-local testから継続検査できます。

```text
fixed source / artifact
  + actual TEI process execution
  + current SOZA Adapter mapping
  = E3b-P2 fixed-artifact Scoped Executable Evidence

  != private artifact credential lifecycle proven
  != arbitrary TEI version compatibility
  != E4 Operational portability
```

### E3b-M1a — live KJ Atlas process + deterministic model stub

ISSUE-000064では、public repository `hat47x/kj-atlas`の固定commit `4f28c13abe4176503c6fed863383a2d1db2299e9`を取得し、KJ Atlas FastAPI backendと同repositoryのdeterministic model stubをSOZAとは別processとして実際に起動しました。

`POST /ai/suggest-card-groups`をactual HTTPで呼び、KJ Atlasのrequest model、LLM input IR、SafeMode、local model routing、response filteringを通したうえで、grouping responseをSOZAのCognitive Method Applicationへ戻しています。

KJ Atlas固有responseはopaqueな`not_verified` Method outputとして保持し、grouping候補をRecommendation / Decisionへ自動昇格させません。

### E3b-M1b — live external model-backed KJ execution

ISSUE-000066ではM1aと同じKJ Atlas revisionを使い、KJ AtlasのMethod surfaceを変えずにdeterministic model stubだけを実際に推論するmodel artifactへ置き換えました。

historical Run `33596839607`では、Ollama `0.32.14`と`qwen2.5:0.5b`を使い、KJ Atlasの`POST /generate`境界をintegration-only AdapterからOllamaへ接続しました。actual inferenceでは`prompt_eval_count = 196`、`eval_count = 78`を観測し、そのresultを既存SOZA Method mapping boundaryへ通しています。

```text
actual model inference succeeded
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != Recommendation
  != Decision
```

### historical reconstruction / model artifact exchange

ISSUE-000067では、異なるlogical Realizationと同一Realization内のhistorical revisionを分け、Exact Bindingを用いたportable historical reconstructionの境界を確立しました。

ISSUE-000068ではKJ Atlas source、Method surface、runtime、入力を固定したままactual model artifactを交換し、後続Application追加後も先行ApplicationのRealization、Provenance、outputが変わらないことを確認しました。

### runtime version exchange

ISSUE-000070では交換軸をruntime versionだけへ狭め、model artifactを固定します。

- revision A: Ollama `0.32.13`
- revision B: Ollama `0.32.14`

repository-local harness、固定runtime archive digest、fixed model digest、Exact Binding control、artifact guard、事前配置artifact経路、run専用Evidence directory、local preflightまで整備しています。

```text
runtime exchange harness / preflight implemented
  != actual runtime A/B inference PASS
```

actual `0.32.13` / `0.32.14`交換は**Not Yet Verified**です。

### outcome-quality evaluation boundary

ISSUE-000071では、execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeを分離する評価境界を確立しました。actual M1b履歴からreview-ready bundleを再構成でき、non-golden case catalogとhuman review templateもあります。

ただし、これはKJ法としての成果品質がSatisfiedになったという意味ではありません。actual human reviewと成果品質判定は後続Evidenceです。

### v0.2.0との関係

v0.2.0のsupported release scopeはE3aまでです。release後に積み上がったE3b、historical reconstruction、model artifact exchange等のEvidenceを、既に公開済みのv0.2.0 supported scopeやRelease Evidenceへ遡及的に追加しません。

### Open questions

- private TEI / external artifactを取得するcredential lifecycleとdeployment境界
- TEI executableの正式な取得・配布方式
- fixed revision以外のTEI version交換
- TEI CLI version交換時に必要なProvenance / Exact Bindingの水準
- ISSUE-000070のactual Ollama runtime version交換
- 別model family / Provider / Realizationへ広げたportability
- actual human reviewとKJ法としての成果品質
- network degradation、rate limit、credential失効、artifact acquisition failure等のfailure behavior
- E4 Operational portabilityを何で測るか

## 10. PMS-07 — release可能な製品として成立する

### Outcome

Product Valueを満たす最小supported scopeが明確で、配布物、versioning、failure handling、release acceptanceを含めてrelease候補を再現可能に評価し、actual releaseを検査済みsource commitへ追跡できます。

### Minimum Evidence

Release Evidence。

### Current state

**Satisfied for v0.2.0 Local Reference Product Baseline.**

v0.2.0はactual release済みです。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- historical Release Candidate Gate Run `33574947445`: **9 gate success**
- GitHub Release ID: `380902898`

Local Reference Packageについて、release preparationで算出したSHA-256とactual release asset digestが一致しています。

`37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`

```text
v0.2.0 Release Evidence Satisfied
  != production readiness
  != E3b全体 Satisfied
  != Operational Evidence
  != Adoption / Outcome Evidence
```

GitHub Actionsは現在停止していますが、actual v0.2.0 publication時のRunはhistorical Release Evidenceとして保持します。後続develop commitの再検証はrepository-local checker、test、probeをローカルで個別に実行します。

## 11. PMS-08 — 実運用と利用者成果からProduct Valueを検証できる

### Outcome

実際の利用環境で、SOZAが単に動作しただけでなく、判断の再構成、引継ぎ、再検討、Provider交換、不確実性保持等に役立ったかを検証できます。

### Minimum Evidence

Operational Evidence、および対象価値に応じたAdoption / Outcome Evidence。

### Current state

**Not Yet Verified.**

v0.2.0 Release Evidenceやpost-releaseのScoped Executable EvidenceをPMS-08の成立へ読み替えません。

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

Product Value、Product Shape、Product Interaction、Packaging、Identity / Access / Collaboration、Realization / Provider Exchange、v0.2.0 Release Evidence、REQ-0001〜0022、SCN-0001〜0018、ISSUE-000053〜000071、current runtime / evaluation資産へ戻ってMilestone全体を再監査しました。

historical Actions Runは、当時actualに得たExecutable / Release Evidenceとして保持しています。一方、current Open Questionから`SOZA Actionsからcredentialを供給する`という実行面固有の表現を外し、private artifact acquisition / credential lifecycleという製品側の論点へ戻しました。current継続検査もGitHub Actionsではなくrepository-local testを前提とします。

PMS-06にはE3b-P2、M1a、M1bだけでなく、ISSUE-000067のhistorical reconstruction、ISSUE-000068のactual model artifact交換、ISSUE-000070のruntime version交換基盤、ISSUE-000071の成果品質評価境界まで反映しました。runtime version交換のactual A/Bとhuman outcome reviewは未完了のままです。

PMS-07のv0.2.0 supported scopeはE3aまでに保ち、post-release EvidenceによってRelease Evidenceを遡及的に拡張していません。E4、production security / Storage、PMS-08のOperational / Adoption・Outcome Evidenceも未検証のままです。

意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語としてMilestoneの現在地を読み通せることを最重要視して全文を再ドラフトしました。
