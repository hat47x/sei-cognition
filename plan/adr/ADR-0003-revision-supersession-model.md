# ADR-0003: Semantic Lineageをstorage revisionから分離する

Status: **Accepted**  
Related Issue: **ISSUE-000003**  
Updated: 2026-08-31

## Context

SOZAは、ある時点で何を知り、何を判断していたかを後から再構成できなければならない。

そのため、単一の`version`番号やGit commit、DB row version、MVCC等から「意味がどう変わったか」を推測する設計を避ける。

## Decision

次の四つを分離する。

1. **Logical identity** — 同じ意味資産として追跡するための参照。
2. **Exact content binding** — Method ApplicationやDecisionが実際に参照した内容の固定。
3. **Semantic lineage** — 後のArtifactが以前のArtifactを意味上どのように扱ったか。
4. **Representation / storage revision** — 誤字、encoding、schema migration、DB row revision等の物理的変更。

Representationやstorageの変更だけからSemantic Lineageを自動推定しない。

### Universal relation vocabulary

Coreで閉じた語彙として持つのは、現時点では次の三つとする。

- `revises` — 以前のArtifactを意味上の前身として受け継ぎながら修正・発展させる。旧Artifactが直ちに無効になることを意味しない。branch / mergeを許す。
- `supersedes` — 明示されたscopeにおいて、後継Artifactを今後採用することを示す。過去Artifactを削除せず、過去のexact bindingも変えない。Truth判定ではない。
- `withdraws` — 明示されたscopeで今後の採用対象から外すが、代替Artifactを指定しない。

```text
SemanticLineageRecord
  relation: revises | supersedes | withdraws
  predecessor_refs[]
  successor_refs[]
  basis_refs[]
  scope_ref?
  effective_at?
```

同じlogical identityの旧内容と新内容を結ぶ場合、必要なendpointはExactArtifactBindingで内容を区別する。

## Consequences

- 過去Decisionを現在の内容へ差し替えずに再構成できる。
- branchingやscope別の後継を表現できる。
- storage implementationを交換しても意味上の改訂関係を保てる。
- `corrects`、`reopens`等をUniversal enumへ増やしたくなる場合は、既存3 relationで意味を失う具体Scenarioが必要になる。

## Revisit conditions

`revises / supersedes / withdraws`では表現できない意味差が複数domainで反復し、その差をProfileやopen relationではなくUniversal Coreで扱う必要が実証された場合に語彙を再検討する。

## Natural Japanese review

Architecture baselineとM48 reference contractへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
