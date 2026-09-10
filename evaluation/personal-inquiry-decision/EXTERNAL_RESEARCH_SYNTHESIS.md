# Personal Inquiry Continuity — External Research Synthesis

更新日: 2026-09-10  
状態: **External Research / Evaluation-only**  
関連: Issue #362 / PR #361

## 1. 目的

この文書は、Personal Inquiry Continuity Profileを、SOZA内部の概念整合だけでなく、外部の研究・製品・標準と照合して再評価する。

対象は次の7系統である。

1. 長期AI memory / agent memory
2. task interruption / task resumption
3. personal information management / re-finding
4. design rationale / decision rationale
5. provenance
6. local-first / durable personal data
7. current PKM / AI research workspace products

目的は競合機能の模倣ではない。

```text
external precedent
  -> evidence for product problem / failure mode / design pressure
  != automatic SOZA Requirement
  != automatic Universal Contract concept
```

## 2. 結論の要約

外部リサーチから、Personal Inquiry Continuityの最初のProduct Valueは次へ絞るのがよい。

> **SOZAは「より多くの内容を覚える」製品ではなく、「何を・いつ・どの状態で知っていたかを壊さず、少ない再読で思考へ戻れるようにする」製品として個人価値を検証する。**

この差は重要である。

```text
content memory
  != epistemic state memory
  != historical decision memory
  != resumption support
```

current PKM / AI workspaceは、保存、検索、source-grounded Q&A、引用、AI要約、connected knowledge、local/offline等を既に強く提供している。

したがって、次はSOZAの差別化中心に置かない。

- file / note storageそのもの
- semantic searchそのもの
- source citationそのもの
- generic AI chat memory
- backlink / graph visualization
- local/offlineであることだけ
- research report generation

一方、次の組合せはSOZAの既存Product Valueと強く整合し、競争軸として比較的明瞭である。

- current stateとhistorical stateを分ける
- source claimとinterpretationを分ける
- Unknown / Conflictを一級の状態として残す
- RecommendationとDecisionを分ける
- Decision後のEvidenceをpast basisへ混入しない
- what changed since last review / Decisionを示す
- reopen condition / residualを残す
- AIが変わっても同じ意味をhandoffできる
- userが明示的な検索質問を作らなくても再開に必要な手掛かりを提示する

## 3. 長期AI memoryから得られる示唆

### 3.1 LongMemEval

LongMemEval（ICLR 2025）は、長期chat memoryを次の5能力で評価している。

- information extraction
- multi-session reasoning
- temporal reasoning
- knowledge updates
- abstention

長い会話履歴に対してcommercial assistant / long-context modelにも大きな性能低下があると報告し、session decomposition、time-aware query expansion等を検討している。

SOZAへの示唆は、単純な「過去turnを検索できる」では不足することである。

特にPersonal Inquiry Continuityでは次を独立に検査すべきである。

```text
recall an old fact
  != know which version is current
  != know what was known at Decision time
  != abstain when evidence is absent
```

### 3.2 LongMemEval-V2

LongMemEval-V2（2026）はagent memoryを、単なるdialog historyではなくenvironment experienceとして扱い、次を評価する。

- static state recall
- dynamic state tracking
- workflow knowledge
- environment gotchas
- premise awareness

このうちPersonal Inquiry Continuityへ特に重要なのは`dynamic state tracking`と`premise awareness`である。

SOZAでは、ObservationやDecisionを永久に同じ意味で有効なfactとして扱うのではなく、成立時点、basis、前提、変更後の状態を読める必要がある。

したがって、`Change-since-*`だけでなく、**その知識・判断がどの前提のもとで成立していたか**をdetailへ辿れることが重要になる。

### 3.3 Mem0等のmemory layer

Mem0は、長期会話からsalient informationを抽出・統合・検索するmemory-centric architectureを提示している。

この方向はSOZAにとって競合というより、異なるproblem framingである。

```text
AI memory layer:
  optimize what context to retrieve for the model

SOZA Personal Inquiry Continuity:
  preserve durable meaning so human and AI can reconstruct the inquiry state
```

SOZAがmemory extraction精度だけで競争すると、専用memory systemと同じ土俵になる。

### 3.4 LOCOMO-CONV

2026年9月のLOCOMO-CONVは、QA型memory benchmarkだけでは見えにくい、implicit / composedな会話でのretrieval gapを報告している。またretrievalが強くてもresponse qualityへ完全には転換しないとしている。

Personal Inquiry Continuityへの重要な示唆は、**利用者へ正しい検索質問を要求しないこと**である。

再開時の第一画面はquery boxだけでは弱い。

```text
open inquiry
  -> system presents compact reorientation cues
  -> user may then ask / inspect / continue
```

この意味でPIC-010 Reorientation Projectionは、単なるsummary viewではなくProduct Valueの中心に置くべきである。

