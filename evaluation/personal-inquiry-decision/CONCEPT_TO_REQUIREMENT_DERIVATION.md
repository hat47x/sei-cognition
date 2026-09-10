# Personal Inquiry Continuity — Concept to Requirement Derivation

更新日: 2026-09-10  
状態: **Evaluation-only Derivation Map / Not Stable Requirement**  
関連: Issue #367 / `README.md`

## 1. この文書の役割

この文書は、Personal Inquiry Continuityの根幹の趣旨から、個別のCandidate Requirement、Acceptance、prototype detailへどう降りるかを示す橋渡しである。

ここでは新しい要件を増やすことより、**既存の個別課題が何を守るために存在するかを遡れること**を優先する。

```text
Root Intent
  ↓
Problem / Failure
  ↓
Required Capability
  ↓
Candidate Normative Difference
  ↓
Acceptance / Falsification
  ↓
Realization
```

逆方向に、implementation detailからProduct Purposeを作らない。

## 2. Root Intent

Personal Inquiry Continuityで守りたい中心は次である。

> **時間が空き、情報・AI・環境が変わっても、Inquiryの認識状態を過去と現在を混同せず保持し、人間またはAIがそこから続きを始められること。**

この中心から二つの価値が導かれる。

### R1 — Faithfulness

「当時何を知っていたか」と「後から分かったこと」を混ぜず、Unknown、Conflict、Recommendation、Decision等の意味差を残す。

### R2 — Resumability

正確な履歴を全部読み直さずとも、再開に必要なcontextへ戻れる。

この二つの片方だけではProduct Hypothesisは十分ではない。

```text
faithful but exhausting to reread
  = archive, not enough resume support

fast but historically wrong
  = false continuity

Personal Inquiry Continuity
  = faithful enough + resumable enough
```

## 3. Root Failure Model

個別機能を考える前に、どの失敗を防ぐ必要があるかを定める。

### F1 — Epistemic Flattening

Observation、Interpretation、Unknown、Conflict、Recommendation、Decision等が一つの要約へ潰れ、元の意味差へ戻れない。

### F2 — Temporal Contamination

後から得たEvidenceが、過去Decision時点で既知だったbasisのように扱われる。

### F3 — Context Loss

正しい記録は残っているが、中断後に何をしていたかを復元するため元chatやsourceを大量に読み直す必要がある。

### F4 — False Continuity

短いsummary等で素早く戻れたように見えるが、old/current state、Recommendation/Decision、known/unknown等を取り違えている。

### F5 — Capture Collapse

意味を正確に残そうとするあまり、入力負担が本作業を妨げ、利用者が記録しなくなる。

### F6 — Environment Lock-in

元chat、特定LLM、特定SaaS、特定UIがなくなると、Inquiryの意味を読めない・続けられない。

### F7 — Product Scope Expansion

再開価値を実現するためにSOZA自身がchat、document repository、task manager、general PKMまで所有し始め、Product Value検証がぼやける。

## 4. FailureからCapabilityを導く

| Root failure | 必要なCapability | 意味 |
|---|---|---|
| F1 Epistemic Flattening | A Faithful State Preservation | semantic roleを区別し、Projectionからdetailへ戻れる |
| F2 Temporal Contamination | A Faithful State Preservation / D Epistemic Delta | subject timeとknowledge-entryを区別し、past basisを非遡及にする |
| F3 Context Loss | C Queryless Reorientation | queryを考える前にorientation cueから戻れる |
| F4 False Continuity | A + C + D + E | 速さだけでなくhistorical correctnessを再開支援に含める |
| F5 Capture Collapse | B Low-friction Capture | semantic commitmentを段階化し、自然入力から始める |
| F6 Environment Lock-in | F Independence and Handoff | durable meaningを特定AI/sessionから独立させる |
| F7 Scope Expansion | E Detail and Provenance Descent + Product Boundary | Sourceは既存toolへ残しMeaning/Resumeへ集中する |

ここでCapability名はProduct設計上の整理であり、新しいUniversal typeではない。

## 5. Capability A — Faithful State Preservation

### 5.1 なぜ必要か

Inquiry continuityは、単に最新版を保存すれば成立するものではない。

Decisionを後から理解するには、Decision時点のbasis、Unknown、Conflict、Constraint等が必要になる。一方で、later Evidenceはcurrent stateには必要でもpast stateへ混入させてはいけない。

