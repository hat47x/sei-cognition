# SOZA Product Milestones

更新日: 2026-09-01  
状態: **Current Deadline-free Product Milestone Baseline**

## 1. この文書の役割

この文書は、SOZAをどの順序で製品として成立させていくかを、日付や期限ではなく**成立条件とEvidenceの高さ**で示します。

Milestoneは開発管理上の目印であり、SOZAのUniversal ontologyや利用者の業務workflowではありません。また、特定versionへ固定されたrelease scheduleでもありません。

```text
Product Value
  → Product Milestone
  → Requirement / Acceptance Scenario
  → Issue / ADR
  → Architecture / Contract
  → Implementation / Evidence
```

未定の領域をMilestone文書だけでRequirementへ昇格させません。具体的な意味境界がまだ分からない場合は、チャット上の議論、資料検討、prototype、fixture、実証実験等を先に行い、その結果から独立した規範上の必要性が確認できた場合だけRequirementへ反映します。

## 2. Milestoneの読み方

各Milestoneは、少なくとも次を分けて扱います。

- **Outcome** — 製品として何が成立している必要があるか。
- **Minimum Evidence** — そのMilestoneを成立とみなす最低限のEvidence。
- **Current state** — 現在確認できている高さ。
- **Open questions** — まだ先に決めない領域。

Milestone間には依存関係がありますが、すべてを直列に完了させる必要はありません。上位価値を壊さない範囲で、実証に必要な作業は並行できます。

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

下位実装やCIの存在をもって、このMilestoneより上のOperational / Adoption Evidenceを主張しません。

## 4. PMS-01 — 耐久的なsemantic substrateを機械的に扱える

### Outcome

判断仕事に必要な意味のうち、現在正本化されている範囲を、特定UIやStorageへ閉じ込めずに読み、検証し、再構成できます。

代表例はSemantic Reference、Decision Memory、Capability Observation、Cognitive Method、Semantic Interchange、Representation Profileです。

### Minimum Evidence

対象ContractごとのExecutable Evidence。

### Current state

**Scoped Executable Evidence available.**

ただし、Contract単体のPASSは製品全体の利用可能性を意味しません。

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

ISSUE-000053では、`runtime/go/interactionprobe`にhuman-oriented Surfaceとmachine-oriented Surfaceを実体化し、同じin-memory canonical sourceへ接続しました。既存`semanticruntime`型を再利用し、Recommendation / Decision / Capability Observation / Cognitive Method Applicationはcurrent validatorを通して保持します。Inquiry / Unknown / Conflictは、未対応意味を理解済みと偽らずopaqueな`not_verified` recordとして扱います。

Semantic Runtime Conformance Run `33504002579`で、current Contract fixture再検査と`runtime/go`全体の`go test ./...`がsuccessしました。

確認できた主な境界は次です。

- machine側が追加したObservation / Recommendationをhuman側から再読できる。
- human側Decisionをmachine側がDecisionとして再読できる。
- RecommendationとDecisionを同一recordへ平坦化しない。
- Unknown / Conflictを失わない。
- Projection生成でcanonical sourceを変更しない。
- Surface-local stateを破棄してもcanonical recordを失わない。
- chat / UIだけの情報をcanonical Recommendation / Decisionへ昇格させない。
- post-decision Observationでhistorical Decision basisを書き換えない。
- machine SurfaceであることからResponsibilityを推定しない。

