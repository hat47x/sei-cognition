# SOZA Contracts

更新日: 2026-09-05  
状態: **Current Contract Baseline / Scoped Executable Evidence Available / v0.2.0 Release Evidence Reflected**

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
| Cognitive Method | `soza.cognitive-method` | `v1alpha1` | Design baseline + scoped Executable Evidence |
| Semantic Interchange | `soza.semantic-interchange` | `v1alpha1` | Design baseline + scoped Executable Evidence |

5 Contract familyの意味境界は各Definitionを正本とします。対応Requirement、ADR、Architecture、fixture、runtimeとの関係は`CONTRACT_CATALOG.md`と`TRACEABILITY.md`を参照します。

## 4. Representation Profile

Exact Artifact Bindingで「どのbytesをどうcanonicalizeし、どのdigestで検証するか」はSemantic Reference Contractへ固定しません。

その責務は`profiles/`配下のRepresentation Profileが所有します。

ADR-0023により、current/future Exact Binding向けの`v1alpha1`基線として次をAcceptedしています。

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

これらはcurrent Profileであり、SOZA Universal Core唯一のrepresentationではありません。historical M47 digest規則についてはISSUE-000034で、保持されている直接Evidenceから権威的に復元できないと整理しています。current Profile conformanceから旧方式を推定しません。

## 5. current Executable Evidence

actual repositoryには、少なくとも次があります。

- 5 Contract familyのJSON Schema
- current Contract checkerの39 fixture
- semantic validator / conformance checker
- Representation Profile fixture / verifier probe
- current known Contractを読むGo semantic runtime
- known typed Contract横断のbundle-local Exact Binding consistency
- Cognitive Method typed runtime
- Capability Observationへ収束するsynthetic Provider A / B Adapter slice

さらに、Contractを利用する下流のScoped Executable Evidenceとして、次があります。

- end-to-end Semantic Product Journey
- E2 out-of-process Realization / Provider exchange
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- E3b-P2 revision A fixed-artifact actual TEI CLI integration
- E3b-M1a / M1b live Cognitive Method integration
- Method Realization historical reconstruction
- actual model artifact exchange後のhistorical Application保持
- fixed-model Ollama runtime version exchange後のhistorical Application保持 — ISSUE-000070 Resolved

historical GitHub Actions Runは、その時点で実際に得たEvidenceとして保持しますが、current Contract成立条件をGitHub Actionsへ依存させません。

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

current baselineでは、5 Contract familyにDesign Evidenceがあり、その意味境界の一部にはscoped Executable Evidenceがあります。

v0.2.0 Local Reference Product Baselineについてactual Release Evidenceがあります。ただし、supported release scopeはE3aまでです。release後に得たE3b、historical reconstruction、model / runtime version exchange Evidenceを、公開済みv0.2.0のsupport範囲へ遡及させません。

Operational EvidenceとAdoption / Outcome EvidenceはNot Establishedです。

```text
Contract conformance / scoped integration PASS
  != arbitrary interoperability
  != v0.2.0 supported scope expanded
  != Operational Evidence
  != user-value realization
```

## 7. Runtime / Provider Adapterとの境界

RuntimeやProvider AdapterはContractの利用者・実装です。Go structやAdapter input schemaを、Contract Definitionより上位の意味上の正本にはしません。

特にProvider Adapterでは、Provider A / B固有inputを共通Universal schemaへ押し込めず、Adapter出力を`soza.capability-observation/v1alpha1`へ適合させます。

```text
Provider-specific input != Universal Contract
Adapter output != Decision != Authority != Execution
```

synthetic Adapterに加え、E3b-P1 public live ProviderとE3b-P2 revision A fixed-artifact actual TEI CLIで、Provider固有情報をCapability Observation境界へ戻すScoped Executable Evidenceがあります。

一方、ISSUE-000072のTEI revision B actual CLI / Provider Plan / current SOZA Adapter compatibilityはNot Yet Verifiedです。revision Aやrepository-side runnerの存在だけから任意TEI version互換性を主張しません。

## 8. historical Contract

旧M48〜M50 candidateのContract、schema、Representation Profile候補、local PASSは`history/HISTORICAL_CONTRACT_MAPPING.md`でcurrent Contractへ対応付けます。

旧field名、version、algorithm、Evidence状態を自動継承しません。currentで同じ技術を採用した場合も、current Product Value、Requirement、ADRへ戻って改めて採用理由を持たせます。

## 9. 文書品質

Contract文書は、意味・規範強度・例外・Evidence境界を確定した後、自然な日本語となることを最重要視して全文を再ドラフトし、最後に意味監査を行います。

## 10. Natural Japanese review

5 Contract Definition、current JSON Schema / 39 fixture、2 Representation Profile、Go semantic runtime、Verifier Registry / Payload Source、synthetic Provider Adapter、Product Journey、E2 / E3a / E3b integration、historical reconstruction、model / runtime exchange、v0.2.0 Release Evidenceへ戻って本READMEを再監査しました。

旧版に残っていた「4 Contract family」「17 fixture」「production Provider / TEI未確認」「Release Evidence未成立」という2026-08-31時点の記述をcurrent stateへ更新しました。

そのうえで、ISSUE-000070のfixed-scope Evidenceをarbitrary portabilityや成果品質へ拡張せず、ISSUE-000072 revision B actual、Operational / Adoption・Outcomeを未検証として残しています。意味、権威関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して最終意味監査を行いました。
