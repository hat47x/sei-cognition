# Personal Inquiry Continuity — Research-derived Requirement Review

更新日: 2026-09-10  
状態: **Research-derived Requirement Review / Evaluation-only**  
関連: Issue #362 / `EXTERNAL_RESEARCH_SYNTHESIS.md` / `COGNITIVE_RESUMPTION_MODEL.md`

## 1. この文書の役割

外部研究・既存製品の調査結果を、Personal Inquiry Continuityの候補要件へ戻す。

目的は`PIC-*`を増やすことではなく、次を明確にすることである。

- 何がSEIの差別化価値に直接効くか
- 何が既存製品でも一般化しておりtable stakesか
- 何がSEIの既存Stable Requirementで既に守られているか
- 何をfirst dogfoodで反証可能にすべきか
- 何をまだStable Requirementへ昇格しないか

## 2. Product categoryの再定義

Personal Inquiry Continuityをgeneric PKM、AI memory、research notebook、decision journalのどれかとして定義しない。

first product hypothesisは次とする。

> **Epistemic Resume Layer** — 既存のchat、文書、Web、note等をsourceとして利用しながら、一つのInquiryについて「当時何を知り、何が未解決で、何を根拠にどう判断し、その後何が変わったか」をdurable meaningとして保持し、再開時には少ないcueでその認識状態へ戻れるようにするlayer。

`Epistemic Resume Layer`は仮称であり、Product NameやUniversal Semantic Conceptではない。

```text
SEI personal wedge
  != generic note store
  != generic semantic search
  != generic chat memory
  != citation-only research assistant
  != decision log only
```

## 3. 三つのplane

### 3.1 Source Plane

既存の外部sourceを置く。

例:

- AI conversation
- Web page
- PDF / document
- source code
- note / Markdown
- external PKM

SEIがsource本体を複製・所有しなければ成立しない設計にしない。

必要な場合はraw source snapshotやportable copyを保持できるが、first prototypeをgeneral-purpose document repositoryへしない。

### 3.2 Meaning Plane

SEIがdurableに守る対象。

- Inquiry context
- Observation / Evidence / Interpretation
- Unknown / Conflict
- Hypothesis
- Recommendation
- Decision / historical basis
- Constraint / premise when material
- residual / reopen information
- provenance / temporal lineage

ここがSEI Product Valueの中心である。

### 3.3 Resume Plane

人間またはAIが続きを始めるためのProjection / cue。

- Orientation Core
- Epistemic Delta
- optional Resume Anchor
- Detail Trail
- AI Handoff Projection

Resume Planeは再生成可能であり、Meaning Planeの正本ではない。

```text
Source Plane
   ↓ reference / extraction
Meaning Plane
   ↓ projection
Resume Plane

Resume Plane != canonical authority
Source availability != semantic truth
```

## 4. 競争軸の除外

外部製品調査から、次をfirst differentiation axisに置かない。

### 4.1 保存容量・文書管理

成熟したPKM / workspace製品が強い。SEIが全文書管理を再実装する理由は弱い。

### 4.2 generic semantic search

検索・RAG・AI searchは既に一般的であり、Personal Inquiry Continuityの成立価値を証明しない。

### 4.3 source-grounded answer / citation

重要だが、既に多くのAI research productが提供する。Source / Claim Separationを守るために利用してよいが、citation UIをwedgeにしない。

### 4.4 generic long-term AI memory

モデルへ次のconversation contextを供給するmemory最適化と、SEIのdurable semantic historyは目的が異なる。

### 4.5 local/offlineそのもの

local-firstはPersonal Profileの信頼性・control上重要だが、既存製品にも存在する。差別化ではなくhygiene factorとして扱う。

## 5. 差別化に直接効く能力

### D1 — Historical Epistemic Integrity

「現在何が正しいか」だけでなく、**Decisionや中断時点で何を知っていたか**を後から読み違えない。

中心PIC:

- PIC-006
- PIC-009
- PIC-013
- PIC-021

### D2 — Unknown-preserving Continuity

答えが無いInquiryでも、Unknown / Conflictを失敗扱いせずその状態から再開できる。

中心PIC:

- PIC-002
- PIC-006
- PIC-010

### D3 — Cognitive Reorientation

過去情報の検索ではなく、作業へ戻るためのmental context reinstatementを助ける。

中心PIC:

- PIC-010
- PIC-011
- PIC-012
- PIC-017

### D4 — Role-safe AI Portability

別AIへ渡すとき、text量だけでなくObservation / Hypothesis / Unknown / Recommendation / Decision / later Evidence等の役割を保つ。

中心PIC:

- PIC-004
- PIC-014
- PIC-015
- PIC-022
- PIC-023

### D5 — Progressive Capture without Semantic Loss

rationale記録の完全性を追求して入力負担で失敗しない。最初はfree-formで入り、必要な意味だけを明示する。

中心PIC:

- PIC-001
- PIC-003
- PIC-008
- PIC-011
- PIC-016
- PIC-025

## 6. PIC priorityの再評価

### 6.1 first dogfoodでMUSTとして扱う

次はProduct Valueを直接検証するため、first dogfoodの必須対象にする。

