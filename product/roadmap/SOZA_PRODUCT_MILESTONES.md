# SOZA Product Milestones

更新日: 2026-09-02  
状態: **Current Deadline-free Product Milestone Baseline — v0.2.0 Release Evidence reflected**

## 1. この文書の役割

この文書は、SOZAをどの順序で製品として成立させていくかを、日付や期限ではなく**成立条件とEvidenceの高さ**で示します。

Milestoneは開発管理上の目印です。SOZAのUniversal ontologyでも、利用者の業務workflowでも、特定versionへ固定されたrelease scheduleでもありません。

```text
Product Value
  → Product Milestone
  → Open Question / Experiment
  → Requirement / Acceptance Scenario
  → Issue / ADR
  → Architecture / Contract
  → Implementation / Evidence
```

未定領域をMilestone文書だけからRequirementへ昇格させません。意味境界や必要性がまだ明らかでない場合は、議論、資料検討、prototype、fixture、実証実験等を先に行い、独立した規範上の必要性が確認できた場合だけRequirementへ反映します。

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

ISSUE-000053のreference probeでは、少なくとも次を確認しました。

- human-oriented Surfaceとmachine-oriented Surfaceが同じcanonical sourceを扱う。
- machine側が追加したObservation / Recommendationをhuman側から再読できる。
- human側Decisionをmachine側がDecisionとして再読できる。
- RecommendationとDecisionを同一recordへ平坦化しない。
- Unknown / Conflictを失わない。
- Projection生成でcanonical sourceを変更しない。
- Surface-local stateを破棄してもcanonical recordを失わない。
- post-decision Observationでhistorical Decision basisを書き換えない。
- machine SurfaceであることからResponsibilityを推定しない。

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

`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`とADR-0030で境界を正本化し、ISSUE-000056のreference probeでは次を限定範囲で確認しました。

- identity交換後もhistorical DecisionのResponsibility Refを書き換えない。
- semantic Responsibilityが存在してもProduct permissionがなければreadを拒否する。
- Product `administer` permissionを与えてもsemantic Responsibilityを生成しない。
- actor kindだけからpermissionを推定しない。
- `not_evaluated`と`denied`を区別する。
- Selective Disclosureで非開示recordを`withheld`として扱う。
- Disclosure Projection生成前後でcanonical sourceを変更しない。

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

**Partial / E2 + E3a + E3b-P1 + E3b-M1a Scoped Executable Evidence available / E3b-P2・E3b-M1b pending.**

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
  │    └─ preparation: external TEI executable injection boundary
  └─ M1 live external Cognitive Method
       ├─ M1a live KJ Atlas process + deterministic model stub
       └─ M1b live external model-backed KJ execution
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

merge後`develop/v0.2.0`でもE3b-P1のScoped Executable Evidenceを再現しています。

### E3b-P2へ進むための準備境界

ISSUE-000061では、actual TEI CLI integrationの前段として次を分離しています。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

`runtime/go/teiintegration`のhelper process testはexternal executable injection boundaryを検査するものであり、actual TEI executableを実行したEvidenceではありません。

### E3b-M1a — live KJ Atlas process + deterministic model stub

ISSUE-000065では、public repository `hat47x/kj-atlas`の固定commit `4f28c13abe4176503c6fed863383a2d1db2299e9`を取得し、KJ Atlas FastAPI backendと同repositoryのdeterministic model stubをSOZAとは別processとして実際に起動しました。

`POST /ai/suggest-card-groups`をactual HTTPで呼び、KJ Atlasのrequest model、LLM input IR、SafeMode、local model routing、response filteringを通したうえで、grouping responseをSOZAのCognitive Method Applicationへ戻しています。

