# SOZA Contracts

更新日: 2026-08-31  
状態: **Current Contract Design Baseline**

## 1. このディレクトリの役割

`contracts/` は、SOZAのArchitectureで定めた意味境界のうち、複数の実装、Provider、Storage、version、componentをまたいで**同じ意味として交換・検証する必要がある境界**を規範化します。

ContractはArchitectureの説明文書でも、runtime実装そのものでもありません。

```text
Product Value
  → Requirement
  → ADR
  → Architecture
  → Contract Definition
  → schema / validator / fixture
  → implementation
```

Contract Definitionが存在することは、implementation conformanceを意味しません。

## 2. 権威関係

ADR-0021に従い、初期baselineでは自然言語で意味・invariant・関係を説明するMarkdown Contract Definitionをsemantic normative sourceとします。

machine-readable schemaは、その意味を検証可能なrepresentationへ落としたものです。

```text
Contract Definition != schema != implementation
Semantic Contract != Representation Profile
```

schemaだけに新しいsemantic requirementを追加しません。Markdownとschemaが矛盾した場合は、どちらかを黙って優先せずContract inconsistencyとして修正します。

## 3. current Contract

| Contract | contract_id | version | 状態 |
|---|---|---|---|
| Semantic Reference | `soza.semantic-reference` | `v1alpha1` | Design baseline |
| Decision Memory | `soza.decision-memory` | `v1alpha1` | Design baseline |
| Capability Observation | `soza.capability-observation` | `v1alpha1` | Design baseline |
| Semantic Interchange | `soza.semantic-interchange` | `v1alpha1` | Design baseline |

詳細は`CONTRACT_CATALOG.md`を参照します。

## 4. Representation Profile

Exact Artifact Bindingの検証方式はSemantic Reference Contractへ固定しません。

JSON canonicalization、digest algorithm、raw bytes等は`profiles/`配下のRepresentation Profileが所有します。

現時点ではstable ProfileをAcceptedとしていません。historical custom canonical JSONやJCS / raw-bytes候補はISSUE-000009で再評価します。

## 5. Evidenceの扱い

current ContractはDesign Evidenceです。

- Design: Contract Definitionの意味整合
- Executable: schema / validator / positive-negative fixtureによる再現可能な検証
- Release: release候補全体でのcontract compatibility
- Operational: 実運用での相互運用・再構成実績

これらを一つの`verified`へまとめません。

## 6. historical Contract

旧M48〜M50 candidateのContract、schema、local PASSは`history/HISTORICAL_CONTRACT_MAPPING.md`でcurrent Contractへ対応付けます。

旧field名、version、algorithm、Evidence状態は自動継承しません。

## 7. 自然な日本語

Contract文書は、意味・規範強度・例外を確定した後、自然な日本語となることを最重要視して全文を再ドラフトし、最後に意味監査を行います。
