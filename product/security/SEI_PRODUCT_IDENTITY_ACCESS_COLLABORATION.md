# SEI Product Identity / Access / Collaboration

更新日: 2026-09-01  
状態: **Current Product Identity / Access / Collaboration Design Baseline**

## 1. この文書の役割

本書は、SEIを個人利用からチームや外部との協働へ広げる際に、**誰を認証するか、誰に製品操作を許すか、誰が意味上の責任と権限を持つか**を混同しないための境界を定めます。

ここでは、特定の認証基盤（IdP）、IAM、RBAC、テナント管理製品、暗号方式は選定しません。SEIが保持する意味を変えずに、製品へのアクセス制御と共同利用を成立させるための責務を区別します。

## 2. 最上位の分離

製品の識別情報とアクセス制御では、次の四つを区別します。

```text
authentication identity
  != Bounded Subject
  != product access permission
  != semantic Responsibility / Authority
```

### authentication identity

OIDCの`sub`、ローカルアカウントID、サービスアカウントIDなど、認証の提供元が現在のセッションや要求元を識別するためのIDです。

資格情報、パスワード、トークン、鍵、多要素認証（MFA）、セッションの管理周期は、認証の提供元または製品のセキュリティ層が扱います。

### Bounded Subject

ADR-0004で定めた、意味上・監査上の主体参照です。

```text
BoundedSubjectRef
  scope_ref
  subject_id
```

外部の認証基盤が発行する識別子とは同一視しません。認証基盤やログイン方式を変更しても、過去の判断や責任が参照する主体を、知らないうちに別人へ置き換えないための安定した参照です。

### product access permission

SEIの記録や操作に対して、現在の利用者が読み取り、追加、確認、共有、管理などを行ってよいかという、**製品利用上の許可**です。

この許可は、製品アクセス規則（Product Access Policy）で評価します。

### semantic Responsibility / Authority

ある判断、問い、実行について、誰がどの責任や権限を持っていたかという意味上の記録です。

製品アクセスの許可からこの記録を自動生成せず、その逆の変換も行いません。

```text
product admin
  != decision authority

recorded decision responsibility
  != product login permission
```

## 3. Product Access Scope

チーム、組織、外部との協働を扱うため、製品の層には**製品アクセス範囲（Product Access Scope）**を設けられます。

これは、どの利用者がどの製品内の資源へアクセスできるかを評価する、製品固有の境界です。

```text
Product Access Scope
  = product security / collaboration container
  != Universal semantic entity
```

実装ではテナント、ワークスペース、プロジェクト、リポジトリなどの名称を使うことがあります。ただし、その名称や階層をSEIの汎用的な中核に自動的に組み込むことはしません。

Product Access ScopeのIDをDecision、Responsibility、Logical Referenceのsemantic identityへ流用することも要求しません。

## 4. Identity Binding

認証の提供元が返す識別情報とBounded Subjectの対応関係は、**Identity Binding**として製品のセキュリティ層で管理します。

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

認証基盤をIdP AからIdP Bへ変更した場合でも、新旧の認証識別情報を同じBounded Subjectへ対応付けられます。

```text
idp-a / old-sub ─┐
                  ├─> subject(org-a, alice)
idp-b / new-sub ─┘
```

過去の判断にある責任主体の参照を、現在の認証基盤の`sub`で上書きすることはしません。

### 4.2 credentialをsemantic historyへ埋め込まない

パスワードのハッシュ、アクセストークン、更新用トークン、セッションID、MFAの秘密情報、秘密鍵などを、Bounded Subjectや判断の記録に含まれる永続的な意味として保存しません。

必要なセキュリティ監査の記録は別の根拠として参照できますが、資格情報そのものを意味上の識別子にはしません。

## 5. Product Access Policy

製品アクセス規則は、認証済みの主体が製品アクセス範囲内でどの操作を行えるかを評価します。

参照用の検証で使用する最小限の操作名は次のとおりです。

- `read`
- `append`
- `review`
- `share`
- `administer`

これらは現行の製品アクセス規則と検証で使用する操作名です。汎用的な役割の階層でも、将来の正式な製品操作権限の一覧でもありません。

### 5.1 Responsibility / Authorityからpermissionを推定しない

判断を行った主体として記録されていても、現行の製品アクセス規則で読み取りや追加が許可されていなければ、製品アクセスを自動的には許可しません。

### 5.2 Product roleからsemantic Authorityを推定しない

製品管理者、ワークスペースの所有者、メンバーなどの役割があっても、それだけで判断権限や責任を生成しません。

### 5.3 actor kindからpermissionを推定しない

人間、AI、サービス、組織という主体の種類だけを理由に、操作を許可することはありません。

AIだから読み取り専用、人間だから判断できる、といった一律の推定は、製品のアクセス制御に持ち込みません。

### 5.4 deniedとnot evaluatedを区別する

認証された識別情報をBounded Subjectへ対応付けられない場合や、規則の評価に必要な情報がない場合は、評価不能の状態として扱います。規則が明示的に拒否した`denied`とは区別します。

製品動作としては安全側に停止できますが、監査上は次を区別します。

```text
not evaluated != denied
```

## 6. Selective Disclosure

外部の利用者が製品アクセス範囲へ参加できても、正本に含まれるすべての情報を共有できるとは限りません。

選択的な情報開示（Selective Disclosure）では、正本の記録を削除・変更せず、共有用の表示（Projection）で開示する範囲を制御します。

