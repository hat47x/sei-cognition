# SOZA Product Access Architecture

更新日: 2026-09-01  
状態: **Current Product Access Architecture Baseline**

## 1. この文書の役割

この文書は、Product Identity / Access / Collaboration baselineとADR-0030を、current SOZA Architectureへ配置します。

ここで扱うIdentity Binding、Product Access Scope、Policy Evaluator、Disclosure ProjectionはProduct security / collaboration componentであり、Universal semantic entityではありません。

## 2. Architecture overview

```text
Authentication Provider
        │ authenticated identity
        ▼
 Identity Binding / Resolver
        │ Bounded Subject
        ▼
 Product Access Policy Evaluator
        │ allowed / denied / not evaluated
        ├──────────────┐
        ▼              ▼
Canonical Access   Disclosure Projection
        │              │
        ▼              ▼
SOZA canonical     visible / withheld
semantic source       view
```

semantic Responsibility / Authorityはこのaccess pipelineの入力として自動利用しません。

```text
semantic Responsibility / Authority
  != Product Access Policy grant
```

## 3. Authentication Adapter

OIDC、SAML、local authentication、service credential等から、現在のrequest主体を識別します。

Authentication Adapterはcredentialやsession lifecycleを所有できますが、それらをBounded SubjectやDecision Memoryへ埋め込みません。

特定IdPをReference Architectureの必須componentにはしません。

## 4. Identity Binding / Resolver

Authentication Provider固有のsubjectをADR-0004のBounded Subjectへ対応付けます。

複数のexternal identityが同じBounded Subjectへbindingされることを許容します。これによりIdP交換時にもhistorical semantic referenceを保持できます。

Binding自体はProduct security configuration / Evidenceであり、Universal Identity ontologyではありません。

ISSUE-000056のreference probeでは、旧・新IdP相当の二つのauthentication identityを同じBounded Subjectへbindingし、どちらからreadしてもhistorical DecisionのResponsibility Refが変化しないことを確認しました。

## 5. Product Access Scope

Product Access ScopeはProduct resourceをaccess-control上まとめる境界です。

実装上のtenant、workspace、project等へ対応させられますが、semantic organization / projectと同一視しません。

```text
Product Access Scope ID
  != Semantic Logical Reference by default
```

current probeのscope IDもProduct-localです。将来の正式tenant / workspace modelとして固定しません。

## 6. Product Access Policy Evaluator

Bounded Subject、Product Access Scope、operation、必要なcontextを入力として、Product permissionを評価します。

reference probeではread / append / review / share / administerを用いています。

評価結果は少なくとも次を区別します。

- allowed
- denied
- not evaluated

`not_evaluated`を`denied`と同じ監査意味へ平坦化しません。ただしenforcementでは両方をsafe failureとして拒否できます。

Product role、actor kind、semantic Responsibility / Authorityからpermissionを黙って推定しません。

probeでは、Responsibility Refを持つ主体でもread grantがなければ拒否され、binding済みAI主体でもappend grantがなければ拒否されることを確認しました。一方、identity binding自体がないhuman主体は`not_evaluated`となり、`denied`と区別されます。

## 7. Guarded Canonical Access

Canonical Semantic Runtime / Storeへ到達する前に、Product Access Policyを評価します。

readが許可されていない主体へcanonical recordを返さず、appendが許可されていない主体へcanonical mutation operationを渡しません。

Product Access Policyが許可したことだけで、追加recordにsemantic Responsibility / Authorityを自動挿入しません。

probeでは、Product `administer` permissionを付与しても既存DecisionのResponsibility Refとcanonical digestが変化しないことを確認しました。

## 8. Disclosure Projection

Product Access Scope自体へのreadが許可されていても、外部collaboratorへ一部recordを開示できない場合があります。

Disclosure Projectionはcanonical sourceからviewを派生させ、非開示recordを`withheld`として外在化できます。

```text
canonical digest before projection
  == canonical digest after projection
```

