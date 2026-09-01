# ISSUE-000039: Human / AI ReadabilityとProgressive Explicitnessを再現可能に評価する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

SOZAのV6 Human / AI ReadabilityとV7 Progressive Explicitnessについて、特定のUI技術や製品画面へ早期固定せず、**同じcanonical meaningを人間向けProjectionとmachine-readable representationの双方から回収できること**、および**案件の影響度に応じて明示量を変えても必要な意味を失わないこと**を、再現可能な評価系で検証する。

このIssueの目的は「UIを完成させること」ではない。

```text
Projection evaluation
  != Product UI completion
  != Universal UI ontology
  != Release readiness
```

## Background

current Product Value Traceabilityでは、V1〜V5とV8にはContract、fixture、Representation Profile、first semantic runtime、synthetic Provider Adapter等の限定Executable Evidenceが存在していた。

一方、V6 / V7では、human-readable Contract Definitionやmachine-readable Schema、Progressive ExplicitnessのDesign boundaryは存在していたものの、具体的なProjectionを使った再現可能なExecutable Evidenceが不足していた。

この状態のままRelease準備やUI実装を先行すると、「意味は厳密だが人間には追いにくい」「簡単に使うためにはcanonical meaningを削る」といった逆転が起こり得るため、本IssueでUI技術から独立した評価harnessを先に実体化した。

## Product Value trace

### Value Axis

- **V6 Human / AI Readability**
- **V7 Progressive Explicitness**

### Requirements

- **REQ-0010** — Progressive Semantic Explicitness
- **REQ-0011** — Projectionを意味上の正本にしない
- **REQ-0019** — 人間とAIの双方が意味を読める
- **REQ-0020** — Evidenceを超える達成主張をしない

### Acceptance Scenarios

- **SCN-0004** — 軽量案件と高影響案件
- **SCN-0006** — Projectionを作り直す
- **SCN-0013** — 簡略UIとcanonical meaningを両立する
- **SCN-0017** — Evidenceが低い段階で達成主張を監査する

### Current Evidence

- Design: **Satisfied within the evaluation boundary** — light / audit Projection、semantic question set、Progressive Explicitness policy、negative cases、structured human review形式を定義した。
- Executable: **Partially Satisfied** — representative canonical sourceからProjectionを生成・交換し、意味整合とnegative caseをactual CIで再現した。
- Release: **Not Yet Verified**。
- Operational: **Not Yet Verified**。
- Adoption / Outcome: **Not Yet Verified**。

## Questions and findings

### 1. 同一canonical Artifactからlight / auditを作れるか

作れることを確認した。

```text
canonical source
  ├─ light Projection
  └─ audit Projection
```

両Projectionは別のcanonical recordを持たず、同じsourceから決定的に再生成する。

### 2. human Projectionとmachine-readable representationから同じ意味へ戻れるか

次の6 semantic questionsを固定し、audit Projectionとmachine-readable sourceの回答が一致することをcheckerで確認した。

1. 何がDecisionされたか。
2. 何が未解決のまま残ったか。
3. 何がbasisとして使われたか。
4. どのResponsibilityが関係するか。
5. Authorization Evidenceの認識状態は何か。
6. basisに関係するProvenanceへ戻れるか。

light ProjectionではQ1 / Q2 / Q5を前景化し、Q3 / Q4 / Q6は存在件数とaudit Projectionへの導線を保持する。

### 3. low-impact / high-impactで明示量を変えられるか

評価用Policyとして、次を再現した。

- low-impact / reversible: lightを標準とし、canonical sourceに存在しない最大詳細を一律入力必須にしない。
- high-impact / consequential: auditを要求し、basis、unresolved、Responsibility、Authorization Evidence state、Provenanceへ降りられなければ合格にしない。

この区別は固定のUniversal impact taxonomyではなく、Progressive Explicitnessの評価入力である。

### 4. Projection固有stateの逆流を検出できるか

Projection生成前後のcanonical source structural digestを比較し、Projection編集によりcanonical sourceを書き換えるケースをnegative caseとして検出する。

### 5. 新しいUniversal Contract / Core概念は必要だったか

不要だった。

current Decision Memory / Semantic Interchange / Capability ObservationとProjectionという既存Architecture concernの組合せで評価系を構成できた。評価harness自体はUniversal Contract familyへ昇格させない。

### 6. Human / AI Readabilityを単一スコアにする必要があるか

必要ない。

machine-checkableな意味整合はsemantic question / invariant checkerで検査し、人間の理解可能性は`HUMAN_REVIEW_TEMPLATE.md`のstructured reviewでScenario単位に記録する。

## Deliverables

### Evaluation protocol

```text
evaluation/v6-v7/README.md
```

V6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017、ADR-0005 / 0018 / 0020 / 0021へ追跡している。

### Canonical evaluation sources

