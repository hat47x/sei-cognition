# ADR-0007: Semantic Persistenceをstorage-neutralな契約として定める

Status: **Accepted**  
Related Issue: **ISSUE-000007**  
Updated: 2026-08-31

## Context

SEIでは、長期にわたって、何を見て、何を根拠とし、何を判断し、その後に何が変わったかを失わないことが重要である。

この目的のためにGit、RDB、object store、document DB、event sourcing等の特定方式をCoreへ固定すると、物理的な保存方式が意味の正本になってしまう。

## Decision

SEIが規定するのは、**storageを交換しても保たれる意味上の永続化契約**とする。

少なくとも、次の条件を満たさなければならない。

1. LogicalArtifactRefをrow ID、file path、object key等の物理identityから独立させる。
2. ExactArtifactBindingが、後から別の内容を指すように変化しない。
3. `revises / supersedes / withdraws`をstorage sequenceとは独立して保存する。
4. source origin、discovery route、Derivation、Method Application等のProvenanceを保持する。
5. 参照対象が取得不能、非開示、retention対象外等である場合、その状態を「存在しなかった」と混同しない。
6. 保存されたrepresentationを、どのsemantic contract / schemaで解釈するか識別できる。
7. schema migrationをsemantic revisionへ自動変換しない。
8. Provider固有の内部構造を知らなくても、portable semantic exportを作れる。

Persistence Providerへ委ねるものには、table / collection layout、transaction実装、MVCC、event store、index、replication、backup、暗号化、compaction等を含む。

意味上確定した状態を外部へ提示する場合、必須参照が中途半端に欠けた状態を、正常に確定した状態として見せてはならない。ただし、この条件を満たすためにRDB transactionそのものをUniversal要件とはしない。

large binaryや外部Sourceをすべてinline保存することも要求しない。内容のintegrityと、現在取得できるかどうかは分けて扱う。

また、物理deleteとsemantic `withdraws`も同一視しない。

## Consequences

- storage providerを交換しても、意味資産のidentityとlineageを保ちやすい。
- event sourcing等を有力な実装方式として選べる一方、Core要件には固定しない。
- Persistence Providerには、portable exportとintegrity条件を満たす実装責任が生じる。

## Revisit conditions

storage-neutralな契約では実際のproduction要件を満たせず、特定の永続化mechanismをSEI Coreが意味上所有しなければならない事例が繰り返し確認された場合に再検討する。

## Natural Japanese review

current Persistence architecture、Semantic Reference Contract、Semantic Interchange Contractへ戻ってDecisionを照合した。その後、storage-neutrality、Exact Binding、Semantic Lineage、portable exportの境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
