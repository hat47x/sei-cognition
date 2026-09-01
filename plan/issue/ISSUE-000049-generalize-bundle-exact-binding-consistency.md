# ISSUE-000049: bundle-local Exact Binding整合をknown Contract横断で実装する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0021, ADR-0022, ADR-0025, ADR-0026**  
Updated: 2026-09-02

## Goal

ADR-0026に基づき、Semantic Interchange内のbundle-local Exact Binding整合検査をDecision `basis_refs`専用の処理から切り離し、current runtimeが意味を理解しているknown ContractのExact Referenceへ同じ規則を適用する。

このIssueが扱うのは、**同一bundleに含まれるexact-bound recordと、known typed Contractから得られたExact Referenceの内部整合**である。payload bytesの取得、digest再計算、Verification Outcome生成、外部Artifactの存在保証は別の責務として維持する。

## Resolution

Decision専用だった検査を、次の二段構成へ一般化した。

```text
known typed Contract
  → typed Exact Reference extraction
  → []ExactBinding

bundle exact index
  + extracted Exact Reference
  → common bundle-local consistency check
```

Go runtimeとPython Contract checkerの双方で同じ意味規則を実装した。実装同士を意味上のauthorityにはせず、ADR-0026と各Contract Definitionを共通の基準とする。

## 実装した境界

### 1. known typed Reference roleからだけ抽出する

Go runtimeでは`extractKnownExactReferences`、Python checkerでは`known_contract_exact_references`を設け、current known Contractのtyped Reference roleだけを対象にした。

主な対象:

- Semantic Reference — lineage endpoint、Verification Outcome binding等
- Decision Memory — context / basis / recommendation / unresolved / responsibility、lineage
- Cognitive Method — Method / Realization / context / input / output / residual / provenance / responsibility
- Capability Observation — condition source / provenance / mapping Reference

Logical Referenceだけの値はExact Referenceとして抽出しない。

### 2. 同一logical identityの複数revisionを保持する

bundle envelopeの`exact_binding`は単一値mapへ潰さず、次の形で索引化する。

```text
logical identity
  → [exact binding A, exact binding B, ...]
```

参照側Exact Bindingがcandidateのいずれか一つと一致すれば整合とする。latest-winsは採用しない。

### 3. binding全体を比較する

同じlogical identityのexact-bound recordがbundle内に存在する場合、少なくとも一つのcandidateと次が一致しなければSemantic Interchange validation errorとする。

- logical reference
- content digest
- Representation Profile ID
- Representation Profile version

### 4. external Exact Referenceをbundle不在だけで拒否しない

同じlogical identityのrecordがbundle内に存在しなければ、この規則だけを理由にFAILにしない。

```text
no matching logical identity in bundle
  != binding mismatch
```

外部payloadの取得・digest再計算はPayload Source / Representation Verifierへ委ねる。

### 5. unknown Contractを推測走査しない

unknown Contract versionはopaque + `not_verified`のまま保持する。

unknown payloadに`logical_ref`、`content_digest`、`representation_profile`らしいfieldがあっても、current Exact Binding semanticsとして再帰探索・推測抽出しない。

```text
unknown Contract
  → opaque + not_verified
  != best-effort semantic introspection
```

## fixture / test

### Positive / boundary

`C9-interchange-exact-reference-consistency.json`で次を一つのbundleとして確認した。

- exact Method Referenceがbundle内Method Definition revisionと一致する。
- exact Realization Referenceがbundle内Realizationと一致する。
- 同一logical identityに複数revisionが存在しても、一致するrevisionを正しく選べる。
- external Exact Referenceがbundle外でも、それだけではFAILしない。
- logical-only ReferenceをExact Referenceへ自動昇格しない。

`unknown-contract-exact-looking-reference.json`では、unknown Contract payload内のexact-looking fieldを推測解釈しないことを確認した。

### Negative

次の不一致をsemantic validation errorとして確認した。

- Cognitive Method exact `method_ref`のdigest mismatch
- Cognitive Method exact `realization_ref`のRepresentation Profile version mismatch
- Capability Observation exact source refのbundle-local mismatch

