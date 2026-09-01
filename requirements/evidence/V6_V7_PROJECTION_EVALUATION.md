# V6 / V7 Projection Evaluation Protocol v0.1

更新日: 2026-09-01  
状態: **Evaluation Baseline / Not Product UI Specification**  
関連Issue: **ISSUE-000039**

## 1. 目的

この文書は、SOZAのV6 Human / AI ReadabilityとV7 Progressive Explicitnessを、特定のWeb画面、CLI、desktop UI、dashboard等へ固定せずに評価するためのprotocolです。

検証する中心は次の二点です。

1. 同じcanonical meaningを、人間向けProjectionとmachine-readable representationの双方から矛盾なく回収できること。
2. 案件の影響度に応じて表示・確認する情報量を変えても、canonical meaningを削除したり、存在しない意味を追加したりしないこと。

このprotocolはProjectionの評価方法を定めるものであり、製品UIの仕様書ではありません。

```text
Projection evaluation
  != Product UI specification
  != Canonical Semantic Authority
```

## 2. Product Value trace

### Value Axis

- V6 Human / AI Readability
- V7 Progressive Explicitness

### Requirements

- REQ-0010 — Progressive Semantic Explicitness
- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0019 — 人間とAIの双方が意味を読める
- REQ-0020 — Evidenceを超える達成主張をしない

### Acceptance Scenarios

- SCN-0004 — 軽量案件と高影響案件
- SCN-0006 — Projectionを作り直す
- SCN-0013 — 簡略UIとcanonical meaningを両立する
- SCN-0017 — Evidenceが低い段階で達成主張を監査する

## 3. Canonical source

評価では、`fixtures/evaluation/v1alpha1/decision-projection-source.json`をcanonical sourceとして使用します。

このfixtureは`soza.decision-memory/v1alpha1`に従うDecisionであり、評価に必要な次の情報を含みます。

- Decision statement
- context reference
- basis references
- unresolved references
- contextual responsibility reference
- rationale

Projection側にだけ新しい意味を追加しません。特にAuthority / Authorizationの成立をDecisionから推定してはなりません。

## 4. 評価する二つのProjection

### 4.1 Light Projection

日常的な確認を想定した、人間向けの簡潔なMarkdown表示です。

Light Projectionは全Reference IDを前景化しません。ただし、次が存在することを隠してはなりません。

- basis
- unresolved state
- responsibility
- Authority / AuthorizationがDecision単独からは確定しないこと

つまり、簡潔さのために意味を消すのではなく、**詳細へ降りられることを残したまま前景情報を減らします。**

### 4.2 Audit Projection

監査・高影響案件の確認を想定した、構造化JSON表示です。

次をcanonical sourceからそのまま保持します。

- source Contract
- Decision reference
- statement
- context references
- basis references
- unresolved references
- responsibility references
- rationale

Audit Projectionもcanonical sourceではありません。Projectionを削除してもDecision Memoryは失われません。

## 5. Semantic question set

人間向けProjectionとmachine-readable representationが「同じ意味を読める」ことは、文章が同じであることではなく、次の問いへの意味上の回答が矛盾しないことで評価します。

1. 何がDecisionされたか。
2. どのbasisが明示的に参照されているか。
3. 何が未解決のまま残っているか。
4. contextual ResponsibilityへのReferenceは存在するか。
5. Decision単独からAuthority / Authorizationの成立を推定していないか。
6. Rationaleは何か。

Light ProjectionではReferenceの全IDを表示しないため、問い2〜4は「存在と件数を識別でき、audit detailへ降りられること」を最低条件とします。

## 6. Progressive Explicitnessの評価規則

このevaluation harnessでは、SCN-0004を再現するために二つの評価caseを置きます。

### low-impact / reversible

- Light Projectionで日常確認を開始できる。
- Audit Projectionも利用できる。
- 最大詳細の表示を常時必須にはしない。

### high-impact / externally consequential

- Light Projectionだけで評価完了としてはならない。
- Audit Projectionへ降り、basis、unresolved、responsibility等を確認できることを要求する。

これは**評価fixture上のpolicy**であり、SOZA Universal Coreへ`low / high`という固定risk levelを追加する判断ではありません。実製品で何を高影響とみなすかはProfile / Policy側の責務です。

## 7. 自動検査する不変条件

`tools/check_projection_evaluation.py`は少なくとも次を検査します。

1. canonical sourceがDecision Memory schemaへ適合する。
2. Light / Audit生成の前後でcanonical sourceが変化しない。
3. Audit Projectionのsemantic answersがcanonical sourceと一致する。
4. Light ProjectionにDecision statement、basis件数、unresolved件数、responsibility件数、Authority非推定の注記が存在する。
5. 保存済みexpected Light / Audit snapshotと生成結果が一致する。
6. Light Projectionからunresolvedを隠す改変を検出する。
7. Light Projectionからresponsibilityを隠す改変を検出する。
8. Audit Projectionからbasisを落とす改変を検出する。
9. Audit Projectionへ`authority_granted`等のcanonical sourceにない意味を追加する改変を検出する。
10. high-impact caseでLightだけを許可しない。
11. low-impact caseへAuditだけを強制しない。
12. Lightを破棄した後でも、同じcanonical sourceからAuditを再生成できる。

## 8. Structured human review

自動checkerだけでは、人間が実際に読みやすいかを十分に評価できません。そのため、後続のreviewでは次を`pass / concern / not reviewed`で記録します。

| 観点 | 確認内容 |
|---|---|
| Decision理解 | 何を決めたかを誤読せず把握できるか |
| Unresolved可視性 | 未解決事項が残っていることを見落としにくいか |
| Basis到達性 | 根拠が存在することを確認し、必要なら詳細へ降りられるか |
| Responsibility到達性 | 誰／何がこの文脈で責任を持つかの参照へ降りられるか |
| Authority境界 | Responsibilityやactor種別からAuthority成立を誤推定させないか |
| Progressive Explicitness | low-impactでは過剰に重くなく、high-impactでは必要情報を隠さないか |
| Projection非正本性 | 表示を変更・削除してもcanonical sourceが別物にならないことを理解できるか |

単一の点数へ集約しません。concernがある場合は、どのScenario・どの意味が読み取りにくかったかを文章で残します。

## 9. Evidence境界

専用CIが成功した場合でも得られるのは、**evaluation-harness scoped Executable Evidence**です。

```text
Projection Evaluation CI PASS
  != production UX validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

structured human reviewを一度実施しても、それだけで実利用者のOperational / Adoption Evidenceとはみなしません。

## 10. 変更時の扱い

canonical ContractやProjection evaluation ruleを変更した場合は、expected snapshotだけを都合よく更新してPASSさせません。

次の順で確認します。

1. Product Value / REQ / SCN上の意味が変わったか。
2. canonical sourceの意味が変わったか。
3. Projectionの表示方法だけが変わったか。
4. negative caseが弱くなっていないか。
5. Evidence claimの高さを誤って上げていないか。

新しいUniversal semantic conceptが必要に見えた場合は、このevaluation harnessへ埋め込まず、別Issue / ADR候補として扱います。

## 11. Natural Japanese review

V6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017、Decision Memory Contract、ISSUE-000039へ戻って評価境界を整理しました。その後、Projection評価と製品UI、自動checkerと人間の理解、Executable EvidenceとOperational / Adoption・Outcomeを混同しないよう意味と留保を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
