# ADR-0006: FederationをSelective Disclosure可能なoptional Profileとして扱う

Status: **Accepted**  
Related Issue: **ISSUE-000006**  
Updated: 2026-08-31

## Context

複数のorganizationや、限定された識別境界を持つ主体が協働する場合、Intent、Capability、Result等を組織境界を越えて交換する必要がある。

しかし、参加者全員の内部world model、identity、credential、判断手続を一つのUniversal ontologyへ統合すると、不要な結合と過剰な情報開示を招く。

## Decision

FederationはUniversal Core ontologyではなく、**既存のCore semanticsを、境界を持つ主体間で交換するためのoptional Profile**として設計する。

SEIは、参加者それぞれのworld model全量を一つへ統合しない。

少なくとも、次の意味境界を守る。

```text
Request != Delegation / Authority Grant != Commitment != Execution
Offer   != Capability proof != Decision
Result  != Business Outcome != Assurance
```

Federation Profileでは、Request、Offer、Commitment、Result、AuthorityGrantRef、RevocationNotice、WithheldContextNotice等を扱える。

### Selective Disclosure

相手が内部情報の一部を開示しない場合、その内容を無理に要求しない。

`WithheldContextNotice`等によって、「情報は存在するが、開示境界のため内容は見えない」という状態を外在化できるようにする。これは単純な`Unknown`とは異なる。

主体参照にはADR-0004のBoundedSubjectRefを用い、関係範囲に限定したaliasを許す。

### Authorityとtransport mechanismを外部へ残す

RequestやCommitmentだけからAuthorityを推定しない。必要なAuthorityは、authoritative providerへの参照として扱う。

TLS / mTLS、OAuth / OIDC、署名、暗号化、key rotation、replay protection、queue等の具体的な通信・実行機構はProviderが所有する。

また、相手からResultを受け取ったことは、自組織側でbusiness Outcomeが確認されたことを意味しない。

## Consequences

- 参加者が内部modelを全量共有しなくても協働できる。
- Authorityと情報交換を分離できる。
- 情報が非開示であるという事実自体を意味として保持できる。
- Federation ProfileとCapability Offeringを同一型へ自動統合せず、それぞれの境界を保てる。

## Revisit conditions

複数組織間での実際の利用において、Profileでは保持できないUniversalな意味が繰り返し現れた場合にのみ、Core化を再検討する。

## Natural Japanese review

current Federation / Selective Disclosure architecture、ADR-0004のBounded Subject境界、Authority / Provider分離へ戻ってDecisionを照合した。その後、Federationをoptional Profileとする判断とSelective Disclosureの意味を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
