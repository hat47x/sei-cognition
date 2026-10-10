# SEI Interaction Working-Set Architecture

更新日: 2026-09-18  
状態: **Reference Architecture Design Baseline — ISSUE-000073 / REQ-0023 formalization reflected / Executable Evidence Pending**

## 1. 目的

この文書は、resume-firstな最初のProduct Sliceを実装・検証するとき、**canonical semantic authorityと、利用者向けworking set、Projection、AI draft、external Provider stateを混同しないためのArchitecture boundary**を定めます。

`SEI_REFERENCE_ARCHITECTURE.md`がSEI全体の意味境界を扱うのに対し、本書はPMS-03 / ADR-0028を具体化するInteraction Application層のReference Architectureです。

ここでいう`working set`、`Resume Brief`、`semantic change plan`、`snapshot token`等はProduct / Application / Persistence上の設計語彙であり、Universal Semantic Contractの新しいrecord typeではありません。

```text
Architecture design term
  != Universal semantic entity
```

## 2. 支配原則

### 2.1 Canonical meaningだけが耐久的authorityである

UI layout、browser state、chat history、recent list、AI context、projection cache等は失われ得ます。

それらを失ってもDecision、basis、Unknown / Conflict、Residual、Provenance、Lineage等の耐久的意味を再構成できなければなりません。

### 2.2 ResumeはProjectionであり、新しい正本ではない

Resume Briefは利用者のorientationを助けるために重要ですが、独立したcanonical summaryを第二の正本として持ちません。

```text
canonical state
  -> Resume Projection

Resume Projection
  != canonical state
```

必要に応じてcacheできますが、cache loss後に再生成可能であることを優先します。

### 2.3 AI outputはcommit前にcanonicalではない

external / local AIのresponseを直接canonical storeへ書き込みません。

AI responseはInteraction Application層でprovisional inputとして扱い、意味種別、対象Reference、basis、unresolved等の変更計画へ変換した後、validation / policy / concurrency boundaryを通します。

### 2.4 Concurrency controlとSemantic Revisionを分ける

stale writeを防ぐruntime revision、ETag、generation、snapshot token等は、同時編集・古いProjection検知のmechanicsです。

```text
concurrency version
  != Semantic Revision
  != Logical Reference
```

Semantic Revisionは意味上のrevises / supersedes等を表し、runtime generationから自動推定しません。

### 2.5 AI availabilityをDurable Coreの成立条件にしない

AI adapterが停止してもcanonical read / write、Decision review、resumeを継続できる構成を標準とします。

## 3. State authorityの4層

Interaction実装ではstateを少なくとも次の4層として読み分けます。

### A. Canonical Semantic State

耐久的authorityです。

例は次のとおりです。

- Inquiry / Intent context
- Observation / Evidence
- Unknown / Conflict
- Cognitive Method Application
- Recommendation
- Decision
- Responsibilityに関わるcanonical reference
- Residual / reopen information
- Provenance / Exact Binding / Semantic Lineage

この層だけが、UIやAI sessionを越えて「判断の意味として保存された」と主張できる対象です。

### B. Derived Product State

canonical stateから導出できるProduct-local stateです。

例は次のとおりです。

- working-set membershipの導出結果
- Resume Brief
- current Decision badge
- unresolved count / summary
- `what changed since Decision` projection
- navigation index
- search index

保存してよいものもありますが、正しさのauthorityはcanonicalへ戻ります。

### C. Transient Interaction State

利用中にだけ必要な一時状態です。

例は次のとおりです。

- form draft
- uncommitted AI suggestion
- semantic change preview
- current tab / selection
- chat turn
- local undo buffer

この層を失ってもhistorical Decision reconstructionが壊れてはなりません。

### D. External Realization State

SEI外の実現状態です。

例は次のとおりです。

- AI provider conversation/session
- model runtime state
- TEI / SaaS / external Provider state
- remote request ID

