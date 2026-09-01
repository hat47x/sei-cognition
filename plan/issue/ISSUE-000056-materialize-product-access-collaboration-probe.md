# ISSUE-000056: Product Access / Collaboration reference probeを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0004, ADR-0006, ADR-0016, ADR-0030**  
Updated: 2026-09-01

## Goal

PMS-05とProduct Identity / Access / Collaboration baselineで定めた境界について、**authentication identity、Bounded Subject、Product access permission、semantic Responsibilityを混同せずに扱えること**をGoのreference probeで検証する。

あわせて、外部collaborator向けSelective Disclosureでcanonical sourceを変更せず、非開示情報を`unknown`へ読み替えないことを確認する。

## Resolution

`runtime/go/accessprobe`に、Product security layerの最小reference probeを実体化した。

```text
Authentication Identity
        │
        ▼
 IdentityDirectory
        │ Bounded Subject
        ▼
 Product Access Policy
        │
        ├─ Guarded Canonical Access
        └─ Disclosure Projection
```

canonical meaningは新しく定義せず、既存の`interactionprobe.CanonicalStore`と`semanticruntime`を再利用している。

`IdentityDirectory`、permission vocabulary、Product Access Policy、Disclosure Policyはprobe-localなProduct security Realizationであり、Universal Semantic Contractではない。

## 必須検査の結果

### 1. 複数authentication identityを同じBounded Subjectへbindingする

**Satisfied in scoped Executable Evidence.**

旧IdP相当と新IdP相当の二つのidentityを`subject(org-a, alice)`へbindingし、どちらから同じDecisionを読んでもhistorical Responsibility Refが変化しないことを確認した。

### 2. IdP相当identity交換後もcanonical Responsibilityを保持する

**Satisfied in scoped Executable Evidence.**

認証Provider固有subjectを変更しても、Decision内のResponsibility Refを現在のlogin subjectへ書き換えない。

### 3. semantic ResponsibilityからProduct permissionを推定しない

**Satisfied in scoped Executable Evidence.**

DecisionにAliceのResponsibilityが記録されていても、Product Policyに`read` grantがなければreadを拒否した。

### 4. Product administratorからsemantic Responsibilityを生成しない

**Satisfied in scoped Executable Evidence.**

Bobへ`administer` permissionを与えても、既存DecisionのResponsibilityはAliceのまま保持され、canonical digestも変化しないことを確認した。

### 5. actor kindからpermissionを推定しない

**Satisfied in scoped Executable Evidence.**

binding済みのAI主体でもgrantがなければappendを拒否する。human主体であることだけからpermissionを付与する経路も持たない。

### 6. `not_evaluated`と`denied`を区別する

**Satisfied in scoped Executable Evidence.**

Bounded Subjectへ解決済みだがgrantがない場合は`denied`、identity bindingが存在せず評価contextを作れない場合は`not_evaluated`として区別した。

### 7. enforcementはsafe failureできる

**Satisfied in scoped Executable Evidence.**

`denied` / `not_evaluated`のいずれでもcanonical accessを許可せず、監査上の評価状態をerrorへ保持できる。

### 8. Selective Disclosureで非開示recordを`withheld`として扱う

**Satisfied in scoped Executable Evidence.**

external collaborator向けProjectionで非開示Decision本文を返さず、`WithheldCount`として非開示recordの存在だけを外在化した。

fake Unknown semantic recordは生成していない。

### 9. Disclosure Projectionでcanonical sourceを変更しない

**Satisfied in scoped Executable Evidence.**

Projection生成前後で`CanonicalStore.Digest()`が一致し、非開示Decision自体もcanonical sourceへ残っていることを確認した。

### 10. Product Scope readなしではProjectionを返さない

**Satisfied in scoped Executable Evidence.**

identity bindingがあっても`read` grantがない主体へSelective Disclosure Projection自体を返さない。

### 11. Product permission変更でhistorical Decision / Responsibilityを書き換えない

**Satisfied in scoped Executable Evidence within tested fixture.**

Product administrator permissionを追加してもcanonical Decision / Responsibilityが変化しないことをdigestとrecord内容で確認した。

## Negative cases

actual testで次を確認した。

