# SOZA Contract v1alpha1 Fixtures

更新日: 2026-09-02  
状態: **Fixture-scoped Executable Evidence Baseline**

## 1. このfixture群の役割

`fixtures/contracts/v1alpha1/`は、current 5 Contract familyの意味境界をpositive / negative / boundary caseとして再現する固定入力です。

fixtureそのものはContract Definitionではありません。また、fixtureが存在するだけではExecutable Evidenceにはなりません。

```text
Contract Definition
  != Schema
  != Fixture
  != Checker Result
```

actual checkerで期待結果を再現できた範囲だけを、fixture-scopedなExecutable Evidenceとして扱います。

## 2. Capability Observation F1〜F7

| Fixture | 主な検証 | Value Axis |
|---|---|---|
| F1 | TEIの部分劣化をCapability全体のunavailableへ潰さない | V1, V2, V4, V5 |
| F2 | proposed stateとactual stateを分ける | V1, V2, V3, V5 |
| F3 | Releaseが存在するだけでEnvironment availabilityを確定しない | V2, V4, V5 |
| F4 | not observedをunavailableへ変換しない | V2, V5 |
| F5 | TEI / SaaSをProvider-neutralに並べ、固有情報を平坦化しない | V4, V8 |
| F6 | 過去Decision時のObservation / mappingをExact Bindingで再構成する | V1, V3, V4 |
| F7 | WithheldとUnknownを区別し、非開示をincompatibleへ変換しない | V2, V4, V5 |

F1〜F7だけを理由に、Capability Choice全体やproduction Provider integrationを検証済みとはしません。

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
- `boundary/interchange-cognitive-method-exact-match.json` — Cognitive Methodのexact `method_ref`がbundle内exact recordと一致する。
- `boundary/interchange-multiple-exact-revisions.json` — 同一logical identityに複数のExact Bindingが存在してもlatest-winsで潰さず、参照が候補の一つに一致すれば受理する。
- `boundary/interchange-external-exact-reference.json` — Exact Referenceの対象recordがbundle内にないことだけを理由にFAILとしない。
- `boundary/interchange-logical-reference-with-exact-record.json` — bundle内にexact recordがあっても、logical-only ReferenceをExact Bindingへ自動昇格しない。

### Expected `not_verified`

- `boundary/unknown-contract-version.json` — unknown nested Contract versionをknown Contractとして解釈しない。
- `boundary/unknown-cognitive-method-version.json` — unknown Cognitive Method versionをcurrent v1alpha1として推測解釈せず、opaque payloadを保持する。
- `boundary/interchange-unknown-exact-looking-payload.json` — unknown ContractのpayloadにExact Bindingらしいfieldがあっても、field名から推測して整合検査へ取り込まない。

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
- `negative/interchange-cognitive-method-exact-mismatch.json` — Cognitive Method Applicationのexact `method_ref`とbundle内Method recordが一致しない。
- `negative/interchange-capability-source-exact-mismatch.json` — Capability Observationのexact source refとbundle内recordのRepresentation Profileが一致しない。

Schemaで自然に表せないcross-record invariantはsemantic validatorで検出します。

## 6. current fixture count

current `v1alpha1` fixture setは合計38件です。

```text
Capability Observation F1〜F7 = 7
Cognitive Method C1〜C8 = 8
Boundary / expected PASS or NOT_VERIFIED = 12
Negative schema / semantic FAIL = 11
Total = 38
```

38件基線では、従来のContract境界に加え、ADR-0026 / ISSUE-000049で定めたknown Contract横断のbundle-local Exact Binding整合を直接検査します。

2026-09-01時点の31-fixture runはhistorical Executable Evidenceとして残しますが、38-fixture current baselineの代わりにはしません。current代表runは、38件を登録したheadのContract Conformanceがsuccessした時点で本節へ追記します。

## 7. Runtimeとの関係

Go semantic runtimeは、このfixture群とruntime testを使ってknown Contractをread / validate / reconstructします。

Cognitive MethodについてはC1〜C7 standaloneとC8 nested Interchangeをruntime testへ接続しています。さらにbundle-local Exact Bindingについて、known typed ContractのReference roleからExact Referenceを抽出し、bundle内の同一logical identityに属するExact Binding群と照合します。

確認している範囲:

- typed Method Definition / Realization / Application
- Reference preservation
- Exact Binding metadata preservation
- Realization省略の非推論
- Pattern Referenceの非昇格
- output / residual保持
- unknown Method versionのopaque + `not_verified`
- Interchange original bytesのlossless export
- Decision / Cognitive Method / Capability Observation / Semantic Referenceのknown typed Reference roleからのExact Reference抽出
- 同一logical identityの複数Exact revision保持
- bundle外Exact Referenceの非FAIL
- logical-only Referenceの非昇格
- unknown Contract payloadの非推測解析

```text
bundle-local consistency PASS
  != referenced payload bytes verified
  != external Artifact exists
  != Truth / Assurance verified
```

Payload取得やdigest再計算はPayload Source / Verifier Registryの責務であり、このbundle-local検査へ混ぜません。

## 8. ISSUE-000049との関係

C6ではCognitive MethodのExact Referenceを表現・読込できることまでを確認していました。ISSUE-000049では、そのReferenceが同一bundle内のexact-bound recordと矛盾していないかを、Decision専用ロジックではなくknown Contract共通の規則として扱います。

```text
Exact Reference preserved
  != payload verified

bundle-local Exact Binding consistent
  != external payload verified
```

Go runtimeとPython Contract checkerは、互いを意味上の正本とはしません。ADR-0026と各Contract Definitionを共通の基準として、同じ境界を独立に検査します。

## 9. Evidence boundary

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current fixture setについてactual checkerで期待結果が再現された範囲だけ、Executable Evidenceとして扱います。

このfixture群から次は主張しません。

- Contract全意味領域の完全coverage
- external payload acquisition / digest再計算
- Method execution / quality / Assurance
- production Provider / Storage / federation interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

Value Axisやfixture件数はtraceabilityのための参照であり、Product Valueの点数ではありません。

## 10. Natural Japanese review

current 5 Contract Definition、ADR-0026、ISSUE-000049、Contract checker、Go semantic runtime、従来31 fixtureへ戻り、Exact Bindingのbundle-local整合とpayload verificationを混同しないよう再整理しました。同一logical identityに複数revisionがある場合、bundle外Reference、logical-only Reference、unknown Contractの扱いも個別fixtureとして外在化しています。そのうえで、意味、期待結果、Evidenceの高さを変えず、自然な日本語となることを重要視して全文を再ドラフトし、最終意味監査を実施済みです。
