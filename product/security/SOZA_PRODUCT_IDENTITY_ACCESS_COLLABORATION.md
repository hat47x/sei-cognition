# SOZA Product Identity / Access / Collaboration

更新日: 2026-09-01  
状態: **Current Product Identity / Access / Collaboration Design Baseline**

## 1. この文書の役割

この文書は、SOZAをsingle-userの利用からteam・外部協働へ広げるときに、**誰を認証し、誰に製品操作を許し、誰が意味上のResponsibility / Authorityを持つのか**を混同しないためのProduct boundaryを定めます。

ここで定めるのは、特定のIdP、IAM製品、RBAC製品、tenant製品、暗号方式ではありません。SOZAのsemantic meaningを保ったまま、実際の製品アクセス制御と協働を成立させるための責務分離を定めます。

## 2. 最上位の分離

Product Identity / Accessでは、次の四つを別のものとして扱います。

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

### authentication identity

OIDC `sub`、local account ID、service account ID等、認証Providerが現在のsessionやrequest主体を識別するためのIDです。

credential、password、token、key、MFA、session lifecycleはAuthentication ProviderまたはProduct security layerの責務です。

### Bounded Subject

ADR-0004で定めた、意味上・監査上の主体参照です。

```text
BoundedSubjectRef
  scope_ref
  subject_id
```

外部IdPの識別子と同一視しません。IdPやlogin方式を変更しても、過去DecisionやResponsibilityが参照する主体を黙って別人へ読み替えないためのstable referenceです。

### product access permission

SOZA製品のrecordやoperationに対して、現在の利用者がread、append、review、share、administer等を行ってよいかという、**製品利用上のpermission**です。

このpermissionはProduct Access Policyが評価します。

### semantic Responsibility / Authority

あるDecision、Inquiry、Execution等について、誰がどのResponsibilityやAuthorityを持っていたかという意味上の記録です。

Product Access Permissionから自動生成せず、逆方向にも自動変換しません。

```text
product admin
  != decision authority

recorded decision responsibility
  != product login permission
```

## 3. Product Access Scope

team・organization・external collaborationを扱うため、Product layerには**Product Access Scope**を置けます。

これは、どの利用者がどのProduct resourceへアクセスできるかを評価するための製品ローカルな境界です。

```text
Product Access Scope
  = product security / collaboration container
  != Universal semantic entity
```

実装ではtenant、workspace、project、repository等の名前を使う可能性がありますが、その名称や階層をSOZA Universal Coreへ自動的に昇格させません。

Product Access ScopeのIDをDecision、Responsibility、Logical Referenceのsemantic identityへ流用することも要求しません。

## 4. Identity binding

認証Providerが返すidentityとBounded Subjectの対応は、**Identity Binding**としてProduct security layerに置きます。

```text
Authentication Provider subject
          │
          ▼
    Identity Binding
          │
          ▼
   Bounded Subject Ref
```

### 4.1 IdP交換

IdP AからIdP Bへ移行した場合、新旧の認証identityを同じBounded Subjectへ対応付けられます。

```text
idp-a / old-sub ─┐
                  ├─> subject(org-a, alice)
idp-b / new-sub ─┘
```

過去DecisionのResponsibility Refを書き換えて現在のIdP `sub`へ置換しません。

### 4.2 credentialをsemantic historyへ埋め込まない

password hash、access token、refresh token、session ID、MFA secret、private key等をBounded SubjectやDecision Memoryの耐久的意味として保持しません。

必要なsecurity auditは別Evidenceとして参照できますが、credential自体をsemantic identityにはしません。

## 5. Product Access Policy

Product Access Policyは、現在の認証主体がProduct Access Scope内でどのoperationを行えるかを評価します。

最小operation vocabularyの候補は次です。

- `read`
- `append`
- `review`
- `share`
- `administer`

これはProduct policy vocabularyであり、Universal semantic role hierarchyではありません。

### 5.1 Responsibility / Authorityからpermissionを推定しない

Decision makerとして記録されている主体でも、現在のProduct Access Policyでread / appendが許可されていなければ、製品アクセスを自動許可しません。

### 5.2 Product roleからsemantic Authorityを推定しない

Product administrator、workspace owner、member等のroleが存在しても、それだけでDecision AuthorityやResponsibilityを生成しません。

### 5.3 actor kindからpermissionを推定しない

human、AI、service、organizationというactor kindだけでpermissionを与えません。

AIだからread-only、人間だからDecision可能、といった固定推定をProduct boundaryに持ち込みません。

### 5.4 deniedとnot evaluatedを区別する

認証identityをBounded Subjectへ解決できない、必要なPolicy contextがない等の理由で評価できなかった状態を、policyが明示的に拒否した`denied`と同じ意味に潰しません。

製品動作としては安全側に停止できますが、監査上は次を区別します。

```text
not evaluated != denied
```

## 6. Selective Disclosure

外部協働では、Product Access Scopeへ参加できても、canonical contextの全量を共有できるとは限りません。

Selective Disclosureでは、canonical recordを削除・改変せず、共有Projection側で開示範囲を制御します。

```text
canonical source
   ├─ internal projection: visible
   └─ external projection: withheld
```

### 6.1 withheldとunknownを分ける

情報が存在するが開示しない場合、それを`unknown`や「存在しない」へ変換しません。

```text
withheld
  != unknown
  != not observed
  != deleted
```

外部Projectionには、内容そのものを漏らさず「開示されていない情報がある」ことだけを示すnoticeを載せられます。

### 6.2 canonical sourceを分岐させない

外部共有のたびにcanonical recordを複製し、internal版・external版を別のmeaning historyとして増殖させることを標準にはしません。

