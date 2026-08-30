# SOZA Value Traceability

更新日: 2026-08-31  
状態: **Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Value、V1〜V8、current Product Requirements、Acceptance Scenarios、ADR、Issue、Evidence gapの関係を一覧化する追跡基線です。

目的は、対応数を増やすことではありません。Product Valueの意味が下位文書へどのように具体化され、どこがまだExecutable / Release / Operational Evidenceへ到達していないかを、後から確認できるようにすることです。

この文書でいう`Design coverage`は、Product / Requirement / ADR等に意味境界が定義されていることを示します。実装済み、test済み、release済み、productionで有効性が確認済みという意味ではありません。

## 2. Evidenceの高さ

Product Valueの追跡では、少なくとも次を分けます。

```text
Value Definition
  != Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
```

Design / Executable / Release / Operational Evidenceの受入れ規則は`SOZA_VALUE_ACCEPTANCE.md`を正とします。

さらに、実運用で期待した性質が成立したことと、製品の採用や意思決定・外部成果の改善を分けます。

```text
Operational Evidence != Adoption / Outcome Evidence
```

`Adoption / Outcome Evidence`はV1〜V8の追加軸ではありません。Product effectivenessを評価するための、より上位のEvidenceです。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なRequirement | 主なAcceptance Scenario | 主なADR | 現在の主なgap |
|---|---|---|---|---|
| V1 Historical Reconstruction | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016, 0017 | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0015, 0016, 0019 | historical reconstructionのactual fixture / operation |
| V2 Semantic Separation | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015 | ADR-0002, 0004, 0010, 0011, 0012, 0015, 0016, 0017, 0019 | end-to-end executable separation |
| V3 Revision Integrity | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016 | ADR-0003, 0007, 0008, 0009, 0010, 0015, 0019 | revision / supersession actual fixture |
| V4 Provider Independence | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014 | ADR-0004, 0006, 0007, 0012, 0013, 0014, 0016, 0019 | cross-provider executable / operational evidence |
| V5 Uncertainty Preservation | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016 | ADR-0002, 0005, 0006, 0010, 0012, 0016, 0019 | Unknown / Conflict / Withheld actual fixture |
| V6 Human / AI Readability | REQ-0010, 0011, 0015, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | ADR-0005, 0010, 0011, 0015, 0018, 0020 | representative human / AI readability acceptance |
| V7 Progressive Explicitness | REQ-0010 | SCN-0004, 0013 | ADR-0005, 0006, 0011, 0018, 0019, 0020 | lightweight / high-impact UX actual evidence |
| V8 Execution Independence | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015 | ADR-0001, 0007, 0012, 0013, 0014, 0016, 0019 | runtime / Provider replacement evidence |

この表はcurrent文書の主要な関係を示すものであり、すべての弱い関連を網羅することを目的にしません。

## 4. Product Requirementの現在地

current baselineでは、REQ-0001〜REQ-0022がAcceptedです。

Design Acceptanceは、多くが`Satisfied`であり、次は`Partially Satisfied`です。

- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0014 — 未解決残差と再開条件の保持
- REQ-0019 — 人間とAIの双方が意味を読める

この`Partially Satisfied`はRequirementが未確定という意味ではありません。Product / ADR層では意味が定まっている一方、Architecture等の具体化がまだ不足していることを表します。

current Requirements文書では、Executable / Release / Operational Acceptanceはactual Evidenceがない限り`Not Yet Verified`とされています。この境界を維持します。

## 5. Acceptance Scenarioの現在地

current baselineではSCN-0001〜SCN-0017が定義されています。

これらは、Product Valueの抽象原則を具体的な利用状況へ戻す主要なcurrent scenarioです。

特にProduct Value上重要な横断Scenarioとして、次を重視します。

- SCN-0001 — 根拠が割れている判断
- SCN-0003 — 新しいEvidenceでDecisionを見直す
- SCN-0004 — 軽量案件と高影響案件
- SCN-0009 — RecommendationからExecutionまでの責任線
- SCN-0010 — 可変Artifact更新後に過去Decisionを再構成する
- SCN-0011 — Providerが部分的にdegraded / 未観測である
- SCN-0012 — Provider内部をSelective Disclosureする
- SCN-0013 — 簡略UIとcanonical meaningを両立する
- SCN-0014 — Execution Providerを交換する
- SCN-0015 — PatternとCognitive Methodを分離する
- SCN-0017 — Design Evidenceしかない状態で達成主張を監査する

Scenarioの存在はExecutable Evidenceではありません。actual Test Case / Fixtureと再実行可能な検査が追加されて初めてExecutable Acceptanceを評価できます。

## 6. ADRのProduct Value上の役割

### ADR-0001〜ADR-0009

主に次を支えます。

- moving future horizon
- Observation / Interpretation境界
- Semantic Lineage
- bounded Responsibility
- Progressive Semantic Explicitness
- Federation / Selective Disclosure
- storage-neutral persistence
- Exact Binding / Representation Contract
- Verification Outcome分離

