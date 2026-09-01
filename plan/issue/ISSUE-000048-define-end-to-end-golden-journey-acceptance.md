# ISSUE-000048: end-to-end golden journeyとProduct Acceptanceを定義する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Updated: 2026-09-01

## Goal

個別Contract、fixture、runtime sliceの成立だけでなく、利用者から見た一続きの判断仕事としてSOZAの価値を確認できる**代表的なend-to-end Acceptance Scenario**を定義する。

このScenarioを固定workflow ontologyにはせず、Product Shapeと既存REQ / SCNを横断してMinimum Usable Product Shapeを検査するためのgolden journeyとして扱う。

## 背景

current repositoryには、Semantic Reference、Decision Memory、Capability Observation、Semantic Interchange、Representation Profile、first runtime、synthetic Provider Adapter、Cognitive Method Contract等がある。

しかし、これらは主に意味境界ごとのDesign / scoped Executable Evidenceであり、利用者が一つのInquiryを始めてからDecision、外部実行、後日のreviewまでを通して価値を確認するend-to-end Acceptanceはまだ確立していない。

```text
component / contract PASS
  != end-to-end product acceptance
```

## 2026-09-01 中間整理

`requirements/PRODUCT_JOURNEY_COMPOSITION.md`でProduct ShapeとREQ-0001〜REQ-0022、SCN-0001〜SCN-0017を照合した。

現時点の結論は次のとおりである。

1. Minimum Usable Product Shapeの主要な意味要求は既存REQで概ね表現できる。
2. Product Journeyを理由に新しいUniversal Requirementを追加する必要は、現時点では確認できない。
3. 不足しているのは、既存Requirementを一つのjourneyで同時に成立させるend-to-end Acceptance Scenarioである。
4. 特に、**external execution後に得たObservationを次のInquiry / Decision reviewへ戻す循環**が、current SCNでは一つのScenarioとして明示されていない。
5. stable Scenarioを確定した後、Executable harnessの実体化は別Issueへ分離する方が、DesignとImplementationの未完了を混同しにくい。

## golden journey候補

代表Scenarioとして、少なくとも次の流れを具体化する。

```text
Inquiryを開始する
  ↓
Observation / Evidenceを追加する
  ↓
Unknown / Conflictを残す
  ↓
Cognitive Methodを適用する
  ↓
Recommendationを作る
  ↓
DecisionとResponsibilityを記録する
  ↓
Capability / Providerを選び外部実行へ渡す
  ↓
Execution Receipt / resulting Observationを戻す
  ↓
時間経過後にhistorical basisを読み直す
  ↓
残差または新EvidenceからInquiryを再開する
```

すべての利用でこの順序を必須にしない。Acceptance harnessが複数の重要境界を一度に検査するための代表経路とする。

## Requirement再整理

新しいREQ番号を先に作らない。

### 一続きのDecision contextを再開できること

既存REQ-0001、REQ-0005、REQ-0014で必要な意味を表現できる。

### human / AI Surfaceから同じcanonical meaningへ戻れること

既存REQ-0010、REQ-0011、REQ-0019で必要な意味を表現できる。

### owned execution engineなしでもProduct journeyが成立すること

既存REQ-0007、REQ-0021、REQ-0022で必要な意味を表現できる。

### execution resultを新しいObservationとして戻せること

必要な個別の意味はREQ-0001、REQ-0002、REQ-0005、REQ-0014、REQ-0022等へ追跡できる。

ただし、外部実行後のObservationから次のInquiryへ戻る循環を一つのAcceptance Scenarioで検証する必要がある。

### low-impactからaudit-readyへ連続的に詳細化できること

既存REQ-0010、REQ-0011、REQ-0019とSCN-0013で必要な意味を表現できる。

## Requirement追加に関する判断

現時点では**新しいREQは追加しない**。

Product Journeyの順序やUXをRequirementへ昇格させると、Product Interactionやworkflow構造をUniversal semantic Coreへ持ち込む危険がある。

新しいREQは、end-to-end Scenarioを具体化する中で既存REQでは表現できない独立した規範上の必要性が確認できた場合だけ追加する。

## Scenario再整理

新しいScenarioは、既存SCN-0001〜SCN-0017の単なる要約ではなく、それらの意味境界が**一つのProduct Journeyで同時に壊れないこと**を検査する。

少なくとも次のvariantを同じScenario familyで扱う。