KJ Atlas固有responseはopaqueな`not_verified` Method outputとして保持し、grouping候補をRecommendation / Decisionへ自動昇格させません。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision
```

current PR #41の検査点`5cd3fff304c6bd99e0ab29dc2df4765d4f0e59be`では、External Method Integration E3b Run `33586658465`、Semantic Runtime `33586658788`、Plan integrity `33586658513`、E3a `33586658524`、Provider側E3b `33586658542`、Local Package `33586658477`、Release Candidate Gate `33586658457`がすべてsuccessしました。

Release Candidate Gateは9/9 successで、既存v0.2.0のrelease preparation / publicationは意図どおりskippedされています。

### v0.2.0との関係

v0.2.0のsupported release scopeはE3aまでです。E3b-P1、TEI executable注入境界、E3b-M1aはrelease後に積み上がったScoped Executable Evidenceであり、既に公開済みのv0.2.0 supported scopeやRelease Evidenceを遡及的に広げません。

```text
post-release E3b Evidence exists
  != v0.2.0 supported scope expanded
  != v0.2.0 Release Evidence expanded
```

### Open questions

- actual TEI executableをどの環境から、どのEvidence付きでintegration testへ渡すか
- private repository credentialをacquisition / deployment policyへどう閉じ込めるか
- TEI CLI version交換時に必要なProvenance / Exact Bindingの水準
- E3b-M1bで利用する実外部modelと、その品質評価をsemantic execution Evidenceからどう分離するか
- model / Method / Provider version交換をまたぐhistorical reconstructionをどう検査するか
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
- Release Candidate Gate Run `33574947445`: **9 gate success**
- release preparation: **success**
- publication: **success**
- GitHub Release ID: `380902898`

Local Reference Packageについて、release preparationで算出したSHA-256とactual release asset digestが一致しています。

`37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`

expected 4 assetも実在を確認しています。

```text
v0.2.0 Release Evidence Satisfied
  != production readiness
  != E3b全体 Satisfied
  != Operational Evidence
  != Adoption / Outcome Evidence
```

v0.2.0でsupportを主張するRealization / Provider exchangeの範囲はE3aまでです。release後に得られたE3b-P1、TEI executable注入境界、E3b-M1aのEvidenceを、v0.2.0のsupported scopeへ自動的に追加しません。

詳細は`release/v0.2.0/RELEASE_EVIDENCE.md`を正とします。

## 11. PMS-08 — 実運用と利用者成果からProduct Valueを検証できる

### Outcome

実際の利用環境で、SOZAが単に動作しただけでなく、判断の再構成、引継ぎ、再検討、Provider交換、不確実性保持等に役立ったかを検証できます。

### Minimum Evidence

Operational Evidence、および対象価値に応じたAdoption / Outcome Evidence。

### Current state

**Not Yet Verified.**

v0.2.0 Release EvidenceやE3b-M1aのScoped Executable EvidenceをPMS-08の成立へ読み替えません。

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

Product Value、Value Proposition、Product Shape、Product Interaction、Product Packaging、Product Identity / Access / Collaboration、Realization / Provider Exchange、v0.2.0 Release Acceptance / Release Evidence、REQ-0001〜0022、SCN-0001〜0018、ADR-0024 / 0025 / 0028 / 0029 / 0030、ISSUE-000046 / 000047 / 000053〜000063 / 000065、current Go runtime、Interaction / Packaging / Product Access / E2 / E3a / E3b-P1 / TEI executable injection boundary / E3b-M1a、actual `v0.2.0` tag / GitHub Release / release assetへ戻ってMilestone全体を再監査しました。

PMS-06にはKJ Atlasを用いたE3b-M1aのScoped Executable Evidenceを追加しましたが、deterministic model stubの生成品質を実外部AI model品質へ昇格させていません。また、PMS-07のv0.2.0 supported scopeはE3aまでに保ち、post-releaseのE3b-P1、TEI executable注入境界、M1aによってRelease Evidenceを遡及的に拡張していません。actual TEI execution、E3b-M1b、E4 Operational portability、production security / Storage、PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。

意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