同じcanonical sourceからDisclosure Policyに応じたProjectionを作ることを基本とします。

### 6.3 Exact Binding / Provenance

相手へpayloadを開示できない場合でも、必要な範囲でprovenanceや検証可能なbindingを共有できる余地を残します。ただし、bindingの存在だけを理由に非開示payloadへアクセスできるようにはしません。

## 7. Collaborationの最小境界

### single-user

最小local packageでは、一つのlocal identityを一つのProduct Access Scopeへ対応付ける簡素なProfileを許容します。

この簡素化を「SOZAにはidentity boundaryが不要」という意味にはしません。

### team

複数のBounded Subjectを同じProduct Access Scopeへ参加させ、各subjectへProduct permissionを割り当てられます。

同じrecordへの並行操作が起きた場合、access controlは「最後に書いた人が意味上正しい」と判定しません。revision / conflict / historical continuityは既存semantic boundaryに従います。

### external collaborator

別organizationや別identity providerの主体も、Product Access Scopeへ限定的に参加できます。

外部主体へ内部directory全量やcredentialを共有することは要求しません。Bounded Subject aliasとSelective Disclosureによって、必要な範囲だけを共有できます。

## 8. Authentication / Authorization Providerとの境界

SOZAは独自IdPの実装をProduct成立条件にしません。

Authenticationはlocal adapter、OIDC、enterprise directory等へ委ねられます。

また、SOZA Product Access Controlと、ADR-0016で扱う**外部Execution ProviderのAuthorization**も分けます。

```text
SOZA product access authorization
  != external execution authorization
```

SOZAへrecordを書き込めることは、TEIやSaaSでoperationを実行できることを意味しません。

## 9. Product Access audit

後からsecurity incidentやcollaboration historyを確認するため、次のようなProduct access eventを監査可能にすることは有用です。

- authentication subjectがどのBounded Subjectへ解決されたか。
- どのProduct Access Scopeで、どのoperationを評価したか。
- allowed / denied / not evaluatedのどの状態だったか。
- Selective Disclosureを適用したか。
- access policyのどのversion / bindingを用いたか。

ただし、現時点ではUniversal `ProductAccessDecision` Contractを追加しません。まずProduct security Evidenceとして扱い、複数deployment / Providerで共通の耐久的意味が必要だと実証された場合に再検討します。

## 10. Requirement / Acceptance

この境界から、既存Requirementだけでは不足するproduct security上の独立した規範として、REQ-0023を追加します。

> SOZAの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出してはならず、認証identityとの対応を含むProduct Access Policyで独立に評価できなければならない。

既存のREQ-0012 / 0013 / 0017と組み合わせて、SCN-0019でIdP交換、product adminとDecision Responsibilityの分離、Selective Disclosureを検査します。

## 11. first reference probe

ISSUE-000056では、production IdPを導入する前にGoの小さなreference probeを作ります。

最低限、次を検査します。

1. 二つのauthentication identityを同じBounded Subjectへbindingできる。
2. IdP交換後もcanonical Responsibility Refを書き換えない。
3. Responsibility Refを持つ主体でもProduct permissionがなければaccessを拒否する。
4. Product administratorでもsemantic Responsibilityを自動生成しない。
5. actor kindがhuman / AIであることからpermissionを推定しない。
6. identity解決不能の`not evaluated`とPolicy上の`denied`を区別する。
7. external collaborator向けProjectionで非開示recordを`withheld`として表し、`unknown` recordを捏造しない。
8. disclosure Projection生成前後でcanonical sourceを変更しない。

このprobeのPASSをproduction securityやOIDC integrationの成立へ昇格させません。

## 12. 現時点で固定しないこと

- OIDC / SAML / passkey等の正式authentication方式
- Keycloak、Entra ID、Okta等の特定IdP
- RBAC / ABACのどちらをProduct標準とするか
- tenant / workspaceの正式名称と階層
- database row-level security
- encryption key management
- MFA policy
- session timeout
- SCIM
- enterprise directory sync
- external collaborator invitation UX
- production security audit retention

## 13. Evidence状態

- Product Identity / Access / Collaboration Design Evidence: **Established by this baseline**
- Product access separation Executable Evidence: **Not Yet Verified at document creation time**
- external IdP integration: **Not Yet Verified**
- production Selective Disclosure: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 14. 関連文書

- `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- `../interaction/SOZA_PRODUCT_INTERACTION.md`
- `../../architecture/SOZA_PRODUCT_ACCESS_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/adr/ADR-0004-responsibility-without-global-identity.md`
- `../../plan/adr/ADR-0006-bounded-federation-selective-disclosure.md`
- `../../plan/adr/ADR-0016-authorization-evidence-provider-boundary.md`
- `../../plan/adr/ADR-0030-product-access-control-separation.md`
- `../../plan/issue/ISSUE-000047-define-product-identity-authorization-and-collaboration-boundary.md`
- `../../plan/issue/ISSUE-000056-materialize-product-access-collaboration-probe.md`

## 15. Natural Japanese review

Product Value、PMS-05、ADR-0004 / 0006 / 0016、REQ-0012 / 0013 / 0017、SCN-0007 / 0012、Product InteractionとLocal Single-Node Packagingへ戻り、identity、product access、semantic Responsibility / Authority、external execution authorizationを別責務として整理しました。tenant / workspaceや特定IdPをUniversal Coreへ先に固定せず、外部identity交換後もhistorical subject referenceを保ち、Selective Disclosureでwithheldとunknownを混同しない境界を中心に置いています。そのうえで、要求の強さ、未決事項、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。