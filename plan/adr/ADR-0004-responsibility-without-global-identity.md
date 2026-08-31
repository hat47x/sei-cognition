# ADR-0004: Bounded Subjectと文脈付きResponsibilityで主体を扱う

Status: **Accepted**  
Related Issue: **ISSUE-000004**  
Updated: 2026-08-31

## Context

SOZAでは、人間、AI、service、job、organization、committee、external provider等の主体を参照する必要がある。

これらを一つのGlobal Principal ontologyへ統合すると、組織階層、IAM、HR directory、agent registry等に固有のモデルをCoreへ取り込みやすくなる。また、actor kindだけを根拠として権限や信頼を推定する危険も生じる。

## Decision

SOZA Coreでは、Global Principal ontologyを作らない。

限定された文脈の中で主体を安定して参照するため、次の最小参照を基本とする。

```text
BoundedSubjectRef
  scope_ref
  subject_id
```

- `scope_ref`はorganization、project、federation relationship等における識別の境界を示す。
- `subject_id`は、その境界内で安定したopaque keyとする。
- global uniquenessは要求しない。
- human / AI / service等のkindからAuthorityを推定しない。

外部directory、IdP、vendor master、agent registry等との対応は、`ExternalIdentityBinding`のような別relationとして表す。credential、authentication、key lifecycleはIdentity / Authorization Providerの責務とする。

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

`responsibility_key`はopen vocabularyとし、Universal role hierarchyは作らない。

同じ主体がdecision makerとreviewerを兼ねてもよい。また、organizationと実務担当者に、それぞれ別のResponsibilityを持たせてもよい。

### ResponsibilityとAuthorityを分離する

```text
Responsibility
  != Authorization
  != Credential
  != Trust ranking
  != Capability eligibility
```

Decision makerとして記録されていることは、Provider mutationを実行する権限があることを意味しない。Authorizationは、実行時のauthoritative boundaryで評価する。

## Consequences

- human / AI / organization等を同じ参照形式で扱いながら、固有のIAM ontologyをCoreへ持ち込まずに済む。
- selective disclosureを行う場合でも、関係範囲に限定したaliasによって責任の来歴を共有しやすい。
- 外部IDが変更されても、過去のResponsibilityを保ちやすい。
- Subjectを解決するdirectory / resolverが別途必要になる場合がある。

## Revisit conditions

Globalな主体同一性がなければ、複数の実際の境界横断Scenarioで意味を保てないことが実証された場合にのみ再検討する。単に実装上のjoinが便利になるという理由だけでは、十分な根拠としない。

## Natural Japanese review

current Responsibility / Authority architecture boundaryと関連Requirementへ戻ってDecisionを照合した。その後、Bounded Subject、文脈付きResponsibility、Global Principalを作らない判断を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