必要な部分をObservation / Provenance / ReferenceとしてSEIへ戻せますが、external stateそのものをcanonical authorityにはしません。

```text
A Canonical
↑ authority
B Derived
C Transient
D External

B / C / D loss
  must not silently rewrite A
```

## 4. Logical component

最初のsliceはsingle processでも実装できますが、責務を次の論理componentとして分けます。

```text
Human Surface Adapter
Machine / AI Surface Adapter
        │
        ▼
Interaction Application Layer
  ├─ Working Set Resolver
  ├─ Projection Builder
  ├─ Semantic Change Planner
  ├─ Commit Coordinator
  └─ Context Egress Planner
        │
        ▼
Canonical Semantic Runtime
        │
   ┌────┴─────┐
   ▼          ▼
Persistence   Integration / Method Adapters
```

一つのGo processへ同居しても構いません。

```text
logical component
  != microservice requirement
```

### 4.1 Human Surface Adapter

人間の自然な操作をInteraction intentへ変換します。

semantic schemaのfield入力をそのままUIへ露出することを必須にしません。

### 4.2 Machine / AI Surface Adapter

AIやmachine clientがstructured Projectionを読み、許されたInteraction intentを提出する境界です。

AIであることからwrite / Decision Authorityを推定しません。

### 4.3 Working Set Resolver

canonical Referenceや関係から、Product上「いま一緒に見る意味」を解決します。

resolverはCase / Workspaceという新しいUniversal recordを作らなくても構成できることをfirst sliceで検証します。

将来、複数domainでworking set自体の耐久的意味が実証された場合だけ上流へ戻ります。

### 4.4 Projection Builder

light view、Resume Brief、audit / structured viewをcanonical stateから生成します。

Projection Builderは意味の要約・選択を行えますが、Unknownをfalseへ、RecommendationをDecisionへ等のsemantic coercionをしてはなりません。

### 4.5 Semantic Change Planner

human intentやAI suggestionを、canonicalへcommit可能な変更候補へ変換します。

例は次のとおりです。

```text
"調査結果ではA案がよさそう"
  ↓
proposed Observation O7
proposed Recommendation R3
unresolved Conflict C2 remains
```

plannerの結果はまだcanonicalではありません。

### 4.6 Commit Coordinator

validation、Product Access / policy、stale snapshot、Persistence commitを調整します。

一つのInteraction operationが複数recordへ影響するとき、意味上半端なsuccessful stateを露出させない責務を持ちます。

実装方式はfirst prototypeで決めます。

### 4.7 Context Egress Planner

external AI / Providerへ送るcontextを選択します。

canonical store全体を暗黙に送るのではなく、taskとpolicyに基づくselected contextを組み立て、監査可能な境界を提供します。

## 5. Resume read path

再開時の標準read pathを次とします。

```text
canonical semantic state
  ↓
Working Set Resolver
  ↓
Projection Builder
  ├─ current question / goal
  ├─ current Decision
  ├─ key historical basis
  ├─ unresolved / residual
  ├─ what changed after Decision
  └─ reopen / review candidates
  ↓
Resume Brief
  ↓
Human / AI Surface
```

### 5.1 Decision時点とcurrent時点を分ける

Resume Projection内部では、少なくとも次の時間的区別を壊しません。

```text
state used by D1
  != state observed after D1
  != current projection
```

latest-wins viewを作る場合でも、historical basisを最新値で上書きしたものを「D1の根拠」と表示しません。

### 5.2 Change setはderivedでよい

`what changed since D1`は、canonical timestamps / lineage / references等から導出するProduct Projectionとして扱えます。

新しいUniversal `ChangeSummary` recordは現時点では不要です。

## 6. Write / commit path

humanまたはAIのwrite intentは次の段階を通します。

