# SOZA Contract Conformance Evidence — 2026-08-31 baseline / current through 2026-09-02

更新日: 2026-09-02  
状態: **Fixture-scoped Executable Evidence — PASS**

## 1. 対象

この文書は、SOZA current Contract `v1alpha1`に対するmachine-readable schema、fixture、semantic validatorのactual CI Evidenceを記録します。

対象となるContract familyは次の5つです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.cognitive-method/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

過去の17-fixture / 31-fixture runは履歴として保持し、現在はISSUE-000049のbundle-local Exact Binding一般化を含む36-fixture runを代表Evidenceとします。

## 2. current実行Evidence

最新developへ追随したPR head `5415972249e5f935337d8d872da2d9596da3098c`に対して、次を再実行しました。

- Contract Conformance Run `33527524514`: **success**
- Semantic Runtime Conformance Run `33527524668`: **success**
- V6/V7 Projection Evaluation Run `33527524747`: **success**
- Local Package Artifact Run `33527524476`: **success**

Contract checker:

```bash
python tools/check_contract_conformance.py
```

current fixture count:

```text
fixture_count = 36
passed = true
```

Projection / PackageのrunはContract coverageを増やすEvidenceではなく、今回の変更を最新developへ重ねたときに既存の評価・package経路を壊していないことの回帰確認です。

## 3. fixture構成

### Capability Observation F1〜F7 — 7件

Provider-neutral observation、partial degradation、proposed / actual、observation gap、historical reconstruction、selective disclosureを扱います。

### Cognitive Method C1〜C9 — 9件

C1〜C8のDefinition / Realization / Application、Pattern、Exact Reference、output / residual、Interchange typed loadに加え、C9で次を確認します。

- exact Method / Realization Referenceがbundle内の対応revisionと一致する。
- 同一logical identityに複数Exact Bindingがあってもlatest-winsで潰さない。
- bundle外Exact Referenceは、bundle内に同一logical identityがないだけではFAILにしない。
- logical-only ReferenceをExact Referenceへ自動昇格しない。

### Boundary — 8件

`verified` / `failed` / `not_verified`の分離、Recommendation-only、unresolved Decision、partial knowledge、unknown Contract versionを扱います。

新しい`unknown-contract-exact-looking-reference.json`では、unknown payload内にExact BindingらしいJSONが存在してもknown semanticsとして推測抽出しないことを確認します。

### Negative — 12件

既存のSchema / semantic negative caseに加え、次を追加しました。

- Cognitive Method exact `method_ref`のdigest mismatch
- Cognitive Method exact `realization_ref`のRepresentation Profile version mismatch
- Capability Observation exact source refのbundle-local mismatch

```text
7 Capability
+ 9 Cognitive Method
+ 8 Boundary
+ 12 Negative
= 36 fixtures
```

## 4. bundle-local Exact Binding consistency

ADR-0026 / ISSUE-000049に基づき、従来Decision `basis_refs`へ閉じていた検査をknown Contract横断へ一般化しました。

実装上は次を分けています。

```text
known typed Contract
  → typed Exact Reference extraction
  → []ExactBinding

bundle envelope
  → logical identity
  → [Exact Binding A, Exact Binding B, ...]

extracted exact refs + bundle index
  → common consistency check
```

同じlogical identityのexact-bound recordがbundle内に存在する場合、Exact Referenceはそのいずれかとbinding全体が一致しなければなりません。比較するのはlogical identity、content digest、Representation Profile ID、Profile versionです。

一方、bundle内に同じlogical identityが存在しない外部Exact Referenceは、この規則だけを理由に拒否しません。

```text
no matching logical identity in bundle
  != binding mismatch
```

## 5. known Contractとunknown Contractを分ける

Exact Referenceの抽出は、current Contractが定めるtyped Reference roleからだけ行います。

対象には、Decision / Recommendation、Cognitive Method、Capability Observation、Semantic Referenceの既知Reference roleを含みます。

unknown Contract payloadはJSON field名を再帰探索しません。未知versionは従来どおりopaque + `not_verified`です。

```text
known typed extraction
  != best-effort unknown payload introspection
```

## 6. 従来境界の回帰確認

36-fixture runでも次を維持しています。

- Recommendation != Decision != Authority != Execution
- Method Application != Decision != Assurance
- Pattern != Cognitive Method
- `not observed != unavailable`
- `not_verified != failed`
- same-logical lineage invariant
- partial knowledgeの保持
- unknown nested Contractの非推測
- current known nested Contractのtyped validation

## 7. payload verificationとの境界

今回のPASSはbundleが内部に持つExact Binding metadata同士の整合を示します。payload bytesを再取得し、digestを再計算したこととは別です。

```text
bundle-local Exact Binding consistency PASS
  != payload content verified
  != Verification Outcome = verified
  != Artifact truth / quality / Assurance
```

payload取得はPayload Source、digest再計算はRepresentation Verifier Registryの責務です。

## 8. Evidenceの高さ

current runから直接主張できる範囲は次です。

- Design Evidence: **Satisfied** — 5 Contract familyとADR-0026の意味境界がcurrent baselineとして成立。
- Executable Evidence: **Satisfied within the 36-fixture / current runtime scope** — typed extractionとbundle-local consistencyをactual checker / Go testsで再現。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

CI PASSをSOZA全体のrelease readiness、production interoperability、利用者価値へ拡張しません。

## 9. 他のscoped Evidence

- Representation Profile / JCS probe: historical current-profile Evidenceあり
- Runtime Verifier Registry Run `33452115728`: **success**
- Payload Source Run `33457416359`: **success**
- synthetic Provider Adapter: scoped Executable Evidenceあり
- latest Semantic Runtime Conformance Run `33527524668`: **success**

これらは互いに別の境界を検査します。あるRunのPASSを別境界のEvidenceへ遡及的に読み替えません。

## 10. currentで未検証の事項

- external Artifactの実在性・取得可能性をbundle consistencyだけから保証すること
- production filesystem / object store / remote sourceとの全面的な相互運用
- Cognitive Methodの結論品質 / Assurance
- production Provider / TEI interoperability
- production Authorization / Action execution
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

historical M47 digest ruleはISSUE-000034のResolved方針どおり、回収不能な範囲を`not_verified`として保持します。

## 11. 再現方法

```bash
python -m pip install -r tools/contract-check-requirements.txt
python tools/check_contract_conformance.py
```

GitHub Actionsでは`.github/workflows/contract-conformance.yml`と`.github/workflows/runtime-conformance.yml`から同じcheckerを再実行します。

## 12. Natural Japanese review

ADR-0026、ISSUE-000049、current 36 fixture、Python Contract checker、Go semantic runtime、最新develop追随後のRun `33527524514` / `33527524668`を相互照合しました。今回成立したEvidenceをbundle-local Exact Bindingの内部整合へ限定し、payload verification、external Artifact存在保証、Truth / Assurance、Release以降へ拡張していません。そのうえで、意味境界、fixture期待結果、run ID、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
