# SOZA Product文書の読み方

更新日: 2026-09-02  
状態: **Current Product Documentation Baseline — v0.2.0 Release Evidence reflected**

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
  → Discussion / Research / Experiment
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture / Contract
  → Runtime / Adapter / Probe / Test
  → Executable Evidence
  → Release Candidate / Release Evidence
  → Operational / Adoption・Outcome Evidence
```

下位の実装・検証から上位仮説への反証が得られた場合は、必要に応じてProduct Valueまで戻って再検討します。ただし、既存実装を温存するためだけに上位価値を書き換えません。

## 2. Product文書の正本関係

### `value/SOZA_PRODUCT_VALUE.md`

SOZAが存在する理由と、最も上位で守る価値を定めます。

Product Valueから個別RequirementやUniversal型を機械的に生成しません。まだ何を要求すべきか十分に分からない領域は、議論・調査・実証を通して必要性を確認します。

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

### `vision/SOZA_PRODUCT_VISION.md`

Product Valueを長期的な到達方向として表します。未来の特定技術を予言する文書ではありません。

### `principles/SOZA_PRODUCT_PRINCIPLES.md`

繰り返し現れる設計判断で利用する製品原則を定めます。未定領域については、Open Question、実証、Candidate Requirement、Stable Requirementを分離します。

### `roadmap/SOZA_PRODUCT_MILESTONES.md`

SOZAをどの順序で製品として成立させるかを、**期限ではなくOutcomeとEvidence**で示します。

v0.2.0 Release Evidenceの成立により、PMS-07はLocal Reference Product Baselineの範囲でSatisfiedです。PMS-08のOperational / Adoption・Outcome Evidenceは未検証のままです。

### `interaction/SOZA_PRODUCT_INTERACTION.md`

PMS-03に対応するfirst usable Product Interactionについて、人間とAIがどのcanonical meaningへ接続し、どの操作を行える必要があるかを定めます。

Web UI、desktop UI、CLI、HTTP API、MCP等を先に標準化せず、利用者向け操作境界とcanonical authorityの関係を正本化します。

ISSUE-000053ではhuman-oriented Surfaceとmachine-oriented Surfaceを同じcanonical sourceへ接続し、Recommendation / Decision分離、Unknown / Conflict保持、Projectionの非権威性、historical Decision basis非改変等をreference probeで確認しました。

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

ISSUE-000056では、IdP相当identity交換後のResponsibility continuity、ResponsibilityとProduct accessの非同一性、Product adminとsemantic Responsibilityの非同一性、`denied` / `not_evaluated`、Selective Disclosureのcanonical source非改変を限定範囲で確認しています。

### `definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`

PMS-06に対応し、Cognitive Method RealizationやCapability Providerを交換するときに、何を交換可能とし、何を判断記憶として保つかを定めます。

現在はE2、E3a、E3b-P1までScoped Executable Evidenceがあります。v0.2.0のsupported release scopeはE3aまでです。

## 3. 未定領域の扱い

未定のProduct領域は、最初からStable Requirementとして扱いません。

```text
Open Question
  → Discussion / Research / Experiment
  → Candidate Requirement
  → Stable Requirement
