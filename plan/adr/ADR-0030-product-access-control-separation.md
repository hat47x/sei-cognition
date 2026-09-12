# ADR-0030: Product Access Controlをsemantic Responsibility / Authorityから分離する

Status: **Accepted**  
Related Issue: **ISSUE-000047**  
Updated: 2026-09-01

## Context

SEIはADR-0004でBounded SubjectとResponsibilityを、ADR-0016で外部Execution ProviderのAuthorizationを分離しています。一方、実際の製品では、loginした主体がSEIのrecordをread / append / review / share / administerしてよいかを評価するProduct Access Controlが必要になります。

semantic ResponsibilityやAuthorityをそのままProduct roleへ変換すると、過去Decisionの意味と現在の製品permissionが混ざります。逆に、Product administratorやworkspace owner等の製品roleからDecision Authorityを推定すると、製品運用上の権限が判断責任へ誤って昇格します。

さらに、外部IdPを交換してもhistorical Responsibilityを読み直せる必要があるため、OIDC `sub`等をcanonical subject identityへ直接採用することも避ける必要があります。

## Decision

### 1. 四つのidentity / authority境界を分離する

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

認証ProviderのsubjectはIdentity Bindingを通してBounded Subjectへ対応付けます。

Product access permissionはProduct Access Policyが評価し、semantic Responsibility / Authorityから自動導出しません。

### 2. Product Access ScopeをProduct-local concernとして扱う

team / organization / external collaboratorのaccess boundaryとしてProduct Access Scopeを置けます。

これはtenant / workspace等の実装名を取り得ますが、Universal semantic entityにはしません。

### 3. IdP交換でhistorical subject referenceを書き換えない

複数のauthentication identityを同一Bounded Subjectへbindingできます。

過去Decision / Responsibilityが参照するBounded Subjectを、現在のIdP subjectへ置換しません。

### 4. Product permissionとsemantic Authorityを相互変換しない

- semantic Responsibility / Authorityが存在してもProduct accessを自動許可しません。
- Product administrator等のroleからDecision Authority / Responsibilityを生成しません。
- human / AI / service等のactor kindだけからpermissionを推定しません。

### 5. deniedとnot evaluatedを区別する

identity mappingやPolicy context不足で評価できなかった状態を、明示的なPolicy拒否と同じ`denied`へ潰しません。

製品動作は安全側に停止できますが、監査上の状態は分離します。

### 6. Selective DisclosureはProjectionで行う

canonical recordを削除・改変して外部共有版を作るのではなく、同じcanonical sourceからDisclosure Policyに応じたProjectionを作ります。

非開示情報は`withheld`として表し、`unknown`や「存在しない」へ変換しません。

### 7. Universal ProductAccessDecision Contractはまだ追加しない

Product access evaluationは当面Product security layerのEvidenceとして扱います。

複数deployment / IdP / domainで、共通のstable logical identityやrevision semanticsが必要だと実証された場合にUniversal Contract化を再検討します。

### 8. Stable Product Requirementはprobe後に再監査する

「Product access permissionをsemantic Responsibility / Authorityやactor kindから自動導出しない」という規範はProduct上重要ですが、read / append / share等の具体operation vocabularyやIdentity Bindingの適用範囲はまだreference probe段階です。

そのため、現時点ではCandidate Requirementとして保持し、ISSUE-000056の結果から、既存REQ-0012 / 0013 / 0017へ統合できるか、新しいStable Requirementが必要かを再監査します。

## Consequences

### Positive

- 現在のlogin roleが過去Responsibilityを書き換えることを避けられます。
- IdP交換後もhistorical subject continuityを保ちやすくなります。
- Product administratorとDecision Authorityを分離できます。
- AI / humanの種別を権限へ短絡させません。
- Selective Disclosureでcanonical sourceを分岐させずに済みます。

### Costs / Risks

- Identity BindingとProduct Access Policyを別途実装する必要があります。
- semantic historyとsecurity auditを別の軸で追跡する必要があります。
- Product Access Scopeとdomain上のorganization / projectを同一視しない運用規律が必要になります。

## Revisit conditions

- Bounded SubjectではIdP交換後のhistorical identityを保持できないことが実証された。
- Product Access ScopeをProduct-localに留めると複数domainで必要なsemantic meaningを保持できない。
- Product access evaluationにUniversalなstable identity / revision / provenanceが必要なケースが複数Providerで反復した。
- Projection-based Selective Disclosureでは実際の外部協働に必要な意味差を保てない。

## Evidence

### Design Evidence

- Product Identity / Access / Collaboration baseline
- ADR-0004 / ADR-0006 / ADR-0016
- REQ-0012 / REQ-0013 / REQ-0017
- SCN-0007 / SCN-0012
- Product access separation Candidate Requirement

### Executable Evidence

ISSUE-000056のreference probeで、identity binding、Product permissionとResponsibilityの非同一性、actor kind非推定、`denied` / `not_evaluated`分離、Selective Disclosureのcanonical非改変を検証します。

Release / Operational / Adoption・Outcome Evidenceは`Not Yet Verified`です。

## Natural Japanese review

ADR-0004 / 0006 / 0016、PMS-05、Product Interaction、Packaging、既存Requirement / Scenarioを照合し、authentication identity、Bounded Subject、Product access permission、semantic Responsibility / Authorityを分離するDecisionとして整理しました。特定IdP、RBAC製品、tenant構造やProduct permission vocabularyを先にStable Requirementへ固定せず、IdP交換時のhistorical continuityとSelective Disclosureの意味差を優先しています。そのうえで、Decision、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。