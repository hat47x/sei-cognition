# SEI Architecture

更新日: 2026-09-01  
状態: **Current Architecture Baseline**

## 1. このディレクトリの役割

`architecture/`は、current Product Value、Requirements、Accepted ADRを、SEIの現在の構造・境界・関係として説明します。

Architectureは新しい設計判断を本文だけで確定する場所ではありません。重要な判断が必要になった場合はIssue / ADRへ戻します。

```text
Product Value
  → Requirement
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
  SEI_REFERENCE_ARCHITECTURE.md
  SEI_DEPLOYMENT_ARCHITECTURE.md
  SEI_PRODUCT_ACCESS_ARCHITECTURE.md
  IMPLEMENTATION_LANGUAGE_POLICY.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

- `SEI_REFERENCE_ARCHITECTURE.md` — current SEI全体のReference Architecture
- `SEI_DEPLOYMENT_ARCHITECTURE.md` — ADR-0029に基づくLocal Single-Node Packageのcomponent配置、Persistence、save / resume、export / import境界
- `SEI_PRODUCT_ACCESS_ARCHITECTURE.md` — ADR-0030に基づくAuthentication、Identity Binding、Product Access Policy、Guarded Canonical Access、Selective Disclosureの配置
- `IMPLEMENTATION_LANGUAGE_POLICY.md` — ADR-0027に基づくproduction runtimeと研究・外部Realizationの実装言語境界
- `TRACEABILITY.md` — Product Value / REQ / ADR / architecture concern / current executable materialの追跡
- `history/HISTORICAL_ARCHITECTURE_MAPPING.md` — historical M48 / M49 / M50等からcurrent Architectureへの対応

設計関心領域が大きくなった場合は個別文書へ分割できます。重要なDecisionの恒久identityはADRが担うため、Architecture文書へ別の連番体系を要求しません。

## 3. Architectureの読み方

SEIのArchitectureは、固定された処理順序やservice topologyとしてではなく、**意味を失わないための関心領域と境界の網**として読みます。

たとえばDecision Memory、Capability、Cognitive Method、Persistence、Product Accessは重要な関心領域ですが、それぞれを独立microserviceやGo packageにすることを意味しません。

同様に、図中の矢印は原則として固定workflowを表しません。情報が参照・派生・判断材料・実行境界として関係し得ることを示します。

Local Single-Node Deploymentでは複数の論理componentを一つのGo processへ同居させられますが、これは配布・起動を小さく始めるための配置です。一つのprocessに入っていることを理由に、Interaction、Semantic Runtime、Persistence、Provider Integration、Product Accessを一つのsemantic concernへ統合しません。

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
SEI product access authorization != external execution authorization
withheld != unknown
```

これらの境界を変更する必要が生じた場合はArchitectureだけを書き換えず、対応するRequirement / ADRを再審査します。

## 5. current実体との関係

2026-09-01時点のactual repositoryには、Architectureの全関心領域を実装した完成系ではありませんが、次の限定された実体があります。

- current Semantic Contract familyとfixture群
- JCS+SHA-256 / raw-bytes+SHA-256 Representation Profile
- Go semantic runtime
- Go Provider Adapter slice
- Go end-to-end semantic Product Journey harness
- Go Product Interaction reference probe
- Go Packaging / Persistence reference probe
- Go Product Access / Collaboration reference probe
- Linux / amd64 Local Reference Package artifact workflow
- PythonによるV6 / V7 Projection Evaluation等の評価・開発補助

これらはArchitectureの一部境界を再現可能に確認するExecutable Evidenceです。Architecture concernをruntime componentへ一対一で固定したことも、Architecture全体を実装済みとしたことも意味しません。

ADR-0027により、SEI自身が所有するproduction runtimeの標準実装言語はGoとします。一方、これはSemantic Contractや外部Cognitive Method / Capability Providerの言語をGoへ固定する意味ではありません。詳細は`IMPLEMENTATION_LANGUAGE_POLICY.md`を参照します。

ADR-0029では、最初のPackaging / Deployment ProfileをLocal Single-Node Packageとしました。Goの単一バイナリ化とfilesystemは初期Realizationの利点として利用しますが、runtime executableやfile layoutをsemantic authorityにはしません。詳細は`SEI_DEPLOYMENT_ARCHITECTURE.md`を参照します。

ADR-0030では、Authentication Identity、Bounded Subject、Product Access Permission、semantic Responsibility / Authorityを分離しました。Product Access Scope、Identity Binding、Policy、Disclosure ProjectionはProduct security componentとして配置し、tenant / workspaceやpermission vocabularyをUniversal Coreへ昇格させません。詳細は`SEI_PRODUCT_ACCESS_ARCHITECTURE.md`を参照します。

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

一方、current Contract fixture、Representation Profile verifier、semantic runtime、Provider Adapter、Product Journey harness、Interaction probe、Packaging / Persistence probe、Product Access probeには、対象を限定したExecutable Evidenceがあります。

```text
Architecture exists
  != Architecture executable coverage complete
  != Product Release proven
  != production IAM / security proven
  != Operational Evidence
  != user-value realization
```

Packaging probeやLocal Reference Packageが通ったことも、power loss時のdurability、production DB migration、formal support matrixを証明しません。