## 4. task interruption / resumption研究から得られる示唆

### 4.1 context cueの重要性

Hodgetts & Jones (2006)は、中断前後のcontext cueがtask recoveryを助けることを示している。cueが変化すると回復が妨げられる。

Altmann & Trafton (2007)も、中断後に失われたmental contextを段階的に回復する過程としてresumption costを説明している。

この研究系統はPersonal Inquiry Continuityの中心Jobを「archive retrieval」より「context reinstatement」と捉える根拠になる。

つまりOrientation Projectionは情報量最大化ではなく、**元のmental contextを再活性化する最小のcue set**を目指すべきである。

### 4.2 suspension時のcue

Trafton et al. (2003)や関連研究では、中断直前に再開準備の時間があるとtask resumptionが改善する。

SOZAへそのまま実装概念を移す必要はないが、Product Interactionとして次が有力である。

> Inquiryを離れるとき、「次に何を見ようとしていたか」「今どこで詰まっているか」を短いResume Anchorとして残せる。

このResume Anchorは新しいUniversal semantic entityでなくてよい。

既存のresidual / reopen information、current working focus、Projection-local metadataの組合せで実現可能かを先に検証する。

### 4.3 explicit suspensionを強制しない

現実の中断は突然起きる。

したがって、毎回利用者へ「終了処理」を要求する設計は摩擦が高い。

first prototypeでは、

- explicit Resume Anchorを任意に残せる
- なければcurrent canonical stateからOrientation Projectionを生成する
- AI生成anchorはcandidateでありcanonical truthにしない

という段階設計が望ましい。

## 5. Personal Information Managementから得られる示唆

PIM研究では、情報管理を`keeping`と`finding / re-finding`のlife cycleとして扱う。

Alvarado, Teevan, Ackermanの研究では、人は個人情報を再発見するとき、対象に関するcontextual knowledgeを手掛かりに、小さなnavigationを重ねることがある。

Jonesらのre-finding研究も、再発見支援は最初のkeeping段階から始まること、複数情報形式とlife cycle全体を見る必要性を指摘する。

これはPIC-003 Friction-bounded CaptureとPIC-017 Inquiry Discoveryを次のように結びつける。

```text
capture quality affects later resumption
but
capture must not become a filing chore
```

SOZAでは、保存時に厳密な分類を全部要求するのではなく、後の再定位に効く最低限のcontextを落とさない設計が必要である。

特に重要なのは、sourceのタイトルだけでなく必要に応じて次を保持できること。

- なぜこの資料を見たか
- 何のInquiryに関係したか
- 何をこの資料からObservationとして使ったか
- 何がまだ解けなかったか

ただしこれらをすべてmanual mandatory fieldにしない。

## 6. design rationale / decision rationaleから得られる示唆

IBIS系およびDRedは、issue、option、pro / con argument等を明示して設計理由を残す系譜を持つ。

DRedの産業導入研究では、routine useにはsimplicityが重要であると報告されている。

SOZAへの示唆は二つある。

第一に、Decisionの理由・alternative・argumentを構造化する価値自体は新しくない。

第二に、構造化の理論的完全さより**記録摩擦が低いこと**が採用上重要である。

したがってPersonal Inquiry Continuityは、IBIS editorのように全思考を明示graphへ入力させる方向へ寄せない。

```text
rich rationale structure available on demand
  != mandatory rationale graph editing
```

PIC-003、PIC-008、PIC-011の優先度はこの観点から高い。

## 7. provenance標準から得られる示唆

W3C PROVは、entity、activity、agent、derivation、responsibility等を扱い、異種system間でprovenanceを表現・交換するための標準的な枠組みを提供する。

SOZAはprovenanceを独自に全部再発明する必要はない。

一方、PROVの存在だけではSOZAのProduct Valueは成立しない。

SOZAが扱うのはprovenanceに加えて、Unknown / Conflict、Recommendation / Decision、historical basis、reopen residual等の判断意味である。

したがって今後は、

```text
SOZA provenance semantics
  may map to / interoperate with W3C PROV where useful
  != adopt PROV wholesale as SOZA Universal Contract
```

とするのがよい。

Personal Profileのfirst value gateではPROV mappingを必須にしない。

## 8. local-first / data ownershipから得られる示唆

Kleppmann et al.のlocal-first workは、offline利用、長期保存、user control、server停止後もdataへアクセス可能であることを重視する。

現行製品でもObsidianはMarkdown plain textをlocal filesystemへ保存し、CapacitiesやHeptabaseもoffline accessを提供している。

このため、Personal Inquiry Continuityにおけるlocal/offlineは重要だが**差別化機能ではなくhygiene factor**と考えるべきである。

つまりPIC-018 / PIC-019 / PIC-020 / PIC-NF-002は削るべきではないが、marketing-level core valueへは置かない。

