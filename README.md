# SOZA — Product / Requirements / Planning Baseline v0.1.0

更新日: 2026-08-31  
状態: **development baseline in progress — release not claimed**

綜座（SOZA）は、人間・AI・組織・プロジェクトなどの主体が、**何を観察し、何をまだ分かっていないと認め、何を問い、何を根拠として、どのように判断したか**を失わずに扱うための認知・意思決定基盤です。

SOZAの中心は、現在のworkflow engineやAI agent runtimeそのものではありません。技術やProviderが入れ替わっても残る、認識、不確実性、問い、根拠、判断、責任、Capability、来歴の意味を保持し、人間とAIが後から読み直し、検証し、必要なら選び直せることを重視します。

このrepositoryは現在、**Product Value、current Product Requirements / Acceptance Scenarios、planning / Architecture Decisionの基線を整えている段階**です。

historical / local candidateにArchitecture、Contracts、Runtime、Fixtures、Tools等が存在していても、actual GitHub treeへまだ実体化されていないものを、このREADMEでは実装済み・検証済みとして扱いません。

## 1. 現在のactual repository

2026-08-31時点で、actual treeの中心は次です。

```text
product/
  ├─ value/
  ├─ vision/
  └─ principles/

requirements/
  ├─ PRODUCT_REQUIREMENTS.md
  └─ ACCEPTANCE_SCENARIOS.md

plan/
  ├─ adr/
  ├─ issue/
  ├─ kj/
  ├─ registry.yaml
  ├─ DOCUMENT_AUTHORING_STANDARD.md
  └─ DEVELOPMENT_WORKFLOW.md
```

Requirementsはcurrent Product Valueから再構成されたDesign baselineです。

次の階層は今後actual treeへ実体化する対象ですが、**存在するまでは実装済みと主張しません。**

```text
architecture/
contracts/
fixtures/
runtime/
tools/
```

## 2. 最初に読む順序

### Product

1. `product/README.md`  
   Product文書の役割、権威関係、Evidence境界。
2. `product/value/SOZA_PRODUCT_VALUE.md`  
   SOZAがなぜ存在し、何を価値として守るか。
3. `product/value/SOZA_VALUE_MODEL.md`  
   価値の優先規則、Core境界、V1〜V8。
4. `product/value/SOZA_VALUE_ACCEPTANCE.md`  
   V1〜V8を満たしたと主張するためのDesign / Executable / Release / Operational Evidence境界。
5. `product/value/SOZA_VALUE_TRACEABILITY.md`  
   V1〜V8とcurrent Requirements、Acceptance Scenarios、ADR、Issue、Evidence gapの対応。
6. `product/vision/SOZA_PRODUCT_VISION.md`  
   技術変化をまたいで目指す長期像。
7. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`  
   下位設計で反復して用いる判断原則。

### Requirements

8. `requirements/PRODUCT_REQUIREMENTS.md`  
   current REQ-0001〜REQ-0022。
9. `requirements/ACCEPTANCE_SCENARIOS.md`  
   current SCN-0001〜SCN-0017。

### Planning

10. `plan/README.md`  
    ADR / Issueの運用規約。
11. `plan/DOCUMENT_AUTHORING_STANDARD.md`  
    自然な日本語を最優先にする文書作成標準。
12. `plan/DEVELOPMENT_WORKFLOW.md`  
    branch、優先順位、開発単位、Evidence更新の規約。
13. `plan/registry.yaml`  
    ADR / Issueの状態と関連の台帳。
14. `plan/adr/`  
    Accepted Decision群。
15. `plan/issue/`  
    未決課題、materialization、後続検証。

## 3. Product Valueの基線

SOZAの価値は、概ね次の三層で整理しています。

1. **失ってはならない意味**  
   Observation、Unknown、Conflict、Evidence、Decision、Responsibility、Authorityへの参照、Provenance等の重要な意味差を失わない。
2. **後から選び直せること**  
   過去Decisionを当時の状態として再構成し、新しいEvidenceやConstraintが入ったときに、過去を消さず再審査できる。
3. **利用し続けられること**  
   人間とAIの双方が扱え、必要な箇所だけ意味を段階的に厳密化できる。

価値が衝突した場合は、判断の意味、不確実性、責任線、来歴を先に守り、その範囲で操作性、性能、自動化、実装容易性を最大化します。

## 4. Value Model

現在のProduct Value検証軸は次の8つです。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

一つの総合点へ還元しません。一つの軸で高い評価を得ても、別の重大な欠損を相殺したことにはしません。

## 5. current Requirements / Acceptance Scenarios

current Product RequirementsはREQ-0001〜REQ-0022です。

Requirementの採用状態とEvidenceの高さは分けます。

```text
Requirement Accepted
  != Executable Evidence Satisfied
  != Release Evidence Satisfied
  != Operational Evidence Satisfied