### 5.2 導かれるCandidate Requirement

主に次へ接続する。

- PIC-005 Source / Claim Separation
- PIC-006 First-class Unknown / Conflict
- PIC-007 Recommendation / Decision Separation
- PIC-008 Lightweight Decision Memory
- PIC-009 Non-retroactive Decision Basis
- PIC-013 Reopen without Rewriting
- PIC-021 Capture Time / Subject Time Separation
- PIC-024 No Composite Truth / Confidence Collapse

### 5.3 Acceptanceへどう降りるか

- Unknownを残したままInquiryを中断・再開できる
- RecommendationをDecisionとして表示しない
- Decision後に初めて知ったEvidenceをpast basisへ追加できない
- historical Decisionとcurrent stateを同時に説明できる

### 5.4 Realizationは後から選ぶ

JSON field、database temporal model、timeline UI等はこのCapabilityから導かれるRealization候補であり、Capabilityそのものではない。

## 6. Capability B — Low-friction Capture

### 6.1 なぜ必要か

記録の正しさを求めるほど、利用者へsemantic classificationを強制したくなる。しかし入力負担で継続利用されなければPersonal Product Valueは成立しない。

### 6.2 導かれるCandidate Requirement

- PIC-001 Minimal Inquiry Start
- PIC-003 Friction-bounded Capture
- PIC-004 Provisional Semantic Extraction
- PIC-016 Bulk Conversation / Note Intake
- PIC-022 Reversible Assistance
- PIC-025 Progressive Impact Depth

### 6.3 Acceptanceへどう降りるか

- 問い一つから開始できる
- material追加のたびにContract型選択を要求しない
- AI分類candidateの誤りをsourceへ戻って訂正できる
- structured captureが本作業の中断原因になっていないか観測する

### 6.4 Stop line

```text
low friction
  != silent semantic commitment

automatic extraction
  != user-confirmed meaning
```

## 7. Capability C — Queryless Reorientation

### 7.1 なぜ必要か

Inquiryを見つけた後でさえ、「何を検索すればよいか」「何をAIへ聞けばよいか」を思い出せないことがある。

検索はfindabilityを助けるが、mental contextへの復帰そのものではない。

### 7.2 導かれるCandidate Requirement

- PIC-010 Reorientation Projection
- PIC-011 Detail-on-demand
- PIC-017 Inquiry Discovery and Resume

PIC-017のInquiry discoveryとPIC-010のresumptionは分ける。

```text
find the inquiry
  != resume the inquiry
```

### 7.3 Acceptanceへどう降りるか

- Inquiryを開いた直後、queryなしでcurrent focusを復元できるか
- 元source/chatを何件開き直したか
- First Useful Actionへどの程度直接進めたか
- Generic Summaryとの差が実際にあるか

## 8. Capability D — Epistemic Delta

### 8.1 なぜ必要か

再開時に必要なのはcurrent summaryだけではない。

前回reviewまたはDecision以後に何が変わったかが分かると、過去を全部読み直さず現在との差分へ集中できる可能性がある。

### 8.2 導かれるCandidate Requirement

- PIC-012 Change-since-Decision / Change-since-Review
- PIC-013 Reopen without Rewriting
- PIC-021 Capture Time / Subject Time Separation

### 8.3 Acceptanceへどう降りるか

- since-reviewで新規・変更情報が区別される
- late-arriving Evidenceがpast basisへ入らない
- premise changeがold Decisionを自動的に`wrong`へ変えない
- Delta表示が実際に再読を減らすかを比較する

### 8.4 Falsification

Deltaが複数real Inquiryで行動や再読量に寄与しなければ、PIC-012を強いProfile MUSTへ上げない。

## 9. Capability E — Detail and Provenance Descent

### 9.1 なぜ必要か

Orientationを短くするには選択・圧縮が必要であり、必ず取りこぼしや誤りの可能性が生じる。

そのためlight viewは便利であっても唯一のauthorityにはしない。

### 9.2 導かれるCandidate Requirement

- PIC-005 Source / Claim Separation
- PIC-011 Detail-on-demand
- PIC-019 Portable Export / Import
- PIC-022 Reversible Assistance

### 9.3 Acceptanceへどう降りるか

- Orientationからbasis/sourceへ降りられる
- summary生成前後でcanonical stateが変化しない
- provenance / timestamp / revisionを必要時に検査できる

