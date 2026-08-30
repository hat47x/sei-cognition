# SOZA Value Traceability

更新日: 2026-08-31  
状態: **Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Value、Value Model、Value Scenarioと、現在AcceptedになっているADRの関係を一覧化するための追跡基線です。

ADRの数や対応数をcoverage scoreとして使うことは目的ではありません。重要なのは、Product Valueのどの意味がどこで具体化され、どこがまだRequirements・Acceptance・実運用Evidenceへ降りていないかを明示することです。

この文書の`Covered`は「設計判断として扱われている」という意味であり、実装済み、検証済み、productionで価値実証済みという意味ではありません。

## 2. Value Model validation axisとADR

| Axis | 主に対応するADR | 現時点の判定 |
|---|---|---|
| V1 Historical Reconstruction | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0015, 0016, 0017, 0019 | 設計境界は厚い。actual repository / operational再構成は未実証 |
| V2 Semantic Separation | ADR-0002, 0004, 0010, 0011, 0012, 0015, 0016, 0017, 0019 | 中核境界は広くAccepted |
| V3 Revision Integrity | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0015, 0016, 0017, 0019 | semantic / representation / historical basisの分離がAccepted |
| V4 Provider Independence | ADR-0004, 0006, 0007, 0012, 0013, 0014, 0016, 0017, 0019 | TEIを含むProvider非特権化までAccepted |
| V5 Uncertainty Preservation | ADR-0002, 0005, 0006, 0010, 0012, 0016, 0019 | Unknown / Conflict / not observed境界はAccepted |
| V6 Human / AI Readability | ADR-0005, 0010, 0011, 0015, 0018 | 設計方針はあるが、利用者視点のAcceptanceとOutcome Evidenceが不足 |
| V7 Progressive Explicitness | ADR-0005, 0006, 0011, 0018 | Profile / PolicyとSelective Disclosureの境界はAccepted |
| V8 Execution Independence | ADR-0001, 0007, 0012, 0013, 0014, 0016, 0019 | 実行基盤・Providerからの独立境界はAccepted |
| V9 Evidence Calibration | ADR-0008, 0009, 0014, 0018, 0019 | claim境界はAccepted。actual repository / operational / outcome Evidenceは今後 |

## 3. Accepted ADRのProduct Value上の役割

### ADR-0001 — Moving Future Horizon

- 主に支える価値: V8 Execution Independence、Core最小化、将来耐性
- 主なValue Scenario: 12
- 意味: 現在の技術制約を恒久Coreへ固定しないための移動基準
- Evidence状態: 設計規律としてAccepted。将来環境での有効性は継続評価

### ADR-0002 — Claim / Interpretation Boundary

- 主に支える価値: V2 Semantic Separation、V5 Uncertainty Preservation
- 主なValue Scenario: 02, 03, 09
- 意味: Source assertion、Observation、Hypothesis、Method固有Artifactを一つのUniversal Claimへ潰さない
- Evidence状態: 設計境界としてAccepted

### ADR-0003 — Revision / Supersession Model

- 主に支える価値: V1 Historical Reconstruction、V3 Revision Integrity
- 主なValue Scenario: 04, 08, 12
- 意味: logical identity、exact binding、semantic lineage、storage revisionを分ける
- Evidence状態: 設計境界としてAccepted

### ADR-0004 — Bounded Subject / Responsibility

- 主に支える価値: V2 Semantic Separation、V4 Provider Independence
- 主なValue Scenario: 01, 07, 10
- 意味: ResponsibilityをGlobal Principal ontologyやAuthorityから分離する
- Evidence状態: 設計境界としてAccepted

### ADR-0005 — Progressive Semantic Explicitness

- 主に支える価値: V5 Uncertainty Preservation、V6 Human / AI Readability、V7 Progressive Explicitness
- 主なValue Scenario: 11
- 意味: 固定risk scoreやUniversal levelではなくProfile / Policyで必要な明示性を構成する
- Evidence状態: 設計境界としてAccepted。actual usabilityは未実証

### ADR-0006 — Federation / Selective Disclosure

- 主に支える価値: V4 Provider Independence、V5 Uncertainty Preservation、V7 Progressive Explicitness
- 主なValue Scenario: 10
- 意味: 全内部model共有を要求せず、非開示の存在とAuthority境界を保つ
- Evidence状態: 設計境界としてAccepted。cross-organization operational evidenceは未取得

### ADR-0007 — Semantic Persistence

- 主に支える価値: V1 Historical Reconstruction、V3 Revision Integrity、V4 Provider Independence、V8 Execution Independence
- 主なValue Scenario: 04, 08, 12
- 意味: storage方式から意味上の永続化契約を分ける
- Evidence状態: 設計境界としてAccepted。actual persistence implementationは別Evidence

