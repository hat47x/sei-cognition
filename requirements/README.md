# SEI Requirements

更新日: 2026-09-16  
状態: **Current Requirements Baseline**

## 1. このディレクトリの役割

`requirements/`では、SEIの製品価値を満たすために**何が必要か**を定めます。

製品価値や長期的な構想そのものは、ここでは定義しません。また、具体的な全体構成や実装方式を先に固定することもしません。

概念上の関係は次のとおりです。

```text
Product Value / Value Model / Value Acceptance / Product Shape
  ↓
Requirements / Acceptance Scenarios
  ↓
Issue / ADR
  ↓
Architecture
  ↓
Contract / Representation Profile
  ↓
Runtime / Provider Adapter / Fixture / Test
  ↓
Evidence
```

要求（Requirement）では主に、何が必要か、なぜ必要か、どのような制約があるかという`what / why / constraint`を扱います。設計上の判断はADR、構造は全体構成の文書、他の実装との接続条件は契約に分けて記録します。

## 2. Current canonical files

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  PRODUCT_JOURNEY_COMPOSITION.md
  history/
    HISTORICAL_REQUIREMENT_MAPPING.md
```

- `PRODUCT_REQUIREMENTS.md` — 現行の製品要求を記録する正本の入口
- `ACCEPTANCE_SCENARIOS.md` — 現行の受入場面を記録する正本の入口
- `PRODUCT_JOURNEY_COMPOSITION.md` — 製品の形を既存のREQ・SCNと照合し、一連の利用過程で要求の重複や不足がないか分析する補助文書
- `history/HISTORICAL_REQUIREMENT_MAPPING.md` — 過去の要求候補と現行の設計基準との意味上の対応

`PRODUCT_JOURNEY_COMPOSITION.md`は、新しい要求や受入場面を定める第二の正本ではありません。分析で見つかった内容を安定した要求や受入場面として採用する場合は、`PRODUCT_REQUIREMENTS.md`または`ACCEPTANCE_SCENARIOS.md`へ反映します。

将来、要求や受入場面を個別のファイルに分ける場合も、確定した識別子は維持します。

## 3. Stable ID

Product Requirement:

```text
REQ-0001 ... REQ-9999
```

Acceptance Scenario:

```text
SCN-0001 ... SCN-9999
```

識別子には、価値の軸、マイルストーン、種類、状態、中核かプロファイルかといった分類を埋め込みません。

## 4. Requirement、Scenario、Testを分ける

```text
Requirement != Acceptance Scenario != Test Case
```

- Requirement — 何が必要かを定める。
- Acceptance Scenario — どのような状況で、その条件に基づく意味の区別が必要になるかを示す。
- Test Case / Fixture — 実際の実装を使い、受入場面をどのように再現して検査するかを定める。

一つの受入場面で複数の要求を同時に検証しても構いません。試験用データによる検査が合格しても、受入場面全体が満たされたとは限りません。確認できた範囲を明示します。

SCN-0018のような統合Scenarioは、既存Scenarioを置き換えるものではありません。個別の意味境界が一つのProduct Journeyでも同時に保たれることを検査します。

SCN-0019のように、利用者とのやり取りで見つかった問題を安定した要求にする場合も、トランザクション、スナップショットトークン、ETagなどの実装方式を、そのまま汎用的な要求にはしません。Requirementには失ってはならない意味だけを残します。

## 5. Product Valueとの追跡

current Requirementは、原則として`SEI_VALUE_MODEL.md`のV1〜V8、または明示的なProduct Principle / external constraintへ追跡します。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

八つの価値軸を形式的にすべて付けるのではなく、実際に関係する軸だけを示します。

上位からの横断的な索引は`product/value/SEI_VALUE_TRACEABILITY.md`を参照します。

製品の形から要求を導く際も、画面構成や操作方法を、そのまま汎用的な要求にしません。まず既存REQとの重複を確認し、既存の規範で表現できない独立した必要性がある場合だけ新しいREQを追加します。

## 6. Requirement statusとEvidenceを分ける

Requirementの意味上の状態には、たとえば次を用います。

- `Proposed`
- `Accepted`
- `Rejected`
- `Superseded`
- `Deprecated`

一方、Evidenceの高さはProduct Value Acceptanceに従い、次の5段階を分けます。

1. Design Evidence
2. Executable Evidence
3. Release Evidence
4. Operational Evidence
5. Adoption / Outcome Evidence

各高さでは必要に応じて次の状態を用います。

- `Satisfied`
- `Partially Satisfied`
- `Not Satisfied`
- `Not Yet Verified`
- `Not Applicable`

```text
Requirement Accepted
  != Executable Evidence Satisfied
  != Release Evidence Satisfied
  != Operational Evidence Satisfied
  != Adoption / Outcome Evidence Satisfied