```text
Interaction Intent
  ↓
Provisional Draft
  ↓
Semantic Change Plan
  ↓
Schema / semantic validation
  ↓
Product access / policy check
  ↓
Snapshot precondition check
  ↓
Meaning-preserving commit
  ↓
New canonical state
  ↓
Projection invalidation / rebuild
```

### 6.1 Interaction Intent

「観察を追加する」「提案を記録する」「Decisionを作る」等のProduct operationです。

UI event名やHTTP endpoint名をArchitectureへ固定しません。

### 6.2 Provisional Draft

human formやAI responseなど、まだcanonicalへ反映していない状態です。

browser crash等で失われても、それをhistorical Decision lossとは扱いません。

将来draft persistenceが必要になっても、そのstorageをcanonical semantic authorityと同一視しません。

### 6.3 Semantic Change Plan

commitによる意味変更をSurfaceから確認できる中間表現です。

first prototypeではApplication-local typed structureとして構いません。portable cross-implementation agreementが必要であるEvidenceが得られるまでContract化しません。

### 6.4 Validation

既存Semantic Contract / runtime validationに加え、Interaction operation固有のpreconditionを確認できます。

ただしUI convenienceを理由にContractで許可されるUnknown等を拒否しないようにします。

### 6.5 Snapshot precondition

readしたsnapshotからcommitまでにcanonical stateが変わっていないか確認します。

古い場合は、少なくとも次のどれかとして明示します。

- reject
- explicit conflict
- rebase / re-plan request

黙ったlast-write-winsをfirst sliceの標準にはしません。

### 6.6 Commit

Persistence側の仕組みを使い、成功時に一貫したcanonical stateを公開します。

「atomic」がどの範囲を意味するかはprototypeで検証します。filesystem first realizationでatomic replace可能な範囲と、将来RDB等でtransactionを使う範囲をUniversal Contractへ固定しません。

## 7. Working setの構成

working setはProduct-localな`view of related meaning`です。

初期候補として、次のsignalから構成できます。

- root Inquiry / Intentへのreference
- Decision basis / unresolved refs
- Recommendation relation
- Semantic Lineage
- post-decision Observation
- explicit residual / reopen refs
-利用者のpin / navigation preference

最後のpin等はProjection-localであり、意味関係とは分けます。

### 7.1 Derived relationとexplicit semantic relationを区別する

UIが「関連していそう」と推測しただけの項目を、canonical basis relationとして保存したことにはしません。

AIがworking set候補を提案する場合もprovisionalです。

## 8. Resume Projectionの品質境界

Projection Builderは要約を行うため、canonical dataをそのまま並べるだけではありません。このため、要約誤りを防ぐ境界が必要です。

### 8.1 Fact-preserving references

重要な要約には元Artifactへ戻れるReferenceを持たせます。

### 8.2 Semantic labelを失わない

Observation / Recommendation / Decision / Unknown / Conflict等の種別を視覚上まとめても、利用者が必要なとき確認できることを求めます。

### 8.3 AI-generated summaryは再生成可能なProjection

AIをResume Brief生成へ使う場合、AI summary text自体をcanonical Decision rationaleへ自動保存しません。

必要ならdeterministic / structured Projectionを土台とし、その上にAI summaryを補助表示します。

```text
structured resume facts
  -> optional AI phrasing

AI phrasing
  != semantic authority
```

## 9. External AI boundary

### 9.1 Selected-context egress

Context Egress Plannerは、taskに必要なcanonical sliceを明示的に選びます。

候補には次があります。

- current question
- selected Observation / Evidence
- unresolved items
- current Recommendation
- Decision summary

全historical payloadをデフォルト送信する必要はありません。

### 9.2 Provenance

AI outputをcanonical Method Application / Recommendation等としてcommitする場合、既存Contractが要求する範囲でRealization / Provenanceを保持します。

network request IDやprovider conversation IDをsemantic identityにはしません。

### 9.3 Failure

AI timeout / unavailable / malformed responseを、案件のUnknownやnegative factへ黙って変換しません。

