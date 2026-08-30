# ADR-0006: FederationをSelective Disclosure可能なoptional Profileとして扱う

Status: **Accepted**  
Related Issue: **ISSUE-000006**  
Updated: 2026-08-31

## Context

複数のorganizationやbounded principalが協働する場合、Intent、Capability、Result等を交換する必要がある。

しかし、参加者全員の内部world model、identity、credential、判断手続を一つのUniversal ontologyへ統合することは、不要な結合と情報開示を招く。

## Decision

FederationはUniversal Core ontologyではなく、**既存Core semanticsをbounded principal間で交換するoptional Profile**として設計する。

SOZAは参加者のworld model全量を一つへ統合しない。

少なくとも次の境界を守る。

```text
Request != Delegation / Authority Grant != Commitment != Execution
Offer   != Capability proof != Decision
Result  != Business Outcome != Assurance
```

Profileでは、Request、Offer、Commitment、Result、AuthorityGrantRef、RevocationNotice、WithheldContextNotice等を扱える。

### Selective Disclosure

相手が内部情報の一部を開示しない場合、その内容を無理に要求しない。

`WithheldContextNotice`等により「情報は存在するが、開示境界により内容は見えない」ことを外在化できる。これは単純な`Unknown`と同じではない。

主体参照にはADR-0004のBoundedSubjectRefを用い、relationship-scoped aliasを許す。

### Authority / transportを外部へ残す

RequestやCommitmentからAuthorityを推定しない。必要なAuthorityはauthoritative providerへの参照として扱う。

TLS / mTLS、OAuth / OIDC、署名、暗号化、key rotation、replay protection、queue等の具体機構はProviderが所有する。

相手からResultを受け取ったことも、自組織側でbusiness Outcomeが確認されたことを意味しない。

## Consequences

- 内部modelを全量共有せずに協働できる。
- Authorityと情報交換を分離できる。
- 非開示の存在自体を意味として保持できる。
- Federation ProfileとCapability Offeringを同一型へ自動統合しない設計余地を保てる。

## Revisit conditions

複数組織間のactual useで、Profileでは保持できないUniversalな意味が反復して見つかった場合にのみCore化を再検討する。

## Natural Japanese review

Federation architecture baselineへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