V1、V2、V3、V4、V5、V7、V8の基礎境界を形成します。

### ADR-0010〜ADR-0013

Decision MemoryとCapability Choiceの中核境界を形成します。

```text
Recommendation != Decision != Authority != Execution
Capability Definition != Observation != Matching != Decision
Capability != Provider
```

V1、V2、V3、V4、V5、V7、V8へまたがります。

### ADR-0014〜ADR-0017

次のProduct Boundaryを明示します。

- SOZA / TEIの独立Product Boundary
- Requirement InquiryとDecision Memory
- Authorization EvidenceをProviderへ残す境界
- Reference Model / Cognitive Methodの境界

### ADR-0018

Product Value governanceを定めます。

Product Valueを下位設計の正当化基準とし、既存実装を守るためだけに上位価値を変更しないこと、Product Value変更を明示的な再基線化として扱うことを定めます。

### ADR-0019

Provider-neutral Capability Observation境界を定めます。

Provider内部schemaをSOZA Coreへ複製せず、Observation、Unknown、Conflict、Withheld、Evidence、mapping provenance、historical bindingを扱います。

actual schema / fixtureはISSUE-000024で継続します。

### ADR-0020

Requirementsのstable identity、Value traceability、Requirement / Scenario / Test分離、Requirement statusとEvidence statusの分離を定めます。

current REQ / SCN baselineの統治基準です。

## 7. Product Valueとcurrent planning Issue

### ISSUE-000009 — Portable Exact Binding verification

historical / local stabilizationが存在しても、actual repository上の再実行可能なverifier Evidenceは別に必要です。

### ISSUE-000015 — Natural Japanese document audit

Product / Plan / Requirementsを含むactive文書を、`DOCUMENT_AUTHORING_STANDARD.md`に従って自然な日本語へ再監査します。

### ISSUE-000021 — Design history provenance

原文Evidenceが利用可能になるまでDeferredです。現在のProduct Decisionを止める理由にはしません。

### ISSUE-000022 — Repository baseline materialization

historical / local candidateとactual repositoryを分けながら、Architecture、Contracts、Fixtures、Runtime、Tools等を段階的に実体化します。

### ISSUE-000024 — Capability Observation schema / fixture

ADR-0019をactual schema / fixtureへ落とし、partial degradation、observation gap、historical reconstruction、Selective Disclosure、cross-provider comparison等を検査します。

### ISSUE-000026 — Current Requirements baseline

REQ / SCNのDesign baselineはactual repositoryへ実体化されています。Issue本文のCompletion / Executable Acceptance条件に従い、current statusをEvidence以上に引き上げません。

## 8. 現在比較的厚い領域

Design Evidenceとして比較的厚く整理されているのは次です。

- Historical Reconstruction
- Semantic Separation
- Revision Integrity
- Provider Independence
- Uncertainty Preservation
- Execution Independence

複数のRequirement、Scenario、ADRから同じ意味境界へ戻れます。

ただし、文書の数や相互参照の数をEvidence強度とみなしません。

## 9. 現在薄い領域

### Human / AI Readability

REQ-0019、V6、SCN-0006 / 0013等で意味は定義されていますが、利用者が実際に判断理由を無理なく追えることや、AIと人間が同じ意味を安定して読めることについて、Executable / Operational Evidenceが不足しています。

### Executable Evidence

Product / Plan / Requirementsはactual treeへ実体化されていますが、Architecture、Contracts、runtime、conformance toolのcurrent baselineはまだ十分ではありません。

Design Evidenceの充実をExecutable Evidenceへ読み替えません。

### Operational Evidence

actual production環境でSOZAの意味境界が維持されるEvidenceは、現時点では未取得または限定的です。

### Adoption / Outcome Evidence

「SOZAによって意思決定が改善した」「再審査やProvider交換が実務上有効だった」「組織へ継続採用された」といったProduct effectiveness Evidenceは、実際に得られるまで主張しません。

この不足は失敗ではなく、Evidence levelを正直に保った現在地です。

## 10. 追跡文書の更新規則

次の場合、この文書を更新します。

- Product Value / Value Model / Value Acceptanceが意味変更された。
- REQ / SCN baselineが変更された。
- ADRが新規Accepted、Superseded、Rejectedになった。
- Executable / Release / Operational Evidenceが新たに得られた。
- Adoption / Outcome Evidenceが得られた。
- active Issueや主要gapが変わった。

ただし、この文書を更新したこと自体をProduct Value coverageの向上とは数えません。

## 11. 関連文書

- `SOZA_PRODUCT_VALUE.md`
- `SOZA_VALUE_MODEL.md`
- `SOZA_VALUE_ACCEPTANCE.md`
- `../README.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/registry.yaml`
- `../../plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `../../plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`

## 12. 自然な日本語ドラフト

current Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0020、active Issueを本文へ戻して確認し、Evidenceの強度や未検証状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
