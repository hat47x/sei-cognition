# SOZA Contract v1alpha1 Fixtures

更新日: 2026-08-31  
状態: **Executable candidate fixtures**

## Capability Observation F1〜F7

| Fixture | 主な検証 | Value Axis |
|---|---|---|
| F1 | TEIの部分劣化をCapability全体のunavailableへ潰さない | V1, V2, V4, V5 |
| F2 | proposed stateとactual stateを分ける | V1, V2, V3, V5 |
| F3 | Release存在だけでEnvironment availabilityを確定しない | V2, V4, V5 |
| F4 | not observedをunavailableへ変換しない | V2, V5 |
| F5 | TEI / SaaSをProvider-neutralに並べ、固有情報を平坦化しない | V4, V8 |
| F6 | 過去Decision時のObservation / mappingをexact bindingで再構成する | V1, V3, V4 |
| F7 | WithheldとUnknownを区別し、非開示をincompatibleへ変換しない | V2, V4, V5 |

F1〜F7はISSUE-000024のRequired scenariosに対応します。

## Negative / boundary fixtures

- `negative/decision-authority-field.json` — DecisionへAuthorityを埋め込むSchema違反
- `negative/capability-missing-observed-at.json` — Observation time欠落
- `negative/same-logical-lineage-without-exact.json` — Schemaだけでは検出しにくいsemantic invariant違反
- `boundary/unknown-contract-version.json` — unknown versionをknownとして扱わないこと

## Evidence境界

fixtureの存在だけではExecutable Acceptanceを満たしません。

validatorをactual repositoryで実行し、expected PASS / FAIL / NOT_VERIFIEDを再現できた時点でExecutable Evidenceとして扱います。

## 自然な日本語レビュー

各fixtureの意味をISSUE-000024とcurrent Contractへ戻して確認し、Value Axisを機械的な点数に変換せず、自然な日本語となることを最重要視して説明を整えました。
