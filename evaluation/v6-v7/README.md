# V6 / V7 Projection Evaluation

更新日: 2026-09-01  
状態: **Evaluation Harness Baseline**  
対象Issue: **ISSUE-000039**

## 1. 目的

この評価系は、SOZAの次のProduct Valueを、特定のUI技術へ固定せず再現可能に検査するためのものです。

- V6 — Human / AI Readability
- V7 — Progressive Explicitness

評価対象は、**同じcanonical meaningから人間向けProjectionとmachine-readable representationの双方が必要な意味へ戻れること**、および**案件の影響度に応じて前景化する詳細を変えてもcanonical meaningを削らないこと**です。

```text
Projection evaluation
  != Product UI completion
  != Projection as semantic authority
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Projectionは評価用の派生表示です。新しいUniversal Contract familyやSOZA Core型ではありません。

## 2. Traceability

### Product Value

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

### ADR

- ADR-0005 — Progressive Semantic Explicitness
- ADR-0018 — Product Value authority / evaluation boundary
- ADR-0020 — Requirements traceability / Evidence boundary
- ADR-0021 — Architecture / Contract authority boundary

## 3. canonical source

評価fixtureはcurrent Contractに従うcanonical sourceです。

```text
fixtures/contracts/v1alpha1/evaluation/
  E1-projection-rich-decision.json
  E2-low-impact-minimal-decision.json
```

### E1 rich decision

高影響案件を模したSemantic Interchangeです。Decisionだけでなく、basis、未解決事項、Responsibility、Capability Observation、Provenanceを保持します。

AuthorizationそのものをDecisionへ埋め込みません。`authorization-evidence`への未解決参照が残っているため、Projectionでは「Authorization Evidence: unresolved」と表現します。

```text
unresolved authorization evidence
  != authority granted
  != authority denied
```

### E2 low-impact decision

可逆なローカル作業を模した最小Decisionです。basisやResponsibilityを一律必須にせず、低影響案件へ監査用最大詳細を強制しないことを確認します。

## 4. semantic question set

単一の可読性スコアは使いません。次の問いへ意味上矛盾なく戻れるかを検査します。

| ID | 問い | light | audit | machine-readable |
|---|---|---:|---:|---:|
| Q1 | 何がDecisionされたか | 必須 | 必須 | 必須 |
| Q2 | 何が未解決のまま残ったか | 必須 | 必須 | 必須 |
| Q3 | 何がbasisとして使われたか | 件数とaudit導線 | 必須 | 必須 |
| Q4 | どのResponsibilityが関係するか | 件数とaudit導線 | 必須 | 必須 |
| Q5 | Authorization Evidenceの認識状態は何か | 必須 | 必須 | 必須 |
| Q6 | basisに関係するProvenanceへ戻れるか | 件数とaudit導線 | 必須 | 必須 |

light Projectionは詳細を全部前景化しませんが、詳細の存在を隠してはいけません。basis、Responsibility、Provenanceが存在する場合は件数とaudit Projectionへの導線を保持します。

## 5. Progressive Explicitness policy

評価harnessでは、UI部品ではなくimpact classを入力として扱います。

### low-impact / reversible

- light Projectionを標準とする。
- Decisionと未解決事項を前景化する。
- canonical sourceに存在しないbasis / Responsibilityを新たに入力必須にはしない。
- audit Projectionは利用可能でも、常時最大詳細を強制しない。

### high-impact / consequential

- audit Projectionでの確認を必須とする。
- basis、unresolved、Responsibility、Authorization Evidence state、Provenanceへ降りられなければ合格にしない。
- light Projectionだけで完了扱いにはしない。

このpolicyは評価用であり、固定のUniversal impact taxonomyではありません。

## 6. Projection

current harnessでは、同じcanonical sourceから次を生成します。

```text
canonical source
  ├─ light Projection
  └─ audit Projection
```

期待例は次です。

```text
evaluation/v6-v7/projections/light.md
evaluation/v6-v7/projections/audit.md
```

Projectionを削除・再生成してもcanonical sourceは変更されません。harnessはcanonical JSONのdigestをProjection生成前後で比較し、暗黙の書換えをnegative caseとして検出します。

## 7. Negative cases

`negative-cases.json`では、少なくとも次を失敗として固定します。

1. 未解決事項をlight Projectionから隠す。
2. basisがcanonical sourceにあるのに、light Projectionから存在さえ辿れない。
3. Responsibilityがcanonical sourceにあるのに、light Projectionから存在さえ辿れない。
4. canonical sourceにないAuthorization成立をProjectionが追加する。
5. Projection編集の副作用としてcanonical sourceを書き換える。
6. high-impact案件をlight Projectionだけで完了扱いにする。
7. low-impact案件へaudit最大詳細を一律必須化する。

negative caseは「悪いProjectionの標準仕様」ではなく、評価checkerが境界違反を検出できることを確かめる固定入力です。

## 8. 実行方法

repository rootで次を実行します。

```bash
python -m pip install -r tools/contract-check-requirements.txt
python evaluation/v6-v7/check_projection_evaluation.py
```

checkerは次を一つのrunで確認します。

1. E1 / E2がcurrent Contract Schemaとsemantic invariantに適合する。
2. rich canonical sourceからlight / audit Projectionを再現できる。
3. committed Projection例と生成結果が一致する。
4. audit Projectionとmachine-readable sourceのsemantic question回答が一致する。
5. light Projectionが未解決事項を保持し、詳細の存在とaudit導線を失わない。
6. low-impact / high-impactの明示量policyを区別できる。
7. Projection生成前後でcanonical sourceが不変である。
8. 7件のnegative caseが期待したerror codeで拒否される。

CIは`.github/workflows/projection-evaluation.yml`を正とします。

## 9. Human structured review

自動checkerは意味欠落や矛盾を検出できますが、実際の人間にとって読みやすいかを完全には代替しません。

`HUMAN_REVIEW_TEMPLATE.md`に、単一スコアへ還元しないstructured review項目を置きます。実利用者による評価が得られるまでは、テンプレートの存在をOperational / Adoption Evidenceへ昇格させません。

## 10. Evidence boundary

このharnessがPASSした場合に直接主張できるのは、evaluation-harness scoped Executable Evidenceまでです。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

production UI、実際の利用者の理解時間、誤読率、判断品質、業務成果は本評価のscope外です。

## 11. Natural Japanese review

ISSUE-000039、V6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017、ADR-0005 / 0018 / 0020 / 0021、current Contract境界へ戻って評価設計を確認しました。その後、Projectionを正本化しないこと、低影響と高影響を固定taxonomyにしないこと、Executable Evidenceを上位Evidenceへ昇格させないことを維持したまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