Product Valueの中心は、localであることではなく、localに保持したdataが**意味を失わず別のhuman / AIへ渡せること**にある。

## 9. current product landscape

### 9.1 ChatGPT Projects

ChatGPT Projectsは、特定のwork bodyについてchat、file、instruction、historyを一つのspaceに置き、継続作業のcontextを保持する。

これは「長期project context」自体が既に一般的product capabilityになっていることを示す。

SOZAは「project contextを持つ」だけでは差別化できない。

### 9.2 Gemini Notebook

2026年のGemini Notebookはsource-grounded research、source attribution、web research、advanced reasoning、artifact generation等を強化している。

source-grounded answerとcitationは既に強い競争領域である。

SOZAのSource / Claim Separationは重要だが、citation UIだけを価値中心にしない。

### 9.3 Notion AI

Notion Enterprise Search / Researchはworkspaceやconnected appを横断し、source citationを伴うAI回答やresearchを提供する。

横断検索・調査生成もSOZA独自性にはしにくい。

### 9.4 Heptabase

Heptabaseはcards / whiteboards / PDF / journal等をconnected knowledge baseとして扱い、AI searchやMCPで外部AIとの連携も提供している。

特に、外部AIがknowledge baseをMCP経由でread / create / editできるため、単なる「AI handoff可能」は差別化として弱い。

SOZAのAI Handoffは、access protocolではなく**epistemic roleとhistorical stateを壊さず渡すこと**で価値を定義する必要がある。

### 9.5 Obsidian / Capacities

local data、offline、structured properties、search、object model等は成熟している。

SOZAはgeneric PKMへの機能拡張競争へ入らない。

## 10. Product wedgeの再定義

外部リサーチを踏まえ、Personal Inquiry Continuityのwedgeを次の一文へ更新する候補を推奨する。

> **SOZAは、長く続く個人のInquiryについて、情報をただ保存・要約するのではなく、「何をその時点で知り、何が未解決で、何を根拠にどう判断し、その後何が変わったか」を壊さず保持し、再開時には最小の手掛かりでそこへ戻れるようにする。**

さらに短くすると、内部設計上は次が核になる。

> **Remember the state of knowing, not only the content.**

これはmarketing copyの確定ではない。

## 11. 新しい設計仮説

### H1 — Orientation is not Summary

Orientation Projectionはsource全体の代表summaryではなく、task / inquiry resumptionのためのcue packetである。

含む候補:

- inquiry question
- current focus
- unresolved item
- latest meaningful change
- Decision / hypothesis if material
- next reopen cue

情報量が少ないほど良いわけではない。再開に必要なcontext reinstatementが成立する最小量を探る。

### H2 — Queryless Reorientation

利用者が「何を聞けばよいか」を思い出す前でもInquiryを開けば現在地を読めること。

semantic searchは二段目でよい。

### H3 — Resume Anchor

利用者が任意に、またはsystemがcandidateとして、「次に何を見るか」「何で止まっているか」を短く残せる。

Resume Anchorはhistorical truthやDecisionではない。

### H4 — Premise Awareness

Observation / Hypothesis / Decisionについて、materialな場合は「どの前提・時点で成立したか」へ戻れる。

current validityを自動Truth判定しない。

### H5 — Change is a first-class reorientation cue

`what changed since I last looked?`を、単なるtimeline browsingより上位の再開操作として評価する。

## 12. PIC候補への影響

外部Evidenceを踏まえ、次の優先度変更を候補とする。

### MUST-PROFILEとして強化

- PIC-003 Friction-bounded Capture
- PIC-005 Source / Claim Separation
- PIC-006 First-class Unknown / Conflict
- PIC-009 Non-retroactive Decision Basis
- PIC-010 Reorientation Projection
- PIC-011 Detail-on-demand
- PIC-014 Chat-independent Readability
- PIC-017 Inquiry Discovery and Resume
- PIC-018 Local Standalone Read / Write
- PIC-019 Portable Export / Import

### SHOULDからMUSTへの昇格をdogfoodで検証

- PIC-012 Change-since-Decision / Change-since-Review
- PIC-021 Capture Time / Subject Time Separation

### 新規候補

- **PIC-026 — Queryless Orientation**: Inquiryを開くためにretrieval queryを要求しない。
- **PIC-027 — Resume Anchor**: 中断時または中断後に再開cueを保持できる。
- **PIC-028 — Premise / Validity Context**: materialなclaim / hypothesis / Decisionの成立前提やvalidity contextへ戻れる。

ただしPIC-026はPIC-010へ統合可能であり、PIC-027はresidual / reopen semanticsで表現可能、PIC-028はexisting Constraint / historical contextで表現可能な可能性が高い。

新規Stable REQ追加はまだ行わない。

## 13. Value Validationへの影響

従来の5-question reorientationだけでは不十分である。

