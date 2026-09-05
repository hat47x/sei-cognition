# SOZA Product文書の読み方

更新日: 2026-09-05  
状態: **Current Product Documentation Baseline — v0.2.0 Release Evidence / E3b-P2 / E3b-M1a・M1b / historical reconstruction / runtime-version exchange / quality-evaluation boundary / PMS-06 current state reflected**

## 1. この文書の役割

`product/`は、SOZAが**なぜ存在するのか、何を失ってはならないのか、どのような製品状態を目指し、どこまで成立したら次の段階へ進めるのか**を定める上位文書の入口です。

個別の実装方式や特定Providerの都合をProduct定義へ持ち込む場所ではありません。期限やcalendar scheduleもここでは固定せず、Product MilestoneはOutcomeとEvidenceの成立条件で表します。

SOZAでは、概ね次の依存方向を維持します。

```text
Product Value / Value Proposition
  → Value Model / Value Acceptance
  → Vision / Principles / Product Shape
  → Deadline-free Product Milestones
  → Product Interaction / Packaging / Identity・Access / other Product boundaries
  → Open Question / Product Hypothesis
  → Discussion / Research / Experiment / Human Review
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture / Contract
  → Runtime / Adapter / Probe / Test
  → Executable Evidence
  → Release Candidate / Release Evidence
  → Operational / Adoption・Outcome Evidence
```

下位の実装・検証から上位仮説への反証が得られた場合は、必要に応じてProduct Valueまで戻って再検討します。ただし、既存実装を温存するためだけに上位価値を書き換えません。

GitHub Actionsは当面完全に停止しています。Product Value、Requirement、Contract、Evidenceの意味を特定の実行基盤へ依存させず、必要なchecker、test、probeはローカルで個別に実行します。

## 2. Product文書の正本関係

### `value/SOZA_PRODUCT_VALUE.md`

SOZAが存在する理由と、最も上位で守る価値を定めます。Product Valueから個別RequirementやUniversal型を機械的に生成しません。

### `value/SOZA_VALUE_PROPOSITION.md`

Product Valueを、利用者がどのような問題を解き、どのような価値を受け取る製品なのかという観点から表します。

### `value/SOZA_VALUE_MODEL.md`

Product Valueを設計判断へ落とせる粒度に精緻化します。現在はV1〜V8を用います。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

V1〜V8は総合点を作るための採点項目ではありません。一つの軸の強さで、別の重大な欠損を相殺しません。

### `value/SOZA_VALUE_ACCEPTANCE.md`

V1〜V8を「満たした」と主張するとき、どの高さのEvidenceが必要かを定めます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### `value/SOZA_VALUE_TRACEABILITY.md`

Product Valueからcurrent Requirements、Acceptance Scenarios、ADR、Architecture、Contract、Representation Profile、runtime、probe、Release Evidence、Evidence gapへ戻るための索引です。

### `definition/SOZA_PRODUCT_SHAPE.md`

SOZAを製品として見たときの主要な仕事、論理Surface、SOZA内外の境界、Minimum Usable Product Shapeを定めます。

### `vision/SOZA_PRODUCT_VISION.md` / `principles/SOZA_PRODUCT_PRINCIPLES.md`

長期的な到達方向と、繰り返し現れる設計判断の原則を定めます。未定領域ではOpen Question、実証、Candidate Requirement、Stable Requirementを分離します。

### `roadmap/SOZA_PRODUCT_MILESTONES.md`

SOZAをどの順序で製品として成立させるかを、期限ではなくOutcomeとEvidenceで示します。

PMS-06では、現在までに次のScoped Executable Evidenceがあります。

- E2 out-of-process reference exchange
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- E3b-P2 fixed-artifact actual TEI CLI execution
- E3b-M1a fixed KJ Atlas + deterministic model stub
- E3b-M1b fixed KJ Atlas + actual inference model
- Method Realization historical revision / portable reconstruction
- actual model artifact交換後のhistorical Application保持
- fixed model artifact下のOllama `0.32.13` / `0.32.14` runtime version交換後のhistorical Application保持

