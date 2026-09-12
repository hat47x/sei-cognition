# Personal Inquiry Continuity — Evaluation Entry Point

更新日: 2026-09-10  
状態: **Evaluation-only Product Hypothesis / Root Concept Entry**  
関連: Issue #367 / Issue #362 / Issue #365

## 1. このディレクトリで確かめたいこと

このディレクトリの目的は、SOZAのProduct Valueを、組織導入や複雑なProvider連携より先に、**一人の利用者が自分の長期的な問いを中断・再開する場面で本当に役立つか**という小さな領域で確かめることである。

ここで最初に守りたいのは、情報量でも検索精度でもAIの回答品質でもない。

> **時間が空き、AIや資料や作業環境が変わっても、そのInquiryについて「当時どこまで知っていたか、何がまだ分からなかったか、何をどう考え、何を決め、その後何が変わったか」を壊さずに保ち、そこから続きを始められること。**

この中心仮説を **Personal Inquiry Continuity** と呼ぶ。

Decisionは重要な一部だが、InquiryはDecisionへ到達しなくても成立する。

```text
Personal Inquiry Continuity
  contains Decision Memory when Decision exists
  != Decision tracker only
  != chat archive
  != note-taking app
  != task manager
```

ここにある文書・prototypeは、現時点ではStable Product RequirementやUniversal Contractではない。

## 2. 根幹の問題

個人が数日から数か月以上にわたり何かを考えるとき、情報は一つの場所に閉じない。

- AI conversation
- Web page
- PDF / document
- code / repository
- personal note
- later observation
- 別のAIやtoolで行った追加検討

このとき単に「情報を保存できる」だけでは、次の問題が残る。

### 2.1 内容を覚えていても、認識状態は失われる

過去の文章や会話を検索できても、次が分からなくなることがある。

- その時点で何を事実として見ていたか
- 何が解釈や仮説だったか
- 何がまだUnknownだったか
- Conflictがどこに残っていたか
- AIのRecommendationと本人のDecisionのどちらだったか
- Decision時点で何をbasisとしていたか
- その後初めて知った情報は何か

したがって、ここで扱う問題は単なるcontent memoryではない。

```text
content memory
  != epistemic state memory
  != historical decision memory
  != cognitive resumption support
```

### 2.2 正確な記録だけでも、人間はすぐ再開できない

逆に、canonical dataを細かく完全に保存しても、それをすべて読み直さなければ作業へ戻れないなら、個人Productとしての価値は弱い。

必要なのは、正確な記録と、人間が続きを始めるための再開支援を分けることである。

```text
Durable Inquiry Memory
  = precise / historical / inspectable / portable meaning

Resumption Projection
  = compact / selective / regenerable cue

Resumption Projection != canonical authority
```

### 2.3 速く戻れたように見えるだけでは成功ではない

再開を高速化しても、later evidenceをpast basisと誤認したり、RecommendationをDecisionと取り違えたりすれば、かえって危険である。

この状態をこのevaluationでは **False Continuity** と呼ぶ。

```text
fast resume
+ wrong historical state
= failure
```

SOZA Personal Profileの価値は、単に再開時間を短くすることではなく、**認識状態を壊さずに再開負担を下げられるか**で判断する。

## 3. Product Hypothesis

個人向けSOZAを、既存のChat、PKM、document repository、Web research toolを置き換える製品として始めない。

それらをSourceとして利用し、その上に薄い意味・再開層を置く。

```text
Source Plane
  external chat / web / document / note / code
        ↓
Meaning Plane
  durable Inquiry semantics
        ↓
Resume Plane
  Orientation / Delta / Anchor / Handoff
```

設計上の仮称として、SOZAがこの範囲で担う役割を **Epistemic Resume Layer** と表現する。

これは製品名ではなく、Product Boundaryを考えるための説明である。

### Source Plane

元情報を保持・参照する場所。

SOZA自身が汎用全文書repositoryになることを要求しない。

### Meaning Plane

時間を越えて持ち運びたい意味を保持する。

中心となるのはcurrent SOZA semanticsの範囲である。

