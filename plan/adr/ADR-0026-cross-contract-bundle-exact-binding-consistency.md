# ADR-0026: Semantic Interchange内のExact Binding整合をContract横断で検査する

Status: **Accepted**  
Related Issues: **ISSUE-000049**  
Updated: 2026-09-01

## Context

SOZAのExact Bindingは、可変Artifactについて「どのlogical objectか」だけでなく、判断・認知・検証の時点で参照した**特定内容**を後から識別するために使う。

current runtimeでは、Semantic Interchangeのbundle内にexact-bound recordが含まれ、そのrecordとDecisionの`basis_refs`が同じlogical identityを指す場合、両者のExact Bindingが一致するかを検査している。

この検査は、過去Decisionのbasisをbundle内の別内容へ読み替えないために有効である。一方、ADR-0025で`soza.cognitive-method/v1alpha1`を追加したことで、Exact BindingはDecision basis以外にも現れる。

たとえばMethod Applicationは、次をExact Bindingで参照できる。

- `method_ref`
- `realization_ref`
- `input_refs`
- 必要に応じたoutput / residual / provenance等のReference

ここで検査をDecision専用のまま増築すると、Contract familyが増えるたびに「このContractだけ別のExact Binding整合ロジックを持つ」という分岐が増える。また、同じ意味上の問題――**bundle自身が含むexact contentと、既知Contractからのexact referenceが食い違っていること**――を参照役割ごとに異なる扱いにしてしまう。

一方で、この整合検査をpayload bytesの再hashやVerification Outcomeと混同してはならない。

```text
bundle-local Exact Binding consistency
  != payload content verification
  != Verification Outcome
  != semantic truth
```

## Decision

### 1. bundle-local Exact Binding整合をContract横断の意味検査として扱う

Semantic Interchangeに、あるlogical identityについてExact Binding付きrecordが含まれている場合、**current runtimeが意味を理解しているknown Contractのexact reference**が同じlogical identityを指すなら、そのreferenceはbundle内のいずれかのExact Bindingと一致しなければならない。

比較対象は少なくとも次である。

- logical reference
- content digest
- Representation Profile identity
- Representation Profile version

```text
same logical identity
  + exact reference
  + exact-bound record present in the same bundle
  → one bundle-local Exact Binding must match
```

bundle内に同じlogical identityのexact-bound recordが複数存在する場合、参照側bindingがそのいずれかと一致すれば整合とする。複数revisionを同一bundleに含めること自体を禁止しない。

### 2. bundle内に対象recordが存在しない外部Exact Referenceは拒否しない

Exact Referenceが外部Artifactを指しており、同じlogical identityのexact-bound recordがbundle内に存在しない場合、本規則だけを理由にFAILへしない。

```text
no matching logical identity in bundle
  != binding mismatch
```

外部payloadの取得・digest再計算はPayload Source / Representation Verifier境界で扱う。

### 3. logical-only Referenceをexactへ自動昇格させない

同じlogical identityのexact-bound recordがbundle内に存在しても、参照側が意図的にLogical Referenceだけを持つ場合、その参照をExact Bindingへ自動変換しない。

```text
Logical Reference != Exact Historical Binding
```

本規則は**既にExact Bindingとして表現されたreference**のbundle内整合を検査するものである。

### 4. unknown Contract payloadを推測走査しない

未知のContract versionは従来どおりopaque payloadとして保持し、`not_verified`とする。

未知payloadのJSON構造を探索して、`logical_ref`や`content_digest`らしきfieldを見つけたからといってcurrent Exact Binding semanticsとして解釈しない。

```text
unknown Contract
  → opaque + not_verified
  != best-effort semantic introspection
```

Contract横断とは、**known Contractに共通する意味規則を横断的に適用する**という意味であり、unknown schemaまで推測解釈することではない。

### 5. known ContractごとのReference抽出と共通整合判定を分ける

runtime implementationでは、各known ContractからExact Reference候補を取得する処理と、bundle-local Exact Bindingを比較する共通判定を分離する。

これにより、Contract固有field名を一つの巨大な汎用JSON探索へ流し込まず、同時に比較規則をDecision専用ロジックへ閉じ込めない。

概念的には次の形とする。

```text
known typed Contract
  → typed Reference extraction
  → exact references
          ↓
bundle exact index
  → common consistency check
```

実装上の関数・interface名はsemantic authorityではない。

### 6. current Contract familyへ段階的に適用する

first implementationでは少なくとも、現在Exact Referenceを持ち得る主要roleを検査対象とする。

- Decision / Recommendationのreference role
- Cognitive Method Definition / Realization / Applicationのreference role
- Capability Observationのprovenance / source / mapping等のreference role
- Semantic Referenceのlineage等、bundle-local比較が意味を持つreference role

ただし、あるroleをexact consistency対象にすることで元Contractの意味が変わる場合は、機械的に追加せず該当Contractへ戻って判断する。

## Non-goals

本ADRは次を決めない。

- payload bytesの取得
- digestの再計算
- Representation Profile verifierの実装方式
- Verification Outcomeの生成
- ArtifactのTruth / quality / Assurance判定
- external referenceが実際に存在することの保証
- unknown Contractのpayload解析
- すべてのLogical ReferenceをExact Bindingへ昇格させること

## Consequences

### Positive

- Decisionだけに閉じたExact Binding整合検査を、同じ意味を持つ他Contractへ一貫して適用できる。
- Cognitive Methodのhistorical reconstructionで、bundle内Method / Realization revisionの取り違えを検出できる。
- Contract family追加時に比較規則そのものを複製せずに済む。
- `bundle-local consistency`と`content verification`を分けたまま維持できる。
- unknown Contractのforward compatibilityを保てる。

### Costs

- known ContractごとにReference抽出の保守が必要になる。
- Reference roleが増えたとき、抽出対象の追加漏れを検査する必要がある。
- bundleに複数exact revisionがある場合を考慮するため、単純な`logical identity → single binding` mapでは不足する。
- Contract checkerとGo runtimeの双方で同じ意味規則を再現する必要がある。

## Evidence boundary

本ADRのAcceptedはDesign Evidenceである。

ISSUE-000049でfixture、Contract checker、Go runtime testを実体化し、actual CIで確認できた範囲だけExecutable Evidenceへ上げる。

```text
bundle-local consistency PASS
  != payload verified
  != historical Artifact true
  != Release Evidence
  != Operational Evidence
```

Release、Operational、Adoption / Outcome Evidenceは本ADRのAcceptedによって変化しない。

## Revisit conditions

次の場合に再検討する。

- bundle-local Exact Binding整合をContract横断で適用すると、正当なpartial / selective disclosure interchangeを継続的に拒否する。
- unknown Contractをopaqueに保ったままではinteroperability上必要な整合性を確保できない具体例が複数現れる。
- Contract固有抽出より安全で明瞭なtyped reference registryが実証される。
- Exact Binding以外の参照整合も同じ機構へ統合する必要性が複数Scenarioで示される。

## Natural Japanese review

ADR-0008 / ADR-0009 / ADR-0022 / ADR-0025、Semantic Reference、Semantic Interchange、Decision Memory、Cognitive Method、current Contract checkerとGo runtimeのbundle-local検査へ戻って意味境界を照合しました。そのうえで、Decision専用だった整合検査を「known ContractのExact Referenceと、同一bundle内のexact-bound recordの整合」という共通意味へ引き上げました。payload再検証、Verification Outcome、unknown Contract推測解釈へ範囲を広げず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