- PIC-001 Minimal Inquiry Start
- PIC-002 Decision-optional Inquiry Continuity
- PIC-003 Friction-bounded Capture
- PIC-005 Source / Claim Separation
- PIC-006 First-class Unknown / Conflict
- PIC-007 Recommendation / Decision Separation
- PIC-008 Lightweight Decision Memory
- PIC-009 Non-retroactive Decision Basis
- PIC-010 Reorientation Projection
- PIC-011 Detail-on-demand
- PIC-013 Reopen without Rewriting
- PIC-014 Chat-independent Readability
- PIC-017 Inquiry Discovery and Resume
- PIC-018 Local Standalone Read / Write
- PIC-019 Portable Export / Import
- PIC-023 No Mandatory Generative AI
- PIC-024 No Composite Truth / Confidence Collapse

### 6.2 SHOULDからMUST相当へ引き上げて検証する候補

#### PIC-012 Change-since-Decision / Change-since-Review

**Research-derived judgement:** first dogfoodではMUST相当。

理由:

- task resumptionでは現在のgoal contextを復元するcueが重要
- long-term memoryではknowledge update / dynamic state trackingが難所
- Personal Inquiryでは「何を知っているか」だけでなく「前回から何が変わったか」が次の行動を決める

Stable Requirementのpriority変更ではなく、evaluation profile上の優先度変更である。

#### PIC-021 Capture Time / Subject Time Separation

**Research-derived judgement:** first dogfoodではMUST相当。

理由:

- late-arriving Evidenceをpast Decision basisへ混入させないための前提となる
- valid time / transaction timeを分けるbitemporalな考え方と整合する
- historical reconstructionで「いつ起きたか」と「いつ知ったか」は異なる

### 6.3 SHOULDのまま維持

- PIC-004 Provisional Semantic Extraction
- PIC-015 Portable AI Handoff Projection
- PIC-016 Bulk Conversation / Note Intake
- PIC-020 Personal Retention Control
- PIC-022 Reversible Assistance
- PIC-025 Progressive Impact Depth

ただしPIC-015はcross-AI handoffがdogfoodで最大価値になる場合、first supported surfaceへ昇格する。

## 7. 新規PICを増やさず既存へ統合するもの

### Queryless Orientation

独立PICを増やさずPIC-010へ含める。

候補追記:

> Inquiry内部の再定位は、利用者が適切な検索queryを思い出し入力することを前提にしてはならない。Inquiryを開くと、current stateへ戻るためのcueを取得できること。

### Resume Anchor

新しいUniversal typeを追加しない。

first prototypeではProduct-local / residual representationとして試す。

### Premise / Validity Context

既存Constraint、Observation、Decision basis、Lineage等で表現可能かを先に検証する。

`validity`という単一truth flagを導入しない。

## 8. Stable Requirement gapの再監査

外部researchでproblem importanceは高まったが、Stable Requirement追加の根拠はまだ不十分である。

### Gap A — Decision-optional Inquiry

Personal Profileでは明示的MUST。

current REQ-0002 / REQ-0014等から意味上は導けるため、まずAcceptance Scenarioで実証する。

### Gap B — Personal data agency

local-first / user ownership研究から重要性は支持される。

しかしこれはPersonal ProfileだけでなくSEI Product Security / Privacy全体の問題である。別IssueでProduct-level Requirementとして扱うべきである。

### Gap C — AI semantic candidate boundary

current REQ-0016 / REQ-0020等でかなり覆える。

bulk importをdogfoodして、AI candidate stateをdurable conceptとして保存する必要が実際に生じるかを確認する。

### Gap D — Temporal knowledge-entry distinction

PIC-021の重要性はresearchで上がった。

ただしcurrent provenance / historical reconstruction requirementのAcceptance強化で足りる可能性が高い。

**現時点では新REQを追加しない。**

## 9. 要件文書へ将来正式化する際の構造

現行`requirements/README.md`のauthorityを維持する。

今は新しい`requirements/profiles/`正本階層を作らない。

正式化順序:

```text
research-derived hypothesis
  -> executable dogfood
  -> observed outcome / failure
  -> Acceptance Scenario addition or refinement
  -> Stable Requirement gap re-audit
  -> only independently necessary REQ addition
```

Personal profileの組合せを説明する文書が必要な場合でも、canonical Requirementの第二の正本にしない。

## 10. first executable sliceへの要件

外部researchを踏まえ、最小surfaceは次だけで価値検証できる。

### MUST operation

```text
create inquiry
open inquiry
add free-form material
record / preserve unknown
record recommendation separately
record decision optionally
record subject time separately from capture time when known
show orientation without requiring a query
show what changed since last review / decision
follow cue to detail/source
add later evidence without rewriting past basis
optional resume anchor
export portable inquiry state
```

### intentionally absent

- integrated full AI chat
- vector database UI
- knowledge graph visualization
- collaboration
- workflow engine
- autonomous agent
- rich task manager
- full document repository

## 11. Product message candidate

外部競合との境界を明瞭にする内部説明候補:

> **Return me to the last faithful state of the inquiry, not merely the last conversation.**

さらにmeaning側を強調すると:

> **Remember the state of knowing, not only the content.**

どちらもmarketing copyとしては未確定であり、dogfoodで価値が成立した場合のみ外向き表現を検討する。

## 12. Current decision

```text
external research strengthens:
  reorientation
  temporal integrity
  unknown preservation
  progressive capture

external research weakens differentiation based on:
  storage
  search
  citations
  generic AI memory
  offline alone

therefore:
  deepen evaluation requirements
  do not add Stable REQ yet
  do not expand Universal Contract
```

次のEvidenceは文書ではなく、real Inquiryを中断・再開するexecutable dogfoodから得る。