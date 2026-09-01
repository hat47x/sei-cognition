# SOZA Contract Conformance Evidence — 2026-08-31 baseline / 2026-09-01 update

更新日: 2026-09-01  
状態: **Fixture-scoped Executable Evidence — PASS**

## 1. 対象

この文書は、SOZA current Contract `v1alpha1`に対するmachine-readable schema、fixture、semantic validatorのactual CI Evidenceを記録します。

current `develop/v0.2.0`で対象となるContract familyは次の5つです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

2026-08-31時点の17-fixture baselineを履歴として否定せず、2026-09-01にCognitive Methodを追加したcurrent 31-fixture runを現在の代表Evidenceとします。

## 2. current実行Evidence

GitHub Actions:

- Workflow: `Contract Conformance`
- Run ID: `33467838961`
- Head SHA: `d9f1e9995b4e512c4042fae5928724fc721e7194`
- Conclusion: **success**
- Checker: `python tools/check_contract_conformance.py`
- Fixture count: **31**
- Overall result: **passed = true**

同じHEADのSemantic Runtime Conformance:

- Run ID: `33467838941`
- Conclusion: **success**

V6/V7 Projection regression:

- Run ID: `33467838952`
- Conclusion: **success**

Projection runはContract coverageを増やすEvidenceではなく、Contract / runtime追加による既存Projection回帰がないことの確認です。

## 3. fixture構成

### Capability Observation F1〜F7 — 7件

- F1 partial degradation
- F2 proposed state vs actual
- F3 release without environment binding
- F4 observation gap
- F5 cross-provider comparison
- F6 historical reconstruction
- F7 selective disclosure

### Cognitive Method C1〜C8 — 8件

- C1 Method Definition
- C2 Method Realization
- C3 Application with Realization
- C4 Application without Realization
- C5 Pattern as input Reference
- C6 Exact-bound Method / Realization Reference
- C7 output / residual refs
- C8 current Semantic Interchange内Method Application

### Boundary / expected PASS or `not_verified` — 7件

- verification-not-verified
- verification-failed
- recommendation-without-decision
- decision-with-unresolved
- partial-knowledge-interchange
- unknown-contract-version → `not_verified`
- unknown-cognitive-method-version → `not_verified`

### Negative Schema / Semantic FAIL — 9件

- decision-authority-field
- capability-missing-observed-at
- same-logical-lineage-without-exact
- interchange-mismatched-exact-binding
- cognitive-method-decision-field
- cognitive-method-assurance-field
- cognitive-method-realization-missing-method-ref
- cognitive-method-application-missing-method-ref
- cognitive-method-pattern-field

```text
7 Capability
+ 8 Cognitive Method
+ 7 Boundary
+ 9 Negative
= 31 fixtures
```

## 4. Cognitive Methodで直接確認した境界

### Definition / Realization / Applicationの分離

`soza.cognitive-method/v1alpha1`は次を別recordとして扱います。

```text
Method Definition
  != Method Realization
  != Method Application
```

Realizationが省略されたApplicationを、Realization不存在やMethod未適用へ読み替えません。

### semantic escalationを拒否する

negative fixtureにより、Method ApplicationへDecisionやAssuranceを直接埋め込む表現を拒否します。

```text
Method Application != Decision != Assurance
```

Pattern固有fieldをCognitive Method recordへ取り込む表現も拒否し、Patternはdomain-specific knowledgeへのReferenceとして保持します。

### Reference / Exact Binding

Method / Realization / input / output / residual / provenance等をReferenceで扱えます。

C6ではMethod / RealizationのExact Binding metadataを保持できることを確認しています。

これはExact Binding metadataの構造・runtime read Evidenceであり、payload bytesをこのfixtureだけで再hashして検証したことを意味しません。

### unknown future version

`soza.cognitive-method/v1alpha2`の未知nested recordは、known v1alpha1として推測解釈せず、opaque payloadを保持した`not_verified`になります。

```text
unknown version != failed != current version
```

## 5. 従来境界の回帰確認

current 31-fixture runでも次を維持しています。

### Capability Observation

- 部分劣化をCapability全体のunavailableへ平坦化しない。
- proposed / actualを分ける。
- `not observed`を`unavailable`へ変換しない。
- Provider-neutral observationとprovider-specific contextを分離する。
- WithheldとUnknownを区別する。

### Decision Memory

- Recommendationだけの状態をDecision済みとしない。
- Decision後もunresolved stateを保持できる。
- AuthorityをDecision recordへ内包させる表現を拒否する。

### Semantic Reference / Interchange

- same-logical lineage invariantを検査する。
- `failed`と`not_verified`を分ける。
- unknown Contract versionをknown扱いしない。
- partial knowledgeをmalformed dataと同一視しない。
- current known nested Contractをtyped validationする。

## 6. bundle-local Exact Binding consistency

current checker / runtimeには、bundle内exact-bound recordとDecision basisの不一致を検出する既存Evidenceがあります。

Cognitive Method追加によって同じ意味規則をMethod / Realization等にも一般化する必要が明確になったため、ADR-0026 / ISSUE-000049を起票しました。

```text
Decision basis mismatch checked
  != all known Contract reference roles generalized
```

ISSUE-000049はOpenであり、その一般化をcurrent 31-fixture PASSへ含めません。

## 7. Evidenceの高さ

current runから直接主張するのは、**31 fixtureとcurrent checkerが表現する範囲に限定したExecutable Evidence**です。

```text
Current 5-Contract Design Baseline: Satisfied
31-fixture Contract Conformance: Satisfied within fixture scope
Cognitive Method typed runtime: Satisfied within first-slice scope
Release Evidence: Not Yet Verified
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

CI PASSをSOZA全体のrelease readiness、production interoperability、Method quality、利用者価値へ拡張しません。

## 8. 主要な後続Evidence

### Representation Profile

- Run `33347989530`: fixture / JCS probe **success**
- current Profile: `soza.jcs+sha256/v1alpha1`, `soza.raw-bytes+sha256/v1alpha1`

### Runtime Verifier Registry

- Run `33452115728`: **success**

### Payload Source

- Run `33457416359`: **success**

### synthetic Provider Adapter

- Run `33349604842`: **success**
- Run `33349801993`: **success**

これらは互いに別のscoped Executable Evidenceです。あるRunのPASSを別境界のEvidenceへ遡及的に読み替えません。

## 9. currentで未検証の事項

- Cognitive Method executor / actual Prompt / AI / human procedure execution
- Method Applicationの結論品質 / Assurance
- ISSUE-000049のcross-Contract bundle consistency一般化
- actual Storage migration
- production Provider / TEI interoperability
- production Decision / Authority / Execution end-to-end
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

historical M47 digest ruleはISSUE-000034のResolved方針どおり回収不能範囲を`not_verified`として保持します。

## 10. 再現方法

```bash
python -m pip install -r tools/contract-check-requirements.txt
python tools/check_contract_conformance.py
```

GitHub Actionsでは`.github/workflows/contract-conformance.yml`から同じcheckerを実行します。

## 11. Natural Japanese review

2026-08-31の17-fixture Evidence、2026-09-01のCognitive Method追加、current 31 fixture、Contract checker、Go runtime、actual Run `33467838961` / `33467838941`へ戻って検査範囲を再確認しました。そのうえで、旧Evidenceを消さずcurrent代表Evidenceを更新し、Method runtime PASSをMethod実行・品質・Release以降へ拡張しない形に整理しました。最後に、数値、run ID、fixture期待結果、意味境界を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
