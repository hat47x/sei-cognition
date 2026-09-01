# ISSUE-000048: end-to-end golden journeyとProduct Acceptanceを定義する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Updated: 2026-09-01

## Goal

個別Contract、fixture、runtime sliceの成立だけでなく、利用者から見た一続きの判断仕事としてSOZAの価値を確認できる**代表的なend-to-end Acceptance Scenario**を定義する。

このScenarioを固定workflow ontologyにはせず、Product Shapeと既存REQ / SCNを横断してMinimum Usable Product Shapeを検査するためのgolden journeyとして扱う。

## 背景

current repositoryには、Semantic Reference、Decision Memory、Capability Observation、Semantic Interchange、Representation Profile、first runtime、synthetic Provider Adapter、Cognitive Method設計等がある。

しかし、これらは主に意味境界ごとのDesign / scoped Executable Evidenceであり、利用者が一つのInquiryを始めてからDecision、外部実行、後日のreviewまでを通して価値を確認するend-to-end Acceptanceはまだ確立していない。

```text
component / contract PASS
  != end-to-end product acceptance
```

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

まずProduct ShapeのMinimum Usable Product Shapeと既存REQ-0001〜REQ-0022を照合し、次の候補が既存Requirementで十分かを確認する。

### 候補A — 一続きのDecision contextを再開できること

主な既存候補:

- REQ-0001 耐久的な意味の連続性
- REQ-0005 Decisionの歴史的再構成
- REQ-0014 未解決残差と再開条件の保持

不足がある場合だけ追加Requirementを定義する。

### 候補B — human / AI Surfaceから同じcanonical meaningへ戻れること

主な既存候補:

- REQ-0010 Progressive Semantic Explicitness
- REQ-0011 Projectionを意味上の正本にしない
- REQ-0019 人間とAIの双方が意味を読める

### 候補C — owned execution engineなしでもProduct journeyが成立すること

主な既存候補:

- REQ-0007 Capability / Providerの中立性
- REQ-0021 Realization / Executionを交換可能にする
- REQ-0022 Provider-neutralなCapability Observation

### 候補D — execution resultを新しいObservationとして戻せること

Recommendation / Decision / Execution / Business Outcomeの非同一性を保ったまま、外部実行から次の認知・判断へ戻るProduct Acceptanceが既存REQ / SCNで十分かを監査する。

### 候補E — low-impactからaudit-readyへ連続的に詳細化できること

主な既存候補:

- REQ-0010
- REQ-0011
- REQ-0019
- SCN-0013

## Scenario再整理

既存SCN-0001〜SCN-0017を組み合わせてもgolden journeyのAcceptanceが明瞭にならない場合は、新しいSCNを追加する。

少なくとも次のvariantを検討する。

1. **normal path** — Evidenceが十分で外部実行まで進む。
2. **uncertain path** — Unknown / Conflictを残したままDecisionし、後日再開する。
3. **human / AI collaborative path** — AIがMethod / Recommendationを担い、人間または委任された主体がDecisionする。
4. **provider replacement path** — 実行Providerを変えてもhistorical Decisionを読める。
5. **no execution path** — SOZA内でDecisionまで行い、実行は行わない。それでも記録価値が成立する。

## Executable Acceptanceの考え方

最初のharnessはproduction UIを必要条件にしない。

Canonical Semantic Access Surfaceに相当する最小adapter / CLI / API / test harness等から、同じjourneyを再構成できる形でもよい。

ただし、次を分ける。

```text
semantic end-to-end harness PASS
  != usable human interaction proven
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

- [ ] Product Shapeと既存REQ / SCNの重複・不足を監査する。
- [ ] 必要な追加REQ / SCNだけをstable IDで起票する。
- [ ] normal / uncertain / collaborative / provider replacement / no executionの主要variantをAcceptanceへ整理する。
- [ ] semantic end-to-end harnessの入力・期待結果・失敗条件を定義する。
- [ ] Cognitive Method、Decision、Capability / Provider、residual / reopenを一続きにtraceできることを確認する。
- [ ] Executable Evidenceを得た範囲だけRequirement / Value Traceabilityを更新する。
- [ ] Release / Operational / Adoption・Outcomeへ過大昇格させない。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Not Yet Verified for end-to-end Acceptance**
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product ShapeのMinimum Usable Product Shape、REQ-0001〜0022、SCN-0001〜0017、5段階Evidence、Cognitive Method / Decision / Capabilityのcurrent境界へ戻り、個別sliceのPASSを製品全体の成立と混同しないend-to-end Acceptance課題として整理した。既存Requirementを優先して再利用し、不足が確認できた意味だけを追加する方針を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