次のtestを追加する。

### A. Queryless resume

数日以上空け、何も検索語を入力せずInquiryを開く。

測定:

- current focusを復元できるか
- first useful actionまでに何sourceを開いたか
-誤ったInquiry branchへ入らないか

### B. Temporal update

Decision / hypothesis後に、それを弱める新Evidenceを追加する。

測定:

- past basisを汚さないか
- new evidenceをcurrent stateとして識別できるか
- old stateとnew stateを混同しないか

### C. Abstention / unknown

答えがまだ無いInquiryを再開する。

測定:

- systemがfalse resolutionを生成しないか
- Unknownをそのまま現在地として提示できるか

### D. Premise change

以前の前提を無効にする条件変更を入れる。

測定:

- historical Decisionを誤りとして上書きせず、前提変化を認識できるか

### E. Cross-AI handoff

別AIへstructured Projectionを渡す。

測定:

- recommendation / decision / unknown / later evidenceの役割を取り違えないか
- raw transcript全量なしに有用なcontinuationができるか

### F. Capture burden

DRed等のrationale-capture研究の教訓から、記録完全性だけでなくfrictionを必須評価する。

測定:

- manual classification回数
- mandatory fields数
- interruption前にResume Anchorを残す操作負担
- userがanchor / unknown / basis記録を飛ばす頻度

## 14. 差別化上のfalsification条件

次が繰り返し成立する場合、Personal Inquiry ContinuityのProduct Shapeをpivotする。

1. current AI project memory +普通のnoteで、historical state混同なく同程度に再開できる。
2. Unknown / Decision basis / later evidenceの分離が、実際の再開行動にほぼ寄与しない。
3. Orientation Projectionより普通のAI summaryの方が一貫して速く正確に再開できる。
4. historical integrityを維持するためのcapture負担が、得られる再開価値を上回る。
5. 利用者がstructured Inquiry memoryを作らず、raw chat searchへ自然に戻る。
6. cross-AI portabilityを実際には利用しない。

反対に、次が複数題材で再現すればProduct ValueのEvidenceが強くなる。

- later evidenceをpast stateと混同しにくい
- 未解決点から再開しやすい
- source再読量が減る
- queryを思い出さなくても現在地へ戻れる
- model / chatを交換してもcontinuityが保たれる
- userが新しいInquiryでも自発的に利用する

## 15. current requirement判断

この調査だけを根拠に`requirements/PRODUCT_REQUIREMENTS.md`へStable Requirementを追加しない。

外部研究はproblem validityを強めたが、SOZA固有のnormative necessityを確定するAdoption / Outcome Evidenceではない。

現時点の変更対象はevaluation-level Product Hypothesisとdogfood protocolである。

## 16. 参考文献・参照先

### AI / agent memory

- Wu et al., "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory", ICLR 2025. https://arxiv.org/abs/2410.10813
- Wu et al., "LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues", 2026. https://arxiv.org/abs/2605.12493
- Chang & Chen, "When Users Don't Ask: Benchmarking Context-Driven Memory Retrieval in Conversational Agents", 2026. https://arxiv.org/abs/2609.03467
- Chhikara et al., "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory", 2025/2026. https://arxiv.org/abs/2504.19413

### task resumption / PIM

- Hodgetts & Jones, "Contextual cues aid recovery from interruption", 2006. DOI: 10.1037/0278-7393.32.5.1120
- Altmann & Trafton, "Timecourse of recovery from task interruption", 2007. DOI: 10.3758/BF03193094
- Trafton et al., "Preparing to resume an interrupted task", 2003. DOI: 10.1016/S1071-5819(03)00023-5
- Alvarado, Teevan & Ackerman, "Surviving the Information Explosion: How People Find Their Electronic Information", 2003.
- Jones et al., "How Do People Re-find Files, Emails and Web Pages?", 2014. DOI: 10.9776/14136
- Jones et al., "Personal Information Management", 2021. https://arxiv.org/abs/2107.03291

### rationale / provenance / local-first

- Bracewell et al., "Capturing design rationale", Computer-Aided Design 41(3), 2009. DOI: 10.1016/j.cad.2008.10.005
- W3C PROV Overview / PROV-DM family. https://www.w3.org/TR/prov-overview/
- Kleppmann et al., "Local-first software: You own your data, in spite of the cloud", Onward! 2019. DOI: 10.1145/3359591.3359737

### current product references checked in 2026-09

- OpenAI, ChatGPT Projects documentation.
- Google, Gemini Notebook / NotebookLM product and research documentation.
- Notion, Enterprise Search / Research Mode documentation.
- Heptabase product and MCP / AI search documentation.
- Obsidian data storage / import / Bases documentation.
- Capacities offline support documentation.

これらの製品参照はfeature comparisonのために使用し、absence of featureを厳密に証明するものではない。