Product Surfaceはmanual modeへdegradeできます。

## 10. Failure model

first sliceで少なくとも次を区別します。

### F1 — Projection rebuild failure

canonical stateが正常なら、Projection failureはcanonical corruptionではありません。

### F2 — Unknown Contract / Profile

保持可能でも理解できない場合は`not_verified`等の既存境界へ戻します。UI都合でdropしません。

### F3 — AI / Method failure

external realization failureであり、Decision failureでもbusiness negative factでもありません。

### F4 — Semantic validation failure

canonical commit前に拒否します。draftは修正可能です。

### F5 — Stale snapshot

concurrency conflictとして扱い、last-write-winsで黙って上書きしません。

### F6 — Persistence commit failure

successful commitとして公開しません。partial visible stateを防ぐ実装をprototypeで検証します。

### F7 — Derived index loss

canonical dataから再構成できることを目標とします。

## 11. Persistenceとの境界

ADR-0029のLocal Single-Node Packageではfilesystem Persistenceがfirst Realizationです。

Interaction sliceはPersistenceへ次を期待します。

- canonical stateをdurableに保存できる。
- read snapshotに相当するprecondition情報を得られる方向を持つ。
-一つのcommitとして公開する範囲を明確にできる。
- derived / transient stateとcanonical dataの保存先・authorityを区別できる。

ただし、filesystem path、inode、mtime等をsemantic identityへ使用しません。

first prototypeで必要になったPersistence interface変更は、Universal RequirementではなくArchitecture / runtime concernとして先に評価します。

## 12. Product Accessとの境界

single-user prototypeであっても、Interaction Layerがsemantic Responsibility / Authorityをactor kindから推定しない原則を維持します。

将来multi-userへ進むときはADR-0030のProduct Access boundaryへ接続します。

```text
can submit a draft
  != can commit any semantic change
  != has Decision Authority
```

first sliceでは認証方式の完成を求めませんが、この分離を壊すAPI shapeを避けます。

## 13. Prototype component placement

first prototypeの有力配置は次です。

```text
┌──────────────────────────────────────────────┐
│ Local SEI Go Runtime                        │
│                                              │
│  Human browser adapter                       │
│  Machine / AI adapter                        │
│          │                                   │
│  Interaction Application Layer               │
│    - Working Set Resolver                    │
│    - Projection Builder                      │
│    - Semantic Change Planner                 │
│    - Commit Coordinator                      │
│    - Context Egress Planner                  │
│          │                                   │
│  Canonical Semantic Runtime                  │
│          │                                   │
│  Persistence Adapter / Integration Adapters  │
└──────────┬──────────────────────┬─────────────┘
           │                      │
           ▼                      ▼
 local durable data         optional external AI
```

browser assetsをruntimeへembedするか別processにするかは実装判断です。PMS-03 human reviewを早く回せることを優先し、deployment ontologyへしません。

## 14. Testability

Architectureは次のprobeを容易にする必要があります。

1. transient state全削除後のcanonical-only resume。
2. historical basisとpost-decision Observationの分離。
3. AI suggestion correction / dismissal。
4. AI adapter unavailable時のmanual operation。
5. working-set metadata loss後のrebuild。
6. commit途中fault injection。
7. stale snapshot commit拒否。
8. outbound AI contextのinspection。

Surface-level testだけでなく、Canonical Storeへ何がcommitされたかを比較できるようにします。

## 15. Current Requirementとの対応

本Architectureは主に次へ具体化されます。

- REQ-0001: transient / realization交換後のmeaning continuity。
- REQ-0005: historical basisの再構成。
- REQ-0006: provisional RecommendationとDecision等の分離。
- REQ-0010: progressive input / detail。
- REQ-0011: Projection / working setの非権威性。
- REQ-0014: residual / reopen。
- REQ-0015: private chain-of-thought非依存。
- REQ-0018: Persistence mechanicsとsemantic identityの分離。
- REQ-0019: Human / AI Surface parity。
- REQ-0023: Product Interactionから公開するcanonical commitの整合性。partial semantic stateやstale draftをsuccessful commitとして扱わない。