PMS-06のversion-exchange探索は現在、次の状態です。

- ISSUE-000070 — **Resolved**。fixed KJ Atlas source / Method input / model artifact / promptの下でOllama `0.32.13` / `0.32.14`をactualに交換し、same logical / different Exact Binding、historical Application不変性、portable reconstruction、Evidence + Provenance `ready-to-review`まで確認したfixed-scope Scoped Executable Evidenceがあります。
- ISSUE-000072 — **Open**。TEI executable revision A / Bを交換する探索です。revision A historical Evidence再検証、exact-B executable + exact-A fixed reference input、E2 / E3 runner、separate toolchains、stage-aware diagnosticsまで実装済みですが、revision B actual CLI / Provider Plan / current SOZA Adapter compatibilityはNot Yet Verifiedです。

最新位置は`roadmap/PMS06_CURRENT_STATE_2026-09-05.md`を参照します。ISSUE-000070のPASSをISSUE-000072のEvidenceへ流用しません。

また、ISSUE-000071ではCognitive Method成果品質の**評価境界**を確立しました。これはhuman reviewやKJ法としての成果品質がSatisfiedになったことを意味しません。

PMS-07はv0.2.0 Local Reference Product Baselineの範囲でRelease EvidenceがSatisfiedです。PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。

### `roadmap/PMS06_CURRENT_STATE_2026-09-05.md`

PMS-06の広域Product基線を置き換えず、ISSUE-000070のfixed-scope ResolutionとISSUE-000072のOpen actual境界を短く確認するsnapshotです。

```text
PMS-06 current snapshot
  != new Product Requirement
  != supported release scope expansion

ISSUE-000070 Resolved
  != arbitrary runtime portability
  != outcome quality satisfied

ISSUE-000072 repository-side ready
  != revision B actual compatibility PASS
```

### `interaction/SOZA_PRODUCT_INTERACTION.md`

PMS-03に対応するfirst usable Product Interactionについて、人間とAIがどのcanonical meaningへ接続し、どの操作を行える必要があるかを定めます。

Web UI、desktop UI、CLI、HTTP API、MCP等を先に標準化せず、利用者向け操作境界とcanonical authorityの関係を正本化します。

### `packaging/SOZA_PRODUCT_PACKAGING.md`

PMS-04に対応する最初のPackaging / Deployment boundaryを定めます。最初のprofileはLocal Single-Node Packageです。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

Linux / amd64のLocal Reference Packageはv0.2.0 release assetとして配布済みです。ただし、formal platform support matrix、production installer、signing、crash durability、production Storage migrationの成立を意味しません。

### `security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`

PMS-05に対応するIdentity / Access / Collaboration boundaryを定めます。

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

### `definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`

PMS-06に対応し、Cognitive Method RealizationやCapability Providerを交換するときに、何を交換可能とし、何を判断記憶として保つかを定めます。

E3b-P2では固定revisionの実TEI CLIをbuild・起動し、actual `deployment-provider-plan`をSOZA Adapterでstrictに読み、current Capability Observationへ戻す範囲まで確認しました。E3b-M1bではKJ Atlasの既存Method surfaceとpromptを保ったままactual model inferenceを通し、その結果を既存SOZA Method mapping boundaryへ戻せることを確認しました。

その後のversion-exchange explorationでは、Cognitive Method側のOllama runtime version交換（ISSUE-000070）と、Capability Provider側のTEI executable / Provider Plan revision交換（ISSUE-000072）を別軸として扱っています。

ISSUE-000070はfixed scopeでResolvedしました。runtime version、archive digest、model digest、prompt digestはRealization-local metadata / Provenance / Evidenceに留まり、新しいUniversal fieldは追加していません。

未検証なのは、より一般化した次の領域です。

