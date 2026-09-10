# Personal Inquiry Continuity — Requirement Gap Audit

更新日: 2026-09-10  
状態: **Candidate Requirement Gap Audit — Not Stable Requirement**  
関連: GitHub Issue #359 / `PRODUCT_PROFILE_REQUIREMENTS_CANDIDATE.md`

## 1. 目的

Personal Inquiry Continuity Profileの候補要件を、current SOZA Product Requirement（REQ-0001〜REQ-0022）と照合し、次を区別する。

```text
existing semantic requirement coverage
  != product-profile specialization
  != interaction / packaging acceptance
  != genuinely new stable requirement
```

個人向けprototypeで必要になったという理由だけでUniversal CoreやStable Requirementを増やさない。

## 2. 判定区分

- **Covered** — 既存REQの意味で本質的に包含される。新規REQ不要。
- **Profile specialization** — 既存REQを個人Profileで具体化する。Profile要件書またはAcceptanceで扱う。
- **Acceptance gap** — Requirementは既存で足りるが、個人利用のScenario / testが不足する。
- **Product-policy candidate** — semantic coreではなく、Product / Packaging / Privacy等の独立Requirement候補。
- **Potential stable gap** — current REQだけでは規範上の欠落があり得る。Evidenceを得て再審査する。

## 3. PICごとの監査

| PIC | 要旨 | 主な既存REQ | 判定 | 現時点の扱い |
|---|---|---|---|---|
| PIC-001 | 問いだけで開始 | REQ-0010 | Profile specialization | Progressive Explicitnessの個人UX具体化 |
| PIC-002 | DecisionなしでもInquiry継続 | REQ-0014, REQ-0002, REQ-0010 | Potential stable gap / mostly covered | 「Decision非必須」をAcceptanceで先に固定 |
| PIC-003 | 低摩擦capture | REQ-0010, REQ-0019 | Profile specialization | Profile要件として重要、Universal semantic要件にはしない |
| PIC-004 | provisional semantic extraction | REQ-0016, REQ-0020, REQ-0003 | Acceptance gap | AI抽出をTruth化しないnegative scenarioを追加候補 |
| PIC-005 | source / claim / interpretation分離 | REQ-0003, REQ-0016 | Covered | 新規REQ不要 |
| PIC-006 | Unknown / Conflict保持 | REQ-0002, REQ-0014 | Covered | 新規REQ不要 |
| PIC-007 | Recommendation / Decision分離 | REQ-0006, REQ-0013 | Covered | 新規REQ不要 |
| PIC-008 | lightweight Decision Memory | REQ-0005, REQ-0010, REQ-0014 | Profile specialization | 個人Profileのminimum projectionとして扱う |
| PIC-009 | historical basis非遡及 | REQ-0005, REQ-0009 | Covered | 既存Executable境界を個人fixtureへ展開 |
| PIC-010 | reorientation projection | REQ-0011, REQ-0014, REQ-0019 | Acceptance gap / Profile specialization | Profileの中核価値。独立Stable REQは保留 |
| PIC-011 | detail-on-demand | REQ-0010, REQ-0011, REQ-0019 | Covered | light / audit Acceptanceで扱う |
| PIC-012 | change-since-decision/review | REQ-0009, REQ-0014 | Acceptance gap | product interaction scenario追加候補 |
| PIC-013 | reopen without rewrite | REQ-0005, REQ-0009, REQ-0014 | Covered | 新規REQ不要 |
| PIC-014 | chat-independent readability | REQ-0001, REQ-0015, REQ-0019, REQ-0021 | Covered | 新規REQ不要 |
| PIC-015 | portable AI handoff projection | REQ-0001, REQ-0011, REQ-0019, REQ-0021 | Acceptance gap | Human/AI parityの実用Scenarioとして追加候補 |
| PIC-016 | bulk conversation / note intake | REQ-0003, REQ-0010, REQ-0016 | Profile specialization | Integration/Interactionのprofile機能。semantic core化しない |
| PIC-017 | Inquiry discovery / resume | REQ-0019 + Product Interaction | Product-policy candidate | semantic identityではなくProduct navigation requirement |
| PIC-018 | local standalone read/write | REQ-0018, REQ-0021 + Packaging | Product-policy candidate | Personal Profile packaging requirement |
| PIC-019 | portable export/import | REQ-0001, REQ-0018, REQ-0021 | Acceptance gap / Profile specialization | concrete export/import acceptanceが必要 |
| PIC-020 | personal retention control | current stable REQに直接対応なし | Potential stable gap | privacy/product data agencyとして別審査 |
| PIC-021 | capture time / subject time分離 | REQ-0003, REQ-0005, REQ-0009 | Acceptance gap | backfill/import scenarioが不足 |
| PIC-022 | reversible AI assistance | REQ-0011, REQ-0016, REQ-0020 | Acceptance gap | summary/classificationのnegative caseが必要 |
| PIC-023 | generative AI非必須 | REQ-0001, REQ-0015, REQ-0021 | Covered | Personal Profileでexplicit acceptanceを追加 |
| PIC-024 | composite truth/confidenceへ潰さない | REQ-0002, REQ-0006 | Covered | sparse/LLM ranking境界のAcceptanceを追加可能 |
| PIC-025 | impactに応じた明示深度 | REQ-0010, REQ-0013 | Covered / Profile specialization | high-stakes policyはlater |