- Inquiry
- Observation / source claim
- Interpretation / Hypothesis
- Unknown / Conflict
- Recommendation
- Decision
- basis
- Constraint / material premise
- residual / reopen information
- provenance / revision / lineage

### Resume Plane

人間または別AIが続きを始めるためのProjectionを生成する。

- Orientation
- change since Decision / last review
- Resume Anchor
- detail trail
- AI/tool handoff

Resume PlaneはMeaning Planeを読むが、過去の意味を権威的に書き換えない。

## 4. 誰のどんな場面から始めるか

first value validationでは、一人の利用者が数日から数か月以上かけて扱う、低〜中影響のInquiryを主対象とする。

例:

- 個人プロジェクトの技術・方式選定
- 学習テーマや教材の比較
- 機器、サービス、作業環境の比較
- 趣味、旅行、創作、調査の計画
- 長期的な設計課題や個人研究

一度きりで終わる質問より、**一度中断し、後から状況や情報が変わった状態で再開する問い**が適している。

first profileでは、医療・法務・重大な金融判断等のhigh-stakes用途、多人数承認、enterprise IdP / RBAC、汎用task management、常時agent orchestration等を中心に置かない。

## 5. 根幹から導かれる能力

個別Requirementへ入る前に、上の趣旨から最低限どの能力が必要になるかを整理する。

### Capability A — Faithful State Preservation

当時のObservation、Unknown、Conflict、Recommendation、Decision、basis等を意味上区別し、後から得た知識で過去を黙って書き換えない。

### Capability B — Low-friction Capture

利用者がContract型を逐一操作しなくても、問いや材料を軽く追加でき、必要なsemantic commitmentは後から深められる。

### Capability C — Queryless Reorientation

Inquiryを開いたとき、正しい検索語やAIへの質問を思い出さなくても、現在地へ戻るためのcueを得られる。

### Capability D — Epistemic Delta

Decisionまたは前回review以後に何が変わったかを、past stateを壊さずに確認できる。

### Capability E — Detail and Provenance Descent

light Orientationだけを権威化せず、必要なときsource、basis、time、revision、provenanceへ降りられる。

### Capability F — Independence and Handoff

元chat、特定LLM、特定providerがなくても保存済みInquiryを読み、別AI / tool / environmentへ意味を渡せる。

これらはまだStable Requirementの新設を意味しない。多くはcurrent SOZA Requirementの組合せを個人Profileへ具体化したものである。

## 6. 能力から個別課題へ降りる

詳細な設計・要件は、上位のProduct Intentから導出できることを前提とする。

```text
Root Intent
  認識状態を壊さず、中断したInquiryを再開できる
    ↓
Problem
  content保存だけではstate of knowingとmental contextが失われる
    ↓
Product Hypothesis
  Sourceの上にMeaning + Resume layerを置く
    ↓
Capabilities
  preservation / capture / orientation / delta / detail / handoff
    ↓
Candidate Requirements
  PIC-*
    ↓
Acceptance / Falsification
  queryless resume / generic summary comparison / late evidence / false continuity ...
    ↓
Prototype
  local evaluation CLI
    ↓
Evidence
  mechanics → real dogfood → Adoption / Outcome
```

個別のfield、CLI command、timestamp rule、UI state等から上位趣旨を逆算するのではなく、原則としてこの方向へ降りる。

具体的な対応関係は `CONCEPT_TO_REQUIREMENT_DERIVATION.md` を参照する。

## 7. 推奨Reading Order

このディレクトリを理解するときは、filename順ではなく次の順に読む。

### Stage 1 — 趣旨とProduct Boundary

1. `README.md` — 根幹の趣旨、問題、Product Hypothesis、必要能力
2. `EXTERNAL_RESEARCH_SYNTHESIS.md` — なぜこの問題が既存研究・製品でどのように現れるか
3. `COGNITIVE_RESUMPTION_MODEL.md` — Durable MemoryとCognitive Resumptionをどう分けるか

### Stage 2 — 趣旨から要件への導出

