# ISSUE-000023: Product Valueの優先規則と検証境界を正式化する

Status: **Resolved**  
Priority: **1**  
Updated: 2026-08-31

## 背景

SOZAのProduct Valueは、判断の意味、不確実性、責任、来歴、CapabilityとProviderの分離、実行基盤からの独立性を中核として既に定義されている。

一方、下位設計が増えるにつれ、次の問いを個別ADRだけで処理すると判断基準が揺れる可能性がある。

- 意味保存、操作性、性能、実装容易性が衝突したとき、何を優先するか。
- 新しい概念をSOZA Universal Coreへ含める基準は何か。
- Product Valueを満たしたと判断するには、どの観点で検証するか。
- 特定ProviderやTEIとの密接な関係が、SOZA Coreへの昇格理由になり得るか。
- 将来技術が変わったときにも残すべき価値は何か。

これらをProduct Value層で明示し、Requirements以下から参照可能にする必要がある。

## 調査・整理した論点

1. Product Valueを「失ってはならない意味」「選び直せること」「利用し続けられること」の三層へ整理する。
2. 価値衝突時の優先規則を定める。
3. Universal Coreへ入れる／入れない判断の基準を明示する。
4. Historical Reconstruction、Semantic Separation、Revision Integrity、Provider Independence、Uncertainty Preservation等を価値検証軸として定義する。
5. 実行成功、Method Application、Recommendation等をProduct Value上の保証へ誤昇格させない。
6. 10〜50倍程度の移動する将来地平を、具体的な未来予測ではなく過適合監査として位置づける。

## 結論

`product/value/SOZA_VALUE_MODEL.md`を追加し、Product Valueを設計判断へ落とせる粒度まで精緻化した。

また、このValue Modelの権威関係と変更規則をADR-0018で固定する。

## Acceptance

- [x] Product Valueの価値階層が明文化されている。
- [x] 価値衝突時の優先規則が明文化されている。
- [x] Universal Coreへの昇格基準と除外基準が明文化されている。
- [x] Product Valueを検証する観点が定義されている。
- [x] 失敗パターンが列挙されている。
- [x] TEIや特定Providerとの近さだけではCoreへ昇格しないことが確認されている。
- [x] 自然な日本語を最優先に全文を再ドラフトし、意味監査を実施している。

## 関連

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `ADR-0001`
- `ADR-0012`
- `ADR-0013`
- `ADR-0014`
- `ADR-0017`
- `ADR-0018`
