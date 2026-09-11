# ADR-0003: Semantic Lineageをstorage revisionから分離する

Status: **Accepted**  
Related Issue: **ISSUE-000003**  
Updated: 2026-08-31

## Context

SOZAでは、ある時点で何を知り、何を判断していたかを、後から再構成できなければならない。

そのため、単一の`version`番号やGit commit、DB row version、MVCC等を手掛かりにして、「意味がどのように変わったか」を推測する設計は採らない。

## Decision

次の四つを分離する。

1. **Logical identity** — 同じ意味資産として追跡するための参照。
2. **Exact content binding** — Method ApplicationやDecisionが実際に参照した内容を固定するための結び付き。
3. **Semantic lineage** — 後のArtifactが、以前のArtifactを意味上どのように扱ったかを示す関係。
4. **Representation / storage revision** — 誤字修正、encoding変更、schema migration、DB row revision等の表現上・物理上の変更。

Representationやstorageの変更だけを根拠として、Semantic Lineageを自動推定しない。

### Universal relation vocabulary

Coreが規定する閉じた語彙は、現時点では次の三つとする。

- `revises` — 以前のArtifactを意味上の前身として受け継ぎながら、修正・発展させる。旧Artifactが直ちに無効になることは意味しない。branch / mergeを許す。
- `supersedes` — 明示されたscopeにおいて、後継Artifactを今後採用することを示す。過去Artifactは削除せず、過去のexact bindingも変更しない。Truth判定ではない。
- `withdraws` — 明示されたscopeで今後の採用対象から外すが、代替Artifactは指定しない。

```text
SemanticLineageRecord
  relation: revises | supersedes | withdraws
  predecessor_refs[]
  successor_refs[]
  basis_refs[]
  scope_ref?
  effective_at?
```

同じlogical identityを持つ旧内容と新内容を結ぶ場合は、必要なendpointをExact Artifact Bindingとして表し、内容の違いを明示する。

## Consequences

- 過去Decisionが参照した内容を、現在の内容へ差し替えずに再構成できる。
- branchやscopeごとに異なる後継関係を表現できる。
- storage implementationを交換しても、意味上の改訂関係を保ちやすい。
- `corrects`、`reopens`等をUniversal enumへ追加する場合は、既存の三relationでは意味を保てない具体的なScenarioが必要になる。

## Revisit conditions

`revises / supersedes / withdraws`では表現できない意味差が複数domainで繰り返し現れ、その差をProfileやopen relationではなくUniversal Coreで扱う必要が実証された場合に、relation vocabularyを再検討する。

## Natural Japanese review

current `sei.semantic-reference/v1alpha1`、Architecture、Exact Binding境界へ戻ってDecisionを照合した。その後、logical identity、exact content、semantic lineage、storage / representation revisionの四分離とrelation vocabularyを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