### ADR-0008 — Exact Binding / Representation Contract

- 主に支える価値: V1 Historical Reconstruction、V3 Revision Integrity、V9 Evidence Calibration
- 主なValue Scenario: 04, 05, 09, 12, 13
- 意味: exact content bindingとrepresentation verification方式を分ける
- Evidence状態: 設計境界としてAccepted。portable verificationのactual実体はISSUE-000009 / 000022に依存

### ADR-0009 — Verification Outcome Separation

- 主に支える価値: V1 Historical Reconstruction、V3 Revision Integrity、V9 Evidence Calibration
- 主なValue Scenario: 08, 13
- 意味: verified / failed / not_verifiedをbinding identityやTruthと混同しない
- Evidence状態: 設計境界としてAccepted

### ADR-0010 — Decision Memory Minimum Boundary

- 主に支える価値: V1 Historical Reconstruction、V2 Semantic Separation、V5 Uncertainty Preservation
- 主なValue Scenario: 01, 02, 03, 04, 08
- 意味: Recommendation / Decision / Responsibility / Authority / Executionを分け、不確実性を含むDecisionを再構成する
- Evidence状態: 意味境界はAccepted。production Decision Memory実装を意味しない

### ADR-0011 — Decision Reference Roles

- 主に支える価値: V1 Historical Reconstruction、V2 Semantic Separation、V3 Revision Integrity、V7 Progressive Explicitness
- 主なValue Scenario: 01, 02, 03, 04, 08
- 意味: context / basis / recommendation / unresolvedの参照役割を分ける
- Evidence状態: 意味境界はAccepted。wire表現は未固定

### ADR-0012 — Capability Choice

- 主に支える価値: V2 Semantic Separation、V4 Provider Independence、V5 Uncertainty Preservation、V8 Execution Independence
- 主なValue Scenario: 05, 06, 07, 08
- 意味: Capability Definition / Observation / Matching / Recommendation / Decision / Authority / Executionを分ける
- Evidence状態: 意味境界はAccepted。actual choice runtimeを意味しない

### ADR-0013 — Capability Realization Boundary

- 主に支える価値: V4 Provider Independence、V8 Execution Independence
- 主なValue Scenario: 05, 12
- 意味: Provider固有Offering / Binding / DeploymentをUniversal Capability Realizationへ早期一般化しない
- Evidence状態: 非Core化DecisionとしてAccepted

### ADR-0014 — SOZA / TEI Product Boundary

- 主に支える価値: V4 Provider Independence、V8 Execution Independence、V9 Evidence Calibration
- 主なValue Scenario: 05, 06, 07, 12, 13
- 意味: SOZAの認知・意思決定境界とTEIの実行可能業務Capability実現境界を分ける
- Evidence状態: Product BoundaryとしてAccepted。双方のrelease / evidence claimを分離

### ADR-0015 — Requirement Inquiry / Decision Memory

- 主に支える価値: V1 Historical Reconstruction、V2 Semantic Separation、V3 Revision Integrity、V6 Human / AI Readability
- 主なValue Scenario: 04
- 意味: Question identity、表示文、AI回答候補、Decision、再審査を分ける
- Evidence状態: 意味境界としてAccepted。Authoring UXでの実証は未取得

### ADR-0016 — Authorization Evidence Provider Boundary

- 主に支える価値: V1 Historical Reconstruction、V2 Semantic Separation、V4 Provider Independence、V5 Uncertainty Preservation
- 主なValue Scenario: 07, 10
- 意味: Authorization engineをProviderへ残し、SOZAは必要なevaluation Evidenceを参照する
- Evidence状態: 意味境界としてAccepted。複数Provider actual evidenceは未取得

### ADR-0017 — Reference Model / Cognitive Method Boundary

- 主に支える価値: V1 Historical Reconstruction、V2 Semantic Separation、V4 Provider Independence
- 主なValue Scenario: 09
- 意味: domain-specific PatternとCognitive Methodを分け、Pattern match / Method ApplicationをDecision / Assuranceへ昇格させない
- Evidence状態: 設計境界としてAccepted

### ADR-0018 — Product Value Governance

- 主に支える価値: V1〜V9全体の統治境界
- 主なValue Scenario: 01〜13全体
- 意味: Product Valueの権威関係、価値衝突、Value Scenario、Evidence level、Core昇格、再基線化を規定する
- Evidence状態: normative governanceとしてAccepted

### ADR-0019 — Provider-neutral Capability Observation

- 主に支える価値: V1 Historical Reconstruction、V2 Semantic Separation、V3 Revision Integrity、V4 Provider Independence、V5 Uncertainty Preservation、V8 Execution Independence、V9 Evidence Calibration
- 主なValue Scenario: 05, 06, 10, 13
- 意味: Provider内部状態をSOZA Capability Observationへ直接同一化せず、adapter、Unknown / Conflict、Evidence、Selective Disclosure、exact referenceを扱う
- Evidence状態: 設計境界としてAccepted。actual contract / fixtureはISSUE-000025でBlocked

