# ISSUE-000006: 最小Federation Contractを調査する

Status: **Resolved**  
Priority: **6**  
Related ADRs: **ADR-0006**  
Updated: 2026-08-31

## Goal

複数のbounded principalが、内部world modelやidentity情報を全量共有せずに協働するための最小Federation境界を定める。

## Investigation

Request、Offer、Commitment、Result、Authority、revocation、非開示情報、provenance crossing、transport / cryptography等を分けて検討した。

## Resolution

FederationはUniversal Coreではなくoptional Profileとし、Request / Offer / Commitment / Result等を既存Core semanticsの交換として扱う。

RequestやCommitmentからAuthorityを推定せず、Resultをbusiness Outcomeへ自動昇格させない。Withheld Contextを単なるUnknownとも区別する。Transportやcredential実装はProviderへ残す。

判断はADR-0006へ確定したため、本IssueはResolvedとする。

## Natural Japanese review

Federation architectureへ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
