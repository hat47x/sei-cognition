# SOZA Contract Conformance Evidence — 2026-08-31

更新日: 2026-08-31  
状態: **Fixture-scoped Executable Evidence**

## 1. 対象

current `develop/v0.1.0` branchで、次のContract v1alpha1についてmachine-readable schema、fixture、semantic validatorを検証した。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

## 2. 実行Evidence

GitHub Actions:

- Workflow: `Contract Conformance`
- Run ID: `33346472419`
- Head SHA: `9921c66f0803ddfe7810ea46c86b995f52895472`
- Conclusion: **success**
- Python: 3.12
- Checker: `python tools/check_contract_conformance.py`
- Fixture count: **17**
- Overall result: **passed = true**

## 3. 検証したfixture

### Expected PASS

1. `F1-tei-partial-degradation.json`
2. `F2-proposed-state-vs-actual.json`
3. `F3-release-without-environment-binding.json`
4. `F4-observation-gap.json`
5. `F5-cross-provider-comparison.json`
6. `F6-historical-reconstruction.json`
7. `F7-selective-disclosure.json`
8. `verification-not-verified.json`
9. `verification-failed.json`
10. `recommendation-without-decision.json`
11. `decision-with-unresolved.json`
12. `partial-knowledge-interchange.json`

### Expected Schema FAIL

13. `decision-authority-field.json`
   - Decision recordへ`authority`を直接埋め込む表現を拒否した。
14. `capability-missing-observed-at.json`
   - Capability Observationの観測時点欠落を拒否した。

### Expected Semantic FAIL

15. `same-logical-lineage-without-exact.json`
   - 同一logical identity内のrevisionにexact endpointがないため拒否した。
16. `interchange-mismatched-exact-binding.json`
   - bundle内に含まれるexact recordとDecision basisのdigest / profileが一致しないため拒否した。

### Expected `not_verified`

17. `unknown-contract-version.json`
   - unknown nested Contract versionを既知Contractとして解釈せず、failureとも混同せず`not_verified`として分類した。

## 4. このEvidenceで確認できたこと

### Capability Observation

- TEIの部分劣化をCapability全体の`unavailable`へ平坦化しない。
- proposed stateとactual stateを区別する。
- Releaseの存在とruntime availabilityを分ける。
- `not observed`を`unavailable`へ変換しない。
- TEIとSaaSをProvider-neutralに同じCapability候補として扱える。
- Provider固有contextをUniversal fieldへ無理に展開しない。
- Decision時点のObservation / mappingをexact bindingで保持できる。
- WithheldとUnknownを区別できる。

### Decision Memory

- RecommendationはDecisionなしでも存在できる。
- DecisionはUnknown / Conflictを残したまま存在できる。
- Decision recordへAuthorityを埋め込む表現を拒否できる。
- Decision basisがbundle内exact recordと食い違う場合をsemantic violationとして検出できる。

### Semantic Reference / Interchange

- Schemaだけでは表しにくいsame-logical-id lineage invariantをvalidatorで検出できる。
- `failed`と`not_verified`を別状態として保持できる。
- unknown Contract versionをknown扱いしない。
- partial knowledgeをmalformed interchangeと同一視しない。

## 5. Evidenceの高さ

この結果から主張するのは、**current repository上の17 fixtureに限定したExecutable Evidence**である。

```text
Design Contract Baseline: Satisfied
Fixture-scoped Executable Conformance: Satisfied
Stable Representation Profile: Not Yet Verified
Historical M47 digest mapping: Not Yet Verified
Release Evidence: Not Yet Verified
Operational Evidence: Not Yet Verified
```

CI PASSをSOZA全体のrelease readinessや実運用相互運用へ拡張して解釈しない。

## 6. 未完了事項

### ISSUE-000009

次は本Evidenceでは解決していない。

- stable JCS verifier選定・実証
- RFC test vectorへの適合
- high-precision semantic value境界
- historical M47 digest規則の正確なRepresentation Profile mapping

fixture内の`fixture.raw-json/v0`は検査用のopaque Profile identityであり、stable Representation Profileではない。

### Release / Operational

実際の複数Provider adapter、Storage migration、external interoperability、production Decision Memory等のEvidenceはまだない。

## 7. 再現方法

```bash
python -m pip install -r tools/contract-check-requirements.txt
python tools/check_contract_conformance.py
```

GitHub Actionsでは`.github/workflows/contract-conformance.yml`から同じcheckerを実行する。

## 8. 自然な日本語レビュー

CIログと17 fixtureの期待結果を一件ずつ照合し、Executable Evidenceの対象範囲と未検証範囲を分離した。その後、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