## 4. Value Scenarioと主要ADR

| Scenario | 主なADR | 現時点のgap |
|---|---|---|
| 01 AI提案を採らず別Decision | 0004, 0010, 0011, 0018 | actual human/AI authoring acceptance |
| 02 Unknownを残して判断 | 0002, 0005, 0010, 0011, 0018 | actual usability / policy acceptance |
| 03 Conflictを残して判断 | 0002, 0010, 0011, 0018 | Conflict lifecycleのactual acceptance |
| 04 Questionを新Evidenceで問い直す | 0003, 0010, 0011, 0015, 0018 | authoring client integration / operational use |
| 05 Provider交換 | 0012, 0013, 0014, 0019 | provider-neutral actual contract / multi-provider fixture |
| 06 Provider状態が不完全 | 0012, 0014, 0019 | ISSUE-000025 |
| 07 DecisionはあるがAuthorityなし | 0004, 0010, 0012, 0014, 0016 | provider authorization integration fixture |
| 08 実行成功と判断妥当性を分ける | 0009, 0010, 0012, 0014, 0018 | operational Decision review evidence |
| 09 Method / Patternを答えにしない | 0002, 0017, 0018 | cross-method actual use evidence |
| 10 Selective Disclosure | 0004, 0006, 0016, 0019 | cross-organization actual fixture / operation |
| 11 軽量利用から厳密化 | 0005, 0011, 0018 | Human / AI Readability、UX acceptance |
| 12 技術交換後も判断記憶を維持 | 0001, 0003, 0007, 0012, 0013, 0014, 0019 | long-horizon migration evidence |
| 13 設計・test成功と利用者価値を分ける | 0008, 0009, 0014, 0018, 0019 | operational / adoption / outcome evidence |

## 5. 現時点で厚い領域

設計判断として比較的厚く整理されているのは次である。

- Historical Reconstruction
- Semantic Separation
- Revision Integrity
- Provider Independence
- Uncertainty Preservation
- Execution Independence

これらは複数ADRから同じ境界へ戻れる。ただし、ADRが多いことを実証強度とみなさない。

## 6. 現時点で薄い領域

### Human / AI Readability

自然な日本語、Progressive Explicitness、Decision rationale等の設計方針はあるが、利用者が実際に意味を追えるか、AIと人間が同じDecision surfaceを扱えるかについてactual Acceptance / Outcome Evidenceが不足している。

ISSUE-000024でRequirement / Acceptanceへ展開する。

### Adoption / Outcome Evidence

現在はProduct Value、ADR、KJ、planningが中心であり、「SOZAにより実際の意思決定が改善した」「Provider交換や再審査が実運用で有効だった」といったEvidenceはまだ主張できない。

この不足は失敗ではなく、Evidence levelを正直に保った現在地である。

### Actual repository conformance

historical / local candidateとactual GitHub repositoryの実体が一致していない。ISSUE-000022で基線を実体化し、ISSUE-000009 / 000025等のactual conformanceへ接続する必要がある。

## 7. 次に優先する計画課題

1. **ISSUE-000024** — Value ScenarioをRequirement / NFR / Acceptanceへ展開し、V1〜V9の検証経路を明示する。
2. **ISSUE-000022** — actual repository baselineを実体化し、historical / local candidateとEvidence claimを分離する。
3. **ISSUE-000009** — portable exact binding verificationをactual repositoryで再検証可能にする。
4. **ISSUE-000025** — ADR-0019をprovider-neutral contract / fixtureへ具体化する。ISSUE-000022完了までactual実体化はBlocked。
5. **ISSUE-000015** — Requirements以降を含む自然な日本語監査を継続する。
6. **ISSUE-000021** — 7チャット原文Evidenceが取得可能になるまでDeferredを維持する。

この順序はProduct ontologyではない。現在のEvidence gapと上位文書整備の優先度から定めたplanning priorityである。

## 8. 追跡文書の更新規則

次の場合、この文書を更新する。

- Product Value / Value Model / Value Scenarioが意味変更された。
- ADRが新規Accepted、Superseded、Rejectedになった。
- Requirement / Acceptance基線がactual repositoryへ追加された。
- operational / adoption / outcome Evidenceが新たに得られた。
- 現在のgap判定が変わった。

ただし、文書を更新したこと自体をValue coverageの向上とは数えない。

## 9. 自然な日本語ドラフト

ADR-0001〜ADR-0019を本文へ戻して確認し、Value Model / Value Scenarioとの対応を整理した後、Evidenceの強度や未検証状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
