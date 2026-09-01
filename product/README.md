# SOZA Product文書の読み方

更新日: 2026-09-01  
状態: **Current Product Documentation Baseline**

## 1. この文書の役割

`product/`は、SOZAが**なぜ存在するのか、何を失ってはならないのか、どのような製品状態を目指し、どこまで成立したら次の段階へ進めるのか**を定める上位文書の入口です。

個別の実装方式や特定Providerの都合をProduct定義へ持ち込む場所ではありません。期限やcalendar scheduleもここでは固定せず、Product MilestoneはOutcomeとEvidenceの成立条件で表します。

SOZAでは、概ね次の依存方向を維持します。

```text
Product Value / Value Proposition
  → Value Model / Value Acceptance
  → Vision / Principles / Product Shape
  → Deadline-free Product Milestones
  → Product Interaction / other Product boundaries
  → Open Question / Product Hypothesis
  → Discussion / Research / Experiment
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture / Contract
  → Runtime / Provider Adapter / Test
  → Evidence
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

Product Valueからcurrent Requirements、Acceptance Scenarios、ADR、Architecture、Contract、Representation Profile、runtime、Provider Adapter、Evidence gapへ戻るための索引です。

### `definition/SOZA_PRODUCT_SHAPE.md`

SOZAを製品として見たときの主要な仕事、論理Surface、SOZA内外の境界、Minimum Usable Product Shapeを定めます。

### `vision/SOZA_PRODUCT_VISION.md`

Product Valueを長期的な到達方向として表します。未来の特定技術を予言する文書ではありません。

### `principles/SOZA_PRODUCT_PRINCIPLES.md`

繰り返し現れる設計判断で利用する製品原則を定めます。未定領域については、Open Question、実証、Candidate Requirement、Stable Requirementを分離します。

### `roadmap/SOZA_PRODUCT_MILESTONES.md`

SOZAをどの順序で製品として成立させるかを、**期限ではなくOutcomeとEvidence**で示します。

historicalなM48 / M49等の実装順序とは役割が異なります。MilestoneはProduct ontologyでも固定workflowでもありません。

### `interaction/SOZA_PRODUCT_INTERACTION.md`

PMS-03に対応するfirst usable Product Interactionについて、人間とAIがどのような仕事を、どのcanonical meaningへ接続して行える必要があるかを定めます。

Web UI、desktop UI、CLI、HTTP API、MCP等を先に標準化せず、**利用者向け操作境界とcanonical authorityの関係**を正本化します。画面、chat、session、workspace等を意味上の正本へ昇格させず、人間向け・AI向けの異なるSurfaceから同じcanonical meaningへ戻れることを中心に置きます。

ISSUE-000053では、この境界を`runtime/go/interactionprobe`のreference probeで限定的に実証しました。human-oriented Surfaceとmachine-oriented Surfaceを同じcanonical sourceへ接続し、Recommendation / Decisionの分離、Unknown / Conflictの保持、Projectionの非権威性、historical Decision basisの非改変等をactual testで確認しています。

ただし、reference probeのSurfaceやin-memory storeはproduction標準ではありません。

## 3. 未定領域の扱い

未定のProduct領域は、最初からstable Requirementとして扱いません。

```text
Open Question
  → Discussion / Research / Experiment
  → Candidate Requirement
  → Stable Requirement
```

詳細な進め方は`../plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`を正とします。

チャット上の議論は探索・統合の作業空間として使えますが、current正本はrepository上のProduct / Requirement / ADR等へ戻します。

Product Interactionについても、Design boundaryとreference probeのExecutable Evidenceが成立したことと、production UI / protocol / Storage / usabilityが成立したことは分けます。実利用やPackagingから新しい意味上の必要性が確認された場合だけRequirement / Scenario追加を再検討します。

## 4. 具体的なScenarioの正本

具体的な利用・検証場面は、`requirements/ACCEPTANCE_SCENARIOS.md`の`SCN-*`をcurrent正本とします。

Product層に第二のScenario番号体系を作りません。

```text
Product Value / V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Architecture / Contract / Test
```

Product MilestoneやProduct Interactionの各項目も、そのままRequirementやScenarioへ変換しません。独立した規範上の必要性が確認できたものだけを下位正本へ反映します。

## 5. 現在のProduct Milestone上の位置

current repositoryでは、少なくとも次の状態まで確認しています。

- Product Value / Value Proposition / Vision / Principles / Product Shape: **Design baseline established**
- current semantic Contract群: **scoped Executable Evidence available**
- SCN-0018 end-to-end Semantic Product Journey: **fixture-scoped Executable Evidence available**
- first usable Product Interaction: **Design baseline established / scoped Executable Evidence available**
- packaged product: **Not Yet Verified**
- Product Identity / Authorization / Collaboration: **Not Yet Verified**
- real Method / Provider portability: **Partial**
- current Product Shape全体のRelease Evidence: **Not Yet Verified**
- Operational / Adoption Outcome: **Not Yet Verified**

Product Interactionについては、`interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028でDesign boundaryを正本化し、ISSUE-000053の`runtime/go/interactionprobe`でhuman-oriented / machine-oriented Surfaceが同じcanonical sourceへ接続できることを限定範囲で確認しました。詳細なEvidenceは`../runtime/INTERACTION_PROBE_EVIDENCE_2026-09-01.md`を参照してください。

