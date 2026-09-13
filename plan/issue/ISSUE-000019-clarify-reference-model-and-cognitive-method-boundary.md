# ISSUE-000019: Reference ModelとCognitive Methodの境界を整理する

Status: **Resolved**  
Priority: **4**  
Related ADRs: **ADR-0014, ADR-0017**  
Updated: 2026-08-31

## Goal

渡辺幸三系のReference Model、Pattern Card、典型業務知識を、TEIのDesign Knowledge、SEIのCognitive Method、historical referenceのどこへ位置付けるかを整理する。

## Background

初期X-TEAでは、Reference Modelが設計の出発点として強い役割を持っていた。

後発議論では、Reference Modelを正解テンプレートとして対象へ適用するのではなく、既存Patternや候補を探索する知識として使い、Analyzer / Simulator / AI等によって対象へ適合するかを確認する方向へ修正された。

一方、SEIはCognitive Method Definition / Realization / Applicationの意味境界を耐久的な中心候補として持つ。

このため、Reference Modelに含まれる「設計対象について何を問い、どう検査するか」という手続きと、具体的な業務PatternやSchemaを分ける必要があった。

## Resolution

ADR-0017で、次の境界をAcceptedとした。

1. **Reference Model / Patternはdomain-specificなDesign Knowledgeとして扱う。**  
   業務domain固有のPattern、典型Data構造、Workflow、Authorization構造等は、TEI Design Knowledgeまたはdomain-specific knowledge assetへ置く。

2. **Cognitive Methodは探索・比較・統合・検査の手続きを表す。**  
   どの資料やPatternを探索するか、何を比較するか、どの反例・残差を調べるかという手続きはSEI側で表現できる。

3. **Pattern matchをRecommendationやDecisionへ自動昇格させない。**

```text
Pattern match != Recommendation != Decision
```

4. **Method ApplicationをAssuranceへ自動昇格させない。**

```text
Method Application != conclusion truth != Assurance
```

5. **重要な過去Decisionで特定版のReference Model / Patternがbasisになった場合は、必要に応じてExactArtifactBinding等で当時の参照内容を特定する。**

6. **historical X-TEA assetは設計系譜としてprovenanceを残すが、現行TEI Productの正本とはみなさない。**

## Questionsへの回答

1. domain固有PatternはTEI Design Knowledge側へ置く。  
2. 探索・検証手続きはSEI Cognitive Methodとして表現できる。  
3. Pattern Cardは「候補となる設計知識」、Method Definitionは「候補をどう探索・比較・検査するか」で分ける。  
4. Reference Modelを使った事実はprovenance / Method Applicationとして、採用判断はDecisionとして分ける。  
5. AIがPattern探索に利用した事実は、再構成上重要な場合にMethod Applicationや参照来歴として残す。  
6. 重要なbasisはexact bindingにより過去版を再構成する。  
7. X-TEA由来assetにはhistorical provenanceを付け、現行canonical assetと分ける。  
8. 対象へ押し付けない探索手続きはMethod、domain上の具体的制約やPatternはDesign Knowledgeとして扱う。

## Acceptance

- [x] Reference Model / Pattern / Methodの意味境界が定義されている。
- [x] ownership boundaryがADR-0017で固定されている。
- [x] historical provenance ruleが定義されている。
- [x] Pattern matchとDecisionが分離されている。
- [x] Method ApplicationとAssuranceが分離されている。
- [x] Product ValueのV1、V2、V3、V4、V8と矛盾しないことを確認した。
- [x] 自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。

## Follow-up

具体的なPattern catalogやMethod catalogのwire schema、TEI Editor上のUI、acceptance fixtureは、それぞれの実装Issueで扱う。これらを本Issueの未解決条件にはしない。

## Source

- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`
- `plan/adr/ADR-0017-reference-model-cognitive-method-boundary.md`
- `product/value/SEI_VALUE_MODEL.md`

## Natural Japanese review

ADR-0017とValue Modelへ戻って結論を再確認した後、意味、留保、技術的境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最終意味監査も実施済み。