- private artifact acquisition / credential lifecycle
- arbitrary TEI / model / runtime version compatibility
- revision B TEI executable / Provider Plan / current SOZA Adapter live compatibility
- model出力品質
- KJ法としての成果品質
- E4 Operational portability

## 3. 未定領域の扱い

未定のProduct領域は、最初からStable Requirementとして扱いません。

```text
Open Question
  → Discussion / Research / Experiment / Human Review
  → Candidate Requirement
  → Requirement audit
  → Stable Requirement / existing integration / No Change
```

詳細な進め方は`../plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`を正とします。

## 4. 具体的なScenarioの正本

具体的な利用・検証場面は、`requirements/ACCEPTANCE_SCENARIOS.md`の`SCN-*`をcurrent正本とします。Product層に第二のScenario番号体系を作りません。

```text
Product Value / V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Architecture / Contract / Test
```

Product Milestoneや各Product boundaryの項目を、そのままRequirementやScenarioへ変換しません。

## 5. 現在のProduct Milestone上の位置

current repositoryでは、少なくとも次の状態まで確認しています。

- Product Value / Value Proposition / Vision / Principles / Product Shape: **Design baseline established**
- current semantic Contract群: **Scoped Executable Evidence available**
- SCN-0018 end-to-end Semantic Product Journey: **fixture-scoped Executable Evidence available**
- first usable Product Interaction: **Design baseline established / scoped Executable Evidence available**
- Packaging / Deployment: **Design baseline established / Minimum scoped Executable Evidence available**
- Local Reference Package: **release asset available for v0.2.0 Linux / amd64 reference profile**
- Product Identity / Access / Collaboration: **Design baseline established / scoped Product Access separation Executable Evidence available**
- Realization / Provider portability: **Partial — E2 / E3a / E3b-P1 / E3b-P2 / E3b-M1a / E3b-M1b / historical reconstruction / actual model artifact exchange / fixed-scope Ollama runtime version exchangeまでScoped Executable Evidenceあり**
- Ollama runtime version exchange: **ISSUE-000070 Resolved — fixed-scope actual A/B exchange / historical reconstruction / canonical Evidence + Provenance verificationまで確認済み**
- TEI executable version exchange: **ISSUE-000072 Open — exact-B + exact-A fixed-input E2/E3 path implemented, revision B actual Not Yet Verified**
- Cognitive Method outcome quality: **evaluation boundary established / actual human review and quality judgement pending**
- PMS-07: **Satisfied for v0.2.0 Local Reference Product Baseline**
- E4 Operational portability: **Not Yet Verified**
- PMS-08 Operational / Adoption・Outcome Evidence: **Not Yet Verified**

## 6. v0.2.0 releaseと後続Evidenceの読み方

v0.2.0は、semantic baselineにProduct Interaction、Local Single-Node Packaging、Product Access責務分離、Realization / Provider交換、E3a external artifact integrationまでを加えたLocal Reference Product Baselineです。

actual releaseではtag、source commit、historical Release Candidate Gate、Local Reference Package、checksum、candidate report、release metadataを追跡できる状態で配布しました。

repositoryにはrelease後に得られたE3b-P1、E3b-P2、E3b-M1a、E3b-M1b、historical reconstruction、model artifact exchange、fixed-scope runtime version exchange等のScoped Executable Evidenceも存在します。しかし、それらを理由にv0.2.0のsupported scopeを後から広げません。

```text
post-release scoped Evidence exists
  != v0.2.0 supported scope expanded
```

E3b-M1bやISSUE-000070ではactual inferenceまで確認しましたが、execution成立と成果品質を分けます。

```text
actual inference / runtime exchange PASS
  != external model quality proven
  != KJ-method outcome quality proven
```

## 7. Product Valueを変更するとき

Product ValueやValue Modelの意味変更は、通常の実装変更より重く扱います。

少なくとも、反証Evidence、影響するMilestone / Requirement / SCN / ADR / Architecture / Contract、過去判断との互換性、再検討条件を確認します。詳細はADR-0018を正とします。

