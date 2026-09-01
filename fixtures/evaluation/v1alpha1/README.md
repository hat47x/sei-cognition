# V6 / V7 Projection Evaluation Fixtures

更新日: 2026-09-01  
状態: **Evaluation-only Fixture Set**

## 1. 目的

このディレクトリは、ISSUE-000039で定義したHuman / AI ReadabilityとProgressive Explicitnessの評価に使うfixtureを保持します。

ここに置くProjectionはSOZAの新しいContract familyでも、Durable Semantic Coreでもありません。

```text
Evaluation fixture / projection
  != Canonical Semantic Authority
  != Product UI specification
```

## 2. Canonical source

`decision-projection-source.json`は`soza.decision-memory/v1alpha1`に従う評価用Decisionです。

専用checkerはcurrent Decision Memory schemaへ適合することを毎回確認します。

このsourceには、Projection評価に必要な次の意味を意図的に含めています。

- Decision statement
- basis 2件
- unresolved 2件（unknown 1件 / conflict 1件）
- responsibility 1件
- rationale

`authority-confirmation`はunresolvedなUnknownへのReferenceです。Authorityが付与済みであることを意味しません。

## 3. Expected Projection

`expected/light.md`と`expected/audit.json`は、current評価rendererの期待出力です。

- light: 人間向けの簡潔な表示
- audit: 詳細な構造表示

snapshotはcanonical sourceの代替ではありません。snapshotを変更してcheckerを通す前に、canonical meaningや評価規則が変わったのか、単なる表示変更なのかを確認します。

## 4. Evidence境界

専用CIがPASSした場合に確認できるのは、このfixtureと評価renderer / checkerの範囲だけです。

```text
Evaluation fixture PASS
  != production Projection validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 5. Natural Japanese review

ISSUE-000039、V6 / V7評価protocol、Decision Memory Contractへ戻ってfixtureの役割を確認した後、canonical sourceとexpected outputの意味を変えず、自然な日本語となることを最重要視して本文を再ドラフトし、最終意味監査を実施済みです。
