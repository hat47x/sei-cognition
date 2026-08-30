# SOZA Value Traceability

更新日: 2026-08-31  
状態: **Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Value、Value Model、Value Acceptance、Value Scenarioと、現在のADR・Issue・Evidence gapの関係を一覧化するための追跡基線です。

ADRの数、Requirement数、対応表の埋まり具合をcoverage scoreとして使うことは目的ではありません。

重要なのは、Product Valueのどの意味がどこで具体化され、どこがまだRequirements、Executable Evidence、Operational Evidence、Adoption / Outcome Evidenceへ降りていないかを明示することです。

この文書の`Design coverage`は「設計判断として扱われている」という意味であり、実装済み、test済み、release済み、productionで価値実証済みという意味ではありません。

## 2. Evidenceの高さ

本書では、少なくとも次を分けます。

```text
Value Definition
  != Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Design / Executable / Release / Operational Evidenceの受入れ規則は`SOZA_VALUE_ACCEPTANCE.md`を正とします。

`Adoption / Outcome Evidence`はV1〜V8の新しいValue Axisではありません。SOZAが実際に採用され、利用者・組織の意思決定や外部成果へ望ましい変化をもたらしたかを評価する、より上位のProduct effectiveness上のEvidenceです。

## 3. Value Model validation axisと現在の設計coverage

| Axis | 主に対応するADR | Design coverage | 主な未検証領域 |
|---|---|---|---|
| V1 Historical Reconstruction | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0015, 0016, 0019 | 厚い | actual historical reconstruction fixture / operation |
| V2 Semantic Separation | ADR-0002, 0004, 0010, 0011, 0012, 0015, 0016, 0017, 0019 | 厚い | end-to-end executable separation |
| V3 Revision Integrity | ADR-0003, 0007, 0008, 0009, 0010, 0015, 0019 | 厚い | current Requirements / runtimeでのrevision fixture |
| V4 Provider Independence | ADR-0004, 0006, 0007, 0012, 0013, 0014, 0016, 0019 | 厚い | cross-provider executable / operational evidence |
| V5 Uncertainty Preservation | ADR-0002, 0005, 0006, 0010, 0012, 0016, 0019 | 厚い | actual Unknown / Conflict / Withheld fixture |
| V6 Human / AI Readability | ADR-0005, 0010, 0011, 0015, 0018, 0020 | 中程度 | representative human / AI readability acceptance |
| V7 Progressive Explicitness | ADR-0005, 0006, 0011, 0018, 0019, 0020 | 厚い | lightweight / high-impact UX actual evidence |
| V8 Execution Independence | ADR-0001, 0007, 0012, 0013, 0014, 0016, 0019 | 厚い | provider / runtime replacement executable evidence |

`厚い`や`中程度`は設計文書の所在を説明するための定性的な表現です。Product Valueの達成度scoreではありません。

## 4. Accepted ADRのProduct Value上の役割

### ADR-0001 — Moving Future Horizon

- 主なAxis: V8
- 主なValue Scenario: 12
- 役割: 現在の技術制約を恒久Coreへ固定しないための移動基準
- Evidence: Design Decision Accepted

### ADR-0002 — Claim / Interpretation Boundary

- 主なAxis: V2, V5
- 主なValue Scenario: 02, 03, 09
- 役割: Source assertion、Observation、Hypothesis、Method固有Artifactを一つのUniversal Claimへ潰さない
- Evidence: Design Decision Accepted

### ADR-0003 — Revision / Supersession Model

- 主なAxis: V1, V3
- 主なValue Scenario: 04, 08, 12
- 役割: logical identity、exact binding、semantic lineage、storage revisionを分ける
- Evidence: Design Decision Accepted

### ADR-0004 — Bounded Subject / Responsibility

- 主なAxis: V2, V4
- 主なValue Scenario: 01, 07, 10
- 役割: ResponsibilityをGlobal Principal ontologyやAuthorityから分離する
- Evidence: Design Decision Accepted

### ADR-0005 — Progressive Semantic Explicitness

- 主なAxis: V5, V6, V7
- 主なValue Scenario: 02, 11
- 役割: 固定risk scoreではなくProfile / Policyで必要な明示性を構成する
- Evidence: Design Decision Accepted。actual usabilityは未実証

### ADR-0006 — Federation / Selective Disclosure

- 主なAxis: V4, V5, V7
- 主なValue Scenario: 10
- 役割: 全内部model共有を要求せず、非開示の存在とAuthority境界を保つ
- Evidence: Design Decision Accepted。cross-organization operational evidenceは未取得

### ADR-0007 — Semantic Persistence

- 主なAxis: V1, V3, V4, V8
- 主なValue Scenario: 04, 08, 12
- 役割: storage方式から意味上の永続化契約を分ける
- Evidence: Design Decision Accepted。actual persistence conformanceは未実証

### ADR-0008 — Exact Binding / Representation Contract

- 主なAxis: V1, V3
- 主なValue Scenario: 04, 05, 09, 12, 13
- 役割: exact content bindingとrepresentation verification方式を分ける
- Evidence: Design Decision Accepted。actual verifierはISSUE-000009 / 000022に依存

### ADR-0009 — Verification Outcome Separation

- 主なAxis: V1, V3
- 主なValue Scenario: 08, 13
- 役割: verified / failed / not_verifiedをbinding identityやTruthと混同しない
- Evidence: Design Decision Accepted

### ADR-0010 — Decision Memory Minimum Boundary

- 主なAxis: V1, V2, V5
- 主なValue Scenario: 01, 02, 03, 04, 08
- 役割: Recommendation / Decision / Responsibility / Authority / Executionを分け、不確実性を含むDecisionを再構成する
- Evidence: Design Decision Accepted。production Decision Memory実装を意味しない

### ADR-0011 — Decision Reference Roles

- 主なAxis: V1, V2, V3, V7
- 主なValue Scenario: 01, 02, 03, 04, 08
- 役割: context / basis / recommendation / unresolvedの参照役割を分ける
- Evidence: Design Decision Accepted。representation shapeは未固定

### ADR-0012 — Capability Choice

- 主なAxis: V2, V4, V5, V8
- 主なValue Scenario: 05, 06, 07, 08
- 役割: Capability Definition / Observation / Matching / Recommendation / Decision / Authority / Executionを分ける
- Evidence: Design Decision Accepted

### ADR-0013 — Capability Realization Boundary

- 主なAxis: V4, V8
- 主なValue Scenario: 05, 12
- 役割: Provider固有Offering / Binding / DeploymentをUniversal Capability Realizationへ早期一般化しない
- Evidence: Non-Core Decision Accepted

### ADR-0014 — SOZA / TEI Product Boundary

- 主なAxis: V4, V8
- 主なValue Scenario: 05, 06, 07, 12, 13
- 役割: SOZAの認知・意思決定境界とTEIの実行可能業務Capability実現境界を分ける
- Evidence: Product Boundary Accepted。双方のrelease / evidence claimを分離

### ADR-0015 — Requirement Inquiry / Decision Memory

- 主なAxis: V1, V2, V3, V6
- 主なValue Scenario: 04
- 役割: Question identity、表示文、AI回答候補、Decision、再審査を分ける
- Evidence: Design Decision Accepted。Authoring UXでの実証は未取得

### ADR-0016 — Authorization Evidence Provider Boundary

- 主なAxis: V1, V2, V4, V5
- 主なValue Scenario: 07, 10
- 役割: Authorization engineをProviderへ残し、SOZAは必要なevaluation Evidenceを参照する
- Evidence: Design Decision Accepted。複数Provider actual evidenceは未取得

### ADR-0017 — Reference Model / Cognitive Method Boundary

- 主なAxis: V1, V2, V4
- 主なValue Scenario: 09
- 役割: domain-specific PatternとCognitive Methodを分け、Pattern match / Method ApplicationをDecision / Assuranceへ昇格させない
- Evidence: Design Decision Accepted

### ADR-0018 — Product Value Governance

- 主なAxis: V1〜V8全体
- 主なValue Scenario: 01〜13全体
- 役割: Product Valueの権威関係、価値衝突、Core昇格、再基線化、Evidence境界を統治する
- Evidence: Normative governance Accepted

### ADR-0019 — Provider-neutral Capability Observation

- 主なAxis: V1, V2, V3, V4, V5, V7, V8
- 主なValue Scenario: 05, 06, 10, 13
- 役割: Provider内部状態をCapability Observationへ直接同一化せず、adapter、Unknown / Conflict / Withheld、provenance、historical bindingを扱う
- Evidence: Design Decision Accepted。actual schema / fixtureはISSUE-000024

### ADR-0020 — Requirements Traceability / Evidence Boundary

- 主なAxis: V1〜V8全体をRequirementsへ追跡する統治境界
- 主なValue Scenario: 01〜13全体
- 役割: REQ / SCNのstable identity、Requirement / Scenario / Test分離、Value traceability、Requirement statusとEvidence statusの分離を定める
- Evidence: Requirements governance Accepted。current requirements materializationはISSUE-000026

## 5. Value Scenarioと主要ADR / Issue

| Scenario | 主なADR | 主なcurrent Issue / gap |
|---|---|---|
| 01 AI提案を採らず別Decision | 0004, 0010, 0011, 0018, 0020 | ISSUE-000026でREQ / SCNへ展開 |
| 02 Unknownを残して判断 | 0002, 0005, 0010, 0011, 0018 | actual uncertainty fixture |
| 03 Conflictを残して判断 | 0002, 0010, 0011, 0018 | Conflict lifecycle actual evidence |
| 04 Questionを新Evidenceで問い直す | 0003, 0010, 0011, 0015, 0018 | Authoring integration / operation |
| 05 Provider交換 | 0012, 0013, 0014, 0019 | ISSUE-000024 cross-provider fixture |
| 06 Provider状態が不完全 | 0012, 0014, 0019 | ISSUE-000024 |
| 07 DecisionはあるがAuthorityなし | 0004, 0010, 0012, 0014, 0016 | provider authorization fixture |
| 08 実行成功と判断妥当性を分ける | 0009, 0010, 0012, 0014, 0018 | operational Decision review evidence |
| 09 Method / Patternを答えにしない | 0002, 0017, 0018 | cross-method actual use evidence |
| 10 Selective Disclosure | 0004, 0006, 0016, 0019 | ISSUE-000024 / cross-organization operation |
| 11 軽量利用から厳密化 | 0005, 0011, 0018 | V6 / V7 actual usability acceptance |
| 12 技術交換後も判断記憶を維持 | 0001, 0003, 0007, 0012, 0013, 0014, 0019 | migration / replacement evidence |
| 13 Evidenceの高さを混同しない | 0008, 0009, 0014, 0018, 0020 | operational / adoption / outcome evidence |

## 6. 現在のactive planning gap

### ISSUE-000009 — Portable Exact Binding verification

historical / local stabilizationが存在しても、actual repository上の再実行可能なverifier Evidenceは別に必要です。

### ISSUE-000015 — Natural Japanese document audit

Product / Plan文書の自然な日本語監査を継続します。Requirements、Architecture、Contractsをactual treeへ実体化するときも同じ工程を適用します。

### ISSUE-000021 — Design history provenance

原文Evidenceが利用可能になるまでDeferredです。現在のProduct Decisionを止める理由にはしません。

### ISSUE-000022 — Repository baseline materialization

historical / local candidateとactual repositoryを分けながら、Requirements、Contracts、Fixtures、Runtime、Tools等を段階的に実体化します。

### ISSUE-000024 — Capability Observation schema / fixture

ADR-0019のProvider-neutral境界をactual schema / fixtureへ落とします。F1〜F7のScenarioでV1〜V8を検証します。

### ISSUE-000026 — Current Requirements baseline

ADR-0020に従って、current Product RequirementsとAcceptance Scenariosをactual `requirements/`へ実体化します。

旧件数・旧ID・旧Evidence状態を保存することは目的にしません。

## 7. 現在比較的厚い領域

Design Evidenceとして比較的厚く整理されているのは次です。

- Historical Reconstruction
- Semantic Separation
- Revision Integrity
- Provider Independence
- Uncertainty Preservation
- Execution Independence

複数ADRから同じ意味境界へ戻れます。ただし、ADRが多いことをEvidence強度とみなしません。

## 8. 現在薄い領域

### Human / AI Readability

自然な日本語、Progressive Explicitness、Decision rationale等の設計方針はありますが、利用者が実際に意味を追えるか、AIと人間が同じDecision surfaceを扱えるかについてactual Acceptance / Operational Evidenceが不足しています。

### Executable Evidence

Product / Plan文書はactual treeへ実体化されていますが、Requirements、Capability Observation schema / fixture、runtime、conformance tool等は進行中です。

Design Evidenceの充実をExecutable Evidenceへ読み替えません。

### Operational Evidence

actual production環境でSOZAの意味境界が維持されるEvidenceは、現時点では限定的または未取得です。

### Adoption / Outcome Evidence

「SOZAによって意思決定が改善した」「再審査やProvider交換が実務上有効だった」「組織に継続採用された」といったProduct effectiveness Evidenceは、実際に得られるまで主張しません。

この不足は失敗ではなく、Evidence levelを正直に保った現在地です。

## 9. 追跡文書の更新規則

次の場合、この文書を更新します。

- Product Value / Value Model / Value Acceptance / Value Scenarioが意味変更された。
- ADRが新規Accepted、Superseded、Rejectedになった。
- current Requirement / SCN baselineがactual repositoryへ追加・変更された。
- Executable / Release / Operational Evidenceが新たに得られた。
- Adoption / Outcome Evidenceが得られた。
- 現在のgap判定が変わった。

ただし、文書を更新したこと自体をValue coverageの向上とは数えません。

## 10. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- `product/README.md`
- `plan/registry.yaml`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`

## 11. 自然な日本語ドラフト

ADR-0001〜ADR-0020、active Issue、Value Model、Value Acceptance、Value Scenarioを本文へ戻して確認し、Evidenceの強度や未検証状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