```text
reference probe PASS
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

`product/packaging/SOZA_PRODUCT_PACKAGING.md`とADR-0029で、最初に成立させるPackaging / Deployment ProfileをLocal Single-Node Packageとして正本化しました。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

runtime executableをcanonical semantic dataにはせず、filesystem pathもLogical Referenceにはしません。portable export / importにはcurrent Semantic Interchangeを再利用し、package専用Universal Contractは追加していません。

ISSUE-000054では、filesystem Persistenceとbuild可能なGo executableを用いて、次を限定範囲で確認しました。

- portable Semantic Interchangeをfilesystemへ保存できる。
- in-memory runtime stateを破棄した後にも同じbytesとtyped recordを再構成できる。
- 独立したsave processを終了した後、別processがdurable dataだけからbundleを再読できる。
- unknown Contractをprocess越しでも`not_verified`のまま保持できる。
- canonical bundle fileを別directoryへcopyし、restore先から再読できる。
- filesystemからmemory Persistenceへportable bytesを移し、同じbundleを再読できる。
- invalid / incomplete stateを正常packageとして扱わない。
- physical data-root変更やPersistence交換をsemantic identity / Semantic Revisionへ持ち込まない。

literal process probeを含むSemantic Runtime Conformance Run `33508376230`とPlan integrity Run `33508376256`はsuccessしました。

ISSUE-000055では、Linux / amd64向けの**Local Reference Package**をdistribution artifactとして生成しました。

Local Package Artifact Run `33509521544`では、次を一続きに検査しています。

- 同一inputからreference binaryを2回buildし、byte-for-byte一致を確認する。
- artifact version、source commit、targetをbuild identityとしてbinaryとmetadataへ持たせる。
- file順、mtime、owner / groupを固定したarchiveを作り、SHA-256 checksumを生成する。
- archiveを別directoryへ展開する。
- 展開したartifact自身でSemantic Interchangeを保存してprocessを終了する。
- 別processで同じdurable data rootから再読し、expected bundleを再構成する。
- tar.gzとchecksumをGitHub Actions artifactとして保存する。

Run `33509521544`で保存されたworkflow artifactは、artifact ID `9801021136`、workflow artifact digest `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`です。

同一headではPlan integrity Run `33509521580`とSemantic Runtime Conformance Run `33509521596`もsuccessしました。

このEvidenceにより、PMS-04が求めるPackaging / Deployment Designと「配布・保存・再開」の最小Executable Evidenceはreference profileの範囲で揃いました。

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

semanticなResponsibility / Authorityと、製品access controlを混同せずに、single-userからteam / external collaborationへ進めます。

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

`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`とADR-0030で、Product Identity / Access / Collaboration boundaryを正本化しました。

Product Access Scopeはtenant / workspace等に対応し得ますが、Product-localなsecurity / collaboration concernとして扱い、Universal semantic entityへ自動昇格させません。

ISSUE-000056では`runtime/go/accessprobe`を実体化し、既存`interactionprobe.CanonicalStore`と`semanticruntime`を再利用して次を限定範囲で確認しました。

- 旧・新IdP相当のauthentication identityを同じBounded Subjectへbindingできる。
- identity交換後もhistorical DecisionのResponsibility Refを書き換えない。
- semantic Responsibilityが存在してもProduct permissionがなければreadを拒否する。
- Product `administer` permissionを与えてもsemantic Responsibilityを生成しない。
- human / AI / serviceというactor kindだけからpermissionを推定しない。
- identityを解決できない`not_evaluated`と、Policy上の`denied`を区別する。
- external collaborator向けSelective Disclosureで非開示recordを`withheld`として扱い、fake Unknownを作らない。
- Disclosure Projection生成前後でcanonical sourceを変更しない。
- Product Scopeのread permissionがなければProjection自体を返さない。

初期probe headのSemantic Runtime Conformance Run `33511885433`はsuccessしました。

このEvidenceは責務分離を支持しますが、production OIDC / IAM、formal RBAC / ABAC、credential / session lifecycle、production Selective Disclosure securityを実証するものではありません。

### Candidate Requirement

Product accessをsemantic Responsibility / Authorityやactor kindから自動導出しない必要性は、Designとscoped probeの双方で確認できました。

一方、reference probeで使った`read / append / review / share / administer` vocabulary、Product Access Scopeの粒度、Identity Binding lifecycleはまだRealization依存です。

そのため、新しいStable Requirement / Scenario IDは現時点で追加せず、次をCandidate Requirementとして保持します。

> SOZAの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出せず、認証identityとの対応を含むProduct Access Policyで独立に評価できる必要がある。

production IdP、実team deployment、external collaborationの実証から、既存REQ-0012 / 0013 / 0017ではこのProduct failureを十分に表現できないことが確認された場合にStable Requirement化を再検討します。

### Open questions

- 最初にsupportedとするauthentication方式
- Product Access Scopeの正式名称・granularity・lifecycle
- Product permission vocabularyとPolicy model
- hosted / team deploymentのmembership・invitation lifecycle
- production Selective Disclosureのsecurity boundary
- security audit eventのretention / tamper resistance
- enterprise IdP / directory integration
- encryption / key management

これらをreference probeのPASSだけでStable Requirementへ固定しません。

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

### Minimum Evidence

複数の実Realization / Providerを用いたExecutable Evidence。必要に応じて限定されたOperational Evidenceも収集します。

### Current state

**Partial / out-of-process reference exchange scoped Executable Evidence available / real external AI・SaaS・TEI pending.**

`product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`で、交換してよいRealization / Providerと、交換後も判断記憶として守る意味を正本化しました。

PMS-06のEvidenceは、少なくとも次の段階に分けて扱います。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3 real external integration
  → E4 operational portability
```

current repositoryではE1に加え、ISSUE-000057でE2まで限定的に実証しました。

`runtime/go/realizationprobe`では、reference Provider A / Bとreference Method Realization A / BをSOZA runtimeとは別のOS processとしてbuild・起動します。Provider固有stateは既存Provider Adapterを通してcurrent Capability Observationへ戻し、Method Applicationは既存Cognitive Method Contractの`realization_ref`を保持します。

Semantic Runtime Conformance Run `33516101445`では、current Contract fixture 31件の再検査と`runtime/go`全体の`go test ./...`が**success**しました。

