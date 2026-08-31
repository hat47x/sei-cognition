# SOZA Contract Conformance Evidence — 2026-08-31

更新日: 2026-08-31  
状態: **Fixture-scoped Executable Evidence — PASS**

## 1. 対象

current `develop/v0.1.0` branchで、次のContract `v1alpha1`についてmachine-readable schema、fixture、semantic validatorを検証した結果を記録します。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

本書はRun `33346472419`のEvidenceを保存しつつ、その後current repositoryへ追加されたProfile / Runtime / Adapter Evidenceとの位置関係も明示します。

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
   - bundle内のexact recordとDecision basisのdigest / profileが一致しないため拒否した。

### Expected `not_verified`

17. `unknown-contract-version.json`
   - unknown nested Contract versionを既知Contractとして解釈せず、failureとも混同せず`not_verified`として分類した。

## 4. このEvidenceで直接確認できたこと

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

本Runから直接主張するのは、**current repository上の17 fixtureに限定したExecutable Evidence**です。

```text
Current Contract Design Baseline: Satisfied
17-fixture Contract Conformance: Satisfied within fixture scope
Release Evidence: Not Yet Verified
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

Design、Executable、Release、Operational、Adoption / Outcomeを一つの`verified`へまとめません。

CI PASSをSOZA全体のrelease readiness、production interoperability、利用者価値へ拡張して解釈しません。

## 6. 後続Evidenceとの関係

本Run以後、同じ意味境界の一部について別のExecutable Evidenceが追加されています。

### Representation Profile

- Run `33347989530`: `profile-fixtures` / `jcs-go-probe` **success**
- current Profile: `soza.jcs+sha256/v1alpha1`, `soza.raw-bytes+sha256/v1alpha1`

これはcurrent/future Exact BindingのRepresentation Profileに対する別のscoped Executable Evidenceです。本17-fixture RunがProfile verifierを実証したことにはしません。

### first semantic runtime

- Semantic Runtime Conformance #3 / Run `33348972805`: **success**

Contract fixtureをGo runtimeがread / validate / reconstructできる範囲を追加で確認しています。

### synthetic Provider Adapter

- Semantic Runtime Conformance #4 / Run `33349604842`: **success**
- Semantic Runtime Conformance #5 / Run `33349801993`: **success**

異なるProvider-specific inputからCapability Observationへ収束し、Provider固有fieldをUniversal schemaへ漏らさず、missing値を`unknown`として扱う境界を追加で確認しています。

```text
later runtime / adapter PASS
  != this Contract Run covered those implementations
```

## 7. currentで未検証の事項

- historical M47 digest規則のRepresentation Profile特定 — ISSUE-000034
- actual Storage migration
- production Provider / TEI interoperability
- production Decision / Authority / Executionをまたぐend-to-end運用
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

current `v1alpha1` Representation Profile自体はADR-0023でAcceptedされ、fixture / verifier probeのscoped Executable Evidenceがあります。historical M47 mappingが未完了であることと混同しません。

## 8. 再現方法

```bash
python -m pip install -r tools/contract-check-requirements.txt
python tools/check_contract_conformance.py
```

GitHub Actionsでは`.github/workflows/contract-conformance.yml`から同じcheckerを実行します。

## 9. Natural Japanese review

Run `33346472419`のCIログと17 fixtureの期待結果を保存したまま、current Contract / Representation Profile / first runtime / synthetic Provider Adapterの後続Evidenceへ戻って位置づけを再監査しました。その後、数値、run ID、fixture期待結果、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
