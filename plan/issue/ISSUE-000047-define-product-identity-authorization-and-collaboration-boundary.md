# ISSUE-000047: Product Identity / Authorization / Collaboration boundaryを定義する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0004, ADR-0006, ADR-0016, ADR-0021, ADR-0030**  
Updated: 2026-09-01

## Goal

SOZAのsemanticなResponsibility / Authorityと、製品利用時のauthentication identity、access control、Product Access Scope、共有、Selective Disclosureを混同せず、single-userからteam・外部協働へ広げられるProduct security / collaboration boundaryを定義する。

## Resolution

Product Identity / Access / Collaborationの正本を`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`、Architecture上の配置を`architecture/SOZA_PRODUCT_ACCESS_ARCHITECTURE.md`、主要DecisionをADR-0030として定義した。

中心となる分離は次である。

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

また、SOZA内部のProduct access authorizationと、ADR-0016で扱う外部Execution ProviderのAuthorizationも別の責務とする。

```text
SOZA product access authorization
  != external execution authorization
```

## Identity boundary

認証Provider固有のsubjectは、Identity Bindingを介してADR-0004のBounded Subjectへ対応付ける。

IdPを交換した場合でも、過去のDecision / Responsibilityが参照するBounded Subjectを、現在のlogin subjectへ書き換えない。

credential、token、session、MFA secret等をsemantic identityへ埋め込まない。

## Product Access Scope

team / organization / external collaboratorのaccess boundaryとして、Product layerにProduct Access Scopeを置ける。

実装ではtenant、workspace、project等の名前を使えるが、それらをUniversal semantic entityへ自動的に昇格させない。

Product Access Scope IDをDecisionやResponsibilityのsemantic identityへ流用することも要求しない。

## Product Access Policy

現在のauthentication identityをBounded Subjectへ解決し、Product Access Scopeとoperationに対するProduct permissionを評価する。

reference probeでは`read / append / review / share / administer`を用いたが、これはprobe-localなvocabularyであり、将来のStable RequirementやUniversal role hierarchyとして固定しない。

次の短絡を認めない。

- semantic Responsibility / Authorityがあることを理由にProduct accessを自動許可する。
- Product administrator等の製品roleからDecision Authority / Responsibilityを生成する。
- human / AI / service等のactor kindだけからpermissionを推定する。

評価できなかった`not_evaluated`と、Policyが明示的に拒否した`denied`も区別する。

## Selective Disclosure

外部協働ではcanonical sourceを複製・改変せず、Disclosure Policyに応じたProjectionを作る。

非開示recordは`withheld`として扱い、`unknown`、`not observed`、削除済みへ読み替えない。

```text
withheld != unknown != deleted
```

## Collaboration boundary

### single-user

一つのlocal identityを一つのProduct Access Scopeへ対応付ける簡素なProfileを許容する。

### team

複数のBounded Subjectを同じProduct Access Scopeへ参加させ、Product permissionを独立して評価できる。

### external collaborator

別organization / IdPの主体も限定的に参加できる。内部directoryやcredentialの全量共有を要求せず、Selective Disclosureで開示範囲を分離する。

## Executable Evidence

ISSUE-000056で`runtime/go/accessprobe`を実体化した。

最終同期前head `4b05854ff4e31dd625e73a0fc05afe8e4bbbf0ec`では、Semantic Runtime Conformance Run `33513323477`、Plan integrity Run `33513323475`、Local Package Artifact Run `33513323460`がすべて**success**した。

さらに、Evidence文書へ最終Runを同期したhead `85401ec7d28aca84047923619bc54abb77880054`でも、Semantic Runtime Conformance Run `33513470530`、Plan integrity Run `33513470462`、Local Package Artifact Run `33513470467`がすべて**success**した。

actual testでは、次を確認している。

- 旧・新IdP相当identityを同じBounded Subjectへbindingできる。
- identity交換後もhistorical Responsibility Refを変更しない。
- ResponsibilityがあってもProduct permissionがなければreadを拒否する。
- Product administrator permissionを与えてもsemantic Responsibilityを生成しない。
- actor kindからpermissionを推定しない。
- `denied`と`not_evaluated`を区別する。
- Selective Disclosureで非開示recordをProjectionから除外しつつ、canonical sourceを変更しない。
- Product Scope readなしではDisclosure Projectionを返さない。

これはproduction OIDC / IAM / securityを実証したEvidenceではない。

## Requirement / Acceptance再監査

Product accessをsemantic Responsibility / Authorityやactor kindから分離する必要性は、Designとscoped probeの双方で確認できた。

ただし、permission vocabulary、Product Access Scopeのgranularity、Identity Binding lifecycleは、まだreference Realizationである。

そのため、新しいStable Requirement / Scenario IDは今回追加しない。

次をCandidate Requirementとして保持する。

> SOZAの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出せず、認証identityとの対応を含むProduct Access Policyで独立に評価できる必要がある。

production IdP / team deployment / external collaborationの実証で、既存REQ-0012 / 0013 / 0017ではこのProduct failureを十分に表現できないことが確認された場合にStable Requirement化を再検討する。

## Non-goals / 未検証範囲

- 独自Identity Providerの内製
- production OIDC / SAML / passkey integration
- password / token / session / MFA lifecycle
- enterprise IAM / SCIM
- RBAC / ABACの正式policy model
- tenant / workspaceの正式階層
- database row-level security
- encryption / key management
- invitation / membership lifecycle
- production Selective Disclosure security
- security audit retention / tamper resistance
- Release / Operational / Adoption / Outcome Evidence

## 完了条件

- [x] semantic Responsibility / AuthorityとProduct access controlの境界を定義する。
- [x] identity source / Bounded Subject / historical continuityの方針を定める。
- [x] single-userからteam / external collaborationへ進む最小境界を定める。
- [x] Selective DisclosureのProduct-level boundaryを具体化する。
- [x] 既存REQ / SCNとの重複監査を行う。Stable IDは今回追加しない。
- [x] Product / Architecture責務をADR-0030で正本化する。
- [x] reference probeのExecutable Evidence条件をISSUE-000056へ定義し、実体化する。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Scoped Product Access separation Evidence available** — ISSUE-000056 / `runtime/go/accessprobe`。
- external IdP integration: **Not Yet Verified**
- production Selective Disclosure / team security: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen条件

- production IdP交換でhistorical Bounded Subject continuityを保持できない。
- Product Access ScopeをProduct-local concernへ留めると実team利用の意味が壊れる。
- semantic Responsibility / Product permission分離では実際のsecurity requirementを満たせない。
- Projection-based Selective Disclosureでは外部協働の開示境界を安全に保持できない。
- Candidate Requirementを既存REQへ統合できず、新しいStable Requirementが必要と実証された。

## Natural Japanese review

Product Value、PMS-05、ADR-0004 / 0006 / 0016 / 0030、REQ-0012 / 0013 / 0017、SCN-0007 / 0012、Product Interaction、Local Single-Node Packaging、`runtime/go/accessprobe`と最終CI Evidenceを照合した。authentication identity、Bounded Subject、Product access permission、semantic Responsibility / Authority、external execution authorizationを別責務とし、tenant / workspaceや特定IdP、permission vocabularyをUniversal CoreやStable Requirementへ先に固定していない。Selective Disclosureではwithheldとunknownを分け、probeの成功をproduction securityへ広げない境界も維持した。そのうえで、意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。