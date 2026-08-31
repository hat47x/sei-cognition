# ADR-0017: Reference Model / PatternとCognitive Methodを分離する

Status: **Accepted**  
Related Issues: **ISSUE-000019, ISSUE-000034**  
Updated: 2026-08-31

## Context

業務domainのReference Modelには、典型構造、設計Pattern、確認観点、実装例、手順等が含まれ得る。

これらを正解テンプレートとして対象へ一律適用すると、実際の業務や制約との差を見落としやすい。一方で、候補を探索・比較するためのDesign Knowledgeとして扱えば、設計支援に利用できる。

SOZAのCognitive Methodは、資料や候補をどのように探索し、比較し、統合し、検査するかという認知上の手続きを扱う。

Reference Model / PatternとCognitive Methodを混ぜると、domain-specificな設計PatternがUniversal Coreへ流入したり、Methodを適用しただけで特定Patternの採用が決まったように見えたりする。

## Decision

### 1. Reference Model / Patternはdomain-specificなDesign Knowledgeとして扱う

業務domain固有のReference Model、Pattern Card、典型的なData / Workflow / Authorization構造等は、原則としてdomain-specificなDesign Knowledgeへ置く。

特定の製品がそれらを管理することはできるが、SOZA Universal Coreの型体系へ自動的に移さない。

### 2. Cognitive Methodは探索・比較・統合・検査の手続きを表す

SOZAのCognitive Methodは、たとえば次のような手続きを表し得る。

- どの資料やPattern候補を探索するか。
- 何を比較するか。
- どの反例、境界、残差を確認するか。
- どの手順で統合・検証するか。

```text
Reference Model / Pattern != Cognitive Method
```

同じPatternを複数のMethodから利用してもよく、同じMethodが異なるdomainのPattern集合を入力としてもよい。

### 3. Pattern matchをDecisionへ自動昇格させない

Patternが対象に似ている、AIがPatternを提示した、MethodがPatternを候補に選んだ、という事実だけでは採用Decisionは成立しない。

```text
Pattern match != Recommendation != Decision
```

必要に応じて候補提示をRecommendationとして表し、採用、不採用、修正等はDecisionとして扱う。

### 4. Method ApplicationをAssuranceへ自動昇格させない

Cognitive Methodを適用したという事実は、その結論が正しいことを意味しない。

```text
Method Application != conclusion truth != Assurance
```

Method Applicationは来歴として保持し、Assuranceは別のEvidence / review境界で扱う。

### 5. historical Reference / Patternを必要に応じてexact-bindする

重要なDecisionでReference Modelの特定版やPatternの内容がbasisになった場合、後から現在版へ差し替えず、必要に応じてExactArtifactBinding等で当時参照した内容を特定できるようにする。

過去の製品名や設計系列に由来するReference Modelも、歴史・設計系譜のProvenanceを残しつつ、現在のProductにおける絶対的な正本とはみなさない。

## Current realization

current SOZAでは、Cognitive MethodのDefinition / Realization / Applicationという意味境界を保持し、Method ApplicationをRecommendation、Decision、Authority、Executionとは分離している。

一方、domain-specificなPattern catalogをSOZA Universal Coreへ実体化してはいない。この非対称性は意図的であり、Patternの内容と、それを探索・利用するMethodの手続きを別の責務として保つためである。

historical Cognitive Methodのdigest規則について未確認の部分はISSUE-000034で扱うが、これは本ADRのPattern / Method分離を変更するものではない。

## Consequences

### Positive

- domain-specificなDesign Knowledgeを豊かにしても、SOZA Coreを特定業務Schemaへ依存させずに済む。
- Reference Modelを答えとして押し付けず、探索・比較の候補資産として利用できる。
- Pattern採用のDecisionと、Patternを参照したMethod Applicationの来歴を分けられる。
- Reference Model改訂後も過去Decisionを再構成しやすい。

### Costs

- Design KnowledgeとCognitive Methodの間に参照境界が必要になる。
- Pattern catalogとMethod catalogを別々に管理する必要がある。
- UIではPattern、Recommendation、Decision、Method Applicationを必要に応じて組み合わせて表示する必要がある。

## Revisit conditions

複数domainでPatternそのものにSOZA共通のstable identity、revision、Responsibility等が必要となり、domain-specificなknowledge assetでは意味を保てないことが実証された場合に、Universal Pattern Artifactを再検討する。

## Natural Japanese review

current Cognitive Method、Decision Memory、Exact Binding境界へ戻ってDecisionを照合した。その後、検討手法や過去の製品名をADRの根拠構造から外し、Reference Model / PatternとCognitive Methodの責務差へ焦点を戻した。Pattern match、Recommendation、Decision、Method Application、Assuranceの意味差を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