## 8. 新しい概念をCoreへ入れる前に

Product文書やMilestoneから新しいUniversal Core概念が自動的に生えるわけではありません。

Coreへ追加する前に、少なくとも次を検討します。

- Providerが変わっても同じ意味が必要か。
- 複数domainで同じ意味境界が反復するか。
- 判断、責任、不確実性、来歴の再構成に不可欠か。
- Reference、Profile、Adapter、Provider、domain-specific knowledgeで扱えないか。
- 評価時点から10〜50倍程度先を見ても意味上の必要性が残るか。

現在の実装で便利であることや、関連製品との距離が近いことだけをCore昇格理由にしません。

## 9. 推奨する読む順序

1. `value/SOZA_PRODUCT_VALUE.md`
2. `value/SOZA_VALUE_PROPOSITION.md`
3. `value/SOZA_VALUE_MODEL.md`
4. `value/SOZA_VALUE_ACCEPTANCE.md`
5. `definition/SOZA_PRODUCT_SHAPE.md`
6. `vision/SOZA_PRODUCT_VISION.md`
7. `principles/SOZA_PRODUCT_PRINCIPLES.md`
8. `roadmap/SOZA_PRODUCT_MILESTONES.md`
9. `roadmap/PMS06_CURRENT_STATE_2026-09-05.md`
10. `interaction/SOZA_PRODUCT_INTERACTION.md`
11. `packaging/SOZA_PRODUCT_PACKAGING.md`
12. `security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
13. `definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`
14. `value/SOZA_VALUE_TRACEABILITY.md`
15. `../release/v0.2.0/RELEASE_ACCEPTANCE.md`
16. `../release/v0.2.0/RELEASE_EVIDENCE.md`
17. `../plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
18. `../requirements/PRODUCT_REQUIREMENTS.md`
19. `../requirements/ACCEPTANCE_SCENARIOS.md`
20. `../architecture/TRACEABILITY.md`
21. `../contracts/TRACEABILITY.md`

## 10. Natural Japanese review

2026-09-05時点のProduct Value、Value Proposition、Value Model / Acceptance、Product Shape、Vision / Principles、Product Milestones、PMS-06 current snapshot、Interaction、Packaging、Identity / Access / Collaboration、Realization / Provider Exchange、v0.2.0 Release Evidence、E3b-P2、E3b-M1a / M1b、ISSUE-000067〜000072へ戻ってProduct文書の入口を再監査しました。

旧文書に残っていた「SOZA Actionsからprivate TEIを取得するcredential運用」という実行面固有の表現は、private artifact acquisition / credential lifecycleというProduct側の未検証境界へ既に戻しています。GitHub Actionsは当面完全停止しており、その停止自体をProduct semanticsへ持ち込みません。

ISSUE-000070は、回収済みactual A/B Evidenceとcurrent-contract Git object equivalence監査によりfixed scopeでResolvedしました。これによりCognitive Method側のruntime version交換について、actual bytes / binary version / model identity / same prompt / A/B inference / Exact Binding / historical Application不変性 / portable reconstructionまでScoped Executable Evidenceがあります。一方、成果品質、任意runtime portability、E4 Operational portabilityは未成立のままです。

Capability Provider側のTEI executable version交換（ISSUE-000072）は引き続きOpenです。revision B actual CLI / Provider Plan / current SOZA Adapter compatibilityはNot Yet Verifiedであり、ISSUE-000070のPASSをそのEvidenceへ流用しません。

historical reconstruction、actual model artifact交換、ISSUE-000071の成果品質評価境界も現在地を維持しています。human outcome reviewは未完了のままであり、version交換PASSから成果品質へ自動昇格させません。

v0.2.0のRelease EvidenceはLocal Reference Product Baselineに限定してSatisfiedとし、release後のEvidenceをsupported scopeへ遡及させません。意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語として現在地をたどれることを最重要視して再監査しました。
