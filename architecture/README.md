# SOZA Architecture

更新日: 2026-09-01  
状態: **Current Architecture Baseline**

## 1. このディレクトリの役割

`architecture/`は、current Product Value、Requirements、Accepted ADRを、SOZAの現在の構造・境界・関係として説明します。

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
```

## 2. Current canonical files

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  IMPLEMENTATION_LANGUAGE_POLICY.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

- `SOZA_REFERENCE_ARCHITECTURE.md` — current SOZA全体のReference Architecture
- `IMPLEMENTATION_LANGUAGE_POLICY.md` — ADR-0027に基づくproduction runtimeと研究・外部Realizationの実装言語境界
- `TRACEABILITY.md` — Product Value / REQ / ADR / architecture concern / current executable materialの追跡
- `history/HISTORICAL_ARCHITECTURE_MAPPING.md` — historical M48 / M49 / M50等からcurrent Architectureへの対応

設計関心領域が大きくなった場合は個別文書へ分割できます。重要なDecisionの恒久identityはADRが担うため、Architecture文書へ別の連番体系を要求しません。

## 3. Architectureの読み方

SOZAのArchitectureは、固定された処理順序やservice topologyとしてではなく、**意味を失わないための関心領域と境界の網**として読みます。

たとえばDecision Memory、Capability、Cognitive Method、Persistenceは重要な関心領域ですが、それぞれを独立microserviceやGo packageにすることを意味しません。

同様に、図中の矢印は原則として固定workflowを表しません。情報が参照・派生・判断材料・実行境界として関係し得ることを示します。

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
```

これらの境界を変更する必要が生じた場合はArchitectureだけを書き換えず、対応するRequirement / ADRを再審査します。

## 5. current実体との関係

2026-09-01時点のactual repositoryには、Architectureの全関心領域を実装した完成系ではありませんが、次の限定された実体があります。

- current Semantic Contract familyとfixture群
- JCS+SHA-256 / raw-bytes+SHA-256 Representation Profile
- Go semantic runtime
- Go Provider Adapter slice
- Go end-to-end semantic Product Journey harness
- PythonによるV6 / V7 Projection Evaluation等の評価・開発補助

これらはArchitectureの一部境界を再現可能に確認するExecutable Evidenceです。Architecture concernをruntime componentへ一対一で固定したことも、Architecture全体を実装済みとしたことも意味しません。

ADR-0027により、SOZA自身が所有するproduction runtimeの標準実装言語はGoとします。一方、これはSemantic Contractや外部Cognitive Method / Capability Providerの言語をGoへ固定する意味ではありません。詳細は`IMPLEMENTATION_LANGUAGE_POLICY.md`を参照します。

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

一方、current Contract fixture、Representation Profile verifier、semantic runtime、Provider Adapter、Product Journey harnessには、対象を限定したExecutable Evidenceがあります。

```text
Architecture exists
  != Architecture executable coverage complete
  != Release Evidence
  != Operational Evidence
  != user-value realization
```

Go runtimeにExecutable Evidenceがあることも、Goがあらゆる将来要件で恒久的に最適であることを意味しません。言語方針の妥当性はPackaging / Deployment / Operational Evidenceを通じて継続的に検証します。

詳細は`../product/value/SOZA_VALUE_ACCEPTANCE.md`と`TRACEABILITY.md`を参照します。

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

詳細は`history/HISTORICAL_ARCHITECTURE_MAPPING.md`を参照します。

## 8. Contract / Representation Profileとの境界

Architectureは意味構造と配置理由を説明します。

複数implementation、Provider、Storage、version等をまたいで検証可能な合意が必要な境界は`contracts/`へContract Definitionとして分離します。bytes、canonicalization、digest等の表現規則は、Semantic ContractからRepresentation Profileへ分けます。

```text
Architecture explains structure and boundaries
Contract defines portable / verifiable semantic agreement
Representation Profile defines bytes / canonicalization / digest agreement
Implementation language defines one realization choice
```

ContractやProfileを増やすこと自体は目的ではなく、独立した互換性・検証境界が必要な場合だけ追加します。Goの型定義やpackage構造をContractの意味上の正本にはしません。

## 9. 文書品質

Architecture文書は、内容と構造を作成した後、意味、規範強度、例外、未決事項を変えず、**自然な日本語となることを最重要視して全文を再ドラフト**します。

その後、文章調整によってCore / Profile / Provider / Adapter / Projection等の境界やEvidence強度が変わっていないか最終意味監査を行います。

## 10. 関連文書

- `../product/value/SOZA_PRODUCT_VALUE.md`
- `../product/value/SOZA_VALUE_MODEL.md`
- `../product/value/SOZA_VALUE_ACCEPTANCE.md`
- `../product/value/SOZA_VALUE_TRACEABILITY.md`
- `../requirements/PRODUCT_REQUIREMENTS.md`
- `../requirements/ACCEPTANCE_SCENARIOS.md`
- `TRACEABILITY.md`
- `IMPLEMENTATION_LANGUAGE_POLICY.md`
- `../plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`
- `../plan/adr/ADR-0022-runtime-first-slice-read-validate-reconstruct.md`
- `../plan/adr/ADR-0023-current-representation-profile-baseline.md`
- `../plan/adr/ADR-0024-provider-adapter-observation-mapping-boundary.md`
- `../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`

## 11. Natural Japanese review

current Product Value、Requirements、Accepted ADR、Semantic Contract / Representation Profile、Go semantic runtime、Provider Adapter、Product Journey harness、Python evaluation tooling、およびADR-0027へ戻ってArchitectureの役割と現在地を再監査した。Goをproduction runtimeの標準Realizationとして明示しつつ、Semantic Contractや外部Method / Providerへ言語制約を広げない境界を維持した。その後、意味、権威関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。