```

個別の契約、実行環境、外部の提供元との接続がそれぞれ検査に合格していても、その結果を足し合わせただけで、一連の製品利用について受入条件を満たしたとは判断しません。

## 7. current actual repositoryのEvidence

現在のactual repositoryには、Product / Plan / Requirementsに加えて、Reference Architecture、5 Contract family、JSON Schema、Contract fixture、Representation Profile、Go first semantic runtime、synthetic Provider Adapter、end-to-end Product Journey harness、Product Interaction probe、各checker / CIが存在します。

主なscoped Executable Evidence:

- Requirements Registry Conformance
- Contract Conformance
- Capability Observation F1〜F7
- Representation Profile Conformance
- first Semantic Runtime Conformance
- synthetic Provider Adapter Conformance
- V6 / V7 Projection Evaluation
- end-to-end Semantic Product Journey harness

これらの検査結果を、すべての要求が満たされた証拠として一律に扱うことはしません。Requirement / Scenarioごとに実際に触れている意味境界だけを`Partially Satisfied`等へ更新します。

SCN-0018のend-to-end Product Journeyにはfixture-scoped harness Evidenceがあり、Scenario全体は`Partially Satisfied`として扱います。本番環境での一連の利用や、利用者にもたらした成果が検証済みになったとは扱いません。

REQ-0023 / SCN-0019についてはinteraction probeとtest sourceが存在しますが、Stable化時点でcurrent Requirement / Scenarioへ結び付けたactual test runを確認していないため、Executable Evidenceは`Not Yet Verified`のままです。

リリース、運用、普及・成果に関する検証は、それぞれ実際の根拠が確認できた段階についてのみ成立したと主張します。

## 8. Historical candidateの扱い

2026-08-30前後のcandidateには`SEI-PR-*`、`SEI-NFR-*`、`SEI-AS-*`が存在しました。

これらから次をcurrent baselineへ自動継承しません。

- 旧ID
- `direct` / `partial` / `design_only`等の旧Evidence状態
- `VERIFIED`やhistorical local PASS
- M48 / M49 / M50等のMilestone上の位置
- old Product Boundaryに依存する型・Architecture

意味核はcurrent Product Valueへ戻って再評価し、必要なものをcurrent REQ / SCNへ統合しています。

REQ-0023 / SCN-0019はhistorical candidateの再採番ではなく、ISSUE-000073でpartial semantic commitとstale writeを具体的failureとして検討した後に追加したcurrent baselineです。

## 9. Requirement作成・更新の必須工程

1. Product Value / Value Model / Value Acceptance / Product Shapeを確認する。
2. Requirementとして必要な意味差を定める。
3. 既存REQとの重複を確認する。
4. 関連するV1〜V8、Scenario、ADR / Issueを確認する。
5. Requirementと実装方式、Product Interaction上の都合を混同していないか確認する。
6. Evidence状態をactual evidenceへ合わせる。
7. 内容と構造を確定する。
8. **意味・強度・例外・留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。**
9. 最終意味監査を行う。
10. Requirements Registry Conformance等、対象CIがある場合はsuccessを確認する。

CIで失敗を検出した場合は、原因を解消し、合格を確認するまで後続の作業へ進みません。

## 10. 関連文書

- `product/README.md`
- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_PROPOSITION.md`
- `product/definition/SEI_PRODUCT_SHAPE.md`
- `product/value/SEI_VALUE_MODEL.md`
- `product/value/SEI_VALUE_ACCEPTANCE.md`
- `product/value/SEI_VALUE_TRACEABILITY.md`
- `product/vision/SEI_PRODUCT_VISION.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `plan/adr/ADR-0020-requirements-traceability-and-evidence-boundary.md`
- `plan/issue/ISSUE-000048-define-end-to-end-golden-journey-acceptance.md`
- `plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

## 11. Natural Japanese review

current Product Value、Product Shape、5段階Evidence、REQ-0001〜REQ-0023、SCN-0001〜SCN-0019、Architecture / Contract / Runtime / Provider Adapter / Product Interactionのactual Evidenceへ戻って運用規則を再確認した。

ISSUE-000073のCandidate Requirement監査では、既存REQで表現できるresume、AI provisional boundary、Progressive Explicitness等を重複してStable化せず、既存Requirement本文で直接禁止できなかったpartial / stale successful commitだけをREQ-0023へ統合した。SCN-0019もtransaction方式をCore化せず、その意味差だけをAcceptanceへ固定している。

RequirementとScenarioとTestの関係、stable ID、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再監査した。
