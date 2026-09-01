# ISSUE-000047: Product Identity / Authorization / Collaboration boundaryを定義する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0004, ADR-0006, ADR-0016, ADR-0021**  
Updated: 2026-09-01

## Goal

SOZAのsemanticなResponsibility / Authorityと、製品利用時のlogin、identity、access control、tenant / workspace、共有、Selective Disclosureを混同せず、実際の製品security / collaboration boundaryを定義する。

## 背景

current SOZAでは次を意図的に分けている。

```text
actor identity
  != Responsibility
  != Authority
  != Authorization Evidence
```

この分離はsemantic modelとして重要だが、実際の製品では「誰がどのrecordを読めるか・書けるか」「どの組織やworkspaceへ属するか」「外部IdPをどう利用するか」も決める必要がある。

Product securityの都合を理由にResponsibility / Authorityの意味をlogin roleへ平坦化せず、逆にsemantic Authority recordが存在することだけからsystem accessを自動付与しない境界が必要である。

## 検討対象

### Identity

- local identityをSOZA自身が所有する必要があるか。
- external IdP / enterprise directoryとの境界をどうするか。
- stable actor referenceとauthentication subjectをどのように対応付けるか。
- identity provider交換後もhistorical Responsibilityを読めるようにするには何が必要か。

### Authorization

- read / write / append / review / administer等の製品access controlをどこで定義するか。
- semantic Authority / Authorization Evidenceとproduct access controlをどう分離するか。
- AI / service account / humanの種別だけから権限を推定しないこと。

### Collaboration boundary

- single-user、team、organization、external collaboratorをどの粒度で扱うか。
- tenant / workspace概念がUniversal semantic Coreに必要か、それともProduct / deployment concernか。
- concurrent edit、review、handoffの最低限の整合条件は何か。

### Selective Disclosure

- withheldとunknownを区別したまま、共有範囲を制御できるか。
- canonical recordを複製して意味を分岐させずに、Projection / disclosure boundaryを構成できるか。
- external collaboration時にProvenance / Exact Bindingをどこまで共有する必要があるか。

## Requirement候補

stable ID付与前に、少なくとも次を監査する。

- REQ-0012 — Bounded CollaborationとSelective Disclosure
- REQ-0013 — actor種別からAuthority等を推定しない
- REQ-0017 — Responsibilityを文脈に結び付ける
- REQ-0020 — Evidenceを超える達成主張をしない

既存Requirementがsemantic側だけを定め、product security上の追加Requirementが必要と確認できた場合だけ追加する。

## Non-goals

- 独自Identity Providerの実装を前提にすること
- enterprise IAM製品との全統合を一度に実装すること
- semantic AuthorityをRBAC roleへ置換すること
- tenant IDをUniversal Coreへ無条件に追加すること
- cryptographic access-control schemeの早期固定

## 完了条件

- [ ] semantic Responsibility / Authorityとproduct access controlの境界を定義する。
- [ ] identity source / actor reference / historical continuityの方針を定める。
- [ ] single-userからteam利用へ進む最小collaboration boundaryを定める。
- [ ] Selective Disclosureのproduct-level Acceptanceを具体化する。
- [ ] 既存REQ / SCNとの重複監査後、必要な追加だけを行う。
- [ ] Architecture / Contract / Product policyのどこへ各責務を置くかADRで決める。
- [ ] security conformanceまたはprototypeのExecutable Evidence条件を定義する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Not Yet Verified for product identity / access control**
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

ADR-0004 / 0006 / 0016、REQ-0012 / 0013 / 0017、Selective DisclosureとAuthorization Evidenceの既存境界へ戻り、semantic Authorityとproduct access controlを別責務として扱う課題に整理した。tenant / workspaceや独自IdPをCoreへ先に固定せず、実際の利用・security要件から配置を決める方針を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
