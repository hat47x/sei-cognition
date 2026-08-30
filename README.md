# SOZA — Product / Planning Baseline v0.1.0

更新日: 2026-08-31  
状態: **Product / Planning baseline in progress — release not claimed**

綜座（SOZA）は、人間・AI・組織・プロジェクトなどの主体が、**何を観察し、何をまだ分かっていないと認め、何を問い、何を根拠として、どのように判断したか**を失わずに扱うための認知・意思決定基盤です。

SOZAの中心は、現在のworkflow engineやAI agent runtimeそのものではありません。技術やProviderが入れ替わっても残る、認識、不確実性、問い、根拠、判断、責任、Capability、来歴の意味を保持し、人間とAIが後から読み直し、検証し、必要なら選び直せることを重視します。

このrepositoryは現在、**Product Valueとplanning / architecture decisionの再基線化を優先している段階**です。Requirements、Architecture、Contracts、Runtime、Fixtures、Tools等についてhistorical / local candidateが存在していても、actual GitHub treeへまだ実体化されていないものを、このREADMEでは実装済み・検証済みとして扱いません。

## 1. 現在のactual repository

2026-08-31時点で、actual treeの中心は次です。

```text
product/
  ├─ value/
  ├─ vision/
  └─ principles/

plan/
  ├─ adr/
  ├─ issue/
  ├─ kj/
  ├─ registry.yaml
  └─ README.md
```

現在は、Product ValueからRequirements / Acceptanceへ降りる追跡基線と、actual repository materializationの準備を進めています。

次の階層は設計上必要ですが、**actual treeへ存在するまでは存在を主張しません。**

```text
requirements/
architecture/
contracts/
fixtures/
runtime/
tools/
```

## 2. 最初に読む順序

### Product Value

1. `product/value/SOZA_PRODUCT_VALUE.md`  
   SOZAがなぜ存在し、何を価値として守るか。
2. `product/value/SOZA_VALUE_MODEL.md`  
   価値の優先規則、Core境界、V1〜V9のvalidation axis、Evidence level。
3. `product/value/SOZA_VALUE_SCENARIOS.md`  
   Product Valueを13の具体的な判断場面へ戻す。
4. `product/value/SOZA_VALUE_TRACEABILITY.md`  
   Value Model / Value ScenarioとADR-0001〜ADR-0019の現在の対応とgap。
5. `product/vision/SOZA_PRODUCT_VISION.md`  
   技術変化をまたいで目指す長期像。
6. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`  
   Requirements、ADR、Architecture、Implementationで反復して使う判断原則。

### Planning

7. `plan/README.md`  
   ADR / Issueの運用、採番、Evidence level、自然な日本語ドラフト工程。
8. `plan/registry.yaml`  
   ADR / Issueの現在の状態と関連を一覧する台帳。
9. `plan/adr/`  
   Accepted / Proposed等の設計判断。
10. `plan/issue/`  
    未決課題、調査、materialization、後続検証。
11. `plan/kj/`  
    Decisionを立ち上げるために用いたKJ統合資料。最終Product文書の主題にはしない。

## 3. Product Valueの現在の基線

SOZAの価値は、概ね次の三層で整理しています。

1. **失ってはならない意味**  
   Observation、Unknown、Conflict、Evidence、Decision、Responsibility、Authorityへの参照、Provenance等の重要な意味差を失わない。
2. **後から選び直せること**  
   過去Decisionを当時の状態として再構成し、新しいEvidenceやConstraintが入ったときに、過去を消さず再審査できる。
3. **利用し続けられること**  
   人間とAIの双方が扱え、必要な箇所だけ意味を段階的に厳密化できる。

価値が衝突した場合は、判断の意味、不確実性、責任線、来歴を先に守り、その範囲で操作性、性能、自動化、実装容易性を最大化します。

## 4. Value Model validation axis

現在のProduct Value検証軸は次の9つです。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence
- V9 Evidence Calibration

一つの総合点へ還元しません。どの価値を満たし、どこに未検証やtrade-offが残るかを個別に扱います。

## 5. 重要な意味境界

SOZAでは、たとえば次を同一視しません。

```text
Recommendation != Decision != Responsibility != Authority != Execution
Unknown != No
Conflict != latest-wins
Question wording != Question semantic identity
Capability != Provider
Provider Observation != Capability Choice Decision
Execution Success != Decision Validity
Method Application != Assurance
```

短い式は確認用であり、正式な意味はProduct Value、ADR、Issue本文で自然な日本語でも説明します。

## 6. SOZAとTEI

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

## 7. Evidence level

このrepositoryでは、少なくとも次を区別します。

```text
Value Definition
  != Design / Requirement Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

さらに、次も分けます。

