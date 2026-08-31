# SOZA Contract v1alpha1 Fixtures

更新日: 2026-08-31  
状態: **Fixture-scoped Executable Evidence Baseline**

## 1. このfixture群の役割

`fixtures/contracts/v1alpha1/`は、current 4 Contract familyの意味境界を、positive / negative / boundary caseとして再現する固定入力です。

fixtureそのものはContract Definitionではありません。また、fixtureが存在するだけではExecutable Evidenceになりません。

```text
Contract Definition
  != Schema
  != Fixture
  != Checker Result
```

actual checkerで期待結果を再現できた範囲を、fixture-scoped Executable Evidenceとして扱います。

## 2. Capability Observation F1〜F7

| Fixture | 主な検証 | Value Axis |
|---|---|---|
| F1 | TEIの部分劣化をCapability全体のunavailableへ潰さない | V1, V2, V4, V5 |
| F2 | proposed stateとactual stateを分ける | V1, V2, V3, V5 |
| F3 | Release存在だけでEnvironment availabilityを確定しない | V2, V4, V5 |
| F4 | not observedをunavailableへ変換しない | V2, V5 |
| F5 | TEI / SaaSをProvider-neutralに並べ、固有情報を平坦化しない | V4, V8 |
| F6 | 過去Decision時のObservation / mappingをexact bindingで再構成する | V1, V3, V4 |
| F7 | WithheldとUnknownを区別し、非開示をincompatibleへ変換しない | V2, V4, V5 |

F1〜F7はISSUE-000024で定めたRequired scenariosをcurrent Capability Observation Contractへ実体化したものです。

この7件を理由にCapability Choice全体やproduction Provider integrationを検証済みとはしません。

## 3. Boundary fixtures

### Expected PASS / semantic boundary

- `boundary/verification-not-verified.json` — verifier / Profile等が利用できず、検証を完了できない状態を`not_verified`として保持する。
- `boundary/verification-failed.json` — 検証を実施した結果の不一致・失敗を`failed`として保持する。
- `boundary/recommendation-without-decision.json` — Recommendationだけが存在する状態をDecision済みと読まない。
- `boundary/decision-with-unresolved.json` — Decision後も未解決状態を保持できる。
- `boundary/partial-knowledge-interchange.json` — Unknown / Withheld等のpartial knowledgeをmalformed dataと同一視しない。

### Expected `not_verified`

- `boundary/unknown-contract-version.json` — unknown nested Contract versionをknown Contractとして解釈しない。

## 4. Negative fixtures

### Expected Schema FAIL

- `negative/decision-authority-field.json` — DecisionへAuthorityを直接埋め込むSchema違反。
- `negative/capability-missing-observed-at.json` — Capability Observationの観測時点欠落。

### Expected Semantic FAIL

- `negative/same-logical-lineage-without-exact.json` — 同一logical identity内のrevisionでexact endpointがないsemantic invariant違反。
- `negative/interchange-mismatched-exact-binding.json` — interchange内recordとDecision basisのExact Binding不一致。

Schemaで表現できない意味上のinvariantもあるため、negative fixtureの一部はsemantic validatorで検出します。

## 5. current fixture count

current `v1alpha1` fixture setは合計17件です。

```text
Capability Observation F1〜F7 = 7
Boundary / expected PASS or NOT_VERIFIED = 6
Negative schema / semantic FAIL = 4
Total = 17
```

Contract Conformanceの代表run:

- Run ID: `33346472419`
- conclusion: **success**
- fixture count: **17**

Contracts文書の再基線化後にもRun `33389771476`および`33389973776`でContract Conformanceがsuccessし、fixture expectationsが回帰していないことを確認しています。

後続runは新しいfixture coverageを増やしたEvidenceではなく、current Contract文書の整理後も既存fixture semanticsが壊れていないことの回帰確認です。

## 6. Runtimeとの関係

first semantic runtimeは、このfixture群の一部を直接読み、schema / semantic invariantを再検査します。

```text
fixture checker PASS
  != runtime coverage complete
runtime PASS
  != production interoperability
```

fixtureはsemantic scenarioの固定入力であり、runtime実装へ意味上のauthorityを移しません。

## 7. Evidence boundary

Product Valueに従い、次を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current fixture setについては、actual checkerで期待結果が再現されているため、対象範囲のExecutable Evidenceがあります。

一方、次はこのfixture群から主張しません。

- Contract全意味領域の完全coverage
- production Provider / Storage / federation interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

Value Axisはfixtureの意味を上位価値へ追跡するための参照であり、件数や軸数をProduct Valueの点数へ変換しません。

## 8. Natural Japanese review

17 fixtureのactual checker結果、current Contract Definition、first semantic runtime、Product Valueの5段階Evidenceへ戻って役割を再監査しました。旧「Executable candidate fixtures」という表現を、actual CIで確認済みのfixture-scoped Executable Evidenceへ再基線化しつつ、fixtureの存在とContract全体の達成を分離しています。その後、各fixtureの期待結果やValue Axisを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