Projection生成でcanonical sourceを削除・上書きしません。

withheld itemをUnknownのopaque semantic recordとして保存することもしません。

ISSUE-000056のprobeでは、外部collaboratorへDecisionを非開示とするProjectionを生成し、Decision本文を返さず`WithheldCount`だけを外在化しました。Projection生成前後でcanonical digestが一致し、canonical Decision自体も残ることを確認しています。

Product Scopeのread permissionがない場合は、Selective Disclosure Projection自体を返しません。

## 9. Security audit

Authentication、identity resolution、Product Access Policy evaluation、Disclosure適用等をaudit eventとして記録できます。

ただしcurrent baselineでは、audit log形式をUniversal Contractへ固定しません。

将来、複数deployment / IdP / security Providerで共通の耐久的意味が必要だと実証された場合にContract化を検討します。

## 10. Execution Authorizationとの境界

Product Access Architectureは「SOZAのrecordやoperationへアクセスできるか」を扱います。

TEI、SaaS、外部resource等への実行AuthorizationはADR-0016のProvider boundaryへ残します。

```text
SOZA append allowed
  != external execution authorized
```

## 11. Local Single-Node Packageとの関係

最初のLocal Single-Node Packageでは、Authentication Adapter、Identity Binding、Product Access Policyを同一processへ配置できます。

同一processであることからsemantic concernを統合しません。team / hosted deploymentへ進む場合も同じcomponent boundaryを維持できます。

## 12. Candidate Requirementとの関係

Product Access Controlをsemantic Responsibility / Authorityやactor kindから分離する必要性は、Designとscoped probeで支持されています。

ただしcurrent permission vocabulary、Product Access Scopeの粒度、Identity Binding lifecycleはreference Realizationです。

そのためArchitectureからStable Requirement IDを自動生成せず、Product層のCandidate Requirementとして保持します。

## 13. Evidence状態

- Product Access Architecture Design Evidence: **Established**
- Identity Binding / Product access separation Executable Evidence: **Scoped Evidence available**
- Selective Disclosure canonical non-mutation Executable Evidence: **Scoped Evidence available**
- production IdP integration: **Not Yet Verified**
- production policy engine / team security: **Not Yet Verified**
- Release / Operational / Adoption Evidence: **Not Yet Verified**

初期probe headのSemantic Runtime Conformance Run `33511885433`と、上流台帳同期後のRun `33513012309`はともにsuccessしています。

詳細は`../runtime/ACCESS_COLLABORATION_PROBE_EVIDENCE_2026-09-01.md`を参照します。

## 14. 関連文書

- `SOZA_REFERENCE_ARCHITECTURE.md`
- `SOZA_DEPLOYMENT_ARCHITECTURE.md`
- `../product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
- `../plan/adr/ADR-0004-responsibility-without-global-identity.md`
- `../plan/adr/ADR-0016-authorization-evidence-provider-boundary.md`
- `../plan/adr/ADR-0030-product-access-control-separation.md`
- `../plan/issue/ISSUE-000056-materialize-product-access-collaboration-probe.md`
- `../runtime/ACCESS_COLLABORATION_PROBE_EVIDENCE_2026-09-01.md`

## 15. Natural Japanese review

Product Identity / Access / Collaboration baseline、ADR-0004 / 0016 / 0030、Product Interaction、Local Single-Node Deployment、`runtime/go/accessprobe`とcurrent CI Evidenceを照合し、Authentication、Identity Binding、Product Access Policy、Guarded Canonical Access、Disclosure Projectionを別componentとして配置しました。IdP相当identity交換後のResponsibility continuity、Product permissionとsemantic Responsibilityの非同一性、`denied` / `not_evaluated`分離、Selective Disclosureのcanonical非改変をscoped Evidenceとして反映する一方、production IAM / securityへは広げていません。同一process、tenant / workspace、permission vocabulary等の実装都合をUniversal semantic entityやStable Requirementへ昇格させない境界も維持しています。そのうえで、Architecture責務、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。