# 綜座 / SOZA

更新日: 2026-09-02  
状態: **v0.2.0 Local Reference Product Baseline released / development continues**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で囲い込むことではありません。実行手段が変わっても残る意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 現在の開発branchとrelease

通常の開発は`develop/vX.Y.Z`形式のbranchで進めます。現在の開発branchは`develop/v0.2.0`です。

v0.2.0は、開発者・評価者が現在のProduct ValueとSemantic Contractを実際に確かめられる **Local Reference Product Baseline** としてrelease済みです。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- Release Candidate Gate: Run `33574947445` — **success**
- Release Evidence: **Satisfied for v0.2.0 Local Reference Product Baseline**

これはproduction完成版を意味しません。

```text
v0.2.0 Release Evidence Satisfied
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Releaseの詳細は`release/v0.2.0/RELEASE_ACCEPTANCE.md`、`RELEASE_NOTES.md`、`RELEASE_EVIDENCE.md`を参照してください。

## 2. repositoryの現在地

current treeには、少なくとも次の領域があります。

```text
.github/
product/
requirements/
architecture/
contracts/
evaluation/
fixtures/
plan/
release/
runtime/
tools/
```

正本関係は概ね次のとおりです。

```text
Product Value / Value Proposition / Product Shape
  ↓
Product Milestone
  ↓
Requirements / Acceptance Scenarios
  ↓
ADR
  ↓
Reference Architecture
  ↓
Semantic Contract / Representation Profile
  ↓
Schema / Fixture / Validator
  ↓
Runtime / Adapter / Probe / Evaluation
  ↓
Executable Evidence
  ↓
Release Candidate / Release Evidence
```

下位の実装やCIが上位の意味を自動的に決めることはありません。上位文書に戻って、何を証明したEvidenceなのかを確認します。

## 3. Evidenceの読み方

SOZAでは、Evidenceの高さを次の5段階で分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

現在、v0.2.0 Local Reference Product BaselineについてRelease Evidenceまで成立しています。一方、production運用の継続性や、実利用によってProduct Valueが届いたことを示すEvidenceはまだありません。

また、過去のPASSを現在のPASSとして扱いません。

```text
historical PASS != current PASS
not_verified != failed
```

## 4. 最初に読む文書

### Product

1. `product/README.md`
2. `product/value/SOZA_PRODUCT_VALUE.md`
3. `product/value/SOZA_VALUE_PROPOSITION.md`
4. `product/value/SOZA_VALUE_MODEL.md`
5. `product/value/SOZA_VALUE_ACCEPTANCE.md`
6. `product/value/SOZA_VALUE_TRACEABILITY.md`
7. `product/definition/SOZA_PRODUCT_SHAPE.md`
8. `product/roadmap/SOZA_PRODUCT_MILESTONES.md`

### Requirements

9. `requirements/README.md`
10. `requirements/PRODUCT_REQUIREMENTS.md`
11. `requirements/ACCEPTANCE_SCENARIOS.md`
12. `requirements/PRODUCT_JOURNEY_COMPOSITION.md`

### Architecture

13. `architecture/README.md`
14. `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
15. `architecture/TRACEABILITY.md`

### Contracts / Representation Profiles

16. `contracts/README.md`
17. `contracts/CONTRACT_CATALOG.md`
18. `contracts/TRACEABILITY.md`
19. `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
20. `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
21. `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
22. `contracts/cognitive-method/SOZA_COGNITIVE_METHOD_v1alpha1.md`
23. `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
24. `contracts/profiles/README.md`

### Release / Planning

25. `release/README.md`
26. `release/v0.2.0/RELEASE_ACCEPTANCE.md`
27. `release/v0.2.0/RELEASE_EVIDENCE.md`
28. `plan/README.md`
29. `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
30. `plan/DEVELOPMENT_WORKFLOW.md`
31. `plan/registry.yaml`

Statusの正本は、各ADR / Issue本文と`plan/registry.yaml`です。

## 5. 守る意味境界

SOZAでは、少なくとも次を同一視しません。

```text
Observation
  != Interpretation / Hypothesis
  != Recommendation
  != Decision
  != Authority
  != Action Intent
  != Execution
  != Business Outcome
