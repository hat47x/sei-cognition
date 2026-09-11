# SOZA Architecture

更新日: 2026-09-11  
状態: **Current Architecture Baseline — resume-first Interaction Working-Set Architecture reflected**

## 1. このディレクトリの役割

`architecture/`は、current Product Value、Requirements、Accepted ADRを、SOZAの現在の構造・境界・関係として説明します。

Architectureは新しい設計判断を本文だけで確定する場所ではありません。重要な判断が必要になった場合はIssue / ADRへ戻します。

```text
Product Value
  → Requirement / Candidate Requirement
  → ADR
  → Architecture
  → Contract / Representation Profile
  → Runtime / Provider Adapter / Test / Evidence
```

```text
Architecture description != Architecture Decision Record
Architecture concern != runtime component
Deployment component != semantic concern
```

## 2. Current canonical files

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  SOZA_INTERACTION_WORKING_SET_ARCHITECTURE.md
  SOZA_DEPLOYMENT_ARCHITECTURE.md
  SOZA_PRODUCT_ACCESS_ARCHITECTURE.md
  IMPLEMENTATION_LANGUAGE_POLICY.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

- `SOZA_REFERENCE_ARCHITECTURE.md` — current SOZA全体のReference Architecture。
- `SOZA_INTERACTION_WORKING_SET_ARCHITECTURE.md` — ISSUE-000073のresume-first Product Sliceについて、canonical / derived / transient / external state authority、working set、Resume Projection、AI suggestion、semantic commit、stale-write / partial-commit境界を定義する。
- `SOZA_DEPLOYMENT_ARCHITECTURE.md` — ADR-0029に基づくLocal Single-Node Packageのcomponent配置、Persistence、save / resume、export / import境界。
- `SOZA_PRODUCT_ACCESS_ARCHITECTURE.md` — ADR-0030に基づくAuthentication、Identity Binding、Product Access Policy、Guarded Canonical Access、Selective Disclosureの配置。
- `IMPLEMENTATION_LANGUAGE_POLICY.md` — ADR-0027に基づくproduction runtimeと研究・外部Realizationの実装言語境界。
- `TRACEABILITY.md` — Product Value / REQ / ADR / architecture concern / current executable materialの追跡。
- `history/HISTORICAL_ARCHITECTURE_MAPPING.md` — historical M48 / M49 / M50等からcurrent Architectureへの対応。

設計関心領域が大きくなった場合は個別文書へ分割できます。重要なDecisionの恒久identityはADRが担うため、Architecture文書へ別の連番体系を要求しません。

## 3. Architectureの読み方

SOZAのArchitectureは、固定された処理順序やservice topologyとしてではなく、**意味を失わないための関心領域と境界の網**として読みます。

たとえばDecision Memory、Capability、Cognitive Method、Persistence、Product Accessは重要な関心領域ですが、それぞれを独立microserviceやGo packageにすることを意味しません。

同様に、図中の矢印は原則として固定workflowを表しません。情報が参照・派生・判断材料・実行境界として関係し得ることを示します。

Local Single-Node Deploymentでは複数の論理componentを一つのGo processへ同居させられますが、これは配布・起動を小さく始めるための配置です。一つのprocessに入っていることを理由に、Interaction、Semantic Runtime、Persistence、Provider Integration、Product Accessを一つのsemantic concernへ統合しません。

ISSUE-000073では、この原則をProduct Interactionへ具体化しています。working set、Resume Brief、semantic change plan、snapshot token等は利用者体験やapplication mechanicsとして重要ですが、存在するだけでUniversal semantic entityになるわけではありません。

## 4. current Architectureが守る上位境界

少なくとも次を弱めません。

