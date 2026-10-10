# SEI Product Access Architecture

更新日: 2026-09-01  
状態: **Current Product Access Architecture Baseline**

## 1. この文書の役割

本書は、製品における主体の識別・アクセス制御・協働についての設計基準とADR-0030を、現行のSEI全体構成に位置付けます。

ここで扱うIdentity Binding、Product Access Scope、Policy Evaluator、Disclosure Projectionは、製品のセキュリティや協働に関する構成要素です。汎用的な意味上の実体ではありません。

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
SEI canonical     visible / withheld
semantic source       view
```

意味上の責任（Responsibility）や権限（Authority）を、このアクセス制御の処理への入力として自動的に使うことはしません。

```text
semantic Responsibility / Authority
  != Product Access Policy grant
```

## 3. Authentication Adapter

OIDC、SAML、ローカル認証、サービス用の資格情報などを通じて、現在の要求元を識別します。

認証用の接続部（Authentication Adapter）は資格情報やセッションの管理周期を扱えます。ただし、それらをBounded Subjectや判断の記録（Decision Memory）へ埋め込みません。

特定の認証基盤（IdP）を参照アーキテクチャの必須構成要素にはしません。

## 4. Identity Binding / Resolver

Authentication Provider固有のsubjectをADR-0004のBounded Subjectへ対応付けます。

複数の外部識別情報を同じBounded Subjectへ対応付けられます。これにより、認証基盤を交換しても過去の意味上の参照を保持できます。

この対応関係は、製品のセキュリティ設定や検証根拠です。汎用的な主体の定義そのものではありません。

ISSUE-000056のreference probeでは、旧・新IdP相当の二つのauthentication identityを同じBounded Subjectへbindingし、どちらからreadしてもhistorical DecisionのResponsibility Refが変化しないことを確認しました。

## 5. Product Access Scope

Product Access Scopeは、製品内の資源をアクセス制御上のまとまりとして扱うための境界です。

実装上はテナント、ワークスペース、プロジェクトなどに対応させられますが、意味上の組織やプロジェクトとは同一視しません。

```text
Product Access Scope ID
  != Semantic Logical Reference by default
```

current probeのscope IDもProduct-localです。将来の正式tenant / workspace modelとして固定しません。

## 6. Product Access Policy Evaluator

Bounded Subject、Product Access Scope、操作、必要な文脈情報を入力として、製品の操作権限を評価します。

参照用の検証では、読み取り、追加、確認、共有、管理に相当するread / append / review / share / administerを使います。

評価結果は少なくとも次を区別します。

- allowed
- denied
- not evaluated

`not_evaluated`と`denied`を、監査上は同じ意味として扱いません。ただし、操作を許可するかどうかの判定では、どちらも安全側に倒して拒否できます。

製品内の役割、主体の種類、意味上の責任や権限から、操作権限を知らないうちに推定することはしません。

probeでは、Responsibility Refを持つ主体でもread grantがなければ拒否され、binding済みAI主体でもappend grantがなければ拒否されることを確認しました。一方、identity binding自体がないhuman主体は`not_evaluated`となり、`denied`と区別されます。

## 7. Guarded Canonical Access

意味の正本を扱う実行環境や保存先に到達する前に、Product Access Policyを評価します。

読み取りを許可していない主体には正本の記録を返しません。また、追加を許可していない主体には正本を変更する操作を渡しません。

Product Access Policyが許可したことだけで、追加recordにsemantic Responsibility / Authorityを自動挿入しません。

probeでは、Product `administer` permissionを付与しても既存DecisionのResponsibility Refとcanonical digestが変化しないことを確認しました。

## 8. Disclosure Projection

Product Access Scopeの読み取りが許可されていても、外部の協力者には一部の記録を開示できない場合があります。

Disclosure Projectionは正本から共有用の表示を作り、非開示の記録を`withheld`として表すことができます。

```text
canonical digest before projection
  == canonical digest after projection
```

共有用の表示を作るときに、元の正本を削除したり上書きしたりすることはありません。

開示しない項目を、内容が不明な意味上の記録（Unknown）として保存することもしません。

ISSUE-000056のprobeでは、外部collaboratorへDecisionを非開示とするProjectionを生成し、Decision本文を返さず`WithheldCount`だけを外在化しました。Projection生成前後でcanonical digestが一致し、canonical Decision自体も残ることを確認しています。

Product Scopeのread permissionがない場合は、Selective Disclosure Projection自体を返しません。

## 9. Security audit

Authentication、identity resolution、Product Access Policy evaluation、Disclosure適用等をaudit eventとして記録できます。

ただし、現行の設計基準では、監査ログの形式を汎用的な契約として固定しません。

将来、複数deployment / IdP / security Providerで共通の耐久的意味が必要だと実証された場合にContract化を検討します。

## 10. Execution Authorizationとの境界

Product Access Architectureは「SEIのrecordやoperationへアクセスできるか」を扱います。

TEI、SaaS、外部resource等への実行AuthorizationはADR-0016のProvider boundaryへ残します。

```text
SEI append allowed
  != external execution authorized
```

## 11. Local Single-Node Packageとの関係

最初のLocal Single-Node Packageでは、Authentication Adapter、Identity Binding、Product Access Policyを同一processへ配置できます。

同じプロセスに配置したという理由で、意味上の責務を統合しません。チーム利用やホスト環境への配備へ進む場合も、同じ構成要素間の境界を維持できます。

## 12. Candidate Requirementとの関係

Product Access Controlをsemantic Responsibility / Authorityやactor kindから分離する必要性は、Designとscoped probeで支持されています。

ただしcurrent permission vocabulary、Product Access Scopeの粒度、Identity Binding lifecycleはreference Realizationです。

そのため、この全体構成だけを根拠に安定した要求IDを自動生成せず、製品の層で要求候補として保持します。

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

- `SEI_REFERENCE_ARCHITECTURE.md`
- `SEI_DEPLOYMENT_ARCHITECTURE.md`
- `../product/security/SEI_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
- `../plan/adr/ADR-0004-responsibility-without-global-identity.md`
- `../plan/adr/ADR-0016-authorization-evidence-provider-boundary.md`
- `../plan/adr/ADR-0030-product-access-control-separation.md`
- `../plan/issue/ISSUE-000056-materialize-product-access-collaboration-probe.md`
- `../runtime/ACCESS_COLLABORATION_PROBE_EVIDENCE_2026-09-01.md`

## 15. Natural Japanese review

Product Identity / Access / Collaboration baseline、ADR-0004 / 0016 / 0030、Product Interaction、Local Single-Node Deployment、`runtime/go/accessprobe`とcurrent CI Evidenceを照合し、Authentication、Identity Binding、Product Access Policy、Guarded Canonical Access、Disclosure Projectionを別componentとして配置しました。IdP相当identity交換後のResponsibility continuity、Product permissionとsemantic Responsibilityの非同一性、`denied` / `not_evaluated`分離、Selective Disclosureのcanonical非改変をscoped Evidenceとして反映する一方、production IAM / securityへは広げていません。同一process、tenant / workspace、permission vocabulary等の実装都合をUniversal semantic entityやStable Requirementへ昇格させない境界も維持しています。そのうえで、Architecture責務、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。