## 4. 現時点で新しいStable Requirementを増やさない理由

Personal Profileの中核mechanicsは、current Requirementの組合せでかなり強く説明できる。

### Historical continuity

REQ-0001 / 0005 / 0009 / 0014 / 0018 / 0021により、過去状態を現在知識で上書きせず、後から再読・再開する基盤は既に存在する。

### Semantic distinction

REQ-0002 / 0003 / 0006 / 0016により、Unknown、Conflict、source、Interpretation、Recommendation、Decision等を平坦化しない境界は既に存在する。

### Human / AI usability

REQ-0010 / 0011 / 0015 / 0019により、Progressive Explicitness、Projection非権威、private chain-of-thought非依存、人間/AI readabilityは既に要求される。

したがって、Personal Profileで必要になった具体操作やProjectionを、それだけで新しいUniversal semantic requirementへ昇格させる根拠はまだない。

## 5. ただしProduct Profile文書は独立させる価値がある

Stable Requirementが既存で足りることと、個人向け製品要件書が不要であることは同じではない。

current `PRODUCT_REQUIREMENTS.md` はSOZA全体が守るsemantic / interoperability requirementを中心にしており、次のようなProfile固有の組合せは一箇所にまとまっていない。

- 問い一つから開始する。
- Decisionを要求しない。
- free-form captureを許す。
- light reorientationを最初の出口とする。
- local single-userで成立する。
- chat transcript importを扱う。
- AI handoffを生成する。
- Inquiryを一覧・検索して再開する。
- user-owned dataをexport / deleteする。

これらはUniversal ontologyではないが、**一つの配布可能なProduct Profileが成立する条件**としては規範化する価値がある。

そのため最終形の第一候補を次とする。

```text
requirements/
  PRODUCT_REQUIREMENTS.md               # current stable cross-product requirements
  ACCEPTANCE_SCENARIOS.md
  profiles/
    PERSONAL_INQUIRY_CONTINUITY.md       # personal product profile requirements
```

Profile文書はStable REQを再定義しない。既存REQを参照しながら、Profile固有のMUST / SHOULD、supported surface、non-goals、acceptanceを正本化する。

## 6. Product Profile RequirementとUniversal Requirementの権威関係

提案する権威関係は次の通り。

```text
SOZA Product Value
  → Stable Product Requirements (REQ-*)
  → Product Profile Requirements
  → Profile Acceptance Scenarios / Tests
  → Packaging / Interaction Realization
```

Product ProfileはStable Requirementに反してはならない。

Profileの都合だけでUniversal meaningを変更しない。

一方、Profileで繰り返し必要となり、他Profileでも独立して必要だとEvidenceが得られた意味差は、Issue / ADRを通してStable Requirementへ昇格できる。

## 7. Formalization Candidate A — Profile-only Requirement

現時点で、次は `PERSONAL_INQUIRY_CONTINUITY.md` のProfile MUSTとして固定する候補が強い。

1. Inquiryを一つの問いだけから開始できる。
2. Decisionなしでも保存・再開できる。
3. natural/free-form captureを入口にできる。
4. Unknown / Conflictを残せる。
5. RecommendationとDecisionを区別する。
6. Decision historical basisを非遡及で保持する。
7. reorientation projectionから現在地へ戻れる。
8. detailへ降りられる。
9. external LLMなしでもread/write/reviewできる。
10. local single-userで起動・保存・再開できる。
11. portable export/importができる。
12. 複数Inquiryから対象を発見・再開できる。

これらの多くは既存Stable REQをProfileへ束ねたものになる。

## 8. Formalization Candidate B — Profile SHOULD

次はProfile価値を高めるが、first executable sliceを阻害するならMUSTにしない。

1. bulk chat / note intake
2. AI semantic candidate extraction
3. AI handoff Projection
4. change-since-last-review表示
5. explicit local data deletion UI
6. human-readable export
7. automated reopen cue

## 9. Potential Stable Gap 1 — Inquiry can remain open without Decision

### 問い

current SOZA文書はInquiry、Unknown、residual、reopenを扱うため、意味上はDecision非必須と読める。

しかしStable Requirement一覧には、

> 「Inquiryの成立・保存・再開はDecisionの存在を要求してはならない」

というnegative requirementが明示されていない。

### リスク

