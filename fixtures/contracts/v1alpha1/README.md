# SOZA Contract v1alpha1 Fixtures

更新日: 2026-09-02  
状態: **Fixture-scoped Executable Evidence Baseline**

## 1. このfixture群の役割

`fixtures/contracts/v1alpha1/`は、current 5 Contract familyの意味境界をpositive / negative / boundary caseとして固定し、Contract checkerとGo semantic runtimeで繰り返し検査するための入力です。

fixtureそのものはContract DefinitionでもEvidenceでもありません。actual checker / runtimeで期待結果を再現できた範囲だけをExecutable Evidenceとして扱います。

```text
Contract Definition
  != Schema
  != Fixture
  != Checker Result
```

## 2. Capability Observation F1〜F7

| Fixture | 主な検証 | Value Axis |
|---|---|---|
| F1 | TEIの部分劣化をCapability全体のunavailableへ潰さない | V1, V2, V4, V5 |
| F2 | proposed stateとactual stateを分ける | V1, V2, V3, V5 |
| F3 | Releaseの存在だけでEnvironment availabilityを確定しない | V2, V4, V5 |
| F4 | not observedをunavailableへ変換しない | V2, V5 |
| F5 | TEI / SaaSをProvider-neutralに並べ、固有情報を平坦化しない | V4, V8 |
| F6 | 過去Decision時のObservation / mappingをExact Bindingで再構成する | V1, V3, V4 |
| F7 | WithheldとUnknownを区別し、非開示をincompatibleへ変換しない | V2, V4, V5 |

F1〜F7のPASSだけを理由に、Capability Choice全体やproduction Provider integrationを検証済みとはしません。

## 3. Cognitive Method C1〜C9

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
| C9 | bundle-local Exact Binding整合を複数revision・外部参照・logical-only参照を含めて検査する | SCN-0003, SCN-0005, SCN-0010 |

C9では、同一logical identityのMethod Definitionを複数revision含むbundleで、参照したExact Bindingがそのうち一つと一致すれば成立することを確認します。同じbundleにexact-bound recordがあっても、logical-only ReferenceはExact Referenceへ自動昇格させません。また、bundle外を指すExact Referenceは、bundle内に同一logical identityが存在しないという理由だけではFAILにしません。

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance

Logical Reference != Exact Historical Binding
Pattern != Cognitive Method
```

## 4. Boundary fixtures

### Expected PASS / semantic boundary

- `boundary/verification-not-verified.json` — 検証を完了できない状態を`not_verified`として保持する。
- `boundary/verification-failed.json` — 実際に不一致を確認した状態を`failed`として保持する。
- `boundary/recommendation-without-decision.json` — Recommendationだけの状態をDecision済みと読まない。
- `boundary/decision-with-unresolved.json` — Decision後も未解決状態を保持する。
- `boundary/partial-knowledge-interchange.json` — Unknown / Withheld等をmalformed dataと同一視しない。

### Expected `not_verified`

- `boundary/unknown-contract-version.json` — unknown nested Contract versionをknown Contractとして解釈しない。
- `boundary/unknown-cognitive-method-version.json` — unknown Cognitive Method versionをcurrent v1alpha1として推測解釈しない。
- `boundary/unknown-contract-exact-looking-reference.json` — unknown payload内にExact Bindingらしい形があっても推測抽出せず、opaque + `not_verified`を維持する。

```text
unknown version != failed != current version
```

## 5. Negative fixtures

### Expected Schema FAIL

- `negative/decision-authority-field.json`
- `negative/capability-missing-observed-at.json`
- `negative/cognitive-method-decision-field.json`
- `negative/cognitive-method-assurance-field.json`
- `negative/cognitive-method-realization-missing-method-ref.json`
- `negative/cognitive-method-application-missing-method-ref.json`
- `negative/cognitive-method-pattern-field.json`

### Expected Semantic FAIL

- `negative/same-logical-lineage-without-exact.json` — 同一logical identity内revisionにExact endpointがない。
- `negative/interchange-mismatched-exact-binding.json` — bundle内recordとDecision basisのExact Bindingが一致しない。
- `negative/interchange-cognitive-method-mismatched-method-ref.json` — Method Applicationのexact `method_ref`とbundle内Method Definitionのdigestが一致しない。
- `negative/interchange-cognitive-method-mismatched-realization-profile.json` — exact `realization_ref`とbundle内RealizationのRepresentation Profile versionが一致しない。
- `negative/interchange-capability-mismatched-source-ref.json` — Capability Observationのexact source refとbundle内exact-bound source recordが一致しない。

Schemaだけでは自然に表せないcross-record invariantはsemantic validatorで検出します。

## 6. current fixture count

current `v1alpha1` fixture setは合計36件です。

```text
Capability Observation F1〜F7 = 7
Cognitive Method C1〜C9 = 9
Boundary / expected PASS or NOT_VERIFIED = 8
Negative schema / semantic FAIL = 12
Total = 36
```

current代表run:

- Contract Conformance Run `33527524514`: **success**
- Semantic Runtime Conformance Run `33527524668`: **success**
- V6/V7 Projection regression Run `33527524747`: **success**

いずれも最新developへ追随したPR head `5415972249e5f935337d8d872da2d9596da3098c`で再実行しています。

2026-08-31の17-fixture runや、その後の31-fixture runはhistorical Executable Evidenceとして残りますが、current 36-fixture baselineの代わりにはしません。

## 7. Runtimeとの関係

Go semantic runtimeは、known Contractのtyped Reference roleからExact Referenceだけを抽出し、bundle envelopeのExact Binding indexと共通規則で比較します。

確認した主な境界:

- Decision / RecommendationのReference role
- Cognitive Method Definition / Realization / ApplicationのReference role
- Capability Observationのcondition source / provenance / mapping Reference
- Semantic Referenceの既知typed Reference role
- 同一logical identityの複数Exact Bindingを単一値へ潰さない
- external Exact Referenceをbundle不在だけでFAILにしない
- logical-only Referenceをexactへ自動昇格しない
- unknown Contractを推測走査しない

```text
bundle-local consistency PASS
  != payload content verification
  != Verification Outcome
  != external Artifact existence verified
```

## 8. ISSUE-000049で確立した範囲

ADR-0026 / ISSUE-000049により、従来Decision `basis_refs`へ閉じていたbundle-local Exact Binding整合検査を、current runtimeが意味を理解しているknown Contractのtyped Reference roleへ一般化しました。

この一般化は、巨大なJSON再帰探索ではなく、Contractごとのtyped extractionと共通比較を分けて実装しています。unknown Contractのforward compatibilityを守るため、未知payloadにExact Bindingらしいfieldがあっても意味を推測しません。

## 9. Evidence boundary

current 36 fixtureについては、actual checkerで期待結果が再現されているためfixture-scoped Executable Evidenceがあります。

このfixture群から次は主張しません。

- Contract全意味領域の完全coverage
- payload bytesの再hash完了
- bundle外Artifactの存在保証
- Method execution / quality / Assurance
- production Provider / Storage / federation interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

## 10. Natural Japanese review

current 5 Contract Definition、ADR-0026、ISSUE-000049、36 fixture、Python Contract checker、Go semantic runtime、actual Run `33527524514` / `33527524668`へ戻って検査境界を再確認しました。今回成立したものをbundle-local Exact Bindingの内部整合に限定し、payload検証や外部Artifactの存在保証へ広げていません。そのうえで、fixtureの期待結果、`not_verified != failed`、Logical ReferenceとExact Historical Bindingの差を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