## 10. Capability F — Independence and Handoff

### 10.1 なぜ必要か

Inquiryが一つのAI conversationより長く生きるなら、元conversationやproviderが失われても意味を残す必要がある。

### 10.2 導かれるCandidate Requirement

- PIC-014 Chat-independent Readability
- PIC-015 Portable AI Handoff Projection
- PIC-018 Local Standalone Read / Write
- PIC-019 Portable Export / Import
- PIC-020 Personal Retention Control
- PIC-023 No Mandatory Generative AI

### 10.3 Acceptanceへどう降りるか

- network / LLMなしでread / manual updateできる
- 元AI conversationなしでInquiryのsemantic rolesを別AIへ渡せる
- export/import後もDecision identity、basis、Unknown等が保たれる

## 11. Product Boundaryを根幹から導く

Source / Meaning / Resumeの三planeはarchitectureありきで決めたものではない。

Root Intentから考えると、SOZAが自ら保持すべきなのは「Inquiry continuityに必要な耐久的意味」であり、元資料そのものをすべて複製する必要はない。

そのため、first prototypeでは次を意図的に外す。

- full chat replacement
- generic document repository
- general-purpose PKM graph
- generic task manager
- semantic searchを中心価値とすること
- autonomous agent workflow

これらが必要になった場合も、まず「どのRoot Failureを防ぐためか」を明示し、既存Source Planeへ委ねられない理由を確認する。

## 12. Candidate Requirementを追加するときの判定順

新しいPICまたはStable Requirement候補を追加する前に、次を順番に確認する。

### Step 1 — Root Intent

Personal Inquiry Continuityのどの部分を守るのか。

説明できない場合はscope外の可能性がある。

### Step 2 — Failure

その要件が無いと具体的に何が壊れるのか。

「あると便利」だけでは足りない。

### Step 3 — Capability

既存A〜Fのどれで扱えるか。

扱えない場合、新Capabilityが本当に必要か、単なるRealization detailかを検討する。

### Step 4 — Existing SOZA Coverage

current Product Value、REQ、Contractですでに規範化されていないか確認する。

### Step 5 — Acceptance first

既存Requirementで意味が表現できるなら、新REQより先にAcceptance Scenarioで不足を表す。

### Step 6 — Stable Requirement

複数Profileでも独立して必要なnormative differenceが残る場合にだけ昇格を検討する。

## 13. Current Traceability Summary

| Root concern | Capability | Main PIC | Main validation |
|---|---|---|---|
| 当時の認識を壊さない | A | 005–009, 013, 021, 024 | late evidence / historical basis / Unknown |
| 記録負担で使われなくならない | B | 001, 003, 004, 016, 022, 025 | capture friction / correction trust |
| 中断後に検索語なしで戻る | C | 010, 011, 017 | queryless resume / first useful action |
| 前回からの変化を見つける | D | 012, 013, 021 | since-review delta / premise change |
| 圧縮表示から根拠へ戻る | E | 005, 011, 019, 022 | detail descent / projection non-authority |
| AI・環境が変わっても続ける | F | 014, 015, 018–020, 023 | offline / cross-AI handoff / migration |

この表はRequirement正本ではなく、導出関係を確認するための索引である。

## 14. Evidenceの順序

Capabilityがもっともらしいことと、Product Valueが成立したことを分ける。

```text
root hypothesis
  ↓
Design Evidence
  ↓
scoped executable mechanics
  ↓
real dogfood observation
  ↓
baseline comparison / falsification
  ↓
Adoption / Outcome signal
  ↓
formal Acceptance
  ↓
Stable Requirement reassessment
```

prototypeが動いたことを理由に、上位Product Hypothesisを確定しない。

## 15. 次に個別課題へ展開するときのテンプレート

今後Issueや設計文書を追加するとき、冒頭で最低限次を示す。

```text
Root intent:
  何を守るための課題か

Observed problem:
  何が壊れる / 何が過剰負担になるのか

Required capability:
  どの能力が必要か

Existing coverage:
  既存REQ / Contract / Profile candidateでどこまで足りるか

Gap:
  それでも残る最小の不足は何か

Validation:
  何を観測すれば必要性を反証できるか

Realization:
  最後に、実装候補を置く
```

この順序を守ることで、詳細設計が増えてもSOZAの根幹の趣旨から離れにくくする。