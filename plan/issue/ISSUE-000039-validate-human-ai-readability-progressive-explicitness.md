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

V1〜V5とV8にはContract、fixture、Representation Profile、semantic runtime、synthetic Provider Adapter等の限定Executable Evidenceが先行していた。一方、V6 / V7については、意味境界は定義されていたものの、具体的なProjectionと明示量切替を使った再現可能なExecutable Evidenceが不足していた。

このため、本IssueではUI製品仕様を作るのではなく、Projectionをcanonical authorityへ昇格させない小さな評価harnessを作り、V6 / V7の意味境界を反証可能な形で検査した。

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

- Design: **Satisfied for this evaluation boundary** — protocol、semantic question set、light / audit Projection、low / high impact評価policy、negative case、structured human review様式を実体化した。
- Executable: **Partially Satisfied at evaluation-harness scope** — current Contractに適合する2件のcanonical sourceからProjectionを再生成し、6 semantic questions、7 negative cases、Projection交換、low / high policyをCIで検査した。
- Release: **Not Yet Verified**。
- Operational: **Not Yet Verified**。
- Adoption / Outcome: **Not Yet Verified**。

## Questionsと得られた回答

### 1. 同一canonical sourceから軽量表示と監査表示を作れるか

作れる。`evaluation/v6-v7/`では、同じrich canonical sourceからlight / audit Projectionを生成し、Projection生成前後でcanonical sourceのstructural digestが変わらないことを検査する。

Projectionを削除・再生成しても、canonical meaning自体はProjectionに依存しない。

### 2. 人間向けProjectionとmachine-readable representationから同じ意味へ戻れるか

評価harnessでは、少なくとも次の6 semantic questionsを固定した。

1. 何がDecisionされたか。
2. 何が未解決のまま残ったか。
3. 何がbasisとして使われたか。
4. どのResponsibilityが関係するか。
5. Authorization Evidenceの認識状態は何か。
6. basisに関係するProvenanceへ戻れるか。

Audit Projectionはmachine-readable canonical sourceと6項目を照合する。Light Projectionでは全詳細を前景化せず、Decision、unresolved、Authorization Evidence stateを保持し、basis / Responsibility / Provenanceの存在件数とauditへの導線を残す。

### 3. 低影響と高影響で明示量を変えられるか

評価用policyとして再現できた。

- low-impact / reversible: light Projectionを許容し、存在しないbasis / Responsibility等を最大詳細として一律入力必須にはしない。
- high-impact / consequential: audit Projectionを要求し、lightだけで完了扱いにしない。

この`low / high`は評価harness上の入力であり、SOZA Universal Coreへ固定risk taxonomyを追加する判断ではない。

### 4. Projection固有stateの逆流をどう検査するか

canonical sourceのdigest比較とnegative caseで検査する。Projection生成や再生成によってcanonical sourceが暗黙に変わる場合は失敗とする。

### 5. 新しいUniversal ContractやCore概念は必要だったか

必要なかった。current Decision Memory / Semantic Interchange Contractをcanonical sourceとして利用し、Projection評価は`evaluation/v6-v7/`へ隔離できた。

したがって、本Issueから新しいADRやUniversal semantic conceptを追加しない。

### 6. Human / AI Readabilityを単一スコアへ還元せず評価できるか

できる。機械評価ではsemantic questionとnegative caseを使い、人間向け評価では`HUMAN_REVIEW_TEMPLATE.md`でScenario単位に`scenario-satisfied / partially-satisfied / not-satisfied / not-yet-verified`を記録する。

人間review templateが存在すること自体は、人間による実利用Evidenceではない。

## 実体化した評価基線

### Protocol / harness

- `evaluation/v6-v7/README.md`
- `evaluation/v6-v7/check_projection_evaluation.py`
- `evaluation/v6-v7/negative-cases.json`
- `evaluation/v6-v7/projections/light.md`
- `evaluation/v6-v7/projections/audit.md`
- `evaluation/v6-v7/HUMAN_REVIEW_TEMPLATE.md`

### Canonical source