将来のProduct InteractionがDecision-centricに実装され、`complete = decision exists` のworkflowへ収束する可能性がある。

### 現時点の判断

**すぐ新REQにはしない。**

まずPersonal Profile Acceptanceで次を固定する。

- Observation + UnknownだけのInquiryを保存できる。
- Recommendationまで存在しDecisionなしでも再開できる。
- UI / runtimeがDecision欠如をinvalid stateとして拒否しない。

他のProfileやdomainでも同じnegative boundaryが必要と確認できた場合、Stable Requirement昇格を再検討する。

## 10. Potential Stable Gap 2 — Personal Retention / Data Agency

### 問い

current SOZAはsemantic historyを消さずに保持することを重視するが、個人Productとしては利用者自身が保存データを削除できる必要性がある。

これはsemantic supersessionとは異なるProduct data lifecycle問題である。

### リスク

「historical integrity」を誤って「利用者が自分のデータを削除できない」と解釈すると、個人製品として不適切になる。

### 現時点の判断

**独立したProduct / Privacy Requirement候補として残す。**

ただしPersonal ProfileだけでStable化せず、Product Security / Privacy / Backup / shared-data semanticsと合わせて設計する。

候補表現:

> SOZAは、semantic historyをsurviving record内で黙って改変しないことと、権限ある利用者がProduct dataを明示的に削除・保持管理することを区別しなければならない。

## 11. Potential Stable Gap 3 — Explicit AI-generated semantic suggestion boundary

current REQ-0016はObservation / Interpretation区別、REQ-0020はEvidenceを超える達成主張を抑える。

しかし、AIが大量のraw conversationを自動構造化する製品では、

```text
AI extracted candidate
  != source statement
  != user-confirmed meaning
  != Decision
```

をInteraction / data representation上で明確にする必要が高まる可能性がある。

現時点ではRealization-dependentなdraft stateで表現可能なため、Universal Contract追加は避ける。

prototypeで誤分類修正やbulk importをdogfoodし、candidate stateがdurable semantic requirementか単なるUI draftかを見極める。

## 12. Acceptance Scenarioとして追加する方がよいもの

新REQよりScenarioの追加候補が強いものを整理する。

### PAS-C01 — Open Inquiry without Decision

ObservationとUnknownだけを記録したInquiryを閉じ、後日再開する。Decision欠如をinvalidにしない。

### PAS-C02 — Resume without Original Chat

元AI conversationを利用不能にした状態で、保存済みSOZA dataだけからcurrent orientationを再構成する。

### PAS-C03 — Bulk Chat Import with Correction

chat transcriptを取り込み、AIがsemantic candidatesを抽出する。一つを意図的に誤分類し、利用者が訂正してもraw source provenanceが保たれる。

### PAS-C04 — New Evidence after Decision

Decision後にEvidenceを追加し、historical basisを変えずに`new since decision`として再開する。

### PAS-C05 — AI Provider Handoff

Provider Aの会話を失った状態で、canonical SOZA contextからhandoff Projectionを生成し、Provider Bまたは別toolがInquiryの意味差を読める。

### PAS-C06 — Offline Personal Continuity

network / LLMなしで既存Inquiryを開き、Unknownを追加し、Decisionを記録し、process再起動後に再読する。

### PAS-C07 — Portable Migration

local dataをexportし、別data rootまたはclean instanceへimportして、Decision identity / basis / unresolvedを保持する。

### PAS-C08 — Backfilled Historical Material

過去の日付のchat / noteを後日importする。capture timeとsubject timeを混同せず、過去Decision作成時に未取得だったmaterialをbasisへ遡及させない。

## 13. `PRODUCT_REQUIREMENTS.md`へ将来反映する場合の候補差分

現時点では次の二方向だけを候補とし、まだ変更しない。

### Option 1 — 新REQなし

- current REQ-0001〜0022を維持
- `requirements/profiles/PERSONAL_INQUIRY_CONTINUITY.md` を追加
- PAS-C01〜C08相当をProfile内Acceptanceとして管理

**現時点の第一候補。**

### Option 2 — 少数のStable REQ追加

実証後、cross-profileな独立必要性が確認できた場合のみ、たとえば次を検討する。

- `Inquiry lifecycle must not require Decision` boundary
- Product data retention / deletion agency
- automated semantic extraction candidate boundary

この場合もPIC-001〜025をそのままREQへコピーしない。

## 14. 結論

現時点の監査結果は次の通り。

```text
Personal Inquiry Continuity profile is product-distinct
  + current stable SOZA semantics cover most durable meaning
  + several new acceptance scenarios are justified
  + profile-specific operational requirements are needed

but

profile usability requirement
  != automatically new Universal semantic requirement
```

したがって次の設計段階では、個人向け要件を**Product Profile正本として独立させる構造**を第一候補にし、Stable Requirement追加はEvidenceに基づき少数へ限定する。