2026-09-16のRequirement auditでは、CR-73.8 / CR-73.9を一つの独立failure boundaryとしてREQ-0023へ統合し、SCN-0019でAcceptance化しました。CR-73.10はexisting selective-disclosure / authority boundaryとhuman Outcome評価へ戻し、新しいStable Requirementは追加していません。

transaction、atomic replace、ETag、digest、generation、snapshot token等は引き続きProduct / Persistence-localなmechanismであり、Universal semantic entityやSemantic Revisionへ昇格させません。

## 16. 意図的に未確定な点

- browser / desktop / CLIの正式supported surface。
- HTTP / MCP / SDKの正式machine protocol。
- semantic change planのportable schema化。
- commit atomicityの正式保証単位。
- concurrency tokenの形。
- working-set resolverのranking algorithm。
- AI summaryの利用有無。
- external AI context policyの正式permission model。
- team / multi-user collaboration。

これらをprototype実装の都合だけでADR / Contractへ昇格させません。

## 17. Evidence状態

```text
Architecture Design Evidence: established by this document
REQ-0023 / SCN-0019 formalization: Accepted / Design Satisfied
E1-E8 prototype / test source: Available
Evidence runner / verifier / one-command capture: Available
E1-E8 actual Go 1.25.x execution: Not Yet Verified
REQ-0023 / SCN-0019 Executable Evidence: Not Yet Verified
H1 human usability Evidence: Not Yet Observed
H2 counterfactual review Evidence: Not Yet Observed
Decision Continuity Product Value: Not Established
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

sourceや受入れtoolingの存在をactual Executable PASSへ読み替えません。E1〜E8がPASSしても、H1 / H2やDecision Continuity Product Valueが自動的に成立するわけではありません。current実行入口とtoolchain blockerは`../evaluation/personal-inquiry-decision/DECISION_CONTINUITY_EXECUTION_READINESS_2026-09-16.md`を参照します。

## 18. 関連文書

- `SEI_REFERENCE_ARCHITECTURE.md`
- `SEI_DEPLOYMENT_ARCHITECTURE.md`
- `SEI_PRODUCT_ACCESS_ARCHITECTURE.md`
- `../product/interaction/SEI_PRODUCT_INTERACTION.md`
- `../product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `../plan/adr/ADR-0005-progressive-semantic-explicitness.md`
- `../plan/adr/ADR-0010-decision-memory-minimal-semantic-boundary.md`
- `../plan/adr/ADR-0028-product-interaction-canonical-operation-boundary.md`
- `../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

## 19. Natural Japanese review

current Reference Architecture、Interaction、Packaging、Product Access、Persistence、Decision Memory、Projection非権威性へ戻り、resume-first Product Sliceに必要なstate authorityを4層へ整理した。

working setやResume Briefを製品上重要な構造として認めつつ、それらを新しいsemantic authorityへ昇格させないことを設計の中心に置いた。またAI responseからcanonical commitまでにprovisional draftとsemantic change planを置き、AIの能力を利用しながらRecommendation / Decision / Authorityの境界を保つ構成とした。

partial commitとstale writeは、単なる実装詳細として無視すると利用者から見たDecision integrityを壊し得るため、Architecture上のfailure boundaryとして明示した。Requirement auditではこの二つをREQ-0023 / SCN-0019へformalizeしたが、transaction modelやconcurrency versionはUniversal semanticsへ持ち込まずProduct / Persistence-localに保っている。actual E1〜E8はまだNot Yet Verifiedであり、formalizationやtest sourceの存在をExecutable Evidenceへ昇格させない。

意味、権威関係、未決事項、Evidenceの高さを固定したうえで全文を自然な日本語として再読し、最終意味監査を実施した。