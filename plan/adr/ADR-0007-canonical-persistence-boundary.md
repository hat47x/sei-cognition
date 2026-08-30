# ADR-0007: Semantic Persistenceをstorage-neutralな契約として定める

Status: **Accepted**  
Related Issue: **ISSUE-000007**  
Updated: 2026-08-31

## Context

SOZAは長期にわたり、何を見て、何を根拠とし、何を判断し、その後何が変わったかを失わない必要がある。

この目的のためにGit、RDB、object store、document DB、event sourcing等の一方式をCoreへ固定すると、物理実装が意味の正本になってしまう。

## Decision

SOZAが規定するのは、**storageを交換しても保たれる意味上の永続化契約**とする。

少なくとも次を満たす。

1. LogicalArtifactRefをrow ID、file path、object key等から独立させる。
2. ExactArtifactBindingが後から別内容を指さない。
3. `revises / supersedes / withdraws`をstorage sequenceとは独立して保存する。
4. source origin、discovery route、Derivation、Method Application等のProvenanceを保持する。
5. 参照対象が取得不能・非開示・retention対象外の場合、その状態を「存在しなかった」と混同しない。
6. 保存representationがどのsemantic contract / schemaで解釈されるかを識別できる。
7. schema migrationをsemantic revisionへ自動変換しない。
8. Provider固有内部構造を知らなくてもportable semantic exportを作れる。

Persistence Providerへ委ねるものには、table / collection layout、transaction実装、MVCC、event store、index、replication、backup、暗号化、compaction等を含む。

Accepted semantic stateを公開するときは必須参照が半端に欠けた状態を正常な確定状態として見せてはならないが、RDB transaction自体をUniversal要件にはしない。

large binaryや外部Sourceをすべてinline保存することも要求しない。内容のintegrityと取得可能性を分けて扱う。

物理deleteとsemantic `withdraws`も同一視しない。

## Consequences

- storage providerを交換しても意味資産のidentityとlineageを保ちやすい。
- event sourcing等を有力実装として選べる一方、Core要件にはしない。
- Providerにはportable exportとintegrity条件を満たす実装責任が生じる。

## Revisit conditions

storage-neutral契約ではactual production要件を満たせず、特定の永続化mechanismをSOZA Coreが意味上所有しなければならない事例が反復して示された場合に再検討する。

## Natural Japanese review

Semantic Persistence architecture baselineへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
