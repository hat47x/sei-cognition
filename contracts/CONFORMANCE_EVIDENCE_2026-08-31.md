# SOZA Contract Conformance Evidence — 2026-08-31 baseline / 2026-09-02 update

更新日: 2026-09-02  
状態: **Fixture-scoped Executable Evidence — PASS**

## 1. 対象

この文書は、SOZA current Contract `v1alpha1`に対するmachine-readable schema、fixture、semantic validatorのactual CI Evidenceを記録します。

current対象は次の5 Contract familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

2026-08-31の17-fixture baseline、2026-09-01の31-fixture baselineを履歴として保持しつつ、ADR-0026 / ISSUE-000049のbundle-local Exact Binding整合を追加した39-fixture runをcurrent代表Evidenceとします。

## 2. current実行Evidence

39-fixture基線を直接確認したGitHub Actions:

- Contract Conformance Run `33527512045`: **success**
- Semantic Runtime Conformance Run `33527512016`: **success**
- Plan integrity Run `33527511976`: **success**
- V6 V7 Projection Evaluation Run `33527511966`: **success**
- Local Package Artifact Run `33527511934`: **success**

Contract checker:

```text
python tools/check_contract_conformance.py
```

current fixture countは**39件**です。

これらのRunは同じ開発head上で、Contract fixture、semantic runtime、既存Projection、package生成との回帰を確認したExecutable Evidenceです。Release、Operational、Adoption / Outcome Evidenceへは昇格させません。

## 3. fixture構成

```text
Capability Observation F1〜F7 = 7
Cognitive Method C1〜C8 = 8
Boundary / expected PASS or NOT_VERIFIED = 12
Negative schema / semantic FAIL = 12
Total = 39
```

### bundle-local Exact Bindingで追加した主なboundary

- Cognitive Method `method_ref`の一致
- 同一logical identityに複数Exact Bindingがある場合の候補保持
- bundle外Exact Referenceをbundle不在だけでFAILにしない境界
- logical-only ReferenceをExactへ自動昇格しない境界
- unknown Contract内のexact風fieldを推測解析しない境界

### bundle-local Exact Bindingで追加した主なnegative

- Cognitive Method `method_ref`のdigest不一致
- Cognitive Method `realization_ref`のRepresentation Profile version不一致
- Capability Observation condition source refのRepresentation Profile不一致
- 従来のDecision basis Exact Binding不一致

## 4. known Contract横断のbundle-local Exact Binding整合

従来runtime / checkerは、Semantic Interchange内のexact-bound recordとDecision `basis_refs`の不一致を検出する最小実装でした。

ADR-0026 / ISSUE-000049では、これをDecision固有のfield比較から切り離し、current runtimeが意味を理解しているknown typed ContractのReference roleへ一般化しました。

対象となる主なrole:

### Decision Memory

- Decision context / basis / recommendation / unresolved / responsibility refs
- Decision lineage from / to / basis refs
- Recommendation context / basis / responsibility refs

### Cognitive Method

- Method Definition context / specification refs
- Method Realization method / implementation / context refs
- Method Application method / realization / context / input / output / residual / provenance / responsibility refs

### Capability Observation

- condition source refs
- provenance refs
- mapping provenance ref

### Semantic Reference

- exact_binding
- lineage from / to / basis refs
- verification outcome binding

Logical Referenceだけの値はExact Referenceとして抽出しません。

## 5. bundle indexと複数revision

Semantic Interchange envelopeの`exact_binding`はlogical identityごとに索引化します。

```text
logical identity
  → [exact binding A, exact binding B, ...]
```

同一logical identityに複数revisionが存在しても、単一値へlatest-winsで潰しません。known typed Referenceが候補のいずれかと、logical identity、content digest、Representation Profile ID / versionのすべてで一致すればbundle-local整合は成立します。

これは「最新revisionが正しい」と判定する規則ではありません。

## 6. external Referenceとpayload verificationの境界

bundle-local整合検査は、同一logical identityのexact-bound recordが**同じbundle内に存在する場合の矛盾**を検出します。