```

current Acceptance ScenariosはSCN-0001〜SCN-0017です。

```text
Requirement != Acceptance Scenario != Test Case
```

ScenarioがDesign baselineに存在するだけでは、actual implementationのExecutable Acceptanceを満たしたことにはなりません。

## 6. 重要な意味境界

SOZAでは、たとえば次を同一視しません。

```text
Recommendation != Decision != Authority != Execution
Unknown != No
Conflict != latest-wins
Question wording != Question semantic identity
Capability != Provider
Provider state != Capability interpretation
Capability interpretation != Decision
Execution Success != Decision Validity
Method Application != Assurance
```

短い式は確認用です。正式な意味はProduct、Requirement、ADR本文でも自然な日本語で説明します。

## 7. SOZAとTEI

SOZAと鼎（TEI）は関連しますが、別Product Boundaryとして維持します。

```text
SOZA
  認識 / 問い / 不確実性 / 根拠 / 判断 / 責任 / Capability Choice

        ↓ explicit provider boundary

TEI
  実行可能な業務Capabilityを実現する一つのProvider
```

SOZAはTEI固有のApplication、Database、Release、Deployment等をUniversal Coreへコピーしません。

TEIもSOZAのDecisionやAuthorityを暗黙に代行しません。SOZAから見たTEIはCapability Providerの一つであり、人間、AI、SaaS、外部組織、custom code等と同じ判断面で比較できることを原則とします。

## 8. Evidence level

少なくとも次を区別します。

```text
Value Definition
  != Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
```

さらに、実運用で期待した性質が成立したことと、利用者・組織の意思決定や外部成果が改善したことも分けます。

```text
Operational Evidence != Adoption / Outcome Evidence
```

Design Evidenceが整ったことを、actual repositoryで実装が動くこと、release済みであること、productionで価値が確認されたことへ自動昇格させません。

historical / local candidateのPASSも、actual repositoryのPASSへ自動継承しません。

## 9. ADR / Issueの現在地

### ADR

ADR-0001〜ADR-0020はAcceptedです。

末尾の主要判断:

- ADR-0014 — SOZA / TEI Product Boundary
- ADR-0015 — Requirement Inquiry / Decision Memory
- ADR-0016 — Authorization Evidence Provider Boundary
- ADR-0017 — Reference Model / Cognitive Method Boundary
- ADR-0018 — Product Value governance
- ADR-0019 — Provider-neutral Capability Observation Boundary
- ADR-0020 — Requirements traceability / Evidence boundary

### 主なactive Issue

- ISSUE-000009: **Blocked** — Portable Exact Bindingのactual verification基線
- ISSUE-000015: **In Progress** — active開発文書の自然な日本語監査
- ISSUE-000021: **Deferred** — 設計史の逐語原文Evidence待ち
- ISSUE-000022: **In Progress** — actual repository baseline materialization
- ISSUE-000024: **Open** — Capability Observation schema / fixture
- ISSUE-000026: **In Progress** — current Requirements / Acceptance Scenarios baseline

最新Statusの正本は`plan/registry.yaml`と各Issue本文です。

## 10. historical / local candidateの扱い

旧Phase 1 / M48 / M49 / M50 candidateで作成されたRequirements、Architecture、Contracts、Runtime、Fixtures、Tools、report等は、現在の設計を考えるうえで重要なhistorical / local candidateです。

ただし、次を原則とします。

- 旧candidateを無検査でactual repositoryへ一括コピーしない。
- 旧IDや旧VERIFIED / PASSをcurrent baselineへ自動継承しない。
- M47 sourceがactual treeに存在しないなら、存在しない回帰試験をPASS扱いしない。
- current Product Value、Requirements、Accepted ADRへ戻して再評価する。
- SOZAとTEIのProduct Boundaryを優先する。

actual repositoryへのmaterializationはISSUE-000022で追跡します。

## 11. 現在の優先作業

現在は、次を優先します。

1. Product Value / Requirements / ADRのtraceabilityを維持する。
2. active文書を自然な日本語ドラフト工程へ通す。
3. Capability Observationをactual schema / fixtureへ落とす。
4. historical / local candidateをcurrent Product ValueとADRへ戻して監査しながら、Architecture / Contracts / runtime / toolを段階的に実体化する。
5. actual Evidenceが得られた段階でExecutable / Release / Operational Acceptanceを更新する。
6. Adoption / Outcome Evidenceは実案件から得られるまで未実証として扱う。

この順序はProduct ontologyではなく、現在のgapと依存関係に基づくplanning priorityです。

## 12. 文書品質

SOZAのactive開発文書は、`plan/DOCUMENT_AUTHORING_STANDARD.md`に従います。

内容・構造・技術的一貫性を確認した後、**意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を通し、最後に意味を再監査します。

## 13. releaseについて

このREADMEはcurrent development baselineの現在地を示すものであり、SOZAのreleaseを宣言するものではありません。

Architecture、Contracts、Runtime、conformance等がactual repositoryへ追加された場合も、Design / Executable / Release / Operational / Adoption・OutcomeのEvidenceを区別して報告します。

## 14. 自然な日本語ドラフト

actual repository tree、Product Value、current Requirements / Acceptance Scenarios、ADR / Issue状態、Evidence levelへ戻して内容を再構成し、存在しない成果物を実体化済みと読める表現を除きました。そのうえで、意味・留保・未実装範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