- Decision Responsibilityの存在からProduct readを自動許可しない。
- Product administratorからDecision Responsibilityを追加しない。
- `actor_kind=human` / `ai`だけからpermissionを付与しない。
- identity binding不在を明示的なPolicy `denied`へ読み替えない。
- withheld recordをUnknown semantic recordへ変換しない。
- Disclosure Projection生成でcanonical recordを削除しない。

## 既存runtimeとの重複監査

Product Access probeは第二のsemantic runtimeを作っていない。

- canonical record — `interactionprobe.CanonicalStore`を再利用。
- Decision / Responsibility — existing `semanticruntime`を再利用。
- canonical非改変検査 — existing `CanonicalStore.Digest()`を再利用。

新しく実体化したのはProduct security layerのIdentity Binding、Policy evaluation、Guarded Access、Disclosure Projectionだけである。

## Requirement / Scenario再監査

probeによって、Product accessをsemantic Responsibility / Authorityやactor kindから分離する必要性は、独立したProduct failureとして実行可能に確認できた。

一方、`read / append / review / share / administer`のoperation vocabulary、Product Access Scopeのgranularity、Identity Bindingのlifecycleはまだreference probeのRealizationである。

そのため、新しいStable Requirement / Scenario IDは今回も追加しない。

次をCandidate Requirementとして保持する。

> SOZAの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出せず、認証identityとの対応を含むProduct Access Policyで独立に評価できる必要がある。

production IdP、実team deployment、またはexternal collaborationの次段階で、この規範を既存REQ-0012 / 0013 / 0017だけでは十分に表現できないことが確認された場合、新しいStable Requirement / Scenarioを再検討する。

## Non-goals / 未検証範囲

- production OIDC / SAML / passkey integration
- password / token / session / MFA lifecycle
- enterprise IAM / SCIM
- formal RBAC / ABAC policy language
- tenant / workspaceの正式model
- database row-level security
- encryption / key management
- production invitation / membership UX
- production Selective Disclosure security
- security audit retention / tamper resistance
- Release / Operational / Adoption / Outcome Evidence

## 完了条件

- [x] Identity Bindingを実体化する。
- [x] Product Access Policy evaluatorを実体化する。
- [x] Guarded Canonical Accessを実体化する。
- [x] Disclosure Projectionを実体化する。
- [x] 必須検査とnegative caseをGo testへ落とす。
- [x] existing interactionprobe / semanticruntimeとの重複監査を行う。
- [x] CIで再現可能なExecutable Evidenceを得る。
- [x] Product / Architecture / Evidence文書へ結果を同期する。
- [x] Stable Requirement / Scenario追加の要否を再監査する。今回は追加しない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 最終headの対象CIをsuccessさせる。

初期probe head `41463a0881d7d9623a1f4fa36350747cce8d8bbd`では、Semantic Runtime Conformance Run `33511885433`が**success**した。

Plan integrityは同headでregistry未同期のため失敗したが、runtime failureではない。最終headでplan registry、Document Review Registry、PMS-05まで同期したうえで再検査する。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Scoped Evidence available** — `runtime/go/accessprobe`とSemantic Runtime Conformance Run `33511885433`。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

詳細は`runtime/ACCESS_COLLABORATION_PROBE_EVIDENCE_2026-09-01.md`を正とする。

## Reopen / escalation条件

- production IdP交換でBounded Subject continuityを保持できない。
- Product Access ScopeをProduct-local concernへ留めると実team利用の意味を保持できない。
- Product access evaluationにUniversalなstable identity / revision semanticsが不可欠と確認された。
- Projection-based Selective Disclosureでは実外部協働の開示境界を安全に保持できない。
- Product access separation Candidate Requirementを既存REQへ統合できず、Stable Requirement化が必要と実証された。

## Natural Japanese review

PMS-05、Product Identity / Access / Collaboration baseline、ADR-0004 / 0006 / 0016 / 0030、REQ-0012 / 0013 / 0017、SCN-0007 / 0012、`runtime/go/accessprobe`のactual testとSemantic Runtime Conformance Run `33511885433`を照合しました。特定IdPやRBAC製品ではなく、authentication identity、Bounded Subject、Product access permission、semantic Responsibilityの責務分離を検査しています。また、probe-localなpermission vocabularyをStable Requirementへ先取りせず、Selective Disclosureの成功をproduction securityへ広げない境界も維持しています。そのうえで、目的、検査結果、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。