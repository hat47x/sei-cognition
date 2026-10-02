# V6 / V7 Human Structured Review Template

更新日: 2026-09-01  
位置づけ: **Review record template — Evidenceではない**

## 1. 使い方

このテンプレートは、人間向けProjectionが実際に理解可能かを、単一スコアへ潰さず記録するためのものです。

自動checkerのPASSだけでは、実利用者にとって十分に読みやすいとは判断しません。また、このテンプレートへ記録しただけでOperational EvidenceやAdoption / Outcome Evidenceが成立するわけでもありません。

## 2. Review context

- Review date:
- Reviewer role / context:
- Projection profile: light / audit / other
- Evaluation fixture or actual case:
- Intended impact class: low / high / other contextual policy

## 3. Semantic questions

各項目について、`確認できた / 辿れば確認できた / 確認できない / 誤読した`のいずれかを記録し、必要なら短い理由を添えます。

| ID | 問い | 結果 | 理由・引っかかり |
|---|---|---|---|
| Q1 | 何がDecisionされたか |  |  |
| Q2 | 何が未解決のまま残ったか |  |  |
| Q3 | 何がbasisとして使われたか |  |  |
| Q4 | どのResponsibilityが関係するか |  |  |
| Q5 | Authorization Evidenceの認識状態は何か |  |  |
| Q6 | basisに関係するProvenanceへ戻れるか |  |  |

## 4. Progressive Explicitness

- 低影響案件で、不要な最大詳細が前景化されていなかったか:
- 高影響案件で、必要なbasis / unresolved / Responsibility / Authorization Evidence / Provenanceが隠れていなかったか:
- 詳細へ降りる導線は、必要なときに見つけられたかは次のとおりです。
- lightからauditへ移っても、別のDecisionへ見えるような意味の断絶はなかったか:

## 5. 誤読・残差

- Projectionから推測してしまったが、canonical sourceには存在しなかった意味:
- machine-readable representationには存在したが、人間向けProjectionから辿れなかった意味:
- 表示量を減らしても残すべきだった情報は次のとおりです。
- 表示量を増やしても理解に寄与しなかった情報は次のとおりです。
- その他の違和感・残差は次のとおりです。

## 6. 判定

最終判定は単一UXスコアではなく、次のいずれかで記録します。

- `scenario-satisfied` — 対象Scenarioの意味を矛盾なく回収できた。
- `scenario-partially-satisfied` — 回収できるが導線・表現に改善余地がある。
- `scenario-not-satisfied` — 重要な意味の欠落・誤読・矛盾がある。
- `not-yet-verified` — 評価条件が不足している。

判定は次のとおりです。

根拠は次のとおりです。

## 7. Evidence boundary

本テンプレートは評価記録の形式です。実利用者による反復評価、production Projection、実運用条件等が伴わない限り、Release / Operational / Adoption・Outcomeを主張しません。

## 8. Natural Japanese review

ISSUE-000039のsemantic question setとEvidence境界を基準に、評価者へ不要な専門用語を押し付けすぎず、一方で意味欠落を曖昧な満足度へ還元しない形式として整理しました。その後、評価強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
