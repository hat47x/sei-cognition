# Historical Requirement Mapping

更新日: 2026-08-31  
状態: **Historical Provenance Mapping**

## 1. この文書の役割

この文書は、2026-08-30前後のSOZA Phase 0 / Phase 1 candidateで使われていた`SOZA-PR-*`、`SOZA-NFR-*`、`SOZA-AS-*`と、現在の`REQ-*` / `SCN-*`の関係を記録します。

historical IDをcurrent IDへ機械的にrenameしたものではありません。

current baselineは、Product Value、Value Model、Value Acceptance、Accepted ADRへ戻って意味核を再構成しています。そのため、一つの旧Requirementが複数のcurrent Requirementへ分かれる場合も、複数の旧Requirement / NFRが一つのcurrent Requirementへ統合される場合もあります。

## 2. 継承しないもの

historical candidateから、次をcurrent baselineへ自動継承しません。

- `direct` / `partial` / `design_only`等のlocal evidence state
- `VERIFIED`、planning PASS、local conformance PASS
- M48 / M49 / M50等のMilestone上の位置づけ
- old repository treeの存在を前提としたExecutable Evidence claim
- 旧Product Boundaryに依存する型・Architecture

historical evidenceは再検証候補として保持しますが、current actual repositoryで確認できるまでExecutable Acceptance以上へ昇格させません。

## 3. Historical Product Requirement mapping

| Historical ID | Historical meaning | Current mapping | 処理 |
|---|---|---|---|
| SOZA-PR-001 | 意味の連続性 | REQ-0001, REQ-0018, REQ-0021 | 意味連続性をStorage / Realization交換と分けて精緻化 |
| SOZA-PR-002 | 認識状態の明示 | REQ-0002 | 継承・精緻化 |
| SOZA-PR-003 | 出所・発見経路・派生の分離 | REQ-0003 | 継承・精緻化 |
| SOZA-PR-004 | Cognitive Methodの独立性 | REQ-0004, REQ-0021 | Method意味とRealization交換を分離 |
| SOZA-PR-005 | 判断理由の再構成 | REQ-0005 | Decision Memory ADR群を反映して精緻化 |
| SOZA-PR-006 | DecisionとAuthorityの分離 | REQ-0006, REQ-0013, REQ-0017 | semantic separation、kind推定禁止、Responsibilityへ分解 |
| SOZA-PR-007 | Capabilityの中立性 | REQ-0007, REQ-0022 | Capability / Provider中立性とObservation境界へ分離 |
| SOZA-PR-008 | 経路の保存 | REQ-0008 | Responsibility / Decision routeを明確化 |
| SOZA-PR-009 | Revision / Supersession | REQ-0009 | Exact Binding / Verification Outcome境界も反映 |
| SOZA-PR-010 | 必要な意味境界の段階化 | REQ-0010 | Progressive Semantic Explicitnessとして継承 |
| SOZA-PR-011 | Projection非権威 | REQ-0011 | 継承。current Architecture未実体化のためDesignはPartial |
| SOZA-PR-012 | Bounded Principal / Selective Disclosure | REQ-0012, REQ-0022 | federationとProvider ObservationのSelective Disclosureへ展開 |
| SOZA-PR-013 | Actor種別からの権限推定禁止 | REQ-0013 | 継承・精緻化 |
| SOZA-PR-014 | 残差の外在化 | REQ-0014 | Decision後のreopen conditionまで明示 |
| SOZA-PR-015 | private chain-of-thought非依存 | REQ-0015 | 継承・精緻化 |
| SOZA-PR-016 | Claim / Interpretation境界の検証可能性 | REQ-0016 | Universal Claim型を要求せず、Observation / Interpretation再構成可能性へ整理 |
| SOZA-PR-017 | Responsibilityの文脈性 | REQ-0017 | 継承・精緻化 |
| SOZA-PR-018 | Storage実装からの意味独立 | REQ-0018, REQ-0021 | Storage independenceと広いRealization交換を分離 |

## 4. Historical NFR mapping

旧NFRはcurrent baselineで別namespaceを維持せず、Product Requirementのtype metadataへ統合しました。

| Historical ID | Historical meaning | Current mapping | 処理 |
|---|---|---|---|
| SOZA-NFR-001 | Human-readable | REQ-0019 | Human / AI Readabilityへ拡張 |
| SOZA-NFR-002 | Model-neutral | REQ-0001, REQ-0021 | semantic continuity / replaceable realizationへ統合 |
| SOZA-NFR-003 | Provider-neutral | REQ-0007, REQ-0022 | Capability / Provider neutralityとObservationへ統合 |
| SOZA-NFR-004 | Partial Knowledge Tolerance | REQ-0002, REQ-0014 | uncertainty preservationとresidualへ統合 |
| SOZA-NFR-005 | Selective Disclosure Readiness | REQ-0012, REQ-0022 | collaboration / Provider Observationへ統合 |
| SOZA-NFR-006 | Local Complexity | REQ-0010 | Progressive Semantic Explicitnessへ統合 |
| SOZA-NFR-007 | Schema Evolution | REQ-0009, REQ-0018 | semantic revision / storage independenceへ統合 |
| SOZA-NFR-008 | Evidence-based Release Claims | REQ-0020 | Value AcceptanceのEvidence階層へ合わせて拡張 |
| SOZA-NFR-009 | Moving Future Horizon | Product Principle / ADR-0001 | Requirementではなく設計評価規則として上位へ配置 |
| SOZA-NFR-010 | Replaceable Realization | REQ-0021, REQ-0007 | Realization / Provider交換要求へ統合 |

