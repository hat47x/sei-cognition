# Product Access / Collaboration Reference Probe Evidence

更新日: 2026-09-01  
状態: **Scoped Executable Evidence**

## 1. この文書の役割

この文書は、PMS-05と`product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`、ADR-0030で定めたProduct Identity / Access / Collaboration boundaryについて、`runtime/go/accessprobe`で確認できた範囲を記録します。

今回のprobeで確認したのは、**authentication identity、Bounded Subject、Product access permission、semantic Responsibilityを別の責務として扱い、Selective Disclosureをcanonical sourceを変更しないProjectionとして構成できること**です。

production OIDC / SAML、enterprise IAM、credential lifecycle、正式なRBAC / ABAC、production Selective Disclosure、security audit運用を実証するものではありません。

```text
access probe PASS
  != production authentication proven
  != production authorization policy proven
  != production Selective Disclosure proven
  != Release Evidence
  != Operational / Adoption Evidence
```

## 2. 実装したprobe

`runtime/go/accessprobe`に、Product security layerの最小componentを実装しました。

```text
Authentication Identity
        │
        ▼
 IdentityDirectory
        │ Bounded Subject
        ▼
 Product Access Policy
        │
        ├─ GuardedStore
        └─ Disclosure Projection
```

canonical meaningは新しく作り直さず、既存の`interactionprobe.CanonicalStore`と`semanticruntime`を再利用しています。

`IdentityDirectory`、Product permission vocabulary、`Policy`、`DisclosurePolicy`はreference probeのProduct security componentであり、Universal Semantic Contractではありません。

## 3. 確認したExecutable Evidence

### 3.1 IdP相当のidentity交換とhistorical subject continuity

旧Providerのauthentication identityと、新Providerのauthentication identityを、同じBounded Subjectへbindingしました。

```text
idp-old / alice-001 ─┐
                      ├─> subject(org-a, alice)
idp-new / new-alice ─┘
```

どちらのidentityから同じDecisionをreadしても、Decisionに記録されたResponsibility Refは`subject(org-a, alice)`のまま保持されました。

これはIdP交換を模したin-memory Identity Binding probeです。実際のOIDC Provider移行を行ったEvidenceではありません。

### 3.2 semantic ResponsibilityはProduct accessを付与しない

DecisionにAliceのResponsibility Refが存在する状態でも、Product Access Policyに`read` grantがなければreadを拒否することを確認しました。

```text
semantic responsibility exists
  != product read allowed
```

### 3.3 Product administratorはsemantic Responsibilityにならない

Bobへprobe上の`administer` permissionを与えても、既存DecisionのResponsibility RefはAliceのままであり、canonical digestも変化しないことを確認しました。

```text
product administer allowed
  != decision responsibility granted
```

### 3.4 actor kindからpermissionを推定しない

`ActorKind=ai`のbinding済み主体でもgrantがなければappendは`denied`になります。

一方、`ActorKind=human`であってもidentity binding自体が存在しなければ`not_evaluated`になります。

human / AI / serviceというkindだけからpermissionを付与する経路はprobeにありません。

### 3.5 deniedとnot_evaluatedの分離

Bounded Subjectへ解決済みだがpermission grantがない状態は`denied`、authentication identityをBounded Subjectへ解決できない状態は`not_evaluated`として区別しました。

```text
not_evaluated != denied
```

Guarded accessでは、どちらもsafe failureとしてcanonical accessを拒否できますが、監査上の評価状態は失いません。

### 3.6 Selective Disclosureとcanonical sourceの非改変

external collaboratorにProduct Scopeの`read`を与えたうえで、DecisionだけをDisclosure Policyで非開示にしました。

ProjectionではDecision本文を返さず、`WithheldCount`として「非開示recordがある」ことだけを保持します。

Projection生成の前後で`CanonicalStore.Digest()`が一致し、canonical Decision自体も残っていることを確認しました。

```text
withheld in projection
  != deleted from canonical source
  != converted to unknown record
```

### 3.7 Product Scope readなしではDisclosure Projectionを返さない

identity bindingがあってもProduct Scopeの`read` permissionがない場合、Selective Disclosure Projection自体を返さず`denied`とすることを確認しました。

