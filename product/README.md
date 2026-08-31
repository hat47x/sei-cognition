# SOZA Product文書の読み方

更新日: 2026-08-31  
状態: **Current Product Documentation Baseline**

## 1. この文書の役割

`product/`は、SOZAが**なぜ存在するのか、何を失ってはならないのか、長期的にどの方向を目指すのか**を定める上位文書の入口です。

個別の実装方式、現在のMilestone、特定Providerの都合をProduct定義へ持ち込む場所ではありません。

SOZAでは、下位設計を上位価値へ戻って検査できるよう、概ね次の依存方向を維持します。

```text
Product Value
  → Value Model / Value Acceptance
  → Vision / Principles
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Contract
  → Implementation / Test / Evidence
```

下位の実装・検証から上位仮説への反証が得られた場合は、この向きに逆らってはいけないという意味ではありません。必要ならProduct Valueまで戻って再検討します。ただし、既存実装を温存するためだけに上位価値を書き換えません。

## 2. Product文書の正本関係

### `value/SOZA_PRODUCT_VALUE.md`

SOZAが存在する理由と、最も上位で守る価値を定めます。

「何を作るか」より先に、「技術やProviderが変わっても何を失ってはいけないか」を扱います。

### `value/SOZA_VALUE_MODEL.md`

Product Valueを設計判断へ落とせる粒度に精緻化します。

現在はV1〜V8を用います。

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

少なくとも次を分離します。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

本番で安定して動作することと、利用者・組織の判断や成果に価値が届くことは別に検証します。

### `value/SOZA_VALUE_TRACEABILITY.md`

Product Valueからcurrent Requirements、Acceptance Scenarios、ADR、Architecture、Contract、Evidence gapへ戻るための索引です。

この文書は新しい意味上の正本を作るものではありません。詳細なRequirementは`requirements/`、Architectureは`architecture/`、Contractは`contracts/`を正とします。

### `vision/SOZA_PRODUCT_VISION.md`

Product Valueを長期的な到達方向として表します。

未来の特定技術を予言する文書ではありません。現在の実装方式が入れ替わっても成立してほしい製品像を扱います。

### `principles/SOZA_PRODUCT_PRINCIPLES.md`

繰り返し現れる設計判断で利用する製品原則を定めます。

PrincipleはProduct Valueより上位ではありません。Product Valueを日々の設計判断へ適用しやすくするための反復可能な指針です。

## 3. 具体的なScenarioの正本

具体的な利用・検証場面は、`requirements/ACCEPTANCE_SCENARIOS.md`の`SCN-*`をcurrent正本とします。

Product層に第二のScenario番号体系を作りません。

```text
Product Value / V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Architecture / Contract / Test
```

Product Value側では、どのScenarioがどの価値軸を具体化しているかをTraceabilityとして参照します。

## 4. 現在のEvidence状態

2026-08-31時点では、少なくとも次がactual repositoryにあります。

- Product Value / Value Model / Value Acceptance
- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017
- ADR-0001〜ADR-0021
- current Reference Architecture
- current Contract Definition
- Requirements registry checker
- Planning registry checker
- Contract v1alpha1のschema、fixture、semantic validator、conformance workflow

このため、Design Evidenceはかなり具体化し、一部の境界にはfixture-scoped Executable Evidenceもあります。

ただし、次を自動的には主張しません。

- SOZA全体のExecutable Acceptance完了
- stable Representation Profileの確立
- release readiness
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

現在のContract fixtureがPASSしたことを、Product Value全体の実証や利用者価値の実現へ拡張しません。

## 5. Product Valueを変更するとき

Product ValueやValue Modelの意味変更は、通常の実装変更より重く扱います。

少なくとも次を確認します。

1. 何が反証されたのか。
2. 変更する価値は何か。
3. V1〜V8、Requirements、SCN、ADR、Architecture、Contractのどこへ影響するか。
4. 過去の判断と互換性があるか。
5. どのEvidenceで変更の必要性を説明できるか。
6. いつ再検討するか。

詳細はADR-0018を正とします。

Value AcceptanceのEvidence区分を精緻化するときも、V1〜V8の意味を暗黙に変更していないかを確認します。

## 6. 新しい概念をCoreへ入れる前に

Product文書から新しいUniversal Core概念が自動的に生えるわけではありません。

Coreへ追加する前に、少なくとも次を検討します。

- Providerが変わっても同じ意味が必要か。
- 複数domainで同じ意味境界が反復するか。
- 判断、責任、不確実性、来歴の再構成に不可欠か。
- Reference、Profile、Adapter、Provider、domain-specific knowledgeで扱えないか。

現在の実装で便利であることや、関連製品との距離が近いことだけをCore昇格理由にしません。

## 7. 読む順序

Product層から読み始める場合は、次の順序を推奨します。

1. `value/SOZA_PRODUCT_VALUE.md`
2. `value/SOZA_VALUE_MODEL.md`
3. `value/SOZA_VALUE_ACCEPTANCE.md`
4. `value/SOZA_VALUE_TRACEABILITY.md`
5. `vision/SOZA_PRODUCT_VISION.md`
6. `principles/SOZA_PRODUCT_PRINCIPLES.md`
7. `../requirements/PRODUCT_REQUIREMENTS.md`
8. `../requirements/ACCEPTANCE_SCENARIOS.md`
9. `../architecture/TRACEABILITY.md`
10. `../contracts/TRACEABILITY.md`

## 8. 文書品質

Product文書は、内容と構造を確定した後に、意味、規範強度、留保、Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直します**。

その後、日本語を整えたことで意味が狭まったり、未検証事項が確定事項へ変わったりしていないか、最終意味監査を行います。

詳細な文書作成手順は`../plan/DOCUMENT_AUTHORING_STANDARD.md`を参照してください。

## 9. Natural Japanese review

current Product / Requirements / Architecture / Contractの正本関係とEvidence状態を確認し、重複した正本や第二のScenario体系を作らないよう役割を整理しました。その後、意味、権威関係、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
