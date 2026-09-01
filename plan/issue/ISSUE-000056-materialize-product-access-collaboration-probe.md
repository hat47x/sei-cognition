# ISSUE-000056: Product Access / Collaboration reference probeを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0004, ADR-0006, ADR-0016, ADR-0030**  
Updated: 2026-09-01

## Goal

PMS-05とProduct Identity / Access / Collaboration baselineで定めた境界について、**authentication identity、Bounded Subject、Product access permission、semantic Responsibilityを混同せずに扱えること**をGoのreference probeで検証する。

あわせて、外部collaborator向けSelective Disclosureでcanonical sourceを変更せず、非開示情報を`unknown`へ読み替えないことを確認する。

## Probe方針

production IdP、OIDC server、enterprise directory、RBAC製品は導入しない。

Product security layerの最小要素だけをGoで実体化する。

```text
Authentication Identity
        │
        ▼
 Identity Binding
        │
        ▼
 Bounded Subject
        │
        ▼
 Product Access Policy
        │
        ├─ Guarded Canonical Access
        └─ Disclosure Projection
```

canonical meaningには既存`interactionprobe.CanonicalStore`と`semanticruntime`型を再利用する。

## 必須検査

1. 異なる二つのauthentication identityを同じBounded Subjectへbindingできる。
2. IdP相当のidentityを交換してもcanonical Responsibility Refを書き換えない。
3. Responsibility Refを持つsubjectでもProduct permissionがなければread / appendを許可しない。
4. Product `administer` permissionを持つsubjectへsemantic Responsibilityを自動付与しない。
5. actor kindがhuman / AI / serviceであることからpermissionを推定しない。
6. identity mapping不能の`not_evaluated`と、Policy上の`denied`を区別する。
7. enforcementでは`denied` / `not_evaluated`の双方をsafe failureとして拒否できる。
8. external collaborator向けProjectionで非開示recordを`withheld`として数え、fake Unknown recordを作らない。
9. Disclosure Projectionの生成前後でcanonical digestが変わらない。
10. scope readがない主体へSelective Disclosure Projection自体を返さない。
11. Product permissionを変更してもhistorical canonical Decision / Responsibilityを変更しない。

## Negative cases

- Decision Responsibilityがあることを理由にProduct readを自動許可する。
- Product administratorであることを理由にDecision Responsibilityを追加する。
- `actor_kind=human`だけでappendを許可する。
- identity bindingがない状態を明示的なPolicy `denied`として記録する。
- withheld recordをopaque Unknown semantic recordとしてcanonical storeへ追加する。
- Disclosure Projection生成時にcanonical recordを削除する。

## Requirement判断

probe開始時点では新しいStable Requirement / Scenario IDを追加しない。

既存REQ-0012 / 0013 / 0017、SCN-0007 / 0012を検査軸として利用し、Product access separationについてはCandidate Requirementとして扱う。

probeで、既存Requirementでは表現できない独立したProduct failureが明瞭になった場合に、新REQ / SCNを上流監査へ戻す。

## Non-goals

- production OIDC / SAML integration
- password / MFA実装
- enterprise IAM統合
- formal RBAC / ABAC policy language
- database row-level security
- encryption / key management
- production invitation UX
- session management
- Release / Operational / Adoption Evidence

## 完了条件

- [ ] Identity Bindingを実体化する。
- [ ] Product Access Policy evaluatorを実体化する。
- [ ] Guarded Canonical Accessを実体化する。
- [ ] Disclosure Projectionを実体化する。
- [ ] 必須検査とnegative caseをGo testへ落とす。
- [ ] existing interactionprobe / semanticruntimeとの重複監査を行う。
- [ ] CIで再現可能なExecutable Evidenceを得る。
- [ ] PMS-05 / Product / Architecture / Evidence文書へ結果を同期する。
- [ ] Stable Requirement / Scenario追加の要否を再監査する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied for probe plan**
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

PMS-05、Product Identity / Access / Collaboration baseline、ADR-0004 / 0006 / 0016 / 0030、REQ-0012 / 0013 / 0017、SCN-0007 / 0012、current interactionprobeを照合し、特定IdPやRBAC製品ではなく責務分離そのものを検査するprobeとして整理しました。Stable Requirementを先取りせず、actual probeで独立したProduct failureが確認された場合だけRequirement化へ戻す境界を維持しています。そのうえで、目的、検査条件、非対象、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。