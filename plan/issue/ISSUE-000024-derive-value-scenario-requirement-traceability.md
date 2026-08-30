# ISSUE-000024: Value ScenarioからRequirement / Acceptanceへの追跡基線を作る

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0018**  
Updated: 2026-08-31

## Goal

`SOZA_PRODUCT_VALUE.md`、`SOZA_VALUE_MODEL.md`、`SOZA_VALUE_SCENARIOS.md`から、Product Requirement、NFR、Acceptance Scenario、ADRへ意味を追跡できる基線を作る。

目的はRequirement数を増やすことではない。Product Valueの重要な境界が下位文書で欠落していないことと、下位の実装都合がProduct Valueへ無断で昇格していないことを確認できる状態にする。

## Background

Product Valueは、意味保存、不確実性、Question / Decision、Responsibility / Authority、Capability / Provider、Semantic Lineage、Evidence calibrationまで精緻化された。

Value Scenarioでは、これらをAI提案、Unknown、Conflict、問い直し、Provider交換、Authorization、Execution、Cognitive Method、Selective Disclosure、Progressive Explicitness、技術交換、Evidence level等の具体場面へ戻している。

一方、actual GitHub repositoryには現時点で`requirements/`やAcceptance Scenario群が実体化していない。historical / candidate資料の存在や過去のPASSをactual repositoryのEvidenceとして扱わず、最新Product Valueから改めて追跡基線を作る必要がある。

## Questions

1. 各Value Scenarioで必ず守るべき意味境界は何か。
2. 複数Scenarioに共通し、Product Requirementへ昇格すべき義務は何か。
3. NFRとして扱うべき性質は何か。
4. Profile / Policy / Provider adapter / domain knowledgeへ置くべきものは何か。
5. ADR-0001〜ADR-0019は、どのValue Scenarioとvalidation axisを具体化しているか。
6. まだADRもRequirement候補もない空白はどこか。
7. Acceptance Scenarioでは、何を観察できればRequirementを満たしたと判断できるか。
8. design coverage、executable conformance、operational evidence、adoption / outcome evidenceをどう区別するか。
9. historical candidate requirementと最新Product Valueが衝突する場合、何を正とするか。

## Constraints

- Value Scenarioを一対一でRequirementへ変換しない。
- Requirement数やcoverage率そのものをProduct Valueの指標にしない。
- historical candidateのVERIFIED / PASSをactual repositoryへ自動継承しない。
- READMEに名前があるだけの成果物を「存在する」と扱わない。
- TEI固有要件をSOZA Universal Requirementへ無断で昇格させない。
- current implementation convenienceをRequirementの根拠にしない。
- Value DefinitionとDesign Coverage、Executable Conformance、Operational Evidence、Adoption / Outcome Evidenceを混同しない。

## Required work

1. Value Scenario、Value Model validation axis、candidate Requirement / NFR、既存ADR、未決gap、必要Evidence levelを対応付ける。
2. 複数Scenarioに繰り返し現れる意味を統合し、Requirement候補の重複を減らす。
3. 正常系だけでなく、Unknownの確定値化、RecommendationのDecision化、Provider statusのDecision化などの意味喪失を検出するAcceptanceを整理する。
4. historical candidateを利用する場合は、retain / revise / split / merge / move / historical only / unresolved等として最新Product Valueへ戻して再評価する。
5. actual repositoryへ実体化する成果物と、まだplanningに留めるものを分ける。

## Deliverables

- Value ScenarioからRequirement / NFR / ADRへの対応表
- candidate Product Requirement / NFR set
- negative acceptanceの候補
- ADR-0001〜ADR-0019とのtraceability
- uncovered-value gap list
- historical candidateの再評価規則
- `ISSUE-000022`との依存関係整理

## Completion criteria

- Product Valueの三層が下位候補へ追跡できる。
- V1〜V9の各validation axisについて、検証経路または未検証状態を明示できる。
- 13 Value Scenarioの主要な意味がどこで扱われるか追跡できる。
- 既存ADRとの重複を増やさず、未決gapだけを次のIssue / ADR候補として残せる。
- actual repositoryに存在しない成果物をPASS扱いしない。
- 成果文書は自然な日本語を最優先に全文を再ドラフトし、意味監査を行う。

## Dependencies

- ADR-0018
- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- ISSUE-000022

分析と候補整理はISSUE-000022の完了前でも進められる。ただし、Requirement / Acceptance成果物がactual repositoryへ追加されたというclaimは、実際にtreeへ追加されるまで行わない。

## Natural Japanese review

上位Product Value文書とADR-0018との整合を確認した後、意味、強度、留保、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