```text
Observation != Interpretation / Hypothesis
Recommendation != Decision
Decision != Authority
Authority != Action Intent
Action Intent != Execution
Execution != Business Outcome
Capability != Provider
Capability Definition != Capability Observation
Provider state != Capability interpretation
Matching != Decision
Pattern != Cognitive Method
Method Application != Assurance
Logical Reference != Exact Historical Binding
Semantic Contract != Representation Profile != verifier implementation
not observed != unavailable
binding not_verified != binding failed
Projection != Canonical Semantic Authority
runtime executable != canonical semantic data
filesystem locator != Logical Reference
Storage migration != Semantic Revision
authentication identity != Bounded Subject
Bounded Subject != product access permission
product access permission != semantic Responsibility / Authority
SOZA product access authorization != external execution authorization
withheld != unknown
working-set membership != semantic relation
AI suggestion != canonical commit
concurrency version != Semantic Revision
post-decision observation != historical decision basis
```

これらの境界を変更する必要が生じた場合はArchitectureだけを書き換えず、対応するRequirement / ADRを再審査します。

## 5. current実体との関係

actual repositoryにはArchitecture全体の完成実装はありませんが、次の限定された実体があります。

- current Semantic Contract familyとfixture群
- JCS+SHA-256 / raw-bytes+SHA-256 Representation Profile
- Go semantic runtime
- Go Provider Adapter slice
- Go end-to-end semantic Product Journey harness
- Go Product Interaction reference probe
- Go Packaging / Persistence reference probe
- Go Product Access / Collaboration reference probe
- Local Reference Package release material
- PythonによるV6 / V7 Projection Evaluation等の評価・開発補助

これらはArchitectureの一部境界を確認するScoped Executable Evidenceです。Architecture concernをruntime componentへ一対一で固定したことも、Architecture全体を実装済みとしたことも意味しません。

`SOZA_INTERACTION_WORKING_SET_ARCHITECTURE.md`は2026-09-11時点でDesign Evidenceです。working-set resolver、Resume Projection、Semantic Change Planner、Commit Coordinator、Context Egress Planner等のprototype Executable EvidenceはISSUE-000073で後続確認します。

ADR-0027により、SOZA自身が所有するproduction runtimeの標準実装言語はGoとします。一方、Semantic Contractや外部Cognitive Method / Capability Providerの言語をGoへ固定する意味ではありません。

ADR-0029では、最初のPackaging / Deployment ProfileをLocal Single-Node Packageとしました。Goの単一バイナリ化とfilesystemは初期Realizationの利点として利用しますが、runtime executableやfile layoutをsemantic authorityにはしません。

ADR-0030では、Authentication Identity、Bounded Subject、Product Access Permission、semantic Responsibility / Authorityを分離しています。Product Access Scopeやpermission vocabularyをUniversal Coreへ昇格させません。

## 6. Evidenceの扱い

Product Valueに従い、次の5段階を分けます。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Architecture本文とtraceabilityはDesign Evidenceです。

current Contract fixture、Representation Profile verifier、semantic runtime、Provider Adapter、Product Journey harness、Interaction probe、Packaging / Persistence probe、Product Access probeには対象を限定したExecutable Evidenceがあります。

```text
Architecture exists
  != Architecture executable coverage complete
  != Product Release proven
  != production UX proven
  != Operational Evidence
  != user-value realization
```

ISSUE-000073のresume-first Designが成立したことも、canonical-only resume、AI correction、fault injection、stale-write protection、human usabilityがactualに成立したことを意味しません。

Packaging probeやLocal Reference Packageが通ったことも、power loss時のdurability、production DB migration、formal support matrixを証明しません。

Product Access probeが通ったことも、production OIDC / IAM、formal RBAC / ABAC、credential lifecycle、team deployment security、production Selective Disclosureを証明しません。

詳細は`../product/value/SOZA_VALUE_ACCEPTANCE.md`と`TRACEABILITY.md`を参照します。

## 7. historical candidateの扱い

LibraryやhistoryにはPhase 1候補として多数のArchitecture文書が残っています。

