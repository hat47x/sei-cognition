# SOZA Product Milestones

更新日: 2026-09-02  
状態: **Current Deadline-free Product Milestone Baseline — v0.2.0 Release Evidence / E3b-M1a reflected**

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

未定領域をMilestoneだけからRequirementへ昇格させません。意味境界や必要性が十分に確認できていない場合は、議論、資料調査、prototype、fixture、実証実験を先に行い、独立した規範上の必要性が確認できた場合だけRequirementへ反映します。

## 2. Milestoneの読み方

各Milestoneでは、少なくとも次を分けます。

- **Outcome** — 製品として何が成立している必要があるか。
- **Minimum Evidence** — 成立を判断する最低限のEvidence。
- **Current state** — 現在どこまで確認できているか。
- **Open questions** — 現時点では固定しない領域。

Milestoneには依存関係がありますが、すべてを直列に完了させる必要はありません。上位価値を壊さない範囲で、必要な実証は並行して進めます。

## 3. PMS-00 — Product Valueと製品境界が正本化されている

### Outcome

SOZAが何のために存在し、何を価値として守り、何を自らの恒久的中心にしないかを説明できます。

少なくとも次が相互に矛盾せず読める状態を求めます。

- Product Value / Value Proposition
- Value Model / Acceptance / Traceability
- Product Vision / Principles / Product Shape
- SOZA / TEI / external Providerの境界

### Minimum Evidence

Design Evidence。

### Current state

**Established at Design level.**

下位実装やCIの存在だけを理由に、Operational / Adoption Evidenceへ昇格させません。

## 4. PMS-01 — 耐久的なsemantic substrateを機械的に扱える

### Outcome

判断仕事に必要な意味のうち、現在正本化されている範囲を、特定UIやStorageへ閉じ込めずに読み、検証し、再構成できます。

代表例はSemantic Reference、Decision Memory、Capability Observation、Cognitive Method、Semantic Interchange、Representation Profileです。

### Minimum Evidence

対象ContractごとのExecutable Evidence。

### Current state

**Scoped Executable Evidence available.**

current runtimeでは、known Contractのtyped read / validate / reconstruct、Representation Verifier Registry、Payload Source、Cognitive Method、Exact Binding consistency等を限定範囲で検査しています。

```text
Contract conformance PASS
  != product readiness
  != Operational Evidence
```

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

この順序を固定workflowとして要求しません。重要なのは、RecommendationとDecision、過去のbasisと後から得たObservation、CapabilityとProvider等を混同しないことです。

### Minimum Evidence

代表variantを含むfixture-scoped Executable Evidence。

### Current state

**Scoped Executable Evidence available.**

SCN-0018とend-to-end Semantic Product Journey harnessで、normal / uncertain / collaborative / provider replacement / no-execution等を限定範囲で検査しています。

## 6. PMS-03 — 人間とAIが最初のusable interactionから同じcanonical meaningへ触れられる

### Outcome

人間とAIが、異なるSurfaceから同じcanonicalな判断文脈へ触れ、Inquiryの開始・再開、Observation追加、Recommendation / Decision確認、historical review等を行えます。

低影響な利用で最大詳細を強制せず、必要なときだけaudit detailへ降りられることを求めます。

### Minimum Evidence

Interaction boundaryのDesign Evidenceと、最小prototypeまたはconformanceによるExecutable Evidence。

### Current state

**Design baseline established / scoped Executable Evidence available.**

