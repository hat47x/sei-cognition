# SOZA Contract v1alpha1 Fixtures

更新日: 2026-09-01  
状態: **Fixture-scoped Executable Evidence Baseline**

## 1. このfixture群の役割

`fixtures/contracts/v1alpha1/`は、current 5 Contract familyの意味境界をpositive / negative / boundary caseとして再現する固定入力です。

fixtureそのものはContract Definitionではありません。また、fixtureが存在するだけではExecutable Evidenceになりません。

```text
Contract Definition
  != Schema
  != Fixture
  != Checker Result
```

actual checkerで期待結果を再現できた範囲だけをfixture-scoped Executable Evidenceとして扱います。

## 2. Capability Observation F1〜F7

| Fixture | 主な検証 | Value Axis |
|---|---|---|
| F1 | TEIの部分劣化をCapability全体のunavailableへ潰さない | V1, V2, V4, V5 |
| F2 | proposed stateとactual stateを分ける | V1, V2, V3, V5 |
| F3 | Release存在だけでEnvironment availabilityを確定しない | V2, V4, V5 |
| F4 | not observedをunavailableへ変換しない | V2, V5 |
| F5 | TEI / SaaSをProvider-neutralに並べ、固有情報を平坦化しない | V4, V8 |
| F6 | 過去Decision時のObservation / mappingをExact Bindingで再構成する | V1, V3, V4 |
| F7 | WithheldとUnknownを区別し、非開示をincompatibleへ変換しない | V2, V4, V5 |

F1〜F7だけを理由にCapability Choice全体やproduction Provider integrationを検証済みとはしません。

## 3. Cognitive Method C1〜C8

| Fixture | 主な検証 | 関連Scenario |
|---|---|---|
| C1 | Method Definitionを独立recordとして表す | SCN-0005 |
| C2 | Method RealizationがMethodをReferenceする | SCN-0005 |
| C3 | ApplicationがMethod / Realizationを分離して参照する | SCN-0005 |
| C4 | Realization未記録を不存在・未適用へ読み替えない | SCN-0005 |
| C5 | Patternをdomain-specific input Referenceのまま保持する | SCN-0015 |
| C6 | Method / RealizationのExact Binding metadataを保持する | SCN-0005, SCN-0015 |
| C7 | output / residualを別Referenceとして保持する | SCN-0005 |
| C8 | current Semantic Interchange内のMethod Applicationをtyped validationする | SCN-0005, SCN-0015 |

基本境界:

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance

Pattern != Cognitive Method
```

C1〜C8はMethodのportable meaningに対するfixtureです。Method executorや結論品質を検査するものではありません。

## 4. Boundary fixtures

### Expected PASS / semantic boundary

- `boundary/verification-not-verified.json` — 検証を完了できない状態を`not_verified`として保持する。
- `boundary/verification-failed.json` — 実際に不一致を確認した状態を`failed`として保持する。
- `boundary/recommendation-without-decision.json` — Recommendationだけの状態をDecision済みと読まない。
- `boundary/decision-with-unresolved.json` — Decision後も未解決状態を保持する。
- `boundary/partial-knowledge-interchange.json` — Unknown / Withheld等をmalformed dataと同一視しない。

### Expected `not_verified`

- `boundary/unknown-contract-version.json` — unknown nested Contract versionをknown Contractとして解釈しない。
- `boundary/unknown-cognitive-method-version.json` — unknown Cognitive Method versionをcurrent v1alpha1として推測解釈せず、opaque payloadを保持する。

```text
unknown version != failed != current version
```

## 5. Negative fixtures

### Expected Schema FAIL

- `negative/decision-authority-field.json` — DecisionへAuthorityを直接埋め込む。
- `negative/capability-missing-observed-at.json` — Capability Observationの観測時点がない。
- `negative/cognitive-method-decision-field.json` — Method ApplicationへDecisionを直接埋め込む。
- `negative/cognitive-method-assurance-field.json` — Method ApplicationへAssuranceを直接埋め込む。
- `negative/cognitive-method-realization-missing-method-ref.json` — RealizationがMethodを参照しない。
- `negative/cognitive-method-application-missing-method-ref.json` — ApplicationがMethodを参照しない。
- `negative/cognitive-method-pattern-field.json` — Pattern固有表現をCognitive Method recordへ直接取り込む。

### Expected Semantic FAIL

- `negative/same-logical-lineage-without-exact.json` — 同一logical identity内revisionにExact endpointがない。
- `negative/interchange-mismatched-exact-binding.json` — bundle内recordとDecision basisのExact Bindingが一致しない。

Schemaで自然に表せないcross-record invariantはsemantic validatorで検出します。

## 6. current fixture count

current `v1alpha1` fixture setは合計31件です。

```text
Capability Observation F1〜F7 = 7
Cognitive Method C1〜C8 = 8
Boundary / expected PASS or NOT_VERIFIED = 7
Negative schema / semantic FAIL = 9
Total = 31
```

Contract Conformanceのcurrent代表run:

- Run ID: `33467838961`
- conclusion: **success**
- fixture count: **31**

同じHEADのSemantic Runtime Conformance:

- Run ID: `33467838941`
- conclusion: **success**

2026-08-31の17-fixture runはhistorical Executable Evidenceとして残りますが、current 31-fixture baselineの代わりにはしません。

## 7. Runtimeとの関係

Go semantic runtimeは、このfixture群を使ってknown Contractをread / validate / reconstructします。

Cognitive Methodについては、C1〜C7 standaloneとC8 nested Interchangeをruntime testへ接続しています。

確認している範囲:

- typed Method Definition / Realization / Application
- Reference preservation
- Exact Binding metadata preservation
- Realization省略の非推論
- Pattern Referenceの非昇格
- output / residual保持
- unknown Method versionのopaque + `not_verified`
- Interchange original bytesのlossless export

```text
fixture checker PASS
  != runtime coverage complete
runtime PASS
  != Method execution
runtime PASS
  != production interoperability
```

fixtureはsemantic scenarioの固定入力であり、runtime実装へ意味上のauthorityを移しません。

## 8. ISSUE-000049との関係

C6によりCognitive MethodのExact Reference自体は表現・読込可能です。一方、bundle内exact-bound recordとknown ContractのExact ReferenceをContract横断で整合検査する一般化は、ADR-0026 / ISSUE-000049で別途扱います。

```text
Exact Reference preserved
  != every known Contract role has bundle-local consistency check
```

ISSUE-000049はOpenなので、その一般化を31-fixture current PASSへ先取りしません。

## 9. Evidence boundary

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current fixture setについてはactual checkerで期待結果が再現されているため、対象範囲のExecutable Evidenceがあります。

このfixture群から次は主張しません。

- Contract全意味領域の完全coverage
- Method execution / quality / Assurance
- ISSUE-000049の一般化完了
- production Provider / Storage / federation interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

Value Axisやfixture件数はtraceabilityのための参照であり、Product Valueの点数ではありません。

## 10. Natural Japanese review

current 31 fixture、5 Contract Definition、Contract checker、Cognitive Method typed runtime、actual Run `33467838961` / `33467838941`、Product Valueの5段階Evidenceへ戻って役割を再監査しました。そのうえで、Cognitive Method C1〜C8とunknown future versionをcurrent fixture baselineへ統合し、fixture PASSをMethod実行やproduction成立へ拡張しない形に整理しました。最後に、各fixtureの期待結果と意味境界を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