「一部を非開示にすること」と「そもそもProduct Scopeを読めること」を別段階として扱っています。

## 4. 既存runtimeとの重複監査

`accessprobe`は第二のsemantic runtimeを作っていません。

- canonical record保持 — `interactionprobe.CanonicalStore`
- Decision / Responsibility representation — existing `semanticruntime`
- record validation — existing `interactionprobe` / `semanticruntime`
- canonical non-authority digest check — existing `CanonicalStore.Digest()`

新しく実体化したのは、これらの手前に置くprobe-localなIdentity Binding、Product Access Policy、Disclosure Projectionだけです。

## 5. Candidate Requirementの再監査

Product Access Controlをsemantic Responsibility / Authorityやactor kindから自動導出しないことは、probeでも独立したProduct failureとして再現できました。

一方、今回使った`read / append / review / share / administer` vocabulary、Product Access Scopeのgranularity、Identity Bindingのlifecycleはreference probeのRealizationです。

そのため、現時点ではCandidate Requirementを保持し、Stable Requirement IDはまだ追加しません。

```text
Product access separation need: supported by scoped probe
specific permission model: still provisional
Stable Requirement ID: not assigned yet
```

production IdP / team deployment等の次の実証で、既存REQ-0012 / 0013 / 0017だけではProduct security上の失敗を十分に表現できないことが確認された場合に、新しいStable Requirement / Scenarioを再検討します。

## 6. PMS-05への反映

PMS-05は、Identity / Access / CollaborationのDesign baselineに加えて、次の**scoped Product Access separation Executable Evidence**まで進められます。

- authentication identityとBounded Subjectの分離
- IdP相当identity交換後のhistorical Responsibility継続
- semantic ResponsibilityとProduct access permissionの非同一性
- Product adminとsemantic Responsibilityの非同一性
- actor kind非推定
- `denied` / `not_evaluated`分離
- Selective Disclosure Projectionのcanonical非改変

ただし、production Identity / Authorization / Collaboration全体が成立したとは主張しません。

## 7. 今回確認していないこと

- production OIDC / SAML / passkey
- password / token / session lifecycle
- MFA
- enterprise directory / SCIM
- production RBAC / ABAC policy engine
- tenant / workspaceの正式model
- invitation / membership lifecycle
- concurrent collaboration / conflict handlingの実運用
- database row-level security
- encryption / key management
- production Selective Disclosure security
- audit log retention / tamper resistance
- external execution authorization integration
- security penetration testing
- Release / Operational / Adoption / Outcome Evidence

## 8. CI Evidence

最終文書同期前のcurrent head `4b05854ff4e31dd625e73a0fc05afe8e4bbbf0ec`では、次の三つがすべて**success**しました。

- Semantic Runtime Conformance Run `33513323477`
  - current Contract fixture再検査
  - `runtime/go`で`go test ./...`
  - `runtime/go/accessprobe`のcurrent test
- Plan integrity Run `33513323475`
  - ADR / Issue / registry integrity
  - Document Review Registry coverage
- Local Package Artifact Run `33513323460`
  - PMS-04の既存Packaging回帰

初期probe head `41463a0881d7d9623a1f4fa36350747cce8d8bbd`のSemantic Runtime Conformance Run `33511885433`もsuccessしています。初期Plan integrityのfailureは、新規ADR / Issueをregistryへ登録する前に早期Runtime CIを行ったことによる台帳未同期であり、その後解消済みです。

これらのsuccessは記載したscopeに限ったEvidenceとして扱います。

## 9. Natural Japanese review

PMS-05、Product Identity / Access / Collaboration baseline、ADR-0004 / 0006 / 0016 / 0030、REQ-0012 / 0013 / 0017、SCN-0007 / 0012、`runtime/go/accessprobe`のactual test、Semantic Runtime Conformance Run `33513323477`、Plan integrity Run `33513323475`、Local Package Artifact Run `33513323460`を照合しました。authentication identity、Bounded Subject、Product permission、semantic Responsibilityを分け、Selective Disclosureの成功をproduction IAMやsecurity成立へ広げていません。また、probe-localなpermission vocabularyやProduct Access ScopeをUniversal semantic modelへ昇格させず、Candidate RequirementをStable IDへ先取りしない境界を維持しています。そのうえで、意味、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。