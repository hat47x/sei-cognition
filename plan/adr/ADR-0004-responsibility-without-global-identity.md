# ADR-0004: Bounded Subjectと文脈付きResponsibilityで主体を扱う

Status: **Accepted**  
Related Issue: **ISSUE-000004**  
Updated: 2026-08-31

## Context

SOZAでは、人間、AI、service、job、organization、committee、external provider等を参照する必要がある。

これらを一つのGlobal Principal ontologyへ統合すると、組織階層、IAM、HR directory、agent registry等の固有モデルをCoreへ取り込みやすい。また、actor kindから権限や信頼を推定する危険がある。

## Decision

SOZA CoreはGlobal Principal ontologyを作らない。

限定された文脈の中で主体を安定して指すため、次の最小参照を基本とする。

```text
BoundedSubjectRef
  scope_ref
  subject_id
```

- `scope_ref`はorganization、project、federation relationship等の識別境界を示す。
- `subject_id`はその境界内で安定したopaque keyとする。
- global uniquenessを要求しない。
- human / AI / service等のkindからAuthorityを推定しない。

外部directory、IdP、vendor master、agent registry等との対応は`ExternalIdentityBinding`のような別relationで表す。credential、authentication、key lifecycleはIdentity / Authorization Providerの責務とする。

### Responsibilityを文脈付きrelationとして扱う

```text
ResponsibilityStatement
  id
  subject_ref
  for_ref
  responsibility_key
  basis_refs[]?
  scope_ref?
  valid_from?
  valid_until?
```

`responsibility_key`はopen vocabularyとし、Universal role hierarchyを作らない。

同じ主体がdecision makerとreviewerを兼ねてもよく、organizationと実務担当者に別のResponsibilityを持たせてもよい。

### ResponsibilityとAuthorityを分離する

```text
Responsibility
  != Authorization
  != Credential
  != Trust ranking
  != Capability eligibility
```

Decision makerとして記録されていても、Provider mutationを実行する権限があるとは限らない。Authorizationは実行時のauthoritative boundaryで評価する。

## Consequences

- human / AI / organization等を同じ参照形で扱いながら、固有IAM ontologyをCoreへ持ち込まずに済む。
- selective disclosure下でもrelationship-scoped aliasで責任来歴を共有できる。
- 外部IDが変わっても過去Responsibilityを保ちやすい。
- Subject解決用directory / resolverが別途必要になる場合がある。

## Revisit conditions

Globalな主体同一性がなければ複数のactual cross-boundary Scenarioで意味を保てないことが実証された場合にのみ再検討する。単なる実装上のjoin利便性は十分な理由にしない。

## Natural Japanese review

Bounded Subject / Responsibility architecture baselineへ戻して照合した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
