# SOZA Value Traceability

更新日: 2026-09-02  
状態: **Current Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Semantic Contract、Representation Profile、runtime、Provider / Storage / Interaction probe、Projection Evaluation、Product Journey、Release Candidate Gate、現在のEvidence状態まで上位から追跡するための索引です。

新しい意味上の正本は作りません。詳細は次を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Value Proposition: `SOZA_VALUE_PROPOSITION.md`
- Product Shape: `../definition/SOZA_PRODUCT_SHAPE.md`
- Evidence受入れ境界: `SOZA_VALUE_ACCEPTANCE.md`
- Requirement: `../../requirements/PRODUCT_REQUIREMENTS.md`
- Acceptance Scenario: `../../requirements/ACCEPTANCE_SCENARIOS.md`
- Product Journey composition: `../../requirements/PRODUCT_JOURNEY_COMPOSITION.md`
- Architecture: `../../architecture/SOZA_REFERENCE_ARCHITECTURE.md`, `../../architecture/TRACEABILITY.md`
- Contract: `../../contracts/TRACEABILITY.md`, `../../contracts/CONTRACT_CATALOG.md`
- Representation Profile: `../../contracts/profiles/`
- runtime: `../../runtime/go/`
- Product Journey harness: `../../runtime/go/journeyharness/`
- V6 / V7 evaluation: `../../evaluation/v6-v7/`
- release acceptance: `../../release/v0.1.0/RELEASE_ACCEPTANCE.md`
- ADR / Issue: `../../plan/`

この追跡表が埋まっていること自体をProduct Valueの達成とはみなしません。

## 2. 追跡の基本形

```text
Product Value / Value Proposition / Product Shape
  → V1〜V8
  → REQ-*
  → SCN-*
  → ADR / Issue
  → Architecture concern
  → Semantic Contract / Representation Profile
  → Runtime / Adapter / Payload Source / Projection / Probe / Journey harness
  → Fixture / Test / CI / Release Candidate Gate
  → Evidence state
```

関係は多対多です。リンク数やcoverage率をProduct ValueのKPIにはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | current executable material |
|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016, 0018 | Semantic Reference / Decision Memory / Interchange、Exact Binding、Cognitive Method、Verifier / Payload Source、Product Journeyのhistorical-basis非改変、known Contract横断bundle-local consistency |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016, 0018 | Recommendation / Decision / Authority分離、Unknown / Withheld、Cognitive Method分離、Responsibility分離、unknown Contract非推測解析 |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016, 0018 | lineage / Exact Binding invariant、Representation Profile、Cognitive Method exact refs、複数exact revision保持、historical basis非改変 |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014, 0018 | Capability Observation、synthetic Provider Adapter、Provider replacement journey、out-of-process realization provider exchange probe |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016, 0018 | Unknown / Conflict / Withheld / partial knowledge、missing→unknown、Decision residual→reopen path |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | human-readable Contract、machine-readable schema、light / audit Projection、first Product Interaction reference probe |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | low-impact / high-impact Projection evaluation、canonical operationとInteractionの分離 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015, 0018 | provider-neutral Contract、Cognitive Method、Payload Source、no-execution journey、local package / storage migration probe、out-of-process realization provider exchange |

表中のmaterialが存在しても、そのValue Axis全体のExecutable AcceptanceがSatisfiedになったとは読みません。

## 4. Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0018`です。

```text
Requirement != Acceptance Scenario != Test Case
```

SCN-0018は個別Scenarioを置き換えません。InquiryからDecision、外部実行、実行後Observation、historical review / reopenまでを代表的な一つのProduct Journeyとして接続し、複数の意味境界が同時に失われないことを検査します。

## 5. Contract / Representation baseline

current Semantic Contractは5 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

current v1alpha1 fixture baselineは39件です。

```text
Capability Observation F1〜F7 = 7
Cognitive Method C1〜C8 = 8
Boundary / expected PASS or NOT_VERIFIED = 12
Negative schema / semantic FAIL = 12
Total = 39
```

39件基線の代表CI:

- Contract Conformance `33527512045`: **success**
- Semantic Runtime Conformance `33527512016`: **success**
- Plan integrity `33527511976`: **success**
- V6 V7 Projection Evaluation `33527511966`: **success**
- Local Package Artifact `33527511934`: **success**

Representation ProfileはSemantic Contractと別のversion空間を持ちます。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