`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028で、Product Interactionをcanonical meaning上の操作境界として正本化しています。

ISSUE-000053のreference probeでは、human-oriented / machine-oriented Surfaceが同じcanonical sourceへ戻ること、RecommendationとDecisionを平坦化しないこと、Unknown / Conflictを失わないこと、Surface-local stateを破棄してもcanonical recordを失わないこと等を確認しました。

### Open questions

- productionで最初にsupportするhuman-facing Surface
- productionで最初にsupportするAI-facing access Surface
- Web / desktop / CLI / API / MCP等のsupported combination
- light / auditを自然に往復する具体UX

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

ISSUE-000054ではprocess終了後の再読、copy / restore、Persistence交換、unknown Contractの`not_verified`保持、invalid state拒否等を確認しました。

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

- 今後正式にsupportするOS / architecture
- production installer / package manager / signing方式
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

`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`とADR-0030で境界を正本化し、ISSUE-000056のreference probeでProduct Accessとsemantic Responsibilityの分離、`denied`と`not_evaluated`の分離、Selective Disclosureでの`withheld`保持等を限定範囲で確認しました。

### Open questions

- 最初にsupportするauthentication方式
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

E3bは、何を実際に確認したかを混同しないため、現在の作業上は次へ分けます。

```text
E3b-P1 public live Provider service
E3b-P2 actual TEI process / service
E3b-M1a live KJ Atlas process + deterministic model stub
E3b-M1b live external model-backed KJ execution
```

P1 / P2 / M1a / M1bはEvidence範囲を明示するための区分であり、新しいProduct ontologyではありません。

### E2 — out-of-process reference exchange

ISSUE-000057では、SOZA runtimeとは別のOS processとしてreference Provider A / Bとreference Method Realization A / Bをbuild・起動し、Provider / Method交換後もhistorical Decisionを変更しないこと、異なるRecommendationをDecisionへ自動昇格しないこと等を確認しました。

### E3a — version固定した実外部artifact integration

ISSUE-000058では、SOZAとは別repositoryで独立にversion管理される実artifactを扱いました。

- Cognitive Method側: `hat47x/cultural-substrate-weaving`のversion固定artifact
- Capability Provider側: `hat47x/tei-platform`のversion固定observed deployment state

source identityを確認し、Provider / repository固有情報をUniversal Contractへ漏らさず、current Cognitive Method / Capability Observation boundaryへ戻すことを検査しています。

### E3b-P1 — public live Provider service

ISSUE-000060では、SOZAとは独立したpublic serviceをネットワーク越しに実際に呼びました。reference ProviderにはGitHub REST APIの固定commit取得面を利用し、期待revisionと一致する場合だけCapability Observationへmappingしています。

revision mismatch、HTTP failure、timeout / cancellation、Provider固有fieldの非漏出も検査済みです。

```text
E3b-P1 PASS
  != E3b全体 PASS
  != actual TEI execution PASS
  != external Method live execution PASS
```

### E3b-P2へ進むための外部実行境界

ISSUE-000061では、actual TEI CLI integrationの前段として次を分離しました。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

`runtime/go/teiintegration`のhelper process testはexternal executable injection boundaryを検査するものであり、actual TEI executableを実行したEvidenceではありません。

### E3b-M1a — live KJ Atlas process + deterministic model stub

ISSUE-000064では、public repository `hat47x/kj-atlas`の固定commitを取得し、KJ Atlas FastAPI backendとKJ Atlas同梱のdeterministic model stubをSOZAとは別processとして実際に起動します。

KJ Atlas自身の`POST /ai/suggest-card-groups`をactual HTTPで呼び、得られたgrouping responseをSOZAの既存Cognitive Method Applicationへ結び付けます。

KJ Atlas固有responseはUniversal Contractへ昇格させず、opaqueな`not_verified` Method outputとして保持します。source repository、commit、entry point、result digestはopaque Provenanceとして残します。

また、grouping候補をRecommendation / Decisionへ自動昇格させません。

```text
KJ Atlas grouping suggestion
  != Recommendation
  != Decision

E3b-M1a PASS
  != external model quality proven
  != E3b-M1b PASS
