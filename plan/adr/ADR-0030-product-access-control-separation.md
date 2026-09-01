# ADR-0030: Product Access Controlをsemantic Responsibility / Authorityから分離する

Status: **Accepted**  
Related Issue: **ISSUE-000047**  
Updated: 2026-09-01

## Context

SOZAはADR-0004でBounded SubjectとResponsibilityを、ADR-0016で外部Execution ProviderのAuthorizationを分離している。一方、実際の製品では、loginした主体がSOZAのrecordをread / append / review / share / administerしてよいかを評価するProduct Access Controlが必要になる。

semantic ResponsibilityやAuthorityをそのままRBAC roleへ変換すると、過去Decisionの意味と現在の製品permissionが混ざる。逆に、Product administratorやworkspace owner等の製品roleからDecision Authorityを推定すると、製品運用上の権限が判断責任へ誤って昇格する。

さらに、外部IdP交換後もhistorical Responsibilityを読み直せる必要があり、OIDC `sub`等をcanonical subject identityへ直接採用することは避けたい。

## Decision

### 1. 四つのidentity / authority境界を分離する

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

認証ProviderのsubjectはIdentity Bindingを通してBounded Subjectへ対応付ける。

Product access permissionはProduct Access Policyが評価し、semantic Responsibility / Authorityから自動導出しない。

### 2. Product Access ScopeをProduct-local concernとして扱う

team / organization / external collaboratorのaccess boundaryとしてProduct Access Scopeを置ける。

これはtenant / workspace等の実装名を取り得るが、Universal semantic entityにはしない。

### 3. IdP交換でhistorical subject referenceを書き換えない

複数のauthentication identityを同一Bounded Subjectへbindingできる。

過去Decision / Responsibilityが参照するBounded Subjectを現在のIdP subjectへ置換しない。

### 4. Product permissionとsemantic Authorityを相互変換しない

- semantic Responsibility / Authorityが存在してもProduct accessを自動許可しない。
- Product administrator等のroleからDecision Authority / Responsibilityを生成しない。
- human / AI / service等のactor kindだけからpermissionを推定しない。

### 5. deniedとnot evaluatedを区別する

identity mappingやPolicy context不足で評価できなかった状態を、明示的なPolicy拒否と同じ`denied`へ潰さない。

製品動作は安全側に停止できるが、監査上の状態は分離する。

### 6. Selective DisclosureはProjectionで行う

canonical recordを削除・改変して外部共有版を作るのではなく、同じcanonical sourceからDisclosure Policyに応じたProjectionを作る。

非開示情報は`withheld`として表し、`unknown`や「存在しない」へ変換しない。

### 7. Universal ProductAccessDecision Contractはまだ追加しない

Product access evaluationは当面Product security layerのEvidenceとして扱う。

複数deployment / IdP / domainで、共通のstable logical identityやrevision semanticsが必要だと実証された場合にUniversal Contract化を再検討する。

## Consequences

### Positive

- 現在のlogin roleが過去Responsibilityを書き換えることを避けられる。
- IdP交換後もhistorical subject continuityを保ちやすい。
- Product administratorとDecision Authorityを分離できる。
- AI / humanの種別を権限へ短絡させない。
- Selective Disclosureでcanonical sourceを分岐させずに済む。

### Costs / Risks

- Identity BindingとProduct Access Policyを別途実装する必要がある。
- semantic historyとsecurity auditを別の軸で追跡する必要がある。
- Product Access Scopeとdomain上のorganization / projectを同一視しない運用規律が必要になる。

## Revisit conditions

- Bounded SubjectではIdP交換後のhistorical identityを保持できないことが実証された。
- Product Access ScopeをProduct-localに留めると複数domainで必要なsemantic meaningを保持できない。
- Product access evaluationにUniversalなstable identity / revision / provenanceが必要なケースが複数Providerで反復した。
- Projection-based Selective Disclosureでは実際の外部協働に必要な意味差を保てない。

## Evidence

### Design Evidence

- Product Identity / Access / Collaboration baseline
- ADR-0004 / ADR-0006 / ADR-0016
- REQ-0012 / 0013 / 0017 / 0023
- SCN-0007 / 0012 / 0019

### Executable Evidence

ISSUE-000056のreference probeで検証する。

Release / Operational / Adoption・Outcome Evidenceは`Not Yet Verified`である。

## Natural Japanese review

ADR-0004 / 0006 / 0016、PMS-05、Product Interaction、Packaging、既存Requirement / Scenarioを照合し、authentication identity、Bounded Subject、Product access permission、semantic Responsibility / Authorityを分離するDecisionとして整理しました。特定IdP、RBAC製品、tenant構造を先に固定せず、IdP交換時のhistorical continuityとSelective Disclosureの意味差を優先しています。そのうえで、Decision、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。