```text
Semantic Contract
  != Representation Profile
  != verifier implementation
```

historical M47 digest ruleはISSUE-000034の方針どおり、直接Evidenceから回収できない範囲を`not_verified`として維持します。

## 6. known Contract横断のbundle-local Exact Binding consistency

ADR-0026 / ISSUE-000049により、Decision `basis_refs`専用だったbundle-local Exact Binding比較を、current runtimeが理解するknown typed ContractのReference roleへ一般化しました。

対象にはDecision Memory、Cognitive Method、Capability Observation、Semantic Referenceを含みます。

```text
known typed Contract
  → typed Exact Reference extraction
  → logical identityごとの複数Exact Binding index
  → common bundle-local consistency check
```

### V1 / V3に対する意味

同じlogical identityに複数revisionが存在する場合でも、latest-winsで一つへ潰さず、Referenceが指すexact revisionを候補の一つとして検査できます。

これにより、「現在版が存在する」ことから「過去のReferenceも現在版を指していた」と読み替える危険を減らします。

### 明確な境界

bundle内に同じlogical identityのexact-bound recordが存在しない場合、この検査だけを理由にFAILとしません。

```text
bundle-local consistency
  != external payload acquisition
  != digest verification
  != Verification Outcome
```

外部bytesの取得はPayload Source、digest再計算はVerifier Registryの責務です。

unknown ContractのpayloadにExact Bindingらしいfieldがあっても、field名から推測解析しません。unknown versionはopaque + `not_verified`を維持します。

## 7. semantic runtime / Provider / Storage

semantic runtimeはread / validate / reconstructを中核にし、SOZA自身をworkflow / agent execution engineへしません。

current scoped material:

- known Contract typed runtime
- Representation Verifier Registry
- synthetic Payload Source
- synthetic Provider Adapter
- Cognitive Method typed runtime
- known Contract横断bundle-local Exact Binding consistency
- out-of-process realization provider exchange probe
- packaged resume / storage migration probe

これらのprobeやruntime PASSは、production Provider / Storageの運用成立を意味しません。

## 8. Product Interaction / Access / Packaging

Product Shapeの外側を明確にするため、現行Planでは次の設計・reference probeもResolvedになっています。

- first usable Product Interaction boundary / reference probe
- v0.2.0 packaging / deployment boundary
- local single-node package artifact
- packaged resume / storage migration probe
- Product Identity / Authorization / Collaboration boundary
- Product access / collaboration probe

これらは、SOZAの耐久的意味を特定UI、process、identity provider、package mechanicsへ固定しないためのscoped Executable Evidenceです。

```text
reference probe PASS
  != production UX validated
  != production authorization validated
  != operational deployment validated
```

## 9. V6 / V7 Projection evaluation

light / audit Projectionを同じcanonical sourceから生成し、semantic question setとnegative caseで意味境界を検査しています。

これはstatic / synthetic evaluation-harness scoped Executable Evidenceです。実利用者の理解可能性、入力負担、見落とし率、production UXのOperational / Adoption Evidenceではありません。

## 10. end-to-end Semantic Product Journey

`runtime/go/journeyharness`はSCN-0018をsynthetic semantic Product Journeyとして検査します。

主な確認範囲:

- normal / uncertain / collaborative / provider replacement / no-execution
- RecommendationとDecisionの分離
- Responsibility分離
- execution後Observationの時間境界
- historical Decision statement / basisの非改変
- unresolved → reopen
- unsupported recordのopaque + `not_verified`
- Projectionがcanonical Decisionを代替しないこと

```text
fixture-scoped Product Journey PASS
  != production Product Journey validated
  != human interaction validated
```

## 11. Evidenceの現在地

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Design Evidence

Product Value、Value Proposition、Product Shape、REQ-0001〜0022、SCN-0001〜0018、current ADR群、Reference Architecture、5 Contract family、2 Representation Profile、Interaction / Access / Packaging boundary等があります。

### Executable Evidence — scoped

- Plan / Requirements structural conformance
- current 39-fixture Contract conformance
- semantic runtime
- Representation Profile / Verifier Registry
- synthetic Payload Source / Provider Adapter
- Cognitive Method typed runtime
- known Contract bundle-local Exact Binding consistency
- V6 / V7 Projection evaluation
- Product Journey harness
- Product Interaction / Packaging / Storage / Access / out-of-process Providerのreference probe
- v0.1.0 Release Candidate Gate