```

再基線化前PR #41では、KJ Atlas取得、install、migration、model/backend起動、actual grouping、SOZA mapping boundary、actual result mappingまでを専用workflowで実行し、成功しています。最新developへ再基線化した後も、merge前に同じ専用workflowと全体回帰を再確認します。

### Open questions

- actual TEI executableをどの環境から、どのEvidence付きでintegration testへ渡すか
- private repository credentialをacquisition / deployment policyへどう閉じ込めるか
- TEI CLI version交換時に必要なProvenance / Exact Bindingの水準
- E3b-M1bで実外部modelを利用したときにもM1aの意味境界が保てるか
- formal integration protocolを本当に標準化する必要があるか
- E4 Operational portabilityを何で測るか

## 10. PMS-07 — release可能な製品として成立する

### Outcome

Product Valueを満たす最小supported scopeが明確で、配布物、versioning、failure handling、release acceptanceを含めてrelease候補を再現可能に評価し、actual releaseを検査済みsource commitへ追跡できます。

### Minimum Evidence

Release Evidence。

### Current state

**Satisfied for v0.2.0 Local Reference Product Baseline.**

v0.2.0はactual release済みで、`release/v0.2.0/RELEASE_EVIDENCE.md`により次の対応を確認しています。

- tag `v0.2.0`
- source commit `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- Release Candidate Gate Run `33574947445`
- GitHub Release `SOZA v0.2.0 — Local Reference Product Baseline`
- Local Reference Packageとrelease asset digest

このRelease Evidenceが成立するsupported scopeは、Release Acceptance / Release Notesで定めた**E3aまで**です。

E3b-P1やE3b-M1aのScoped Executable Evidenceがrelease後に存在しても、v0.2.0のscopeを遡及的に広げません。

```text
v0.2.0 Release Evidence Satisfied
  != E3b included in v0.2.0 supported scope
  != Operational Evidence
```

### Open questions

- 次releaseでsupport範囲をどこまで広げるか
- installer / signing / platform support matrixをいつrelease条件へ含めるか
- upgrade compatibilityをどこまでrelease acceptanceへ含めるか

## 11. PMS-08 — 実運用と利用成果を評価できる

### Outcome

実際の利用環境でSOZAが継続利用でき、Product Valueが利用者や組織の判断仕事へどのような影響を与えたかを評価できます。

### Minimum Evidence

Operational EvidenceおよびAdoption / Outcome Evidence。

### Current state

**Not Yet Verified.**

v0.2.0 Release Evidence、E3b-P1、E3b-M1a等のExecutable Evidenceだけから、運用安定性、利用定着、意思決定品質、組織成果を推測しません。

### Open questions

- 実利用で最初に測るfailure / recovery / portability指標
- 利用者負担と判断記憶の継続性をどう評価するか
- AI / Method / Provider交換が実際の判断品質へ与える影響
- Adoption / Outcomeを短期engagement指標へ矮小化しない評価方法

## 12. Moving Rebaseline — 将来地平を固定しない

SOZAは、現在の生成AI、UI、workflow engine、database、agent frameworkの制約を恒久前提にしません。

評価時点から概ね10〜50倍程度の能力向上を仮置きし、現在の実装都合だけでUniversal semanticsを固定していないかを継続的に再検査します。

これは数値benchmarkではなく、設計の近視眼化を防ぐための移動する地平です。

```text
current implementation constraint
  != durable product meaning
```

## 13. Evidenceの共通境界

このMilestone全体では、次を混同しません。

```text
Design Evidence
  != Executable Evidence
  != Release Candidate Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidate Evidenceは5段階Evidenceへ新しい普遍段階を追加するものではなく、特定candidateに必要なExecutable Evidence群をまとめて再検査した記録として扱います。

同様に、あるMilestoneで最低限のEvidenceが成立していても、より高いEvidenceや隣接Milestoneが自動的に成立したとはみなしません。

## 14. 自然な日本語レビュー

Product Value / Shape、current Requirements / Architecture / Contract、ISSUE-000045〜000064、v0.2.0 Release Acceptance / Release Evidence、Realization / Provider Exchange、各runtime Evidenceを照合しました。

そのうえで、PMS-06にはE3b-M1aのScoped Executable Evidenceを追加し、PMS-07では既に成立しているv0.2.0 Release Evidenceを維持しました。release後に得られたM1aをv0.2.0のsupported scopeへ遡及させず、E3b-P2、M1b、E4、Operational / Adoption Evidenceを未検証のまま明示しています。

意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