- `fixtures/contracts/v1alpha1/evaluation/E1-projection-rich-decision.json`
- `fixtures/contracts/v1alpha1/evaluation/E2-low-impact-minimal-decision.json`

E1はbasis、unresolved、Responsibility、Capability Observation、Provenanceを含むrich / high-impact側の入力である。E2は低影響・可逆な案件を想定したminimal Decisionであり、最大詳細を一律必須にしないことの反証材料として使う。

### Negative cases

次の7件を固定し、期待するerror codeで拒否できることを検査する。

1. 未解決事項をlight Projectionから隠す。
2. basisがcanonical sourceにあるのにlightから存在へ辿れなくする。
3. Responsibilityがcanonical sourceにあるのにlightから存在へ辿れなくする。
4. canonical sourceにないAuthorization成立をProjectionが追加する。
5. Projectionの副作用としてcanonical sourceを書き換える。
6. high-impact案件をlightだけで完了扱いにする。
7. low-impact案件へaudit最大詳細を一律必須化する。

## Executable Evidence

GitHub Actions `V6 V7 Projection Evaluation` Run `33456710459`（run #2）がsuccessした。

このRunでは、少なくとも次を確認した。

- current Contract baseline recheck: **success**
- canonical source: **2件**
- Projection profile: **light / audit**
- semantic question: **6件**
- negative case: **7件**
- Projection再生成: canonical sourceを変更せず再現可能
- low-impact: lightを許容
- high-impact: auditを要求

この結果はProduct Value TraceabilityとSCN-0004 / 0006 / 0013 / 0017へ反映済みである。

## Completion criteria

### Semantic / Design Acceptance

- [x] 評価protocolがV6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017へ追跡できる。
- [x] light / auditの意味差を表示量の差として扱い、別canonical meaningにしていない。
- [x] 人間向けProjectionとmachine-readable representationのsemantic question setを定義した。
- [x] negative caseがcanonical meaning lossと過剰明示の双方を含む。

### Executable Acceptance

- [x] representative canonical sourceから少なくとも二つのProjectionを再現できる。
- [x] 自動検査可能なsemantic invariant / negative caseがactual repositoryでPASSした。
- [x] Projection交換後もcanonical sourceが保持されることを再現した。
- [x] high-impact caseでは必要情報を隠さず、low-impact caseでは不要な最大詳細を強制しないことを評価できる。

## Resolution

本Issueは**evaluation-harness scoped Executable Acceptanceまで完了したためResolved**とする。

このResolutionは、V6 / V7全体が実運用で実証されたことを意味しない。特に、実利用者が必要な時間と負担で意味を理解できるか、production UIで誤読や見落としが起きないか、異なるAI実装が長期に同じ意味へ戻れるか、判断品質や業務成果が改善するかは未検証である。

```text
Projection Evaluation PASS
  != production UX validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

また、評価中に既存意味境界では表せない新しいUniversal semantic conceptは確認されなかったため、本Issueから新しいADR / Core概念は追加しない。

## Reopen conditions

次の場合は、本Issueを再開するか、より具体的な後続Issueを作成する。

- production Projectionで必要な意味が人間から見えない。
- light化によってcanonical meaningや重要な未解決状態が失われる。
- high-impact案件で必要な明示量が不足する。
- low-impact案件で最大詳細が事実上必須となり、Progressive Explicitnessが機能しない。
- 人間reviewや異なるAI実装で、6 semantic questionsへ安定して戻れない反例が得られる。
- evaluation harnessのpolicyをUniversal Coreへ昇格させなければならないように見える新しい意味差が現れる。

## Natural Japanese review

Product Value Traceability、Value Acceptance、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017、ADR-0005 / 0018 / 0020 / 0021、current Contract、`evaluation/v6-v7/`の実装、Run `33456710459`へ戻って、設計時の問いと実測結果を照合した。その後、UI実装とProduct Value評価、evaluation-harness scoped Executable EvidenceとRelease / Operational / Adoption・Outcomeを混同しないよう意味と留保を固定し、自然な日本語となることを最重要視して全文を再ドラフトした。最後に、ResolutionによってEvidence強度を過大評価していないことを再監査済みである。