確認した主な境界は次です。

- Provider A / Bを別OS processとして起動し、異なるProvider固有state shapeを取得できる。
- A / Bを別Provider identityとして保持しつつ、同じCapabilityへmappingできる。
- mapping後のCapability Observationをcurrent validatorへ戻せる。
- 同じMethod Definitionに対し、二つのMethod Realizationを別OS processで実行できる。
- 各Method Applicationが異なる`realization_ref`を保持できる。
- Realizationごとに異なるRecommendationを生成しても、RecommendationをDecisionへ自動昇格しない。
- Provider / Methodを交換した後も、交換前Decisionのbasis、Recommendation、Responsibility、unresolvedを変更しない。
- failed Provider / Method processがcanonical sourceを変更しない。

交換の成功を「異なるRealizationが同じ文字列を返すこと」とは定義しません。重要なのは、どのRealization / Providerを用い、どのObservation / Recommendationが生じたかを区別したまま、historical Decisionを当時のbasisで読み直せることです。

```text
out-of-process reference exchange PASS
  != real external AI / SaaS / TEI integration proven
  != production network / credential / version portability proven
  != Operational portability
  != Release / Adoption Evidence
```

### Open questions

- E3で最初に接続する実Cognitive Method Realization
- TEIと非TEI Providerをどの組み合わせで比較するか
- 実外部Providerのcredential / rate limit / network failureをどう評価するか
- production Realization protocolを標準化する必要が本当にあるか
- process-local protocolとportable Contractの境界
- Realization version交換時のExact Binding / Provenanceの必要水準
- E4のOperational portabilityを何で測るか

これらをE2のPASSだけでStable Requirementや正式protocolへ固定しません。

## 10. PMS-07 — release可能な製品として成立する

### Outcome

Product Valueを満たす最小supported scopeが明確で、配布物、versioning、migration、security、failure handling、release acceptanceを含めてrelease候補を再現可能に評価できます。

### Minimum Evidence

Release Evidence。

### Current state

**Not Yet Verified for the current Product Shape as a whole.**

PMS-04のLocal Reference PackageはPackagingのMinimum Executable Evidenceであり、PMS-07のProduct Releaseではありません。reference archive、workflow artifact、個別CI PASSをRelease Evidenceへ自動昇格させません。

## 11. PMS-08 — 実運用と利用者成果からProduct Valueを検証できる

### Outcome

実際の利用環境で、SOZAが単に動作しただけでなく、判断の再構成、引継ぎ、再検討、Provider交換、不確実性保持等に役立ったかを検証できます。

### Minimum Evidence

Operational Evidence、および対象価値に応じたAdoption / Outcome Evidence。

### Current state

**Not Yet Verified.**

## 12. 横断Milestone — Moving Rebaseline

PMS-00〜08とは別に、主要な技術変化・利用知見・反証Evidenceが得られた場合は、評価時点の現在から10〜50倍程度先を見渡すMoving Future Horizonで上位文書を再監査します。

これは「最後に行う工程」ではありません。どのMilestoneでも、下位Evidenceが上位仮説を反証した時点でProduct Value / Vision / Principlesへ戻ります。

## 13. 未定領域の扱い

未定領域には、次の三状態を明確に認めます。

- **Open Question** — まだ何を要求すべきか自体が分からない。
- **Candidate Requirement** — 議論や実証から必要性が見えたが、重複・耐久性・適用範囲を未監査。
- **Stable Requirement** — Product Valueから独立した規範上の必要性を説明でき、既存REQとの重複を監査し、Acceptanceを定義できる。

Open Questionを直接Stable Requirementへ飛ばしません。

## 14. Natural Japanese review

Product Value、Value Proposition、Product Shape、Product Interaction、Product Packaging、Product Identity / Access / Collaboration、Realization / Provider Exchange、REQ-0001〜0022、SCN-0005 / 0007 / 0008 / 0010 / 0012 / 0013 / 0014 / 0018、ADR-0024 / 0025 / 0028 / 0029 / 0030、ISSUE-000046 / 000047 / 000053〜000057、current Go runtime、Interaction / Packaging / Product Access / Realization exchange probeとcurrent CI Evidenceへ戻ってMilestoneを再監査しました。PMS-03はscoped Interaction Executable Evidence、PMS-04はLocal Reference PackageによるMinimum scoped Executable Evidence、PMS-05はProduct Access責務分離のDesignとscoped Executable Evidence、PMS-06はout-of-process reference exchangeのE2 scoped Executable Evidenceまでを明確にしています。一方、production IdP、formal access policy、実AI / SaaS / TEI integration、Operational portability、Product Release、Adoption / Outcome Evidenceは未検証のままです。probe固有のpermission vocabulary、process-local JSON、binary構成、Provider ID等をUniversal Core、Stable Requirement、正式protocolへ先に固定しない境界も維持しました。そのうえで、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。