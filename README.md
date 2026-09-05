# 綜座 / SOZA

更新日: 2026-09-05  
状態: **v0.2.0 Local Reference Product Baseline released / development continues**

SOZAは、人間・AI・組織・既存システム・外部サービスが入れ替わっても、**何を見て、何を問い、何を根拠とし、何を決め、何を未解決として残したか**を失わないための、可搬な認知・意思決定基盤です。

SOZAの中心は、workflowやAI agent runtimeを自前で囲い込むことではありません。実行手段が変わっても残る意味、不確実性、判断、責任、Capability、Provenance、Semantic Lineageを扱います。

## 1. 現在の開発branchとrelease

通常の開発は`develop/vX.Y.Z`形式のbranchで進めます。現在の開発branchは`develop/v0.2.0`です。

v0.2.0は、開発者・評価者が現在のProduct ValueとSemantic Contractを実際に確かめられる **Local Reference Product Baseline** としてrelease済みです。

- tag: `v0.2.0`
- source commit: `c3640bdfcc43652b63a5b9941fd6b472312ec28f`
- historical Release Candidate Gate: Run `33574947445` — **success**
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

GitHub Actionsは当面完全に停止しており、current `develop/v0.2.0`には`.github/workflows`を置いていません。必要なchecker、test、probeは変更範囲に応じてローカルで個別に実行します。

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

下位の実装や検証手段が上位の意味を自動的に決めることはありません。上位文書に戻って、何を証明したEvidenceなのかを確認します。

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

GitHub Actions停止中も検証を省略するわけではありません。ローカルで実行したchecker、test、probeの結果だけをその高さのEvidenceとして扱い、実行できない検証は`Not Yet Verified`のまま残します。

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
9. `product/roadmap/PMS06_CURRENT_STATE_2026-09-05.md`

### Requirements

10. `requirements/README.md`
11. `requirements/PRODUCT_REQUIREMENTS.md`
12. `requirements/ACCEPTANCE_SCENARIOS.md`
13. `requirements/PRODUCT_JOURNEY_COMPOSITION.md`

### Architecture

14. `architecture/README.md`
15. `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
16. `architecture/TRACEABILITY.md`

### Contracts / Representation Profiles

17. `contracts/README.md`
18. `contracts/CONTRACT_CATALOG.md`
19. `contracts/TRACEABILITY.md`
20. `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
21. `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
22. `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
23. `contracts/cognitive-method/SOZA_COGNITIVE_METHOD_v1alpha1.md`
24. `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
25. `contracts/profiles/README.md`

### Release / Planning

26. `release/README.md`
27. `release/v0.2.0/RELEASE_ACCEPTANCE.md`
28. `release/v0.2.0/RELEASE_EVIDENCE.md`
29. `plan/README.md`
30. `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
31. `plan/DEVELOPMENT_WORKFLOW.md`
32. `plan/registry.yaml`

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

現在のrepositoryには、限定されたExecutable Evidenceまたはその再実行資産として、少なくとも次があります。

- semantic runtime
- Representation Verifier Registry
- synthetic Payload Source / Provider Adapter
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
- E3b-P2 fixed-artifact actual TEI CLI integration
- E3b-M1a fixed KJ Atlas + deterministic model-stub integration
- E3b-M1b Ollama actual model-backed Cognitive Method integration
- actual model artifact交換のhistorical Application保持
- Method Realization historical revision / portable reconstruction
- fixed model artifact下のOllama runtime version交換後のhistorical Application保持
- Cognitive Method outcome-quality evaluation boundary
- Ollama runtime version交換用repository-local harness / artifact guard / preflight / Evidence verifier / progress observer
- TEI executable version交換用source / fixed-input identity verifier、E2 / E3 runner、separate toolchains、stage-aware diagnostics

このうち、v0.2.0の**supported release scopeはE3aまで**です。release後に得られたE3b-P2、M1a / M1b、historical reconstruction、model / runtime version exchange等のEvidenceを理由に、公開済みv0.2.0のsupport範囲を後から広げません。

version交換の現在地は次のとおりです。

```text
ISSUE-000070
  = Resolved
  = fixed-scope Ollama 0.32.13 / 0.32.14 actual runtime exchangeのScoped Executable Evidence available

ISSUE-000072
  = Open
  = revision B TEI actual build / Provider Plan / current SOZA Adapter compatibility Not Yet Verified
```

ISSUE-000070ではfixed KJ Atlas source / Method input / model artifact / promptを保ち、A/B actual inference、same logical / different Exact Binding、historical Application不変性、portable reconstruction、canonical Evidence + Provenance `ready-to-review`まで確認しました。これは任意runtime portabilityや成果品質の成立を意味しません。

## 9. v0.2.0 Release Evidence

v0.2.0のactual release時には、同じsource commitに対してPlan、Requirements、Contract、Representation Profile、JCS probe、semantic runtime、Projection evaluation、Local Reference Package、release policyをまとめて再検査しました。

actual releaseでは、tag、source commit、GitHub Release、release asset、package digestを相互に照合しています。

```text
candidate PASS
  + exact tag binding
  + released artifact digest match
  → scoped Release Evidence Satisfied
```

Local Reference PackageのSHA-256は次です。

`37f34d3ae4885df655e889f2799b9aea1d8c7c8c060c207df83f50459431ef17`

release preparationで得たdigestと、GitHub Release上のpackage asset digestが一致しています。