current baselineでは、それらから意味境界、反例、非採用理由、Acceptance上の論点、設計系譜を再利用できます。一方、old package / field / schema shape、historical local PASS、旧Milestone identityをcurrentへ自動継承しません。

JCS / SHA-256 / JSON等のhistorical実装選択も、それ自体を理由にcurrent採用しません。current採用はAccepted ADRとactual Evidenceへ戻します。

同様にLocal Single-Node Package、filesystem Persistence、Product Access Scope、permission vocabulary、Interaction working set等を、current初期profileやprototypeで使うことだけからUniversal Coreへ固定しません。

詳細は`history/HISTORICAL_ARCHITECTURE_MAPPING.md`を参照します。

## 8. Contract / Representation Profileとの境界

Architectureは意味構造と配置理由を説明します。

複数implementation、Provider、Storage、version等をまたいで検証可能な合意が必要な境界は`contracts/`へContract Definitionとして分離します。bytes、canonicalization、digest等の表現規則はSemantic ContractからRepresentation Profileへ分けます。

```text
Architecture explains structure and boundaries
Contract defines portable / verifiable semantic agreement
Representation Profile defines bytes / canonicalization / digest agreement
Implementation language defines one realization choice
Deployment profile defines one component placement
Product Interaction working set defines one product-level navigation / projection concern
```

ContractやProfileを増やすこと自体は目的ではありません。

ISSUE-000073の`semantic change plan`やsnapshot tokenも、複数implementationをまたぐportable agreementが必要だとEvidenceで確認されるまでContract化しません。

## 9. 文書品質

Architecture文書は、内容と構造を作成した後、意味、規範強度、例外、未決事項を変えず、**自然な日本語となることを最重要視して全文を再ドラフト**します。

その後、文章調整によってCore / Profile / Provider / Adapter / Projection / Persistence / Product Access / Interaction working set等の境界やEvidence強度が変わっていないか最終意味監査を行います。

## 10. 関連文書

- `../product/value/SOZA_PRODUCT_VALUE.md`
- `../product/value/SOZA_VALUE_MODEL.md`
- `../product/value/SOZA_VALUE_ACCEPTANCE.md`
- `../product/value/SOZA_VALUE_TRACEABILITY.md`
- `../product/interaction/SOZA_PRODUCT_INTERACTION.md`
- `../product/interaction/SOZA_FIRST_USABLE_PRODUCT_SLICE.md`
- `../product/packaging/SOZA_PRODUCT_PACKAGING.md`
- `../product/security/SOZA_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
- `../requirements/PRODUCT_REQUIREMENTS.md`
- `../requirements/ACCEPTANCE_SCENARIOS.md`
- `SOZA_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `SOZA_DEPLOYMENT_ARCHITECTURE.md`
- `SOZA_PRODUCT_ACCESS_ARCHITECTURE.md`
- `TRACEABILITY.md`
- `IMPLEMENTATION_LANGUAGE_POLICY.md`
- `../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`
- `../plan/adr/ADR-0028-product-interaction-canonical-operation-boundary.md`
- `../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../plan/adr/ADR-0030-product-access-control-separation.md`

## 11. Natural Japanese review

2026-09-11時点のProduct Value、Requirements、Accepted ADR、Semantic Contract / Representation Profile、Go semantic runtime、Provider Adapter、Product Interaction probe、Packaging / Persistence、Product Access、Local Reference Package、ISSUE-000073へ戻ってArchitectureの入口を再監査した。

新しいInteraction Working-Set Architectureをcurrent canonical fileとして登録し、working set / Resume Brief等を製品設計上の重要な関心として扱いつつUniversal Coreへ昇格させない境界を追加した。また、AI suggestionとcanonical commit、concurrency versionとSemantic Revision、post-decision Observationとhistorical basisの非同一性をArchitecture入口でも読めるようにした。

意味、権威関係、留保、Evidence強度を変えず、自然な日本語として一続きに読めるよう全文を再ドラフトし、最終意味監査を実施した。