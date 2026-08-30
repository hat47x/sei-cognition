# ADR-0017: Reference Model / PatternとCognitive Methodを分離する

Status: **Accepted**  
Related Issue: **ISSUE-000019**  
Updated: 2026-08-31

## Context

X-TEA時代のReference Modelには、業務domainの典型構造、設計Pattern、確認観点、実装例、手順が混在していた。

後発議論では、Reference Modelを正解テンプレートとして対象へ適用するのではなく、AIや設計者が候補を探索・比較するためのPattern Cardとして扱う方向へ修正された。

一方SOZAは、KJ法やcultural-substrate-weavingのように、資料をどう探索し、どう比較し、どう統合・検査するかというCognitive Methodの意味境界を持つ。

両者を混ぜると、domain-specificな設計PatternがSOZA Universal Coreへ流入したり、Methodを使っただけで特定Patternの採用が決まったように見えたりする。

## Decision

### 1. Reference Model / Patternはdomain-specificなDesign Knowledgeとして扱う

業務domain固有のReference Model、Pattern Card、典型的なData / Workflow / Authorization構造等は、原則としてTEI Design Knowledgeまたはdomain-specific knowledge assetへ置く。

それらをSOZA Universal Coreの型体系へ移さない。

### 2. Cognitive Methodは探索・比較・統合・検査の手続きを表す

SOZA側のCognitive Methodは、たとえば次を表し得る。

- どの資料やPattern候補を探索するか。
- 何を比較するか。
- どの反例・境界・残差を確認するか。
- どの手順で統合・検証するか。

```text
Reference Model / Pattern != Cognitive Method
```

同じPatternを複数Methodから利用してもよく、同じMethodが異なるdomainのPattern集合を入力にしてもよい。

### 3. Pattern matchをDecisionへ自動昇格させない

Patternが対象へ似ている、AIがPatternを提示した、MethodがPatternを候補に選んだ、という事実だけでは採用Decisionは成立しない。

```text
Pattern match != Recommendation != Decision
```

必要に応じてAIの候補提示をRecommendationとして表し、採用・不採用・修正はDecisionへ戻す。

### 4. Method ApplicationをAssuranceへ自動昇格させない

Cognitive Methodを適用した事実は、その結論が正しいことを意味しない。

```text
Method Application != conclusion truth != Assurance
```

Method Applicationは来歴として保持し、Assuranceは別のEvidence / review境界で扱う。

### 5. historical Reference / Patternを必要に応じてexact-bindする

重要なDecisionでReference Modelの特定版やPatternの内容がbasisになった場合、後から現在版へ差し替えず、必要に応じてExactArtifactBinding等で当時参照した内容を特定できるようにする。

X-TEA由来のReference Modelは、歴史・設計系譜のprovenanceを残しつつ、現行TEI Productの絶対的正本とはみなさない。

## Consequences

### Positive

- TEIはdomain-specificなDesign Knowledgeを豊かにできる。
- SOZAは特定業務Schemaへ依存せずCognitive Methodを再利用できる。
- Reference Modelを答えとして押し付けず、AI探索の候補資産として使える。
- Pattern採用のDecisionとPattern利用の来歴を分けられる。
- Reference Model改訂後も過去Decisionを再構成しやすい。

### Costs

- TEI Design KnowledgeとSOZA Cognitive Methodの間に参照・adapterが必要になる。
- Pattern catalogとMethod catalogを別々に管理する必要がある。
- UIではPattern、Recommendation、Decision、Method Applicationを組み立てて表示する必要がある。

## Revisit conditions

複数domainでPatternそのものにSOZA共通のstable identity / revision / responsibilityが必要となり、domain-specific knowledge assetでは意味を保てないことが実証された場合に、Universal Pattern Artifactを再検討する。

## Evidence

- `plan/kj/2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md`
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`
- M47 Cognitive Method boundary
- TEI設計系列におけるReference Model→Pattern Card化の更新線

## Natural Japanese review

KJ統合とSOZA / TEI Product Boundaryを確定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