```text
historical evidence
local candidate evidence
actual repository evidence
operational evidence
adoption / outcome evidence
```

historical / local candidateでfixtureやtestがPASSしていても、actual repositoryに同じ資産と再実行可能な入口がなければ、actual repository PASSとは扱いません。

設計文書が整ったことも、productionで動いたことも、それだけでは利用者の意思決定が改善したことの証明にはなりません。

## 8. ADR / Issueの現在地

### ADR

- ADR-0001〜ADR-0019: **Accepted**

現在の末尾の主要判断:

- ADR-0014 — SOZA / TEI Product Boundary
- ADR-0015 — Requirement Inquiry / Decision Memory
- ADR-0016 — Authorization Evidence Provider Boundary
- ADR-0017 — Reference Model / Cognitive Method Boundary
- ADR-0018 — Product Value governance
- ADR-0019 — Provider-neutral Capability Observation Boundary

### Active Issue

- ISSUE-000009: **Blocked** — actual repository上のportable Exact Binding verification基線待ち
- ISSUE-000015: **In Progress** — active開発文書の自然な日本語監査
- ISSUE-000021: **Deferred** — 7チャット設計史の逐語原文Evidence待ち
- ISSUE-000022: **In Progress** — actual repository baseline materializationとEvidence claim再整合
- ISSUE-000024: **Open** — Value ScenarioからRequirement / NFR / Acceptanceへの追跡基線
- ISSUE-000025: **Blocked** — Provider-neutral Capability Observationのactual contract / fixture。ISSUE-000022待ち

その他、ISSUE-000001〜000008、000010〜000014、000016〜000020、000023は、対応するplanning / Decision boundaryを完了して**Resolved**です。

最新状態の正本は`plan/registry.yaml`と各Issue本文です。

## 9. 現在の最優先作業

現時点では、次の順に進めます。

1. Product Value / Value ScenarioからRequirements / Acceptanceへ追跡可能な基線を作る。
2. active開発文書を自然な日本語ドラフト工程へ通す。
3. historical / local candidateを最新Product ValueとADRへ戻して監査しながら、actual repositoryへ必要資産を段階的に実体化する。
4. actual treeにcontract / fixture / toolの入口ができた後、Exact BindingとCapability Observationのconformanceを再実行可能にする。
5. operational evidence、adoption / outcome evidenceは、実際に得られるまで未実証として扱う。

この順序はProduct ontologyではなく、現在のgapと依存関係に基づくplanning priorityです。

## 10. historical / local candidateの扱い

旧Phase 1 / M48 / M49 / M50 candidateで作成されたRequirements、Architecture、Contracts、Runtime、Fixtures、Tools、report等は、現在の設計を考えるうえで重要なhistorical / local candidateです。

ただし、次を原則とします。

- 旧candidateを無検査でactual repositoryへ一括コピーしない。
- 旧VERIFIED / PASSをactual repositoryへ自動継承しない。
- M47 sourceがactual treeに存在しないなら、存在しない回帰試験をPASS扱いしない。
- 最新Product ValueとAccepted ADRへ戻して、retain / revise / split / merge / move / historical only等を判断する。
- SOZAとTEIのProduct Boundaryを優先する。

このmaterializationはISSUE-000022で追跡します。

## 11. 文書品質

SOZAのactive開発文書は、内容・構造・技術的一貫性を確認した後、**意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を通します。

新規文書だけでなく、既存のactive開発文書も順次同じ工程へ通します。運用規則は`plan/README.md`、進捗はISSUE-000015で管理します。

## 12. releaseについて

このREADMEはProduct / Planning baselineの現在地を示すものであり、SOZAのreleaseを宣言するものではありません。

Requirements、Architecture、Contracts、Runtime、conformance等のactual repository基線が整った場合も、Design Coverage、Executable Conformance、Operational Evidence、Adoption / Outcome Evidenceを区別して報告します。

## 13. 次に参照するIssue

上位設計から作業を続ける場合は、まず次を参照します。

- `plan/issue/ISSUE-000024-derive-value-scenario-requirement-traceability.md`
- `plan/issue/ISSUE-000015-natural-japanese-document-audit.md`
- `plan/issue/ISSUE-000022-materialize-repository-baseline.md`

実装・検証基線が必要な課題は、次で依存関係を明示しています。

- `plan/issue/ISSUE-000009-stabilize-portable-exact-binding-verification.md`
- `plan/issue/ISSUE-000025-materialize-capability-observation-contract.md`

## 14. 自然な日本語ドラフト

actual repository tree、Product Value一式、ADR / Issueの現在状態、Evidence levelへ戻して内容を再構成した後、存在しない成果物を実体化済みと読める表現を除き、意味・留保・未実装範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