Product Access probeが通ったことも、production OIDC / IAM、formal RBAC / ABAC、credential lifecycle、team deployment security、production Selective Disclosureを証明しません。

Go runtimeにExecutable Evidenceがあることも、Goがあらゆる将来要件で恒久的に最適であることを意味しません。言語方針の妥当性はPackaging / Deployment / Operational Evidenceを通じて継続的に検証します。

詳細は`../product/value/SEI_VALUE_ACCEPTANCE.md`と`TRACEABILITY.md`を参照します。

## 7. historical candidateの扱い

LibraryにはPhase 1候補として多数のArchitecture文書が残っています。

current baselineでは、それらから次を再利用します。

- 意味境界
- 反例
- 非採用理由
- Acceptance上の論点
- 設計系譜

一方、次は自動継承しません。

- M48 / M49 / M50というMilestone identity
- old package / field / schema shape
- historical local PASS
- current Product Boundaryと矛盾する配置

JCS / SHA-256 / JSON等のhistorical実装選択も、それ自体を理由にcurrent採用しません。ただしcurrentではADR-0023によりJCS+SHA-256とraw-bytes+SHA-256をRepresentation Profileとして改めてAcceptedし、actual fixture / verifierで限定的に検証しています。

同様に、過去にPythonを用いていたことやcurrent runtimeがGoであることだけからUniversalな言語制約を作りません。実装言語のcurrent DecisionはADR-0027を正本とします。

Local Single-Node Package、filesystem Persistence、`semantic.bundle.json`というlayoutもhistorical固定ではなく、ADR-0029に基づくcurrent初期profileです。将来別のPersistenceやdeployment topologyへ移行する際にsemantic identityを変えないことを優先します。

Product Access Scope、`read / append / review / share / administer`等のprobe vocabulary、Identity Bindingのcurrent shapeもhistorical固定ではありません。実IdP / team利用のEvidenceを得るまではProduct-localなRealizationとして扱います。

詳細は`history/HISTORICAL_ARCHITECTURE_MAPPING.md`を参照します。

## 8. Contract / Representation Profileとの境界

Architectureは意味構造と配置理由を説明します。

複数implementation、Provider、Storage、version等をまたいで検証可能な合意が必要な境界は`contracts/`へContract Definitionとして分離します。bytes、canonicalization、digest等の表現規則は、Semantic ContractからRepresentation Profileへ分けます。

```text
Architecture explains structure and boundaries
Contract defines portable / verifiable semantic agreement
Representation Profile defines bytes / canonicalization / digest agreement
Implementation language defines one realization choice
Deployment profile defines one component placement
Product Access Policy defines one security realization
```

ContractやProfileを増やすこと自体は目的ではなく、独立した互換性・検証境界が必要な場合だけ追加します。Goの型定義やpackage構造、Persistence interface、filesystem layout、Product Access Scopeやpermission vocabularyをContractの意味上の正本にはしません。

## 9. 文書品質

Architecture文書は、内容と構造を作成した後、意味、規範強度、例外、未決事項を変えず、**自然な日本語となることを最重要視して全文を再ドラフト**します。

その後、文章調整によってCore / Profile / Provider / Adapter / Projection / Persistence / Product Access等の境界やEvidence強度が変わっていないか最終意味監査を行います。

## 10. 関連文書

- `../product/value/SEI_PRODUCT_VALUE.md`
- `../product/value/SEI_VALUE_MODEL.md`
- `../product/value/SEI_VALUE_ACCEPTANCE.md`
- `../product/value/SEI_VALUE_TRACEABILITY.md`
- `../product/packaging/SEI_PRODUCT_PACKAGING.md`
- `../product/security/SEI_PRODUCT_IDENTITY_ACCESS_COLLABORATION.md`
- `../requirements/PRODUCT_REQUIREMENTS.md`
- `../requirements/ACCEPTANCE_SCENARIOS.md`
- `SEI_DEPLOYMENT_ARCHITECTURE.md`
- `SEI_PRODUCT_ACCESS_ARCHITECTURE.md`
- `TRACEABILITY.md`
- `IMPLEMENTATION_LANGUAGE_POLICY.md`
- `../plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`
- `../plan/adr/ADR-0022-runtime-first-slice-read-validate-reconstruct.md`
- `../plan/adr/ADR-0023-current-representation-profile-baseline.md`
- `../plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`
- `../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../plan/adr/ADR-0030-product-access-control-separation.md`

## 11. Natural Japanese review

current Product Value、Requirements、Accepted ADR、Semantic Contract / Representation Profile、Go semantic runtime、Provider Adapter、Product Journey harness、Product Interaction probe、Packaging / Persistence probe、Product Access / Collaboration probe、Local Reference Package、Python evaluation tooling、ADR-0027 / 0029 / 0030へ戻ってArchitectureの役割と現在地を再監査しました。Goをproduction runtimeの標準Realization、Local Single-Node Packageを初期Deployment Profileとして配置しつつ、Product Accessではauthentication identity、Bounded Subject、Product permission、semantic Responsibility / Authorityを分離しています。Semantic Contractや外部Method / Providerへ言語制約を広げず、single process、filesystem、Product Access Scope、permission vocabulary等をsemantic authorityやUniversal Coreへ昇格させない境界を維持しました。その後、意味、権威関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。