# SOZA Architecture

更新日: 2026-08-31  
状態: **Current Architecture Baseline**

## 1. このディレクトリの役割

`architecture/`は、current Product Value、Requirements、Accepted ADRを、SOZAの現在の構造・境界・関係として説明します。

Architectureは新しい設計判断を本文だけで確定する場所ではありません。重要な判断が必要になった場合はIssue / ADRへ戻します。

```text
Product Value
  → Requirement
  → ADR
  → Architecture
  → Contract
  → Implementation / Test / Evidence
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
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

- `SOZA_REFERENCE_ARCHITECTURE.md` — current SOZA全体のReference Architecture
- `TRACEABILITY.md` — Product Value / REQ / ADR / architecture concernの追跡
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
Matching != Decision
Pattern != Cognitive Method
Method Application != Assurance
Logical Reference != Exact Historical Binding
not observed != unavailable
binding not_verified != binding failed
Projection != Canonical Semantic Authority
```

これらの境界を変更する必要が生じた場合はArchitectureだけを書き換えず、対応するRequirement / ADRを再審査します。

## 5. Evidenceの扱い

このArchitecture baselineはDesign Evidenceです。

Architecture文書がactual repositoryに存在することは、runtime implementation、schema conformance、release、production operationを証明しません。

```text
Architecture exists != Executable Evidence
```

Executable / Release / Operational Acceptanceは`SOZA_VALUE_ACCEPTANCE.md`に従って別に確認します。

## 6. historical candidateの扱い

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
- JCS / Go / JSON等の実装選択
- historical local PASS
- current Product Boundaryと矛盾する配置

詳細は`history/HISTORICAL_ARCHITECTURE_MAPPING.md`を参照します。

## 7. Contractとの境界

Architectureは意味構造と配置理由を説明します。

複数implementation、Provider、Storage、version等をまたいで検証可能な合意が必要な場合は`contracts/`へContract Definitionを作ります。

```text
Architecture explains structure and boundaries
Contract defines portable / verifiable agreement
```

Contract新設の必要性はArchitectureから導出しますが、Architectureを詳しく書くためだけにContractを増やしません。

## 8. 文書品質

Architecture文書は、内容と構造を作成した後、意味、規範強度、例外、未決事項を変えず、**自然な日本語となることを最重要視して全文を再ドラフト**します。

その後、文章調整によってCore / Profile / Provider / Adapter / Projection等の境界が変わっていないか最終意味監査を行います。

## 9. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`

## 10. Natural Japanese review

current / historical / runtimeの境界とArchitectureの責務を確定した後、意味とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