このprobeのPASSから、production UIの使いやすさ、supported protocol、Packaging、Operational / Adoption Evidenceを推定しません。

## 6. Product Valueを変更するとき

Product ValueやValue Modelの意味変更は、通常の実装変更より重く扱います。

少なくとも次を確認します。

1. 何が反証されたのか。
2. 変更する価値は何か。
3. Milestone、V1〜V8、Requirements、SCN、ADR、Architecture、Contractのどこへ影響するか。
4. 過去の判断と互換性があるか。
5. どのEvidenceで変更の必要性を説明できるか。
6. どの条件で再検討するか。

詳細はADR-0018を正とします。

## 7. 新しい概念をCoreへ入れる前に

Product文書やMilestoneから新しいUniversal Core概念が自動的に生えるわけではありません。

Coreへ追加する前に、少なくとも次を検討します。

- Providerが変わっても同じ意味が必要か。
- 複数domainで同じ意味境界が反復するか。
- 判断、責任、不確実性、来歴の再構成に不可欠か。
- Reference、Profile、Adapter、Provider、domain-specific knowledgeで扱えないか。
- 評価時点から10〜50倍程度先を見ても意味上の必要性が残るか。

現在の実装で便利であることや、関連製品との距離が近いことだけをCore昇格理由にしません。

Product Interaction上の`Case`、`Session`、`Workspace`、`Thread`等についても、UI上便利という理由だけでUniversal Coreへ追加しません。reference probeの`CanonicalStore`やSurface DTOも同様です。

## 8. 推奨する読む順序

1. `value/SOZA_PRODUCT_VALUE.md`
2. `value/SOZA_VALUE_PROPOSITION.md`
3. `value/SOZA_VALUE_MODEL.md`
4. `value/SOZA_VALUE_ACCEPTANCE.md`
5. `definition/SOZA_PRODUCT_SHAPE.md`
6. `vision/SOZA_PRODUCT_VISION.md`
7. `principles/SOZA_PRODUCT_PRINCIPLES.md`
8. `roadmap/SOZA_PRODUCT_MILESTONES.md`
9. `interaction/SOZA_PRODUCT_INTERACTION.md`
10. `../plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`
11. `../requirements/PRODUCT_REQUIREMENTS.md`
12. `../requirements/ACCEPTANCE_SCENARIOS.md`
13. `../architecture/TRACEABILITY.md`
14. `../contracts/TRACEABILITY.md`

## 9. 文書品質

Product文書は、内容と構造を確定した後に、意味、規範強度、留保、Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直します**。

その後、日本語を整えたことで意味が狭まったり、未検証事項が確定事項へ変わったりしていないか、最終意味監査を行います。

詳細な文書作成手順は`../plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。

## 10. Natural Japanese review

current Product Value、Value Proposition、Product Shape、Product Milestone、Product Journey、Product Interaction baseline、ISSUE-000053のreference probeとcurrent Evidenceを確認し、Product Interactionの状態をDesign baselineだけでなくscoped Executable Evidenceが得られた段階へ同期しました。一方、reference probeの成功をproduction UX、supported protocol、Storage、Packaging、Operational / Adoptionへ広げていません。画面やchat、probe固有DTO等の都合からUniversal概念を増やさない境界も維持しています。そのうえで、Product Value、Milestone、Requirement、Implementationの権威関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。