```text
fixtures/contracts/v1alpha1/evaluation/
  E1-projection-rich-decision.json
  E2-low-impact-minimal-decision.json
```

E1はbasis、unresolved、Responsibility、Capability Observation、Provenanceを含むrich caseである。

E2は可逆なlow-impact Decisionであり、basis / Responsibility等の最大詳細を一律必須にしない。

### Projection examples

```text
evaluation/v6-v7/projections/
  light.md
  audit.md
```

### Checker / negative cases

```text
evaluation/v6-v7/check_projection_evaluation.py
evaluation/v6-v7/negative-cases.json
```

7件のnegative caseを固定した。

1. unresolvedを隠す。
2. basisへの導線を失う。
3. Responsibilityへの導線を失う。
4. canonical sourceにないAuthorization成立を追加する。
5. Projection編集でcanonical sourceを書き換える。
6. high-impactをlightだけで完了扱いにする。
7. low-impactへaudit最大詳細を一律強制する。

### Human structured review

```text
evaluation/v6-v7/HUMAN_REVIEW_TEMPLATE.md
```

テンプレートの存在自体をOperational / Adoption Evidenceとは扱わない。

### CI

```text
.github/workflows/projection-evaluation.yml
```

同じrunでcurrent Contract baselineを再検査した後、V6 / V7 evaluation harnessを実行する。

## Executable Evidence

GitHub Actions `V6 V7 Projection Evaluation`:

- Run ID: `33456710459`
- Head SHA: `513600724976a110aa21a48cd3fc3db44e55a048`
- current Contract baseline recheck: **success**
- V6 / V7 Projection evaluation: **success**
- conclusion: **success**

評価harnessでは次を直接確認した。

- canonical source 2件がcurrent Contractに適合する。
- rich canonical sourceからlight / auditの2 Projectionを再現できる。
- committed Projection例と決定的rendererの出力が一致する。
- audit Projectionとmachine-readable sourceで6 semantic questionsが一致する。
- light ProjectionがDecision、unresolved、Authorization Evidence stateを保持する。
- light Projectionがbasis / Responsibility / Provenanceの存在とaudit導線を失わない。
- Projectionを再生成してもcanonical sourceが変化しない。
- low-impactは最大詳細を強制しない。
- high-impactはaudit detailを要求する。
- 7 negative casesを期待したerror codeで検出する。

## Completion criteria

### Semantic / Design Acceptance

- [x] 評価protocolがV6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017へ追跡できる。
- [x] light / auditの意味差を「表示量の差」として扱い、別canonical meaningにしていない。
- [x] 人間向けProjectionとmachine-readable representationのsemantic question setを定義している。
- [x] negative caseがcanonical meaning lossと過剰明示の双方を含む。

### Executable Acceptance

- [x] representative canonical sourceから少なくとも二つのProjectionを再現できる。
- [x] 自動検査可能なsemantic invariant / negative caseがactual repositoryでPASSする。
- [x] Projection交換後もcanonical sourceが保持されることを再現できる。
- [x] high-impact caseでは必要情報が欠落せず、low-impact caseでは不要な最大詳細を強制しないことを評価できる。

## Evidence boundary

本Issueで成立したのは、**evaluation-harness scoped Executable Evidence**までである。

```text
projection harness PASS
  != production UX validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

特に、次は未検証のまま残す。

- 実利用者が実務上必要な時間・負担で意味を理解できるか。
- 実際のWeb / desktop / CLI等のProjectionで同じ境界を維持できるか。
- 異なるAI実装が同じcanonical meaningを安定して回収できるか。
- productionでimpact classをどのように決定・変更するか。
- 判断品質、誤読率、見落とし率、業務成果が改善するか。

## Resolution / reopen conditions

本IssueはExecutable Acceptanceまで満たしたためResolvedとする。

新しいUniversal semantic conceptは追加していない。

次の場合は再開または後続Issueを検討する。

- production Projectionや実利用で、人間には必要な意味が見えない反例が得られた。
- 簡略化のためにcanonical意味を削らなければ成立しないケースが見つかった。
- high-impact案件で必要な明示量がcurrent評価境界では不足する。
- low-impact案件でlight boundaryでも過剰な入力負担が生じる。
- human / AI間でsemantic questionへの回答が継続的に食い違う。

production UX、Operational、Adoption / Outcomeの未検証だけを理由に本IssueをOpenへ戻さず、それぞれ適切な後続Evidence sliceとして扱う。

## Natural Japanese review

Product Value Traceability、Value Acceptance、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017、ADR-0005 / 0018 / 0020 / 0021、current Contract、実際のevaluation fixture / checker / Projection、GitHub Actions Run `33456710459`へ戻ってResolutionを照合した。その後、UI実装とProduct Value評価、Executable EvidenceとRelease / Operational / Adoption・Outcomeを混同しないよう意味と留保を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