### SOZA-NFR-009をcurrent REQにしない理由

10〜50倍程度先を見るMoving Future Horizonは、利用者世界の機能・意味要求というより、Core候補やArchitectureを評価するときの**設計上の移動基準**です。

そのためcurrent baselineではRequirementへ無理に残さず、`ADR-0001`、Product Value / Vision / Principles側で管理します。

この配置により、将来倍率をProduct機能やperformance targetと誤読しにくくします。

## 5. Historical Acceptance Scenario mapping

| Historical ID | Current ID | 主な変更 |
|---|---|---|
| SOZA-AS-001 | SCN-0001 | Conflict / Unknown / residual / reopenをcurrent Decision Memoryへ照合 |
| SOZA-AS-002 | SCN-0002 | Capability Definition / Observation / Provider / Choice境界を追加 |
| SOZA-AS-003 | SCN-0003 | Exact historical reconstructionとDecision revisionを精緻化 |
| SOZA-AS-004 | SCN-0004 | Progressive Explicitnessとcanonical meaning保持を明確化 |
| SOZA-AS-005 | SCN-0005 | Pattern / Method、Method Application / Assurance境界を反映 |
| SOZA-AS-006 | SCN-0006 | Human / AI ReadabilityとProjection non-authorityを反映 |
| SOZA-AS-007 | SCN-0007 | Withheld contextとAuthority分離を反映 |
| SOZA-AS-008 | SCN-0008 | Exact Binding / semantic revision / Storage independenceを精緻化 |

current baselineでは、後発ADRとValue Acceptanceに必要な意味差を検証するため、SCN-0009〜SCN-0017を追加しています。

## 6. 新しく独立したcurrent Requirement

historical 18 Product Requirements / 10 NFRに一対一対応しないcurrent Requirementとして、特に次を独立させました。

### REQ-0019 — 人間とAIの双方が意味を読める

旧Human-readableを、人間だけの可読性ではなく、human-readable Projectionとmachine-readable structureが同じcanonical meaningへ戻れる要求へ拡張しました。

### REQ-0020 — Evidenceを超える達成主張をしない

旧NFR-008を、Design / Executable / Release / Operational Evidenceの明示的な階層へ拡張しました。current repository実体とhistorical candidate evidenceを混同しないための開発上のProduct Requirementでもあります。

### REQ-0022 — Provider-neutralなCapability Observation

ADR-0019で新たに確定した境界です。historical PR-007 / NFR-003にも萌芽はありましたが、Provider内部状態、adapter mapping、Unknown / Withheld、historical bindingまで独立Requirementとして扱う必要が明確になりました。

## 7. Historical Evidence matrixの扱い

Libraryで回収した`PRODUCT_REQUIREMENT_CANDIDATE_EVIDENCE_v1.yaml`には、旧Requirementごとに`direct`、`partial`、`design_only`等の状態と、historical local executable evidenceが記録されています。

このmatrix自体も、次の点を明記していました。

- design evidence
- local executable evidence
- historical reference evidence
- operational evidence

を分け、percentageやautomatic VERIFIED inheritanceを導かない。

この原則はcurrent `SOZA_VALUE_ACCEPTANCE.md`およびREQ-0020へ継承しています。ただし、旧matrixに記録されたlocal executable evidenceはactual `develop/v0.1.0` treeへまだ実体化されていないため、current Executable Acceptanceへは継承していません。

## 8. Provenance

historical mappingの主な入力:

- Library `requirements/PRODUCT_REQUIREMENTS_v1.md` — 2026-08-30 Draft / Phase 0 Rebaseline
- Library `requirements/ACCEPTANCE_SCENARIOS_v1.md` — 2026-08-30 Draft / Phase 0 Rebaseline
- Library `requirements/PRODUCT_REQUIREMENT_CANDIDATE_EVIDENCE_v1.yaml`
- Library bundle manifest
- current Product Value / Value Model / Value Acceptance
- ADR-0001〜ADR-0020

historical source本文はcurrent Requirement本文へ逐語的に保存することを目的にしません。必要な意味核と更新線を追跡できることを目的とします。

## 9. 自然な日本語ドラフト

historical Product Requirements、NFR、Acceptance Scenariosをcurrent REQ / SCNへ一件ずつ照合し、統合・分離・上位移管の理由を整理した後、対応関係とEvidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