このrelease Evidenceはhistoricalに確定しています。後続develop commitの検証は、必要なローカルchecker、test、probeを別途実行して判断します。

## 10. SOZAとTEI

鼎（TEI）はSOZAそのものではなく、SOZAから利用し得るCapability Providerの一つです。

```text
SOZA = 何を見るか、何を問うか、何を残すか、何を判断するか
TEI  = 実行可能な業務Capabilityを実現する一つの手段
```

関連製品であることだけを理由にTEIへPriority / Trust / Authorityを付与しません。TEI固有のApplication、Database、Release、Deployment schemaをSOZA Universal Coreへ複製しません。

## 11. current Plan

current registryはADR-0001〜ADR-0030、ISSUE-000001〜ISSUE-000072を管理します。

現在の未解決Issueは次です。

- ISSUE-000072: **Open** — TEI executable revision交換後もProvider Observation境界を保てるかのactual実証

また、次は意図的にDeferredです。

- ISSUE-000021: **Deferred** — historical design provenanceの逐語監査

ISSUE-000069はGitHub Actions / runner availabilityと検証責務の分離としてResolvedです。ISSUE-000070はfixed model artifact下のOllama runtime version交換をactualに確認したfixed-scope Scoped Executable EvidenceによりResolvedです。ISSUE-000071はCognitive Method成果品質の**評価境界の確立**としてResolvedですが、actual human reviewや成果品質そのものがSatisfiedになったことを意味しません。

Resolvedは、対象作業の完了を示します。Release / Operational / Adoption・Outcome Evidenceまで自動的にVerifiedになったことを意味しません。

## 12. 次に深める領域

現時点では、PMS-06で残る主要Open version-exchange探索であるISSUE-000072のactual実証が最優先です。ISSUE-000070のPASSをISSUE-000072のEvidenceへ流用しません。

1. ISSUE-000072で、exact revision B executable + exact revision A fixed inputによりactual `deployment-provider-plan`を実行する。
2. ISSUE-000072で、revision Bをcurrent SOZA Adapterからactualに起動し、Capability Observation mapping成立可否を確認する。
3. ISSUE-000072のactual結果をREQ-0001 / 0007 / 0021、SCN-0014 / 0018へ戻し、必要なら隣接REQ-0022も監査する。
4. ISSUE-000071で整えたreview bundleを使い、必要に応じてactual human reviewを行う。
5. 別model family、別Provider、別Realizationへbroader portabilityを広げる。
6. network degradation、credential失効、artifact acquisition failure等のfailure behaviorを探索する。
7. E4 Operational portabilityとAdoption / Outcome Evidenceへ進む。

ISSUE-000070については、Reopen conditionに該当するEvidenceやContract driftが観測された場合に再開します。Resolvedであることを理由にarbitrary runtime portabilityや成果品質へ主張を広げません。

実装量やIssue数を増やすこと自体は目的にしません。既存RequirementとContractで表現できる場合は、実証のためだけにUniversal semanticsを増やしません。

## 13. 検証の実行方針

GitHub Actionsは当面完全に停止しています。workflowの追加・復元、historical runの再実行、runner監視は行いません。

変更内容に応じて、repository同梱のchecker、test、fixture、probeをローカルで個別に実行します。

```text
change scope
  → relevant local check
  → observed result
  → fix if needed
  → Evidence update
```

検証できなかった項目は`Not Yet Verified`として残します。GitHub Actionsが停止していることを、検証済みの代替にはしません。

## 14. 文書品質

開発文書は、内容・構造・技術的一貫性を整えた後、**意味・仕様・留保・Evidenceの強さを変えず、自然な日本語となることを最重要視して全文をドラフトし直す工程**を通し、その後に最終意味監査を行います。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。

## 15. 自然な日本語レビュー

2026-09-05時点のProduct Value、Product Milestone、PMS-06 current snapshot、REQ-0001〜0022、SCN-0001〜0018、ADR-0001〜0030、ISSUE-000001〜000072、5 Semantic Contract family、2 Representation Profile、current runtime / probe / evaluation資産、v0.2.0 historical Release Evidence、ISSUE-000067〜000072へ戻って現在地を再監査しました。

旧READMEに残っていた`.github/`のcurrent tree記載、ISSUE-000063までのPlan状態、既に完了したTEI / external Cognitive Method実証を「次の作業」とする記述は以前に更新済みです。ISSUE-000072追加後のPlan範囲も同期し、GitHub Actionsのhistorical Evidenceは保存しながら、現在の検証はローカル個別実行へ切り替えています。

今回さらに、ISSUE-000070をactual runtime version交換Evidenceとcurrent-contract object-equivalence監査に基づくResolved状態へ同期しました。fixed-scope Ollama `0.32.13` / `0.32.14` version exchangeはScoped Executable Evidence availableですが、arbitrary runtime portability、model / KJ-method outcome quality、E4、Operational / Adoption Evidenceへは広げません。

現在PMS-06で残る主要Open version-exchange探索はISSUE-000072です。revision B TEI actual CLI / Provider Plan / current SOZA Adapter compatibilityはNot Yet Verifiedのままです。

v0.2.0のRelease EvidenceはLocal Reference Product Baselineに限定してSatisfiedとし、後続E3b Evidenceをrelease scopeへ遡及させません。意味、規範強度、Evidence強度を変えず、入口文書として自然な日本語で現在地をたどれることを最重要視して再監査しました。
