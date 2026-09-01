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

**Design baseline established / scoped persistence・literal process restart Executable Evidence available / supported distributable artifact pending.**

`product/packaging/SOZA_PRODUCT_PACKAGING.md`とADR-0029で、最初に成立させるPackaging / Deployment ProfileをLocal Single-Node Packageとして正本化しました。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

runtime executableはcanonical semantic dataではなく、filesystem pathもLogical Referenceではありません。portable export / importにはcurrent Semantic Interchangeを再利用し、package専用Universal Contractは追加していません。

ISSUE-000054では、`runtime/go/packagingprobe`とbuild可能な`soza-package-probe` executableを用いて、次を限定範囲で確認しました。

- portable Semantic Interchangeをfilesystemへ保存できる。
- in-memory runtime stateを破棄した後にも同じbytesとtyped recordを再構成できる。
- 実際にGo executableをbuildできる。
- 独立したsave processを終了した後、別のinspect processがdurable dataだけからbundleを再読できる。
- unknown Contractをprocess越しでも`not_verified`のまま保持できる。
- canonical bundle fileを別directoryへcopyし、restore先から再読できる。
- filesystemからmemory Persistenceへportable bytesを移し、同じbundleを再読できる。
- invalid / incomplete stateを正常packageとして扱わない。
- physical data-root変更やPersistence交換をsemantic identity / Semantic Revisionへ持ち込まない。

literal process probeを含むSemantic Runtime Conformance Run `33508376230`とPlan integrity Run `33508376256`はともにsuccessしました。

```text
same-version process restart PASS
  != supported distributable artifact proven
  != executable version upgrade proven
  != crash durability proven
  != actual production Storage migration proven
  != Release / Operational / Adoption Evidence
```

PMS-04の残差は、test内でbuildできることとsupportedな配布artifactとして成立することの差です。ISSUE-000055で、package lifecycle controlとProduct Interactionを分けたまま、reproducible build、artifact identity、version表示、配布artifactからのsave / reloadを検証します。

### Open questions

- first supported artifactのOS / architecture scope
- archive形式とartifact integrity metadata
- package lifecycle用管理入口の最小範囲
- executable version upgrade後のresume
- productionで最初にsupportedとするhuman / AI Product Interaction Surface
- server-side StorageをいつRDB / object storeへ進めるか
- team / multi-user deployment topology
- online migration、production backup SLA、HA / replication
- container / cloud-managed distribution

これらはprocess probeのPASSだけを理由にRequirementへ固定しません。

## 8. PMS-05 — identity・authorization・collaborationを製品として安全に扱える

### Outcome

semanticなResponsibility / Authorityと、製品access controlを混同せずに、single-userからteam / external collaborationへ進めます。

```text
actor identity
  != Responsibility
  != Authority
  != product access permission
```

Selective Disclosureを扱う場合も、withheldとunknown等の意味差を失いません。

### Minimum Evidence

security / collaboration boundaryのDesign Evidenceと、対象範囲のExecutable Evidence。

### Current state

**Not Yet Verified.**

ISSUE-000047で検討します。

## 9. PMS-06 — 実際のMethod / Providerを交換しても判断記憶が保たれる

### Outcome

synthetic fixtureだけでなく、実際のCognitive Method Realization、AI、外部SaaS、TEI、custom code等を接続し、実現手段を交換してもIntent、Decision、Responsibility、Provenance等が壊れないことを確認します。

### Minimum Evidence

複数の実Realization / Providerを用いたExecutable Evidence。必要に応じて限定されたOperational Evidenceも収集します。

### Current state

**Partial.**

Provider-neutralな境界やsynthetic Adapter、Cognitive Method portable ContractにはExecutable Evidenceがありますが、production Realization交換や実Provider横断はまだ一般化して主張しません。

## 10. PMS-07 — release可能な製品として成立する

### Outcome

Product Valueを満たす最小supported scopeが明確で、配布物、versioning、migration、security、failure handling、release acceptanceを含めてrelease候補を再現可能に評価できます。

### Minimum Evidence

Release Evidence。

### Current state

**Not Yet Verified for the current Product Shape as a whole.**

過去のrelease candidate gateや個別CI Evidenceを、このMilestoneへ自動昇格させません。

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

Product Value、Value Proposition、Product Shape、Product Interaction、Product Packaging、REQ-0001〜0022、SCN-0008 / 0010 / 0013 / 0018、ADR-0028 / 0029、ISSUE-000046 / 000053 / 000054 / 000055、current Go runtime、Semantic Interchange、Interaction / Packaging probeとcurrent CI Evidenceへ戻ってMilestoneを再監査しました。PMS-03はscoped Interaction Executable Evidenceまで、PMS-04はPackaging / Deployment Design、filesystem persistence、runtime-state-independent reconstruction、same-versionのliteral process restartまでを明確にEvidence化しています。一方、supported distributable artifact、version upgrade、actual production Storage migration、Release / Operational Evidenceは未検証のままです。Local Single-Node Package、filesystem、probe executableを唯一のdeployment topology、正式Product Interaction、semantic authorityへ昇格させず、未定領域を先にRequirementへ固定しない境界を維持したうえで、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。