1. **normal path** — Evidenceが十分で外部実行まで進む。
2. **uncertain path** — Unknown / Conflictを残したままDecisionし、後日再開する。
3. **human / AI collaborative path** — AIがMethod / Recommendationを担い、人間または委任された主体がDecisionする。
4. **provider replacement path** — 実行Providerを変えてもhistorical Decisionを読める。
5. **no execution path** — SOZA内でDecisionまで行い、実行しなくても記録価値が成立する。

## stable Scenarioへ入れる期待

- Inquiry開始時に最大詳細を強制しない。
- Observation、Interpretation、Unknown、ConflictをDecisionへ黙って畳み込まない。
- Method Definition / Realization / Applicationを必要な範囲で読み分けられる。
- RecommendationをDecisionへ自動昇格させない。
- DecisionとResponsibility / Authorityを必要な粒度で追える。
- Provider run IDをDecision identityにしない。
- Execution successをDecision correctnessへ昇格させない。
- 実行後に得たObservationを、過去Decision作成時のEvidenceとして扱わない。
- residual / reopen informationを保持し、後からInquiryへ戻れる。
- ProjectionやProviderを交換してもcanonical meaningを再読できる。

## stable Scenarioへ入れる失敗例

- AI RecommendationをそのままDecisionとして保存する。
- Decision作成時にUnknown / Conflictをresolvedへ変える。
- Provider runが成功しただけでDecisionを`verified`とする。
- 後から得たObservationで過去Decisionのbasisを上書きする。
- current ProviderやUIがなくなると過去Decisionを読めない。

## Executable Acceptanceの考え方

最初のharnessはproduction UIを必要条件にしない。

Canonical Semantic Access Surfaceに相当する最小adapter / CLI / API / test harness等から、同じjourneyを再構成できる形でもよい。

最小harnessでは、少なくとも次を確認する。

1. journey内の各Artifact / recordをstable Referenceで辿れる。
2. Decisionからbasis、Method Application、Responsibility、residualへ戻れる。
3. external execution resultを新しいObservationとして接続できる。
4. 実行後Observationが過去Decision basisへ時間逆行して混入しない。
5. Provider交換後もhistorical Decisionを再構成できる。
6. no-execution variantでもDecision recordが成立する。
7. unknown / unsupported record versionをopaque + `not_verified`として保持できる。
8. Projectionだけからcanonical meaningを推測復元しない。

ただし、次を分ける。

```text
semantic end-to-end harness PASS
  != usable human interaction proven
  != packaged product proven
  != release ready
  != operationally reliable
  != user outcome proven
```

human usabilityはISSUE-000045、PackagingはISSUE-000046、Identity / CollaborationはISSUE-000047と連携して段階的にEvidenceを高める。

## Non-goals

- 一つのgolden journeyを全利用者へ強制すること
- 現在のMilestone順序を業務workflowへ固定すること
- production UI完成を本Issueの開始条件にすること
- workflow / agent engineの内製
- Adoption / Outcomeをsynthetic harnessだけでSatisfiedにすること

## 完了条件

- [x] Product Shapeと既存REQ / SCNの重複・不足を監査する。
- [x] 新しいREQを追加する必要が現時点でないことを確認する。
- [x] normal / uncertain / collaborative / provider replacement / no executionの主要variantをAcceptanceへ整理する。
- [x] semantic end-to-end harnessの入力・期待結果・失敗条件をDesignとして定義する。
- [ ] 必要な追加SCNへstable IDを付与し、Acceptance Scenario正本へ反映する。
- [ ] Cognitive Method、Decision、Capability / Provider、residual / reopenを一続きにtraceするExecutable harnessを別Issueへ起票する。
- [ ] Executable Evidenceを得た範囲だけRequirement / Value Traceabilityを更新する。
- [ ] Release / Operational / Adoption・Outcomeへ過大昇格させない。
- [x] 今回追加・更新した文書を自然な日本語へ全文再ドラフトし、最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Partially Satisfied** — Requirement composition、主要variant、期待・失敗条件、semantic harnessの最小条件まで整理済み。stable SCNへの反映は未完了。
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product ShapeのMinimum Usable Product Shape、REQ-0001〜0022、SCN-0001〜0017、`PRODUCT_JOURNEY_COMPOSITION.md`、5段階Evidence、Cognitive Method / Decision / Capabilityのcurrent境界へ戻り、Requirement追加の必要性とAcceptance gapを再評価した。その結果、新しいUniversal Requirementは増やさず、外部実行後のObservationから再検討へ戻る循環を含むend-to-end Scenarioを追加する方針へ絞った。意味、規範強度、Evidenceの高さを変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