```

詳細な進め方は`../plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`を正とします。

チャット上の議論は探索・統合の作業空間として使えますが、current正本はrepository上のProduct / Requirement / ADR等へ戻します。

## 4. 具体的なScenarioの正本

具体的な利用・検証場面は、`requirements/ACCEPTANCE_SCENARIOS.md`の`SCN-*`をcurrent正本とします。

Product層に第二のScenario番号体系を作りません。

```text
Product Value / V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Architecture / Contract / Test
```

Product Milestoneや各Product boundaryの項目を、そのままRequirementやScenarioへ変換しません。独立した規範上の必要性が確認できたものだけを下位正本へ反映します。

## 5. 現在のProduct Milestone上の位置

current repositoryでは、少なくとも次の状態まで確認しています。

- Product Value / Value Proposition / Vision / Principles / Product Shape: **Design baseline established**
- current semantic Contract群: **scoped Executable Evidence available**
- SCN-0018 end-to-end Semantic Product Journey: **fixture-scoped Executable Evidence available**
- first usable Product Interaction: **Design baseline established / scoped Executable Evidence available**
- Packaging / Deployment: **Design baseline established / Minimum scoped Executable Evidence available**
- Local Reference Package: **release asset available for v0.2.0 Linux / amd64 reference profile**
- Product Identity / Access / Collaboration: **Design baseline established / scoped Product Access separation Executable Evidence available**
- Realization / Provider portability: **Partial — E2 / E3a / E3b-P1 Scoped Executable Evidence available**
- PMS-07: **Satisfied for v0.2.0 Local Reference Product Baseline**
- production IdP / team collaboration security: **Not Yet Verified**
- E3b-P2 actual TEI process / service: **Not Yet Verified**
- E3b-M1 external Cognitive Method live execution: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- PMS-08 Operational / Adoption・Outcome Evidence: **Not Yet Verified**

v0.2.0 Release Evidenceの詳細は`../release/v0.2.0/RELEASE_EVIDENCE.md`を参照してください。

```text
v0.2.0 Release Evidence Satisfied
  != production readiness
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 6. v0.2.0 releaseの読み方

v0.2.0は、現在のsemantic baselineにProduct Interaction、Local Single-Node Packaging、Product Access責務分離、Realization / Provider交換、E3a external artifact integrationまでを加えた **Local Reference Product Baseline** です。

actual releaseでは、tag、source commit、Release Candidate Gate、Local Reference Package、checksum、candidate report、release metadataを追跡できる状態で配布しています。

一方、repositoryにはrelease scope確定後に得られたE3b-P1やTEI executable injection boundaryのScoped Evidenceも存在します。これらを理由に、v0.2.0のsupported scopeを後から広げません。

```text
later scoped Evidence exists
  != v0.2.0 supported scope expanded
```

## 7. Product Valueを変更するとき

Product ValueやValue Modelの意味変更は、通常の実装変更より重く扱います。

少なくとも次を確認します。

1. 何が反証されたのか。
2. 変更する価値は何か。
3. Milestone、V1〜V8、Requirements、SCN、ADR、Architecture、Contractのどこへ影響するか。
4. 過去の判断と互換性があるか。
5. どのEvidenceで変更の必要性を説明できるか。
6. どの条件で再検討するか。

詳細はADR-0018を正とします。

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
9. `interaction/SOZA_PRODUCT_INTERACTION.md`
10. `packaging/SOZA_PRODUCT_PACKAGING.md`
11. `security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
12. `definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`
13. `value/SOZA_VALUE_TRACEABILITY.md`
14. `../release/v0.2.0/RELEASE_ACCEPTANCE.md`
15. `../release/v0.2.0/RELEASE_EVIDENCE.md`
16. `../plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
17. `../requirements/PRODUCT_REQUIREMENTS.md`
18. `../requirements/ACCEPTANCE_SCENARIOS.md`
19. `../architecture/TRACEABILITY.md`
20. `../contracts/TRACEABILITY.md`

## 10. Natural Japanese review

Product Value、Value Proposition、Value Model / Acceptance、Product Shape、Vision / Principles、Product Milestones、Interaction、Packaging、Identity / Access / Collaboration、Realization / Provider Exchange、REQ-0001〜0022、SCN-0001〜0018、v0.2.0 Release Acceptance / Release Evidence、actual tag / GitHub Release / release assetへ戻ってProduct文書の入口を再監査しました。

旧本文に残っていた「Product Release / current Product Shape全体のRelease Evidenceは未検証」という状態を、actual v0.2.0 release後の現在地へ更新しました。ただし、成立したRelease EvidenceはLocal Reference Product Baselineに限定し、E3b全体、E4、production IdP / Storage / security、formal support matrix、Operational / Adoption・Outcome Evidenceは未検証のままです。

意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