既存Decision basis mismatchも回帰確認した。

## Acceptance criteria

### Design

- [x] ADR-0026でbundle-local Exact Binding整合の意味境界をAcceptedした。
- [x] current Contractごとのtyped Reference roleを監査し、抽出対象を実装・Evidence文書へ明文化した。

### Executable

- [x] Decision専用比較を共通bundle-local consistency判定へ分離した。
- [x] Cognitive Methodのexact Method / Realization Referenceを検査できる。
- [x] Capability Observationを含むDecision以外のknown Contractにも同じ規則を適用した。
- [x] 同一logical identityの複数exact revisionをlatest-winsで潰さない。
- [x] external Exact Referenceをbundle不在だけでFAILにしない。
- [x] logical-only Referenceをexactへ自動昇格しない。
- [x] unknown Contractはopaque + `not_verified`を維持する。
- [x] positive / negative / boundary fixtureをContract checkerとGo runtime testで検査した。
- [x] 最新develop追随後のContract ConformanceとSemantic Runtime Conformanceをsuccessさせた。

### Evidence

- [x] Contract / runtime / fixture Evidenceへscopeを反映した。
- [x] historical reconstructionに関するExecutable Evidenceを、bundle-local consistencyとして実際に確認した範囲だけ更新した。
- [x] Release / Operational / Adoption・Outcomeへは昇格させていない。

## Actual CI Evidence

最新developを取り込んだPR head `5415972249e5f935337d8d872da2d9596da3098c`で次を確認した。

- Contract Conformance Run `33527524514`: **success**
- Semantic Runtime Conformance Run `33527524668`: **success**
- V6/V7 Projection Evaluation Run `33527524747`: **success**
- Local Package Artifact Run `33527524476`: **success**

Contract / Runtimeのsuccessが本Issueの直接Evidenceであり、Projection / Packageは回帰確認として扱う。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Satisfied within the bundle-local known-Contract consistency scope**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
bundle-local Exact Binding consistency PASS
  != payload content verified
  != Verification Outcome = verified
  != external Artifact existence verified
  != Release / Operational / Outcome verified
```

## Non-goalsとして維持するもの

- external payload acquisition
- digest再計算
- signature / timestamp verification
- Truth / quality / Assurance判定
- unknown Contractのbest-effort field introspection
- Logical ReferenceをExact Bindingへ自動変換すること
- bundle外Artifactの存在保証

## Reopen条件

次のいずれかが具体的なScenarioで確認された場合は、本Issueを再開するか後続Issueを起票する。

- current known Contractに新しいReference roleが加わり、typed extractorへの追加漏れが生じた。
- selective disclosureとして正当なbundleがcommon consistency checkによって継続的に拒否される。
- exact-bound recordの候補選択にlogical identity以外の規範が必要になった。
- unknown Contractをopaqueに保つだけではinteroperabilityを維持できない具体例が複数現れた。

## Relation to ISSUE-000043

ISSUE-000043はCognitive Method Contractとfirst typed runtime sliceを実体化した。本Issueは、そのsliceで新たに現れたExact ReferenceをDecision専用規則へ押し込まず、known Contract横断の共通整合規則へ引き上げた後続課題である。

```text
Cognitive Method typed runtime established
  != bundle-local exact consistency generalized
```

両者は別のEvidenceとして追跡する。

## Natural Japanese review

ADR-0008 / ADR-0009 / ADR-0022 / ADR-0025 / ADR-0026、5 current Contract Definition、Python Contract checker、Go semantic runtime、36 fixture、最新develop追随後のactual CIへ戻って意味境界を再確認した。実装結果をpayload verificationやunknown Contract解析へ拡張せず、同一bundle内で既に表明されたExact Bindingの整合に限定した。そのうえで、実装内容、Acceptance、Evidence、Non-goal、Reopen条件が自然につながるよう全文を再構成し、自然な日本語となることを最重要視して再ドラフトした後、最終意味監査を実施済みである。
