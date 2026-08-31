# SOZA Contracts

更新日: 2026-08-31  
状態: **Current Contract Baseline / Scoped Executable Evidence Available**

## 1. このディレクトリの役割

`contracts/`は、SOZAのArchitectureで定めた意味境界のうち、複数の実装、Provider、Storage、version、componentをまたいで、**同じ意味として交換・検証する必要がある境界**を規範化します。

ContractはArchitectureの説明文書でも、runtime実装そのものでもありません。

```text
Product Value
  → Requirement
  → ADR
  → Architecture
  → Contract Definition
  → schema / validator / fixture
  → Runtime / Adapter / other implementation
  → Evidence
```

Contract Definitionが存在すること、schemaが存在すること、fixtureがPASSすること、本番で相互運用できること、利用者価値が実現することは別の主張です。

## 2. 権威関係

ADR-0021に従い、current `v1alpha1`では、意味・invariant・関係を自然言語で定義するMarkdown Contract Definitionをsemantic normative sourceとします。

machine-readable schemaは、その意味を検査可能なrepresentationへ落としたものです。

```text
Contract Definition != schema != implementation
Semantic Contract != Representation Profile != verifier implementation
```

schemaだけに新しいsemantic requirementを追加しません。Markdownとschemaが矛盾した場合は、どちらかを黙って優先せずContract inconsistencyとして修正します。

## 3. current Contract

| Contract | contract_id | version | current state |
|---|---|---|---|
| Semantic Reference | `soza.semantic-reference` | `v1alpha1` | Design baseline + scoped Executable Evidence |
| Decision Memory | `soza.decision-memory` | `v1alpha1` | Design baseline + scoped Executable Evidence |
| Capability Observation | `soza.capability-observation` | `v1alpha1` | Design baseline + scoped Executable Evidence |
| Semantic Interchange | `soza.semantic-interchange` | `v1alpha1` | Design baseline + scoped Executable Evidence |

4 Contract familyの意味境界は各Definitionを正本とします。対応Requirement、ADR、Architecture、fixture、runtimeとの関係は`CONTRACT_CATALOG.md`と`TRACEABILITY.md`を参照します。

## 4. Representation Profile

Exact Artifact Bindingで「どのbytesをどうcanonicalizeし、どのdigestで検証するか」はSemantic Reference Contractへ固定しません。

その責務は`profiles/`配下のRepresentation Profileが所有します。

ADR-0023により、current/future Exact Binding向けの`v1alpha1`基線として次をAcceptedしています。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

これらはcurrent Profileであり、SOZA Universal Core唯一のrepresentationではありません。historical M47 digest規則の特定はISSUE-000034で別途追跡します。

## 5. current Executable Evidence

actual repositoryには、少なくとも次があります。

- 4 ContractのJSON Schema
- Contract v1alpha1の17 fixture
- semantic validator / conformance checker
- Representation Profile fixture / verifier probe
- Contract fixtureを読むGo first semantic runtime slice
- Capability Observationへ収束するsynthetic Provider A / B Adapter slice

代表的なCI:

- Contract Conformance — Run `33346472419`: **success**
- Representation Profile Conformance — Run `33347989530`: **success**
- Semantic Runtime Conformance #3 — Run `33348972805`: **success**
- Semantic Runtime Conformance #4 — Run `33349604842`: **success**
- Semantic Runtime Conformance #5 — Run `33349801993`: **success**

Contract fixtureやruntimeが確認した範囲だけをExecutable Evidenceとし、Contract全体やProduct Value全体の達成へ広げません。

## 6. Evidenceの高さ

Product Valueに従い、次を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current baselineでは、4 Contract familyにDesign Evidenceがあり、その一部意味境界にはscoped Executable Evidenceがあります。

一方、Release、Operational、Adoption / Outcomeは`Not Yet Verified`です。

```text
Contract CI PASS
  != release readiness
  != production interoperability
  != user-value realization
```

## 7. Runtime / Provider Adapterとの境界

RuntimeやProvider AdapterはContractの利用者・実装です。Go structやAdapter input schemaを、Contract Definitionより上位の意味上の正本にはしません。

特にProvider Adapterでは、Provider A / B固有inputを共通Universal schemaへ押し込めず、Adapter出力を`soza.capability-observation/v1alpha1`へ適合させます。

```text
Provider-specific input != Universal Contract
Adapter output != Decision != Authority != Execution
```

synthetic Adapterの成功はproduction Provider / TEI interoperabilityのEvidenceではありません。

## 8. historical Contract

旧M48〜M50 candidateのContract、schema、Representation Profile候補、local PASSは`history/HISTORICAL_CONTRACT_MAPPING.md`でcurrent Contractへ対応付けます。

旧field名、version、algorithm、Evidence状態を自動継承しません。currentで同じ技術を採用した場合も、current Product Value、Requirement、ADRへ戻って改めて採用理由を持たせます。

## 9. 文書品質

Contract文書は、意味・規範強度・例外・Evidence境界を確定した後、自然な日本語となることを最重要視して全文を再ドラフトし、最後に意味監査を行います。

## 10. Natural Japanese review

4 Contract Definition、current JSON Schema / 17 fixture、2 Representation Profile、first semantic runtime、synthetic Provider Adapter、およびactual CI Evidenceへ戻って本READMEを再監査しました。historical候補とcurrentでAccepted・実体化・限定検証済みの境界を分け、Evidenceを5段階へ揃えています。その後、意味、権威関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