同一identityのrecordがbundle内に存在しないExact Referenceは、この検査だけを理由にFAILとしません。

```text
bundle record absent
  != exact reference invalid
  != payload missing proven
```

外部payloadの取得はPayload Source、digest再計算とRepresentation Profileによる検証はVerifier Registryの責務です。

```text
bundle-local consistency
  != payload acquisition
  != digest verification
  != Verification Outcome
```

## 7. unknown Contractを推測解析しない

unknown Contract versionは従来どおりopaque payload + `not_verified`として保持します。

payload内に`exact_binding`、`content_digest`等のfield名が現れても、それだけからcurrent known ContractのReference roleと推測しません。

```text
unknown payload looks familiar
  != known typed Contract
```

これによりforward compatibilityを保ち、未知の意味をcurrent runtimeの意味へ勝手に読み替えません。

## 8. Cognitive Methodと従来境界の回帰確認

39-fixture runでも、次を維持しています。

- Method Definition / Realization / Applicationを分ける。
- Realization未記録を不存在・未適用へ読み替えない。
- Method ApplicationをDecision / Assuranceへ昇格させない。
- PatternをCognitive Methodへ昇格させない。
- RecommendationとDecisionを分ける。
- Decision後もunresolvedを保持できる。
- Capability Observationのproposed / actual、Unknown / Withheldを平坦化しない。
- unknown Contractをknown扱いしない。
- `failed`と`not_verified`を分ける。

## 9. Evidenceの高さ

current runから直接主張するのは、**39 fixture、current checker、Go semantic runtime testが表現する範囲に限定したExecutable Evidence**です。

```text
Current 5-Contract Design Baseline: Satisfied
39-fixture Contract Conformance: Satisfied within fixture scope
Known Contract bundle-local Exact Binding consistency: Satisfied within current typed-role scope
Release Evidence: Not Yet Verified
Operational Evidence: Not Yet Verified
Adoption / Outcome Evidence: Not Yet Verified
```

次は主張しません。

- すべての将来Contract roleを自動的にcoverageすること
- external payload bytesの取得・digest再計算が成功したこと
- historical Artifactが実在すること
- Truth / Assurance
- production interoperability
- Release / Operational / Adoption / Outcomeの成立

## 10. 主要な後続Evidence

Representation Profile、Verifier Registry、Payload Source、synthetic Provider Adapter等は別のscoped Evidenceです。

- Representation Profile fixture / JCS probe Run `33347989530`: **success**
- Runtime Verifier Registry Run `33452115728`: **success**
- Payload Source Run `33457416359`: **success**
- synthetic Provider Adapter Run `33349604842`, `33349801993`: **success**

あるRunのPASSを別境界のEvidenceへ遡及的に読み替えません。

## 11. currentで未検証の事項

- external payload acquisitionを伴うcross-bundle verification
- production Storage migrationをまたぐ長期的なExact Binding検証
- production Provider / TEI interoperability
- Cognitive Method executor / Method quality / Assurance
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

historical M47 digest ruleはISSUE-000034のResolved方針どおり、回収不能範囲を`not_verified`として保持します。

## 12. 再現方法

```bash
python -m pip install -r tools/contract-check-requirements.txt
python tools/check_contract_conformance.py
```

Go側はSemantic Runtime Conformance内の`go test ./...`で、known typed ContractからのExact Reference抽出とbundle-local consistencyを独立に検査します。

## 13. Natural Japanese review

17件、31件のhistorical Evidence、ADR-0026、ISSUE-000049、current 39 fixture、Python Contract checker、Go semantic runtime、Payload Source / Verifierの責務境界へ戻って全文を再監査しました。bundle内の整合とpayload自体の検証、logical ReferenceとExact Binding、known Contractとunknown Contractを混同しないことを中心に整理しています。actual CI successを確認した範囲だけExecutable Evidenceへ反映し、Release以降へは昇格させていません。そのうえで、意味とEvidence強度を変えず、自然な日本語となることを重要視して全文を再ドラフトし、最終意味監査を実施済みです。