4. `CONCEPT_TO_REQUIREMENT_DERIVATION.md` — 根幹→能力→候補要件→検証の対応
5. `PRODUCT_PROFILE_REQUIREMENTS_CANDIDATE.md` — PIC-* の詳細
6. `REQUIREMENT_GAP_AUDIT.md` — current REQとの重複・gap
7. `RESEARCH_DERIVED_REQUIREMENT_REVIEW.md` — external researchを受けた優先度・表現再検討

### Stage 3 — Product Interactionと検証

8. `INTERACTION_STATE_MODEL.md` — Product-local stateとdurable semanticsの境界
9. `VALUE_VALIDATION_PROTOCOL.md` — Product Valueをどう反証可能に検証するか
10. `RESEARCH_DERIVED_VALIDATION_AMENDMENTS.md` — queryless resume、late evidence、False Continuity等の追加検証

### Stage 4 — 実装・Evidence

11. `DOGFOOD_SURFACE.md` — evaluation CLIの役割と使い方
12. `dogfood_core.py` / `dogfood_cli.py` / focused tests — executable mechanics
13. `REQUIREMENTS_FORMALIZATION_PLAN.md` — Evidenceからactual requirementsへ進む条件

この順序は「必ず全て読む」という意味ではない。上流の判断に疑問がある場合、下流detailへ進む前に上流へ戻れることを重視する。

## 8. 今後の文書整備順

新しい課題を発見した場合、原則として次の順序で文書化する。

1. **Root Intentとの関係** — 何を守るための課題か。
2. **Problem** — どの失敗・不便・意味損失を防ぐのか。
3. **Evidence / Observation** — research、dogfood、actual repositoryのどこから問題が見えたか。
4. **Design Principle / Capability** — 問題を解くために何が必要か。
5. **Existing Coverage** — current Product Value / REQ / Contractで既に表現されていないか。
6. **Candidate Requirement / Acceptance** — 独立規範が必要な場合だけ具体化する。
7. **Realization** — UI、CLI、schema、algorithm、storage等を選ぶ。
8. **Evidence** — 実装が何を確認でき、何をまだ確認していないかを分ける。

次の進め方は避ける。

```text
implementation idea
  -> field / command / typeを追加
  -> 後から理由を探す
```

代わりに、

```text
root purpose
  -> observed problem
  -> required capability
  -> minimum normative difference
  -> realization
```

の順を優先する。

新しい詳細を追加するとき、既存の上位文書で説明できない場合は、詳細を先に正本化せず、上位仮説自体の不足またはscope creepを先に検討する。

## 9. 現時点のEvidence

現時点では次まで進んでいる。

- Product hypothesis / candidate requirementのDesign Evidence
- external researchによるproblem validityの補強
- Source / Meaning / Resume modelのDesign Evidence
- local evaluation CLIによるscoped executable mechanics
- focused testsによる一部semantic boundaryの確認

まだ確認していないもの:

- 複数real Inquiryでの継続dogfood
- Generic SummaryよりSOZA Orientationが有用であること
- capture burdenが継続利用可能であること
- False Continuityが実際に減ること
- voluntary reuse
- Adoption / Outcome Evidence
- production UX / packaging

したがって、prototypeが動くことをProduct Value成立と同一視しない。

## 10. 次に進める順序

次段階では、新しい機能を増やすより先にreal dogfoodを行う。

1. actualな低〜中影響Inquiryを複数扱う。
2. 中断後にqueryless Orientationで再開する。
3. Generic Summaryとの比較を行う。
4. late-arriving Evidence / premise change / since-review deltaを踏む。
5. First Useful Action、Source Reopen Count、False Continuity、capture burdenを記録する。
6. 有効でなかったCapability / cue / candidate requirementを削る。
7. その結果からAcceptance Scenarioを先にformalizeする。
8. current REQで表現できない独立必要性が残る場合だけStable Requirement追加を検討する。

```text
working prototype
  != Product Value proven
  != Stable Requirement justified
```

## 11. この評価で守るstop lines

```text
content retrieved != inquiry resumed
summary != historical authority
later evidence != past decision basis
recommendation != decision
unknown != missing field
retrieval rank != truth
resume cue != canonical meaning
prototype mechanics != adoption evidence
personal profile convenience != universal semantic requirement
```

この境界を保ちながら、個人にとってSOZAが本当に必要な部分だけを残す。