### Release Evidence

**Not Yet Verified**

actual release identityと、そのrelease対象source / artifact / gateを結ぶProduct Value上のRelease Evidenceは、ここでは成立済みと主張しません。

### Operational Evidence

**Not Yet Verified**

### Adoption / Outcome Evidence

**Not Yet Verified**

## 12. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

bundle-local Exact Binding整合、historical basis非改変、Payload Source / Verifier境界はscopedに検査済みです。production Storage、長期間のProvider / representation変更をまたぐhistorical reconstructionと、実際の再判断への寄与は未検証です。

### V2 Semantic Separation

主要な意味分離はfixture / runtimeで検査しています。production責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

同一logical identityの複数Exact Bindingを保持し、参照先revisionをlatest-winsで潰さない境界を追加で検査しました。cross-bundleの実payload検証や長期Storage revisionは未検証です。

### V4 Provider Independence

synthetic Adapter、Provider replacement journey、out-of-process realization provider exchangeはscopedに検査済みです。実Providerの交換・廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / residual / reopenの境界はscopedに検査済みです。実際の誤判断回避や再検討品質へのOutcome Evidenceはありません。

### V6 Human / AI Readability

ProjectionとInteraction reference probeはありますが、実利用者・異なるAI実装による理解度Evidenceはありません。

### V7 Progressive Explicitness

low-impact / high-impactのsynthetic evaluationはあります。実運用でのimpact判定、入力負担、見落とし率は未検証です。

### V8 Execution Independence

Provider / Storage / Realization交換のscoped probeは増えました。異なるproduction Execution / Storage Provider間で長期的に意味を維持したOperational Evidenceはありません。

## 13. current Planとの関係

current registryはADR-0001〜0030、ISSUE-000001〜000057を管理します。

主要状態:

- ISSUE-000021: **Deferred** — design history provenance逐語監査
- ISSUE-000049: **Resolved** — known Contract横断bundle-local Exact Binding consistency
- ISSUE-000001〜000020、000022〜000057: **Resolved**

IssueがResolvedであることは、その対象についてRelease / Operational / Adoption・Outcome EvidenceまでVerifiedであることを意味しません。

## 14. CoverageをKPIにしない

次の読み方をしません。

- REQリンクが多いValue Axisほど重要である。
- Contractやfixtureが多いほどProduct Valueが高い。
- CIが多く通るほど利用者価値が高い。
- Executable Evidenceが増えればRelease / Operational / Outcomeも自動的に増える。
- IssueがResolvedなら、その対象がすべてVerifiedである。
- reference probeやProduct Journey fixtureが通ればproduct usabilityやbusiness outcomeが証明されたことになる。

追跡の目的は、**どこまで確認したかと、どこから先をまだ主張してはいけないかを見失わないこと**です。

## 15. 更新規則

Product Value、Value Proposition、Product Shape、REQ、SCN、ADR、Architecture、Contract、Profile、runtime、各probe、Projection Evaluation、Product Journey、release candidate、Evidence stateのいずれかが変わった場合、この文書を必要に応じて更新します。

下位実装の都合に合わせてProduct Valueを後付けで変更しません。上位仮説を変える必要がある場合はADR-0018の再基線化規則に従います。

## 16. Natural Japanese review

V1〜V8、Value Proposition、Product Shape、REQ-0001〜0022、SCN-0001〜0018、current ADR / Issue registry、5 Semantic Contract family、39-fixture baseline、2 Representation Profile、semantic runtime、Verifier / Payload Source、Provider / Storage / Interaction / Accessのscoped probe、V6/V7 Projection evaluation、end-to-end Product Journey、v0.1.0 Release Candidate Evidenceへ戻って追跡を再確認しました。ISSUE-000049については、actual 39-fixture Contract ConformanceとSemantic Runtime Conformanceで確認したknown Contract横断bundle-local consistencyだけをV1 / V3のExecutable Evidenceへ反映し、external payload verificationやproduction historical reconstructionへは昇格させていません。そのうえで、Issue closureとVerification、Design / Executable / Release / Operational / Adoption・OutcomeのEvidence強度を混同せず、自然な日本語となることを重要視して全文を再ドラフトし、最終意味監査を実施済みです。