```

さらに、次の境界を守ります。

- `Unknown != No`
- `Conflict != latest-wins`
- `not observed != unavailable`
- `not_verified != failed`
- Capability != Provider
- Capability Definition != Capability Observation
- Matching != Decision
- Pattern != Cognitive Method
- Method Application != Assurance
- Logical Reference != Exact Historical Binding
- Projection != Canonical Semantic Authority
- Requirement != Acceptance Scenario != Test Case
- Semantic Contract != Representation Profile
- Product access permission != semantic Responsibility / Authority

## 6. Product Value

Product Valueは単一スコアへ還元せず、8軸で確認します。

- V1 — Historical Reconstruction
- V2 — Semantic Separation
- V3 — Revision Integrity
- V4 — Provider Independence
- V5 — Uncertainty Preservation
- V6 — Human / AI Readability
- V7 — Progressive Explicitness
- V8 — Execution Independence

受入れ境界は`product/value/SOZA_VALUE_ACCEPTANCE.md`、現在の追跡状態は`SOZA_VALUE_TRACEABILITY.md`を正とします。

## 7. current semantic baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0018`です。

current Semantic Contractは5 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Representation ProfileはSemantic Contractと別のversion空間を持ちます。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

historical M47 digest規則は、現在保持されている直接Evidenceから回収できないため、ISSUE-000034の方針どおり`not_verified`を維持します。

## 8. current executable material

現在のrepositoryには、限定されたExecutable Evidenceとして少なくとも次があります。

- semantic runtime
- Representation Verifier Registry
- synthetic Payload Source
- synthetic Provider Adapter
- Cognitive Method typed runtime
- known Contract横断bundle-local Exact Binding consistency
- V6 / V7 Projection evaluation
- end-to-end Semantic Product Journey harness
- human / machine Product Interaction reference probe
- Local Single-Node Packaging / resume / Storage migration probe
- Product Access / Collaboration responsibility separation probe
- out-of-process Realization / Provider exchange
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- actual TEI実行に先立つexternal executable injection boundary

このうち、v0.2.0の**supported release scopeはE3aまで**です。E3b-P1やTEI integration準備のEvidenceがrepositoryに存在することだけを理由に、v0.2.0のsupport範囲を後から広げません。

## 9. v0.2.0 Release Evidence

v0.2.0では、Release Candidate Gateで同じsource commitに対してPlan、Requirements、Contract、Representation Profile、JCS probe、semantic runtime、Projection evaluation、Local Reference Package、release policyをまとめて再検査しました。

actual releaseでは、tag、source commit、GitHub Release、4つのrelease asset、package digestを相互に照合しています。

```text
candidate PASS
  + exact tag binding
  + released artifact digest match
  → scoped Release Evidence Satisfied
```

Local Reference PackageのSHA-256は次です。

`37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`

release preparationで得たdigestと、GitHub Release上のpackage asset digestが一致しています。

## 10. SOZAとTEI

鼎（TEI）はSOZAそのものではなく、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

関連製品であることだけを理由にTEIへPriority / Trust / Authorityを付与しません。TEI固有のApplication、Database、Release、Deployment schemaをSOZA Universal Coreへ複製しません。

## 11. current Plan

current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000063を管理します。

- ISSUE-000021: **Deferred** — historical design provenanceの逐語監査
- ISSUE-000001〜000020、000022〜000063: **Resolved**

Resolvedは、対象作業の完了を示します。Release / Operational / Adoption・Outcome Evidenceまで自動的にVerifiedになったことを意味しません。

## 12. 次に深める領域

v0.2.0のrelease後も、実装量やIssue数を増やすこと自体を目的にしません。Product Valueへ戻りながら、主に次を深めます。

1. actual TEI process / serviceを用いたE3b-P2のEvidence
2. external Cognitive Methodのlive execution
3. E4 Operational portabilityの測定方法
4. production Provider / Storage / identity / securityを必要とする具体的ユースケースとAcceptance
5. 実運用後のOperational Evidence
6. 実利用後のAdoption / Outcome Evidence
7. historical design provenanceの一次資料が得られた場合のISSUE-000021再開

## 13. 文書品質

開発文書は、内容・構造・技術的一貫性を整えた後、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を通し、その後に最終意味監査を行います。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。

## 14. 自然な日本語レビュー

2026-09-02時点のProduct Value、Value Proposition、Product Shape、Product Milestone、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、5 Semantic Contract family、2 Representation Profile、current runtime / probe群、v0.2.0 Release Candidate Gate、actual tag / GitHub Release / release asset、ISSUE-000001〜000063へ戻って現在地を再監査しました。

そのうえで、旧READMEに残っていた`develop/v0.1.0`、4 Contract family、Release未成立等の古い記述をcurrent stateへ更新しました。v0.2.0のRelease EvidenceはLocal Reference Product Baselineに限定してSatisfiedとし、E3b全体、E4、production readiness、Operational Evidence、Adoption / Outcome Evidenceは未検証のまま保持しています。意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