```text
canonical source
   ├─ internal projection: visible
   └─ external projection: withheld
```

### 6.1 withheldとunknownを分ける

情報が存在していても開示しない場合は、それを`unknown`や「存在しない」という状態に置き換えません。

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

この簡素化を「SEIにはidentity boundaryが不要」という意味にはしません。

### team

複数のBounded Subjectを同じProduct Access Scopeへ参加させ、各subjectへProduct permissionを割り当てられます。

同じrecordへの並行操作が起きた場合、access controlは「最後に書いた人が意味上正しい」と判定しません。revision / conflict / historical continuityは既存semantic boundaryに従います。

### external collaborator

別organizationや別identity providerの主体も、Product Access Scopeへ限定的に参加できます。

外部主体へ内部directory全量やcredentialを共有することは要求しません。Bounded SubjectとSelective Disclosureによって、必要な範囲だけを共有できる構成を優先します。

## 8. Authentication / Authorization Providerとの境界

SEIは独自IdPの実装をProduct成立条件にしません。

Authenticationはlocal adapter、OIDC、enterprise directory等へ委ねられます。

また、SEI Product Access Controlと、ADR-0016で扱う**外部Execution ProviderのAuthorization**も分けます。

```text
SEI product access authorization
  != external execution authorization
```

SEIへrecordを書き込めることは、TEIやSaaSでoperationを実行できることを意味しません。

## 9. Product Access audit

後からsecurity incidentやcollaboration historyを確認するため、次のようなProduct access eventを監査可能にすることは有用です。

- authentication subjectがどのBounded Subjectへ解決されたか。
- どのProduct Access Scopeで、どのoperationを評価したか。
- allowed / denied / not evaluatedのどの状態だったか。
- Selective Disclosureを適用したか。
- access policyのどのversion / bindingを用いたか。

ただし、現時点ではUniversal `ProductAccessDecision` Contractを追加しません。まずProduct security Evidenceとして扱い、複数deployment / Providerで共通の耐久的意味が必要だと実証された場合に再検討します。

## 10. Requirement / Acceptanceの扱い

Product Access Controlをsemantic Responsibility / Authorityやactor kindから分離することには、独立したProduct security上の必要性があります。

一方、read / append / review / share / administer等のpermission vocabulary、Identity Bindingの適用範囲、Product Access Scopeのgranularityはまだreference probe段階です。

そのため、現時点では次を**Candidate Requirement**として保持します。

> SEIの製品アクセス権は、semantic Responsibility / Authorityやactor kindから自動導出せず、認証identityとの対応を含むProduct Access Policyで独立に評価できる必要がある。

ISSUE-000056のprobe結果から、既存REQ-0012 / 0013 / 0017へ統合できるか、新しいStable Requirement / Acceptance Scenarioが必要かを再監査します。

Stable IDはこのDesign baselineだけを理由に先取りしません。

## 11. first reference probe

ISSUE-000056では、production IdPを導入する前にGoの小さなreference probeを作ります。

最低限、次を検査します。

1. 二つのauthentication identityを同じBounded Subjectへbindingできる。
2. IdP交換後もcanonical Responsibility Refを書き換えない。
3. Responsibility Refを持つ主体でもProduct permissionがなければaccessを拒否する。
4. Product administratorでもsemantic Responsibilityを自動生成しない。
5. actor kindがhuman / AIであることからpermissionを推定しない。
6. identity解決不能の`not_evaluated`とPolicy上の`denied`を区別する。
7. external collaborator向けProjectionで非開示recordを`withheld`として表し、fake Unknown recordを作らない。
8. Disclosure Projection生成前後でcanonical sourceを変更しない。

probeのPASSをproduction securityやOIDC integrationの成立へ昇格させません。

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
- Product access separation Executable Evidence: **Scoped probe implemented; final CI synchronization pending**
- external IdP integration: **Not Yet Verified**
- production Selective Disclosure: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 14. 関連文書

- `../roadmap/SEI_PRODUCT_MILESTONES.md`
- `../interaction/SEI_PRODUCT_INTERACTION.md`
- `../../architecture/SEI_PRODUCT_ACCESS_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/adr/ADR-0004-responsibility-without-global-identity.md`
- `../../plan/adr/ADR-0006-bounded-federation-selective-disclosure.md`
- `../../plan/adr/ADR-0016-authorization-evidence-provider-boundary.md`
- `../../plan/adr/ADR-0030-product-access-control-separation.md`
- `../../plan/issue/ISSUE-000047-define-product-identity-authorization-and-collaboration-boundary.md`
- `../../plan/issue/ISSUE-000056-materialize-product-access-collaboration-probe.md`

## 15. Natural Japanese review

Product Value、PMS-05、ADR-0004 / 0006 / 0016、REQ-0012 / 0013 / 0017、SCN-0007 / 0012、Product Interaction、Local Single-Node Packaging、`runtime/go/accessprobe`へ戻り、identity、product access、semantic Responsibility / Authority、external execution authorizationを別責務として整理しました。tenant / workspaceや特定IdP、permission vocabularyをUniversal CoreやStable Requirementへ先に固定せず、外部identity交換後もhistorical subject referenceを保ち、Selective Disclosureでwithheldとunknownを混同しない境界を中心に置いています。そのうえで、要求の強さ、未決事項、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。