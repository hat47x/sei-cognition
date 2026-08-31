# ISSUE-000023: Product Valueの優先規則と検証境界を正式化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0018**  
Updated: 2026-08-31

## 背景

SOZAのProduct Valueは、判断の意味、不確実性、責任、来歴、CapabilityとProviderの分離、実行基盤からの独立性を中核として定義している。

下位設計が増えるにつれ、次の問いを個別ADRだけで処理すると、設計判断や達成主張の基準が揺れる可能性がある。

- 意味保存、操作性、性能、実装容易性が衝突したとき、何を優先するか。
- 新しい概念をSOZA Universal Coreへ含める基準は何か。
- Product Valueを満たしたと判断するには、どの観点で検証するか。
- Design、Executable、Release、Operationalの各Evidenceをどこまで区別するか。
- 本番で正常に動いたことと、利用者や組織へ価値が届いたことをどう分けるか。
- 特定ProviderやTEIとの密接な関係が、SOZA Coreへの昇格理由になり得るか。
- 将来技術が変わったときにも残すべき価値は何か。

これらをProduct Value層で明示し、Requirements以下から参照できる状態にする必要がある。

## 整理した論点

1. Product Valueを「失ってはならない意味」「選び直せること」「利用し続けられること」の三層として扱う。
2. 価値衝突時の優先規則を定める。
3. Universal Coreへ入れる／入れない判断の基準を明示する。
4. V1 Historical Reconstruction〜V8 Execution Independenceを、相互に相殺しない価値検証軸として定義する。
5. 実行成功、Method Application、Recommendation等をProduct Value上の保証へ誤昇格させない。
6. Design / Executable / Release / Operational / Adoption・OutcomeのEvidenceを分離する。
7. 運用成功だけを利用者価値の実現とみなさない。
8. V1〜V8からREQ、SCN、ADR、Architecture、Contract、Evidenceへ追跡できるようにする。
9. 10〜50倍程度の移動する将来地平を、具体的な未来予測ではなく過適合監査として位置づける。

## Resolution

Product Value governanceは、次の文書群をcurrent baselineとして確定した。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

`SOZA_VALUE_MODEL.md`は価値の階層・優先関係・V1〜V8を定める。

`SOZA_VALUE_ACCEPTANCE.md`は、V1〜V8をどの高さのEvidenceで確認するかを定める。Evidenceは次を分ける。

```text
Design
  != Executable
  != Release
  != Operational
  != Adoption / Outcome
```

`SOZA_VALUE_TRACEABILITY.md`は、Product Valueからcurrent REQ / SCN / ADR / Architecture / Contract / Evidence gapへ戻るための索引とする。

これらの権威関係と変更規則はADR-0018で固定する。

## Acceptance

- [x] Product Valueの価値階層が明文化されている。
- [x] 価値衝突時の優先規則が明文化されている。
- [x] Universal Coreへの昇格基準と除外基準が明文化されている。
- [x] V1〜V8の検証軸が定義されている。
- [x] 各軸を単一スコアで相殺しないことが定義されている。
- [x] Design / Executable / Release / Operational / Adoption・Outcomeを区別している。
- [x] Operational Successと利用者価値の実現を同一視しない。
- [x] Product Valueから下位設計・Evidenceまで追跡する規則がある。
- [x] 失敗パターンが列挙されている。
- [x] TEIや特定Providerとの近さだけではCoreへ昇格しないことが確認されている。
- [x] 自然な日本語を最優先に全文を再ドラフトし、意味監査を実施している。

## Evidence state

本Issueの`Resolved`は、Product Value governanceの**Design boundaryが確定したこと**を示す。

current repositoryではContract v1alpha1の一部にfixture-scoped Executable Evidenceがあるが、それをProduct Value全体のExecutable Acceptanceへ拡張しない。

Release、Operational、Adoption / Outcome Evidenceは、それぞれ対象Scenarioに応じた後続Evidenceが必要である。

## 関連

- `product/README.md`
- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `architecture/TRACEABILITY.md`
- `contracts/TRACEABILITY.md`
- `ADR-0001`
- `ADR-0012`
- `ADR-0013`
- `ADR-0014`
- `ADR-0017`
- `ADR-0018`
- `ADR-0020`
- `ADR-0021`

## Natural Japanese review

Product Value、Value Acceptance、current Requirements / Architecture / Contractの実体を再確認し、Design Evidenceと実際の価値実現を混同しないよう論点を再整理した。その後、意味、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
